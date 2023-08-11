#### TimeFrame+Alignment evaluation code

This tool processes human-annotated(.srt) and machine-generated(.mmif) and outputs the evaluation results.

#### Parameters:
-m or --machine_dir: Directory containing machine annotated .mmif files.

-o or --gold_dir: Directory containing human annotated .srt files.

-r or --result_file: File path to store the evaluation results. Defaults to results.txt if not provided.

#### Usage:

To run the evaluation code, run the following command:
```bash

python3 fa_eval.py -m <machine_dir> -o <gold_dir> -r <result_file>

```
#### Important Notes

If your .mmif files end with .spacy.mmif, modify the respective code lines, e.g., replace 'file.endswith(".mmif")' with 'file.endswith(".spacy.mmif")'.