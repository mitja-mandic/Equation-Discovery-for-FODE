import numpy as np


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

    return frequency[valid], impedance[valid], coherence[valid]