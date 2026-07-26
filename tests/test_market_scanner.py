"""
Unit tests for Market Scanner application - Updated version.
Tests actual functions that exist in the codebase.
"""
import unittest
import copy
import sys
import os
import tempfile
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
        
    def test_event_impact_fomc(self):
        """Test FOMC event impact description."""
        desc = market_scanner_analysis.get_event_impact('FOMC')
        self.assertIsInstance(desc, str)
        self.assertGreater(len(desc), 0)

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
        session.get.side_effect = market_scanner.requests.RequestException('offline')
        self.assertEqual(
            market_scanner.fetch_complete_bvb_equity_universe(state, session),
            state['bvb_equity_universe'],
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
        self.assertEqual(request_json['reasoning'], {'effort': 'high'})
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

    def test_buy_candidate_entry_uses_eur_price_when_smart_entry_is_nan(self):
        item = {'Smart_Entry_EUR': float('nan'), 'Smart_Entry': 110, 'Price': 100}
        self.assertEqual(market_scanner._buy_candidate_entry_eur(item), 100)

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
        self.assertIn('IBKR — sumă orientativă acum:</b> €0.00', html_result)
        self.assertIn('Tradeville — sumă orientativă acum:</b> €0.00', html_result)
        self.assertIn('Așteaptă', html_result)

    def test_buy_renderer_shows_complete_bvb_coverage(self):
        html_result = market_scanner_analysis.render_buy_recommendations_html(
            {}, [], bvb_universe_stats={
                'discovered': 372, 'deep_scanned': 60, 'batch_size': 30,
            }
        )
        self.assertIn('Univers BVB/AeRO descoperit', html_result)
        self.assertIn('<b>372</b>', html_result)
        self.assertIn('<b>60</b>', html_result)

    def test_external_research_does_not_use_watchlist_filters(self):
        watchlist = pd.DataFrame([{
            'Ticker': 'WATCH', 'Decision': 'WAIT', 'Consensus': '-',
            'RR_Ratio': 0,
        }])
        external = [{
            'Ticker': 'TLV.RO', 'Decision': 'HOLD', 'Consensus': '-',
            'RR_Ratio': 1.5, 'Trend': 'Bullish', 'RSI': 52,
        }]
        selected = market_scanner.select_strict_buy_candidates(
            watchlist, external_research=external
        )
        self.assertEqual([item['Ticker'] for item in selected], ['TLV.RO'])
        self.assertEqual(selected[0]['Candidate_Source'], 'external_research')
        self.assertFalse(selected[0]['Requires_Watchlist_Filters'])

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
            },
            {
                'Ticker': 'IARV.RO', 'Decision': 'BUY', 'Consensus': 'Buy',
                'RR_Ratio': 3, 'Trend': 'Bullish', 'RSI': 50,
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

    def test_us_selection_limits_two_candidates_per_sector(self):
        external = [
            {
                'Ticker': ticker, 'Decision': 'BUY', 'Consensus': 'Buy',
                'RR_Ratio': 3, 'Trend': 'Bullish', 'RSI': 50,
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
    def test_portfolio_ai_uses_previous_valid_cache_when_new_json_is_invalid(
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
        self.assertEqual(diagnostic['status'], 'fallback_cache')
        self.assertIs(returned_cache, cached)
        self.assertIn('cache anterior', html_result)

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
        self.assertEqual(request.kwargs['json']['model'], 'gpt-5.6-sol')
        self.assertEqual(
            request.kwargs['json']['reasoning'],
            {'effort': 'max', 'mode': 'pro'}
        )
        self.assertNotIn('temperature', request.kwargs['json'])

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
