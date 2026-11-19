"""Run an editable queue of experiment campaigns without interactive help.

Edit only the CONFIGURATION section, validate it with ``--dry-run``, then start
it with ``--run``. Campaigns run sequentially. Each enabled job gets immutable
plan/settings snapshots, a separate log, and persistent state under
``Results/overnight_queues/<QUEUE_NAME>``.

The queue never retries a failed, timed-out, interrupted, or blocked job. Give a
corrected retry a new campaign ID (and normally a new queue name).
"""

from __future__ import annotations

import argparse
import fcntl
import json
import math
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from experiments import run_experiments  # noqa: E402


# =============================================================================
# CONFIGURATION — edit this section to define an overnight queue.
# =============================================================================

QUEUE_NAME = "simulated_no_G_relaxed_7"

# Continue to later jobs if one job fails. Failed jobs are recorded, not retried.
CONTINUE_AFTER_FAILURE = True

# How often state.json records that the current child process is still alive.
HEARTBEAT_SECONDS = 60

# Duplicate the example mapping for every campaign you want to run. Campaign IDs
# must be unique and must not already exist under Results/campaigns.
#
# settings_overrides are merged over settings_path. This is the easiest place to
# request longer runs, for example: {"number_starts": 24}.
# timeout_hours=None means no queue-imposed timeout.
JOBS: list[dict[str, object]] = [
    {
        "enabled": True,
        "campaign_id": (
            "simulated_008_sofc_009_battery_no_G_relaxed_7_relative_soft_l1_"
            "fscale_0p001_optimizer_value_combinatorial_score_6starts_20261119"
        ),
        "plan_path": "experiments/simulated_sofc_battery_008_009_plan.csv",
        "settings_path": "experiments/simulated_no_G_relaxed_7_settings.json",
        "settings_overrides": {},
        "timeout_hours": None,
        "notes": "Seven-element no-G relaxed grammar on simulated SOFC 008 and battery 009.",
    },
]


# =============================================================================
# RUNNER — normal users should not need to edit below this line.
# =============================================================================

QUEUE_ROOT = PROJECT_DIR / "Results" / "overnight_queues"
CAMPAIGNS_DIR = PROJECT_DIR / "Results" / "campaigns"
TERMINAL_STATUSES = {"completed", "failed", "timed_out", "interrupted", "blocked"}


@dataclass(frozen=True)
class Job:
    """One validated queue entry."""

    campaign_id: str
    plan_path: Path
    settings_path: Path
    settings_overrides: dict[str, object]
    timeout_hours: float | None
    notes: str


@dataclass(frozen=True)
class JobSnapshot:
    """Immutable queue-local inputs used to launch one campaign."""

    plan_path: Path
    settings_path: Path
    datasets: tuple[str, ...]


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def project_path(value: object) -> Path:
    """Resolve a configured path relative to the repository root."""
    path = Path(str(value))
    return (PROJECT_DIR / path).resolve() if not path.is_absolute() else path.resolve()


def configured_jobs(raw_jobs: Sequence[Mapping[str, object]] | None = None) -> list[Job]:
    """Parse and validate enabled mappings from the configuration section."""
    raw_jobs = JOBS if raw_jobs is None else raw_jobs
    jobs: list[Job] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_jobs, start=1):
        enabled = raw.get("enabled", False)
        if not isinstance(enabled, bool):
            raise ValueError(f"Job {index} enabled must be true or false")
        if not enabled:
            continue
        campaign_id = str(raw.get("campaign_id", ""))
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", campaign_id):
            raise ValueError(f"Job {index} has invalid campaign_id {campaign_id!r}")
        if campaign_id in seen:
            raise ValueError(f"Duplicate enabled campaign_id: {campaign_id}")
        seen.add(campaign_id)
        overrides = raw.get("settings_overrides", {})
        if not isinstance(overrides, dict):
            raise ValueError(f"Job {campaign_id} settings_overrides must be a mapping")
        unknown = set(overrides).difference(run_experiments.SETTINGS_FLAGS)
        if unknown:
            raise ValueError(
                f"Job {campaign_id} has unknown settings overrides: "
                + ", ".join(sorted(unknown))
            )
        timeout = raw.get("timeout_hours")
        if timeout is not None:
            timeout = float(timeout)
            if not math.isfinite(timeout) or timeout <= 0:
                raise ValueError(f"Job {campaign_id} timeout_hours must be positive or null")
        jobs.append(Job(
            campaign_id=campaign_id,
            plan_path=project_path(raw.get("plan_path", "")),
            settings_path=project_path(raw.get("settings_path", "")),
            settings_overrides=dict(overrides),
            timeout_hours=timeout,
            notes=str(raw.get("notes", "")),
        ))
    if not jobs:
        raise ValueError("No overnight jobs are enabled in JOBS")
    return jobs


