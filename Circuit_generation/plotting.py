"""Export reference Nyquist plots for representative generated circuits.

Run this file directly:

    python plotting.py

The plots use positive logarithmic frequencies:

    f = logspace(-3, 5)
    omega = 2*pi*f
"""

from __future__ import annotations

import argparse
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import FancyBboxPatch

from circuit_class import (
    CPE,
    CircuitNode,
    Element,
    Gerischer,
    Inductor,
    Parallel,
    Resistor,
    Series,
    SeriesResistance,
    Warburg,
)


@dataclass(frozen=True)
class PlotCase:
    name: str
    circuit: CircuitNode
    parameters: Mapping[str, float]
    reference_impedance: Callable[[np.ndarray, Mapping[str, float]], np.ndarray]
    color: str


def impedance_expression(node: CircuitNode) -> str:
    """Return a readable Python-style impedance equation for a circuit."""
    if isinstance(node, Resistor):
        return node.resistance
    if isinstance(node, Inductor):
        return f"1j * omega * {node.inductance}"
    if isinstance(node, CPE):
        return (
            f"1 / ({node.coefficient} * "
            f"(1j * omega) ** {node.exponent})"
        )
    if isinstance(node, Warburg):
        return f"{node.coefficient} / (1j * omega) ** 0.5"
    if isinstance(node, Gerischer):
        return (
            f"{node.resistance} / "
            f"(1 + 1j * omega * {node.time_constant}) ** 0.5"
        )
    if isinstance(node, Series):
        return " + ".join(impedance_expression(child) for child in node.children)
    if isinstance(node, Parallel):
        return f"1 / ({admittance_expression(node)})"
    raise TypeError(f"Unsupported circuit node: {type(node).__name__}")


def admittance_expression(node: CircuitNode) -> str:
    """Return the matching admittance equation used by parallel branches."""
    if isinstance(node, Resistor):
        return f"1 / {node.resistance}"
    if isinstance(node, Inductor):
        return f"1 / (1j * omega * {node.inductance})"
    if isinstance(node, CPE):
        return f"{node.coefficient} * (1j * omega) ** {node.exponent}"
    if isinstance(node, Warburg):
        return f"(1j * omega) ** 0.5 / {node.coefficient}"
    if isinstance(node, Gerischer):
        return (
            f"(1 + 1j * omega * {node.time_constant}) ** 0.5 "
            f"/ {node.resistance}"
        )
    if isinstance(node, Series):
        return f"1 / ({impedance_expression(node)})"
    if isinstance(node, Parallel):
        return " + ".join(
            admittance_expression(child) for child in node.children
        )
    raise TypeError(f"Unsupported circuit node: {type(node).__name__}")


def parameter_names(node: CircuitNode) -> tuple[str, ...]:
    """Collect parameter names in the circuit's canonical traversal order."""
    if isinstance(node, Resistor):
        return (node.resistance,)
    if isinstance(node, Inductor):
        return (node.inductance,)
    if isinstance(node, CPE):
        return node.coefficient, node.exponent
    if isinstance(node, Warburg):
        return (node.coefficient,)
    if isinstance(node, Gerischer):
        return node.resistance, node.time_constant
    if isinstance(node, (Series, Parallel)):
        return tuple(
            name
            for child in node.children
            for name in parameter_names(child)
        )
    raise TypeError(f"Unsupported circuit node: {type(node).__name__}")


def _zarc_reference(
    omega: np.ndarray,
    parameters: Mapping[str, float],
) -> np.ndarray:
    cpe = 1 / (
        parameters["Q2"] * (1j * omega) ** parameters["alpha2"]
    )
    parallel = 1 / (1 / parameters["R1"] + 1 / cpe)
    return parameters["Rs"] + parallel


def _randles_warburg_reference(
    omega: np.ndarray,
    parameters: Mapping[str, float],
) -> np.ndarray:
    cpe = 1 / (
        parameters["Q2"] * (1j * omega) ** parameters["alpha2"]
    )
    warburg = parameters["sigma3"] / (1j * omega) ** 0.5
    parallel = 1 / (1 / parameters["R1"] + 1 / (cpe + warburg))
    return parameters["Rs"] + parallel


