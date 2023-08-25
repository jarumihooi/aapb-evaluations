#### app
The `dbpedia-spotlight-wrapper` app ([https://apps.clams.ai/dbpedia-spotlight-wrapper/v1.1/](https://apps.clams.ai/dbpedia-spotlight-wrapper/v1.1/)) was used with default runtime parameters to generate the preds MMIF files.

#### evaluation dataset

The gold annotation data files are in TSV format and can be found [here](https://github.com/clamsproject/aapb-annotations/tree/f96f857ef83acf85f64d9a10ac8fe919e06ce51e/newshour-namedentity-wikipedialink/golds/aapb-collaboration-21). 

#### evaluation code

The script used for evaluation is [here](https://github.com/clamsproject/aapb-evaluations/blob/ba7a4d9a3a0dda2cd8cb9b1eb69308fb7f9ab8de/nel_eval/evaluate.py).

#### evaluation metrics

System annotations are evaluated against gold annotations based on three properties:

- Span: The document GUID and character offsets of the entity.
- KBID: The knowledge base ID, which in this case is the Wikidata QID.
- type: The entity category.

Evaluation metrics include precision, recall, and F1. They are calculated as follows:

- __Precision__ is computed by taking the cardinality of the intersection between the set of gold annotations and the set of system annotations, divided by the cardinality of the set of system annotations.

- __Recall__ is computed by taking the cardinality of the intersection between the set of gold annotations and the set of system annotations, divided by the cardinality of the set of gold annotations.

- __F1__ is calculated using the conventional F1 formula (2 * _pr_ / _p_ + _r_).

Since the dbpedia spotlight app does not perform NIL recognition (marking entities as not having a node in a knowledge base), this is not evaluated.

#### evaluation results

The results for each catalog item are displayed in the table below. 

| **AABP GUID**            | **Gold Annotations** | **System Annotations** | **Precision** | **Recall** | **F1** |
|--------------------------|----------------------|------------------------|---------------|------------|--------|
| cpb-aacip-507-154dn40c26 | 367                  | 253                    | 0.20          | 0.14       | 0.16   |
| cpb-aacip-507-v11vd6pz5w | 431                  | 200                    | 0.32          | 0.15       | 0.20   |
| cpb-aacip-507-v40js9j432 | 548                  | 200                    | 0.32          | 0.12       | 0.17   |
| cpb-aacip-507-9882j68s35 | 81                   | 89                     | 0.15          | 0.16       | 0.15   |
| cpb-aacip-507-n29p26qt59 | 469                  | 259                    | 0.33          | 0.18       | 0.24   |
| cpb-aacip-507-vm42r3pt6h | 351                  | 203                    | 0.22          | 0.13       | 0.16   |
| cpb-aacip-507-7659c6sk7z | 139                  | 91                     | 0.25          | 0.17       | 0.20   |
| cpb-aacip-507-4746q1t25k | 492                  | 235                    | 0.25          | 0.12       | 0.16   |
| cpb-aacip-507-cf9j38m509 | 488                  | 264                    | 0.31          | 0.17       | 0.22   |
| cpb-aacip-507-pc2t43js98 | 392                  | 296                    | 0.21          | 0.16       | 0.18   |
| cpb-aacip-507-r785h7cp0z | 378                  | 234                    | 0.24          | 0.15       | 0.18   |
| cpb-aacip-507-6w96689725 | 137                  | 71                     | 0.20          | 0.10       | 0.13   |
| cpb-aacip-507-6h4cn6zk0  | 552                  | 192                    | 0.28          | 0.10       | 0.14   |
| cpb-aacip-507-pr7mp4wf25 | 531                  | 267                    | 0.36          | 0.18       | 0.24   |
| cpb-aacip-507-zw18k75z4h | 132                  | 62                     | 0.26          | 0.12       | 0.16   |
| cpb-aacip-507-4t6f18t178 | 138                  | 65                     | 0.23          | 0.11       | 0.15   |
| cpb-aacip-507-zk55d8pd1h | 331                  | 169                    | 0.18          | 0.09       | 0.12   |
| cpb-aacip-507-1v5bc3tf81 | 528                  | 238                    | 0.37          | 0.17       | 0.23   |

#### evaluation limitations


* Missing data: Due to an error in the naming of the annotation batch files, only 18 of 20 were used in the evaluation.

These metrics are staggeringly low given the accuracy scores in the previous report. This could be for a multitude reasons. For one, the comparison of `Span` is more strict here, since it is based on character offsets rather than the strings themselves. System annotations that are substrings of gold annotations are no longer counted as being a match. Secondly, an additional criterion has been added for annotations to be considered a match, namely the `type` property. Even if a system annotation has the correct `Span` and `KBID`, it would still be a miss if the `type` does not match the gold. In the future, it could be helpful to compute metrics for each property separately to isolate where the shortcomings are.

