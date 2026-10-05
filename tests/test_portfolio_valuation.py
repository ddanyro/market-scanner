"""Regressions for metadata quotes overriding actual broker position prices."""
import datetime
import json

import pandas as pd
import pytest

import market_scanner as scanner


@pytest.fixture
def pricing_environment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    old = (datetime.datetime.now(datetime.timezone.utc)
           - datetime.timedelta(days=60)).isoformat()
    instrument = {
        'symbol': 'TVBETETF.RO', 'aliases': ['TVBETETF.RO', 'TVBETETF'],
        'instrument_type': 'ETF', 'fetched_at': old,
        'contract': {'currency': 'RON', 'long_name': 'ETF BET'},
        'market_data': {'close': 60.8, 'as_of': old[:10]},
        'bars': [{'date': old[:10], 'open': 60.8, 'high': 61,
                  'low': 60, 'close': 60.8, 'volume': 1000}],
    }
    (tmp_path / 'tws_instruments.json').write_text(json.dumps({
        'instruments': {'TVBETETF.RO': instrument}}))
    dates = pd.bdate_range(end='2026-10-05', periods=220)
    history = pd.DataFrame({
        'Open': 57.3, 'High': 57.6, 'Low': 57.1,
        'Close': 57.3, 'Volume': 1000,
    }, index=dates)
    monkeypatch.setattr(scanner, '_download_yahoo_history',
                        lambda *args, **kwargs: history.copy())
    monkeypatch.setattr(scanner.market_data, 'get_finviz_data', lambda *args: {})
    monkeypatch.setattr(scanner, '_get_yahoo_info', lambda *args, **kwargs: {})
    monkeypatch.setattr(scanner, 'get_earnings_snapshot', lambda *args: {})
    monkeypatch.setattr(scanner.time, 'sleep', lambda _: None)
    return history


def test_expired_contract_metadata_cannot_supply_a_market_quote(pricing_environment):
    history, _, instrument, _ = scanner._load_analysis_history('TVBETETF', 'TVBETETF')
    assert history['Close'].iloc[-1] == 57.3
    assert scanner._tws_instrument_market_price(instrument) is None
    assert instrument['contract']['long_name'] == 'ETF BET'


@pytest.mark.parametrize('empty_history', [False, True])
@pytest.mark.parametrize('account,shares,cost,profit,pct', [
    ('Personal', 555, 57.458290100097656, -5.02, -0.08),
    ('Company', 1254, 56.83564758300781, 134.99, 1.01),
])
def test_tradeville_profit_uses_own_snapshot_price(
    pricing_environment, monkeypatch, empty_history, account, shares, cost, profit, pct,
):
    if empty_history:
        monkeypatch.setattr(scanner, '_download_yahoo_history',
                            lambda *args, **kwargs: pd.DataFrame())
    row = {'symbol': 'TVBETETF', 'broker': 'Tradeville', 'account': account,
           'account_id': account, 'shares': shares, 'buy_price': cost,
           'currency': 'RON', 'current_price': 57.41,
           'snapshot_timestamp': '2026-10-05T14:47:09.661Z'}
    result = scanner.process_portfolio_ticker(
        row, 18, {'RON': 0.18743088596010254, 'USD': 0.8921, 'EUR': 1})
    assert result is not None
    assert result['Price_Native'] == 57.41
    assert result['Profit'] == profit
    assert result['Profit_Pct'] == pct
    assert result['Valuation_Source'] == 'Tradeville snapshot'
    assert result['Valuation_As_Of'] == row['snapshot_timestamp']


def test_final_quote_refresh_preserves_tradeville_valuation(monkeypatch):
    monkeypatch.setattr(scanner, '_prefetch_ibkr_mcp_market_data',
                        lambda *args, **kwargs: {'updated': 1, 'updated_symbols': ['TVBETETF']})
    monkeypatch.setattr(scanner, '_load_mcp_market_instrument', lambda _: {
        'market_data': {'close': 60.8},
    })
    position = {'Symbol': 'TVBETETF', 'Broker': 'Tradeville',
                'Shares': 555, 'Currency': 'RON', 'Buy_Price': 10.77,
                'Investment': 5977.05, 'Price_Native': 57.41,
                'Current_Price': 10.76, 'Current_Value': 5972.03,
                'Profit': -5.02, 'Profit_Pct': -0.08,
                'Valuation_Source': 'Tradeville snapshot',
                'Valuation_As_Of': '2026-10-05T14:47:09.661Z'}
    result = scanner._refresh_portfolio_quotes_before_save(
        {'portfolio': [position]}, {'RON': 0.18743088596010254})
    assert result['portfolio'][0] == position


@pytest.mark.parametrize('price', [None, 0, -1, float('nan'), float('inf')])
def test_invalid_tradeville_price_falls_back_to_history_not_expired_metadata(
    pricing_environment, price,
):
    result = scanner.process_portfolio_ticker(
        {'symbol': 'TVBETETF', 'broker': 'Tradeville', 'shares': 100,
         'buy_price': 57, 'currency': 'RON', 'current_price': price},
        18, {'RON': 0.2, 'USD': 0.9})
    assert result['Price_Native'] == 57.3
    assert result['Profit'] == 6
    assert result.get('Valuation_Source') != 'Tradeville snapshot'


def test_ibkr_position_does_not_treat_csv_price_as_tradeville_authority(pricing_environment):
    result = scanner.process_portfolio_ticker(
        {'symbol': 'TVBETETF', 'broker': 'IBKR', 'shares': 100,
         'buy_price': 57, 'currency': 'RON', 'current_price': 60.8},
        18, {'RON': 0.2, 'USD': 0.9})
    assert result['Price_Native'] == 57.3
    assert result['Profit'] == 6
    assert result.get('Valuation_Source') != 'Tradeville snapshot'


@pytest.mark.parametrize('currency,rate', [('RON', 0.2), ('USD', 0.9)])
def test_unrelated_foreign_listing_cannot_change_tradeville_snapshot_currency(
    pricing_environment, monkeypatch, currency, rate,
):
    monkeypatch.setattr(scanner, '_download_yahoo_history',
                        lambda symbol, **kwargs: pricing_environment.copy()
                        if symbol.endswith('.DE') else pd.DataFrame())
    result = scanner.process_portfolio_ticker(
        {'symbol': 'TVBETETF', 'broker': 'Tradeville', 'shares': 100,
         'buy_price': 57, 'currency': currency, 'current_price': 57.41},
        18, {'RON': 0.2, 'USD': 0.9})
    assert result['Currency'] == currency
    assert result['Price_Native'] == 57.41
    assert result['Profit'] == pytest.approx(41 * rate)