def _zarc_series_warburg_reference(
    omega: np.ndarray,
    parameters: Mapping[str, float],
) -> np.ndarray:
    cpe = 1 / (
        parameters["Q2"] * (1j * omega) ** parameters["alpha2"]
    )
    parallel = 1 / (1 / parameters["R1"] + 1 / cpe)
    warburg = parameters["sigma3"] / (1j * omega) ** 0.5
    return parameters["Rs"] + parallel + warburg


def _gerischer_inductive_reference(
    omega: np.ndarray,
    parameters: Mapping[str, float],
) -> np.ndarray:
    gerischer = parameters["Rg2"] / (
        1 + 1j * omega * parameters["tau2"]
    ) ** 0.5
    parallel = 1 / (1 / parameters["R1"] + 1 / gerischer)
    inductor = 1j * omega * parameters["L3"]
    return parameters["Rs"] + parallel + inductor


def example_cases() -> tuple[PlotCase, ...]:
    """Build representative parameterized circuits for visual validation."""
    zarc = Series(
        (
            SeriesResistance("Rs"),
            Parallel(
                (
                    Resistor("R1"),
                    CPE("Q2", "alpha2"),
                )
            ),
        )
    )

    randles_warburg = Series(
        (
            SeriesResistance("Rs"),
            Parallel(
                (
                    Resistor("R1"),
                    Series(
                        (
                            CPE("Q2", "alpha2"),
                            Warburg("sigma3"),
                        )
                    ),
                )
            ),
        )
    )

    gerischer_inductive = Series(
        (
            SeriesResistance("Rs"),
            Parallel(
                (
                    Resistor("R1"),
                    Gerischer("Rg2", "tau2"),
                )
            ),
            Inductor("L3"),
        )
    )

    zarc_series_warburg = Series(
        (
            SeriesResistance("Rs"),
            Parallel(
                (
                    Resistor("R1"),
                    CPE("Q2", "alpha2"),
                )
            ),
            Warburg("sigma3"),
        )
    )

    return (
        PlotCase(
            name="ZARC-like response",
            circuit=zarc,
            parameters={"Rs": 0.15, "R1": 2.0, "Q2": 0.18, "alpha2": 0.88},
            reference_impedance=_zarc_reference,
            color="#1769aa",
        ),
        PlotCase(
            name="Randles-Warburg response",
            circuit=randles_warburg,
            parameters={
                "Rs": 0.12,
                "R1": 2.5,
                "Q2": 0.12,
                "alpha2": 0.92,
                "sigma3": 0.35,
            },
            reference_impedance=_randles_warburg_reference,
            color="#b94a48",
        ),
        PlotCase(
            name="Gerischer with inductive response",
            circuit=gerischer_inductive,
            parameters={
                "Rs": 0.08,
                "R1": 2.2,
                "Rg2": 1.4,
                "tau2": 0.7,
                "L3": 2e-6,
            },
            reference_impedance=_gerischer_inductive_reference,
            color="#2d7d46",
        ),
        PlotCase(
            name="ZARC with series Warburg response",
            circuit=zarc_series_warburg,
            parameters={
                "Rs": 0.15,
                "R1": 2.0,
                "Q2": 0.18,
                "alpha2": 0.88,
                "sigma3": 0.35,
            },
            reference_impedance=_zarc_series_warburg_reference,
            color="#7b4ab5",
        ),
    )


def _validate_parameters(case: PlotCase) -> None:
    required = set(parameter_names(case.circuit))
    supplied = set(case.parameters)
    missing = sorted(required - supplied)
    extra = sorted(supplied - required)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing={missing}")
        if extra:
            details.append(f"extra={extra}")
        raise ValueError(f"Invalid parameters for {case.name}: {', '.join(details)}")


