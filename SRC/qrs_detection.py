import numpy as np
import scipy.signal as signal
from preprocessing import bandpass_filter # I have imported the bandpass_filter function from the preprocessing module


def pan_tompkins(ecg, sampling_rate):
    """
    Simplified Pan-Tompkins-style R-peak detection.

    Returns:
        np.ndarray: Detected R-peak sample indices.
    """

    fs = sampling_rate

    # Stage 1: Bandpass filtering
    pt_bandpass = bandpass_filter(
        ecg,
        5.0,
        15.0,
        fs,
        order=4
    )

    # Stage 2: Five-point derivative
    derivative = np.zeros_like(pt_bandpass)

    for i in range(4, len(pt_bandpass)):
        derivative[i] = (1 / 8) * (
            2 * pt_bandpass[i]
            + pt_bandpass[i - 1]
            - pt_bandpass[i - 3]
            - 2 * pt_bandpass[i - 4]
        )

    # Stage 3: Squaring
    squared = derivative ** 2

    # Stage 4: Moving-window integration
    window_size = int(0.150 * fs)
    window = np.ones(window_size) / window_size

    integrated = np.convolve(
        squared,
        window,
        mode="same"
    )

    # Stage 5: Thresholding and peak detection
    threshold = 0.15 * np.max(integrated)

    peaks, _ = signal.find_peaks(
        integrated,
        height=threshold,
        distance=int(0.2 * fs)
    )

    # Stage 6: Refine candidate peaks on filtered ECG
    search_window_back = int(0.05 * fs)
    search_window_fwd = int(0.15 * fs)

    true_peaks = []

    for p in peaks:
        start = max(0, p - search_window_back)
        end = min(len(ecg), p + search_window_fwd)

        local_max = start + np.argmax(
            ecg[start:end]
        )

        true_peaks.append(local_max)

    true_peaks = np.array(true_peaks)
    true_peaks = np.unique(true_peaks)

    return true_peaks