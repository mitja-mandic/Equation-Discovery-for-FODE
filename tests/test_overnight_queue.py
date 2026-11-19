"""Check unattended queue validation, snapshots, execution, and state."""

import csv
import json
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from experiments import overnight_queue as queue
from experiments import run_experiments


class OvernightQueueTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "data" / "simulation" / "generated").mkdir(parents=True)
        (self.root / "data" / "circuits").mkdir(parents=True)
        (self.root / "data" / "simulation" / "generated" / "sample.npz").touch()
        (self.root / "data" / "circuits" / "models.json").touch()
        self.plan = self.root / "plan.csv"
        with self.plan.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=run_experiments.PLAN_FIELDS)
            writer.writeheader()
            writer.writerow({
                "dataset_id": "simulated_sample",
                "format": "simulated",
                "path": "data/simulation/generated/sample.npz",
                "channel": "",
                "enabled": "1",
                "notes": "test",
            })
        self.settings = self.root / "settings.json"
        settings = {
            "circuit_path": "data/circuits/models.json",
            "grammar": "no_G_relaxed",
            "elements": 5,
            "residual_scale": "relative",
            "scatter_floor": 0.0,
            "f_scale": 0.001,
            "loss": "soft_l1",
            "spectrum_column_index": None,
            "number_starts": 6,
            "random_seed": 42,
            "reoptimization_error_margin": 0.2,
            "sort_first_round": "optimizer_value",
            "sort_second_round": "combinatorial_score",
        }
        self.settings.write_text(json.dumps(settings), encoding="utf-8")
        self.raw_job = {
            "enabled": True,
            "campaign_id": "overnight_test",
            "plan_path": str(self.plan),
            "settings_path": str(self.settings),
            "settings_overrides": {"number_starts": 24},
            "timeout_hours": None,
            "notes": "long test",
        }

    def patched_environment(self) -> ExitStack:
        stack = ExitStack()
        stack.enter_context(patch.object(queue, "PROJECT_DIR", self.root))
        stack.enter_context(patch.object(queue, "QUEUE_ROOT", self.root / "queues"))
        stack.enter_context(patch.object(queue, "CAMPAIGNS_DIR", self.root / "campaigns"))
        stack.enter_context(patch.object(queue, "QUEUE_NAME", "test_queue"))
        stack.enter_context(patch.object(queue, "HEARTBEAT_SECONDS", 1))
        stack.enter_context(patch.object(run_experiments, "PROJECT_DIR", self.root))
        return stack

    def test_dry_run_validates_overrides_without_writing(self):
        with self.patched_environment(), redirect_stdout(StringIO()) as output:
            jobs = queue.configured_jobs([self.raw_job])
            queue.dry_run(jobs)
        self.assertIn("number_starts: 24", output.getvalue())
        self.assertFalse((self.root / "queues").exists())
        self.assertFalse((self.root / "campaigns").exists())

    def test_queue_snapshots_inputs_runs_job_and_records_state(self):
        def command(job, snapshot):
            campaign_dir = self.root / "campaigns" / job.campaign_id
            script = (
                "from pathlib import Path; "
                f"Path({str(campaign_dir)!r}).mkdir(parents=True)"
            )
            return [sys.executable, "-c", script]

        with self.patched_environment(), patch.object(queue, "build_job_command", command):
            jobs = queue.configured_jobs([self.raw_job])
            self.assertEqual(queue.run_queue(jobs), 0)

        queue_dir = self.root / "queues" / "test_queue"
        state = json.loads((queue_dir / "state.json").read_text(encoding="utf-8"))
        record = state["jobs"]["overnight_test"]
        self.assertEqual(record["status"], "completed")
        self.assertEqual(record["return_code"], 0)
        snapshot_settings = json.loads(
            (queue_dir / "inputs" / "overnight_test" / "settings.json").read_text()
        )
        self.assertEqual(snapshot_settings["number_starts"], 24)
        self.assertTrue((queue_dir / "logs" / "overnight_test.log").is_file())
        self.assertIn("status=completed", (queue_dir / "queue.log").read_text())

    def test_invalid_or_duplicate_jobs_are_rejected(self):
        duplicate = dict(self.raw_job)
        with self.patched_environment():
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                queue.configured_jobs([self.raw_job, duplicate])
            invalid = dict(self.raw_job, timeout_hours=0)
            with self.assertRaisesRegex(ValueError, "timeout_hours"):
                queue.configured_jobs([invalid])

    def test_dry_run_rejects_invalid_effective_cli_settings(self):
        invalid = dict(self.raw_job)
        invalid["settings_overrides"] = {"number_starts": 0}
        with self.patched_environment(), redirect_stderr(StringIO()):
            jobs = queue.configured_jobs([invalid])
            with self.assertRaisesRegex(ValueError, "invalid fitting settings"):
                queue.dry_run(jobs)


if __name__ == "__main__":
    unittest.main()
