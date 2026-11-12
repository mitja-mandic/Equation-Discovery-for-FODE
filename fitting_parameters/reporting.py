"""Create compact, document-ready outputs from ranked circuit fits."""

from __future__ import annotations

import hashlib
import json
from math import sqrt
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from Circuit_generation.circuit_class import CircuitNode, Element


def build_fit_dataset_info(
    *,
    source_path: str | Path,
    mode: str,
    channel: str | None,
    preprocessing: str,
    frequency: np.ndarray,
    measured_impedance: np.ndarray,
    loader_real_scale: np.ndarray,
    loader_imag_scale: np.ndarray,
    normalized_real_scale: np.ndarray,
    normalized_imag_scale: np.ndarray,
    fitting_real_divisor: np.ndarray | float,
    fitting_imag_divisor: np.ndarray | float,
    coherence: np.ndarray | None,
    selected_spectrum_columns: Sequence[int] | None = None,
) -> dict[str, Any]:
    """Snapshot the exact processed data and divisors used in one fit."""
    source_path = Path(source_path)
    frequency = np.asarray(frequency, dtype=float)
    measured_impedance = np.asarray(measured_impedance, dtype=complex)
    if frequency.ndim != 1 or frequency.shape != measured_impedance.shape:
        raise ValueError("Frequency and measured impedance must be matching 1D arrays")

    size_bytes = None
    source_sha256 = None
    if source_path.is_file():
        size_bytes = source_path.stat().st_size
        with source_path.open("rb") as handle:
            source_sha256 = hashlib.file_digest(handle, "sha256").hexdigest()

    return {
        "source_path": str(source_path),
        "source_size_bytes": size_bytes,
        "source_sha256": source_sha256,
        "mode": mode,
        "channel": channel,
        "preprocessing": preprocessing,
        "loader_scale_kind": "unit_placeholders" if mode == "pcl" else "component_mad_ohm",
        "frequency_hz": _json_array(frequency),
        "measured_impedance_ohm": _complex_json_array(measured_impedance),
        "loader_scales": {
            "real": _json_array(loader_real_scale, frequency.shape),
            "imag": _json_array(loader_imag_scale, frequency.shape),
        },
        "normalized_scales": {
            "real": _json_array(normalized_real_scale, frequency.shape),
            "imag": _json_array(normalized_imag_scale, frequency.shape),
        },
        "fitting_residual_divisors": {
            "real": _json_array(fitting_real_divisor, frequency.shape),
            "imag": _json_array(fitting_imag_divisor, frequency.shape),
        },
        "coherence": None if coherence is None else _json_array(coherence, frequency.shape),
        "selected_spectrum_columns": (
            [int(column) for column in selected_spectrum_columns]
            if selected_spectrum_columns is not None else None
        ),
    }


def build_fit_output_paths(
    project_directory: str | Path,
    dataset_path: str | Path,
    grammar_name: str,
    maximum_elements: int,
    filename_suffix: str,
    filename_prefix: str = "",
    channel: str | None = None,
) -> tuple[Path, Path]:
    """Return matching, dataset-specific paths for one plot and summary."""
    project_directory = Path(project_directory)
    dataset_name = Path(dataset_path).stem
    if channel:
        dataset_name = f"{dataset_name}_{channel}"
    run_name = (
        f"{filename_prefix}{dataset_name}_"
        f"{grammar_name}_{maximum_elements}"
    )
    plot_path = (
        project_directory
        / "Results"
        / "Plots"
        / "Nyquists"
        / f"{run_name}_best_5_{filename_suffix}.png"
    )
    summary_path = (
        project_directory
        / "Results"
        / "fit_results"
        / f"{run_name}_fit_summary_{filename_suffix}.json"
    )
    return plot_path, summary_path


