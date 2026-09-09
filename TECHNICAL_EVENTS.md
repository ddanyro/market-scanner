# Technical Events Engine

`technical_events.py` is an independent, deterministic shadow engine. Its
outputs do not enter Baseline, Enhanced, Risk Score, Portfolio Fit, position
sizing, stops, or BUY/WAIT/AVOID.

## Timeframes

All periods are configurable daily-session counts:

| Timeframe | Lookback | SMA pair | Swing confirmation | Event window | Recency half-life |
|---|---:|---:|---:|---:|---:|
| Short term | 45 | 5/20 | 2 bars | 10 | 6 sessions |
| Intermediate | 130 | 20/50 | 3 bars | 20 | 15 sessions |
| Long term | 260 | 50/200 | 5 bars | 35 | 40 sessions |

These horizons represent roughly two months, six months, and one trading year.
They were selected for the scanner's daily OHLCV history and are not copied
from Trading Central.

## Support and resistance

Confirmed local extrema are found using the configured number of bars on both
sides. Nearby pivots are clustered when their distance is at most the larger
of `0.75% × current price` and `0.5 × ATR14`. Each level retains touch count,
last touch, and a 0–100 structural strength. The nearest valid level on either
side of current price is selected. The breakout buffer is:

`max(0.30% × current price, 0.25 × ATR14)`.

## Events, strength and recency

The engine detects SMA and MACD crosses, momentum/RSI reversals, clustered
support/resistance breaks and bounces, confirmed higher highs/lower lows,
volume confirmation, relative-strength 20-session breaks, and ATR volatility
expansion. Event strength is a transparent 0–100 rule score based on event
type, magnitude, and confirmation.

Recency is exponential:

`effective_strength = event_strength × 0.5^(age_sessions / half_life)`.

Within each timeframe, Event Score is neutral at 50 and moves toward 100/0
according to the balance of recency-adjusted bullish/bearish strength:

`50 + 50 × (bullish_strength - bearish_strength) / total_strength`.

Overall score uses 30% short, 40% intermediate, and 30% long among available
timeframes. Direction is BULLISH at 57+, BEARISH at 43 or lower, otherwise
NEUTRAL. This is a shadow-only Technical Events score, not an investment score.

## Confidence

Confidence is capped at 100 and combines event-count sufficiency (25 points),
mean effective strength (30), timeframe agreement (25), and confirmed-event
ratio (20). It is a deterministic descriptive measure and has not been
calibrated against returns.

## Storage and validation

`technical_events_predictions.jsonl` is a separate append-only, hash-chained
ledger. Each observation freezes raw events, summaries, support/resistance,
source-data hash, Baseline/Enhanced comparison fields, entry price, and pending
1D/5D/10D/20D/60D + MAE/MFE outcome slots. Outcomes are never populated at
signal time.

## Forward validation

`evaluate_technical_events_forward.py` reads the immutable ledger and writes a
separate derived dataset under `analysis/technical_events_validation/`. It
uses the captured entry price and only daily sessions strictly after the
signal's `data_as_of` day. The original ledger is never rewritten.

The report measures timeframe scores and directions, score/confidence buckets,
event types, recency, timeframe agreement, support/resistance events, market
regimes, and incremental predictive power versus the existing Technical Score.
The reported 50/50 combination is simulation-only and is not connected to any
production score or decision.
