"""Execute real update scripts with stand-ins only for their external commands."""
import os
from pathlib import Path
import subprocess
import textwrap

import pytest


@pytest.mark.parametrize('filename', ['update_portfolio.sh', 'update_all.sh', 'update_international.sh'])
def test_updates_publish_without_running_research(tmp_path, filename):
    root = Path(__file__).resolve().parents[1]
    (tmp_path / filename).write_text((root / filename).read_text())
    (tmp_path / 'update_git_sync.sh').write_text('''
git_sync_start() { echo start >> "$TRACE"; }
git_sync_finish() { echo finish >> "$TRACE"; }
load_shadow_r2_config() { :; }
runtime_r2_pull() { :; }
load_order_cache_password() { :; }
sync_log_step() { :; }
''')
    bindir = tmp_path / '.venv/bin'
    bindir.mkdir(parents=True)
    for name in ['python', 'gh']:
        script = bindir / name
        script.write_text('#!/bin/bash\nprintf "%s\\n" "$*" >> "$TRACE"\n')
        script.chmod(0o755)
    trace = tmp_path / 'trace'
    env = dict(os.environ, PATH=f'{bindir}:{os.environ["PATH"]}', TRACE=str(trace), TRADEVILLE_WS_SYNC_ENABLED='false')
    result = subprocess.run(['bash', filename], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=5)
    assert result.returncode == 0, result.stderr
    calls = trace.read_text()
    assert 'market_scanner.py' in calls
    assert 'finish' in calls
    assert 'run_shadow_maintenance' not in calls
    if filename == 'update_portfolio.sh':
        assert 'workflow run update_dashboard.yml' in calls


def test_dashboard_action_publishes_without_any_shadow_evaluator(tmp_path):
    root = Path(__file__).resolve().parents[1]
    workflow = (root / '.github/workflows/update_dashboard.yml').read_text()
    step = workflow.split('    - name: Run Market Scanner\n', 1)[1].split('\n    - name:', 1)[0]
    script = textwrap.dedent(step.split('      run: |\n', 1)[1])
    for expression, value in [('github.event_name', 'workflow_dispatch'), ('inputs.update_mode', 'portfolio'), ('github.event.schedule', '')]:
        script = script.replace('${{ ' + expression + ' }}', value)
    python = tmp_path / 'python'
    python.write_text('#!/bin/bash\nprintf "%s\\n" "$*" >> "$TRACE"\n')
    python.chmod(0o755)
    trace = tmp_path / 'trace'
    env = dict(os.environ, PATH=f'{tmp_path}:{os.environ["PATH"]}', TRACE=str(trace))
    result = subprocess.run(['bash', '-e', '-c', script], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=5)
    assert result.returncode == 0, result.stderr
    assert trace.read_text().splitlines() == [
        'update_sp500_json.py', 'market_scanner.py --mode portfolio',
        'runtime_r2_store.py push --publish-loader',
    ]


def test_standalone_research_does_not_sync_or_publish(tmp_path):
    root = Path(__file__).resolve().parents[1]
    (tmp_path / 'run_shadow_research.sh').write_text((root / 'run_shadow_research.sh').read_text())
    (tmp_path / 'update_git_sync.sh').write_text('''
load_shadow_r2_config() { :; }
git_sync_start() { exit 91; }
git_sync_finish() { exit 92; }
runtime_r2_pull() { exit 93; }
runtime_r2_push() { exit 94; }
''')
    bindir = tmp_path / '.venv/bin'
    bindir.mkdir(parents=True)
    python = bindir / 'python'
    python.write_text('#!/bin/bash\nprintf "%s\\n" "$*"\n')
    python.chmod(0o755)
    result = subprocess.run(['bash', 'run_shadow_research.sh', '--only', 'technical', '--timeout-seconds', '60'],
                            cwd=tmp_path, capture_output=True, text=True, timeout=5)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == '-u run_shadow_maintenance.py --only technical --timeout-seconds 60'


def test_git_merge_refresh_only_updates_collection_report(tmp_path):
    root = Path(__file__).resolve().parents[1]
    python = tmp_path / 'python'
    trace = tmp_path / 'trace'
    python.write_text('#!/bin/bash\nprintf "%s\\n" "$*" >> "$TRACE"\n')
    python.chmod(0o755)
    env = dict(os.environ, TRACE=str(trace), RESEARCH_TEST_PYTHON=str(python))
    result = subprocess.run(['bash', '-e', '-c',
        'source "$1"; sync_python_bin() { echo "$RESEARCH_TEST_PYTHON"; }; git_sync_refresh_shadow_reports',
        'test', str(root / 'update_git_sync.sh')], env=env, capture_output=True, text=True, timeout=5)
    assert result.returncode == 0, result.stderr
    assert trace.read_text().splitlines() == [
        '-c import shadow_validation; shadow_validation.generate_readiness_report()',
    ]
