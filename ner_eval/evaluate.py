import argparse
import os
import sys
from collections import defaultdict
import json
import re

from clams.app import ClamsApp
from clams.restify import Restifier
from clams.appmetadata import AppMetadata
from mmif.serialize import Mmif
from mmif.vocabulary import AnnotationTypes, DocumentTypes
from lapps.discriminators import Uri

from seqeval.metrics import accuracy_score
from seqeval.metrics import classification_report
from seqeval.metrics import f1_score

label_dict = {'PERSON':'person', 'ORG':'organization', 'FAC':'location', 'GPE':'location', 'LOC':'location',
              'EVENT':'event', 'PRODUCT':'product', 'WORK_OF_ART':'program/publication_title',
              'program_title':'program/publication_title', 'publication_title':'program/publication_title'}
valid_labels = set(list(label_dict.keys()) + list(label_dict.values()))


def entity_to_tokens(index, entity):
    """this function return a list of tokens (with a BIO label associated with
    each token) from an entity """
    
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
            tokens.append(((index, start, end), 'B-'+label))
        else:
            tokens.append(((index, start, end), 'I-'+label))
        start = end + 1
    return tokens


def file_to_tokens(index, filepath):
    """this function check whether the file is in .ann or .mmif format, then
    send it to the respective function to get the list of tokens """
    
    if(filepath.endswith('.ann')):
        return ann_to_tokens(index, filepath)
    else: # mmif file, ends with .json or .mmif
        return mmif_to_tokens(index, filepath)
    

def ann_to_tokens(index, ann_path):
    """this function read .ann input file and return the list of tokens"""

    with open(ann_path, 'r') as fh_in:
        lines = fh_in.readlines()

    tokens = []
    for line in lines:
        ent = line.split()
        entity = { "start": int(ent[2]), "end": int(ent[3]),
                   "text": (" ".join(ent[4:])), "category": ent[1] }
        tokens = tokens + entity_to_tokens(index, entity)
    return tokens


def mmif_to_tokens(index, mmif_path):
    """this function read .mmif input file and return the list of tokens"""
    
    with open(mmif_path) as fh_in:
        mmif_serialized = fh_in.read()
        
    mmif = Mmif(mmif_serialized)
    ner_views = mmif.get_all_views_contain(at_types = Uri.NE)
    view = ner_views[-1] #read only the first view (from last) with Uri.NE
    annotations = view.get_annotations(at_type = Uri.NE)

    tokens = []
    for annotation in annotations:
        entity = annotation.properties
        entity["start"] = view.get_annotation_by_id(entity["targets"][0]).properties["start"]
        tokens = tokens + entity_to_tokens(index, entity)
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

def label_dict_to_string():
    # get the tap-separated string for printing out label dict relatively prettily
    return "\n".join(["original_label"+"\t"+"mapped_label"]+ \
                    [k+"\t"+label_dict[k] for k in label_dict])

def write_result(result, goldfile, testfile, resultpath):
    # write out eval results to text file
    s = "gold-standard directory: " + goldfile + "\n"
    s += ("model prediction directory: " + testfile + "\n")
    s += "\nStrict Evaluation Result\nevery token in an entity must have the matching tagging with \
the gold standard to count as the same entity\n"
    s += result['strict']
    s += "\nToken-based Evaluation Result\nthe evaluation is done on the token level, and the \
difference between B- and I- is disregarded\n"
    s += result['token']
    s += ("\nthe labels from both files are mapped to the following labels\nlabels not in \
any column of the following table will be discarded\n")
    s += ("\n"+label_dict_to_string())

    with open(resultpath, 'w') as fh_out:
        fh_out.write(s)
             

def directory_to_tokens(directory):
    tokens = []
    index = 0
    for file in directory:
        tokens = tokens + file_to_tokens(index, file)
        index += 1
    return tokens


def file_match(golddirectory, testdirectory):
    """compares the files in the golddirectory and testdirectory, returns lists of matching gold and test files in corresponding order"""
    gold_matches = []
    test_matches = []
    gold_list = os.listdir(golddirectory)
    test_list = os.listdir(testdirectory)
    for gold_file in gold_list:
        reg = "^" + os.path.splitext(gold_file)[0]
        for test_file in test_list:
            if re.search(reg, test_file):
                gold_matches.append(gold_file)
                test_matches.append(test_file)
                continue
        continue
    return [os.path.join(golddirectory, match) for match in gold_matches], [os.path.join(testdirectory, match) for match in test_matches]

def evaluate(golddirectory, testdirectory, resultpath):

    gold_matches, test_matches = file_match(golddirectory, testdirectory)

    tokens_true = directory_to_tokens(gold_matches)
    tokens_pred = directory_to_tokens(test_matches)

    #find a dict that maps all entity spans to indices
    tokens_all = (tokens_true + tokens_pred)
    spans_all = sorted(set([span for (span, label) in tokens_all]))
    span_map = {span:i for i, span in enumerate(spans_all)}

    result = {}
    for mode in ['strict','token']:
        y_true = tokens_to_tags(tokens_true, span_map, mode)
        y_pred = tokens_to_tags(tokens_pred, span_map, mode)
        result[mode] = classification_report([y_true], [y_pred], mode='strict', output_dict=False)
        #do NOT change mode to 'token' here even if we're doing token-based eval, since \
        #we have already dealt with that in the tokens_to_tags function

    write_result(result, golddirectory, testdirectory, resultpath)
    print("evaluation for "+ testdirectory + " is complete")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('gold_directory', nargs='?', help="directory that contains gold annotations")
    parser.add_argument('test_directory', nargs='?', help="directory that contains test annotations")
    parser.add_argument('result_path', nargs='?', help="path to print out eval result", default='results.txt')
    args = parser.parse_args()

    evaluate(args.gold_directory, args.test_directory, args.result_path)

"""
example usage:
python evaluate.py gold-files test-files
NOTE: gold annotation files and test output files that correspond to the same aapb catalog item must share the same file name (with the exception of file extension). i.e. gold-files/cpb-aacip-507-1v5bc3tf81-transcript.ann and test-files/cpb-aacip-507-1v5bc3tf81-transcript.mmif) 
"""

#If gold is "Mark(B-PER) Zuckerburg(I-PER)" and model predict "Zuckerburg(B-PER)"
#strict:  1 FP (entity "Zuckerburg(PER)") and 1 FN (entity "Mark Zuckerburg(PER)")
#token: 1 TP (token "Zuckerburg(PER)") and 1 FN (token "Mark(PER)"), note that the evaluation doesn't care between B- and I- difference
