"""Export generated circuit objects to reusable JSON files.

Each output file represents one grammar/depth combination and is written to
``data/circuits`` by default.  Besides the circuit topologies, the file records
the grammar source and the element types that occur in the generated circuits.
"""

from __future__ import annotations

import argparse
import json
from array import array
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any

from Circuit_generation.circuit_class import (
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
EXPORT_FORMAT_VERSION = 2
DEFAULT_OUTPUT_DIRECTORY = Path(__file__).resolve().parent / "data" / "circuits"


def export_large_relaxed_count(
    element_count: int,
    output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY,
) -> Path:
    """Export a large exact-size relaxed set using an integer DAG.

    This representation interns every normalized network once and uses shallow
    integer keys during generation. It produces the same compact JSON topology
    format as the regular bounded exporter, while avoiding millions of Python
    circuit objects during the largest runs.
    """
    from Circuit_generation.circuit_from_grammar import GRAMMAR_SOURCES

    if element_count < 2:
        raise ValueError("element_count must be at least 2")

    # Fixed IDs for primitive nodes. Connection nodes are appended afterward.
    # Counts use six four-bit fields in this order: Rs, R, L, CPE, W, G.
    node_keys: list[tuple[int, ...]] = [(kind,) for kind in range(6)]
    node_sizes = bytearray([1] * 6)
    packed_counts = array("I", (1 << (4 * kind) for kind in range(6)))
    interned: dict[tuple[int, ...], int] = {
        key: node_id for node_id, key in enumerate(node_keys)
    }

    SERIES_KIND = 6
    PARALLEL_KIND = 7
    RESISTOR_ID = 1
    INDUCTOR_ID = 2

    def connect(kind: int, left: int, right: int) -> tuple[int, bool]:
        children: list[int] = []
        for node_id in (left, right):
            key = node_keys[node_id]
            if key[0] == kind:
                children.extend(key[1:])
            else:
                children.append(node_id)

        # Match simplify(): only one immediate primitive R and L is retained.
        simplified: list[int] = []
        seen_collapsible: set[int] = set()
        for node_id in children:
            if node_id in (RESISTOR_ID, INDUCTOR_ID):
                if node_id in seen_collapsible:
                    continue
                seen_collapsible.add(node_id)
            simplified.append(node_id)

        simplified.sort(key=lambda node_id: (_dag_sort_rank(node_keys[node_id][0]), node_id))
        if len(simplified) == 1:
            return simplified[0], False

        key = (kind, *simplified)
        existing = interned.get(key)
        if existing is not None:
            return existing, False

        node_id = len(node_keys)
        interned[key] = node_id
        node_keys.append(key)
        node_sizes.append(sum(node_sizes[child] for child in simplified))
        packed_counts.append(sum(packed_counts[child] for child in simplified))
        return node_id, True

    # The relaxed grammar starts from all five non-Rs primitive elements.
    buckets: dict[int, array[int]] = {1: array("I", range(1, 6))}
    maximum_network_size = element_count - 1

    for size in range(2, maximum_network_size + 1):
        bucket = array("I")
        for left_size in range(1, size // 2 + 1):
            right_size = size - left_size
            left_nodes = buckets[left_size]
            right_nodes = buckets[right_size]

            if left_size == right_size:
                pairs = (
                    (left_nodes[i], left_nodes[j])
                    for i in range(len(left_nodes))
                    for j in range(i, len(left_nodes))
                )
            else:
                pairs = product(left_nodes, right_nodes)

            for left, right in pairs:
                for kind in (SERIES_KIND, PARALLEL_KIND):
                    node_id, is_new = connect(kind, left, right)
                    if is_new and node_sizes[node_id] == size:
                        bucket.append(node_id)

        buckets[size] = bucket
        print(f"Built relaxed network size {size}: {len(bucket)} topologies", flush=True)

    final_networks = buckets[maximum_network_size]

    # Adding Rs to a root Series removes an immediate primitive R according to
    # the existing normalizer. Such a circuit has one fewer physical element
    # and therefore does not belong in this exact-size export.
    def belongs_to_final_set(node_id: int) -> bool:
        key = node_keys[node_id]
        return key[0] != SERIES_KIND or RESISTOR_ID not in key[1:]

    circuit_count = 0
    aggregate_counts = [0] * 6
    for node_id in final_networks:
        if not belongs_to_final_set(node_id):
            continue
        circuit_count += 1
        packed = packed_counts[node_id] + 1  # Add the mandatory Rs field.
        for kind in range(6):
            aggregate_counts[kind] += (packed >> (4 * kind)) & 0xF

    element_names = ("Rs", "R", "L", "CPE", "W", "G")
    totals = {
        name: aggregate_counts[index]
        for index, name in enumerate(element_names)
        if aggregate_counts[index]
    }
    metadata = {
        "format_version": EXPORT_FORMAT_VERSION,
        "grammar": {
            "name": "relaxed",
            "source": GRAMMAR_SOURCES["relaxed"].strip(),
        },
        "element_constraint": {
            "comparison": "exact",
            "count": element_count,
            "includes_series_resistance": True,
        },
        "elements_used": sorted(totals),
        "total_element_counts": dict(sorted(totals.items())),
        "circuit_count": circuit_count,
    }

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / f"relaxed_elements_{element_count}.json"
    temporary_path = output_path.with_suffix(".json.tmp")

    with temporary_path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write("{")
        for index, (key, value) in enumerate(metadata.items()):
            if index:
                stream.write(",")
            json.dump(key, stream)
            stream.write(":")
            json.dump(value, stream, separators=(",", ":"))
        stream.write(',"circuits":[')

        written = 0
        for node_id in final_networks:
            if not belongs_to_final_set(node_id):
                continue
            if written:
                stream.write(",")
            stream.write(_serialize_dag_circuit(node_id, node_keys))
            written += 1

        stream.write("]}\n")

    temporary_path.replace(output_path)
    return output_path


def _dag_sort_rank(kind: int) -> int:
    """Return the circuit_class normalization rank for an integer-DAG kind."""
    return (0, 10, 20, 30, 40, 50, 100, 110)[kind]


def _serialize_dag_circuit(
    network_id: int,
    node_keys: list[tuple[int, ...]],
) -> str:
    """Serialize one DAG network after attaching and numbering Rs."""
    parameter_index = 1

    def serialize(node_id: int) -> str:
        nonlocal parameter_index
        key = node_keys[node_id]
        kind = key[0]

        if kind == 0:
            return '["Rs","Rs"]'
        if kind == 1:
            value = f'["R","R{parameter_index}"]'
            parameter_index += 1
            return value
        if kind == 2:
            value = f'["L","L{parameter_index}"]'
            parameter_index += 1
            return value
        if kind == 3:
            value = f'["CPE","Q{parameter_index}","alpha{parameter_index}"]'
            parameter_index += 1
            return value
        if kind == 4:
            value = f'["W","sigma{parameter_index}"]'
            parameter_index += 1
            return value
        if kind == 5:
            value = f'["G","Rg{parameter_index}","tau{parameter_index}"]'
            parameter_index += 1
            return value

        connection = "S" if kind == 6 else "P"
        return f'["{connection}",' + ",".join(serialize(child) for child in key[1:]) + "]"

    network_key = node_keys[network_id]
    if network_key[0] == 6:
        children = (0, *network_key[1:])
    else:
        children = (0, network_id)

    return '["S",' + ",".join(serialize(child) for child in children) + "]"


def export_circuits(
    grammar_name: str,
    depth: int,
    output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY,
) -> Path:
    """Generate circuits and save one deterministic JSON collection.

    The filename includes the grammar and depth, so exports made with different
    generator settings do not overwrite one another.
    """
    # Import the generator only when an export is requested.  Loading an
    # existing JSON file therefore does not require NLTK or rerun generation.
    from Circuit_generation.circuit_from_grammar import (
        GRAMMAR_SOURCES,
        generate_trees,
    )

    if grammar_name not in GRAMMAR_SOURCES:
        choices = ", ".join(sorted(GRAMMAR_SOURCES))
        raise ValueError(
            f"Unknown grammar {grammar_name!r}; choose from {choices}"
        )
    if depth < 1:
        raise ValueError("depth must be at least 1")

    circuits = generate_trees(grammar_name, depth)
    ordered_circuits = sorted(circuits, key=str)

    # Count element types over the complete exported collection.  The list of
    # keys makes it easy to see which physical elements this grammar produced.
    total_element_counts: Counter[str] = Counter()
    circuit_documents = []

    for circuit_id, circuit in enumerate(ordered_circuits, start=1):
        element_counts = count_element_types(circuit)
        total_element_counts.update(element_counts)

        circuit_documents.append(
            {
                "id": circuit_id,
                "expression": str(circuit),
                "elements_used": sorted(element_counts),
                "element_counts": dict(sorted(element_counts.items())),
                "topology": node_to_data(circuit),
            }
        )

    document = {
        "format_version": EXPORT_FORMAT_VERSION,
        "grammar": {
            "name": grammar_name,
            "depth": depth,
            # Keeping the exact source makes the export traceable even if the
            # named grammar is edited later.
            "source": GRAMMAR_SOURCES[grammar_name].strip(),
        },
        "elements_used": sorted(total_element_counts),
        "total_element_counts": dict(sorted(total_element_counts.items())),
        "circuit_count": len(circuit_documents),
        "circuits": circuit_documents,
    }

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / f"{grammar_name}_depth_{depth}.json"

    # Write a temporary file first so an interrupted export cannot leave a
    # partially written JSON file at the final path.
    temporary_path = output_path.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)

    return output_path


def export_element_range(
    grammar_name: str,
    minimum_elements: int,
    maximum_elements: int,
    output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY,
) -> list[Path]:
    """Export one JSON file per exact physical-element count.

    Unlike NLTK derivation depth, these limits count actual circuit elements,
    including the mandatory series resistance ``Rs``.
    """
    from Circuit_generation.circuit_from_grammar import GRAMMAR_SOURCES
    from Circuit_generation.custom_generation import (
        GeneratorConfig,
        LimitedCircuitGenerator,
    )

    if grammar_name not in GRAMMAR_SOURCES:
        choices = ", ".join(sorted(GRAMMAR_SOURCES))
        raise ValueError(
            f"Unknown grammar {grammar_name!r}; choose from {choices}"
        )
    if minimum_elements < 1:
        raise ValueError("minimum_elements must be at least 1")
    if maximum_elements < minimum_elements:
        raise ValueError("maximum_elements must be at least minimum_elements")

    config = GeneratorConfig.for_grammar(
        max_elements=maximum_elements,
        grammar_name=grammar_name,
    )
    generator = LimitedCircuitGenerator(config)
    # Keep normalized subtrees shared during the large generation phase.
    # Parameter names are assigned one circuit at a time during streaming.
    circuits = generator.generate_unnumbered()

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = []

    for element_count in range(minimum_elements, maximum_elements + 1):
        matching_circuits = {
            circuit
            for circuit in circuits
            if generator.count_elements(circuit) == element_count
        }
        output_path = (
            output_directory
            / f"{grammar_name}_elements_{element_count}.json"
        )
        _write_element_count_export(
            circuits=matching_circuits,
            grammar_name=grammar_name,
            grammar_source=GRAMMAR_SOURCES[grammar_name],
            element_count=element_count,
            output_path=output_path,
        )
        paths.append(output_path)

    return paths


def _write_element_count_export(
    circuits: set[CircuitNode],
    grammar_name: str,
    grammar_source: str,
    element_count: int,
    output_path: Path,
) -> None:
    """Write one exact-element-count collection using streaming JSON."""
    from Circuit_generation.circuit_from_grammar import add_indexes

    ordered_circuits = sorted(circuits, key=lambda node: (str(node), repr(node)))
    total_element_counts: Counter[str] = Counter()

    for circuit in ordered_circuits:
        total_element_counts.update(count_element_types(circuit))

    metadata = {
        "format_version": EXPORT_FORMAT_VERSION,
        "grammar": {
            "name": grammar_name,
            "source": grammar_source.strip(),
        },
        "element_constraint": {
            "comparison": "exact",
            "count": element_count,
            "includes_series_resistance": True,
        },
        "elements_used": sorted(total_element_counts),
        "total_element_counts": dict(sorted(total_element_counts.items())),
        "circuit_count": len(ordered_circuits),
    }

    temporary_path = output_path.with_suffix(".json.tmp")
    with temporary_path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write("{")
        for index, (key, value) in enumerate(metadata.items()):
            if index:
                stream.write(",")
            json.dump(key, stream)
            stream.write(":")
            json.dump(value, stream, separators=(",", ":"))

        stream.write(',"circuits":[')
        for index, circuit in enumerate(ordered_circuits):
            if index:
                stream.write(",")
            numbered_circuit = add_indexes(circuit)
            json.dump(
                node_to_data(numbered_circuit),
                stream,
                separators=(",", ":"),
            )
        stream.write("]}\n")

    temporary_path.replace(output_path)


def load_circuits(path: str | Path) -> set[CircuitNode]:
    """Reconstruct circuit objects from a JSON file created by this module."""
    document = json.loads(Path(path).read_text(encoding="utf-8"))

    if document.get("format_version") not in (1, EXPORT_FORMAT_VERSION):
        raise ValueError(
            "Unsupported circuit export format; regenerate the JSON file"
        )

    circuits = set()
    for circuit_document in document["circuits"]:
        topology = (
            circuit_document["topology"]
            if isinstance(circuit_document, dict)
            else circuit_document
        )
        circuits.add(node_from_data(topology))

    if len(circuits) != document["circuit_count"]:
        raise ValueError("Circuit count does not match the JSON metadata")

    return circuits


def count_element_types(node: CircuitNode) -> Counter[str]:
    """Return the number of occurrences of every element type in a circuit."""
    if isinstance(node, Element):
        return Counter({_element_name(node): 1})

    counts: Counter[str] = Counter()
    for child in node.children:  # type: ignore[attr-defined]
        counts.update(count_element_types(child))
    return counts


def node_to_data(node: CircuitNode) -> list[Any]:
    """Convert a circuit tree into compact JSON-compatible recursive data."""
    # SeriesResistance must be checked before Resistor because it is a
    # Resistor subclass.
    if type(node) is SeriesResistance:
        return ["Rs", node.resistance]
    if type(node) is Resistor:
        return ["R", node.resistance]
    if type(node) is CPE:
        return ["CPE", node.coefficient, node.exponent]
    if type(node) is Warburg:
        return ["W", node.coefficient]
    if type(node) is Inductor:
        return ["L", node.inductance]
    if type(node) is Gerischer:
        return ["G", node.resistance, node.time_constant]
    if type(node) in (Series, Parallel):
        connection_name = "S" if type(node) is Series else "P"
        return [connection_name, *[node_to_data(child) for child in node.children]]

    raise TypeError(f"Cannot serialize circuit node {type(node).__name__}")


def node_from_data(data: dict[str, Any] | list[Any]) -> CircuitNode:
    """Reconstruct one circuit tree from its serialized representation."""
    if isinstance(data, list):
        return _node_from_compact_data(data)

    node_type = data["type"]

    if node_type == "SeriesResistance":
        return SeriesResistance(resistance=data["resistance"])
    if node_type == "Resistor":
        return Resistor(resistance=data["resistance"])
    if node_type == "CPE":
        return CPE(
            coefficient=data["coefficient"],
            exponent=data["exponent"],
        )
    if node_type == "Warburg":
        return Warburg(coefficient=data["coefficient"])
    if node_type == "Inductor":
        return Inductor(inductance=data["inductance"])
    if node_type == "Gerischer":
        return Gerischer(
            resistance=data["resistance"],
            time_constant=data["time_constant"],
        )
    if node_type in ("Series", "Parallel"):
        connection_type = Series if node_type == "Series" else Parallel
        return connection_type(
            tuple(node_from_data(child) for child in data["children"])
        )

    raise ValueError(f"Unknown circuit node type {node_type!r}")


def _node_from_compact_data(data: list[Any]) -> CircuitNode:
    """Reconstruct one node from the compact format-version-2 encoding."""
    node_type = data[0]

    if node_type == "Rs":
        return SeriesResistance(resistance=data[1])
    if node_type == "R":
        return Resistor(resistance=data[1])
    if node_type == "CPE":
        return CPE(coefficient=data[1], exponent=data[2])
    if node_type == "W":
        return Warburg(coefficient=data[1])
    if node_type == "L":
        return Inductor(inductance=data[1])
    if node_type == "G":
        return Gerischer(resistance=data[1], time_constant=data[2])
    if node_type in ("S", "P"):
        connection_type = Series if node_type == "S" else Parallel
        return connection_type(tuple(node_from_data(child) for child in data[1:]))

    raise ValueError(f"Unknown compact circuit node type {node_type!r}")


def _element_name(element: Element) -> str:
    """Return the short, parameter-independent name of an element type."""
    names = {
        SeriesResistance: "Rs",
        Resistor: "R",
        CPE: "CPE",
        Warburg: "W",
        Inductor: "L",
        Gerischer: "G",
    }

    try:
        return names[type(element)]
    except KeyError as error:
        raise TypeError(
            f"Unknown circuit element {type(element).__name__}"
        ) from error


def _parse_arguments() -> argparse.Namespace:
    # This import is intentionally local for the same reason as the import in
    # export_circuits(): cached files can be loaded without importing NLTK.
    from Circuit_generation.circuit_from_grammar import GRAMMAR_SOURCES

    parser = argparse.ArgumentParser(
        description="Generate circuits and export them to data/circuits."
    )
    parser.add_argument(
        "--grammar",
        nargs="+",
        choices=sorted(GRAMMAR_SOURCES),
        default=["relaxed"],
        help="One or more grammars to export (default: relaxed).",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=5,
        help="NLTK generation-depth limit (default: 5).",
    )
    parser.add_argument(
        "--element-range",
        nargs=2,
        type=int,
        metavar=("MIN", "MAX"),
        help="Export one file per exact physical-element count.",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Destination directory (default: data/circuits).",
    )
    return parser.parse_args()


def main() -> None:
    """Export every grammar requested on the command line."""
    arguments = _parse_arguments()

    for grammar_name in arguments.grammar:
        if arguments.element_range is not None:
            minimum_elements, maximum_elements = arguments.element_range
            paths = export_element_range(
                grammar_name=grammar_name,
                minimum_elements=minimum_elements,
                maximum_elements=maximum_elements,
                output_directory=arguments.output_directory,
            )
            for path in paths:
                print(f"Exported {grammar_name!r} circuits to {path}")
        else:
            path = export_circuits(
                grammar_name=grammar_name,
                depth=arguments.depth,
                output_directory=arguments.output_directory,
            )
            print(f"Exported {grammar_name!r} circuits to {path}")


if __name__ == "__main__":
    main()
