import numpy as np
import scipy.signal as signal
from preprocessing import bandpass_filter, preprocess_ecg


def pan_tompkins(
    ecg,
    sampling_rate,
    filter_method=None,
    return_stages=False,
):
    """
    Simplified Pan-Tompkins-style R-peak detection.

    Parameters
    ----------
    ecg : numpy.ndarray
        Input ECG signal.
    sampling_rate : float
        ECG sampling frequency in Hz.
    filter_method : str or None
        Optional preprocessing method. Supported methods are ``raw``,
        ``butterworth``, ``chebyshev1``, and ``chebyshev2``. If None,
        the input is used unchanged before the Pan-Tompkins bandpass.
    return_stages : bool
        If True, return the detected peaks and intermediate stages.

    Returns:
        np.ndarray or tuple
            Detected R-peak sample indices, optionally followed by a
            dictionary of intermediate processing stages.
    """

    fs = sampling_rate

    # Optional comparison preprocessing. The default preserves the original
    # detector behavior by using the input signal unchanged here.
    if filter_method is None:
        filtered = np.asarray(ecg, dtype=float)
    else:
        filtered = preprocess_ecg(
            ecg,
            sampling_rate=fs,
            method=filter_method,
        )

    # Stage 1: Pan-Tompkins bandpass filtering
    pt_bandpass = bandpass_filter(
        filtered,
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

    # Stage 6: Refine candidate peaks on the selected filtered ECG
    search_window_back = int(0.05 * fs)
    search_window_fwd = int(0.15 * fs)

    true_peaks = []

    for p in peaks:
        start = max(0, p - search_window_back)
        end = min(len(filtered), p + search_window_fwd)

        local_max = start + np.argmax(
            filtered[start:end]
        )

        true_peaks.append(local_max)

    true_peaks = np.array(true_peaks)
    true_peaks = np.unique(true_peaks)

    if return_stages:
        stages = {
            "filtered": filtered,
            "pt_bandpass": pt_bandpass,
            "derivative": derivative,
            "squared": squared,
            "integrated": integrated,
        }
        return true_peaks, stages

    return true_peaks
