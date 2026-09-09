"""Append-only ledger for Technical Events shadow observations."""

from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path


LEDGER_PATH = Path("technical_events_predictions.jsonl")
SCHEMA = "market-scanner.technical-events.v1"


def _number(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _hash(payload):
    clean = dict(payload)
    clean.pop("content_hash", None)
    clean.pop("snapshot_id", None)
    canonical = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _timestamp(value=None):
    value = value or dt.datetime.now(dt.timezone.utc)
    if not isinstance(value, dt.datetime):
        value = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt.timezone.utc)
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds")


def build_snapshot(rows, enhanced_by_symbol=None, *, run_mode=None, recorded_at=None,
                   state=None):
    timestamp = _timestamp(recorded_at)
    enhanced_by_symbol = enhanced_by_symbol or {}
    state = state or {}
    predictions = []
    seen = set()
    for row in rows or []:
        getter = row.get
        symbol = str(getter("Ticker", getter("Symbol", "")) or "").upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        events = getter("Technical_Events") or getter("technical_events")
        if not isinstance(events, dict):
            continue
        enhanced = enhanced_by_symbol.get(symbol, {})
        existing_technical_score = enhanced.get("technical_score")
        if existing_technical_score is None:
            existing_technical_score = getter("technical_score")
        if existing_technical_score is None:
            checks = _number(getter("Checks_Passed"))
            existing_technical_score = checks / 4 * 100 if checks is not None else None
        entry = enhanced.get("entry") if isinstance(enhanced.get("entry"), dict) else {}
        predictions.append({
            "ticker": symbol,
            "recorded_at": timestamp,
            "entry_price": _number(getter("Price_Native", getter("Current_Price", getter("Price")))),
            "entry_source": entry.get("source") or events.get("input_provenance", {}).get("source"),
            "data_as_of": events.get("data_as_of"),
            "market_timezone": entry.get("market_timezone") or getter("Market_Timezone") or "UTC",
            "market": enhanced.get("market") or getter("Market"),
            "sector": enhanced.get("sector") or getter("Sector"),
            "currency": entry.get("currency") or getter("Currency"),
            "existing_technical_score": _number(existing_technical_score),
            # Kept for compatibility with v1 consumers. This is the existing
            # four-rule Technical Score, not the Technical Events score.
            "baseline_score": _number(existing_technical_score),
            "baseline_decision": getter("Decision", getter("Sell_Decision")),
            "enhanced_raw_score": _number(enhanced.get("raw_stock_score")),
            "enhanced_adjusted_score": _number(enhanced.get("portfolio_adjusted_score")),
            "enhanced_decision": enhanced.get("enhanced_decision"),
            "technical_events_score": _number(events.get("overall_event_score")),
            "technical_events_direction": events.get("overall_direction"),
            "technical_events_confidence": _number(events.get("confidence")),
            "technical_events": events,
            "outcomes": {
                "status": "PENDING",
                "forward_returns": {f"{horizon}D": None for horizon in (1, 5, 10, 20, 60)},
                "mae": None,
                "mfe": None,
            },
        })
    snapshot = {
        "schema": SCHEMA,
        "snapshot_id": None,
        "previous_snapshot_hash": None,
        "recorded_at": timestamp,
        "run_mode": run_mode,
        "shadow_mode": True,
        "authoritative_decision_changed": False,
        "market_regime": state.get("us_market_regime") or {},
        "candidate_count": len(predictions),
        "predictions": predictions,
    }
    snapshot["input_data_provenance"] = {
        "captured_at": timestamp,
        "immutable_append_only": True,
        "market_regime_source": "dashboard_state.us_market_regime",
        "forward_outcomes_present": False,
    }
    snapshot["content_hash"] = _hash(snapshot)
    snapshot["snapshot_id"] = snapshot["content_hash"][:24]
    snapshot["content_hash"] = _hash(snapshot)
    return snapshot


def append_snapshot(rows, enhanced_by_symbol=None, *, run_mode=None,
                    recorded_at=None, state=None, path=LEDGER_PATH):
    snapshot = build_snapshot(
        rows, enhanced_by_symbol, run_mode=run_mode, recorded_at=recorded_at,
        state=state,
    )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.seek(0)
        lines = [line for line in handle.read().splitlines() if line.strip()]
        if lines:
            previous = json.loads(lines[-1])
            snapshot["previous_snapshot_hash"] = previous.get("content_hash")
        snapshot["content_hash"] = _hash(snapshot)
        snapshot["snapshot_id"] = snapshot["content_hash"][:24]
        snapshot["content_hash"] = _hash(snapshot)
        handle.seek(0, os.SEEK_END)
        handle.write(json.dumps(snapshot, separators=(",", ":"), ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    return snapshot


def load_ledger(path=LEDGER_PATH):
    target = Path(path)
    if not target.exists():
        return []
    rows = []
    known = set()
    for line_number, line in enumerate(target.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if payload.get("schema") != SCHEMA:
            raise ValueError(f"unknown Technical Events schema at line {line_number}")
        if payload.get("content_hash") != _hash(payload):
            raise ValueError(f"invalid Technical Events hash at line {line_number}")
        parent = payload.get("previous_snapshot_hash")
        # Concurrent first writers may legitimately create more than one
        # immutable root before Git reconciliation. Keep the ledger a forest;
        # every non-root parent must still be known and hash-valid.
        if parent is not None and parent not in known:
            raise ValueError(f"unknown Technical Events parent at line {line_number}")
        known.add(payload["content_hash"])
        rows.append(payload)
    return rows


def validate_ledger(snapshots):
    errors = []
    observations = set()
    for snapshot in snapshots:
        for row in snapshot.get("predictions", []):
            key = (snapshot.get("recorded_at"), row.get("ticker"))
            if key in observations:
                errors.append(f"duplicate ticker/timestamp: {key}")
            observations.add(key)
            if row.get("recorded_at") != snapshot.get("recorded_at"):
                errors.append(f"timestamp mismatch: {key}")
            events = row.get("technical_events") or {}
            if events.get("affects_baseline") is not False or events.get("affects_enhanced") is not False:
                errors.append(f"shadow isolation missing: {key}")
            outcomes = row.get("outcomes") or {}
            if outcomes.get("status") != "PENDING" or any(
                value is not None for value in (outcomes.get("forward_returns") or {}).values()
            ):
                errors.append(f"future outcome present at signal time: {key}")
    return errors
