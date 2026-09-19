#!/usr/bin/env python3
"""Local, read-only bridge between the authenticated Tradeville tab and scanner.

The Chrome extension owns the authenticated WebSocket.  This process only
accepts one short-lived snapshot over loopback, validates it, and atomically
updates the scanner's existing Tradeville inputs.  A failed sync never replaces
the last known-good portfolio or orders with empty files.
"""

from __future__ import annotations

import argparse
import copy
import hmac
import json
import math
import os
import secrets
import tempfile
import threading
import time
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd

import market_security


SCHEMA = "market-scanner.tradeville.websocket.v2"
BRIDGE_HEADER = "market-scanner-tradeville-v1"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 43129
MAX_BODY_BYTES = 32 * 1024 * 1024
PORTFOLIO_PATH = Path("tradeville_portfolio.csv")
ORDERS_PATH = Path("tradeville_orders.csv")
ACCOUNT_ENCRYPTED_PATH = Path("tradeville_account.enc.json")
RAW_ENCRYPTED_PATH = Path("tradeville_ws_snapshot.enc.json")
STATUS_PATH = Path("tradeville_sync_status.json")
IBKR_ACCOUNT_PATH = Path("tws_account.json")
DEFAULT_HISTORY_START = date(2025, 9, 16)

PORTFOLIO_COLUMNS = [
    "Symbol", "Shares", "Buy_Price", "Current_Price", "Current_Value",
    "Investment", "Profit", "Profit_Pct", "Currency", "Trail_Pct",
    "Trail_Stop", "Target", "Description", "Entry_Date", "Broker",
    "Account", "Account_ID", "Raw_Symbol", "Market", "Exchange",
    "Snapshot_Timestamp", "Source",
]
ORDER_COLUMNS = [
    "Symbol", "OrderType", "Action", "Total_Qty", "Aux_Price",
    "Limit_Price", "Stop_Price", "Trail_Pct", "Calculated_Stop",
    "Currency", "Order_Source", "Account", "Account_ID", "Order_ID",
    "Status", "Valid_Until", "Executed_Qty", "Raw_Symbol", "Market",
    "Snapshot_Timestamp",
]


class SnapshotError(ValueError):
    """Snapshot failed structural or integrity validation."""


def _text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"", "nan", "none", "null"} else text


def _number(value: Any, default: float | None = None) -> float | None:
    if value is None or isinstance(value, bool):
        return default
    try:
        if isinstance(value, str):
            value = value.strip().replace(" ", "").replace(",", ".")
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _first_number(row: dict[str, Any], *keys: str) -> float | None:
    lowered = {str(key).lower(): value for key, value in row.items()}
    for key in keys:
        number = _number(lowered.get(key.lower()))
        if number is not None:
            return number
    return None


def _first_text(row: dict[str, Any], *keys: str) -> str:
    lowered = {str(key).lower(): value for key, value in row.items()}
    for key in keys:
        value = _text(lowered.get(key.lower()))
        if value:
            return value
    return ""


def _is_cash_row(row: dict[str, Any]) -> bool:
    symbol = _first_text(row, "simbol", "symbol").upper()
    kind = _first_text(row, "tsim", "tip", "type", "ba").lower()
    return symbol in {"RON", "EUR", "USD", "GBP", "CHF"} or kind in {
        "bani", "cash", "money",
    }


def _canonical_symbol(raw_symbol: str, market: str, exchange: str) -> str:
    symbol = _text(raw_symbol).upper()
    if not symbol:
        return ""
    venue = f"{market} {exchange}".upper()
    if "." not in symbol and any(token in venue for token in ("BVB", "BUCHAREST")):
        return f"{symbol}.RO"
    return symbol


def _action(value: Any) -> str:
    text = _text(value).upper()
    if text in {"C", "CUMP", "CUMPARARE", "BUY", "B"}:
        return "BUY"
    if text in {"V", "VANZ", "VANZARE", "SELL", "S"}:
        return "SELL"
    return text


def _status_payload(ok: bool, **extra: Any) -> dict[str, Any]:
    return {
        "schema": "market-scanner.tradeville.sync-status.v1",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "ok": bool(ok),
        **extra,
    }


