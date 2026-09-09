"""Read-only live runner for the Technical Events shadow engine."""

from __future__ import annotations

import argparse

import pandas as pd

import market_scanner
import technical_events


DEFAULT_TICKERS = "NVDA,MSFT,AMZN,META,MU,LRCX,CLS,AAPL,AMD,GOOGL"


def run(tickers):
    benchmark, _, _, benchmark_source = market_scanner._load_analysis_history(
        "SPY", "SPY", period="2y"
    )
    rows = []
    for ticker in tickers:
        history, _, _, attribution = market_scanner._load_analysis_history(
            ticker, ticker, period="2y"
        )
        result = technical_events.analyze(
            history,
            benchmark,
            source={
                "provider": attribution.get("Market_Data_Source"),
                "benchmark": "SPY",
                "ticker": ticker,
            },
        )
        timeframes = result.get("timeframes") or {}
        rows.append({
            "Ticker": ticker,
            "Short Term": (timeframes.get("SHORT_TERM") or {}).get("direction", "N/A"),
            "Intermediate": (timeframes.get("INTERMEDIATE_TERM") or {}).get("direction", "N/A"),
            "Long Term": (timeframes.get("LONG_TERM") or {}).get("direction", "N/A"),
            "Bullish Events": result.get("bullish_events", 0),
            "Bearish Events": result.get("bearish_events", 0),
            "Event Score": result.get("overall_event_score"),
            "Support": result.get("nearest_support"),
            "Resistance": result.get("nearest_resistance"),
            "Confidence": result.get("confidence"),
            "Source": attribution.get("Market_Data_Source"),
        })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", default=DEFAULT_TICKERS)
    args = parser.parse_args()
    tickers = [value.strip().upper() for value in args.tickers.split(",") if value.strip()]
    print(run(tickers).to_string(index=False))


if __name__ == "__main__":
    main()
