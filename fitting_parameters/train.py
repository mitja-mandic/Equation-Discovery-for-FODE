import numpy as np
from scipy.optimize import least_squares, minimize
from time import perf_counter

from fitting_parameters.initialize_parameters import (
    get_parameter_names,
    set_deterministic_initial_values,
    generate_initial_values
)
from fitting_parameters.model_selection import compute_aic, compute_bic, compute_mse, compute_weighted_mse, compute_weighted_lp


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
    "method": "trf"
}

POWELL_SETTINGS = {
    "xtol": 1e-4,
    "ftol": 1e-4,
    "maxiter": 100,
    #"maxfev": max(1000, 200 * len(x0)),
    "disp": False,
}

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


def fit_circuit_parameters_fixed_start(
    circuit,
    frequency,
    measured_impedance,
    real_scatter,
    imag_scatter,
    optimizer="least_squares",
):
    '''
    finds best parameters for a circuit for a single set of starting values
    '''


    names = get_parameter_names(circuit)
    initial = set_deterministic_initial_values(circuit)
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

    def residual(values, scaled = True):
        parameters = dict(zip(names, to_physical(values)))
        predicted = evaluate_impedance(
            circuit,
            frequency,
            parameters,
        )
        error = predicted - measured_impedance

        if scaled:
            return np.concatenate([error.real/real_scatter, error.imag/imag_scatter])
        else:
            return np.concatenate([error.real, error.imag])
        

    def objective(values):
        errors = residual(values)
        return np.sum(errors ** 2)

#    def objective(values):
#            errors = residual(values)
#            return np.sum(np.abs(errors))
        
    if optimizer == "least_squares":
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

def fit_circuit_parameters_random_start(
    circuit,
    frequency,
    measured_impedance,
    real_scatter,
    imag_scatter,
    #optimizer="least_squares",
):
    '''function that fits parameters for every starting value for a given circuit'''

    attempts = []
    starting_values = generate_initial_values(circuit, number_starts=NUMBER_INITIAL_STARTS, random_seed=RANDOM_SEED)
    names = get_parameter_names(circuit)

    bounds_physical = [physical_bounds(name) for name in names]
    is_alpha = np.array([name.startswith("alpha") for name in names])

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
    
    def residual(values, scaled = True):
        parameters = dict(zip(names, to_physical(values)))
        predicted = evaluate_impedance(
            circuit,
            frequency,
            parameters,
        )
        error = predicted - measured_impedance

        if scaled:
            return np.concatenate([error.real/real_scatter, error.imag/imag_scatter])
        else:
            return np.concatenate([error.real, error.imag])
        
    for start_index, physical_initial_values in enumerate(starting_values):
        #initial_values = np.asarray(physical_initial_values)
        physical_x0 = np.array([physical_initial_values[name] for name in names])
        x0 = np.where(is_alpha, physical_x0, np.log(physical_x0))

        result = least_squares(
            residual,
            x0,
            bounds=(lower, upper),
            **LEAST_SQUARES_SETTINGS,
        )

        parameter_values = to_physical(result.x)
        parameters = dict(zip(names, parameter_values))

        predicted = evaluate_impedance(
            circuit,
            frequency,
            parameters,
        )

        score = compute_mse(measured_impedance,predicted)

        attempts.append({
        "start_index": start_index,
        "initial_values": physical_initial_values,
        "parameters": parameters,
        "result": result,
        "score": score
    })
    
    best_attempt = min(
        attempts,
        key=lambda attempt: attempt["score"],
    )
    return best_attempt
        
def compare_circuits(
    circuits,
    frequency,
    measured_impedance,
    real_scatter,
    imag_scatter,
    optimizer="least_squares",
):
    results = []
    circuit_count = len(circuits)
    progress_interval = max(10, min(50, circuit_count // 20))
    start_time = perf_counter()

    for circuit_index, circuit in enumerate(circuits, start=1):
        #circuit = add_indexes(circuit)

        initial_values = set_deterministic_initial_values(circuit)

        #parameters, optimization = fit_circuit_parameters_fixed_start(
        #    circuit,
        #    frequency,
        #    measured_impedance,
        #    real_scatter=real_scatter,
        #    imag_scatter=imag_scatter,
        #    optimizer=optimizer
        #)

        optimization = fit_circuit_parameters_random_start(
            circuit,
            frequency,
            measured_impedance,
            real_scatter=real_scatter,
            imag_scatter=imag_scatter,
        )
        parameters = optimization['parameters']
        result = optimization['result']
        ## FINAL RESULTS ##
        predicted = evaluate_impedance(
            circuit,
            frequency,
            parameters,
        )

        error = predicted - measured_impedance
        #med_real = np.median(error.real)
        #med_imag = np.median(error.imag)
        #print(med_real)
        #print(med_imag)

        mse = optimization['score'] #compute_mse(measured_impedance, predicted)
        
        lp_error = compute_weighted_lp(measured_impedance, predicted, real_scatter, imag_scatter, p=0.6)
        #rmse = np.sqrt(mse)


        n = len(error)
        num_parameters = len(parameters)

        results.append({
            "circuit": circuit,
            "parameters": parameters,
            "predicted_impedance": predicted,
            "lp_error": lp_error,
            "mse": mse,
#            "aic": compute_aic(n, mse, num_parameters),
            "bic": compute_bic(n, mse, num_parameters),
#            "aic": compute_aic(n, mse, num_parameters),
            "wbic": compute_bic(n, lp_error, num_parameters),
            "success": result.success,
            "optimizer_status": int(result.status),
            "optimizer_message": str(result.message),
            "function_evaluations": int(result.nfev),
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

    results.sort(key=lambda result: result["mse"])

    fitted_parameters = {
        str(result["circuit"]): result["parameters"]
        for result in results
    }

    return results, fitted_parameters
