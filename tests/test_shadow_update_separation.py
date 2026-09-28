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


@pytest.mark.parametrize('outcome,receipt,expected_sync', [(0, True, True), (1, True, False), (124, False, False), (0, False, False)])
def test_standalone_research_syncs_only_successful_online_work(tmp_path, outcome, receipt, expected_sync):
    root = Path(__file__).resolve().parents[1]
    (tmp_path / 'run_shadow_research.sh').write_text((root / 'run_shadow_research.sh').read_text())
    (tmp_path / 'update_git_sync.sh').write_text('''
load_shadow_r2_config() { :; }
git_sync_assert_ready() { :; }
git_sync_research_finish() { echo synced >> "$TRACE"; }
git_sync_start() { exit 91; }
git_sync_finish() { exit 92; }
runtime_r2_pull() { exit 93; }
runtime_r2_push() { exit 94; }
''')
    bindir = tmp_path / '.venv/bin'
    bindir.mkdir(parents=True)
    python = bindir / 'python'
    python.write_text('#!/bin/bash\nprintf "%s\\n" "$*"\n'
                      + ('[ -z "${SHADOW_RESEARCH_COMPLETION_FILE:-}" ] || echo ready > "$SHADOW_RESEARCH_COMPLETION_FILE"\n' if receipt else '')
                      + f'exit {outcome}\n')
    python.chmod(0o755)
    gh = bindir / 'gh'
    gh.write_text('#!/bin/bash\nexit 0\n')
    gh.chmod(0o755)
    trace = tmp_path / 'trace'
    env = dict(os.environ, PATH=f'{bindir}:{os.environ["PATH"]}', TRACE=str(trace))
    result = subprocess.run(['bash', 'run_shadow_research.sh', '--only', 'technical', '--timeout-seconds', '60'],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=5)
    assert result.returncode == outcome, result.stderr
    assert '-u run_shadow_maintenance.py --only technical --timeout-seconds 60' in result.stdout
    assert trace.exists() is expected_sync


def test_research_git_sync_preserves_portfolio_and_excludes_private_cache(tmp_path):
    root = Path(__file__).resolve().parents[1]
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=tmp_path, text=True).strip()
    git('init', '-b', 'main')
    git('config', 'user.name', 'Research Test')
    git('config', 'user.email', 'research@example.invalid')
    (tmp_path / '.gitignore').write_text('.shadow_research_cache/\nanalysis/technical_events_validation/labelled_predictions.csv.gz\n')
    (tmp_path / 'portfolio.csv').write_text('original portfolio')
    report = tmp_path / 'analysis/technical_events_validation/technical_events_validation_report.md'
    report.parent.mkdir(parents=True)
    report.write_text('old report')
    git('add', '.')
    git('commit', '-m', 'initial')
    remote = tmp_path / 'remote.git'
    subprocess.run(['git', 'init', '--bare', str(remote)], check=True, capture_output=True)
    git('remote', 'add', 'origin', str(remote))
    git('push', '-u', 'origin', 'main')
    report.write_text('new report')
    (tmp_path / 'portfolio.csv').write_text('user unsaved changes')
    (report.parent / 'labelled_predictions.csv.gz').write_bytes(b'private dataset')
    bindir = tmp_path / 'bin'
    bindir.mkdir()
    gh = bindir / 'gh'
    gh.write_text('#!/bin/bash\necho "$*" >> "$TRACE"\n')
    gh.chmod(0o755)
    trace = tmp_path / 'trace'
    result = subprocess.run(['bash', '-e', '-c', 'source "$1"; git_sync_research_finish', 'test', str(root / 'update_git_sync.sh')],
                            cwd=tmp_path, env=dict(os.environ, PATH=f'{bindir}:{os.environ["PATH"]}', TRACE=str(trace)),
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert git('show', 'origin/main:analysis/technical_events_validation/technical_events_validation_report.md') == 'new report'
    assert git('show', 'origin/main:portfolio.csv') == 'original portfolio'
    assert (tmp_path / 'portfolio.csv').read_text() == 'user unsaved changes'
    assert git('ls-files', '*labelled_predictions*') == ''
    assert trace.read_text().strip() == 'workflow run update_dashboard.yml -f update_mode=portfolio'
    # An unchanged report must not dispatch another dashboard run.
    command = ['bash', '-e', '-c', 'source "$1"; git_sync_research_finish',
               'test', str(root / 'update_git_sync.sh')]
    env = dict(os.environ, PATH=f'{bindir}:{os.environ["PATH"]}', TRACE=str(trace))
    unchanged = subprocess.run(command, cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15)
    assert unchanged.returncode == 0, unchanged.stderr
    assert len(trace.read_text().splitlines()) == 1
    # Pre-staged user edits must remain untouched and must not be committed.
    report.write_text('another report')
    git('add', 'portfolio.csv')
    head = git('rev-parse', 'HEAD')
    blocked = subprocess.run(command, cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15)
    assert blocked.returncode != 0
    assert git('rev-parse', 'HEAD') == head
    assert git('diff', '--cached', '--name-only') == 'portfolio.csv'
    assert len(trace.read_text().splitlines()) == 1


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
