import ast
from pathlib import Path

import pandas as pd
import wfdb


# ============================================================
# PTB-XL ECG DATA LOADER
# ============================================================

LEADS = [
    "I", "II", "III",
    "aVR", "aVL", "aVF",
    "V1", "V2", "V3",
    "V4", "V5", "V6"
]


# ============================================================
# PATHS
# ============================================================

# Project structure:
#
# ECG/
# ├── SRC/
# │   └── data_loader.py
# │
# └── physionet.org/
#     └── files/
#         └── ptb-xl/
#             └── 1.0.3/
#                 ├── ptbxl_database.csv
#                 └── records100/
#
# This automatically finds the ECG project root.

ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    ROOT
    / "physionet.org"
    / "files"
    / "ptb-xl"
    / "1.0.3"
)

METADATA_PATH = DATA_PATH / "ptbxl_database.csv"


# ============================================================
# LOAD METADATA
# ============================================================

def load_metadata():
    """
    Load the PTB-XL metadata CSV.

    Returns
    -------
    pandas.DataFrame
        PTB-XL metadata containing information for all ECG records.
    """

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"\nCould not find PTB-XL metadata:\n"
            f"{METADATA_PATH}\n"
        )

    df = pd.read_csv(METADATA_PATH)

    # Convert SCP diagnostic codes from strings
    # into Python dictionaries.
    df["scp_codes"] = df["scp_codes"].apply(ast.literal_eval)

    return df


# ============================================================
# LOAD A SINGLE ECG RECORD
# ============================================================

def load_record(record_path):
    """
    Load one PTB-XL ECG record.

    Parameters
    ----------
    record_path : str or Path
        Path without .hea or .dat extension.

    Returns
    -------
    ecg : numpy.ndarray
        ECG signal with shape:

            samples x leads

    info : dict
        WFDB record metadata.
    """

    record_path = Path(record_path)

    header_path = Path(str(record_path) + ".hea")
    data_path = Path(str(record_path) + ".dat")

    if not header_path.exists():
        raise FileNotFoundError(
            f"\nECG header file not found:\n"
            f"{header_path}\n"
        )

    if not data_path.exists():
        raise FileNotFoundError(
            f"\nECG data file not found:\n"
            f"{data_path}\n"
        )

    ecg, info = wfdb.rdsamp(str(record_path))

    return ecg, info


# ============================================================
# GET RECORD PATH FROM METADATA
# ============================================================

def get_record_path(df, index):
    """
    Get the local path of a 100 Hz PTB-XL record.

    PTB-XL metadata contains paths such as:

        records100/00000/00001_lr
    """

    relative_path = df.iloc[index]["filename_lr"]

    record_path = DATA_PATH / relative_path

    return record_path


# ============================================================
# LOAD ECG USING METADATA INDEX
# ============================================================

def load_ecg(df, index):
    """
    Load one ECG using its row in the metadata.

    Parameters
    ----------
    df : pandas.DataFrame
        PTB-XL metadata.

    index : int
        Row number of the ECG.

    Returns
    -------
    ecg : numpy.ndarray
        12-lead ECG signal.

    info : dict
        ECG metadata.
    """

    record_path = get_record_path(df, index)

    ecg, info = load_record(record_path)

    return ecg, info


# ============================================================
# SELECT ONE ECG LEAD
# ============================================================

def get_lead(ecg, lead_name):
    """
    Extract one lead from the 12-lead ECG.

    Parameters
    ----------
    ecg : numpy.ndarray
        ECG matrix with shape:

            samples x 12

    lead_name : str
        Lead name, e.g. "II".

    Returns
    -------
    numpy.ndarray
        Selected ECG lead.
    """

    if lead_name not in LEADS:
        raise ValueError(
            f"\nUnknown lead: {lead_name}\n"
            f"Available leads:\n{LEADS}"
        )

    lead_index = LEADS.index(lead_name)

    return ecg[:, lead_index]


# ============================================================
# GET DIAGNOSIS
# ============================================================

def get_diagnosis(df, index):
    """
    Get the SCP diagnostic codes for one ECG.
    """

    return df.iloc[index]["scp_codes"]


# ============================================================
# GET SAMPLING FREQUENCY
# ============================================================

def get_sampling_frequency(info):
    """
    Return the ECG sampling frequency.
    """

    return info["fs"]


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PTB-XL ECG DATA LOADER")
    print("=" * 60)

    # --------------------------------------------------------
    # Check paths
    # --------------------------------------------------------

    print("\nProject root:")
    print(ROOT)

    print("\nPTB-XL data path:")
    print(DATA_PATH)

    print("\nMetadata:")
    print(METADATA_PATH)

    # --------------------------------------------------------
    # Load metadata
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("LOADING METADATA")
    print("=" * 60)

    df = load_metadata()

    print(f"\nNumber of records: {len(df)}")

    # --------------------------------------------------------
    # Show first record
    # --------------------------------------------------------

    print("\nFirst record:")
    print(df.iloc[0])

    # --------------------------------------------------------
    # Get first ECG path
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("LOADING FIRST ECG")
    print("=" * 60)

    record_path = get_record_path(df, 0)

    print("\nRecord path:")
    print(record_path)

    # --------------------------------------------------------
    # Load ECG
    # --------------------------------------------------------

    ecg, info = load_ecg(df, 0)

    # --------------------------------------------------------
    # Display ECG information
    # --------------------------------------------------------

    print("\nECG information:")
    print(f"Shape: {ecg.shape}")
    print(f"Sampling frequency: {info['fs']} Hz")
    print(f"Number of samples: {ecg.shape[0]}")
    print(f"Number of leads: {ecg.shape[1]}")

    # --------------------------------------------------------
    # Verify 12 leads
    # --------------------------------------------------------

    print("\nAvailable leads:")
    for i, lead in enumerate(LEADS):
        print(f"{i}: {lead}")

    # --------------------------------------------------------
    # Extract Lead II
    # --------------------------------------------------------

    lead_ii = get_lead(ecg, "II")

    print("\n" + "=" * 60)
    print("LEAD II")
    print("=" * 60)

    print(f"\nLead II shape: {lead_ii.shape}")

    print("\nFirst 10 samples:")
    print(lead_ii[:10])

    # --------------------------------------------------------
    # Diagnosis
    # --------------------------------------------------------

    diagnosis = get_diagnosis(df, 0)

    print("\n" + "=" * 60)
    print("DIAGNOSIS")
    print("=" * 60)

    print(diagnosis)

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("SUCCESS")
    print("=" * 60)

    print("\nPTB-XL 100 Hz ECG loaded successfully.")
    print("12 leads available.")
    print("Lead II extracted successfully.")