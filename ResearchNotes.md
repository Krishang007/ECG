# A Comparative Review and Implementation of Digital Signal Processing Techniques for ECG-Based Cardiac Abnormality Detection

## A Comparative Review and Implementation of ECG Signal Processing Techniques: From Classical Digital Signal Processing to Artificial Intelligence-Based Cardiac Abnormality Detection
## How do different ECG preprocessing and feature detection techniques affect the accuracy and robustness of QRS complex and T-wave detection using single-lead ECG signals from  PTB-XL dataset
## Paper Notes 


## Aim:
This study aims to synthesize and compare existing digital signal processing techniques used for QRS complex and T-wave detection in ECG signals, and to implement and evaluate a representative pipeline to assess how filtering and detection choices affect accuracy and robustness in cardiac abnormality analysis. 
## Methodology:
This project uses 12-lead electrocardiogram (ECG) data from the PTB-XL dataset hosted on PhysioNet, with Lead II selected for signal analysis. The digital waveforms were recorded at a sampling frequency ($f_s$) of 500 Hz (2 ms temporal resolution) with 16-bit analog-to-digital precision and a quantization resolution of $1\ \mu\text{V/LSB}$. Lead II was isolated from the multilead record to evaluate a single-channel processing pipeline optimized for rhythm analysis and morphological feature extraction.