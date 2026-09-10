"""Forward-only statistical validation for Technical Events shadow signals.

The immutable signal ledger is never rewritten.  This module joins each
point-in-time observation to later daily sessions and writes derived analysis
artifacts.  It measures the frozen engine; it cannot alter production scores,
weights, thresholds, or decisions.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

import technical_events_shadow


HORIZONS = (1, 5, 10, 20, 60)
SCORE_BINS = [-np.inf, 40, 50, 60, 70, 80, np.inf]
SCORE_LABELS = ["<40", "40-49", "50-59", "60-69", "70-79", "80+"]
TIMEFRAMES = ("SHORT_TERM", "INTERMEDIATE_TERM", "LONG_TERM")
SCORE_FEATURES = (
    "short_event_score", "intermediate_event_score", "long_event_score",
    "overall_event_score", "confidence", "bullish_event_count",
    "bearish_event_count",
)
EVENT_TYPES = (
    "BREAKOUT", "BREAKDOWN", "CROSSOVER", "CROSSUNDER", "BOUNCE",
    "REVERSAL", "MOMENTUM", "VOLUME_CONFIRMATION", "RELATIVE_STRENGTH",
    "VOLATILITY",
)
OUTPUT_DIR = Path("analysis/technical_events_validation")
TWS_INSTRUMENTS_FILE = Path("tws_instruments.json")


def _number(value, default=None):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _signal_day(prediction, snapshot):
    data_as_of = prediction.get("data_as_of")
    value = pd.Timestamp(data_as_of or snapshot.get("recorded_at"))
    if data_as_of:
        if value.tzinfo is not None:
            value = value.tz_convert(None)
    else:
        if value.tzinfo is None:
            value = value.tz_localize("UTC")
        else:
            value = value.tz_convert("UTC")
        try:
            value = value.tz_convert(prediction.get("market_timezone") or "UTC")
        except (KeyError, TypeError, ValueError):
            value = value.tz_convert("UTC")
        value = value.tz_localize(None)
    return value.normalize()


def _agreement_label(directions):
    short, intermediate, long = (
        directions.get(name, "NEUTRAL") for name in TIMEFRAMES
    )
    if short == intermediate == long == "BULLISH":
        return "all_three_bullish"
    if short == intermediate == long == "BEARISH":
        return "all_three_bearish"
    if short == "BULLISH" and long == "BEARISH":
        return "short_bullish_long_bearish"
    if short == "BEARISH" and long == "BULLISH":
        return "short_bearish_long_bullish"
    return "other_combinations"


def _trend_regime(stage):
    text = str(stage or "").casefold()
    if any(token in text for token in ("creștere", "crestere", "bull", "uptrend")):
        return "bullish"
    if any(token in text for token in ("descendent", "bear", "corec", "downtrend")):
        return "bearish"
    return "sideways"


def _load_history_symbol_aliases(path=TWS_INSTRUMENTS_FILE):
    """Map broker/local symbols to the exact Yahoo exchange listing.

    Contract metadata is non-predictive identity data, so resolving a legacy
    ledger symbol here cannot introduce price look-ahead.  New observations
    also retain the resolved symbol in the derived validation dataset.
    """
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        return {}
    instruments = payload.get("instruments", {})
    if not isinstance(instruments, dict):
        return {}
    result = {}
    for key, instrument in instruments.items():
        if not isinstance(instrument, dict):
            continue
        aliases = [
            str(value).strip().upper()
            for value in instrument.get("aliases", [])
            if str(value).strip()
        ]
        canonical = str(instrument.get("symbol") or key or "").strip().upper()
        candidates = aliases + [canonical]
        # The metadata generator orders the preferred exchange-qualified
        # Yahoo symbol first (for example 3USL.MI before 3USL.BVME/3USL).
        preferred = next(
            (value for value in candidates if "." in value), canonical
        )
        if not preferred:
            continue
        contract = instrument.get("contract") or {}
        lookup_values = candidates + [
            str(key).strip().upper(),
            str(contract.get("symbol") or "").strip().upper(),
            str(contract.get("local_symbol") or "").strip().upper(),
        ]
        for value in lookup_values:
            if value:
                result.setdefault(value, preferred)
    return result


def flatten_ledger(snapshots, history_symbol_aliases=None):
    """Freeze ledger observations into a tabular event-study dataset."""
    history_symbol_aliases = (
        _load_history_symbol_aliases()
        if history_symbol_aliases is None else history_symbol_aliases
    )
    rows = []
    for snapshot in snapshots:
        regime = snapshot.get("market_regime") or {}
        for prediction in snapshot.get("predictions", []):
            technical = prediction.get("technical_events") or {}
            timeframes = technical.get("timeframes") or {}
            directions = {
                name: (timeframes.get(name) or {}).get("direction", "NEUTRAL")
                for name in TIMEFRAMES
            }
            vix = _number(regime.get("vix"))
            ticker = str(prediction.get("ticker") or "").upper()
            stored_history_ticker = str(
                prediction.get("history_ticker") or ""
            ).strip().upper()
            history_ticker = (
                stored_history_ticker
                or history_symbol_aliases.get(ticker)
                or ticker
            )
            rows.append({
                "observation_id": (
                    f"{snapshot.get('snapshot_id')}:{prediction.get('ticker')}"
                ),
                "snapshot_id": snapshot.get("snapshot_id"),
                "recorded_at": snapshot.get("recorded_at"),
                "ticker": prediction.get("ticker"),
                "history_ticker": history_ticker,
                "history_ticker_source": (
                    "snapshot"
                    if stored_history_ticker
                    else "instrument_metadata"
                    if history_ticker != ticker
                    else "ticker"
                ),
                "market": prediction.get("market"),
                "sector": prediction.get("sector"),
                "currency": prediction.get("currency"),
                "entry_price": _number(prediction.get("entry_price")),
                "entry_source": prediction.get("entry_source"),
                "data_as_of": prediction.get("data_as_of") or technical.get("data_as_of"),
                "market_timezone": prediction.get("market_timezone") or "UTC",
                "signal_day": _signal_day(prediction, snapshot),
                "existing_technical_score": _number(
                    prediction.get("existing_technical_score"),
                    _number(prediction.get("baseline_score")),
                ),
                "overall_event_score": _number(
                    prediction.get("technical_events_score"),
                    _number(technical.get("overall_event_score")),
                ),
                "confidence": _number(
                    prediction.get("technical_events_confidence"),
                    _number(technical.get("confidence")),
                ),
                "bullish_event_count": _number(technical.get("bullish_events"), 0),
                "bearish_event_count": _number(technical.get("bearish_events"), 0),
                "short_event_score": _number(
                    (timeframes.get("SHORT_TERM") or {}).get("event_score")
                ),
                "intermediate_event_score": _number(
                    (timeframes.get("INTERMEDIATE_TERM") or {}).get("event_score")
                ),
                "long_event_score": _number(
                    (timeframes.get("LONG_TERM") or {}).get("event_score")
                ),
                "short_direction": directions["SHORT_TERM"],
                "intermediate_direction": directions["INTERMEDIATE_TERM"],
                "long_direction": directions["LONG_TERM"],
                "overall_direction": prediction.get(
                    "technical_events_direction", technical.get("overall_direction")
                ),
                "timeframe_agreement": _agreement_label(directions),
                "market_stage_raw": regime.get("market_stage"),
                "trend_regime": _trend_regime(regime.get("market_stage")),
                "vix_at_signal": vix,
                "volatility_regime": (
                    "high_volatility" if vix is not None and vix >= 25
                    else "low_volatility" if vix is not None else "unknown"
                ),
                "raw_events": technical.get("events") or [],
                "source_provenance": technical.get("input_provenance") or {},
            })
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=[
            "observation_id", "snapshot_id", "recorded_at", "ticker",
            "history_ticker", "history_ticker_source",
            "market", "sector", "currency", "entry_price", "entry_source",
            "data_as_of", "market_timezone", "signal_day",
            "existing_technical_score", "overall_event_score", "confidence",
            "bullish_event_count", "bearish_event_count", "short_event_score",
            "intermediate_event_score", "long_event_score", "short_direction",
            "intermediate_direction", "long_direction", "overall_direction",
            "timeframe_agreement", "market_stage_raw", "trend_regime",
            "vix_at_signal", "volatility_regime", "raw_events",
            "source_provenance", "simulated_equal_weight_score",
        ])
    if not frame.empty:
        frame["simulated_equal_weight_score"] = (
            frame.existing_technical_score + frame.overall_event_score
        ) / 2
    return frame


def _download_history(ticker, start, end, ticker_factory=yf.Ticker):
    history = ticker_factory(ticker).history(
        start=start, end=end, interval="1d", auto_adjust=False, actions=False
    )
    if history is None or history.empty or "Close" not in history:
        return pd.DataFrame()
    frame = history.copy()
    index = pd.to_datetime(frame.index, utc=True).tz_convert(None).normalize()
    close = pd.to_numeric(frame["Close"], errors="coerce")
    adjusted = pd.to_numeric(frame.get("Adj Close", close), errors="coerce")
    factor = adjusted / close.replace(0, np.nan)
    result = pd.DataFrame({
        "close": close.to_numpy(),
        "adjusted": adjusted.to_numpy(),
        "high": pd.to_numeric(frame.get("High", close), errors="coerce").to_numpy()
        * factor.to_numpy(),
        "low": pd.to_numeric(frame.get("Low", close), errors="coerce").to_numpy()
        * factor.to_numpy(),
    }, index=index).dropna(subset=["close", "adjusted"])
    return result[~result.index.duplicated(keep="last")].sort_index()


def _adjusted_entry(stored_entry, signal_day, history):
    if stored_entry is None or stored_entry <= 0:
        return None
    prior = history[history.index <= signal_day]
    if prior.empty or prior.iloc[-1].close <= 0:
        return None
    return stored_entry * prior.iloc[-1].adjusted / prior.iloc[-1].close


def label_forward_outcomes(frame, now=None, ticker_factory=yf.Ticker):
    """Attach only sessions strictly after T; never mutate the signal ledger."""
    if frame.empty:
        return frame.copy()
    result = frame.copy(deep=True)
    now = pd.Timestamp(now or dt.datetime.now(dt.timezone.utc))
    if now.tzinfo is not None:
        now = now.tz_convert(None)
    start = (result.signal_day.min() - pd.Timedelta(days=10)).date().isoformat()
    end = (now + pd.Timedelta(days=2)).date().isoformat()
    histories = {}
    history_column = (
        result.history_ticker
        if "history_ticker" in result else result.ticker
    )
    for ticker in sorted(history_column.dropna().astype(str).unique()):
        try:
            histories[ticker] = _download_history(ticker, start, end, ticker_factory)
        except Exception:
            histories[ticker] = pd.DataFrame()
    for horizon in HORIZONS:
        for column in ("return_pct", "mae_pct", "mfe_pct"):
            result[f"{column}_{horizon}d"] = np.nan
        result[f"outcome_status_{horizon}d"] = "pending"
    for index, row in result.iterrows():
        history_ticker = str(
            row.history_ticker
            if "history_ticker" in result else row.ticker
        )
        history = histories.get(history_ticker, pd.DataFrame())
        if not history.empty:
            # Defensive clipping: never trust a provider/test double to honor
            # the requested end date.
            history = history[history.index <= now.normalize()]
        if history.empty:
            for horizon in HORIZONS:
                result.at[index, f"outcome_status_{horizon}d"] = "missing_history"
            continue
        entry = _adjusted_entry(_number(row.entry_price), row.signal_day, history)
        # Strict inequality is the core anti-look-ahead invariant.
        future = history[history.index > row.signal_day]
        for horizon in HORIZONS:
            if entry is None:
                result.at[index, f"outcome_status_{horizon}d"] = "missing_entry"
                continue
            if len(future) < horizon:
                continue
            window = future.iloc[:horizon]
            result.at[index, f"return_pct_{horizon}d"] = (
                window.iloc[-1].adjusted / entry - 1
            ) * 100
            result.at[index, f"mae_pct_{horizon}d"] = (
                window.low.min() / entry - 1
            ) * 100
            result.at[index, f"mfe_pct_{horizon}d"] = (
                window.high.max() / entry - 1
            ) * 100
            result.at[index, f"outcome_status_{horizon}d"] = "matured"
    return result


def _summary(group, horizon, expected_direction=None, direction_column=None):
    def numeric(column):
        if column not in group:
            return pd.Series(dtype=float)
        return pd.to_numeric(group[column], errors="coerce").dropna()

    returns = numeric(f"return_pct_{horizon}d")
    mae = numeric(f"mae_pct_{horizon}d")
    mfe = numeric(f"mfe_pct_{horizon}d")
    directional_hits = pd.Series(dtype=bool)
    if len(returns) and expected_direction in {"BULLISH", "BEARISH"}:
        directional_hits = (
            returns > 0 if expected_direction == "BULLISH" else returns < 0
        )
    elif len(returns) and direction_column and direction_column in group:
        directions = group.loc[returns.index, direction_column]
        eligible = directions.isin(["BULLISH", "BEARISH"])
        directional_hits = (
            ((directions[eligible] == "BULLISH") & (returns[eligible] > 0))
            | ((directions[eligible] == "BEARISH") & (returns[eligible] < 0))
        )
    return {
        "n": int(len(returns)),
        "average_return": returns.mean() if len(returns) else np.nan,
        "median_return": returns.median() if len(returns) else np.nan,
        "win_rate": (returns > 0).mean() * 100 if len(returns) else np.nan,
        "directional_hit_rate": directional_hits.mean() * 100
        if len(directional_hits) else np.nan,
        "expectancy": returns.mean() if len(returns) else np.nan,
        "average_mae": mae.mean() if len(mae) else np.nan,
        "average_mfe": mfe.mean() if len(mfe) else np.nan,
    }


def score_bucket_table(labelled):
    rows = []
    for feature in SCORE_FEATURES:
        if feature not in labelled:
            continue
        buckets = pd.cut(
            pd.to_numeric(labelled[feature], errors="coerce"), SCORE_BINS,
            labels=SCORE_LABELS, right=False,
        )
        for bucket in SCORE_LABELS:
            group = labelled[buckets == bucket]
            for horizon in HORIZONS:
                rows.append({
                    "feature": feature, "bucket": bucket, "horizon": horizon,
                    **_summary(group, horizon),
                })
    return pd.DataFrame(rows)


def direction_table(labelled):
    rows = []
    for timeframe, column in (
        ("SHORT_TERM", "short_direction"),
        ("INTERMEDIATE_TERM", "intermediate_direction"),
        ("LONG_TERM", "long_direction"),
        ("OVERALL", "overall_direction"),
    ):
        for direction in ("BULLISH", "NEUTRAL", "BEARISH"):
            group = labelled[labelled[column] == direction]
            for horizon in HORIZONS:
                rows.append({
                    "timeframe": timeframe, "direction": direction,
                    "horizon": horizon,
                    **_summary(group, horizon, expected_direction=direction),
                })
    return pd.DataFrame(rows)


def explode_events(labelled):
    rows = []
    outcome_columns = [
        f"{metric}_{horizon}d"
        for horizon in HORIZONS
        for metric in ("return_pct", "mae_pct", "mfe_pct")
    ]
    for _, observation in labelled.iterrows():
        for event in observation.raw_events or []:
            row = {
                "observation_id": observation.observation_id,
                "ticker": observation.ticker,
                "recorded_at": observation.recorded_at,
                "event_type": event.get("type"),
                "event_name": event.get("name"),
                "event_direction": event.get("direction"),
                "event_timeframe": event.get("timeframe"),
                "event_timestamp": event.get("timestamp"),
                "event_strength": _number(event.get("strength")),
                "effective_strength": _number(event.get("effective_strength")),
                "recency_factor": _number(event.get("recency_factor")),
                "age_sessions": _number(event.get("age_sessions")),
            }
            for column in outcome_columns:
                row[column] = observation.get(column)
            rows.append(row)
    return pd.DataFrame(rows)


def event_type_table(events):
    rows = []
    for event_type in EVENT_TYPES:
        group = events[events.event_type == event_type] if not events.empty else events
        for horizon in HORIZONS:
            rows.append({
                "event_type": event_type, "horizon": horizon,
                **_summary(group, horizon, direction_column="event_direction"),
            })
    return pd.DataFrame(rows)


def recency_table(events):
    if events.empty:
        return pd.DataFrame(columns=["recency_bucket", "horizon", "n"])
    age = pd.to_numeric(events.age_sessions, errors="coerce")
    labels = ["0-2 sessions", "3-5 sessions", "6-10 sessions", "11+ sessions"]
    buckets = pd.cut(age, [-np.inf, 3, 6, 11, np.inf], labels=labels, right=False)
    rows = []
    for bucket in labels:
        group = events[buckets == bucket]
        for horizon in HORIZONS:
            rows.append({
                "recency_bucket": bucket, "horizon": horizon,
                "mean_recency_factor": group.recency_factor.mean(),
                **_summary(group, horizon, direction_column="event_direction"),
            })
    return pd.DataFrame(rows)


def agreement_table(labelled):
    rows = []
    labels = (
        "all_three_bullish", "all_three_bearish",
        "short_bullish_long_bearish", "short_bearish_long_bullish",
        "other_combinations",
    )
    for label in labels:
        group = labelled[labelled.timeframe_agreement == label]
        expected = (
            "BULLISH" if label == "all_three_bullish"
            else "BEARISH" if label == "all_three_bearish" else None
        )
        for horizon in HORIZONS:
            rows.append({
                "timeframe_agreement": label, "horizon": horizon,
                **_summary(group, horizon, expected_direction=expected),
            })
    return pd.DataFrame(rows)


def support_resistance_table(events):
    labels = {
        "price breakout above resistance": "breakout_above_resistance",
        "breakdown below support": "breakdown_below_support",
        "bounce from support": "bounce_from_support",
        "rejection from resistance": "rejection_from_resistance",
    }
    rows = []
    for event_name, label in labels.items():
        group = events[events.event_name == event_name] if not events.empty else events
        expected = (
            "BULLISH" if label in {
                "breakout_above_resistance", "bounce_from_support"
            } else "BEARISH"
        )
        for horizon in HORIZONS:
            rows.append({
                "support_resistance_event": label, "horizon": horizon,
                **_summary(group, horizon, expected_direction=expected),
            })
    return pd.DataFrame(rows)


def _correlation(left, right, method="pearson"):
    """Correlation with an in-process Spearman implementation.

    Pandas delegates ``method='spearman'`` to optional SciPy.  Ranking first
    and applying Pearson is mathematically equivalent (including average
    ranks for ties) and keeps the validator runnable in the project venv.
    """
    pair = pd.DataFrame({"left": left, "right": right}).apply(
        pd.to_numeric, errors="coerce"
    ).dropna()
    if (
        len(pair) < 3
        or pair.left.nunique(dropna=True) < 2
        or pair.right.nunique(dropna=True) < 2
    ):
        return np.nan
    if method == "spearman":
        left_values = pair.left.rank(method="average")
        right_values = pair.right.rank(method="average")
    elif method == "pearson":
        left_values = pair.left
        right_values = pair.right
    else:
        raise ValueError(f"unsupported correlation method: {method}")
    return left_values.corr(right_values)


def predictive_power_table(labelled):
    rows = []
    for feature in SCORE_FEATURES:
        for horizon in HORIZONS:
            target = f"return_pct_{horizon}d"
            pair = labelled[[feature, target]].apply(
                pd.to_numeric, errors="coerce"
            ).dropna()
            rows.append({
                "feature": feature, "horizon": horizon, "n": len(pair),
                "pearson": _correlation(pair[feature], pair[target]),
                "spearman": _correlation(
                    pair[feature], pair[target], method="spearman"
                ),
            })
    return pd.DataFrame(rows)


def score_comparison_table(labelled):
    rows = []
    scores = (
        "existing_technical_score", "overall_event_score",
        "simulated_equal_weight_score",
    )
    for horizon in HORIZONS:
        target = f"return_pct_{horizon}d"
        for score in scores:
            pair = labelled[[score, target]].apply(
                pd.to_numeric, errors="coerce"
            ).dropna()
            high = labelled[pd.to_numeric(labelled[score], errors="coerce") >= 70]
            rows.append({
                "score": score, "horizon": horizon, "n": len(pair),
                "pearson": _correlation(pair[score], pair[target]),
                "spearman": _correlation(
                    pair[score], pair[target], method="spearman"
                ),
                **{f"high_score_{key}": value for key, value in _summary(high, horizon).items()},
                "incremental_r2_of_events": np.nan,
            })
        complete = labelled[[
            "existing_technical_score", "overall_event_score", target
        ]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(complete) >= 30 and complete[target].var() > 0:
            y = complete[target].to_numpy(float)
            base = np.column_stack([
                np.ones(len(complete)), complete.existing_technical_score.to_numpy(float)
            ])
            full = np.column_stack([
                np.ones(len(complete)),
                complete.existing_technical_score.to_numpy(float),
                complete.overall_event_score.to_numpy(float),
            ])
            total = np.square(y - y.mean()).sum()
            base_residual = y - base @ np.linalg.lstsq(base, y, rcond=None)[0]
            full_residual = y - full @ np.linalg.lstsq(full, y, rcond=None)[0]
            incremental = (
                (1 - np.square(full_residual).sum() / total)
                - (1 - np.square(base_residual).sum() / total)
            )
            for row in rows[-3:]:
                row["incremental_r2_of_events"] = incremental
    return pd.DataFrame(rows)


def regime_table(labelled):
    rows = []
    for dimension, labels in (
        ("trend_regime", ("bullish", "bearish", "sideways")),
        ("volatility_regime", ("low_volatility", "high_volatility", "unknown")),
    ):
        for label in labels:
            group = labelled[labelled[dimension] == label]
            for horizon in HORIZONS:
                rows.append({
                    "regime_dimension": dimension, "regime": label,
                    "horizon": horizon, **_summary(group, horizon),
                })
    return pd.DataFrame(rows)


def integrity_errors(snapshots, labelled):
    errors = list(technical_events_shadow.validate_ledger(snapshots))
    if not labelled.empty:
        duplicates = labelled.duplicated(["recorded_at", "ticker"], keep=False)
        if duplicates.any():
            errors.append(f"duplicate observations: {int(duplicates.sum())}")
        future_as_of = []
        for _, row in labelled.dropna(subset=["data_as_of"]).iterrows():
            recorded_day = pd.Timestamp(row.recorded_at)
            if recorded_day.tzinfo is not None:
                recorded_day = recorded_day.tz_convert(None)
            if pd.Timestamp(row.data_as_of).tzinfo is not None:
                data_day = pd.Timestamp(row.data_as_of).tz_convert(None)
            else:
                data_day = pd.Timestamp(row.data_as_of)
            if data_day.normalize() > recorded_day.normalize():
                future_as_of.append(row.observation_id)
        if future_as_of:
            errors.append(f"data_as_of after recorded_at: {future_as_of[:10]}")
        invalid = labelled[
            (labelled.overall_event_score < 0)
            | (labelled.overall_event_score > 100)
        ]
        if len(invalid):
            errors.append(f"event scores outside 0-100: {len(invalid)}")
    return errors


def verdict(labelled, comparison):
    status = (
        labelled["outcome_status_20d"]
        if "outcome_status_20d" in labelled
        else pd.Series("pending", index=labelled.index)
    )
    matured = labelled[status == "matured"]
    if len(matured) < 100:
        return "INSUFFICIENT DATA", f"{len(matured)}/100 matured 20D observations"
    current = comparison[
        (comparison.horizon == 20) & (comparison.score == "overall_event_score")
    ]
    base_pair = matured[["existing_technical_score", "overall_event_score"]].dropna()
    redundancy = (
        abs(base_pair.corr().iloc[0, 1]) if len(base_pair) >= 3 else np.nan
    )
    correlation = current.iloc[0].pearson if not current.empty else np.nan
    incremental = current.iloc[0].incremental_r2_of_events if not current.empty else np.nan
    if pd.notna(incremental) and incremental >= 0.01 and pd.notna(correlation) and correlation > 0:
        return "ADDITIVE", f"20D incremental R²={incremental:.4f}; correlation={correlation:.4f}"
    if pd.notna(redundancy) and redundancy >= 0.80 and (
        pd.isna(incremental) or incremental < 0.002
    ):
        return "REDUNDANT", f"score correlation={redundancy:.4f}; incremental R²={incremental:.4f}"
    return "MIXED", f"incremental R²={incremental}; score correlation={redundancy}"


def _markdown(frame, limit=60):
    if frame.empty:
        return "_No observations._"
    return "```csv\n" + frame.head(limit).to_csv(index=False).strip() + "\n```"


def write_report(labelled, tables, errors, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    coverage = pd.DataFrame([{
        "snapshots": labelled.snapshot_id.nunique() if len(labelled) else 0,
        "observations": len(labelled),
        "tickers": labelled.ticker.nunique() if len(labelled) else 0,
        **{
            f"matured_{horizon}d": int((
                labelled.get(f"outcome_status_{horizon}d", pd.Series(dtype=str))
                == "matured"
            ).sum()) for horizon in HORIZONS
        },
    }])
    result, reason = verdict(labelled, tables["score_comparison"])
    report = f"""# TECHNICAL EVENTS VALIDATION REPORT

