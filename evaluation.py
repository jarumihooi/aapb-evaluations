
# import 
import os
import sys
from collections import defaultdict
import spacy
import json

from clams.app import ClamsApp
from clams.restify import Restifier
from clams.appmetadata import AppMetadata
from mmif.serialize import Mmif
from mmif.vocabulary import AnnotationTypes, DocumentTypes
from lapps.discriminators import Uri

# import from directory, read in gold standard and test annotation
# gold standard stored in the folder called annotations 
# gold_dir = "annotations"

gold_mmif_data = None  # Load your gold MMIF data here
test_mmif_data = None  # Load your test MMIF data here
label_choice = None  # Set your label_choice here, can be changed. It's for cases when comparing gold labels and test labels

# TODO: write annotation code to call spacy on file to generate annotations 

'''TODO: MMIF JSON files use a hierarchical structure to represent annotations, 
with each file containing multiple views, each view containing multiple annotations,
 and each annotation consisting of multiple properties. 
 MMIF JSON files can also include metadata, provenance information,
   and other types of annotations (such as image regions, audio segments, or gesture annotations)'''

# evaluation code
# the below is the clams vocabulary, I will match 
'''
Thing : id
    Annotation : [document] : document
            Region : [unit]
                TimePoint : point
                Interval : start, end, targets
                    Span
                        TimeFrame : frameType
                            Chapter : title
                Polygon : coordinates, timePoint
                    BoundingBox
                VideoObject : polygons
            Relation
    Document : location, mime
        VideoDocument
        AudioDocument
        ImageDocument
        TextDocument : text
    Alignment : source, target

'''
# heiarchy -> keep it 
MMIF_HIERARCHY = {
    "Thing": {
        "id": None,
        "Annotation": {
            "document": "document",
            "Region": {
                "unit": None,
                "TimePoint": "point",
                "Interval": {
                    "start": None,
                    "end": None,
                    "targets": None,
                    "Span": {
                        "TimeFrame": {
                            "frameType": None,
                            "Chapter": {
                                "title": None
                            }
                        }
                    }
                },
                "Polygon": {
                    "coordinates": None,
                    "timePoint": None,
                    "BoundingBox": {},
                    "VideoObject": {
                        "polygons": None
                    }
                }
            },
            "Relation": {}
        },
        "Document": {
            "location": None,
            "mime": None,
            "VideoDocument": {},
            "AudioDocument": {},
            "ImageDocument": {},
            "TextDocument": {
                "text": None
            }
        },
        "Alignment": {
            "source": None,
            "target": None
        }
    }
}

# TODO: from this weeks meeting, instead of using the CLAMS vocab, look for lables used in SpaCy


#converts them into a list of entity tuples 
def mmif_to_entity_list(mmif_data):
    # TODO: Implement the conversion from MMIF data to a list of entity tuples
    # based on your specific MMIF data format.
    pass

def evaluate_mmif(gold_mmif_data, test_mmif_data, label_choice):
    goldlist = mmif_to_entity_list(gold_mmif_data)
    testlist = mmif_to_entity_list(test_mmif_data)
    confusion_dict = evaluate_strict(goldlist, testlist, label_choice)
    calculate_F1(confusion_dict)

# calculation code
def sum_over_labels(confusion_dict):
    for s in ['true_pos','false_neg','false_pos']:
        confusion_dict[(s,'all')] = sum([confusion_dict[(s,label)] for label in interested_labels])


# macro F1:calculates the F1 score for each label individually and then takes the average of those F1 scores. 
# Equal weight to each label, more sensitive to the performance on the minority classes.
# Macro F1 = (F1_label1 + F1_label2 + ... + F1_labelN) / N

# Micro F1: F1 Calculate metrics globally by counting the total true positives, false negatives and false positives.
#  less sensitive to minority label performance, considers overall
# Micro F1 = 2 * (Aggregated_TP) / (2 * Aggregated_TP + Aggregated_FP + Aggregated_FN)


'''off the shelf code: 
def macro_micro_f1(confusion_dict, labels):
    macro_f1_sum = 0
    micro_tp = micro_fp = micro_fn = 0
    
    for label in labels:
        tp = confusion_dict[('true_pos', label)]
        fp = confusion_dict[('false_pos', label)]
        fn = confusion_dict[('false_neg', label)]
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        macro_f1_sum += f1
        micro_tp += tp
        micro_fp += fp
        micro_fn += fn
    
    macro_f1 = macro_f1_sum / len(labels)
    micro_precision = micro_tp / (micro_tp + micro_fp) if (micro_tp + micro_fp) > 0 else 0
    micro_recall = micro_tp / (micro_tp + micro_fn) if (micro_tp + micro_fn) > 0 else 0
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0
    
    return macro_f1, micro_f1
'''

