"""BVB rendering, proxy freshness and independent research/execution gates."""
import datetime
from unittest.mock import patch

import numpy as np
import pandas as pd

import market_scanner
import market_scanner_analysis
import pytest


def _migration_snapshot(dated=False):
    result = {'VIX_Current': 18, 'Breadth_Pct': 55}
    for prefix in ('SPX', 'NDX'):
        result.update({f'{prefix}_{key}': value for key, value in
                       [('Price', 120), ('SMA10', 115), ('SMA50', 110), ('SMA200', 100)]})
    if dated:
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        for key in ('SPX_Observed_At', 'NDX_Observed_At', 'VIX_Observed_At', 'Breadth_Fetched_At'):
            result[key] = timestamp
    return result


@pytest.mark.parametrize('mode', ['portfolio', 'ro'])
def test_legacy_swing_cache_refreshes_once_and_persists(mode):
    old, fresh = _migration_snapshot(), _migration_snapshot(dated=True)
    state = {'market_overviews': {'SUA': {'data': old}}}
    with patch('market_scanner.get_swing_trading_data', return_value=fresh) as fetch, \
            patch('market_scanner.market_utils.save_state') as save:
        result = market_scanner._refresh_legacy_swing_cache(state, old, mode)
        assert result == fresh
        assert state['market_overviews']['SUA']['data'] == fresh
        assert market_scanner._refresh_legacy_swing_cache(state, result, mode) == fresh
        fetch.assert_called_once()
        save.assert_called_once_with(state)
    assert 'SPX_Observed_At' not in old


@pytest.mark.parametrize('mode,data', [('html-only', _migration_snapshot()),
                                     ('portfolio', None), ('portfolio', {}),
                                     ('portfolio', _migration_snapshot(dated=True))])
def test_swing_cache_migration_does_not_fetch_unnecessarily(mode, data):
    with patch('market_scanner.get_swing_trading_data') as fetch:
        assert market_scanner._refresh_legacy_swing_cache({}, data, mode) == data
        fetch.assert_not_called()


@pytest.mark.parametrize('failure', [None, RuntimeError('offline')])
def test_failed_cache_migration_preserves_old_snapshot(failure):
    old = _migration_snapshot()
    state = {'market_overviews': {'SUA': {'data': old}}}
    with patch('market_scanner.get_swing_trading_data', return_value={}, side_effect=failure), \
            patch('market_scanner.market_utils.save_state') as save:
        assert market_scanner._refresh_legacy_swing_cache(state, old, 'portfolio') == old
        assert state['market_overviews']['SUA']['data'] == old
        save.assert_not_called()


def test_missing_observation_dates_are_explained_in_primary_signal():
    from swing_model import evaluate_international
    signal = evaluate_international(_migration_snapshot())
    assert signal['regime'] == 'UNKNOWN'
    for key in ('SPX_Observed_At', 'NDX_Observed_At', 'VIX_Observed_At', 'Breadth_Fetched_At'):
        assert key in signal['reason']
        assert key in signal['pullback']['reason']
    assert 'valoare lipsă' not in signal['reason']


def _proxy(length=220, rsi=60, age_days=0, price=60):
    today = pd.Timestamp(datetime.datetime.now(datetime.timezone.utc)).normalize()
    end = today - pd.Timedelta(days=age_days)
    return {
        'Symbol': 'TVBETETF.RO',
        'Price_Native': price,
        'RSI': rsi,
        'Chart_History': np.linspace(40, price, length).tolist(),
        'Chart_Dates': pd.date_range(end=end, periods=length).strftime('%Y-%m-%d').tolist(),
        'Market_Data_Observed_At': end.isoformat(),
    }


def _overview(row):
    return market_scanner._generate_bvb_market_overview_html(
        pd.DataFrame([row]), pd.DataFrame(), return_signal=True,
    )


