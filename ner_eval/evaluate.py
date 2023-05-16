import argparse
import os
import sys
from collections import defaultdict
import json

from clams.app import ClamsApp
from clams.restify import Restifier
from clams.appmetadata import AppMetadata
from mmif.serialize import Mmif
from mmif.vocabulary import AnnotationTypes, DocumentTypes
from lapps.discriminators import Uri

from seqeval.metrics import accuracy_score
from seqeval.metrics import classification_report
from seqeval.metrics import f1_score
from seqeval.scheme import IOB2

#======================= initializing label mapping =========================================================

label_dict = {'PERSON':'person', 'ORG':'organization', 'FAC':'location', 'GPE':'location', 'LOC':'location',
              'EVENT':'event', 'PRODUCT':'product', 'WORK_OF_ART':'program/publication_title',
              'program_title':'program/publication_title', 'publication_title':'program/publication_title'}
valid_labels = set(list(label_dict.keys()) + list(label_dict.values()))

def label_dict_to_string():
    # get the tap-separated string for printing out label dict relatively prettily
    return "\n".join(["original_label"+"\t"+"mapped_label"]+ \
                    [k+"\t"+label_dict[k] for k in label_dict])

label_dict_pretty = label_dict_to_string()

#======================= end initializing label mapping =====================================================


def entity_to_tokens(entity):
    """this function return a list of tokens (with a BIO label associated with
    each token) from an entity (currently only used when the entity is read from
    ann file, not mmif file) """
    
    words = entity['text'].split()
    start = entity['start']
    tokens = []
    label = entity['category']
    if(label not in valid_labels): #e.g. QUANTITY
        return tokens # do not include in the final list of entities
    if(label in label_dict):
        label = label_dict[label] # e.g. ORG -> organization
    for i, word in enumerate(words):
        end = start + len(word)
        if i==0:
            tokens.append(((start, end), 'B-'+label))
        else:
            tokens.append(((start, end), 'I-'+label))
        start = end + 1
    return tokens


def file_to_tokens(filename):
    """this function check whether the file is in .ann or .mmif format, then
    send it to the respective function to get the list of tokens """
    
    if(filename.endswith('.ann')):
        return ann_to_tokens(filename)
    elif(filename.endswith('.json') or filename.endswith('.mmif')):
        return mmif_to_tokens(filename)
    else:
        raise Exception("The annotation file must be ann file (end in .ann) or \
        mmif file (end in .json or .mmif)")
    

def ann_to_tokens(ann_path):
    """this function read .ann input file and return the list of tokens"""

    with open(ann_path, 'r') as fh_in:
        lines = fh_in.readlines()

    tokens = []
    for line in lines:
        ent = line.split()
        entity = { "start": int(ent[2]), "end": int(ent[3]),
                   "text": (" ".join(ent[4:])), "category": ent[1] }
        tokens = tokens + entity_to_tokens(entity)
    return tokens


def mmif_to_tokens(mmif_path):
    """this function read .mmif input file and return the list of tokens"""
    
    with open(mmif_path) as fh_in:
        mmif_serialized = fh_in.read()
        
    mmif = Mmif(mmif_serialized)
    ner_views = mmif.get_all_views_contain(at_types = Uri.NE)
    view = ner_views[-1] #read only the first view (from last) with Uri.NE
    
    token_annotations = view.get_annotations(at_type = Uri.TOKEN)
    span_to_id = {} # a dict that map token span to its id
    for token_annotation in token_annotations:
        token = token_annotation.properties
        span_to_id[token['id']] = (token['start'], token['end'])
    
    ner_annotations = view.get_annotations(at_type = Uri.NE)
    tokens = []
    for ner_annotation in ner_annotations:
        label = ner_annotation.properties['category']
        if(label in valid_labels): # we discard invalid labels e.g. QUANTITY
            if(label in label_dict):
                label = label_dict[label] # e.g. ORG -> organization
            targets = ner_annotation.properties['targets']
            for i, target in enumerate(targets):
                (start, end) = span_to_id[target]
                if(i == 0):
                    tokens.append(((start, end), 'B-'+label))
                else:
                    tokens.append(((start, end), 'I-'+label))
                        
    return tokens


