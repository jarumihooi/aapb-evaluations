# WER Calculation

The app will take two arguments: a hypothesis mmif file, either from Kaldi or Whisper, and a gold .txt file. The output is a number indicating WER. 

WER calculation is done through WordErrorRate from torchmetrics. 

Sample data are included in the folder.

To run the app: 
```bash
python3 asr_eval --hyp-file "your hypothesis file" --gold-file "your gold file", optional: --exact-case (if do not want to ignore casing)
```

### Next step:
1. try to use the functions from mmif package
2. consider the case when having a folder with multiple mmif files
