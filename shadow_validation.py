"""Append-only, point-in-time ledger for Enhanced Scoring validation.

This module records evidence; it never changes scoring weights or the
authoritative BUY/WAIT/AVOID decision.  Feature availability is first-class so
that a neutral formula fallback cannot be mistaken for observed IBKR data.
"""

from __future__ import annotations

import datetime as dt
import ast
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
SCHEMA = "market-scanner.shadow-prediction.v3"
HASHED_SCHEMAS = {"market-scanner.shadow-prediction.v2", SCHEMA}
LEGACY_SCHEMAS = {"market-scanner.shadow-prediction.v1"}
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


def _source_hash(path, function_name=None):
    source = Path(path).read_text(encoding="utf-8")
    segment = source
    if function_name:
        tree = ast.parse(source)
        node = next(
            item for item in tree.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            and item.name == function_name
        )
        segment = "".join(
            source.splitlines(keepends=True)[node.lineno - 1:node.end_lineno]
        )
    return hashlib.sha256(segment.encode("utf-8")).hexdigest()


def validate_frozen_model(policy=None):
    """Fail closed if the registered scoring implementation has drifted."""
    policy = policy or load_policy()
    freeze = policy.get("model_freeze") or {}
    base = Path(__file__).resolve().parent
    actual = {
        "enhanced_scoring_source_sha256": _source_hash(base / "enhanced_scoring.py"),
        "portfolio_fit_source_sha256": _source_hash(
            base / "market_scanner_analysis.py", "_portfolio_fit_from_weights"
        ),
    }
    import enhanced_scoring
    actual.update({
        "raw_score_weights": enhanced_scoring.RAW_SCORE_WEIGHTS,
        "portfolio_raw_weight": enhanced_scoring.PORTFOLIO_RAW_WEIGHT,
        "portfolio_fit_weight": enhanced_scoring.PORTFOLIO_FIT_WEIGHT,
    })
    errors = [
        f"frozen model drift: {key} expected={freeze.get(key)} actual={value}"
        for key, value in actual.items()
        if freeze.get(key) != value
    ]
    if errors:
        raise ValueError("; ".join(errors))
    return policy_hash(freeze)


def is_official_shadow(timestamp, policy=None):
    policy = policy or load_policy()
    start = _utc_timestamp(policy["official_shadow_start"])
    return _utc_timestamp(timestamp) >= start


def _content_hash(payload):
    canonical = dict(payload)
    canonical.pop("content_hash", None)
    canonical.pop("snapshot_id", None)
    encoded = json.dumps(
        canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _market_timezone(candidate):
    explicit = candidate.get("market_timezone")
    if explicit:
        return str(explicit)
    market = str(candidate.get("market") or "").casefold()
    symbol = str(candidate.get("symbol") or "").upper()
    if market == "sua":
        return "America/New_York"
    if "rom" in market or symbol.endswith(".RO"):
        return "Europe/Bucharest"
    return "Europe/Paris" if symbol.endswith(".PA") else "UTC"


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
        "market_timezone": _market_timezone(candidate),
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
        "formula_fallback_used": False,
        "adjustment_applied": bool(
            candidate.get("portfolio_adjustment_applied") and fit_available
        ),
        "exposure_before": before,
        "exposure_after": after,
        "hypothetical_purchase_weight_pct": _number(
            candidate.get("hypothetical_purchase_weight_pct")
        ),
        "marginal_exposure_pct": _number(candidate.get("marginal_exposure_pct")),
        "hypothetical_units": _number(candidate.get("conditional_units")),
        "fit_score_posttrade_observed": _number(
            candidate.get("portfolio_fit_posttrade_observed_score")
        ),
    }


