import json
import tempfile
import unittest
from pathlib import Path

from Circuit_generation.custom_generation import LimitedCircuitGenerator
from circuit_export import (
    count_element_types,
    export_element_range,
    export_large_relaxed_count,
    load_circuits,
)


def element_count(circuit) -> int:
    return sum(count_element_types(circuit).values())


class CircuitExportTests(unittest.TestCase):
    def test_element_range_exports_cumulative_collections(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            paths = export_element_range(
                grammar_name="relaxed",
                minimum_elements=3,
                maximum_elements=5,
                output_directory=temporary_directory,
            )

            previous_circuits = set()
            for maximum_elements, path in zip(range(3, 6), paths):
                document = json.loads(path.read_text(encoding="utf-8"))
                circuits = load_circuits(path)

                self.assertEqual(
                    document["element_constraint"],
                    {
                        "comparison": "at_most",
                        "count": maximum_elements,
                        "minimum_count": 1,
                        "includes_series_resistance": True,
                    },
                )
                self.assertEqual(
                    {element_count(circuit) for circuit in circuits},
                    set(range(1, maximum_elements + 1)),
                )
                self.assertTrue(previous_circuits.issubset(circuits))
                previous_circuits = circuits

    def test_large_relaxed_export_matches_regular_cumulative_export(self):
        with tempfile.TemporaryDirectory() as regular_directory:
            regular_path = export_element_range(
                grammar_name="relaxed",
                minimum_elements=4,
                maximum_elements=4,
                output_directory=regular_directory,
            )[0]

            with tempfile.TemporaryDirectory() as large_directory:
                large_path = export_large_relaxed_count(
                    element_count=4,
                    output_directory=large_directory,
                )

                self.assertEqual(
                    load_circuits(large_path),
                    load_circuits(regular_path),
                )

    def test_no_gerischer_export_uses_requested_name_and_contains_no_g(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = export_element_range(
                grammar_name="relaxed_no_G",
                minimum_elements=5,
                maximum_elements=5,
                output_directory=temporary_directory,
                output_name="no_G_relaxed",
            )[0]

            document = json.loads(path.read_text(encoding="utf-8"))

            self.assertEqual(path.name, "no_G_relaxed_elements_5.json")
            self.assertEqual(document["grammar"]["name"], "relaxed_no_G")
            self.assertNotIn("G", document["elements_used"])
            for circuit in load_circuits(path):
                self.assertNotIn("G", count_element_types(circuit))

    def test_loader_accepts_existing_version_two_exports(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "legacy.json"
            path.write_text(
                json.dumps(
                    {
                        "format_version": 2,
                        "element_constraint": {
                            "comparison": "exact",
                            "count": 1,
                            "includes_series_resistance": True,
                        },
                        "circuit_count": 1,
                        "circuits": [["Rs", "Rs"]],
                    }
                ),
                encoding="utf-8",
            )

            circuits = load_circuits(path)

            self.assertEqual(len(circuits), 1)
            self.assertEqual(
                LimitedCircuitGenerator.count_elements(next(iter(circuits))),
                1,
            )


if __name__ == "__main__":
    unittest.main()
