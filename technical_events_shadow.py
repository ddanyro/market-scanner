"""Append-only ledger for Technical Events shadow observations."""

from __future__ import annotations

import datetime as dt
import fcntl
import gzip
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path


LEDGER_PATH = Path("technical_events_predictions.jsonl.gz")
SCHEMA = "market-scanner.technical-events.v1"
MAX_ACTIVE_LEDGER_BYTES = 40 * 1024 * 1024
TARGET_ARCHIVE_BYTES = 28 * 1024 * 1024


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


def _archive_prefix(target):
    name = target.name
    if name.endswith(".jsonl.gz"):
        name = name[:-len(".jsonl.gz")]
    else:
        name = target.stem
    return f"{name}.archive-"


def archive_paths(path=LEDGER_PATH):
    target = Path(path)
    return sorted(target.parent.glob(f"{_archive_prefix(target)}*.jsonl.gz"))


def _read_payloads(target):
    if not target.exists() or target.stat().st_size == 0:
        return []
    if target.suffix == ".gz":
        with gzip.open(target, "rt", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    else:
        lines = target.read_text(encoding="utf-8").splitlines()
    rows = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if payload.get("schema") != SCHEMA:
            raise ValueError(
                f"unknown Technical Events schema in {target}:{line_number}"
            )
        if payload.get("content_hash") != _hash(payload):
            raise ValueError(
                f"invalid Technical Events hash in {target}:{line_number}"
            )
        rows.append(payload)
    return rows


def rotate_ledger(path=LEDGER_PATH, *, max_bytes=MAX_ACTIVE_LEDGER_BYTES,
                  target_bytes=TARGET_ARCHIVE_BYTES):
    """Move a large active ledger into immutable gzip shards below Git limits."""
    target = Path(path)
    if not target.exists() or target.stat().st_size <= max_bytes:
        return []
    snapshots = _read_payloads(target)
    if not snapshots:
        return []
    chunks = []
    current = []
    current_size = 0
    for snapshot in snapshots:
        encoded = (
            json.dumps(snapshot, separators=(",", ":"), ensure_ascii=False)
            + "\n"
        ).encode("utf-8")
        member = gzip.compress(encoded)
        if current and current_size + len(member) > target_bytes:
            chunks.append(current)
            current = []
            current_size = 0
        current.append(member)
        current_size += len(member)
    if current:
        chunks.append(current)

    created = []
    stamp = str(snapshots[0].get("recorded_at") or "unknown")
    stamp = "".join(character for character in stamp if character.isalnum())[:14]
    for index, members in enumerate(chunks):
        first_id = str(snapshots[0].get("snapshot_id") or "unknown")[:12]
        if index:
            prior_count = sum(len(chunk) for chunk in chunks[:index])
            first_id = str(
                snapshots[prior_count].get("snapshot_id") or "unknown"
            )[:12]
        archive = target.parent / (
            f"{_archive_prefix(target)}{stamp}-p{index:03d}-{first_id}.jsonl.gz"
        )
        content = b"".join(members)
        if archive.exists() and archive.read_bytes() != content:
            raise ValueError(f"Technical Events archive collision: {archive}")
        if not archive.exists():
            descriptor, temporary = tempfile.mkstemp(
                prefix=f".{archive.name}.", suffix=".tmp", dir=archive.parent
            )
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
                Path(temporary).replace(archive)
            except Exception:
                Path(temporary).unlink(missing_ok=True)
                raise
        created.append(archive)

    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    os.close(descriptor)
    Path(temporary).replace(target)
    return created


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
            "history_ticker": str(
                getter("History_Ticker", symbol) or symbol
            ).upper(),
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
    cloud_previous = None
    if target == LEDGER_PATH:
        try:
            import shadow_parquet_store
            if shadow_parquet_store.is_configured():
                cloud_previous = shadow_parquet_store.latest_snapshot(
                    shadow_parquet_store.TECHNICAL_DATASET
                )
        except Exception as exc:
            required = os.environ.get("SHADOW_R2_REQUIRED", "").casefold() in {
                "1", "true", "yes", "on",
            }
            if required:
                raise
            print(f"[Shadow R2] Nu am putut citi ultimul Technical snapshot: {exc}")
    with target.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        existing = load_local_ledger(
            target, allow_external_root=target == LEDGER_PATH
        )
        previous_candidates = ([existing[-1]] if existing else [])
        if cloud_previous:
            previous_candidates.append(cloud_previous)
        if previous_candidates:
            previous = max(
                previous_candidates,
                key=lambda item: (item.get("recorded_at", ""), item.get("snapshot_id", "")),
            )
            snapshot["previous_snapshot_hash"] = previous.get("content_hash")
        snapshot["content_hash"] = _hash(snapshot)
        snapshot["snapshot_id"] = snapshot["content_hash"][:24]
        snapshot["content_hash"] = _hash(snapshot)
        handle.seek(0, os.SEEK_END)
        encoded = (
            json.dumps(snapshot, separators=(",", ":"), ensure_ascii=False) + "\n"
        ).encode("utf-8")
        if target.suffix == ".gz":
            # Concatenated gzip members remain a valid stream and let each
            # immutable snapshot be appended without rewriting older bytes.
            handle.write(gzip.compress(encoded))
        else:
            handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    rotate_ledger(target)
    if target == LEDGER_PATH:
        import shadow_parquet_store
        shadow_parquet_store.persist_optional(
            snapshot, shadow_parquet_store.TECHNICAL_DATASET
        )
    return snapshot


def load_local_ledger(
    path=LEDGER_PATH, *, archive_base=None, allow_external_root=False
):
    target = Path(path)
    parts = [*archive_paths(archive_base or target), target]
    if not any(part.exists() for part in parts):
        return []
    rows = []
    known = set()
    for part in parts:
        for payload in _read_payloads(part):
            parent = payload.get("previous_snapshot_hash")
            # Concurrent first writers may legitimately create more than one
            # immutable root before Git reconciliation. Every non-root parent
            # must still exist in an earlier archive or active-ledger row.
            if (
                parent is not None
                and parent not in known
                and not (allow_external_root and not known)
            ):
                raise ValueError(
                    f"unknown Technical Events parent while loading {part}"
                )
            known.add(payload["content_hash"])
            rows.append(payload)
    return rows


def load_ledger(path=LEDGER_PATH, *, archive_base=None):
    target = Path(path)
    # Fișierul canonic local este un segment append-only ancorat în ultimul
    # snapshot păstrat în R2. Arhivele/fișierele explicite rămân strict
    # self-contained și resping părinții necunoscuți.
    rows = load_local_ledger(
        target,
        archive_base=archive_base,
        allow_external_root=target == LEDGER_PATH and archive_base is None,
    )
    if target != LEDGER_PATH or archive_base is not None:
        return rows
    try:
        import shadow_parquet_store
        cloud = shadow_parquet_store.load_snapshots(
            shadow_parquet_store.TECHNICAL_DATASET
        )
    except Exception as exc:
        required = os.environ.get("SHADOW_R2_REQUIRED", "").casefold() in {
            "1", "true", "yes", "on",
        }
        if required:
            raise
        print(f"[Shadow R2] Citirea Technical Events a eșuat; folosesc local: {exc}")
        cloud = []
    merged = {
        item.get("snapshot_id") or item.get("content_hash"): item
        for item in [*rows, *cloud]
    }
    return sorted(
        merged.values(),
        key=lambda item: (item.get("recorded_at", ""), item.get("snapshot_id", "")),
    )


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
