import numpy as np
from scipy.optimize import least_squares, minimize
from time import perf_counter

from fitting_parameters.initialize_parameters import (
    get_parameter_names,
    set_initial_values,
)
from fitting_parameters.model_selection import compute_aic, compute_bic


LEAST_SQUARES_SETTINGS = {
    "x_scale": "jac",
    "ftol": 1e-6,
    "xtol": 1e-6,
    "gtol": 1e-6,
    "max_nfev": 100,
}

POWELL_SETTINGS = {
    "xtol": 1e-4,
    "ftol": 1e-4,
    "maxiter": 100,
    "maxfev": max(1000, 200 * len(x0)),
    "disp": False,
}

def evaluate_impedance(circuit, frequency, parameters):
    omega = 2 * np.pi * frequency
    return circuit.impedance(omega, parameters)


def fit_circuit_parameters(
    circuit,
    frequency,
    measured_impedance,
    optimizer="least_squares",
):
    names = get_parameter_names(circuit)
    initial = set_initial_values(circuit)
    #x0 = np.array([initial[name] for name in names])

    is_alpha = np.array([name.startswith("alpha") for name in names])
    physical_x0 = np.array([initial[name] for name in names])

    x0 = np.where(is_alpha, physical_x0, np.log(physical_x0))

    #bounds to be removed
    #bounds = [
    #    (0.01, 1.0) if name.startswith("alpha") else (1e-18, np.inf)
    #    for name in names
    #]
    #################

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

    bounds_physical = [physical_bounds(name) for name in names]
    #zipped_physical = zip(bounds_physical, is_alpha)

    lower = np.array([
        lo if alpha else np.log(lo)
        for (lo, _), alpha in zip(bounds_physical, is_alpha)])
    upper = np.array([
        hi if alpha else np.log(hi)
        for (_, hi), alpha in zip(bounds_physical, is_alpha)])

    def to_physical(values):
        physical = values.copy()
        physical[~is_alpha] = np.exp(values[~is_alpha])
        return physical

    def residual(values):
        parameters = dict(zip(names, to_physical(values)))
        predicted = evaluate_impedance(
            circuit,
            frequency,
            parameters,
        )
        error = predicted - measured_impedance

        return np.concatenate([error.real, error.imag])
    def objective(values):
        errors = residual(values)
        return np.sum(errors ** 2)

    if optimizer == "least_squares":
        #lower, upper = zip(*bounds)

        result = least_squares(
            residual, #minimize residuals
            x0, #starting values
            bounds=(lower, upper), #parameter bounds for estimations
            **LEAST_SQUARES_SETTINGS,
        )
    elif optimizer == "powell":
        result = minimize(
            objective,
            x0,
            method=optimizer,
            bounds=list(zip(lower, upper)),
            options=POWELL_SETTINGS,
        )
    else:
        result = minimize(
            objective, #minimize squared errors
            x0, 
            method=optimizer, #choose something else than least_squares
            bounds=list(zip(lower, upper)),
        )

    fitted_parameters = dict(zip(names, to_physical(result.x)))
    return fitted_parameters, result

def compare_circuits(
    circuits,
    frequency,
    measured_impedance,
    optimizer="least_squares",
):
    results = []
    circuit_count = len(circuits)
    progress_interval = max(10, min(50, circuit_count // 20))
    start_time = perf_counter()

    for circuit_index, circuit in enumerate(circuits, start=1):
        #circuit = add_indexes(circuit)

        parameters, optimization = fit_circuit_parameters(
            circuit,
            frequency,
            measured_impedance,
            optimizer=optimizer,
        )

        predicted = evaluate_impedance(
            circuit,
            frequency,
            parameters,
        )

        error = predicted - measured_impedance
        residuals = np.concatenate([error.real, error.imag])

        mse = np.mean(residuals**2)
        n = len(residuals)
        num_parameters = len(parameters)

        results.append({
            "circuit": circuit,
            "parameters": parameters,
            "predicted_impedance": predicted,
            "mse": mse,
            "aic": compute_aic(n, mse, num_parameters),
            "bic": compute_bic(n, mse, num_parameters),
            "success": optimization.success,
            "optimizer_status": int(optimization.status),
            "optimizer_message": str(optimization.message),
            "function_evaluations": int(optimization.nfev),
        })

        if (
            circuit_index == 1
            or circuit_index % progress_interval == 0
            or circuit_index == circuit_count
        ):
            elapsed = perf_counter() - start_time
            remaining = (
                elapsed / circuit_index * (circuit_count - circuit_index)
            )
            print(
                f"Fitted {circuit_index}/{circuit_count} circuits "
                f"({elapsed / 60:.1f} min elapsed, "
                f"{remaining / 60:.1f} min estimated remaining)",
                flush=True,
            )

    results.sort(key=lambda result: result["bic"])

    fitted_parameters = {
        str(result["circuit"]): result["parameters"]
        for result in results
    }

    return results, fitted_parameters
