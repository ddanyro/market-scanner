import datetime
import json
import os
import tempfile
import types
import unittest
from unittest.mock import Mock

import ib_tws_sync


def _contract(symbol, currency, exchange, con_id):
    return types.SimpleNamespace(
        conId=con_id,
        symbol=symbol,
        localSymbol=symbol,
        secType='STK',
        currency=currency,
        exchange=exchange,
        primaryExchange=exchange,
        tradingClass=symbol,
    )


def _detail(contract, long_name):
    return types.SimpleNamespace(
        contract=contract,
        secIdList=[
            types.SimpleNamespace(tag='ISIN', value=f'ISIN-{contract.symbol}')
        ],
        longName=long_name,
        marketName=contract.exchange,
        industry='Funds',
        category='ETF',
        subcategory='Equity',
        stockType='ETF',
        validExchanges=contract.exchange,
        timeZoneId='Europe/Bucharest',
        tradingHours='',
        liquidHours='',
    )


def _bars():
    start = datetime.date(2026, 1, 2)
    return [
        types.SimpleNamespace(
            date=start + datetime.timedelta(days=index),
            open=10 + index / 10,
            high=10.5 + index / 10,
            low=9.5 + index / 10,
            close=10.2 + index / 10,
            volume=1000 + index,
        )
        for index in range(90)
    ]


class TestTwsInstrumentSync(unittest.TestCase):
    def test_tvbetetf_uses_ibkr_only_as_data_provider(self):
        lqq_contract = _contract('LQQ', 'EUR', 'SBF', 101)
        tvbet_contract = _contract('TVBETETF', 'RON', 'BVB', 202)
        contracts = {'LQQ': lqq_contract, 'TVBETETF': tvbet_contract}
        details = {
            101: _detail(lqq_contract, 'Amundi Nasdaq-100 Daily 2x'),
            202: _detail(tvbet_contract, 'ETF BET Patria-Tradeville'),
        }
        ib = Mock()
        ib.reqMatchingSymbols.side_effect = lambda symbol: [
            types.SimpleNamespace(contract=contracts[symbol])
        ]
        ib.reqContractDetails.side_effect = lambda contract: [
            details[contract.conId]
        ]
        ib.reqHistoricalData.return_value = _bars()
        ib.reqTickers.return_value = [
            types.SimpleNamespace(
                marketPrice=lambda: 12.34,
                bid=12.33,
                ask=12.35,
                last=12.34,
                close=12.20,
                volume=5000,
            )
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'tws_instruments.json')
            payload = ib_tws_sync.fetch_research_instruments(
                ib, output_file=path
            )

        tvbet = payload['instruments']['TVBETETF.RO']
        lqq = payload['instruments']['LQQ.PA']
        self.assertEqual(tvbet['data_broker'], 'IBKR')
        self.assertTrue(tvbet['ibkr_data_only'])
        self.assertEqual(tvbet['execution_brokers'], ['Tradeville'])
        self.assertEqual(tvbet['contract']['currency'], 'RON')
        self.assertEqual(len(tvbet['bars']), 90)
        self.assertFalse(tvbet['corporate_fundamentals_applicable'])
        self.assertFalse(lqq['ibkr_data_only'])
        self.assertEqual(lqq['execution_brokers'], ['IBKR', 'Tradeville'])
        ib.reqTickers.assert_not_called()

    def test_last_valid_instrument_cache_survives_tws_error(self):
        cached_at = '2026-07-28T06:00:00+00:00'
        cached_entry = {
            'symbol': 'TVBETETF.RO',
            'fetched_at': cached_at,
            'execution_brokers': ['Tradeville'],
            'bars': [{
                'date': '2026-07-27',
                'open': 60,
                'high': 62,
                'low': 59,
                'close': 61,
                'volume': 1000,
            }],
        }
        ib = Mock()
        ib.reqMatchingSymbols.side_effect = RuntimeError('TWS offline')

        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'tws_instruments.json')
            with open(path, 'w', encoding='utf-8') as handle:
                json.dump({
                    'fetched_at': cached_at,
                    'instruments': {'TVBETETF.RO': cached_entry},
                }, handle)
            payload = ib_tws_sync.fetch_research_instruments(
                ib,
                output_file=path,
                instruments={
                    'TVBETETF.RO': (
                        ib_tws_sync.RESEARCH_INSTRUMENTS['TVBETETF.RO']
                    )
                },
            )

        result = payload['instruments']['TVBETETF.RO']
        self.assertTrue(result['cache_fallback'])
        self.assertEqual(result['fetched_at'], cached_at)
        self.assertEqual(result['execution_brokers'], ['Tradeville'])


if __name__ == '__main__':
    unittest.main()
