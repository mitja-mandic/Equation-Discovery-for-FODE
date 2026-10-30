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
        with patch("circuit_export.load_circuits") as load, contextlib.redirect_stdout(io.StringIO()) as output:
            namespace = runpy.run_path(str(SCRIPT), run_name="imported_main")
        load.assert_not_called()
        self.assertEqual(output.getvalue(), "")
        self.assertTrue(callable(namespace["main"]))

    def test_script_starts_workflow(self):
        with patch("sys.argv", [str(SCRIPT)]), patch("circuit_export.load_circuits", side_effect=RuntimeError("entry reached")) as load:
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
                "--f-scale", "1.5", "--number-starts", "3", "--random-seed", "7",
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
        self.assertEqual(
            kwargs["final_least_squares_settings"]["max_nfev"],
            main.FINAL_LEAST_SQUARES_SETTINGS["max_nfev"],
        )
        self.assertFalse(plot.call_args.kwargs["show"])
        self.assertEqual(residual_plot.call_args.kwargs["f_scale"], 1.5)
        self.assertEqual(report.call_count, 2)
        initial_report, refined_report = report.call_args_list
        self.assertEqual(initial_report.kwargs["ranking_metric"], "lp_error")
        self.assertEqual(refined_report.kwargs["ranking_metric"], "mse")
        for call in (initial_report, refined_report):
            self.assertEqual(call.kwargs["optimizer"], "least_squares")
            self.assertEqual(call.kwargs["run_settings"]["residual_scale"], "scatter")
            self.assertEqual(call.kwargs["run_settings"]["scatter_floor"], 0.2)
            self.assertEqual(call.kwargs["run_settings"]["number_starts"], 3)
            self.assertEqual(call.kwargs["run_settings"]["random_seed"], 7)
            self.assertEqual(call.kwargs["run_settings"]["first_round_ranking_metric"], "lp_error")
            self.assertEqual(call.kwargs["run_settings"]["second_round_ranking_metric"], "mse")
            self.assertEqual(call.kwargs["run_settings"]["reoptimization_error_margin"], 0.3)
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

    def test_other_least_squares_options_are_not_exposed(self):
        import main
        for flag in ("--final-f-scale", "--loss", "--method", "--x-scale", "--ftol", "--xtol", "--gtol", "--max-nfev"):
            with self.subTest(flag=flag), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main.build_parser().parse_args([flag, "1"])

if __name__ == "__main__":
    unittest.main()
