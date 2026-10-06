"""Simulate EIS spectra using the project's existing circuit trees."""

from dataclasses import dataclass, fields
import json
from pathlib import Path
from typing import TYPE_CHECKING, Mapping

import numpy as np

from Circuit_generation.circuit_class import (
    CPE, CircuitNode, Gerischer, Inductor, Parallel, Resistor, Series, Warburg,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def validate_circuit(circuit: CircuitNode, parameters: Mapping[str, float]) -> None:
    """Reject empty connections, missing/unused parameters and invalid values."""
    required = set()

    def visit(node: CircuitNode) -> None:
        if isinstance(node, (Series, Parallel)):
            if not node.children:
                raise ValueError("Series and Parallel must contain at least one child.")
            for child in node.children:
                visit(child)
            return
        if not isinstance(node, (Resistor, CPE, Warburg, Inductor, Gerischer)):
            raise TypeError(f"Unsupported circuit element: {type(node).__name__}")
        for field in fields(node):
            name = getattr(node, field.name)
            required.add(name)
            if name not in parameters:
                raise ValueError(f"Missing parameter: {name}")
            value = parameters[name]
            if not np.isscalar(value) or not np.isrealobj(value) or not np.isfinite(value):
                raise ValueError(f"{name} must be a finite real number.")
            if isinstance(node, CPE) and field.name == "exponent":
                if not 0 <= value <= 1:
                    raise ValueError(f"CPE exponent {name} must lie in [0, 1].")
            elif value <= 0:
                raise ValueError(f"{name} must be positive.")

    visit(circuit)
    unused = set(parameters) - required
    if unused:
        raise ValueError(f"Unused parameters: {', '.join(sorted(unused))}")


def frequency_sweep(
    minimum_hz: float = 1e-3,
    maximum_hz: float = 1e6,
    points_per_decade: int = 30,
) -> np.ndarray:
    """Return an ascending log sweep including both endpoints (Hz)."""
    if not (np.isfinite(minimum_hz) and np.isfinite(maximum_hz)):
        raise ValueError("Frequency limits must be finite.")
    if not 0 < minimum_hz < maximum_hz:
        raise ValueError("Require 0 < minimum_hz < maximum_hz.")
    if not isinstance(points_per_decade, (int, np.integer)) or points_per_decade < 1:
        raise ValueError("points_per_decade must be a positive integer.")
    decades = np.log10(maximum_hz) - np.log10(minimum_hz)
    count = int(np.ceil(decades * points_per_decade)) + 1
    logspace = np.geomspace(minimum_hz, maximum_hz, count)
    #linspace = np.linspace(minimum_hz, maximum_hz, count)
    return logspace


@dataclass(frozen=True)
class Spectrum:
    frequency_hz: np.ndarray
    clean_impedance: np.ndarray
    measurements: np.ndarray  # (frequency, repeat), complex ohms
    noise_std_ohm: np.ndarray  # per real/imaginary component, per measurement
    metadata: dict


def simulate(
    circuit: CircuitNode,
    parameters: Mapping[str, float],
    frequency_hz: np.ndarray,
    *,
    repeats: int = 20,
    relative_noise: float = 0.0,
    absolute_noise_ohm: float = 0.0,
    seed: int | None = 42,
) -> Spectrum:
    """Evaluate a circuit and add independent Gaussian real/imaginary noise.

    Each component has standard deviation
    hypot(relative_noise * abs(Z_clean), absolute_noise_ohm).
    Thus relative_noise=0.01 means 1% of |Z| per component per repeat;
    it is not the noise level of the median used by the fitter.
    """
    validate_circuit(circuit, parameters)
    frequency = np.asarray(frequency_hz, dtype=float)
    if frequency.ndim != 1 or not frequency.size:
        raise ValueError("frequency_hz must be a nonempty one-dimensional array.")
    if not np.all(np.isfinite(frequency)) or np.any(frequency <= 0):
        raise ValueError("Frequencies must be finite and positive.")
    if not isinstance(repeats, (int, np.integer)) or repeats < 1:
        raise ValueError("repeats must be a positive integer.")
    for name, value in (("relative_noise", relative_noise), ("absolute_noise_ohm", absolute_noise_ohm)):
        if not np.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and nonnegative.")

    with np.errstate(over="raise", divide="raise", invalid="raise"):
        clean = np.asarray(circuit.impedance(2 * np.pi * frequency, parameters), dtype=complex)
    if clean.shape != frequency.shape or not np.all(np.isfinite(clean)):
        raise ValueError("Circuit produced invalid impedance; check parameters and frequency limits.")
    sigma = np.hypot(relative_noise * np.abs(clean), absolute_noise_ohm)
    rng = np.random.default_rng(seed)
    shape = (frequency.size, repeats)
    noise = sigma[:, None] * (rng.normal(size=shape) + 1j * rng.normal(size=shape))
    measurements = clean[:, None] + noise
    metadata = {
        "circuit": str(circuit),
        "parameters": {name: float(value) for name, value in parameters.items()},
        "frequency_unit": "Hz",
        "impedance_unit": "ohm",
        "repeats": int(repeats),
        "relative_noise": float(relative_noise),
        "absolute_noise_ohm": float(absolute_noise_ohm),
        "seed": None if seed is None else int(seed),
        "noise_model": "independent Gaussian real/imag; sigma=hypot(relative*abs(Z_clean), absolute)",
    }
    return Spectrum(frequency.copy(), clean, measurements, sigma, metadata)


def save_spectrum(spectrum: Spectrum, path: str | Path) -> Path:
    """Save loader-compatible F/Z plus ground truth and JSON metadata.

    Z has shape (1, frequency, repeat), matching load_spectrum's block format.
    All entries can be read with allow_pickle=False. Existing files are replaced.
    """
    path = Path(path)
    if path.suffix.lower() != ".npz":
        raise ValueError("Output path must end in .npz.")
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        F=spectrum.frequency_hz,
        Z=spectrum.measurements[None, :, :],
        Z_clean=spectrum.clean_impedance,
        noise_std_ohm=spectrum.noise_std_ohm,
        metadata_json=json.dumps(spectrum.metadata, indent=2),
    )
    return path


def plot_spectrum(spectrum: Spectrum) -> "Figure":
    """Return a figure with Nyquist, magnitude and phase plots."""
    import matplotlib.pyplot as plt

    measured = np.median(spectrum.measurements.real, axis=1) + 1j * np.median(
        spectrum.measurements.imag, axis=1
    )
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for values, style, label in (
        (spectrum.clean_impedance, "-", "Ground truth"),
        (measured, ".", "Measurement median"),
    ):
        axes[0].plot(values.real, -values.imag, style, label=label)
        axes[1].loglog(spectrum.frequency_hz, np.abs(values), style, label=label)
        axes[2].semilogx(spectrum.frequency_hz, np.angle(values, deg=True), style, label=label)
    axes[0].set(xlabel="Re(Z) [ohm]", ylabel="-Im(Z) [ohm]", title="Nyquist")
    axes[0].set_aspect("equal", adjustable="datalim")
    axes[1].set(xlabel="Frequency [Hz]", ylabel="|Z| [ohm]", title="Bode magnitude")
    axes[2].set(xlabel="Frequency [Hz]", ylabel="Phase [degrees]", title="Bode phase")
    for ax in axes:
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
    fig.tight_layout()
    return fig
