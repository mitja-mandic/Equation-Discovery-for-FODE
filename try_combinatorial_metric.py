"""Inspect the combinatorial complexity of circuits from a saved collection.

Run from the repository root with: .venv/bin/python try_combinatorial_metric.py
"""

from collections import Counter
from math import log
from pathlib import Path

from Circuit_generation.circuit_export import count_element_types, load_circuits
from fitting_parameters.model_selection import count_circuit_arrangements


# Configuration: edit these values to inspect another circuit collection or
# element multiset. Set ELEMENT_COUNTS to None to show every loaded circuit.
CIRCUIT_PATH = Path(__file__).resolve().parent / "data/circuits/no_G_relaxed_elements_4.json"
ELEMENT_COUNTS: dict[str, int] | None = {"Rs": 1, "L": 2, "CPE": 1}
SHOW_PLOT = True
ALPHA = 0.5  # Weight for log(arrangement count).
BETA = 0.5 # Weight for the number of elements, including Rs.


def show_distribution(arrangement_counts: list[int], element_counts: list[int]) -> None:
    """Show the arrangement and weighted-complexity distributions."""
    import matplotlib.pyplot as plt

    arrangement_penalties = Counter(log(count) for count in arrangement_counts)
    penalty_values = sorted(arrangement_penalties)
    combined_scores = [
        ALPHA * log(arrangements) + BETA * elements
        for arrangements, elements in zip(arrangement_counts, element_counts)
    ]
    combined_penalties = Counter(combined_scores)

    first_width = 8
    figure, (arrangement_axis, combined_axis) = plt.subplots(
        1, 2, figsize=(first_width + 10, 5),
        gridspec_kw={"width_ratios": (first_width, 10)},
    )
    bar_width = (
        0.8 * min(right - left for left, right in zip(penalty_values, penalty_values[1:]))
        if len(penalty_values) > 1 else 0.5
    )
    arrangement_axis.bar(
        penalty_values,
        [arrangement_penalties[value] for value in penalty_values],
        width=bar_width,
    )
    arrangement_axis.set_xlabel("Penalty: log(arrangement count)")
    arrangement_axis.set_ylabel("Circuits with this penalty")
    arrangement_axis.set_title(f"Arrangement penalty ({len(arrangement_counts)} circuits)")

    penalty_values = sorted(combined_penalties)
    combined_axis.plot(
        penalty_values,
        [combined_penalties[value] for value in penalty_values],
        marker="o",
    )
    combined_axis.set_xlabel("alpha * log(arrangements) + beta * number of elements")
    combined_axis.set_ylabel("Circuits with this penalty")
    combined_axis.set_title(
        f"Combined penalty ({len(combined_scores)} circuits; alpha={ALPHA}, beta={BETA})"
    )
    combined_axis.grid(alpha=0.25)
    figure.tight_layout()

    plt.show()
    plt.close(figure)


def main() -> None:
    circuits = sorted(load_circuits(CIRCUIT_PATH), key=str)
    matching = [
        circuit for circuit in circuits
        if ELEMENT_COUNTS is None or count_element_types(circuit) == Counter(ELEMENT_COUNTS)
    ]

    print(f"Loaded {len(circuits)} circuits from {CIRCUIT_PATH}")
    print(f"Showing {len(matching)} circuits with element counts {ELEMENT_COUNTS}\n")
    print("arrangements  log(arrangements)  circuit")
    arrangement_counts = []
    element_counts = []
    for circuit in matching:
        arrangements = count_circuit_arrangements(circuit)
        arrangement_counts.append(arrangements)
        element_counts.append(sum(count_element_types(circuit).values()))
        print(f"{arrangements:>12}  {log(arrangements):>17.4f}  {circuit}")

    if SHOW_PLOT and arrangement_counts:
        show_distribution(arrangement_counts, element_counts)


if __name__ == "__main__":
    main()
