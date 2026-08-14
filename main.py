import numpy as np
from Circuit_generation.circuit_class import  (CircuitNode, Element, Resistor, SeriesResistance, CPE, Warburg, Inductor, Series, Parallel, Gerischer)
from Circuit_generation.circuit_from_grammar import add_indexes, generate_trees
from fitting_parameters.initialize_parameters import set_initial_values
from fitting_parameters.train import fit_circuit_parameters, evaluate_impedance
from fitting_parameters.load_data import load_spectrum
from fitting_parameters.model_selection import compute_aic, compute_bic
import matplotlib.pyplot as plt

from fitting_parameters.import_freq_data import raw_impedance


from Circuit_generation.custom_generation import GeneratorConfig, LimitedCircuitGenerator

import time

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
    plt.figure(figsize=(16, 9))

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
    #plt.tight_layout()    
    #plt.savefig(f'Plots/Nyquists/{grammar}_{depth}.png', bbox_inches = 'tight', dpi = 300, pad_inches=2)
    plt.show()
grammars = [('compact_hybrid',6), ('relaxed',6), ('compact_only_blocks',6)]



st = time.time()
config = GeneratorConfig(max_elements = 5)
trees = LimitedCircuitGenerator(config).generate()

freq, imp = load_spectrum(r"data\eis_20200224_190006.npz")


results, fitted_parameters = compare_circuits(
    trees,
    freq,
    imp,
)
plot_circuit_fits(imp, results[:10])


et = time.time()

# get the execution time
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')

#circuits, impedance, coherence = raw_impedance(
#    "data/bank4_20260208-184533_1.npz",
#    channel="batt_2",
#)


#
#print(results)
#
#top10_imp = imp[:10]
#