def _element_label(node: Element) -> str:
    if isinstance(node, SeriesResistance):
        return node.resistance
    if isinstance(node, Resistor):
        return node.resistance
    if isinstance(node, Inductor):
        return f"L\n{node.inductance}"
    if isinstance(node, CPE):
        return f"CPE\n{node.coefficient}, {node.exponent}"
    if isinstance(node, Warburg):
        return f"W\n{node.coefficient}"
    if isinstance(node, Gerischer):
        return f"G\n{node.resistance}, {node.time_constant}"
    raise TypeError(f"Unsupported element: {type(node).__name__}")


def _node_size(node: CircuitNode) -> tuple[float, float]:
    if isinstance(node, Element):
        return 1.0, 1.0

    child_sizes = [_node_size(child) for child in node.children]  # type: ignore[attr-defined]
    if isinstance(node, Series):
        return sum(width for width, _ in child_sizes), max(
            height for _, height in child_sizes
        )
    if isinstance(node, Parallel):
        return max(width for width, _ in child_sizes), sum(
            height for _, height in child_sizes
        )
    raise TypeError(f"Unsupported circuit node: {type(node).__name__}")


def _draw_node(
    axis: Axes,
    node: CircuitNode,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
) -> None:
    if isinstance(node, Element):
        midpoint = (y0 + y1) / 2
        span = x1 - x0
        box_left = x0 + 0.18 * span
        box_right = x1 - 0.18 * span
        box_height = min(0.10, 0.42 * (y1 - y0))

        axis.plot([x0, box_left], [midpoint, midpoint], color="#343a40", lw=1.4)
        axis.plot([box_right, x1], [midpoint, midpoint], color="#343a40", lw=1.4)
        box = FancyBboxPatch(
            (box_left, midpoint - box_height / 2),
            box_right - box_left,
            box_height,
            boxstyle="round,pad=0.008,rounding_size=0.012",
            linewidth=1.2,
            edgecolor="#343a40",
            facecolor="#f1f3f5",
        )
        axis.add_patch(box)
        axis.text(
            (box_left + box_right) / 2,
            midpoint,
            _element_label(node),
            ha="center",
            va="center",
            fontsize=7.5,
        )
        return

    if isinstance(node, Series):
        widths = [_node_size(child)[0] for child in node.children]
        total_width = sum(widths)
        cursor = x0
        for child, width in zip(node.children, widths):
            child_x1 = cursor + (x1 - x0) * width / total_width
            _draw_node(axis, child, cursor, child_x1, y0, y1)
            cursor = child_x1
        return

    if isinstance(node, Parallel):
        span = x1 - x0
        left_rail = x0 + 0.10 * span
        right_rail = x1 - 0.10 * span
        heights = [_node_size(child)[1] for child in node.children]
        total_height = sum(heights)
        bands = []
        cursor = y1
        for child, height in zip(node.children, heights):
            child_y0 = cursor - (y1 - y0) * height / total_height
            bands.append((child, child_y0, cursor))
            cursor = child_y0

        centers = [(low + high) / 2 for _, low, high in bands]
        midpoint = (y0 + y1) / 2
        axis.plot([x0, left_rail], [midpoint, midpoint], color="#343a40", lw=1.4)
        axis.plot([right_rail, x1], [midpoint, midpoint], color="#343a40", lw=1.4)
        axis.plot(
            [left_rail, left_rail],
            [min(centers), max(centers)],
            color="#343a40",
            lw=1.4,
        )
        axis.plot(
            [right_rail, right_rail],
            [min(centers), max(centers)],
            color="#343a40",
            lw=1.4,
        )
        for child, child_y0, child_y1 in bands:
            _draw_node(axis, child, left_rail, right_rail, child_y0, child_y1)
        return

    raise TypeError(f"Unsupported circuit node: {type(node).__name__}")


