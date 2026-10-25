import argparse
import math
from pathlib import Path

from fitting_parameters.reporting import (
    build_fit_output_paths,
    export_fit_summary,
    plot_circuit_fits,
    plot_fit_residuals,
)

from fitting_parameters.train_refactored import LEAST_SQUARES_SETTINGS, FINAL_LEAST_SQUARES_SETTINGS, compare_circuits, count_models_by_num_params
from fitting_parameters.train_refactored import RESIDUAL_SCALE, _residual_scales, NUMBER_INITIAL_STARTS, RANDOM_SEED
from Circuit_generation.circuit_export import load_circuits
from fitting_parameters.load_data import raw_impedance, load_spectrum, load_pcl_spectrum, uniform_frequency_indices
from fitting_parameters.model_selection import normalize_sigma
from Circuit_generation.circuit_class import (
    CPE, Inductor, Parallel, Resistor, Series, SeriesResistance, Warburg,
)

PROJECT_DIR = Path(__file__).resolve().parent
SAVE_RESULTS = False

# ---------------------------------------------------------------------------
# SELECT INPUT FORMAT
# ---------------------------------------------------------------------------

# Use "raw" for bank4 files containing curr, batt_1, batt_2, etc.
# Use "spectrum" for files containing F and Z.
# Use "simulated" for output from data/simulation/run_simulation.py.
# Use "pcl" for processed battery dictionaries with frequency/Z at indices 0/1.
DATA_MODE = "pcl"


# ---------------------------------------------------------------------------
# DATA FILES
# ---------------------------------------------------------------------------

RAW_DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "battery"
    #/ "bank3_20260208-084547_1.npz"
    #/ "bank4_20260208-184533_1.npz"
    #/ "bank2_20260207-224617_0.01.npz"
)

BATTERY_CHANNEL = "batt_1" #bank3 battery 5 is weird, ask Pavle

PCL_DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "battery"
    / "EIS_mitja"
    #/ "eis_bank1_20251126-004055.pcl"
    #/ "eis_bank1_20251112-103715.pcl"
    #/ "eis_bank1_20251027-171541.pcl" #zelo cuden dataset
    / "eis_bank1_20251112-103715.pcl"
)
#eis_bank1_20251112-103715
PCL_BATTERY_CHANNEL = "batt_1"

SPECTRUM_DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "spectrum"
    #/ "eis_20200224_190006.npz" #tu se re-fitting cudno obnasa
    #/ "eis_20200227_030006.npz"
    #/ "eis_20200226_150005.npz"
    #/ "eis_20200227_070006.npz"
    / "eis_20200226_190006.npz"

)

SIMULATED_DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "simulation"
    / "generated"
    / "simulated_spectrum_001.npz"
)


# ---------------------------------------------------------------------------
# GENERATED CIRCUITS
# ---------------------------------------------------------------------------

#grammar_type = "compact_hybrid"
grammar_type ="no_G_relaxed"
nr_elements = 5


OPTIMIZER = "least_squares"
# Refine every circuit with MSE <= best first-round MSE * (1 + this margin).
REOPTIMIZATION_ERROR_MARGIN = 0.20  # 20%; plots still show only the top five.
FILENAME_PREFIX = ""
FILENAME_SUFFIX = "first_round" #fixed_starting_values_no_normalization
FILENAME_SUFFIX_REOPTIMIZED = "reoptimized" #fixed_starting_values_no_normalization
PLOT_TITLE = "Nyquist plot with stratified random starting values, normalized residuals and more robust solver"
PLOT_TITLE_REOPTIMIZED = "Top circuits after reoptimization"

collection_name = f"{FILENAME_PREFIX}{grammar_type}"

CIRCUIT_PATH = (PROJECT_DIR
    / "data"
    / "circuits"
    / f"{grammar_type}_elements_{nr_elements}.json"
)

def positive_float(value: str) -> float:
    """Parse a finite positive command-line value."""
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be finite and greater than zero")
    return number


def nonnegative_float(value: str) -> float:
    """Parse a finite nonnegative command-line value."""
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("must be finite and nonnegative")
    return number


