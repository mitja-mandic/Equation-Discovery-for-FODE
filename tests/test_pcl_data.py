from pathlib import Path
import pickle
import tempfile
import unittest

import numpy as np

from fitting_parameters.load_data import load_pcl_spectrum
from fitting_parameters.model_selection import normalize_sigma


class PclDataTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "spectrum.pcl"

    def write_data(self, data):
        with self.path.open("wb") as handle:
            pickle.dump(data, handle)

    def test_channel_selection_preserves_points_and_ignores_metadata(self):
        frequency = np.array([1000.0, 0.001, 1.0])
        impedance = np.array([0.02 + 0.001j, -0.01 - 0.03j, 0.025 - 0.002j])
        self.write_data({
            "batt_1": (frequency, impedance * 2),
            "batt_2": (frequency, impedance, "uninterpreted", None, [np.nan]),
        })
        f, z, real_scale, imag_scale = load_pcl_spectrum(self.path, "batt_2")
        np.testing.assert_array_equal(f, frequency)
        np.testing.assert_array_equal(z, impedance)
        for scale in (real_scale, imag_scale):
            np.testing.assert_array_equal(normalize_sigma(scale), np.ones(3))

    def test_missing_channel_lists_available_channels(self):
        self.write_data({"batt_2": ([1.0], [0.02 - 0.01j])})
        with self.assertRaisesRegex(ValueError, "available channels: batt_2"):
            load_pcl_spectrum(self.path)

    def test_invalid_spectra_raise_clear_errors(self):
        cases = [
            ([], "dictionary"),
            ({"batt_1": ([1.0],)}, "must contain"),
            ({"batt_1": ([[1.0]], [[1j]])}, "one-dimensional"),
            ({"batt_1": ([1.0, 2.0], [1j])}, "matching"),
            ({"batt_1": ([], [])}, "at least one"),
            ({"batt_1": ([0.0], [1j])}, "positive"),
            ({"batt_1": ([-1.0], [1j])}, "positive"),
            ({"batt_1": ([np.nan], [1j])}, "finite"),
            ({"batt_1": ([np.inf], [1j])}, "finite"),
            ({"batt_1": ([1.0], [complex(1, np.nan)])}, "Impedances"),
        ]
        for data, message in cases:
            with self.subTest(data=data):
                self.write_data(data)
                with self.assertRaisesRegex(ValueError, message):
                    load_pcl_spectrum(self.path)


if __name__ == "__main__":
    unittest.main()
