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
from zoneinfo import ZoneInfo


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
MARKET_CACHE_VERSION = 2
CONTRACT_RESOLVER_VERSION = 2
MARKET_DATA_TTL_HOURS = float(
    os.environ.get("IBKR_MCP_MARKET_TTL_HOURS", "1")
)
HISTORY_FULL_REFRESH_DAYS = max(
    1, int(os.environ.get("IBKR_MCP_HISTORY_FULL_REFRESH_DAYS", "7"))
)
HISTORY_MAX_BARS = max(
    220, int(os.environ.get("IBKR_MCP_HISTORY_MAX_BARS", "280"))
)
CONTRACT_CACHE_TTL_DAYS = float(
    os.environ.get("IBKR_MCP_CONTRACT_TTL_DAYS", "30")
)
MARKET_DATA_CONCURRENCY = max(
    1, min(10, int(os.environ.get("IBKR_MCP_MARKET_CONCURRENCY", "2")))
)
TRANSIENT_FAILURE_TTL_SECONDS = max(
    30, int(os.environ.get("IBKR_MCP_TRANSIENT_FAILURE_TTL_SECONDS", "120"))
)
MCP_CALL_ATTEMPTS = max(
    1, min(5, int(os.environ.get("IBKR_MCP_CALL_ATTEMPTS", "3")))
)
MARKET_DATA_BATCH_SIZE = max(
    1, int(os.environ.get("IBKR_MCP_MARKET_BATCH", "70"))
)
RESEARCH_TTL_HOURS = float(os.environ.get("IBKR_MCP_RESEARCH_TTL_HOURS", "168"))
OPTIONS_TTL_HOURS = float(os.environ.get("IBKR_MCP_OPTIONS_TTL_HOURS", "6"))
RESEARCH_BATCH_SIZE = max(1, int(os.environ.get("IBKR_MCP_RESEARCH_BATCH", "8")))
OPTIONS_BATCH_SIZE = max(0, int(os.environ.get("IBKR_MCP_OPTIONS_BATCH", "3")))
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
    "get_company_connections",
    "get_company_themes",
    "get_option_data",
    "get_option_parameters",
    "search_contracts",
    "search_investment_topics",
    "get_theme_details",
}

# A single snapshot request is cheaper than multiple per-field calls.  The
# groups document which consumer owns each value and keep display-only fields
# out of the decision logic unless explicitly promoted later.
SNAPSHOT_FIELD_GROUPS = {
    "quote": (
        "last", "bid_ask", "top_status", "prior_close", "volume",
        "open", "low", "high",
    ),
    "ranking": (
        "avg_90d_usd_volume", "year_to_date_change",
        "cumulative_perf_1d", "cumulative_perf_1w",
        "cumulative_perf_1m", "cumulative_perf_ytd",
        "cumulative_perf_1y",
    ),
    "risk": (
        "implied_volatility_percentile", "implied_vol_underlying",
        "historical_vol", "misc_statistics",
    ),
    "display": ("dividend_yield",),
}
SNAPSHOT_FIELDS = tuple(dict.fromkeys(
    field
    for fields in SNAPSHOT_FIELD_GROUPS.values()
    for field in fields
))


class IBKRMCPError(RuntimeError):
    """Raised when the official IBKR MCP source cannot be used."""


class IBKRMCPAuthorizationRequired(IBKRMCPError):
    """Raised when IBKR requires a new interactive OAuth authorisation."""


def _is_transient_mcp_error(error: Any) -> bool:
    """Distinguish retryable IBKR/service failures from permanent data gaps."""
    message = str(error or "").casefold()
    permanent_markers = (
        "no market data permissions",
        "contract_not_found",
        "not permitted",
        "permission denied",
        "invalid contract",
    )
    if any(marker in message for marker in permanent_markers):
        return False
    transient_markers = (
        "-32400",
        "try again later",
        "temporarily",
        "timeout",
        "timed out",
        "connection",
        "stream",
        "rate limit",
        "too many requests",
        "http 408",
        "http 409",
        "http 425",
        "http 429",
        "http 500",
        "http 502",
        "http 503",
        "http 504",
    )
    return any(marker in message for marker in transient_markers)


def _failure_ttl_seconds(failure: dict[str, Any]) -> float:
    transient = failure.get("transient")
    if transient is None:
        transient = _is_transient_mcp_error(failure.get("error"))
    if transient:
        return float(TRANSIENT_FAILURE_TTL_SECONDS)
    return MARKET_DATA_TTL_HOURS * 3600


