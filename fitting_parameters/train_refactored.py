"""Refactored copy of train.py; existing callers remain unchanged."""

import numpy as np
from scipy.optimize import least_squares
from time import perf_counter
from fitting_parameters.model_selection import select_refinement_candidates

from fitting_parameters.initialize_parameters import (
    get_parameter_names,
    generate_initial_values
)
from fitting_parameters.model_selection import compute_bic, compute_mse, compute_relative_mse, compute_weighted_lp, compute_ebic

from collections import Counter
from collections.abc import Iterable

from Circuit_generation.circuit_class import CircuitNode

# Fitting configuration: "unscaled", "scatter", "relative", or "magnitude".
# "magnitude" uses max(|Z|, 10% of median positive |Z|) for both components.
RESIDUAL_SCALE = "relative"

NUMBER_INITIAL_STARTS = 6
RANDOM_SEED = 42

LEAST_SQUARES_SETTINGS = {
    "x_scale": "jac",
    "ftol": 1e-6,
    "xtol": 1e-6,
    "gtol": 1e-6,
    "f_scale": 0.001, #Larger f_scale → more residuals behave quadratically; less robust, smaller f_scale → more residuals are downweighted; more robust.
    "max_nfev": 100,
    "loss": "soft_l1",
    #"loss": "linear",
    "method": "trf"
}

FINAL_LEAST_SQUARES_SETTINGS = {
    **LEAST_SQUARES_SETTINGS,
    "ftol": 1e-8,
    "xtol": 1e-8,
    "gtol": 1e-8,
    "max_nfev": 10000,
}


POWELL_SETTINGS = {
    "xtol": 1e-4,
    "ftol": 1e-4,
    "maxiter": 100,
    #"maxfev": max(1000, 200 * len(x0)),
    "disp": False,
}

def count_models_by_num_params(
    circuits: Iterable[CircuitNode],
) -> dict[int, int]:
    """Count candidate circuits by number of fitted circuit parameters.

    Assumes circuits come from the normalized circuit collection.
    Removes duplicate circuit objects using their equality/hash definition.
    Excludes the noise variance from the parameter count.
    """
    return dict(
        Counter(
            len(get_parameter_names(circuit))
            for circuit in set(circuits)
        )
    )

def evaluate_impedance(circuit, frequency, parameters):
    omega = 2 * np.pi * frequency
    return circuit.impedance(omega, parameters)

def physical_bounds(name):
    if name.startswith("alpha"):
        return 0.01, 0.99
    if name == "Rs" or name.startswith(("R", "Rg")):
        return 1e-10, 1e4
    if name.startswith("Q"):
        return 1e-12, 1e6
    if name.startswith("sigma"):
        return 1e-12, 1e6
    if name.startswith("L"):
        return 1e-12, 1e2
    if name.startswith("tau"):
        return 1e-10, 1e10
    raise ValueError(f"No bounds defined for {name!r}")

def _parameter_space(names):
    """Build optimizer bounds and conversions; alpha stays in linear space."""
    is_alpha = np.array([name.startswith("alpha") for name in names])
    bounds = np.array([physical_bounds(name) for name in names])
    bounds[~is_alpha] = np.log(bounds[~is_alpha])

    def to_optimizer(parameters):
        values = np.array([parameters[name] for name in names])
        return np.where(is_alpha, values, np.log(values))

    def to_physical(values):
        physical = values.copy()
        physical[~is_alpha] = np.exp(values[~is_alpha])
        return physical

    return (bounds[:, 0], bounds[:, 1]), to_optimizer, to_physical


def _residual_scales(measured_impedance, real_scatter, imag_scatter, scale_type):
    """Return separate real/imaginary divisors, computed once per fit setup."""
    if scale_type == "unscaled":
        return 1.0, 1.0
    if scale_type == "scatter":
        scales = (real_scatter, imag_scatter)
    elif scale_type == "relative":
        # Use component magnitudes, with a floor of 10% of their median.
        scales = tuple(
            np.maximum(np.abs(component), 0.1 * np.median(np.abs(component)))
            for component in (measured_impedance.real, measured_impedance.imag)
        )
        # An entirely zero component has no relative scale; use unit weight.
        scales = tuple(np.where(scale > 0, scale, 1.0) for scale in scales)
    elif scale_type == "magnitude":
        magnitude = np.abs(measured_impedance)
        positive = magnitude[magnitude > 0]
        # Positive-only median also handles spectra with many zero values.
        # An entirely zero spectrum has no relative scale; use unit weight.
        floor = 0.1 * np.median(positive) if positive.size else 1.0
        shared_scale = np.maximum(magnitude, floor)
        scales = (shared_scale, shared_scale)
    else:
        raise ValueError(
            "scale_type must be 'unscaled', 'scatter', 'relative', or 'magnitude'"
        )
    validated = []
    for scale in scales:
        scale = np.broadcast_to(np.asarray(scale, dtype=float), measured_impedance.shape)
        if not np.all(np.isfinite(scale) & (scale > 0)):
            raise ValueError("Residual scales must be finite and strictly positive")
        validated.append(scale)
    return tuple(validated)


