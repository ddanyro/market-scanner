"""Cadenced maintenance for Enhanced and Technical Events shadow outcomes.

Snapshot collection stays in the scanner and therefore runs every time. This
runner only performs the expensive, derived forward analyses when their
independent cadence is due. The small state file is persisted through R2.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


STATE_PATH = Path(
    os.environ.get("SHADOW_MAINTENANCE_STATE_FILE", ".shadow_maintenance_state.json")
)
LOCK_PATH = Path(
    os.environ.get("SHADOW_MAINTENANCE_LOCK_FILE", ".shadow_maintenance.lock")
)
SCHEMA = "market-scanner.shadow-maintenance.v1"

TASKS = {
    "enhanced": {
        "interval_hours": float(
            os.environ.get("SHADOW_FORWARD_INTERVAL_HOURS", "24")
        ),
        "command": "evaluate_shadow_forward.py",
        "report": Path("analysis/shadow_forward_validation/integrity_report.json"),
        "label": "Evaluare forward Enhanced",
    },
    "technical": {
        "interval_hours": float(
            os.environ.get("TECHNICAL_EVENTS_VALIDATION_INTERVAL_HOURS", "168")
        ),
        "command": "evaluate_technical_events_forward.py",
        "report": Path("analysis/technical_events_validation/integrity_report.json"),
        "label": "Validare forward Technical Events",
    },
}


def _parse_timestamp(value):
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _report_timestamp(path):
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        return None
    return _parse_timestamp(payload.get("generated_at"))


def load_state(path=None):
    path = Path(path or STATE_PATH)
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        payload = {}
    if payload.get("schema") != SCHEMA:
        payload = {"schema": SCHEMA, "tasks": {}}
    payload.setdefault("tasks", {})
    # Seamless first-run migration: existing reports are evidence of the last
    # successful run, so deployment does not immediately repeat both jobs.
    for name, spec in TASKS.items():
        if payload["tasks"].get(name, {}).get("last_success_at"):
            continue
        generated_at = _report_timestamp(spec["report"])
        if generated_at:
            payload["tasks"][name] = {
                "last_success_at": generated_at.isoformat(),
                "source": "existing_integrity_report",
            }
    return payload


def save_state(payload, path=None):
    target = Path(path or STATE_PATH)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{target.name}.", dir=target.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def task_due(state, name, now, force=False):
    if force:
        return True
    last = _parse_timestamp(
        state.get("tasks", {}).get(name, {}).get("last_success_at")
    )
    if last is None:
        return True
    elapsed = (now - last).total_seconds() / 3600
    return elapsed >= TASKS[name]["interval_hours"]


def run_maintenance(*, selected=None, force=False, offline=False, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    selected = list(selected or TASKS)
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    failures = []
    with LOCK_PATH.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        state = load_state()
        # Persist bootstrapped timestamps even when every task is skipped.
        save_state(state)
        for name in selected:
            spec = TASKS[name]
            if not task_due(state, name, now, force=force):
                last = state["tasks"][name]["last_success_at"]
                print(
                    f"[Shadow maintenance] {spec['label']}: omisă; "
                    f"ultima rulare reușită {last}."
                )
                continue
            print(f"[Shadow maintenance] {spec['label']}: pornește.")
            command = [sys.executable, "-u", spec["command"]]
            if offline:
                command.append("--offline")
            completed = subprocess.run(command, check=False)
            if completed.returncode:
                failures.append(name)
                state["tasks"].setdefault(name, {})["last_failure_at"] = (
                    now.isoformat()
                )
                state["tasks"][name]["last_returncode"] = completed.returncode
                save_state(state)
                print(
                    f"[Shadow maintenance] {spec['label']}: EȘEC "
                    f"(cod {completed.returncode}); va fi reîncercată."
                )
                continue
            state["tasks"][name] = {
                "last_success_at": now.isoformat(),
                "last_returncode": 0,
                "source": "maintenance_runner",
            }
            save_state(state)
            print(f"[Shadow maintenance] {spec['label']}: finalizată.")
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument(
        "--only", choices=tuple(TASKS), action="append",
        help="Rulează/verifică doar jobul selectat (poate fi repetat).",
    )
    args = parser.parse_args()
    raise SystemExit(run_maintenance(
        selected=args.only, force=args.force, offline=args.offline
    ))


if __name__ == "__main__":
    main()
