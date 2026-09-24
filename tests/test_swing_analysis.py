
import unittest
from unittest.mock import patch, MagicMock, mock_open
import datetime
import pandas as pd
import numpy as np
import json
import sys
import os

# Add parent dir to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_scanner_analysis import (
    calculate_international_swing_score,
    calculate_market_bias,
    generate_swing_trading_html,
    get_swing_trading_data,
    get_finviz_market_tide,
    _usable_tide_cache,
)

class TestSwingAnalysis(unittest.TestCase):

    @patch('market_scanner_analysis.yf.Ticker')
    @patch('market_scanner_analysis.requests.get')
    def test_get_swing_data_success(self, mock_get, mock_ticker):
        """ Test extracting data when APIs work correctly """
        
        # 1. Mock SPX Data
        mock_spx = MagicMock()
        dates = pd.date_range(start='2024-01-01', periods=300)
        df_spx = pd.DataFrame({'Close': np.linspace(4000, 5000, 300)}, index=dates)
        mock_spx.history.return_value = df_spx
        
        # 2. Mock NDX Data - IMPORTANT to include since logic fetches it
        mock_ndx = MagicMock()
        df_ndx = pd.DataFrame({'Close': np.linspace(14000, 16000, 300)}, index=dates)
        mock_ndx.history.return_value = df_ndx

        # 3. Mock VIX Data
        mock_vix = MagicMock()
        df_vix = pd.DataFrame({'Close': np.full(100, 15.0)}, index=dates[:100])
        mock_vix.history.return_value = df_vix

        # 4. Mock SKEW Data
        mock_skew = MagicMock()
        df_skew = pd.DataFrame({'Close': np.full(100, 130.0)}, index=dates[:100])
        mock_skew.history.return_value = df_skew

        # 5. Mock PCR Data
        mock_pcr = MagicMock()
        df_pcr = pd.DataFrame({'Close': np.linspace(0.6, 0.9, 100)}, index=dates[:100])
        mock_pcr.history.return_value = df_pcr
        
        # Setup Ticker side_effect
        def side_effect(ticker):
            ticker = ticker.upper()
            if ticker == "^GSPC": return mock_spx
            if ticker == "^NDX": return mock_ndx
            if ticker == "^VIX": return mock_vix
            if ticker == "^SKEW": return mock_skew
            if ticker in ["^CPC", "^PCR", "^PCX"]: return mock_pcr
            return MagicMock()
        mock_ticker.side_effect = side_effect
        
        # 6. Mock CNN Data & Finviz
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Determine based on URL which JSON to return
        def get_side_effect(url, **kwargs):
            mock_res_cnn = MagicMock()
            mock_res_cnn.status_code = 200
            mock_res_cnn.json.return_value = {
                "fear_and_greed": {"score": 65, "rating": "greed"},
                "fear_and_greed_historical": {
                    "data": [{"x": 1000, "y": 60}, {"x": 2000, "y": 65}]
                }
            }
            
            if "cnn.io" in url:
                return mock_res_cnn
            
            # Finviz mocks (return text for regex)
            mock_res_finviz = MagicMock()
            mock_res_finviz.status_code = 200
            mock_res_finviz.text = "300 Total" # Mocking 300 stocks above SMA
            return mock_res_finviz

        mock_get.side_effect = get_side_effect
        
        # Run function
        data = get_swing_trading_data()
        
        # Assertions for Core Data
        self.assertIn('SPX_Price', data)
        self.assertIn('SPX_SMA200', data)
        self.assertIn('SPX_RSI', data) # Check RSI
        self.assertEqual(data['SPX_Observed_At'], dates[-1].isoformat())
        
        self.assertIn('NDX_Price', data)
        self.assertIn('NDX_RSI', data)
        self.assertEqual(data['NDX_Observed_At'], dates[-1].isoformat())
        
        self.assertIn('VIX_Current', data)
        self.assertEqual(data['VIX_Observed_At'], dates[99].isoformat())
        self.assertIn('SKEW_Current', data)
        
        self.assertEqual(data['FG_Score'], 65)
        self.assertIn('FG_Observed_At', data)
        self.assertIn('Breadth_Fetched_At', data)
        self.assertIsNone(data['Breadth_Observed_At'])
        self.assertIn('PCR_Value', data)
        
        # Check Breadth keys (might be None if finviz parsing fails, but keys should generally be attempted)
        # With our mock text "300 Total", it might pass the regex if implemented simply
        # or fail if regex is strict. Let's just check if it didn't crash.
        
        # Check Chart Data structure
        self.assertIsInstance(data.get('Chart_SPX', {}).get('price'), list)
        self.assertEqual(len(data.get('Chart_SPX', {}).get('sma200', [])), 60) 

    @patch('market_scanner_analysis.get_fallback_breadth', return_value=None)
    @patch('market_scanner_analysis.yf.Ticker')
    @patch('market_scanner_analysis.requests.get')
    def test_get_swing_data_failures(self, mock_get, mock_ticker, _mock_breadth):
        """ Test robust handling when APIs fail """
        
        # Mock exceptions
        mock_ticker.side_effect = Exception("Yahoo Down")
        mock_get.side_effect = Exception("CNN Down")
        
        data = get_swing_trading_data()
        
        # Should return safe defaults, not crash
        self.assertIsNone(data.get('FG_Score'))
        self.assertEqual(data.get('FG_Rating'), 'indisponibil')
        self.assertEqual(data.get('Chart_FG'), [])
        
        # Ensure VIX/SKEW access doesn't crash HTML gen later
        # They might be missing keys, which HTML gen handles via .get(..., default)

    @patch('market_scanner_analysis.get_swing_trading_data')
    def test_generate_html(self, mock_get_data):
        """ Test HTML generation structure with FULL data """
        
        mock_get_data.return_value = {
            'SPX_Price': 5000, 'SPX_SMA200': 4800, 'SPX_SMA50': 4900, 'SPX_SMA10': 4950,
            'SPX_RSI': 55.5,
            
            'NDX_Price': 16000, 'NDX_SMA200': 15000, 'NDX_SMA50': 15500,
            'NDX_RSI': 60.0,
            
            'VIX_Current': 14.5, 'VIX_SMA20': 16.0, 'VIX_Percentile': 30,
            'SKEW_Current': 140.0,
            
            'Breadth_Pct': 65.0, 'Breadth_Above': 328, 'Breadth_Total': 505,
            'Breadth_200_Pct': 70.0, 
            'Breadth_Quality': 'Rally Solid',
            'Breadth_Quality_Color': '#4caf50',
            
            'FG_Score': 20, 'FG_Rating': 'extreme fear', 'FG_SMA5': 25,
            'PCR_Value': 1.2,
            
            'Chart_SPX': {'labels': [], 'price': [], 'sma50': [], 'sma200': [], 'rsi': []},
            'Chart_NDX': {'labels': [], 'price': [], 'sma50': [], 'sma200': [], 'rsi': []},
            'Chart_FG': [20, 25, 20],
            'Chart_PCR': [1.0, 1.1, 1.2],
            'Chart_VIX': {'labels': [], 'values': []}
        }
        
        html = generate_swing_trading_html()
        
        self.assertIn("Swing Trading Signal", html)
        self.assertIn("Scor swing internațional", html)
        self.assertIn("Încredere", html)
        self.assertIn("Date disponibile:", html)
        self.assertIn("Calitatea datelor, nu probabilitatea de câștig", html)
        self.assertIn("minimum 90% din cele 13 câmpuri", html)
        self.assertIn("Cum se calculează și ce înseamnă intervalele", html)
        self.assertIn("100/100", html)
        self.assertIn("nu declanșează singur cumpărarea", html)
        self.assertIn("BULLISH", html) # SPX 5000 > 4800
        self.assertIn("Extreme Fear", html) # Score 20
        self.assertIn("OPORTUNITATE (Fear)", html) # PCR 1.2
        
        # New Indicators Checks
        self.assertIn("Momentum (RSI14)", html)
        self.assertIn("55.5", html) # RSI Value
        
        self.assertIn("Volatilitate (VIX)", html)
        self.assertIn("14.5", html) # VIX Value
        
        self.assertIn("Tail Risk (SKEW)", html)
        self.assertIn("140", html) # SKEW Value
        
        self.assertIn("Breadth (Finviz)", html)
        self.assertIn("65%", html) # Breadth Pct
        self.assertIn("Rally Solid", html) # Breadth Quality
        
        self.assertIn("<canvas id=\"chart_trend_", html)

        _, signal = generate_swing_trading_html(return_signal=True)
        self.assertEqual(signal['key'], 'international')
        self.assertIn(signal['verdict'], html)

    def test_international_swing_score_uses_both_indices_and_data_quality(self):
        complete_data = {
            'SPX_Price': 5100, 'SPX_SMA200': 4700, 'SPX_SMA50': 5000,
            'SPX_SMA10': 5050, 'SPX_RSI': 58,
            'NDX_Price': 18100, 'NDX_SMA200': 16000, 'NDX_SMA50': 17500,
            'NDX_SMA10': 17900, 'NDX_RSI': 61,
            'Breadth_Pct': 72, 'VIX_Current': 18, 'FG_Score': 48,
            'Market_Tide': {'Advancing': 3000, 'Declining': 1800},
        }
        result = calculate_international_swing_score(complete_data)
        self.assertEqual(result['score'], 100)
        self.assertEqual(result['confidence'], 'Ridicată')
        self.assertIn('Market Tide', result['confidence_explanation'])
        self.assertEqual(result['completeness_pct'], 100)
        self.assertEqual(result['band'], 'Aliniere foarte puternică')
        self.assertEqual(result['breakdown']['trend'], 40)
        self.assertEqual(result['breakdown']['timing'], 15)

        incomplete = calculate_international_swing_score({'SPX_Price': 5100})
        self.assertEqual(incomplete['confidence'], 'Scăzută')
        self.assertEqual(incomplete['band'], 'Context nefavorabil')
        self.assertLess(incomplete['score'], result['score'])
        self.assertEqual(incomplete['breakdown']['trend'], 0)
        self.assertEqual(incomplete['breakdown']['timing'], 0)
        self.assertEqual(calculate_market_bias({'SPX_Price': 5100})['score'], 0)

    @patch('market_scanner_analysis.get_swing_trading_data')
    def test_generate_html_missing_data(self, mock_get_data):
        """ Test HTML generation when data is missing (API failure) """
        # Return minimal dict as if all fetches failed
        mock_get_data.return_value = {}
        
        try:
            html = generate_swing_trading_html()
            # Should not crash.
            # Verify basic structure exists
            self.assertIn("Swing Trading Signal", html)
            self.assertIn("DATE INSUFICIENTE", html)
            self.assertNotIn("TECH ONLY", html)
            
            # Verify graceful fallbacks for new indicators
            self.assertIn("OFFLINE", html) # Breadth offline
            self.assertIn("N/A", html) # Or similar default handling
            
        except Exception as e:
            self.fail(f"HTML Generation crashed on missing data: {e}")

    def _fresh_data(self):
        stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {
            'SPX_Price': 5100, 'SPX_SMA200': 4700, 'SPX_SMA50': 5000,
            'SPX_SMA10': 5050, 'SPX_RSI': 58, 'SPX_Observed_At': stamp,
            'NDX_Price': 18100, 'NDX_SMA200': 16000, 'NDX_SMA50': 17500,
            'NDX_SMA10': 17900, 'NDX_RSI': 61, 'NDX_Observed_At': stamp,
            'Breadth_Pct': 72, 'Breadth_Observed_At': stamp,
            'VIX_Current': 18, 'VIX_Observed_At': stamp,
            'FG_Score': 48, 'FG_SMA5': 46, 'FG_Observed_At': stamp,
            'Market_Tide': {'Advancing': 3000, 'Declining': 1800,
                            'NewHighs': 200, 'NewLows': 50, 'observed_at': stamp},
        }

    def test_regime_and_two_entry_setups_are_separate(self):
        data = self._fresh_data()
        data['FG_Score'] = 55
        html, signal = generate_swing_trading_html(data, return_signal=True)
        self.assertEqual(signal['regime'], 'FAVORABLE')
        self.assertTrue(signal['research_allowed'])
        self.assertEqual(signal['verdict'], 'WAIT')
        self.assertEqual(signal['continuation']['status'], 'READY')
        self.assertEqual(signal['validation_status'], 'UNVALIDATED')
        self.assertIn('REGIM FAVORABIL', html)
        self.assertIn('Continuarea trendului — NEVALIDAT', html)
        self.assertIn('Intrarea pe acțiune:', html)
        self.assertNotIn('euforie excesivă', html)

    def test_common_safety_guards_apply_to_both_subcards(self):
        stale = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=5)).isoformat()
        for override in ({'VIX_Current': 31}, {'Breadth_Pct': 29},
                         {'SPX_Observed_At': stale}, {'NDX_SMA200': None}):
            with self.subTest(override=override):
                data = {**self._fresh_data(), **override}
                _, signal = generate_swing_trading_html(data, return_signal=True)
                self.assertFalse(signal['verdict'].startswith('BUY'))
                self.assertFalse(signal['spx_verdict'].startswith('BUY'))
                self.assertFalse(signal['ndx_verdict'].startswith('BUY'))
                self.assertEqual(signal['spx_verdict'], signal['verdict'])
                self.assertEqual(signal['ndx_verdict'], signal['verdict'])

    def test_renderer_handles_none_nan_infinite_observations(self):
        for value in (None, float('nan'), float('inf')):
            with self.subTest(value=value):
                data = {key: value if isinstance(item, (float, int)) else item
                        for key, item in self._fresh_data().items()}
                data.update({'SPX_RSI_Weekly': value, 'SKEW_Current': value,
                             'Breadth_Above': value, 'Breadth_Total': value})
                html, signal = generate_swing_trading_html(data, return_signal=True)
                self.assertEqual(signal['regime'], 'UNKNOWN')
                self.assertIn('REGIM DATE INSUFICIENTE', html)
                self.assertEqual(signal['spx_verdict'], 'DATE INSUFICIENTE')

    def test_renderer_handles_malformed_tide_and_rejects_boolean_indicators(self):
        data = self._fresh_data()
        data['Market_Tide'] = 'unavailable'
        html, signal = generate_swing_trading_html(data, return_signal=True)
        self.assertIn('Market Tide', html)
        self.assertFalse(signal['verdict'].startswith('BUY'))
        boolean_data = {key: True for key in ('SPX_Price', 'SPX_SMA200', 'SPX_SMA50',
                                             'SPX_SMA10', 'VIX_Current', 'FG_Score')}
        score = calculate_international_swing_score(boolean_data)
        self.assertEqual(score['score'], 0)
        self.assertEqual(score['completeness_pct'], 0)
        self.assertEqual(calculate_market_bias(boolean_data)['score'], 0)

    def test_put_call_does_not_promote_wait_to_strong(self):
        data = self._fresh_data()
        data['FG_Score'] = 55
        data['PCR_Value'] = 1.3
        html, signal = generate_swing_trading_html(data, return_signal=True)
        self.assertEqual(signal['verdict'], 'WAIT')
        self.assertNotIn('WAIT (STRONG)', html)

    def test_tide_retrieval_is_not_market_observation(self):
        data = self._fresh_data()
        tide = data['Market_Tide']
        tide['fetched_at'] = tide.pop('observed_at')
        _, signal = generate_swing_trading_html(data, return_signal=True)
        self.assertEqual(signal['regime'], 'SELECTIVE')
        self.assertEqual(signal['data_quality']['status'], 'PARTIAL')
        self.assertTrue(signal['research_allowed'])

    def test_tide_cache_age_is_bounded_and_timezone_aware(self):
        now = datetime.datetime(2026, 9, 24, 12, tzinfo=datetime.timezone.utc)
        data = {'Advancing': 3000, 'Declining': 1800}
        for age, usable in ((95, True), (96, True), (97, False), (-2, False)):
            with self.subTest(age=age):
                stamp = (now - datetime.timedelta(hours=age)).astimezone(
                    datetime.timezone(datetime.timedelta(hours=3))).isoformat()
                result = _usable_tide_cache(data, stamp, now=now)
                self.assertEqual(result is not None, usable)
                if usable:
                    self.assertTrue(result['is_cached'])
                    self.assertIsNone(result['observed_at'])
                    self.assertEqual(result['cache_age_hours'], age)
        self.assertIsNone(_usable_tide_cache(data, 'invalid', now=now))

    @patch('market_scanner_analysis.os.path.exists', return_value=True)
    @patch('market_scanner_analysis.requests.get')
    def test_expired_tide_not_returned_on_fetch_failure(self, mock_get, _mock_exists):
        stale = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=5)).isoformat()
        payload = json.dumps({'timestamp': stale, 'data': {'Advancing': 1, 'Declining': 2}})
        mock_get.return_value.status_code = 503
        with patch('builtins.open', mock_open(read_data=payload)):
            self.assertIsNone(get_finviz_market_tide())

if __name__ == '__main__':
    unittest.main()
