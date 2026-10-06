import json
import ast
import datetime
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

import market_data


def metrics(item):
    from volatility_metrics import volatility_payload
    result = volatility_payload(item)
    json.dumps(result, allow_nan=False)
    return result


def test_nan_finviz_uses_native_history_atr():
    result = metrics({'Price_Native': 100, 'ATR_Native': 3,
                      'Finviz_ATR': float('nan'), 'Vol_W': float('nan')})
    assert result['ATR_Val'] == 3
    assert result['ATR_Pct'] == 3
    assert result['Trail_Larg'] == 9
    assert result['Vol_W'] is None
    assert result['ATR_Source'] == 'Istoric prețuri'


def test_legacy_watchlist_atr_is_converted_from_eur():
    result = metrics({'Price_Native': 100, 'Price': 80, 'ATR_14': 4})
    assert result['ATR_Val'] == 5
    assert result['ATR_Pct'] == 5


def test_legacy_portfolio_recovers_atr_from_eur_ohlc_with_gaps():
    # Last 14 true ranges are 8 EUR (10 native), including overnight gaps.
    bars = [{'high': 80 + i * 6, 'low': 76 + i * 6, 'close': 78 + i * 6}
            for i in range(15)]
    result = metrics({'Price_Native': 202.5, 'Current_Price': 162,
                      'Chart_OHLC': bars})
    assert result['ATR_Val'] == 10
    assert result['ATR_Pct'] == pytest.approx(10 / 202.5 * 100, abs=0.005)


def test_valid_finviz_is_preserved():
    result = metrics({'Price_Native': 100, 'Finviz_ATR': 2,
                      'ATR_Native': 3, 'Vol_W': 4, 'Vol_M': 5})
    assert result['ATR_Val'] == 2
    assert result['ATR_Source'] == 'Finviz'
    assert result['Trail_Larg'] == 15


def range_history():
    # 16 days at 2%, four at 4%, last at 10%; not close-to-close returns.
    return [dict(date=(datetime.date(2026, 9, 1) + datetime.timedelta(days=i)).isoformat(),
                 high=100 + spread, low=100, close=101)
            for i, spread in enumerate([2] * 16 + [4] * 4 + [10])]


def test_missing_finviz_recovers_three_ranges_and_trails_from_history():
    result = metrics({'Price_Native': 100, 'ATR_Native': 3,
                      'Chart_OHLC': range_history(), 'Market_Data_Source': 'Yahoo Finance'})
    assert result.get('Vol_D') == 10
    assert result['Vol_W'] == 5.2
    assert result['Vol_M'] == pytest.approx(2.7619)
    # Daily range is descriptive, not a fourth input to existing trail formulas.
    assert result['Trail_Larg'] == 15.6
    assert result['Vol_W_Source'] == 'Calculat OHLC · Yahoo Finance'
    assert result['Vol_As_Of'] == '2026-09-21'


def test_history_ranges_are_currency_invariant():
    bars = [{**bar, **{key: bar[key] * 0.8 for key in ('high', 'low', 'close')}}
            for bar in range_history()]
    result = metrics({'Chart_OHLC': bars})
    assert result.get('Vol_D') == 10
    assert result['Vol_W'] == 5.2
    assert result['Vol_M'] == pytest.approx(2.7619)


def test_partial_finviz_preserves_real_value_and_labels_each_fallback():
    result = metrics({'Vol_W': 7, 'Vol_M': float('nan'), 'Chart_OHLC': range_history()})
    assert result['Vol_W'] == 7
    assert result.get('Vol_W_Source') == 'Finviz'
    assert result['Vol_M'] == pytest.approx(2.7619)
    assert result['Vol_M_Source'] == 'Calculat OHLC'


def test_history_requires_full_window_but_allows_a_genuine_zero():
    result = metrics({'Chart_OHLC': [dict(high=100, low=100, close=100)] * 5})
    assert result.get('Vol_D') == 0
    assert result['Vol_W'] == 0
    assert result['Vol_M'] is None


@pytest.mark.parametrize('bad_bar', [
    {'high': 99, 'low': 100, 'close': 100},
    {'high': 102, 'low': 0, 'close': 101},
    {'high': float('inf'), 'low': 100, 'close': 101},
    {}, None,
])
def test_invalid_bar_is_not_skipped_to_fill_a_window(bad_bar):
    bars = range_history()
    bars[-2] = bad_bar
    result = metrics({'Chart_OHLC': bars})
    assert result.get('Vol_D') == 10
    assert result['Vol_W'] is None
    assert result['Vol_M'] is None


@pytest.mark.parametrize('close', [None, float('nan'), 150])
def test_high_low_ranges_do_not_depend_on_close(close):
    # Some stored histories have an adjusted close outside unadjusted H/L.
    bars = [{**bar, 'close': close} for bar in range_history()]
    result = metrics({'Chart_OHLC': bars})
    assert result['Vol_D'] == 10
    assert result['Vol_W'] == 5.2
    assert result['Vol_M'] == pytest.approx(2.7619)


@pytest.mark.parametrize('mutation', ['duplicate', 'reversed'])
def test_ambiguous_session_order_does_not_generate_ranges(mutation):
    bars = range_history()
    if mutation == 'duplicate':
        bars[-2]['date'] = bars[-1]['date']
    else:
        bars.reverse()
    result = metrics({'Chart_OHLC': bars})
    assert result.get('Vol_D') is None
    assert result['Vol_W'] is None
    assert result['Vol_M'] is None


