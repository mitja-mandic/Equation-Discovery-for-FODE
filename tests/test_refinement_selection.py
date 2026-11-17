import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from Circuit_generation.circuit_class import SeriesResistance
from fitting_parameters import train_refactored
from fitting_parameters.model_selection import select_refinement_candidates


class RefinementSelectionTests(unittest.TestCase):
    def test_inclusive_margin_and_nonfinite_errors(self):
        results = [{"mse": value} for value in [12., 10., 12.01, np.nan, np.inf]]
        self.assertEqual(select_refinement_candidates(results, .2), results[:2])
        self.assertEqual(select_refinement_candidates(results, 0), [results[1]])

    def test_empty_zero_and_invalid_margin(self):
        self.assertEqual(select_refinement_candidates([], .2), [])
        results = [{"mse": 0.}, {"mse": .001}, {"mse": 0.}]
        self.assertEqual(select_refinement_candidates(results, .2), [results[0], results[2]])
        for margin in [-1, np.nan, np.inf]:
            with self.subTest(margin=margin), self.assertRaises(ValueError):
                select_refinement_candidates([], margin)

    def test_optimizer_value_refinement_margin(self):
        results = [
            {"optimizer_value": 0.1, "mse": 2.0},
            {"optimizer_value": 0.119, "mse": 1.0},
            {"optimizer_value": 0.121, "mse": 0.1},
        ]
        self.assertEqual(
            select_refinement_candidates(results, 0.2, "optimizer_value"), results[:2]
        )

    def test_scaled_lp_bic_uses_additive_bic_margin(self):
        results = [
            {"scaled_lp_bic": -100.},
            {"scaled_lp_bic": -91.},
            {"scaled_lp_bic": -89.},
        ]
        self.assertEqual(
            select_refinement_candidates(results, 0.2, "scaled_lp_bic"),
            results[:2],
        )

    def test_circuit_refinement_uses_optimizer_value_when_mse_disagrees(self):
        circuits = [SeriesResistance("R0"), SeriesResistance("R1")]
        attempts = [
            {
                "parameters": {"R0": 1.0},
                "result": SimpleNamespace(success=True, status=1, message="test", nfev=1),
                "score": 0.01,
                "optimizer_value": 0.2,
                "start_index": 0,
            },
            {
                "parameters": {"R1": 2.0},
                "result": SimpleNamespace(success=True, status=1, message="test", nfev=1),
                "score": 0.2,
                "optimizer_value": 0.1,
                "start_index": 0,
            },
        ]
        with patch.object(
            train_refactored, "fit_circuit_parameters_random_start", side_effect=attempts
        ), patch.object(train_refactored, "finalize_fit", return_value=attempts[1]) as refine:
            results, _, refined = train_refactored.compare_circuits(
                circuits, {1: 2}, np.array([1., 2.]),
                np.full(2, 1.2 + 0.1j),
                np.ones(2), np.ones(2), None, reoptimization_error_margin=0,
            )
        self.assertEqual(results[0]["circuit"], circuits[1])
        self.assertEqual(len(refined), 1)
        self.assertEqual(refine.call_args.args[2], circuits[1])

    def test_fitter_refines_every_eligible_circuit_from_fitted_parameters(self):
        circuits = [SeriesResistance(f"R{i}") for i in range(8)]
        frequency = np.array([1., 2., 3.])
        measured = np.ones(3, dtype=complex)
        errors = [10., 10.2, 10.4, 10.6, 10.8, 11., 12., 12.01]
        status = SimpleNamespace(success=True, status=1, message="test", nfev=1)
        attempts = [
            {"parameters": {f"R{i}": 2. + i}, "result": status,
             "score": error, "optimizer_value": error, "start_index": 0}
            for i, error in enumerate(errors)
        ]
        for margin, count in [(0., 1), (.2, 7)]:
            with self.subTest(margin=margin), patch.object(
                train_refactored, "fit_circuit_parameters_random_start", side_effect=attempts
            ), patch.object(train_refactored, "finalize_fit", side_effect=attempts[:count]) as refine:
                results, _, refined = train_refactored.compare_circuits(
                    circuits, {1: len(circuits)}, frequency, measured,
                    np.ones(3), np.ones(3), None,
                    reoptimization_error_margin=margin,
                )
                self.assertEqual(len(results), 8)
                self.assertEqual(len(refined), count)
                self.assertEqual(refine.call_count, count)
                for i, call in enumerate(refine.call_args_list):
                    self.assertEqual(call.args[2], circuits[i])
                    self.assertEqual(call.args[3], attempts[i]["parameters"])


if __name__ == "__main__":
    unittest.main()