def plot_circuit_fits(
    measured_impedance: np.ndarray,
    results: Sequence[Mapping[str, Any]],
    output_path: str | Path,
    *,
    show: bool = True,
    save_output: bool,
    plot_title: str
) -> Path:
    """Plot the five best ranked circuits and emphasize the winner."""
    import matplotlib.pyplot as plt

    plotted_results = list(results[:5])
    #plotted_results = list(results[:6])
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
            label=_circuit_plot_label(index, result["circuit"]),
            linestyle="-" if is_best else "--",
            linewidth=3.2 if is_best else 1.6,
            alpha=1.0 if is_best else 0.85,
            zorder=6 if is_best else 4,
        )

    axis.set_xlabel("Re(Z)")
    axis.set_ylabel("-Im(Z)")
    axis.set_title(plot_title)
    axis.grid(True, alpha=0.3)

    legend = axis.legend()
    for label in legend.get_texts():
        if label.get_text() == _circuit_plot_label(
            1, plotted_results[0]["circuit"]
        ):
            label.set_fontweight("bold")

    #################################
    #                               #
    #UNCOMMENT BELOW TO SAVE FIGURES#
    #                               #
    #################################


    if save_output:
        figure.tight_layout()
        figure.savefig(
            output_path,
            bbox_inches="tight",
            dpi=300,
            pad_inches=0.2,
        )

    if show:
        plt.show()
    plt.close(figure)

    return output_path


