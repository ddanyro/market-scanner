import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import market_scanner

class TestMarketHistory(unittest.TestCase):
    
    def setUp(self):
        # Backup history file path
        self.original_history_file = market_scanner.MARKET_HISTORY_FILE
        market_scanner.MARKET_HISTORY_FILE = "test_market_history.json"
        
    def tearDown(self):
        # Restore history file path and cleanup
        market_scanner.MARKET_HISTORY_FILE = self.original_history_file
        if os.path.exists("test_market_history.json"):
            os.remove("test_market_history.json")

    def test_save_and_load_history(self):
        """Test simple save and load functionality."""
        test_data = {
            "TEST_IND": [
                {"date": "2025-01-01", "value": 10.5},
                {"date": "2025-01-02", "value": 11.0}
            ]
        }
        
        # Save
        market_scanner.save_market_history(test_data)
        
        # Verify file exists
        self.assertTrue(os.path.exists("test_market_history.json"))
        
        # Load
        loaded_data = market_scanner.load_market_history()
        self.assertEqual(loaded_data, test_data)

    def test_load_history_no_file(self):
        """Test loading when file doesn't exist returns empty dict."""
        if os.path.exists("test_market_history.json"):
            os.remove("test_market_history.json")
            
        data = market_scanner.load_market_history()
        self.assertEqual(data, {})

    @patch('market_scanner.yf.Ticker')
    def test_history_accumulation_logic(self, mock_ticker):
        """
        Test that get_market_indicators properly accumulates history
        and limits it to 60 days.
        """
        # Create dummy initial history with 59 entries
        history = {"LTV": []}
        start_date = datetime(2025, 1, 1)
        for i in range(59):
            d = start_date + timedelta(days=i)
            history["LTV"].append({
                "date": d.strftime("%Y-%m-%d"),
                "value": 10.0 + i
            })
            
        # Save initial history
        market_scanner.save_market_history(history)
        
        # Mock Yahoo Finance to return data for a NEW day (Day 60)
        # and another NEW day (Day 61) to test limiting
        
        # We need to mock Ticker().history() to return a DataFrame
        mock_hist_df = pd.DataFrame({
            'Close': [100.0, 101.0]
        }, index=pd.to_datetime([
            start_date + timedelta(days=59), # Day 60
            start_date + timedelta(days=60)  # Day 61
        ]))
        
        def ticker_side_effect(ticker_symbol):
            mock_instance = MagicMock()
            if ticker_symbol == '^LTV':
                mock_instance.history.return_value = mock_hist_df
            else:
                mock_instance.history.return_value = pd.DataFrame() # Empty for others
            return mock_instance
            
        mock_ticker.side_effect = ticker_side_effect
        
        # Run function
        # We assume standard thresholds since we can't patch local var
        # But that's fine, we only care about history accumulation here
        indicators = market_scanner.get_market_indicators()
                
        # Now verify the history file
        updated_history = market_scanner.load_market_history()
        ltv_hist = updated_history["LTV"]
        
        # Should have added the new points
        # Total was 59 + 2 = 61. Limit is 60.
        self.assertEqual(len(ltv_hist), 60)
        
        # Check that the oldest point (Day 1) was removed
        expected_first_date = (start_date + timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertEqual(ltv_hist[0]['date'], expected_first_date)
        
        # Check that the newest points are present
        self.assertEqual(ltv_hist[-1]['value'], 101.0) # Day 61
        self.assertEqual(ltv_hist[-2]['value'], 100.0) # Day 60

    @patch('market_scanner.yf.Ticker')
    def test_sparkline_generation(self, mock_ticker):
        """Test that sparkline contains exactly the last 30 points."""
        # Create history with 40 points
        history = {"LTV": []}
        for i in range(40):
            history["LTV"].append({
                "date": f"2025-01-{i+1:02d}",
                "value": float(i)
            })
        market_scanner.save_market_history(history)
        
        def ticker_side_effect(ticker_symbol):
            mock_instance = MagicMock()
            # Return empty to force usage of history DB
            mock_instance.history.return_value = pd.DataFrame() 
            return mock_instance
            
        mock_ticker.side_effect = ticker_side_effect
        
        # Run function
        indicators = market_scanner.get_market_indicators()
        
        # Check LTV indicator output
        self.assertIn('LTV', indicators)
        ltv_ind = indicators['LTV']
        
        # Sparkline should be last 30 points
        # Values 0 to 39. Last 30 are 10 to 39.
        sparkline = ltv_ind['sparkline']
        self.assertEqual(len(sparkline), 30)
        self.assertEqual(sparkline[0], 10.0)
        self.assertEqual(sparkline[-1], 39.0)

if __name__ == '__main__':
    unittest.main()