def draw_circuit_schema(axis: Axes, circuit: CircuitNode) -> None:
    axis.set_title("Circuit schema", fontsize=10, loc="left")
    _draw_node(axis, circuit, 0.04, 0.96, 0.31, 0.91)
    midpoint = 0.61
    axis.scatter([0.04, 0.96], [midpoint, midpoint], s=14, color="#343a40", zorder=5)
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.set_aspect("equal", adjustable="box")
    axis.axis("off")


def create_figure(samples: int = 300) -> plt.Figure:
    if samples < 2:
        raise ValueError("samples must be at least 2")

    cases = example_cases()
    frequency = np.logspace(-3, 5, samples)
    omega = 2 * np.pi * frequency

    figure, axes = plt.subplots(
        nrows=len(cases),
        ncols=2,
        figsize=(14, 4 * len(cases)),
        gridspec_kw={"width_ratios": (3.2, 1.5)},
        constrained_layout=True,
    )
    figure.suptitle(
        "Nyquist validation of circuit impedance implementations\n"
        "f = logspace(-3, 5) Hz; omega = 2*pi*f",
        fontsize=15,
    )

    for row, case in enumerate(cases):
        _validate_parameters(case)
        plot_axis = axes[row, 0]
        schema_axis = axes[row, 1]

        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            impedance = np.asarray(
                case.circuit.impedance(omega, case.parameters),
                dtype=complex,
            )
            reference = np.asarray(
                case.reference_impedance(omega, case.parameters),
                dtype=complex,
            )

        np.testing.assert_allclose(
            impedance,
            reference,
            rtol=1e-12,
            atol=1e-12,
            err_msg=f"Impedance mismatch for {case.name}",
        )

        finite = np.isfinite(impedance.real) & np.isfinite(impedance.imag)
        if not np.any(finite):
            raise ValueError(f"No finite impedance values for {case.name}")

        plot_axis.plot(
            impedance.real[finite],
            -impedance.imag[finite],
            color=case.color,
            linestyle="-",
            lw=2.0,
        )

        low_frequency_index = np.flatnonzero(finite)[0]
        plot_axis.scatter(
            [impedance.real[low_frequency_index]],
            [-impedance.imag[low_frequency_index]],
            marker="o",
            s=28,
            facecolor="none",
            edgecolor=case.color,
            linewidth=1.2,
            zorder=3,
        )

        equation = impedance_expression(case.circuit)
        wrapped_equation = textwrap.fill(
            f"Z(omega) = {equation}",
            width=92,
            subsequent_indent="    ",
        )
        plot_axis.set_title(
            f"{case.name}\n{wrapped_equation}",
            fontsize=10,
            loc="left",
            fontfamily="monospace",
        )
        plot_axis.set_xlabel("Re(Z) [ohm]")
        plot_axis.set_ylabel("-Im(Z) [ohm]")
        plot_axis.grid(True, color="#ced4da", linewidth=0.7, alpha=0.75)
        plot_axis.axhline(0, color="#868e96", linewidth=0.8)
        plot_axis.set_aspect("equal", adjustable="datalim")
        draw_circuit_schema(schema_axis, case.circuit)
        parameter_text = "Parameters\n" + "\n".join(
            f"{name} = {value:g}" for name, value in case.parameters.items()
        )
        schema_axis.text(
            0.04,
            0.24,
            parameter_text,
            ha="left",
            va="top",
            fontsize=8.5,
            fontfamily="monospace",
            transform=schema_axis.transAxes,
        )

    return figure


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export reference Nyquist plots for circuit impedances."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("nyquist_validation.png"),
        help="PNG output path (a PDF with the same stem is also exported).",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=300,
        help="Number of logarithmic positive-frequency samples.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    figure = create_figure(samples=args.samples)
    figure.savefig(output_path, dpi=220, bbox_inches="tight")
    pdf_path = output_path.with_suffix(".pdf")
    figure.savefig(pdf_path, bbox_inches="tight")
    plt.close(figure)

    print(f"Exported {output_path}")
    print(f"Exported {pdf_path}")


if __name__ == "__main__":
    main()
