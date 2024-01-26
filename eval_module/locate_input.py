import argparse
import goldretriever
from pathlib import Path

def dummy_read_golds(gold_dir):
    print(gold_dir)
    return gold_dir


def dummy_read_preds_mmifs(preds_dir, gold_entries):
    print(f"{preds_dir=}", f"{gold_entries}")
    return preds_dir

def locate(args, APPNAME, APPVERSION, GOLDS_DIR):
    # sets the folder names/paths correctly, modify GOLDS_DIR for the correct link to the eval needed.
    golds_dir = goldretriever.download_golds(GOLDS_DIR) if args.golds_dir is None else args.golds_dir
    preds_dir = f"preds@{APPNAME}{APPVERSION}@batch2" if args.preds_dir is None else args.preds_dir
    # out_dir = Path(args.output_dir) if args.output_dir else Path(f"results@{APPNAME}{APPVERSION}@batch2") # Add this line if an output dir is needed for results.
    out_dir = None
    if out_dir is not None and not out_dir.exists():
        out_dir.mkdir()

    golds_entries = dummy_read_golds(Path(golds_dir).glob("*.tsv"))
    preds_entries = dummy_read_preds_mmifs(Path(preds_dir).glob("*.mmif"),
                                           golds_entries)  # uses gold_entries to get GUIDS to get matching preds?

    return golds_dir, preds_dir, out_dir

def get_guid_matches():
    '''Goal is to get the matches-list, and generate warnings/errors/output for unmatched-list. '''
    # TODO: Progress here, continue to determine other useful, similar modules.
    pass

