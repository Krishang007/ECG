from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

LEADS = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
ROOT = Path(__file__).resolve().parent.parent


def plot_12_leads(ecg, fs, title="12 Lead ECG", filename="ecg_12Leads.png"):
    """Plot all 12 leads of the ECG signal in the time domain."""
    time = np.arange(ecg.shape[0]) / fs
    plt.figure(figsize=(12, 10))

    for lead in range(ecg.shape[1]):
        plt.subplot(12, 1, lead + 1)
        plt.plot(time, ecg[:, lead])
        plt.ylabel(LEADS[lead])

    plt.xlabel("Time (seconds)")
    plt.suptitle(title)
    plt.savefig(ROOT / filename, dpi=300, bbox_inches="tight")
    plt.show()


def plot_lead(ecg_lead, fs, title="Lead ECG", filename="ecg_lead.png"):
    """Plot a single ECG lead."""
    time = np.arange(len(ecg_lead)) / fs
    plt.figure(figsize=(12, 4))
    plt.plot(time, ecg_lead)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude (mV)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.savefig(ROOT / filename, dpi=300, bbox_inches="tight")
    plt.show()


def plot_psd(freqs, psd_list, labels, title="Power Spectral Density", filename="ecg_psd.png", colors=None, alphas=None):
    """Plot Power Spectral Density for one or more signals."""
    plt.figure(figsize=(12, 5))
    
    if colors is None:
        colors = [None] * len(psd_list)
    if alphas is None:
        alphas = [1.0] * len(psd_list)
        
    for psd, label, color, alpha in zip(psd_list, labels, colors, alphas):
        if color:
            plt.semilogy(freqs, psd, label=label, color=color, alpha=alpha)
        else:
            plt.semilogy(freqs, psd, label=label, alpha=alpha)

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Power (mV²/Hz)")
    plt.title(title)
    plt.xlim(0, 150)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(ROOT / filename, dpi=300, bbox_inches="tight")
    plt.show()


def plot_filtered_signal(raw_ecg, filtered_ecg, fs, title="Filtered vs Raw ECG", filename="ecg_filtered.png"):
    """Plot raw and filtered ECG signals together."""
    time = np.arange(len(raw_ecg)) / fs
    plt.figure(figsize=(12, 5))
    plt.plot(time, raw_ecg, label="Raw ECG", alpha=0.5)
    plt.plot(time, filtered_ecg, label="Filtered ECG", color="red")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (mV)")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(ROOT / filename, dpi=300, bbox_inches="tight")
    plt.show()


def plot_r_peaks(ecg, r_peaks, fs, title="R-peak Detection", filename="ecg_rpeaks.png"):
    """Plot the ECG signal with detected R-peaks marked."""
    time = np.arange(len(ecg)) / fs
    plt.figure(figsize=(12, 5))
    plt.plot(time, ecg, label="Filtered ECG", alpha=0.7)
    plt.plot(time[r_peaks], ecg[r_peaks], "rx", markersize=10, label="R-peaks")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (mV)")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(ROOT / filename, dpi=300, bbox_inches="tight")
    plt.show()