def positive_int(value: str) -> int:
    """Parse a positive integer."""
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def nonnegative_int(value: str) -> int:
    """Parse a nonnegative random seed."""
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be nonnegative")
    return number


def build_parser() -> argparse.ArgumentParser:
    """Expose data, fitting, and reporting options without changing globals."""
    parser = argparse.ArgumentParser(description="Fit and rank impedance circuits.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--data-mode", choices=("raw", "spectrum", "simulated", "pcl"), default=DATA_MODE)
    parser.add_argument("--data-path", type=Path, help="Input file; defaults to the configured path for the selected mode")
    parser.add_argument("--channel", help="Battery channel for raw/PCL data")
    parser.add_argument("--circuit-path", type=Path, help="Circuit JSON; otherwise derived from grammar and elements")
    parser.add_argument("--grammar", default=grammar_type, help="Circuit collection name")
    parser.add_argument("--elements", type=positive_int, default=nr_elements)
    parser.add_argument("--residual-scale", choices=("unscaled", "relative", "magnitude", "scatter"), default=RESIDUAL_SCALE)
    parser.add_argument("--scatter-floor", type=nonnegative_float, default=0, help="Floor passed to normalize_sigma. Only used in data-scaling")
    parser.add_argument("--number-starts", type=positive_int, help = "Number of stratified initial values. Default 5",default=NUMBER_INITIAL_STARTS)
    parser.add_argument("--random-seed", type=nonnegative_int, default=RANDOM_SEED, metavar="SEED")
    parser.add_argument("--reoptimization-error-margin", type=nonnegative_float, help = "What percentage of highest MSE circuits are considered for reoptimization",default=REOPTIMIZATION_ERROR_MARGIN)
    parser.add_argument(
        "--f-scale",
        type=positive_float,
        default=LEAST_SQUARES_SETTINGS["f_scale"],
        help="Soft-L1 transition scale used in both fitting stages",
    )

    parser.add_argument("--save-results", action=argparse.BooleanOptionalAction, default=SAVE_RESULTS)
    parser.add_argument("--show-plots", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--show-residual-plots", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--output-root", type=Path, default=PROJECT_DIR, help="Parent directory for the Results tree")
    parser.add_argument("--filename-prefix", default=FILENAME_PREFIX)
    parser.add_argument("--filename-suffix", default=FILENAME_SUFFIX)
    parser.add_argument("--final-filename-suffix", default=FILENAME_SUFFIX_REOPTIMIZED)
    parser.add_argument("--plot-title", default="Nyquist plot with stratified random starting values and normalized residuals")
    parser.add_argument("--final-plot-title", default="Top circuits after MSE-margin reoptimization")
    parser.add_argument("--sort-first-round", default="wmse", help="Metric by which the first round of optimization is sorted", choices=("bic", "wbic", "ebic", "mse", "wmse"))
    parser.add_argument("--sort-second-round", default="wbic", help="Metric by which the second round of optimization is sorted", choices=("bic", "wbic", "ebic", "mse", "wmse"))
    return parser


