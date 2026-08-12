"""Read-only client for the official Interactive Brokers MCP connector.

The OAuth grant is deliberately restricted to ``mcp.read``.  This module is
kept independent from TWS so the scanner can try MCP first and retain all
existing fallbacks when MCP has not yet been authorised or is unavailable.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import datetime
import hashlib
import json
import os
import re
import secrets
import stat
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


MCP_URL = os.environ.get(
    "IBKR_MCP_URL", "https://api.ibkr.com/v1/api/mcp-public"
)
CALLBACK_HOST = "127.0.0.1"
CALLBACK_PORT = int(os.environ.get("IBKR_MCP_CALLBACK_PORT", "8765"))
CALLBACK_URL = f"http://{CALLBACK_HOST}:{CALLBACK_PORT}/callback"
CREDENTIALS_FILE = Path(
    os.environ.get("IBKR_MCP_CREDENTIALS_FILE", ".ibkr_mcp_credentials.json")
)
MARKET_CACHE_FILE = Path(
    os.environ.get(
        "IBKR_MCP_MARKET_CACHE_FILE", ".ibkr_mcp_market_cache.json"
    )
)
MARKET_CACHE_VERSION = 1
MARKET_DATA_TTL_HOURS = float(
    os.environ.get("IBKR_MCP_MARKET_TTL_HOURS", "1")
)
CONTRACT_CACHE_TTL_DAYS = float(
    os.environ.get("IBKR_MCP_CONTRACT_TTL_DAYS", "30")
)
MARKET_DATA_CONCURRENCY = max(
    1, min(10, int(os.environ.get("IBKR_MCP_MARKET_CONCURRENCY", "5")))
)
MARKET_DATA_BATCH_SIZE = max(
    1, int(os.environ.get("IBKR_MCP_MARKET_BATCH", "70"))
)
READ_ONLY_SCOPES = "mcp.read"
AUTHORIZATION_URL = "https://api.ibkr.com/oauth2/authorize"
TOKEN_URL = "https://api.ibkr.com/oauth2/api/v1/token"
REGISTRATION_URL = "https://api.ibkr.com/oauth2/register"
USER_AGENT = "Market-Scanner-IBKR-MCP/1.0"
ALLOWED_READ_ONLY_TOOLS = {
    "get_account_balances",
    "get_account_orders",
    "get_account_positions",
    "get_account_summary",
    "get_account_trades",
    "get_pa_allocation",
    "get_pa_performance_all_periods",
    "get_price_history",
    "get_price_snapshot",
    "search_contracts",
}


class IBKRMCPError(RuntimeError):
    """Raised when the official IBKR MCP source cannot be used."""


class IBKRMCPAuthorizationRequired(IBKRMCPError):
    """Raised when IBKR requires a new interactive OAuth authorisation."""


def _load_sdk():
    try:
        import httpx
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client
    except ImportError as exc:  # pragma: no cover - depends on local install
        raise IBKRMCPError(
            "SDK-ul MCP lipsește. Rulează pip install -r requirements.txt."
        ) from exc
    return {
        "httpx": httpx,
        "ClientSession": ClientSession,
        "streamable_http_client": streamable_http_client,
    }


class FileTokenStorage:
    """Small local OAuth store excluded from Git and created with mode 0600."""

    def __init__(self, path: Path = CREDENTIALS_FILE):
        self.path = path

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise IBKRMCPError(
                f"Credentialele MCP IBKR sunt invalide: {self.path}"
            ) from exc

    def _write(self, payload: dict[str, Any]) -> None:
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def get_tokens(self) -> dict[str, Any] | None:
        raw = self._read().get("tokens")
        return raw if isinstance(raw, dict) else None

    def set_tokens(self, tokens: dict[str, Any]) -> None:
        payload = self._read()
        payload["tokens"] = tokens
        self._write(payload)

    def get_client_info(self) -> dict[str, Any] | None:
        raw = self._read().get("client_info")
        return raw if isinstance(raw, dict) else None

    def set_client_info(self, client_info: dict[str, Any]) -> None:
        payload = self._read()
        payload["client_info"] = client_info
        self._write(payload)


class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    result: dict[str, str | None] = {}

    def do_GET(self):  # noqa: N802 - stdlib callback name
        query = parse_qs(urlparse(self.path).query)
        self.__class__.result = {
            "code": query.get("code", [None])[0],
            "state": query.get("state", [None])[0],
            "error": query.get("error", [None])[0],
        }
        ok = bool(self.__class__.result.get("code"))
        body = (
            "Autorizarea IBKR a reușit. Poți închide această fereastră."
            if ok
            else "Autorizarea IBKR nu a reușit. Revino în terminal."
        )
        encoded = body.encode("utf-8")
        self.send_response(200 if ok else 400)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, _format, *_args):
        return


async def _redirect_handler(url: str) -> None:
    print("Se deschide pagina securizată IBKR pentru autorizare read-only...")
    opened = await asyncio.to_thread(webbrowser.open, url, new=2)
    if not opened:
        print(f"Deschide manual această adresă:\n{url}")


async def _callback_handler() -> tuple[str, str | None]:
    _OAuthCallbackHandler.result = {}
    try:
        server = HTTPServer(
            (CALLBACK_HOST, CALLBACK_PORT), _OAuthCallbackHandler
        )
    except OSError as exc:
        raise IBKRMCPError(
            f"Portul OAuth local {CALLBACK_PORT} nu este disponibil."
        ) from exc
    server.timeout = 300
    try:
        await asyncio.to_thread(server.handle_request)
    finally:
        server.server_close()
    result = _OAuthCallbackHandler.result
    if result.get("error"):
        raise IBKRMCPError(f"IBKR OAuth: {result['error']}")
    code = result.get("code")
    if not code:
        raise IBKRMCPError("IBKR nu a returnat codul OAuth în 5 minute.")
    return str(code), result.get("state")


def _pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(96)[:128]
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).decode("ascii").rstrip("=")
    return verifier, challenge


def _assert_read_only_token(token: dict[str, Any]) -> None:
    scopes = set(str(token.get("scope", READ_ONLY_SCOPES)).split())
    if "mcp.write" in scopes:
        raise IBKRMCPError(
            "IBKR a returnat permisiunea mcp.write; tokenul a fost refuzat."
        )
    if "mcp.read" not in scopes:
        raise IBKRMCPError("Tokenul IBKR nu conține permisiunea mcp.read.")


class ReadOnlyOAuthClient:
    """Minimal OAuth 2.1 + PKCE client that never requests ``mcp.write``."""

    def __init__(self, storage: FileTokenStorage):
        self.storage = storage

    async def _register(self, client) -> dict[str, Any]:
        info = self.storage.get_client_info()
        if info and info.get("client_id"):
            return info
        response = await client.post(
            REGISTRATION_URL,
            json={
                "redirect_uris": [CALLBACK_URL],
                "token_endpoint_auth_method": "none",
                "grant_types": ["authorization_code", "refresh_token"],
                "response_types": ["code"],
                "scope": READ_ONLY_SCOPES,
                "client_name": "Market Scanner — IBKR read-only",
            },
        )
        if response.status_code != 201:
            raise IBKRMCPError(
                "Înregistrarea OAuth IBKR a eșuat: "
                f"HTTP {response.status_code}."
            )
        info = response.json()
        if not info.get("client_id"):
            raise IBKRMCPError("IBKR nu a returnat client_id.")
        # The registration response advertises all capabilities accepted by
        # the client.  The authorization request below still asks only for
        # mcp.read, and the resulting grant is verified independently.
        self.storage.set_client_info(info)
        return info

    async def _store_token(
        self,
        token: dict[str, Any],
        previous: dict[str, Any] | None = None,
    ) -> str:
        if previous and not token.get("refresh_token"):
            token["refresh_token"] = previous.get("refresh_token")
        _assert_read_only_token(token)
        token["expires_at"] = time.time() + float(token.get("expires_in", 0))
        self.storage.set_tokens(token)
        return str(token["access_token"])

    async def _refresh(
        self,
        client,
        client_info: dict[str, Any],
        token: dict[str, Any],
    ) -> str | None:
        refresh_token = token.get("refresh_token")
        if not refresh_token:
            return None
        response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_info["client_id"],
                "scope": READ_ONLY_SCOPES,
                "resource": MCP_URL,
            },
        )
        if response.status_code != 200:
            return None
        return await self._store_token(response.json(), previous=token)

    async def access_token(self, *, interactive: bool) -> str:
        sdk = _load_sdk()
        async with sdk["httpx"].AsyncClient(
            follow_redirects=True,
            timeout=60,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        ) as client:
            client_info = await self._register(client)
            token = self.storage.get_tokens()
            if token:
                _assert_read_only_token(token)
                if float(token.get("expires_at", 0)) > time.time() + 60:
                    return str(token["access_token"])
                refreshed = await self._refresh(client, client_info, token)
                if refreshed:
                    return refreshed
            if not interactive:
                raise IBKRMCPAuthorizationRequired(
                    "Sesiunea IBKR MCP a expirat; rulează o dată "
                    "python ibkr_mcp.py login."
                )

            verifier, challenge = _pkce()
            state = secrets.token_urlsafe(32)
            from urllib.parse import urlencode

            authorization_params = urlencode({
                'response_type': 'code',
                'client_id': client_info['client_id'],
                'redirect_uri': CALLBACK_URL,
                'state': state,
                'code_challenge': challenge,
                'code_challenge_method': 'S256',
                'scope': READ_ONLY_SCOPES,
                'resource': MCP_URL,
            })
            authorization_url = f"{AUTHORIZATION_URL}?{authorization_params}"
            await _redirect_handler(authorization_url)
            code, returned_state = await _callback_handler()
            if returned_state is None or not secrets.compare_digest(
                returned_state, state
            ):
                raise IBKRMCPError("Verificarea OAuth state a eșuat.")
            response = await client.post(
                TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": CALLBACK_URL,
                    "client_id": client_info["client_id"],
                    "code_verifier": verifier,
                    "resource": MCP_URL,
                },
            )
            if response.status_code != 200:
                raise IBKRMCPError(
                    f"Schimbul tokenului IBKR a eșuat: HTTP "
                    f"{response.status_code}."
                )
            return await self._store_token(response.json())


async def list_tools(*, interactive: bool = True) -> list[dict[str, Any]]:
    """Authenticate if needed and return the official IBKR MCP tool schemas."""
    sdk = _load_sdk()
    storage = FileTokenStorage()
    if not interactive and not CREDENTIALS_FILE.exists():
        raise IBKRMCPAuthorizationRequired(
            "IBKR MCP nu este încă autorizat local."
        )
    token = await ReadOnlyOAuthClient(storage).access_token(
        interactive=interactive
    )
    async with sdk["httpx"].AsyncClient(
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
        },
        follow_redirects=True,
        timeout=60,
    ) as client:
        async with sdk["streamable_http_client"](
            MCP_URL, http_client=client
        ) as (read_stream, write_stream, _):
            async with sdk["ClientSession"](
                read_stream, write_stream
            ) as session:
                await session.initialize()
                response = await session.list_tools()
                return [
                    tool.model_dump(mode="json", exclude_none=True)
                    for tool in response.tools
                ]


async def call_tool(
    name: str,
    arguments: dict[str, Any] | None = None,
    *,
    interactive: bool = False,
) -> dict[str, Any]:
    """Call one IBKR MCP tool and return its structured JSON result."""
    if name not in ALLOWED_READ_ONLY_TOOLS:
        raise IBKRMCPError(
            f"Instrumentul IBKR {name} nu este permis de clientul read-only."
        )
    sdk = _load_sdk()
    token = await ReadOnlyOAuthClient(FileTokenStorage()).access_token(
        interactive=interactive
    )
    async with sdk["httpx"].AsyncClient(
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
        },
        follow_redirects=True,
        timeout=60,
    ) as client:
        async with sdk["streamable_http_client"](
            MCP_URL, http_client=client
        ) as (read_stream, write_stream, _):
            async with sdk["ClientSession"](
                read_stream, write_stream
            ) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments or {})
                if result.isError:
                    message = " ".join(
                        str(getattr(item, "text", ""))
                        for item in result.content
                    ).strip()
                    raise IBKRMCPError(
                        f"Instrumentul IBKR {name} a eșuat: {message}"
                    )
                if isinstance(result.structuredContent, dict):
                    return result.structuredContent
                for item in result.content:
                    text = getattr(item, "text", None)
                    if text:
                        try:
                            payload = json.loads(text)
                        except ValueError:
                            continue
                        if isinstance(payload, dict):
                            return payload
                raise IBKRMCPError(
                    f"Instrumentul IBKR {name} nu a returnat JSON structurat."
                )


def _tool_result_json(result: Any, name: str) -> dict[str, Any]:
    """Extrage rezultatul JSON al unui apel dintr-o sesiune MCP persistentă."""
    if result.isError:
        message = " ".join(
            str(getattr(item, "text", ""))
            for item in result.content
        ).strip()
        raise IBKRMCPError(f"Instrumentul IBKR {name} a eșuat: {message}")
    if isinstance(result.structuredContent, dict):
        return result.structuredContent
    for item in result.content:
        text = getattr(item, "text", None)
        if not text:
            continue
        try:
            payload = json.loads(text)
        except ValueError:
            continue
        if isinstance(payload, dict):
            return payload
    raise IBKRMCPError(
        f"Instrumentul IBKR {name} nu a returnat JSON structurat."
    )


class ReadOnlyMCPSession:
    """O singură conexiune MCP reutilizată de toate simbolurile unei rulări."""

    def __init__(self):
        self.sdk: dict[str, Any] | None = None
        self.http_client = None
        self.stream_context = None
        self.session_context = None
        self.session = None

    async def __aenter__(self):
        try:
            self.sdk = _load_sdk()
            token = await ReadOnlyOAuthClient(FileTokenStorage()).access_token(
                interactive=False
            )
            self.http_client = self.sdk["httpx"].AsyncClient(
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": USER_AGENT,
                },
                follow_redirects=True,
                timeout=60,
            )
            await self.http_client.__aenter__()
            self.stream_context = self.sdk["streamable_http_client"](
                MCP_URL, http_client=self.http_client
            )
            read_stream, write_stream, _ = await self.stream_context.__aenter__()
            self.session_context = self.sdk["ClientSession"](
                read_stream, write_stream
            )
            self.session = await self.session_context.__aenter__()
            await self.session.initialize()
            return self
        except BaseException:
            await self._close(None, None, None)
            raise

    async def __aexit__(self, exc_type, exc, traceback):
        await self._close(exc_type, exc, traceback)

    async def _close(self, exc_type, exc, traceback):
        for context in (
            self.session_context, self.stream_context, self.http_client,
        ):
            if context is None:
                continue
            try:
                await context.__aexit__(exc_type, exc, traceback)
            except BaseException:
                pass

    async def call(self, name: str, arguments=None) -> dict[str, Any]:
        if name not in ALLOWED_READ_ONLY_TOOLS:
            raise IBKRMCPError(
                f"Instrumentul IBKR {name} nu este permis de clientul read-only."
            )
        result = await self.session.call_tool(name, arguments or {})
        return _tool_result_json(result, name)


def _read_market_cache(path: Path = MARKET_CACHE_FILE) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        payload = {}
    if payload.get("version") != MARKET_CACHE_VERSION:
        payload = {}
    payload.setdefault("version", MARKET_CACHE_VERSION)
    payload.setdefault("contracts", {})
    payload.setdefault("instruments", {})
    payload.setdefault("failures", {})
    for symbol, instrument in payload["instruments"].items():
        if isinstance(instrument, dict):
            instrument["ibkr_data_only"] = _market_symbol(symbol) in {
                "TVBETETF", "TVBETETF.RO",
            }
    return payload


def _write_market_cache(
    payload: dict[str, Any], path: Path = MARKET_CACHE_FILE
) -> None:
    payload["version"] = MARKET_CACHE_VERSION
    payload["updated_at"] = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.chmod(stat.S_IRUSR | stat.S_IWUSR)
    os.replace(temporary, path)


def _market_symbol(symbol: Any) -> str:
    value = str(symbol or "").strip().upper()
    aliases = {"LQQ.FR": "LQQ.PA", "FR.LQQ": "LQQ.PA"}
    return aliases.get(value, value)


def _contract_query(symbol: str) -> str:
    normalized = _market_symbol(symbol)
    for suffix in (".RO", ".PA", ".DE", ".AS", ".L", ".MI", ".MC", ".US"):
        if normalized.endswith(suffix):
            return normalized[:-len(suffix)]
    return normalized.replace("-", " ")


def _expected_country(symbol: str) -> str:
    normalized = _market_symbol(symbol)
    suffix_map = {
        ".RO": "RO", ".PA": "FR", ".DE": "DE", ".AS": "NL",
        ".L": "GB", ".MI": "IT", ".MC": "ES",
    }
    return next(
        (country for suffix, country in suffix_map.items()
         if normalized.endswith(suffix)),
        "US",
    )


def _select_contract(symbol: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    normalized_symbol = _market_symbol(symbol)
    query = _contract_query(symbol).replace(" ", "").replace("-", "")
    country = _expected_country(symbol)
    explicit_listing = any(normalized_symbol.endswith(suffix) for suffix in (
        ".RO", ".PA", ".DE", ".AS", ".L", ".MI", ".MC", ".US",
    ))
    candidates = []
    for item in payload.get("results", []):
        if not isinstance(item, dict) or not item.get("underlying_contract_id"):
            continue
        security_types = {
            str(section.get("security_type", "")).upper()
            for section in item.get("sections", [])
            if isinstance(section, dict)
        }
        if "STK" not in security_types and "FUND" not in security_types:
            continue
        if (
            explicit_listing
            and str(item.get("country_code", "")).upper() != country
        ):
            continue
        result_symbol = str(item.get("symbol", "")).upper()
        compact = result_symbol.replace(" ", "").replace("-", "")
        score = 0
        if compact == query:
            score += 100
        elif compact.startswith(query):
            score += 20
        if str(item.get("country_code", "")).upper() == country:
            score += 30
        if country == "US" and str(item.get("exchange", "")).upper() in {
            "SMART", "NASDAQ", "NYSE", "ARCA", "AMEX"
        }:
            score += 10
        candidates.append((score, item))
    if not candidates:
        return None
    candidates.sort(key=lambda entry: entry[0], reverse=True)
    if candidates[0][0] < 100:
        return None
    return candidates[0][1]


def _iso_timestamp(value: Any) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        number = float(raw)
    except ValueError:
        return raw
    if number > 1e12:
        number /= 1000
    if number > 1e9:
        return datetime.datetime.fromtimestamp(
            number, datetime.timezone.utc
        ).isoformat()
    return raw


def _normalise_price_history(payload: dict[str, Any]) -> list[dict[str, Any]]:
    columns = {
        name: payload.get(name, [])
        for name in ("time", "open", "high", "low", "close", "volume")
    }
    row_count = len(columns["close"])
    bars = []
    for index in range(row_count):
        close = _number(columns["close"][index], default=float("nan"))
        if close != close or close <= 0:
            continue
        def at(name, default=close):
            values = columns[name]
            return _number(values[index], default) if index < len(values) else default
        raw_time = columns["time"][index] if index < len(columns["time"]) else ""
        date = _iso_timestamp(raw_time)
        if not date:
            continue
        bars.append({
            "date": date,
            "open": at("open"),
            "high": at("high"),
            "low": at("low"),
            "close": close,
            "volume": at("volume", 0.0),
        })
    return bars


def _snapshot_number(value: Any) -> float | None:
    if isinstance(value, (int, float, str)):
        number = _number(value, default=float("nan"))
        return number if number == number and number > 0 else None
    if isinstance(value, dict):
        for key in ("price", "value", "last", "close", "mid"):
            if key in value:
                found = _snapshot_number(value[key])
                if found is not None:
                    return found
    return None


def _fresh_iso(value: Any, max_age_seconds: float) -> bool:
    try:
        parsed = datetime.datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except (TypeError, ValueError):
        return False
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    age = datetime.datetime.now(datetime.timezone.utc) - parsed
    return age.total_seconds() <= max_age_seconds


async def _resolve_market_contract(
    session: ReadOnlyMCPSession,
    symbol: str,
    cache: dict[str, Any],
) -> dict[str, Any] | None:
    normalized = _market_symbol(symbol)
    cached = cache["contracts"].get(normalized)
    if isinstance(cached, dict):
        ttl_days = (
            1 if cached.get("status") == "not_found"
            else CONTRACT_CACHE_TTL_DAYS
        )
        if _fresh_iso(cached.get("resolved_at"), ttl_days * 86400):
            return cached if cached.get("contract_id") else None
    response = await session.call(
        "search_contracts", {"query": _contract_query(normalized)}
    )
    match = _select_contract(normalized, response)
    resolved_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if match is None:
        cache["contracts"][normalized] = {
            "status": "not_found", "resolved_at": resolved_at,
        }
        return None
    contract = {
        "status": "ok",
        "resolved_at": resolved_at,
        "contract_id": int(match["underlying_contract_id"]),
        "symbol": str(match.get("symbol") or _contract_query(normalized)),
        "exchange": str(match.get("exchange") or ""),
        "country_code": str(match.get("country_code") or ""),
        "description": str(match.get("description") or ""),
        "issuer": str(match.get("issuer") or ""),
        "security_type": (
            "STK"
            if any(
                str(section.get("security_type", "")).upper() == "STK"
                for section in match.get("sections", [])
                if isinstance(section, dict)
            )
            else "FUND"
        ),
    }
    cache["contracts"][normalized] = contract
    return contract


async def _fetch_market_instrument(
    session: ReadOnlyMCPSession,
    symbol: str,
    cache: dict[str, Any],
) -> tuple[str, dict[str, Any] | None, str | None]:
    normalized = _market_symbol(symbol)
    cache.setdefault("failures", {})
    existing = cache["instruments"].get(normalized)
    if isinstance(existing, dict) and _fresh_iso(
        existing.get("fetched_at"), MARKET_DATA_TTL_HOURS * 3600
    ):
        return normalized, existing, "cached"
    recent_failure = cache.get("failures", {}).get(normalized)
    if isinstance(recent_failure, dict) and _fresh_iso(
        recent_failure.get("failed_at"), MARKET_DATA_TTL_HOURS * 3600
    ):
        return normalized, None, str(
            recent_failure.get("error") or "market_data_error_cached"
        )
    contract = await _resolve_market_contract(session, normalized, cache)
    if not contract:
        return normalized, None, "contract_not_found"
    arguments = {
        "contract_id": contract["contract_id"],
        "security_type": contract.get("security_type", "STK"),
        "period": "ONE_YEAR",
        "step": "ONE_DAY",
        "outside_rth": False,
        "include_corporate_actions": True,
    }
    if contract.get("exchange") and _expected_country(normalized) != "US":
        arguments["exchange"] = contract["exchange"]
    history_task = session.call("get_price_history", arguments)
    snapshot_task = session.call(
        "get_price_snapshot",
        {
            "contract_id": contract["contract_id"],
            **(
                {"exchange": contract["exchange"]}
                if contract.get("exchange") and _expected_country(normalized) != "US"
                else {}
            ),
            "market_data_names": [
                "last", "prior_close", "volume", "open", "low", "high",
            ],
        },
    )
    history_result, snapshot_result = await asyncio.gather(
        history_task, snapshot_task, return_exceptions=True
    )
    if isinstance(history_result, Exception):
        error = str(history_result)
        cache["failures"][normalized] = {
            "failed_at": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
            "error": error[:500],
        }
        return normalized, None, error
    bars = _normalise_price_history(history_result)
    if not bars:
        error = str(history_result.get("error") or "no_history")
        cache["failures"][normalized] = {
            "failed_at": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
            "error": error[:500],
        }
        return normalized, None, error
    snapshot = snapshot_result if isinstance(snapshot_result, dict) else {}
    latest = _snapshot_number(snapshot.get("last")) or bars[-1]["close"]
    fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    aliases = sorted({normalized, _contract_query(normalized), contract["symbol"]})
    instrument = {
        "symbol": normalized,
        "aliases": aliases,
        "fetched_at": fetched_at,
        "data_provider": "IBKR MCP",
        "data_broker": "IBKR",
        "ibkr_data_only": normalized in {"TVBETETF", "TVBETETF.RO"},
        "contract": {
            "conId": contract["contract_id"],
            "exchange": contract.get("exchange"),
            "local_symbol": contract.get("symbol"),
            "long_name": contract.get("description") or contract.get("issuer"),
            "country_code": contract.get("country_code"),
        },
        "market_data": {
            "market_price": latest,
            "last": latest,
            "close": bars[-1]["close"],
            "prior_close": _snapshot_number(snapshot.get("prior-close")),
            "volume": _snapshot_number(snapshot.get("volume")),
            "delayed": history_result.get("delayed"),
        },
        "bars": bars,
    }
    cache["instruments"][normalized] = instrument
    cache["failures"].pop(normalized, None)
    return normalized, instrument, "updated"


async def _prefetch_market_data_async(
    symbols: list[str], concurrency: int,
    batch_size: int = MARKET_DATA_BATCH_SIZE,
) -> dict[str, Any]:
    cache = _read_market_cache()
    unique_symbols = sorted(set(
        _market_symbol(symbol) for symbol in symbols if str(symbol).strip()
    ))
    stats = {
        "requested": len(unique_symbols), "scheduled": 0, "deferred": 0,
        "cached": 0, "updated": 0, "unavailable": 0, "errors": {},
    }
    semaphore = asyncio.Semaphore(max(1, min(10, int(concurrency))))
    results = []
    pending_symbols = []
    for symbol in unique_symbols:
        existing = cache["instruments"].get(symbol)
        if isinstance(existing, dict) and _fresh_iso(
            existing.get("fetched_at"), MARKET_DATA_TTL_HOURS * 3600
        ):
            results.append((symbol, existing, "cached"))
            continue
        recent_failure = cache.get("failures", {}).get(symbol)
        if isinstance(recent_failure, dict) and _fresh_iso(
            recent_failure.get("failed_at"), MARKET_DATA_TTL_HOURS * 3600
        ):
            results.append((
                symbol, None,
                str(recent_failure.get("error") or "market_data_error_cached"),
            ))
            continue
        pending_symbols.append(symbol)
    selected_symbols = pending_symbols
    batch_size = max(1, int(batch_size))
    if len(pending_symbols) > batch_size:
        cursor = int(cache.get("rotation_cursor", 0)) % len(unique_symbols)
        rotated = unique_symbols[cursor:] + unique_symbols[:cursor]
        pending_set = set(pending_symbols)
        selected_symbols = [
            symbol for symbol in rotated if symbol in pending_set
        ][:batch_size]
        last_index = unique_symbols.index(selected_symbols[-1])
        cache["rotation_cursor"] = (last_index + 1) % len(unique_symbols)
        stats["deferred"] = len(pending_symbols) - len(selected_symbols)
    stats["scheduled"] = len(selected_symbols)
    if selected_symbols:
        print(
            f"  [IBKR MCP] Prefetch lot {len(selected_symbols)}/"
            f"{len(pending_symbols)} simboluri; "
            f"{stats['deferred']} rămân pentru rulările următoare."
        )
        async with ReadOnlyMCPSession() as session:
            async def fetch(symbol):
                async with semaphore:
                    try:
                        return await _fetch_market_instrument(session, symbol, cache)
                    except (Exception, asyncio.CancelledError) as exc:
                        return symbol, None, str(exc)
            tasks = [
                asyncio.create_task(fetch(symbol))
                for symbol in selected_symbols
            ]
            completed = 0
            for task in asyncio.as_completed(tasks):
                result = await task
                results.append(result)
                completed += 1
                if (
                    completed == 1
                    or completed % 10 == 0
                    or completed == len(tasks)
                ):
                    symbol, instrument, status = result
                    outcome = (
                        "actualizat"
                        if instrument and status == "updated"
                        else "indisponibil"
                    )
                    print(
                        f"  [IBKR MCP {completed}/{len(tasks)}] "
                        f"{symbol}: {outcome}"
                    )
    for symbol, instrument, status in results:
        if status == "cached":
            stats["cached"] += 1
        elif status == "updated" and instrument:
            stats["updated"] += 1
        else:
            stats["unavailable"] += 1
            stats["errors"][symbol] = str(status or "indisponibil")[:240]
    _write_market_cache(cache)
    return stats


def prefetch_market_data(
    symbols: list[str], *, concurrency: int = MARKET_DATA_CONCURRENCY,
    batch_size: int = MARKET_DATA_BATCH_SIZE,
) -> dict[str, Any]:
    """Prefetch local OHLCV + snapshot, fără autentificare interactivă."""
    if not symbols:
        return {"requested": 0, "scheduled": 0, "deferred": 0,
                "cached": 0, "updated": 0, "unavailable": 0,
                "errors": {}}
    return asyncio.run(
        _prefetch_market_data_async(symbols, concurrency, batch_size)
    )


def _number(value: Any, default: float = 0.0) -> float:
    try:
        number = float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return default
    return number if abs(number) < 1e100 else default


def _normalise_positions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in payload.get("positions", []):
        shares = _number(item.get("position"))
        symbol = str(item.get("contract_description", "")).strip()
        if not symbol or shares == 0:
            continue
        rows.append({
            "Symbol": symbol.replace(" ", "."),
            "Shares": shares,
            "Buy_Price": _number(item.get("average_price")),
            "Current_Price": _number(item.get("market_price")),
            "Currency": str(item.get("currency", "")).upper() or "USD",
        })
    return rows


def _order_symbol(item: dict[str, Any]) -> str:
    description = str(item.get("primary_description", "")).strip()
    match = re.search(
        r"^(?:Buy|Sell)\s+[\d,.]+\s+(.+)$", description, re.IGNORECASE
    )
    return (match.group(1) if match else description).strip().replace(" ", ".")


def _normalise_orders(payload: dict[str, Any]) -> list[dict[str, Any]]:
    type_map = {
        "LIMIT": "LMT",
        "STOP": "STP",
        "STOP_LIMIT": "STP LMT",
        "TRAILING_STOP": "TRAIL",
    }
    rows = []
    for item in payload.get("orders", []):
        symbol = _order_symbol(item)
        if not symbol:
            continue
        raw_type = str(item.get("order_type", "")).upper()
        order_type = type_map.get(raw_type, raw_type)
        details = str(item.get("secondary_description", ""))
        limit_price = _number(item.get("limit_price"))
        trail_match = re.search(
            r"TRAIL\s+([\d.]+)(?:\s+STP\s+([\d.]+))?",
            details,
            re.IGNORECASE,
        )
        stop_match = re.search(
            r"(?:STP|STOP)\s+([\d.]+)", details, re.IGNORECASE
        )
        trail_pct = _number(trail_match.group(1)) if trail_match else 0.0
        stop_price = 0.0
        if trail_match and trail_match.group(2):
            stop_price = _number(trail_match.group(2))
        elif stop_match:
            stop_price = _number(stop_match.group(1))
        rows.append({
            "Symbol": symbol,
            "OrderType": order_type,
            "Action": str(item.get("side", "")).upper(),
            "Total_Qty": _number(item.get("total_shares_qty")),
            "Aux_Price": stop_price if order_type in {"STP", "STP LMT"} else 0.0,
            "Limit_Price": limit_price,
            "Stop_Price": stop_price,
            "Trail_Pct": trail_pct,
            "Calculated_Stop": stop_price,
        })
    return rows


def _normalise_nav_history(
    payload: dict[str, Any], base_currency: str
) -> tuple[str, list[dict[str, Any]]]:
    accounts = payload.get("accounts", {})
    if not isinstance(accounts, dict) or not accounts:
        return "IBKR", []
    account_id, account = next(iter(accounts.items()))
    account = account if isinstance(account, dict) else {}
    periods = account.get("periods", {})
    for period_name in ("1Y", "YTD", "1M", "7D", "1D"):
        period = periods.get(period_name, {}) if isinstance(periods, dict) else {}
        dates = period.get("dates", []) if isinstance(period, dict) else []
        values = period.get("nav", []) if isinstance(period, dict) else []
        points = [
            {
                "date": _normalise_history_date(date),
                "nav": round(_number(nav), 2),
                "currency": str(
                    account.get("base_currency", base_currency)
                ).upper(),
            }
            for date, nav in zip(dates, values)
            if str(date).strip() and _number(nav) > 0
        ]
        if points:
            return str(account_id), points[-366:]
    return str(account_id), []


def _normalise_history_date(value: Any) -> str:
    """Returnează o dată IBKR fără ghilimelele incluse în payload."""
    raw = str(value).strip().strip("'\"").strip()
    if re.fullmatch(r"\d{8}\.0+", raw):
        return raw[:8]
    return raw


async def _call_with_retry(
    name: str, *, required: bool = True, attempts: int = 2,
    interactive: bool = False,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return await call_tool(name, interactive=interactive)
        except IBKRMCPAuthorizationRequired:
            raise
        except Exception as exc:
            last_error = exc
            if attempt + 1 < attempts:
                await asyncio.sleep(1)
    if required:
        raise IBKRMCPError(f"IBKR MCP {name} indisponibil: {last_error}")
    print(f"  -> IBKR MCP {name} indisponibil; continuăm fără el.")
    return {}


async def build_account_snapshot(*, interactive: bool = False) -> dict[str, Any]:
    """Read the authorised account without exposing any mutation tools."""
    summary = await _call_with_retry(
        "get_account_summary", interactive=interactive
    )
    positions = await _call_with_retry(
        "get_account_positions", interactive=interactive
    )
    orders = await _call_with_retry(
        "get_account_orders", interactive=interactive
    )
    balances = await _call_with_retry(
        "get_account_balances", required=False, attempts=2,
        interactive=interactive,
    )
    performance = await _call_with_retry(
        "get_pa_performance_all_periods", required=False, attempts=1,
        interactive=interactive,
    )

    base_currency = str(summary.get("currency", "EUR")).upper() or "EUR"
    account_id, nav_history = _normalise_nav_history(
        performance, base_currency
    )
    try:
        import ibkr_flex_history
        previous = ibkr_flex_history.load_existing_snapshot()
    except Exception:
        previous = {}
    if not nav_history:
        nav_history = list(previous.get("nav_history", []))[-366:]
    cash_history = list(previous.get("cash_history", []))[-366:]
    cash_by_currency = {
        str(item.get("currency", "")).upper(): _number(
            item.get("cash_balance")
        )
        for item in balances.get("balances", [])
        if str(item.get("currency", "")).strip()
    }
    if not cash_by_currency:
        cash_by_currency[base_currency] = _number(
            summary.get("total_cash_value")
        )

    summary_map = {
        "NetLiquidation": _number(summary.get("net_liquidation")),
        "EquityWithLoanValue": _number(
            summary.get("equity_with_loan_value")
        ),
        "TotalCashValue": _number(summary.get("total_cash_value")),
        "AvailableFunds": _number(summary.get("available_funds")),
        "BuyingPower": _number(summary.get("buying_power")),
        "ExcessLiquidity": _number(summary.get("excess_liquidity")),
        "InitMarginReq": _number(summary.get("initial_margin")),
        "MaintMarginReq": _number(summary.get("maintenance_margin")),
        "GrossPositionValue": _number(summary.get("gross_position_value")),
    }
    nav = summary_map["NetLiquidation"]
    summary_map["Cushion"] = (
        summary_map["ExcessLiquidity"] / nav if nav > 0 else 0.0
    )
    return {
        "fetched_at": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(),
        "source": "IBKR MCP (read-only)",
        "accounts": [{
            "account_id": account_id,
            "label": "IBKR",
            "source": "IBKR MCP (read-only)",
            "base_currency": base_currency,
            "summary": summary_map,
            "cash_by_currency": cash_by_currency,
        }],
        "positions": positions.get("positions", []),
        "nav_history": nav_history,
        "cash_history": cash_history,
        "_position_rows": _normalise_positions(positions),
        "_order_rows": _normalise_orders(orders),
    }


def sync_account_snapshot(
    password: str | None = None, *, interactive: bool = False,
) -> dict[str, Any]:
    """Persist MCP account, position and order snapshots for the dashboard."""
    payload = asyncio.run(build_account_snapshot(interactive=interactive))
    position_rows = payload.pop("_position_rows")
    order_rows = payload.pop("_order_rows")

    import pandas as pd
    import ibkr_web_api

    pd.DataFrame(
        position_rows,
        columns=[
            "Symbol", "Shares", "Buy_Price", "Current_Price", "Currency",
        ],
    ).to_csv("tws_positions.csv", index=False)
    pd.DataFrame(
        order_rows,
        columns=[
            "Symbol", "OrderType", "Action", "Total_Qty", "Aux_Price",
            "Limit_Price", "Stop_Price", "Trail_Pct", "Calculated_Stop",
        ],
    ).to_csv("tws_orders.csv", index=False)
    ibkr_web_api.persist_account_snapshot(payload, password=password)
    return payload


async def _run_cli(args: argparse.Namespace) -> int:
    if args.command == "prefetch":
        if not args.symbols:
            raise IBKRMCPError(
                "Adaugă cel puțin un simbol după comanda prefetch."
            )
        stats = await _prefetch_market_data_async(
            args.symbols, MARKET_DATA_CONCURRENCY, MARKET_DATA_BATCH_SIZE
        )
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0
    tools = await list_tools(interactive=True)
    if args.json:
        print(json.dumps(tools, ensure_ascii=False, indent=2))
    else:
        print(f"IBKR MCP conectat read-only: {len(tools)} instrumente.")
        for tool in tools:
            print(f"  - {tool.get('name')}: {tool.get('description', '')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Autorizare și diagnostic pentru IBKR MCP read-only"
    )
    parser.add_argument(
        "command", nargs="?",
        choices=["login", "tools", "prefetch"], default="tools",
    )
    parser.add_argument("symbols", nargs="*")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        return asyncio.run(_run_cli(args))
    except (IBKRMCPError, OSError, TimeoutError) as exc:
        print(f"IBKR MCP indisponibil: {exc}")
        return 1
    except Exception as exc:
        print(f"IBKR MCP indisponibil: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
