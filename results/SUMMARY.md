# ECG filter comparison — results

Source: `ptbxl_filter_comparison_4methods.csv`. This report summarizes saved outputs; it does not rerun detection.

- Unique records: **20**
- Method evaluations: **80**
- Successful executions: **80**

| Method | Runs | Failed | Mean peaks | Mean detected HR (BPM) | Mean within-record RR SD (s) |
|---|---:|---:|---:|---:|---:|
| raw | 20 | 0 | 13.00 | 77.51 | 0.0488 |
| butterworth | 20 | 0 | 13.00 | 77.51 | 0.0490 |
| chebyshev1 | 20 | 0 | 12.95 | 77.50 | 0.0494 |
| chebyshev2 | 20 | 0 | 13.00 | 77.51 | 0.0490 |

Among 20 records with results for all represented methods, 1 had different peak counts across methods.
ECG IDs with count disagreement: 12.

## Interpretation

The four pipelines execute on this small subset and sometimes produce different beat counts. Equal counts do not establish equal peak timing. Mean heart rate and RR variability describe the detector outputs; neither ranks detection accuracy or establishes a best filter.

## Limitations and next steps

The bundled v1 experiment uses the first 20 metadata records, not a representative sample. SUCCESS means no processing exception, not a correct detection. There are no beat-level reference annotations in this evaluation, so sensitivity, precision, and F1 are not reported. The raw baseline still uses the detector’s internal 5–15 Hz bandpass. Next: broaden sampling, inspect disagreements, and evaluate against annotated beats.
