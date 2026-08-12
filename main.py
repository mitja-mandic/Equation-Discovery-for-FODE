import numpy as np
from Circuit_generation.circuit_class import  (CircuitNode, Element, Resistor, SeriesResistance, CPE, Warburg, Inductor, Series, Parallel, Gerischer)
from Circuit_generation.circuit_from_grammar import add_indexes, generate_trees
from fitting_parameters.initialize_parameters import set_initial_values
from fitting_parameters.train import fit_circuit_parameters, evaluate_impedance
from fitting_parameters.load_data import load_spectrum
from fitting_parameters.model_selection import compute_aic, compute_bic
import matplotlib.pyplot as plt

from fitting_parameters.import_freq_data import raw_impedance

#t = Series((SeriesResistance(), Series((Inductor(),CPE()))))
#
#u = add_indexes(t)
#p = set_initial_values(u)

def compare_circuits(
    circuits,
    frequency,
    measured_impedance,
    optimizer="least_squares",
):
    results = []

    for circuit in circuits:
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
        })

    results.sort(key=lambda result: result["bic"])

    fitted_parameters = {
        str(result["circuit"]): result["parameters"]
        for result in results
    }

    return results, fitted_parameters

import matplotlib.pyplot as plt


def plot_circuit_fits(measured_impedance, results):
    plt.figure(figsize=(8, 6))

    plt.scatter(
        measured_impedance.real,
        -measured_impedance.imag,
        facecolors='none', edgecolors='r',
        s=25,
        label="Measured data",
        zorder=10,
    )

    for result in results:
        predicted = result["predicted_impedance"]

        plt.plot(
            predicted.real,
            -predicted.imag,
            label=(
                f'{result["circuit"]} '
                f'(BIC={result["bic"]:.2f})'
            ),
        )

    plt.xlabel("Re(Z)")
    plt.ylabel("-Im(Z)")
    plt.title("Nyquist plot")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

circuits = generate_trees('relaxed_no_G', 7)

freq, imp = load_spectrum(r"data\eis_20200226_190006.npz")


#results, fitted_parameters = compare_circuits(
#    circuits,
#    freq,
#    imp,
#)


frequency, impedance, coherence = raw_impedance(
    "data/bank4_20260208-184533_1.npz",
    channel="batt_2",
)

results, fitted_parameters = compare_circuits(
    circuits,
    freq,
    imp,
)
#
#print(results)
#
#top10_imp = imp[:10]
top10_results = results[:10]
#
plot_circuit_fits(
    imp,
    top10_results,
)