def _options_snapshot(candidate):
    available = bool(candidate.get("options_data_available"))
    partial = bool(candidate.get("options_data_partial"))
    selected = bool(candidate.get("options_collection_selected"))
    context = candidate.get("options_context") or {}
    if not isinstance(context, dict):
        context = {}
    contracts = [
        row for row in (context.get("contracts") or [])
        if isinstance(row, dict)
    ]
    option_volume = sum(
        _number(row.get("volume"), 0) or 0 for row in contracts
    ) if contracts else None
    open_interest = sum(
        _number(row.get("open_interest"), 0) or 0 for row in contracts
    ) if contracts else None
    return {
        "collection_eligible": bool(candidate.get("options_collection_eligible")),
        "selection_rank": _number(candidate.get("options_collection_rank")),
        "selected_for_operational_fetch": selected,
        "data_available": available,
        "data_partial": partial,
        "cohort": candidate.get("options_cohort") or (
            "OPTIONS_AVAILABLE" if available else "OPTIONS_DATA_PARTIAL"
            if partial else "OPTIONS_UNAVAILABLE" if candidate.get(
                "options_collection_eligible"
            ) else "OPTIONS_NOT_ELIGIBLE"
        ),
        "eligibility_reason": candidate.get("options_eligibility_reason"),
        "formula_score": _number(candidate.get("options_score")),
        "observed_score": _number(candidate.get("options_score")) if available else None,
        "neutral_fallback_explicit": not available,
        "average_spread_pct": _number(context.get("average_spread_pct")),
        "quoted_contract_ratio": _number(context.get("quoted_contract_ratio")),
        "put_call_volume_ratio": _number(context.get("put_call_volume_ratio")),
        "put_call_open_interest_ratio": _number(context.get("put_call_open_interest_ratio")),
        "data_quality": context.get("data_quality", "unavailable"),
        "analytics_available": bool(context.get("analytics_available")),
        "quote_coverage_ratio": _number(context.get("quote_coverage_ratio")),
        "volume_coverage_ratio": _number(context.get("volume_coverage_ratio")),
        "open_interest_coverage_ratio": _number(
            context.get("open_interest_coverage_ratio")
        ),
        "contract_iv_coverage_ratio": _number(
            context.get("contract_iv_coverage_ratio")
        ),
        "fetched_at": context.get("fetched_at"),
        "expiration": context.get("expiration"),
        "expirations": context.get("expirations") or [],
        "implied_volatility": _number(candidate.get("implied_volatility")),
        "iv_percentile": _number(candidate.get("iv_percentile")),
        "option_volume": option_volume,
        "open_interest": open_interest,
        "sampled_bid_ask": [
            {
                "side": row.get("side"),
                "strike": _number(row.get("strike")),
                "bid": _number(row.get("bid")),
                "ask": _number(row.get("ask")),
            }
            for row in contracts
        ],
        "raw_context": context,
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
    observed_components = dict(components)
    if not options["data_available"]:
        observed_components["options_score"] = None
    component_provenance = {
        "technical_score": {
            "source": "baseline_four_rule_engine",
            "raw_fields": ["checks_passed", "trend"],
        },
        "momentum_score": {
            "source": candidate.get("market_data_source") or "scanner_price_history",
            "raw_fields": ["rsi", "relative_strength"],
        },
        "research_score": {
            "source": candidate.get("research_source") or "scanner_research_inputs",
            "raw_fields": ["consensus", "analysts", "earnings_risk"],
        },
        "volatility_score": {
            "source": candidate.get("market_data_source") or "scanner_price_history",
            "raw_fields": ["atr_eur", "historical_vol", "implied_volatility", "iv_percentile"],
        },
        "liquidity_score": {
            "source": candidate.get("market_data_source") or "scanner_market_data",
            "raw_fields": ["avg_90d_usd_volume", "relative_volume_20d", "spread_pct"],
        },
        "options_score": {
            "source": (context.get("source") if isinstance((context := candidate.get("options_context") or {}), dict) else None),
            "status": options["cohort"],
            "available": options["data_available"],
            "raw_fields": ["average_spread_pct", "put_call_volume_ratio", "put_call_open_interest_ratio", "quoted_contract_ratio"],
        },
        "relative_opportunity_score": {
            "source": "company_context",
            "raw_fields": ["relative_performance_percentile"],
        },
        "risk_reward_score": {
            "source": "scanner_technical_levels",
            "raw_fields": ["rr_ratio"],
        },
    }
    return {
        "symbol": str(candidate.get("symbol") or "").upper(),
        "market": candidate.get("market"),
        "sector": candidate.get("sector"),
        "industry": candidate.get("industry"),
        "instrument_metadata": {
            "country": candidate.get("country"),
            "exchange": candidate.get("exchange"),
            "security_type": candidate.get("security_type"),
            "currency": candidate.get("execution_currency") or candidate.get("currency"),
            "contract_id": candidate.get("contract_id"),
            "source": candidate.get("market_metadata_source"),
        },
        "baseline_score": _number(candidate.get("technical_score")),
        "baseline_decision": candidate.get("decision"),
        "enhanced_decision_shadow": candidate.get("enhanced_decision"),
        "enhanced_decision_reason": candidate.get("enhanced_decision_reason"),
        "score_version": candidate.get("score_version"),
        "raw_score": _number(candidate.get("raw_stock_score")),
        "raw_score_availability_adjusted": _number(
            candidate.get("raw_stock_score_availability_adjusted")
        ),
        "portfolio_fit_observed": portfolio["fit_score_observed"],
        "adjusted_score_formula": _number(candidate.get("portfolio_adjusted_score")),
        "portfolio_adjustment_applied": portfolio["adjustment_applied"],
        "adjusted_score_observed_fit": (
            _number(candidate.get("portfolio_adjusted_score"))
            if portfolio["available"] else None
        ),
        "adjusted_score_posttrade_fit": _number(
            candidate.get("portfolio_adjusted_posttrade_score")
        ),
        "adjusted_score_availability_posttrade": _number(
            candidate.get("portfolio_adjusted_availability_score")
        ),
        "components": components,
        "observed_components": observed_components,
        "component_provenance": component_provenance,
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
                "checks_passed", "atr_eur", "rr_ratio", "earnings_risk",
                "relative_volume_20d", "historical_vol",
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
    freeze_hash = validate_frozen_model(policy)
    records = [
        _candidate_record(item, state or {}, timestamp)
        for item in candidates or []
        if isinstance(item, dict) and item.get("symbol")
    ]
    snapshot = {
        "schema": SCHEMA,
        "snapshot_id": None,
        "previous_snapshot_hash": None,
        "recorded_at": timestamp,
        "run_mode": run_mode,
        "score_mode": "shadow",
        "authoritative_decision": "baseline",
        "policy_id": policy["policy_id"],
        "policy_hash": policy_hash(policy),
        "model_freeze_hash": freeze_hash,
        "validation_phase": (
            "official_shadow" if is_official_shadow(timestamp, policy)
            else "pre_official"
        ),
        "sample_partition": sample_partition(timestamp, policy),
        "market_regime": state.get("us_market_regime") or {},
        "candidate_count": len(records),
        "predictions": records,
    }
    snapshot["input_data_provenance"] = {
        "captured_at": timestamp,
        "immutable_append_only": True,
        "market_regime_source": "dashboard_state.us_market_regime",
        "candidate_sources_embedded_per_prediction": True,
        "forward_outcomes_present": False,
    }
    snapshot["content_hash"] = _content_hash(snapshot)
    snapshot["snapshot_id"] = snapshot["content_hash"][:24]
    snapshot["content_hash"] = _content_hash(snapshot)
    return snapshot


def append_snapshot(candidates, state, recorded_at=None, run_mode=None, path=LEDGER_PATH):
    snapshot = build_snapshot(candidates, state, recorded_at, run_mode)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(snapshot, separators=(",", ":"), ensure_ascii=False)
    with target.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.seek(0)
        existing_lines = [line for line in handle.read().splitlines() if line.strip()]
        if existing_lines:
            previous = json.loads(existing_lines[-1])
            snapshot["previous_snapshot_hash"] = (
                previous.get("content_hash") or _content_hash(previous)
            )
        snapshot["content_hash"] = _content_hash(snapshot)
        snapshot["snapshot_id"] = snapshot["content_hash"][:24]
        snapshot["content_hash"] = _content_hash(snapshot)
        payload = json.dumps(snapshot, separators=(",", ":"), ensure_ascii=False)
        handle.seek(0, os.SEEK_END)
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
    seen_hashes = set()
    for line_number, line in enumerate(target.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        payload = json.loads(line)
        schema = payload.get("schema")
        if schema not in LEGACY_SCHEMAS | HASHED_SCHEMAS:
            raise ValueError(f"Unknown shadow schema at line {line_number}")
        if schema in HASHED_SCHEMAS:
            if payload.get("content_hash") != _content_hash(payload):
                raise ValueError(f"Invalid snapshot hash at line {line_number}")
            if payload.get("snapshot_id") != payload["content_hash"][:24]:
                raise ValueError(f"Invalid snapshot id at line {line_number}")
            parent_hash = payload.get("previous_snapshot_hash")
            if seen_hashes and parent_hash not in seen_hashes:
                raise ValueError(f"Unknown snapshot parent at line {line_number}")
            if not seen_hashes and parent_hash is not None:
                raise ValueError(f"Broken snapshot root at line {line_number}")
        snapshots.append(payload)
        seen_hashes.add(payload.get("content_hash") or _content_hash(payload))
    return snapshots


def validate_ledger(snapshots):
    """Return deterministic integrity errors without mutating the ledger."""
    errors = []
    snapshot_ids = set()
    observations = set()
    score_fields = (
        "baseline_score", "raw_score", "raw_score_availability_adjusted",
        "portfolio_fit_observed", "adjusted_score_formula",
        "adjusted_score_observed_fit", "adjusted_score_posttrade_fit",
    )
    forbidden = ("forward", "outcome", "mae", "mfe", "future_return")
    policy = load_policy()
    frozen_hash = policy_hash(policy.get("model_freeze") or {})
    for snapshot in snapshots:
        snapshot_id = snapshot.get("snapshot_id")
        if snapshot_id in snapshot_ids:
            errors.append(f"duplicate snapshot_id: {snapshot_id}")
        snapshot_ids.add(snapshot_id)
        timestamp = snapshot.get("recorded_at")
        official = is_official_shadow(timestamp, policy)
        if official and snapshot.get("schema") != SCHEMA:
            errors.append(f"unregistered schema after official activation: {snapshot_id}")
        if official and snapshot.get("schema") == SCHEMA:
            if snapshot.get("validation_phase") != "official_shadow":
                errors.append(f"official snapshot has wrong phase: {snapshot_id}")
            if snapshot.get("model_freeze_hash") != frozen_hash:
                errors.append(f"official snapshot model freeze mismatch: {snapshot_id}")
            provenance = snapshot.get("input_data_provenance") or {}
            if provenance.get("forward_outcomes_present") is not False:
                errors.append(f"official snapshot provenance invalid: {snapshot_id}")
        for prediction in snapshot.get("predictions", []):
            symbol = prediction.get("symbol")
            key = (timestamp, symbol)
            if key in observations:
                errors.append(f"duplicate ticker/timestamp: {symbol} {timestamp}")
            observations.add(key)
            if prediction.get("recorded_at") != timestamp:
                errors.append(f"timestamp mismatch: {symbol} {timestamp}")
            for field in score_fields:
                value = _number(prediction.get(field))
                if value is not None and not 0 <= value <= 100:
                    errors.append(f"impossible {field}: {symbol}={value}")
            for field in prediction:
                if any(token in field.casefold() for token in forbidden):
                    errors.append(f"future field in snapshot: {symbol}.{field}")
            options = prediction.get("options") or {}
            if not options.get("data_available") and options.get("observed_score") is not None:
                errors.append(f"unavailable options has observed score: {symbol}")
            if official and snapshot.get("schema") == SCHEMA:
                observed = prediction.get("observed_components") or {}
                if not options.get("data_available") and observed.get("options_score") is not None:
                    errors.append(f"missing options treated as observed component: {symbol}")
                portfolio = prediction.get("portfolio") or {}
                if not portfolio.get("available"):
                    raw = _number(prediction.get("raw_score"))
                    adjusted = _number(prediction.get("adjusted_score_formula"))
                    if raw is not None and adjusted != raw:
                        errors.append(f"missing fit changed adjusted score: {symbol}")
                if set(prediction.get("component_provenance") or {}) != set(COMPONENTS):
                    errors.append(f"incomplete component provenance: {symbol}")
    return errors


def generate_readiness_report(path=REPORT_PATH, ledger_path=LEDGER_PATH):
    snapshots = load_ledger(ledger_path)
    integrity_errors = validate_ledger(snapshots)
    policy = load_policy()
    official_snapshots = [
        snap for snap in snapshots
        if is_official_shadow(snap.get("recorded_at"), policy)
        and snap.get("validation_phase") == "official_shadow"
    ]
    predictions = [
        item for snap in official_snapshots for item in snap.get("predictions", [])
    ]
    options = sum(bool(item.get("options", {}).get("data_available")) for item in predictions)
    fit = sum(bool(item.get("portfolio", {}).get("available")) for item in predictions)
    executable = sum(
        item.get("entry", {}).get("fresh_for_execution") is True
        for item in predictions
    )
    holdout = sum(
        snap.get("sample_partition") == "holdout_locked"
        for snap in official_snapshots
    )
    options_pct = options / len(predictions) * 100 if predictions else 0.0
    options_quality = {}
    for item in predictions:
        quality = str(item.get("options", {}).get("data_quality") or "legacy_unknown")
        options_quality[quality] = options_quality.get(quality, 0) + 1
    fit_pct = fit / len(predictions) * 100 if predictions else 0.0
    executable_pct = executable / len(predictions) * 100 if predictions else 0.0
    report = f"""# Enhanced shadow forward-validation readiness

Generated: {_utc_timestamp()}

- Official activation: **{policy['official_shadow_start']}**
- Frozen model hash: **{policy_hash(policy.get('model_freeze') or {})}**

## Coverage

- Official snapshots: **{len(official_snapshots)}**
- Pre-official/legacy snapshots excluded: **{len(snapshots) - len(official_snapshots)}**
- Predictions: **{len(predictions)}**
- Execution-eligible predictions: **{executable}** ({executable_pct:.1f}%)
- Options observed: **{options}** ({options_pct:.1f}%)
- Options quality: **{json.dumps(options_quality, sort_keys=True)}**
- Portfolio Fit observed: **{fit}** ({fit_pct:.1f}%)
- Locked-holdout snapshots: **{holdout}**
- Integrity errors: **{len(integrity_errors)}**
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
    coverage_path = target.parent / "collection_coverage.json"
    coverage_path.write_text(json.dumps({
        "generated_at": _utc_timestamp(),
        "ledger_path": str(ledger_path),
        "last_snapshot_id": (
            official_snapshots[-1].get("snapshot_id") if official_snapshots else None
        ),
        "snapshots": len(official_snapshots),
        "pre_official_snapshots_excluded": len(snapshots) - len(official_snapshots),
        "predictions": len(predictions),
        "execution_eligible": executable,
        "options_observed": options,
        "options_quality": options_quality,
        "portfolio_fit_observed": fit,
        "locked_holdout_snapshots": holdout,
        "performance_outcomes_evaluated": False,
        "integrity_errors": integrity_errors,
    }, indent=2), encoding="utf-8")
    return report