Generated: {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}

## Sample size and coverage

{_markdown(coverage)}

## Score buckets

{_markdown(tables['score_buckets'])}

## Direction and timeframe results

{_markdown(tables['directions'])}

## Event types

{_markdown(tables['event_types'])}

## Recency decay

{_markdown(tables['recency'])}

## Timeframe agreement

{_markdown(tables['agreement'])}

## Support / resistance events

{_markdown(tables['support_resistance'])}

## Confidence and feature predictive power

{_markdown(tables['predictive_power'])}

## Existing Technical Score versus Technical Events

{_markdown(tables['score_comparison'])}

`simulated_equal_weight_score` is a 50/50 analytical simulation only. It is
not consumed by Baseline, Enhanced, Risk Score, or BUY/WAIT/AVOID.

## Market regimes

{_markdown(tables['regimes'])}

Trend regimes are a deterministic grouping of the point-in-time market stage.
High volatility means point-in-time VIX >= 25; these are reporting categories,
not changes to Technical Events thresholds.

## Anti-look-ahead and integrity

- The stored entry is never replaced with a later entry price.
- Split/dividend adjustment uses only a mechanical adjustment factor.
- Outcomes use daily sessions strictly after `signal_day`.
- MAE/MFE use only the path through each matured horizon.
- The immutable signal ledger is never rewritten by this evaluator.
- Integrity errors: **{len(errors)}**
- Details: `{json.dumps(errors, ensure_ascii=False)}`

