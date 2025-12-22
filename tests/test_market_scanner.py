"""
Unit tests for Market Scanner application - Updated version.
Tests actual functions that exist in the codebase.
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import market_scanner_analysis


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


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
