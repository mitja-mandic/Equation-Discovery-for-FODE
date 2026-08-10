import numpy as np

def evaluate_impedance(circuit, frequency, parameters):
    omega = 2 * np.pi * frequency
    return circuit.impedance(omega, parameters)