def test_bvb_separates_market_regime_from_proxy_entry_and_stock_setup():
    rendered, signal = _overview(_proxy(rsi=75))
    assert signal['regime'] == 'FAVORABLE'
    assert signal['research_allowed'] is True
    assert signal['entry_status'] == 'WAIT'
    assert signal['verdict'] == 'AȘTEAPTĂ CONFIRMAREA'
    assert signal['validation_status'] == 'UNVALIDATED'
    assert 'REGIM:' in rendered
    assert 'Intrare pe proxy' in rendered
    assert 'Continuarea trendului — cercetare, nevalidată' in rendered
    assert 'Acțiunea concretă:' in rendered
    assert 'regimul favorabil nu este un ordin de cumpărare' in rendered


def test_bvb_chat_and_dashboard_share_regime_and_entry_rules():
    for row in [_proxy(rsi=75), _proxy(rsi=60), _proxy(age_days=10), _proxy(rsi=None)]:
        _, signal = _overview(row)
        summary = market_scanner_analysis._tvbetetf_market_summary(row)
        assert summary['technical_verdict'] == signal['verdict']
        assert summary['swing_assessment']['regime'] == signal['regime']
        assert summary['swing_assessment']['entry_status'] == signal['entry_status']


def test_regime_change_invalidates_cached_stock_analysis():
    candidate = {'symbol': 'TEST', 'market_assessment': {'regime': 'FAVORABLE'}}
    snapshot = {'buy_candidates': [candidate]}
    before = market_scanner_analysis._portfolio_critical_fingerprint(snapshot)
    candidate['market_assessment']['regime'] = 'SELECTIVE'
    assert market_scanner_analysis._portfolio_critical_fingerprint(snapshot) != before


def test_bvb_missing_rsi_does_not_receive_buy_or_green_score():
    row = _proxy(rsi=None)
    with patch('market_scanner.calculate_rsi', return_value=pd.Series([np.nan] * 220)):
        rendered, signal = _overview(row)
    assert signal['entry_status'] == 'UNKNOWN'
    assert signal['verdict'] != 'CUMPĂRĂ'
    assert signal['score'] is None
    assert '>N/D</div>' in rendered


