"""Deterministic diagnostics tests; these do not validate a trading strategy."""

from datetime import date, timedelta
import json
import math

import pandas as pd
import pytest

from scripts.validate_swing_regimes import (
    forward_return_summary,
    legacy_bvb_buy,
    load_local_series,
    main,
    normalize_series,
    replay_series,
    sequential_snapshots,
)


def example_series(size=260):
    dates = [(date(2025, 1, 1) + timedelta(days=i)).isoformat() for i in range(size)]
    closes = [100 + i * 0.1 + math.sin(i / 3) for i in range(size)]
    return dates, closes


def research_evaluator(**values):
    return {
        'regime': 'SELECTIVE',
        'research_allowed': True,
        'pullback': {'status': 'WAIT'},
        'continuation': {'status': 'READY'},
        'legacy_verdict': 'AȘTEAPTĂ CONFIRMAREA',
        'entry_status': 'WAIT',
    }


def test_sequential_rsi_matches_existing_wilder_method():
    dates, closes = example_series()
    series = pd.Series(closes)
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    expected = 100 - 100 / (
        1 + gain.ewm(alpha=1 / 14, adjust=False).mean()
        / loss.ewm(alpha=1 / 14, adjust=False).mean()
    )
    rows = list(sequential_snapshots(dates, closes))
    assert len(rows) == 61
    assert rows[0]['index'] == 199
    for row in rows:
        assert row['rsi'] == pytest.approx(expected.iloc[row['index']], abs=1e-10)


def test_decisions_do_not_use_future_prices_and_use_historical_clock():
    dates, closes = example_series()
    calls = []

    def capture(**values):
        calls.append(values)
        assert values['observed_at'] == values['now'].isoformat()
        return research_evaluator(**values)

    replay_series(dates[:230], closes[:230], 0, capture)
    original = list(calls)
    calls.clear()
    replay_series(dates, closes[:230] + [1000] * 30, 0, capture)
    assert calls[:len(original)] == original


def test_frequency_distinguishes_research_from_entry():
    dates, closes = example_series()
    report = replay_series(dates, closes, 20, research_evaluator)
    assert report['evaluated_sessions'] == 61
    assert report['cohorts']['regime_research_eligible']['sessions'] == 61
    assert report['cohorts']['continuation_research_only']['sessions'] == 61
    assert report['entry_status_counts'] == {'WAIT': 61}
    expected_old_buy = sum(legacy_bvb_buy(row) for row in sequential_snapshots(dates, closes))
    assert report['cohorts']['legacy_buy']['sessions'] == expected_old_buy
    horizon = report['cohorts']['regime_research_eligible']['forward_returns']['20']
    assert horizon['available_outcomes'] == 41
    assert horizon['missing_future_outcomes'] == 20
    assert any('overlap' in item for item in report['limitations'])
    assert any('US replay' in item for item in report['limitations'])


def test_cost_adjustment_and_missing_outcomes_are_explicit():
    closes = [100, 110, 121]
    result = forward_return_summary(closes, [0, 1, 2], 1, 40)
    assert result['available_outcomes'] == 2
    assert result['missing_future_outcomes'] == 1
    assert result['mean_proxy_close_return_pct'] == 10.0
    assert result['mean_less_hypothetical_roundtrip_cost_pct'] == 9.6
    missing = forward_return_summary(closes, [2], 1, 40)
    assert missing['available_outcomes'] == 0
    assert missing['mean_proxy_close_return_pct'] is None
    assert missing['mean_less_hypothetical_roundtrip_cost_pct'] is None


def test_old_rule_missing_rsi_and_boundary_are_frozen():
    row = {'price': 100, 'sma200': 90, 'sma10': 95, 'rsi': None}
    assert legacy_bvb_buy(row) is True
    assert legacy_bvb_buy({**row, 'rsi': 45}) is True
    assert legacy_bvb_buy({**row, 'rsi': 70}) is False


@pytest.mark.parametrize('cost', [-1, float('inf'), float('nan'), True])
def test_invalid_cost_is_rejected(cost):
    dates, closes = example_series()
    with pytest.raises(ValueError, match='cost'):
        replay_series(dates, closes, cost, research_evaluator)


def test_series_rejects_bad_alignment_order_and_values():
    dates, closes = example_series()
    with pytest.raises(ValueError, match='identical lengths'):
        normalize_series(dates, closes[:-1])
    with pytest.raises(ValueError, match='strictly increasing'):
        normalize_series(dates[:1] + dates[:-1], closes)
    with pytest.raises(ValueError, match='finite positive'):
        normalize_series(dates, closes[:-1] + [float('nan')])
    with pytest.raises(ValueError, match='at least 200'):
        normalize_series(dates[:199], closes[:199])


def test_loader_accepts_snapshot_and_cli_requires_explicit_cost(tmp_path):
    dates, closes = example_series()
    path = tmp_path / 'state.json'
    path.write_text(json.dumps({'bvb_proxy': {'Chart_Dates': dates, 'Chart_History': closes}}))
    assert load_local_series(path) == (dates, closes)
    with pytest.raises(SystemExit) as error:
        main(['--input', str(path)])
    assert error.value.code == 2


def test_real_evaluator_smoke_and_json_serialization():
    dates, _ = example_series()
    closes = [100 + i for i in range(len(dates))]
    report = replay_series(dates, closes, 20)
    assert report['cohorts']['legacy_buy']['sessions'] == 0
    assert report['cohorts']['continuation_research_only']['sessions'] == 61
    assert report['cohorts']['regime_research_eligible']['sessions'] == 61
    json.dumps(report, allow_nan=False)


def test_cli_emits_only_json_without_changing_input(tmp_path, capsys):
    dates, closes = example_series()
    path = tmp_path / 'closes.json'
    original = json.dumps({'dates': dates, 'closes': closes})
    path.write_text(original)
    assert main(['--input', str(path), '--roundtrip-cost-bps', '20']) == 0
    output = capsys.readouterr()
    assert json.loads(output.out)['evaluated_sessions'] == 61
    assert output.err == ''
    assert path.read_text() == original
    assert list(tmp_path.iterdir()) == [path]
