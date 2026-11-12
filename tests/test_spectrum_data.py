"""Check median and direct loading of repeated F/Z spectra."""

import tempfile
import unittest
from pathlib import Path

import numpy as np

from fitting_parameters.load_data import load_spectrum, load_spectrum_direct


class SpectrumDataTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "spectrum.npz"
        self.blocks = [
            np.array([
                [np.nan + 1j * np.nan, 1 + 1j, 2 + 2j, 3 + 3j, 4 + 4j],
                [np.nan + 1j * np.nan, 5 + 1j, 6 + 2j, 7 + 3j, 8 + 4j],
            ]),
            np.array([[10 + 1j, 11 + 2j, 12 + 3j]]),
        ]
        np.savez(
            self.path,
            F=np.array([1., 10., 100.]),
            Z=np.array(self.blocks, dtype=object),
        )

    def test_direct_uses_middle_column_per_block_and_keeps_repeat_scatter(self):
        frequency, impedance, real_scatter, imag_scatter, columns = load_spectrum_direct(
            self.path
        )
        np.testing.assert_array_equal(frequency, [1., 10., 100.])
        np.testing.assert_array_equal(impedance, [2 + 2j, 6 + 2j, 11 + 2j])
        self.assertEqual(columns, [2, 1])
        median = load_spectrum(self.path)
        np.testing.assert_array_equal(median[1], [2.5 + 2.5j, 6.5 + 2.5j, 11 + 2j])
        np.testing.assert_array_equal(real_scatter, median[2])
        np.testing.assert_array_equal(imag_scatter, median[3])

    def test_explicit_column_and_invalid_selection(self):
        frequency, impedance, *_ = load_spectrum_direct(self.path, column_index=0)
        np.testing.assert_array_equal(frequency, [100.])
        np.testing.assert_array_equal(impedance, [10 + 1j])
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            load_spectrum_direct(self.path, column_index=-1)
        with self.assertRaisesRegex(ValueError, "outside impedance block 1"):
            load_spectrum_direct(self.path, column_index=3)

    def test_empty_direct_selection_is_rejected(self):
        np.savez(
            self.path,
            F=np.array([1.]),
            Z=np.array([[[np.nan + 1j * np.nan, 1 + 1j]]]),
        )
        with self.assertRaisesRegex(ValueError, "No finite impedance points"):
            load_spectrum_direct(self.path, column_index=0)


if __name__ == "__main__":
    unittest.main()
