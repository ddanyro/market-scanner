import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

import market_scanner


class TestBVBYahooHistoryCache(unittest.TestCase):
    def setUp(self):
        market_scanner._BVB_YAHOO_HISTORY_CACHE = None
        market_scanner._YAHOO_HISTORY_MEMORY_CACHE.clear()

    @staticmethod
    def _history(end="2026-09-11", periods=70):
        dates = pd.bdate_range(end=end, periods=periods)
        return pd.DataFrame({
            "Open": range(1, periods + 1),
            "High": range(2, periods + 2),
            "Low": range(1, periods + 1),
            "Close": range(2, periods + 2),
            "Volume": [1000] * periods,
        }, index=dates)

    @patch("market_scanner._download_yahoo_history")
    def test_second_request_uses_persistent_cache_without_download(self, download):
        download.return_value = self._history()
        with tempfile.TemporaryDirectory() as directory:
            cache_path = os.path.join(directory, "bvb-cache.json.gz")
            first = market_scanner._load_bvb_yahoo_history(
                "BIO.RO",
                cache_path=cache_path,
                now="2026-09-12T08:00:00Z",
            )
            market_scanner._BVB_YAHOO_HISTORY_CACHE = None
            second = market_scanner._load_bvb_yahoo_history(
                "BIO.RO",
                cache_path=cache_path,
                now="2026-09-12T12:00:00Z",
            )

        self.assertEqual(download.call_count, 1)
        self.assertEqual(len(first), 70)
        self.assertEqual(len(second), 70)
        self.assertEqual(float(second["Close"].iloc[-1]), 71.0)

    @patch("market_scanner._download_yahoo_history")
    def test_expired_cache_downloads_only_incremental_overlap(self, download):
        initial = self._history()
        extra_date = initial.index[-1] + pd.offsets.BDay(1)
        incremental = pd.DataFrame({
            "Open": [72], "High": [73], "Low": [71],
            "Close": [72], "Volume": [1500],
        }, index=[extra_date])
        download.side_effect = [initial, incremental]

        with tempfile.TemporaryDirectory() as directory:
            cache_path = os.path.join(directory, "bvb-cache.json.gz")
            market_scanner._load_bvb_yahoo_history(
                "BRD.RO",
                cache_path=cache_path,
                now="2026-09-12T00:00:00Z",
            )
            refreshed = market_scanner._load_bvb_yahoo_history(
                "BRD.RO",
                cache_path=cache_path,
                now="2026-09-13T00:01:00Z",
            )

        self.assertEqual(download.call_count, 2)
        _, incremental_kwargs = download.call_args_list[1]
        self.assertEqual(incremental_kwargs["period"], "1y")
        self.assertIn("start", incremental_kwargs)
        self.assertIn("end", incremental_kwargs)
        self.assertEqual(len(refreshed), 71)


if __name__ == "__main__":
    unittest.main()
