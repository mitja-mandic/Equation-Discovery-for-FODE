import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from Circuit_generation.circuit_class import CPE, Parallel, Resistor, Series
from data.simulation.simulator import frequency_sweep, save_spectrum, simulate
from fitting_parameters.load_data import load_spectrum


class SimulationTests(unittest.TestCase):
    def test_rc_spectrum_matches_analytic_solution(self):
        circuit = Series(children=(
            Resistor("Rs"),
            Parallel(children=(Resistor("R"), CPE("C", "alpha"))),
        ))
        frequency = frequency_sweep()
        result = simulate(circuit, {"Rs": 2, "R": 3, "C": 0.02, "alpha": 1}, frequency)
        expected = 2 + 3 / (1 + 2j * np.pi * frequency * 3 * 0.02)
        np.testing.assert_allclose(result.clean_impedance, expected)
        np.testing.assert_array_equal(
            result.measurements, np.repeat(result.clean_impedance[:, None], 20, axis=1)
        )

    def test_sweep_spans_nine_decades_uniformly(self):
        frequency = frequency_sweep()
        self.assertEqual(len(frequency), 271)
        self.assertEqual(frequency[0], 1e-3)
        self.assertEqual(frequency[-1], 1e6)
        np.testing.assert_allclose(np.diff(np.log10(frequency)), 1 / 30)

    def test_noise_is_reproducible_and_has_requested_scale(self):
        options = dict(repeats=100000, relative_noise=0.03, absolute_noise_ohm=0.08)
        first = simulate(Resistor(), {"R": 2}, np.array([1.0]), seed=12, **options)
        second = simulate(Resistor(), {"R": 2}, np.array([1.0]), seed=12, **options)
        np.testing.assert_array_equal(first.measurements, second.measurements)
        np.testing.assert_allclose(first.noise_std_ohm, 0.1)
        noise = first.measurements[0] - 2
        self.assertAlmostEqual(noise.real.std(), 0.1, delta=0.001)
        self.assertAlmostEqual(noise.imag.std(), 0.1, delta=0.001)
        self.assertLess(abs(np.corrcoef(noise.real, noise.imag)[0, 1]), 0.01)

    def test_saved_data_round_trips_through_existing_loader(self):
        spectrum = simulate(Resistor(), {"R": 2}, frequency_sweep(), relative_noise=0.01)
        with tempfile.TemporaryDirectory() as directory:
            path = save_spectrum(spectrum, Path(directory) / "nested" / "test.npz")
            with np.load(path, allow_pickle=False) as data:
                self.assertEqual(data["Z"].shape, (1, 271, 20))
                self.assertEqual(json.loads(str(data["metadata_json"]))["parameters"], {"R": 2.0})
                np.testing.assert_array_equal(data["Z_clean"], spectrum.clean_impedance)
            frequency, impedance, real_sigma, imag_sigma = load_spectrum(path)
        np.testing.assert_array_equal(frequency, spectrum.frequency_hz)
        expected = np.median(spectrum.measurements.real, axis=1) + 1j * np.median(
            spectrum.measurements.imag, axis=1
        )
        np.testing.assert_array_equal(impedance, expected)
        self.assertTrue(np.all(real_sigma > 0))
        self.assertTrue(np.all(imag_sigma > 0))

    def test_invalid_configuration_is_rejected(self):
        for parameters in ({}, {"R": -1}, {"R": float("nan")}, {"R": 1, "typo": 2}):
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                simulate(Resistor(), parameters, np.array([1.0]))
        for frequency in ([], [0], [-1], [np.inf], [[1]]):
            with self.subTest(frequency=frequency), self.assertRaises(ValueError):
                simulate(Resistor(), {"R": 1}, frequency)
        for options in ({"repeats": 0}, {"relative_noise": -1}, {"absolute_noise_ohm": np.nan}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                simulate(Resistor(), {"R": 1}, np.array([1.0]), **options)
        with self.assertRaises(ValueError):
            simulate(Series(children=()), {}, np.array([1.0]))
        with self.assertRaises(ValueError):
            simulate(CPE(), {"Q": 1, "alpha": 1.1}, np.array([1.0]))
        for limits in ((0, 1, 30), (2, 1, 30), (1, np.inf, 30), (1, 2, 0)):
            with self.subTest(limits=limits), self.assertRaises(ValueError):
                frequency_sweep(*limits)


if __name__ == "__main__":
    unittest.main()
