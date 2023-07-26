# ASR Evalutation Report -- Whisper `tiny`

### App:
1. [whisper-wrapper `v3`](https://github.com/clamsproject/app-whisper-wrapper/tree/b9a423a04e9f3bf9c89bef48343f2ab0473b6d41) is used to generated the preds MMIF files from 20 videos. For this evaluation, MMIF files are generated through whisper `tiny` model. 
2. Preds MMIF files can be found [here](https://github.com/clamsproject/aapb-evaluations/tree/db6bbb4598a845ea9fba1168ab9ed2f3d15411df/asr_eval/preds%40whisper-wrapper-tiny%40aapb-collaboration-21).
* **Note**: `cpb-aacip-507-vd6nz81n6r.video` does not exist, therefore no MMIF file is generated. The total number of valid MMIF files is **19**, **NOT** 20.

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

#### A brief summary
1. The lowest WER is **0.16295157372951508**, from `cpb-aacip-507-r785h7cp0z`, CaseI.
2. The highest WER is **0.9988582134246826**, from `cpb-aacip-507-n29p26qt59`, CaseS. This particular file has such a high WER due to the predictied transcrption being almost entirely wrong.
3. The majority of the WERs fall within 20% ~ 35% range.
4. When ignoring the case, **ALL** of the WERs become slighly lower, indicating a slightly higher accuracy.
5. The avarage WER among 19 MMIF files are:
   
    | CaseS | CaseI |
    | :---: | :---: |
    | 0.331559629032486 | 0.307924005546068 |

#### Full results
| tiny | CaseS | CaseI |
| --- | --- | --- |
| cpb-aacip-507-4746q1t25k | 0.2891427278518677 | 0.2552209496498108 |
| cpb-aacip-507-r785h7cp0z | 0.18008126318454742 | 0.16295157372951508 |
| cpb-aacip-507-cf9j38m509 | 0.3160593509674072 | 0.2897665202617645 |
| cpb-aacip-507-9882j68s35 | 0.24402371048927307 | 0.22662076354026794 |
| cpb-aacip-507-v40js9j432 | 0.20044207572937012 | 0.18105094134807587 |
| cpb-aacip-507-154dn40c26 | 0.20499999821186066 | 0.18414893746376038 |
| cpb-aacip-507-6h4cn6zk04 | 0.25853243470191956 | 0.2247226983308792 |
| cpb-aacip-507-6w96689725 | 0.20788303017616272 | 0.17779190838336945 |
| cpb-aacip-507-zk55d8pd1h | 0.35740694403648376 | 0.33756470680236816 |
| cpb-aacip-507-pr7mp4wf25 | 0.2574303150177002 | 0.23036891222000122 |
| cpb-aacip-507-vm42r3pt6h | 0.2609429657459259 | 0.2364644855260849 |
| cpb-aacip-507-n29p26qt59 | 0.9988582134246826 | 0.9973012208938599 |
| cpb-aacip-507-1v5bc3tf81 | 0.230140820145607 | 0.2058475762605667 |
| cpb-aacip-507-nk3610wp6s | 0.21808844804763794 | 0.19932928681373596 |
| cpb-aacip-507-v11vd6pz5w | 0.3740215599536896 | 0.3283040225505829 |
| cpb-aacip-507-pc2t43js98 | 0.3128015697002411 | 0.27779489755630493 |
| cpb-aacip-507-4t6f18t178 | 0.32556235790252686 | 0.29815950989723206 |
| cpb-aacip-507-7659c6sk7z | 0.7583128213882446 | 0.7527709603309631 |
| cpb-aacip-507-zw18k75z4h | 0.3049023449420929 | 0.28437623381614685 |


### Evaluation limitation: 
1. A considerable number of useless strings are found in all of the gold files. These files include titles such as `INFO`, `News Summary` as well as each speaker's name along with every utterance. These are useful information for readers, but are, in reality, non-existent in the actual speech. This significantly affects the evaluation **negatively**. Some processing needs to be done on gold files.
2. On the other hand, some of the gold files are missing preview or summary content in the video, whereas whisper preserves this information. This disprepancy also has a **negative** impact on evaluation results. 
3. Aside from the file that has 0.99 WER, another MMIF file `cpb-aacip-507-7659c6sk7z` generates a 0.75 WER due to failing to transcribe the first part of the video. It would help to understand what causes low transcribing quality.
4. Considering `tiny` model's size, WER is expected to decrease in the future when transcribing with bigger models.
