"""Check plan selection and reproducible campaign output layout."""

import csv
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from experiments import run_experiments as campaign


class ExperimentCampaignTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "data" / "spectrum").mkdir(parents=True)
        (self.root / "data" / "battery" / "EIS_mitja").mkdir(parents=True)
        (self.root / "data" / "circuits").mkdir(parents=True)
        (self.root / "data" / "spectrum" / "sample.npz").touch()
        (self.root / "data" / "battery" / "EIS_mitja" / "sample.pcl").touch()
        (self.root / "data" / "circuits" / "models.json").touch()
        self.project_patch = patch.object(campaign, "PROJECT_DIR", self.root)
        self.project_patch.start()
        self.addCleanup(self.project_patch.stop)
        self.plan_path = self.root / "plan.csv"
        self.settings_path = self.root / "settings.json"
        settings = {key: 1 for key in campaign.SETTINGS_FLAGS}
        settings.update(circuit_path="data/circuits/models.json", loss="linear")
        self.settings_path.write_text(json.dumps(settings), encoding="utf-8")

    def test_prepare_selects_only_enabled_rows_and_preserves_plan(self):
        campaign.prepare_plan(self.plan_path)
        with self.plan_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([row["format"] for row in rows], ["pcl", "spectrum"])
        self.assertEqual([row["enabled"] for row in rows], ["0", "0"])
        rows[0]["enabled"] = "1"
        rows[0]["channel"] = "batt_2"
        with self.plan_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=campaign.PLAN_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        self.assertEqual(campaign.selected_datasets(self.plan_path), [rows[0]])
        with self.assertRaises(FileExistsError):
            campaign.prepare_plan(self.plan_path)

    def test_run_uses_separate_folder_and_refuses_reused_campaign_id(self):
        campaign.prepare_plan(self.plan_path)
        with self.plan_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            row["enabled"] = "1"
        with self.plan_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=campaign.PLAN_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        with patch.object(campaign, "CAMPAIGNS_DIR", self.root / "campaigns"), \
             patch.object(campaign.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run:
            output = campaign.run_campaign("baseline", self.plan_path, self.settings_path)
            self.assertEqual(run.call_count, 2)
            with self.assertRaises(FileExistsError):
                campaign.run_campaign("baseline", self.plan_path, self.settings_path)
        self.assertEqual((output / "plan.csv").read_bytes(), self.plan_path.read_bytes())
        self.assertTrue((output / "settings.json").is_file())
        self.assertEqual(json.loads((output / "settings.json").read_text())["loss"], "linear")
        for row in rows:
            run_dir = output / "runs" / row["dataset_id"]
            record = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(record["exit_code"], 0)
            self.assertIn(str(run_dir), record["command"])
            self.assertIn("--loss", record["command"])
            self.assertEqual(record["command"][record["command"].index("--loss") + 1], "linear")
            self.assertEqual((run_dir / "fit.log").read_text(encoding="utf-8"), "")

    def test_old_settings_default_to_soft_l1(self):
        settings = json.loads(self.settings_path.read_text(encoding="utf-8"))
        del settings["loss"]
        del settings["spectrum_column_index"]
        self.settings_path.write_text(json.dumps(settings), encoding="utf-8")
        self.assertEqual(campaign.load_settings(self.settings_path)["loss"], "soft_l1")
        self.assertIsNone(campaign.load_settings(self.settings_path)["spectrum_column_index"])

    def test_direct_spectrum_plan_passes_column_selection(self):
        campaign.prepare_plan(self.plan_path)
        with self.plan_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        row = rows[1]
        row["enabled"] = "1"
        row["format"] = "spectrum_direct"
        with self.plan_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=campaign.PLAN_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        self.assertEqual(campaign.selected_datasets(self.plan_path), [row])
        settings = campaign.load_settings(self.settings_path)
        settings["spectrum_column_index"] = 2
        command = campaign.build_command(row, settings, self.root / "results")
        self.assertEqual(command[command.index("--data-mode") + 1], "spectrum_direct")
        self.assertEqual(command[command.index("--spectrum-column-index") + 1], "2")
        settings["spectrum_column_index"] = None
        self.assertNotIn("--spectrum-column-index", campaign.build_command(row, settings, self.root / "results"))

    def test_simulated_dataset_is_discovered_and_uses_simulated_mode(self):
        simulated_dir = self.root / "data" / "simulation" / "generated"
        simulated_dir.mkdir(parents=True)
        (simulated_dir / "simulated_spectrum_006.npz").touch()
        campaign.prepare_plan(self.plan_path)
        with self.plan_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        simulated_row = next(row for row in rows if row["format"] == "simulated")
        simulated_row["enabled"] = "1"
        with self.plan_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=campaign.PLAN_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        self.assertEqual(campaign.selected_datasets(self.plan_path), [simulated_row])
        command = campaign.build_command(
            simulated_row, campaign.load_settings(self.settings_path), self.root / "results"
        )
        self.assertEqual(command[command.index("--data-mode") + 1], "simulated")


if __name__ == "__main__":
    unittest.main()
