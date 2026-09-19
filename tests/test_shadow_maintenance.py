import datetime as dt
import json
import subprocess

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
        return 0

    monkeypatch.setattr(maintenance, "run_with_heartbeat", fake_run)

    assert maintenance.run_maintenance(now=now) == 0
    assert len(calls) == 1
    assert calls[0][0][-1] == "evaluate_shadow_forward.py"
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
    monotonic_values = iter((10.0, 75.0))
    monkeypatch.setattr(maintenance.subprocess, "Popen", lambda _command: process)
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
