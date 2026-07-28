import datetime
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
        session = Mock()
        session.get.return_value = response

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


if __name__ == "__main__":
    unittest.main()
