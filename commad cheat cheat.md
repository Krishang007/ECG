## Python Command Cheat Sheet for Computational Physiology

This project uses Python to load ECG data, inspect metadata, filter signals, and visualize time-domain and frequency-domain behavior. Keep this sheet as a reusable reference for future computational physiology projects.

## Environment Setup

```bash
source .venv/bin/activate
python --version
which python
pip install -r requirements.txt
```

If you do not have a requirements file yet, install the core libraries directly:

```bash
pip install numpy pandas scipy matplotlib wfdb
```

## Run the Project

```bash
python SRC/main.py
```

If you want to run the script with the project virtual environment explicitly:

```bash
.venv/bin/python SRC/main.py
```

## Core Libraries Used in This Project

- `pathlib.Path`: clean file and folder path handling.
- `wfdb`: reads PhysioNet/ECG waveform records and header files.
- `numpy`: array math, time vectors, indexing, and numerical operations.
- `pandas`: metadata tables, CSV loading, and label extraction.
- `scipy.signal`: filtering, Welch PSD, and frequency-domain processing.
- `matplotlib.pyplot`: plotting ECG waveforms and spectral results.
- `ast.literal_eval`: safely converts stringified label dictionaries into Python objects.

## Important Python Patterns

### Load a CSV metadata file

```python
import pandas as pd
df = pd.read_csv("data/ptbxl_database.csv")
```

### Read a WFDB ECG record

```python
import wfdb
ecg, info = wfdb.rdsamp("data/00001_hr")
```

### Build a time axis

```python
import numpy as np
time = np.arange(ecg.shape[0]) / info["fs"]
```

### Plot one lead

```python
import matplotlib.pyplot as plt
lead_ii = ecg[:, 1]
plt.plot(time, lead_ii)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (mV)")
plt.show()
```

### Compute a power spectral density

```python
from scipy import signal
freqs, psd = signal.welch(lead_ii, fs=info["fs"], nperseg=1024)
```

### Design and apply a bandpass filter

```python
from scipy.signal import butter, filtfilt

def bandpass(x, lowcut, highcut, fs, order=4):
	nyquist = 0.5 * fs
	low = lowcut / nyquist
	high = highcut / nyquist
	b, a = butter(order, [low, high], btype="band")
	return filtfilt(b, a, x)
```

### Apply a notch filter

```python
from scipy.signal import iirnotch, filtfilt

def notch(x, notch_freq, fs, quality_factor=30):
	nyquist = 0.5 * fs
	freq = notch_freq / nyquist
	b, a = iirnotch(freq, quality_factor)
	return filtfilt(b, a, x)
```

## Transferable Skills Learned

- Reading biomedical data from real files rather than synthetic examples.
- Working with multi-channel physiological signals.
- Converting raw samples into a time axis for interpretation.
- Cleaning biosignals with digital filtering.
- Comparing raw and filtered signals in both time and frequency domains.
- Using metadata to connect a waveform to patient and record context.
- Saving figures for reporting and research documentation.
- Building a reproducible analysis workflow with a virtual environment.

## Reusable Workflow for Future Projects

1. Load metadata and inspect the table structure.
2. Read one record and confirm sampling rate, duration, and channels.
3. Plot the full signal first to check quality.
4. Choose one channel for detailed analysis.
5. Filter the signal if noise or drift is present.
6. Compare raw vs filtered traces.
7. Compute a frequency-domain view such as PSD or FFT.
8. Save plots and write short findings in the notes.

## Useful Commands for Future Projects

```bash
mkdir data results SRC
touch SRC/main.py
python -m venv .venv
source .venv/bin/activate
pip freeze > requirements.txt
```

```bash
python -m pip install --upgrade pip
python -m pip install numpy pandas scipy matplotlib wfdb
```

```bash
git status
git diff
```

## Short Reminder

For computational physiology projects, always check:

- What the data source is.
- What the sampling rate is.
- Which channel or lead you are analyzing.
- Whether your filter changes the signal shape too much.
- Whether your plots support the story you want to tell.
