import numpy as np
from scipy.signal import (
    butter,
    cheby1,
    cheby2,
    sosfiltfilt,
    iirnotch,
    tf2sos,
)


# ============================================================
# BANDPASS FILTER
# ============================================================

def bandpass_filter(
    ecg,
    lowcut=0.5,
    highcut=40.0,
    sampling_rate=100,
    order=4
):
    """
    Apply a Butterworth bandpass filter to an ECG signal.

    Uses second-order sections (SOS) rather than the (b, a)
    transfer-function form. For bandpass filters, scipy
    internally doubles the requested order (a bandpass is a
    combined lowpass + highpass), so an order=4 request here
    is realized as an 8th-order filter. At that order, the
    (b, a) polynomial coefficients become numerically
    ill-conditioned -- especially with a low cutoff like
    0.5 Hz close to DC -- which distorts the realized
    frequency response. SOS avoids this by factoring the
    filter into stable 2nd-order stages.

    Parameters
    ----------
    ecg : numpy.ndarray
        ECG signal.

    lowcut : float
        Lower cutoff frequency in Hz.

    highcut : float
        Upper cutoff frequency in Hz.

    sampling_rate : float
        ECG sampling frequency in Hz.

    order : int
        Butterworth filter order.

    Returns
    -------
    numpy.ndarray
        Filtered ECG signal.
    """

    nyquist = 0.5 * sampling_rate

    # Check cutoff frequencies
    if lowcut <= 0 or highcut >= nyquist:
        raise ValueError(
            "Cutoff frequencies must satisfy "
            "0 < lowcut < highcut < Nyquist frequency."
        )

    if lowcut >= highcut:
        raise ValueError(
            "lowcut must be less than highcut."
        )

    # Normalize frequencies
    low = lowcut / nyquist
    high = highcut / nyquist

    # Design Butterworth bandpass filter as second-order sections
    sos = butter(
        order,
        [low, high],
        btype="band",
        output="sos"
    )

    # Zero-phase filtering.
    #
    # sosfiltfilt applies the filter forward and backward,
    # removing phase shift, using the numerically stable
    # SOS representation.
    filtered_ecg = sosfiltfilt(
        sos,
        ecg
    )

    return filtered_ecg

# ============================================================
# CHEBYSHEV TYPE I BANDPASS FILTER
# ============================================================

def chebyshev1_bandpass_filter(
    ecg,
    lowcut=0.5,
    highcut=40.0,
    sampling_rate=100,
    order=4,
    ripple_db=0.5,
):
    """
    Apply a Chebyshev Type I bandpass filter.

    Type I has an equiripple passband and a monotonic
    stopband. It provides a sharper transition than a
    Butterworth filter of the same order.

    Parameters
    ----------
    ecg : numpy.ndarray
        Input ECG signal.
    lowcut, highcut : float
        Bandpass cutoff frequencies in Hz.
    sampling_rate : float
        Sampling frequency in Hz.
    order : int
        Prototype filter order.
    ripple_db : float
        Maximum allowed passband ripple in decibels.

    Returns
    -------
    numpy.ndarray
        Zero-phase filtered ECG.
    """
    nyquist = sampling_rate / 2

    if not 0 < lowcut < highcut < nyquist:
        raise ValueError(
            "Cutoffs must satisfy "
            "0 < lowcut < highcut < Nyquist."
        )

    if order < 1:
        raise ValueError("Filter order must be positive.")

    if ripple_db <= 0:
        raise ValueError("Passband ripple must be positive.")

    sos = cheby1(
        order,
        ripple_db,
        [lowcut, highcut],
        btype="bandpass",
        fs=sampling_rate,
        output="sos",
    )

    return sosfiltfilt(sos, np.asarray(ecg, dtype=float))


# ============================================================
# CHEBYSHEV TYPE II BANDPASS FILTER
# ============================================================

def chebyshev2_bandpass_filter(
    ecg,
    lowcut=0.5,
    highcut=40.0,
    sampling_rate=100,
    order=4,
    attenuation_db=40,
):
    """
    Apply a Chebyshev Type II bandpass filter.

    Type II has a monotonic passband and an equiripple
    stopband. attenuation_db specifies the minimum stopband
    attenuation.

    Returns
    -------
    numpy.ndarray
        Zero-phase filtered ECG.
    """
    nyquist = sampling_rate / 2

    if not 0 < lowcut < highcut < nyquist:
        raise ValueError(
            "Cutoffs must satisfy "
            "0 < lowcut < highcut < Nyquist."
        )

    if order < 1:
        raise ValueError("Filter order must be positive.")

    if attenuation_db <= 0:
        raise ValueError(
            "Stopband attenuation must be positive."
        )

    sos = cheby2(
        order,
        attenuation_db,
        [lowcut, highcut],
        btype="bandpass",
        fs=sampling_rate,
        output="sos",
    )

    return sosfiltfilt(sos, np.asarray(ecg, dtype=float))
# ============================================================
# NOTCH FILTER
# ============================================================

