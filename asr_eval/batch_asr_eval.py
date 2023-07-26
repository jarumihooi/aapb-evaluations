from asr_eval import calculateWer
import click
import os
import json
import shutil


# write wer result into .json
def write_result_to_file(dir, filename, content): 
    filepath = os.path.join(dir, filename + '.json')
    with open(filepath, 'w') as fp:
        fp.write(json.dumps(content))


# check file id in preds and gold paths, and find the matching ids
def batch_run_wer(hyp_dir, gold_dir): 
    hyp_files = os.listdir(hyp_dir)
    gold_files = os.listdir(gold_dir)
    
    for hyp_file in hyp_files:
        id = hyp_file.split('.')[0]
        gold_file = next(x for x in gold_files if x.startswith(id))
        print("Processing file: ", hyp_file, gold_file)

        if gold_file:
            hyp_file_path = os.path.join(hyp_dir, hyp_file)
            gold_file_path = os.path.join(gold_dir, gold_file)
            try:
                wer_result_exact_case = calculateWer(hyp_file_path, gold_file_path, True)
                wer_result_ignore_case = calculateWer(hyp_file_path, gold_file_path, False)
                wer_result_in_json = {
                    "wer_results": [
                        {
                            "wer_result": wer_result_exact_case,
                            "exact_case": True
                        },
                        {
                            "wer_result": wer_result_ignore_case,
                            "exact_case": False
                        }
                    ]
                }
                write_result_to_file('wer_results', id, wer_result_in_json)
            except Exception as wer_exception:
                print(wer_exception)


@click.command()
@click.option("--hyp-dir", type=click.Path(readable=True), required=True)
@click.option("--gold-dir", type=click.Path(readable=True), required=True)
def main(hyp_dir, gold_dir):
    # change the path name when needed 
    try: 
        try:
            shutil.rmtree('wer_results')
        except Exception as error:
            print(error)
        os.mkdir('wer_results')
        batch_run_wer(hyp_dir, gold_dir)
    except Exception as batch_run_error:
        print(batch_run_error)

if __name__ == "__main__":
  main()
