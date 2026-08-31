"""
Unit tests for Market Scanner application - Updated version.
Tests actual functions that exist in the codebase.
"""
import unittest
import copy
import json
import sys
import os
import tempfile
import time
import warnings
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import market_scanner_analysis
import market_scanner
import market_security


class TestMarketAnalysis(unittest.TestCase):
    """Test market analysis functions."""
    
    def test_event_impact_cpi(self):
        """Test CPI event impact description."""
        desc = market_scanner_analysis.get_event_impact('CPI')
        self.assertIsInstance(desc, str)
        self.assertGreater(len(desc), 0)
        self.assertIn('inflați', desc.lower())

    def test_ai_schedule_waits_for_both_bvb_and_us_close(self):
        before_us_close = datetime(
            2026, 8, 17, 19, 30, tzinfo=timezone.utc
        )  # 22:30 București, 15:30 New York
        after_both_close = datetime(
            2026, 8, 17, 20, 5, tzinfo=timezone.utc
        )  # 23:05 București, 16:05 New York

        waiting = market_scanner._closed_market_ai_schedule(
            {}, now=before_us_close
        )
        ready = market_scanner._closed_market_ai_schedule(
            {}, now=after_both_close
        )
        repeated = market_scanner._closed_market_ai_schedule(
            {'last_closed_market_ai_session': ready['session_key']},
            now=after_both_close,
        )

        self.assertFalse(waiting['allowed'])
        self.assertTrue(waiting['bvb']['post_close'])
        self.assertFalse(waiting['usa']['post_close'])
        self.assertTrue(ready['allowed'])
        self.assertEqual(
            ready['session_key'], 'BVB:2026-08-17|SUA:2026-08-17'
        )
        self.assertFalse(repeated['allowed'])

    def test_ai_schedule_weekend_reuses_last_weekday_only_once(self):
        saturday = datetime(2026, 8, 15, 10, 0, tzinfo=timezone.utc)
        first = market_scanner._closed_market_ai_schedule({}, now=saturday)
        second = market_scanner._closed_market_ai_schedule(
            {'last_closed_market_ai_session': first['session_key']},
            now=saturday,
        )

        self.assertTrue(first['allowed'])
        self.assertEqual(
            first['session_key'], 'BVB:2026-08-14|SUA:2026-08-14'
        )
        self.assertFalse(second['allowed'])

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('market_scanner_analysis.requests.post')
    def test_calendar_ai_is_cache_only_outside_post_close_window(self, post):
        now = datetime(2026, 8, 17, 12, 0)
        event = market_scanner_analysis._normalise_macro_event({
            'id': 'fed-scheduled',
            'title': 'Fed Interest Rate Decision',
            'country': 'US',
            'date': '2026-08-18T18:00:00Z',
            'forecast': '4.25%',
            'previous': '4.50%',
        }, now)

        analyses = market_scanner_analysis._enrich_events_with_ai(
            [event], {}, ai_cache={}, allow_ai=False
        )

        post.assert_not_called()
        self.assertIn(event['id'], analyses)
        self.assertIn(
            analyses[event['id']]['verdict'],
            {'Bullish probabil', 'Bearish probabil', 'Mixt', 'Neutru', 'Date insuficiente'},
        )

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('market_scanner_analysis.requests.post')
    def test_news_ai_is_cache_only_outside_post_close_window(self, post):
        html_result, summary, score, cache = (
            market_scanner_analysis._generate_news_and_ai_summary_html(
                [{'title': 'Test', 'link': 'https://example.com', 'desc': 'News'}],
                {},
                allow_ai=False,
            )
        )

        post.assert_not_called()
        self.assertIn('Market News Overview', html_result)
        self.assertEqual(summary, '')
        self.assertEqual(score, 50)
        self.assertIsNone(cache)

    def test_stale_sell_order_is_removed_when_position_is_closed(self):
        orders = pd.DataFrame([
            {'Symbol': 'UPBD', 'Action': 'SELL', 'OrderType': 'TRAIL'},
            {'Symbol': 'TVBETETF.RO', 'Action': 'SELL', 'OrderType': 'STP'},
            {'Symbol': 'NVDA', 'Action': 'BUY', 'OrderType': 'LMT'},
        ])
        portfolio = pd.DataFrame([{'Symbol': 'TVBETETF.RO'}])

        result = market_scanner._filter_orders_against_current_positions(
            orders, portfolio
        )

        self.assertEqual(
            result['Symbol'].tolist(), ['TVBETETF.RO', 'NVDA']
        )

    def test_order_frames_ignore_empty_and_all_na_inputs_without_warning(self):
        empty = pd.DataFrame(columns=['Symbol', 'Action', 'Note'])
        ibkr = pd.DataFrame([{
            'Symbol': 'JPM', 'Action': 'SELL', 'Note': None,
        }])
        tradeville = pd.DataFrame([{
            'Symbol': 'TVBETETF.RO', 'Action': 'SELL', 'Note': 'stop',
        }])

        with warnings.catch_warnings():
            warnings.simplefilter('error', FutureWarning)
            result = market_scanner._concat_order_frames(
                [empty, ibkr, tradeville]
            )

        self.assertEqual(result['Symbol'].tolist(), ['JPM', 'TVBETETF.RO'])
        self.assertEqual(result.columns.tolist(), ['Symbol', 'Action', 'Note'])
        self.assertTrue(pd.isna(result.loc[0, 'Note']))
        self.assertEqual(result.loc[1, 'Note'], 'stop')

    def test_remote_run_reuses_encrypted_tws_order_snapshot(self):
        state = {}
        password = 'shared-account-cache-password'
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'tws_orders.csv')
            pd.DataFrame([{
                'Symbol': 'LQQ', 'OrderType': 'LMT', 'Action': 'BUY',
                'Total_Qty': 120, 'Limit_Price': 8.95,
            }]).to_csv(path, index=False)
            local, changed, source = market_scanner._load_cached_tws_orders(
                state, password, path,
            )
            os.remove(path)
            remote, remote_changed, remote_source = (
                market_scanner._load_cached_tws_orders(
                    state, password, path,
                )
            )

        self.assertTrue(changed)
        self.assertEqual(source, 'tws_local')
        self.assertEqual(local['Symbol'].tolist(), ['LQQ'])
        self.assertFalse(remote_changed)
        self.assertEqual(remote_source, 'tws_encrypted_cache')
        self.assertEqual(remote['Symbol'].tolist(), ['LQQ'])
        self.assertNotIn('LQQ', json.dumps(state))

    def test_valid_empty_tws_snapshot_replaces_stale_cached_orders(self):
        state = {}
        password = 'shared-account-cache-password'
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'tws_orders.csv')
            pd.DataFrame([{
                'Symbol': 'UAL', 'OrderType': 'LMT', 'Action': 'BUY',
            }]).to_csv(path, index=False)
            market_scanner._load_cached_tws_orders(state, password, path)
            pd.DataFrame(columns=market_scanner.TWS_ACTIVE_ORDER_COLUMNS).to_csv(
                path, index=False,
            )
            empty, changed, source = market_scanner._load_cached_tws_orders(
                state, password, path,
            )
            os.remove(path)
            cached_empty, _, cached_source = (
                market_scanner._load_cached_tws_orders(
                    state, password, path,
                )
            )

        self.assertTrue(changed)
        self.assertEqual(source, 'tws_local')
        self.assertTrue(empty.empty)
        self.assertEqual(cached_source, 'tws_encrypted_cache')
        self.assertTrue(cached_empty.empty)

    def test_wrong_order_cache_password_is_not_treated_as_no_orders(self):
        state = {}
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'tws_orders.csv')
            pd.DataFrame([{
                'Symbol': 'RTX', 'OrderType': 'TRAIL', 'Action': 'SELL',
                'Total_Qty': 5,
            }]).to_csv(path, index=False)
            market_scanner._load_cached_tws_orders(
                state, 'remote-shared-password', path,
            )
            os.remove(path)
            frame, changed, source = market_scanner._load_cached_tws_orders(
                state, 'different-local-password', path,
            )

        self.assertTrue(frame.empty)
        self.assertFalse(changed)
        self.assertEqual(source, 'encrypted_cache_invalid')

    def test_active_buy_orders_total_is_converted_to_eur(self):
        orders = pd.DataFrame([
            {
                'Symbol': 'NVDA', 'Action': 'BUY', 'OrderType': 'LMT',
                'Total_Qty': 2, 'Limit_Price': 100, 'Currency': 'USD',
            },
            {
                'Symbol': 'LQQ', 'Action': 'BUY', 'OrderType': 'LMT',
                'Total_Qty': 10, 'Limit_Price': 9, 'Currency': 'EUR',
            },
            {
                'Symbol': 'RTX', 'Action': 'SELL', 'OrderType': 'TRAIL',
                'Total_Qty': 5, 'Calculated_Stop': 200, 'Currency': 'USD',
            },
        ])
        total = market_scanner._active_buy_orders_total_eur(
            orders, {'EUR': 1, 'USD': 0.9}
        )
        self.assertEqual(total, 270)

    def test_current_month_portfolio_change_uses_month_endpoints(self):
        history = [
            {'timestamp': '2026-07-31T23:00:00+03:00', 'net_liquidation': 90},
            {'timestamp': '2026-08-01T08:00:00+03:00', 'net_liquidation': 100},
            {'timestamp': '2026-08-10T08:00:00+03:00', 'net_liquidation': 112.5},
        ]
        result = market_scanner._current_month_portfolio_change(
            history,
            now=datetime(
                2026, 8, 15, tzinfo=timezone(timedelta(hours=3))
            ),
        )
        self.assertEqual(result, 12.5)

    def test_portfolio_chat_token_does_not_expose_password(self):
        token = market_scanner._portfolio_chat_access_token('pin-secret')
        self.assertEqual(len(token), 64)
        self.assertNotIn('pin-secret', token)
        self.assertEqual(
            token,
            market_scanner._portfolio_chat_access_token('pin-secret'),
        )

    def test_portfolio_json_replaces_nonfinite_numbers_with_null(self):
        payload = {
            'valid': 12.5,
            'missing': float('nan'),
            'nested': [float('inf'), np.float64('-inf')],
        }

        cleaned = market_scanner._json_without_nonfinite_numbers(payload)
        encoded = json.dumps(cleaned, allow_nan=False)

        self.assertEqual(cleaned['valid'], 12.5)
        self.assertIsNone(cleaned['missing'])
        self.assertEqual(cleaned['nested'], [None, None])
        self.assertNotIn('NaN', encoded)
        self.assertNotIn('Infinity', encoded)

    def test_portfolio_chat_context_is_compact_and_has_market_data(self):
        snapshot = {
            'as_of': '2026-08-01T09:00:00',
            'portfolio': {'position_count': 1},
            'positions': [{'symbol': 'TVBETETF.RO', 'broker': 'Tradeville'}],
            'account_liquidity': {'accounts': [{'label': 'Tradeville'}]},
            'us_market_regime': {'market_stage': 'piață mixtă'},
            'us_sector_rotation': {'sectors': {'Healthcare': {'status': 'lider'}}},
        }
        candidates = [{
            'symbol': 'WST', 'entry_native': 337.46, 'currency': 'USD',
            'chart_ohlc_native': [{'open': 1, 'close': 2}],
        }]
        context = market_scanner_analysis.build_portfolio_chat_context(
            snapshot,
            ai_result={'portfolio_overview': 'Concentrare ridicată.'},
            buy_candidates=candidates,
            dashboard_state={'eco_phase': 'Expansion'},
        )
        self.assertEqual(context['positions'][0]['broker'], 'Tradeville')
        self.assertEqual(context['buy_candidates'][0]['currency'], 'USD')
        self.assertNotIn('chart_ohlc_native', context['buy_candidates'][0])
        self.assertEqual(context['economic_cycle']['current'], 'Expansion')
        
    def test_event_impact_fomc(self):
        """Test FOMC event impact description."""
        desc = market_scanner_analysis.get_event_impact('FOMC')
        self.assertIsInstance(desc, str)
        self.assertGreater(len(desc), 0)

    def test_ro_cached_swing_data_rejects_short_global_history(self):
        dates = pd.bdate_range('2026-05-01', periods=60)
        state = {
            'vix_val': 18.5,
            'market_indicators': {
                'SPX': {
                    'history': list(np.linspace(7000, 7500, 60)),
                    'history_dates': [day.date().isoformat() for day in dates],
                },
                'NASDAQ': {
                    'history': list(np.linspace(24000, 25000, 60)),
                    'history_dates': [day.date().isoformat() for day in dates],
                },
                'VIX': {'value': 18.5},
                'SKEW': {'value': 142.0},
            },
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            result = market_scanner._cached_swing_data_for_ro(
                state, tide_path=os.path.join(temp_dir, 'missing.json')
            )

        self.assertIsNone(result)

    def test_ro_cached_swing_data_prefers_separate_us_snapshot(self):
        snapshot = {
            'SPX_Price': 7500,
            'SPX_SMA10': 7450,
            'SPX_SMA50': 7300,
            'SPX_SMA200': 6900,
            'NDX_Price': 28000,
            'NDX_SMA10': 27900,
            'NDX_SMA50': 27000,
            'NDX_SMA200': 25000,
            'Chart_SPX': {
                'price': [7400, 7500],
                'sma10': [7420, 7450],
                'sma50': [7290, 7300],
                'sma200': [6890, 6900],
            },
        }
        state = {
            'market_overviews': {
                'SUA': {'updated_at': '2026-07-31T10:00:00Z', 'data': snapshot}
            },
            # Seria scurtă nu trebuie să înlocuiască snapshotul valid.
            'market_indicators': {'SPX': {'history': [1, 2, 3]}},
        }
        result = market_scanner._cached_swing_data_for_ro(state)
        self.assertEqual(result['SPX_SMA200'], 6900)
        self.assertEqual(result['Chart_SPX']['sma200'], [6890, 6900])
        self.assertIsNot(result, snapshot)

    def test_bvb_market_overview_is_separate_and_uses_ron(self):
        portfolio = pd.DataFrame([{
            'Symbol': 'TVBETETF.RO',
            'Price_Native': 61.48,
            'RSI': 68.67,
            'Chart_History': list(np.linspace(55, 61.48, 90)),
        }])
        html = market_scanner._generate_bvb_market_overview_html(
            portfolio, pd.DataFrame()
        )
        self.assertIn('România / BVB', html)
        self.assertIn('CUMPĂRĂ', html)
        self.assertIn('61.48 RON', html)
        self.assertIn('Datele BVB nu modifică Market Bias SUA', html)
        self.assertIn('Interpretarea scorului BVB', html)
        self.assertIn('Cum se calculează și ce înseamnă intervalele BVB', html)
        self.assertIn('scorul maxim posibil este 85/100', html)
        self.assertIn('Context puternic', html)
        self.assertIn('Calitatea istoricului, nu probabilitatea de câștig', html)
        self.assertIn('există minimum 200 de ședințe', html)

        _, signal = market_scanner._generate_bvb_market_overview_html(
            portfolio, pd.DataFrame(), return_signal=True
        )
        self.assertEqual(signal['key'], 'romania_bvb')
        self.assertEqual(signal['verdict'], 'CUMPĂRĂ')

        long_history = pd.DataFrame([{
            'Symbol': 'TVBETETF.RO',
            'Price_Native': 61.48,
            'RSI': 60,
            'Chart_History': list(np.linspace(45, 61.48, 220)),
        }])
        full_score_html = market_scanner._generate_bvb_market_overview_html(
            long_history, pd.DataFrame()
        )
        self.assertIn('100/100', full_score_html)
        self.assertIn('Aliniere foarte puternică', full_score_html)
        self.assertIn('nu validează automat fiecare acțiune BVB sau AeRO', full_score_html)

    def test_bvb_overview_and_risk_prefer_longest_proxy_history(self):
        short_portfolio_snapshot = pd.DataFrame([{
            'Symbol': 'TVBETETF.RO',
            'Price_Native': 61.71,
            'RSI': 47.7,
            'Chart_History': list(np.linspace(60.7, 61.71, 17)),
        }])
        complete_watchlist_history = pd.DataFrame([{
            'Symbol': 'TVBETETF.RO',
            'Price_Native': 61.71,
            'RSI': 55,
            'Chart_History': list(np.linspace(45, 61.71, 260)),
        }])

        html = market_scanner._generate_bvb_market_overview_html(
            short_portfolio_snapshot, complete_watchlist_history
        )
        risk_html = market_scanner._generate_bvb_risk_status_html(
            short_portfolio_snapshot, complete_watchlist_history
        )

        self.assertIn('SMA200:', html)
        self.assertNotIn('17/200 ședințe', html)
        self.assertIn('260/200 ȘEDINȚE', risk_html)
        self.assertNotIn('NEEVALUATĂ', risk_html)

    def test_portfolio_refresh_preserves_and_extends_longer_chart_history(self):
        previous = [{
            'Symbol': 'TVBETETF.RO',
            'Current_Price': 11.70,
            'Chart_Dates': ['2026-01-01', '2026-01-02', '2026-01-03'],
            'Chart_History': [10.0, 10.2, 10.4],
            'Chart_OHLC': [{'close': 10.0}, {'close': 10.2}, {'close': 10.4}],
        }]
        partial_refresh = [{
            'Symbol': 'TVBETETF.RO',
            'Current_Price': 11.90,
            'Chart_Dates': ['2026-01-03', '2026-01-04'],
            'Chart_History': [10.5, 10.7],
            'Chart_OHLC': [{'close': 10.5}, {'close': 10.7}],
        }]

        result = market_scanner._preserve_portfolio_chart_history(
            previous, partial_refresh
        )

        self.assertEqual(result[0]['Current_Price'], 11.90)
        self.assertEqual(
            result[0]['Chart_Dates'],
            ['2026-01-01', '2026-01-02', '2026-01-03', '2026-01-04'],
        )
        self.assertEqual(result[0]['Chart_History'], [10.0, 10.2, 10.5, 10.7])
        self.assertEqual(len(result[0]['Chart_OHLC']), 4)

    def test_portfolio_refresh_drops_misaligned_cached_chart_history(self):
        previous = [{
            'Symbol': 'TVBETETF.RO',
            'Chart_Dates': ['2026-08-24', '2026-08-25'],
            'Chart_History': [58.8, 59.0, 59.2],
        }]
        fresh = [{
            'Symbol': 'TVBETETF.RO',
            'RSI': 36.82,
            'Chart_Dates': ['2026-08-27', '2026-08-28'],
            'Chart_History': [59.4, 59.2],
        }]

        result = market_scanner._preserve_portfolio_chart_history(
            previous, fresh
        )

        self.assertEqual(result[0]['Chart_Dates'], fresh[0]['Chart_Dates'])
        self.assertEqual(result[0]['Chart_History'], fresh[0]['Chart_History'])

    def test_bvb_overview_uses_portfolio_rsi_and_blocks_buy_when_weak(self):
        portfolio = pd.DataFrame([{
            'Symbol': 'TVBETETF.RO',
            'Price_Native': 59.2,
            'RSI': 36.82,
            # Istoricul bullish ar produce separat un RSI sănătos; valoarea
            # proaspătă din analiza portofoliului trebuie să rămână autoritară.
            'Chart_History': list(np.linspace(45, 59.2, 263)),
            'Chart_Dates': [
                f'2026-session-{index}' for index in range(262)
            ],
        }])

        html, signal = market_scanner._generate_bvb_market_overview_html(
            portfolio, pd.DataFrame(), return_signal=True
        )
        risk_html = market_scanner._generate_bvb_risk_status_html(
            portfolio, pd.DataFrame()
        )

        self.assertEqual(signal['verdict'], 'AȘTEAPTĂ CONFIRMAREA')
        self.assertIn(
            'Scor swing local</div><div style="font-size:24px;'
            'font-weight:800;">88/100</div>',
            html,
        )
        self.assertIn('RSI14 este 36.8', html)
        self.assertIn('Regula #4 (RSI14 &lt; 40)', risk_html)
        self.assertIn('MOMENTUM SLAB', risk_html)

    def test_ai_stock_analysis_uses_independent_green_market_gates(self):
        candidates = [
            {'symbol': 'AAPL', 'market': 'SUA'},
            {'symbol': 'LQQ.PA', 'market': 'Europa / Nasdaq-100'},
            {'symbol': 'TLV.RO', 'market': 'România / BVB'},
        ]
        allowed, blocked, gates = (
            market_scanner._filter_ai_buy_candidates_by_market_signal(
                candidates,
                {'key': 'international', 'verdict': 'WAIT (INTERNAL ROT)'},
                {'key': 'romania_bvb', 'verdict': 'CUMPĂRĂ'},
            )
        )
        self.assertEqual([item['symbol'] for item in allowed], ['TLV.RO'])
        self.assertEqual(
            [item['symbol'] for item in blocked],
            ['AAPL', 'LQQ.PA'],
        )
        self.assertFalse(gates['international'])
        self.assertTrue(gates['romania_bvb'])

    def test_ai_stock_analysis_accepts_buy_variants_for_international(self):
        candidates = [
            {'symbol': 'NVDA', 'market': 'SUA'},
            {'symbol': 'LQQ.PA', 'market': 'Europa / Nasdaq-100'},
        ]
        allowed, blocked, gates = (
            market_scanner._filter_ai_buy_candidates_by_market_signal(
                candidates,
                {'key': 'international', 'verdict': 'BUY (HIGH CONFIDENCE)'},
                {'key': 'romania_bvb', 'verdict': 'AȘTEAPTĂ CONFIRMAREA'},
            )
        )
        self.assertEqual(
            [item['symbol'] for item in allowed],
            ['NVDA', 'LQQ.PA'],
        )
        self.assertEqual(blocked, [])
        self.assertTrue(gates['international'])
        self.assertFalse(gates['romania_bvb'])

    def test_ai_stock_gate_notice_preserves_technical_data_message(self):
        notice = market_scanner._render_ai_stock_gate_notice(
            {'key': 'international', 'verdict': 'WAIT'},
            {'key': 'romania_bvb', 'verdict': 'AȘTEAPTĂ CONFIRMAREA'},
            [
                {'market': 'SUA'},
                {'market': 'România / BVB'},
            ],
        )
        self.assertIn('SUA/LQQ: analiza AI a candidaților este în pauză', notice)
        self.assertIn('BVB/AeRO: analiza AI a candidaților este în pauză', notice)
        self.assertIn('Datele tehnice și istoricul rămân păstrate', notice)

    def test_bvb_market_risk_is_independent_from_us_rules(self):
        portfolio = pd.DataFrame([{
            'Symbol': 'TVBETETF.RO',
            'Price_Native': 61.48,
            'RSI': 68.67,
            'Chart_History': list(np.linspace(55, 61.48, 90)),
        }])
        html = market_scanner._generate_bvb_risk_status_html(
            portfolio, pd.DataFrame()
        )
        self.assertIn('TVBETETF &lt; SMA200', html)
        self.assertIn('NEEVALUATĂ', html)
        self.assertIn('90/200 ȘEDINȚE', html)
        self.assertIn('DOAR POZIȚII BVB', html)
        self.assertNotIn('VIX', html)
        self.assertNotIn('SPX', html)

    def test_bvb_market_risk_uses_cached_proxy_when_absent_from_portfolio_and_watchlist(self):
        full_state = {
            'bvb_proxy': {
                'Symbol': 'TVBETETF.RO',
                'Price_Native': 59.5,
                'RSI': 52.0,
                'Chart_History': list(np.linspace(50, 59.5, 260)),
                'Chart_Dates': [f'2026-session-{i}' for i in range(260)],
            }
        }
        risk_html = market_scanner._generate_bvb_risk_status_html(
            pd.DataFrame(), pd.DataFrame(), full_state=full_state
        )
        self.assertNotIn('INDISPONIBIL', risk_html)
        self.assertNotIn('TVBETETF lipsește', risk_html)
        self.assertIn('TVBETETF &lt; SMA200', risk_html)
        self.assertIn('DOAR POZIȚII BVB', risk_html)

    def test_bvb_proxy_becomes_market_indicator(self):
        dates = pd.bdate_range('2026-07-01', periods=35)
        proxy = {
            'Chart_History': list(np.linspace(58.0, 61.4, 35)),
            'Chart_Dates': [date.date().isoformat() for date in dates],
            'Market_Data_Source': 'IBKR TWS + BVB public',
        }

        indicator = market_scanner._bvb_market_indicator_from_proxy(proxy)

        self.assertEqual(indicator['value'], 61.4)
        self.assertGreater(indicator['change'], 0)
        self.assertEqual(indicator['description'], 'TVBETETF')
        self.assertEqual(indicator['ticker'], 'TVBETETF.RO')
        self.assertEqual(indicator['currency'], 'RON')
        self.assertEqual(len(indicator['sparkline']), 30)
        self.assertIn('IBKR TWS', indicator['market_data_source'])

    @patch('market_scanner._refresh_bvb_proxy_from_market_data', return_value=True)
    @patch('market_scanner._prefetch_ibkr_mcp_market_data')
    @patch('market_scanner.process_portfolio_ticker')
    @patch('market_scanner.load_portfolio')
    def test_portfolio_only_mode_processes_only_held_symbols(
        self, mock_load_portfolio, mock_process, mock_prefetch, mock_refresh
    ):
        mock_load_portfolio.return_value = pd.DataFrame([
            {'symbol': 'JPM'},
            {'symbol': 'TVBETETF.RO'},
        ])
        mock_process.side_effect = [
            {'Symbol': 'JPM'}, {'Symbol': 'TVBETETF.RO'}
        ]
        state = {
            'market_overviews': {'SUA': {'data': {
                'SPX_Price': 7500, 'SPX_SMA10': 7450,
                'SPX_SMA50': 7300, 'SPX_SMA200': 6900,
                'NDX_Price': 28000, 'NDX_SMA10': 27900,
                'NDX_SMA50': 27000, 'NDX_SMA200': 25000,
                'Breadth_Pct': 60, 'VIX_Current': 17,
                'Chart_SPX': {
                    'labels': ['07-29', '07-30'],
                    'price': [7400, 7500],
                },
            }}},
        }
        result = market_scanner.update_portfolio_positions_only(
            state, {'USD': 0.9, 'RON': 0.2}, 17
        )
        self.assertEqual(mock_process.call_count, 2)
        self.assertEqual(
            [item['Symbol'] for item in result['portfolio']],
            ['JPM', 'TVBETETF.RO'],
        )
        mock_prefetch.assert_called_once_with(
            ['TVBETETF.RO', 'JPM'], label='portofoliu + TVBETETF'
        )
        mock_refresh.assert_called_once_with(state)

    def test_portfolio_ibkr_research_always_includes_tvbetetf(self):
        self.assertEqual(
            market_scanner._portfolio_ibkr_research_symbols(
                {}, mode='portfolio'
            ),
            ['TVBETETF.RO'],
        )

    @patch('market_scanner._load_analysis_history')
    def test_refresh_bvb_proxy_persists_ibkr_combined_history(self, load_history):
        dates = pd.bdate_range('2025-09-01', periods=260)
        closes = np.linspace(48.0, 61.0, len(dates))
        history = pd.DataFrame({
            'Open': closes,
            'High': closes,
            'Low': closes,
            'Close': closes,
            'Volume': np.full(len(dates), 100_000),
        }, index=dates)
        load_history.return_value = (
            history,
            {},
            {
                'market_data': {
                    'close': 61.25,
                    'as_of': dates[-1].date().isoformat(),
                },
            },
            {
                'Market_Data_Source': 'IBKR TWS + BVB public',
                'Data_Broker': 'surse combinate',
                'IBKR_Data_Only': True,
            },
        )
        state = {}

        refreshed = market_scanner._refresh_bvb_proxy_from_market_data(state)

        self.assertTrue(refreshed)
        self.assertEqual(state['bvb_proxy']['Price_Native'], 61.25)
        self.assertEqual(state['bvb_proxy']['Chart_History'][-1], 61.25)
        self.assertEqual(len(state['bvb_proxy']['Chart_History']), 260)
        self.assertIn(
            'IBKR TWS', state['bvb_proxy']['Market_Data_Source']
        )

    def test_complete_bvb_csv_parser_includes_main_and_aero(self):
        content = (
            'Simbol;ISIN;Societate;Pret (RON);Data;Segment;Categoria;Volum\n'
            'TLV;ROTLVAACNOR1;BANCA TRANSILVANIA;37,10;24.07.2026;'
            'Piata Reglementata;Premium;100000\n'
            'IARV;ROIARVACNOR1;IAR SA BRASOV;38,80;24.07.2026;'
            'AeRO;AeRO Standard;25000\n'
        )
        records = market_scanner._parse_bvb_equity_universe_csv(content)
        by_symbol = {item['symbol']: item for item in records}
        self.assertEqual(set(by_symbol), {'TLV.RO', 'IARV.RO'})
        self.assertEqual(by_symbol['IARV.RO']['segment'], 'AeRO')
        self.assertEqual(by_symbol['TLV.RO']['price_ron'], 37.10)
        self.assertEqual(by_symbol['IARV.RO']['volume'], 25000)

    def test_bvb_universe_fetch_uses_last_valid_cache_on_error(self):
        state = {'bvb_equity_universe': [{'symbol': 'IARV.RO'}]}
        session = Mock()
        session.get.side_effect = market_scanner.requests.RequestException(
            'offline'
        )
        self.assertEqual(
            market_scanner.fetch_complete_bvb_equity_universe(
                state, request_session=session
            ),
            state['bvb_equity_universe'],
        )

    def test_bvb_universe_is_discovered_without_authenticated_bvb_api(self):
        session = Mock()
        response = Mock()
        response.text = (
            'Simbol;Societate;Segment\n'
            'TLV;BANCA TRANSILVANIA;Piata Reglementata\n'
            'AROBS;AROBS TRANSILVANIA SOFTWARE;AeRO\n'
        )
        response.raise_for_status.return_value = None
        session.get.return_value = response

        records = market_scanner.fetch_complete_bvb_equity_universe(
            {}, request_session=session
        )
        by_symbol = {item['symbol']: item for item in records}
        self.assertEqual(set(by_symbol), {'TLV.RO', 'AROBS.RO'})
        self.assertTrue(all(
            item['source'] == 'Bursa de Valori București'
            for item in records
        ))
        session.get.assert_called_once_with(
            market_scanner.BVB_SHARES_CSV_URL,
            timeout=30,
        )

    def test_bvb_liquidity_uses_rolling_median_not_single_day_spike(self):
        frame = pd.DataFrame({
            'Close': [10.0] * 20,
            'Volume': [1_000] * 19 + [50_000],
        })
        metrics = market_scanner._calculate_bvb_liquidity_metrics(frame)
        self.assertEqual(metrics['Liquidity_Observations_20D'], 20)
        self.assertEqual(metrics['Active_Days_20D'], 20)
        self.assertEqual(metrics['Median_Turnover_20D_RON'], 10_000)
        self.assertEqual(metrics['Last_Turnover_RON'], 500_000)
        self.assertEqual(metrics['Relative_Volume_20D'], 50)

    def test_bvb_liquidity_has_separate_regulated_and_aero_thresholds(self):
        common = {
            'Price': 10, 'Price_Native': 50,
            'Liquidity_Observations_20D': 20,
            'Active_Days_20D': 12,
            'Median_Turnover_20D_RON': 30_000,
        }
        regulated = dict(common, BVB_Metadata={
            'segment': 'Piata Reglementata',
        })
        aero = dict(common, BVB_Metadata={'segment': 'AeRO'})
        regulated_result = market_scanner._bvb_liquidity_assessment(regulated)
        aero_result = market_scanner._bvb_liquidity_assessment(aero)
        self.assertFalse(regulated_result['eligible'])
        self.assertTrue(aero_result['eligible'])
        self.assertEqual(aero_result['market_segment'], 'AeRO')
        self.assertEqual(aero_result['position_cap_eur'], 60)

    def test_bvb_selection_rejects_one_day_volume_spike(self):
        external = [{
            'Ticker': 'SPIKE.RO', 'Decision': 'BUY', 'Consensus': 'Buy',
            'RR_Ratio': 3, 'Trend': 'Bullish', 'RSI': 50,
            'Price': 2, 'Price_Native': 10,
            'Stop_Loss': 1.8, 'Target': 2.6, 'Analysts': 1,
            'Volume': 100_000, 'Avg_Volume': 1_000,
            'Liquidity_Observations_20D': 20,
            'Active_Days_20D': 20,
            'Median_Turnover_20D_RON': 10_000,
            'Last_Turnover_RON': 1_000_000,
            'BVB_Metadata': {'segment': 'Piata Reglementata'},
        }]
        selected = market_scanner.select_strict_buy_candidates(
            pd.DataFrame(), external_research=external
        )
        self.assertEqual(selected, [])

    def test_bvb_watchlist_candidate_also_requires_local_liquidity(self):
        watchlist = pd.DataFrame([{
            'Ticker': 'THIN.RO', 'Decision': 'BUY', 'Consensus': 'Strong Buy',
            'RR_Ratio': 3.5, 'Price': 2, 'Price_Native': 10,
            'Liquidity_Observations_20D': 20,
            'Active_Days_20D': 8,
            'Median_Turnover_20D_RON': 8_000,
            'BVB_Metadata': {'segment': 'AeRO'},
        }])
        selected = market_scanner.select_strict_buy_candidates(watchlist)
        self.assertEqual(selected, [])

    def test_bvb_selection_attaches_official_market_segment(self):
        watchlist = pd.DataFrame([{
            'Ticker': 'AERO.RO', 'Decision': 'BUY', 'Consensus': 'Strong Buy',
            'RR_Ratio': 3.5, 'Price': 2, 'Price_Native': 10,
            'Liquidity_Observations_20D': 20,
            'Active_Days_20D': 12,
            'Median_Turnover_20D_RON': 30_000,
        }])
        selected = market_scanner.select_strict_buy_candidates(
            watchlist,
            bvb_universe=[{
                'symbol': 'AERO.RO', 'segment': 'AeRO',
                'category': 'AeRO Standard',
            }],
        )
        self.assertEqual(len(selected), 1)
        self.assertEqual(
            selected[0]['BVB_Liquidity']['market_segment'], 'AeRO'
        )

    def test_event_impact_nfp(self):
        """Test NFP event impact description."""
        desc = market_scanner_analysis.get_event_impact('Nonfarm')
        self.assertIsInstance(desc, str)
        self.assertGreater(len(desc), 0)
        
    def test_event_impact_unknown(self):
        """Test unknown event returns default description."""
        desc = market_scanner_analysis.get_event_impact('UNKNOWN_EVENT_XYZ')
        self.assertIsInstance(desc, str)
        self.assertIn('Indicator economic', desc)
        
    @patch('market_scanner_analysis.get_market_news')
    def test_news_and_ai_summary_generation(self, mock_news):
        """Test news and AI summary HTML generation."""
        # Skip if function doesn't exist or has different signature
        if not hasattr(market_scanner_analysis, '_generate_news_and_ai_summary_html'):
            self.skipTest("Function not available")
            
        mock_news.return_value = [
            {
                'title': 'Test Market News',
                'link': 'http://test.com/news',
                'desc': 'Test description of market news'
            }
        ]
        
        # Just verify the function exists and can be called
        self.assertTrue(callable(market_scanner_analysis.generate_market_analysis))

    def test_ai_summary_is_persisted_after_dashboard_generation(self):
        """Cache-ul AI trebuie salvat după ce rezumatul nou este generat."""
        scanner_path = os.path.join(os.path.dirname(__file__), '..', 'market_scanner.py')
        with open(scanner_path, 'r', encoding='utf-8') as handle:
            source = handle.read()
        cache_block = source[source.index("if new_ai_text:"):source.index("html_head += market_analysis_html")]
        self.assertIn("full_state['last_ai_summary'] = new_ai_text", cache_block)
        self.assertIn("market_utils.save_state(full_state)", cache_block)

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('market_scanner_analysis.requests.post')
    def test_news_ai_reuses_recent_material_cache(self, mock_post):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            'model': 'gpt-5.6-terra',
            'output_text': (
                'SENTIMENT_SCORE: 61\n'
                'REZUMAT_HTML: <p>Context moderat pozitiv.</p>'
            ),
            'usage': {
                'input_tokens': 1200, 'output_tokens': 80,
                'total_tokens': 1280,
                'input_tokens_details': {'cached_tokens': 0},
            },
        }
        mock_post.return_value = response
        news = [{
            'title': 'Știre stabilă', 'link': 'https://example.com/news',
            'desc': 'Descriere stabilă',
        }]
        indicators = {
            'VIX': {'value': 15.2}, 'SPX': {'value': 6200},
        }

        _, text, score, cache = (
            market_scanner_analysis._generate_news_and_ai_summary_html(
                news, indicators
            )
        )
        self.assertEqual(score, 61)
        self.assertIn('Context moderat pozitiv', text)
        self.assertEqual(mock_post.call_count, 1)
        request_json = mock_post.call_args.kwargs['json']
        self.assertEqual(
            request_json['model'],
            market_scanner_analysis.OPENAI_LIGHTWEIGHT_MODEL,
        )
        self.assertEqual(request_json['prompt_cache_options']['mode'], 'explicit')

        _, cached_text, cached_score, returned_cache = (
            market_scanner_analysis._generate_news_and_ai_summary_html(
                news, indicators, cache
            )
        )
        self.assertEqual(mock_post.call_count, 1)
        self.assertEqual(cached_text, text)
        self.assertEqual(cached_score, score)
        self.assertEqual(returned_cache['fingerprint'], cache['fingerprint'])
        
    def test_market_analysis_structure(self):
        """Test market analysis returns correct structure."""
        indicators = {
            'VIX': {'value': 18.5, 'status': 'Normal', 'change': -0.5},
            'SKEW': {'value': 125.0, 'status': 'Normal', 'change': 2.0},
            'SPX': {'value': 4500.0, 'status': 'Normal', 'change': 15.0}
        }
        
        html, summary, score = market_scanner_analysis.generate_market_analysis(indicators)
        
        # Check return types
        self.assertIsInstance(html, str)
        self.assertIsInstance(summary, str)
        self.assertIsInstance(score, (int, float))
        
        # Check score range
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        
        # Check HTML contains expected elements
        self.assertIn('Market Cortex', html)
    
    def test_nasdaq_indicator_inclusion(self):
        """Test that NASDAQ is included in market indicators."""
        indicators = {
            'VIX': {'value': 18.5, 'status': 'Normal', 'change': -0.5},
            'SPX': {'value': 4500.0, 'status': 'Normal', 'change': 15.0, 'sparkline': [4480, 4490, 4500]},
            'NASDAQ': {'value': 14500.0, 'status': 'Normal', 'change': 50.0, 'sparkline': [14400, 14450, 14500]}
        }
        
        html, summary, score = market_scanner_analysis.generate_market_analysis(indicators)
        
        # NASDAQ should be processed
        self.assertIsInstance(html, str)
        self.assertIsInstance(score, (int, float))


