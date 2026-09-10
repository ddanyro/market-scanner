"""Transparent, deterministic Technical Events Engine running in shadow mode.

This module has no dependency on Baseline or Enhanced scoring.  It consumes
only point-in-time OHLCV bars and an optional benchmark series.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd


ENGINE_VERSION = "technical-events-v2-structural-shadow"


@dataclass(frozen=True)
class TimeframeConfig:
    lookback: int
    fast_sma: int
    slow_sma: int
    swing_order: int
    event_window: int
    recency_half_life: float
    roc_period: int
    structural_weight: float | None = None


# Trailing daily history plus weekly/monthly structural confirmation. These are
# transparent scanner horizons, not copies of any proprietary provider's model.
DEFAULT_TIMEFRAMES = {
    "SHORT_TERM": TimeframeConfig(63, 5, 20, 2, 15, 7.0, 5, 0.25),
    "INTERMEDIATE_TERM": TimeframeConfig(190, 20, 50, 3, 30, 20.0, 10, 0.65),
    "LONG_TERM": TimeframeConfig(320, 50, 200, 5, 45, 60.0, 20, 0.80),
}

DIRECTION_THRESHOLD = 57.0
BREAKOUT_MIN_PCT = 0.003
LEVEL_CLUSTER_MIN_PCT = 0.0075
VOLUME_CONFIRMATION_MULTIPLE = 1.5
VOLATILITY_EXPANSION_MULTIPLE = 1.2


def _number(value, default=None):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _normalize(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame()
    data = frame.copy()
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    required = ("Open", "High", "Low", "Close")
    if any(column not in data for column in required):
        return pd.DataFrame()
    for column in (*required, "Volume"):
        if column not in data:
            data[column] = np.nan
        data[column] = pd.to_numeric(data[column], errors="coerce")
    index = pd.to_datetime(data.index)
    if getattr(index, "tz", None) is not None:
        index = index.tz_convert(None)
    data.index = index.normalize()
    data = data.dropna(subset=list(required)).sort_index()
    return data[~data.index.duplicated(keep="last")]


def _rsi(close: pd.Series, period=14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50.0)


def _atr(frame: pd.DataFrame, period=14) -> pd.Series:
    previous = frame.Close.shift(1)
    true_range = pd.concat([
        frame.High - frame.Low,
        (frame.High - previous).abs(),
        (frame.Low - previous).abs(),
    ], axis=1).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def _pivot_values(series: pd.Series, order: int, high: bool) -> list[dict]:
    values = series.to_numpy(float)
    result = []
    for index in range(order, len(values) - order):
        window = values[index - order:index + order + 1]
        value = values[index]
        is_pivot = value >= np.max(window) if high else value <= np.min(window)
        if is_pivot and np.sum(np.isclose(window, value)) == 1:
            result.append({
                "index": index,
                "timestamp": pd.Timestamp(series.index[index]).isoformat(),
                "price": float(value),
            })
    return result


def _cluster_levels(pivots: list[dict], current_price: float, atr: float) -> list[dict]:
    tolerance = max(current_price * LEVEL_CLUSTER_MIN_PCT, atr * 0.5)
    clusters: list[list[dict]] = []
    for pivot in sorted(pivots, key=lambda item: item["price"]):
        target = next((
            cluster for cluster in clusters
            if abs(np.mean([item["price"] for item in cluster]) - pivot["price"])
            <= tolerance
        ), None)
        if target is None:
            clusters.append([pivot])
        else:
            target.append(pivot)
    levels = []
    total = max((pivot["index"] for pivot in pivots), default=1)
    for cluster in clusters:
        price = float(np.mean([item["price"] for item in cluster]))
        recency = max(item["index"] for item in cluster) / max(total, 1)
        levels.append({
            "price": round(price, 6),
            "touches": len(cluster),
            "strength": round(min(100.0, 35 + 15 * len(cluster) + 20 * recency), 2),
            "last_touch": max(item["timestamp"] for item in cluster),
        })
    return sorted(levels, key=lambda item: item["price"])


def support_resistance(frame, config: TimeframeConfig) -> dict[str, Any]:
    data = _normalize(frame).tail(config.lookback)
    if len(data) < max(20, config.swing_order * 2 + 3):
        return {"available": False, "reason": "insufficient_ohlc_history"}
    price = float(data.Close.iloc[-1])
    atr = float(_atr(data).iloc[-1])
    supports = _cluster_levels(
        _pivot_values(data.Low, config.swing_order, high=False), price, atr
    )
    resistances = _cluster_levels(
        _pivot_values(data.High, config.swing_order, high=True), price, atr
    )
    support = max((item for item in supports if item["price"] <= price), key=lambda item: item["price"], default=None)
    resistance = min((item for item in resistances if item["price"] >= price), key=lambda item: item["price"], default=None)
    threshold = max(price * BREAKOUT_MIN_PCT, atr * 0.25)
    return {
        "available": True,
        "method": "confirmed_swing_extrema_clustered_by_max_0.75pct_or_half_ATR",
        "support_levels": supports,
        "resistance_levels": resistances,
        "nearest_support": support["price"] if support else None,
        "nearest_resistance": resistance["price"] if resistance else None,
        "distance_to_support_pct": round((price / support["price"] - 1) * 100, 3) if support else None,
        "distance_to_resistance_pct": round((resistance["price"] / price - 1) * 100, 3) if resistance else None,
        "breakout_threshold": round(threshold, 6),
    }


def recency_factor(age_sessions: int, half_life: float) -> float:
    return 0.5 ** (max(age_sessions, 0) / max(half_life, 1e-9))


def _event(events, *, event_type, name, direction, timestamp, timeframe,
           raw_strength, age, half_life, price, confirmed, source_data):
    strength = max(0.0, min(100.0, float(raw_strength)))
    factor = recency_factor(age, half_life)
    events.append({
        "type": event_type,
        "name": name,
        "direction": direction,
        "timestamp": pd.Timestamp(timestamp).isoformat(),
        "timeframe": timeframe,
        "strength": round(strength, 2),
        "recency_factor": round(factor, 6),
        "effective_strength": round(strength * factor, 2),
        "age_sessions": int(age),
        "price_at_event": round(float(price), 6),
        "confirmation_status": "CONFIRMED" if confirmed else "UNCONFIRMED",
        "source_data": source_data,
    })


def _direction(score):
    if score >= DIRECTION_THRESHOLD:
        return "BULLISH"
    if score <= 100 - DIRECTION_THRESHOLD:
        return "BEARISH"
    return "NEUTRAL"


def _bounded_signal(value, scale):
    """Map a signed observation to [-1, 1] without a hard bucket."""
    value = _number(value, 0.0)
    return max(-1.0, min(1.0, value / max(float(scale), 1e-9)))


def _last_return(close, periods):
    if len(close) <= periods or not close.iloc[-periods - 1]:
        return None
    return float(close.iloc[-1] / close.iloc[-periods - 1] - 1)


def _structural_trend(window, timeframe, config):
    """Calculate trailing trend state independently from recent events."""
    close = window.Close
    weekly = window.resample("W-FRI").last().dropna(subset=["Close"])
    monthly = window.resample("ME").last().dropna(subset=["Close"])
    evidence = []

    def add(name, signal, weight, raw):
        evidence.append({
            "name": name,
            "signal": round(float(max(-1.0, min(1.0, signal))), 6),
            "weight": float(weight),
            "raw_value": None if raw is None else round(float(raw), 8),
        })

    if timeframe == "LONG_TERM":
        sma50 = close.rolling(50).mean()
        sma200 = close.rolling(200).mean()
        if pd.notna(sma200.iloc[-1]):
            raw = close.iloc[-1] / sma200.iloc[-1] - 1
            add("price_vs_sma200", _bounded_signal(raw, 0.10), 0.25, raw)
            slope = sma200.iloc[-1] / sma200.iloc[-41] - 1 if len(sma200.dropna()) > 40 else None
            if slope is not None and pd.notna(slope):
                add("sma200_40d_slope", _bounded_signal(slope, 0.04), 0.20, slope)
        if pd.notna(sma50.iloc[-1]) and pd.notna(sma200.iloc[-1]):
            raw = sma50.iloc[-1] / sma200.iloc[-1] - 1
            add("sma50_vs_sma200", _bounded_signal(raw, 0.08), 0.20, raw)
        raw = _last_return(close, min(252, len(close) - 1))
        if raw is not None:
            add("trailing_12m_return", _bounded_signal(raw, 0.25), 0.15, raw)
        if len(close) >= 126:
            rolling_low, rolling_high = close.tail(252).min(), close.tail(252).max()
            location = (close.iloc[-1] - rolling_low) / max(rolling_high - rolling_low, 1e-9)
            add("52w_range_location", (location - 0.5) * 2, 0.10, location)
        if len(weekly) >= 40:
            fast_w = weekly.Close.rolling(10).mean().iloc[-1]
            slow_w = weekly.Close.rolling(40).mean().iloc[-1]
            raw = fast_w / slow_w - 1
            add("weekly_sma10_vs_sma40", _bounded_signal(raw, 0.08), 0.05, raw)
        if len(monthly) >= 9:
            fast_m = monthly.Close.rolling(3).mean().iloc[-1]
            slow_m = monthly.Close.rolling(9).mean().iloc[-1]
            raw = fast_m / slow_m - 1
            add("monthly_sma3_vs_sma9", _bounded_signal(raw, 0.10), 0.05, raw)
    elif timeframe == "INTERMEDIATE_TERM":
        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()
        if pd.notna(sma50.iloc[-1]):
            raw = close.iloc[-1] / sma50.iloc[-1] - 1
            add("price_vs_sma50", _bounded_signal(raw, 0.08), 0.30, raw)
            slope = sma50.iloc[-1] / sma50.iloc[-21] - 1 if len(sma50.dropna()) > 20 else None
            if slope is not None and pd.notna(slope):
                add("sma50_20d_slope", _bounded_signal(slope, 0.04), 0.25, slope)
        if pd.notna(sma20.iloc[-1]) and pd.notna(sma50.iloc[-1]):
            raw = sma20.iloc[-1] / sma50.iloc[-1] - 1
            add("sma20_vs_sma50", _bounded_signal(raw, 0.06), 0.20, raw)
        raw = _last_return(close, min(63, len(close) - 1))
        if raw is not None:
            add("trailing_3m_return", _bounded_signal(raw, 0.15), 0.15, raw)
        if len(weekly) >= 13:
            fast_w = weekly.Close.rolling(4).mean().iloc[-1]
            slow_w = weekly.Close.rolling(13).mean().iloc[-1]
            raw = fast_w / slow_w - 1
            add("weekly_sma4_vs_sma13", _bounded_signal(raw, 0.06), 0.10, raw)
    else:
        sma5 = close.rolling(5).mean()
        sma20 = close.rolling(20).mean()
        if pd.notna(sma20.iloc[-1]):
            raw = close.iloc[-1] / sma20.iloc[-1] - 1
            add("price_vs_sma20", _bounded_signal(raw, 0.05), 0.40, raw)
            slope = sma20.iloc[-1] / sma20.iloc[-11] - 1 if len(sma20.dropna()) > 10 else None
            if slope is not None and pd.notna(slope):
                add("sma20_10d_slope", _bounded_signal(slope, 0.03), 0.25, slope)
        if pd.notna(sma5.iloc[-1]) and pd.notna(sma20.iloc[-1]):
            raw = sma5.iloc[-1] / sma20.iloc[-1] - 1
            add("sma5_vs_sma20", _bounded_signal(raw, 0.04), 0.20, raw)
        raw = _last_return(close, min(20, len(close) - 1))
        if raw is not None:
            add("trailing_1m_return", _bounded_signal(raw, 0.10), 0.15, raw)

    weight = sum(item["weight"] for item in evidence)
    signed = sum(item["signal"] * item["weight"] for item in evidence) / weight if weight else 0.0
    score = 50 + 50 * signed
    return {
        "available": bool(evidence),
        "score": round(score, 2),
        "direction": _direction(score),
        "evidence": evidence,
        "method": "trailing_multi_horizon_structural_trend_v1",
    }


def _event_is_eligible(event, timeframe):
    """Keep fast oscillators out of structural horizons."""
    name = event.get("name", "")
    if timeframe == "LONG_TERM":
        return (
            "SMA crossover" in name
            or event.get("type") in {
                "BREAKOUT", "BREAKDOWN", "RELATIVE_STRENGTH",
                "VOLUME_CONFIRMATION",
            }
        )
    if timeframe == "INTERMEDIATE_TERM" and event.get("type") == "VOLATILITY":
        return False
    return True


def _event_family(event):
    name = event.get("name", "")
    if "SMA crossover" in name:
        return "TREND_CROSS"
    if "RSI" in name or "MACD" in name or "momentum reversal" in name:
        return "MOMENTUM"
    if event.get("type") in {
        "BREAKOUT", "BREAKDOWN", "BOUNCE", "REVERSAL",
        "VOLUME_CONFIRMATION",
    }:
        return "PRICE_STRUCTURE"
    return event.get("type", "OTHER")


def _score_event_flow(events):
    """Discount correlated observations while retaining them for audit/UI."""
    grouped = {}
    for event in events:
        key = (_event_family(event), event["direction"])
        grouped.setdefault(key, []).append(event)
    totals = {"BULLISH": 0.0, "BEARISH": 0.0}
    for (family, direction), members in grouped.items():
        members.sort(key=lambda item: item["effective_strength"], reverse=True)
        for index, event in enumerate(members):
            multiplier = 1.0 if index == 0 else 0.35
            contribution = event["effective_strength"] * multiplier
            event["signal_family"] = family
            event["correlation_discount"] = multiplier
            event["scoring_effective_strength"] = round(contribution, 2)
            totals[direction] += contribution
    total = totals["BULLISH"] + totals["BEARISH"]
    score = 50.0 if total == 0 else 50 + 50 * (totals["BULLISH"] - totals["BEARISH"]) / total
    return score, totals


def _timeframe_analysis(data, benchmark, name, config, source):
    window = data.tail(config.lookback).copy()
    minimum = max(config.slow_sma + 2, 30)
    if len(window) < minimum:
        return {
            "available": False, "direction": "NEUTRAL", "event_score": 50.0,
            "bullish_events": 0, "bearish_events": 0, "events": [],
            "reason": f"requires_{minimum}_bars_has_{len(window)}",
            "support_resistance": support_resistance(window, config),
            "configuration": asdict(config),
        }
    close = window.Close
    volume = window.Volume
    fast = close.rolling(config.fast_sma).mean()
    slow = close.rolling(config.slow_sma).mean()
    rsi = _rsi(close)
    macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    signal = macd.ewm(span=9, adjust=False).mean()
    roc = close.pct_change(config.roc_period)
    atr = _atr(window)
    atr_pct = atr / close
    average_volume = volume.rolling(20).mean()
    levels = support_resistance(window, config)
    events = []
    start = max(1, len(window) - config.event_window)
    for i in range(start, len(window)):
        age = len(window) - 1 - i
        common = dict(timestamp=window.index[i], timeframe=name, age=age,
                      half_life=config.recency_half_life, price=close.iloc[i])
        if pd.notna(slow.iloc[i - 1]) and fast.iloc[i - 1] <= slow.iloc[i - 1] and fast.iloc[i] > slow.iloc[i]:
            magnitude = abs(fast.iloc[i] / slow.iloc[i] - 1) * 100
            _event(events, event_type="CROSSOVER", name="bullish SMA crossover", direction="BULLISH", raw_strength=60 + min(20, magnitude * 20), confirmed=True, source_data={"fast_sma": config.fast_sma, "slow_sma": config.slow_sma}, **common)
        if pd.notna(slow.iloc[i - 1]) and fast.iloc[i - 1] >= slow.iloc[i - 1] and fast.iloc[i] < slow.iloc[i]:
            magnitude = abs(fast.iloc[i] / slow.iloc[i] - 1) * 100
            _event(events, event_type="CROSSUNDER", name="bearish SMA crossover", direction="BEARISH", raw_strength=60 + min(20, magnitude * 20), confirmed=True, source_data={"fast_sma": config.fast_sma, "slow_sma": config.slow_sma}, **common)
        bearish_rsi_threshold = {
            "SHORT_TERM": 60,
            "INTERMEDIATE_TERM": 50,
            "LONG_TERM": 45,
        }.get(name, 55)
        bullish_rsi_threshold = 100 - bearish_rsi_threshold
        for crossed, event_type, label, direction in (
            (roc.iloc[i - 1] <= 0 < roc.iloc[i], "REVERSAL", "bullish momentum reversal", "BULLISH"),
            (roc.iloc[i - 1] >= 0 > roc.iloc[i], "REVERSAL", "bearish momentum reversal", "BEARISH"),
            (rsi.iloc[i - 1] <= bullish_rsi_threshold < rsi.iloc[i], "MOMENTUM", "RSI bullish recovery", "BULLISH"),
            (rsi.iloc[i - 1] >= bearish_rsi_threshold > rsi.iloc[i], "MOMENTUM", "RSI deterioration", "BEARISH"),
            (macd.iloc[i - 1] <= signal.iloc[i - 1] and macd.iloc[i] > signal.iloc[i], "CROSSOVER", "MACD bullish crossover", "BULLISH"),
            (macd.iloc[i - 1] >= signal.iloc[i - 1] and macd.iloc[i] < signal.iloc[i], "CROSSUNDER", "MACD bearish crossover", "BEARISH"),
        ):
            if crossed:
                _event(events, event_type=event_type, name=label, direction=direction, raw_strength=58 if "RSI" not in label else 62, confirmed=True, source_data={"roc_period": config.roc_period, "rsi": round(float(rsi.iloc[i]), 3), "macd": round(float(macd.iloc[i]), 6)}, **common)

    latest = len(window) - 1
    previous_close = float(close.iloc[-2])
    threshold = _number(levels.get("breakout_threshold"), 0)
    resistance = _number(levels.get("nearest_resistance"))
    support = _number(levels.get("nearest_support"))
    broken_resistance = max((
        _number(item.get("price")) for item in levels.get("resistance_levels", [])
        if _number(item.get("price")) is not None
        and _number(item.get("price")) < close.iloc[-1]
    ), default=None)
    broken_support = min((
        _number(item.get("price")) for item in levels.get("support_levels", [])
        if _number(item.get("price")) is not None
        and _number(item.get("price")) > close.iloc[-1]
    ), default=None)
    bullish_breakout = broken_resistance is not None and previous_close <= broken_resistance + threshold and close.iloc[-1] > broken_resistance + threshold
    bearish_breakdown = broken_support is not None and previous_close >= broken_support - threshold and close.iloc[-1] < broken_support - threshold
    volume_confirmed = pd.notna(average_volume.iloc[-1]) and volume.iloc[-1] >= average_volume.iloc[-1] * VOLUME_CONFIRMATION_MULTIPLE
    if bullish_breakout:
        _event(events, event_type="BREAKOUT", name="price breakout above resistance", direction="BULLISH", raw_strength=75, confirmed=True, timestamp=window.index[-1], timeframe=name, age=0, half_life=config.recency_half_life, price=close.iloc[-1], source_data={"resistance": broken_resistance, "threshold": threshold})
    if bearish_breakdown:
        _event(events, event_type="BREAKDOWN", name="breakdown below support", direction="BEARISH", raw_strength=75, confirmed=True, timestamp=window.index[-1], timeframe=name, age=0, half_life=config.recency_half_life, price=close.iloc[-1], source_data={"support": broken_support, "threshold": threshold})
    if volume_confirmed and (bullish_breakout or bearish_breakdown):
        direction = "BULLISH" if bullish_breakout else "BEARISH"
        _event(events, event_type="VOLUME_CONFIRMATION", name=f"volume-confirmed {'breakout' if bullish_breakout else 'breakdown'}", direction=direction, raw_strength=78, confirmed=True, timestamp=window.index[-1], timeframe=name, age=0, half_life=config.recency_half_life, price=close.iloc[-1], source_data={"volume_multiple": round(float(volume.iloc[-1] / average_volume.iloc[-1]), 3)})

    highs = _pivot_values(window.High, config.swing_order, high=True)
    lows = _pivot_values(window.Low, config.swing_order, high=False)
    for pivots, direction, label, event_type in (
        (highs, "BULLISH", "higher-high breakout", "BREAKOUT"),
        (lows, "BEARISH", "lower-low breakdown", "BREAKDOWN"),
    ):
        if len(pivots) >= 2:
            first, second = pivots[-2], pivots[-1]
            condition = second["price"] > first["price"] if direction == "BULLISH" else second["price"] < first["price"]
            age = len(window) - 1 - second["index"]
            if condition and age <= config.event_window:
                _event(events, event_type=event_type, name=label, direction=direction, raw_strength=68, confirmed=True, timestamp=window.index[second["index"]], timeframe=name, age=age, half_life=config.recency_half_life, price=second["price"], source_data={"previous_pivot": first["price"], "swing_order": config.swing_order})

    if support is not None and window.Low.iloc[-1] <= support + threshold and close.iloc[-1] > support and close.iloc[-1] > previous_close:
        _event(events, event_type="BOUNCE", name="bounce from support", direction="BULLISH", raw_strength=64, confirmed=True, timestamp=window.index[-1], timeframe=name, age=0, half_life=config.recency_half_life, price=close.iloc[-1], source_data={"support": support})
    if resistance is not None and window.High.iloc[-1] >= resistance - threshold and close.iloc[-1] < resistance and close.iloc[-1] < previous_close:
        _event(events, event_type="REVERSAL", name="rejection from resistance", direction="BEARISH", raw_strength=64, confirmed=True, timestamp=window.index[-1], timeframe=name, age=0, half_life=config.recency_half_life, price=close.iloc[-1], source_data={"resistance": resistance})

    recent_vol = atr_pct.rolling(20).mean().iloc[-1]
    if pd.notna(recent_vol) and atr_pct.iloc[-1] > recent_vol * VOLATILITY_EXPANSION_MULTIPLE:
        direction = "BULLISH" if close.iloc[-1] > previous_close else "BEARISH"
        _event(events, event_type="VOLATILITY", name=f"volatility expansion {direction.lower()}", direction=direction, raw_strength=60, confirmed=True, timestamp=window.index[-1], timeframe=name, age=0, half_life=config.recency_half_life, price=close.iloc[-1], source_data={"atr_expansion_multiple": round(float(atr_pct.iloc[-1] / recent_vol), 3)})

    if benchmark is not None and not benchmark.empty:
        aligned = pd.concat([close.rename("stock"), benchmark.Close.rename("benchmark")], axis=1).dropna()
        if len(aligned) >= 22:
            relative = aligned.stock / aligned.benchmark
            prior_high = relative.shift(1).rolling(20).max().iloc[-1]
            prior_low = relative.shift(1).rolling(20).min().iloc[-1]
            if pd.notna(prior_high) and relative.iloc[-1] > prior_high:
                _event(events, event_type="RELATIVE_STRENGTH", name="relative-strength breakout", direction="BULLISH", raw_strength=70, confirmed=True, timestamp=aligned.index[-1], timeframe=name, age=0, half_life=config.recency_half_life, price=close.iloc[-1], source_data={"benchmark": source.get("benchmark")})
            elif pd.notna(prior_low) and relative.iloc[-1] < prior_low:
                _event(events, event_type="RELATIVE_STRENGTH", name="relative-strength breakdown", direction="BEARISH", raw_strength=70, confirmed=True, timestamp=aligned.index[-1], timeframe=name, age=0, half_life=config.recency_half_life, price=close.iloc[-1], source_data={"benchmark": source.get("benchmark")})

    eligible_events = [item for item in events if _event_is_eligible(item, name)]
    excluded_events = [item for item in events if item not in eligible_events]
    for item in excluded_events:
        item["excluded_from_score"] = True
        item["exclusion_reason"] = f"not_eligible_for_{name.lower()}"
        item["scoring_effective_strength"] = 0.0
    event_flow_score, flow = _score_event_flow(eligible_events)
    bullish = flow["BULLISH"]
    bearish = flow["BEARISH"]
    structural = _structural_trend(window, name, config)
    default_structural_weights = {
        "SHORT_TERM": 0.25,
        "INTERMEDIATE_TERM": 0.65,
        "LONG_TERM": 0.80,
    }
    structural_weight = config.structural_weight
    if structural_weight is None:
        structural_weight = default_structural_weights.get(name, 0.30)
    if not structural["available"]:
        structural_weight = 0.0
    score = (
        structural_weight * structural["score"]
        + (1 - structural_weight) * event_flow_score
    )
    return {
        "available": True,
        "direction": _direction(score),
        "bullish_events": sum(item["direction"] == "BULLISH" for item in events),
        "bearish_events": sum(item["direction"] == "BEARISH" for item in events),
        "event_score": round(score, 2),
        "recent_event_score": round(event_flow_score, 2),
        "structural_score": structural["score"],
        "structural_direction": structural["direction"],
        "structural_trend": structural,
        "structural_weight": round(structural_weight, 4),
        "score_formula": "structural_weight * structural_score + (1 - structural_weight) * recent_event_score",
        "effective_bullish_strength": round(bullish, 2),
        "effective_bearish_strength": round(bearish, 2),
        "scored_events": len(eligible_events),
        "excluded_events": len(excluded_events),
        "events": sorted(events, key=lambda item: (item["timestamp"], item["effective_strength"]), reverse=True),
        "support_resistance": levels,
        "configuration": asdict(config),
    }


def conflict_description(directions: dict[str, str]) -> str | None:
    short = directions.get("SHORT_TERM")
    intermediate = directions.get("INTERMEDIATE_TERM")
    long = directions.get("LONG_TERM")
    if short == "BEARISH" and intermediate == long == "BULLISH":
        return "SHORT-TERM PULLBACK INSIDE LONG-TERM BULL TREND"
    if short == "BULLISH" and intermediate == long == "BEARISH":
        return "SHORT-TERM RALLY INSIDE LONG-TERM BEAR TREND"
    if len({value for value in directions.values() if value != "NEUTRAL"}) > 1:
        return "MIXED SIGNALS ACROSS TIMEFRAMES"
    return None


def analyze(frame, benchmark_frame=None, *, source=None, timeframe_config=None,
            generated_at=None):
    data = _normalize(frame)
    benchmark = _normalize(benchmark_frame)
    configs = timeframe_config or DEFAULT_TIMEFRAMES
    source = dict(source or {})
    if data.empty:
        return {
            "engine_version": ENGINE_VERSION, "available": False,
            "reason": "missing_or_invalid_ohlcv", "overall_direction": "NEUTRAL",
            "overall_event_score": 50.0, "confidence": 0.0,
            "timeframes": {}, "events": [],
        }
    summaries = {
        name: _timeframe_analysis(data, benchmark, name, config, source)
        for name, config in configs.items()
    }
    weights = {"SHORT_TERM": 0.30, "INTERMEDIATE_TERM": 0.40, "LONG_TERM": 0.30}
    available = [name for name, value in summaries.items() if value["available"]]
    weight_total = sum(weights[name] for name in available)
    overall_score = (
        sum(summaries[name]["event_score"] * weights[name] for name in available) / weight_total
        if weight_total else 50.0
    )
    events = [event for summary in summaries.values() for event in summary["events"]]
    scored_events = [event for event in events if not event.get("excluded_from_score")]
    directions = {name: value["direction"] for name, value in summaries.items()}
    directional = [value for value in directions.values() if value != "NEUTRAL"]
    agreement = max((directional.count(value) for value in set(directional)), default=0) / max(len(directional), 1)
    confirmation = sum(item["confirmation_status"] == "CONFIRMED" for item in scored_events) / max(len(scored_events), 1)
    mean_strength = np.mean([item.get("scoring_effective_strength", 0) for item in scored_events]) if scored_events else 0
    confidence = min(100.0, min(len(scored_events) / 8, 1) * 25 + mean_strength / 100 * 30 + agreement * 25 + confirmation * 20)
    bullish_events = [item for item in scored_events if item["direction"] == "BULLISH"]
    bearish_events = [item for item in scored_events if item["direction"] == "BEARISH"]
    latest_levels = next((summaries[name]["support_resistance"] for name in ("INTERMEDIATE_TERM", "SHORT_TERM", "LONG_TERM") if summaries.get(name, {}).get("support_resistance", {}).get("available")), {})
    input_rows = [
        [str(index), *[round(float(row[column]), 8) for column in ("Open", "High", "Low", "Close")]]
        for index, row in data.iterrows()
    ]
    input_hash = hashlib.sha256(json.dumps(input_rows, separators=(",", ":")).encode()).hexdigest()
    return {
        "engine_version": ENGINE_VERSION,
        "shadow_mode": True,
        "affects_baseline": False,
        "affects_enhanced": False,
        "available": bool(available),
        "generated_at": generated_at,
        "data_as_of": pd.Timestamp(data.index[-1]).isoformat(),
        "input_provenance": {
            **source, "bars": len(data), "input_ohlc_sha256": input_hash,
            "future_outcomes_present": False,
        },
        "timeframes": summaries,
        "events": events,
        "total_events": len(events),
        "scored_events": len(scored_events),
        "excluded_events": len(events) - len(scored_events),
        "bullish_events": len(bullish_events),
        "bearish_events": len(bearish_events),
        "net_events": len(bullish_events) - len(bearish_events),
        "overall_event_score": round(overall_score, 2),
        "overall_direction": _direction(overall_score),
        "confidence": round(confidence, 2),
        "conflict": conflict_description(directions),
        "strongest_bullish_event": max(bullish_events, key=lambda item: item["effective_strength"], default=None),
        "strongest_bearish_event": max(bearish_events, key=lambda item: item["effective_strength"], default=None),
        "nearest_support": latest_levels.get("nearest_support"),
        "nearest_resistance": latest_levels.get("nearest_resistance"),
        "support_resistance": latest_levels,
        "forward_validation_horizons": [1, 5, 10, 20, 60],
    }
