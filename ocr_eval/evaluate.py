# Import Statements
import argparse
from collections import defaultdict
import csv
import json
import os
import pathlib
from typing import Sequence, Dict, Union, Tuple

import mmif
from mmif.utils import video_document_helper as vdh
from mmif import Mmif, AnnotationTypes, DocumentTypes
import pandas as pd
from torchmetrics.text import CharErrorRate
import goldretriever

# Constants ==|
GOLD_URL = 'https://raw.githubusercontent.com/clamsproject/aapb-annotations/80a36781fd55b5b8cb74f2de187be026f1ecbb7f/newshour-chyron/golds/batch2/2022-jul-chyron.csv'

# File Loaders ==|
def get_csv(out_dir, gold_url: str) -> Sequence[str]:
    """Convert a gold URL into a directory of individual csv files"""
    out = []
    df = pd.read_csv(gold_url)
    df = df.sort_values(by='video_filename')
    groups = df.groupby('video_filename')

    for video_file in groups.groups:
        file_annotations = groups.get_group(video_file)
        file_annotations = file_annotations.iloc[:,1:]
        file_annotations.to_csv(f"{os.path.join(out_dir, video_file[:-4])}.csv", index=False)
        out.append(video_file[:-4])
    return out

def get_mmif(mmif_dir: Union[str, os.PathLike]) -> Sequence[str]:
    """Retrieve pathnames for all hypothesis mmifs"""
    mmif_files = os.listdir(mmif_dir)
    return [os.path.join(mmif_dir, file) for file in mmif_files if file.endswith(".mmif")]

# Gold Data
def load_gold_file(csvfile:Union[str, os.PathLike]) -> Dict[Tuple[float, float], str]:
    """Loads the OCR data of a single gold file"""
    gold_annotations = {}
    with open(csvfile, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            start, end, text = row
            text = text.strip().lower()
            gold_annotations.update({(start, end):text})
    return gold_annotations

def load_gold_data(csvdir: Union[str, os.PathLike])-> Dict[str, Dict[Tuple[float, float],str]]:
    """Loads OCR data from the gold directory"""
    return {os.path.basename(filename)[:-4] : load_gold_file(os.path.join(csvdir, filename)) for filename in os.listdir(csvdir)}

# Test Data
def process_mmifs(mmif_files: Union[str, os.PathLike]) -> Dict[str, Dict[float, str]]:
    """Load in hypothesis mmifs and retrieve annotations"""
    ocr_annotations = defaultdict(dict)
    for mmif in mmif_files:
        mmif_obj = Mmif(open(mmif).read())
        video_filename = mmif_obj.get_documents_by_type(DocumentTypes.VideoDocument)[0].location
        video_filename = os.path.basename(video_filename)
        if video_filename not in ocr_annotations:
            ocr_annotations[video_filename[:-6]] = {}
        ocr_view = mmif_obj.get_view_contains(AnnotationTypes.Alignment)
        bounding_box_views = mmif_obj.get_view_contains(AnnotationTypes.BoundingBox)
        if ocr_view is not None:
            anno_id_to_annotation = {annotation.id : annotation
                                     for annotation in ocr_view.annotations}
        if bounding_box_views is not None:
            anno_id_to_annotation.update({annotation.id : annotation
                                          for annotation in bounding_box_views.annotations})
        if ocr_view is not None:
            for annotation in ocr_view.annotations:
                if annotation.at_type == AnnotationTypes.Alignment:
                    source_id = annotation.properties['source']
                    target_id = annotation.properties['target']
                    vid_anno, bbox_anno = source_id.split(":")
                    source_anno = anno_id_to_annotation[bbox_anno]
                    target_anno = anno_id_to_annotation[target_id]
                    #fps = vdh.get_annotation_property(mmif_obj,, 'fps')
                    fps = 29.97
                    time_point = vdh.convert(source_anno.properties['timePoint'], 'frames', 'seconds', fps)
                    time_text = target_anno.properties['text'].value
                    time_text = time_text.strip().lower()
                    ocr_annotations[video_filename[:-6]].update({time_point:time_text})
    return ocr_annotations

# CER Calculation
def compare_gold_with_test(gold_doc: Dict[tuple, str], test_doc: Dict[float, str]) -> Dict[float,Dict[str,Union[str,float]]]:
    vals = {}
    doc_level_cer = CharErrorRate()
    for timepoint, text in test_doc.items():
        for timespan, gold_text in gold_doc.items():
            start = float(timespan[0])
            end = float(timespan[1])
            if start <= timepoint and end > timepoint:
                vals[timepoint] = {'gold_text': gold_text,
                                   'test_text': text,
                                   'cer': doc_level_cer(text, gold_text).item()}
    return vals

def calculate_results(gold_data: Dict[str, Dict[tuple, str]], test_data:Dict[str, Dict[float, str]], outdir: Union[str, os.PathLike]) -> None:
    output = {}
    for filename, annotations in test_data.items():
        if filename in gold_data:
            results = compare_gold_with_test(gold_data[filename], annotations)
            output[filename] = results
            file_json = json.dumps(results,indent=2)
            with open(f'./{outdir}/{filename}.json', 'w') as b:
                b.write(file_json)

# Main Block
if __name__ == "__main__":
    APPNAME = "tesseractocr-wrapper" #default app
    APPVERSION = 1.0                 #default version 

    parser = argparse.ArgumentParser(description="compare the results of CLAMS OCR apps to a gold standard")
    parser.add_argument('-t', '--test-dir',
                        type=str,
                        default=None,
                        help="Directory of non-gold/hypothesis mmif files")
    parser.add_argument('-g', '--gold-dir',
                        type=str,
                        default=None,
                        help="Directory of gold annotations")
    parser.add_argument('-o', '--output-dir',
                        type=str,
                        default=None,
                        help="Directory to store results")
    args = parser.parse_args()

    # Gold Dir
    if args.gold_dir is None:
        args.gold_dir = goldretriever.download_golds(GOLD_URL,  'golds')

    # Test Dir
    if args.test_dir is None:
        args.test_dir = f"preds@{APPNAME}{APPVERSION}@batch2"

    # Out Dir
    if args.output_dir:
        outdir = pathlib.Path(args.output_dir)
    else:
        outdir = pathlib.Path(f"results@{APPNAME}{APPVERSION}@batch2")
    if not outdir.exists():
        outdir.mkdir()
        
    # Main
    gold_data = load_gold_data(args.gold_dir)
    test_data = process_mmifs(get_mmif(args.test_dir))
    results = calculate_results(gold_data, test_data, outdir)