def _make_fitter(
    circuit, frequency, measured_impedance, names, settings,
    real_scatter, imag_scatter, scale_type,
):
    """Share parameter conversion and residual setup across starting points."""
    bounds, to_optimizer, to_physical = _parameter_space(names)
    real_scale, imag_scale = _residual_scales(
        measured_impedance, real_scatter, imag_scatter, scale_type,
    )

    def residual(values):
        parameters = dict(zip(names, to_physical(values)))
        error = evaluate_impedance(circuit, frequency, parameters) - measured_impedance
        #print(f"real: {np.median(error.real)}")
        #print(f"imag: {np.median(error.imag)}")
        return np.concatenate([error.real / real_scale, error.imag / imag_scale])

    def fit(initial_values):
        x0 = to_optimizer(initial_values)
        result = least_squares(residual, x0, bounds=bounds, **settings)
        parameters = dict(zip(names, to_physical(result.x)))
        predicted = evaluate_impedance(circuit, frequency, parameters)
        return {
            "initial_values": to_physical(x0),
            "parameters": parameters,
            "result": result,
            "score": compute_mse(measured_impedance, predicted),
        }

    return fit


def fit_circuit_parameters_random_start(
    circuit,
    frequency,
    measured_impedance,
    real_scatter,
    imag_scatter,
    least_squares_settings=LEAST_SQUARES_SETTINGS,
    *, scale_type=RESIDUAL_SCALE,
    number_starts=NUMBER_INITIAL_STARTS, random_seed=RANDOM_SEED,
):
    """Fit every starting point and return the attempt with the lowest MSE."""
    starting_values = generate_initial_values(
        circuit, number_starts=number_starts,
        random_seed=random_seed, deterministic=False,
    )
    fit = _make_fitter(
        circuit, frequency, measured_impedance,
        get_parameter_names(circuit), least_squares_settings,
        real_scatter, imag_scatter, scale_type,
    )
    attempts = []
    for start_index, initial_values in enumerate(starting_values):
        attempt = fit(initial_values)
        attempt.update(start_index=start_index, initial_values=initial_values)
        attempts.append(attempt)
    return min(attempts, key=lambda attempt: attempt["score"])


def finalize_fit(
    frequency, measured_impedance, circuit, parameters: dict[str, float],
    sigma_real, sigma_imag, *, scale_type=RESIDUAL_SCALE,
    least_squares_settings=FINAL_LEAST_SQUARES_SETTINGS,
):
    """Refine parameters with tighter tolerances, preserving parameter order."""
    fit = _make_fitter(
        circuit, frequency, measured_impedance,
        list(parameters), least_squares_settings,
        sigma_real, sigma_imag, scale_type,
    )
    return fit(parameters)


def _summarize_fit(
    circuit, optimization, frequency, measured_impedance,
    real_scatter, imag_scatter, number_circuit_per_size, rand_start,
    *, gamma=1, manual=False,
):
    """Build the common scoring and optimizer metadata for a fitted circuit."""
    parameters = optimization["parameters"]
    result = optimization["result"]
    predicted = evaluate_impedance(circuit, frequency, parameters)
    mse = optimization["score"]
    lp_error = compute_weighted_lp(
        measured_impedance, predicted, 1, 1,
        p=2 if manual else 0.5,
    )
    n = len(predicted - measured_impedance) * 2
    num_parameters = len(parameters)
    summary = {
        "circuit": circuit,
        "parameters": parameters,
        "predicted_impedance": predicted,
        "wmse": lp_error,
        "mse": mse,
        "bic": compute_bic(n, mse, num_parameters),
        "wbic": compute_bic(n, lp_error, num_parameters),
        "ebic": 0 if manual else compute_ebic(
            len(measured_impedance), mse, num_parameters,
            number_circuit_per_size[num_parameters], gamma=gamma,
        ),
        "ewbic": 0 if manual else compute_ebic(
            len(measured_impedance), lp_error, num_parameters,
            number_circuit_per_size[num_parameters], gamma=gamma,
        ),
        "success": result.success,
        "optimizer_status": int(result.status),
        "optimizer_message": str(result.message),
        "function_evaluations": int(result.nfev),
        "rand_start": rand_start,
    }
    if not manual:
        summary["relative_mse"] = compute_relative_mse(measured_impedance, predicted)
    return summary


