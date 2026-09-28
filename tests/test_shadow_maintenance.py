import datetime as dt
import json
import subprocess
import sys
import time
import fcntl
import signal
import os
from pathlib import Path

import pytest

import run_shadow_maintenance as maintenance


def _configure(tmp_path, monkeypatch, enhanced_at, technical_at):
    state_path = tmp_path / "state.json"
    lock_path = tmp_path / "state.lock"
    enhanced_report = tmp_path / "enhanced.json"
    technical_report = tmp_path / "technical.json"
    enhanced_report.write_text(json.dumps({"generated_at": enhanced_at}))
    technical_report.write_text(json.dumps({"generated_at": technical_at}))
    tasks = {
        "enhanced": {
            **maintenance.TASKS["enhanced"],
            "report": enhanced_report,
        },
        "technical": {
            **maintenance.TASKS["technical"],
            "report": technical_report,
        },
    }
    monkeypatch.setattr(maintenance, "STATE_PATH", state_path)
    monkeypatch.setattr(maintenance, "LOCK_PATH", lock_path)
    monkeypatch.setattr(maintenance, "TASKS", tasks)
    return state_path


def test_existing_reports_bootstrap_state_and_skip_expensive_jobs(
    tmp_path, monkeypatch
):
    now = dt.datetime(2026, 9, 12, 12, tzinfo=dt.timezone.utc)
    state_path = _configure(
        tmp_path, monkeypatch,
        "2026-09-12T08:00:00+00:00",
        "2026-09-10T08:00:00+00:00",
    )
    monkeypatch.setattr(
        maintenance.subprocess, "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("maintenance should be skipped")
        ),
    )

    assert maintenance.run_maintenance(now=now) == 0

    state = json.loads(state_path.read_text())
    assert state["tasks"]["enhanced"]["source"] == "existing_integrity_report"
    assert state["tasks"]["technical"]["source"] == "existing_integrity_report"


def test_only_due_task_runs_and_success_timestamp_is_persisted(
    tmp_path, monkeypatch
):
    now = dt.datetime(2026, 9, 12, 12, tzinfo=dt.timezone.utc)
    state_path = _configure(
        tmp_path, monkeypatch,
        "2026-09-10T08:00:00+00:00",
        "2026-09-10T08:00:00+00:00",
    )
    calls = []

    def fake_run(command, label):
        calls.append((command, label))
        if '--output' in command:
            destination = Path(command[command.index('--output') + 1])
            (destination / 'integrity_report.json').write_text(json.dumps({'generated_at': now.isoformat()}))
        return 0

    monkeypatch.setattr(maintenance, "run_with_heartbeat", fake_run)

    assert maintenance.run_maintenance(now=now) == 0
    assert len(calls) == 1
    assert calls[0][0][2] == "evaluate_shadow_forward.py"
    state = json.loads(state_path.read_text())
    assert state["tasks"]["enhanced"]["last_success_at"] == now.isoformat()
    assert state["tasks"]["technical"]["last_success_at"].startswith(
        "2026-09-10"
    )


def test_failed_task_is_retried_because_success_time_is_not_advanced(
    tmp_path, monkeypatch
):
    now = dt.datetime(2026, 9, 12, 12, tzinfo=dt.timezone.utc)
    state_path = _configure(
        tmp_path, monkeypatch,
        "2026-09-10T08:00:00+00:00",
        "2026-09-10T08:00:00+00:00",
    )
    monkeypatch.setattr(
        maintenance, "run_with_heartbeat",
        lambda *_args, **_kwargs: 2,
    )

    assert maintenance.run_maintenance(selected=["enhanced"], now=now) == 1
    state = json.loads(state_path.read_text())
    assert state["tasks"]["enhanced"]["last_success_at"].startswith(
        "2026-09-10"
    )
    assert state["tasks"]["enhanced"]["last_failure_at"] == now.isoformat()


def test_long_running_child_emits_heartbeat(monkeypatch, capsys):
    class FakeProcess:
        pid = 4321

        def __init__(self):
            self.waits = 0

        def wait(self, timeout):
            self.waits += 1
            if self.waits == 1:
                raise subprocess.TimeoutExpired("job", timeout)
            return 0

    process = FakeProcess()
    monotonic_values = iter((10.0, 10.0, 75.0, 75.0))
    monkeypatch.setattr(maintenance.subprocess, "Popen", lambda _command, **kw: process)
    monkeypatch.setattr(
        maintenance.time, "monotonic", lambda: next(monotonic_values)
    )

    assert maintenance.run_with_heartbeat(
        ["python", "job.py"], "Job lung", heartbeat_seconds=1
    ) == 0
    output = capsys.readouterr().out
    assert "încă rulează" in output
    assert "1m 05s" in output
    assert "PID 4321" in output


