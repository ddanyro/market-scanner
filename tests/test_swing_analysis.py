
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
        # Create a DF with 200 days of data + SMA cols
        dates = pd.date_range(start='2024-01-01', periods=300)
        df_spx = pd.DataFrame({'Close': np.linspace(4000, 5000, 300)}, index=dates)
        mock_spx.history.return_value = df_spx
        
        # 2. Mock PCR Data
        mock_pcr = MagicMock()
        df_pcr = pd.DataFrame({'Close': np.linspace(0.6, 0.9, 100)}, index=dates[:100])
        mock_pcr.history.return_value = df_pcr
        
        # Setup Ticker side_effect
        def side_effect(ticker):
            if ticker == "^GSPC": return mock_spx
            if ticker in ["^CPC", "^PCR", "^PCX"]: return mock_pcr
            return MagicMock()
        mock_ticker.side_effect = side_effect
        
        # 3. Mock CNN Data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "fear_and_greed": {"score": 65, "rating": "greed"},
            "fear_and_greed_historical": {
                "data": [{"x": 1000, "y": 60}, {"x": 2000, "y": 65}]
            }
        }
        mock_get.return_value = mock_response
        
        # Run function
        data = get_swing_trading_data()
        
        # Assertions
        self.assertIn('SPX_Price', data)
        self.assertIn('SPX_SMA200', data)
        self.assertEqual(data['FG_Score'], 65)
        self.assertIn('PCR_Value', data)
        self.assertIn('Chart_SPX', data)
        self.assertIn('Chart_FG', data)
        
        # Check Chart Data structure
        self.assertIsInstance(data['Chart_SPX']['price'], list)
        self.assertEqual(len(data['Chart_SPX']['sma200']), 60) # We requested lookback=60

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

    @patch('market_scanner_analysis.get_swing_trading_data')
    def test_generate_html(self, mock_get_data):
        """ Test HTML generation structure """
        
        mock_get_data.return_value = {
            'SPX_Price': 5000, 'SPX_SMA200': 4800, 'SPX_SMA50': 4900,
            'FG_Score': 20, 'FG_Rating': 'extreme fear',
            'PCR_Value': 1.2,
            'Chart_SPX': {'labels': [], 'price': [], 'sma50': [], 'sma200': []},
            'Chart_FG': [20, 25, 20],
            'Chart_PCR': [1.0, 1.1, 1.2]
        }
        
        html = generate_swing_trading_html()
        
        self.assertIn("Swing Trading Signal", html)
        self.assertIn("BULLISH", html) # 5000 > 4800
        self.assertIn("Extreme Fear", html) # Score 20
        self.assertIn("Panică (PCR>1)", html) # PCR 1.2
        self.assertIn("<canvas id=\"chart_trend_", html)
        self.assertIn("const spxData =", html)

    @patch('market_scanner_analysis.get_swing_trading_data')
    def test_generate_html_missing_data(self, mock_get_data):
        """ Test HTML generation when data is missing (API failure) """
        # Return minimal dict as if all fetches failed
        mock_get_data.return_value = {}
        
        try:
            html = generate_swing_trading_html()
            # Should not crash, but defaults might cause JS issues if not handled.
            # We just verify it generates HTML successfully.
            self.assertIn("Swing Trading Signal", html)
            self.assertIn("const spxData = {}", html) # Or whatever default
        except Exception as e:
            self.fail(f"HTML Generation crashed on missing data: {e}")

if __name__ == '__main__':
    unittest.main()
