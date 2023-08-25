import argparse
import os

import pandas as pd
import goldretriever
from mmif.serialize import Mmif
from mmif.vocabulary import AnnotationTypes
from pyannote.core import Segment, Timeline, Annotation
from pyannote.metrics.detection import DetectionErrorRate, DetectionPrecisionRecallFMeasure


#Yao: If the mmif file ends with .spacy.mmif, then you need to change the code. e.g. it should be 'file.endswith(".spacy.mmif")' instead of 'file.endswith(".mmif")'

########## small tools ##########
def time_to_ms(time_str):
    try:
        h, m, s = time_str.split(':')
        s, ms = s.split('.')
        return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)
    except ValueError:
        raise ValueError("Invalid time format. Expected format: hh:mm:ss.mmm")

########## small tools end ##########

def get_tsv_list(tsv_dir):
    srt_files = os.listdir(tsv_dir)
    return [os.path.join(tsv_dir, file) for file in srt_files if file.endswith(".tsv")]

def process_tsv(tsv_file_list):
    gold_timeframes = {}
    for tsv_file in tsv_file_list:
        gold_timeframes[os.path.splitext(os.path.basename(tsv_file))[0]] = Timeline()
        df = pd.read_csv(tsv_file, sep='\t')
        for index, row in df[['starts', 'ends']].iterrows():
            gold_timeframes[os.path.splitext(os.path.basename(tsv_file))[0]].add(Segment(time_to_ms(row['starts']), time_to_ms(row['ends'])))
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
                except StopIteration:
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
    if args.gold_dir is None:
        args.gold_dir = goldretriever.download_golds('https://github.com/clamsproject/aapb-annotations/tree/f884e10d0b9d4b1d68e294d83c6e838528d2c249/newshour-transcript-sync/golds/aapb-collaboration-21')
    gold_timeframes = process_tsv(get_tsv_list(args.gold_dir))
    test_timeframes = process_mmif(get_mmif_list(args.machine_dir))
    calculate_detection_metrics(gold_timeframes, test_timeframes, args.result_file)

