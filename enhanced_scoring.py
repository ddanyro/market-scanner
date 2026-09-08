"""Transparent shadow scoring for IBKR-enriched stock candidates.

The existing four-check BUY/WAIT/AVOID decision remains authoritative.  This
module only produces a comparable enhanced decision and explicit components.
Every component is 0..100; missing optional evidence is neutral (50), never a
silent penalty.
"""

from __future__ import annotations

import math
from typing import Any


RAW_SCORE_WEIGHTS = {
    "technical_score": 0.25,
    "momentum_score": 0.15,
    "research_score": 0.10,
    "volatility_score": 0.10,
    "liquidity_score": 0.10,
    "options_score": 0.10,
    "relative_opportunity_score": 0.10,
    "risk_reward_score": 0.10,
}
PORTFOLIO_RAW_WEIGHT = 0.85
PORTFOLIO_FIT_WEIGHT = 0.15


def _number(value: Any, default: float | None = None) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _first_number(item: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = _number(item.get(key))
        if value is not None:
            return value
    return None


def _fraction_to_pct(value: float | None) -> float | None:
    if value is None:
        return None
    return value * 100 if abs(value) <= 2 else value


def technical_score(item: dict[str, Any]) -> float:
    checks = _first_number(item, "Checks_Passed", "checks_passed")
    if checks is not None:
        return _clamp(checks / 4 * 100)
    decision = str(item.get("Decision") or item.get("decision") or "").upper()
    return {"BUY": 100, "WAIT": 70, "HOLD": 60, "AVOID": 25}.get(decision, 50)


def momentum_score(item: dict[str, Any]) -> float:
    rs = _first_number(item, "RS_vs_SPX", "relative_strength")
    rsi = _first_number(item, "RSI", "rsi")
    rs_score = 50 if rs is None else _clamp(50 + rs * 2)
    if rsi is None:
        rsi_score = 50
    elif 45 <= rsi <= 65:
        rsi_score = 90
    elif 35 <= rsi < 45 or 65 < rsi <= 72:
        rsi_score = 65
    else:
        rsi_score = 30
    return round(rs_score * 0.65 + rsi_score * 0.35, 2)


def research_score(item: dict[str, Any]) -> float:
    consensus = str(item.get("Consensus") or item.get("consensus") or "").lower()
    score = {
        "strong buy": 95, "buy": 85, "hold": 55,
        "underperform": 25, "sell": 15,
    }.get(consensus, 50)
    analysts = _first_number(item, "Analysts", "analysts") or 0
    if analysts >= 10:
        score += 5
    if item.get("Earnings_Danger") or item.get("earnings_risk"):
        score -= 15
    return _clamp(score)


def volatility_score(item: dict[str, Any]) -> tuple[float, str]:
    price = _first_number(item, "Price", "price_eur", "Price_Native") or 0
    atr = _first_number(item, "ATR_14", "atr_eur") or 0
    atr_pct = atr / price * 100 if price > 0 and atr > 0 else None
    hv_pct = _fraction_to_pct(_first_number(item, "Historical_Vol", "historical_vol"))
    iv_pct = _fraction_to_pct(_first_number(item, "Implied_Volatility", "implied_volatility"))
    iv_rank = _fraction_to_pct(_first_number(item, "IV_Percentile", "iv_percentile"))
    observed = [value for value in (hv_pct, iv_pct) if value is not None]
    reference = max(observed) if observed else None
    score = 75.0
    if atr_pct is not None:
        score -= max(atr_pct - 3, 0) * 5
    if reference is not None:
        score -= max(reference - 35, 0) * 0.8
    if iv_rank is not None:
        score -= max(iv_rank - 70, 0) * 1.1
    score = _clamp(score)
    if score >= 70:
        regime = "calm"
    elif score >= 45:
        regime = "elevated"
    else:
        regime = "extreme"
    return round(score, 2), regime


def liquidity_score(item: dict[str, Any]) -> float:
    usd_volume = _first_number(item, "Avg_90D_USD_Volume", "avg_90d_usd_volume")
    relative_volume = _first_number(item, "Relative_Volume_20D", "relative_volume_20d")
    if usd_volume is not None and usd_volume > 0:
        # Log scaling: roughly 35 at $100k/day, 65 at $10m, 95 at $1bn.
        score = 35 + max(math.log10(usd_volume) - 5, 0) * 15
    else:
        score = 50
    if relative_volume is not None:
        score += _clamp((relative_volume - 1) * 20, -15, 15)
    spread = _first_number(item, "Spread_Pct", "spread_pct")
    if spread is not None:
        score -= max(spread - 0.25, 0) * 25
    return round(_clamp(score), 2)


def options_score(item: dict[str, Any]) -> float:
    context = item.get("Options_Context") or item.get("options_context") or {}
    if not isinstance(context, dict) or not context.get("available"):
        return 50.0
    score = 65.0
    spread = _number(context.get("average_spread_pct"))
    if spread is not None:
        score -= max(spread - 2, 0) * 3
    put_call_volume = _number(context.get("put_call_volume_ratio"))
    if put_call_volume is not None and put_call_volume > 1.5:
        score -= min((put_call_volume - 1.5) * 15, 25)
    put_call_oi = _number(context.get("put_call_open_interest_ratio"))
    if put_call_oi is not None and put_call_oi > 1.5:
        score -= min((put_call_oi - 1.5) * 10, 15)
    quoted = _number(context.get("quoted_contract_ratio"))
    if quoted is not None:
        score += (quoted - 0.5) * 20
    return round(_clamp(score), 2)


def relative_opportunity_score(item: dict[str, Any]) -> float:
    context = item.get("Company_Context") or item.get("company_context") or {}
    if not isinstance(context, dict) or not context.get("available"):
        return 50.0
    # Theme relevance alone is not price opportunity.  Keep this neutral until
    # peer market metrics have been collected and a real percentile exists.
    percentile = _number(context.get("relative_performance_percentile"))
    return 50.0 if percentile is None else round(_clamp(percentile), 2)


def risk_reward_score(item: dict[str, Any]) -> float:
    rr = _first_number(item, "RR_Ratio", "rr_ratio")
    return 50.0 if rr is None else round(_clamp(rr / 4 * 100), 2)


def calculate_scores(
    item: dict[str, Any], *, portfolio_fit_score: float | None = None,
) -> dict[str, Any]:
    vol_score, regime = volatility_score(item)
    components = {
        "technical_score": technical_score(item),
        "momentum_score": momentum_score(item),
        "research_score": research_score(item),
        "volatility_score": vol_score,
        "liquidity_score": liquidity_score(item),
        "options_score": options_score(item),
        "relative_opportunity_score": relative_opportunity_score(item),
        "risk_reward_score": risk_reward_score(item),
    }
    raw = sum(components[key] * weight for key, weight in RAW_SCORE_WEIGHTS.items())
    options_context = item.get("Options_Context") or item.get("options_context") or {}
    options_observed = bool(
        isinstance(options_context, dict) and options_context.get("available")
    )
    observed_weights = dict(RAW_SCORE_WEIGHTS)
    if not options_observed:
        observed_weights.pop("options_score")
    observed_weight_total = sum(observed_weights.values())
    availability_adjusted_raw = sum(
        components[key] * weight for key, weight in observed_weights.items()
    ) / observed_weight_total
    fit = _clamp(portfolio_fit_score if portfolio_fit_score is not None else 50)
    adjusted = raw * PORTFOLIO_RAW_WEIGHT + fit * PORTFOLIO_FIT_WEIGHT
    risk = (
        components["volatility_score"] * 0.4
        + components["liquidity_score"] * 0.3
        + components["options_score"] * 0.15
        + fit * 0.15
    )
    current = str(item.get("Decision") or item.get("decision") or "WAIT").upper()
    enhanced = current
    reasons: list[str] = []
    quote_status = str(item.get("Quote_Status") or item.get("quote_status") or "").upper()
    spread = _first_number(item, "Spread_Pct", "spread_pct")
    iv_rank = _fraction_to_pct(_first_number(item, "IV_Percentile", "iv_percentile"))
    if current == "BUY":
        if quote_status == "REJECT":
            reasons.append("IBKR quote status is REJECT")
        if spread is not None and spread > 1.5:
            reasons.append(f"bid/ask spread is {spread:.2f}%")
        if components["liquidity_score"] < 30:
            reasons.append("Liquidity Score is below 30")
        if iv_rank is not None and iv_rank >= 90 and vol_score < 35:
            reasons.append("IV percentile is extreme")
        if fit < 30:
            reasons.append("Portfolio Concentration Penalty")
        if reasons:
            enhanced = "WAIT"
    price = _first_number(item, "Price", "price_eur", "Price_Native") or 0
    atr = _first_number(item, "ATR_14", "atr_eur") or 0
    hv = _fraction_to_pct(_first_number(item, "Historical_Vol", "historical_vol"))
    stop_distances = [2 * atr] if atr > 0 else []
    if price > 0 and hv is not None and hv > 0:
        stop_distances.append(2 * price * (hv / 100) / math.sqrt(252))
    enhanced_stop = (
        price - max(stop_distances)
        if price > 0 and stop_distances and max(stop_distances) < price
        else None
    )
    return {
        **{key: round(value, 2) for key, value in components.items()},
        "portfolio_fit_score": round(fit, 2),
        "raw_stock_score": round(raw, 2),
        # Diagnostic only: preserves the registered score while allowing a
        # fair observed-vs-control analysis when option evidence is missing.
        "raw_stock_score_availability_adjusted": round(
            availability_adjusted_raw, 2
        ),
        "options_score_observed": (
            round(components["options_score"], 2) if options_observed else None
        ),
        "portfolio_adjusted_score": round(adjusted, 2),
        "risk_score": round(_clamp(risk), 2),
        "volatility_regime": regime,
        "current_decision": current,
        "enhanced_decision": enhanced,
        "enhanced_decision_reason": "; ".join(reasons),
        "enhanced_stop": round(enhanced_stop, 4) if enhanced_stop else None,
        "enhanced_stop_distance_pct": round(
            (price - enhanced_stop) / price * 100, 2
        ) if enhanced_stop and price > 0 else None,
        "score_version": "ibkr-enhanced-v1-shadow",
    }
