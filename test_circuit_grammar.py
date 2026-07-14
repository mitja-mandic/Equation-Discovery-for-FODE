import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("circuit grammar.py")
SPEC = importlib.util.spec_from_file_location("circuit_grammar", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {MODULE_PATH}")

circuit_grammar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(circuit_grammar)


class GenerateCircuitsTest(unittest.TestCase):
    def test_zero_elements_returns_series_resistance(self) -> None:
        self.assertEqual(circuit_grammar.generate_circuits(0), ["Rs"])

    def test_one_element_returns_both_element_productions(self) -> None:
        self.assertEqual(
            circuit_grammar.generate_circuits(1),
            [
                "Rs",
                "Series(Rs, Parallel(R, Series(CPE, W)))",
                "Series(Rs, Parallel(R, CPE))",
            ],
        )

    def test_two_elements_generates_all_combinations_without_duplicates(self) -> None:
        circuits = circuit_grammar.generate_circuits(2)

        self.assertEqual(len(circuits), 7)
        self.assertEqual(len(circuits), len(set(circuits)))
        self.assertIn(
            "Series(Rs, Series(Parallel(R, CPE), Parallel(R, Series(CPE, W))))",
            circuits,
        )

    def test_negative_element_limit_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            circuit_grammar.generate_circuits(-1)


if __name__ == "__main__":
    unittest.main()
