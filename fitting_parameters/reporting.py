"""Create compact, document-ready outputs from ranked circuit fits."""

from __future__ import annotations

import json
from math import sqrt
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from Circuit_generation.circuit_class import CircuitNode, Element


def build_fit_output_paths(
    project_directory: str | Path,
    dataset_path: str | Path,
    grammar_name: str,
    maximum_elements: int,
    filename_prefix: str = "",
) -> tuple[Path, Path]:
    """Return matching, dataset-specific paths for one plot and summary."""
    project_directory = Path(project_directory)
    run_name = (
        f"{filename_prefix}{Path(dataset_path).stem}_"
        f"{grammar_name}_{maximum_elements}"
    )
    plot_path = (
        project_directory
        / "Results"
        / "Plots"
        / "Nyquists"
        / f"{run_name}_best_5.png"
    )
    summary_path = (
        project_directory
        / "Results"
        / "fit_results"
        / f"{run_name}_fit_summary.json"
    )
    return plot_path, summary_path


def plot_circuit_fits(
    measured_impedance: np.ndarray,
    results: Sequence[Mapping[str, Any]],
    output_path: str | Path,
    *,
    show: bool = True,
) -> Path:
    """Plot the five best ranked circuits and emphasize the winner."""
    import matplotlib.pyplot as plt

    plotted_results = list(results[:5])
    if not plotted_results:
        raise ValueError("At least one fit result is required to create a plot")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(10, 7))
    axis.scatter(
        measured_impedance.real,
        -measured_impedance.imag,
        facecolors="none",
        edgecolors="tab:red",
        s=28,
        label="Measured data",
        zorder=10,
    )

    for index, result in enumerate(plotted_results, start=1):
        predicted = np.asarray(result["predicted_impedance"])
        is_best = index == 1
        axis.plot(
            predicted.real,
            -predicted.imag,
            label=f"Circuit {index}",
            linestyle="-" if is_best else "--",
            linewidth=3.2 if is_best else 1.6,
            alpha=1.0 if is_best else 0.85,
            zorder=6 if is_best else 4,
        )

    axis.set_xlabel("Re(Z)")
    axis.set_ylabel("-Im(Z)")
    axis.set_title("Nyquist plot")
    axis.grid(True, alpha=0.3)

    legend = axis.legend()
    for label in legend.get_texts():
        if label.get_text() == "Circuit 1":
            label.set_fontweight("bold")

    #################################
    #                               #
    #UNCOMMENT BELOW TO SAVE FIGURES#
    #                               #
    #################################



    #figure.tight_layout()
    #figure.savefig(
    #    output_path,
    #    bbox_inches="tight",
    #    dpi=300,
    #    pad_inches=0.2,
    #)

    if show:
        plt.show()
    plt.close(figure)

    return output_path


def export_fit_summary(
    results: Sequence[Mapping[str, Any]],
    output_path: str | Path,
    *,
    plot_path: str | Path,
    dataset_path: str | Path,
    circuit_path: str | Path,
    grammar_name: str,
    maximum_elements: int,
    optimizer: str,
    optimizer_settings: Mapping[str, Any],
    frequency: np.ndarray,
) -> Path:
    """Write fit metadata and the ten best ranked circuits to JSON."""
    if not results:
        raise ValueError("At least one fit result is required to create a summary")

    frequency = np.asarray(frequency)
    successful_count = sum(bool(result["success"]) for result in results)
    best_bic = float(results[0]["bic"])

    top_circuits = []
    for rank, result in enumerate(results[:10], start=1):
        mse = float(result["mse"])
        parameters = {
            name: _json_number(value)
            for name, value in result["parameters"].items()
        }
        top_circuits.append(
            {
                "rank": rank,
                "plot_label": f"Circuit {rank}" if rank <= 5 else None,
                "circuit": str(result["circuit"]),
                "element_count": _count_elements(result["circuit"]),
                "parameter_count": len(parameters),
                "parameters": parameters,
                "mse": _json_number(mse),
                "rmse": _json_number(sqrt(mse)),
                "aic": _json_number(result["aic"]),
                "bic": _json_number(result["bic"]),
                "delta_bic": _json_number(float(result["bic"]) - best_bic),
                "success": bool(result["success"]),
                "optimizer_status": result.get("optimizer_status"),
                "optimizer_message": result.get("optimizer_message"),
                "function_evaluations": result.get("function_evaluations"),
            }
        )

    document = {
        "format_version": 1,
        "dataset": str(dataset_path),
        "circuit_collection": str(circuit_path),
        "grammar": grammar_name,
        "maximum_elements": maximum_elements,
        "frequency": {
            "points": int(frequency.size),
            "minimum_hz": _json_number(np.min(frequency)),
            "maximum_hz": _json_number(np.max(frequency)),
        },
        "optimizer": {
            "name": optimizer,
            "settings": {
                key: _json_value(value)
                for key, value in optimizer_settings.items()
            },
        },
        "circuits": {
            "fitted": len(results),
            "successful": successful_count,
            "unsuccessful": len(results) - successful_count,
        },
        "ranking_metric": "bic",
        "associated_plot": str(plot_path),
        "circuits_shown_in_plot": min(5, len(results)),
        "top_circuits": top_circuits,
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ###############################
    #                             #
    #UNCOMMENT BELOW TO SAVE JSONS#
    #                             #
    ###############################

    #temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    #temporary_path.write_text(
    #    json.dumps(document, indent=2, allow_nan=False) + "\n",
    #    encoding="utf-8",
    #)
    #temporary_path.replace(output_path)
    return output_path


def _count_elements(node: CircuitNode) -> int:
    if isinstance(node, Element):
        return 1
    return sum(_count_elements(child) for child in node.children)  # type: ignore[attr-defined]


def _json_number(value: Any) -> float | int | None:
    number = value.item() if isinstance(value, np.generic) else value
    if isinstance(number, int):
        return number
    number = float(number)
    return number if np.isfinite(number) else None


def _json_value(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value