def plot_fit_residuals(
    frequency: np.ndarray,
    measured_impedance: np.ndarray,
    results: Sequence[Mapping[str, Any]],
    output_path: str | Path,
    *,
    real_scale: np.ndarray | float,
    imag_scale: np.ndarray | float,
    f_scale: float,
    scale_type: str,
    plot_title: str,
    save_output: bool,
    show: bool = False,
    loss: str = "soft_l1",
) -> Path:
    """Plot raw errors and optimizer-scaled residuals, with shared raw limits."""
    import matplotlib.pyplot as plt

    if not results:
        raise ValueError("At least one fit result is required to create a plot")
    frequency = np.asarray(frequency)
    measured_impedance = np.asarray(measured_impedance)
    if (
        frequency.ndim != 1
        or frequency.size == 0
        or frequency.shape != measured_impedance.shape
        or not np.all(np.isfinite(frequency) & (frequency > 0))
    ):
        raise ValueError("Frequencies must be positive and match the impedance array")
    if not np.isfinite(f_scale) or f_scale <= 0:
        raise ValueError("f_scale must be finite and strictly positive")
    scales = [
        np.broadcast_to(np.asarray(scale, dtype=float), frequency.shape)
        for scale in (real_scale, imag_scale)
    ]
    if any(not np.all(np.isfinite(scale) & (scale > 0)) for scale in scales):
        raise ValueError("Residual scales must be finite and strictly positive")
    errors = []
    for result in results[:5]:
        predicted = np.asarray(result["predicted_impedance"])
        if predicted.shape != measured_impedance.shape:
            raise ValueError("Predicted impedance must match the measured array")
        errors.append(predicted - measured_impedance)

    order = np.argsort(frequency)
    figure, panels = plt.subplots(2, 2, figsize=(15, 9), sharex=True)
    raw_axes = panels[:, 0]
    axes = panels[:, 1]
    raw_axes[1].sharey(raw_axes[0])
    for index, (result, error) in enumerate(zip(results[:5], errors), start=1):
        for axis, component in zip(raw_axes, (error.real, error.imag)):
            axis.plot(
                frequency[order], component[order],
                label=_circuit_plot_label(index, result["circuit"]),
                linestyle="-" if index == 1 else "--",
                linewidth=2.5 if index == 1 else 1.3,
            )
        for axis, component, scale in zip(axes, (error.real, error.imag), scales):
            axis.plot(
                frequency[order], (component / scale)[order],
                label=_circuit_plot_label(index, result["circuit"]),
                linestyle="-" if index == 1 else "--",
                linewidth=2.5 if index == 1 else 1.3,
            )
    for axis, component in zip(axes, ("Real", "Imaginary")):
        axis.axhline(0, color="0.5", linewidth=0.8)
        if loss != "linear":
            axis.axhline(f_scale, color="black", linestyle=":", label="±f_scale")
            axis.axhline(-f_scale, color="black", linestyle=":")
        axis.set_xscale("log")
        axis.set_ylabel(f"{component} residual ({scale_type})")
        axis.grid(True, alpha=0.3)
    for axis, component in zip(raw_axes, ("Real", "Imaginary")):
        axis.axhline(0, color="0.5", linewidth=0.8)
        axis.set_xscale("log")
        axis.set_ylabel(f"{component} error (Ω)")
        axis.grid(True, alpha=0.3)
    raw_axes[0].set_title("Raw errors — shared vertical scale")
    axes[0].set_title(f"Normalized residuals ({scale_type})")
    raw_axes[0].legend(fontsize="small")
    if loss != "linear":
        axes[0].legend(handles=axes[0].lines[-2:-1], fontsize="small")
    for axis in panels[1]:
        axis.set_xlabel("Frequency (Hz)")
    loss_description = "loss = linear" if loss == "linear" else f"loss = {loss}, f_scale = {f_scale:g}"
    figure.suptitle(f"{plot_title}\nModel − data; {loss_description}")
    figure.tight_layout()
    output_path = Path(output_path)
    if save_output:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(output_path, dpi=300, bbox_inches="tight")
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
    ranking_metric: str,
    run_settings: Mapping[str, Any],
    dataset_info: Mapping[str, Any] | None = None,
    fit_stage: str | None = None,
    residual_plot_path: str | Path | None = None,
) -> Path:
    """Write run settings, processed data, and the ten best fits to JSON."""
    if not results:
        raise ValueError("At least one fit result is required to create a summary")

    frequency = np.asarray(frequency)
    successful_count = sum(bool(result["success"]) for result in results)
    finite_bics = [float(result["bic"]) for result in results if np.isfinite(result["bic"])]
    best_bic = min(finite_bics) if finite_bics else None

    circuit_metrics = []
    top_circuits = []
    for rank, result in enumerate(results, start=1):
        metrics = _fit_metric_record(result, rank, ranking_metric, best_bic, optimizer_settings)
        circuit_metrics.append(metrics)
        if rank <= 10:
            top_circuits.append({
                **metrics,
                "plot_label": _circuit_plot_label(rank, result["circuit"]) if rank <= 5 else None,
                "predicted_impedance_ohm": _complex_json_array(result["predicted_impedance"]),
            })

    document = {
        "format_version": 3,
        "fit_stage": fit_stage,
        "ranking_metric": ranking_metric,
        "run_settings": {
            key: _json_value(value) for key, value in run_settings.items()
        },
        "dataset": str(dataset_path),
        "dataset_info": dict(dataset_info) if dataset_info is not None else None,
        "circuit_collection": str(circuit_path),
        "grammar": grammar_name,
        "maximum_elements": maximum_elements,
        "frequency": {
            "points": int(frequency.size),
            "scalar_observations": int(2 * frequency.size),
            "minimum_hz": _json_number(np.min(frequency)),
            "maximum_hz": _json_number(np.max(frequency)),
        },
        "optimizer": {
            "name": optimizer,
            "value_definition": "optimizer_value = 2 * scipy_cost / frequency_points",
            "settings": {
                key: _json_value(value)
                for key, value in optimizer_settings.items()
            },
        },
        "circuits": {
            "fitted": len(results),
            "successful": successful_count,
            "unsuccessful": len(results) - successful_count,
            "total_attempts": sum(int(result.get("attempt_count", 1)) for result in results),
            "successful_attempts": sum(
                int(result.get("successful_attempt_count", bool(result["success"])))
                for result in results
            ),
            "total_function_evaluations": sum(
                int(result.get("total_function_evaluations", result.get("function_evaluations") or 0))
                for result in results
            ),
            "total_fit_elapsed_seconds": sum(
                float(result.get("total_fit_elapsed_seconds") or 0.0)
                for result in results
            ),
        },
        "associated_plot": str(plot_path),
        "associated_residual_plot": str(residual_plot_path) if residual_plot_path is not None else None,
        "circuits_shown_in_plot": min(5, len(results)),
        "circuit_metrics": circuit_metrics,
        "top_circuits": top_circuits,
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(document, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)
    return output_path


def _count_elements(node: CircuitNode) -> int:
    if isinstance(node, Element):
        return 1
    return sum(_count_elements(child) for child in node.children)  # type: ignore[attr-defined]


def _fit_metric_record(
    result: Mapping[str, Any],
    rank: int,
    ranking_metric: str,
    best_bic: float | None,
    optimizer_settings: Mapping[str, Any],
) -> dict[str, Any]:
    """Serialize the best attempt and all scoring metrics for one circuit."""
    mse = float(result["mse"])
    relative_mse = result.get("relative_mse")
    parameters = {name: _json_number(value) for name, value in result["parameters"].items()}
    return {
        "rank": rank,
        "circuit": str(result["circuit"]),
        "rand_start": result["rand_start"],
        "element_count": _count_elements(result["circuit"]),
        "parameter_count": len(parameters),
        "parameters": parameters,
        "initial_values": {
            name: _json_number(value)
            for name, value in result.get("initial_values", {}).items()
        },
        "parameter_bounds": {
            name: {"lower": _json_number(bounds[0]), "upper": _json_number(bounds[1])}
            for name, bounds in result.get("parameter_bounds", {}).items()
        },
        "parameters_at_bounds": list(result.get("parameters_at_bounds", [])),
        "mse": _json_number(mse),
        "optimizer_value": _optional_json_number(result.get("optimizer_value")),
        "rmse": _json_number(sqrt(mse)),
        "relative_mse": _optional_json_number(relative_mse),
        "relative_rmse": _optional_json_number(sqrt(relative_mse) if relative_mse is not None else None),
        "lp_error": _optional_json_number(result.get("lp_error")),
        "aic": _optional_json_number(result.get("aic")),
        "bic": _json_number(result["bic"]),
        "lp_bic": _optional_json_number(result.get("lp_bic")),
        "ebic": _optional_json_number(result.get("ebic")),
        "lp_ebic": _optional_json_number(result.get("lp_ebic")),
        "ebic_gamma": _optional_json_number(result.get("ebic_gamma")),
        "ranking_value": _optional_json_number(result.get(ranking_metric)),
        "delta_bic": _optional_json_number(
            float(result["bic"]) - best_bic if best_bic is not None else None
        ),
        "success": bool(result["success"]),
        "optimizer_status": result.get("optimizer_status"),
        "optimizer_message": result.get("optimizer_message"),
        "function_evaluations": result.get("function_evaluations"),
        "total_function_evaluations": result.get(
            "total_function_evaluations", result.get("function_evaluations")
        ),
        "fit_elapsed_seconds": result.get("fit_elapsed_seconds"),
        "total_fit_elapsed_seconds": result.get("total_fit_elapsed_seconds"),
        "attempt_count": result.get("attempt_count"),
        "successful_attempt_count": result.get("successful_attempt_count"),
        "selected_start_index": result.get("selected_start_index"),
        "optimizer_max_nfev": result.get(
            "optimizer_max_nfev", optimizer_settings.get("max_nfev")
        ),
    }


def _circuit_plot_label(rank: int, circuit: CircuitNode) -> str:
    """Return the ranked legend label, including the circuit expression."""
    return f"Circuit {rank}: {circuit}"


def _json_number(value: Any) -> float | int | None:
    number = value.item() if isinstance(value, np.generic) else value
    if isinstance(number, int):
        return number
    number = float(number)
    return number if np.isfinite(number) else None


def _optional_json_number(value: Any) -> float | int | None:
    return None if value is None else _json_number(value)


def _json_array(values: Any, shape: tuple[int, ...] | None = None) -> list[float | int | None]:
    array = np.asarray(values, dtype=float)
    if shape is not None:
        array = np.broadcast_to(array, shape)
    if array.ndim != 1:
        raise ValueError("Exported data arrays must be one-dimensional")
    return [_json_number(value) for value in array]


def _complex_json_array(values: Any) -> dict[str, list[float | int | None]]:
    array = np.asarray(values, dtype=complex)
    if array.ndim != 1:
        raise ValueError("Exported impedance arrays must be one-dimensional")
    return {"real": _json_array(array.real), "imag": _json_array(array.imag)}


def _json_value(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value
