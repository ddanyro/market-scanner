import datetime
import json
import os
import tempfile
import types
import unittest
from unittest.mock import Mock

import ib_sync
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
    def test_only_romanian_stock_positions_are_selected_for_ro_sync(self):
        positions = [
            types.SimpleNamespace(
                position=10,
                contract=_contract('TLV', 'RON', 'BVB', 1),
            ),
            types.SimpleNamespace(
                position=5,
                contract=_contract('JPM', 'USD', 'SMART', 2),
            ),
            types.SimpleNamespace(
                position=0,
                contract=_contract('SNP', 'RON', 'BVB', 3),
            ),
        ]
        self.assertEqual(
            ib_tws_sync._romanian_position_symbols(positions),
            ['TLV.RO'],
        )

    def test_recent_romanian_tws_cache_skips_reconnection(self):
        fetched_at = datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'tws_instruments.json')
            with open(path, 'w', encoding='utf-8') as handle:
                json.dump({
                    'instruments': {
                        'TLV.RO': {
                            'symbol': 'TLV.RO',
                            'market': 'România / BVB',
                            'position_held_in_ibkr': True,
                            'fetched_at': fetched_at,
                            'bars': [{'date': '2026-07-30'}],
                        },
                    },
                }, handle)
            result = ib_tws_sync.sync_romanian_position_instruments(
                output_file=path, max_age_hours=1
            )
        self.assertTrue(result)

    def test_recent_tws_positions_skip_flex_when_disabled(self):
        previous_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                with open('tws_positions.csv', 'w', encoding='utf-8') as handle:
                    handle.write(
                        'Symbol,Shares,Buy_Price,Current_Price,Currency\n'
                        'JPM,4,300,320,USD\n'
                    )
                request = Mock(
                    side_effect=AssertionError('Flex nu trebuie apelat')
                )
                original_request = ib_sync.requests.get
                ib_sync.requests.get = request
                try:
                    result = ib_sync.sync_ibkr(allow_flex=False)
                finally:
                    ib_sync.requests.get = original_request
            finally:
                os.chdir(previous_cwd)

        self.assertTrue(result)
        request.assert_not_called()

    def test_dynamic_bvb_equity_is_data_only_and_tradeville_executable(self):
        instruments = ib_tws_sync.build_research_instruments(
            ['ALR.RO', 'TVBETETF.RO']
        )

        self.assertIn('ALR.RO', instruments)
        self.assertEqual(instruments['ALR.RO']['query_symbol'], 'ALR')
        self.assertEqual(instruments['ALR.RO']['currency'], 'RON')
        self.assertEqual(
            instruments['ALR.RO']['execution_brokers'], ['Tradeville']
        )
        self.assertEqual(
            instruments['ALR.RO']['instrument_type'], 'Equity'
        )
        self.assertEqual(
            list(instruments).count('TVBETETF.RO'), 1
        )

    def test_contract_resolution_rejects_unrelated_bond_match(self):
        bond = types.SimpleNamespace(
            conId=303,
            symbol='TALD',
            localSymbol='TALD',
            secType='BOND',
            currency='USD',
            exchange='SMART',
            primaryExchange='',
        )
        ib = Mock()
        ib.reqMatchingSymbols.return_value = [
            types.SimpleNamespace(contract=bond)
        ]
        ib.qualifyContracts.return_value = []
        ib.reqContractDetails.return_value = []
        config = ib_tws_sync.build_research_instruments(
            ['TALD.RO']
        )['TALD.RO']

        with self.assertRaises(ValueError):
            ib_tws_sync._resolve_research_contract(ib, config)

        fallback = ib.reqContractDetails.call_args.args[0]
        self.assertEqual(fallback.symbol, 'TALD')
        self.assertEqual(fallback.currency, 'RON')

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
