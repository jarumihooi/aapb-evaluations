import os
from mmif.serialize import Mmif
from mmif.vocabulary import AnnotationTypes, DocumentTypes
from lapps.discriminators import Uri
from pyannote.core import Segment, Timeline, Annotation
from pyannote.metrics.detection import DetectionErrorRate, DetectionPrecisionRecallFMeasure
import re
import argparse
import pysrt
import pandas as pd

#Yao: If the mmif file ends with .spacy.mmif, then you need to change the code. e.g. it should be 'file.endswith(".spacy.mmif")' instead of 'file.endswith(".mmif")'

########## small tools ##########
def time_to_ms(time_str):
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)

########## small tools end ##########

def get_srt_list(srt_dir):
    srt_files = os.listdir(srt_dir)
    return [os.path.join(srt_dir, file) for file in srt_files if file.endswith(".srt")]

def process_srt(srt_file_list):
    gold_timeframes = {}
    for srt_file in srt_file_list:
        gold_timeframes[os.path.splitext(os.path.basename(srt_file))[0]] = Timeline()
        subs = pysrt.open(srt_file)
        for sub in subs:
            gold_timeframes[os.path.splitext(os.path.basename(srt_file))[0]].add(Segment(time_to_ms(str(sub.start)), time_to_ms(str(sub.end))))
    return gold_timeframes

def get_mmif_list(mmif_dir):
    mmif_files = os.listdir(mmif_dir)
    return [os.path.join(mmif_dir, file) for file in mmif_files if file.endswith(".mmif")]

def process_mmif(mmif_file_list):
    test_timeframes = {}
    for mmif_file in mmif_file_list:
        with open(mmif_file, 'r') as file:
            mmif = Mmif(file.read())
            ann = mmif.get_view_contains(AnnotationTypes.TimeFrame).get_annotations(AnnotationTypes.TimeFrame)
            test_timeframes[os.path.splitext(os.path.basename(mmif_file))[0]] = Timeline()
            starts,ends = [],[]
            for cur in ann:
                try:
                    starts.append(float(cur.properties["start"]))
                    ends.append(float(cur.properties["end"]))
                except StopIteration:  # Use specific exception
                    break
            for start, end in zip(starts, ends):
                test_timeframes[os.path.splitext(os.path.basename(mmif_file))[0]].add(Segment(start, end))
    return test_timeframes


def calculate_detection_metrics(gold_timeframes, test_timeframes, result_path):
    metric = DetectionErrorRate()
    final = DetectionPrecisionRecallFMeasure()
    data = pd.DataFrame(columns=['GUID', 'FN seconds', 'FP seconds', 'Total true seconds','Detection Error Rate'])
    TP, FP, FN = 0, 0, 0
    for file_ID in test_timeframes:
        if file_ID not in gold_timeframes:
            print(f"Warning: {file_ID} not found in gold annotations.")
            continue
        reference = Annotation()
        for segment in gold_timeframes[file_ID]:
            reference[segment] = "fa_eval"
        hypothesis = Annotation()
        for segment in test_timeframes[file_ID]:
            hypothesis[segment] = "fa_eval"
        try:
            results_dict = metric.compute_components(reference, hypothesis, collar=1.0, detailed=True)
            average = final.compute_components(reference, hypothesis, collar=1.0, detailed=True)
            true_positive = average.get('relevant retrieved', 0.0)
            false_negative = average.get('relevant', 0.0) - true_positive
            false_positive = average.get('retrieved', 0.0) - true_positive
            TP += true_positive
            FP += false_positive
            FN += false_negative
            file_precision = true_positive / (
                        true_positive + false_positive) if true_positive + false_positive > 0 else 0.0
            file_recall = true_positive / (
                        true_positive + false_negative) if true_positive + false_negative > 0 else 0.0
            file_f1 = (2 * file_precision * file_recall) / (
                        file_precision + file_recall) if file_precision + file_recall > 0 else 0.0
            data_row = {
                'GUID': file_ID,
                'FN seconds': results_dict['miss'],
                'FP seconds': results_dict['false alarm'],
                'Total true seconds': results_dict['total'],
                'Detection Error Rate': (results_dict['miss']+results_dict['false alarm'])/results_dict['total'],
            }
            data = pd.concat([data, pd.DataFrame([data_row])], ignore_index=True)
        except KeyError:
            print(f"Error: Issue with keys in results for file {file_ID}")
    overall_precision = TP / (TP + FP) if TP + FP > 0 else 0.0
    overall_recall = TP / (TP + FN) if TP + FN > 0 else 0.0
    overall_f1 = (2 * overall_precision * overall_recall) / (
                overall_precision + overall_recall) if overall_precision + overall_recall > 0 else 0.0
    s = f'Total Precision = {overall_precision}\t Total Recall = {overall_recall}\t Total F1 = {overall_f1}\n\n\nIndividual file results:\n{data.to_string()}'
    with open(result_path, 'w') as fh_out:
        fh_out.write(s)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some directories.')
    parser.add_argument('-m', '--machine_dir', help='directory containing machine annotated files', default=None)
    parser.add_argument('-o', '--gold_dir', help='directory containing human annotated files', default=None)
    parser.add_argument('-r', '--result_file', help='file to store evaluation results', default='results.txt')
    args = parser.parse_args()
    gold_timeframes = process_srt(get_srt_list(args.gold_dir))
    test_timeframes = process_mmif(get_mmif_list(args.machine_dir))
    calculate_detection_metrics(gold_timeframes, test_timeframes, args.result_file)