def notch_filter(
    ecg,
    notch_freq,
    sampling_rate,
    quality_factor=30
):
    """
    Apply a notch filter to remove powerline interference.

    iirnotch produces a 2nd-order filter, so the (b, a) form
    is numerically fine here. It's converted to SOS anyway
    for consistency with bandpass_filter and to keep the
    zero-phase filtering path uniform across the module.

    Parameters
    ----------
    ecg : numpy.ndarray
        ECG signal.

    notch_freq : float
        Frequency to remove, typically 50 or 60 Hz.

    sampling_rate : float
        ECG sampling frequency.

    quality_factor : float
        Controls the width of the notch.

    Returns
    -------
    numpy.ndarray
        Filtered ECG signal.
    """

    nyquist = 0.5 * sampling_rate

    # Check notch frequency
    if notch_freq <= 0 or notch_freq >= nyquist:
        raise ValueError(
            "Notch frequency must be between "
            "0 and the Nyquist frequency."
        )

    # Normalize frequency
    freq = notch_freq / nyquist

    # Design notch filter, then convert to SOS
    b, a = iirnotch(
        freq,
        quality_factor
    )

    sos = tf2sos(b, a)

    # Zero-phase filtering
    filtered_ecg = sosfiltfilt(
        sos,
        ecg
    )

    return filtered_ecg


# ============================================================
# COMPLETE ECG PREPROCESSING
# ============================================================

def preprocess_ecg(
    ecg,
    sampling_rate=100,
    method="butterworth",
    lowcut=0.5,
    highcut=40.0,
):
    """
    Preprocess an ECG using the selected filtering method.

    Supported methods:
        raw
        butterworth
        chebyshev1
        chebyshev2
    """
    methods = {
        "raw": lambda signal: np.asarray(
            signal,
            dtype=float,
        ).copy(),

        "butterworth": lambda signal: bandpass_filter(
            signal,
            lowcut=lowcut,
            highcut=highcut,
            sampling_rate=sampling_rate,
            order=4,
        ),

        "chebyshev1": lambda signal: chebyshev1_bandpass_filter(
            signal,
            lowcut=lowcut,
            highcut=highcut,
            sampling_rate=sampling_rate,
            order=4,
            ripple_db=0.5,
        ),

        "chebyshev2": lambda signal: chebyshev2_bandpass_filter(
            signal,
            lowcut=lowcut,
            highcut=highcut,
            sampling_rate=sampling_rate,
            order=4,
            attenuation_db=40,
        ),
    }

    if method not in methods:
        valid = ", ".join(methods)
        raise ValueError(
            f"Unknown method '{method}'. Valid methods: {valid}"
        )

    filtered_ecg = methods[method](ecg)

    if not np.all(np.isfinite(filtered_ecg)):
        raise ValueError(
            f"{method} produced NaN or infinite values."
        )

    return filtered_ecg


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    
    from data_loader import (
        load_metadata,
        load_ecg,
        get_lead
    )

    print("=" * 60)
    print("ECG PREPROCESSING TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Load metadata
    # --------------------------------------------------------

    df = load_metadata()

    print("\nPTB-XL records:")
    print(len(df))

    # --------------------------------------------------------
    # Load first ECG
    # --------------------------------------------------------

    ecg, info = load_ecg(
        df,
        0
    )

    sampling_rate = info["fs"]

    print("\nRaw ECG:")
    print(f"Shape: {ecg.shape}")
    print(f"Sampling rate: {sampling_rate} Hz")

    # --------------------------------------------------------
    # Extract Lead II
    # --------------------------------------------------------

    lead_ii = get_lead(
        ecg,
        "II"
    )

    print("\nRaw Lead II:")
    print(f"Shape: {lead_ii.shape}")

    filter_methods = [
        "raw",
        "butterworth",
        "chebyshev1",
        "chebyshev2",
    ]

    results = {}

    for method in filter_methods:
        filtered = preprocess_ecg(
            lead_ii,
            sampling_rate=sampling_rate,
            method=method,
        )
        results[method] = filtered

        print(f"\nMethod: {method}")
        print(f"Shape: {filtered.shape}")
        print(f"Finite: {np.all(np.isfinite(filtered))}")
        print(f"Minimum: {np.min(filtered):.6f}")
        print(f"Maximum: {np.max(filtered):.6f}")
        print(f"Mean: {np.mean(filtered):.6f}")
        print(f"Standard deviation: {np.std(filtered):.6f}")

    for method, filtered in results.items():
        assert filtered.shape == lead_ii.shape, (
            f"{method} changed the signal shape: "
            f"{filtered.shape} != {lead_ii.shape}"
        )
        assert np.all(np.isfinite(filtered)), (
            f"{method} produced NaN or infinite values"
        )

    print("\nALL FILTER TESTS PASSED")

    # --------------------------------------------------------
    # Preprocess Lead II
    # --------------------------------------------------------

    filtered_lead_ii = preprocess_ecg(
        lead_ii,
        sampling_rate=sampling_rate
    )

    print("\nFiltered Lead II:")
    print(f"Shape: {filtered_lead_ii.shape}")

    # --------------------------------------------------------
    # Display samples
    # --------------------------------------------------------

    print("\nRaw samples:")
    print(lead_ii[:10])

    print("\nFiltered samples:")
    print(filtered_lead_ii[:10])

    print("\n" + "=" * 60)
    print("PREPROCESSING SUCCESS")
    print("=" * 60)
