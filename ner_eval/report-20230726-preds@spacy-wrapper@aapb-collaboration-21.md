
#### app
The Spacy NLP wrapper was used to generate the preds MMIF files. http://apps.clams.ai/spacy-wrapper/v1.1/

#### evaluation dataset
The gold annotation can be found [here](https://github.com/clamsproject/aapb-annotations/tree/main/newshour-namedentity/golds/aapb-collaboration-21).

#### evaluation code
The script used for evaluation is [here](https://github.com/clamsproject/aapb-evaluations/blob/0ad076f50bd1703133d3ae76dfddcb4c3ac4d7b1/ner_eval/evaluate.py).

#### evaluation metrics

##### Evaluation Types
In this particular evaluation, two types of evaluations are made:

###### Strict Evaluation
The model's predictions are compared exactly with the gold standard. Every token in an entity must have the matching tagging with the gold standard to be counted as the same entity.
There are four possibilities: (we use “Mark Zuckerberg" as an example)
* The sentence contains the entity "Mark Zuckerberg" and the model correctly detects the entire entity "Mark Zuckerberg" as a person (True Positive).
* The sentence does not detect the whole entity "Mark Zuckerberg", but the model detects "Zuckerberg" as a person (False Positive).
* The sentence contains the entity "Mark Zuckerberg", but the model fails to detect the whole “Mark Zuckerberg"(False Negative).
* The sentence does not contain the entity "Mark Zuckerberg" and the model does not predict it. (True negative)

###### Token-based Evaluation
The evaluation is done on the token level, and the difference between 'B-' and 'I-' is disregarded. This means that as long as the model predicts the right entity type for a token, it's considered correct, regardless of whether it correctly identified the boundaries of multi-token entities. 
There are four possibilities: (we use “Mark Zuckerberg" as an example)
* The sentence contains the entity "Mark Zuckerberg", the model correctly identified "Zuckerburg" as part of the entity "Mark Zuckerburg"  (True Positive).
* A token (let's say "Apple") is not part of any entity in the sentence, but the model predicts it as part of an entity (False Positive).
* The sentence contains the entity "Mark Zuckerberg", the model failed to identify "Mark" as part of the entity "Mark Zuckerburg" (False Negative).
* A token (let's say "Apple") is not part of any entity in the sentence, and the model correctly does not identify it as part of an entity. (True negative)

The different entity types that are being evaluated include 'event', 'location', 'organization', 'person', 'product', and 'program/publication_title'.

##### measurements
Precision evaluates the proportion of correctly predicted entities among all instances that the model predicted as entities. Recall measures the proportion of actual entities that the model correctly identified. F1 is the harmonic mean of precision and recall, aiming to balance the two.

For more details, refer to the [pytyhon `seqeval` library](https://github.com/chakki-works/seqeval). The evaluation code internally uses this library.

##### aggregation of evalution measurements 
We use micro, macro, and weighted averaging to get an overall picture of the model's performance:

* **Micro Average**: Aggregates the contributions of all classes. It gives a global performance score.

* **Macro Average**: Computes the metric independently for each class and then takes the average. It provides an equal-weighted performance score.

* **Weighted Average**: Similar to macro-average, but each class metric is weighted by its proportion in the dataset. It provides a balanced performance score in case of class imbalance.

#### evaluation results

Here are the evaluation results for this batch:

```
**Strict Evaluation Result**
                       precision    recall  f1-score   support

                event       0.20      0.14      0.17       143
             location       0.67      0.75      0.71      1644
         organization       0.43      0.57      0.49      1515
               person       0.46      0.27      0.34      4770
              product       0.14      0.23      0.17        26

            micro avg       0.50      0.41      0.45      8443
            macro avg       0.37      0.33      0.32      8443
         weighted avg       0.48      0.41      0.42      8443
```

```
**Token-based Evaluation Result**
                       precision    recall  f1-score   support

                event       0.54      0.33      0.41       377
             location       0.74      0.87      0.80      2265
         organization       0.57      0.78      0.66      2693
               person       0.93      0.41      0.57      8870
              product       0.15      0.24      0.19        33

            micro avg       0.74      0.53      0.61     15084
            macro avg       0.57      0.45      0.46     15084
         weighted avg       0.80      0.53      0.59     15084
```



#### side-by-side views

The side-by-side views of the gold annotations and app predictions can be found [here](https://github.com/clamsproject/aapb-evaluations/tree/0ad076f50bd1703133d3ae76dfddcb4c3ac4d7b1/ner_eval/results%40spacy-wrapper%40aapb-collaboration-21).
Each file contains rows of token-offset intervals, gold annotations, and app predictions, in that order. For example, a row of

> 4, PERSON, O

means that for the 4th token from the document, the gold annotation records a PERSON, but the app predicted no NE.
Note that the SBS view files are using token indices starting from 1. Also we use indices instead of words themselves to avoid copyrigth issues.
