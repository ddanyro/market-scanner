"""Web push pentru tranzițiile noi în starea „Cumpărare acum”."""

import argparse
import datetime
import json
import os
import uuid

import requests


ONESIGNAL_NOTIFICATIONS_URL = "https://api.onesignal.com/notifications"
BUY_NOW_VERDICT = "Candidat valid"
STATE_VERSION = 1


def _normalized_symbol(value):
    return str(value or "").strip().upper()


def _subscription_ids(value):
    identifiers = []
    for raw_identifier in str(value or "").split(","):
        raw_identifier = raw_identifier.strip()
        if not raw_identifier:
            continue
        try:
            identifiers.append(str(uuid.UUID(raw_identifier)))
        except (ValueError, AttributeError, TypeError):
            continue
    return identifiers


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
    subscription_ids=None,
):
    message = buy_now_message(symbol)
    payload = {
        "app_id": app_id,
        "target_channel": "push",
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
    if subscription_ids:
        payload["include_subscription_ids"] = list(subscription_ids)
    else:
        payload["included_segments"] = ["Subscribed Users"]
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
        response_errors = response_payload.get("errors")
        error_detail = (
            f" Detalii OneSignal: {str(response_errors)[:300]}."
            if response_errors
            else ""
        )
        raise RuntimeError(
            "OneSignal nu a găsit niciun abonament web push activ."
            + error_detail
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
    subscription_ids=None,
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
    if subscription_ids is None:
        subscription_ids = _subscription_ids(
            os.environ.get("ONESIGNAL_SUBSCRIPTION_IDS")
        )
    else:
        subscription_ids = _subscription_ids(
            ",".join(subscription_ids)
            if isinstance(subscription_ids, (list, tuple, set))
            else subscription_ids
        )
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
                    subscription_ids=subscription_ids,
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


def retry_cached_buy_now_notifications(
    state_path="dashboard_state.json",
    **delivery_options,
):
    """Reîncearcă imediat semnalele BUY restante din ultimul cache valid."""
    with open(state_path, "r", encoding="utf-8") as handle:
        dashboard_state = json.load(handle)
    cached_analysis = (
        dashboard_state.get("last_portfolio_ai_analysis") or {}
    )
    result = cached_analysis.get("result") or {}
    candidates = cached_analysis.get("buy_candidates") or []
    previous_state = dashboard_state.get("buy_now_push_state") or {}
    next_state, diagnostic = send_new_buy_now_notifications(
        previous_state,
        result,
        candidates,
        event_token=cached_analysis.get("generated_at"),
        **delivery_options,
    )
    if next_state != previous_state:
        dashboard_state["buy_now_push_state"] = next_state
        with open(state_path, "w", encoding="utf-8") as handle:
            json.dump(
                dashboard_state,
                handle,
                ensure_ascii=False,
                indent=2,
            )
            handle.write("\n")
    return diagnostic


def send_test_notification(
    symbol="TEST",
    subscription_id=None,
    app_id=None,
    api_key=None,
    site_url=None,
    post=None,
    now=None,
):
    """Trimite un push de test independent de recomandările din cache."""
    symbol = _normalized_symbol(symbol) or "TEST"
    app_id = str(
        app_id or os.environ.get("ONESIGNAL_APP_ID") or ""
    ).strip()
    api_key = str(
        api_key or os.environ.get("ONESIGNAL_API_KEY") or ""
    ).strip()
    site_url = str(
        site_url
        or os.environ.get("ONESIGNAL_SITE_URL")
        or "https://ddanyro.github.io/market-scanner/"
    ).strip()
    if not app_id or not api_key:
        return {
            "status": "configuration_missing",
            "symbol": symbol,
            "notification_id": None,
            "error": "Lipsesc ONESIGNAL_APP_ID sau ONESIGNAL_API_KEY.",
        }
    now = now or datetime.datetime.now(datetime.timezone.utc)
    subscription_ids = _subscription_ids(
        subscription_id
        or os.environ.get("ONESIGNAL_SUBSCRIPTION_IDS")
    )
    if subscription_id and not subscription_ids:
        return {
            "status": "invalid_subscription_id",
            "symbol": symbol,
            "notification_id": None,
            "error": "Subscription ID-ul OneSignal nu este un UUID valid.",
        }
    try:
        notification_id = _send_onesignal_notification(
            symbol,
            app_id,
            api_key,
            site_url,
            f"manual-test:{now.isoformat()}",
            post or requests.post,
            subscription_ids=subscription_ids,
        )
    except Exception as exc:
        return {
            "status": "failed",
            "symbol": symbol,
            "notification_id": None,
            "error": str(exc)[:500],
        }
    return {
        "status": "sent",
        "symbol": symbol,
        "notification_id": notification_id,
        "error": None,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Trimite sau reîncearcă alerte BUY prin OneSignal."
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--retry-state",
        metavar="FILE",
        help="Reîncearcă alertele din cache-ul dashboardului.",
    )
    action.add_argument(
        "--test-symbol",
        metavar="SYMBOL",
        help="Trimite imediat un push de test pentru simbolul indicat.",
    )
    parser.add_argument(
        "--subscription-id",
        help="Țintește direct un Subscription ID OneSignal.",
    )
    args = parser.parse_args()
    if args.retry_state:
        diagnostic = retry_cached_buy_now_notifications(args.retry_state)
        prefix = "Retry web push BUY: "
    else:
        diagnostic = send_test_notification(
            args.test_symbol,
            subscription_id=args.subscription_id,
        )
        prefix = "Test web push BUY: "
    print(prefix + json.dumps(diagnostic, ensure_ascii=False))


if __name__ == "__main__":
    main()
