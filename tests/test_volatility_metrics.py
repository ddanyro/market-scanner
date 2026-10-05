import json
import ast
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
