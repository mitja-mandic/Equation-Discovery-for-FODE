import sys
import unittest
from pathlib import Path

import numpy as np


CIRCUIT_GENERATION_DIR = Path(__file__).with_name("Circuit_generation")
sys.path.insert(0, str(CIRCUIT_GENERATION_DIR))

import circuit_from_tree  # noqa: E402
import generate_trees  # noqa: E402
import main as circuit_main  # noqa: E402


class GenerateTreesTest(unittest.TestCase):
    def test_tokens_become_normalized_tree(self) -> None:
        tokens = ("Rs", "+", "(", "R", "||", "CPE", ")")

        tree = generate_trees.canonical_circuit_tree(tokens)

        self.assertEqual(tree, ("+", ("Rs", ("||", ("CPE", "R")))))

    def test_normalization_flattens_repeated_series_connections(self) -> None:
        parsed_tree = ("+", "Rs", ("+", "CPE", "W"))

        self.assertEqual(
            generate_trees.normalize(parsed_tree),
            ("+", ("Rs", "CPE", "W")),
        )


class CircuitFromTreeTest(unittest.TestCase):
    def test_resistor_supports_frequency_arrays_for_plotting(self) -> None:
        circuit = circuit_from_tree.circuit_from_tree("Rs")
        omega = np.array([1.0, 10.0, 100.0])

        impedance = circuit.impedance(omega, {"Rs": 0.25})

        np.testing.assert_array_equal(impedance, np.full(3, 0.25))

    def test_zarc_tree_becomes_executable_circuit(self) -> None:
        circuit = circuit_from_tree.circuit_from_tree(("+", ("Rs", "zarc")))
        parameters = {"Rs": 0.1, "R1": 2.0, "Q1": 0.25, "alpha1": 1.0}
        omega = 3.0

        actual = circuit.impedance(omega, parameters)
        cpe_impedance = 1 / (parameters["Q1"] * 1j * omega)
        expected_zarc = 1 / (1 / parameters["R1"] + 1 / cpe_impedance)

        self.assertEqual(
            circuit.parameter_names,
            ("Rs", "R1", "Q1", "alpha1"),
        )
        self.assertAlmostEqual(actual, parameters["Rs"] + expected_zarc)

    def test_relaxed_tree_numbers_elements_from_left_to_right(self) -> None:
        tree = ("+", ("Rs", ("||", ("CPE", "R"))))

        circuit = circuit_from_tree.circuit_from_tree(tree)

        self.assertEqual(
            circuit.parameter_names,
            ("Rs", "Q1", "alpha1", "R2"),
        )
        self.assertEqual(str(circuit), "Rs + (CPE(Q1, alpha1) || R2)")

    def test_missing_parameters_are_reported_before_evaluation(self) -> None:
        circuit = circuit_from_tree.circuit_from_tree("CPE")

        with self.assertRaisesRegex(ValueError, "Q1, alpha1"):
            circuit.impedance(1.0, {})

    def test_zarc_has_executable_python_impedance_expression(self) -> None:
        circuit = circuit_from_tree.circuit_from_tree(("+", ("Rs", "zarc")))

        self.assertEqual(
            circuit.impedance_expression(),
            "Rs + 1 / (1 / R1 + Q1 * (1j * omega) ** alpha1)",
        )

    def test_python_expression_matches_numerical_circuit(self) -> None:
        tree = (
            "+",
            (
                "Rs",
                ("||", ("G", ("+", ("CPE", "W")))),
            ),
        )
        circuit = circuit_from_tree.circuit_from_tree(tree)
        values = {
            "omega": 7.0,
            "Rs": 0.1,
            "Rg1": 2.0,
            "tauG1": 0.5,
            "Q2": 0.02,
            "alpha2": 0.8,
            "sigma3": 1.5,
        }

        numerical = circuit.impedance(values["omega"], values)
        from_expression = eval(
            circuit.impedance_expression(),
            {"__builtins__": {}},
            values,
        )

        self.assertAlmostEqual(numerical, from_expression)


class MainWorkflowTest(unittest.TestCase):
    def test_equation_listing_is_numbered_and_deterministic(self) -> None:
        trees = {("+", ("Rs", "zarc")), "Rs"}

        listing = circuit_main.build_equation_listing(trees)

        self.assertEqual(
            listing,
            (
                "1. Circuit: Rs\n"
                "   Z_1(omega) = Rs\n"
                "   Parameters: Rs\n\n"
                "2. Circuit: Rs + (R1 || CPE(Q1, alpha1))\n"
                "   Z_2(omega) = Rs + 1 / "
                "(1 / R1 + Q1 * (1j * omega) ** alpha1)\n"
                "   Parameters: Rs, R1, Q1, alpha1"
            ),
        )


if __name__ == "__main__":
    unittest.main()
