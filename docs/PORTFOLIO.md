# Portfolio and résumé copy

## Project title

ECG Signal Processing & Filter Comparison | Python, SciPy, NumPy, pandas, WFDB

## Short portfolio description

Built a modular Python pipeline to load PTB-XL ECG recordings, process Lead II signals, detect R-peaks with a simplified Pan–Tompkins-style algorithm, and visualize waveform and frequency-domain behavior. Compared raw input with Butterworth and two Chebyshev preprocessing methods across 20 recordings, exporting 80 per-method evaluations and reproducible summary reports. Documented experimental limitations and a roadmap for evaluation against annotated beats.

## Résumé bullets

- Built a Python ECG analysis pipeline using NumPy, SciPy, pandas, and WFDB, integrating signal filtering, Pan–Tompkins-style R-peak detection, RR-interval analysis, and spectral visualization.
- Compared four preprocessing configurations across 20 PTB-XL recordings, completing 80 processing runs and generating reproducible CSV reports and waveform/PSD figures.

## Interview explanation

The question was whether preprocessing changes the output of a fixed QRS detector. I kept the detector constant and compared raw input, Butterworth, Chebyshev I, and Chebyshev II preprocessing on the same recordings. Aggregate detected heart rates were similar, while some individual detections differed. The important limitation is that execution success and agreement are not accuracy: the next step is comparison against beat-level annotations on a broader sample.

## Claims to keep precise

This release demonstrates digital signal processing and reproducible experimentation. It does not include machine learning, disease classification, clinical validation, or measured detection accuracy. The 80 runs are method evaluations of 20 recordings, not 80 independent recordings.
