
#### Target App
The [Gentle Forced Aligner Wrapper (v1.0)](https://apps.clams.ai/gentle-forced-aligner-wrapper/v1.0/) is used to generate the preds MMIF files from 19 audio files (the evaluation batch consist of 20 NewsHour episode, but only 19 of them were delivered to Brandeis previously).

#### evaluation dataset
The gold annotation can be found [here](https://github.com/clamsproject/aapb-annotations/tree/61bd60e99ef24a1ca369e23de8b2c74bb2cb37d3/newshour-transcript-sync/221101-batch1/annotations).

##### Problems and limitations
* The Cadet-based "gold" synchronization used non-gold transcript as base text. See https://github.com/clamsproject/aapb-annotations/issues/5#issuecomment-1693697601. 
* The Cadet-based "gold" synchronization only manually marked the beginning of each text segment, then end points were automatically added by subtracting 10 milliseconds from the start point of the following segment. 

#### Evaluation Code
The script used for evaluation is [here](https://github.com/clamsproject/aapb-evaluations/blob/49483eb5b6b35f35ded31fd62a3815701cdfc516/fa_eval/evaluate.py).

#### Evaluation Metrics

We evaluated forced alignment performance considering it as two different tasks: Diarization and Segmentation. 
For each, we report a paired metrics of Coverage and Purity, and their harmonic mean, F1.
For implementation of those metrics, we used [pyannote.metrics](http://pyannote.github.io/pyannote-metrics/reference.html#evaluation-metrics) python library. For implementation details, please refer to the [library documentation](http://pyannote.github.io/pyannote-metrics/reference.html#segmentation) or the [accompanying publication](https://www.isca-speech.org/archive_v0/Interspeech_2017/pdfs/0411.PDF).

* Segmentation: in `pyannote.metrics`, this task is defined as speaker change detection task. When we apply this to forced alignment, we consider each start and end point of the text segments as speaker change points.
* Diarization: this task is an extension of the segmentation task, where we consider each audio segment (with start and end points) **labeled** with the speaker identifier. In our case, we consider each text segment as a speaker segment, and the speaker identifier is the text itself.
* Coverage vs Purity: simply put, **coverage** measures how much of the gold segments are correctly detected in the hypothesis segmentation, while **purity** measures how much of the gold segments are mixed into any given single hypothesis segment, or in the other words, it measures the degree of 1-to-1 mapping between the gold and hypothesis segments. For more details, the documents linked above are good resources. 

#### evaluation results

Here are the evaluation results for this batch:

```
Individual file results:
GUID   DiaCov   DiaPur  D-C-P-F1   SegCov  SegPur  S-C-P-F1
cpb-aacip-507-6w96689725 0.976800 0.972071  0.974430 0.939031     1.0  0.968557
cpb-aacip-507-154dn40c26 0.974231 0.964671  0.969428 0.935661     1.0  0.966761
cpb-aacip-507-r785h7cp0z 0.979036 0.971423  0.975215 0.946178     1.0  0.972345
cpb-aacip-507-n29p26qt59 0.973329 0.970259  0.971792 0.935249     1.0  0.966541
cpb-aacip-507-pc2t43js98 0.974697 0.968273  0.971474 0.936596     1.0  0.967260
cpb-aacip-507-nk3610wp6s 0.973057 0.965097  0.969061 0.930397     1.0  0.963944
cpb-aacip-507-6h4cn6zk04 0.975139 0.969976  0.972551 0.922537     1.0  0.959708
cpb-aacip-507-pr7mp4wf25 0.969234 0.955383  0.962259 0.929009     1.0  0.963198
cpb-aacip-507-4746q1t25k 0.974794 0.964196  0.969466 0.932502     1.0  0.965072
cpb-aacip-507-4t6f18t178 0.969985 0.959975  0.964954 0.928064     1.0  0.962690
cpb-aacip-507-zw18k75z4h 0.967243 0.958316  0.962759 0.933812     1.0  0.965773
cpb-aacip-507-v11vd6pz5w 0.980989 0.977637  0.979310 0.942218     1.0  0.970250
cpb-aacip-507-vm42r3pt6h 0.977702 0.969733  0.973701 0.939191     1.0  0.968642
cpb-aacip-507-zk55d8pd1h 0.971831 0.960442  0.966103 0.930962     1.0  0.964247
cpb-aacip-507-9882j68s35 0.964569 0.958660  0.961606 0.925507     1.0  0.961313
cpb-aacip-507-1v5bc3tf81 0.977150 0.970972  0.974051 0.937488     1.0  0.967735
cpb-aacip-507-cf9j38m509 0.980175 0.976447  0.978307 0.948909     1.0  0.973785
cpb-aacip-507-7659c6sk7z 0.975849 0.966133  0.970967 0.922775     1.0  0.959837
cpb-aacip-507-v40js9j432 0.975791 0.970891  0.973335 0.937696     1.0  0.967846


Average results:
DiaCov      0.974295
DiaPur      0.966871
D-C-P-F1    0.970567
SegCov      0.934410
SegPur      1.000000
S-C-P-F1    0.966079
```

#### Evaluation Limitations
* Due to the non-gold status of the gold annotation used as the evaluation dataset, replicating the same evaluation process on other apps (or versions) may not be as possible.
* Kaldi/Gentle does its own tokenization and normalization during processing the text input. This may cause some discrepancies in text between the gold and hypothesis text segments. To mitigate this issue, we had to implement [a number of "reverse" processes](https://github.com/clamsproject/aapb-evaluations/blob/49483eb5b6b35f35ded31fd62a3815701cdfc516/fa_eval/evaluate.py#L48-L99) in the evaluation code, which will not be applicable to other apps that does not use Kaldi/Gentle.
* The manual annotation process didn't include marking of end points, but instead relied on automatic end point generation from the start point of immediately following segment. This means that the gold annotation might include a fair number of noises, *especially for some the end points*.