def test_timeout_bounds_a_real_child_without_marking_success(tmp_path, monkeypatch):
    now = dt.datetime(2026, 9, 28, tzinfo=dt.timezone.utc)
    state_path = _configure(tmp_path, monkeypatch, '2026-09-01', '2026-09-01')
    script = tmp_path / 'slow.py'
    script.write_text('import time\ntime.sleep(20)\n')
    monkeypatch.setitem(maintenance.TASKS['technical'], 'command', str(script))
    started = time.monotonic()
    assert maintenance.run_maintenance(selected=['technical'], now=now, timeout_seconds=0.2) == 1
    assert time.monotonic() - started < 5
    task = json.loads(state_path.read_text())['tasks']['technical']
    assert task['last_returncode'] == 124
    assert task['last_success_at'].startswith('2026-09-01')


def test_busy_lock_returns_immediately_and_does_not_change_state(tmp_path, monkeypatch):
    _configure(tmp_path, monkeypatch, '2026-09-01', '2026-09-01')
    # The old implementation would hang on this lock; use a bounded subprocess.
    with maintenance.LOCK_PATH.open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = subprocess.run([sys.executable, '-c',
            'import run_shadow_maintenance as m; from pathlib import Path; '
            f'm.LOCK_PATH=Path({str(maintenance.LOCK_PATH)!r}); '
            f'm.STATE_PATH=Path({str(maintenance.STATE_PATH)!r}); '
            'raise SystemExit(m.run_maintenance())'], capture_output=True, text=True, timeout=3)
    assert result.returncode == 0
    assert 'deja' in result.stdout
    assert not maintenance.STATE_PATH.exists()


@pytest.mark.parametrize('seconds', [0, -1, float('inf'), float('nan')])
def test_invalid_time_budget_rejected_before_spawning(seconds):
    with pytest.raises(ValueError):
        maintenance.run_with_heartbeat([sys.executable, '-c', 'pass'], 'test', timeout_seconds=seconds)


def test_manual_interrupt_cleans_only_the_new_child_group(monkeypatch):
    class Process:
        pid = 987654
        waits = 0
        def wait(self, timeout=None):
            self.waits += 1
            if self.waits == 1:
                raise KeyboardInterrupt()
            return -15
    kills = []
    monkeypatch.setattr(maintenance.subprocess, 'Popen', lambda *a, **kw: Process())
    monkeypatch.setattr(maintenance.os, 'killpg', lambda pid, sig: kills.append((pid, sig)))
    with pytest.raises(KeyboardInterrupt):
        maintenance.run_with_heartbeat(['unused'], 'interrupt')
    assert kills == [(987654, signal.SIGTERM), (987654, signal.SIGKILL)]


