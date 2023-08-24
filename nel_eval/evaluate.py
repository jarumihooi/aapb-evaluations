"""Named Entity Linking Evaluation

$ evaluate.py [-h] [-o [OUTPUT]] [test-dir] [gold-dir]

Evaluate .mmif files with named entity linking annotations produced as output
from the DBpedia Spotlight wrapper app. Compares system
generated data with the gold data found in the aapb-annotations
repository.

NOTE: gold annotation files and test output files that correspond
to the same AAPB catalog item must begin with the same GUID.
i.e. `gold-files/cpb-aacip-507-1v5bc3tf81.tsv` and `test-files/cpb-aacip-507-1v5bc3tf81-transcript.txt.dbps.mmif

"""

import argparse
from collections import defaultdict
import fnmatch
import json
from lapps.discriminators import Uri
from mmif.serialize import Mmif
import os
import pandas as pd
from typing import List, Union
from warnings import warn


class NamedEntityLink:
    def __init__(self, surface_form: str, uris: Union[List[str], str]) -> None:
        """
        Initializes NEL instance. Gold data provides the URI as a string, whereas system output MMIFs provide
        the URI(s) in a list format.
        :param surface_form: the text span corresponding to the entity.
        :param uris: the Wikidata URI(s) grounding the entity.
        """
        self.surface_form = surface_form
        if isinstance(uris, str):
            if uris != '':
                self.qid = uris.rsplit("/", 1)[1]
            else:
                self.qid = ''
        elif isinstance(uris, list):
            # multiple wikidata URIs
            if len(uris) > 1:
                self.qid = []
                for uri in uris:
                    self.qid.append(uri.rsplit("/", 1)[1])
            # single URI
            elif len(uris) == 1:
                self.qid = uris[0].rsplit("/", 1)[1]
            # in case URI is missing
            else:
                self.qid = ''
                warn("NEL object initialized without a QID")
        else:
            raise TypeError(f"Argument uris must be of type List[str] or str, not {type(uris)}")

    def __str__(self) -> str:
        """Returns a printable string representation of the NEL instance."""
        return f"{self.surface_form} (QID: {self.qid})"

    def __eq__(self, other) -> bool:
        """Returns True if another object is an NEL instance with the same surface form
        and QID as this one. Returns False otherwise."""
        if isinstance(other, NamedEntityLink):
            if isinstance(self.qid, str):
                if self.qid == other.qid and self.surface_form == other.surface_form:
                    return True
            elif isinstance(self.qid, list):
                if other.qid in self.qid and self.surface_form == other.surface_form:
                    return True
        return False

    def substring_match(self, other) -> bool:
        """Returns True if the surface form of this instance is a substring of the surface form
        of another NEL instance and both objects have the same QID."""
        if isinstance(other, NamedEntityLink):
            if isinstance(self.qid, str):
                if self.qid == other.qid and self.surface_form in other.surface_form:
                    return True
            elif isinstance(self.qid, list):
                if other.qid in self.qid and self.surface_form in other.surface_form:
                    return True
        return False


def match_files(test_dir, gold_dir) -> list:
    """Compare the files in the gold and test directories. Return pairs of matching files in a list.
    :param test_dir: Directory of test .mmif files
    :param gold_dir: Directory of gold .tsv files
    :return: list of tuples containing corresponding data file locations in (test, gold) format.
    """
    test_files, gold_files = os.listdir(test_dir), os.listdir(gold_dir)
    file_matches = []
    for gold_file in gold_files:
        pattern = gold_file[:24] + "*"
        for test_file in test_files:
            if fnmatch.fnmatch(test_file, pattern):
                gold_match = os.path.join(gold_dir, gold_file)
                test_match = os.path.join(test_dir, test_file)
                file_matches.append((test_match, gold_match))
                test_files.remove(test_file)
                break

    return file_matches


