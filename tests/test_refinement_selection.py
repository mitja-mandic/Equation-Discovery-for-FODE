import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from Circuit_generation.circuit_class import CPE, Inductor, Parallel, Resistor, Series, SeriesResistance, Warburg
from fitting_parameters import train_refactored
from fitting_parameters.model_selection import count_circuit_arrangements, select_refinement_candidates


class RefinementSelectionTests(unittest.TestCase):
    def test_combinatorial_score_counts_distinct_arrangements(self):
        rs, inductor, cpe, warburg = SeriesResistance(), Inductor(), CPE(), Warburg()
        circuit = Series((rs, inductor, Parallel((cpe, warburg))))
        swapped = Series((rs, inductor, Parallel((warburg, cpe))))
        self.assertEqual(count_circuit_arrangements(circuit), 3)
        self.assertEqual(count_circuit_arrangements(swapped), 3)
        self.assertEqual(count_circuit_arrangements(Series((rs, inductor, cpe, warburg))), 1)
        self.assertEqual(
            count_circuit_arrangements(Series((rs, Parallel((Resistor(), Resistor(), cpe))))), 1,
        )
        self.assertEqual(
            count_circuit_arrangements(Series((rs, Parallel((Resistor(), Series((Resistor(), cpe))))))), 1,
        )
        optimization = {
            "parameters": {"Rs": 1., "L": 1e-6, "Q": 1., "alpha": .8, "sigma": .1},
            "result": SimpleNamespace(success=True, status=1, message="test", nfev=1),
            "score": .5,
            "optimizer_value": .5,
        }
        summary = train_refactored._summarize_fit(
            circuit, optimization, np.array([1., 2.]), np.ones(2, dtype=complex),
            np.ones(2), np.ones(2), {}, "False", scale_type="unscaled", manual=True,
        )
        scaled_lp = train_refactored.compute_weighted_lp(
            np.ones(2, dtype=complex), summary["predicted_impedance"], 1, 1, p=.5,
        )
        self.assertEqual(summary["arrangement_count"], 3)
        self.assertAlmostEqual(
            summary["combinatorial_score"],
            4 * np.log(scaled_lp)
            + train_refactored.COMBINATORIAL_ELEMENT_WEIGHT * 4
            + train_refactored.COMBINATORIAL_ARRANGEMENT_WEIGHT * np.log(3),
        )
        harsher = train_refactored._summarize_fit(
            circuit, optimization, np.array([1., 2.]), np.ones(2, dtype=complex),
            np.ones(2), np.ones(2), {}, "False", scale_type="unscaled", manual=True,
            combinatorial_element_weight=18,
            combinatorial_arrangement_weight=.5,
        )
        self.assertAlmostEqual(
            harsher["combinatorial_score"],
            4 * np.log(scaled_lp) + 18 * 4 + .5 * np.log(3),
        )

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
