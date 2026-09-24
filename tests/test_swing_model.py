from datetime import datetime, timedelta, timezone
import math

import pytest

from swing_model import evaluate_bvb, evaluate_international


NOW = datetime(2026, 9, 24, 18, tzinfo=timezone.utc)


def international_data():
    data = {'VIX_Current': 18, 'Breadth_Pct': 72, 'FG_Score': 48, 'FG_SMA5': 47,
            'VIX_Observed_At': NOW.isoformat(), 'FG_Observed_At': NOW.isoformat(),
            'Breadth_Observed_At': NOW.isoformat(),
            'Market_Tide': {'NewHighs': 100, 'NewLows': 80, 'observed_at': NOW.isoformat()}}
    for prefix in ('SPX', 'NDX'):
        data.update({f'{prefix}_{key}': value for key, value in {
            'Price': 120, 'SMA10': 115, 'SMA50': 110, 'SMA200': 100,
            'RSI': 60, 'Observed_At': NOW.isoformat(),
        }.items()})
    return data


def test_sentiment_wait_does_not_disable_healthy_market_research():
    data = international_data()
    legacy = evaluate_international(data, now=NOW)
    assert legacy['legacy_verdict'] == 'BUY'
    data['FG_Score'] = 55
    result = evaluate_international(data, now=NOW)
    assert result['regime'] == 'FAVORABLE'
    assert result['research_allowed'] is True
    assert result['pullback']['status'] == 'WAIT'
    assert result['continuation']['status'] == 'READY'
    assert result['continuation']['research_only'] is True
    assert result['execution_permission'] is False
    assert result['validation_status'] == 'UNVALIDATED'


@pytest.mark.parametrize('patch', [{'VIX_Current': 31}, {'Breadth_Pct': 29},
                                 {'SPX_Price': 90, 'NDX_Price': 90}])
def test_defensive_guards_cannot_be_bypassed_by_continuation(patch):
    data = international_data()
    data.update(patch)
    result = evaluate_international(data, now=NOW)
    assert result['regime'] == 'DEFENSIVE'
    assert result['research_allowed'] is False
    assert result['entry_status'] != 'READY'
    assert result['continuation']['status'] != 'READY'


@pytest.mark.parametrize('patch', [{'NDX_SMA200': 0}, {'SPX_Price': math.nan},
                                 {'Breadth_Pct': None}, {'VIX_Observed_At': None},
                                 {'SPX_Observed_At': (NOW - timedelta(days=5)).isoformat()}])
def test_bad_or_stale_core_data_is_unknown_not_bullish(patch):
    data = international_data()
    data.update(patch)
    result = evaluate_international(data, now=NOW)
    assert result['regime'] == 'UNKNOWN'
    assert result['entry_status'] == 'UNKNOWN'
    assert result['research_allowed'] is False


def test_tide_weakness_is_selective_research_not_automatic_buy():
    data = international_data()
    data['Market_Tide']['NewLows'] = 101
    result = evaluate_international(data, now=NOW)
    assert result['regime'] == 'SELECTIVE'
    assert result['research_allowed'] is True
    assert result['legacy_verdict'] == 'WAIT (INTERNAL ROT)'


def test_stale_tide_is_unknown_confirmation_not_fresh_veto():
    data = international_data()
    data['Market_Tide'].update(NewLows=999, observed_at=(NOW - timedelta(days=5)).isoformat())
    result = evaluate_international(data, now=NOW)
    assert result['regime'] == 'SELECTIVE'
    assert result['entry_status'] == 'UNKNOWN'
    assert result['data_quality']['status'] == 'PARTIAL'


def test_fetch_timestamp_does_not_claim_session_confirmation():
    data = international_data()
    data['Breadth_Observed_At'] = None
    data['Breadth_Fetched_At'] = NOW.isoformat()
    data['Market_Tide'].pop('observed_at')
    data['Market_Tide']['fetched_at'] = NOW.isoformat()
    result = evaluate_international(data, now=NOW)
    assert result['regime'] == 'SELECTIVE'
    assert result['data_quality']['status'] == 'PARTIAL'
    assert len(result['data_quality']['issues']) >= 2


@pytest.mark.parametrize('rsi', [70, 85, 100])
def test_bvb_strong_momentum_does_not_block_research(rsi):
    result = evaluate_bvb(120, 115, 110, 100, rsi, NOW.isoformat(), NOW)
    assert result['regime'] == 'FAVORABLE'
    assert result['pullback']['status'] == 'WAIT'
    assert result['continuation']['status'] == 'READY'
    assert result['execution_permission'] is False


def test_bvb_missing_rsi_never_confirms_entry():
    result = evaluate_bvb(120, 115, 110, 100, None, NOW.isoformat(), NOW)
    assert result['entry_status'] == 'UNKNOWN'
    assert result['continuation']['status'] == 'UNKNOWN'


def test_bvb_intermediate_weakness_keeps_legacy_pullback_but_not_continuation():
    result = evaluate_bvb(105, 103, 110, 100, 55, NOW.isoformat(), NOW)
    assert result['regime'] == 'SELECTIVE'
    assert result['legacy_verdict'] == 'CUMPĂRĂ'
    assert result['continuation']['status'] == 'WAIT'


@pytest.mark.parametrize('sma200,observed', [(None, NOW.isoformat()), (100, None),
                                        (100, (NOW - timedelta(days=5)).isoformat())])
def test_bvb_insufficient_data_blocks_research(sma200, observed):
    result = evaluate_bvb(120, 115, 110, sma200, 55, observed, NOW)
    assert result['regime'] == 'UNKNOWN'
    assert result['research_allowed'] is False


def test_weekend_tolerance_and_zero_rsi_are_explicit():
    result = evaluate_bvb(90, 110, 105, 100, 0,
                          (NOW - timedelta(hours=90)).isoformat(), NOW)
    assert result['regime'] == 'DEFENSIVE'
    assert result['pullback']['status'] == 'WAIT'


def test_boolean_numbers_and_malformed_tide_do_not_confirm_entry():
    data = international_data()
    data.update(FG_Score=False, FG_SMA5=False)
    assert evaluate_international(data, now=NOW)['entry_status'] == 'UNKNOWN'
    data = international_data()
    data['Market_Tide'] = 'unavailable'
    assert evaluate_international(data, now=NOW)['entry_status'] == 'UNKNOWN'
    data = international_data()
    data['SPX_Price'] = True
    assert evaluate_international(data, now=NOW)['regime'] == 'UNKNOWN'
