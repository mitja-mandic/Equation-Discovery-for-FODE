import unittest

from Circuit_generation.circuit_class import (
    CPE,
    Gerischer,
    Inductor,
    Resistor,
    Series,
    SeriesResistance,
    Warburg,
)
from fitting_parameters.initialize_parameters import (
    generate_initial_values,
    set_deterministic_initial_values,
)


class InitialValueTests(unittest.TestCase):
    def setUp(self):
        self.circuit = Series(
            children=(
                SeriesResistance(),
                Resistor("R1"),
                CPE("Q2", "alpha2"),
                Warburg("sigma3"),
                Inductor("L4"),
                Gerischer("Rg5", "tau5"),
            )
        )

    def test_first_start_is_the_deterministic_start(self):
        starts = generate_initial_values(self.circuit, number_starts=6)

        self.assertEqual(
            starts[0],
            set_deterministic_initial_values(self.circuit),
        )

    def test_starts_are_reproducible(self):
        first = generate_initial_values(
            self.circuit,
            number_starts=6,
            random_seed=123,
        )
        second = generate_initial_values(
            self.circuit,
            number_starts=6,
            random_seed=123,
        )

        self.assertEqual(first, second)

    def test_random_starts_stay_in_the_configured_sampling_ranges(self):
        starts = generate_initial_values(self.circuit, number_starts=6)

        expected_ranges = {
            "Rs": (0.005, 0.5),
            "R1": (0.0002, 2.0),
            "Q2": (0.01, 100.0),
            "alpha2": (0.3, 0.98),
            "sigma3": (0.0001, 1.0),
            "L4": (1e-8, 1e-4),
            "Rg5": (0.0002, 2.0),
            "tau5": (0.01, 100.0),
        }

        for start in starts[1:]:
            for name, (lower, upper) in expected_ranges.items():
                with self.subTest(name=name, value=start[name]):
                    self.assertGreaterEqual(start[name], lower)
                    self.assertLessEqual(start[name], upper)

    def test_number_starts_must_be_positive(self):
        with self.assertRaisesRegex(ValueError, "at least 1"):
            generate_initial_values(self.circuit, number_starts=0)


if __name__ == "__main__":
    unittest.main()
