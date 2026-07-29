"""Web push pentru tranzițiile noi în starea „Cumpărare acum”."""

import datetime
import os
import uuid

import requests


ONESIGNAL_NOTIFICATIONS_URL = "https://api.onesignal.com/notifications"
BUY_NOW_VERDICT = "Candidat valid"
STATE_VERSION = 1


def _normalized_symbol(value):
    return str(value or "").strip().upper()


def immediate_buy_symbols(result, candidates):
    """Întoarce exact simbolurile afișate de dashboard ca „Cumpărare acum”."""
    candidates_by_symbol = {
        _normalized_symbol(candidate.get("symbol")): candidate
        for candidate in (candidates or [])
        if _normalized_symbol(candidate.get("symbol"))
    }
    symbols = set()
    for recommendation in (result or {}).get("buy_recommendations", []):
        symbol = _normalized_symbol(recommendation.get("symbol"))
        candidate = candidates_by_symbol.get(symbol)
        if (
            not candidate
            or recommendation.get("verdict") != BUY_NOW_VERDICT
        ):
            continue
        filters_allow_action = (
            not candidate.get("requires_watchlist_filters", True)
            or candidate.get("strict_eligible", True)
        )
        if filters_allow_action:
            symbols.add(symbol)
    return sorted(symbols)


def buy_now_message(symbol):
    return f"Ordin de cumpărare acum: {_normalized_symbol(symbol)}."


def _event_idempotency_key(symbol, event_token):
    event_identity = (
        f"market-scanner:buy-now:{_normalized_symbol(symbol)}:"
        f"{str(event_token or 'current')}"
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, event_identity))


def _send_onesignal_notification(
    symbol,
    app_id,
    api_key,
    site_url,
    event_token,
    post,
):
    message = buy_now_message(symbol)
    payload = {
        "app_id": app_id,
        "target_channel": "push",
        "included_segments": ["Subscribed Users"],
        "headings": {
            "en": "Market Scanner",
            "ro": "Market Scanner",
        },
        "contents": {
            "en": message,
            "ro": message,
        },
        "name": f"buy-now-{_normalized_symbol(symbol)}",
        "idempotency_key": _event_idempotency_key(symbol, event_token),
    }
    if site_url:
        payload["url"] = site_url
    response = post(
        ONESIGNAL_NOTIFICATIONS_URL,
        headers={
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    response_payload = response.json()
    notification_id = response_payload.get("id")
    if not notification_id:
        raise RuntimeError(
            "OneSignal nu a găsit niciun abonament web push activ."
        )
    return str(notification_id)


def send_new_buy_now_notifications(
    previous_state,
    result,
    candidates,
    event_token=None,
    app_id=None,
    api_key=None,
    site_url=None,
    post=None,
    now=None,
):
    """Trimite o singură alertă la intrarea unui simbol în „Cumpărare acum”."""
    previous_state = (
        dict(previous_state) if isinstance(previous_state, dict) else {}
    )
    current_symbols = set(immediate_buy_symbols(result, candidates))
    previously_notified = {
        _normalized_symbol(symbol)
        for symbol in previous_state.get("notified_active_symbols", [])
        if _normalized_symbol(symbol)
    }
    still_notified = previously_notified & current_symbols
    pending_symbols = sorted(current_symbols - still_notified)

    app_id = str(app_id or os.environ.get("ONESIGNAL_APP_ID") or "").strip()
    api_key = str(
        api_key or os.environ.get("ONESIGNAL_API_KEY") or ""
    ).strip()
    site_url = str(
        site_url
        or os.environ.get("ONESIGNAL_SITE_URL")
        or "https://ddanyro.github.io/market-scanner/"
    ).strip()
    post = post or requests.post
    now = now or datetime.datetime.now(datetime.timezone.utc)
    delivered_symbols = []
    errors = {}

    configured = bool(app_id and api_key)
    if configured:
        for symbol in pending_symbols:
            try:
                _send_onesignal_notification(
                    symbol,
                    app_id,
                    api_key,
                    site_url,
                    event_token,
                    post,
                )
                delivered_symbols.append(symbol)
                still_notified.add(symbol)
            except Exception as exc:
                errors[symbol] = str(exc)[:500]

    state_core = {
        "version": STATE_VERSION,
        "current_symbols": sorted(current_symbols),
        "notified_active_symbols": sorted(still_notified),
    }
    previous_core = {
        key: previous_state.get(key)
        for key in state_core
    }
    if state_core != previous_core:
        state_core["updated_at"] = now.isoformat()
    elif previous_state.get("updated_at"):
        state_core["updated_at"] = previous_state["updated_at"]

    if delivered_symbols:
        state_core["last_delivery_at"] = now.isoformat()
        state_core["last_delivered_symbols"] = delivered_symbols
    else:
        for key in ("last_delivery_at", "last_delivered_symbols"):
            if previous_state.get(key):
                state_core[key] = previous_state[key]

    diagnostic = {
        "status": (
            "configuration_missing"
            if not configured
            else "failed"
            if errors
            else "sent"
            if delivered_symbols
            else "no_new_orders"
        ),
        "current_symbols": sorted(current_symbols),
        "pending_symbols": pending_symbols,
        "delivered_symbols": delivered_symbols,
        "errors": errors,
    }
    return state_core, diagnostic
