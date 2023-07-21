"""Named Entity Linking Evaluation

$ evaluate.py [-h] [-o [OUTPUT]] [test-dir] [gold-dir]

Evaluate .mmif files with named entity linking annotations produced as output
from the DBpedia Spotlight wrapper app. Compares system
generated data with the gold data found in the aapb-annotations
repository.

NOTE: gold annotation files and test output files that correspond
to the same aapb catalog item must share the same file name (with the exception of file extension).
i.e. `gold-files/cpb-aacip-507-1v5bc3tf81.tsv` and `test-files/cpb-aacip-507-1v5bc3tf81.mmif`

"""

import argparse
from collections import defaultdict
import fnmatch
import json
from lapps.discriminators import Uri
from mmif.serialize import Mmif
import os
import pandas as pd


def match_files(test_dir, gold_dir):
    """Compare the files in the gold and test directories. Return pairs of matching files in a list.
    :param test_dir: Directory of test .mmif files
    :param gold_dir: Directory of gold .tsv files
    :return: list of tuples containing corresponding data file locations in (test, gold) format.
    """
    test_files, gold_files = os.listdir(test_dir), os.listdir(gold_dir)
    file_matches = []
    for gold_file in gold_files:
        pattern = gold_file.rsplit(sep='.', maxsplit=1)[0]
        for test_file in test_files:
            if fnmatch.fnmatch(test_file, '{}.mmif'.format(pattern)):
                gold_match = os.path.join(gold_dir, gold_file)
                test_match = os.path.join(test_dir, test_file)
                file_matches.append((test_match, gold_match))
                test_files.remove(test_file)
                gold_files.remove(gold_file)
                continue

    return file_matches


def filter_common_entities(test_mmif, gold_tsv) -> (dict, dict):
    """Return dictionaries of the common named entities between system-generated mmif and gold data."""
    test_entities, gold_entities = file_to_ne(test_mmif), file_to_ne(gold_tsv)
    # remove gold entity keys whose values are empty strings
    gold_entities = {entity: gold_entities[entity] for entity in gold_entities if gold_entities[entity]}
    # remove test entity keys not present in gold entity dict
    test_entities = {entity: test_entities[entity] for entity in test_entities if entity in gold_entities}

    return test_entities, gold_entities


def file_to_ne(file_path: str) -> dict:
    """Checks whether the file is in .mmif or .tsv format and calls the appropriate function
    to get a dictionary of named entities and URIs."""
    if file_path.endswith('.mmif'):
        return mmif_to_ne(file_path)
    elif file_path.endswith('.tsv'):
        return tsv_to_ne(file_path)
    else:
        raise Exception("Unsupported file type.")


def mmif_to_ne(mmif_path) -> dict:
    """Fetch named entities from the input mmif.
    Returns a dictionary, where the keys are the entities and their values are the grounding.
    """
    with open(mmif_path) as fh_in:
        mmif_serialized = fh_in.read()
    mmif = Mmif(mmif_serialized)
    ne_views = mmif.get_all_views_contain(at_types=Uri.NE)
    view = ne_views[-1]  # read only the first view (from last) with Uri.NE
    annotations = view.get_annotations(at_type=Uri.NE)
    ne_dict = {}
    for anno in annotations:
        entity = anno.properties
        ne_dict[entity['text']] = entity['grounding'][1]

    return ne_dict


def tsv_to_ne(gold_tsv_path):
    """Fetch named entities from the input tsv.
    Returns a dictionary, where the keys are the entities and their values are the grounding."""
    with open(gold_tsv_path) as fh_in:
        annotations_df = pd.read_csv(fh_in, sep='\t', encoding='utf-16')
        annotations_df.fillna('', inplace=True)
    ne_dict = dict(zip(annotations_df['entity'], annotations_df['QID']))

    return ne_dict


def evaluate(test_dir, gold_dir):
    results = defaultdict(dict)
    file_matches = match_files(test_dir, gold_dir)
    for test_file, gold_file in file_matches:
        guid = os.path.basename(test_file).rstrip('.mmif')

        # calculate proportion of gold and test data actually used
        unfiltered_test, unfiltered_gold = file_to_ne(test_file), file_to_ne(gold_file)
        test_entities, gold_entities = filter_common_entities(test_file, gold_file)
        used_gold = len(gold_entities) / len(unfiltered_gold)
        used_test = len(test_entities) / len(unfiltered_test)

        # calculate accuracy
        hits = 0
        misses = 0
        for ent in test_entities:
            # compares by QID only
            if test_entities[ent].rsplit("/", 1)[1] == gold_entities[ent].rsplit("/", 1)[1]:
                hits += 1
            else:
                misses += 1
        acc = hits / (hits + misses)

        results[guid]['Accuracy'] = "{:.2f}".format(acc)
        results[guid]['Gold Entities'] = {"count": len(gold_entities),
                                          "proportion of total": "{:.2f}".format(used_gold)}
        results[guid]['Test Entities'] = {"count": len(test_entities),
                                          "proportion of total": "{:.2f}".format(used_test)}

    return results


def write_results(data: dict, result_path: str):
    """Write evaluation results to txt file."""
    with open(result_path, 'w') as fh_out:
        json.dump(data, fh_out, indent=4)


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument('test_directory', metavar='test-dir', nargs='?',
                    help='directory containing test data in .mmif format.')
    ap.add_argument('gold_directory', metavar='gold-dir', nargs='?',
                    help='directory containing gold data in .tsv format.')
    ap.add_argument('-o', '--output', nargs='?', help='path to print out eval result.', default='results.txt')
    args = ap.parse_args()

    data = evaluate(args.test_directory, args.gold_directory)
    write_results(data, args.output)
