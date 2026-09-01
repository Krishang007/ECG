## Python Command Cheat Sheet for Computational Physiology

This project uses Python to load ECG data, inspect metadata, filter signals, and visualize time-domain and frequency-domain behavior. Keep this sheet as a reusable reference for future computational physiology projects.

## Environment Setup

Create and activate a project-local virtual environment from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
which python
python -m pip install --upgrade pip
```

Install the runtime and test dependencies:

```bash
python -m pip install numpy pandas scipy matplotlib wfdb pytest
```

If `requirements.txt` exists, install from it instead:

```bash
python -m pip install -r requirements.txt
```

Verify that the active interpreter can import the required packages:

```bash
python -c "import numpy, pandas, scipy, matplotlib, wfdb, pytest; print('Dependencies OK')"
```

If pytest reports `No module named pytest`, install it into the same interpreter used to run the tests:

```bash
python -m pip install pytest
python -m pytest -q
```

To leave the virtual environment:

```bash
deactivate
```

## Run the Project

```bash
python SRC/main.py
```

If you want to run the script with the project virtual environment explicitly:

```bash
.venv/bin/python SRC/main.py
```

The main script reads the first PTB-XL metadata row, analyzes Lead II, detects QRS peaks, and saves plots in the repository root. Run commands from the repository root so the relative data paths resolve correctly.

## Run Tests

Run the complete test suite with quiet output:

```bash
python -m pytest -q
```

Run one test file or one test function:

```bash
python -m pytest -q tests/test_pan_tompkins.py
python -m pytest -q tests/test_pan_tompkins.py::test_pan_tompkins_first_record
```

Show detailed output and stop at the first failure:

```bash
python -m pytest -vv -x
```

Collect tests without executing them:

```bash
python -m pytest --collect-only -q
```

Note: `tests/test_qrs_plot.py` is an interactive plotting script, not a conventional assertion-based test. Run it directly when visual inspection is needed:

```bash
python tests/test_qrs_plot.py
```

## Validation Scripts

Run batch validation across multiple records:

```bash
python SRC/batch_validation.py
```

Generate validation plots for selected records:

```bash
python SRC/visual_validation.py
```

Generated CSV and image files are written under `results/` by the validation scripts.

## Useful Diagnostics

Confirm the current directory and Python executable:

```bash
pwd
which python
python --version
```

Check that the local PTB-XL files exist:

```bash
ls data/00001_hr.hea data/00001_hr.dat data/ptbxl_database.csv
```

Check installed package versions:

```bash
python -m pip show pytest numpy pandas scipy matplotlib wfdb
```

If imports fail, activate `.venv` again and install packages using `python -m pip`, not a different system `pip` command. If data-loading fails, run the command from the repository root and verify that the PTB-XL files are present.

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
python -m pip install numpy pandas scipy matplotlib wfdb pytest
python -m pip freeze > requirements.txt
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
