import sys
import json
import csv
import os
import pandas as pd
import mmif
import argparse
import glob
from pyannote.core import Segment, Timeline, Annotation
from pyannote.metrics.detection import DetectionErrorRate
from mmif import Mmif, DocumentTypes, AnnotationTypes
from moviepy.editor import VideoFileClip
import pathlib
import math


########## small tools

#convert time from string in csv to the pyannote-style time format
def convert_time(time_str):
    parts = str(time_str).replace(';', ':').replace(',', '').split(':')
    if len(parts)==4:
        microsecond=int(parts[3].strip())
        seconds = int(parts[2].strip())
        minutes = int(parts[1].strip())
        hours = int(parts[0].strip())
        total_seconds = hours * 3600 + minutes * 60 + seconds+microsecond*0.01
        return total_seconds
    elif len(parts)==3:
        seconds = float(parts[2].strip())
        minutes = int(parts[1].strip())
        hours = int(parts[0].strip())
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    else:
        return 0

#get fps info from a video file
def get_video_fps(url):
    video = VideoFileClip(url)
    fps = video.fps
    return fps

##########

#read the video file, turn that into a dict looks like: {file_id: fps; ...}
def video_to_fps_dict(mp4_files):
    video_fps_dict = {}
    for directory in mp4_files:
        filename = os.path.basename(directory)
        file_id = filename.split('.')[0]
        video_fps_dict[file_id]=get_video_fps(directory)
    return video_fps_dict

#download the 'goldfile' from github
def get_csv(gold_url):
    df = pd.read_csv(gold_url)
    df.to_csv('goldfiles.csv', index=False)
    return 'goldfiles.csv'

#adapt the code from Kelley Lynch - 'evaluate_chyrons.py'
def load_gold_standard(file_name, test_dir):
    gold_timeframes = {}
    with open(file_name, 'r') as gold_csv:
        reader = csv.DictReader(gold_csv)
        for row in reader:
            video_fileID = row["GUID"]
            Slate_Start = convert_time(row["Slate Start ,"])
            Slate_End = convert_time(row["Slate End   ,"])
            if video_fileID not in gold_timeframes:
                gold_timeframes[video_fileID] = Timeline()
            if video_fileID in [filename.split(".")[0] for filename in os.listdir(test_dir)]:
                gold_timeframes[video_fileID].add(Segment(Slate_Start, Slate_End))
    return gold_timeframes

#give each mmif file an absolute path, return a list
def get_mmif(mmif_dir):
    mmif_files = os.listdir(mmif_dir)
    mmif_file_list = [os.path.join(mmif_dir, file) for file in mmif_files if file.endswith(".mmif")]
    return mmif_file_list

#get info from mmif files
def process_mmif_file(mmif_file_path):
    mmif_files = get_mmif(mmif_file_path)
    test_timeframes = {}
    for mmif_file in mmif_files:
        mmif = Mmif(open(mmif_file).read())
        document_location = mmif.get_documents_by_type(DocumentTypes.VideoDocument)[0].location
        filename = os.path.basename(document_location)
        video_fileID = filename.split(".")[0]
        if video_fileID not in test_timeframes:
            test_timeframes[video_fileID] = Timeline()
        #get the slate start and end time
        try:
            Slate_Start = float(next(mmif.get_view_contains(AnnotationTypes.TimeFrame).get_annotations(AnnotationTypes.TimeFrame)).properties["start"])
            Slate_End = float(next(mmif.get_view_contains(AnnotationTypes.TimeFrame).get_annotations(AnnotationTypes.TimeFrame)).properties["end"])
        #check if it's been annotated based on the next version of the slate app
        except:
            continue
        result = mmif.get_all_views_contain(at_types=AnnotationTypes.TimeFrame)
        view = result[-1]
        annotations = view.get_annotations(at_type=AnnotationTypes.Annotation)
        annotations = list(annotations)
        ##if it's not annotated, actually read the video, aka the fps_dict just created
        fps = 29.97
        ##if it's annotated, use the existing 'fps'
        if len(annotations) > 0:
            for annotation in annotations:
                entity = annotation.properties
                if 'fps' in entity:
                    fps=float(entity['fps'])
        # get the test_timeframes dict
        calculated_Slate_Start = round(Slate_Start/fps, 2)
        calculated_Slate_End = round(Slate_End/fps, 2)
        test_timeframes[video_fileID].add(Segment(calculated_Slate_Start , calculated_Slate_End))
    return test_timeframes