## Verdict

**{result}**

Reason: `{reason}`

No engine formula, weight, decay parameter, threshold, Enhanced score, or
authoritative decision is recalibrated by this report.
"""
    (output_dir / "technical_events_validation_report.md").write_text(
        report, encoding="utf-8"
    )
    coverage.to_csv(output_dir / "coverage.csv", index=False)
    return report, result


def generate_analysis(labelled):
    events = explode_events(labelled)
    return {
        "score_buckets": score_bucket_table(labelled),
        "directions": direction_table(labelled),
        "event_types": event_type_table(events),
        "recency": recency_table(events),
        "agreement": agreement_table(labelled),
        "support_resistance": support_resistance_table(events),
        "predictive_power": predictive_power_table(labelled),
        "score_comparison": score_comparison_table(labelled),
        "regimes": regime_table(labelled),
        "events": events,
    }


def _add_pending_columns(frame):
    result = frame.copy()
    for horizon in HORIZONS:
        result[f"outcome_status_{horizon}d"] = "pending"
        for metric in ("return_pct", "mae_pct", "mfe_pct"):
            result[f"{metric}_{horizon}d"] = np.nan
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", default=str(technical_events_shadow.LEDGER_PATH))
    parser.add_argument("--output", default=str(OUTPUT_DIR))
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    snapshots = technical_events_shadow.load_ledger(args.ledger)
    immutable_copy = copy.deepcopy(snapshots)
    flat = flatten_ledger(snapshots)
    labelled = (
        _add_pending_columns(flat)
        if args.offline or flat.empty
        else label_forward_outcomes(flat)
    )
    if snapshots != immutable_copy:
        raise RuntimeError("immutable Technical Events ledger was mutated")
    errors = integrity_errors(snapshots, labelled)
    tables = generate_analysis(labelled)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    serializable = labelled.copy()
    if "raw_events" in serializable:
        serializable["raw_events"] = serializable.raw_events.map(
            lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        )
    if "source_provenance" in serializable:
        serializable["source_provenance"] = serializable.source_provenance.map(
            lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        )
    # The point-in-time event payload is intentionally rich and grows with
    # every shadow run. Keep the complete dataset, but store it as gzip so it
    # remains practical to persist in Git without Git LFS.
    serializable.to_csv(
        output / "labelled_predictions.csv.gz",
        index=False,
        compression="gzip",
    )
    filenames = {
        "score_buckets": "score_buckets.csv",
        "directions": "direction_analysis.csv",
        "event_types": "event_types.csv",
        "recency": "recency_analysis.csv",
        "agreement": "timeframe_agreement.csv",
        "support_resistance": "support_resistance_events.csv",
        "predictive_power": "predictive_power.csv",
        "score_comparison": "score_comparison.csv",
        "regimes": "market_regimes.csv",
        "events": "event_observations.csv",
    }
    for key, filename in filenames.items():
        tables[key].to_csv(output / filename, index=False)
    write_report(labelled, tables, errors, output)
    (output / "integrity_report.json").write_text(json.dumps({
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "snapshots": len(snapshots),
        "observations": len(labelled),
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
