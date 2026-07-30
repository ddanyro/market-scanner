"""Web push Firebase pentru tranzițiile noi în starea „Cumpărare acum”."""

import argparse
import datetime
import json
import os

import requests


FCM_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"
FCM_SEND_URL = "https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
BUY_NOW_VERDICT = "Candidat valid"
STATE_VERSION = 2


def _normalized_symbol(value):
    return str(value or "").strip().upper()


def _registration_tokens(value):
    """Normalizează lista de tokenuri FCM fără a le publica în loguri."""
    tokens = []
    raw_value = value
    if isinstance(value, (list, tuple, set)):
        raw_value = "\n".join(str(item or "") for item in value)
    for raw_token in str(raw_value or "").replace(",", "\n").splitlines():
        token = raw_token.strip()
        if len(token) < 40 or any(character.isspace() for character in token):
            continue
        if token not in tokens:
            tokens.append(token)
    return tokens


def _service_account_info(value):
    if isinstance(value, dict):
        info = dict(value)
    else:
        try:
            info = json.loads(str(value or ""))
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
    if not isinstance(info, dict):
        return {}
    if not info.get("project_id") or not info.get("private_key"):
        return {}
    if not info.get("client_email"):
        return {}
    return info


def _firebase_access_token(service_account_info):
    """Obține un token OAuth scurt folosind biblioteca oficială Google."""
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=[FCM_SCOPE],
    )
    credentials.refresh(Request())
    return credentials.token


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
        if not candidate or recommendation.get("verdict") != BUY_NOW_VERDICT:
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


def _send_firebase_notification(
    symbol,
    registration_token,
    project_id,
    access_token,
    site_url,
    post,
):
    message = buy_now_message(symbol)
    payload = {
        "message": {
            "token": registration_token,
            "notification": {
                "title": "Market Scanner",
                "body": message,
            },
            "data": {
                "symbol": _normalized_symbol(symbol),
                "kind": "buy_now",
            },
            "webpush": {
                "headers": {
                    "Urgency": "high",
                    "TTL": "3600",
                },
                "fcm_options": {"link": site_url},
            },
        }
    }
    response = post(
        FCM_SEND_URL.format(project_id=project_id),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; UTF-8",
        },
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    response_payload = response.json()
    message_id = response_payload.get("name")
    if not message_id:
        raise RuntimeError("Firebase nu a returnat ID-ul mesajului.")
    return str(message_id)


def _delivery_configuration(
    service_account_json=None,
    registration_tokens=None,
    access_token_factory=None,
):
    service_account_info = _service_account_info(
        service_account_json
        if service_account_json is not None
        else os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    )
    tokens = _registration_tokens(
        registration_tokens
        if registration_tokens is not None
        else os.environ.get("FIREBASE_REGISTRATION_TOKENS")
    )
    if not service_account_info or not tokens:
        return {}, [], ""
    token_factory = access_token_factory or _firebase_access_token
    return (
        service_account_info,
        tokens,
        str(token_factory(service_account_info) or "").strip(),
    )