def effective_settings(job: Job) -> dict[str, object]:
    """Return validated base settings with this job's explicit overrides."""
    settings = run_experiments.load_settings(job.settings_path)
    settings.update(job.settings_overrides)
    circuit_path = project_path(settings["circuit_path"])
    if not circuit_path.is_file():
        raise ValueError(
            f"Job {job.campaign_id} circuit collection not found: {circuit_path}"
        )
    return settings


def validate_job(job: Job) -> tuple[tuple[str, ...], dict[str, object]]:
    """Validate all job inputs without creating queue or campaign outputs."""
    rows = run_experiments.selected_datasets(job.plan_path)
    settings = effective_settings(job)
    from main import build_parser

    parser = build_parser()
    for row in rows:
        command = run_experiments.build_command(
            row, settings, PROJECT_DIR / "Results" / "dry_run"
        )
        try:
            parser.parse_args(command[2:])
        except SystemExit as error:
            raise ValueError(
                f"Job {job.campaign_id} contains invalid fitting settings"
            ) from error
    return tuple(row["dataset_id"] for row in rows), settings


def validate_queue_name() -> None:
    """Reject queue names that cannot safely name an output directory."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", QUEUE_NAME):
        raise ValueError(
            "QUEUE_NAME may contain letters, digits, dots, underscores, and dashes"
        )
    if not isinstance(HEARTBEAT_SECONDS, int) or HEARTBEAT_SECONDS <= 0:
        raise ValueError("HEARTBEAT_SECONDS must be a positive integer")
    if not isinstance(CONTINUE_AFTER_FAILURE, bool):
        raise ValueError("CONTINUE_AFTER_FAILURE must be true or false")


def queue_directory() -> Path:
    """Return the configured queue's persistent output directory."""
    validate_queue_name()
    return QUEUE_ROOT / QUEUE_NAME