## label-specific F1 scores and an overall F1 score. From Jinny's code, I think this part can be reused 
# Next step, implement it to calculate macro and micro F1. I wrote the code here, but still need to test it 
def calculate_F1(confusion_dict):
    all_labels = (interested_labels + ['all'])
    macro_f1_sum = 0
    macro_f1_count = 0
    for label in all_labels:
        try:
            confusion_dict[('precision',label)] = (confusion_dict[('true_pos',label)] / (confusion_dict[('true_pos',label)] + confusion_dict[('false_pos',label)]))
        except ZeroDivisionError:
            confusion_dict[('precision',label)] = None
        try:
            confusion_dict[('recall',label)] = (confusion_dict[('true_pos',label)] / (confusion_dict[('true_pos',label)] + confusion_dict[('false_neg',label)]))
        except ZeroDivisionError:
            confusion_dict[('recall',label)] = None
        if((confusion_dict[('precision',label)] != None) and (confusion_dict[('recall',label)] != None)):
            confusion_dict[('F1',label)] = ((2 * confusion_dict[('precision',label)] * confusion_dict[('recall',label)]) / \
                                        (confusion_dict[('precision',label)] + confusion_dict[('recall',label)]))
            if label != 'all':
                macro_f1_sum += confusion_dict[('F1', label)]
                macro_f1_count += 1
        else:
            confusion_dict[('F1',label)] = None

    print('Macro F1:\t', macro_f1)
    print('Micro F1:\t', micro_f1)
    gold_entity_count = (confusion_dict[('true_pos',label)] + confusion_dict[('false_neg',label)])
    test_entity_count = (confusion_dict[('true_pos',label)] + confusion_dict[('false_pos',label)])
    if(confusion_dict[('F1','all')]!=None):
        print('precision\t'+('%.3f' % confusion_dict[('precision','all')])+' ('+str(confusion_dict[('true_pos',label)])+'/'+str(test_entity_count)+')')
        print('recall\t'+('%.3f' % confusion_dict[('recall','all')])+' ('+str(confusion_dict[('true_pos',label)])+'/'+str(gold_entity_count)+')')
        print('F1\t'+('%.3f' % confusion_dict[('F1','all')]))
    else:
        print("F1 can't be calculated because the number of false positive, or false negative, or both, is zero.")
    
    # macro and micro f1
    macro_f1 = macro_f1_sum / macro_f1_count if macro_f1_count > 0 else None
    micro_f1 = confusion_dict[('F1', 'all')]
    print('Macro F1:\t', macro_f1)
    print('Micro F1:\t', micro_f1)


# From Jinny's code 
def evaluate_strict(goldlist, testlist, label_choice):
    """ Here, the named entities' spans, or tokens, in the gold and test file must strictly match to count as True Positive.
    The algorithm implemented here is that: First, the entities from the gold file will be put into dictionary (with their
    (start_index, end_index) tuple as the dict's key). Then the entities from the test file will be checked whether they
    find their matchs in the dictionary. """

    def same_label(e1_0, e2_0):
        if((e1_0 == e2_0) or ((e1_0 == 'organization') and (e2_0 == 'location') and (label_choice == 'LOC_to_ORG')) \
           or (label_choice == 'blind')):
            return True
        return False

    #print("number of real entities:",len(goldlist))
    #print("number of proposed entities:",len(testlist))
    confusion_dict = defaultdict(lambda: 0)
    gold_dict = { (start, end): label for (label, start, end, ent_text) in goldlist}
    for (test_label, start, end, ent_text) in testlist:
        if((start, end) in gold_dict):
            gold_label = gold_dict[(start, end)]
            if(same_label(gold_label, test_label)):
                confusion_dict[('true_pos', gold_label)] += 1
                gold_dict.pop((start, end))
            else:   # the model get the span right but the label wrong
                confusion_dict[('false_pos', test_label)] += 1
        else:
            confusion_dict[('false_pos', test_label)] += 1

    for (start, end) in gold_dict: # iterate over tbe spans in gold file that are not matched by those in test file
        gold_label = gold_dict[(start, end)]
        confusion_dict[('false_neg', gold_label)] += 1
    sum_over_labels(confusion_dict)
        
    return confusion_dict