#adapt the code from Kelley Lynch - 'evaluate_chyrons.py'
#add the situation which the mmif file is not in the gold timeframes
def calculate_detection_metrics(gold_timeframes_dict, test_timeframes):
    metric = DetectionErrorRate()
    for file_ID in test_timeframes:
        reference = Annotation()
        try:
            for segment in gold_timeframes_dict[file_ID]:
                reference[segment] = "aapb"
            hypothesis = Annotation()
            for segment in test_timeframes[file_ID]:
                hypothesis[segment] = "aapb"
        except KeyError:
            print(f"Error: {file_ID} not in the gold timeframes")
            continue
        try:
            results_dict = metric.compute_components(reference, hypothesis, collar=1.0,detailed=True)
            print (results_dict)
        except KeyError:
            print(f"Error: {file_ID} not in annotations")


def generate_side_by_side(golddir, testdir, outdir):
    for guid in golddir:
        path = outdir / f"{guid}.sbs.csv"
        gold_time_chunks = []
        test_time_chunks = []
        for segment in golddir[guid]:
            gold_start = math.floor(segment.start)
            gold_end = math.floor(segment.end)
            gold_time_chunks.extend(range(gold_start, gold_end))
        if guid in testdir:
            for segment in testdir[guid]:
                test_start = math.floor(segment.start)
                test_end = math.ceil(segment.end)
                test_time_chunks.extend(range(test_start, test_end))
        if len(gold_time_chunks) > 0 and len(test_time_chunks) > 0:
            maximum = max(max(gold_time_chunks), max(test_time_chunks))
        elif len(gold_time_chunks) > 0:
            maximum = max(gold_time_chunks)
        elif len(test_time_chunks) > 0:
            maximum = max(test_time_chunks)
        else:
            continue
        with open(path, "w") as out_f:
            i = 0
            while i < maximum:
                interval = (i, i+1)
                if i in gold_time_chunks:
                    gold = 1
                else:
                    gold = 0
                if i in test_time_chunks:
                    test = 1
                else:
                    test = 0
                out_f.write(",".join([str(interval), str(gold), str(test)]))
                out_f.write("\n")
                i += 1


if __name__ == "__main__":
    #get the absolute path of video-file-dir and hypothesis-file-dir
    parser = argparse.ArgumentParser(description='Process some directories.')
    parser.add_argument('-m', '--machine_dir', type=str, required=True,
                        help='directory containing machine annotated files')
    parser.add_argument('-o', '--output_dir', help='directory to publish side-by-side results', default=None)
    parser.add_argument('-g', '--gold_url', help='url to csv that contains the gold annotations', default = 'https://raw.githubusercontent.com/clamsproject/aapb-annotations/main/january-slates/230101-aapb-collaboration-7/CLAMS_slate_annotation_metadata.csv')
    args = parser.parse_args()
    if args.output_dir:
        outdir = pathlib.Path(args.output_dir)
    else:
        outdir = pathlib.Path(__file__).parent

    # create the 'gold_timeframes'

    gold_timeframes_dict=load_gold_standard(get_csv(args.gold_url), args.machine_dir)

    # create the 'test_timeframes'
    test_timeframes=process_mmif_file(args.machine_dir)

    #final calculation
    calculate_detection_metrics(gold_timeframes_dict, test_timeframes)
    generate_side_by_side(gold_timeframes_dict, test_timeframes, outdir)
