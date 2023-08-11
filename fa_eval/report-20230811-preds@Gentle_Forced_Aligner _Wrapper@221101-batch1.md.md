
#### app
The [Gentle Forced Aligner Wrapper](https://apps.clams.ai/gentle-forced-aligner-wrapper/v1.0/) is used to generate the preds MMIF files from 19 audio files. 

#### evaluation dataset
The gold annotation can be found [here](https://github.com/clamsproject/aapb-annotations/tree/61bd60e99ef24a1ca369e23de8b2c74bb2cb37d3/newshour-transcript-sync/221101-batch1/annotations).

#### evaluation code
The script used for evaluation is [here]( **To be determined** ).

#### evaluation metrics

For an individual file, we assess the module using the Detection Error Rate as our evaluation metric, utilizing the [pyannote.metrics](http://pyannote.github.io/pyannote-metrics/reference.html#evaluation-metrics) for computation.

The detection error rate is calculated as the sum of the durations of false alarms (non-speech classified as speech) and missed detections (speech classified as non-speech) divided by the total duration of speech in the reference, where false alarm is the duration of non-speech incorrectly classified as speech, missed detection is the duration of speech incorrectly classified as non-speech, and total is the total duration of speech in the reference.

To get an overall picture of the model's performance, we use Precision, Recall and F1. Precision evaluates the proportion of correctly predicted entities among all instances that the model predicted as entities. Recall measures the proportion of actual entities that the model correctly identified. F1 is the harmonic mean of precision and recall, aiming to balance the two.

For more details, refer to the [pytyhon `seqeval` library](https://github.com/chakki-works/seqeval). The evaluation code internally uses this library.

#### evaluation results

Here are the evaluation results for this batch:

```
Total Precision = 0.996763737399742	 Total Recall = 0.6952650481056941	 Total F1 = 0.8191527162774934

Individual file results:
                        GUID  FN seconds  FP seconds Total true seconds  Detection Error Rate
0   cpb-aacip-507-n29p26qt59   1301151.0      8203.0            3778056              0.346568
1   cpb-aacip-507-4t6f18t178    512078.0      4396.0            1697471              0.304261
2   cpb-aacip-507-7659c6sk7z    753246.0      2870.0            1536172              0.492208
3   cpb-aacip-507-4746q1t25k   1313698.0      7735.0            3705128              0.356650
4   cpb-aacip-507-vm42r3pt6h    840490.0      7382.0            3157830              0.268498
5   cpb-aacip-507-cf9j38m509   1318604.0      8155.0            3813244              0.347934
6   cpb-aacip-507-v40js9j432    850273.0      8549.0            3461378              0.248116
7   cpb-aacip-507-pr7mp4wf25   1262879.0      7335.0            3581853              0.354625
8   cpb-aacip-507-6h4cn6zk04    931016.0      8140.0            3452812              0.271997
9   cpb-aacip-507-154dn40c26    811274.0      8034.0            3457057              0.236996
10  cpb-aacip-507-zw18k75z4h    384703.0      4166.0            1685729              0.230683
11  cpb-aacip-507-v11vd6pz5w   1314098.0      7750.0            3757628              0.351777
12  cpb-aacip-507-r785h7cp0z    926117.0      7753.0            3476553              0.268620
13  cpb-aacip-507-9882j68s35    474984.0      4542.0            1695670              0.282794
14  cpb-aacip-507-zk55d8pd1h   1267602.0      6813.0            3454967              0.368865
15  cpb-aacip-507-1v5bc3tf81   1093021.0      8023.0            3585495              0.307083
16  cpb-aacip-507-nk3610wp6s    788657.0      8355.0            3396476              0.234659
17  cpb-aacip-507-6w96689725    420635.0      4265.0            1701894              0.249663
18  cpb-aacip-507-pc2t43js98   1102783.0      8407.0            3580572              0.310339
```

#### evaluation limitations
In cases where there's a high class imbalance (e.g., very few speech segments in a long audio), small errors can result in a significantly skewed detection error rate. For instance, a short false alarm in an overwhelmingly non-speech audio can lead to a high error rate.

