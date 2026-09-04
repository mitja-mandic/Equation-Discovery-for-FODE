import os
from pathlib import Path

import numpy as np

from fitting_parameters.reporting import (
    build_fit_output_paths,
    export_fit_summary,
    plot_circuit_fits,
)
from fitting_parameters.train import LEAST_SQUARES_SETTINGS, compare_circuits
from circuit_export import load_circuits
from fitting_parameters.load_data import raw_impedance, load_spectrum, logarithmic_frequency_indices, uniform_frequency_indices

def normalize_sigma(sigma, percentage_floor=0.1):
    floor = percentage_floor * np.nanmedian(sigma)
    return np.maximum(np.abs(sigma), floor)
    #return np.sqrt(sigma ** 2 + floor ** 2)

PROJECT_DIR = Path(__file__).resolve().parent



# ---------------------------------------------------------------------------
# SELECT INPUT FORMAT
# ---------------------------------------------------------------------------

# Use "raw" for bank4 files containing curr, batt_1, batt_2, etc.
# Use "spectrum" for files containing F and Z.
DATA_MODE = "spectrum"


# ---------------------------------------------------------------------------
# DATA FILES
# ---------------------------------------------------------------------------

RAW_DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "battery"
    / "bank3_20260208-084547_1.npz"
    #/ "bank4_20260208-184533_1.npz"
    #/ "bank2_20260207-224617_0.01.npz"
)

SPECTRUM_DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "spectrum"
    / "eis_20200224_190006.npz"
)

BATTERY_CHANNEL = "batt_4" #bank3 battery 5 is weird, ask Pavle


# ---------------------------------------------------------------------------
# GENERATED CIRCUITS
# ---------------------------------------------------------------------------

#grammar_type = "compact_hybrid"
grammar_type = "no_G_relaxed"
nr_elements = 5
filename_prefix = os.environ.get("FODE_FILENAME_PREFIX", "")


OPTIMIZER = "least_squares"

collection_name = f"{filename_prefix}{grammar_type}"

CIRCUIT_PATH = (PROJECT_DIR
    / "data"
    / "circuits"
    / f"{grammar_type}_elements_{nr_elements}.json"
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
    frequency, measured_impedance, coherence, real_scatter, imag_scatter = raw_impedance(
        RAW_DATA_PATH,
        channel=BATTERY_CHANNEL,
    )
    selected_data_path = RAW_DATA_PATH

    selected = uniform_frequency_indices(frequency, 300)
    #selected = logarithmic_frequency_indices(
    #    frequency,
    #    number_points=400,
    #)

    frequency = frequency[selected]
    measured_impedance = measured_impedance[selected]
    coherence = coherence[selected]
    real_scatter = real_scatter[selected]
    imag_scatter = imag_scatter[selected]


elif DATA_MODE == "spectrum":
    # Already processed frequency-domain data:
    # F and Z
    frequency, measured_impedance, real_scatter, imag_scatter = load_spectrum(
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

floor = 0.002
real_smooth_scatter = normalize_sigma(real_scatter)#, floor)
imag_smooth_scatter = normalize_sigma(imag_scatter)#, floor)

results, fitted_parameters = compare_circuits(
    circuits=circuits,
    frequency=frequency,
    measured_impedance=measured_impedance,
    real_scatter=real_smooth_scatter,
    imag_scatter=imag_smooth_scatter,
    #real_scatter=real_scatter,
    #imag_scatter=imag_scatter,
    optimizer=OPTIMIZER,
)
# ---------------------------------------------------------------------------
# PRINT THE BEST RESULTS
# ---------------------------------------------------------------------------

print("\nBest fitted circuits:\n")

for rank, result in enumerate(results[:5], start=1):
    print(f"{rank}. {result['circuit']}")
    #print(f"   BIC: {result['bic']:.4f}")
    print(f"   lp_error: {result['lp_error']:.6g}")
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

#export_fit_summary(
#    results=results,
#    output_path=summary_path,
#    plot_path=plot_path.relative_to(PROJECT_DIR),
#    dataset_path=selected_data_path.relative_to(PROJECT_DIR),
#    circuit_path=CIRCUIT_PATH.relative_to(PROJECT_DIR),
#    grammar_name=collection_name,
#    maximum_elements=nr_elements,
#    optimizer=OPTIMIZER,
#    optimizer_settings=LEAST_SQUARES_SETTINGS,
#    frequency=frequency,
#)
#
#print(f"Saved plot: {plot_path}")
#print(f"Saved fit summary: {summary_path}")

