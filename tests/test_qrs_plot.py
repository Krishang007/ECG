import sys
from pathlib import Path

import matplotlib.pyplot as plt

SRC = Path(__file__).resolve().parent.parent / "SRC"
sys.path.insert(0, str(SRC))

from data_loader import load_metadata, load_record
from qrs_detection import pan_tompkins


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "physionet.org"
    / "files"
    / "ptb-xl"
    / "1.0.3"
)


# --------------------------------------------------
# Load first PTB-XL record
# --------------------------------------------------

df = load_metadata()

record_path = df.iloc[0]["filename_lr"]
full_path = DATA_PATH / record_path

ecg, info = load_record(full_path)

fs = info["fs"]

# Lead II
lead_ii = ecg[:, 1]

# Time axis
time = range(len(lead_ii))
time = [t / fs for t in time]


# --------------------------------------------------
# Detect R-peaks
# --------------------------------------------------

r_peaks = pan_tompkins(lead_ii, fs)

peak_times = r_peaks / fs


# --------------------------------------------------
# Plot
# --------------------------------------------------

plt.figure(figsize=(12, 5))

plt.plot(
    time,
    lead_ii,
    label="Lead II"
)

plt.scatter(
    peak_times,
    lead_ii[r_peaks],
    marker="o",
    label="Detected R-peaks"
)

plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude (mV)")
plt.title("PTB-XL Lead II — Pan-Tompkins R-Peak Detection")

plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()