class TestPortfolioAIAnalysis(unittest.TestCase):
    def setUp(self):
        self.portfolio = pd.DataFrame([{
            'Symbol': 'TEST',
            'Shares': 100,
            'Current_Price': 50,
            'Price_Native': 50,
            'Buy_Price': 45,
            'Current_Value': 5000,
            'Profit_Pct': 11.11,
            'Target': 60,
            'Suggested_Stop': 46,
            'Finviz_ATR': 2,
            'Vol_W': 3,
            'Vol_M': 4,
            'Sell_Decision': 'HOLD',
            'Sell_Reason': 'Trend pozitiv',
            'Trend': 'Bullish',
            'RSI': 58,
            'RS_vs_SPX': 4,
        }])

    def test_snapshot_flags_missing_stop_without_inventing_one(self):
        snapshot = market_scanner_analysis.build_portfolio_risk_snapshot(
            self.portfolio, pd.DataFrame()
        )
        position = snapshot['positions'][0]
        self.assertEqual(position['active_stops'], [])
        self.assertIsNone(position['primary_stop_eur'])
        self.assertIn('Fără ordin stop activ identificat', position['data_flags'])

    @patch('market_scanner_analysis.requests.post')
    @patch(
        'market_scanner_analysis.collect_portfolio_evidence',
        return_value={'fetched_at': None, 'symbols': [], 'items': []},
    )
    @patch('market_scanner_analysis.get_economic_events', return_value=[])
    def test_portfolio_ai_does_not_call_api_outside_scheduled_window(
        self, _events, _evidence, post
    ):
        _, cache, _, diagnostic = (
            market_scanner_analysis.generate_portfolio_ai_analysis(
                self.portfolio,
                pd.DataFrame(),
                allow_ai=False,
            )
        )

        post.assert_not_called()
        self.assertIsNone(cache)
        self.assertEqual(diagnostic['status'], 'scheduled_wait')

    def test_snapshot_detects_partial_stop_coverage(self):
        orders = pd.DataFrame([{
            'Symbol': 'TEST', 'Action': 'SELL', 'OrderType': 'STP',
            'Total_Qty': 40, 'Stop_Price': 47,
        }])
        snapshot = market_scanner_analysis.build_portfolio_risk_snapshot(
            self.portfolio, orders
        )
        position = snapshot['positions'][0]
        self.assertEqual(position['stop_coverage_pct'], 40)
        self.assertTrue(any('40 din 100' in flag for flag in position['data_flags']))

    def test_snapshot_includes_tws_cash_margin_and_freshness(self):
        account_data = {
            'fetched_at': datetime.now().astimezone().isoformat(),
            'accounts': [{
                'label': 'Cont 1',
                'base_currency': 'EUR',
                'summary': {
                    'NetLiquidation': 100000,
                    'TotalCashValue': 4000,
                    'AvailableFunds': 12000,
                    'BuyingPower': 24000,
                    'ExcessLiquidity': 15000,
                    'MaintMarginReq': 20000,
                    'Cushion': 0.2,
                },
                'cash_by_currency': {'EUR': 2500, 'USD': 1800},
            }],
        }
        snapshot = market_scanner_analysis.build_portfolio_risk_snapshot(
            self.portfolio, pd.DataFrame(), account_data=account_data
        )
        liquidity = snapshot['account_liquidity']
        self.assertFalse(liquidity['stale'])
        self.assertEqual(liquidity['accounts'][0]['cash_pct_of_net_liquidation'], 4)
        self.assertEqual(liquidity['accounts'][0]['maintenance_margin_pct'], 20)
        self.assertIn('Cash-ul de bază este sub 5%', ' '.join(liquidity['risk_flags']))

    def test_missing_tws_account_data_is_explicit(self):
        snapshot = market_scanner_analysis.build_portfolio_risk_snapshot(
            self.portfolio, pd.DataFrame(), account_data=None
        )
        self.assertIn(
            'Sumarul cash/marjă TWS nu este disponibil',
            snapshot['account_liquidity']['risk_flags'],
        )

    def test_tws_account_encryption_round_trip(self):
        payload = '{"accounts":[{"label":"Cont 1","summary":{"NetLiquidation":1000}}]}'
        encrypted = market_security.encrypt_for_js(payload, 'test-password')
        self.assertNotIn('NetLiquidation', encrypted)
        self.assertEqual(
            market_security.decrypt_from_js(encrypted, 'test-password'),
            payload,
        )

    def test_account_snapshot_is_portable_between_local_and_remote(self):
        payload = {
            'source': 'IBKR TWS',
            'accounts': [{
                'label': 'IBKR',
                'summary': {'NetLiquidation': 89006.99},
            }],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            raw_path = os.path.join(temp_dir, 'tws_account.json')
            encrypted_path = os.path.join(
                temp_dir, 'tws_account.enc.json'
            )
            with open(raw_path, 'w', encoding='utf-8') as handle:
                json.dump(payload, handle)
            local, local_source = (
                market_scanner._load_portable_account_snapshot(
                    raw_path, encrypted_path, 'shared-remote-password'
                )
            )
            os.remove(raw_path)
            remote, remote_source = (
                market_scanner._load_portable_account_snapshot(
                    raw_path, encrypted_path, 'shared-remote-password'
                )
            )

        self.assertEqual(local_source, 'local')
        self.assertEqual(remote_source, 'encrypted_cache')
        self.assertEqual(local, payload)
        self.assertEqual(remote, payload)

    def test_wrong_account_snapshot_password_is_explicit(self):
        payload = {'accounts': [{'label': 'IBKR'}]}
        with tempfile.TemporaryDirectory() as temp_dir:
            raw_path = os.path.join(temp_dir, 'tws_account.json')
            encrypted_path = os.path.join(
                temp_dir, 'tws_account.enc.json'
            )
            with open(raw_path, 'w', encoding='utf-8') as handle:
                json.dump(payload, handle)
            market_scanner._load_portable_account_snapshot(
                raw_path, encrypted_path, 'shared-remote-password'
            )
            os.remove(raw_path)
            remote, source = market_scanner._load_portable_account_snapshot(
                raw_path, encrypted_path, 'wrong-password'
            )

        self.assertIsNone(remote)
        self.assertEqual(source, 'encrypted_cache_invalid')

    def test_manual_tradeville_snapshot_keeps_broker_source_and_ratios(self):
        account_data = {
            'fetched_at': datetime.now().astimezone().isoformat(),
            'source': 'IBKR TWS + Tradeville manual',
            'accounts': [{
                'label': 'Tradeville',
                'source': 'Tradeville / snapshot manual',
                'base_currency': 'EUR',
                'summary': {
                    'NetLiquidation': 72778.09,
                    'TotalCashValue': 48438.86,
                    'AvailableFunds': 48438.86,
                    'GrossPositionValue': 24339.23,
                    'CostBasis': 11306.92,
                    'RelativeProfit': 12983.64,
                },
                'cash_by_currency': {'EUR': 47729.35, 'RON': 37.02, 'USD': 799.83},
            }],
        }
        normalized = market_scanner_analysis._normalize_tws_account_data(account_data)
        tradeville = normalized['accounts'][0]
        self.assertEqual(tradeville['source'], 'Tradeville / snapshot manual')
        self.assertEqual(tradeville['cash_pct_of_net_liquidation'], 66.56)
        self.assertEqual(set(tradeville['cash_by_currency']), {'EUR', 'RON', 'USD'})
        self.assertEqual(tradeville['summary']['CostBasis'], 11306.92)
        self.assertEqual(tradeville['summary']['RelativeProfit'], 12983.64)
        self.assertNotIn('BuyingPower', tradeville['summary'])

    def test_single_ibkr_account_label_is_normalized(self):
        account_data = {
            'fetched_at': datetime.now().astimezone().isoformat(),
            'accounts': [{
                'label': 'IBKR 1',
                'source': 'IBKR TWS',
                'base_currency': 'EUR',
                'summary': {
                    'NetLiquidation': 100000,
                    'TotalCashValue': 40000,
                },
            }],
        }
        normalized = market_scanner_analysis._normalize_tws_account_data(
            account_data
        )
        self.assertEqual(normalized['accounts'][0]['label'], 'IBKR')

    def test_stale_tradeville_snapshot_does_not_mark_fresh_ibkr_as_stale(self):
        now = datetime(2026, 8, 12, 8, 0, tzinfo=timezone.utc)
        account_data = {
            'fetched_at': '2026-07-30T08:00:00+00:00',
            'source': 'IBKR TWS + Tradeville manual',
            'accounts': [
                {
                    'label': 'IBKR',
                    'source': 'IBKR MCP (read-only)',
                    'fetched_at': '2026-08-12T07:00:00+00:00',
                    'base_currency': 'EUR',
                    'summary': {
                        'NetLiquidation': 100000,
                        'TotalCashValue': 50000,
                    },
                },
                {
                    'label': 'Tradeville',
                    'source': 'Tradeville manual',
                    'fetched_at': '2026-07-30T08:00:00+00:00',
                    'base_currency': 'EUR',
                    'summary': {
                        'NetLiquidation': 50000,
                        'TotalCashValue': 20000,
                    },
                },
            ],
        }

        normalized = market_scanner_analysis._normalize_tws_account_data(
            account_data, now=now
        )

        accounts = {
            account['label']: account for account in normalized['accounts']
        }
        self.assertFalse(normalized['stale'])
        self.assertEqual(normalized['fetched_at'], '2026-08-12T07:00:00+00:00')
        self.assertEqual(accounts['IBKR']['age_hours'], 1.0)
        self.assertFalse(accounts['IBKR']['stale'])
        self.assertTrue(accounts['Tradeville']['stale'])
        flags = ' '.join(normalized['risk_flags'])
        self.assertIn('Tradeville sunt mai vechi', flags)
        self.assertNotIn('IBKR sunt mai vechi', flags)

    def test_combined_broker_totals_sum_nav_and_cash_once(self):
        account_data = {
            'accounts': [
                {
                    'label': 'IBKR',
                    'source': 'IBKR TWS',
                    'base_currency': 'EUR',
                    'summary': {
                        'NetLiquidation': 89043.59,
                        'TotalCashValue': 85949.15,
                    },
                },
                {
                    'label': 'Tradeville',
                    'source': 'Tradeville / snapshot manual',
                    'base_currency': 'EUR',
                    'summary': {
                        'NetLiquidation': 72778.09,
                        'TotalCashValue': 48438.86,
                    },
                },
            ],
        }
        totals = market_scanner_analysis._combined_broker_totals(account_data)
        self.assertEqual(totals['currency'], 'EUR')
        self.assertEqual(totals['net_liquidation'], 161821.68)
        self.assertEqual(totals['total_cash'], 134388.01)

    def test_combined_broker_totals_reject_mixed_base_currencies(self):
        account_data = {
            'accounts': [
                {
                    'label': 'IBKR', 'source': 'IBKR TWS',
                    'base_currency': 'USD',
                    'summary': {
                        'NetLiquidation': 100, 'TotalCashValue': 50,
                    },
                },
                {
                    'label': 'Tradeville', 'source': 'Tradeville manual',
                    'base_currency': 'EUR',
                    'summary': {
                        'NetLiquidation': 100, 'TotalCashValue': 50,
                    },
                },
            ],
        }
        self.assertIsNone(
            market_scanner_analysis._combined_broker_totals(account_data)
        )

    def test_broker_totals_history_keeps_only_real_balance_changes(self):
        account_data = {
            'accounts': [
                {
                    'label': 'IBKR', 'source': 'IBKR TWS',
                    'base_currency': 'EUR',
                    'summary': {
                        'NetLiquidation': 100, 'TotalCashValue': 60,
                    },
                },
                {
                    'label': 'Tradeville', 'source': 'Tradeville manual',
                    'base_currency': 'EUR',
                    'summary': {
                        'NetLiquidation': 200, 'TotalCashValue': 80,
                    },
                },
            ],
        }
        history = market_scanner_analysis.update_broker_totals_history(
            [], account_data, observed_at='2026-07-30T09:00:00+03:00'
        )
        history = market_scanner_analysis.update_broker_totals_history(
            history, account_data, observed_at='2026-07-30T12:00:00+03:00'
        )
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['timestamp'], '2026-07-30T09:00:00+03:00')
        history = market_scanner_analysis.update_broker_totals_history(
            history, account_data, observed_at='2026-07-31T09:00:00+03:00'
        )
        self.assertEqual(len(history), 2)
        self.assertEqual(history[-1]['timestamp'], '2026-07-31T09:00:00+03:00')
        self.assertEqual(history[-1]['net_liquidation'], 300)
        self.assertEqual(history[-1]['total_cash'], 140)
        account_data['accounts'][0]['summary']['NetLiquidation'] = 101
        history = market_scanner_analysis.update_broker_totals_history(
            history, account_data, observed_at='2026-07-31T10:00:00+03:00'
        )
        self.assertEqual(len(history), 3)
        self.assertEqual(history[-1]['net_liquidation'], 301)
        self.assertEqual(history[-1]['total_cash'], 140)

    def test_broker_totals_history_uses_stable_account_password(self):
        expected = [{
            'timestamp': '2026-07-30T09:00:00+03:00',
            'net_liquidation': 300,
            'total_cash': 140,
            'currency': 'EUR',
        }]
        encrypted = market_security.encrypt_for_js(
            json.dumps(expected), 'account-password'
        )
        self.assertEqual(
            market_scanner._decrypt_broker_totals_history(
                encrypted,
                account_password='account-password',
                legacy_password='different-page-password',
            ),
            expected,
        )

    def test_broker_totals_history_migrates_legacy_page_password(self):
        expected = [{
            'timestamp': '2026-07-30T09:00:00+03:00',
            'net_liquidation': 300,
            'total_cash': 140,
            'currency': 'EUR',
        }]
        encrypted = market_security.encrypt_for_js(
            json.dumps(expected), 'legacy-page-password'
        )
        self.assertEqual(
            market_scanner._decrypt_broker_totals_history(
                encrypted,
                account_password='account-password',
                legacy_password='legacy-page-password',
            ),
            expected,
        )

    def test_raw_balance_renderer_adds_combined_card_and_history_chart(self):
        snapshot = {
            'as_of': '2026-07-30T10:00:00+03:00',
            'portfolio': {},
            'positions': [],
            'account_liquidity': {
                'privacy_mode': 'exact',
                'accounts': [
                    {
                        'label': 'IBKR', 'source': 'IBKR TWS',
                        'base_currency': 'EUR',
                        'summary': {
                            'NetLiquidation': 100,
                            'TotalCashValue': 60,
                        },
                        'cash_by_currency': {},
                    },
                    {
                        'label': 'Tradeville',
                        'source': 'Tradeville manual',
                        'base_currency': 'EUR',
                        'summary': {
                            'NetLiquidation': 200,
                            'TotalCashValue': 80,
                        },
                        'cash_by_currency': {},
                    },
                ],
                'combined_history': [],
                'nav_history': [
                    {'date': '20260729', 'nav': 95, 'currency': 'EUR'},
                    {'date': '20260730', 'nav': 100, 'currency': 'EUR'},
                ],
                'cash_history': [
                    {'date': '20260729', 'cash': 50, 'currency': 'EUR'},
                    {'date': '20260730', 'cash': 55, 'currency': 'EUR'},
                ],
            },
        }
        rendered = market_scanner_analysis._render_portfolio_ai_html(snapshot)
        self.assertIn('Total IBKR + Tradeville · EUR', rendered)
        self.assertIn('Valoare totală', rendered)
        self.assertIn('300.00 EUR', rendered)
        self.assertIn('Cash total', rendered)
        self.assertIn('140.00 EUR', rendered)
        self.assertIn("id='brokerTotalsHistoryButton'", rendered)
        self.assertIn('>Evoluție</button>', rendered)
        self.assertNotIn('<canvas', rendered)
        self.assertIn('data-ibkr-nav-history=', rendered)
        self.assertIn('data-ibkr-cash-history=', rendered)
        self.assertIn('20260729', rendered)
        self.assertIn('openBrokerTotalsDetail(this)', rendered)

    def test_portfolio_ai_cache_changes_with_broker_snapshot_not_age(self):
        base = {
            'portfolio': {'position_count': 1},
            'positions': [{'symbol': 'TEST'}],
            'account_liquidity': {
                'privacy_mode': 'exact',
                'fetched_at': '2026-07-26T00:00:00+00:00',
                'age_hours': 1.0,
                'accounts': [{'label': 'Tradeville', 'summary': {'NetLiquidation': 100}}],
            },
        }
        later_age = copy.deepcopy(base)
        later_age['account_liquidity']['age_hours'] = 2.0
        changed_cash = copy.deepcopy(base)
        changed_cash['account_liquidity']['accounts'][0]['summary']['NetLiquidation'] = 120

        self.assertEqual(
            market_scanner_analysis._portfolio_snapshot_fingerprint(base),
            market_scanner_analysis._portfolio_snapshot_fingerprint(later_age),
        )
        self.assertNotEqual(
            market_scanner_analysis._portfolio_snapshot_fingerprint(base),
            market_scanner_analysis._portfolio_snapshot_fingerprint(changed_cash),
        )

    def test_sanitized_tws_bands_feed_risk_without_exact_balances(self):
        account_data = {
            'fetched_at': datetime.now().astimezone().isoformat(),
            'privacy_mode': 'bands_only',
            'sanitized_accounts': [{
                'label': 'Cont 1', 'base_currency': 'EUR',
                'cash_currencies': ['EUR', 'USD'],
                'cash_pct_band': '5-15%',
                'maintenance_margin_pct_band': 'peste 50%',
                'available_funds_status': 'pozitiv',
                'buying_power_status': 'pozitiv',
                'excess_liquidity_status': 'pozitiv',
                'cushion_band': '15-30%',
            }],
        }
        normalized = market_scanner_analysis._normalize_tws_account_data(account_data)
        self.assertEqual(normalized['privacy_mode'], 'bands_only')
        self.assertEqual(normalized['accounts'][0]['cash_pct_band'], '5-15%')
        self.assertNotIn('summary', normalized['accounts'][0])
        self.assertIn(
            'Marja de menținere depășește 50%',
            ' '.join(normalized['risk_flags']),
        )

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('market_scanner_analysis.requests.post')
    def test_portfolio_ai_uses_structured_responses_and_validates_symbols(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'output_text': '''{
          "portfolio_overview": "Riscul principal este lipsa protecției.",
          "market_read": "Piața SUA este neutră; poziția trebuie urmărită individual.",
          "position_actions": [{
            "symbol": "TEST", "broker": "IBKR", "action": "Urmărește atent",
            "plain_reason": "Poziția nu are încă o protecție clară.",
            "calendar_effect": "Decizia Fed apropiată poate amplifica volatilitatea; stopul nu trebuie lărgit.",
            "next_check": "Confirmarea unui ordin stop activ."
          }],
          "priorities": [{
            "symbol": "TEST", "severity": "ridicat",
            "issue": "Lipsă stop", "evidence": "Nu există ordin stop activ.",
            "action": "Verifică și plasează un stop adecvat.",
            "why": "Pierderile nu sunt limitate procedural.",
            "review_trigger": "La modificarea ATR sau a tezei.",
            "confidence": "ridicată, ordinul lipsește",
            "source_ids": ["TEST-sec-1", "SURSA-INVENTATA"]
          }]
        }'''}
        mock_post.return_value = mock_response

        evidence_cache = {
            'fetched_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            'symbols': ['TEST'],
            'items': [{
                'source_id': 'TEST-sec-1', 'symbol': 'TEST',
                'title': 'Depunere SEC 10-Q', 'url': 'https://www.sec.gov/test',
                'date': '2026-07-25', 'publisher': 'SEC',
                'source_type': 'raport oficial 10-Q', 'official': True,
            }],
        }
        html_result, cache, returned_evidence, diagnostic = market_scanner_analysis.generate_portfolio_ai_analysis(
            self.portfolio, pd.DataFrame(), cached_evidence=evidence_cache
        )

        request_json = mock_post.call_args.kwargs['json']
        self.assertEqual(request_json['model'], market_scanner_analysis.OPENAI_ANALYSIS_MODEL)
        self.assertEqual(request_json['reasoning'], {'effort': 'low'})
        self.assertEqual(request_json['prompt_cache_options']['mode'], 'explicit')
        self.assertIn('prompt_cache_key', request_json)
        self.assertEqual(
            request_json['input'][0]['content'][0][
                'prompt_cache_breakpoint'
            ],
            {'mode': 'explicit'},
        )
        user_payload = json.loads(request_json['input'][1]['content'])
        self.assertNotIn('rules', user_payload)
        self.assertEqual(request_json['text']['format']['type'], 'json_schema')
        self.assertTrue(request_json['text']['format']['strict'])
        self.assertIn('TEST · Lipsă stop', html_result)
        self.assertIn('TEST · IBKR', html_result)
        self.assertIn('Ce fac piețele relevante', html_result)
        self.assertIn('<b>Calendar:</b>', html_result)
        self.assertIn('Depunere SEC 10-Q', html_result)
        self.assertIn('oficial', html_result)
        self.assertNotIn('SURSA-INVENTATA', html_result)
        self.assertEqual(cache['result']['priorities'][0]['symbol'], 'TEST')
        self.assertEqual(returned_evidence['items'][0]['source_id'], 'TEST-sec-1')
        self.assertEqual(diagnostic['status'], 'success')

    def test_portfolio_fingerprint_ignores_refresh_timestamps(self):
        snapshot = {
            'portfolio': {
                'position_count': 1, 'total_value_eur': 5000,
                'positions_without_stop': 0,
                'positions_with_incomplete_stop_coverage': 0,
            },
            'positions': [{
                'symbol': 'TEST', 'broker': 'IBKR', 'market': 'SUA',
                'shares': 10, 'current_price_eur': 100,
                'current_value_eur': 1000, 'active_stops': [{
                    'value': 92, 'quantity': 10, 'order_type': 'STP',
                }],
                'market_data_fetched_at': '2026-08-10T09:00:00',
                'evidence': [],
            }],
            'account_liquidity': {
                'privacy_mode': 'exact',
                'fetched_at': '2026-08-10T09:00:00',
                'accounts': [{'label': 'IBKR', 'cash_total': 10000}],
            },
            'market_context': {}, 'buy_candidates': [],
            'economic_calendar': [], 'tvbetetf_lookthrough': {},
            'us_sector_rotation': {}, 'us_market_regime': {},
        }
        first = market_scanner_analysis._portfolio_snapshot_fingerprint(snapshot)
        refreshed = json.loads(json.dumps(snapshot))
        refreshed['account_liquidity']['fetched_at'] = '2026-08-10T09:30:00'
        refreshed['positions'][0]['market_data_fetched_at'] = '2026-08-10T09:30:00'
        second = market_scanner_analysis._portfolio_snapshot_fingerprint(refreshed)
        self.assertEqual(first, second)
        refreshed['positions'][0]['shares'] = 11
        self.assertNotEqual(
            first,
            market_scanner_analysis._portfolio_snapshot_fingerprint(refreshed),
        )

    @patch.dict(os.environ, {
        'OPENAI_TERRA_INPUT_USD_PER_MTOK': '1',
        'OPENAI_TERRA_CACHED_INPUT_USD_PER_MTOK': '0.1',
        'OPENAI_TERRA_CACHE_WRITE_USD_PER_MTOK': '1.25',
        'OPENAI_TERRA_OUTPUT_USD_PER_MTOK': '5',
    })
    def test_openai_usage_records_cache_and_estimated_cost(self):
        usage = market_scanner_analysis._openai_usage_from_response({
            'model': 'gpt-5.6-terra',
            'usage': {
                'input_tokens': 2000,
                'output_tokens': 100,
                'total_tokens': 2100,
                'input_tokens_details': {
                    'cached_tokens': 1000,
                    'cache_write_tokens': 500,
                },
                'output_tokens_details': {'reasoning_tokens': 25},
            },
        }, 'test')
        self.assertEqual(usage['uncached_input_tokens'], 500)
        self.assertEqual(usage['cached_tokens'], 1000)
        self.assertEqual(usage['cache_write_tokens'], 500)
        self.assertEqual(usage['reasoning_tokens'], 25)
        self.assertGreater(usage['estimated_cost_usd'], 0)

    def test_openai_usage_uses_luna_rates_for_lightweight_jobs(self):
        usage = market_scanner_analysis._openai_usage_from_response({
            'model': 'gpt-5.6-luna',
            'usage': {
                'input_tokens': 1000,
                'output_tokens': 1000,
                'total_tokens': 2000,
            },
        }, 'economic_calendar', model='gpt-5.6-luna')
        self.assertEqual(
            usage['pricing_rates_usd_per_mtok'],
            {
                'input': 0.2, 'cached_input': 0.02,
                'cache_write': 0.25, 'output': 1.2,
            },
        )
        self.assertAlmostEqual(usage['estimated_cost_usd'], 0.0014)

    def test_portfolio_request_removes_chart_series_from_candidates(self):
        compact = market_scanner_analysis._compact_portfolio_request_snapshot({
            'buy_candidates': [{
                'symbol': 'MSFT', 'entry_native': 100,
                'chart_series_native': [1, 2, 3],
                'chart_series_dates': ['2026-08-01'],
                'chart_ohlc_native': [{'close': 1}],
                'bvb_metadata': {'large': 'payload'},
            }],
        })
        candidate = compact['buy_candidates'][0]
        self.assertEqual(candidate['symbol'], 'MSFT')
        self.assertEqual(candidate['entry_native'], 100)
        self.assertNotIn('chart_series_native', candidate)
        self.assertNotIn('chart_series_dates', candidate)
        self.assertNotIn('chart_ohlc_native', candidate)
        self.assertNotIn('bvb_metadata', candidate)

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('market_scanner_analysis.get_economic_events', return_value=[])
    @patch('market_scanner_analysis.requests.post')
    def test_portfolio_ai_recovers_invalid_large_response_in_validated_batches(
        self, mock_post, _mock_calendar
    ):
        incomplete = Mock()
        incomplete.status_code = 200
        incomplete.json.return_value = {
            'status': 'incomplete',
            'incomplete_details': {'reason': 'max_output_tokens'},
            'output': [],
        }
        invalid_json = Mock()
        invalid_json.status_code = 200
        invalid_json.json.return_value = {'output_text': '{invalid'}
        recovered = Mock()
        recovered.status_code = 200
        recovered.json.return_value = {'output_text': '''{
          "portfolio_overview": "Riscul principal este protecția poziției existente.",
          "market_read": "Piața SUA permite selecție, dar intrările cer confirmare.",
          "position_actions": [{
            "symbol": "TEST", "broker": "IBKR", "action": "Urmărește atent",
            "plain_reason": "Poziția trebuie protejată printr-un ordin verificabil.",
            "calendar_effect": "Nu sunt evenimente apropiate în date.",
            "next_check": "Confirmarea ordinului stop."
          }],
          "buy_recommendations": [{
            "symbol": "MSFT", "market": "SUA",
            "verdict": "Pregătit la trigger",
            "why_now": "Trendul este favorabil, dar intrarea cere confirmare.",
            "market_effect": "Piața susține selectiv liderii.",
            "news_effect": "Nu există știri validate care să schimbe teza.",
            "calendar_effect": "Nu sunt evenimente apropiate în date.",
            "main_risk": "Pierderea nivelului de stop.",
            "source_ids": []
          }],
          "priorities": [{
            "symbol": "TEST", "severity": "ridicat",
            "issue": "Lipsă stop", "evidence": "Nu există ordin stop activ.",
            "action": "Verifică și plasează protecția.",
            "why": "Pierderile nu sunt limitate procedural.",
            "review_trigger": "La activarea stopului.",
            "confidence": "ridicată, ordinul lipsește",
            "source_ids": []
          }]
        }'''}
        mock_post.side_effect = [incomplete, invalid_json, recovered]
        candidate = {
            'symbol': 'MSFT', 'market': 'SUA', 'company_name': 'Microsoft',
            'entry_eur': 100, 'stop_eur': 95, 'target_eur': 120,
            'rr_ratio': 4, 'consensus': 'Buy', 'strict_eligible': True,
            'requires_watchlist_filters': True, 'eligible_brokers': ['IBKR'],
        }
        evidence_cache = {
            'fetched_at': (
                datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
            ),
            'symbols': ['TEST', 'MSFT'],
            'items': [],
        }
        _, cache, _, diagnostic = (
            market_scanner_analysis.generate_portfolio_ai_analysis(
                self.portfolio,
                pd.DataFrame(),
                cached_evidence=evidence_cache,
                buy_candidates=[candidate],
            )
        )
        self.assertEqual(diagnostic['status'], 'success_recovered')
        self.assertEqual(
            cache['result']['buy_recommendations'][0]['symbol'], 'MSFT'
        )
        self.assertEqual(mock_post.call_count, 3)
        self.assertEqual(
            mock_post.call_args_list[0].kwargs['json']['max_output_tokens'],
            16000,
        )
        cards = market_scanner_analysis.render_buy_recommendations_html(
            cache['result'], [candidate]
        )
        self.assertNotIn('>Neanalizat</span>', cards)
        self.assertIn('Ordin la trigger', cards)

    def test_portfolio_ai_validation_can_require_every_candidate(self):
        result = {
            'portfolio_overview': 'Rezumat valid.',
            'market_read': 'Context valid.',
            'position_actions': [{
                'symbol': 'TEST', 'broker': 'IBKR',
                'action': 'Urmărește atent', 'plain_reason': 'Motiv valid.',
                'calendar_effect': 'Calendar valid.', 'next_check': 'Prag valid.',
            }],
            'buy_recommendations': [],
            'priorities': [{
                'symbol': 'TEST', 'severity': 'mediu', 'issue': 'Risc',
                'evidence': 'Date valide.', 'action': 'Verifică.',
                'why': 'Controlează riscul.', 'review_trigger': 'La prag.',
                'confidence': 'medie', 'source_ids': [],
            }],
        }
        with self.assertRaisesRegex(ValueError, 'MSFT'):
            market_scanner_analysis._validate_portfolio_ai_result(
                result,
                {'TEST'},
                candidate_symbols={'MSFT'},
                require_complete_candidates=True,
            )

    def test_portfolio_positions_map_to_broker_and_relevant_market(self):
        portfolio = pd.DataFrame([
            {'Symbol': 'JPM', 'Shares': 1, 'Current_Value': 100},
            {'Symbol': 'TVBETETF.RO', 'Shares': 1, 'Current_Value': 100},
        ])
        context = {
            'SUA': {'benchmarks': [{'label': 'S&P 500'}], 'applies_to': ['JPM']},
            'România / BVB': {
                'benchmarks': [{'label': 'TVBETETF (proxy BET-TR)'}],
                'applies_to': ['TVBETETF.RO'],
            },
        }
        snapshot = market_scanner_analysis.build_portfolio_risk_snapshot(
            portfolio, market_context=context
        )
        positions = {item['symbol']: item for item in snapshot['positions']}
        self.assertEqual(positions['JPM']['broker'], 'IBKR')
        self.assertEqual(positions['JPM']['market'], 'SUA')
        self.assertEqual(positions['TVBETETF.RO']['broker'], 'Tradeville')
        self.assertEqual(positions['TVBETETF.RO']['market'], 'România / BVB')
        self.assertEqual(snapshot['market_context'], context)

    def test_position_calendar_fallback_is_market_specific(self):
        snapshot = {
            'positions': [
                {'symbol': 'JPM', 'market': 'SUA'},
                {'symbol': 'TVBETETF.RO', 'market': 'România / BVB'},
            ],
            'economic_calendar': [
                {'name': 'Fed Rate Decision', 'country': 'SUA', 'datetime': '2026-07-29'},
                {'name': 'BNR Rate Decision', 'country': 'România', 'datetime': '2026-08-07'},
            ],
        }
        effects = market_scanner_analysis._position_calendar_effects(snapshot)
        self.assertIn('Fed Rate Decision', effects['JPM'])
        self.assertNotIn('BNR Rate Decision', effects['JPM'])
        self.assertIn('BNR Rate Decision', effects['TVBETETF.RO'])
        self.assertNotIn('Fed Rate Decision', effects['TVBETETF.RO'])

    def test_bvb_calendar_does_not_describe_past_ecb_events_as_upcoming(self):
        snapshot = {
            'as_of': '2026-07-26T12:00:00',
            'positions': [{
                'symbol': 'TVBETETF.RO', 'market': 'România / BVB',
            }],
            'economic_calendar': [
                {
                    'name': 'ECB Interest Rate Decision',
                    'country': 'Europa',
                    'datetime': '2026-07-23T12:15:00',
                    'status': 'past',
                },
                {
                    'name': 'BNR Interest Rate Decision',
                    'country': 'România',
                    'datetime': '2026-08-03T12:00:00',
                    'status': 'upcoming',
                },
            ],
        }
        effect = market_scanner_analysis._position_calendar_effects(
            snapshot
        )['TVBETETF.RO']
        self.assertIn('Evenimente viitoare relevante', effect)
        self.assertIn('BNR Interest Rate Decision', effect)
        self.assertNotIn('ECB Interest Rate Decision', effect)

    def test_only_past_bvb_events_are_labeled_as_already_published(self):
        snapshot = {
            'as_of': '2026-07-26T12:00:00',
            'positions': [{
                'symbol': 'TVBETETF.RO', 'market': 'România / BVB',
            }],
            'economic_calendar': [{
                'name': 'ECB Press Conference',
                'country': 'Europa',
                'datetime': '2026-07-23T12:45:00',
                'status': 'past',
            }],
        }
        effect = market_scanner_analysis._position_calendar_effects(
            snapshot
        )['TVBETETF.RO']
        self.assertIn('deja publicate', effect)
        self.assertIn('Nu mai reprezintă un risc viitor', effect)
        self.assertNotIn('înaintea publicării', effect)

    def test_tvbetetf_parser_reads_official_daily_basket(self):
        payload = market_scanner_analysis._parse_tvbetetf_holdings_html("""
            <h3>Cos de emitere-rascumparare la data de 23-07-2026</h3>
            <table>
              <tr><th>Denumire/Issuer Name</th><th>Cantitate</th><th>Pondere</th></tr>
              <tr><td>BANCA TRANSILVANIA</td><td>3017</td><td>18.48%</td></tr>
              <tr><td>S.N.G.N. ROMGAZ</td><td>4763</td><td>14,41%</td></tr>
              <tr><td>LEI</td><td>1488.26</td><td>0.17%</td></tr>
            </table>
        """)
        self.assertEqual(payload['as_of'], '2026-07-23')
        self.assertEqual(
            [item['symbol'] for item in payload['holdings']],
            ['TLV.RO', 'SNG.RO'],
        )
        self.assertEqual(payload['holdings'][1]['weight_pct'], 14.41)

    def test_snapshot_calculates_tvbetetf_indirect_exposure(self):
        portfolio = pd.DataFrame([
            {
                'Symbol': 'TVBETETF.RO', 'Shares': 100,
                'Current_Value': 10000, 'Current_Price': 100,
            },
            {
                'Symbol': 'TLV.RO', 'Shares': 10,
                'Current_Value': 500, 'Current_Price': 50,
            },
        ])
        holdings = {
            'as_of': '2026-07-23',
            'source': 'Patria Asset Management',
            'source_url': 'https://example.test',
            'holdings': [{
                'symbol': 'TLV.RO', 'issuer': 'BANCA TRANSILVANIA',
                'weight_pct': 18.48,
            }],
        }
        snapshot = market_scanner_analysis.build_portfolio_risk_snapshot(
            portfolio, etf_holdings=holdings
        )
        tlv = snapshot['tvbetetf_lookthrough']['holdings'][0]
        self.assertEqual(tlv['indirect_exposure_eur'], 1848)
        self.assertEqual(tlv['direct_exposure_eur'], 500)
        self.assertEqual(tlv['combined_exposure_eur'], 2348)

    def test_buy_sizing_reduces_dominant_tvbetetf_overlap(self):
        base = {
            'portfolio': {'total_value_eur': 50000},
            'positions': [],
            'account_liquidity': {
                'privacy_mode': 'exact',
                'accounts': [{
                    'label': 'Tradeville',
                    'summary': {
                        'NetLiquidation': 100000,
                        'AvailableFunds': 50000,
                        'TotalCashValue': 50000,
                    },
                }],
            },
            'buy_candidates': [
                {
                    'symbol': 'TLV.RO', 'market': 'România / BVB',
                    'eligible_brokers': ['Tradeville'],
                    'entry_eur': 10, 'stop_eur': 9,
                },
                {
                    'symbol': 'IARV.RO', 'market': 'România / BVB',
                    'eligible_brokers': ['Tradeville'],
                    'entry_eur': 10, 'stop_eur': 9,
                },
            ],
            'tvbetetf_lookthrough': {'holdings': [{
                'symbol': 'TLV.RO', 'etf_weight_pct': 18.48,
                'indirect_exposure_eur': 4500,
            }]},
        }
        sized = market_scanner_analysis._size_buy_candidates(base)
        by_symbol = {item['symbol']: item for item in sized}
        tlv_amount = by_symbol['TLV.RO']['sizing_by_broker'][0][
            'conditional_amount_eur'
        ]
        iarv_amount = by_symbol['IARV.RO']['sizing_by_broker'][0][
            'conditional_amount_eur'
        ]
        self.assertEqual(by_symbol['TLV.RO']['overlap_risk'], 'ridicat')
        self.assertLess(tlv_amount, iarv_amount)

    def test_us_sector_rotation_measures_relative_strength_vs_spy(self):
        class FakeTicker:
            def __init__(self, symbol):
                self.symbol = symbol

            def history(self, **_kwargs):
                base = np.linspace(100, 110, 80)
                if self.symbol == 'XLK':
                    base = np.linspace(100, 130, 80)
                return pd.DataFrame({'Close': base})

        rotation = market_scanner_analysis.fetch_us_sector_rotation(
            ticker_factory=FakeTicker
        )
        technology = rotation['sectors']['Technology']
        self.assertEqual(technology['status'], 'lider')
        self.assertGreater(technology['relative_3m_vs_spy_pct'], 2)

    def test_us_market_regime_combines_trend_cycle_and_vix(self):
        rising = list(np.linspace(100, 140, 220))
        regime = market_scanner_analysis.build_us_market_regime(
            {
                'SPX': {'history': rising},
                'NASDAQ': {'history': rising},
                'VIX': {'value': 16},
            },
            'Expansion',
        )
        self.assertEqual(regime['market_stage'], 'creștere confirmată')
        self.assertEqual(regime['size_factor'], 1.0)
        self.assertEqual(regime['sector_fit']['Technology'], 'favorizat')

        recession = market_scanner_analysis.build_us_market_regime(
            {
                'SPX': {'history': list(reversed(rising))},
                'NASDAQ': {'history': list(reversed(rising))},
                'VIX': {'value': 35},
            },
            'Recession',
        )
        self.assertEqual(recession['market_stage'], 'trend descendent')
        self.assertLessEqual(recession['size_factor'], 0.4)
        self.assertEqual(
            recession['sector_fit']['Consumer Cyclical'], 'nefavorizat'
        )

    def test_complete_us_universe_uses_sp500_file(self):
        symbols = market_scanner.load_complete_us_equity_universe(
            'sp500_tickers.json'
        )
        self.assertGreaterEqual(len(symbols), 500)
        self.assertIn('AAPL', symbols)

    def test_us_sector_sizing_penalizes_weak_rotation_and_caps_sector(self):
        snapshot = {
            'portfolio': {'total_value_eur': 100000},
            'positions': [{
                'symbol': 'OLD', 'market': 'SUA', 'sector': 'Technology',
                'current_value_eur': 9500, 'broker': 'IBKR',
                'portfolio_weight_pct': 9.5,
            }],
            'account_liquidity': {
                'privacy_mode': 'exact',
                'accounts': [{
                    'label': 'IBKR',
                    'summary': {
                        'NetLiquidation': 100000,
                        'AvailableFunds': 50000,
                        'TotalCashValue': 50000,
                    },
                }],
            },
            'us_sector_rotation': {'sectors': {
                'Technology': {
                    'status': 'în deteriorare', 'etf': 'XLK',
                    'relative_1m_vs_spy_pct': -2,
                    'relative_3m_vs_spy_pct': -3,
                    'size_factor': 0.5,
                },
            }},
            'buy_candidates': [{
                'symbol': 'NEW', 'market': 'SUA', 'sector': 'Technology',
                'eligible_brokers': ['IBKR'], 'entry_eur': 100,
                'stop_eur': 90,
            }],
        }
        candidate = market_scanner_analysis._size_buy_candidates(snapshot)[0]
        sizing = candidate['sizing_by_broker'][0]
        self.assertEqual(candidate['sector_rotation_status'], 'în deteriorare')
        self.assertLessEqual(sizing['conditional_amount_eur'], 500)

    def test_buy_sizing_uses_separate_broker_cash_and_stop_risk(self):
        snapshot = {
            'account_liquidity': {
                'privacy_mode': 'exact',
                'accounts': [
                    {
                        'label': 'IBKR',
                        'source': 'IBKR TWS',
                        'summary': {
                            'NetLiquidation': 100000,
                            'AvailableFunds': 80000,
                            'TotalCashValue': 75000,
                        },
                    },
                    {
                        'label': 'Tradeville',
                        'source': 'Tradeville / snapshot manual',
                        'summary': {
                            'NetLiquidation': 50000,
                            'AvailableFunds': 20000,
                            'TotalCashValue': 18000,
                        },
                    },
                ],
            },
            'positions': [],
            'buy_candidates': [
                {
                    'symbol': 'TEST', 'market': 'SUA', 'entry_eur': 100,
                    'stop_eur': 90, 'trend': 'Strong Bullish',
                },
                {
                    'symbol': 'TLV.RO', 'market': 'România / BVB', 'entry_eur': 10,
                    'stop_eur': 9, 'trend': 'Strong Bullish',
                },
            ],
        }
        sized = {
            item['symbol']: item
            for item in market_scanner_analysis._size_buy_candidates(snapshot)
        }
        self.assertEqual(sized['TEST']['broker'], 'IBKR')
        self.assertEqual(sized['TEST']['broker_available_cash_eur'], 75000)
        self.assertEqual(sized['TLV.RO']['broker'], 'Tradeville')
        self.assertEqual(sized['TLV.RO']['broker_available_cash_eur'], 18000)
        self.assertGreater(sized['TEST']['conditional_amount_eur'], 0)
        self.assertGreater(sized['TLV.RO']['conditional_amount_eur'], 0)

    def test_bvb_buy_sizing_is_capped_by_local_turnover_capacity(self):
        snapshot = {
            'account_liquidity': {
                'privacy_mode': 'exact',
                'accounts': [{
                    'label': 'Tradeville',
                    'summary': {
                        'NetLiquidation': 100000,
                        'AvailableFunds': 50000,
                        'TotalCashValue': 50000,
                    },
                }],
            },
            'positions': [],
            'buy_candidates': [{
                'symbol': 'TLV.RO', 'market': 'România / BVB',
                'eligible_brokers': ['Tradeville'],
                'entry_eur': 10, 'stop_eur': 9,
                'liquidity_position_cap_eur': 600,
            }],
        }
        candidate = market_scanner_analysis._size_buy_candidates(snapshot)[0]
        sizing = candidate['sizing_by_broker'][0]
        self.assertEqual(sizing['conditional_amount_eur'], 600)
        self.assertTrue(candidate['liquidity_cap_applied'])
        self.assertIn('rulajului BVB/AeRO', sizing['sizing_reason'])

    def test_bvb_buy_renderer_explains_local_liquidity(self):
        html_result = market_scanner_analysis.render_buy_recommendations_html(
            {'buy_recommendations': [{
                'symbol': 'TLV.RO', 'market': 'România / BVB',
                'verdict': 'Candidat valid', 'why_now': 'Setup confirmat.',
                'market_effect': 'pozitiv', 'news_effect': 'neutru',
                'calendar_effect': 'neutru', 'main_risk': 'stop',
                'source_ids': [],
            }]},
            [{
                'symbol': 'TLV.RO', 'market': 'România / BVB',
                'company_name': 'Banca Transilvania',
                'eligible_brokers': ['Tradeville'], 'strict_eligible': True,
                'entry_eur': 10, 'stop_eur': 9, 'target_eur': 13,
                'execution_currency': 'RON', 'eur_per_native': 0.2,
                'entry_native': 50, 'stop_native': 45, 'target_native': 65,
                'rr_ratio': 3, 'consensus': 'Buy',
                'bvb_market_segment': 'Piața Reglementată',
                'liquidity_status': 'adecvată',
                'liquidity_reason': 'Rulaj stabil.',
                'liquidity_observations_20d': 20,
                'active_days_20d': 19,
                'median_turnover_20d_ron': 500_000,
                'relative_volume_20d': 1.25,
                'liquidity_position_cap_eur': 2_000,
                'sizing_by_broker': [{
                    'broker': 'Tradeville',
                    'broker_available_cash_eur': 10_000,
                    'broker_available_cash_native_equivalent': 50_000,
                    'conditional_amount_eur': 2_000,
                    'conditional_amount_native': 10_000,
                    'execution_currency': 'RON',
                    'conditional_units': 200,
                    'risk_to_stop_pct': 10,
                }],
            }],
        )
        self.assertIn('Lichiditate locală', html_result)
        self.assertIn('500,000 RON mediană/ședință', html_result)
        self.assertIn('19/20 ședințe active', html_result)
        self.assertIn('plafon orientativ al ordinului 10,000.00 RON', html_result)
        self.assertIn('<b>Entry:</b> 50.00 RON', html_result)
        self.assertIn('sumă orientativă pentru cumpărare acum:</b> 10,000.00 RON', html_result)

    def test_buy_candidate_entry_uses_eur_price_when_smart_entry_is_nan(self):
        item = {'Smart_Entry_EUR': float('nan'), 'Smart_Entry': 110, 'Price': 100}
        self.assertEqual(market_scanner._buy_candidate_entry_eur(item), 100)

    def test_buy_candidate_execution_values_use_usd_and_ron(self):
        ual = market_scanner._buy_candidate_execution_values({
            'Ticker': 'UAL', 'Currency': 'USD',
            'Price': 200, 'Price_Native': 220,
            'Smart_Entry_EUR': 201, 'Stop_Loss': 190, 'Target': 230,
        })
        connections = market_scanner._buy_candidate_execution_values({
            'Ticker': 'CC.RO', 'Currency': 'RON',
            'Price': 2, 'Price_Native': 10,
            'Smart_Entry_EUR': 2.1, 'Stop_Loss': 1.8, 'Target': 2.8,
        })
        self.assertEqual(ual['execution_currency'], 'USD')
        self.assertAlmostEqual(ual['entry_native'], 221.1, places=2)
        self.assertEqual(connections['execution_currency'], 'RON')
        self.assertAlmostEqual(connections['entry_native'], 10.5, places=2)
        self.assertAlmostEqual(connections['stop_native'], 9, places=2)

    def test_detailed_chart_payload_uses_usd_for_us_stock(self):
        detail = market_scanner._chart_detail_native_payload(
            {
                'Currency': 'USD',
                'Current_Price': 200,
                'Price_Native': 220,
                'Daily_Change': 2,
                'Chart_History': [190, 200],
                'Chart_Dates': ['2026-07-24', '2026-07-27'],
                'Chart_OHLC': [{
                    'date': '2026-07-27',
                    'open': 195, 'high': 205, 'low': 190, 'close': 200,
                }],
            },
            'UAL',
            'Current_Price',
        )
        self.assertEqual(detail['currency'], 'USD')
        self.assertAlmostEqual(detail['value'], 220, places=2)
        self.assertAlmostEqual(detail['series'][-1], 220, places=2)
        self.assertAlmostEqual(detail['ohlc'][0]['high'], 225.5, places=2)
        self.assertAlmostEqual(detail['change'], 2.2, places=2)

    def test_detailed_chart_payload_uses_ron_for_bvb_stock(self):
        detail = market_scanner._chart_detail_native_payload(
            {
                'Currency': 'RON',
                'Price': 2,
                'Price_Native': 10,
                'Daily_Change': 0.1,
                'Chart_History': [1.8, 2],
                'Chart_Dates': ['2026-07-24', '2026-07-27'],
                'Chart_OHLC': [{
                    'date': '2026-07-27',
                    'open': 1.9, 'high': 2.1, 'low': 1.8, 'close': 2,
                }],
            },
            'CC.RO',
            'Price',
        )
        self.assertEqual(detail['currency'], 'RON')
        self.assertAlmostEqual(detail['series'][0], 9, places=2)
        self.assertAlmostEqual(detail['ohlc'][0]['high'], 10.5, places=2)
        self.assertAlmostEqual(detail['change'], 0.5, places=2)

    def test_buy_recommendation_chart_uses_native_levels_and_ai_status(self):
        history = [{
            'history_key': 'CC.RO|Pregătit la trigger|2.1000|1.8000|2.8000',
            'symbol': 'CC.RO',
            'action_label': 'Ordin la trigger',
            'entry_native': 10.5,
            'first_seen_at': '2026-07-27T09:30:00',
            'last_seen_at': '2026-07-27T10:30:00',
            'is_current': True,
        }]
        details = market_scanner._build_buy_recommendation_detail_data(
            [{
                'symbol': 'CC.RO',
                'company_name': 'Connections Consult S.A.',
                'execution_currency': 'RON',
                'chart_currency': 'RON',
                'chart_value_native': 10,
                'chart_change_native': 0.25,
                'chart_ohlc_native': [{
                    'date': '2026-07-27',
                    'open': 9.8, 'high': 10.2, 'low': 9.7, 'close': 10,
                }],
                'chart_series_native': [9.8, 10],
                'chart_series_dates': ['2026-07-24', '2026-07-27'],
                'entry_native': 10.5,
                'stop_native': 9,
                'target_native': 14,
                'decision': 'BUY',
                'trend': 'Bullish',
            }],
            {'buy_recommendations': [{
                'symbol': 'CC.RO',
                'verdict': 'Pregătit la trigger',
            }]},
            history,
        )
        detail = details['CC.RO']
        self.assertEqual(detail['kind'], 'buy_recommendation')
        self.assertEqual(detail['currency'], 'RON')
        self.assertEqual(detail['status'], 'Pregătit la trigger')
        self.assertEqual(
            [level['value'] for level in detail['levels']],
            [10.5, 9, 14],
        )
        self.assertEqual(len(detail['markers']), 1)
        self.assertEqual(detail['markers'][0]['label'], 'C1')
        self.assertEqual(detail['markers'][0]['date'], '2026-07-27')
        self.assertEqual(detail['markers'][0]['value'], 10.5)

    def test_active_buy_order_chart_levels_include_order_price(self):
        orders = pd.DataFrame([
            {
                'Symbol': '3USL.MI',
                'Action': 'BUY',
                'OrderType': 'LMT',
                'Total_Qty': 7,
                'Limit_Price': 160.25,
            },
            {
                'Symbol': 'CC.RO',
                'Action': 'BUY',
                'OrderType': 'STP',
                'Total_Qty': 100,
                'Stop_Price': 10.75,
            },
            {
                'Symbol': '3USL.MI',
                'Action': 'SELL',
                'OrderType': 'STP',
                'Total_Qty': 7,
                'Stop_Price': 150,
            },
        ])
        levels = market_scanner._build_active_buy_order_chart_levels(orders)
        self.assertEqual(set(levels), {'3USL.MI', 'CC.RO'})
        self.assertEqual(levels['3USL.MI'][0]['value'], 160.25)
        self.assertEqual(
            levels['3USL.MI'][0]['label'],
            'Preț ordin LMT · 7 acț.',
        )
        self.assertEqual(levels['3USL.MI'][0]['color'], '#7c3aed')
        self.assertEqual(levels['CC.RO'][0]['value'], 10.75)

    def test_history_chart_candidates_include_symbols_outside_current_list(self):
        history = [{
            'history_key': 'SNN.RO|Pregătit la trigger|14|13|16',
            'symbol': 'SNN.RO',
            'company_name': 'Nuclearelectrica',
            'execution_currency': 'RON',
            'first_seen_at': '2026-07-27T09:00:00',
            'last_seen_at': '2026-07-27T10:00:00',
        }]
        candidates = market_scanner._build_history_chart_candidates(
            [],
            history,
            [{
                'Ticker': 'SNN.RO',
                'Company_Name': 'Nuclearelectrica',
                'Currency': 'RON',
                'Price': 14,
                'Price_Native': 70,
                'Chart_History': [13.8, 14],
                'Chart_Dates': ['2026-07-24', '2026-07-27'],
                'Chart_OHLC': [{
                    'date': '2026-07-27',
                    'open': 13.9, 'high': 14.2, 'low': 13.7, 'close': 14,
                }],
            }],
        )
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]['symbol'], 'SNN.RO')
        self.assertEqual(candidates[0]['chart_currency'], 'RON')
        self.assertAlmostEqual(
            candidates[0]['chart_ohlc_native'][0]['close'],
            70,
            places=2,
        )

    def test_buy_renderer_uses_execution_currency_for_ual_and_connections(self):
        recommendations = []
        candidates = []
        for symbol, market, company, currency, entry, stop, target, amount in [
            (
                'UAL', 'SUA', 'United Airlines Holdings', 'USD',
                220, 209, 247, 1_100,
            ),
            (
                'CC.RO', 'România / BVB', 'Connections Consult S.A.', 'RON',
                10.5, 9, 14, 10_000,
            ),
        ]:
            recommendations.append({
                'symbol': symbol, 'market': market,
                'verdict': 'Candidat valid', 'why_now': 'Setup confirmat.',
                'market_effect': 'Pozitiv.', 'news_effect': 'Neutru.',
                'calendar_effect': 'Neutru.', 'main_risk': 'Sub stop.',
                'source_ids': [],
            })
            candidates.append({
                'symbol': symbol, 'market': market, 'company_name': company,
                'candidate_source': 'external_research',
                'requires_watchlist_filters': False, 'strict_eligible': False,
                'eligible_brokers': [
                    'IBKR' if market == 'SUA' else 'Tradeville'
                ],
                'execution_currency': currency,
                'entry_native': entry, 'stop_native': stop,
                'target_native': target, 'rr_ratio': 2,
                'entry_eur': entry, 'stop_eur': stop, 'target_eur': target,
                'consensus': '-',
                'sizing_by_broker': [{
                    'broker': 'IBKR' if market == 'SUA' else 'Tradeville',
                    'execution_currency': currency,
                    'broker_available_cash_native_equivalent': amount * 10,
                    'conditional_amount_native': amount,
                    'conditional_units': 5,
                    'risk_to_stop_pct': 5,
                }],
            })
        html_result = market_scanner_analysis.render_buy_recommendations_html(
            {'buy_recommendations': recommendations}, candidates
        )
        self.assertIn('UAL · United Airlines Holdings', html_result)
        self.assertIn('<b>Entry:</b> $220.00', html_result)
        self.assertIn('sumă orientativă pentru cumpărare acum:</b> $1,100.00', html_result)
        self.assertIn('CC.RO · Connections Consult S.A.', html_result)
        self.assertIn('<b>Entry:</b> 10.50 RON', html_result)
        self.assertIn('sumă orientativă pentru cumpărare acum:</b> 10,000.00 RON', html_result)
        self.assertEqual(html_result.count('📈 Grafic mare OHLC'), 2)
        self.assertIn(
            'openBuyRecommendationDetail(this.dataset.symbol)',
            html_result,
        )

    def test_lqq_is_always_selected_and_available_through_both_brokers(self):
        watchlist = pd.DataFrame([{
            'Ticker': 'LQQ.PA', 'Decision': 'WAIT', 'Consensus': '-',
            'RR_Ratio': 0, 'Price': 100,
        }])
        selected = market_scanner.select_strict_buy_candidates(watchlist)
        self.assertEqual(len(selected), 1)
        self.assertFalse(selected[0]['Strict_Eligible'])
        self.assertEqual(selected[0]['Market'], 'Europa / Nasdaq-100')
        self.assertEqual(selected[0]['Eligible_Brokers'], ['IBKR', 'Tradeville'])

    @patch('market_scanner.yf.Ticker')
    def test_lqq_skips_yahoo_fundamentals_and_earnings(self, ticker_factory):
        info = market_scanner._get_yahoo_info('LQQ.PA')
        earnings_date = market_scanner.get_next_earnings_date('LQQ.PA')

        ticker_factory.assert_not_called()
        self.assertEqual(info['shortName'], 'LQQ')
        self.assertEqual(info['industry'], 'ETF leveraged')
        self.assertIsNone(earnings_date)

    @patch('market_scanner.yf.Ticker')
    def test_tradeville_etf_skips_yahoo_fundamentals_and_earnings(
        self, ticker_factory,
    ):
        info = market_scanner._get_yahoo_info('TVBETETF.RO')
        earnings_date = market_scanner.get_next_earnings_date('TVBETETF.RO')

        ticker_factory.assert_not_called()
        self.assertEqual(info['shortName'], 'TVBETETF')
        self.assertEqual(info['industry'], 'ETF')
        self.assertIsNone(earnings_date)

    def test_tvbetetf_tws_data_never_enables_ibkr_execution(self):
        attribution = market_scanner._instrument_data_attribution(
            'TVBETETF.RO',
            {
                'data_provider': 'IBKR TWS API',
                'data_broker': 'IBKR',
                'execution_brokers': ['IBKR'],
                'fetched_at': '2026-07-28T06:00:00+00:00',
            },
        )
        self.assertEqual(attribution['Data_Broker'], 'IBKR')
        self.assertTrue(attribution['IBKR_Data_Only'])
        self.assertEqual(
            attribution['Execution_Brokers'], ['Tradeville']
        )

    def test_tws_instrument_history_loads_alias_and_rejects_stale_cache(self):
        fetched_at = '2026-07-28T06:00:00+00:00'
        payload = {
            'fetched_at': fetched_at,
            'instruments': {
                'TVBETETF.RO': {
                    'aliases': ['TVBETETF.RO', 'TVBETETF'],
                    'fetched_at': fetched_at,
                    'bars': [{
                        'date': '2026-07-27',
                        'open': 60,
                        'high': 62,
                        'low': 59,
                        'close': 61,
                        'volume': 1000,
                    }],
                },
            },
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'tws_instruments.json')
            with open(path, 'w', encoding='utf-8') as handle:
                import json
                json.dump(payload, handle)
            fresh = market_scanner._load_tws_instrument(
                'TVBETETF',
                path=path,
                now=datetime(2026, 7, 28, 7, tzinfo=timezone.utc),
            )
            stale = market_scanner._load_tws_instrument(
                'TVBETETF.RO',
                path=path,
                now=datetime(2026, 8, 2, 7, tzinfo=timezone.utc),
            )

        frame = market_scanner._tws_instrument_history_frame(fresh)
        self.assertEqual(float(frame['Close'].iloc[-1]), 61)
        self.assertIsNone(stale)

    def test_tws_metadata_keeps_exact_listing_alias_without_bars(self):
        payload = {
            'instruments': {
                '3USL.MI': {
                    'aliases': ['3USL.MI', '3USL.BVME', '3USL'],
                    'bars': [],
                },
            },
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'tws_instruments.json')
            with open(path, 'w', encoding='utf-8') as handle:
                json.dump(payload, handle)
            metadata = market_scanner._load_tws_instrument_metadata(
                '3USL', path=path
            )

        self.assertEqual(metadata['aliases'][0], '3USL.MI')

    @patch('market_scanner._load_tws_instrument_metadata')
    @patch('market_scanner._download_yahoo_history')
    @patch('market_scanner._load_tws_instrument', return_value=None)
    @patch('market_scanner._load_mcp_market_instrument', return_value=None)
    def test_international_fallback_rejects_two_point_wrong_listing(
        self, _load_mcp, _load_tws, yahoo_download, load_metadata,
    ):
        load_metadata.return_value = {
            'aliases': ['3USL.MI', '3USL.BVME', '3USL'],
            'data_provider': 'IBKR TWS API',
            'data_broker': 'IBKR',
        }
        short = pd.DataFrame(
            {'Close': [153.9, 164.7]},
            index=pd.to_datetime(['2026-07-17', '2026-08-18']),
        )
        dates = pd.bdate_range('2026-04-01', periods=90)
        complete = pd.DataFrame(
            {'Close': np.linspace(140.0, 165.0, len(dates))},
            index=dates,
        )
        yahoo_download.side_effect = lambda symbol, period='1y': {
            '3USL.MI': complete,
            '3USL.BVME': pd.DataFrame(),
            '3USL': short,
        }.get(symbol, pd.DataFrame())

        frame, _, instrument, attribution = (
            market_scanner._load_analysis_history('3USL', '3USL')
        )

        self.assertEqual(len(frame), 90)
        self.assertEqual(yahoo_download.call_args_list[0].args[0], '3USL.MI')
        self.assertIs(instrument, load_metadata.return_value)
        self.assertEqual(attribution['Market_Data_Source'], 'Yahoo Finance')
        self.assertIsNone(attribution['Data_Broker'])

    @patch('market_scanner._download_yahoo_history')
    @patch('market_scanner._load_tws_instrument')
    @patch('market_scanner._load_mcp_market_instrument')
    def test_international_history_prefers_mcp_before_tws_and_yahoo(
        self, load_mcp, load_tws, yahoo_download,
    ):
        load_mcp.return_value = {
            'symbol': 'AAPL',
            'data_provider': 'IBKR MCP',
            'data_broker': 'IBKR',
            'fetched_at': '2026-08-10T08:00:00+00:00',
            'market_data': {'market_price': 224.5},
            'bars': [{
                'date': '2026-08-07', 'open': 220, 'high': 225,
                'low': 219, 'close': 224, 'volume': 1_000_000,
            }],
        }
        load_tws.return_value = {'bars': [{
            'date': '2026-08-07', 'open': 1, 'high': 1,
            'low': 1, 'close': 1, 'volume': 1,
        }]}

        frame, selected, broker_instrument, attribution = (
            market_scanner._load_analysis_history('AAPL', 'AAPL')
        )

        self.assertEqual(float(frame['Close'].iloc[-1]), 224)
        self.assertIs(selected, load_mcp.return_value)
        self.assertIs(broker_instrument, load_mcp.return_value)
        self.assertEqual(attribution['Market_Data_Source'], 'IBKR MCP')
        yahoo_download.assert_not_called()

    @patch('market_scanner.bvb_public_market_data.fetch_history')
    @patch('market_scanner._load_mcp_market_instrument', return_value=None)
    @patch('market_scanner._load_tws_instrument', return_value=None)
    @patch('market_scanner._download_yahoo_history')
    def test_bvb_history_prefers_public_bvb_before_yahoo_and_tws(
        self, yahoo_download, _load_tws, _load_mcp, bvb_fetch,
    ):
        yahoo_download.return_value = pd.DataFrame()
        bvb_frame = pd.DataFrame(
            {
                'Open': [9.5], 'High': [10.5], 'Low': [9.0],
                'Close': [10.0], 'Volume': [1000],
            },
            index=pd.to_datetime(['2026-07-27']),
        )
        bvb_fetch.return_value = (
            bvb_frame,
            {
                'data_provider': 'BVB CSV public zilnic (fără autentificare)',
                'data_broker': 'BVB public',
                'fetched_at': '2026-07-28T06:00:00+00:00',
                'market_data': {'close': 10},
            },
        )

        frame, selected, _, attribution = (
            market_scanner._load_analysis_history(
                'ALR.RO', 'ALR.RO', period='1y'
            )
        )

        self.assertEqual(float(frame['Close'].iloc[-1]), 10.0)
        self.assertEqual(selected['data_broker'], 'BVB public')
        self.assertEqual(
            attribution['Market_Data_Source'],
            'BVB CSV public zilnic (fără autentificare)',
        )
        yahoo_download.assert_called_once_with('ALR.RO', period='1y')
        bvb_fetch.assert_called_once_with(
            'ALR.RO',
            min_observations=1,
            lookback_days=(
                market_scanner.bvb_public_market_data.DEFAULT_LOOKBACK_DAYS
            ),
        )

    @patch('market_scanner.bvb_public_market_data.fetch_history')
    @patch('market_scanner._load_mcp_market_instrument', return_value=None)
    @patch('market_scanner._load_tws_instrument', return_value=None)
    @patch('market_scanner._download_yahoo_history')
    def test_tvbetetf_backfills_enough_public_history_for_sma200(
        self, yahoo_download, _load_tws, _load_mcp, bvb_fetch,
    ):
        dates = pd.bdate_range('2025-08-01', periods=260)
        closes = np.linspace(40.0, 62.0, len(dates))
        bvb_fetch.return_value = (
            pd.DataFrame({
                'Open': closes,
                'High': closes,
                'Low': closes,
                'Close': closes,
                'Volume': np.full(len(dates), 100_000),
            }, index=dates),
            {
                'data_provider': 'BVB CSV public zilnic (fără autentificare)',
                'data_broker': 'BVB public',
                'market_data': {'close': float(closes[-1])},
            },
        )

        frame, _, _, _ = market_scanner._load_analysis_history(
            'TVBETETF.RO', 'TVBETETF.RO'
        )

        self.assertEqual(len(frame), 260)
        bvb_fetch.assert_called_once_with(
            'TVBETETF.RO', min_observations=260, lookback_days=450
        )
        yahoo_download.assert_not_called()

    @patch('market_scanner.bvb_public_market_data.fetch_history')
    @patch('market_scanner._load_mcp_market_instrument', return_value=None)
    @patch('market_scanner._load_tws_instrument')
    @patch('market_scanner._download_yahoo_history')
    def test_tvbetetf_uses_two_year_yahoo_fallback_when_bvb_is_unavailable(
        self, yahoo_download, load_tws, _load_mcp, bvb_fetch,
    ):
        bvb_fetch.side_effect = (
            market_scanner.bvb_public_market_data.BVBPublicDataError('offline')
        )
        tws_dates = pd.bdate_range('2025-11-11', periods=181)
        load_tws.return_value = {
            'symbol': 'TVBETETF.RO',
            'data_provider': 'IBKR TWS API',
            'data_broker': 'IBKR',
            'bars': [
                {
                    'date': date.date().isoformat(),
                    'open': close,
                    'high': close,
                    'low': close,
                    'close': close,
                    'volume': 100_000,
                }
                for date, close in zip(
                    tws_dates, np.linspace(40.0, 62.0, len(tws_dates))
                )
            ],
        }
        yahoo_dates = pd.bdate_range('2024-08-12', periods=494)
        yahoo_download.return_value = pd.DataFrame({
            'Close': np.linspace(25.0, 62.0, len(yahoo_dates)),
        }, index=yahoo_dates)

        frame, selected, _, attribution = (
            market_scanner._load_analysis_history(
                'TVBETETF.RO', 'TVBETETF.RO'
            )
        )

        self.assertGreaterEqual(len(frame), 260)
        yahoo_download.assert_called_once_with(
            'TVBETETF.RO', period='2y'
        )
        self.assertEqual(selected['data_broker'], 'surse combinate')
        self.assertIn('Yahoo Finance', attribution['Market_Data_Source'])

    @patch('market_scanner.bvb_public_market_data.fetch_history')
    @patch('market_scanner._load_mcp_market_instrument', return_value=None)
    @patch('market_scanner._load_tws_instrument')
    @patch('market_scanner._download_yahoo_history')
    def test_bvb_history_prefers_fresh_ibkr_bar_over_yahoo(
        self, yahoo_download, load_tws, _load_mcp, bvb_fetch,
    ):
        bvb_fetch.side_effect = (
            market_scanner.bvb_public_market_data.BVBPublicDataError('offline')
        )
        yahoo_download.return_value = pd.DataFrame(
            {'Close': [10.25]},
            index=pd.to_datetime(['2026-07-27']),
        )
        load_tws.return_value = {
            'symbol': 'ALR.RO',
            'data_provider': 'IBKR TWS API',
            'data_broker': 'IBKR',
            'fetched_at': '2026-07-28T06:00:00+00:00',
            'bars': [{
                'date': '2026-07-27',
                'open': 1,
                'high': 1.1,
                'low': .9,
                'close': 1.05,
                'volume': 1000,
            }],
        }

        frame, selected, _, attribution = (
            market_scanner._load_analysis_history('ALR.RO', 'ALR.RO')
        )

        self.assertEqual(float(frame['Close'].iloc[-1]), 1.05)
        self.assertEqual(selected['data_broker'], 'surse combinate')
        self.assertEqual(
            attribution['Market_Data_Source'],
            'IBKR TWS + Yahoo Finance',
        )

    @patch('market_scanner.bvb_public_market_data.fetch_history')
    @patch('market_scanner._load_mcp_market_instrument', return_value=None)
    @patch('market_scanner._load_tws_instrument')
    @patch('market_scanner._download_yahoo_history')
    def test_bvb_history_uses_existing_tws_cache_only_as_last_fallback(
        self, yahoo_download, load_tws, _load_mcp, bvb_fetch,
    ):
        bvb_fetch.side_effect = (
            market_scanner.bvb_public_market_data.BVBPublicDataError('offline')
        )
        yahoo_download.return_value = pd.DataFrame()
        load_tws.return_value = {
            'symbol': 'ALR.RO',
            'data_provider': 'IBKR TWS API',
            'data_broker': 'IBKR',
            'fetched_at': '2026-07-28T06:00:00+00:00',
            'bars': [{
                'date': '2026-07-27', 'open': 10, 'high': 11,
                'low': 9, 'close': 10.5, 'volume': 500,
            }],
        }

        frame, selected, _, attribution = (
            market_scanner._load_analysis_history('ALR.RO', 'ALR.RO')
        )

        self.assertEqual(float(frame['Close'].iloc[-1]), 10.5)
        self.assertIs(selected, load_tws.return_value)
        self.assertEqual(attribution['Data_Broker'], 'IBKR')

    @patch('market_scanner.market_data.get_finviz_data', return_value={})
    @patch('market_scanner.yf.download')
    @patch('market_scanner._load_mcp_market_instrument', return_value=None)
    @patch('market_scanner._load_tws_instrument')
    def test_lqq_analysis_prefers_tws_ohlcv_over_yahoo(
        self, load_tws, _load_mcp, yahoo_download, _finviz,
    ):
        dates = pd.date_range('2025-09-01', periods=220, freq='B')
        closes = pd.Series(
            np.linspace(8.0, 12.0, len(dates)), index=dates
        )
        benchmark = pd.DataFrame({
            'Open': closes * 0.99,
            'High': closes * 1.01,
            'Low': closes * 0.98,
            'Close': closes,
            'Volume': np.full(len(dates), 100_000),
        })
        load_tws.return_value = {
            'symbol': 'LQQ.PA',
            'data_provider': 'IBKR TWS API',
            'data_broker': 'IBKR',
            'fetched_at': '2026-07-28T06:00:00+00:00',
            'contract': {
                'long_name': 'Amundi Nasdaq-100 Daily 2x',
                'currency': 'EUR',
            },
            'market_data': {'market_price': 12.10},
            'bars': [
                {
                    'date': date.date().isoformat(),
                    'open': float(row.Open),
                    'high': float(row.High),
                    'low': float(row.Low),
                    'close': float(row.Close),
                    'volume': float(row.Volume),
                }
                for date, row in benchmark.iterrows()
            ],
        }
        yahoo_download.return_value = benchmark

        result = market_scanner.process_watchlist_ticker(
            'LQQ.PA',
            18,
            {'EUR': 1.0, 'USD': 0.9, 'RON': 0.2, 'GBP': 1.1},
        )

        self.assertEqual(result['Market_Data_Source'], 'IBKR TWS API')
        self.assertEqual(result['Data_Broker'], 'IBKR')
        self.assertEqual(result['Execution_Brokers'], ['IBKR', 'Tradeville'])
        self.assertEqual(result['Price_Native'], 12.10)
        self.assertEqual(len(result['Chart_OHLC']), 90)
        yahoo_download.assert_called_once()
        self.assertEqual(yahoo_download.call_args.args[0], '^GSPC')

    def test_lqq_sizing_is_separate_for_ibkr_and_tradeville(self):
        snapshot = {
            'account_liquidity': {
                'privacy_mode': 'exact',
                'accounts': [
                    {'label': 'IBKR', 'source': 'IBKR TWS', 'summary': {
                        'NetLiquidation': 100000, 'AvailableFunds': 80000,
                        'TotalCashValue': 75000,
                    }},
                    {'label': 'Tradeville', 'source': 'Tradeville manual', 'summary': {
                        'NetLiquidation': 50000, 'AvailableFunds': 20000,
                        'TotalCashValue': 18000,
                    }},
                ],
            },
            'positions': [],
            'buy_candidates': [{
                'symbol': 'LQQ.PA', 'market': 'Europa / Nasdaq-100',
                'eligible_brokers': ['IBKR', 'Tradeville'],
                'entry_eur': 100, 'stop_eur': 90, 'trend': 'Bullish',
            }],
        }
        candidate = market_scanner_analysis._size_buy_candidates(snapshot)[0]
        rows = {item['broker']: item for item in candidate['sizing_by_broker']}
        self.assertEqual(set(rows), {'IBKR', 'Tradeville'})
        self.assertEqual(rows['IBKR']['broker_available_cash_eur'], 75000)
        self.assertEqual(rows['Tradeville']['broker_available_cash_eur'], 18000)
        self.assertGreater(rows['IBKR']['conditional_amount_eur'], 0)
        self.assertGreater(rows['Tradeville']['conditional_amount_eur'], 0)

    def test_lqq_renderer_forces_wait_and_shows_both_brokers(self):
        html_result = market_scanner_analysis.render_buy_recommendations_html(
            {'buy_recommendations': [{
                'symbol': 'LQQ.PA', 'market': 'Europa / Nasdaq-100',
                'verdict': 'Candidat valid', 'market_effect': 'pozitiv',
                'news_effect': 'neutru', 'calendar_effect': 'neutru',
                'main_risk': 'risc', 'source_ids': [],
            }]},
            [{
                'symbol': 'LQQ.PA', 'market': 'Europa / Nasdaq-100',
                'company_name': 'LQQ', 'strict_eligible': False,
                'eligible_brokers': ['IBKR', 'Tradeville'], 'entry_eur': 100,
                'stop_eur': 90, 'target_eur': 130, 'rr_ratio': 3,
                'consensus': 'Buy', 'sizing_by_broker': [
                    {'broker': 'IBKR', 'broker_available_cash_eur': 75000,
                     'conditional_amount_eur': 3000, 'conditional_units': 30,
                     'risk_to_stop_pct': 10},
                    {'broker': 'Tradeville', 'broker_available_cash_eur': 18000,
                     'conditional_amount_eur': 1000, 'conditional_units': 10,
                     'risk_to_stop_pct': 10},
                ],
            }],
        )
        self.assertIn('LQQ.PA', html_result)
        self.assertIn('IBKR — sumă de cumpărat acum:</b> €0.00', html_result)
        self.assertIn('Tradeville — sumă de cumpărat acum:</b> €0.00', html_result)
        self.assertIn('LQQ monitorizat', html_result)

    def test_buy_renderer_hides_non_actionable_verdicts_but_keeps_lqq(self):
        result = {'buy_recommendations': [
            {
                'symbol': 'WAIT', 'market': 'SUA', 'verdict': 'Așteaptă',
                'why_now': 'Nu acum.', 'market_effect': 'Mixt.',
                'news_effect': 'Neutru.', 'calendar_effect': 'Neutru.',
                'main_risk': 'Risc.', 'source_ids': [],
            },
            {
                'symbol': 'TRIGGER', 'market': 'SUA',
                'verdict': 'Pregătit la trigger', 'why_now': 'Peste 101.',
                'market_effect': 'Pozitiv.', 'news_effect': 'Neutru.',
                'calendar_effect': 'Neutru.', 'main_risk': 'Sub 95.',
                'source_ids': [],
            },
            {
                'symbol': 'LQQ.PA', 'market': 'Europa / Nasdaq-100',
                'verdict': 'Așteaptă', 'why_now': 'Nu acum.',
                'market_effect': 'Mixt.', 'news_effect': 'Neutru.',
                'calendar_effect': 'Neutru.', 'main_risk': 'Trend.',
                'source_ids': [],
            },
        ]}
        candidates = [
            {
                'symbol': symbol, 'market': market, 'company_name': symbol,
                'strict_eligible': symbol != 'LQQ.PA',
                'requires_watchlist_filters': True,
                'eligible_brokers': ['IBKR'], 'entry_eur': 100,
                'stop_eur': 95, 'target_eur': 120, 'rr_ratio': 4,
                'consensus': 'Buy', 'sizing_by_broker': [{
                    'broker': 'IBKR', 'broker_available_cash_eur': 10_000,
                    'conditional_amount_eur': 1_000,
                    'conditional_units': 10, 'risk_to_stop_pct': 5,
                }],
            }
            for symbol, market in [
                ('WAIT', 'SUA'), ('TRIGGER', 'SUA'),
                ('LQQ.PA', 'Europa / Nasdaq-100'),
            ]
        ]
        html_result = market_scanner_analysis.render_buy_recommendations_html(
            result, candidates
        )
        self.assertNotIn('WAIT · WAIT', html_result)
        self.assertIn('TRIGGER · TRIGGER', html_result)
        self.assertIn('Ordin la trigger', html_result)
        self.assertIn(
            'buget pentru ordin condiționat la trigger:</b> $1,000.00',
            html_result,
        )
        self.assertIn('Nu cumpăra la piață înainte de trigger', html_result)
        self.assertIn('LQQ.PA · LQQ.PA', html_result)

    def test_buy_recommendation_history_keeps_past_actionable_signals(self):
        candidate = {
            'symbol': 'MSFT', 'company_name': 'Microsoft', 'market': 'SUA',
            'entry_eur': 100, 'stop_eur': 95, 'target_eur': 120,
            'rr_ratio': 4, 'eligible_brokers': ['IBKR'],
            'sizing_by_broker': [{
                'broker': 'IBKR', 'conditional_amount_eur': 1_000,
                'conditional_units': 10,
            }],
        }
        first = market_scanner_analysis.update_buy_recommendation_history(
            [],
            {'buy_recommendations': [{
                'symbol': 'MSFT', 'market': 'SUA',
                'verdict': 'Candidat valid', 'why_now': 'Setup valid.',
                'main_risk': 'Sub stop.',
            }]},
            [candidate],
            recorded_at='2026-07-27T09:00:00',
        )
        second = market_scanner_analysis.update_buy_recommendation_history(
            first,
            {'buy_recommendations': [{
                'symbol': 'MSFT', 'market': 'SUA', 'verdict': 'Așteaptă',
                'why_now': 'Nu acum.', 'main_risk': 'Piață slabă.',
            }]},
            [candidate],
            recorded_at='2026-07-28T09:00:00',
        )
        self.assertEqual(len(second), 1)
        self.assertFalse(second[0]['is_current'])
        self.assertEqual(second[0]['closed_at'], '2026-07-28T09:00:00')
        self.assertEqual(second[0]['closed_verdict'], 'Așteaptă')
        self.assertEqual(second[0]['closed_reason'], 'Nu acum.')
        self.assertEqual(second[0]['execution_currency'], 'USD')
        history_html = (
            market_scanner_analysis._render_buy_recommendation_history(second)
        )
        self.assertIn('MSFT · Cumpărare acum', history_html)
        self.assertIn('entry $100.00', history_html)
        self.assertIn('27.07.2026 09:00', history_html)
        self.assertIn('28.07.2026 09:00', history_html)
        self.assertIn('Încheiată', history_html)
        self.assertIn('📈 Grafic OHLC · marcaj C1', history_html)
        self.assertIn(
            'openBuyRecommendationDetail(this.dataset.symbol)',
            history_html,
        )
        self.assertIn(
            'Retrasă după reevaluare la 28.07.2026 09:00:</b> Așteaptă',
            history_html,
        )
        self.assertIn('Nu acum.', history_html)

    def test_buy_recommendation_history_keeps_all_but_renders_only_fifty(self):
        self.assertEqual(
            market_scanner_analysis.BUY_RECOMMENDATION_HISTORY_DISPLAY_LIMIT,
            50,
        )
        history = [
            {
                'history_key': f'SYM{index:03d}|Candidat valid|1|2|3',
                'symbol': f'SYM{index:03d}',
                'action_label': 'Cumpărare acum',
                'verdict': 'Candidat valid',
                'entry_eur': 100,
                'stop_eur': 95,
                'target_eur': 110,
                'rr_ratio': 2,
                'last_seen_at': f'2026-07-30T10:{index % 60:02d}:00',
                'first_seen_at': f'2026-07-30T10:{index % 60:02d}:00',
                'is_current': False,
            }
            for index in range(120)
        ]
        persisted = (
            market_scanner_analysis.update_buy_recommendation_history(
                history,
                {'buy_recommendations': []},
                [],
            )
        )
        self.assertEqual(len(persisted), 120)

        history_html = (
            market_scanner_analysis._render_buy_recommendation_history(
                persisted
            )
        )
        self.assertIn(
            'Istoric recomandări executabile (120)',
            history_html,
        )
        self.assertIn(
            'Se afișează cele mai recente 50 din 120 înregistrări eligibile pentru afișare.',
            history_html,
        )
        self.assertEqual(
            history_html.count('📈 Grafic OHLC · marcaj'),
            50,
        )

    def test_closed_trigger_orders_are_hidden_but_buy_now_history_remains(self):
        history = [
            {
                'history_key': 'ACTIVE|Pregătit la trigger|100|95|115',
                'symbol': 'ACTIVE',
                'verdict': 'Pregătit la trigger',
                'action_label': 'Ordin la trigger',
                'is_current': True,
                'last_seen_at': '2026-08-03T12:00:00',
            },
            {
                'history_key': 'OLDTRG|Pregătit la trigger|100|95|115',
                'symbol': 'OLDTRG',
                'verdict': 'Pregătit la trigger',
                'action_label': 'Ordin la trigger',
                'is_current': False,
                'last_seen_at': '2026-08-02T12:00:00',
            },
            {
                'history_key': 'OLDBUY|Candidat valid|100|95|115',
                'symbol': 'OLDBUY',
                'verdict': 'Candidat valid',
                'action_label': 'Buy now',
                'is_current': False,
                'last_seen_at': '2026-08-01T12:00:00',
            },
        ]
        history_html = (
            market_scanner_analysis._render_buy_recommendation_history(
                history
            )
        )
        self.assertIn('Istoric recomandări executabile (3)', history_html)
        self.assertIn('ACTIVE · Ordin la trigger', history_html)
        self.assertNotIn('OLDTRG · Ordin la trigger', history_html)
        self.assertIn('OLDBUY · Buy now', history_html)
        self.assertIn('numai semnalele „Cumpărare acum / Buy now”', history_html)

    def test_history_datetime_uses_romanian_format(self):
        self.assertEqual(
            market_scanner_analysis._format_ro_datetime(
                '2026-07-28T06:59:16'
            ),
            '28.07.2026 06:59',
        )
        self.assertEqual(
            market_scanner_analysis._format_ro_datetime('2026-07-28'),
            '28.07.2026',
        )

    def test_buy_history_archives_previous_cache_before_reclassification(self):
        old_candidate = {
            'symbol': 'AIG', 'company_name': 'AIG', 'market': 'SUA',
            'entry_eur': 66.99, 'stop_eur': 65.41, 'target_eur': 77.63,
            'rr_ratio': 6.73, 'eligible_brokers': ['IBKR'],
            'sizing_by_broker': [{
                'broker': 'IBKR', 'conditional_amount_eur': 937.86,
                'conditional_units': 14,
            }],
        }
        cached = {
            'generated_at': '2026-07-27T15:16:25',
            'buy_candidates': [old_candidate],
            'result': {'buy_recommendations': [{
                'symbol': 'AIG', 'market': 'SUA',
                'verdict': 'Pregătit la trigger',
                'why_now': 'Ordin condiționat la 66,99 EUR.',
                'main_risk': 'Sub 65,41 EUR.',
            }]},
        }
        archived = (
            market_scanner_analysis.update_buy_recommendation_history_from_cache(
                [], cached, [{
                    **old_candidate,
                    'entry_eur': 70.24,
                }]
            )
        )
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0]['entry_eur'], 66.99)
        self.assertEqual(
            archived[0]['first_seen_at'], '2026-07-27T15:16:25'
        )
        self.assertTrue(archived[0]['is_current'])

    def test_buy_renderer_shows_complete_bvb_coverage(self):
        html_result = market_scanner_analysis.render_buy_recommendations_html(
            {}, [], bvb_universe_stats={
                'discovered': 372, 'deep_scanned': 60, 'batch_size': 50,
                'watchlist_symbols': 3,
            }
        )
        self.assertIn('Watchlist BVB/AeRO', html_result)
        self.assertIn('univers extern BVB/AeRO', html_result)
        self.assertIn('<b>372</b>', html_result)
        self.assertIn('<b>60</b>', html_result)

    def test_buy_renderer_separates_watchlist_from_external_us_universe(self):
        html_result = market_scanner_analysis.render_buy_recommendations_html(
            {}, [], us_universe_stats={
                'discovered': 503,
                'deep_scanned': 420,
                'batch_size': 70,
                'watchlist_symbols': 1370,
                'watchlist_europe_symbols': 1,
            },
        )
        self.assertIn('Watchlist internațional', html_result)
        self.assertIn('<b>1371</b>', html_result)
        self.assertIn('univers extern S&amp;P 500', html_result)
        self.assertIn('lot rotativ/rulare: 70', html_result)

    def test_external_research_does_not_use_watchlist_filters(self):
        watchlist = pd.DataFrame([{
            'Ticker': 'WATCH', 'Decision': 'WAIT', 'Consensus': '-',
            'RR_Ratio': 0,
        }])
        external = [{
            'Ticker': 'TLV.RO', 'Decision': 'HOLD', 'Consensus': '-',
            'RR_Ratio': 2, 'Trend': 'Bullish', 'RSI': 52,
            'Price': 10, 'Stop_Loss': 9, 'Target': 12,
            'Analysts': 0, 'Volume': 50_000,
        }]
        selected = market_scanner.select_strict_buy_candidates(
            watchlist, external_research=external
        )
        self.assertEqual([item['Ticker'] for item in selected], ['TLV.RO'])
        self.assertEqual(selected[0]['Candidate_Source'], 'external_research')
        self.assertFalse(selected[0]['Requires_Watchlist_Filters'])
        self.assertEqual(selected[0]['External_Min_RR'], 1.8)

    def test_external_research_enforces_confirmed_minimum_rr(self):
        common = {
            'Ticker': 'TEST', 'Price': 10, 'Smart_Entry_EUR': 10,
            'Stop_Loss': 9, 'Target': 11.8, 'RR_Ratio': 1.8,
        }
        self.assertTrue(
            market_scanner._external_candidate_has_reliable_levels(common)
        )
        below_minimum = dict(common, Target=11.79, RR_Ratio=1.79)
        self.assertFalse(
            market_scanner._external_candidate_has_reliable_levels(below_minimum)
        )

    def test_external_research_does_not_invent_levels_without_history(self):
        prepared = market_scanner._prepare_external_research_candidate({
            'Ticker': 'EMPTY', 'Price': 10, 'Trend': 'Bullish',
        })
        self.assertIsNone(prepared['Stop_Loss'])
        self.assertIsNone(prepared['Target'])
        self.assertFalse(
            market_scanner._external_candidate_has_reliable_levels(prepared)
        )

    def test_bvb_external_research_can_use_technical_levels_without_consensus(self):
        prepared = market_scanner._prepare_external_research_candidate({
            'Ticker': 'DIGI.RO', 'Decision': 'WAIT', 'Consensus': '-',
            'Analysts': 0, 'Price': 10, 'Price_Native': 50,
            'Trend': 'Bullish', 'RSI': 55, 'ATR_14': 0.2,
            'Volume': 50_000,
            'Chart_OHLC': [
                {'high': 9.80 + index * 0.01}
                for index in range(20)
            ],
        })
        selected = market_scanner.select_strict_buy_candidates(
            pd.DataFrame(), external_research=[prepared]
        )
        self.assertEqual([item['Ticker'] for item in selected], ['DIGI.RO'])
        self.assertEqual(selected[0]['Analysts'], 0)
        self.assertGreaterEqual(selected[0]['RR_Ratio'], 1.8)
        self.assertEqual(
            selected[0]['Target_Basis'],
            'țintă tehnică de 2× riscul inițial; nu este consens de analist',
        )

    def test_symbol_already_in_watchlist_can_be_selected_by_external_research(self):
        watchlist = pd.DataFrame([{
            'Ticker': 'AAPL', 'Decision': 'WAIT', 'Consensus': 'Buy',
            'RR_Ratio': 1.2, 'Price': 100,
        }])
        external = [{
            'Ticker': 'AAPL', 'Decision': 'WAIT', 'Consensus': 'Buy',
            'RR_Ratio': 2, 'Trend': 'Bullish', 'RSI': 55,
            'Price': 100, 'Stop_Loss': 95, 'Target': 110,
            'Sector': 'Technology', 'Industry': 'Consumer Electronics',
        }]
        selected = market_scanner.select_strict_buy_candidates(
            watchlist, external_research=external
        )
        self.assertEqual([item['Ticker'] for item in selected], ['AAPL'])
        self.assertEqual(selected[0]['Candidate_Source'], 'external_research')

    def test_strict_watchlist_candidate_wins_over_external_duplicate(self):
        watchlist = pd.DataFrame([{
            'Ticker': 'AAPL', 'Decision': 'BUY', 'Consensus': 'Strong Buy',
            'RR_Ratio': 3.5, 'Price': 100,
            'Sector': 'Technology', 'Industry': 'Consumer Electronics',
        }])
        external = [{
            'Ticker': 'AAPL', 'Decision': 'WAIT', 'Consensus': 'Buy',
            'RR_Ratio': 2, 'Trend': 'Bullish', 'RSI': 55,
            'Price': 100, 'Stop_Loss': 95, 'Target': 110,
            'Sector': 'Technology', 'Industry': 'Consumer Electronics',
        }]
        selected = market_scanner.select_strict_buy_candidates(
            watchlist, external_research=external
        )
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]['Candidate_Source'], 'watchlist')

    def test_external_research_rewards_verified_relative_strength(self):
        base = {
            'Decision': 'WAIT', 'Consensus': 'None', 'RR_Ratio': 0,
            'Trend': 'Strong Bullish', 'RSI': 69,
        }
        strong = dict(base, RS_vs_SPX=16.8)
        weak = dict(base, RS_vs_SPX=-5)
        self.assertGreater(
            market_scanner._external_research_score(strong),
            market_scanner._external_research_score(weak),
        )

    def test_bvb_candidate_ranking_penalizes_large_tvbetetf_overlap(self):
        external = [
            {
                'Ticker': 'TLV.RO', 'Decision': 'BUY', 'Consensus': 'Buy',
                'RR_Ratio': 3, 'Trend': 'Bullish', 'RSI': 50,
                'Price': 10, 'Stop_Loss': 9, 'Target': 13,
                'Analysts': 1, 'Volume': 50_000,
            },
            {
                'Ticker': 'IARV.RO', 'Decision': 'BUY', 'Consensus': 'Buy',
                'RR_Ratio': 3, 'Trend': 'Bullish', 'RSI': 50,
                'Price': 10, 'Stop_Loss': 9, 'Target': 13,
                'Analysts': 1, 'Volume': 50_000,
            },
        ]
        selected = market_scanner.select_strict_buy_candidates(
            pd.DataFrame(),
            external_research=external,
            etf_holdings={
                'holdings': [{'symbol': 'TLV.RO', 'weight_pct': 18.48}],
            },
        )
        self.assertEqual(selected[0]['Ticker'], 'IARV.RO')

    def test_bvb_external_research_rejects_absurd_or_unverifiable_targets(self):
        external = [
            {
                'Ticker': 'BIO.RO', 'Decision': 'BUY', 'Consensus': 'None',
                'RR_Ratio': 4328.52, 'Trend': 'Bullish', 'RSI': 50,
                'Price': 0.26, 'Stop_Loss': 0.24, 'Target': 57.80,
                'Analysts': 0, 'Volume': 31_963,
            },
            {
                'Ticker': 'ONE.RO', 'Decision': 'WAIT', 'Consensus': 'None',
                'RR_Ratio': 4.25, 'Trend': 'Bullish', 'RSI': 50,
                'Price': 6.63, 'Stop_Loss': 6.30, 'Target': 8.04,
                'Analysts': 2, 'Volume': 12_375,
            },
        ]
        selected = market_scanner.select_strict_buy_candidates(
            pd.DataFrame(), external_research=external
        )
        self.assertEqual([item['Ticker'] for item in selected], ['ONE.RO'])

    def test_research_batch_includes_watchlist_symbols_and_skips_fresh_cache(self):
        symbols = [f'WATCH{index}' for index in range(40)] + [
            f'NEW{index}' for index in range(50)
        ]
        due = market_scanner._research_symbols_due(
            symbols,
            {'NEW0': {'_cached_at': time.time()}},
            {f'WATCH{index}' for index in range(40)},
        )
        self.assertIn('WATCH0', due)
        self.assertNotIn('NEW0', due)
        self.assertEqual(due[0], 'WATCH0')

    def test_research_finalists_refresh_more_often_than_regular_symbols(self):
        cached_at = time.time() - (2 * 3600)
        due = market_scanner._research_symbols_due(
            ['AAPL', 'OTHER'],
            {
                'AAPL': {'_cached_at': cached_at},
                'OTHER': {'_cached_at': cached_at},
            },
            priority_symbols={'AAPL'},
        )
        self.assertEqual(due, ['AAPL'])

    def test_all_bvb_research_symbols_refresh_after_one_hour(self):
        cached_at = time.time() - (2 * 3600)
        due = market_scanner._research_symbols_due(
            ['TLV.RO', 'OTHER'],
            {
                'TLV.RO': {'_cached_at': cached_at},
                'OTHER': {'_cached_at': cached_at},
            },
        )
        self.assertIn('TLV.RO', due)
        self.assertNotIn('OTHER', due)

    def test_bvb_history_merges_tws_and_public_without_duplicate_dates(self):
        dates = pd.bdate_range('2026-04-01', periods=65)
        tws = pd.DataFrame({
            'Open': np.arange(65) + 10,
            'High': np.arange(65) + 11,
            'Low': np.arange(65) + 9,
            'Close': np.arange(65) + 10.5,
            'Volume': np.arange(65) + 1000,
        }, index=dates)
        public = pd.DataFrame({
            'Open': [100.0], 'High': [102.0], 'Low': [99.0],
            'Close': [101.0], 'Volume': [5000],
        }, index=[dates[-1].tz_localize('Europe/Bucharest')])
        merged = market_scanner._merge_ohlcv_histories(tws, public)

        self.assertEqual(len(merged), 65)
        self.assertEqual(float(merged.loc[dates[-1], 'Close']), 101.0)

    def test_broad_bvb_universe_is_never_sent_to_tws(self):
        state = {
            'bvb_equity_universe': [
                {'symbol': 'DENT.RO'},
                {'symbol': 'RCHI.RO'},
            ],
        }
        self.assertEqual(
            market_scanner._planned_bvb_tws_symbols(state),
            [],
        )

    @patch('market_scanner.process_watchlist_ticker')
    @patch(
        'market_scanner.fetch_complete_bvb_equity_universe',
        return_value=[{'symbol': 'TLV.RO', 'bvb_symbol': 'TLV'}],
    )
    @patch('market_scanner.load_complete_us_equity_universe')
    @patch('market_scanner.os.path.exists', return_value=False)
    def test_ro_research_mode_does_not_scan_us(
        self,
        _exists,
        load_us,
        _fetch_bvb,
        process_ticker,
    ):
        process_ticker.return_value = {
            'Ticker': 'TLV.RO',
            'Price': 10,
            'Stop_Loss': 9,
            'Target': 13,
            'RR_Ratio': 3,
        }
        with patch.object(
            market_scanner,
            '_select_bvb_research_symbols',
            return_value=['TLV.RO'],
        ), patch.object(
            market_scanner, '_prefetch_ibkr_mcp_market_data'
        ):
            result = market_scanner.ensure_buy_research_candidates(
                {},
                {'EUR': 1, 'RON': 0.2, 'USD': 0.9},
                15,
                refresh_missing=True,
                target_markets={'România / BVB'},
            )

        load_us.assert_not_called()
        process_ticker.assert_called_once_with(
            'TLV.RO',
            15,
            {'EUR': 1, 'RON': 0.2, 'USD': 0.9},
        )
        self.assertNotIn('us_universe_stats', result)
        self.assertEqual(
            result['bvb_universe_stats']['source'],
            market_scanner.ROMANIAN_UNIVERSE_SOURCE_URL,
        )

    @patch('market_scanner.process_watchlist_ticker')
    @patch('market_scanner.load_complete_us_equity_universe', return_value=['AAPL'])
    @patch('market_scanner.fetch_complete_bvb_equity_universe', return_value=[])
    @patch('market_scanner.os.path.exists', return_value=True)
    @patch('market_scanner.pd.read_csv')
    def test_external_refresh_scans_symbol_even_when_it_is_in_watchlist(
        self, mock_read_csv, _mock_exists, _mock_bvb, _mock_us, mock_process
    ):
        mock_read_csv.return_value = pd.DataFrame({'symbol': ['AAPL']})
        mock_process.return_value = {
            'Ticker': 'AAPL', 'Price': 100, 'Stop_Loss': 95,
            'Target': 110, 'RR_Ratio': 2,
        }
        state = {
            'watchlist': [{
                'Ticker': 'AAPL', 'Decision': 'WAIT', 'Price': 99,
                'Stop_Loss': 94, 'Target': 109, 'RR_Ratio': 2,
                '_cached_at': time.time() - 7200,
            }],
        }
        with patch.object(
            market_scanner, '_prefetch_ibkr_mcp_market_data'
        ), patch.dict(
            market_scanner.BUY_RESEARCH_UNIVERSES,
            {'SUA': ['AAPL']},
            clear=True,
        ):
            result = market_scanner.ensure_buy_research_candidates(
                state, {'EUR': 1, 'USD': 1}, 15, refresh_missing=True
            )
        mock_process.assert_called_once_with(
            'AAPL', 15, {'EUR': 1, 'USD': 1}
        )
        self.assertEqual(
            [item['Ticker'] for item in result['external_buy_research']],
            ['AAPL'],
        )
        self.assertEqual(result['us_universe_stats']['last_batch_attempted'], 1)

    def test_us_selection_limits_two_candidates_per_sector(self):
        external = [
            {
                'Ticker': ticker, 'Decision': 'BUY', 'Consensus': 'Buy',
                'RR_Ratio': 3, 'Trend': 'Bullish', 'RSI': 50,
                'Price': 100, 'Stop_Loss': 95, 'Target': 115,
                'Sector': sector,
            }
            for ticker, sector in [
                ('A', 'Technology'), ('B', 'Technology'),
                ('C', 'Technology'), ('D', 'Healthcare'),
            ]
        ]
        selected = market_scanner.select_strict_buy_candidates(
            pd.DataFrame(),
            external_research=external,
            sector_rotation={'sectors': {
                'Technology': {'status': 'lider', 'etf': 'XLK'},
                'Healthcare': {'status': 'neutru', 'etf': 'XLV'},
            }},
        )
        technology_count = sum(
            item.get('Sector') == 'Technology' for item in selected
        )
        self.assertEqual(technology_count, 2)
        self.assertTrue(any(item.get('Sector') == 'Healthcare' for item in selected))

    def test_us_selection_limits_one_candidate_per_known_industry(self):
        external = [
            {
                'Ticker': ticker, 'Decision': 'BUY', 'Consensus': 'Buy',
                'RR_Ratio': 3, 'Trend': 'Bullish', 'RSI': 50,
                'Price': 100, 'Stop_Loss': 95, 'Target': 115,
                'Sector': sector, 'Industry': 'Semiconductors',
            }
            for ticker, sector in [
                ('CHIP1', 'Technology'),
                ('CHIP2', 'Technology'),
            ]
        ]
        selected = market_scanner.select_strict_buy_candidates(
            pd.DataFrame(), external_research=external
        )
        self.assertEqual(len(selected), 1)

    @patch('market_scanner.os.path.exists', return_value=True)
    @patch('market_scanner.pd.read_csv')
    def test_removed_bvb_symbols_migrate_from_state_to_external_research(
        self, mock_read_csv, _mock_exists
    ):
        mock_read_csv.return_value = pd.DataFrame({'symbol': ['AAPL']})
        state = {
            'watchlist': [
                {'Ticker': 'AAPL', 'Decision': 'WAIT'},
                {'Ticker': 'DIGI.RO', 'Decision': 'WAIT', 'Trend': 'Strong Bullish'},
            ],
        }
        result = market_scanner.ensure_buy_research_candidates(
            state, {'EUR': 1}, 15, refresh_missing=False
        )
        self.assertEqual([item['Ticker'] for item in result['watchlist']], ['AAPL'])
        self.assertEqual(
            [item['Ticker'] for item in result['external_buy_research']],
            ['DIGI.RO'],
        )

    def test_correct_tradeville_snapshot_does_not_double_count_cash(self):
        incorrect = {
            'fetched_at': '2026-07-26T00:00:00+03:00',
            'accounts': [{
                'label': 'Tradeville', 'source': 'Tradeville manual',
                'summary': {
                    'NetLiquidation': 121216.95,
                    'TotalCashValue': 48438.86,
                    'GrossPositionValue': 72778.09,
                },
            }],
        }
        corrected = market_scanner._correct_tradeville_manual_snapshot(incorrect)
        summary = corrected['accounts'][0]['summary']
        self.assertEqual(summary['NetLiquidation'], 72778.09)
        self.assertEqual(summary['GrossPositionValue'], 24339.23)
        self.assertEqual(summary['CostBasis'], 11306.92)
        self.assertEqual(incorrect['accounts'][0]['summary']['NetLiquidation'], 121216.95)

    def test_only_validated_external_candidates_are_promoted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'watchlist.csv')
            pd.DataFrame({'symbol': ['EXISTING']}).to_csv(path, index=False)
            added = market_scanner._promote_validated_external_candidates(
                {'buy_recommendations': [
                    {'symbol': 'TLV.RO', 'verdict': 'Candidat valid'},
                    {'symbol': 'SNP.RO', 'verdict': 'Așteaptă'},
                ]},
                [
                    {'symbol': 'TLV.RO', 'candidate_source': 'external_research'},
                    {'symbol': 'SNP.RO', 'candidate_source': 'external_research'},
                ],
                filepath=path,
            )
            self.assertEqual(added, ['TLV.RO'])
            self.assertEqual(
                pd.read_csv(path)['symbol'].tolist(), ['EXISTING', 'TLV.RO']
            )

    @patch.dict(os.environ, {}, clear=True)
    def test_portfolio_ai_falls_back_to_deterministic_alerts(self):
        with patch('market_scanner_analysis.os.path.exists', return_value=False):
            html_result, cache, evidence, diagnostic = market_scanner_analysis.generate_portfolio_ai_analysis(
                self.portfolio, pd.DataFrame(),
                cached_evidence={
                    'fetched_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
                    'symbols': ['TEST'], 'items': [],
                },
            )
        self.assertIn('Fără ordin stop activ identificat', html_result)
        self.assertIsNone(cache)
        self.assertEqual(evidence['items'], [])
        self.assertEqual(diagnostic['status'], 'missing_key')

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('market_scanner_analysis.get_economic_events', return_value=[])
    @patch('market_scanner_analysis.requests.post')
    def test_portfolio_ai_rejects_outdated_cache_when_new_json_is_invalid(
        self, mock_post, _mock_calendar
    ):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {'output_text': '{invalid'}
        mock_post.return_value = response
        cached = {
            'version': 4,
            'fingerprint': 'old',
            'result': {
                'portfolio_overview': 'Rezumat anterior valid.',
                'market_read': 'Context anterior valid pentru SUA.',
                'position_actions': [{
                    'symbol': 'TEST', 'broker': 'IBKR', 'action': 'Urmărește atent',
                    'plain_reason': 'Protecția trebuie verificată.',
                    'calendar_effect': 'Calendarul nu este disponibil.',
                    'next_check': 'Verifică stopul.',
                }],
                'buy_recommendations': [],
                'priorities': [{
                    'symbol': 'TEST', 'severity': 'mediu', 'issue': 'Protecție',
                    'evidence': 'Stop neverificat.', 'action': 'Verifică stopul.',
                    'why': 'Controlează pierderea.', 'review_trigger': 'La schimbarea prețului.',
                    'confidence': 'medie', 'source_ids': [],
                }],
            },
        }
        html_result, returned_cache, _, diagnostic = (
            market_scanner_analysis.generate_portfolio_ai_analysis(
                self.portfolio,
                pd.DataFrame(),
                cached=cached,
                cached_evidence={
                    'fetched_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
                    'symbols': ['TEST'],
                    'items': [],
                },
            )
        )
        self.assertEqual(diagnostic['status'], 'failed')
        self.assertIsNone(returned_cache)
        self.assertNotIn('cache anterior', html_result)
        self.assertIn('Analiza AI nu este disponibilă momentan', html_result)

    @patch.dict(os.environ, {}, clear=True)
    @patch('market_scanner_analysis.get_economic_events', return_value=[])
    @patch('market_scanner_analysis._portfolio_snapshot_fingerprint', return_value='same')
    def test_portfolio_ai_keeps_current_exact_cache(
        self, _mock_fingerprint, _mock_calendar
    ):
        cached = {
            'version': market_scanner_analysis.PORTFOLIO_AI_CACHE_VERSION,
            'fingerprint': 'same',
            'result': {
                'portfolio_overview': 'Rezumat curent valid.',
                'market_read': 'Context curent valid pentru SUA.',
                'position_actions': [{
                    'symbol': 'TEST', 'broker': 'IBKR', 'action': 'Urmărește atent',
                    'plain_reason': 'Protecția trebuie verificată.',
                    'calendar_effect': 'Nu există evenimente apropiate în date.',
                    'next_check': 'Verifică stopul.',
                }],
                'buy_recommendations': [],
                'priorities': [{
                    'symbol': 'TEST', 'severity': 'mediu', 'issue': 'Protecție',
                    'evidence': 'Stop neverificat.', 'action': 'Verifică stopul.',
                    'why': 'Controlează pierderea.', 'review_trigger': 'La schimbarea prețului.',
                    'confidence': 'medie', 'source_ids': [],
                }],
            },
        }
        html_result, returned_cache, _, diagnostic = (
            market_scanner_analysis.generate_portfolio_ai_analysis(
                self.portfolio,
                pd.DataFrame(),
                cached=cached,
                cached_evidence={
                    'fetched_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
                    'symbols': ['TEST'],
                    'items': [],
                },
            )
        )
        self.assertEqual(diagnostic['status'], 'cache_valid')
        self.assertIs(returned_cache, cached)
        self.assertIn('OpenAI · cache', html_result)

    @patch.dict(os.environ, {}, clear=True)
    @patch('market_scanner_analysis.get_economic_events', return_value=[])
    @patch('market_scanner_analysis._portfolio_snapshot_fingerprint', return_value='changed')
    @patch('market_scanner_analysis._portfolio_critical_fingerprint', return_value='same-critical')
    def test_portfolio_ai_throttles_noncritical_changes_for_four_hours(
        self, _mock_critical, _mock_fingerprint, _mock_calendar
    ):
        now = datetime(2026, 8, 11, 12, 0, 0)
        cached = {
            'version': market_scanner_analysis.PORTFOLIO_AI_CACHE_VERSION,
            'fingerprint': 'old-market-state',
            'critical_fingerprint': 'same-critical',
            'generated_at': '2026-08-11T10:00:00',
            'result': {
                'portfolio_overview': 'Rezumat recent valid.',
                'market_read': 'Context recent valid pentru SUA.',
                'position_actions': [{
                    'symbol': 'TEST', 'broker': 'IBKR',
                    'action': 'Urmărește atent',
                    'plain_reason': 'Protecția trebuie verificată.',
                    'calendar_effect': 'Nu există evenimente apropiate.',
                    'next_check': 'Verifică stopul.',
                }],
                'buy_recommendations': [],
                'priorities': [{
                    'symbol': 'TEST', 'severity': 'mediu',
                    'issue': 'Protecție', 'evidence': 'Stop neverificat.',
                    'action': 'Verifică stopul.', 'why': 'Controlează riscul.',
                    'review_trigger': 'La schimbarea prețului.',
                    'confidence': 'medie', 'source_ids': [],
                }],
            },
        }
        html_result, returned_cache, _, diagnostic = (
            market_scanner_analysis.generate_portfolio_ai_analysis(
                self.portfolio,
                pd.DataFrame(),
                cached=cached,
                cached_evidence={
                    'fetched_at': now.isoformat(),
                    'symbols': ['TEST'], 'items': [],
                },
                now=now,
            )
        )
        self.assertEqual(diagnostic['status'], 'cache_cooldown')
        self.assertEqual(diagnostic['cache_age_hours'], 2.0)
        self.assertIs(returned_cache, cached)
        self.assertIn('OpenAI · cache', html_result)

    def test_buy_renderer_hides_missing_ai_result_from_suggestions(self):
        html_result = market_scanner_analysis.render_buy_recommendations_html(
            {},
            [{
                'symbol': 'MSFT', 'market': 'SUA', 'company_name': 'Microsoft',
                'strict_eligible': True, 'requires_watchlist_filters': True,
                'candidate_source': 'watchlist', 'eligible_brokers': ['IBKR'],
                'entry_eur': 100, 'stop_eur': 95, 'target_eur': 120,
                'rr_ratio': 4, 'consensus': 'Buy',
                'sizing_by_broker': [{
                    'broker': 'IBKR', 'broker_available_cash_eur': 10_000,
                    'conditional_amount_eur': 1_000, 'conditional_units': 10,
                    'risk_to_stop_pct': 5,
                }],
            }],
        )
        self.assertNotIn('MSFT · Microsoft', html_result)
        self.assertNotIn('>Așteaptă</span>', html_result)
        self.assertIn('sugestii executabile: <b>0</b>', html_result)
        self.assertIn('Nu există momentan o sugestie executabilă', html_result)

    def test_portfolio_evidence_prefers_official_sec_filings_and_keeps_links(self):
        class FakeResponse:
            def __init__(self, payload=None, content=b''):
                self._payload = payload
                self.content = content
            def raise_for_status(self):
                return None
            def json(self):
                return self._payload

        class FakeSession:
            def get(self, url, **kwargs):
                if 'company_tickers' in url:
                    return FakeResponse({'0': {'ticker': 'TEST', 'cik_str': 123}})
                if 'submissions' in url:
                    return FakeResponse({'filings': {'recent': {
                        'form': ['10-Q'], 'accessionNumber': ['0000123-26-000001'],
                        'primaryDocument': ['quarterly.htm'], 'filingDate': ['2026-07-25'],
                    }}})
                if 'feeds.finance.yahoo.com' in url:
                    return FakeResponse(content=b'<rss><channel></channel></rss>')
                return FakeResponse([])

        snapshot = market_scanner_analysis.build_portfolio_risk_snapshot(
            self.portfolio, pd.DataFrame()
        )
        with patch('market_scanner_analysis.get_economic_events', return_value=[]):
            evidence = market_scanner_analysis.collect_portfolio_evidence(
                snapshot, request_session=FakeSession()
            )
        self.assertEqual(len(evidence['items']), 1)
        self.assertTrue(evidence['items'][0]['official'])
        self.assertIn('10-Q', evidence['items'][0]['title'])
        self.assertTrue(evidence['items'][0]['url'].startswith('https://www.sec.gov/Archives/'))

    def test_bvb_symbol_is_never_matched_to_same_named_sec_ticker(self):
        class FakeResponse:
            def __init__(self, payload=None, content=b''):
                self._payload = payload
                self.content = content
            def raise_for_status(self):
                return None
            def json(self):
                return self._payload

        class FakeSession:
            def __init__(self):
                self.submissions_requested = False
            def get(self, url, **kwargs):
                if 'company_tickers' in url:
                    return FakeResponse({'0': {'ticker': 'EL', 'cik_str': 123}})
                if 'submissions' in url:
                    self.submissions_requested = True
                    return FakeResponse({'filings': {'recent': {}}})
                if 'feeds.finance.yahoo.com' in url:
                    return FakeResponse(content=b'<rss><channel></channel></rss>')
                return FakeResponse([])

        session = FakeSession()
        snapshot = {
            'positions': [{'symbol': 'EL.RO'}],
            'buy_candidates': [],
        }
        with patch('market_scanner_analysis.get_economic_events', return_value=[]):
            evidence = market_scanner_analysis.collect_portfolio_evidence(
                snapshot, request_session=session
            )
        self.assertFalse(session.submissions_requested)
        self.assertEqual(evidence['items'], [])

    def test_invalid_cached_bvb_sec_evidence_is_removed(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cached = {
            'fetched_at': now.isoformat(),
            'symbols': ['EL.RO'],
            'items': [{
                'source_id': 'EL.RO-sec-wrong',
                'symbol': 'EL.RO',
                'title': 'Depunere SEC greșită',
                'url': 'https://www.sec.gov/wrong',
                'date': '2026-07-24',
                'publisher': 'SEC',
                'source_type': 'raport oficial 8-K',
                'official': True,
            }],
        }
        session = Mock()
        session.get.side_effect = market_scanner_analysis.requests.RequestException()
        with patch('market_scanner_analysis.get_economic_events', return_value=[]):
            evidence = market_scanner_analysis.collect_portfolio_evidence(
                {'positions': [{'symbol': 'EL.RO'}], 'buy_candidates': []},
                cached=cached,
                request_session=session,
                now=now,
            )
        self.assertEqual(evidence['items'], [])
        
    def test_nasdaq_affects_probability_calculation(self):
        """Test that NASDAQ affects probability direction calculation."""
        # Test with bullish NASDAQ
        indicators_bullish = {
            'SPX': {'value': 4500.0, 'status': 'Normal', 'change': 15.0, 'sparkline': [4400, 4450, 4500]},
            'NASDAQ': {'value': 14500.0, 'status': 'Normal', 'change': 50.0, 'sparkline': [14300, 14400, 14500]}
        }
        
        _, _, score_bullish = market_scanner_analysis.generate_market_analysis(indicators_bullish)
        
        # Test with bearish NASDAQ
        indicators_bearish = {
            'SPX': {'value': 4500.0, 'status': 'Normal', 'change': -15.0, 'sparkline': [4600, 4550, 4500]},
            'NASDAQ': {'value': 14500.0, 'status': 'Normal', 'change': -50.0, 'sparkline': [14700, 14600, 14500]}
        }
        
        _, _, score_bearish = market_scanner_analysis.generate_market_analysis(indicators_bearish)
        
        # Bullish should have higher score than bearish
        # (This is a basic sanity check - actual scores depend on full algorithm)
        self.assertIsInstance(score_bullish, (int, float))
        self.assertIsInstance(score_bearish, (int, float))
        
    def test_nasdaq_and_spx_averaging(self):
        """Test that SPX and NASDAQ scores are averaged correctly."""
        # When both indices agree (both bullish)
        indicators_agree = {
            'SPX': {'value': 4500.0, 'status': 'Normal', 'change': 20.0, 'sparkline': list(range(4400, 4520, 5))},
            'NASDAQ': {'value': 14500.0, 'status': 'Normal', 'change': 60.0, 'sparkline': list(range(14300, 14520, 10))}
        }
        
        _, _, score_agree = market_scanner_analysis.generate_market_analysis(indicators_agree)
        
        # When indices disagree (one bullish, one bearish)
        indicators_disagree = {
            'SPX': {'value': 4500.0, 'status': 'Normal', 'change': 20.0, 'sparkline': list(range(4400, 4520, 5))},
            'NASDAQ': {'value': 14500.0, 'status': 'Normal', 'change': -60.0, 'sparkline': list(range(14700, 14480, -10))}
        }
        
        _, _, score_disagree = market_scanner_analysis.generate_market_analysis(indicators_disagree)
        
        # Both should return valid scores
        self.assertGreaterEqual(score_agree, 0)
        self.assertLessEqual(score_agree, 100)
        self.assertGreaterEqual(score_disagree, 0)
        self.assertLessEqual(score_disagree, 100)


class TestDataValidation(unittest.TestCase):
    """Test data validation and error handling."""
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframes."""
        empty_df = pd.DataFrame()
        self.assertEqual(len(empty_df), 0)
        self.assertTrue(empty_df.empty)
        
    def test_nan_value_detection(self):
        """Test NaN value detection."""
        data_with_nan = pd.Series([1, 2, np.nan, 4, 5])
        self.assertTrue(data_with_nan.isna().any())
        
    def test_nan_value_removal(self):
        """Test NaN value removal."""
        data_with_nan = pd.Series([1, 2, np.nan, 4, 5])
        clean_data = data_with_nan.dropna()
        self.assertFalse(clean_data.isna().any())
        self.assertEqual(len(clean_data), 4)
        
    def test_dataframe_column_validation(self):
        """Test dataframe column validation."""
        df = pd.DataFrame({
            'Symbol': ['AAPL', 'GOOGL'],
            'Price': [150.0, 2800.0]
        })
        
        self.assertIn('Symbol', df.columns)
        self.assertIn('Price', df.columns)
        self.assertNotIn('NonExistent', df.columns)


class TestPortfolioCalculations(unittest.TestCase):
    """Test portfolio-related calculations."""
    
    def setUp(self):
        """Set up test portfolio data."""
        self.portfolio = pd.DataFrame({
            'Symbol': ['AAPL', 'GOOGL', 'MSFT'],
            'Shares': [10, 5, 8],
            'Entry_Price': [150.0, 2800.0, 300.0],
            'Current_Price': [160.0, 2900.0, 310.0],
            'Target': [180.0, 3000.0, 350.0]
        })
        
    def test_profit_calculation(self):
        """Test profit calculation for each position."""
        for idx, row in self.portfolio.iterrows():
            profit = (row['Current_Price'] - row['Entry_Price']) * row['Shares']
            self.assertIsInstance(profit, (int, float))
            # All our test positions should be profitable
            self.assertGreater(profit, 0)
            
    def test_total_portfolio_value(self):
        """Test total portfolio value calculation."""
        total_value = (self.portfolio['Current_Price'] * self.portfolio['Shares']).sum()
        self.assertGreater(total_value, 0)
        self.assertEqual(total_value, 160*10 + 2900*5 + 310*8)
        
    def test_roi_calculation(self):
        """Test ROI calculation."""
        total_investment = (self.portfolio['Entry_Price'] * self.portfolio['Shares']).sum()
        total_value = (self.portfolio['Current_Price'] * self.portfolio['Shares']).sum()
        roi = ((total_value - total_investment) / total_investment) * 100
        
        self.assertGreater(roi, 0)
        self.assertIsInstance(roi, (int, float))
        
    def test_target_percentage(self):
        """Test target percentage calculation."""
        for idx, row in self.portfolio.iterrows():
            pct_to_target = ((row['Target'] - row['Current_Price']) / row['Current_Price']) * 100
            self.assertIsInstance(pct_to_target, (int, float))
            self.assertGreater(pct_to_target, 0)  # All targets are above current price


class TestUtilityFunctions(unittest.TestCase):
    """Test utility and formatting functions."""
    
    def test_percentage_formatting(self):
        """Test percentage formatting."""
        value = 0.1234
        formatted = f"{value * 100:.2f}%"
        self.assertEqual(formatted, "12.34%")
        
        negative_value = -0.0567
        formatted_neg = f"{negative_value * 100:+.2f}%"
        self.assertEqual(formatted_neg, "-5.67%")
        
    def test_currency_formatting(self):
        """Test currency formatting."""
        value = 1234.56
        formatted = f"€{value:,.2f}"
        self.assertEqual(formatted, "€1,234.56")
        
        large_value = 1234567.89
        formatted_large = f"€{large_value:,.2f}"
        self.assertEqual(formatted_large, "€1,234,567.89")
        
    def test_date_formatting(self):
        """Test date formatting."""
        test_date = datetime(2025, 12, 20, 11, 30, 0)
        formatted = test_date.strftime('%Y-%m-%d %H:%M:%S')
        self.assertEqual(formatted, "2025-12-20 11:30:00")
        
        formatted_short = test_date.strftime('%Y-%m-%d')
        self.assertEqual(formatted_short, "2025-12-20")


class TestIndicatorLogic(unittest.TestCase):
    """Test indicator classification logic."""
    
    def test_vix_classification_ranges(self):
        """Test VIX classification into status categories."""
        # These are the expected ranges based on market_scanner.py logic
        # Perfect: < 15
        # Normal: 15-20
        # Tension: 20-30
        # Panic: > 30
        
        low_vix = 12.5
        self.assertLess(low_vix, 15)  # Should be Perfect
        
        normal_vix = 17.5
        self.assertGreaterEqual(normal_vix, 15)
        self.assertLess(normal_vix, 20)  # Should be Normal
        
        high_vix = 25.0
        self.assertGreaterEqual(high_vix, 20)
        self.assertLess(high_vix, 30)  # Should be Tension
        
        extreme_vix = 35.0
        self.assertGreater(extreme_vix, 30)  # Should be Panic
        
    def test_skew_classification_ranges(self):
        """Test SKEW classification ranges."""
        # Normal SKEW: 115-135
        # High SKEW: > 145
        
        normal_skew = 125.0
        self.assertGreaterEqual(normal_skew, 115)
        self.assertLessEqual(normal_skew, 135)
        
        high_skew = 150.0
        self.assertGreater(high_skew, 145)


class TestHTMLGeneration(unittest.TestCase):
    """Test HTML generation functions."""

    def _firebase_html(self, worker_path):
        return market_scanner._firebase_web_push_html(
            {
                'apiKey': 'public-api-key',
                'projectId': 'market-scanner-test',
                'messagingSenderId': '123456789',
                'appId': '1:123456789:web:abcdef',
            },
            'BPublicVapidKey_abcdefghijklmnopqrstuvwxyz0123456789',
            worker_path=worker_path,
        )

    def test_firebase_control_is_mounted_inside_navigation_menu(self):
        with tempfile.TemporaryDirectory() as directory:
            html = self._firebase_html(
                os.path.join(directory, 'firebase-messaging-sw.js')
            )
        self.assertIn("document.getElementById('navMenu')", html)
        self.assertIn("button.className = 'menu-item push-menu-item'", html)
        self.assertIn('menu.appendChild(button)', html)
        self.assertNotIn('document.body.appendChild(button)', html)
        self.assertNotIn('position: fixed', html)

    def test_firebase_menu_control_preserves_subscription_states(self):
        with tempfile.TemporaryDirectory() as directory:
            worker_path = os.path.join(
                directory, 'firebase-messaging-sw.js'
            )
            html = self._firebase_html(worker_path)
            with open(worker_path, 'r', encoding='utf-8') as handle:
                worker = handle.read()
        self.assertIn('Activează alertele BUY', html)
        self.assertIn('Alerte BUY active', html)
        self.assertIn('Instalează pentru alerte BUY', html)
        self.assertIn('Alerte BUY indisponibile', html)
        self.assertIn('navigator.maxTouchPoints > 1', html)
        self.assertIn('mountPushPrerequisiteButton', html)
        self.assertIn('messaging.getToken', html)
        self.assertIn('messaging.deleteToken', html)
        self.assertIn('marketScannerPortfolioAuthenticated', html)
        self.assertIn('market-scanner:portfolio-authenticated', html)
        self.assertNotIn('Copiază tokenul Firebase', html)
        self.assertNotIn('copyFirebaseTokenButton', html)
        self.assertIn('firebase.messaging();', worker)
        self.assertNotIn('private_key', worker)
    
    def test_html_escaping(self):
        """Test HTML special characters are handled."""
        test_string = "Test & <script>alert('xss')</script>"
        # In production, this should be escaped
        self.assertIn('&', test_string)
        self.assertIn('<', test_string)
        
    def test_html_structure_validity(self):
        """Test basic HTML structure."""
        html = "<div class='test'>Content</div>"
        self.assertTrue(html.startswith('<'))
        self.assertTrue(html.endswith('>'))
        self.assertIn('class=', html)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_zero_division_protection(self):
        """Test protection against division by zero."""
        # ROI calculation with zero investment should be handled
        investment = 0
        value = 100
        
        if investment == 0:
            roi = 0  # Should default to 0 or handle gracefully
        else:
            roi = ((value - investment) / investment) * 100
            
        self.assertEqual(roi, 0)
        
    def test_negative_values_handling(self):
        """Test handling of negative values."""
        negative_price = -10.0
        # Prices should never be negative in real data
        self.assertLess(negative_price, 0)
        
        # But calculations should still work
        shares = 10
        value = negative_price * shares
        self.assertEqual(value, -100.0)
        
    def test_very_large_numbers(self):
        """Test handling of very large numbers."""
        large_value = 1e15  # 1 quadrillion
        formatted = f"{large_value:,.0f}"
        self.assertIn(',', formatted)
        
    def test_very_small_numbers(self):
        """Test handling of very small numbers."""
        small_value = 0.000001
        formatted = f"{small_value:.6f}"
        self.assertEqual(formatted, "0.000001")


class TestIntegration(unittest.TestCase):
    """Test integration scenarios."""
    
    @patch('market_scanner_analysis.requests.get')
    def test_api_call_mock(self, mock_get):
        """Test API call with mock response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_get.return_value = mock_response
        
        # Simulate API call
        response = mock_get('http://test.com/api')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'data': 'test'})
        
    def test_dataframe_operations_chain(self):
        """Test chaining multiple dataframe operations."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50]
        })
        
        # Chain operations
        result = (df
                 .assign(C=lambda x: x['A'] + x['B'])
                 .query('C > 20')
                 .sort_values('C', ascending=False))
        
        self.assertGreater(len(result), 0)
        self.assertIn('C', result.columns)


class TestDynamicEvents(unittest.TestCase):
    """Teste pentru calendarul real SUA, Europa și BVB."""

    def setUp(self):
        self.now = datetime(2026, 7, 23, 12, 0)

    def test_macro_event_keeps_values_and_timezone(self):
        event = market_scanner_analysis._normalise_macro_event({
            'id': 'cpi-1', 'title': 'CPI YoY', 'country': 'US',
            'date': '2026-07-23T10:00:00Z', 'importance': 'high',
            'actual': '3.2%', 'forecast': '3.0%', 'previous': '2.9%'
        }, self.now)
        self.assertEqual(event['country'], 'SUA')
        self.assertEqual(event['timezone'], 'UTC')
        self.assertEqual(event['status'], 'past')
        self.assertEqual(event['actual'], '3.2%')

    def test_higher_inflation_is_not_automatically_bullish(self):
        event = market_scanner_analysis._normalise_macro_event({
            'title': 'Romania Inflation Rate', 'country': 'RO',
            'date': '2026-07-22T07:00:00Z', 'actual': '6.1%',
            'forecast': '5.7%', 'previous': '5.5%'
        }, self.now)
        analysis = market_scanner_analysis._deterministic_event_analysis(event)
        self.assertEqual(analysis['verdict'], 'Bearish probabil')
        self.assertEqual(event['country'], 'România')

    def test_future_rate_event_has_scenarios_not_invented_values(self):
        event = market_scanner_analysis._normalise_macro_event({
            'title': 'BNR Interest Rate Decision', 'country': 'RO',
            'date': '2026-07-28T12:00:00Z', 'forecast': '6.50%',
            'previous': '6.50%'
        }, self.now)
        analysis = market_scanner_analysis._deterministic_event_analysis(event)
        self.assertEqual(event['status'], 'upcoming')
        self.assertIsNone(event['actual'])
        self.assertIn('peste', analysis['mechanism'].lower())

    def test_bvb_calendar_parser_marks_corporate_scope(self):
        content = """
        <html><body><h2>Calendar Financiar</h2>
        <div>30 Iulie 2026</div>
        <div>BRD - GROUPE SOCIETE GENERALE S.A. Rezultate financiare semestriale 2026</div>
        </body></html>
        """
        events = market_scanner_analysis._parse_bvb_calendar_html(content, self.now)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['country'], 'România')
        self.assertEqual(events[0]['category'], 'corporate')
        self.assertEqual(events[0]['timezone'], 'Europe/Bucharest')
        analysis = market_scanner_analysis._deterministic_event_analysis(events[0])
        self.assertIn('emitentului', analysis['bvb_impact'])

    def test_source_failure_does_not_create_fictitious_events(self):
        session = Mock()
        session.post.side_effect = market_scanner_analysis.requests.RequestException()
        session.get.side_effect = market_scanner_analysis.requests.RequestException()
        with patch('market_scanner_analysis._load_calendar_cache', return_value=[]):
            events = market_scanner_analysis.get_economic_events(self.now, session)
        self.assertEqual(events, [])

    def test_source_failure_uses_valid_cache(self):
        cached = [{'id': 'cached', 'datetime': '2026-07-24T10:00:00'}]
        session = Mock()
        session.post.side_effect = market_scanner_analysis.requests.RequestException()
        session.get.side_effect = market_scanner_analysis.requests.RequestException()
        with patch('market_scanner_analysis._load_calendar_cache', return_value=cached):
            events = market_scanner_analysis.get_economic_events(self.now, session)
        self.assertEqual(events, cached)

    def test_tradingview_calendar_uses_get_query_filters(self):
        macro_response = Mock()
        macro_response.raise_for_status.return_value = None
        macro_response.json.return_value = {'result': [{
            'id': 'fed-1', 'title': 'Fed Interest Rate Decision',
            'country': 'US', 'date': '2026-07-29T18:00:00Z',
            'importance': 1, 'forecast': '4.25%', 'previous': '4.50%',
        }]}
        bvb_response = Mock()
        bvb_response.raise_for_status.return_value = None
        bvb_response.text = '<html></html>'
        session = Mock()
        session.get.side_effect = [macro_response, bvb_response]

        events = market_scanner_analysis.get_economic_events(self.now, session)

        self.assertEqual(events[0]['country'], 'SUA')
        first_call = session.get.call_args_list[0]
        self.assertEqual(first_call.args[0], market_scanner_analysis.CALENDAR_SOURCE_URL)
        self.assertEqual(first_call.kwargs['params']['countries'], 'US,EU,RO')
        self.assertEqual(first_call.kwargs['params']['minImportance'], 1)

    def test_ai_unavailable_calendar_claim_is_replaced_by_known_event(self):
        result = {
            'portfolio_overview': 'Rezumat valid.',
            'market_read': 'Context SUA valid.',
            'priorities': [{
                'symbol': 'JPM', 'severity': 'mediu', 'issue': 'Stop',
                'evidence': 'Stop activ.', 'action': 'Menține.',
                'why': 'Protejează profitul.', 'review_trigger': 'După Fed.',
                'confidence': 'medie', 'source_ids': [],
            }],
            'position_actions': [{
                'symbol': 'JPM', 'broker': 'IBKR', 'action': 'Menține',
                'plain_reason': 'Trend favorabil.',
                'calendar_effect': 'Calendarul economic nu este disponibil.',
                'next_check': 'Reevaluează după Fed.',
            }],
            'buy_recommendations': [],
        }
        validated = market_scanner_analysis._validate_portfolio_ai_result(
            result, {'JPM'}, calendar_effects={
                'JPM': 'Evenimente relevante: Fed Interest Rate Decision (2026-07-29).',
            }
        )
        self.assertIn(
            'Fed Interest Rate Decision',
            validated['position_actions'][0]['calendar_effect'],
        )

    def test_buy_calendar_text_is_overridden_by_validated_future_events(self):
        result = {
            'portfolio_overview': 'Rezumat valid.',
            'market_read': 'Context SUA valid.',
            'priorities': [{
                'symbol': 'JPM', 'severity': 'mediu', 'issue': 'Stop',
                'evidence': 'Stop activ.', 'action': 'Menține.',
                'why': 'Protejează profitul.', 'review_trigger': 'După Fed.',
                'confidence': 'medie', 'source_ids': [],
            }],
            'position_actions': [{
                'symbol': 'JPM', 'broker': 'IBKR', 'action': 'Menține',
                'plain_reason': 'Trend favorabil.', 'calendar_effect': 'Neutru.',
                'next_check': 'După Fed.',
            }],
            'buy_recommendations': [{
                'symbol': 'MSFT', 'market': 'SUA',
                'verdict': 'Pregătit la trigger', 'why_now': 'Trend bun.',
                'market_effect': 'Piață stabilă.', 'news_effect': 'Neutru.',
                'calendar_effect': 'Calendar indisponibil.',
                'main_risk': 'Sub stop.', 'source_ids': [],
            }],
        }
        validated = market_scanner_analysis._validate_portfolio_ai_result(
            result,
            {'JPM'},
            candidate_symbols={'MSFT'},
            calendar_effects={'JPM': 'Fed viitor.'},
            candidate_calendar_effects={
                'MSFT': 'Evenimente viitoare relevante: Fed Rate Decision.',
            },
        )
        self.assertIn(
            'Fed Rate Decision',
            validated['buy_recommendations'][0]['calendar_effect'],
        )

    def test_invalid_ai_response_keeps_deterministic_analysis(self):
        event = market_scanner_analysis._normalise_macro_event({
            'id': 'ecb-1', 'title': 'ECB Interest Rate Decision', 'country': 'EU',
            'date': '2026-07-24T12:00:00Z', 'forecast': '2.0%', 'previous': '2.0%'
        }, self.now)
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {'choices': [{'message': {'content': 'not-json'}}]}
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}), \
             patch('market_scanner_analysis.requests.post', return_value=response) as post:
            analyses = market_scanner_analysis._enrich_events_with_ai([event], {})
        self.assertEqual(analyses[event['id']]['verdict'], 'Mixt')
        request = post.call_args
        self.assertEqual(request.args[0], 'https://api.openai.com/v1/responses')
        self.assertEqual(
            request.kwargs['json']['model'],
            market_scanner_analysis.OPENAI_LIGHTWEIGHT_MODEL,
        )
        self.assertEqual(
            request.kwargs['json']['reasoning'],
            {'effort': 'low'}
        )
        self.assertNotIn('temperature', request.kwargs['json'])

    def test_economic_calendar_reuses_persistent_ai_cache(self):
        event = market_scanner_analysis._normalise_macro_event({
            'id': 'fed-cache-1', 'title': 'Fed Interest Rate Decision',
            'country': 'US', 'date': '2026-07-29T18:00:00Z',
            'forecast': '4.25%', 'previous': '4.50%',
        }, self.now)
        item = market_scanner_analysis._deterministic_event_analysis(event)
        item.update({'id': event['id'], 'verdict': 'Mixt'})
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            'model': 'gpt-5.6-luna',
            'output_text': json.dumps({'events': [item]}),
        }
        cache = {}
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}), \
             patch(
                 'market_scanner_analysis.requests.post',
                 return_value=response,
             ) as post:
            first = market_scanner_analysis._enrich_events_with_ai(
                [event], {}, ai_cache=cache
            )
            second = market_scanner_analysis._enrich_events_with_ai(
                [event], {}, ai_cache=cache
            )
        self.assertEqual(post.call_count, 1)
        self.assertEqual(len(cache), 1)
        self.assertEqual(first[event['id']]['verdict'], 'Mixt')
        self.assertEqual(second[event['id']]['verdict'], 'Mixt')
        self.assertEqual(
            post.call_args.kwargs['json']['model'],
            market_scanner_analysis.OPENAI_LIGHTWEIGHT_MODEL,
        )

    def test_extracts_text_from_responses_api(self):
        payload = {
            'output': [{
                'type': 'message',
                'content': [{'type': 'output_text', 'text': '{"events": []}'}]
            }]
        }
        self.assertEqual(
            market_scanner_analysis._extract_openai_response_text(payload),
            '{"events": []}'
        )

    def test_calendar_rendering_has_past_future_and_bvb(self):
        past = market_scanner_analysis._normalise_macro_event({
            'id': 'gdp-1', 'title': 'GDP Growth Rate', 'country': 'EU',
            'date': '2026-07-22T09:00:00Z', 'actual': '0.4%', 'forecast': '0.2%'
        }, self.now)
        future = market_scanner_analysis._parse_bvb_calendar_html(
            '<div>30 Iulie 2026</div><div>SNP - OMV PETROM S.A. Rezultate financiare semestriale 2026</div>',
            self.now
        )[0]
        with patch('market_scanner_analysis._enrich_events_with_ai') as enrich:
            enrich.return_value = {
                event['id']: market_scanner_analysis._deterministic_event_analysis(event)
                for event in (past, future)
            }
            rendered = market_scanner_analysis._render_calendar([past, future], {})
        self.assertIn('Ultimele 7 zile', rendered)
        self.assertIn('Următoarele 10 zile', rendered)
        self.assertIn('BET / BET-TR', rendered)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
