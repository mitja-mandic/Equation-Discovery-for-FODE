from pathlib import Path

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

        for block in impedance_blocks:
            block = np.asarray(block)

            median_real = np.nanmedian(block.real, axis=1) #type: ignore
            median_imaginary = np.nanmedian(block.imag, axis=1) #type: ignore

            median_impedance = median_real + 1j * median_imaginary
            median_blocks.append(median_impedance)

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

    return frequency[valid], impedance[valid]

#x = load_spectrum(r"C:\Users\Mitja\Work\ijs\baterije\FODE for SOFC\Equation-Discovery-for-FODE\data\eis_20200226_190006.npz")
#
#y = [[1],[2]]
#print(np.asarray(y).shape, x[1].shape)