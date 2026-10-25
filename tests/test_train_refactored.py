import unittest
from unittest.mock import patch
import numpy as np
from Circuit_generation.circuit_class import SeriesResistance
from fitting_parameters import train_refactored as train


class ResidualScalingTests(unittest.TestCase):
    def test_optimizer_receives_all_residual_modes(self):
        frequency = np.array([1., 2., 3.])
        measured = np.array([1.+2j, 3.+4j, 0.+0j])
        real_scatter = np.array([2., 3., 4.])
        imag_scatter = np.array([4., 5., 6.])
        error = 2. - measured
        divisors = {
            'unscaled': (1., 1.),
            'scatter': (real_scatter, imag_scatter),
            'relative': (np.array([1., 3., .1]), np.array([2., 4., .2])),
            'magnitude': (
                np.array([np.sqrt(5), 5., 0.1 * (np.sqrt(5) + 5) / 2]),
                np.array([np.sqrt(5), 5., 0.1 * (np.sqrt(5) + 5) / 2]),
            ),
        }
        for mode, (real, imag) in divisors.items():
            with self.subTest(mode=mode):
                fit = train._make_fitter(
                    SeriesResistance(), frequency, measured, ['Rs'], {},
                    real_scatter, imag_scatter, mode,
                )
                with patch.object(train, 'least_squares') as solver:
                    solver.return_value.x = np.log([2.])
                    fit({'Rs': 2.})
                    residual, x0 = solver.call_args.args
                    np.testing.assert_allclose(
                        residual(x0), np.concatenate([error.real / real, error.imag / imag])
                    )

    def test_scale_validation_and_zero_data(self):
        measured = np.zeros(3, dtype=complex)
        for mode, scatter in [('bad', 1.), ('scatter', 0.), ('scatter', np.nan)]:
            with self.assertRaises(ValueError):
                train._residual_scales(measured, scatter, 1., mode)
        for mode in ('relative', 'magnitude'):
            real, imag = train._residual_scales(measured, None, None, mode)
            np.testing.assert_array_equal(real, np.ones(3))
            np.testing.assert_array_equal(imag, np.ones(3))

    def test_magnitude_floor_with_majority_zero_and_invalid_data(self):
        real, imag = train._residual_scales(
            np.array([0j, 0j, 3 + 4j]), None, None, 'magnitude',
        )
        np.testing.assert_allclose(real, [.5, .5, 5])
        np.testing.assert_array_equal(real, imag)
        for value in (np.nan, np.inf):
            with self.assertRaises(ValueError):
                train._residual_scales(
                    np.array([1 + 0j, complex(value, 0)]), None, None, 'magnitude',
                )

    def test_mode_reaches_initial_final_and_manual_fits(self):
        circuit = SeriesResistance()
        frequency = np.array([1., 2., 3.])
        measured = np.array([.1+.01j, .2+.02j, .3+.03j])
        for mode in ('unscaled', 'scatter', 'relative', 'magnitude'):
            with self.subTest(mode=mode), patch.object(
                train, '_residual_scales', wraps=train._residual_scales
            ) as scales:
                results, _, best = train.compare_circuits(
                    [circuit], {1: 1}, frequency, measured,
                    np.ones(3), np.ones(3), circuit, scale_type=mode,
                )
                self.assertEqual(len(results), 1)
                self.assertEqual(len(best), 2)
                self.assertEqual(scales.call_count, 3)
                self.assertTrue(all(call.args[-1] == mode for call in scales.call_args_list))


if __name__ == '__main__':
    unittest.main()
