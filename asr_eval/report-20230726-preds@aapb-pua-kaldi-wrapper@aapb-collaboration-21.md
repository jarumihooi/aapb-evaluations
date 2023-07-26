# ASR Evalutation Report -- Kaldi

### App:
1. [AAPB-PUA Kaldi Wrapper (v2)](https://github.com/clamsproject/app-aapb-pua-kaldi-wrapper/tree/bc7209a0b548c87878948ed5b820fd74c1c7819a) is used to generated the preds MMIF files from 20 videos. For this evaluation, MMIF files are generated through Kaldi. 
2. Preds MMIF files can be found [here](https://github.com/clamsproject/aapb-evaluations/tree/c581728ff6703856c687159fd2d3829f77f127dc/asr_eval/preds%40aapb-pua-kaldi-wrapper%40aapb-collaboration-21).
* **Note**: 4 out of the 20 videos were not transcribed properly, therefore the total number of valid evaluation generated is **16**.

### Evaluation code: 
The evaluation code can be found [here](https://github.com/clamsproject/aapb-evaluations/tree/db6bbb4598a845ea9fba1168ab9ed2f3d15411df/asr_eval).

### Evaluation metric: 
**WER** (Word Error Rate) is used as the evaluation metric that is implemented by the above mentioned evaluation code. WER calculates the accuracy of Automatic Speech Recognition (ASR) on the word level. To get a WER, the number of errors is divided by the number of total words spoken. In other words, WER tells "how wrong" the predicted result can be. Therefore, a smaller WER indicates a better performance. More information can be found [here](https://en.wikipedia.org/wiki/Word_error_rate).
`TorchMetrics` has a [WER module](https://torchmetrics.readthedocs.io/en/stable/text/word_error_rate.html) and is used in our evaluation code.

### Evaluation dataset: 
Gold standard annotations are located [here](https://github.com/clamsproject/aapb-collaboration/tree/89b8b123abbd4a9a67c525cc480173b52e0d05f0/21), with file name starting with the corresponding video IDs.

### Evaluation results: 
We evaluate MMIF files under 2 conditions:
>1. **Case-sensitive (CaseS)**: Upper case and lower case are treated differently, e.g. Apple ≠ apple. 
>2. **Case Insensitive (CaseI)**: The transcripts from both gold and preds are capitalized, thus making case insignificant, e.g. APPLE = APPLE.

These 2 conditions generate 2 different WERs.

#### A brief summary:
1. The lowest WER is **0.3326976001262665**, from `cpb-aacip-507-6w96689725`, CaseI.
2. The highest WER is **0.6443965435028076**, from `cpb-aacip-507-7659c6sk7z`, CaseS. 
3. When ignoring the case, **ALL** of the WERs become slighly lower, indicating a higher accuracy. This is also observed from [whisper `tiny` model evaluation](https://github.com/clamsproject/aapb-evaluations/blob/c84383e052d363399d7a4ba18ac38cc48a0f012a/asr_eval/report-20230725-preds%40whisper-wrapper-tiny%40aapb-collaboration-21.md) and [whisper `base` model evaluation](https://github.com/clamsproject/aapb-evaluations/blob/c84383e052d363399d7a4ba18ac38cc48a0f012a/asr_eval/report-20230726-preds%40whisper-wrapper-base%40aapb-collaboration-21.md).
4. The avarage WER among 16 MMIF files are:
   
    | CaseS | CaseI |
    | :---: | :---: |
    | 0.49073969386518| 0.427692139521241 | 

#### Full results
| base | CaseS | CaseI |
| --- | --- | --- |
| cpb-aacip-507-1v5bc3tf81 | 0.48887455463409424 | 0.41255509853363037 |
| cpb-aacip-507-6w96689725 | 0.3920322060585022 | 0.3326976001262665 |
| cpb-aacip-507-pc2t43js98 | 0.5126783847808838 | 0.45015913248062134 |
| cpb-aacip-507-v11vd6pz5w | 0.48996028304100037 | 0.41928529739379883 |
| cpb-aacip-507-154dn40c26 | 0.42861703038215637 | 0.36234042048454285 |
| cpb-aacip-507-zw18k75z4h | 0.4599441885948181 | 0.41650059819221497 |
| cpb-aacip-507-r785h7cp0z | 0.4382343292236328 | 0.37740200757980347 |
| cpb-aacip-507-9882j68s35 | 0.52763432264328 | 0.4865174889564514 |
| cpb-aacip-507-zk55d8pd1h | 0.49235889315605164 | 0.4301207661628723 |
| cpb-aacip-507-v40js9j432 | 0.460966557264328 | 0.38892796635627747 |
| cpb-aacip-507-6h4cn6zk04 | 0.483148455619812 | 0.399637371301651 |
| cpb-aacip-507-n29p26qt59 | 0.5308282971382141 | 0.46242475509643555 |
| cpb-aacip-507-4t6f18t178 | 0.5087934732437134 | 0.46973416209220886 |
| cpb-aacip-507-7659c6sk7z | 0.6443965435028076 | 0.5951354503631592 |
| cpb-aacip-507-4746q1t25k | 0.5374408960342407 | 0.45159801840782166 |
| cpb-aacip-507-vm42r3pt6h | 0.45592668652534485 | 0.38803809881210327 |



### Evaluation limitation: 
1. A considerable number of useless strings are found in all of the gold files. These files include titles such as `INFO`, `News Summary` as well as each speaker's name along with every utterance. These are useful information for readers, but are, in reality, non-existent in the actual speech. This significantly affects the evaluation **negatively**. Some processing needs to be done on gold files.
2. On the other hand, some of the gold files are missing preview or summary content in the video, whereas whisper preserves this information. This disprepancy also has a **negative** impact on evaluation results. 
3. Comparing to `whisper tiny` and `whisper base`, Kaldi has the highest average WER.
