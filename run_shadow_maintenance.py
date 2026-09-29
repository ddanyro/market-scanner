"""Cadenced maintenance for Enhanced and Technical Events shadow outcomes.

Snapshot collection stays in the scanner and therefore runs every time. This
runner only performs the expensive, derived forward analyses when their
independent cadence is due. Standalone cadence state is local, so an R2 pull
for dashboard updates cannot overwrite a newer successful research timestamp.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import math
import os
from pathlib import Path
import subprocess
import signal
import sys
import tempfile
import time


STATE_PATH = Path(
    os.environ.get("SHADOW_MAINTENANCE_STATE_FILE", ".shadow_research_cache/maintenance-state.json")
)
LOCK_PATH = Path(
    os.environ.get("SHADOW_MAINTENANCE_LOCK_FILE", ".shadow_maintenance.lock")
)
SCHEMA = "market-scanner.shadow-maintenance.v1"
HEARTBEAT_SECONDS = float(
    os.environ.get("SHADOW_MAINTENANCE_HEARTBEAT_SECONDS", "60")
)
TIMEOUT_SECONDS = float(os.environ.get('SHADOW_MAINTENANCE_TIMEOUT_SECONDS', '3600'))

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
    if not path.exists() and path == Path('.shadow_research_cache/maintenance-state.json'):
        path = Path('.shadow_maintenance_state.json')  # one-time legacy migration
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
        last = _parse_timestamp(payload['tasks'].get(name, {}).get('last_success_at'))
        generated_at = _report_timestamp(spec["report"])
        if generated_at and (last is None or generated_at > last):
            payload["tasks"][name] = {
                "last_success_at": generated_at.isoformat(),
                "source": "existing_integrity_report",
            }
    return payload


def save_state(payload, path=None):
    target = Path(path or STATE_PATH)
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
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


def _terminate_process_group(process):
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    finally:
        # A descendant may ignore TERM even if the direct child exits first.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def run_with_heartbeat(command, label, heartbeat_seconds=None, timeout_seconds=None):
    """Run a maintenance child while periodically proving it is still alive."""
    interval = (
        HEARTBEAT_SECONDS if heartbeat_seconds is None else heartbeat_seconds
    )
    interval = max(float(interval), 0.1)
    budget = TIMEOUT_SECONDS if timeout_seconds is None else float(timeout_seconds)
    if not math.isfinite(budget) or budget <= 0:
        raise ValueError('Limita de durată trebuie să fie pozitivă și finită.')
    started = time.monotonic()
    # Only this newly spawned session is ever terminated; never other runs.
    env = dict(os.environ)
    env.setdefault('SHADOW_RESEARCH_CACHE_DIR', '.shadow_research_cache')
    process = subprocess.Popen(command, start_new_session=True, env=env)
    while True:
        remaining = budget - (time.monotonic() - started)
        if remaining <= 0:
            print(f'[Shadow maintenance] {label}: limită de {budget:g}s atinsă; '
                  'progresul salvat va fi reutilizat la reluare.', flush=True)
            _terminate_process_group(process)
            return 124
        try:
            return process.wait(timeout=min(interval, remaining))
        except subprocess.TimeoutExpired:
            elapsed = int(time.monotonic() - started)
            minutes, seconds = divmod(elapsed, 60)
            print(
                f"[Shadow maintenance] {label}: încă rulează; "
                f"timp scurs {minutes}m {seconds:02d}s (PID {process.pid}).",
                flush=True,
            )
        except KeyboardInterrupt:
            _terminate_process_group(process)
            raise


def run_maintenance(*, selected=None, force=False, offline=False, now=None, timeout_seconds=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    selected = list(selected or TASKS)
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    failures = []
    with LOCK_PATH.open("a+", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('[Shadow maintenance] Există deja o rulare activă; ies fără a o modifica.', flush=True)
            return 0
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
            print(
                f"[Shadow maintenance] {spec['label']}: pornește.",
                flush=True,
            )
            command = [sys.executable, "-u", spec["command"]]
            if offline:
                command.append("--offline")
            if force and name == 'technical':
                command.append('--refresh-prices')
            options = {} if timeout_seconds is None else {'timeout_seconds': timeout_seconds}
            # Both evaluators write only to a private staging directory. A
            # timeout/error never replaces the previous completed reports.
            destination = spec['report'].parent / 'offline' if offline else spec['report'].parent
            destination.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='.research-stage-', dir=destination) as directory:
                stage = Path(directory)
                returncode = run_with_heartbeat(
                    [*command, '--output', str(stage)], spec['label'], **options,
                )
                if returncode == 0:
                    # The completion marker is installed after all other files.
                    for artifact in sorted(stage.iterdir(), key=lambda item: item.name == 'integrity_report.json'):
                        if artifact.is_file():
                            os.replace(artifact, destination / artifact.name)
                    if name == 'technical' and (destination / 'event_observations.csv.gz').exists():
                        (destination / 'event_observations.csv').unlink(missing_ok=True)
            if returncode:
                failures.append(name)
                state["tasks"].setdefault(name, {})["last_failure_at"] = (
                    now.isoformat()
                )
                state["tasks"][name]["last_returncode"] = returncode
                save_state(state)
                print(
                    f"[Shadow maintenance] {spec['label']}: EȘEC "
                    f"(cod {returncode}); va fi reîncercată."
                )
                continue
            if offline:
                print(f"[Shadow maintenance] {spec['label']}: diagnostic offline; cadența online nu este avansată.")
                continue
            state["tasks"][name] = {
                "last_success_at": now.isoformat(),
                "last_returncode": 0,
                "source": "maintenance_runner",
            }
            save_state(state)
            print(f"[Shadow maintenance] {spec['label']}: finalizată.")
            completion_file = os.environ.get("SHADOW_RESEARCH_COMPLETION_FILE")
            if completion_file:
                Path(completion_file).write_text("ready\n", encoding="utf-8")
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument('--timeout-seconds', type=float, default=TIMEOUT_SECONDS,
                        help='Limită per evaluare (implicit 3600s / 60 minute); checkpointurile se păstrează.')
    parser.add_argument(
        "--only", choices=tuple(TASKS), action="append",
        help="Rulează/verifică doar jobul selectat (poate fi repetat).",
    )
    args = parser.parse_args()
    def interrupted(signum, frame):
        raise KeyboardInterrupt()
    previous = {sig: signal.signal(sig, interrupted) for sig in (signal.SIGTERM, signal.SIGHUP)}
    try:
        code = run_maintenance(
            selected=args.only, force=args.force, offline=args.offline,
            timeout_seconds=args.timeout_seconds,
        )
    except KeyboardInterrupt:
        print('[Shadow maintenance] Întreruptă; checkpointurile finalizate sunt păstrate.', flush=True)
        code = 130
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
