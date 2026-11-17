import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

try:
    import matplotlib
except ModuleNotFoundError:
    matplotlib = None
else:
    matplotlib.use("Agg")

from Circuit_generation.circuit_class import SeriesResistance
from fitting_parameters.reporting import (
    build_fit_dataset_info,
    build_fit_output_paths,
    export_fit_summary,
    plot_circuit_fits,
    plot_fit_residuals,
)


class FitReportingTests(unittest.TestCase):
    @unittest.skipIf(matplotlib is None, "matplotlib is not installed")
    def test_residual_plot_uses_separate_scales_and_sorted_frequency(self):
        import matplotlib.pyplot as plt

        results = [{
            "circuit": SeriesResistance(),
            "predicted_impedance": np.array([5 + 8j, 3 + 5j]),
        }]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "residuals.png"
            with patch.object(plt, "close"):
                plot_fit_residuals(
                    np.array([10., 1.]), np.array([1 + 2j, 1 + 1j]),
                    results, path, real_scale=np.array([2., 4.]),
                    imag_scale=np.array([3., 2.]), f_scale=0.1,
                    scale_type="scatter", plot_title="Test",
                    save_output=True, show=False,
                )
                figure = plt.gcf()
            self.assertTrue(path.is_file())
            raw_real, real_axis, raw_imag, imag_axis = figure.axes
            np.testing.assert_allclose(raw_real.lines[0].get_xdata(), [1, 10])
            np.testing.assert_allclose(raw_real.lines[0].get_ydata(), [2, 4])
            np.testing.assert_allclose(raw_imag.lines[0].get_ydata(), [4, 6])
            np.testing.assert_allclose(raw_real.get_ylim(), raw_imag.get_ylim())
            self.assertEqual(len(raw_real.lines), 2)
            self.assertEqual(len(raw_imag.lines), 2)
            np.testing.assert_allclose(real_axis.lines[0].get_xdata(), [1, 10])
            np.testing.assert_allclose(real_axis.lines[0].get_ydata(), [0.5, 2])
            np.testing.assert_allclose(imag_axis.lines[0].get_ydata(), [2, 2])
            np.testing.assert_allclose(real_axis.lines[2].get_ydata(), [0.1, 0.1])
            np.testing.assert_allclose(imag_axis.lines[3].get_ydata(), [-0.1, -0.1])
            plt.close(figure)

    @unittest.skipIf(matplotlib is None, "matplotlib is not installed")
    def test_linear_loss_plot_omits_robust_threshold(self):
        import matplotlib.pyplot as plt

        results = [{
            "circuit": SeriesResistance(),
            "predicted_impedance": np.array([2 + 1j, 3 + 2j]),
        }]
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(plt, "close"):
                plot_fit_residuals(
                    np.array([1., 10.]), np.array([1 + 1j, 1 + 1j]),
                    results, Path(directory) / "residuals.png",
                    real_scale=1.0, imag_scale=1.0, f_scale=0.001,
                    scale_type="relative", plot_title="Test", save_output=True,
                    loss="linear",
                )
                figure = plt.gcf()
            self.assertEqual(len(figure.axes[1].lines), 2)
            self.assertIn("loss = linear", figure._suptitle.get_text())
            self.assertNotIn("f_scale", figure._suptitle.get_text())
            plt.close(figure)

    def setUp(self):
        measured = np.array([1.0 - 0.5j, 1.5 - 0.25j])
        self.measured = measured
        self.frequency = np.array([1.0, 10.0])
        self.results = [
            {
                "circuit": SeriesResistance(),
                "parameters": {"Rs": np.float64(rank)},
                "predicted_impedance": measured + rank * 0.01,
                "mse": rank * 0.1,
                "optimizer_value": rank * 0.05,
                "aic": rank + 1.0,
                "bic": rank + 2.0,
                "scaled_lp_bic": rank + 3.0,
                "success": rank != 10,
                "rand_start": "False",
                "optimizer_status": 1,
                "optimizer_message": "test result",
                "function_evaluations": rank,
                "optimizer_max_nfev": rank * 5,
            }
            for rank in range(1, 13)
        ]

    def test_output_paths_share_a_dataset_and_fit_identifier(self):
        plot_path, summary_path = build_fit_output_paths(
            project_directory="project",
            dataset_path="data/spectrum/example.npz",
            grammar_name="relaxed_elements",
            maximum_elements=5,
            filename_suffix="test",
        )

        self.assertEqual(
            plot_path.name,
            "example_relaxed_elements_5_best_5_test.png",
        )
        self.assertEqual(plot_path.parent, Path("project/Results/Plots/Nyquists"))
        self.assertEqual(
            summary_path.name,
            "example_relaxed_elements_5_fit_summary_test.json",
        )
        self.assertEqual(summary_path.parent, Path("project/Results/fit_results"))

    def test_output_paths_can_start_with_a_filename_prefix(self):
        plot_path, summary_path = build_fit_output_paths(
            project_directory="project",
            dataset_path="data/spectrum/example.npz",
            grammar_name="relaxed_elements",
            maximum_elements=5,
            filename_prefix="no_G_",
            filename_suffix="test",
        )

        self.assertTrue(plot_path.name.startswith("no_G_"))
        self.assertTrue(summary_path.name.startswith("no_G_"))

    def test_pcl_channel_is_part_of_output_name(self):
        plot_path, summary_path = build_fit_output_paths(
            project_directory="project",
            dataset_path="data/battery/example.pcl",
            grammar_name="relaxed",
            maximum_elements=5,
            filename_suffix="first_round",
            channel="batt_2",
        )
        self.assertIn("example_batt_2_relaxed_5", plot_path.name)
        self.assertIn("example_batt_2_relaxed_5", summary_path.name)

    def test_plot_uses_requested_ranking_styles_and_labels(self):
        fake_matplotlib = types.ModuleType("matplotlib")
        fake_pyplot = types.ModuleType("matplotlib.pyplot")
        fake_figure = MagicMock()
        fake_axis = MagicMock()
        circuit_one_label = MagicMock()
        circuit_one_label.get_text.return_value = "Circuit 1: Rs"
        fake_axis.legend.return_value.get_texts.return_value = [
            circuit_one_label
        ]
        fake_pyplot.subplots = MagicMock(
            return_value=(fake_figure, fake_axis)
        )
        fake_pyplot.show = MagicMock()
        fake_pyplot.close = MagicMock()
        fake_matplotlib.pyplot = fake_pyplot

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "best_5.png"
            with patch.dict(
                sys.modules,
                {
                    "matplotlib": fake_matplotlib,
                    "matplotlib.pyplot": fake_pyplot,
                },
            ):
                plot_circuit_fits(
                    measured_impedance=self.measured,
                    results=self.results,
                    output_path=output_path,
                    show=False,
                    save_output=True,
                    plot_title="Top five",
                )

        self.assertEqual(fake_axis.plot.call_count, 5)
        plot_options = [call.kwargs for call in fake_axis.plot.call_args_list]
        self.assertEqual(
            [options["label"] for options in plot_options],
            [f"Circuit {rank}: Rs" for rank in range(1, 6)],
        )
        self.assertEqual(plot_options[0]["linestyle"], "-")
        self.assertEqual(plot_options[0]["linewidth"], 3.2)
        for options in plot_options[1:]:
            self.assertEqual(options["linestyle"], "--")
            self.assertEqual(options["linewidth"], 1.6)
        circuit_one_label.set_fontweight.assert_called_once_with("bold")
        fake_figure.savefig.assert_called_once()

    @unittest.skipUnless(matplotlib is not None, "Matplotlib is not available")
    def test_plot_writes_five_ranked_circuits(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            plot_path = Path(temporary_directory) / "best_5.png"

            returned_path = plot_circuit_fits(
                measured_impedance=self.measured,
                results=self.results,
                output_path=plot_path,
                show=False,
                save_output=True,
                plot_title="Top five",
            )

            self.assertEqual(returned_path, plot_path)
            self.assertTrue(plot_path.is_file())
            self.assertGreater(plot_path.stat().st_size, 0)

    def test_summary_contains_counts_top_ten_and_plot_reference(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "fit_summary.json"
            source_path = Path(temporary_directory) / "measurement.pcl"
            source_path.write_bytes(b"source data")
            dataset_info = build_fit_dataset_info(
                source_path=source_path,
                mode="pcl",
                channel="batt_2",
                preprocessing="Selected channel arrays",
                frequency=self.frequency,
                measured_impedance=self.measured,
                loader_real_scale=np.ones(2),
                loader_imag_scale=np.ones(2),
                normalized_real_scale=np.ones(2),
                normalized_imag_scale=np.ones(2),
                fitting_real_divisor=np.array([2., 3.]),
                fitting_imag_divisor=np.array([4., 5.]),
                coherence=None,
            )
            self.results[0].update({
                "predicted_impedance": self.measured + (0.01 + 0.02j),
                "relative_mse": 0.25,
                "lp_error": 0.3,
                "lp_bic": 1.2,
                "ebic": 4.5,
                "lp_ebic": 6.7,
                "attempt_count": 6,
                "successful_attempt_count": 5,
                "total_function_evaluations": 60,
                "fit_elapsed_seconds": 0.5,
                "total_fit_elapsed_seconds": 2.5,
                "selected_start_index": 3,
                "initial_values": {"Rs": 0.05},
                "parameter_bounds": {"Rs": (1e-10, 1e4)},
                "parameters_at_bounds": [],
            })

            export_fit_summary(
                results=self.results,
                output_path=output_path,
                plot_path="Plots/Nyquists/example_best_5.png",
                dataset_path="data/spectrum/example.npz",
                circuit_path="data/circuits/relaxed_elements_5.json",
                grammar_name="relaxed_elements",
                maximum_elements=5,
                optimizer="least_squares",
                optimizer_settings={"max_nfev": 100},
                frequency=self.frequency,
                ranking_metric="bic",
                run_settings={
                    "residual_scale": "scatter",
                    "scatter_floor": 0.1,
                    "number_starts": 6,
                    "random_seed": 42,
                    "first_round_ranking_metric": "mse",
                    "second_round_ranking_metric": "bic",
                    "reoptimization_error_margin": 0.2,
                },
                dataset_info=dataset_info,
                fit_stage="refined",
                residual_plot_path="Plots/Residuals/example_residuals.png",
            )

            document = json.loads(output_path.read_text(encoding="utf-8"))

            self.assertEqual(document["circuits"]["fitted"], 12)
            self.assertEqual(document["format_version"], 3)
            self.assertEqual(document["fit_stage"], "refined")
            self.assertEqual(document["ranking_metric"], "bic")
            self.assertEqual(
                document["optimizer"]["value_definition"],
                "optimizer_value = 2 * scipy_cost / frequency_points",
            )
            self.assertEqual(document["run_settings"]["residual_scale"], "scatter")
            self.assertEqual(document["run_settings"]["scatter_floor"], 0.1)
            self.assertEqual(document["run_settings"]["number_starts"], 6)
            self.assertEqual(document["run_settings"]["random_seed"], 42)
            self.assertEqual(document["run_settings"]["first_round_ranking_metric"], "mse")
            self.assertEqual(document["run_settings"]["second_round_ranking_metric"], "bic")
            self.assertEqual(document["run_settings"]["reoptimization_error_margin"], 0.2)
            self.assertEqual(document["circuits"]["successful"], 11)
            self.assertEqual(len(document["circuit_metrics"]), 12)
            self.assertEqual(document["circuit_metrics"][11]["rank"], 12)
            self.assertEqual(document["circuit_metrics"][0]["relative_mse"], 0.25)
            self.assertEqual(document["circuit_metrics"][0]["optimizer_value"], 0.05)
            self.assertEqual(document["circuits"]["total_attempts"], 17)
            self.assertEqual(document["circuits"]["total_function_evaluations"], 137)
            self.assertEqual(document["dataset_info"]["mode"], "pcl")
            self.assertEqual(document["dataset_info"]["channel"], "batt_2")
            self.assertEqual(document["dataset_info"]["frequency_hz"], [1.0, 10.0])
            self.assertEqual(document["frequency"]["scalar_observations"], 4)
            self.assertEqual(document["dataset_info"]["measured_impedance_ohm"]["imag"], [-0.5, -0.25])
            self.assertEqual(document["dataset_info"]["fitting_residual_divisors"]["real"], [2.0, 3.0])
            self.assertEqual(len(document["dataset_info"]["source_sha256"]), 64)
            self.assertEqual(len(document["top_circuits"]), 10)
            self.assertEqual(
                document["associated_plot"],
                "Plots/Nyquists/example_best_5.png",
            )
            self.assertEqual(
                document["top_circuits"][0]["plot_label"],
                "Circuit 1: Rs",
            )
            self.assertIsNone(document["top_circuits"][5]["plot_label"])
            self.assertEqual(document["top_circuits"][0]["optimizer_max_nfev"], 5)
            self.assertEqual(document["top_circuits"][0]["relative_mse"], 0.25)
            self.assertEqual(document["top_circuits"][0]["relative_rmse"], 0.5)
            self.assertEqual(document["top_circuits"][0]["lp_error"], 0.3)
            self.assertEqual(len([row for row in document["circuit_metrics"] if "scaled_lp_bic" in row]), 12)
            self.assertEqual(document["circuit_metrics"][0]["scaled_lp_bic"], 4.0)
            self.assertEqual(document["top_circuits"][0]["scaled_lp_bic"], 4.0)
            self.assertEqual(document["top_circuits"][0]["optimizer_value"], 0.05)
            self.assertEqual(document["top_circuits"][0]["aic"], 2.0)
            self.assertEqual(document["top_circuits"][0]["ebic"], 4.5)
            self.assertEqual(document["top_circuits"][0]["predicted_impedance_ohm"]["real"], [1.01, 1.51])
            self.assertEqual(document["top_circuits"][0]["total_function_evaluations"], 60)
            self.assertEqual(document["associated_residual_plot"], "Plots/Residuals/example_residuals.png")

    def test_delta_bic_uses_lowest_bic_even_when_ranked_by_mse(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            results = [dict(self.results[0], bic=10.0), dict(self.results[1], bic=8.0)]
            path = Path(temporary_directory) / "summary.json"
            export_fit_summary(
                results=results,
                output_path=path,
                plot_path="plot.png",
                dataset_path="measurement.npz",
                circuit_path="circuits.json",
                grammar_name="relaxed",
                maximum_elements=5,
                optimizer="least_squares",
                optimizer_settings={},
                frequency=self.frequency,
                ranking_metric="mse",
                run_settings={},
            )
            document = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual([row["delta_bic"] for row in document["top_circuits"]], [2.0, 0.0])
        self.assertEqual(
            [row["scaled_lp_bic"] for row in document["top_circuits"]],
            [4.0, 5.0],
        )


if __name__ == "__main__":
    unittest.main()