def compare_circuits(
    circuits, number_circuit_per_size, frequency, measured_impedance,
    real_scatter, imag_scatter, manual_entry, optimizer="least_squares",
    *, scale_type=RESIDUAL_SCALE,
    reoptimization_error_margin: float = 0.20,
    least_squares_settings=LEAST_SQUARES_SETTINGS,
    final_least_squares_settings=FINAL_LEAST_SQUARES_SETTINGS,
    number_starts=NUMBER_INITIAL_STARTS, random_seed=RANDOM_SEED,
    sort_first = "wmse", sort_second = "wbic"
):
    """Rank by MSE and refine candidates within a fractional margin of the best.

    Scatter and optimizer arguments retain the original public interface.
    scale_type selects unscaled, repeated-measurement scatter, component-relative,
    or shared impedance-magnitude residuals for every fitting stage.
    Ranking metrics are unchanged.
    """
    if not np.isfinite(reoptimization_error_margin) or reoptimization_error_margin < 0:
        raise ValueError("reoptimization_error_margin must be finite and nonnegative")
    results = []
    circuit_count = len(circuits)
    progress_interval = max(10, min(50, circuit_count // 20))
    start_time = perf_counter()

    def summarize(circuit, optimization, rand_start, **options):
        return _summarize_fit(
            circuit, optimization, frequency, measured_impedance,
            real_scatter, imag_scatter, number_circuit_per_size, rand_start,
            **options,
        )

    for circuit_index, circuit in enumerate(circuits, start=1):
        optimization = fit_circuit_parameters_random_start(
            circuit, frequency, measured_impedance, real_scatter, imag_scatter,
            scale_type=scale_type, least_squares_settings=least_squares_settings,
            number_starts=number_starts, random_seed=random_seed,
        )
        rand_start = "False" if optimization["start_index"] == 0 else "True"
        results.append(summarize(circuit, optimization, rand_start))

        if (circuit_index == 1 or circuit_index % progress_interval == 0
                or circuit_index == circuit_count):
            elapsed = perf_counter() - start_time
            remaining = elapsed / circuit_index * (circuit_count - circuit_index)
            print(
                f"Fitted {circuit_index}/{circuit_count} circuits "
                f"({elapsed / 60:.1f} min elapsed, "
                f"{remaining / 60:.1f} min estimated remaining)",
                flush=True,
            )

    results.sort(key=lambda result: result[sort_first])
    best_results = []
    refinement_candidates = select_refinement_candidates(results, reoptimization_error_margin, sort_first)
    print(f"\nReoptimizing {len(refinement_candidates)}/{len(results)} circuits "
          f"within {reoptimization_error_margin:.1%} of the best first-round {sort_first.upper()}.", flush=True)
    for result in refinement_candidates:
        circuit = result["circuit"]
        optimized = finalize_fit(
            frequency, measured_impedance, circuit, result["parameters"],
            real_scatter, imag_scatter, scale_type=scale_type,
            least_squares_settings=final_least_squares_settings,
        )
        best_results.append(
            summarize(circuit, optimized, result["rand_start"], gamma=0.5)
        )
    best_results.sort(key=lambda result: result[sort_second])

    if manual_entry:
        manual_result = fit_circuit_parameters_random_start(
            manual_entry, frequency, measured_impedance, real_scatter,
            imag_scatter, final_least_squares_settings, scale_type=scale_type,
            number_starts=number_starts, random_seed=random_seed,
        )
        best_results.append(summarize(manual_entry, manual_result, "True", manual=True))

    fitted_parameters = {
        str(result["circuit"]): result["parameters"] for result in results
    }
    return results, fitted_parameters, best_results
