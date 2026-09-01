import scipy.signal as signal


def compute_welch_psd(ecg_signal, fs, nperseg=256, min_segments=4):
    """
    Compute Welch's Power Spectral Density for an ECG signal.

    Welch's method reduces variance (smooths the PSD estimate)
    by averaging across multiple overlapping segments. If
    nperseg ends up close to -- or clamped to -- the full
    signal length, welch() effectively collapses to a single
    periodogram with no averaging, which produces a noisy,
    high-variance estimate. For a quasi-periodic signal like
    ECG, that shows up as a comb of sharp lines at multiples
    of the heart rate, rather than a smooth spectrum.

    To avoid silently losing all averaging on short signals,
    nperseg is capped so that at least `min_segments`
    50%-overlapping segments are used whenever the signal is
    long enough to support it.

    Parameters
    ----------
    ecg_signal : numpy.ndarray
        ECG signal.

    fs : float
        Sampling frequency in Hz.

    nperseg : int
        Requested segment length in samples. Will be reduced
        if needed to guarantee at least `min_segments` segments.

    min_segments : int
        Minimum number of (50%-overlapping) segments to
        average over, when the signal length allows it.

    Returns
    -------
    freqs_welch : numpy.ndarray
    psd : numpy.ndarray
    """

    n = len(ecg_signal)

    # With 50% overlap (scipy's default noverlap = nperseg // 2),
    # the number of segments from a signal of length n is
    # approximately: 1 + (n - nperseg) / (nperseg / 2)
    # Solve for the largest nperseg that still yields
    # min_segments segments (bounded below at a sane minimum).
    max_nperseg_for_min_segments = int(
        n / (1 + (min_segments - 1) / 2)
    )

    effective_nperseg = min(
        nperseg,
        max_nperseg_for_min_segments,
        n
    )

    # Keep a sane floor so very short signals don't collapse
    # nperseg to something degenerate.
    effective_nperseg = max(effective_nperseg, min(32, n))

    freqs_welch, psd = signal.welch(
        ecg_signal,
        fs=fs,
        nperseg=effective_nperseg
    )

    return freqs_welch, psd