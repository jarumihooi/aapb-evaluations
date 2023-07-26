from torchmetrics import WordErrorRate
import json
import click
import mmif
from mmif import Mmif


def get_text_from_mmif(mmif): 
  with open(mmif, 'r') as f:
    data = json.load(f)

  # view is a list with only one dict
  view_dict = data['views'][0]
  # annotation is a list of dictionaries
  annotation_dict = view_dict['annotations'][0]
  text = annotation_dict['properties']['text']['@value']

  return text


def get_text_from_txt(txt):
  with open(txt, 'r') as f:
    text = f.read()
  return text


  # for now, we only care about casing, more processing steps might be added in the future
def process_text(text, ignore_case):
  if ignore_case:
    text = text.upper()
  return text


  # todo: using mmif sdk
  # with open('/content/drive/MyDrive/output.mmif', 'r') as f:
  # mmif_obj = Mmif(f.read())

def calculateWer(hyp_file, gold_file, exact_case):
   # if we want to ignore casing
  hyp = process_text(get_text_from_mmif(hyp_file), not exact_case)
  gold = process_text(get_text_from_txt(gold_file), not exact_case)

  wer = WordErrorRate()
  return wer(hyp, gold).item()


@click.command()
@click.option("--hyp-file", type=click.Path(readable=True), required=True)
@click.option("--gold-file", type=click.Path(readable=True), required=True)
@click.option("--exact-case", is_flag=True)
def main(hyp_file, gold_file, exact_case):

  print(calculateWer(hyp_file, gold_file, exact_case))


if __name__ == "__main__":
  main()

  

