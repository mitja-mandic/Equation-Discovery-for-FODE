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
    build_fit_output_paths,
    export_fit_summary,
    plot_circuit_fits,
)


class FitReportingTests(unittest.TestCase):
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
                "aic": rank + 1.0,
                "bic": rank + 2.0,
                "success": rank != 10,
                "optimizer_status": 1,
                "optimizer_message": "test result",
                "function_evaluations": rank,
            }
            for rank in range(1, 13)
        ]

    def test_output_paths_share_a_dataset_and_fit_identifier(self):
        plot_path, summary_path = build_fit_output_paths(
            project_directory="project",
            dataset_path="data/spectrum/example.npz",
            grammar_name="relaxed_elements",
            maximum_elements=5,
        )

        self.assertEqual(
            plot_path.name,
            "example_relaxed_elements_5_best_5.png",
        )
        self.assertEqual(plot_path.parts[-3:-1], ("Plots", "Nyquists"))
        self.assertEqual(
            summary_path.name,
            "example_relaxed_elements_5_fit_summary.json",
        )
        self.assertEqual(summary_path.parts[-2], "fit_results")

    def test_output_paths_can_start_with_a_filename_prefix(self):
        plot_path, summary_path = build_fit_output_paths(
            project_directory="project",
            dataset_path="data/spectrum/example.npz",
            grammar_name="relaxed_elements",
            maximum_elements=5,
            filename_prefix="no_G_",
        )

        self.assertTrue(plot_path.name.startswith("no_G_"))
        self.assertTrue(summary_path.name.startswith("no_G_"))

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
            )

            self.assertEqual(returned_path, plot_path)
            self.assertTrue(plot_path.is_file())
            self.assertGreater(plot_path.stat().st_size, 0)

    def test_summary_contains_counts_top_ten_and_plot_reference(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "fit_summary.json"

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
            )

            document = json.loads(output_path.read_text(encoding="utf-8"))

            self.assertEqual(document["circuits"]["fitted"], 12)
            self.assertEqual(document["circuits"]["successful"], 11)
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


if __name__ == "__main__":
    unittest.main()
