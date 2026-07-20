"""Build executable impedance circuits from normalized Python trees.

The arithmetic deliberately uses only Python operators. Consequently, omega and
parameter values can be Python scalars, NumPy arrays, or PyTorch tensors. This
lets plotting and fitting use the same circuit object.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from typing import Any, Mapping, Protocol

if __package__:
    from .generate_trees import Tree
else:
    from generate_trees import Tree


ParameterValues = Mapping[str, Any]


class Component(Protocol):
    """Behavior shared by primitive elements and circuit connections."""

    @property
    def parameter_names(self) -> tuple[str, ...]: ...

    def impedance(self, omega: Any, parameters: ParameterValues) -> Any: ...

    def impedance_expression(self) -> str: ...

    def admittance_expression(self) -> str: ...


def _parameter(parameters: ParameterValues, name: str) -> Any:
    try:
        return parameters[name]
    except KeyError as error:
        raise ValueError(f"Missing circuit parameter: {name}") from error


def _unique_parameter_names(components: tuple[Component, ...]) -> tuple[str, ...]:
    names: list[str] = []
    seen: set[str] = set()
    for component in components:
        for name in component.parameter_names:
            if name not in seen:
                seen.add(name)
                names.append(name)
    return tuple(names)


@dataclass(frozen=True)
class Resistor:
    resistance: str

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return (self.resistance,)

    def impedance(self, omega: Any, parameters: ParameterValues) -> Any:
        resistance = _parameter(parameters, self.resistance)
        return resistance + 0 * omega

    def impedance_expression(self) -> str:
        return self.resistance

    def admittance_expression(self) -> str:
        return f"1 / {self.resistance}"

    def __str__(self) -> str:
        return self.resistance


@dataclass(frozen=True)
class Inductor:
    inductance: str

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return (self.inductance,)

    def impedance(self, omega: Any, parameters: ParameterValues) -> Any:
        return 1j * omega * _parameter(parameters, self.inductance)

    def impedance_expression(self) -> str:
        return f"1j * omega * {self.inductance}"

    def admittance_expression(self) -> str:
        return f"1 / (1j * omega * {self.inductance})"

    def __str__(self) -> str:
        return f"L({self.inductance})"


@dataclass(frozen=True)
class CPE:
    coefficient: str
    exponent: str

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return self.coefficient, self.exponent

    def impedance(self, omega: Any, parameters: ParameterValues) -> Any:
        q = _parameter(parameters, self.coefficient)
        alpha = _parameter(parameters, self.exponent)
        return 1 / (q * (1j * omega) ** alpha)

    def impedance_expression(self) -> str:
        return (
            f"1 / ({self.coefficient} * "
            f"(1j * omega) ** {self.exponent})"
        )

    def admittance_expression(self) -> str:
        return f"{self.coefficient} * (1j * omega) ** {self.exponent}"

    def __str__(self) -> str:
        return f"CPE({self.coefficient}, {self.exponent})"


@dataclass(frozen=True)
class Warburg:
    coefficient: str

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return (self.coefficient,)

    def impedance(self, omega: Any, parameters: ParameterValues) -> Any:
        sigma = _parameter(parameters, self.coefficient)
        return sigma / (1j * omega) ** 0.5

    def impedance_expression(self) -> str:
        return f"{self.coefficient} / (1j * omega) ** 0.5"

    def admittance_expression(self) -> str:
        return f"(1j * omega) ** 0.5 / {self.coefficient}"

    def __str__(self) -> str:
        return f"W({self.coefficient})"


@dataclass(frozen=True)
class Gerischer:
    resistance: str
    time_constant: str

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return self.resistance, self.time_constant

    def impedance(self, omega: Any, parameters: ParameterValues) -> Any:
        resistance = _parameter(parameters, self.resistance)
        tau = _parameter(parameters, self.time_constant)
        return resistance / (1 + 1j * omega * tau) ** 0.5

    def impedance_expression(self) -> str:
        return (
            f"{self.resistance} / "
            f"(1 + 1j * omega * {self.time_constant}) ** 0.5"
        )

    def admittance_expression(self) -> str:
        return (
            f"(1 + 1j * omega * {self.time_constant}) ** 0.5 "
            f"/ {self.resistance}"
        )

    def __str__(self) -> str:
        return f"G({self.resistance}, {self.time_constant})"


@dataclass(frozen=True)
class Series:
    components: tuple[Component, ...]

    def __post_init__(self) -> None:
        if not self.components:
            raise ValueError("A series connection needs at least one component")

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return _unique_parameter_names(self.components)

    def impedance(self, omega: Any, parameters: ParameterValues) -> Any:
        total = self.components[0].impedance(omega, parameters)
        for component in self.components[1:]:
            total = total + component.impedance(omega, parameters)
        return total

    def impedance_expression(self) -> str:
        return " + ".join(
            component.impedance_expression() for component in self.components
        )

    def admittance_expression(self) -> str:
        return f"1 / ({self.impedance_expression()})"

    def __str__(self) -> str:
        parts = []
        for component in self.components:
            description = str(component)
            if isinstance(component, Parallel):
                description = f"({description})"
            parts.append(description)
        return " + ".join(parts)


@dataclass(frozen=True)
class Parallel:
    components: tuple[Component, ...]

    def __post_init__(self) -> None:
        if not self.components:
            raise ValueError("A parallel connection needs at least one component")

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return _unique_parameter_names(self.components)

    def impedance(self, omega: Any, parameters: ParameterValues) -> Any:
        admittance = 1 / self.components[0].impedance(omega, parameters)
        for component in self.components[1:]:
            admittance = admittance + 1 / component.impedance(omega, parameters)
        return 1 / admittance

    def impedance_expression(self) -> str:
        return f"1 / ({self.admittance_expression()})"

    def admittance_expression(self) -> str:
        return " + ".join(
            component.admittance_expression() for component in self.components
        )

    def __str__(self) -> str:
        parts = []
        for component in self.components:
            description = str(component)
            if isinstance(component, Series):
                description = f"({description})"
            parts.append(description)
        return " || ".join(parts)


@dataclass(frozen=True)
class Circuit:
    """A circuit topology that can be evaluated with different parameters."""

    root: Component

    @classmethod
    def from_tree(cls, tree: Tree) -> "Circuit":
        """Build and consistently number a circuit from a normalized tree."""
        return cls(_CircuitFactory().build(tree))

    @property
    def parameter_names(self) -> tuple[str, ...]:
        return self.root.parameter_names

    def impedance(self, omega: Any, parameters: ParameterValues) -> Any:
        """Evaluate complex impedance at one or many angular frequencies."""
        missing = [name for name in self.parameter_names if name not in parameters]
        if missing:
            raise ValueError(f"Missing circuit parameters: {', '.join(missing)}")
        return self.root.impedance(omega, parameters)

    def impedance_expression(self) -> str:
        """Return the executable Python expression used to calculate Z(omega)."""
        return self.root.impedance_expression()

    def __str__(self) -> str:
        return str(self.root)


class _CircuitFactory:
    def __init__(self) -> None:
        self._indices = count(start=1)

    def build(self, tree: Tree) -> Component:
        if isinstance(tree, str):
            return self._build_element(tree)

        operator, children = tree
        built_children = tuple(self.build(child) for child in children)
        if operator == "+":
            return Series(built_children)
        if operator == "||":
            return Parallel(built_children)
        raise ValueError(f"Unsupported composition operator: {operator!r}")

    def _build_element(self, kind: str) -> Component:
        if kind == "Rs":
            return Resistor("Rs")

        index = next(self._indices)
        if kind == "R":
            return Resistor(f"R{index}")
        if kind == "L":
            return Inductor(f"L{index}")
        if kind == "CPE":
            return CPE(f"Q{index}", f"alpha{index}")
        if kind == "W":
            return Warburg(f"sigma{index}")
        if kind == "G":
            return Gerischer(f"Rg{index}", f"tauG{index}")
        if kind == "zarc":
            return Parallel(
                (
                    Resistor(f"R{index}"),
                    CPE(f"Q{index}", f"alpha{index}"),
                )
            )
        if kind == "randles":
            return Parallel(
                (
                    Resistor(f"R{index}"),
                    Series(
                        (
                            CPE(f"Q{index}", f"alpha{index}"),
                            Warburg(f"sigma{index}"),
                        )
                    ),
                )
            )
        raise ValueError(f"Unsupported circuit element: {kind!r}")


def circuit_from_tree(tree: Tree) -> Circuit:
    """Return an executable circuit object for a normalized tree."""
    return Circuit.from_tree(tree)
