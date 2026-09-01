import sys
from pathlib import Path

import numpy as np

SRC = Path(__file__).resolve().parent.parent / "SRC"
sys.path.insert(0, str(SRC))

from data_loader import load_metadata, load_record
from qrs_detection import pan_tompkins


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "physionet.org"
    / "files"
    / "ptb-xl"
    / "1.0.3"
)


def test_pan_tompkins_first_record():

    # Load metadata
    df = load_metadata()

    # First 100 Hz record
    record_path = df.iloc[0]["filename_lr"]
    full_path = DATA_PATH / record_path

    # Load ECG
    ecg, info = load_record(full_path)

    # Basic checks
    assert ecg.shape == (1000, 12)
    assert info["fs"] == 100

    # Extract Lead II
    lead_ii = ecg[:, 1]

    assert len(lead_ii) == 1000

    # Detect R-peaks
    r_peaks = pan_tompkins(
        lead_ii,
        info["fs"]
    )

    # Detection checks
    assert isinstance(r_peaks, np.ndarray)
    assert len(r_peaks) > 0

    # Peaks must be valid sample indices
    assert np.all(r_peaks >= 0)
    assert np.all(r_peaks < len(lead_ii))

    # Peaks should be sorted
    assert np.all(np.diff(r_peaks) > 0)