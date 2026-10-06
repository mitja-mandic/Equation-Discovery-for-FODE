import os
from pathlib import Path

from fitting_parameters.reporting import (
    build_fit_output_paths,
    export_fit_summary,
    plot_circuit_fits,
)
from fitting_parameters.train import LEAST_SQUARES_SETTINGS, FINAL_LEAST_SQUARES_SETTINGS, compare_circuits
from circuit_export import load_circuits
from fitting_parameters.load_data import raw_impedance, load_spectrum, uniform_frequency_indices
from fitting_parameters.model_selection import normalize_sigma
from Circuit_generation.circuit_class import (
    CPE, Gerischer, Inductor, Parallel, Resistor, Series, SeriesResistance, Warburg,
)

PROJECT_DIR = Path(__file__).resolve().parent
SAVE_RESULTS = False

if not SAVE_RESULTS:
    print("Results will not be saved!")

# ---------------------------------------------------------------------------
# SELECT INPUT FORMAT
# ---------------------------------------------------------------------------

# Use "raw" for bank4 files containing curr, batt_1, batt_2, etc.
# Use "spectrum" for files containing F and Z.
# Use "simulated" for output from data/simulation/run_simulation.py.
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

BATTERY_CHANNEL = "batt_4" #bank3 battery 5 is weird, ask Pavle

SPECTRUM_DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "spectrum"
    #/ "eis_20200224_190006.npz"
    / "eis_20200227_070006.npz"
    #/ "eis_20200226_150005.npz"
)

SIMULATED_DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "simulation"
    / "generated"
    / "simulated_spectrum.npz"
)


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


elif DATA_MODE in ("spectrum", "simulated"):
    # Measured and simulated spectra share the F/Z format.
    selected_data_path = (
        SIMULATED_DATA_PATH if DATA_MODE == "simulated" else SPECTRUM_DATA_PATH
    )
    frequency, measured_impedance, real_scatter, imag_scatter = load_spectrum(
        selected_data_path
    )

    # Coherence is not present in the F/Z files.
    coherence = None

    print(f"Loaded {DATA_MODE} F/Z impedance data from {selected_data_path}")

else:
    raise ValueError(
        f"Unknown DATA_MODE {DATA_MODE!r}; "
        "choose 'raw', 'spectrum', or 'simulated'"
    )


print(f"Frequency points: {len(frequency)}")
print(
    f"Frequency range: "
    f"{frequency.min():.4g}–{frequency.max():.4g} Hz"
)


# ---------------------------------------------------------------------------
# FIT AND RANK THE CIRCUITS
# ---------------------------------------------------------------------------

floor = 0.1
real_smooth_scatter = normalize_sigma(real_scatter, percentage_floor=floor)#, floor)
imag_smooth_scatter = normalize_sigma(imag_scatter, percentage_floor=floor)#, floor)

#manual_circuit = Series(children=(
#    SeriesResistance("Rs"),
#    Inductor("L"),
#    Parallel(children=(Resistor("R1"), CPE("Q1", "alpha1"))),
#    Parallel(children=(Resistor("R2"), CPE("Q2", "alpha2"))),
#    Warburg("sigma3"),
#))

manual_circuit = Series(children=(
    SeriesResistance("Rs"),
    Inductor("L"),
    Parallel(children=(Resistor("R1"), CPE("Q1", "alpha1"))),
    Parallel(children=(Resistor("R2"), CPE("Q2", "alpha2"))),
    Parallel(children=(Resistor("R3"), CPE("Q3", "alpha3"))),
))


results, fitted_parameters, besties = compare_circuits(
    circuits=circuits,
    frequency=frequency,
    measured_impedance=measured_impedance,
    real_scatter=real_smooth_scatter,
    imag_scatter=imag_smooth_scatter,
    #real_scatter=real_scatter,
    #imag_scatter=imag_scatter,
    manual_entry=manual_circuit,
    optimizer=OPTIMIZER,
)

# ---------------------------------------------------------------------------
# PRINT THE BEST RESULTS
# ---------------------------------------------------------------------------

print("\nBest fitted circuits:\n")

for rank, result in enumerate(results[:5], start=1):
    print(f"{rank}. {result['circuit']}")
    #print(f"   BIC: {result['bic']:.4f}")
    #print(f"   lp_error: {result['lp_error']:.6g}")
    #print(f"   Random start: {result['rand_start']}")
    print(f"   MSE: {result['mse']:.6g}")
    print(f"   Success: {result['success']}")
    print(f"   Parameters: {result['parameters']}")
    print()

print("\nBest 5 reoptimized:\n")
for rank, result in enumerate(besties, start=1):
    print(f"{rank}. {result['circuit']}")
    print(f"   Parameters: {result['parameters']}")
    print(f"   BIC: {result['bic']:.4f}")
    print(f"   WMSE: {result['wmse']:.6g}")
    #print(f"   Random start: {result['rand_start']}")
    print(f"   MSE: {result['mse']:.6g}")
    #print(f"   Success: {result['success']}")
    #print(f"   Parameters: {result['parameters']}")
    #print()
# ---------------------------------------------------------------------------
# PLOT THE BEST RESULTS
# -----------------------

FILENAME_SUFFIX = "extra_numerics" #fixed_starting_values_no_normalization
FILENAME_SUFFIX_REOPTIMIZED = "extra_numerics_converged" #fixed_starting_values_no_normalization
PLOT_TITLE = "Nyquist plot with stratified random starting values, normalized residuals and more robust solver"
PLOT_TITLE_REOPTIMIZED = "Top 5 circuits parameters refitted until convergence"

plot_path, summary_path = build_fit_output_paths(
    project_directory=PROJECT_DIR,
    dataset_path=selected_data_path,
    grammar_name=grammar_type,
    maximum_elements=nr_elements,
    filename_prefix=filename_prefix,
    filename_suffix=FILENAME_SUFFIX
)

plot_path, summary_path = build_fit_output_paths(
    project_directory=PROJECT_DIR,
    dataset_path=selected_data_path,
    grammar_name=grammar_type,
    maximum_elements=nr_elements,
    filename_prefix=filename_prefix,
    filename_suffix=FILENAME_SUFFIX_REOPTIMIZED
)


plot_circuit_fits(
    measured_impedance=measured_impedance,
    results=results,
    output_path=plot_path,
    save_output = True,
    plot_title=PLOT_TITLE
)

plot_circuit_fits(
    measured_impedance=measured_impedance,
    results=besties,
    output_path=plot_path,
    save_output = SAVE_RESULTS,
    plot_title=PLOT_TITLE_REOPTIMIZED
)

if SAVE_RESULTS:
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
    export_fit_summary(
        results=besties,
        output_path=summary_path,
        plot_path=plot_path.relative_to(PROJECT_DIR),
        dataset_path=selected_data_path.relative_to(PROJECT_DIR),
        circuit_path=CIRCUIT_PATH.relative_to(PROJECT_DIR),
        grammar_name=collection_name,
        maximum_elements=nr_elements,
        optimizer=OPTIMIZER,
        optimizer_settings=FINAL_LEAST_SQUARES_SETTINGS,
        frequency=frequency,
    )

    print(f"Saved plot: {plot_path}")
    print(f"Saved fit summary: {summary_path}")
else:
    print("Fitting done, results not saved")

