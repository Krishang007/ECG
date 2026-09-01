from pathlib import Path

import numpy as np

from analysis import compute_welch_psd
from data_loader import get_lead, load_metadata, load_record
from preprocessing import bandpass_filter
from qrs_detection import pan_tompkins
from visualization import (
    plot_filtered_signal,
    plot_lead,
    plot_psd,
    plot_r_peaks,
)


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


# ============================================================
# MAIN ECG PIPELINE
# ============================================================

def main():

    print("=" * 60)
    print("PTB-XL ECG ANALYSIS PIPELINE")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Load PTB-XL metadata
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("LOADING METADATA")
    print("=" * 60)

    df = load_metadata()

    print("Number of records:", len(df))
    print("Dataset shape:", df.shape)

    # --------------------------------------------------------
    # 2. Select first ECG record
    # --------------------------------------------------------

    record = df.iloc[0]

    print("\nFirst record:")
    print("ECG ID:", record["ecg_id"])
    print("Patient ID:", record["patient_id"])
    print("Diagnosis:", record["scp_codes"])

    # --------------------------------------------------------
    # 3. Load 100 Hz ECG
    # --------------------------------------------------------

    record_path = DATA_PATH / record["filename_lr"]

    print("\n" + "=" * 60)
    print("LOADING ECG")
    print("=" * 60)

    print("Record path:")
    print(record_path)

    ecg, info = load_record(record_path)

    fs = info["fs"]

    print("\nECG shape:", ecg.shape)
    print("Sampling frequency:", fs, "Hz")
    print("Number of samples:", ecg.shape[0])
    print("Number of leads:", ecg.shape[1])
    print("Duration:", ecg.shape[0] / fs, "seconds")

    # --------------------------------------------------------
    # 4. Extract Lead II
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("SELECTING LEAD II")
    print("=" * 60)

    lead_II = get_lead(ecg, "II")

    print("Lead II shape:", lead_II.shape)

    # --------------------------------------------------------
    # 5. Plot raw Lead II
    # --------------------------------------------------------

    plot_lead(
        lead_II,
        fs,
        title=f"Lead II ECG - Patient {record['patient_id']}",
        filename="ecg_leadII_raw_time.png",
    )

    # --------------------------------------------------------
    # 6. Welch PSD - Raw ECG
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("FREQUENCY DOMAIN - RAW ECG")
    print("=" * 60)

    freqs_raw, psd_raw = compute_welch_psd(
        lead_II,
        fs
    )

    print("PSD calculated successfully.")

    plot_psd(
        freqs_raw,
        [psd_raw],
        ["Raw ECG"],
        title="Power Spectral Density - Raw Lead II",
        filename="ecg_psd_raw.png",
        alphas=[0.7],
    )

    # --------------------------------------------------------
    # 7. Bandpass filtering
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("BANDPASS FILTERING")
    print("=" * 60)

    bandpassed_ecg = bandpass_filter(
        lead_II,
        lowcut=0.5,
        highcut=40.0,
        sampling_rate=fs,
        order=4,
    )

    print("Bandpass filter: 0.5 - 40 Hz")

    # --------------------------------------------------------
    # 8. Notch filtering
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("NOTCH FILTER")
    print("=" * 60)

    # At fs = 100 Hz:
    # Nyquist frequency = 50 Hz.
    # Therefore a 50 Hz notch cannot be applied because
    # the notch frequency must be strictly below Nyquist.

    if 50.0 < fs / 2:

        from preprocessing import notch_filter

        filtered_ecg = notch_filter(
            bandpassed_ecg,
            notch_freq=50.0,
            sampling_rate=fs,
            quality_factor=30,
        )

        print("50 Hz notch filter applied.")

    else:

        filtered_ecg = bandpassed_ecg

        print("50 Hz notch filter skipped.")
        print(f"Sampling frequency: {fs} Hz")
        print(f"Nyquist frequency: {fs / 2} Hz")
        print("Reason: 50 Hz is at the Nyquist frequency.")

    print("Filtering complete.")

    # --------------------------------------------------------
    # 9. Plot filtered ECG
    # --------------------------------------------------------

    plot_lead(
        filtered_ecg,
        fs,
        title=f"Lead II ECG - Patient {record['patient_id']} (Filtered)",
        filename="ecg_leadII_filtered_time.png",
    )

    plot_filtered_signal(
        lead_II,
        filtered_ecg,
        fs,
        title="Lead II ECG - Raw vs Filtered",
        filename="ecg_leadII_filtered_and_raw_time.png",
    )

    # --------------------------------------------------------
    # 10. Welch PSD - Filtered ECG
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("FREQUENCY DOMAIN - FILTERED ECG")
    print("=" * 60)

    freqs_filtered, psd_filtered = compute_welch_psd(
        filtered_ecg,
        fs
    )

    print("Filtered PSD calculated successfully.")

    plot_psd(
        freqs_filtered,
        [psd_filtered],
        ["Filtered ECG"],
        title="Power Spectral Density - Filtered Lead II",
        filename="ecg_psd_filtered.png",
    )

    # --------------------------------------------------------
    # 11. Compare raw vs filtered PSD
    # --------------------------------------------------------

    plot_psd(
        freqs_raw,
        [psd_raw, psd_filtered],
        ["Raw ECG", "Filtered ECG"],
        title="Power Spectral Density - Raw vs Filtered",
        filename="ecg_psd_comparison.png",
        alphas=[0.5, 1.0],
    )

    # --------------------------------------------------------
    # 12. Pan-Tompkins R-peak detection
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("PAN-TOMPKINS QRS DETECTION")
    print("=" * 60)

    r_peaks = pan_tompkins(
        filtered_ecg,
        sampling_rate=fs
    )

    print("\nNumber of detected R-peaks:", len(r_peaks))

    print("\nR-peak sample indices:")
    print(r_peaks)

    # --------------------------------------------------------
    # 13. Convert R-peaks to time
    # --------------------------------------------------------

    r_peak_times = r_peaks / fs

    print("\nR-peak times (seconds):")
    print(r_peak_times)

    # --------------------------------------------------------
    # 14. Calculate RR intervals
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("RR INTERVAL ANALYSIS")
    print("=" * 60)

    if len(r_peaks) >= 2:

        rr_intervals = np.diff(r_peaks) / fs

        print("\nRR intervals (seconds):")
        print(rr_intervals)

        mean_rr = rr_intervals.mean()

        print("\nMean RR interval:")
        print(f"{mean_rr:.3f} seconds")

        # ----------------------------------------------------
        # 15. Calculate heart rate
        # ----------------------------------------------------

        heart_rate = 60.0 / mean_rr

        print("\nMean heart rate:")
        print(f"{heart_rate:.1f} BPM")

    else:

        print("\nNot enough R-peaks to calculate RR intervals.")

    # --------------------------------------------------------
    # 16. Plot R-peaks
    # --------------------------------------------------------

    plot_r_peaks(
        filtered_ecg,
        r_peaks,
        fs,
        title="R-Peak Detection - Pan-Tompkins",
        filename="ecg_rpeaks.png",
    )

    # --------------------------------------------------------
    # 17. Finished
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("ECG PIPELINE COMPLETE")
    print("=" * 60)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()