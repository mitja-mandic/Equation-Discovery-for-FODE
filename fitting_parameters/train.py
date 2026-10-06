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

FINAL_LEAST_SQUARES_SETTINGS = {
    "x_scale": "jac",
    "ftol": 1e-8,
    "xtol": 1e-8,
    "gtol": 1e-8,
    "f_scale": 0.001, #Larger f_scale → more residuals behave quadratically; less robust, smaller f_scale → more residuals are downweighted; more robust.
    "max_nfev": 10000,
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

def fit_circuit_parameters_random_start(
    circuit,
    frequency,
    measured_impedance,
    real_scatter,
    imag_scatter,
    least_squares_settings = LEAST_SQUARES_SETTINGS
    #optimizer="least_squares",
):
    '''function that fits parameters for every starting value for a given circuit'''
    starting_values = generate_initial_values(circuit, number_starts=NUMBER_INITIAL_STARTS, random_seed=RANDOM_SEED, deterministic=False)

    attempts = []
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

        physical_x0 = np.array([physical_initial_values[name] for name in names])
        x0 = np.where(is_alpha, physical_x0, np.log(physical_x0))

        result = least_squares(
            residual,
            x0,
            bounds=(lower, upper),
            **least_squares_settings,
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

def finalize_fit(frequency, measured_impedance,
                circuit,
                parameters: dict[str,float],
                sigma_real,
                sigma_imag):
    parameter_names = [y for y in parameters.keys()]
    parameter_values = np.asarray([y for y in parameters.values()])
    is_alpha = np.array([name.startswith("alpha") for name in parameter_names])

    log_initial_values = np.where(is_alpha, parameter_values, np.log(parameter_values)) #logarithm of parameters

    bounds_physical = [physical_bounds(name) for name in parameter_names]
    is_alpha = np.array([name.startswith("alpha") for name in parameter_names])

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
        parameters = dict(zip(parameter_names, to_physical(values)))
        predicted = evaluate_impedance(
            circuit,
            frequency,
            parameters,
        )
        error = predicted - measured_impedance

        if scaled:
            return np.concatenate([error.real/sigma_real, error.imag/sigma_imag])
        else:
            return np.concatenate([error.real, error.imag])
    
    optimization_result = least_squares(
        residual,
        log_initial_values,
        bounds=(lower, upper),
        **FINAL_LEAST_SQUARES_SETTINGS
    )
    parameter_values = to_physical(optimization_result.x)
    parameters = dict(zip(parameter_names, parameter_values))

    predicted = evaluate_impedance(
            circuit,
            frequency,
            parameters,
        )

    score = compute_mse(measured_impedance, predicted)

    final_result = {
        #"start_index": start_index,
        "initial_values": to_physical(log_initial_values),
        "parameters": parameters,
        "result": optimization_result,
        "score": score
    }
    return final_result


def compare_circuits(
    circuits,
    frequency,
    measured_impedance,
    real_scatter,
    imag_scatter,
    manual_entry,
    optimizer="least_squares",
):
    results = []
    circuit_count = len(circuits)
    progress_interval = max(10, min(50, circuit_count // 20))
    start_time = perf_counter()

    for circuit_index, circuit in enumerate(circuits, start=1):
        
        #circuit = add_indexes(circuit)

        #initial_values = set_deterministic_initial_values(circuit)

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
        rand_start = "False" if optimization['start_index'] == 0 else "True"
        error = predicted - measured_impedance
        #med_real = np.median(error.real)
        #med_imag = np.median(error.imag)
        #print(med_real)
        #print(med_imag)

        mse = optimization['score'] #compute_mse(measured_impedance, predicted)
        
        lp_error = compute_weighted_lp(measured_impedance, predicted, real_scatter, imag_scatter, p=2)
        #rmse = np.sqrt(mse)


        n = len(error)
        num_parameters = len(parameters)

        results.append({
            "circuit": circuit,
            "parameters": parameters,
            "predicted_impedance": predicted,
            "wmse": lp_error,
            "mse": mse,
#            "aic": compute_aic(n, mse, num_parameters),
            "bic": compute_bic(n, mse, num_parameters),
#            "aic": compute_aic(n, mse, num_parameters),
            "wbic": compute_bic(n, lp_error, num_parameters),
            "success": result.success,
            "optimizer_status": int(result.status),
            "optimizer_message": str(result.message),
            "function_evaluations": int(result.nfev),
            "rand_start": rand_start
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

    best_results = []

    for result in results[:5]:
        rand_string = result['rand_start']
        circuit = result['circuit']

        optimized = finalize_fit(frequency,measured_impedance,circuit,result['parameters'],real_scatter,imag_scatter)
        #if not result['success']:
        #else:
        #    optimized = result

        parameters = optimized['parameters']
        improved_result = optimized['result']
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
        mse = optimized['score'] #compute_mse(measured_impedance, predicted)
        lp_error = compute_weighted_lp(measured_impedance, predicted, real_scatter, imag_scatter, p=2)
        #rmse = np.sqrt(mse)
        n = len(error)
        num_parameters = len(parameters)
        
        best_results.append({
            "circuit": circuit,
            "parameters": parameters,
            "predicted_impedance": predicted,
            "wmse": lp_error,
            "mse": mse,
#            "aic": compute_aic(n, mse, num_parameters),
            "bic": compute_bic(n, mse, num_parameters),
#            "aic": compute_aic(n, mse, num_parameters),
#            "wbic": compute_bic(n, lp_error, num_parameters),
            "success": improved_result.success,
            "optimizer_status": int(improved_result.status),
            "optimizer_message": str(improved_result.message),
            "function_evaluations": int(improved_result.nfev),
            "rand_start": rand_string
        })

    best_results.sort(key=lambda best_result: best_result["bic"])
    if manual_entry:
        manual_result = fit_circuit_parameters_random_start(manual_entry,frequency,measured_impedance,real_scatter,imag_scatter, FINAL_LEAST_SQUARES_SETTINGS)
        manual_parameters = manual_result['parameters']
        manual_predicted = evaluate_impedance(
            manual_entry,
            frequency,
            manual_parameters,
        )
        manual_result_dict = manual_result['result']       
        mse = manual_result['score'] #compute_mse(measured_impedance, manual_predicted)
        lp_error = compute_weighted_lp(measured_impedance, manual_predicted, real_scatter, imag_scatter, p=2)
        error = manual_predicted - measured_impedance
        n = len(error)
        num_parameters = len(manual_parameters)
        
        best_results.append({
            "circuit": manual_entry,
            "parameters": manual_parameters,
            "predicted_impedance": manual_predicted,
            "wmse": lp_error,
            "mse": mse,
#            "aic": compute_aic(n, mse, num_parameters),
            "bic": compute_bic(n, mse, num_parameters),
#            "aic": compute_aic(n, mse, num_parameters),
#            "wbic": compute_bic(n, lp_error, num_parameters),
            "success": manual_result_dict.success,
            "optimizer_status": int(manual_result_dict.status),
            "optimizer_message": str(manual_result_dict.message),
            "function_evaluations": int(manual_result_dict.nfev),
            "rand_start": "True"
        })
        
    fitted_parameters = {
        str(result["circuit"]): result["parameters"]
        for result in results
    }

    return results, fitted_parameters, best_results
