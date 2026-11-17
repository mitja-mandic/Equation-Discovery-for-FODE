"""Check that fitting starts only through the explicit entry point."""
import contextlib
import io
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "main.py"


class MainEntrypointTests(unittest.TestCase):
    def test_import_does_not_start_workflow(self):
        with patch("Circuit_generation.circuit_export.load_circuits") as load, contextlib.redirect_stdout(io.StringIO()) as output:
            namespace = runpy.run_path(str(SCRIPT), run_name="imported_main")
        load.assert_not_called()
        self.assertEqual(output.getvalue(), "")
        self.assertTrue(callable(namespace["main"]))

    def test_script_starts_workflow(self):
        with patch("sys.argv", [str(SCRIPT)]), patch("Circuit_generation.circuit_export.load_circuits", side_effect=RuntimeError("entry reached")) as load:
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, "entry reached"):
                runpy.run_path(str(SCRIPT), run_name="__main__")
        load.assert_called_once()


    def test_cli_options_reach_fit_and_reports(self):
        import main
        import numpy as np
        from contextlib import ExitStack
        original = dict(main.LEAST_SQUARES_SETTINGS)
        with ExitStack() as stack:
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            stack.enter_context(patch.object(main, "load_circuits", return_value=[]))
            stack.enter_context(patch.object(main, "load_spectrum", return_value=(np.array([1.]), np.array([2.+1j]), np.ones(1), np.ones(1))))
            compare = stack.enter_context(patch.object(main, "compare_circuits", return_value=([], {}, [])))
            plot = stack.enter_context(patch.object(main, "plot_circuit_fits"))
            residual_plot = stack.enter_context(patch.object(main, "plot_fit_residuals"))
            report = stack.enter_context(patch.object(main, "export_fit_summary"))
            main.main([
                "--data-path", str(SCRIPT.parent.parent / "external.npz"),
                "--residual-scale", "scatter", "--scatter-floor", "0.2",
                "--f-scale", "1.5", "--loss", "linear", "--number-starts", "3", "--random-seed", "7",
                "--sort-first-round", "lp_error", "--sort-second-round", "mse",
                "--reoptimization-error-margin", "0.3",
                "--save-results", "--no-show-plots",
            ])
        kwargs = compare.call_args.kwargs
        self.assertEqual(kwargs["scale_type"], "scatter")
        self.assertEqual(kwargs["number_starts"], 3)
        self.assertEqual(kwargs["random_seed"], 7)
        self.assertEqual(kwargs["least_squares_settings"]["f_scale"], 1.5)
        self.assertEqual(kwargs["final_least_squares_settings"]["f_scale"], 1.5)
        self.assertEqual(kwargs["least_squares_settings"]["loss"], "linear")
        self.assertEqual(kwargs["final_least_squares_settings"]["loss"], "linear")
        self.assertEqual(
            kwargs["final_least_squares_settings"]["max_nfev"],
            main.FINAL_LEAST_SQUARES_SETTINGS["max_nfev"],
        )
        self.assertFalse(plot.call_args.kwargs["show"])
        self.assertEqual(residual_plot.call_args.kwargs["f_scale"], 1.5)
        self.assertEqual(residual_plot.call_args.kwargs["loss"], "linear")
        self.assertEqual(report.call_count, 2)
        initial_report, refined_report = report.call_args_list
        self.assertEqual(initial_report.kwargs["ranking_metric"], "lp_error")
        self.assertEqual(refined_report.kwargs["ranking_metric"], "mse")
        self.assertEqual(initial_report.kwargs["fit_stage"], "first_round")
        self.assertEqual(refined_report.kwargs["fit_stage"], "refined")
        for call in (initial_report, refined_report):
            self.assertEqual(call.kwargs["optimizer"], "least_squares")
            self.assertEqual(call.kwargs["run_settings"]["residual_scale"], "scatter")
            self.assertEqual(call.kwargs["run_settings"]["loss"], "linear")
            self.assertEqual(call.kwargs["run_settings"]["scatter_floor"], 0.2)
            self.assertEqual(call.kwargs["run_settings"]["number_starts"], 3)
            self.assertEqual(call.kwargs["run_settings"]["random_seed"], 7)
            self.assertEqual(call.kwargs["run_settings"]["initial_max_nfev_per_parameter"], 7)
            self.assertEqual(call.kwargs["run_settings"]["first_round_ranking_metric"], "lp_error")
            self.assertEqual(call.kwargs["run_settings"]["second_round_ranking_metric"], "mse")
            self.assertEqual(call.kwargs["run_settings"]["reoptimization_error_margin"], 0.3)
            self.assertEqual(call.kwargs["dataset_info"]["mode"], "spectrum")
            self.assertEqual(call.kwargs["dataset_info"]["frequency_hz"], [1.0])
            self.assertEqual(call.kwargs["dataset_info"]["measured_impedance_ohm"]["real"], [2.0])
            self.assertEqual(call.kwargs["residual_plot_path"].parent.name, "Residuals")
        self.assertIn(
            main.FILENAME_SUFFIX_REOPTIMIZED,
            str(report.call_args.kwargs["plot_path"]),
        )
        self.assertEqual(main.LEAST_SQUARES_SETTINGS, original)

    def test_invalid_numeric_options_are_rejected(self):
        import main
        for flag, value in (("--f-scale", "0"), ("--f-scale", "nan"), ("--number-starts", "0"), ("--random-seed", "-1")):
            with self.subTest(flag=flag, value=value), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main.build_parser().parse_args([flag, value])

    def test_optimizer_value_is_default_first_round_and_available_for_both(self):
        import main
        defaults = main.build_parser().parse_args([])
        self.assertEqual(defaults.sort_first_round, "optimizer_value")
        self.assertEqual(defaults.sort_second_round, "bic")
        options = main.build_parser().parse_args([
            "--sort-first-round", "optimizer_value",
            "--sort-second-round", "optimizer_value",
        ])
        self.assertEqual(options.sort_second_round, "optimizer_value")
        scaled_options = main.build_parser().parse_args([
            "--sort-first-round", "scaled_lp_bic",
            "--sort-second-round", "scaled_lp_bic",
        ])
        self.assertEqual(scaled_options.sort_first_round, "scaled_lp_bic")
        self.assertEqual(scaled_options.sort_second_round, "scaled_lp_bic")

    def test_direct_spectrum_mode_reaches_loader_and_report(self):
        import main
        import numpy as np
        from contextlib import ExitStack

        with ExitStack() as stack:
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            stack.enter_context(patch.object(main, "load_circuits", return_value=[]))
            loader = stack.enter_context(patch.object(
                main, "load_spectrum_direct",
                return_value=(np.array([1.]), np.array([2. + 1j]), np.ones(1), np.ones(1), [2]),
            ))
            stack.enter_context(patch.object(main, "compare_circuits", return_value=([], {}, [])))
            stack.enter_context(patch.object(main, "plot_circuit_fits"))
            stack.enter_context(patch.object(main, "plot_fit_residuals"))
            report = stack.enter_context(patch.object(main, "export_fit_summary"))
            main.main([
                "--data-mode", "spectrum_direct",
                "--data-path", str(SCRIPT.parent / "sample.npz"),
                "--spectrum-column-index", "2",
                "--save-results", "--no-show-plots",
            ])
        self.assertEqual(loader.call_args.kwargs["column_index"], 2)
        for call in report.call_args_list:
            self.assertEqual(call.kwargs["dataset_info"]["mode"], "spectrum_direct")
            self.assertEqual(call.kwargs["dataset_info"]["selected_spectrum_columns"], [2])
            self.assertEqual(call.kwargs["run_settings"]["spectrum_column_index"], 2)
            self.assertIn("spectrum_direct_", call.kwargs["output_path"].name)

    def test_other_least_squares_options_are_not_exposed(self):
        import main
        for flag in ("--final-f-scale", "--method", "--x-scale", "--ftol", "--xtol", "--gtol", "--max-nfev"):
            with self.subTest(flag=flag), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main.build_parser().parse_args([flag, "1"])

    def test_unsupported_loss_is_rejected(self):
        import main
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main.build_parser().parse_args(["--loss", "unsupported"])

if __name__ == "__main__":
    unittest.main()