def filter_common_entities(test_mmif, gold_tsv) -> (list, list):
    """Return lists of the common NEL instances between system-generated mmif and gold data."""
    test_entities, gold_entities = file_to_ne(test_mmif), file_to_ne(gold_tsv)
    # remove gold NEL instances whose QIDs are empty strings
    gold_entities = [gold_ent for gold_ent in gold_entities if gold_ent.qid != '']
    # remove test NEL instances whose surface forms do not overlap with the gold NEL instances
    gold_surface_forms = [gold_ent.surface_form for gold_ent in gold_entities]
    test_entities = [test_ent for test_ent in test_entities
                     if any(test_ent.surface_form in g for g in gold_surface_forms)]

    return test_entities, gold_entities


def file_to_ne(file_path: str) -> list:
    """Checks whether the file is in .mmif or .tsv format and calls the appropriate function
    to get a list of NEL objects"""
    if file_path.endswith('.mmif'):
        return mmif_to_ne(file_path)
    elif file_path.endswith('.tsv'):
        return tsv_to_ne(file_path)
    else:
        raise Exception("Unsupported file type.")


def mmif_to_ne(mmif_path) -> list:
    """Fetch named entities from the input mmif.
    Returns a list of NEL objects.
    """
    with open(mmif_path) as fh_in:
        mmif_serialized = fh_in.read()
    mmif = Mmif(mmif_serialized)
    ne_views = mmif.get_all_views_contain(at_types=Uri.NE)
    view = ne_views[-1]  # read only the first view (from last) with Uri.NE
    annotations = view.get_annotations(at_type=Uri.NE)
    ne_list = []
    for anno in annotations:
        entity = anno.properties
        ne = NamedEntityLink(entity['text'], entity['grounding'][1:])
        ne_list.append(ne)

    return ne_list


def tsv_to_ne(gold_tsv_path) -> list:
    """Fetch named entities from the input tsv.
    Returns a list of NEL objects."""
    with open(gold_tsv_path) as fh_in:
        annotations_df = pd.read_csv(fh_in, sep='\t', encoding='utf-16')
        annotations_df.fillna('', inplace=True)
    ne_list = [NamedEntityLink(ent, qid) for ent, qid in zip(annotations_df['entity'], annotations_df['QID'])]

    return ne_list


def evaluate(test_dir, gold_dir):
    results = defaultdict(dict)
    file_matches = match_files(test_dir, gold_dir)
    for test_file, gold_file in file_matches:
        print(f'>>> Evaluating {os.path.basename(test_file)}')
        guid = os.path.basename(test_file)[:24]

        # calculate proportion of gold and test data actually used
        unfiltered_test, unfiltered_gold = file_to_ne(test_file), file_to_ne(gold_file)
        test_entities, gold_entities = filter_common_entities(test_file, gold_file)
        used_gold = len(gold_entities) / len(unfiltered_gold)
        used_test = len(test_entities) / len(unfiltered_test)
        results[guid]['Gold Entities'] = {"count": len(gold_entities),
                                          "proportion of total": "{:.2f}".format(used_gold)}
        results[guid]['Test Entities'] = {"count": len(test_entities),
                                          "proportion of total": "{:.2f}".format(used_test)}

        # calculate accuracy
        hits = 0
        misses = 0
        while test_entities:
            test_ent = test_entities.pop(0)
            found_match = False
            for gold_ent in gold_entities:
                if test_ent == gold_ent or test_ent.substring_match(gold_ent):
                    hits += 1
                    found_match = True
                    gold_entities.remove(gold_ent)
                    break
            if not found_match:
                misses += 1
        acc = hits / (hits + misses)

        results[guid]['Accuracy'] = "{:.2f}".format(acc)
        print('... done')

    return results


def write_results(data: dict, result_path: str):
    """Write evaluation results to txt file."""
    with open(result_path, 'w') as fh_out:
        json.dump(data, fh_out, indent=4, sort_keys=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description='Evaluate accuracy of NEL mmif files against gold labeled data.')
    ap.add_argument('test_directory', metavar='test-dir', nargs='?',
                    help='directory containing test data in .mmif format.')
    ap.add_argument('gold_directory', metavar='gold-dir', nargs='?',
                    help='directory containing gold data in .tsv format.')
    ap.add_argument('-o', '--output', nargs='?', help='path to print out eval result.', default='results.txt')
    args = ap.parse_args()

    data = evaluate(args.test_directory, args.gold_directory)
    write_results(data, args.output)