def send_new_buy_now_notifications(
    previous_state,
    result,
    candidates,
    event_token=None,
    service_account_json=None,
    registration_tokens=None,
    site_url=None,
    post=None,
    access_token_factory=None,
    now=None,
):
    """Trimite o singură alertă FCM la intrarea în „Cumpărare acum”."""
    del event_token  # Păstrat în semnătură pentru compatibilitatea apelurilor.
    previous_state = (
        dict(previous_state) if isinstance(previous_state, dict) else {}
    )
    current_symbols = set(immediate_buy_symbols(result, candidates))
    previously_notified = (
        {
            _normalized_symbol(symbol)
            for symbol in previous_state.get("notified_active_symbols", [])
            if _normalized_symbol(symbol)
        }
        if previous_state.get("provider") == "firebase"
        else set()
    )
    still_notified = previously_notified & current_symbols
    pending_symbols = sorted(current_symbols - still_notified)
    site_url = str(
        site_url
        or os.environ.get("FIREBASE_SITE_URL")
        or "https://ddanyro.github.io/market-scanner/"
    ).strip()
    post = post or requests.post
    now = now or datetime.datetime.now(datetime.timezone.utc)
    errors = {}
    delivered_symbols = []

    try:
        account, tokens, access_token = _delivery_configuration(
            service_account_json,
            registration_tokens,
            access_token_factory,
        )
    except Exception as exc:
        account, tokens, access_token = {}, [], ""
        errors["configuration"] = str(exc)[:500]
    configured = bool(account and tokens and access_token)

    if configured:
        project_id = str(account["project_id"])
        for symbol in pending_symbols:
            token_errors = []
            sent_count = 0
            for registration_token in tokens:
                try:
                    _send_firebase_notification(
                        symbol,
                        registration_token,
                        project_id,
                        access_token,
                        site_url,
                        post,
                    )
                    sent_count += 1
                except Exception as exc:
                    token_errors.append(str(exc)[:300])
            if sent_count:
                delivered_symbols.append(symbol)
                still_notified.add(symbol)
            if token_errors:
                errors[symbol] = token_errors

    state_core = {
        "version": STATE_VERSION,
        "provider": "firebase",
        "current_symbols": sorted(current_symbols),
        "notified_active_symbols": sorted(still_notified),
    }
    previous_core = {key: previous_state.get(key) for key in state_core}
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
        "provider": "firebase",
        "status": (
            "configuration_missing"
            if not configured
            else "failed"
            if errors and not delivered_symbols
            else "sent"
            if delivered_symbols
            else "no_new_orders"
        ),
        "current_symbols": sorted(current_symbols),
        "pending_symbols": pending_symbols,
        "delivered_symbols": delivered_symbols,
        "target_count": len(tokens),
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
    cached_analysis = dashboard_state.get("last_portfolio_ai_analysis") or {}
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
            json.dump(dashboard_state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    return diagnostic


def send_test_notification(
    symbol="TEST",
    registration_token=None,
    service_account_json=None,
    site_url=None,
    post=None,
    access_token_factory=None,
    now=None,
):
    """Trimite un push FCM de test independent de recomandările din cache."""
    symbol = _normalized_symbol(symbol) or "TEST"
    now = now or datetime.datetime.now(datetime.timezone.utc)
    try:
        account, tokens, access_token = _delivery_configuration(
            service_account_json,
            registration_token,
            access_token_factory,
        )
    except Exception as exc:
        return {
            "provider": "firebase",
            "status": "configuration_invalid",
            "symbol": symbol,
            "message_ids": [],
            "error": str(exc)[:500],
        }
    if not account or not tokens or not access_token:
        return {
            "provider": "firebase",
            "status": "configuration_missing",
            "symbol": symbol,
            "message_ids": [],
            "error": (
                "Lipsesc FIREBASE_SERVICE_ACCOUNT_JSON sau "
                "FIREBASE_REGISTRATION_TOKENS."
            ),
        }
    site_url = str(
        site_url
        or os.environ.get("FIREBASE_SITE_URL")
        or "https://ddanyro.github.io/market-scanner/"
    ).strip()
    message_ids = []
    errors = []
    for token in tokens:
        try:
            message_ids.append(
                _send_firebase_notification(
                    symbol,
                    token,
                    str(account["project_id"]),
                    access_token,
                    site_url,
                    post or requests.post,
                )
            )
        except Exception as exc:
            errors.append(str(exc)[:300])
    return {
        "provider": "firebase",
        "status": "sent" if message_ids else "failed",
        "symbol": symbol,
        "message_ids": message_ids,
        "target_count": len(tokens),
        "error": "; ".join(errors) if errors else None,
        "sent_at": now.isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Trimite sau reîncearcă alerte BUY prin Firebase."
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
        help="Trimite imediat un push Firebase de test.",
    )
    parser.add_argument(
        "--registration-token",
        help="Țintește direct un token de înregistrare FCM.",
    )
    args = parser.parse_args()
    if args.retry_state:
        diagnostic = retry_cached_buy_now_notifications(args.retry_state)
        prefix = "Retry Firebase BUY: "
    else:
        diagnostic = send_test_notification(
            args.test_symbol,
            registration_token=args.registration_token,
        )
        prefix = "Test Firebase BUY: "
    print(prefix + json.dumps(diagnostic, ensure_ascii=False))


if __name__ == "__main__":
    main()
