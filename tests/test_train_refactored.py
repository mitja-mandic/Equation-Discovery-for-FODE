import unittest
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from Circuit_generation.circuit_class import Resistor, Series, SeriesResistance
from fitting_parameters import train_refactored as train
from fitting_parameters.model_selection import compute_bic, compute_weighted_lp


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
                self.assertEqual(results[0]["ebic_gamma"], 1)
                self.assertEqual(best[0]["ebic_gamma"], 0.5)
                self.assertIsNone(best[1]["ebic_gamma"])
                self.assertIn("relative_mse", best[1])
                self.assertIn("optimizer_value", results[0])
                self.assertIn("optimizer_value", best[0])
                self.assertIn("scaled_lp_bic", results[0])
                self.assertIn("scaled_lp_bic", best[0])
                self.assertIn("scaled_lp_bic", best[1])
                self.assertEqual(scales.call_count, 6)
                self.assertTrue(all(call.args[-1] == mode for call in scales.call_args_list))

    def test_scaled_lp_bic_uses_optimizer_residual_divisors(self):
        circuit = SeriesResistance()
        frequency = np.array([1., 2.])
        measured = np.array([1. + 2j, 3. + 4j])
        real_scatter = np.array([2., 4.])
        imag_scatter = np.array([5., 10.])
        optimization = train._make_fitter(
            circuit, frequency, measured, ["Rs"],
            {"loss": "linear", "method": "trf"},
            real_scatter, imag_scatter, "scatter",
        )({"Rs": 2.})
        summary = train._summarize_fit(
            circuit, optimization, frequency, measured,
            real_scatter, imag_scatter, {1: 1}, "False",
            scale_type="scatter",
        )
        expected_error = compute_weighted_lp(
            measured, summary["predicted_impedance"],
            real_scatter, imag_scatter, p=0.5,
        )
        self.assertAlmostEqual(
            summary["scaled_lp_bic"], compute_bic(4, expected_error, 1)
        )

    def test_effective_evaluation_limit_is_retained_with_each_fit(self):
        frequency = np.array([1., 2., 3.])
        measured = np.array([1.+0j, 1.+0j, 1.+0j])
        for circuit, parameter_count in (
            (SeriesResistance(), 1),
            (Series((SeriesResistance(), Resistor("R1"))), 2),
        ):
            with self.subTest(circuit=str(circuit)):
                initial = train.fit_circuit_parameters_random_start(
                    circuit, frequency, measured, np.ones(3), np.ones(3),
                    number_starts=1,
                )
                self.assertEqual(
                    initial["optimizer_max_nfev"],
                    parameter_count * train.INITIAL_MAX_NFEV_PER_PARAMETER,
                )
        refined = train.finalize_fit(
            frequency, measured, SeriesResistance(), {"Rs": 1.},
            np.ones(3), np.ones(3),
        )
        self.assertEqual(refined["optimizer_max_nfev"], 10000)

    def test_selected_fit_keeps_aggregate_cost_without_each_attempt(self):
        initial = train.fit_circuit_parameters_random_start(
            SeriesResistance(), np.array([1., 2., 3.]),
            np.ones(3, dtype=complex), np.ones(3), np.ones(3),
            number_starts=3,
        )
        self.assertEqual(initial["attempt_count"], 3)
        self.assertGreaterEqual(initial["total_function_evaluations"], initial["result"].nfev)
        self.assertGreaterEqual(initial["total_fit_elapsed_seconds"], initial["fit_elapsed_seconds"])
        self.assertIn(initial["start_index"], range(3))

    def test_optimizer_value_matches_scipy_cost_and_linear_mse(self):
        frequency = np.array([1., 2., 3.])
        measured = np.array([1. + 0.2j, 1.5 + 0.3j, 2. + 0.4j])
        settings = {"loss": "linear", "method": "trf"}
        fit = train._make_fitter(
            SeriesResistance(), frequency, measured, ["Rs"], settings,
            np.ones(3), np.ones(3), "unscaled",
        )
        optimization = fit({"Rs": 1.})
        self.assertAlmostEqual(
            optimization["optimizer_value"], 2 * optimization["result"].cost / len(frequency)
        )
        self.assertAlmostEqual(optimization["optimizer_value"], optimization["score"])

        robust_fit = train._make_fitter(
            SeriesResistance(), frequency, measured, ["Rs"],
            {"loss": "soft_l1", "f_scale": 0.1, "method": "trf"},
            np.ones(3), np.ones(3), "unscaled",
        )
        robust = robust_fit({"Rs": 1.})
        residuals = robust["result"].fun
        expected = np.sum(2 * 0.1**2 * (np.sqrt(1 + (residuals / 0.1)**2) - 1)) / len(frequency)
        self.assertAlmostEqual(robust["optimizer_value"], expected)

    def test_best_start_uses_optimizer_value_even_when_mse_disagrees(self):
        attempts = [
            {
                "optimizer_value": value,
                "score": mse,
                "result": SimpleNamespace(success=True, nfev=1),
                "fit_elapsed_seconds": 0.1,
            }
            for value, mse in ((0.3, 0.1), (0.2, 0.2))
        ]
        with patch.object(train, "generate_initial_values", return_value=[{"Rs": 1.}, {"Rs": 2.}]), patch.object(
            train, "_make_fitter", return_value=lambda _: attempts.pop(0)
        ):
            selected = train.fit_circuit_parameters_random_start(
                SeriesResistance(), np.array([1.]), np.array([1. + 0j]),
                np.ones(1), np.ones(1), number_starts=2,
            )
        self.assertEqual(selected["start_index"], 1)
        self.assertEqual(selected["optimizer_value"], 0.2)


if __name__ == '__main__':
    unittest.main()
