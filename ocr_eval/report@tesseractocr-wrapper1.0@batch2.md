# Tesseract OCR Evaluation Report

## App

The `preds` MMIF files were generated using the [Tesseract OCR Wrapper](http://apps.clams.ai/tesseractocr-wrapper/v1.0/). Annotations were generated on bounding boxes created through the [East Text Detection](http://apps.clams.ai/east-textdetection/v1.1/) app.

## Evaluation Dataset

The gold annotation data can be found [here](https://github.com/clamsproject/aapb-annotations/tree/f96f857ef83acf85f64d9a10ac8fe919e06ce51e/newshour-chyron/golds/batch2).

## Evaluation Code

The script used for evaluation can be found [here](https://github.com/clamsproject/aapb-evaluations/blob/d9cf9312851f77a1acfc2a7f394ec5fbccc69193/ocr_eval/evaluate.py).

## Metrics

This dataset was evaluated using `Character Error Rate` , or `CER`. CER is a measurement of the accuracy of the predictions - it is the proportion of *incorrectly* predicted characters, calculated using edit distance. Edit distance can be thought of as *"the least number of operations required to convert one string to another, where an operation can be one of substitution, deletion or insertion."*

As such, a higher CER represents a more inaccurate prediction, with perfect prediction being 0.0. Ideal CER performance is below 10% (<0.1).

### Aggregation

Since the hypothesis MMIF contains a `TextDocument` for each `BoundingBox` annotation, we first concatenate all the `TextDocument`s anchored on the same time point into a single string. We then compare the time points of the concatenated hypothesis and "chyron" time frames in the gold standard annotation to map the hypothesis to the gold standard. Finally, we picked the longest hypothesis string for each gold standard time frame and computed CER between gold standard transcription and concatenated hypothesis string.
CER for each gold standard time frame is recorded in the `results` directory. For each AAPB document, we aggregate the CER across all time frames by means of simple averaging.

### Results

```
cpb-aacip-507-n29p26qt59:	1.5
cpb-aacip-507-4t6f18t178:	1.0755642354488373
cpb-aacip-507-7659c6sk7z:	0.9064856568972269
cpb-aacip-525-9g5gb1zh9b:	1.5558925718069077
cpb-aacip-507-vm42r3pt6h:	1.0013089627027512
cpb-aacip-507-cf9j38m509:	1.4557802081108093
cpb-aacip-507-v40js9j432:	0.9444444477558136
cpb-aacip-507-bz6154fc44:	1.2977279822031658
cpb-aacip-525-028pc2v94s:	1.4122449159622192
cpb-aacip-507-pr7mp4wf25:	1.1577192942301433
cpb-aacip-525-bg2h70914g:	1.481121301651001
cpb-aacip-525-3b5w66b279:	1.3123106002807616
cpb-aacip-507-154dn40c26:	0.9260243574778239
cpb-aacip-507-zw18k75z4h:	0.8915034174919129
cpb-aacip-507-v11vd6pz5w:	1.1515151262283325
cpb-aacip-507-r785h7cp0z:	1.50960373878479
cpb-aacip-507-9882j68s35:	1.0496031641960144
cpb-aacip-507-zk55d8pd1h:	1.1039215326309204
cpb-aacip-507-nk3610wp6s:	0.9235169972692218
cpb-aacip-507-m61bk17f5g:	0.9577703674634298
cpb-aacip-507-6w96689725:	1.0756963193416595
cpb-aacip-507-pc2t43js98:	1.3655394315719604
Total Mean CER:	1.184331574068441
```

### Side-by-Side Views

The side-by-side comparison of gold and test annotations is visible within the [`results` output](https://github.com/clamsproject/aapb-evaluations/blob/94812e7c20d9efa535b9c2e810bdf6104b602cad/ocr_eval/results@tesseractocr-wrapper1.0@batch2).
Each file consists of the annotations for one video document,a which look like the following:

```json
{
  "561.5271": {
    "ref_text": "donald rumsfeld secretary of defense-designate",
    "hyp_text": " g d e s ; e n a t e d o n a l d  s e c r e t a r y t r a n s i t i o \u00a5 *   b u s h - c h ",
    "cer": 1.5
  },
  "mean_cer": 1.5
}
```

### Limitations

The MMIFs evaluated with the script are from a pipeline of `text-localization`-`OCR`. However, since the gold standard annotation used in the evaluation process does not include text localization annotation, we were only able to evaluate the OCR performance. **Hence, the evaluation results do not reflect the performance of the text localization app**.

On top of that, the evaluation code simply concatenated all text from multiple localization results (`BoundingBox`es) without implementing a specific *reading order* algorithm. However, the gold standard annotation does not include explicit reading order annotations, but just transcribed based on the annotator's un-documented intuitively *natural* reading order. CER simply compares strings character-by-character and thus is sensitive to the order of characters. Therefore, the evaluation results may be affected by the difference in reading order between the gold standard and the hypothesis.