def test_foreign_listing_does_not_use_us_finviz_values():
    result = metrics({'Currency': 'RON', 'Price_Native': 100, 'ATR_Native': 3,
                      'Finviz_ATR': 60, 'Vol_W': 90, 'Vol_M': 80,
                      'Chart_OHLC': range_history()})
    assert result['ATR_Val'] == 3
    assert result['Vol_W'] == 5.2
    assert result['Vol_W_Source'] != 'Finviz'


def test_calculator_displays_history_ranges_and_clears_previous_values():
    source = (Path(__file__).resolve().parents[1] / 'market_scanner.py').read_text()
    js = source.split('function calcVolatility() {', 1)[1].split('// Track source tab', 1)[0]
    payload = metrics({'Price_Native': 100, 'ATR_Native': 3,
                       'Chart_OHLC': range_history()})
    script = '''
      const elements = {};
      const document = {getElementById: id => elements[id] ||= {innerText: '', value: '', style: {}}};
      const renderAdjustTable = () => {};
      const volData = DATA;
      function calcVolatility() {FUNCTION
      document.getElementById('vol-input').value = 'HISTORY';
      calcVolatility();
      const first = JSON.parse(JSON.stringify(elements));
      document.getElementById('vol-input').value = 'EMPTY';
      calcVolatility();
      console.log(JSON.stringify({first, last: elements}));
    '''.replace('DATA', json.dumps({'HISTORY': payload, 'EMPTY': metrics({})})).replace('FUNCTION', js)
    result = json.loads(subprocess.check_output(['node', '-e', script], text=True))
    assert result['first']['res-day']['innerText'] == '10.00%'
    assert result['first']['res-week']['innerText'] == '5.20%'
    assert result['first']['res-month']['innerText'] == '2.76%'
    assert 'Calculat OHLC' in result['first']['vol-data-note']['innerText']
    assert result['first']['stop-larg-sell']['innerText'] == '84.40'
    assert result['last']['res-day']['innerText'] == 'Indisponibil'
    assert result['last']['stop-larg-sell']['innerText'] == 'Indisponibil'


@pytest.mark.parametrize('item', [
    {}, {'Price_Native': 100, 'ATR_14': 4},
    {'Price_Native': 100, 'Chart_OHLC': [{'high': 3, 'low': 1, 'close': 2}]},
    {'Price_Native': 100, 'ATR_Native': float('inf'), 'Finviz_ATR': -2},
])
def test_missing_data_does_not_invent_zero_atr(item):
    result = metrics(item)
    assert result['ATR_Val'] is None
    assert result['ATR_Pct'] is None
    assert result['Trail_Larg'] == 0


def test_finviz_403_is_explicit_and_cached(monkeypatch, capsys):
    monkeypatch.setattr(market_data, '_finviz_cache', {})
    request = Mock(return_value=Mock(status_code=403))
    monkeypatch.setattr(market_data.requests, 'get', request)
    result = market_data.get_finviz_data('CLS')
    assert result['ATR'] is None
    assert result['Status'] == 'http_403'
    assert 'Finviz CLS: HTTP 403' in capsys.readouterr().out
    assert market_data.get_finviz_data('CLS') == result
    assert request.call_count == 1


def test_finviz_missing_table_is_not_silent(monkeypatch, capsys):
    monkeypatch.setattr(market_data, '_finviz_cache', {})
    monkeypatch.setattr(market_data.requests, 'get', Mock(return_value=Mock(
        status_code=200, text='<html><title>Empty</title></html>')))
    result = market_data.get_finviz_data('CLS')
    assert result['Status'] == 'missing_metrics'
    assert 'Finviz CLS' in capsys.readouterr().out


def test_dashboard_serializes_finite_fallback_for_both_lists():
    """Execute the generator's real volatility section without its AI/network work."""
    from volatility_metrics import volatility_payload
    from portfolio_identity import position_key, account_label
    source = Path(__file__).resolve().parents[1] / 'market_scanner.py'
    tree = ast.parse(source.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'generate_html_dashboard')

    def assigns(node, name):
        return isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets)

    start = next(i for i, n in enumerate(function.body) if assigns(n, 'vol_map'))
    end = next(i for i, n in enumerate(function.body) if assigns(n, 'vol_json'))
    scope = {'json': json, 'volatility_payload': volatility_payload,
             'position_key': position_key, 'account_label': account_label,
             'watchlist_df': pd.DataFrame([{'Ticker': 'WATCH', 'Price_Native': 100,
                 'Price': 80, 'ATR_14': 4, 'Finviz_ATR': float('nan')}]),
             'portfolio_df': pd.DataFrame([{'Symbol': 'HELD', 'Price_Native': 50,
                 'ATR_Native': 2, 'Finviz_ATR': None}])}
    exec(compile(ast.Module(body=function.body[start:end+1], type_ignores=[]),
                 '<dashboard-volatility>', 'exec'), scope)
    data = json.loads(scope['vol_json'])
    assert data['WATCH']['ATR_Val'] == 5
    assert data['HELD']['ATR_Val'] == 2
    assert data['WATCH']['Trail_Larg'] == 15
    assert data['HELD']['Trail_Larg'] == 12
    assert data['WATCH']['Vol_W'] is None
