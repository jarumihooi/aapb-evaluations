import sys
import json
import csv
import os
import pandas as pd
import mmif
import pyannote.metrics
from mmif.vocabulary import AnnotationTypes, DocumentTypes
from pyannote.core import Segment, Timeline, Annotation
from moviepy.editor import VideoFileClip
from pyannote.metrics.detection import DetectionErrorRate
from urllib.parse import urlparse


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

#download the 'goldfile' from github
# In this time, we use 'https://github.com/clamsproject/aapb-annotations/blob/main/uploads/2022-slates/annotations/CLAMS_slate_annotation_metadata.csv#'
def get_csv(gold_url):
    df = pd.read_csv(gold_url)
    df.to_csv('goldfiles.csv', index=False)
    return 'goldfiles.csv'

#adapt the code from Kelley Lynch - 'evaluate_chyrons.py'
def load_gold_standard(file_name):
    gold_timeframes = {}
    with open(file_name, 'r') as gold_csv:
        reader = csv.DictReader(gold_csv)
        for row in reader:
            video_fileID = row["GUID"]
            Slate_Start =convert_time(row["Slate Start ,"])
            Slate_End = convert_time(row["Slate End   ,"])
            if video_fileID not in gold_timeframes:
                gold_timeframes[video_fileID] = Timeline()
            gold_timeframes[video_fileID].add(Segment(Slate_Start, Slate_End))
    return gold_timeframes

#give each mmif file an absolute path, return a list
def get_mmif(mmif_dir):
    mmif_files = os.listdir(mmif_dir)
    mmif_file_list = [os.path.join(mmif_dir, file) for file in mmif_files if file.endswith(".mmif")]
    return mmif_file_list

#adapt the code from Kelley Lynch - 'evaluate_chyrons.py'
def calculate_detection_metrics(gold_timeframes_dict, test_timeframes):
    metric = DetectionErrorRate()
    for file_ID in test_timeframes:
        reference = Annotation()
        for segment in gold_timeframes_dict[file_ID]:
            reference[segment] = "aapb"
        hypothesis = Annotation()
        for segment in test_timeframes[file_ID]:
            hypothesis[segment] = "aapb"
        try:
            results_dict = metric.compute_components(reference, hypothesis, collar=1.0,detailed=True)
            print (results_dict)
        except KeyError:
            print(f"Error: {file_ID} not in annotations")


if __name__ == "__main__":
    #get the fps from local video
    #input from keyboard: the absoulte path of local file
    directories=[]
    video_fps_dict={}
    if len(sys.argv) > 1:
        directories = sys.argv[1:]
    else:
        directories = []
    for directory in directories:
        filename = os.path.basename(directory)
        file_id = filename.split('.')[0]
        video_fps_dict[file_id]=get_video_fps(directory)

    # for the 'gold_timeframes'
    gold_url = 'https://raw.githubusercontent.com/clamsproject/aapb-annotations/main/uploads/2022-slates/annotations/CLAMS_slate_annotation_metadata.csv'
    file_name=get_csv(gold_url)
    gold_timeframes_dict=load_gold_standard(file_name)

    # for the 'test_timeframes'
    # I assume that all the mmif files are all locally saved in a folder locally, so type in the path of the folder here
    mmif_files_folderpath='/type/in/1your/path/here'
    mmif_files=get_mmif(mmif_files_folderpath)
    print(mmif_files)
    test_timeframes = {}
    for mmif_file in mmif_files:
        mmif_data = open(mmif_file).read()
        mmif_data=json.loads(mmif_data)
        document_location = mmif_data["documents"][0]["properties"]["location"]
        parsed_url = urlparse(document_location)
        filename = parsed_url.path.split("/")[-1]
        video_fileID = filename.split(".")[0]
        if video_fileID not in test_timeframes:
            test_timeframes[video_fileID] = Timeline()
        Slate_Start = round(float(mmif_data["views"][0]["annotations"][0]["properties"]["start"]) / video_fps_dict[video_fileID], 2)
        Slate_End = round(float(mmif_data["views"][0]["annotations"][0]["properties"]["end"]) / video_fps_dict[video_fileID], 2)
        test_timeframes[video_fileID].add(Segment(Slate_Start, Slate_End))

    #print result
    calculate_detection_metrics(gold_timeframes_dict, test_timeframes)

