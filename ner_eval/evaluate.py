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

label_dict = {'PERSON':'person', 'ORG':'organization', 'FAC':'location', 'GPE':'location', 'LOC':'location',
              'EVENT':'event', 'PRODUCT':'product', 'WORK_OF_ART':'program/publication_title',
              'program_title':'program/publication_title', 'publication_title':'program/publication_title'}
valid_labels = set(list(label_dict.keys()) + list(label_dict.values()))


def entity_to_tokens(entity):
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
            tokens.append(((start, end), 'B-'+label))
        else:
            tokens.append(((start, end), 'I-'+label))
        start = end + 1
    return tokens


def file_to_tokens(filepath):
    """this function check whether the file is in .ann or .mmif format, then
    send it to the respective function to get the list of tokens """
    
    if(filepath.endswith('.ann')):
        return ann_to_tokens(filepath)
    else: # mmif file, ends with .json or .mmif
        return mmif_to_tokens(filepath)
    

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
    annotations = view.get_annotations(at_type = Uri.NE)

    tokens = []
    for annotation in annotations:
        entity = annotation.properties
        tokens = tokens + entity_to_tokens(entity)
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
    s = "gold-standard file: " + goldfile + "\n"
    s += ("model prediction file: " + testfile + "\n")
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
             

def evaluate(goldfile, testfile, resultpath):

    tokens_true = file_to_tokens(goldfile)
    tokens_pred = file_to_tokens(testfile)

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

    write_result(result, goldfile, testfile, resultpath)
    print("finish evaluating "+testfile)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('goldfile', nargs='?', help="gold annotation")
    parser.add_argument('testfile', nargs='?', help="test annotation")
    parser.add_argument('resultpath', nargs='?', help="path to print out eval result", default='results.txt')
    args = parser.parse_args()

    evaluate(args.goldfile, args.testfile, args.resultpath)

"""
example usage:
python evaluate.py gold-file-examples/gold-ann-example.ann test-file-examples/test-mmif-example.mmif result-examples/result-example.txt
python evaluate.py gold-mmif.mmif test-mmif.mmif
"""

#If gold is "Mark(B-PER) Zuckerburg(I-PER)" and model predict "Zuckerburg(B-PER)"
#strict:  1 FP (entity "Zuckerburg(PER)") and 1 FN (entity "Mark Zuckerburg(PER)")
#token: 1 TP (token "Zuckerburg(PER)") and 1 FN (token "Mark(PER)"), note that the evaluation doesn't care between B- and I- difference
