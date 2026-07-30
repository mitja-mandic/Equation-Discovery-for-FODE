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


@dataclass(frozen=True)
class CPE(Element):
    coefficient: str = "Q"
    exponent: str = "alpha"


@dataclass(frozen=True)
class Warburg(Element):
    coefficient: str = "sigma"


@dataclass(frozen=True)
class Inductor(Element):
    inductance: str = "L"


@dataclass(frozen=True)
class Gerischer(Element):
    resistance: str = "Rg"
    time_constant: str = "tau"

@dataclass(frozen=True)
class Parallel(CircuitNode):
    children: tuple[CircuitNode, ...]

@dataclass(frozen=True)
class Series(CircuitNode):
    children: tuple[CircuitNode, ...]

