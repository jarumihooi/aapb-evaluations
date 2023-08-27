import argparse
import csv
import json
import os
import pathlib
from collections import defaultdict
from typing import Dict, Union, Tuple, Iterable

from mmif import Mmif, AnnotationTypes, DocumentTypes
from mmif.utils import video_document_helper as vdh
from torchmetrics.text import CharErrorRate

import goldretriever

# Constants ==|
GOLD_URL = 'https://github.com/clamsproject/aapb-annotations/tree/f96f857ef83acf85f64d9a10ac8fe919e06ce51e/newshour-chyron/golds/batch2'


def filename_to_guid(filename) -> str:
    return pathlib.Path(filename).stem


def load_reference(ref_fname) -> Dict[Tuple[float, float], str]:
    gold_annotations = {}
    with open(ref_fname, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            start, end, text = row
            text = text.strip().lower()
            gold_annotations.update({(start, end): text})
    return gold_annotations


def load_references(ref_dir: Union[str, pathlib.Path]) -> Dict[str, Dict[Tuple[float, float], str]]:
    """
    Loads OCR data from the gold directory, 
    text transcripts are keyed by guid, then by (start, end) tuple ,
    where start and end are in seconds (floats)
    """
    ref_dir = pathlib.Path(ref_dir)
    refs = {}
    for ref_src_fname in ref_dir.glob("*.?sv"):
        guid = filename_to_guid(ref_src_fname)
        refs[guid] = load_reference(ref_src_fname)
    return refs


def load_hypotheses(mmif_files: Iterable[pathlib.Path]) -> Dict[str, Dict[float, str]]:
    """
    Load in hypothesis mmifs and retrieve annotations,
    text transcripts are keyed by guid, then by timepoint (float)
    the unit of the timepoints is seconds (converted if necessary, assuming 29.97 fps)
    """
    ocr_annotations = defaultdict(dict)
    for mmif_file in mmif_files:
        guid = filename_to_guid(mmif_file)
        mmif = Mmif(open(mmif_file).read())
        vd = mmif.get_documents_by_type(DocumentTypes.VideoDocument)[0]
        try:
            fps = vd.get('fps')
        except KeyError:
            # meaning there were no video document or no file found for the VD
            continue
        ocr_view = mmif.get_view_contains(AnnotationTypes.Alignment)
        bb_view = mmif.get_view_contains(AnnotationTypes.BoundingBox)
        if ocr_view is not None:
            anno_id_to_annotation = {annotation.id: annotation
                                     for annotation in ocr_view.annotations}
        if bb_view is not None:
            anno_id_to_annotation.update({annotation.id: annotation
                                          for annotation in bb_view.annotations})
        if ocr_view is not None:
            for annotation in ocr_view.annotations:
                if annotation.at_type == AnnotationTypes.Alignment:
                    source_id = annotation.properties['source']
                    target_id = annotation.properties['target']
                    vid_anno, bbox_anno = source_id.split(":")
                    source_anno = anno_id_to_annotation[bbox_anno]
                    target_anno = anno_id_to_annotation[target_id]
                    time_point = vdh.convert(source_anno.properties['timePoint'], 'frames', 'seconds', fps)
                    time_text = target_anno.properties['text'].value
                    time_text = time_text.strip().lower()
                    ocr_annotations[guid].update({time_point: time_text})
    return ocr_annotations


# CER Calculation
def compare_gold_with_test(gold_doc: Dict[tuple, str], test_doc: Dict[float, str]) \
        -> Dict[float, Dict[str, Union[str, float]]]:
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


def evaluate(gold_data: Dict[str, Dict[tuple, str]], test_data: Dict[str, Dict[float, str]],
             outdir: Union[str, os.PathLike]) -> None:
    output = {}
    for filename, annotations in test_data.items():
        if filename in gold_data:
            results = compare_gold_with_test(gold_data[filename], annotations)
            output[filename] = results
            file_json = json.dumps(results, indent=2)
            with open(f'./{outdir}/{filename}.json', 'w') as b:
                b.write(file_json)


# Main Block
if __name__ == "__main__":
    APPNAME = "parseqocr-wrapper"  # default app
    APPVERSION = 1.0  # default version 

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

    ref_dir = goldretriever.download_golds(GOLD_URL) if args.gold_dir is None else args.gold_dir
    hyp_dir = f"preds@{APPNAME}{APPVERSION}@batch2" if args.test_dir is None else args.test_dir
    out_dir = pathlib.Path(args.output_dir) if args.output_dir else pathlib.Path(f"results@{APPNAME}{APPVERSION}@batch2")
    if not out_dir.exists():
        out_dir.mkdir()

    references = load_references(pathlib.Path(ref_dir))
    hypotheses = load_hypotheses(pathlib.Path(hyp_dir).glob("*.mmif"))
    evaluate(references, hypotheses, out_dir)
