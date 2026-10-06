"""Generate a portfolio report from saved batch results; no waveform data needed."""
import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def summarize(source, output_dir):
    data = pd.read_csv(source)
    valid = data[data['status'].eq('SUCCESS')]
    rows = []
    for method, group in data.groupby('filter_method', sort=False):
        ok = group[group['status'].eq('SUCCESS')]
        rows.append(dict(method=method, evaluations=len(group), successful=len(ok),
                         failed=len(group)-len(ok), mean_peaks=ok.r_peaks.mean(),
                         mean_hr_bpm=ok.heart_rate.mean(),
                         mean_rr_std_s=ok.rr_std.mean()))
    summary = pd.DataFrame(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_dir / 'filter_summary.csv', index=False)
    counts = valid.pivot(index='ecg_id', columns='filter_method', values='r_peaks').dropna()
    disagreements = counts.index[counts.nunique(axis=1).gt(1)].tolist()
    lines = ['# ECG filter comparison — results', '',
             f'Source: `{source.name}`. This report summarizes saved outputs; it does not rerun detection.', '',
             f'- Unique records: **{data.ecg_id.nunique()}**',
             f'- Method evaluations: **{len(data)}**',
             f'- Successful executions: **{len(valid)}**', '',
             '| Method | Runs | Failed | Mean peaks | Mean detected HR (BPM) | Mean within-record RR SD (s) |',
             '|---|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['method']} | {r['evaluations']} | {r['failed']} | {r['mean_peaks']:.2f} | {r['mean_hr_bpm']:.2f} | {r['mean_rr_std_s']:.4f} |")
    lines += ['', f'Among {len(counts)} records with results for all represented methods, '
              f'{len(disagreements)} had different peak counts across methods.',
              f'ECG IDs with count disagreement: {", ".join(map(str, disagreements)) or "none"}.', '',
              '## Interpretation', '',
              'The four pipelines execute on this small subset and sometimes produce different beat counts. '
              'Equal counts do not establish equal peak timing. Mean heart rate and RR variability describe '
              'the detector outputs; neither ranks detection accuracy or establishes a best filter.', '',
              '## Limitations and next steps', '',
              'The bundled v1 experiment uses the first 20 metadata records, not a representative sample. '
              'SUCCESS means no processing exception, not a correct detection. '
              'There are no beat-level reference annotations in this evaluation, so sensitivity, precision, '
              'and F1 are not reported. The raw baseline still uses the detector’s internal 5–15 Hz bandpass. '
              'Next: broaden sampling, inspect disagreements, and evaluate against annotated beats.']
    (output_dir / 'SUMMARY.md').write_text('\n'.join(lines)+'\n')
    print(summary.to_string(index=False))
    print(f'Report saved to {output_dir / "SUMMARY.md"}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'results' / 'ptbxl_filter_comparison_4methods.csv')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'results')
    args = parser.parse_args()
    summarize(args.input, args.output_dir)
