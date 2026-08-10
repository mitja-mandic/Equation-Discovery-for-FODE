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

def set_initial_values(circuit):
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

        elif name.startswith("Rg"):
            parameters[name] = 0.02

        elif name.startswith("R"):
            parameters[name] = 0.02

        elif name.startswith("Q"):
            parameters[name] = 1.0

        elif name.startswith("alpha"):
            parameters[name] = 0.8

        elif name.startswith("sigma"):
            parameters[name] = 0.01

        elif name.startswith("L"):
            parameters[name] = 1e-6

        elif name.startswith("tau"):
            parameters[name] = 1.0

        else:
            raise ValueError(
                f"No initial value is defined for parameter {name!r}."
            )

    return parameters