def test_bvb_stale_history_is_not_refreshed_by_cache_fetch_timestamp():
    row = _proxy(age_days=10)
    row['Market_Data_Fetched_At'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rendered, signal = _overview(row)
    assert signal['regime'] == 'UNKNOWN'
    assert signal['entry_status'] == 'UNKNOWN'
    assert signal['research_allowed'] is False
    assert signal['score'] is None
    assert 'Date insuficiente sau neactualizate' in rendered


def test_bvb_missing_major_average_is_not_replaced_by_sma50():
    _, signal = _overview(_proxy(length=90))
    assert signal['regime'] == 'UNKNOWN'
    assert signal['research_allowed'] is False
    assert signal['verdict'] != 'CUMPĂRĂ'
    assert signal['score'] is None


def test_bvb_missing_observation_timestamp_does_not_confirm_entry():
    row = _proxy()
    row.pop('Market_Data_Observed_At')
    row.pop('Chart_Dates')
    _, signal = _overview(row)
    assert signal['regime'] == 'UNKNOWN'
    assert signal['entry_status'] == 'UNKNOWN'


def test_bvb_newer_adequate_history_beats_longest_stale_history():
    old = _proxy(length=260, age_days=20, price=55)
    fresh = _proxy(length=220, price=60)
    state = {'bvb_proxy': old}
    result = market_scanner._select_best_bvb_proxy_row(
        pd.DataFrame([fresh]), pd.DataFrame(), full_state=state,
    )
    assert result['Price_Native'] == 60
    assert len(result['Chart_History']) == 220
    assert result['Chart_Dates'][-1] == fresh['Chart_Dates'][-1]
    assert state['bvb_proxy']['Price_Native'] == 60


def test_bvb_merges_shorter_fresh_history_in_native_currency():
    old = _proxy(length=200, age_days=20, price=50)
    old['Chart_History'] = np.linspace(8, 10, 200).tolist()  # Portfolio EUR.
    fresh = _proxy(length=20, price=60)
    fresh['Chart_History'] = np.linspace(50.5, 60, 20).tolist()  # Native RON.
    fresh['RSI'] = 48
    result = market_scanner._select_best_bvb_proxy_row(
        pd.DataFrame([fresh]), pd.DataFrame([old]),
    )
    assert len(result['Chart_History']) == 220
    assert result['Chart_History'][0] == 40
    assert result['Chart_History'][-1] == 60
    assert result['Price_Native'] == 60
    assert result['RSI'] == 48
    assert result['Chart_Dates'] == sorted(result['Chart_Dates'])


def test_bvb_without_mergeable_dates_preserves_fresh_quote_conservatively():
    old = _proxy(length=260, age_days=20, price=50)
    old.pop('Chart_Dates')
    fresh = _proxy(length=20, price=60)
    result = market_scanner._select_best_bvb_proxy_row(
        pd.DataFrame([fresh]), pd.DataFrame([old]),
    )
    assert result['Price_Native'] == 60
    assert len(result['Chart_History']) == 20


def test_market_research_gate_allows_wait_in_selective_regime_only_for_own_market():
    international = {
        'key': 'international', 'regime': 'SELECTIVE',
        'research_allowed': True, 'verdict': 'WAIT (INTERNAL ROT)',
    }
    bvb = {
        'key': 'romania_bvb', 'regime': 'DEFENSIVE',
        'research_allowed': False, 'verdict': 'PRUDENȚĂ',
    }
    allowed, blocked, gates = market_scanner._filter_ai_buy_candidates_by_market_signal(
        [{'symbol': 'AMD', 'market': 'SUA'}, {'symbol': 'TLV.RO', 'market': 'România / BVB'}],
        international, bvb,
    )
    assert [item['symbol'] for item in allowed] == ['AMD']
    assert [item['symbol'] for item in blocked] == ['TLV.RO']
    assert gates == {'international': True, 'romania_bvb': False}


def test_market_research_gate_rejects_unknown_even_with_old_buy_verdict():
    assert not market_scanner._market_signal_allows_ai_stock_analysis({
        'key': 'international', 'regime': 'UNKNOWN', 'research_allowed': False,
        'verdict': 'BUY',
    })
    assert not market_scanner._market_signal_allows_ai_stock_analysis({
        'key': 'international', 'regime': 'FAVORABLE', 'research_allowed': 'true',
        'verdict': 'BUY',
    })


def test_legacy_signal_gate_remains_conservative_until_snapshot_refresh():
    assert market_scanner._market_signal_allows_ai_stock_analysis({
        'key': 'international', 'verdict': 'BUY (RELIEF)',
    })
    assert not market_scanner._market_signal_allows_ai_stock_analysis({
        'key': 'international', 'verdict': 'WAIT',
    })


def test_gate_notice_describes_research_not_permission_to_execute():
    rendered = market_scanner._render_ai_stock_gate_notice(
        {'regime_label': 'Defensiv', 'verdict': 'WAIT'}, {},
        [{'symbol': 'AMD', 'market': 'SUA'}],
    )
    assert 'regim/date piață: Defensiv' in rendered
    assert 'Cercetarea nu autorizează execuția' in rendered
    assert 'devine verde' not in rendered


def test_unavailable_bvb_proxy_returns_unknown_new_schema():
    with patch('market_scanner._select_best_bvb_proxy_row', return_value=None):
        _, signal = market_scanner._generate_bvb_market_overview_html(
            pd.DataFrame(), pd.DataFrame(), return_signal=True,
        )
    assert signal['regime'] == 'UNKNOWN'
    assert signal['research_allowed'] is False
    assert signal['entry_status'] == 'UNKNOWN'