def tokens_to_tags(tokens, span_map, mode='strict'):
    """this function transform list of tokens to list of tags"""
    tags = ['O'] * len(span_map)
    for (span, tag) in tokens:
        span_index = span_map[span]
        tags[span_index] = tag

    if(mode=='token'):
        # let each token be perceived as its own entity to 'trick' the entity-based eval module
        new_tags = ['B-'+tag[2:] if tag.startswith('I-') else tag for tag in tags]
        tags = new_tags

    return tags


def file_pair_to_tags(goldfile, testfile):
    # given a pair of files to be evaluated, return a pair of a list of tags that can be passed to
    # the seqeval NER evaluation

    tokens_true = file_to_tokens(goldfile)
    tokens_pred = file_to_tokens(testfile)

    #find a dict that maps all entity spans to indices
    tokens_all = (tokens_true + tokens_pred)
    spans_all = sorted(set([span for (span, label) in tokens_all]))
    span_map = {span:i for i, span in enumerate(spans_all)}

    tags_true, tags_pred = {}, {}
    for mode in ['strict','token']:
        tags_true[mode] = tokens_to_tags(tokens_true, span_map, mode)
        tags_pred[mode] = tokens_to_tags(tokens_pred, span_map, mode)

    return (tags_true, tags_pred)


def ner_report(result, goldfile, testfile, tail=False):
    # when the inputs are only one pair of goldfile and testfile
    # return 'pretty' NER result that could be written out to text file
    s = ""
    if(goldfile != None and testfile != None):
        s += "gold-standard file: " + goldfile + "\n"
        s += ("model prediction file: " + testfile + "\n\n")
    s += "Strict Evaluation Result\nevery token in an entity must have the matching tagging with \
the gold standard to count as the same entity\n"
    s += (result['strict'] + "\n")
    s += "Token-based Evaluation Result\nthe evaluation is done on the token level, and the \
difference between B- and I- is disregarded\n"
    s += (result['token'] + "\n")
    s += "=======================================================================================\n\n"
    if(tail==True):
        s += ("the labels from both files are mapped to the following labels\nlabels not in \
any column of the following table will be discarded\n\n")
        s += label_dict_pretty
    return s
             

def evaluate_single_file(goldfile, testfile, resultpath):
    # evaluate a pair of goldfile and testfile

    # transform the pair of files to a list of tags that can be passed to
    # the seqeval NER evaluation
    (tags_true, tags_pred) = file_pair_to_tags(goldfile, testfile)

    # evaluate
    result = {}
    for mode in ['strict','token']:
        y_true, y_pred = tags_true[mode], tags_pred[mode]
        result[mode] = classification_report([y_true], [y_pred], mode='strict', scheme=IOB2, output_dict=False)
        #do NOT change mode to 'token' here even if we're doing token-based eval, since \
        #we have already dealt with that in the tokens_to_tags function

    # write the result to text file
    s = ner_report(result, goldfile, testfile, tail=True)
    with open(resultpath, 'w') as fh_out:
        fh_out.write(s)


def find_videoname(filename):
    """
    find the name of the cpb video that the NER is done on.
    for example, "cpb-aacip-507-4746q1t25k-transcript.ann" would return
    "cpb-aacip-507-4746q1t25k"
    also check that the file is valid (either mmif file or .ann file)
    """
    if(not(filename.endswith('.ann') or filename.endswith('.json') or filename.endswith('.mmif'))):
        return None
    filename = os.path.splitext(filename)[0]
    filename_ts = filename.strip().split('-')
    if('cpb' in filename_ts):
        index_cpb = filename_ts.index('cpb')
        if((index_cpb + 3) < len(filename_ts)):
            return "-".join(filename_ts[index_cpb:(index_cpb+4)])
    return None


