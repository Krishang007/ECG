from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from data_loader import get_lead, load_metadata, load_record
from preprocessing import bandpass_filter
from qrs_detection import pan_tompkins


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    ROOT
    / "physionet.org"
    / "files"
    / "ptb-xl"
    / "1.0.3"
)

OUTPUT_PATH = (
    ROOT
    / "results"
    / "visual_validation"
)

OUTPUT_PATH.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# RECORDS TO VALIDATE
# ============================================================

VALIDATION_RECORDS = [
    1,
    2,
    11,
    17,
    18,
    20,
]


# ============================================================
# FIND ECG RECORD
# ============================================================

def find_record(df, ecg_id):

    matches = df[
        df["ecg_id"] == ecg_id
    ]

    if len(matches) == 0:
        raise ValueError(
            f"ECG ID {ecg_id} not found."
        )

    return matches.iloc[0]


# ============================================================
# VALIDATE ONE ECG
# ============================================================

def validate_record(record):

    ecg_id = int(record["ecg_id"])

    print(
        f"\nValidating ECG {ecg_id}..."
    )

    # --------------------------------------------------------
    # Load ECG
    # --------------------------------------------------------

    record_path = (
        DATA_PATH
        / record["filename_lr"]
    )

    ecg, info = load_record(
        record_path
    )

    fs = info["fs"]

    # --------------------------------------------------------
    # Extract Lead II
    # --------------------------------------------------------

    lead_II = get_lead(
        ecg,
        "II"
    )

    # --------------------------------------------------------
    # Bandpass filter
    # --------------------------------------------------------

    filtered_ecg = bandpass_filter(
        lead_II,
        lowcut=0.5,
        highcut=40.0,
        sampling_rate=fs,
        order=4,
    )

    # --------------------------------------------------------
    # Pan-Tompkins
    # --------------------------------------------------------

    r_peaks = pan_tompkins(
        filtered_ecg,
        sampling_rate=fs
    )

    r_peak_times = (
        r_peaks / fs
    )

    # --------------------------------------------------------
    # RR intervals
    # --------------------------------------------------------

    if len(r_peaks) >= 2:

        rr_intervals = (
            np.diff(r_peaks) / fs
        )

        mean_rr = np.mean(
            rr_intervals
        )

        heart_rate = (
            60.0 / mean_rr
        )

    else:

        rr_intervals = np.array([])

        mean_rr = np.nan

        heart_rate = np.nan

    # --------------------------------------------------------
    # Time axis
    # --------------------------------------------------------

    time = (
        np.arange(len(lead_II))
        / fs
    )

    # ========================================================
    # FIGURE
    # ========================================================

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(14, 10)
    )

    # ========================================================
    # 1. RAW ECG
    # ========================================================

    axes[0].plot(
        time,
        lead_II
    )

    axes[0].set_title(
        f"ECG {ecg_id} - Raw Lead II"
    )

    axes[0].set_ylabel(
        "Amplitude (mV)"
    )

    axes[0].grid(
        True,
        alpha=0.3
    )

    # ========================================================
    # 2. FILTERED ECG
    # ========================================================

    axes[1].plot(
        time,
        filtered_ecg
    )

    axes[1].set_title(
        "Filtered Lead II (0.5–40 Hz)"
    )

    axes[1].set_ylabel(
        "Amplitude (mV)"
    )

    axes[1].grid(
        True,
        alpha=0.3
    )

    # ========================================================
    # 3. R-PEAK DETECTION
    # ========================================================

    axes[2].plot(
        time,
        filtered_ecg,
        label="Filtered ECG"
    )

    axes[2].scatter(
        r_peak_times,
        filtered_ecg[r_peaks],
        marker="x",
        s=60,
        label="Detected R-peaks"
    )

    axes[2].set_title(
        "Pan-Tompkins R-Peak Detection"
    )

    axes[2].set_xlabel(
        "Time (seconds)"
    )

    axes[2].set_ylabel(
        "Amplitude (mV)"
    )

    axes[2].grid(
        True,
        alpha=0.3
    )

    axes[2].legend()

    # ========================================================
    # METADATA
    # ========================================================

    diagnosis = str(
        record["scp_codes"]
    )

    report = str(
        record["report"]
    )

    metadata_text = (
        f"ECG ID: {ecg_id}\n"
        f"Patient ID: {record['patient_id']}\n"
        f"Age: {record['age']}\n"
        f"Sex: {record['sex']}\n"
        f"Sampling rate: {fs} Hz\n"
        f"Detected R-peaks: {len(r_peaks)}\n"
        f"Mean RR: {mean_rr:.3f} s\n"
        f"Detected HR: {heart_rate:.1f} BPM\n\n"
        f"PTB-XL SCP codes:\n"
        f"{diagnosis}\n\n"
        f"Report:\n"
        f"{report}"
    )

    fig.text(
        0.72,
        0.02,
        metadata_text,
        fontsize=9,
        verticalalignment="bottom"
    )

    # ========================================================
    # FORMAT
    # ========================================================

    fig.suptitle(
        f"PTB-XL Visual Validation - ECG {ecg_id}",
        fontsize=16
    )

    plt.tight_layout(
        rect=[0, 0.16, 1, 0.95]
    )

    # ========================================================
    # SAVE
    # ========================================================

    output_file = (
        OUTPUT_PATH
        / f"ecg_{ecg_id}_validation.png"
    )

    plt.savefig(
        output_file,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {output_file}"
    )

    print(
        f"R-peaks: {len(r_peaks)}"
    )

    if not np.isnan(heart_rate):

        print(
            f"Heart rate: "
            f"{heart_rate:.1f} BPM"
        )

    return {
        "ecg_id": ecg_id,
        "r_peaks": len(r_peaks),
        "mean_rr": mean_rr,
        "heart_rate": heart_rate,
        "output_file": output_file,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("PTB-XL VISUAL VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load metadata
    # --------------------------------------------------------

    df = load_metadata()

    results = []

    # --------------------------------------------------------
    # Validate selected records
    # --------------------------------------------------------

    for ecg_id in VALIDATION_RECORDS:

        record = find_record(
            df,
            ecg_id
        )

        result = validate_record(
            record
        )

        results.append(
            result
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("VISUAL VALIDATION COMPLETE")
    print("=" * 70)

    for result in results:

        print(
            f"ECG {result['ecg_id']:2d} | "
            f"R-peaks: {result['r_peaks']:2d} | "
            f"HR: {result['heart_rate']:.1f} BPM"
        )

    print(
        f"\nPlots saved to:\n"
        f"{OUTPUT_PATH}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()