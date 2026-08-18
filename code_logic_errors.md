# Code Logic Errors and Mistakes

This file lists the main mistakes, logic issues, and misleading parts in `SRC/main.py`.

## 1. Pan-Tompkins is only partially implemented

- The code says `Pan-Tompkins R-peak Detection`, but it is not a full Pan-Tompkins implementation.
- The real algorithm normally includes a more exact sequence of bandpass filtering, derivative, squaring, moving-window integration, adaptive thresholding, and peak refinement.
- In this project, the detection is a simplified approximation, so the name is more advanced than the implementation.

## 2. The first heart-rate estimate used the wrong peak set

- The script originally computed heart rate from `peaks` instead of `true_peaks`.
- `peaks` are the integrated-envelope maxima, while `true_peaks` are the refined R-peak locations in the filtered ECG.
- That made the heart-rate result less accurate than the final plot suggested.
- This was fixed, but it is still an important logic lesson in the code.

## 3. The R-peak search refinement was easy to break with a typo

- The search-window variable originally had a spelling mistake.
- That kind of typo creates a runtime `NameError` even when the algorithm logic is otherwise correct.
- This shows the detection block is fragile and should be cleaned up into smaller tested functions.

## 4. The script is hardcoded to one record

- `record = df.iloc[0]` always selects the first row.
- `record_path = DATA_PATH / "00001_hr"` is also hardcoded.
- This means the code does not generalize to other ECG files without manual editing.
- A better design would read `filename_hr` from the metadata row and loop over multiple records.

## 5. The project mixes analysis code with reporting code

- The script loads data, processes signals, plots figures, prints metadata, and performs detection all in one file.
- That makes the code harder to test and harder to reuse.
- The logic should be split into functions such as `load_record`, `plot_multilead`, `filter_ecg`, and `detect_r_peaks`.

## 6. Some comments are misleading or outdated

- The code comment for Pan-Tompkins suggests a full standard implementation, but the logic is only a simplified version.
- The note about processing delays being irrelevant is fine conceptually, but it does not belong inside the code logic flow.
- Some comments describe what the code is trying to do rather than what it actually does.

## 7. The script is not robust to missing or different data

- It assumes the ECG file exists and can be read successfully.
- It assumes the first row of the CSV is a valid example record.
- It assumes the lead order matches the hardcoded `LEADS` list.
- It does not check for missing file paths, invalid headers, or empty arrays before processing.

## 8. The plotting code is repetitive

- The same figure setup pattern is repeated for 12-lead plots, raw Lead II, filtered Lead II, PSDs, and peak plots.
- This is not a mathematical bug, but it is a structural mistake because it increases maintenance cost.
- Repeated plotting logic should be wrapped in helper functions.

## 9. The code currently analyzes only one lead in depth

- The full 12-lead record is loaded, but the actual signal analysis is centered on Lead II.
- That is fine for a first project, but it limits the insight you can claim from the dataset.
- The code cannot yet compare across leads or across multiple records.

## 10. Some imports are unused

- `lfilter` is imported but never used.
- `scipy.io` is imported but never used.
- Unused imports are not a logic error by themselves, but they make the script look more complex than it is.

## 11. The output filenames are inconsistent

- One filename contains spaces: `ecg_leadII_filtered and_raw_time.png`.
- This can create awkward file handling later.
- Filenames should be normalized with underscores for easier reuse.

## 12. The analysis is based on only one sample

- The heart rate, plots, and noise conclusions are all based on a single ECG record.
- That is useful for demonstration, but not strong enough for a broader scientific claim.
- The code should eventually support batch analysis across several PTB-XL records.

## Summary

The biggest logic mistakes are:

- labeling the detector as full Pan-Tompkins when it is only a simplified version,
- computing heart rate from the wrong peak array before the fix,
- hardcoding the analysis to one record,
- and keeping too much logic in one long script.

The code works for a first exploratory ECG project, but it still needs cleanup before it becomes a reusable computational physiology pipeline.