def append_queue_log(queue_dir: Path, message: str) -> None:
    """Write a timestamped message to both the console and queue log."""
    line = f"[{utc_now()}] {message}"
    print(line, flush=True)
    queue_dir.mkdir(parents=True, exist_ok=True)
    with (queue_dir / "queue.log").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def load_state(queue_dir: Path) -> dict[str, Any]:
    """Load queue state, or return a new state document."""
    path = queue_dir / "state.json"
    if not path.exists():
        return {"queue_name": QUEUE_NAME, "created_at_utc": utc_now(), "jobs": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("queue_name") != QUEUE_NAME or not isinstance(state.get("jobs"), dict):
        raise ValueError(f"Invalid queue state: {path}")
    return state


def write_state(queue_dir: Path, state: Mapping[str, Any]) -> None:
    """Atomically persist queue state."""
    document = dict(state)
    document["updated_at_utc"] = utc_now()
    queue_dir.mkdir(parents=True, exist_ok=True)
    path = queue_dir / "state.json"
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@contextmanager
def exclusive_queue_lock(queue_dir: Path):
    """Prevent two scheduler processes from operating the same queue."""
    queue_dir.mkdir(parents=True, exist_ok=True)
    with (queue_dir / "queue.lock").open("w", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError(f"Queue {QUEUE_NAME!r} is already running") from error
        handle.write(f"pid={os.getpid()} started_at_utc={utc_now()}\n")
        handle.flush()
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def update_job_state(
    queue_dir: Path, state: dict[str, Any], campaign_id: str, **updates: object,
) -> None:
    """Merge fields into one job record and persist the queue state."""
    record = state["jobs"].setdefault(campaign_id, {})
    record.update(updates)
    write_state(queue_dir, state)


def prepare_snapshot(job: Job, queue_dir: Path) -> JobSnapshot:
    """Create or verify immutable queue-local plan and settings snapshots."""
    datasets, settings = validate_job(job)
    snapshot_dir = queue_dir / "inputs" / job.campaign_id
    plan_path = snapshot_dir / "plan.csv"
    settings_path = snapshot_dir / "settings.json"
    plan_bytes = job.plan_path.read_bytes()
    settings_text = json.dumps(settings, indent=2) + "\n"
    if snapshot_dir.exists():
        if (
            not plan_path.is_file()
            or not settings_path.is_file()
            or plan_path.read_bytes() != plan_bytes
            or settings_path.read_text(encoding="utf-8") != settings_text
        ):
            raise ValueError(
                f"Configured inputs changed for snapshotted job {job.campaign_id}; "
                "use a new campaign ID or QUEUE_NAME"
            )
    else:
        snapshot_dir.mkdir(parents=True)
        plan_path.write_bytes(plan_bytes)
        settings_path.write_text(settings_text, encoding="utf-8")
    return JobSnapshot(plan_path, settings_path, datasets)


def build_job_command(job: Job, snapshot: JobSnapshot) -> list[str]:
    """Build the exact standalone command for one queued campaign."""
    return [
        sys.executable,
        "-u",
        str(PROJECT_DIR / "experiments" / "run_experiments.py"),
        "run",
        job.campaign_id,
        "--plan",
        str(snapshot.plan_path),
        "--settings",
        str(snapshot.settings_path),
    ]


def terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    """Terminate a queued job and its child fit process after timeout/interrupt."""
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def process_is_alive(pid: object) -> bool:
    """Return whether a previously recorded local process still exists."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def execute_job(
    job: Job,
    snapshot: JobSnapshot,
    queue_dir: Path,
    state: dict[str, Any],
) -> tuple[str, int]:
    """Execute one campaign subprocess while recording periodic heartbeats."""
    log_path = queue_dir / "logs" / f"{job.campaign_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    command = build_job_command(job, snapshot)
    started_at = utc_now()
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"\n[{started_at}] START {shlex.join(command)}\n")
        log.flush()
        process = subprocess.Popen(
            command,
            cwd=PROJECT_DIR,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        update_job_state(
            queue_dir,
            state,
            job.campaign_id,
            status="running",
            command=command,
            pid=process.pid,
            started_at_utc=started_at,
            heartbeat_at_utc=started_at,
            log_path=str(log_path),
            datasets=list(snapshot.datasets),
            timeout_hours=job.timeout_hours,
            notes=job.notes,
        )
        started_monotonic = time.monotonic()
        timeout_seconds = None if job.timeout_hours is None else job.timeout_hours * 3600
        while True:
            try:
                return_code = process.wait(timeout=HEARTBEAT_SECONDS)
                break
            except subprocess.TimeoutExpired:
                elapsed = time.monotonic() - started_monotonic
                update_job_state(
                    queue_dir,
                    state,
                    job.campaign_id,
                    heartbeat_at_utc=utc_now(),
                    elapsed_seconds=round(elapsed, 3),
                )
                if timeout_seconds is not None and elapsed >= timeout_seconds:
                    log.write(f"[{utc_now()}] TIMEOUT after {elapsed:.1f} seconds\n")
                    log.flush()
                    terminate_process_group(process)
                    return "timed_out", 124
            except KeyboardInterrupt:
                log.write(f"[{utc_now()}] INTERRUPTED by user\n")
                log.flush()
                terminate_process_group(process)
                raise
    return ("completed", 0) if return_code == 0 else ("failed", return_code)


def dry_run(jobs: Sequence[Job]) -> None:
    """Print the effective queue after validating every input."""
    validate_queue_name()
    print(f"Queue: {QUEUE_NAME}")
    for number, job in enumerate(jobs, start=1):
        campaign_dir = CAMPAIGNS_DIR / job.campaign_id
        if campaign_dir.exists():
            raise ValueError(
                f"Campaign ID already exists for job {job.campaign_id}: {campaign_dir}"
            )
        datasets, settings = validate_job(job)
        print(f"{number}. {job.campaign_id}")
        print(f"   datasets: {', '.join(datasets)}")
        print(f"   plan: {job.plan_path}")
        print(f"   base settings: {job.settings_path}")
        print(f"   overrides: {json.dumps(job.settings_overrides, sort_keys=True)}")
        print(f"   number_starts: {settings['number_starts']}")
        print(f"   timeout_hours: {job.timeout_hours}")
    print("Dry run passed; no files or campaigns were created.")


def run_queue(jobs: Sequence[Job]) -> int:
    """Snapshot and execute all pending jobs in sequence."""
    queue_dir = queue_directory()
    with exclusive_queue_lock(queue_dir):
        return run_queue_locked(jobs, queue_dir)


def run_queue_locked(jobs: Sequence[Job], queue_dir: Path) -> int:
    """Execute a queue after its exclusive process lock has been acquired."""
    state = load_state(queue_dir)
    for record in state["jobs"].values():
        if record.get("status") == "running":
            if process_is_alive(record.get("pid")):
                record.update(
                    status="blocked",
                    finished_at_utc=utc_now(),
                    message=(
                        "Queue restarted while the recorded job process was still alive; "
                        "the process was not killed or duplicated."
                    ),
                )
            else:
                record.update(
                    status="interrupted",
                    finished_at_utc=utc_now(),
                    message=(
                        "Queue restarted while this job was marked running; not retried."
                    ),
                )
    write_state(queue_dir, state)

    snapshots = {job.campaign_id: prepare_snapshot(job, queue_dir) for job in jobs}
    append_queue_log(queue_dir, f"Queue {QUEUE_NAME} started with {len(jobs)} enabled jobs")
    failed = False
    for job in jobs:
        record = state["jobs"].get(job.campaign_id, {})
        status = record.get("status")
        if status in TERMINAL_STATUSES:
            append_queue_log(queue_dir, f"Skipping {job.campaign_id}: status={status}")
            failed = failed or status != "completed"
            continue
        campaign_dir = CAMPAIGNS_DIR / job.campaign_id
        if campaign_dir.exists():
            update_job_state(
                queue_dir,
                state,
                job.campaign_id,
                status="blocked",
                finished_at_utc=utc_now(),
                message=f"Campaign directory already exists: {campaign_dir}",
            )
            append_queue_log(queue_dir, f"Blocked {job.campaign_id}: campaign already exists")
            failed = True
            if not CONTINUE_AFTER_FAILURE:
                break
            continue
        append_queue_log(queue_dir, f"Starting {job.campaign_id}")
        try:
            job_status, return_code = execute_job(
                job, snapshots[job.campaign_id], queue_dir, state,
            )
        except KeyboardInterrupt:
            update_job_state(
                queue_dir,
                state,
                job.campaign_id,
                status="interrupted",
                return_code=130,
                finished_at_utc=utc_now(),
            )
            append_queue_log(queue_dir, f"Interrupted {job.campaign_id}; queue stopped")
            return 130
        except OSError as error:
            job_status, return_code = "failed", 1
            update_job_state(
                queue_dir,
                state,
                job.campaign_id,
                message=f"Could not start process: {error}",
            )
        update_job_state(
            queue_dir,
            state,
            job.campaign_id,
            status=job_status,
            return_code=return_code,
            finished_at_utc=utc_now(),
        )
        append_queue_log(
            queue_dir,
            f"Finished {job.campaign_id}: status={job_status}, return_code={return_code}",
        )
        if job_status != "completed":
            failed = True
            if not CONTINUE_AFTER_FAILURE:
                break
    append_queue_log(queue_dir, f"Queue {QUEUE_NAME} finished")
    return 1 if failed else 0


def show_status() -> None:
    """Print the persisted status of the configured queue."""
    queue_dir = queue_directory()
    if not (queue_dir / "state.json").is_file():
        print(f"No state exists for queue {QUEUE_NAME!r}")
        return
    state = load_state(queue_dir)
    print(f"Queue: {QUEUE_NAME}")
    print(f"Updated: {state.get('updated_at_utc', 'unknown')}")
    for campaign_id, record in state["jobs"].items():
        print(
            f"- {campaign_id}: {record.get('status', 'unknown')}"
            f" (return_code={record.get('return_code')})"
        )


def main(argv: Sequence[str] | None = None) -> int:
    """Validate, execute, or inspect the configured overnight queue."""
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--dry-run", action="store_true", help="validate without writing")
    action.add_argument("--run", action="store_true", help="start or resume the queue")
    action.add_argument("--status", action="store_true", help="show saved queue state")
    args = parser.parse_args(argv)
    try:
        if args.status:
            show_status()
            return 0
        jobs = configured_jobs()
        if args.dry_run:
            dry_run(jobs)
            return 0
        return run_queue(jobs)
    except (FileExistsError, FileNotFoundError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
