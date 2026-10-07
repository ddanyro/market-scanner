"""Contracts at the GitHub scheduler boundary, plus the real publish guard."""
import os
import json
from pathlib import Path
import subprocess

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]


def workflow(name):
    return yaml.safe_load((ROOT / '.github/workflows' / name).read_text())


def test_waiting_pages_cannot_own_the_market_writer_lock():
    dashboard = workflow('update_dashboard.yml')
    romanian = workflow('update_ro.yml')
    assert 'concurrency' not in dashboard
    assert 'concurrency' not in romanian
    build = dashboard['jobs']['build']
    ro = romanian['jobs']['update-ro']
    for job in (build, ro):
        assert job['concurrency']['group'] == 'market-dashboard-writes'
        assert job['concurrency']['cancel-in-progress'] is False
        # BVB must wait its turn, not be evicted by the next portfolio refresh.
        assert job['concurrency']['queue'] == 'max'
        assert 0 < job['timeout-minutes'] <= 120
        checkout = next(step for step in job['steps'] if step.get('uses', '').startswith('actions/checkout@'))
        assert checkout['with']['ref'] == 'main'
    deploy = dashboard['jobs']['deploy-pages']
    assert deploy['concurrency']['group'] != build['concurrency']['group']
    assert deploy['concurrency']['cancel-in-progress'] is False
    assert 0 < deploy['timeout-minutes'] <= 15
    assert deploy['environment']['name'] == 'github-pages'
    assert deploy['needs'] == 'build'


def test_pages_artifact_revision_is_exported_after_market_commit():
    build = workflow('update_dashboard.yml')['jobs']['build']
    steps = build['steps']
    commit = next(i for i, s in enumerate(steps) if s.get('name') == 'Commit and Push changes')
    revision = next((i for i, s in enumerate(steps) if s.get('id') == 'pages-revision'), None)
    assert revision is not None, 'Capture the post-update commit, not the triggering SHA'
    assert revision > commit
    assert build['outputs']['pages_sha'] == '${{ steps.pages-revision.outputs.sha }}'
    deploy = workflow('update_dashboard.yml')['jobs']['deploy-pages']
    guard = next(s for s in deploy['steps'] if s.get('id') == 'pages-current')
    assert guard['env']['ARTIFACT_SHA'] == '${{ needs.build.outputs.pages_sha }}'
    publish = next(s for s in deploy['steps'] if s.get('uses', '').startswith('actions/deploy-pages@'))
    assert publish['if'] == "${{ steps.pages-current.outputs.deploy == 'true' }}"


def test_romanian_refresh_schedules_publication_without_another_scan():
    ro = workflow('update_ro.yml')['jobs']['update-ro']
    dispatch = next((s for s in ro['steps'] if s.get('name') == 'Schedule Pages publication'), None)
    assert dispatch is not None, 'GITHUB_TOKEN pushes do not trigger the push workflow'
    dashboard = workflow('update_dashboard.yml')
    triggers = dashboard.get('on', dashboard.get(True))
    option = triggers['workflow_dispatch']['inputs'].get('publish_only')
    assert option and option['type'] == 'boolean' and option['default'] is False
    assert dispatch['env']['GH_TOKEN'] == '${{ github.token }}'
    assert '-f publish_only=true' in dispatch['run']
    # Evaluate the actual simple boolean guards against a publishing-only event.
    # Missing guards would rescan the portfolio / write R2 after every BVB scan.
    for step in dashboard['jobs']['build']['steps']:
        if step.get('name') not in {
            'Set up Python', 'Install dependencies', 'Restore private runtime state from R2',
            'Retry pending Firebase BUY alerts', 'Run Market Scanner', 'Commit and Push changes',
        }:
            continue
        expression = step['if'].removeprefix('${{').removesuffix('}}').strip()
        for key, value in {'github.event_name': 'workflow_dispatch',
                           'inputs.publish_only': True, 'inputs.push_test_symbol': ''}.items():
            expression = expression.replace(key, json.dumps(value))
        assert subprocess.check_output(['node', '-e', f'console.log({expression})'], text=True).strip() == 'false', step['name']


@pytest.mark.parametrize('latest,exit_code,expected', [
    ('a' * 40, 0, 'true'), ('b' * 40, 0, 'false'), ('', 1, None),
])
def test_publish_guard_skips_stale_artifacts_and_fails_closed(tmp_path, latest, exit_code, expected):
    steps = workflow('update_dashboard.yml')['jobs']['deploy-pages']['steps']
    guard = next((s for s in steps if s.get('id') == 'pages-current'), None)
    assert guard is not None, 'An older Pages artifact must not overwrite a newer revision'
    gh = tmp_path / 'gh'
    gh.write_text(f'#!/bin/sh\nprintf "%s\\n" "{latest}"\nexit {exit_code}\n')
    gh.chmod(0o755)
    output = tmp_path / 'output'
    summary = tmp_path / 'summary'
    env = dict(os.environ, PATH=f'{tmp_path}:{os.environ["PATH"]}',
               ARTIFACT_SHA='a' * 40, GITHUB_REPOSITORY='owner/repo',
               GITHUB_OUTPUT=str(output), GITHUB_STEP_SUMMARY=str(summary))
    result = subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', guard['run']],
                            env=env, capture_output=True, text=True, timeout=5)
    if expected is None:
        assert result.returncode != 0
        assert not output.exists()
    else:
        assert result.returncode == 0, result.stderr
        assert output.read_text().strip() == f'deploy={expected}'
