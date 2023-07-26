# WER Calculation

Suppose both preds and gold files have their file ids start with the corresponding video id:
```
pred = cpb-aacip-123-1234567890.whisper-tiny.mmif
gold = cpb-aacip-123-1234567890.txt
```
the app will take two arguments: 
1. the directory where hypothesis MMIF files locate, and
2. the directory where gold .txt files locate.

The output is a .json file also named after the video Id: `cpb-aacip-123-1234567890.json`. It stores a number of WER results depending on the evaluation conditions (currently two conditions: case-sensitive and non case-sensitive). In the future more conditions will be taken into consieration, so the result .json could extend accordingly. The .json file is stored in `/wer_results/`

A sample .json file:
```
{"wer_results": [{"wer_result": 0.230140820145607, "exact_case": true}, {"wer_result": 0.2058475762605667, "exact_case": false}]}
```

WER calculation is done through WordErrorRate from torchmetrics. 

### To run the app: 
```bash
python3 batch_asr_eval.py --hyp-dir "your hypothesis file dir" --gold-dir "your gold file dir"
```
* optional: if you want to change the directory where .json results are stored (other than default `/wer_results/`), do so under `main` in `batch_asr_eval.py`:
* 
        ...
        shutil.rmtree(**'wer_results'**)
        os.mkdir(**'wer_results'**)
        ...

### Next step:
try to use the functions from mmif package
