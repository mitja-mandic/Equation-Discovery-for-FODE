"""Prepare and run comparable PCL and spectrum fitting campaigns."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from fitting_parameters.train_refactored import (
    COMBINATORIAL_ARRANGEMENT_WEIGHT,
    COMBINATORIAL_ELEMENT_WEIGHT,
)


PROJECT_DIR = Path(__file__).resolve().parents[1]
PLAN_PATH = PROJECT_DIR / "experiments" / "local_plan.csv"
SETTINGS_PATH = PROJECT_DIR / "experiments" / "settings.json"
CAMPAIGNS_DIR = PROJECT_DIR / "Results" / "campaigns"
PLAN_FIELDS = ("dataset_id", "format", "path", "channel", "enabled", "notes")
SETTINGS_FLAGS = {
    "circuit_path": "--circuit-path",
    "grammar": "--grammar",
    "elements": "--elements",
    "residual_scale": "--residual-scale",
    "scatter_floor": "--scatter-floor",
    "f_scale": "--f-scale",
    "loss": "--loss",
    "spectrum_column_index": "--spectrum-column-index",
    "number_starts": "--number-starts",
    "random_seed": "--random-seed",
    "reoptimization_error_margin": "--reoptimization-error-margin",
    "combinatorial_element_weight": "--combinatorial-element-weight",
    "combinatorial_arrangement_weight": "--combinatorial-arrangement-weight",
    "sort_first_round": "--sort-first-round",
    "sort_second_round": "--sort-second-round",
}


def discover_datasets() -> list[dict[str, str]]:
    """List local measurements without opening large NPZ files or pickles."""
    rows = []
    for data_format, directory, pattern in (
        ("pcl", PROJECT_DIR / "data" / "battery" / "EIS_mitja", "*.pcl"),
        ("spectrum", PROJECT_DIR / "data" / "spectrum", "*.npz"),
        ("simulated", PROJECT_DIR / "data" / "simulation" / "generated", "*.npz"),
    ):
        for path in sorted(directory.glob(pattern)):
            channel = "batt_1" if data_format == "pcl" else ""
            rows.append({
                "dataset_id": f"{data_format}_{path.stem}" + (f"_{channel}" if channel else ""),
                "format": data_format,
                "path": str(path.relative_to(PROJECT_DIR)),
                "channel": channel,
                "enabled": "0",
                "notes": "",
            })
    return rows


def prepare_plan(path: Path = PLAN_PATH) -> Path:
    """Create an editable local plan, leaving an existing plan untouched."""
    rows = discover_datasets()
    if not rows:
        raise ValueError("No PCL or spectrum files were found under data/.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PLAN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def selected_datasets(path: Path) -> list[dict[str, str]]:
    """Validate the plan and return only rows explicitly enabled for fitting."""
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(PLAN_FIELDS):
            raise ValueError(f"Plan columns must be: {', '.join(PLAN_FIELDS)}")
        rows = list(reader)
    selected = []
    seen = set()
    for row in rows:
        if row["enabled"] not in {"0", "1"}:
            raise ValueError(f"Invalid enabled value for {row['dataset_id']!r}; use 0 or 1.")
        if row["enabled"] == "0":
            continue
        dataset_id = row["dataset_id"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", dataset_id):
            raise ValueError(f"Invalid dataset_id: {dataset_id!r}")
        if dataset_id in seen:
            raise ValueError(f"Duplicate enabled dataset_id: {dataset_id}")
        seen.add(dataset_id)
        if row["format"] not in {"pcl", "spectrum", "spectrum_direct", "simulated"}:
            raise ValueError(f"Unsupported format for {dataset_id}: {row['format']!r}")
        expected_suffix = ".pcl" if row["format"] == "pcl" else ".npz"
        source = (PROJECT_DIR / row["path"]).resolve()
        if not source.is_file() or source.suffix.lower() != expected_suffix:
            raise ValueError(f"Missing or invalid {row['format']} file: {source}")
        if row["format"] == "pcl" and not row["channel"]:
            raise ValueError(f"PCL dataset {dataset_id} needs a channel.")
        selected.append(row)
    if not selected:
        raise ValueError("No datasets enabled. Set enabled to 1 for the rows to fit.")
    return selected


def load_settings(path: Path) -> dict[str, object]:
    """Load only settings that the main fitting CLI can reproduce."""
    settings = json.loads(path.read_text(encoding="utf-8"))
    optional = {
        "loss", "spectrum_column_index", "combinatorial_element_weight",
        "combinatorial_arrangement_weight",
    }
    required = set(SETTINGS_FLAGS) - optional
    if not isinstance(settings, dict) or not required <= set(settings) <= set(SETTINGS_FLAGS):
        raise ValueError(
            f"Settings must contain: {', '.join(sorted(required))}; "
            "loss, spectrum_column_index, and combinatorial weights are optional "
            "for older campaigns"
        )
    settings.setdefault("loss", "soft_l1")
    settings.setdefault("spectrum_column_index", None)
    settings.setdefault("combinatorial_element_weight", COMBINATORIAL_ELEMENT_WEIGHT)
    settings.setdefault(
        "combinatorial_arrangement_weight", COMBINATORIAL_ARRANGEMENT_WEIGHT,
    )
    circuit_path = (PROJECT_DIR / str(settings["circuit_path"])).resolve()
    if not circuit_path.is_file():
        raise ValueError(f"Circuit collection not found: {circuit_path}")
    return settings


def build_command(row: dict[str, str], settings: dict[str, object], output_root: Path) -> list[str]:
    """Build a complete main.py invocation from one row and shared settings."""
    command = [
        sys.executable, str(PROJECT_DIR / "main.py"),
        "--data-mode", row["format"],
        "--data-path", str((PROJECT_DIR / row["path"]).resolve()),
        "--output-root", str(output_root),
        "--save-results", "--no-show-plots", "--no-show-residual-plots",
        "--filename-prefix", "", "--filename-suffix", "first_round",
        "--final-filename-suffix", "refined",
    ]
    if row["format"] == "pcl":
        command.extend(("--channel", row["channel"]))
    for key, flag in SETTINGS_FLAGS.items():
        value = settings[key]
        if value is None or (key == "spectrum_column_index" and row["format"] != "spectrum_direct"):
            continue
        if key == "circuit_path":
            value = (PROJECT_DIR / str(value)).resolve()
        command.extend((flag, str(value)))
    return command


def run_campaign(campaign_id: str, plan_path: Path = PLAN_PATH, settings_path: Path = SETTINGS_PATH) -> Path:
    """Run enabled rows into a new campaign directory and record each outcome."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", campaign_id):
        raise ValueError("Campaign ID may contain letters, digits, dots, underscores, and dashes.")
    rows = selected_datasets(plan_path)
    settings = load_settings(settings_path)
    campaign_dir = CAMPAIGNS_DIR / campaign_id
    campaign_dir.mkdir(parents=True, exist_ok=False)
    (campaign_dir / "plan.csv").write_bytes(plan_path.read_bytes())
    (campaign_dir / "settings.json").write_text(
        json.dumps(settings, indent=2) + "\n", encoding="utf-8"
    )
    failed = []
    for row in rows:
        run_dir = campaign_dir / "runs" / row["dataset_id"]
        run_dir.mkdir(parents=True)
        command = build_command(row, settings, run_dir)
        started_at = datetime.now(timezone.utc).isoformat()
        with (run_dir / "fit.log").open("w", encoding="utf-8") as log:
            result = subprocess.run(command, cwd=PROJECT_DIR, stdout=log, stderr=subprocess.STDOUT, check=False)
        record = {
            "dataset_id": row["dataset_id"],
            "format": row["format"],
            "path": row["path"],
            "channel": row["channel"] or None,
            "command": command,
            "started_at_utc": started_at,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "exit_code": result.returncode,
        }
        (run_dir / "run.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(f"{row['dataset_id']}: {'OK' if result.returncode == 0 else f'FAILED ({result.returncode})'}")
        if result.returncode:
            failed.append(row["dataset_id"])
    if failed:
        raise RuntimeError(f"Campaign finished with failed runs: {', '.join(failed)}. See fit.log in each run folder.")
    return campaign_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("prepare", help="Create an editable local_plan.csv from local measurements")
    run_parser = actions.add_parser("run", help="Fit enabled datasets into a new campaign folder")
    run_parser.add_argument("campaign_id", help="Unique name for this set of comparable fits")
    run_parser.add_argument(
        "--plan", type=Path, default=PLAN_PATH,
        help="CSV dataset plan to snapshot and execute",
    )
    run_parser.add_argument(
        "--settings", type=Path, default=SETTINGS_PATH,
        help="JSON fitting settings to snapshot and execute",
    )
    args = parser.parse_args(argv)
    try:
        if args.action == "prepare":
            print(f"Prepared {prepare_plan()}")
        else:
            print(
                f"Saved campaign to "
                f"{run_campaign(args.campaign_id, args.plan, args.settings)}"
            )
    except (FileExistsError, FileNotFoundError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
