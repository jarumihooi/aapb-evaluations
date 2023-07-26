# ASR Evalutation Report -- Whisper `tiny`

### App:
1. [whisper-wrapper `v3`](https://github.com/clamsproject/app-whisper-wrapper) is used to generated the preds MMIF files from 20 videos. For this evaluation, MMIF files are generated through whisper `tiny` model. 
2. Preds MMIF files can be found [here](https://github.com/clamsproject/aapb-evaluations/tree/2-asr-eval/asr_eval/preds%40whisper-wrapper-tiny%40aapb-collaboration-21).
* **Note**: `cpb-aacip-507-vd6nz81n6r.video` does not exist, therefore no MMIF file is generated. The total number of valid MMIF files is **19**, **NOT** 20.

### Evaluation code: 
The evaluation code can be found [here](https://github.com/clamsproject/aapb-evaluations/tree/2-asr-eval/asr_eval).

### Evaluation metric: 
WER (World Error Rate) is used as the evaluation metric that is implemented by the above mentioned evaluation code. WER calculates the accuracy of Automatic Speech Recognition (ASR) on the word level. To get a WER, the number of errors is divided by the number of total words spoken. In other words, WER tells "how wrong" the predicted result can be. Therefore, a smaller WER indicates a better performance. More information can be found [here](https://en.wikipedia.org/wiki/Word_error_rate).
`TorchMetrics` has a [WER module](https://torchmetrics.readthedocs.io/en/stable/text/word_error_rate.html) and is used in our evaluation code.

### Evaluation dataset: 
Gold standard annotations are located [here](https://github.com/clamsproject/aapb-collaboration/tree/21-undocumented-changes/21), with file name starting with the corresponding video IDs.

### Evaluation results: 
WER results are located [here](https://github.com/clamsproject/aapb-evaluations/tree/2-asr-eval/asr_eval/wer_results). Each of the 19 videos has their WER stored in a .json file.
We evaluate MMIF files under 2 conditions:
>1. **Case-sensitive**: Upper case and lower case are treated differently, e.g. Apple ≠ apple. 
>2. **Non case-sensitive**: The transcripts from both gold and preds are converted into upper case, therefore making case insignificant, e.g. APPLE = APPLE.

These 2 conditions generate 2 different WERs. Each .json files contains both numbers, with a notation referring the casing.

#### A brief summary
1. The lowest WER we get is **0.16295157372951508**, from `cpb-aacip-507-r785h7cp0z`, non case-sensitive.
2. The highest WER is **0.9988582134246826**, from `cpb-aacip-507-n29p26qt59`, case-sensitive. This particular file has such a high WER due to the predictied transcrption being almost entirely wrong.
3. The majority of the WERs falls within 20% ~ 35% range.
4. When ignoring the case, **ALL** of the WERs become slighly lower, indicating a slightly higher accuracy.
5. The avarage WER among 19 MMIF files are:
   
    | Case-sensitive   | Non case-sensitive|
    | -----------      | -----------       |
    | 0.331559629032486| 0.307924005546068 |

### Evaluation limitation: 
1. A considerable number of useless strings are found in all of the gold files. These files include titles such as `INFO`, `News Summary` as well as each speaker's name along with every utterance. These are useful information for readers, but are, in reality, non-existent in the actual speech. This significantly affects the evaluation **negatively**. Some processing needs to be done on gold files. 
1. Aside from the file that has 0.99 WER, another MMIF file `cpb-aacip-507-7659c6sk7z` generates a 0.75 WER due to failing to transcribe the first part of the video. It would help to understand what causes low transcribing quality.
2. Considering `tiny` model's size, WER is expected to decrease in the future when transcribing with bigger models.
