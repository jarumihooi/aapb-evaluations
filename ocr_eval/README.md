# CLAMS OCR Evaluation

This script evaluates `.mmif` files which contain OCR annotations. The annotations are generated in a two-step process: First, bounding
boxes are created via [`CLAMS East Text Detection Tool`](https://apps.clams.ai/east-textdetection/v1.1/), and then the text within those boxes is parsed via [`CLAMS Tesseract Wrapper`](https://apps.clams.ai/tesseractocr-wrapper/v1.0/) and [`CLAMS Parseq Wrapper`](https://apps.clams.ai/parseqocr-wrapper/v1.0/). The evaluation code here only looks at the accuracy of the text within the boxes - as such, errors in the East tool may proliferate downstream into the CER for the text boxes.

## Metrics

The metric used for the evaluation of this OCR tool is Character Error Rate, or CER. This metric represents the percentage of characters that were *incorrectly* predicted. This means that higher CER values, representing a higher error rate, represent worse model performance, with a CER of 0 representing a perfect score.

## Output

By default, the script outputs to `'results.json'`. This `.json` file has the following structure:

```json
"filename": {
    "timepoint": {
        "gold",
        "test",
        "cer"
    }
}
```

Which, in practice, looks like the following:

```json
"cpb-aacip-507-pr7mp4wf25": {

}
```

The script contains an optional `'-i'` flag, which will print each file's annotations to a separate json document within the output directrory.

## Evaluation

Parseq performed slightly better than Tesseract, with Parseq's average CER being **0.84** and Tesseract having a CER of **0.89**. Additionally, Parseq had no documents that were completely inaccurate (CER of 1.0), whereas Tesseract had several of these.

Document level averages for CER are as follows:

| Document               |Tesseract  | Parseq   |
| ---------------------  | --------- | -----    |
|cpb-aacip-507-bz6154fc44|  0.8678   |
|cpb-aacip-507-cf9j38m509|  0.8603   |
|cpb-aacip-507-zw18k75z4h|  0.9815   |
|cpb-aacip-507-pc2t43js98|  0.9524   |
|cpb-aacip-525-9g5gb1zh9b|  0.9031   |
|cpb-aacip-507-n29p26qt59|  0.9872   |
|cpb-aacip-507-nk3610wp6s|  0.9026   |
|cpb-aacip-507-7659c6sk7z|  0.8912   |
|cpb-aacip-507-vd6nz81n6r|  0 (empty)|
|cpb-aacip-525-bg2h70914g|  0.8892   |
|cpb-aacip-507-4t6f18t178|  0.9485   |
|cpb-aacip-507-6w96689725|  1.0      |
|cpb-aacip-507-zk55d8pd1h|  1.0      |
|cpb-aacip-525-028pc2v94s|  0.9398   |
|cpb-aacip-507-v40js9j432|  1.0      |
|cpb-aacip-507-m61bk17f5g|  0.8753   |
|cpb-aacip-507-pr7mp4wf25|  0.9427   |
|cpb-aacip-507-vm42r3pt6h|  0.8831   |
|cpb-aacip-507-9882j68s35|  1.0      |
|cpb-aacip-525-3b5w66b279|  0.9568   |
|cpb-aacip-507-v11vd6pz5w|  0.8235   |
|cpb-aacip-507-r785h7cp0z|  0.9387   |
|cpb-aacip-507-154dn40c26|  0.9807   |
| **TOTAL**              |**0.8924** |
