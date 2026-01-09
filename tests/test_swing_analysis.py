
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import json
import sys
import os

# Add parent dir to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_scanner_analysis import get_swing_trading_data, generate_swing_trading_html

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
        
        self.assertIn('NDX_Price', data)
        self.assertIn('NDX_RSI', data)
        
        self.assertIn('VIX_Current', data)
        self.assertIn('SKEW_Current', data)
        
        self.assertEqual(data['FG_Score'], 65)
        self.assertIn('PCR_Value', data)
        
        # Check Breadth keys (might be None if finviz parsing fails, but keys should generally be attempted)
        # With our mock text "300 Total", it might pass the regex if implemented simply
        # or fail if regex is strict. Let's just check if it didn't crash.
        
        # Check Chart Data structure
        self.assertIsInstance(data.get('Chart_SPX', {}).get('price'), list)
        self.assertEqual(len(data.get('Chart_SPX', {}).get('sma200', [])), 60) 

    @patch('market_scanner_analysis.yf.Ticker')
    @patch('market_scanner_analysis.requests.get')
    def test_get_swing_data_failures(self, mock_get, mock_ticker):
        """ Test robust handling when APIs fail """
        
        # Mock exceptions
        mock_ticker.side_effect = Exception("Yahoo Down")
        mock_get.side_effect = Exception("CNN Down")
        
        data = get_swing_trading_data()
        
        # Should return safe defaults, not crash
        self.assertEqual(data.get('FG_Score'), 50)
        self.assertEqual(data.get('FG_Rating'), 'neutral')
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
            # Default logic with 0 values leads to NDX=True (sma=0) and SPX=False (0>0 False) -> "TECH ONLY"
            self.assertIn("TECH ONLY", html) 
            
            # Verify graceful fallbacks for new indicators
            self.assertIn("OFFLINE", html) # Breadth offline
            self.assertIn("N/A", html) # Or similar default handling
            
        except Exception as e:
            self.fail(f"HTML Generation crashed on missing data: {e}")

if __name__ == '__main__':
    unittest.main()
