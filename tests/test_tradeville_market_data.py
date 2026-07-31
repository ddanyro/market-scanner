import datetime
import json
import os
import tempfile
import unittest
from unittest.mock import Mock

import pandas as pd

import tradeville_market_data


def _payload(rows):
    return {
        "cmd": "graficdata",
        "directJSON": 1,
        "data": (
            "data,deschide,maxim,minim,last,volum\n"
            + "\n".join(rows)
            + "\n"
        ),
    }


class TestTradevilleMarketData(unittest.TestCase):
    def test_default_session_retries_temporary_connection_failures(self):
        tradeville_market_data._RETRY_SESSION = None
        session = tradeville_market_data._retry_session()
        retry = session.get_adapter("https://").max_retries

        self.assertEqual(retry.connect, 3)
        self.assertEqual(retry.read, 2)
        self.assertIn(503, retry.status_forcelist)
        self.assertIn(
            "Mozilla/5.0", session.headers["User-Agent"]
        )
        self.assertEqual(
            session.headers["Referer"], "https://tradeville.ro/"
        )

    def test_parses_public_tradeville_symbol_list(self):
        links = "".join(
            f'<a href="/actiuni/S{index}">Companie</a>'
            for index in range(25)
        )
        symbols = tradeville_market_data.parse_listed_symbols(links)

        self.assertIn("S0", symbols)
        self.assertIn("S24", symbols)

    def test_last_valid_public_list_survives_source_403(self):
        response = Mock()
        response.raise_for_status.side_effect = (
            tradeville_market_data.requests.HTTPError("403")
        )
        session = Mock()
        session.get.return_value = response

        symbols = tradeville_market_data.fetch_listed_symbols(
            session=session
        )

        self.assertEqual(
            symbols, set(tradeville_market_data.LAST_VALID_LISTED_SYMBOLS)
        )
        self.assertIn("ALR", symbols)
        self.assertNotIn("TALD", symbols)

    def test_parses_valid_ohlcv_and_scientific_volume(self):
        rows = []
        start = datetime.date(2026, 4, 29)
        for index in range(90):
            day = start + datetime.timedelta(days=index)
            rows.append(
                f"{day.isoformat()},10,11,9,10.5,{100 + index}e2"
            )

        frame = tradeville_market_data.parse_chart_payload(
            _payload(rows),
            now=datetime.date(2026, 7, 28),
        )

        self.assertEqual(
            list(frame.columns), ["Open", "High", "Low", "Close", "Volume"]
        )
        self.assertEqual(len(frame), 90)
        self.assertEqual(float(frame["Close"].iloc[-1]), 10.5)
        self.assertEqual(float(frame["Volume"].iloc[0]), 10_000)

    def test_rejects_history_with_no_recent_trade(self):
        rows = [
            (
                f"{(datetime.date(2015, 1, 1) + datetime.timedelta(days=index)).isoformat()},"
                "1,1.1,.9,1,100"
            )
            for index in range(90)
        ]

        with self.assertRaises(
            tradeville_market_data.TradevilleStaleDataError
        ):
            tradeville_market_data.parse_chart_payload(
                _payload(rows),
                now=datetime.date(2026, 7, 28),
            )

    def test_rejects_missing_or_invented_ohlc_columns(self):
        with self.assertRaises(tradeville_market_data.TradevilleDataError):
            tradeville_market_data.parse_chart_payload(
                {"data": "data,last\n2026-07-27,10\n"},
                now=datetime.date(2026, 7, 28),
            )

    def test_fetch_history_uses_raw_bvb_symbol(self):
        rows = []
        start = datetime.date(2026, 4, 29)
        for index in range(90):
            day = start + datetime.timedelta(days=index)
            rows.append(f"{day.isoformat()},10,11,9,10.5,100")
        response = Mock()
        response.json.return_value = _payload(rows)
        response.raise_for_status.return_value = None
        list_response = Mock()
        list_response.text = "".join(
            f'<a href="/actiuni/{symbol}">{symbol}</a>'
            for symbol in (
                ["ALR"]
                + [f"S{index}" for index in range(24)]
            )
        )
        list_response.raise_for_status.return_value = None
        session = Mock()
        session.get.side_effect = [list_response, response]

        frame, metadata = tradeville_market_data.fetch_history(
            "ALR.RO",
            session=session,
            now=datetime.date(2026, 7, 28),
        )

        self.assertFalse(frame.empty)
        self.assertEqual(metadata["symbol"], "ALR.RO")
        self.assertEqual(metadata["data_broker"], "Tradeville")
        self.assertEqual(metadata["market_data"]["as_of"], "2026-07-27")
        self.assertEqual(
            session.get.call_args.kwargs["params"],
            {"simbol": "ALR", "lat": ""},
        )

    def test_fetch_history_skips_symbol_absent_from_public_list(self):
        list_response = Mock()
        list_response.text = "".join(
            f'<a href="/actiuni/S{index}">S{index}</a>'
            for index in range(25)
        )
        list_response.raise_for_status.return_value = None
        session = Mock()
        session.get.return_value = list_response

        with self.assertRaises(tradeville_market_data.TradevilleDataError):
            tradeville_market_data.fetch_history(
                "TALD.RO",
                session=session,
                now=datetime.date(2026, 7, 28),
            )

        session.get.assert_called_once()

    def test_fetch_history_uses_valid_local_cache_when_source_fails(self):
        rows = []
        start = datetime.date(2026, 4, 29)
        for index in range(90):
            day = start + datetime.timedelta(days=index)
            rows.append(f"{day.isoformat()},10,11,9,10.5,100")
        source_frame = tradeville_market_data.parse_chart_payload(
            _payload(rows),
            now=datetime.date(2026, 7, 28),
        )
        response = Mock()
        response.raise_for_status.side_effect = (
            tradeville_market_data.requests.HTTPError("offline")
        )
        session = Mock()
        session.get.return_value = response

        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = os.path.join(temp_dir, "bvb_market_cache.json")
            with open(cache_path, "w", encoding="utf-8") as handle:
                json.dump({
                    "version": 1,
                    "symbols": {
                        "ALR": {
                            "fetched_at": "2026-07-28T06:00:00+00:00",
                            "bars": tradeville_market_data._frame_to_cache_rows(
                                source_frame
                            ),
                        }
                    },
                }, handle)

            frame, metadata = tradeville_market_data.fetch_history(
                "ALR.RO",
                session=session,
                cache_path=cache_path,
                now=datetime.date(2026, 7, 28),
            )

        self.assertEqual(float(frame["Close"].iloc[-1]), 10.5)
        self.assertTrue(metadata["cache_fallback"])
        self.assertIn("cache local", metadata["data_provider"])


if __name__ == "__main__":
    unittest.main()
