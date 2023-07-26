#### app
The `dbpedia-spotlight-wrapper` app ([https://apps.clams.ai/dbpedia-spotlight-wrapper/v1.1/](https://apps.clams.ai/dbpedia-spotlight-wrapper/v1.1/)) was used to generate the preds MMIF files.

#### evaluation dataset

The gold annotation data files are in TSV format and can be found [here](https://github.com/clamsproject/aapb-annotations/tree/80a36781fd55b5b8cb74f2de187be026f1ecbb7f/newshour-namedentity-wikipedialink/golds/nel/221201-aapb-collaboration-21). 

#### evaluation code

The script used for evaluation is [here](https://github.com/clamsproject/aapb-evaluations/blob/c01ae38e993b42865a09e319635991e89783611f/nel_eval/evaluate.py).

#### evaluation metrics

The primary metric used was accuracy. For the purpose of evaluating named entity linking, only the named entities present in both the gold data and the system output data were considered. The system output mmifs were evaluated against the gold data using binary classification in terms of "hits" and "misses." A "hit" is considered to be when (i.) an NE instance output by the system has a surface form that exactly matches or is a substring of the surface text form of a gold-labeled NE, and (ii.) the grounding contains a Q identifier matching that of the gold NE. Accuracy was calculated by dividing the number of hits by the sum of hits and misses. 

#### evaluation results

The results for each catalog item are displayed in the table below. The entity count corresponds to the number entities retained after filtering the data, and consequently the number of comparisons made.

| **AAPB GUID**            | **Entity Count** | **Accuracy** |
|--------------------------|------------------|--------------|
| cpb-aacip-507-154dn40c26 | 115              | 0.71         |
| cpb-aacip-507-1v5bc3tf81 | 142              | 0.81         |
| cpb-aacip-507-4746q1t25k | 143              | 0.71         |
| cpb-aacip-507-4t6f18t178 | 29               | 0.72         |
| cpb-aacip-507-6h4cn6zk04 | 127              | 0.77         |
| cpb-aacip-507-6w96689725 | 29               | 0.62         |
| cpb-aacip-507-7659c6sk7z | 37               | 0.78         |
| cpb-aacip-507-9882j68s35 | 29               | 0.62         |
| cpb-aacip-507-cf9j38m509 | 155              | 0.76         |
| cpb-aacip-507-n29p26qt59 | 157              | 0.74         |
| cpb-aacip-507-nk3610wp6s | 144              | 0.67         |
| cpb-aacip-507-pc2t43js98 | 116              | 0.72         |
| cpb-aacip-507-r785h7cp0z | 116              | 0.72         |
| cpb-aacip-507-vm42r3pt6h | 93               | 0.70         |
| cpb-aacip-507-zk55d8pd1h | 75               | 0.61         |
| cpb-aacip-507-zw18k75z4h | 24               | 0.88         |
| **Overall**              | 1531             | 0.72         |
#### evaluation limitations

##### Missing Data

* Due to an error in the naming of the annotation batch files, only 16 of 20 were used in the evaluation.
* Additionally, some of the gold-labeled entities were missing Wikipedia URLs and as a result, the relevant Q identifiers could not be retrieved. These data were not used in the evaluation.