def evaluate_whole_folder(goldpath, testpath, resultpath):
    # evaluate whole folder of goldfiles and testfiles

    """
    iterate in both folder, to find matching pairs between the two folder
    for example, a file with name containing a substring "cpb-aacip-507-nk3610wp6s"
    will be matched to the file containing the same substring in another folder
    """
    filepairs = []
    for testfile in os.listdir(testpath):
        testfilename = find_videoname(testfile)
        #print('testfile', testfile, testfilename)
        if(testfilename != None):
            for goldfile in os.listdir(goldpath):
                #print('goldfile', goldfile, find_videoname(goldfile))
                if(find_videoname(goldfile) == testfilename):
                    filepairs.append((goldfile, testfile))

    s =  ("folder containing gold-standard files: " + goldpath + "\n")
    s += ("folder containing model prediction files: " + testpath + "\n")
    s += ("number of pairs of matching annotation files to be evaluated: " + str(len(filepairs))+"\n")
    s += "=======================================================================================\n\n"
    y_true_all = {'strict': [], 'token': []}
    y_pred_all = {'strict': [], 'token': []}
    for i, (goldfile, testfile) in enumerate(filepairs, start=1):
        # transform the pair of files to a list of tags that can be passed to
        # the seqeval NER evaluation
        (tags_true, tags_pred) = file_pair_to_tags(goldpath+goldfile, testpath+testfile)

        # evaluate
        result = {}
        for mode in ['strict','token']:
            y_true, y_pred = tags_true[mode], tags_pred[mode]
            y_true_all[mode] = (y_true_all[mode] + [y_true]) # store the tags for aggregated result
            y_pred_all[mode] = (y_pred_all[mode] + [y_pred])
            result[mode] = classification_report([y_true], [y_pred], mode='strict', scheme=IOB2, output_dict=False)
            #do NOT change mode to 'token' here even if we're doing token-based eval, since \
            #we have already dealt with that in the tokens_to_tags function

        # get 'pretty-printed' result
        s += ("Pair "+str(i)+"\n")
        s += ner_report(result, goldfile, testfile, tail=False)
        print(i)

    #calculate aggregated result
    result = {}
    for mode in ['strict','token']:
        result[mode] = classification_report(y_true_all[mode], y_pred_all[mode], mode='strict', scheme=IOB2, output_dict=False)
    s += ("Aggregated Result from "+str(len(filepairs))+" pairs of (gold standard file, model prediction file)\n\n")
    s += ner_report(result, goldfile, testfile, tail=True)

    # write the result to text file
    with open(resultpath, 'w') as fh_out:
        fh_out.write(s)
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('goldpath', nargs='?', help="gold annotation")
    parser.add_argument('testpath', nargs='?', help="test annotation")
    parser.add_argument('resultpath', nargs='?', help="path to print out eval result", default='results.txt')
    args = parser.parse_args()

    if(os.path.isdir(args.goldpath) and os.path.isdir(args.testpath)):
        evaluate_whole_folder(args.goldpath, args.testpath, args.resultpath)
    elif(os.path.isfile(args.goldpath) and os.path.isfile(args.testpath)):
        evaluate_single_file(args.goldpath, args.testpath, args.resultpath)
    else:
        raise Exception("The path to gold-standard annotation(s) and the path to model's annotation(s) must be the same type:\
        either both of them are directories, or both are regular files (and the files must exist)")


"""
example usage:
python evaluate.py goldfiles-example/ testfiles-example/
python evaluate.py goldfiles-example/ testfiles-example/ result-example.txt
python evaluate.py goldfiles/cpb-aacip-507-154dn40c26-transcript.ann testfiles/cpb-aacip-507-154dn40c26.mmif result-one-pair.txt
"""

#If gold is "Mark(B-PER) Zuckerburg(I-PER)" and model predict "Zuckerburg(B-PER)"
#strict:  1 FP (entity "Zuckerburg(PER)") and 1 FN (entity "Mark Zuckerburg(PER)")
#token: 1 TP (token "Zuckerburg(PER)") and 1 FN (token "Mark(PER)"), note that the evaluation doesn't care between B- and I- difference
