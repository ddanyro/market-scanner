import os
import sys
import tempfile
import unittest
from unittest.mock import Mock

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bvb_public_market_data


SAMPLE_DAILY_CSV = b'''"Symbol","Name","Market","Trades","Volume","Value","Open","Low","High","Avg.","Close","Ref. price","Var (%)"
"TLV","BANCA TRANSILVANIA S.A.","DEALS","2","100","3800","38.00","38.00","38.00","38.00","38.00","37.80","0.53"
"TLV","BANCA TRANSILVANIA S.A.","REGS","500","200000","7600000","37.90","37.70","38.30","38.00","38.10","37.80","0.79"
"DN","DN AGRAR GROUP S.A.","XRS1","20","12000","15000","1.24","1.22","1.28","1.25","1.27","1.24","2.42"
'''


class TestBVBPublicMarketData(unittest.TestCase):
    def setUp(self):
        bvb_public_market_data._CACHE_FRAMES.clear()

    def test_daily_csv_keeps_regular_market_and_includes_aero_symbol(self):
        frame = bvb_public_market_data.parse_daily_csv(
            SAMPLE_DAILY_CSV, "2026-07-30"
        )
        by_symbol = frame.set_index("Symbol")

        self.assertEqual(set(by_symbol.index), {"TLV", "DN"})
        self.assertEqual(by_symbol.loc["TLV", "Market"], "REGS")
        self.assertEqual(float(by_symbol.loc["TLV", "Volume"]), 200000)
        self.assertEqual(by_symbol.loc["DN", "Market"], "XRS1")

    def test_daily_request_uses_public_date_parameter(self):
        session = Mock()
        response = Mock()
        response.content = SAMPLE_DAILY_CSV
        response.raise_for_status.return_value = None
        session.get.return_value = response

        frame = bvb_public_market_data.fetch_daily_snapshot(
            "2026-07-30", session=session
        )

        self.assertEqual(len(frame), 2)
        session.get.assert_called_once_with(
            bvb_public_market_data.BVB_DAILY_URL,
            params={"day": "20260730"},
            timeout=20,
        )

    def test_valid_cache_survives_temporary_source_failure(self):
        dates = pd.bdate_range(end="2026-07-30", periods=60)
        cached = pd.DataFrame({
            "Date": [date.date().isoformat() for date in dates],
            "Symbol": ["DN"] * 60,
            "Market": ["XRS1"] * 60,
            "Open": [1.20] * 60,
            "High": [1.30] * 60,
            "Low": [1.15] * 60,
            "Close": [1.25] * 60,
            "Volume": [10000] * 60,
            "Value": [12500] * 60,
        })
        session = Mock()
        session.get.side_effect = (
            bvb_public_market_data.requests.RequestException("offline")
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = os.path.join(temp_dir, "bvb_daily_cache.csv")
            cached.to_csv(cache_path, index=False)
            frame, metadata = bvb_public_market_data.fetch_history(
                "DN.RO",
                cache_path=cache_path,
                session=session,
                now="2026-07-31",
            )

        self.assertEqual(len(frame), 60)
        self.assertEqual(metadata["data_broker"], "BVB public")
        self.assertEqual(metadata["market_data"]["as_of"], "2026-07-30")


if __name__ == "__main__":
    unittest.main()
