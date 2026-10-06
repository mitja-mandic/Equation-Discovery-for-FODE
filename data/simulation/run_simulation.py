"""Edit the configuration below, then run this file from your IDE."""

from pathlib import Path
import sys

# Support an IDE's Run File command from any working directory.
PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from Circuit_generation.circuit_class import (
    CPE, Gerischer, Inductor, Parallel, Resistor, Series, SeriesResistance, Warburg,
)
from data.simulation.simulator import frequency_sweep, plot_spectrum, save_spectrum, simulate


# ---------------------------------------------------------------------------
# CONFIGURATION: CIRCUIT AND COMPONENT VALUES (SI units)
# ---------------------------------------------------------------------------
# Connections take tuples of components; nest Series/Parallel as needed.
# Example: Rs + L + (R1 || CPE1) + (R2 || CPE2).
# For an ideal capacitor, use CPE("C1", "alpha1") with alpha1=1 and C1 in F.
CIRCUIT = Series(children=(
    SeriesResistance("Rs"),
    #Inductor("L"),
    Parallel(children=(Resistor("R1"), CPE("Q1", "alpha1"))),
    #Parallel(children=(Resistor("R2"), CPE("Q2", "alpha2"))),
    Warburg("sigma"),
))

PARAMETERS = {
    "Rs": 0.1,       # ohm
    #"L": 1e-6,       # H
    "R1": 0.4,       # ohm
    "Q1": 0.02,      # S * s**alpha1
    "alpha1": 0.85,
    "sigma": 0.01,
    #"R2": 0.8,       # ohm
    #"Q2": 0.5,       # S * s**alpha2
    #"alpha2": 0.7,
}

# ---------------------------------------------------------------------------
# CONFIGURATION: FREQUENCY, NOISE, AND OUTPUT
# ---------------------------------------------------------------------------
MIN_FREQUENCY_HZ = 1e-2
MAX_FREQUENCY_HZ = 1e5
POINTS_PER_DECADE = 30  # 271 logarithmically spaced points over nine decades

ADD_NOISE = True
RELATIVE_NOISE = 0.01  # 1% of |Z|, standard deviation of EACH complex component
ABSOLUTE_NOISE_OHM = 0.0  # optional independent noise floor, combined in quadrature
REPEATS = 20             # fitter takes the median over these measurements
RANDOM_SEED = 42         # integer for reproducibility; None for a fresh draw

OUTPUT_PATH = Path(__file__).resolve().parent / "generated" / "simulated_spectrum.npz"
SAVE_PLOT = True
SHOW_PLOT = True


def main() -> None:
    frequency = frequency_sweep(MIN_FREQUENCY_HZ, MAX_FREQUENCY_HZ, POINTS_PER_DECADE)
    spectrum = simulate(
        CIRCUIT,
        PARAMETERS,
        frequency,
        repeats=REPEATS,
        relative_noise=RELATIVE_NOISE if ADD_NOISE else 0.0,
        absolute_noise_ohm=ABSOLUTE_NOISE_OHM if ADD_NOISE else 0.0,
        seed=RANDOM_SEED,
    )
    path = save_spectrum(spectrum, OUTPUT_PATH)
    print(f"Circuit: {CIRCUIT}")
    print(f"Sweep: {frequency[0]:g} to {frequency[-1]:g} Hz, {len(frequency)} points")
    print(f"Saved {REPEATS} measurements per frequency to {path}")
    if SAVE_PLOT or SHOW_PLOT:
        import matplotlib.pyplot as plt

        figure = plot_spectrum(spectrum)
        if SAVE_PLOT:
            figure.savefig(path.with_suffix(".png"), dpi=160)
        if SHOW_PLOT:
            plt.show()
        plt.close(figure)


if __name__ == "__main__":
    main()
