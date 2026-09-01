# A Comparative Evaluation of Butterworth, Chebyshev Type I and Type II, Notch, and Wavelet Filtering for Pan–Tompkins QRS Detection in Single-Lead PTB-XL ECG Signals


# How do Butterworth, Chebyshev Type I, and Chebyshev Type II bandpass filters, power-line notch filtering, and wavelet denoising affect the robustness and consistency of Pan–Tompkins-style QRS detection in Lead II ECG signals from the PTB-XL dataset?
##
## Paper Notes 


## Aim:

This study aims to synthesize and compare existing digital signal processing techniques used for QRS complex detection in ECG signals, and to implement and evaluate a representative pipeline to assess how filtering and detection choices affect accuracy and robustness in cardiac abnormality analysis. 
## Methodology:
This project uses 12-lead electrocardiogram (ECG) data from the PTB-XL dataset hosted on PhysioNet, with Lead II selected for signal analysis. The digital waveforms were recorded at a sampling frequency ($f_s$) of 100 Hz (2 ms temporal resolution) with 16-bit analog-to-digital precision and a quantization resolution of $1\ \mu\text{V/LSB}$. Lead II was isolated from the multilead record to evaluate a single-channel processing pipeline optimized for rhythm analysis and morphological feature extraction.