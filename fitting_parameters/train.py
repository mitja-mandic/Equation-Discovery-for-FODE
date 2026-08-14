import numpy as np

from typing import Any

import numpy as np
from scipy.optimize import OptimizeResult, differential_evolution, least_squares, minimize

from fitting_parameters.initialize_parameters import (
    get_parameter_names,
    set_initial_values,
)

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
    x0 = np.array([initial[name] for name in names])

    bounds = [
        (0.01, 1.0) if name.startswith("alpha") else (1e-18, np.inf)
        for name in names
    ]

    def residual(values):
        parameters = dict(zip(names, values))
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
        lower, upper = zip(*bounds)

        result = least_squares(
            residual, #minimize residuals
            x0, #starting values
            bounds=(lower, upper), #parameter bounds for estimations
        )
    else:
        result = minimize(
            objective, #minimize squared errors
            x0, 
            method=optimizer, #choose something else than least_squares
            bounds=bounds,
        )

    fitted_parameters = dict(zip(names, result.x))
    return fitted_parameters, result


print("gell")