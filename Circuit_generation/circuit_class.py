from typing import Any, Mapping, Protocol
from dataclasses import dataclass, fields

#simplifying old versions

class CircuitNode:
    '''anything that can appear in a circuit, either elements (resistors, capacitors...) or 
    connections (parallel, series)'''
    
class Element(CircuitNode):
    pass


@dataclass(frozen=True)
class Resistor(Element):
    resistance: str = "R"
    def parameter_names(self):
        return (self.resistance,)

    
    def impedance(self, omega, parameters):
        #v = vars(self)
        #resistance_name = v['resistance']
        resistance = parameters[self.resistance]
        return resistance + 0 * omega

    def number_parameters(self, number):
        return Resistor(resistance=f'{self.resistance}{number}')
    
    def __str__(self) -> str:
        return self.resistance

#this is resistor class without dataclass decorator:
#class Resistor(Element):
#    def __init__(self, resistance: str = "R") -> None:
#        self.resistance = resistance
#
#    def __repr__(self) -> str:
#        return f"Resistor(resistance={self.resistance!r})"
#
#    def __eq__(self, other: object) -> bool:
#        if not isinstance(other, Resistor):
#            return NotImplemented
#        return self.resistance == other.resistance
#
#    def __hash__(self) -> int:
#        return hash((Resistor, self.resistance))


@dataclass(frozen=True)
class SeriesResistance(Resistor):
    '''Rs'''
    resistance: str = "Rs"

    def impedance(self, omega, parameters):
        resistance = parameters[self.resistance]
        return resistance + 0 * omega
    
@dataclass(frozen=True)
class CPE(Element):
    coefficient: str = "Q"
    exponent: str = "alpha"

    def impedance(self, omega, parameters):
        q = parameters[self.coefficient]
        alpha = parameters[self.exponent]
        return 1 / (q * (1j * omega) ** alpha)

    def number_parameters(self, number):
        return CPE(
            coefficient=f'{self.coefficient}{number}',
            exponent = f'{self.exponent}{number}'
            )

    def __str__(self) -> str:
        return f"CPE({self.coefficient}, {self.exponent})"


@dataclass(frozen=True)
class Warburg(Element):
    coefficient: str = "sigma"

    def impedance(self, omega, parameters):
        sigma = parameters[self.coefficient]
        return sigma / (1j * omega) ** 0.5
    
    def number_parameters(self, number):
        return Warburg(
            coefficient=f'{self.coefficient}{number}'
            )
    
    def __str__(self) -> str:
        return f"W({self.coefficient})"


@dataclass(frozen=True)
class Inductor(Element):
    inductance: str = "L"

    def impedance(self, omega, parameters):
        inductance = parameters[self.inductance]
        return 1j * omega * inductance
    
    def number_parameters(self, number):
        return Inductor(
            inductance=f'{self.inductance}{number}'
            )
    def __str__(self) -> str:
        return f"L({self.inductance})"


@dataclass(frozen=True)
class Gerischer(Element):
    resistance: str = "Rg"
    time_constant: str = "tau"

    def impedance(self, omega, parameters):
        resistance = parameters[self.resistance]
        tau = parameters[self.time_constant]
        return resistance / (1 + 1j * omega * tau) ** 0.5
    
    def number_parameters(self, number):
        return Gerischer(
            resistance=f'{self.resistance}{number}',
            time_constant = f'{self.time_constant}{number}'
            )
    
    def __str__(self) -> str:
        return f"G({self.resistance}, {self.time_constant})"


@dataclass(frozen=True)
class Parallel(CircuitNode):
    children: tuple[CircuitNode, ...]

    def impedance(self, omega, parameters):
        admittance = sum(
            1 / child.impedance(omega, parameters)  #type: ignore
            for child in self.children
        )
        return 1 / admittance

    def __str__(self) -> str:
        parts = []
        for child in self.children:
            description = str(child)
            if isinstance(child, Series):
                description = f"({description})"
            parts.append(description)
        return " || ".join(parts)

@dataclass(frozen=True)
class Series(CircuitNode):
    children: tuple[CircuitNode, ...]

    def impedance(self, omega, parameters):
        return sum(child.impedance(omega, parameters) for child in self.children) #type: ignore

    def __str__(self) -> str:
        parts = []
        for child in self.children:
            description = str(child)
            if isinstance(child, Parallel):
                description = f"({description})"
            parts.append(description)
        return " + ".join(parts)

