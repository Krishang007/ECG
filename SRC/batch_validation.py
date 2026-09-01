from pathlib import Path

import numpy as np
import pandas as pd

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


# ============================================================
# TEST MULTIPLE RECORDS
# ============================================================

def test_records(num_records=20):

    df = load_metadata()

    results = []

    print("=" * 70)
    print("PTB-XL MULTI-RECORD VALIDATION")
    print("=" * 70)

    print(f"\nTesting {num_records} records...")

    for index in range(num_records):

        record = df.iloc[index]

        try:

            # ------------------------------------------------
            # Load ECG
            # ------------------------------------------------

            record_path = DATA_PATH / record["filename_lr"]

            ecg, info = load_record(record_path)

            fs = info["fs"]

            # ------------------------------------------------
            # Extract Lead II
            # ------------------------------------------------

            lead_II = get_lead(
                ecg,
                "II"
            )

            # ------------------------------------------------
            # Bandpass filtering
            # ------------------------------------------------

            filtered_ecg = bandpass_filter(
                lead_II,
                lowcut=0.5,
                highcut=40.0,
                sampling_rate=fs,
                order=4,
            )

            # ------------------------------------------------
            # Pan-Tompkins
            # ------------------------------------------------

            r_peaks = pan_tompkins(
                filtered_ecg,
                sampling_rate=fs
            )

            # ------------------------------------------------
            # RR interval analysis
            # ------------------------------------------------

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

                min_rr = np.min(
                    rr_intervals
                )

                max_rr = np.max(
                    rr_intervals
                )

            else:

                mean_rr = np.nan
                heart_rate = np.nan
                min_rr = np.nan
                max_rr = np.nan

            # ------------------------------------------------
            # Store metadata + DSP results
            # ------------------------------------------------

            results.append({

                # ==============================
                # PTB-XL METADATA
                # ==============================

                "ecg_id": record["ecg_id"],
                "patient_id": record["patient_id"],
                "age": record["age"],
                "sex": record["sex"],
                "device": record["device"],

                "report": record["report"],
                "scp_codes": record["scp_codes"],

                "heart_axis": record["heart_axis"],

                "infarction_stadium1":
                    record["infarction_stadium1"],

                "infarction_stadium2":
                    record["infarction_stadium2"],

                "validated_by_human":
                    record["validated_by_human"],

                # ==============================
                # SIGNAL QUALITY
                # ==============================

                "baseline_drift":
                    record["baseline_drift"],

                "static_noise":
                    record["static_noise"],

                "burst_noise":
                    record["burst_noise"],

                "electrodes_problems":
                    record["electrodes_problems"],

                "extra_beats":
                    record["extra_beats"],

                "pacemaker":
                    record["pacemaker"],

                # ==============================
                # ECG FILES
                # ==============================

                "filename_lr":
                    record["filename_lr"],

                "filename_hr":
                    record["filename_hr"],

                # ==============================
                # DSP RESULTS
                # ==============================

                "sampling_rate": fs,

                "r_peaks":
                    len(r_peaks),

                "mean_rr":
                    mean_rr,

                "heart_rate":
                    heart_rate,

                "min_rr":
                    min_rr,

                "max_rr":
                    max_rr,

                "status":
                    "SUCCESS",
            })

            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if not np.isnan(heart_rate):

                print(
                    f"[{index + 1:02d}/{num_records}] "
                    f"ECG {record['ecg_id']} | "
                    f"R-peaks: {len(r_peaks):2d} | "
                    f"HR: {heart_rate:.1f} BPM"
                )

            else:

                print(
                    f"[{index + 1:02d}/{num_records}] "
                    f"ECG {record['ecg_id']} | "
                    f"R-peaks: {len(r_peaks):2d} | "
                    f"HR: N/A"
                )

        except Exception as error:

            # ------------------------------------------------
            # Failed record
            # ------------------------------------------------

            results.append({

                "ecg_id": record["ecg_id"],
                "patient_id": record["patient_id"],
                "age": record["age"],
                "sex": record["sex"],
                "device": record["device"],

                "report": record["report"],
                "scp_codes": record["scp_codes"],

                "heart_axis":
                    record["heart_axis"],

                "infarction_stadium1":
                    record["infarction_stadium1"],

                "infarction_stadium2":
                    record["infarction_stadium2"],

                "validated_by_human":
                    record["validated_by_human"],

                "baseline_drift":
                    record["baseline_drift"],

                "static_noise":
                    record["static_noise"],

                "burst_noise":
                    record["burst_noise"],

                "electrodes_problems":
                    record["electrodes_problems"],

                "extra_beats":
                    record["extra_beats"],

                "pacemaker":
                    record["pacemaker"],

                "filename_lr":
                    record["filename_lr"],

                "filename_hr":
                    record["filename_hr"],

                "sampling_rate": np.nan,

                "r_peaks": np.nan,

                "mean_rr": np.nan,

                "heart_rate": np.nan,

                "min_rr": np.nan,

                "max_rr": np.nan,

                "status":
                    f"FAILED: {error}",
            })

            print(
                f"[{index + 1:02d}/{num_records}] "
                f"ECG {record['ecg_id']} | FAILED"
            )

    return pd.DataFrame(results)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    results = test_records(
        num_records=20
    )

    # ========================================================
    # VALIDATION RESULTS
    # ========================================================

    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    print(
        results[
            [
                "ecg_id",
                "patient_id",
                "age",
                "sex",
                "scp_codes",
                "r_peaks",
                "mean_rr",
                "heart_rate",
                "status",
            ]
        ].to_string(index=False)
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    successful = (
        results["status"] == "SUCCESS"
    ).sum()

    failed = (
        results["status"] != "SUCCESS"
    ).sum()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Records tested: {len(results)}"
    )

    print(
        f"Successful:     {successful}"
    )

    print(
        f"Failed:         {failed}"
    )

    if successful > 0:

        valid_hr = results[
            results["status"] == "SUCCESS"
        ]["heart_rate"]

        print(
            f"Mean detected HR: "
            f"{valid_hr.mean():.1f} BPM"
        )

        print(
            f"Minimum HR: "
            f"{valid_hr.min():.1f} BPM"
        )

        print(
            f"Maximum HR: "
            f"{valid_hr.max():.1f} BPM"
        )

    # ========================================================
    # SAVE CSV
    # ========================================================

    output_file = (
        ROOT
        / "results"
        / "ptbxl_batch_validation.csv"
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    results.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nResults saved to:\n"
        f"{output_file}"
    )

    # ========================================================
    # PRINT CSV CONTENT
    # ========================================================

    print("\n" + "=" * 70)
    print("CSV CONTENT")
    print("=" * 70)

    print(
        results.to_csv(
            index=False
        )
    )