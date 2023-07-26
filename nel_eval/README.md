# NEL Evaluation

This script evaluates `.mmif` files with named entity linking annotations produced as output
from the [DBpedia Spotlight wrapper](https://github.com/clamsproject/app-dbpedia-spotlight-wrapper) app.
The system-generated data in the `.mmif` files are compared to the gold `.tsv` data in order to compute accuracy.
Gold annotations can be found in the [aapb-annotations](https://github.com/clamsproject/aapb-annotations) repository.

__Note__: gold annotation files and test output files that correspond
to the same aapb catalog item must share the same file name (with the exception of file extension).
i.e. `gold-files/cpb-aacip-507-1v5bc3tf81.tsv` and `test-files/cpb-aacip-507-1v5bc3tf81.mmif`.

## Metrics

The only metric computed is accuracy (number of hits divided by the number of hits and misses). Only named entities
shared in common by the system data and the gold data are included in the evaluation.
A "hit" is considered to be when the named entity output from the system has the same surface text form and 
grounding (QID) as the entity labeled in the gold data.

## Output file format

The output txt file is in json format, where each top level item is a dictionary corresponding
to the catalog item GUID. Within each dictionary is a field for the accuracy and two nested dictionaries
describing how many gold/test entities were retained and their proportion with respect to the original file.
Specifically, gold labeled entities were omitted from the evaluation when there was no QID available, while
system-generated entities were not included if they were not present in the gold data.

Example output:

```json
{
    "cpb-aacip-507-zw18k75z4h": {
        "Accuracy": "0.86",
        "Gold Entities": {
            "count": 40,
            "proportion of total": "0.75"
        },
        "Test Entities": {
            "count": 22,
            "proportion of total": "0.35"
        }
    }
}
```