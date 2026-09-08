"""Append-only, point-in-time ledger for Enhanced Scoring validation.

This module records evidence; it never changes scoring weights or the
authoritative BUY/WAIT/AVOID decision.  Feature availability is first-class so
that a neutral formula fallback cannot be mistaken for observed IBKR data.
"""

from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any


LEDGER_PATH = Path("shadow_predictions.jsonl")
POLICY_PATH = Path("shadow_validation_policy.json")
REPORT_PATH = Path("analysis/shadow_forward_validation/readiness_report.md")
SCHEMA = "market-scanner.shadow-prediction.v1"
COMPONENTS = (
    "technical_score", "momentum_score", "research_score",
    "volatility_score", "liquidity_score", "options_score",
    "relative_opportunity_score", "risk_reward_score",
)


def _number(value: Any, default=None):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _utc_timestamp(value=None):
    if isinstance(value, dt.datetime):
        parsed = value
    elif value:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    else:
        parsed = dt.datetime.now(dt.timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc).isoformat(timespec="seconds")


def load_policy(path=POLICY_PATH):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not payload.get("holdout_is_locked"):
        raise ValueError("Shadow holdout policy must remain locked")
    return payload


def policy_hash(policy):
    canonical = json.dumps(policy, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sample_partition(timestamp, policy):
    day = str(timestamp)[:10]
    if day < policy["collection_start"]:
        return "pre_collection"
    if day <= policy["calibration_end"]:
        return "calibration"
    if policy["holdout_start"] <= day <= policy["holdout_end"]:
        return "holdout_locked"
    return "post_holdout_monitoring"


def _cost_assumptions(candidate):
    currency = str(
        candidate.get("execution_currency") or candidate.get("currency") or ""
    ).upper()
    return {
        "model_version": "ibkr-estimated-v1",
        "commission_per_share": _number(
            os.environ.get("SHADOW_IBKR_COMMISSION_PER_SHARE"), 0.005
        ),
        "minimum_commission_per_order": _number(
            os.environ.get("SHADOW_IBKR_MIN_COMMISSION"), 1.0
        ),
        "slippage_bps_per_side": _number(
            os.environ.get("SHADOW_SLIPPAGE_BPS_PER_SIDE"), 5.0
        ),
        "fx_bps_per_conversion": _number(
            os.environ.get("SHADOW_FX_BPS_PER_CONVERSION"), 3.0
        ),
        "round_trip_fx_conversions_assumed": 2 if currency not in {"", "EUR"} else 0,
        "spread_pct_at_signal": _number(candidate.get("spread_pct")),
        "assumption_status": "estimated_configurable_not_realized",
    }


def _entry_snapshot(candidate):
    ask = _number(candidate.get("ask"))
    last = _number(candidate.get("price_native"), _number(candidate.get("entry_native")))
    if ask and ask > 0:
        price, source = ask, "ask_at_signal"
    elif last and last > 0:
        price, source = last, "last_available_at_signal"
    else:
        price, source = None, "missing"
    data_age_hours = _number(candidate.get("data_age_hours"))
    return {
        "price": price,
        "source": source,
        "bid": _number(candidate.get("bid")),
        "ask": ask,
        "last": last,
        "spread_pct": _number(candidate.get("spread_pct")),
        "quote_status": candidate.get("quote_status"),
        "currency": candidate.get("execution_currency") or candidate.get("currency"),
        "market_data_source": candidate.get("market_data_source"),
        "market_data_fetched_at": candidate.get("market_data_fetched_at"),
        "data_as_of": candidate.get("data_as_of"),
        "data_age_hours": data_age_hours,
        "fresh_for_execution": bool(
            price is not None
            and (data_age_hours is None or data_age_hours <= 1.0)
        ),
    }


def _portfolio_snapshot(candidate):
    fit_available = bool(candidate.get("portfolio_fit_available"))
    fit = _number(candidate.get("portfolio_fit_observed_score")) if fit_available else None
    before = {
        "sector_pct": _number(candidate.get("ibkr_sector_weight_pct")),
        "country_pct": _number(candidate.get("ibkr_country_weight_pct")),
        "region_pct": _number(candidate.get("ibkr_region_weight_pct")),
        "symbol_direct_pct": _number(candidate.get("combined_pretrade_portfolio_weight_pct")),
    }
    after = {
        "sector_pct": _number(candidate.get("hypothetical_sector_weight_after_pct")),
        "country_pct": _number(candidate.get("hypothetical_country_weight_after_pct")),
        "region_pct": _number(candidate.get("hypothetical_region_weight_after_pct")),
        "symbol_direct_pct": _number(candidate.get("hypothetical_symbol_weight_after_pct")),
    }
    return {
        "available": fit_available,
        "fit_score_observed": fit,
        "fit_source": candidate.get("portfolio_fit_source"),
        "formula_fallback_used": not fit_available,
        "exposure_before": before,
        "exposure_after": after,
        "hypothetical_purchase_weight_pct": _number(
            candidate.get("hypothetical_purchase_weight_pct")
        ),
        "hypothetical_units": _number(candidate.get("conditional_units")),
    }


def _options_snapshot(candidate):
    available = bool(candidate.get("options_data_available"))
    selected = bool(candidate.get("options_collection_selected"))
    context = candidate.get("options_context") or {}
    if not isinstance(context, dict):
        context = {}
    return {
        "collection_eligible": bool(candidate.get("options_collection_eligible")),
        "selection_rank": _number(candidate.get("options_collection_rank")),
        "selected_for_operational_fetch": selected,
        "data_available": available,
        "cohort": (
            "options_observed" if available
            else "selected_but_unavailable" if selected
            else "eligible_control_without_options"
            if candidate.get("options_collection_eligible")
            else "not_eligible"
        ),
        "formula_score": _number(candidate.get("options_score")),
        "observed_score": _number(candidate.get("options_score")) if available else None,
        "neutral_fallback_explicit": not available,
        "average_spread_pct": _number(context.get("average_spread_pct")),
        "quoted_contract_ratio": _number(context.get("quoted_contract_ratio")),
        "put_call_volume_ratio": _number(context.get("put_call_volume_ratio")),
        "put_call_open_interest_ratio": _number(context.get("put_call_open_interest_ratio")),
    }


def _benchmark_snapshot(candidate, state):
    rotation = state.get("us_sector_rotation") or {}
    snapshots = rotation.get("benchmark_snapshots") or {}
    sector_etf = candidate.get("sector_etf")
    result = {}
    for label, ticker in (
        ("spy", "SPY"), ("qqq", "QQQ"),
        ("sector", sector_etf), ("cash", "CASH_USD"),
    ):
        raw = snapshots.get(ticker) if ticker else None
        result[label] = dict(raw) if isinstance(raw, dict) else {
            "ticker": ticker, "available": False
        }
    return result


def _candidate_record(candidate, state, timestamp):
    options = _options_snapshot(candidate)
    portfolio = _portfolio_snapshot(candidate)
    components = {name: _number(candidate.get(name)) for name in COMPONENTS}
    return {
        "symbol": str(candidate.get("symbol") or "").upper(),
        "market": candidate.get("market"),
        "sector": candidate.get("sector"),
        "industry": candidate.get("industry"),
        "baseline_score": _number(candidate.get("technical_score")),
        "baseline_decision": candidate.get("decision"),
        "enhanced_decision_shadow": candidate.get("enhanced_decision"),
        "enhanced_decision_reason": candidate.get("enhanced_decision_reason"),
        "score_version": candidate.get("score_version"),
        "raw_score": _number(candidate.get("raw_stock_score")),
        "portfolio_fit_observed": portfolio["fit_score_observed"],
        "adjusted_score_formula": _number(candidate.get("portfolio_adjusted_score")),
        "adjusted_score_observed_fit": (
            _number(candidate.get("portfolio_adjusted_score"))
            if portfolio["available"] else None
        ),
        "components": components,
        "feature_availability": {
            "options": options["data_available"],
            "portfolio_fit": portfolio["available"],
            "bid_ask": _number(candidate.get("bid")) is not None
            and _number(candidate.get("ask")) is not None,
            "historical_volatility": _number(candidate.get("historical_vol")) is not None,
            "implied_volatility": _number(candidate.get("implied_volatility")) is not None,
            "average_volume": _number(candidate.get("avg_90d_usd_volume")) is not None,
        },
        "point_in_time_features": {
            key: candidate.get(key) for key in (
                "trend", "rsi", "relative_strength", "consensus", "analysts",
                "atr_eur", "rr_ratio", "earnings_risk", "historical_vol",
                "implied_volatility", "iv_percentile", "avg_90d_usd_volume",
                "quote_status", "spread_pct", "volatility_regime",
            )
        },
        "entry": _entry_snapshot(candidate),
        "portfolio": portfolio,
        "options": options,
        "benchmarks": _benchmark_snapshot(candidate, state),
        "costs": _cost_assumptions(candidate),
        "recorded_at": timestamp,
    }


def build_snapshot(candidates, state, recorded_at=None, run_mode=None):
    timestamp = _utc_timestamp(recorded_at)
    policy = load_policy()
    records = [
        _candidate_record(item, state or {}, timestamp)
        for item in candidates or []
        if isinstance(item, dict) and item.get("symbol")
    ]
    identity_material = json.dumps({
        "timestamp": timestamp,
        "mode": run_mode,
        "symbols": [item["symbol"] for item in records],
    }, sort_keys=True)
    return {
        "schema": SCHEMA,
        "snapshot_id": hashlib.sha256(identity_material.encode()).hexdigest()[:24],
        "recorded_at": timestamp,
        "run_mode": run_mode,
        "score_mode": "shadow",
        "authoritative_decision": "baseline",
        "policy_id": policy["policy_id"],
        "policy_hash": policy_hash(policy),
        "sample_partition": sample_partition(timestamp, policy),
        "market_regime": state.get("us_market_regime") or {},
        "candidate_count": len(records),
        "predictions": records,
    }


def append_snapshot(candidates, state, recorded_at=None, run_mode=None, path=LEDGER_PATH):
    snapshot = build_snapshot(candidates, state, recorded_at, run_mode)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(snapshot, separators=(",", ":"), ensure_ascii=False)
    with target.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.write(payload + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    return snapshot


def load_ledger(path=LEDGER_PATH):
    snapshots = []
    target = Path(path)
    if not target.exists():
        return snapshots
    for line_number, line in enumerate(target.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if payload.get("schema") != SCHEMA:
            raise ValueError(f"Unknown shadow schema at line {line_number}")
        snapshots.append(payload)
    return snapshots


def generate_readiness_report(path=REPORT_PATH, ledger_path=LEDGER_PATH):
    snapshots = load_ledger(ledger_path)
    predictions = [item for snap in snapshots for item in snap.get("predictions", [])]
    options = sum(bool(item.get("options", {}).get("data_available")) for item in predictions)
    fit = sum(bool(item.get("portfolio", {}).get("available")) for item in predictions)
    executable = sum(
        item.get("entry", {}).get("fresh_for_execution") is True
        for item in predictions
    )
    holdout = sum(snap.get("sample_partition") == "holdout_locked" for snap in snapshots)
    options_pct = options / len(predictions) * 100 if predictions else 0.0
    fit_pct = fit / len(predictions) * 100 if predictions else 0.0
    executable_pct = executable / len(predictions) * 100 if predictions else 0.0
    report = f"""# Enhanced shadow forward-validation readiness

Generated: {_utc_timestamp()}

## Coverage

- Snapshots: **{len(snapshots)}**
- Predictions: **{len(predictions)}**
- Execution-eligible predictions: **{executable}** ({executable_pct:.1f}%)
- Options observed: **{options}** ({options_pct:.1f}%)
- Portfolio Fit observed: **{fit}** ({fit_pct:.1f}%)
- Locked-holdout snapshots: **{holdout}**
- Matured 1D/5D/10D/20D/60D outcomes: **not evaluated in the collection job**

## Performance status

Baseline performance, Enhanced performance, benchmark alpha, gross/net return,
drawdown, volatility, Sharpe and Sortino remain **PENDING** until observations
mature. Entry prices and cost assumptions are frozen in the ledger at signal
time; later evaluation may add outcomes but may not alter these inputs.

## Preliminary verdict

**CONTINUE SHADOW**

The ledger is an evidence-collection mechanism. It cannot promote Enhanced and
the locked holdout cannot be used for calibration, thresholds, or weights.
"""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report, encoding="utf-8")
    return report
