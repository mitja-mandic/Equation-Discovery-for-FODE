#from Circuit_generation import circuit_from_grammar
from Circuit_generation.circuit_class import  (CircuitNode, Element, Resistor, SeriesResistance, CPE, Warburg, Inductor, Series, Parallel, Gerischer)
from Circuit_generation.circuit_from_grammar import add_indexes
from fitting_parameters.initialize_parameters import set_initial_values
from fitting_parameters.evaluate_impedance import evaluate_impedance
from fitting_parameters.load_data import load_spectrum


t = Series((SeriesResistance(), Series((Inductor(),CPE()))))

u = add_indexes(t)
p = set_initial_values(u)

data = load_spectrum(r"C:\Users\Mitja\Work\ijs\baterije\FODE for SOFC\Equation-Discovery-for-FODE\data\eis_20200224_190006.npz")


