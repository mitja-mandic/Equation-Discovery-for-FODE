from Circuit_generation.circuit_class import (
    CircuitNode,
    Resistor,
    SeriesResistance,
    CPE,
    Warburg,
    Inductor,
    Gerischer,
    Series,
    Parallel,
)

import numpy as np
import hashlib

LOG10_PERTURBATION_HALF_WIDTHS = {
    "Rs": 1.0,
    "R": 2.0,
    "Rg": 2.0,
    "Q": 2.0,
    "sigma": 2.0,
    "L": 2.0,
    "tau": 2.0,
}

ALPHA_INITIAL_RANGE = (0.3, 0.98)

def get_parameter_names(circuit: CircuitNode):
    """Return the parameter names required by a circuit."""

    if isinstance(circuit, SeriesResistance):
        return (circuit.resistance,)

    if isinstance(circuit, Resistor):
        return (circuit.resistance,)

    if isinstance(circuit, CPE):
        return (
            circuit.coefficient,
            circuit.exponent,
        )

    if isinstance(circuit, Warburg):
        return (circuit.coefficient,)

    if isinstance(circuit, Inductor):
        return (circuit.inductance,)

    if isinstance(circuit, Gerischer):
        return (
            circuit.resistance,
            circuit.time_constant,
        )

    if isinstance(circuit, (Series, Parallel)):
        names = []

        for child in circuit.children:
            names.extend(get_parameter_names(child))

        # Remove duplicates while preserving order.
        return tuple(dict.fromkeys(names))

    raise TypeError(
        f"Unsupported circuit type: {type(circuit).__name__}"
    )


def set_deterministic_initial_values(circuit):
    """
    Create initial values for every parameter required by a circuit.

    Parameters
    ----------
    circuit
        Circuit object exposing a parameter_names attribute.

    Returns
    -------
    dict
        Mapping from parameter names to initial values.
    """
    parameters = {}
    for name in get_parameter_names(circuit):
        if name == "Rs":
            parameters[name] = 0.05
#               parameters[name] = 0.001
        elif name.startswith("Rg"):
            parameters[name] = 0.02
#               parameters[name] = 0.1
        elif name.startswith("R"):
            parameters[name] = 0.02
#               parameters[name] = 0.04
        elif name.startswith("Q"):
            parameters[name] = 1.0
        elif name.startswith("alpha"):
            parameters[name] = 0.8
#               parameters[name] = 0.2
        elif name.startswith("sigma"):
            parameters[name] = 0.01
#               parameters[name] = 0.09
        elif name.startswith("L"):
            parameters[name] = 1e-6
        elif name.startswith("tau"):
            parameters[name] = 1.0
#               parameters[name] = 0.2
        else:
            raise ValueError(
                f"No initial value is defined for parameter {name!r}."
            )

    return parameters

def set_initial_values(circuit: CircuitNode) -> dict[str, float]:
    """Return the deterministic start used by existing fitter callers."""

    return set_deterministic_initial_values(circuit)


def generate_initial_values(
    circuit: CircuitNode,
    number_starts: int,# = 6,
    random_seed: int #= 42,
) -> list[dict[str, float]]:
    """Generate reproducible, stratified initial values for one circuit.

    The first start always contains the existing deterministic values. Positive
    parameters in the remaining starts are perturbed multiplicatively in
    log10 space. CPE exponents are sampled directly from
    ``ALPHA_INITIAL_RANGE``.

    A stable circuit-specific seed makes the generated starts independent of
    the order in which circuits are fitted.
    """

    if number_starts < 1:
        raise ValueError("number_starts must be at least 1.")

    deterministic = set_deterministic_initial_values(circuit)
    starts = [deterministic.copy() for _ in range(number_starts)]

    number_random_starts = number_starts - 1
    if number_random_starts == 0:
        return starts

    #"42:Series(...circuit...)" → hash bytes → integer → RNG 

    #Global random seed combined with circuit string used as local seed for each circuit
    
    seed_material = f"{random_seed}:{repr(circuit)}".encode("utf-8")
    digest = hashlib.blake2b(seed_material, digest_size=16).digest()
    rng = np.random.default_rng(int.from_bytes(digest, byteorder="big"))

    for name, deterministic_value in deterministic.items():
        if name.startswith("alpha"):
            sampled_values = _stratified_uniform(
                rng,
                low=ALPHA_INITIAL_RANGE[0],
                high=ALPHA_INITIAL_RANGE[1],
                size=number_random_starts,
            )

        else:
            half_width = _log10_perturbation_half_width(name)
            offsets = _stratified_uniform(
                rng,
                low=-half_width,
                high=half_width,
                size=number_random_starts,
            )
            sampled_values = deterministic_value * np.power(10.0, offsets)

        for start, sampled_value in zip(starts[1:], sampled_values):
            start[name] = float(sampled_value)

    return starts

def _log10_perturbation_half_width(parameter_name: str) -> float:
    """Return the sampling half-width in decades for a positive parameter."""

    if parameter_name == "Rs":
        return LOG10_PERTURBATION_HALF_WIDTHS["Rs"]

    for prefix in ("Rg", "R", "Q", "sigma", "L", "tau"):
        if parameter_name.startswith(prefix):
            return LOG10_PERTURBATION_HALF_WIDTHS[prefix]

    raise ValueError(
        f"No initial-value perturbation is defined for {parameter_name!r}."
    )

#Stratified means it is distributed evenly across interval

def _stratified_uniform(
    rng: np.random.Generator,
    low: float,
    high: float,
    size: int,
) -> np.ndarray:
    """Draw one shuffled uniform sample from each equal-width interval."""

    positions = (np.arange(size) + rng.random(size)) / size
    rng.shuffle(positions)
    return low + (high - low) * positions