def main(argv: list[str] | None = None) -> None:
    """Load the configured data, fit circuits, and report the results."""
    args = build_parser().parse_args(argv)
    DATA_MODE = args.data_mode
    SAVE_RESULTS = args.save_results
    RESIDUAL_SCALE = args.residual_scale
    grammar_type, nr_elements = args.grammar, args.elements
    filename_prefix = args.filename_prefix
    collection_name = f"{filename_prefix}{grammar_type}"
    CIRCUIT_PATH = (args.circuit_path or PROJECT_DIR / "data" / "circuits" / f"{grammar_type}_elements_{nr_elements}.json").resolve()
    defaults = {"raw": RAW_DATA_PATH, "pcl": PCL_DATA_PATH, "spectrum": SPECTRUM_DATA_PATH, "simulated": SIMULATED_DATA_PATH}
    data_path = (args.data_path or defaults[DATA_MODE]).resolve()
    output_root = args.output_root.resolve()
    initial_settings = dict(LEAST_SQUARES_SETTINGS)
    final_settings = dict(FINAL_LEAST_SQUARES_SETTINGS)
    initial_settings["f_scale"] = args.f_scale
    final_settings["f_scale"] = args.f_scale
    sort_first_round = args.sort_first_round
    sort_second_round = args.sort_second_round
    if not SAVE_RESULTS:
        print("Results will not be saved!")

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
            data_path,
            channel=args.channel or BATTERY_CHANNEL,
        )
        selected_data_path = data_path

        selected = uniform_frequency_indices(frequency, args.raw_points)
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
        selected_data_path = data_path
        frequency, measured_impedance, real_scatter, imag_scatter = load_spectrum(
            selected_data_path
        )

        # Coherence is not present in the F/Z files.
        coherence = None

        print(f"Loaded {DATA_MODE} F/Z impedance data from {selected_data_path}")

    elif DATA_MODE == "pcl":
        selected_data_path = data_path
        frequency, measured_impedance, real_scatter, imag_scatter = load_pcl_spectrum(
            selected_data_path, channel=args.channel or PCL_BATTERY_CHANNEL,
        )
        coherence = None
        print(f"Loaded PCL impedance data from {selected_data_path} ({args.channel or PCL_BATTERY_CHANNEL})")
        

    else:
        raise ValueError(
            f"Unknown DATA_MODE {DATA_MODE!r}; "
            "choose 'raw', 'spectrum', 'simulated', or 'pcl'"
        )


    #print(f"Frequency points: {len(frequency)}")
    #print(
    #    f"Frequency range: "
    #    f"{frequency.min():.4g}–{frequency.max():.4g} Hz"
    #)


    # ---------------------------------------------------------------------------
    # FIT AND RANK THE CIRCUITS
    # ---------------------------------------------------------------------------

    floor = args.scatter_floor
    real_smooth_scatter = normalize_sigma(real_scatter, percentage_floor=floor)#, floor)
    imag_smooth_scatter = normalize_sigma(imag_scatter, percentage_floor=floor)#, floor)

    manual_circuit_1 = Series(children=(
        SeriesResistance("Rs"),
        Inductor("L"),
        Parallel(children=(Resistor("R1"), CPE("Q1", "alpha1"))),
        Parallel(children=(Resistor("R2"), CPE("Q2", "alpha2"))),
        Warburg("sigma3"),
    ))

    MANUAL_CIRCUIT = Series(children=(
        SeriesResistance("Rs"),
        Inductor("L"),
        Parallel(children=(Resistor("R1"), CPE("Q1", "alpha1"))),
        Parallel(children=(Resistor("R2"), CPE("Q2", "alpha2"))),
        Parallel(children=(Resistor("R3"), CPE("Q3", "alpha3"))),
    ))
    MANUAL_PARAMETER_COUNT = 8

    circuit_sizes = count_models_by_num_params(circuits)

    results, fitted_parameters, besties = compare_circuits(
        circuits=circuits,
        number_circuit_per_size=circuit_sizes,
        frequency=frequency,
        measured_impedance=measured_impedance,
        real_scatter=real_smooth_scatter,
        imag_scatter=imag_smooth_scatter,
        #real_scatter=real_scatter,
        #imag_scatter=imag_scatter,
        manual_entry=None,
        optimizer=OPTIMIZER,
        reoptimization_error_margin=args.reoptimization_error_margin,
        scale_type=RESIDUAL_SCALE,
        least_squares_settings=initial_settings,
        final_least_squares_settings=final_settings,
        number_starts=args.number_starts, random_seed=args.random_seed,
        sort_first = sort_first_round, sort_second = sort_second_round
    )

    # ---------------------------------------------------------------------------
    # PRINT THE BEST RESULTS
    # ---------------------------------------------------------------------------

    print(f"\nBest fitted circuits and sorted according to {sort_first_round.upper}:\n")

    for rank, result in enumerate(results[:5], start=1):
        print(f"{rank}. {result['circuit']}")
        print(f"   BIC: {result['bic']:.4f}")
        #print(f"   lp_error: {result['lp_error']:.6g}")
        #print(f"   Random start: {result['rand_start']}")
        print(f"   EBIC: {result['ebic']:.6g}")
        print(f"   MSE: {result['mse']:.6g}")
        print(f"   RelMSE: {result['relative_mse']:.6g}")
        print(f"   Success: {result['success']}")
        print(f"   Parameters: {result['parameters']}")
        print()

    print(f"\nBest 5 reoptimized and sorted according to {sort_second_round.upper()}:\n")
    for rank, result in enumerate(besties[:5], start=1):
        print(f"{rank}. {result['circuit']}")
        print(f"   Parameters: {result['parameters']}")
        print(f"   BIC: {result['bic']:.4f}")
        print(f"   EBIC: {result['ebic']:.6g}")
        #print(f"   Random start: {result['rand_start']}")
        print(f"   RelMSE: {result['relative_mse']:.6g}")
        print(f"   MSE: {result['mse']:.6g}")
        print(f"   Success: {result['success']}")
        #print(f"   Parameters: {result['parameters']}")
        #print()
    # ---------------------------------------------------------------------------
    # PLOT THE BEST RESULTS
    # -----------------------


    plot_path, summary_path = build_fit_output_paths(
        project_directory=output_root,
        dataset_path=selected_data_path,
        grammar_name=grammar_type,
        maximum_elements=nr_elements,
        filename_prefix=filename_prefix,
        filename_suffix=args.filename_suffix
    )

    plot_path_converged, summary_path_converged = build_fit_output_paths(
        project_directory=output_root,
        dataset_path=selected_data_path,
        grammar_name=grammar_type,
        maximum_elements=nr_elements,
        filename_prefix=filename_prefix,
        filename_suffix=args.final_filename_suffix
    )


    plot_circuit_fits(
        measured_impedance=measured_impedance,
        results=results,
        output_path=plot_path,
        save_output = SAVE_RESULTS, show=args.show_plots,
        plot_title=args.plot_title
    )

    plot_circuit_fits(
        measured_impedance=measured_impedance,
        results=besties,
        output_path=plot_path_converged,
        save_output = SAVE_RESULTS, show=args.show_plots,
        plot_title=args.final_plot_title
    )

    real_residual_scale, imag_residual_scale = _residual_scales(
        measured_impedance, real_smooth_scatter, imag_smooth_scatter, RESIDUAL_SCALE,
    )
    for stage_results, stage_path, stage_settings, stage_title in (
        (results, plot_path, initial_settings, "First-round residuals"),
        (besties, plot_path_converged, final_settings, "Reoptimized residuals"),
    ):
        residual_path = output_root / "Results" / "Plots" / "Residuals" / (
            stage_path.stem + "_residuals.png"
        )
        plot_fit_residuals(
            frequency, measured_impedance, stage_results, residual_path,
            real_scale=real_residual_scale, imag_scale=imag_residual_scale,
            f_scale=stage_settings["f_scale"], scale_type=RESIDUAL_SCALE,
            plot_title=stage_title, save_output=SAVE_RESULTS, show=args.show_residual_plots,
        )
        if SAVE_RESULTS:
            print(f"Saved residual plot: {residual_path}")

    if SAVE_RESULTS:
        export_fit_summary(
            results=results,
            output_path=summary_path,
            plot_path=plot_path,
            dataset_path=selected_data_path,
            circuit_path=CIRCUIT_PATH,
            grammar_name=collection_name,
            maximum_elements=nr_elements,
            optimizer=OPTIMIZER,
            optimizer_settings=initial_settings,
            frequency=frequency,
        )
        export_fit_summary(
            results=besties,
            output_path=summary_path_converged,
            plot_path=plot_path_converged,
            dataset_path=selected_data_path,
            circuit_path=CIRCUIT_PATH,
            grammar_name=collection_name,
            maximum_elements=nr_elements,
            optimizer=OPTIMIZER,
            optimizer_settings=final_settings,
            frequency=frequency,
        )

        print(f"Saved plot first round: {plot_path}")
        print(f"Saved fit summary first round: {summary_path}")
        print(f"Saved plot second round: {plot_path_converged}")
        print(f"Saved fit summary second round: {summary_path_converged}")
    else:
        print("Fitting done, results not saved")


if __name__ == "__main__":
    main()
