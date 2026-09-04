from pathlib import Path
import heapq
import numpy as np


def load_spectrum(file_path):
    """
    Load one EIS NPZ file and produce one median impedance value
    for every frequency.

    Returns
    -------
    frequency : np.ndarray
        One-dimensional array of frequencies.

    impedance : np.ndarray
        One-dimensional array of complex median impedances.
    """
    file_path = Path(file_path)

    with np.load(file_path, allow_pickle=True) as data:
        frequency = np.asarray(data["F"], dtype=float)
        impedance_blocks = data["Z"]

        median_blocks = []
        sigma_real_overall = []
        sigma_imag_overall = []
        for block in impedance_blocks:
            block = np.asarray(block)

            median_real = np.nanmedian(block.real, axis=1)
            median_imag = np.nanmedian(block.imag, axis=1)

            median_impedance = median_real + 1j * median_imag
            median_blocks.append(median_impedance)

            sigma_real = 1.4826 * np.nanmedian(
                np.abs(block.real - median_real[:, None]),
                axis=1,
            )

            sigma_imag = 1.4826 * np.nanmedian(
                np.abs(block.imag - median_imag[:, None]),
                axis=1,
            )
            sigma_imag_overall.extend(sigma_imag)
            sigma_real_overall.extend(sigma_real)
    impedance = np.concatenate(median_blocks)

    if len(frequency) != len(impedance):
        raise ValueError(
            f"Number of frequencies ({len(frequency)}) does not match "
            f"number of impedance values ({len(impedance)})."
        )

    # Remove frequencies for which no valid measurements were available.
    valid = (
        np.isfinite(frequency)
        & np.isfinite(impedance.real)
        & np.isfinite(impedance.imag)
    )
    sigma_real_overall = np.asarray(sigma_real_overall)
    sigma_imag_overall = np.asarray(sigma_imag_overall)

    return frequency[valid], impedance[valid], sigma_real_overall[valid], sigma_imag_overall[valid]

def raw_impedance(path, channel="batt_1", period_seconds=100):
    with np.load(path, allow_pickle=False) as data:
        fs = float(data["fs"][0])
        current = np.asarray(data["curr"], dtype=float)
        voltage = np.asarray(data[channel], dtype=float)

    samples_per_period = round(period_seconds * fs)
    repeats = min(len(current), len(voltage)) // samples_per_period

    current = current[:repeats * samples_per_period]
    voltage = voltage[:repeats * samples_per_period]

    current = current.reshape(repeats, samples_per_period)
    voltage = voltage.reshape(repeats, samples_per_period)

    # Remove absolute battery voltage and current offset.
    current -= current.mean(axis=1, keepdims=True)
    voltage -= voltage.mean(axis=1, keepdims=True)

    I = np.fft.rfft(current, axis=1)
    V = np.fft.rfft(voltage, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        repeated_impedance = V / I

    median_real = np.nanmedian(repeated_impedance.real, axis=0)
    median_imag = np.nanmedian(repeated_impedance.imag, axis=0)

    mad_real = 1.4826 * np.nanmedian(
        np.abs(repeated_impedance.real - median_real[None, :]),
        axis=0,
    )
    mad_imag = 1.4826 * np.nanmedian(
        np.abs(repeated_impedance.imag - median_imag[None, :]),
        axis=0,
    )

    Sii = np.mean(np.abs(I) ** 2, axis=0)
    Svv = np.mean(np.abs(V) ** 2, axis=0)
    Siv = np.mean(np.conj(I) * V, axis=0)

    impedance = Siv / Sii
    coherence = np.abs(Siv) ** 2 / (Sii * Svv)
    frequency = np.fft.rfftfreq(samples_per_period, 1 / fs)

    # Keep frequencies with adequate excitation and repeatability.
    valid = (
        (frequency > 0)
        & (Sii > 1e-4 * Sii[1:].max())
        & (coherence > 0.98)
    )

    return frequency[valid], impedance[valid], coherence[valid], mad_real[valid], mad_imag[valid]

def logarithmic_frequency_indices(frequency, number_points=300):
    """Select existing samples distributed across log-frequency space."""

    frequency = np.asarray(frequency)

    if np.any(frequency <= 0):
        raise ValueError(
            "Logarithmic downsampling requires positive frequencies."
        )

    if len(frequency) <= number_points:
        return np.arange(len(frequency))

    order = np.argsort(frequency)
    log_frequency = np.log(frequency[order])

    # Always retain the lowest and highest frequencies.
    selected = {0, len(frequency) - 1}

    # Heap entries contain: negative logarithmic gap, left, right.
    intervals = [
        (
            -(log_frequency[-1] - log_frequency[0]),
            0,
            len(frequency) - 1,
        )
    ]

    while len(selected) < number_points:
        _, left, right = heapq.heappop(intervals)

        if right - left <= 1:
            continue

        logarithmic_midpoint = (
            log_frequency[left] + log_frequency[right]
        ) / 2

        insertion = np.searchsorted(
            log_frequency,
            logarithmic_midpoint,
        )

        candidates = [
            index
            for index in (insertion - 1, insertion)
            if left < index < right
        ]

        midpoint = min(
            candidates,
            key=lambda index: abs(
                log_frequency[index] - logarithmic_midpoint
            ),
        )

        selected.add(midpoint)

        if midpoint - left > 1:
            heapq.heappush(
                intervals,
                (
                    -(log_frequency[midpoint] - log_frequency[left]),
                    left,
                    midpoint,
                ),
            )

        if right - midpoint > 1:
            heapq.heappush(
                intervals,
                (
                    -(log_frequency[right] - log_frequency[midpoint]),
                    midpoint,
                    right,
                ),
            )

    # Return original array indices ordered by increasing frequency.
    return order[np.array(sorted(selected))]


def uniform_frequency_indices(frequency, number_points=300):
    """Select existing samples at uniformly spaced frequency ranks."""
    frequency = np.asarray(frequency)

    if frequency.ndim != 1:
        raise ValueError("frequency must be one-dimensional.")

    if number_points < 1:
        raise ValueError("number_points must be at least 1.")

    if len(frequency) <= number_points:
        return np.arange(len(frequency))

    order = np.argsort(frequency)

    # Uniform positions include the lowest and highest frequencies.
    selected = np.linspace(
        0,
        len(frequency) - 1,
        num=number_points,
        dtype=int,
    )

    # Return original array indices ordered by increasing frequency.
    return order[selected]



#def normalize_sigma(sigma, floor):
#    return np.sqrt(sigma ** 2 + floor ** 2)
#
#loc = r"data\spectrum\eis_20200224_190006.npz"
#
#res = load_spectrum(loc)
#
#print(np.mean(res[2]))