def _atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=str(path.parent or Path(".")), text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _atomic_json(path: Path, payload: Any) -> None:
    _atomic_text(path, json.dumps(payload, ensure_ascii=False, indent=2))


def _atomic_csv(path: Path, frame: pd.DataFrame) -> None:
    _atomic_text(path, frame.to_csv(index=False))


def _existing_overlays(path: Path = PORTFOLIO_PATH) -> dict[tuple[str, str], dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        frame = pd.read_csv(path)
    except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError):
        return {}
    overlays: dict[tuple[str, str], dict[str, Any]] = {}
    for _, row in frame.iterrows():
        symbol = _text(row.get("Symbol")).upper()
        account = _text(row.get("Account"))
        if not symbol:
            continue
        values = {
            key: row.get(key) for key in (
                "Trail_Pct", "Trail_Stop", "Target", "Description", "Entry_Date"
            ) if key in frame.columns and not pd.isna(row.get(key))
        }
        overlays[(account, symbol)] = values
        overlays.setdefault(("", symbol), values)
    return overlays


def validate_snapshot(snapshot: Any, expected_accounts: int = 2) -> dict[str, Any]:
    if not isinstance(snapshot, dict) or snapshot.get("schema") != SCHEMA:
        raise SnapshotError(
            "versiune Tradeville bridge veche; apasă Reload în "
            "chrome://extensions și reîncarcă fila Tradeville"
        )
    if snapshot.get("bridge_version") != 2:
        raise SnapshotError(
            "extensia Tradeville nu include protocolul de istoric v2; "
            "apasă Reload în chrome://extensions"
        )
    fetched_at = _text(snapshot.get("fetched_at"))
    try:
        parsed = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SnapshotError("timestamp Tradeville invalid") from exc
    if parsed.tzinfo is None:
        raise SnapshotError("timestamp Tradeville fără fus orar")
    age = (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds()
    if age < -120 or age > 300:
        raise SnapshotError("snapshot Tradeville nu este contemporan")

    accounts = snapshot.get("accounts")
    if not isinstance(accounts, list) or len(accounts) < expected_accounts:
        raise SnapshotError(
            f"snapshot incomplet: {len(accounts) if isinstance(accounts, list) else 0}/"
            f"{expected_accounts} conturi"
        )
    seen: set[str] = set()
    for account in accounts:
        if not isinstance(account, dict):
            raise SnapshotError("cont Tradeville invalid")
        person = account.get("person")
        if not isinstance(person, dict):
            raise SnapshotError("identitatea contului Tradeville lipsește")
        person_id = _text(person.get("id"))
        name = _text(person.get("name"))
        if not person_id or not name or person_id in seen:
            raise SnapshotError("cont Tradeville lipsă sau duplicat")
        seen.add(person_id)
        for key in ("portfolio", "orders", "account_info", "settlement"):
            if not isinstance(account.get(key), list):
                raise SnapshotError(f"{key} nu este un snapshot complet")
        if not isinstance(account.get("portfolio_graph"), list):
            raise SnapshotError(
                "portfolio_graph lipsește; extensia Chrome trebuie reîncărcată"
            )
        if not isinstance(account.get("portfolio_graph_request"), dict):
            raise SnapshotError(
                "proveniența portfolio_graph lipsește; extensia Chrome "
                "trebuie reîncărcată"
            )
    return snapshot


def _decode_parallel_rows(value: Any) -> list[dict[str, Any]]:
    """Decode the column-oriented tables used by Tradeville's pf4 protocol."""
    if not value:
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if not isinstance(value, dict):
        return []
    lengths = [len(item) if isinstance(item, list) else 1 for item in value.values()]
    length = max(lengths, default=0)
    return [{
        key: item[index] if isinstance(item, list) and index < len(item) else (
            None if isinstance(item, list) else item
        )
        for key, item in value.items()
    } for index in range(length)]


def _history_start(path: Path = IBKR_ACCOUNT_PATH) -> date:
    """Use the first actual IBKR NAV observation as the common start date."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return DEFAULT_HISTORY_START
    dates: list[date] = []
    for point in payload.get("nav_history", []):
        raw = _text(point.get("date")) if isinstance(point, dict) else ""
        raw = raw.strip("'\"")[:10]
        try:
            parsed = (
                datetime.strptime(raw[:8], "%Y%m%d").date()
                if "-" not in raw else date.fromisoformat(raw)
            )
        except ValueError:
            continue
        dates.append(parsed)
    return min(dates) if dates else DEFAULT_HISTORY_START


def _eur_rate(snapshot: dict[str, Any]) -> float | None:
    for row in snapshot.get("exchange_rates", []):
        if (
            isinstance(row, dict)
            and _first_text(row, "valuta", "currency").upper() == "EUR"
        ):
            rate = _first_number(row, "curs", "rate")
            if rate and rate > 0:
                return rate
    return None


def _tradeville_graph_points(raw_graph: Any) -> tuple[list[dict[str, Any]], bool]:
    """Rebuild the non-intraday series using Tradeville PortfolioPage.Ir rules."""
    if not isinstance(raw_graph, list) or not raw_graph:
        return [], False
    if (
        isinstance(raw_graph[0], dict)
        and {"data", "eval"} <= set(raw_graph[0])
    ):
        return [dict(item) for item in raw_graph if isinstance(item, dict)], False
    if len(raw_graph) < 4:
        return [], False

    holdings: dict[str, dict[str, Any]] = {}
    rates: dict[str, float] = {}
    for row in _decode_parallel_rows(raw_graph[3]):
        symbol = _text(row.get("simbol")).strip()
        account = _text(row.get("cont"))
        if not symbol and not account:
            continue
        key = symbol or f"${account}"
        if symbol and key in holdings:
            holdings[key]["sold"] += _number(row.get("sold"), 0.0) or 0.0
        else:
            holdings[key] = dict(row)
            holdings[key]["pret"] = (
                _number(row.get("pret"), 0.0) if symbol else 1.0
            )
            holdings[key]["sold"] = _number(row.get("sold"), 0.0) or 0.0

    events: list[dict[str, Any]] = []
    for table_index in (2, 1, 0):
        events.extend(_decode_parallel_rows(raw_graph[table_index]))
    events.sort(key=lambda row: _number(row.get("mnt"), 0.0) or 0.0)

    points: list[dict[str, Any]] = []
    epoch = datetime(2000, 1, 1, tzinfo=timezone.utc)
    index = 0
    while index < len(events):
        minute = _number(events[index].get("mnt"), 0.0) or 0.0
        end = index + 1
        if minute:
            while end < len(events):
                candidate = _number(events[end].get("mnt"), 0.0) or 0.0
                if candidate >= minute + 5:
                    break
                end += 1
        group = events[index:end]
        contribution = 0.0
        turnover = 0.0

        # The portal applies all currency events before holdings/cash events
        # within the same five-minute bucket.
        for event in group:
            if "curs" in event and "valuta" in event:
                account = _text(event.get("cont"))
                rate = _number(event.get("curs"))
                if account and rate is not None:
                    rates[account] = rate
                    for holding in holdings.values():
                        if _text(holding.get("cont")) == account:
                            holding["curs"] = rate

        for event in group:
            if "curs" in event and "valuta" in event:
                continue
            account = _text(event.get("cont"))
            quantity = _number(event.get("cant"), 0.0) or 0.0
            amount = _number(event.get("suma"), 0.0) or 0.0
            symbol = _text(event.get("simbol")).strip()
            price = _number(event.get("pret"))
            if account and (quantity or amount):
                if symbol:
                    holding = holdings.setdefault(symbol, {
                        "cont": account,
                        "simbol": symbol,
                        "sold": 0.0,
                        "pret": price or 0.0,
                        "curs": rates.get(account, 1.0),
                    })
                    if account in rates:
                        holding["curs"] = rates[account]
                    holding["sold"] = (
                        _number(holding.get("sold"), 0.0) or 0.0
                    ) + quantity
                    if price is not None:
                        holding["pret"] = price
                    if not holding["sold"]:
                        holdings.pop(symbol, None)
                cash_key = f"${account}"
                cash = holdings.setdefault(cash_key, {
                    "sold": 0.0,
                    "pret": 1.0,
                    "cont": account,
                    "curs": rates.get(account, 1.0),
                })
                if account in rates:
                    cash["curs"] = rates[account]
                rate = _number(cash.get("curs"), 1.0) or 1.0
                if event.get("aport") is not None:
                    contribution += (
                        _number(event.get("aport"), 0.0) or 0.0
                    ) * rate
                if (
                    (event.get("aport") is None or not _number(event.get("aport"), 0.0))
                    and amount
                ):
                    turnover += abs(amount * rate)
                cash["sold"] = (
                    _number(cash.get("sold"), 0.0) or 0.0
                ) + amount
            elif symbol and symbol in holdings and price is not None:
                holdings[symbol]["pret"] = price

        for holding in holdings.values():
            account = _text(holding.get("cont"))
            holding["curs"] = rates.get(
                account, _number(holding.get("curs"), 1.0) or 1.0
            )
        nav_ron = sum(
            (_number(item.get("sold"), 0.0) or 0.0)
            * (_number(item.get("pret"), 0.0) or 0.0)
            * (_number(item.get("curs"), 1.0) or 1.0)
            for item in holdings.values()
        )
        cash_ron = sum(
            (_number(item.get("sold"), 0.0) or 0.0)
            * (_number(item.get("curs"), 1.0) or 1.0)
            for key, item in holdings.items() if key.startswith("$")
        )
        event_minute = _number(group[-1].get("mnt"), 0.0) or 0.0
        point_date = (epoch + timedelta(minutes=event_minute)).date().isoformat()
        points.append({
            "data": point_date,
            "eval": nav_ron,
            "cash": cash_ron,
            "aport": contribution,
            "rulaj": turnover,
        })
        index = end
    return points, True


def _account_history(
    account: dict[str, Any],
    snapshot: dict[str, Any],
    start: date | None = None,
) -> dict[str, Any]:
    start = start or _history_start()
    points, reconstructed = _tradeville_graph_points(
        account.get("portfolio_graph")
    )
    graph_request = account.get("portfolio_graph_request") or {}
    fallback_last_good = bool(graph_request.get("fallback_last_good"))
    eur_rate = _eur_rate(snapshot)
    if not points or not eur_rate:
        return {
            "nav_history": [],
            "adjusted_nav_history": [],
            "cash_history": [],
            "profit_history": [],
            "history_metadata": {
                "available": False,
                "stale": fallback_last_good,
                "start_requested": start.isoformat(),
                "source": "Tradeville WebSocket pf4 / graf_pers_brut",
                "reason": "graph_or_eur_rate_missing",
            },
        }

    normalized = []
    for item in points:
        raw_value = item.get("data")
        try:
            if isinstance(raw_value, (int, float)):
                point_date = datetime.fromtimestamp(
                    raw_value, tz=timezone.utc
                ).date()
            else:
                point_date = date.fromisoformat(_text(raw_value)[:10])
        except (ValueError, TypeError, OSError):
            continue
        if point_date >= start:
            normalized.append({**item, "data": point_date.isoformat()})
    # One immutable end-of-day observation per date.
    by_date = {item["data"]: item for item in normalized}
    normalized = [by_date[key] for key in sorted(by_date)]
    adjusted = [dict(item) for item in normalized]
    future_contributions = 0.0
    for item in reversed(adjusted):
        item["adjusted_eval"] = (
            _number(item.get("eval"), 0.0) or 0.0
        ) + future_contributions
        future_contributions += _number(item.get("aport"), 0.0) or 0.0

    person = account.get("person", {})
    common = {
        "currency": "EUR",
        "account_id": _text(person.get("id")),
        "account": _text(person.get("name")),
        "source": "Tradeville WebSocket pf4 / graf_pers_brut",
    }
    nav_history = [{
        **common,
        "date": item["data"],
        "nav": round((_number(item.get("eval"), 0.0) or 0.0) / eur_rate, 2),
    } for item in normalized]
    adjusted_nav = [{
        **common,
        "date": item["data"],
        "nav": round(
            (_number(item.get("adjusted_eval"), 0.0) or 0.0) / eur_rate, 2
        ),
    } for item in adjusted]
    cash_history = [{
        **common,
        "date": item["data"],
        "cash": round((_number(item.get("cash"), 0.0) or 0.0) / eur_rate, 2),
    } for item in normalized if item.get("cash") is not None]
    base = adjusted_nav[0]["nav"] if adjusted_nav else None
    profit_history = [{
        **common,
        "date": item["date"],
        "profit": round(item["nav"] - base, 2),
        "return_pct": round((item["nav"] / base - 1) * 100, 4) if base else None,
    } for item in adjusted_nav] if base is not None else []
    return {
        "nav_history": nav_history,
        "adjusted_nav_history": adjusted_nav,
        "cash_history": cash_history,
        "profit_history": profit_history,
        "history_metadata": {
            "available": bool(nav_history),
            "stale": fallback_last_good,
            "fallback_reason": graph_request.get("fallback_reason"),
            "start_requested": start.isoformat(),
            "first_date": nav_history[0]["date"] if nav_history else None,
            "last_date": nav_history[-1]["date"] if nav_history else None,
            "point_count": len(nav_history),
            "raw_reconstructed": reconstructed,
            "transfer_adjustment": "portal_equivalent_backward_contribution_adjustment",
            "currency_conversion": f"RON divided by current BNR EUR rate {eur_rate}",
            "source": "Tradeville WebSocket pf4 / graf_pers_brut",
        },
    }


def _position_records(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    overlays = _existing_overlays()
    records: list[dict[str, Any]] = []
    fetched_at = snapshot["fetched_at"]
    for account in snapshot["accounts"]:
        person = account["person"]
        account_name = _text(person.get("name"))
        account_id = _text(person.get("id"))
        for raw in account["portfolio"]:
            if not isinstance(raw, dict) or _is_cash_row(raw):
                continue
            raw_symbol = _first_text(raw, "simbol", "symbol")
            market = _first_text(raw, "market", "piata")
            exchange = _first_text(raw, "exchange", "bursa")
            symbol = _canonical_symbol(raw_symbol, market, exchange)
            shares = _first_number(raw, "sold", "cant", "shares", "quantity") or 0.0
            if not symbol or shares <= 0:
                continue
            buy_price = _first_number(raw, "costm", "buy_price", "costmediu") or 0.0
            current_price = _first_number(raw, "ppiata", "pret", "current_price") or 0.0
            investment = _first_number(raw, "investitie", "valcump", "costtotal")
            if investment is None:
                investment = shares * buy_price
            current_value = _first_number(raw, "eval", "evaluare", "current_value")
            if current_value is None:
                current_value = shares * current_price
            profit = _first_number(raw, "profit", "profitpierdere")
            if profit is None:
                profit = current_value - investment
            record = {
                "Symbol": symbol,
                "Shares": shares,
                "Buy_Price": buy_price,
                "Current_Price": current_price,
                "Current_Value": current_value,
                "Investment": investment,
                "Profit": profit,
                "Profit_Pct": (profit / investment * 100) if investment else 0.0,
                "Currency": _first_text(raw, "valuta", "currency").upper(),
                "Trail_Pct": 0.0,
                "Trail_Stop": 0.0,
                "Target": None,
                "Description": _first_text(raw, "nume", "name"),
                "Entry_Date": "",
                "Broker": "Tradeville",
                "Account": account_name,
                "Account_ID": account_id,
                "Raw_Symbol": raw_symbol,
                "Market": market,
                "Exchange": exchange,
                "Snapshot_Timestamp": fetched_at,
                "Source": "Tradeville WebSocket pf4",
            }
            overlay = overlays.get((account_name, symbol)) or overlays.get(("", symbol), {})
            for key, value in overlay.items():
                record[key] = value
            records.append(record)
    return records


def _order_records(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    fetched_at = snapshot["fetched_at"]
    for account in snapshot["accounts"]:
        person = account["person"]
        account_name = _text(person.get("name"))
        account_id = _text(person.get("id"))
        for raw in account["orders"]:
            if not isinstance(raw, dict):
                continue
            raw_symbol = _first_text(raw, "simbol", "symbol")
            market = _first_text(raw, "market", "piata")
            symbol = _canonical_symbol(raw_symbol, market, _first_text(raw, "exchange", "bursa"))
            action = _action(_first_text(raw, "csauv", "action", "side"))
            if not symbol or action not in {"BUY", "SELL"}:
                continue
            order_type = _first_text(raw, "tipord", "ordact", "ordertype", "type").upper()
            price = _first_number(raw, "pret", "price") or 0.0
            stop = _first_number(raw, "pretn", "stop", "stop_price", "declansat") or 0.0
            limit_price = _first_number(raw, "pretev", "limit_price")
            if limit_price is None and order_type in {"LMT", "LIMIT", "LIMITA"}:
                limit_price = price
            records.append({
                "Symbol": symbol,
                "OrderType": order_type or "UNKNOWN",
                "Action": action,
                "Total_Qty": _first_number(raw, "cant", "quantity", "total_qty") or 0.0,
                "Aux_Price": price if not limit_price else 0.0,
                "Limit_Price": limit_price or 0.0,
                "Stop_Price": stop,
                "Trail_Pct": _first_number(raw, "trail_pct", "trailpct") or 0.0,
                "Calculated_Stop": stop,
                "Currency": _first_text(raw, "valuta", "currency").upper(),
                "Order_Source": "Tradeville WebSocket",
                "Account": account_name,
                "Account_ID": account_id,
                "Order_ID": _first_text(raw, "idord", "id", "order_id"),
                "Status": _first_text(raw, "stare", "status", "trdstatus"),
                "Valid_Until": _first_text(raw, "valabil", "valid_until"),
                "Executed_Qty": _first_number(raw, "cantexec", "executed_qty") or 0.0,
                "Raw_Symbol": raw_symbol,
                "Market": market,
                "Snapshot_Timestamp": fetched_at,
            })
    return records


def _cash_rows(account: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in account["portfolio"] if isinstance(row, dict) and _is_cash_row(row)]


def _eur_value(row: dict[str, Any]) -> float | None:
    return _first_number(
        row, "evaleuro", "evaleur", "evaluare_eur", "value_eur", "valoareeur"
    )


def _account_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    accounts = []
    history_start = _history_start()
    for account in snapshot["accounts"]:
        person = account["person"]
        history = _account_history(account, snapshot, start=history_start)
        cash_by_currency: dict[str, float] = {}
        cash_value_eur: dict[str, float] = {}
        for row in _cash_rows(account):
            currency = _first_text(row, "valuta", "currency", "simbol", "symbol").upper()
            amount = _first_number(row, "sold", "cant", "amount", "quantity")
            if currency and amount is not None:
                cash_by_currency[currency] = cash_by_currency.get(currency, 0.0) + amount
            eur = _eur_value(row)
            if currency and eur is not None:
                cash_value_eur[currency] = cash_value_eur.get(currency, 0.0) + eur

        all_eur = [
            _eur_value(row) for row in account["portfolio"] if isinstance(row, dict)
        ]
        known_all_eur = [value for value in all_eur if value is not None]
        total_cash = sum(cash_value_eur.values()) if cash_value_eur else None
        nav = sum(known_all_eur) if known_all_eur else total_cash
        if nav is None and history["nav_history"]:
            nav = history["nav_history"][-1]["nav"]
        if total_cash is None and history["cash_history"]:
            total_cash = history["cash_history"][-1]["cash"]
        summary = {
            "NetLiquidation": nav,
            "TotalCashValue": total_cash,
            "AvailableFunds": total_cash,
            "GrossPositionValue": (nav - total_cash) if nav is not None and total_cash is not None else None,
        }
        accounts.append({
            "label": _text(person.get("name")),
            "account_id": _text(person.get("id")),
            "source": "Tradeville WebSocket pf4",
            "fetched_at": snapshot["fetched_at"],
            "base_currency": "EUR",
            "summary": summary,
            "cash_by_currency": cash_by_currency,
            "cash_value_eur_by_currency": cash_value_eur,
            "raw_account_info": account.get("account_info", []),
            "raw_settlement": account.get("settlement", []),
            **history,
        })
    result = {
        "fetched_at": snapshot["fetched_at"],
        "source": "Tradeville WebSocket pf4",
        "accounts": accounts,
    }
    for field in (
        "nav_history", "adjusted_nav_history", "cash_history", "profit_history"
    ):
        result[f"tradeville_{field}"] = [
            point for item in accounts for point in item.get(field, [])
        ]
    result["tradeville_history_start"] = history_start.isoformat()
    return result


def persist_snapshot(
    snapshot: dict[str, Any], password: str | None = None,
    expected_accounts: int = 2,
) -> dict[str, Any]:
    snapshot = _reuse_previous_graph(snapshot, password=password)
    validated = validate_snapshot(snapshot, expected_accounts=expected_accounts)
    positions = pd.DataFrame(_position_records(validated), columns=PORTFOLIO_COLUMNS)
    orders = pd.DataFrame(_order_records(validated), columns=ORDER_COLUMNS)
    account = _account_snapshot(validated)

    # Build every artifact before replacing any last-known-good file.
    portfolio_csv = positions.to_csv(index=False)
    orders_csv = orders.to_csv(index=False)
    encrypted_account = None
    encrypted_raw = None
    if password:
        encrypted_account = json.loads(market_security.encrypt_for_js(
            json.dumps(account, ensure_ascii=False), password
        ))
        encrypted_raw = json.loads(market_security.encrypt_for_js(
            json.dumps(validated, ensure_ascii=False), password
        ))

    _atomic_text(PORTFOLIO_PATH, portfolio_csv)
    _atomic_text(ORDERS_PATH, orders_csv)
    if encrypted_account is not None:
        _atomic_json(ACCOUNT_ENCRYPTED_PATH, encrypted_account)
        _atomic_json(RAW_ENCRYPTED_PATH, encrypted_raw)

    status = _status_payload(
        True,
        fetched_at=validated["fetched_at"],
        source=validated.get("source"),
        account_count=len(validated["accounts"]),
        position_count=len(positions),
        active_order_count=len(orders),
        history_start=account.get("tradeville_history_start"),
        history_point_count=sum(
            len(item.get("nav_history", [])) for item in account["accounts"]
        ),
        history_account_count=sum(
            bool(item.get("nav_history")) for item in account["accounts"]
        ),
        stale_history_account_count=sum(
            bool(item.get("history_metadata", {}).get("stale"))
            for item in account["accounts"]
        ),
    )
    _atomic_json(STATUS_PATH, status)
    return status


def _reuse_previous_graph(
    snapshot: dict[str, Any], password: str | None,
    path: Path | None = None,
) -> dict[str, Any]:
    """Reuse only historical graphs when the optional endpoint times out."""
    if not password or not isinstance(snapshot, dict):
        return snapshot
    target = Path(path or RAW_ENCRYPTED_PATH)
    try:
        encrypted = json.loads(target.read_text(encoding="utf-8"))
        previous = json.loads(market_security.decrypt_from_js(encrypted, password))
    except (OSError, TypeError, ValueError, KeyError):
        return snapshot
    previous_accounts = {
        _text((account.get("person") or {}).get("id")): account
        for account in previous.get("accounts", [])
        if isinstance(account, dict)
    }
    result = copy.deepcopy(snapshot)
    for account in result.get("accounts", []):
        if not isinstance(account, dict) or account.get("portfolio_graph"):
            continue
        person_id = _text((account.get("person") or {}).get("id"))
        old_account = previous_accounts.get(person_id) or {}
        old_graph = old_account.get("portfolio_graph")
        if not isinstance(old_graph, list) or not old_graph:
            continue
        request = dict(account.get("portfolio_graph_request") or {})
        request.update({
            "fallback_last_good": True,
            "fallback_reason": request.get("error") or "graph_unavailable",
            "fallback_snapshot_at": previous.get("fetched_at"),
        })
        account["portfolio_graph"] = copy.deepcopy(old_graph)
        account["portfolio_graph_request"] = request
    return result


class _BridgeState:
    def __init__(self) -> None:
        self.job_id = secrets.token_urlsafe(12)
        self.token = secrets.token_urlsafe(32)
        self.history_start = _history_start().isoformat()
        self.claimed = False
        self.result: dict[str, Any] | None = None
        self.event = threading.Event()
        self.lock = threading.Lock()


def _handler_factory(state: _BridgeState):
    class Handler(BaseHTTPRequestHandler):
        server_version = "MarketScannerTradevilleBridge/1"

        def log_message(self, _format: str, *_args: Any) -> None:
            return

        def _authorised(self) -> bool:
            return hmac.compare_digest(
                self.headers.get("X-Market-Scanner-Bridge", ""), BRIDGE_HEADER
            )

        def _json(self, status: int, payload: Any) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802
            if not self._authorised():
                self._json(403, {"error": "forbidden"})
                return
            if urlparse(self.path).path != "/v1/job":
                self._json(404, {"error": "not_found"})
                return
            with state.lock:
                if state.claimed or state.result is not None:
                    self.send_response(204)
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers()
                    return
                state.claimed = True
                payload = {
                    "id": state.job_id,
                    "token": state.token,
                    "historyStart": state.history_start,
                }
            self._json(200, payload)

        def do_POST(self) -> None:  # noqa: N802
            if not self._authorised():
                self._json(403, {"error": "forbidden"})
                return
            expected_path = f"/v1/jobs/{state.job_id}/result"
            if urlparse(self.path).path != expected_path:
                self._json(404, {"error": "not_found"})
                return
            length = int(self.headers.get("Content-Length", "0") or 0)
            if length <= 0 or length > MAX_BODY_BYTES:
                self._json(413, {"error": "invalid_size"})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, ValueError):
                self._json(400, {"error": "invalid_json"})
                return
            if not hmac.compare_digest(str(payload.get("token", "")), state.token):
                self._json(403, {"error": "invalid_token"})
                return
            with state.lock:
                if state.result is not None:
                    self._json(409, {"error": "already_completed"})
                    return
                state.result = payload
                state.event.set()
            self._json(200, {"ok": True})

    return Handler


def run_sync(
    timeout: float = 50.0, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT,
    expected_accounts: int = 2,
) -> dict[str, Any]:
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise SnapshotError("bridge-ul poate asculta numai pe loopback")
    state = _BridgeState()
    server = ThreadingHTTPServer((host, port), _handler_factory(state))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        print(
            "Tradeville bridge așteaptă extensia Chrome pe "
            f"http://{host}:{port} ({int(timeout)}s)..."
        )
        if not state.event.wait(timeout):
            raise TimeoutError(
                "extensia nu a răspuns; verifică dacă este instalată și "
                "portal.tradeville.ro este deschis și autentificat"
            )
        result = state.result or {}
        if result.get("ok") is not True:
            raise SnapshotError(_text(result.get("error")) or "sync Tradeville eșuat")
        password = os.environ.get("PORTFOLIO_ORDER_CACHE_PASSWORD") or os.environ.get(
            "PORTFOLIO_PASSWORD"
        )
        return persist_snapshot(
            result.get("snapshot"), password=password,
            expected_accounts=expected_accounts,
        )
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=2)


def record_failure(error: Exception) -> None:
    status = _status_payload(
        False,
        stale=True,
        error=type(error).__name__,
        message=str(error)[:400],
        last_good_snapshot_preserved=True,
    )
    _atomic_json(STATUS_PATH, status)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", default="sync", choices=("sync",))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get(
        "TRADEVILLE_BRIDGE_TIMEOUT", "50"
    )))
    parser.add_argument("--port", type=int, default=int(os.environ.get(
        "TRADEVILLE_BRIDGE_PORT", str(DEFAULT_PORT)
    )))
    parser.add_argument("--expected-accounts", type=int, default=int(os.environ.get(
        "TRADEVILLE_EXPECTED_ACCOUNTS", "2"
    )))
    args = parser.parse_args()
    try:
        status = run_sync(
            timeout=args.timeout, port=args.port,
            expected_accounts=args.expected_accounts,
        )
    except Exception as error:  # Preserve last-known-good data on every failure.
        record_failure(error)
        print(f"Tradeville WebSocket indisponibil: {error}")
        return 1
    print(
        "Tradeville WebSocket sincronizat: "
        f"{status['account_count']} conturi, {status['position_count']} poziții, "
        f"{status['active_order_count']} ordine active; "
        f"istoric {status['history_point_count']} puncte pentru "
        f"{status['history_account_count']} conturi, din {status['history_start']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
