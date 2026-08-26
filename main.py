import heapq
import os
from pathlib import Path

import numpy as np

from fitting_parameters.reporting import (
    build_fit_output_paths,
    export_fit_summary,
    plot_circuit_fits,
)
from fitting_parameters.train import LEAST_SQUARES_SETTINGS, compare_circuits
from fitting_parameters.load_data import load_spectrum

from circuit_export import load_circuits
from fitting_parameters.import_freq_data import raw_impedance


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

PROJECT_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# SELECT INPUT FORMAT
# ---------------------------------------------------------------------------

# Use "raw" for bank4 files containing curr, batt_1, batt_2, etc.
# Use "spectrum" for files containing F and Z.
DATA_MODE = "raw"


# ---------------------------------------------------------------------------
# DATA FILES
# ---------------------------------------------------------------------------

RAW_DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "battery"
    #/ "bank4_20260208-184533_1.npz"
    / "bank3_20260208-084547_1.npz"
)

SPECTRUM_DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "spectrum"
    / "eis_20200224_190006.npz"
)

BATTERY_CHANNEL = "batt_8"


# ---------------------------------------------------------------------------
# GENERATED CIRCUITS
# ---------------------------------------------------------------------------

grammar_type = "compact_hybrid_elements"
nr_elements = 7
filename_prefix = os.environ.get("FODE_FILENAME_PREFIX", "")
OPTIMIZER = "least_squares"

collection_name = f"{filename_prefix}{grammar_type}"

CIRCUIT_PATH = (PROJECT_DIR
    / "data"
    / "circuits"
    / f"{grammar_type}_{nr_elements}.json"
)

circuits = sorted(
    load_circuits(CIRCUIT_PATH),
    key=str,
)

print(f"Loaded {len(circuits)} circuits from:")
print(CIRCUIT_PATH)


# ---------------------------------------------------------------------------
# LOAD THE SELECTED DATA FORMAT
# ---------------------------------------------------------------------------

if DATA_MODE == "raw":
    # Raw time-domain data:
    # fs, curr, batt_1, batt_2, ...
    frequency, measured_impedance, coherence = raw_impedance(
        RAW_DATA_PATH,
        channel=BATTERY_CHANNEL,
    )
    selected_data_path = RAW_DATA_PATH

    selected = logarithmic_frequency_indices(
        frequency,
        number_points=300,
    )

    frequency = frequency[selected]
    measured_impedance = measured_impedance[selected]
    coherence = coherence[selected]

elif DATA_MODE == "spectrum":
    # Already processed frequency-domain data:
    # F and Z
    frequency, measured_impedance = load_spectrum(
        SPECTRUM_DATA_PATH
    )
    selected_data_path = SPECTRUM_DATA_PATH

    # Coherence is not present in the F/Z files.
    coherence = None

    print("Loaded an existing F/Z impedance spectrum")

else:
    raise ValueError(
        f"Unknown DATA_MODE {DATA_MODE!r}; "
        "choose 'raw' or 'spectrum'"
    )


print(f"Frequency points: {len(frequency)}")
print(
    f"Frequency range: "
    f"{frequency.min():.4g}–{frequency.max():.4g} Hz"
)


# ---------------------------------------------------------------------------
# FIT AND RANK THE CIRCUITS
# ---------------------------------------------------------------------------

results, fitted_parameters = compare_circuits(
    circuits=circuits,
    frequency=frequency,
    measured_impedance=measured_impedance,
    optimizer=OPTIMIZER,
)
# ---------------------------------------------------------------------------
# PRINT THE BEST RESULTS
# ---------------------------------------------------------------------------

print("\nBest fitted circuits:\n")

for rank, result in enumerate(results[:5], start=1):
    print(f"{rank}. {result['circuit']}")
    print(f"   BIC: {result['bic']:.4f}")
    print(f"   MSE: {result['mse']:.6g}")
    print(f"   Success: {result['success']}")
    print(f"   Parameters: {result['parameters']}")
    print()

# ---------------------------------------------------------------------------
# PLOT THE BEST RESULTS
# ---------------------------------------------------------------------------

plot_path, summary_path = build_fit_output_paths(
    project_directory=PROJECT_DIR,
    dataset_path=selected_data_path,
    grammar_name=grammar_type,
    maximum_elements=nr_elements,
    filename_prefix=filename_prefix,
)

plot_circuit_fits(
    measured_impedance=measured_impedance,
    results=results,
    output_path=plot_path,
)

export_fit_summary(
    results=results,
    output_path=summary_path,
    plot_path=plot_path.relative_to(PROJECT_DIR),
    dataset_path=selected_data_path.relative_to(PROJECT_DIR),
    circuit_path=CIRCUIT_PATH.relative_to(PROJECT_DIR),
    grammar_name=collection_name,
    maximum_elements=nr_elements,
    optimizer=OPTIMIZER,
    optimizer_settings=LEAST_SQUARES_SETTINGS,
    frequency=frequency,
)

print(f"Saved plot: {plot_path}")
print(f"Saved fit summary: {summary_path}")