def _market_failure(error: Any) -> dict[str, Any]:
    message = str(error or "market_data_error")
    return {
        "failed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "error": message[:500],
        "transient": _is_transient_mcp_error(message),
    }


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
            raw_environment = os.environ.get("IBKR_MCP_CREDENTIALS_JSON", "")
            if not raw_environment.strip():
                return {}
            try:
                payload = json.loads(raw_environment)
            except (TypeError, ValueError) as exc:
                raise IBKRMCPError(
                    "IBKR_MCP_CREDENTIALS_JSON nu conține JSON valid."
                ) from exc
            return payload if isinstance(payload, dict) else {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise IBKRMCPError(
                f"Credentialele MCP IBKR sunt invalide: {self.path}"
            ) from exc

    def _write(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f".{self.path.name}.{os.getpid()}.tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.chmod(stat.S_IRUSR | stat.S_IWUSR)
        os.replace(temporary, self.path)

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
        for attempt in range(MCP_CALL_ATTEMPTS):
            try:
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
            except Exception:
                response = None
            if response is not None and response.status_code == 200:
                return await self._store_token(response.json(), previous=token)
            status = getattr(response, "status_code", 0)
            if status and status not in {408, 409, 425, 429} and status < 500:
                return None
            if attempt + 1 < MCP_CALL_ATTEMPTS:
                await asyncio.sleep(0.5 * (2 ** attempt))
        return None

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

    def __init__(self, *, interactive: bool = False):
        self.interactive = interactive
        self.sdk: dict[str, Any] | None = None
        self.http_client = None
        self.stream_context = None
        self.session_context = None
        self.session = None

    async def __aenter__(self):
        try:
            self.sdk = _load_sdk()
            token = await ReadOnlyOAuthClient(FileTokenStorage()).access_token(
                interactive=self.interactive
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
        last_error: Exception | None = None
        for attempt in range(MCP_CALL_ATTEMPTS):
            try:
                result = await self.session.call_tool(name, arguments or {})
                return _tool_result_json(result, name)
            except IBKRMCPAuthorizationRequired:
                raise
            except Exception as exc:
                last_error = exc
                if (
                    not _is_transient_mcp_error(exc)
                    or attempt + 1 >= MCP_CALL_ATTEMPTS
                ):
                    raise
                await asyncio.sleep(0.5 * (2 ** attempt))
        raise IBKRMCPError(f"Instrumentul IBKR {name} a eșuat: {last_error}")


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
    payload.setdefault("company_context", {})
    payload.setdefault("options_context", {})
    payload.setdefault("topic_discovery", {})
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


def _listing_identity_matches(
    symbol: str, country_code: Any, exchange: Any
) -> bool:
    """Match a provider listing without requiring IBKR's broad EU country tag."""
    expected_country = _expected_country(symbol)
    country = str(country_code or "").upper()
    venue = str(exchange or "").upper()
    if country == expected_country:
        return True
    # IBKR classifies some Romanian listings as EU although the exchange is
    # unambiguously BVB. This is venue metadata, not a ticker allow-list.
    return expected_country == "RO" and country in {"EU", ""} and venue == "BVB"


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
        if explicit_listing and not _listing_identity_matches(
            normalized_symbol,
            item.get("country_code"),
            item.get("exchange"),
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


def _snapshot_scalar(value: Any) -> float | None:
    """Extract a signed finite scalar from the heterogeneous snapshot shape."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float, str)):
        number = _number(value, default=float("nan"))
        return number if number == number else None
    if isinstance(value, dict):
        for key in (
            "value", "price", "last", "close", "mid", "annual_iv",
            "annual_pct", "iv", "percent", "percentage", "change",
            "change_pct", "volume", "yield_pct",
        ):
            if key in value:
                found = _snapshot_scalar(value[key])
                if found is not None:
                    return found
    return None


def _snapshot_key(payload: dict[str, Any], field: str) -> Any:
    """IBKR responds with hyphenated keys although requests use underscores."""
    return payload.get(field.replace("_", "-"), payload.get(field))


def _snapshot_bid_ask(value: Any) -> tuple[float | None, float | None]:
    if not isinstance(value, dict):
        return None, None
    bid = _snapshot_scalar(value.get("bid"))
    ask = _snapshot_scalar(value.get("ask"))
    if bid is None and isinstance(value.get("bid-price"), (dict, int, float, str)):
        bid = _snapshot_scalar(value.get("bid-price"))
    if ask is None and isinstance(value.get("ask-price"), (dict, int, float, str)):
        ask = _snapshot_scalar(value.get("ask-price"))
    return bid, ask


def _snapshot_status(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip().upper() or None
    if isinstance(value, dict):
        for key in ("status", "value", "top_status", "top-status"):
            status = value.get(key)
            if isinstance(status, str) and status.strip():
                return status.strip().upper()
    return None


def _snapshot_named_scalar(value: Any, *name_parts: str) -> float | None:
    """Find a scalar whose nested key contains one of the requested names."""
    if not isinstance(value, dict):
        return _snapshot_scalar(value)
    lowered = tuple(part.lower() for part in name_parts)
    for key, nested in value.items():
        normalized = str(key).lower().replace("_", "-")
        if any(part in normalized for part in lowered):
            found = _snapshot_scalar(nested)
            if found is not None:
                return found
    for nested in value.values():
        if isinstance(nested, dict):
            found = _snapshot_named_scalar(nested, *name_parts)
            if found is not None:
                return found
    return _snapshot_scalar(value)


def _normalise_snapshot_metrics(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Keep raw MCP evidence and stable scalar fields for scanner consumers."""
    raw = {
        field: _snapshot_key(snapshot, field)
        for field in SNAPSHOT_FIELDS
        if _snapshot_key(snapshot, field) is not None
    }
    bid, ask = _snapshot_bid_ask(raw.get("bid_ask"))
    midpoint = (bid + ask) / 2 if bid and ask and bid > 0 and ask > 0 else None
    spread_pct = (
        (ask - bid) / midpoint * 100
        if midpoint and ask >= bid else None
    )
    scalars = {
        field: _snapshot_scalar(raw.get(field))
        for field in SNAPSHOT_FIELDS
        if field not in {"bid_ask", "top_status", "misc_statistics"}
    }
    return {
        "groups": {
            group: [field for field in fields if field in raw]
            for group, fields in SNAPSHOT_FIELD_GROUPS.items()
        },
        "raw": raw,
        "scalars": {key: value for key, value in scalars.items() if value is not None},
        "bid": bid,
        "ask": ask,
        "midpoint": midpoint,
        "spread_pct": spread_pct,
        "top_status": _snapshot_status(raw.get("top_status")),
        "derived": {
            "iv_percentile_52w": _snapshot_named_scalar(
                raw.get("implied_volatility_percentile"), "52"
            ),
            "historical_vol": _snapshot_scalar(raw.get("historical_vol")),
            "implied_vol_underlying": _snapshot_scalar(
                raw.get("implied_vol_underlying")
            ),
        },
    }


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
        stale_negative = (
            cached.get("status") == "not_found"
            and cached.get("resolver_version") != CONTRACT_RESOLVER_VERSION
        )
        ttl_days = (
            1 if cached.get("status") == "not_found"
            else CONTRACT_CACHE_TTL_DAYS
        )
        if not stale_negative and _fresh_iso(
            cached.get("resolved_at"), ttl_days * 86400
        ):
            return cached if cached.get("contract_id") else None
    response = await session.call(
        "search_contracts", {"query": _contract_query(normalized)}
    )
    match = _select_contract(normalized, response)
    resolved_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if match is None:
        cache["contracts"][normalized] = {
            "status": "not_found", "resolved_at": resolved_at,
            "resolver_version": CONTRACT_RESOLVER_VERSION,
        }
        return None
    contract = {
        "status": "ok",
        "resolver_version": CONTRACT_RESOLVER_VERSION,
        "resolved_at": resolved_at,
        "contract_id": int(match["underlying_contract_id"]),
        "symbol": str(match.get("symbol") or _contract_query(normalized)),
        "exchange": str(match.get("exchange") or ""),
        "country_code": (
            _expected_country(normalized)
            if _listing_identity_matches(
                normalized, match.get("country_code"), match.get("exchange")
            )
            else str(match.get("country_code") or "")
        ),
        "description": str(match.get("description") or ""),
        "issuer": str(match.get("issuer") or ""),
        "currency": str(match.get("currency") or "").upper(),
        "security_type": (
            "STK"
            if any(
                str(section.get("security_type", "")).upper() == "STK"
                for section in match.get("sections", [])
                if isinstance(section, dict)
            )
            else "FUND"
        ),
        "sections": sorted({
            str(section.get("security_type", "")).upper()
            for section in match.get("sections", [])
            if isinstance(section, dict) and section.get("security_type")
        }),
    }
    cache["contracts"][normalized] = contract
    return contract


def get_cached_contract_metadata(symbol: str) -> dict[str, Any]:
    """Return immutable search_contracts metadata without opening MCP."""
    cache = _read_market_cache()
    value = cache.get("contracts", {}).get(_market_symbol(symbol))
    return dict(value) if isinstance(value, dict) and value.get("contract_id") else {}


def get_cached_contract_metadata_map(symbols) -> dict[str, dict[str, Any]]:
    """Load the private contract cache once for a scanner batch."""
    cache = _read_market_cache().get("contracts", {})
    result = {}
    for symbol in symbols or []:
        requested = str(symbol or "").strip().upper()
        normalized = _market_symbol(symbol)
        value = cache.get(normalized)
        if isinstance(value, dict) and value.get("contract_id"):
            result[normalized] = dict(value)
            if requested:
                result[requested] = dict(value)
    return result


async def _resolve_contract_metadata_async(symbols) -> dict[str, dict[str, Any]]:
    """Resolve missing canonical contracts through search_contracts."""
    cache = _read_market_cache()
    result: dict[str, dict[str, Any]] = {}
    async with ReadOnlyMCPSession() as session:
        for raw_symbol in symbols or []:
            requested = str(raw_symbol or "").strip().upper()
            if not requested:
                continue
            contract = await _resolve_market_contract(
                session, requested, cache
            )
            if contract:
                result[requested] = dict(contract)
                result[_market_symbol(requested)] = dict(contract)
    _write_market_cache(cache)
    return result


def resolve_contract_metadata(symbols) -> dict[str, dict[str, Any]]:
    """Public, cached search_contracts fallback for a bounded symbol batch."""
    requested = [str(value or "").strip().upper() for value in symbols or []]
    cached = get_cached_contract_metadata_map(requested)
    missing = [value for value in requested if value and value not in cached]
    if missing:
        cached.update(asyncio.run(_resolve_contract_metadata_async(missing)))
    return cached


def runtime_enabled() -> bool:
    """True only when MCP use is explicitly usable in this environment."""
    configured = os.environ.get("IBKR_MCP_RESEARCH_ENABLED", "1").lower()
    if configured in {"0", "false", "no", "off"}:
        return False
    if os.environ.get("GITHUB_ACTIONS") == "true":
        opt_in = os.environ.get("IBKR_MCP_GITHUB_ACTIONS_ENABLED", "0").lower()
        if opt_in not in {"1", "true", "yes", "on"}:
            return False
        return bool(
            os.environ.get("IBKR_MCP_CREDENTIALS_JSON", "").strip()
            or CREDENTIALS_FILE.exists()
        )
    return True


def _previous_weekday(value: datetime.date) -> datetime.date:
    value -= datetime.timedelta(days=1)
    while value.weekday() >= 5:
        value -= datetime.timedelta(days=1)
    return value


def _latest_completed_session_date(
    symbol: str, now: datetime.datetime | None = None
) -> str:
    """Return the latest likely completed daily session for a listing.

    Exchange holidays are handled naturally after the first successful check:
    the requested session key is persisted even if IBKR returns no newer bar.
    """
    normalized = _market_symbol(symbol)
    venue_rules = (
        (".RO", "Europe/Bucharest", (18, 15)),
        (".PA", "Europe/Paris", (17, 45)),
        (".DE", "Europe/Berlin", (17, 45)),
        (".AS", "Europe/Amsterdam", (17, 45)),
        (".L", "Europe/London", (16, 45)),
        (".MI", "Europe/Rome", (17, 45)),
        (".MC", "Europe/Madrid", (17, 45)),
    )
    timezone_name, close_time = "America/New_York", (16, 15)
    for suffix, candidate_timezone, candidate_close in venue_rules:
        if normalized.endswith(suffix):
            timezone_name, close_time = candidate_timezone, candidate_close
            break
    current = now or datetime.datetime.now(datetime.timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=datetime.timezone.utc)
    local = current.astimezone(ZoneInfo(timezone_name))
    session = local.date()
    if session.weekday() >= 5:
        while session.weekday() >= 5:
            session = _previous_weekday(session)
    elif (local.hour, local.minute) < close_time:
        session = _previous_weekday(session)
    return session.isoformat()


def _bar_session_date(bar: dict[str, Any]) -> str:
    raw = str(bar.get("date") or "")
    return raw[:10] if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", raw) else raw


def _merge_price_bars(
    existing: list[dict[str, Any]], incoming: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Merge overlapping daily windows and keep a bounded indicator history."""
    by_session: dict[str, dict[str, Any]] = {}
    for bar in [*(existing or []), *(incoming or [])]:
        if not isinstance(bar, dict):
            continue
        key = _bar_session_date(bar)
        if key:
            by_session[key] = bar
    return [by_session[key] for key in sorted(by_session)][-HISTORY_MAX_BARS:]


def _history_refresh_plan(
    symbol: str,
    existing: dict[str, Any] | None,
    now: datetime.datetime | None = None,
) -> tuple[bool, bool, str]:
    """Return (refresh_needed, full_refresh, completed_session_key)."""
    current = now or datetime.datetime.now(datetime.timezone.utc)
    instrument = existing if isinstance(existing, dict) else {}
    bars = instrument.get("bars") if isinstance(instrument.get("bars"), list) else []
    session_key = _latest_completed_session_date(symbol, current)
    if not bars:
        return True, True, session_key
    latest_bar = _bar_session_date(bars[-1])
    already_checked = str(instrument.get("history_checked_session") or "")
    if latest_bar >= session_key or already_checked == session_key:
        return False, False, session_key
    full_at = (
        instrument.get("full_history_fetched_at")
        or instrument.get("history_fetched_at")
        or instrument.get("fetched_at")
    )
    full_due = not _fresh_iso(
        full_at, HISTORY_FULL_REFRESH_DAYS * 86400
    )
    return True, full_due, session_key


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
        existing["last_run_history_mode"] = "cache"
        return normalized, existing, "cached"
    recent_failure = cache.get("failures", {}).get(normalized)
    if isinstance(recent_failure, dict) and _fresh_iso(
        recent_failure.get("failed_at"), _failure_ttl_seconds(recent_failure)
    ):
        if isinstance(existing, dict) and existing.get("bars"):
            existing["last_run_history_mode"] = "cache"
            return normalized, existing, "cached"
        return normalized, None, str(
            recent_failure.get("error") or "market_data_error_cached"
        )
    contract = await _resolve_market_contract(session, normalized, cache)
    if not contract:
        return normalized, None, "contract_not_found"
    now = datetime.datetime.now(datetime.timezone.utc)
    fetched_at = now.isoformat()
    history_needed, full_refresh, session_key = _history_refresh_plan(
        normalized, existing, now
    )
    existing_bars = (
        list(existing.get("bars") or []) if isinstance(existing, dict) else []
    )
    history_arguments = {
        "contract_id": contract["contract_id"],
        "security_type": contract.get("security_type", "STK"),
        "period": "ONE_YEAR" if full_refresh else "ONE_MONTH",
        "step": "ONE_DAY",
        "outside_rth": False,
        "include_corporate_actions": True,
    }
    # contract_id is globally unique. Supplying the listing venue as well can
    # make IBKR reject an otherwise authorised contract (for example LQQ on
    # SBF), so history and quotes are intentionally conId-only.
    snapshot_task = session.call(
        "get_price_snapshot",
        {
            "contract_id": contract["contract_id"],
            "market_data_names": list(SNAPSHOT_FIELDS),
        },
    )
    if history_needed:
        history_result, snapshot_result = await asyncio.gather(
            session.call("get_price_history", history_arguments),
            snapshot_task,
            return_exceptions=True,
        )
    else:
        history_result = None
        snapshot_result = (
            await asyncio.gather(snapshot_task, return_exceptions=True)
        )[0]

    history_error = None
    history_updated = False
    if history_needed and isinstance(history_result, Exception):
        history_error = str(history_result)
        incoming_bars = []
    elif history_needed:
        incoming_bars = _normalise_price_history(history_result)
        if not incoming_bars:
            history_error = str(history_result.get("error") or "no_history")
    else:
        incoming_bars = []
    if history_needed and incoming_bars:
        bars = (
            incoming_bars[-HISTORY_MAX_BARS:]
            if full_refresh
            else _merge_price_bars(existing_bars, incoming_bars)
        )
        history_updated = True
    else:
        bars = existing_bars
    if not bars:
        error = history_error or "no_history"
        cache["failures"][normalized] = _market_failure(error)
        return normalized, None, error

    snapshot = snapshot_result if isinstance(snapshot_result, dict) else {}
    snapshot_metrics = _normalise_snapshot_metrics(snapshot)
    latest = _snapshot_number(snapshot.get("last")) or bars[-1]["close"]
    aliases = sorted({normalized, _contract_query(normalized), contract["symbol"]})
    previous_market = (
        dict(existing.get("market_data") or {})
        if isinstance(existing, dict) else {}
    )
    previous_quote = dict(previous_market.get("quote") or {})
    quote_observed = bool(snapshot) and not snapshot.get("error")
    quote = {
        "bid": snapshot_metrics.get("bid"),
        "ask": snapshot_metrics.get("ask"),
        "midpoint": snapshot_metrics.get("midpoint"),
        "spread_pct": snapshot_metrics.get("spread_pct"),
        "top_status": snapshot_metrics.get("top_status"),
    } if quote_observed else previous_quote
    history_fetched_at = (
        fetched_at if history_updated
        else (existing or {}).get("history_fetched_at")
        or (existing or {}).get("fetched_at")
    )
    instrument = {
        "symbol": normalized,
        "aliases": aliases,
        "fetched_at": (
            fetched_at if quote_observed or history_updated
            else (existing or {}).get("fetched_at") or fetched_at
        ),
        "quote_fetched_at": (
            fetched_at if quote_observed
            else (existing or {}).get("quote_fetched_at")
        ),
        "history_fetched_at": history_fetched_at,
        "history_checked_session": (
            session_key if history_updated
            else (existing or {}).get("history_checked_session")
        ),
        "full_history_fetched_at": (
            fetched_at if history_updated and full_refresh
            else (existing or {}).get("full_history_fetched_at")
            or (existing or {}).get("history_fetched_at")
            or (existing or {}).get("fetched_at")
        ),
        "history_refresh_mode": (
            "full" if history_updated and full_refresh
            else "incremental" if history_updated
            else "cache"
        ),
        "last_run_history_mode": (
            "full" if history_updated and full_refresh
            else "incremental" if history_updated
            else "cache"
        ),
        "history_refresh_error": history_error,
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
            "prior_close": (
                _snapshot_number(snapshot.get("prior-close"))
                or previous_market.get("prior_close")
            ),
            "volume": (
                _snapshot_number(snapshot.get("volume"))
                or previous_market.get("volume")
            ),
            "delayed": (
                history_result.get("delayed")
                if isinstance(history_result, dict)
                else previous_market.get("delayed")
            ),
            "quote": quote,
            "snapshot_metrics": (
                snapshot_metrics if quote_observed
                else previous_market.get("snapshot_metrics", {})
            ),
        },
        "bars": bars,
    }
    cache["instruments"][normalized] = instrument
    cache["failures"].pop(normalized, None)
    return normalized, instrument, (
        "updated" if quote_observed or history_updated else "cached"
    )


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
            existing["last_run_history_mode"] = "cache"
            results.append((symbol, existing, "cached"))
            continue
        recent_failure = cache.get("failures", {}).get(symbol)
        if isinstance(recent_failure, dict) and _fresh_iso(
            recent_failure.get("failed_at"),
            _failure_ttl_seconds(recent_failure),
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


def _nested_named_items(value: Any, names: set[str]) -> list[dict[str, Any]]:
    rows = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in names and isinstance(nested, list):
                rows.extend(item for item in nested if isinstance(item, dict))
            if isinstance(nested, (dict, list)):
                rows.extend(_nested_named_items(nested, names))
    elif isinstance(value, list):
        for nested in value:
            if isinstance(nested, (dict, list)):
                rows.extend(_nested_named_items(nested, names))
    return rows


async def _fetch_company_context(session, symbol, cache, contract):
    existing = cache["company_context"].get(symbol)
    if isinstance(existing, dict) and _fresh_iso(
        existing.get("fetched_at"), RESEARCH_TTL_HOURS * 3600
    ):
        return existing
    themes_result, connections_result = await asyncio.gather(
        session.call("get_company_themes", {
            "contract_id": contract["contract_id"],
            "max_themes": 5,
            "max_companies": 5,
        }),
        session.call("get_company_connections", {
            "contract_id": contract["contract_id"],
            "max": 20,
        }),
        return_exceptions=True,
    )
    themes = themes_result if isinstance(themes_result, dict) else {}
    connections = connections_result if isinstance(connections_result, dict) else {}
    linked_themes = themes.get("linked_themes", [])
    if not isinstance(linked_themes, list):
        linked_themes = []
    peers = _nested_named_items(themes, {"companies", "peers", "linked_companies"})
    context = {
        "available": bool(themes or connections),
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "theme_count": len(linked_themes),
        "peer_count": len(peers),
        "peer_rank": 1 if peers else None,
        "themes": linked_themes,
        "connections": connections.get("groups", []),
        "source": "IBKR MCP company research",
    }
    cache["company_context"][symbol] = context
    return context


def _expiration_sort_key(item):
    raw = str(item.get("date") or "")
    try:
        parsed = datetime.datetime.strptime(raw, "%Y%m%d").date()
    except ValueError:
        parsed = datetime.date.max
    days = (parsed - datetime.date.today()).days
    preferred = 0 if 21 <= days <= 75 else 1
    regular = 0 if item.get("regular") else 1
    return preferred, regular, abs(days - 45), parsed


def _annotate_options_quality(context):
    """Classify cached and fresh chains without treating quotes as analytics."""
    details = [
        item for item in (context.get("contracts") or [])
        if isinstance(item, dict)
    ]
    count = len(details)
    fields = {
        "quote_coverage_ratio": (
            sum(bool(item.get("bid") and item.get("ask")) for item in details) / count
            if count else 0
        ),
        "volume_coverage_ratio": (
            sum(item.get("volume") is not None for item in details) / count
            if count else 0
        ),
        "open_interest_coverage_ratio": (
            sum(item.get("open_interest") is not None for item in details) / count
            if count else 0
        ),
        "contract_iv_coverage_ratio": (
            sum(item.get("iv") is not None for item in details) / count
            if count else 0
        ),
    }
    analytics = (
        fields["volume_coverage_ratio"],
        fields["open_interest_coverage_ratio"],
        fields["contract_iv_coverage_ratio"],
    )
    chain_contracts_count = int(context.get("chain_contracts_count") or 0)
    if not details and chain_contracts_count > 0:
        quality = "contracts_only"
    elif not details:
        quality = "unavailable"
    elif all(value >= 0.5 for value in analytics):
        quality = "complete"
    elif any(value > 0 for value in analytics):
        quality = "partial"
    elif fields["quote_coverage_ratio"] > 0:
        quality = "quote_only"
    else:
        quality = "contracts_only"
    context.update(fields)
    context["data_quality"] = quality
    context["analytics_available"] = quality in {"complete", "partial"}
    return context


async def _fetch_options_context(session, symbol, cache, contract, spot):
    existing = cache["options_context"].get(symbol)
    if isinstance(existing, dict) and _fresh_iso(
        existing.get("fetched_at"), OPTIONS_TTL_HOURS * 3600
    ):
        return _annotate_options_quality(existing)
    if "OPT" not in set(contract.get("sections", [])) or not spot or spot <= 0:
        context = {
            "available": False,
            "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "reason": "option chain unavailable",
        }
        cache["options_context"][symbol] = context
        return context
    parameters = await session.call("get_option_parameters", {
        "underlying_contract_id": contract["contract_id"],
        "option_sec_type": "OPT",
    })
    expirations = parameters.get("expirations", [])
    expirations = [item for item in expirations if isinstance(item, dict)]
    if not expirations:
        return {"available": False, "reason": "no expirations"}
    expiration = sorted(expirations, key=_expiration_sort_key)[0]
    chain = await session.call("get_option_data", {
        "expiration_id": expiration["id"],
        "min_strike": round(spot * 0.85, 4),
        "max_strike": round(spot * 1.15, 4),
    })
    rows = chain.get("contracts", [])
    rows = [item for item in rows if isinstance(item, dict)]
    rows.sort(key=lambda item: abs(_number(item.get("strike")) - spot))
    selected = rows[:5]
    exchange = str(chain.get("exchange") or parameters.get("current_exchange") or "SMART")
    requests = []
    labels = []
    for row in selected:
        for side in ("call", "put"):
            contract_id = row.get(f"{side}_contract_id")
            if not contract_id:
                continue
            labels.append((side, _number(row.get("strike"))))
            requests.append(session.call("get_price_snapshot", {
                "contract_id": int(contract_id),
                "exchange": exchange,
                "market_data_names": [
                    "bid_ask", "option_volume", "option_open_interest",
                    "option_midpoint_iv", "top_status",
                ],
            }))
    snapshots = await asyncio.gather(*requests, return_exceptions=True)
    snapshot_errors = [
        str(payload)[:500] for payload in snapshots
        if isinstance(payload, BaseException)
    ]
    details = []
    for (side, strike), payload in zip(labels, snapshots):
        if not isinstance(payload, dict):
            continue
        bid, ask = _snapshot_bid_ask(_snapshot_key(payload, "bid_ask"))
        midpoint = (bid + ask) / 2 if bid and ask else None
        spread = (ask - bid) / midpoint * 100 if midpoint and ask >= bid else None
        details.append({
            "side": side,
            "strike": strike,
            "bid": bid,
            "ask": ask,
            "spread_pct": spread,
            "volume": _snapshot_scalar(_snapshot_key(payload, "option_volume")),
            "open_interest": _snapshot_scalar(
                _snapshot_key(payload, "option_open_interest")
            ),
            "iv": _snapshot_scalar(_snapshot_key(payload, "option_midpoint_iv")),
            "quote_status": _snapshot_status(_snapshot_key(payload, "top_status")),
        })
    calls = [item for item in details if item["side"] == "call"]
    puts = [item for item in details if item["side"] == "put"]
    call_volume = sum(item["volume"] or 0 for item in calls)
    put_volume = sum(item["volume"] or 0 for item in puts)
    call_oi = sum(item["open_interest"] or 0 for item in calls)
    put_oi = sum(item["open_interest"] or 0 for item in puts)
    spreads = [item["spread_pct"] for item in details if item["spread_pct"] is not None]
    quoted = [item for item in details if item["bid"] and item["ask"]]
    context = {
        "available": bool(details),
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "expiration": expiration.get("date"),
        "expirations": [item.get("date") for item in expirations if item.get("date")],
        "exchange": exchange,
        "contracts_sampled": len(details),
        "chain_contracts_count": len(rows),
        "chain_contracts_sampled": selected,
        "snapshot_error_count": len(snapshot_errors),
        "snapshot_errors": snapshot_errors[:3],
        "quoted_contract_ratio": len(quoted) / len(details) if details else 0,
        "average_spread_pct": sum(spreads) / len(spreads) if spreads else None,
        "put_call_volume_ratio": put_volume / call_volume if call_volume > 0 else None,
        "put_call_open_interest_ratio": put_oi / call_oi if call_oi > 0 else None,
        "contracts": details,
        "source": "IBKR MCP option chain snapshots",
    }
    _annotate_options_quality(context)
    cache["options_context"][symbol] = context
    return context


async def _prefetch_candidate_context_async(candidates):
    cache = _read_market_cache()
    normalized = []
    for item in candidates or []:
        if isinstance(item, dict):
            symbol = _market_symbol(item.get("symbol"))
            spot = _number(item.get("price"))
        else:
            symbol = _market_symbol(item)
            spot = 0
        if symbol and symbol not in {entry[0] for entry in normalized}:
            normalized.append((symbol, spot))
    research = normalized[:RESEARCH_BATCH_SIZE]
    options_symbols = normalized[:OPTIONS_BATCH_SIZE]
    async with ReadOnlyMCPSession() as session:
        for symbol, spot in research:
            contract = await _resolve_market_contract(session, symbol, cache)
            if not contract:
                continue
            try:
                await _fetch_company_context(session, symbol, cache, contract)
            except Exception as exc:
                cache["failures"][f"research:{symbol}"] = {
                    "failed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "error": str(exc)[:500],
                }
            if (symbol, spot) in options_symbols:
                try:
                    await _fetch_options_context(session, symbol, cache, contract, spot)
                except Exception as exc:
                    cache["failures"][f"options:{symbol}"] = {
                        "failed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "error": str(exc)[:500],
                    }
    _write_market_cache(cache)
    return {
        symbol: {
            "company_context": cache["company_context"].get(symbol, {}),
            "options_context": cache["options_context"].get(symbol, {}),
            "instrument_metadata": dict(cache["contracts"].get(symbol, {})),
        }
        for symbol, _spot in normalized
    }


def prefetch_candidate_context(candidates):
    """Lazy research for already-ranked candidates, never the full universe."""
    if not candidates:
        return {}
    return asyncio.run(_prefetch_candidate_context_async(candidates))


async def _discover_topic_candidates_async(queries):
    cache = _read_market_cache()
    cached = cache.get("topic_discovery", {})
    if isinstance(cached, dict) and _fresh_iso(
        cached.get("fetched_at"), RESEARCH_TTL_HOURS * 3600
    ):
        return cached
    discovered = []
    async with ReadOnlyMCPSession() as session:
        for query in queries:
            search = await session.call(
                "search_investment_topics", {"query": query, "max": 3}
            )
            themes = search.get("themes", [])
            if not themes:
                continue
            theme = themes[0]
            if not isinstance(theme, dict) or not theme.get("key"):
                continue
            details = await session.call("get_theme_details", {
                "key": theme["key"], "max": 12, "offset": 0, "max_funds": 0,
            })
            for company in details.get("linked_companies", []):
                if not isinstance(company, dict):
                    continue
                symbol = str(company.get("symbol") or "").strip().upper()
                if symbol:
                    discovered.append({
                        "symbol": symbol,
                        "topic": details.get("name") or theme.get("name") or query,
                        "theme_key": theme["key"],
                        "rank": company.get("rank"),
                        "contract_id": company.get("contract_id"),
                    })
    result = {
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "queries": list(queries),
        "candidates": list({item["symbol"]: item for item in discovered}.values()),
        "source": "IBKR MCP investment topics",
    }
    cache["topic_discovery"] = result
    _write_market_cache(cache)
    return result


def discover_topic_candidates(queries=None):
    """Weekly thematic discovery; scoring remains in the market scanner."""
    if queries is None:
        configured = os.environ.get(
            "IBKR_MCP_DISCOVERY_TOPICS",
            "ai,semiconductor,cybersecurity,energy",
        )
        queries = [item.strip() for item in configured.split(",") if item.strip()]
    return asyncio.run(_discover_topic_candidates_async(tuple(queries)))


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
            "Contract_ID": item.get("contract_id"),
            "Asset_Class": str(item.get("asset_class") or ""),
            "Market_Value_IBKR": _number(item.get("market_value")),
            "Daily_PnL_IBKR": _number(item.get("daily_pnl")),
            "Unrealized_PnL_IBKR": _number(item.get("unrealized_pnl")),
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
            "Currency": str(
                item.get("currency") or item.get("currency_code") or ""
            ).upper(),
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
    interactive: bool = False, arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return await call_tool(
                name, arguments=arguments, interactive=interactive
            )
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


async def _session_call(
    session: ReadOnlyMCPSession,
    name: str,
    *, required: bool = True,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call one tool on an already initialised, reusable MCP connection."""
    try:
        return await session.call(name, arguments)
    except IBKRMCPAuthorizationRequired:
        raise
    except Exception as exc:
        if required:
            raise IBKRMCPError(f"IBKR MCP {name} indisponibil: {exc}") from exc
        print(f"  -> IBKR MCP {name} indisponibil; continuăm fără el.")
        return {}


async def _read_account_tools(*, interactive: bool) -> tuple[dict[str, Any], ...]:
    """Read the account through one session instead of seven handshakes."""
    async with ReadOnlyMCPSession(interactive=interactive) as session:
        summary = await _session_call(session, "get_account_summary")
        positions = await _session_call(session, "get_account_positions")
        orders = await _session_call(session, "get_account_orders")
        balances = await _session_call(
            session, "get_account_balances", required=False
        )
        performance = await _session_call(
            session, "get_pa_performance_all_periods", required=False
        )
        allocation = await _session_call(
            session,
            "get_pa_allocation",
            arguments={"type": "ALL"},
            required=False,
        )
        trades = await _session_call(
            session,
            "get_account_trades",
            arguments={"period": "DAYS_90"},
            required=False,
        )
    return summary, positions, orders, balances, performance, allocation, trades


def _normalise_trades(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Persist an analysis-ready journal while leaving future score links null."""
    rows = []
    for item in payload.get("trades", []):
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol") or "").strip().upper()
        if not symbol:
            continue
        rows.append({
            "trade_id": str(item.get("trade_id") or ""),
            "order_id": item.get("order_id"),
            "symbol": symbol,
            "side": str(item.get("side") or "").upper(),
            "size": _number(item.get("size")),
            "price": _number(item.get("price")),
            "currency": str(item.get("currency") or "").upper(),
            "commission": _number(item.get("commission")),
            "net_amount": _number(item.get("net_amount")),
            "realized_pnl": _number(item.get("realized_pnl")),
            "trade_time": str(item.get("trade_time") or ""),
            "order_type": str(item.get("order_type") or ""),
            "stop_price": _number(item.get("stop_price")),
            "security_type": str(item.get("sec_type") or ""),
            # Filled by the scanner when a contemporaneous recommendation is
            # available; never back-filled with invented historical evidence.
            "initial_score": None,
            "portfolio_state_at_entry": None,
            "target_at_entry": None,
            "outcome": None,
            "entry_price": None,
            "exit_price": None,
            "holding_period_days": None,
        })
    rows.sort(key=lambda item: item.get("trade_time") or "")
    open_lots: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        symbol = row["symbol"]
        size = abs(_number(row.get("size")))
        if row["side"] in {"BUY", "BOT"}:
            open_lots.setdefault(symbol, []).append({
                "remaining": size,
                "price": row["price"],
                "time": row["trade_time"],
            })
            row["entry_price"] = row["price"]
            continue
        if row["side"] not in {"SELL", "SLD"}:
            continue
        remaining = size
        matched = []
        for lot in open_lots.get(symbol, []):
            if remaining <= 0:
                break
            quantity = min(remaining, lot["remaining"])
            if quantity <= 0:
                continue
            matched.append((lot, quantity))
            lot["remaining"] -= quantity
            remaining -= quantity
        if matched:
            matched_size = sum(quantity for _lot, quantity in matched)
            row["entry_price"] = sum(
                lot["price"] * quantity for lot, quantity in matched
            ) / matched_size
            row["exit_price"] = row["price"]
            try:
                entry_time = min(
                    datetime.datetime.fromisoformat(
                        str(lot["time"]).replace("Z", "+00:00")
                    ) for lot, _quantity in matched
                )
                exit_time = datetime.datetime.fromisoformat(
                    str(row["trade_time"]).replace("Z", "+00:00")
                )
                row["holding_period_days"] = round(
                    (exit_time - entry_time).total_seconds() / 86400, 3
                )
            except (TypeError, ValueError):
                pass
        pnl = _number(row.get("realized_pnl"))
        row["outcome"] = "win" if pnl > 0 else "loss" if pnl < 0 else "flat"
    return rows


async def build_account_snapshot(*, interactive: bool = False) -> dict[str, Any]:
    """Read the authorised account without exposing any mutation tools."""
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            (
                summary,
                positions,
                orders,
                balances,
                performance,
                allocation,
                trades,
            ) = await _read_account_tools(interactive=interactive)
            break
        except IBKRMCPAuthorizationRequired:
            raise
        except Exception as exc:
            last_error = exc
            if not _is_transient_mcp_error(exc) or attempt == 1:
                raise
            await asyncio.sleep(1)
    else:  # pragma: no cover - defensive; loop either breaks or raises
        raise IBKRMCPError(f"IBKR MCP cont indisponibil: {last_error}")

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
        "portfolio_allocation": allocation,
        "account_performance": performance,
        "trade_journal": _normalise_trades(trades),
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
            "Contract_ID", "Asset_Class", "Market_Value_IBKR",
            "Daily_PnL_IBKR", "Unrealized_PnL_IBKR",
        ],
    ).to_csv("tws_positions.csv", index=False)
    pd.DataFrame(
        order_rows,
        columns=[
            "Symbol", "OrderType", "Action", "Total_Qty", "Aux_Price",
            "Limit_Price", "Stop_Price", "Trail_Pct", "Calculated_Stop",
            "Currency",
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