def test_sigterm_to_cli_cleans_its_child(tmp_path):
    child_file = tmp_path / 'child-pid'
    child = tmp_path / 'child.py'
    child.write_text(f'import os,time\nfrom pathlib import Path\nPath({str(child_file)!r}).write_text(str(os.getpid()))\ntime.sleep(20)\n')
    runner = subprocess.Popen([sys.executable, '-c',
        'import run_shadow_maintenance as m; from pathlib import Path; import sys; '
        f'm.STATE_PATH=Path({str(tmp_path / "state.json")!r}); '
        f'm.LOCK_PATH=Path({str(tmp_path / "state.lock")!r}); '
        f'm.TASKS["technical"]["command"]={str(child)!r}; '
        'sys.argv=["research", "--only", "technical", "--force"]; m.main()'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    child_pid = None
    try:
        until = time.monotonic() + 5
        while not child_file.exists() and time.monotonic() < until:
            time.sleep(0.02)
        assert child_file.exists()
        child_pid = int(child_file.read_text())
        runner.terminate()
        assert runner.wait(timeout=5) == 130
        with pytest.raises(ProcessLookupError):
            os.kill(child_pid, 0)
    finally:
        if runner.poll() is None:
            runner.kill()
            runner.wait()
        if child_pid:
            try:
                os.kill(child_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_failed_enhanced_export_cannot_overwrite_completed_artifacts(tmp_path, monkeypatch):
    now = dt.datetime(2026, 9, 28, tzinfo=dt.timezone.utc)
    _configure(tmp_path, monkeypatch, '2026-09-01', '2026-09-01')
    artifact = tmp_path / 'labelled_predictions.csv'
    artifact.write_text('previous complete dataset')
    job = tmp_path / 'enhanced.py'
    job.write_text('import argparse\nfrom pathlib import Path\np=argparse.ArgumentParser()\n'
                   f'p.add_argument("--output",default={str(tmp_path)!r})\n'
                   'args=p.parse_args()\n(Path(args.output)/"labelled_predictions.csv").write_text("partial")\n'
                   'raise SystemExit(1)\n')
    monkeypatch.setitem(maintenance.TASKS['enhanced'], 'command', str(job))
    assert maintenance.run_maintenance(selected=['enhanced'], now=now) == 1
    assert artifact.read_text() == 'previous complete dataset'


def test_standalone_cadence_survives_legacy_r2_state_restore(tmp_path, monkeypatch):
    now = dt.datetime(2026, 9, 28, tzinfo=dt.timezone.utc)
    monkeypatch.chdir(tmp_path)
    # Keep the production default state path: R2 still restores only legacy file.
    monkeypatch.setattr(maintenance, 'LOCK_PATH', tmp_path / 'lock')
    for task in maintenance.TASKS.values():
        monkeypatch.setitem(task, 'report', tmp_path / 'missing-report.json')
    monkeypatch.setattr(maintenance, 'run_with_heartbeat', lambda *a, **kw: 0)
    assert maintenance.run_maintenance(selected=['technical'], now=now) == 0
    Path('.shadow_maintenance_state.json').write_text(json.dumps({
        'schema': maintenance.SCHEMA, 'tasks': {'technical': {'last_success_at': '2026-09-01T00:00:00Z'}}}))
    assert maintenance.load_state()['tasks']['technical']['last_success_at'] == now.isoformat()


def test_offline_diagnostics_preserve_online_reports_and_cadence(tmp_path, monkeypatch):
    now = dt.datetime(2026, 9, 28, tzinfo=dt.timezone.utc)
    state_path = _configure(tmp_path, monkeypatch, '2026-09-01', '2026-09-01')
    report = tmp_path / 'forward_validation_report.md'
    report.write_text('completed online report')
    def diagnostic(command, label, **kwargs):
        destination = Path(command[command.index('--output') + 1])
        (destination / 'forward_validation_report.md').write_text('pending offline')
        (destination / 'integrity_report.json').write_text(json.dumps({'generated_at': now.isoformat()}))
        return 0
    monkeypatch.setattr(maintenance, 'run_with_heartbeat', diagnostic)
    assert maintenance.run_maintenance(selected=['enhanced'], offline=True, now=now) == 0
    assert report.read_text() == 'completed online report'
    assert (tmp_path / 'offline/forward_validation_report.md').read_text() == 'pending offline'
    assert json.loads(state_path.read_text())['tasks']['enhanced']['last_success_at'].startswith('2026-09-01')


def test_force_technical_refreshes_prices_without_disabling_checkpoints(tmp_path, monkeypatch):
    _configure(tmp_path, monkeypatch, '2026-09-28', '2026-09-28')
    commands = []
    def run(command, label, **kwargs):
        commands.append(command)
        return 0
    monkeypatch.setattr(maintenance, 'run_with_heartbeat', run)
    assert maintenance.run_maintenance(selected=['technical'], force=True) == 0
    assert '--refresh-prices' in commands[0]


@pytest.mark.parametrize('offline,returncode,ready', [(False, 0, True), (True, 0, False), (False, 124, False)])
def test_sync_receipt_only_for_completed_online_work(tmp_path, monkeypatch, offline, returncode, ready):
    _configure(tmp_path, monkeypatch, '2026-09-01', '2026-09-01')
    receipt = tmp_path / 'receipt'
    monkeypatch.setenv('SHADOW_RESEARCH_COMPLETION_FILE', str(receipt))
    monkeypatch.setattr(maintenance, 'run_with_heartbeat', lambda *a, **kw: returncode)
    maintenance.run_maintenance(selected=['technical'], force=True, offline=offline)
    assert receipt.exists() is ready


def test_technical_success_migrates_only_obsolete_uncompressed_export(tmp_path, monkeypatch):
    _configure(tmp_path, monkeypatch, '2026-09-01', '2026-09-01')
    legacy = tmp_path / 'event_observations.csv'
    legacy.write_text('old large export')
    def completed(command, label, **kwargs):
        stage = Path(command[command.index('--output') + 1])
        (stage / 'event_observations.csv.gz').write_bytes(b'new compressed export')
        return 0
    monkeypatch.setattr(maintenance, 'run_with_heartbeat', completed)
    assert maintenance.run_maintenance(selected=['technical'], force=True) == 0
    assert (tmp_path / 'event_observations.csv.gz').read_bytes() == b'new compressed export'
    assert not legacy.exists()
