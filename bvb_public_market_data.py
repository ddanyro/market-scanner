"""Istoric OHLCV BVB din fișierele zilnice publice, fără autentificare.

Sursa nu este BVB Web Service și nu necesită cont, token sau cheie API.
Cache-ul CSV este incremental: prima rulare face backfill, apoi fiecare rulare
înlocuiește numai ultimele ședințe și adaugă zilele noi.
"""

import datetime
import os
import threading
import time
from io import BytesIO

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BVB_DAILY_URL = (
    "https://www.bvb.ro/TradingAndStatistics/Trading/"
    "HistoricalTradingInfo.ashx"
)
DEFAULT_CACHE_FILE = "bvb_daily_cache.csv"
DEFAULT_MIN_OBSERVATIONS = 60
DEFAULT_MAX_AGE_DAYS = 10
DEFAULT_LOOKBACK_DAYS = 150
DEFAULT_MAX_CONSECUTIVE_ERRORS = 3
MIN_REQUEST_INTERVAL_SECONDS = 0.20
CACHE_COLUMNS = [
    "Date",
    "Symbol",
    "Market",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Value",
]
_SESSION = None
_CACHE_FRAMES = {}
_REQUESTED_DATES = {}
_UNAVAILABLE_CACHE_KEYS = set()
_REQUEST_LOCK = threading.Lock()
_LAST_REQUEST_AT = 0.0


class BVBPublicDataError(ValueError):
    """Fișier BVB absent, invalid sau fără suficiente date."""


class BVBPublicStaleDataError(BVBPublicDataError):
    """Ultima ședință din cache este prea veche."""


def normalize_symbol(symbol):
    normalized = str(symbol or "").strip().upper()
    return normalized[:-3] if normalized.endswith(".RO") else normalized


def _session():
    global _SESSION
    if _SESSION is None:
        retry = Retry(
            total=3,
            connect=3,
            read=2,
            status=2,
            backoff_factor=0.4,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            raise_on_status=False,
        )
        _SESSION = requests.Session()
        _SESSION.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            "Accept": "text/csv,application/octet-stream,*/*",
            "Referer": (
                "https://www.bvb.ro/TradingAndStatistics/Trading/"
                "HistoricalTradingInfo"
            ),
        })
        adapter = HTTPAdapter(max_retries=retry)
        _SESSION.mount("https://", adapter)
        _SESSION.mount("http://", adapter)
    return _SESSION


def _throttled_get(client, *args, **kwargs):
    global _LAST_REQUEST_AT
    with _REQUEST_LOCK:
        remaining = (
            MIN_REQUEST_INTERVAL_SECONDS
            - (time.monotonic() - _LAST_REQUEST_AT)
        )
        if remaining > 0:
            time.sleep(remaining)
        try:
            return client.get(*args, **kwargs)
        finally:
            _LAST_REQUEST_AT = time.monotonic()


def _numeric(series):
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )


def parse_daily_csv(content, trading_date):
    """Normalizează fișierul unei ședințe și elimină piețele DEALS duplicate."""
    try:
        raw = pd.read_csv(BytesIO(content if isinstance(content, bytes) else content.encode()))
    except Exception as exc:
        raise BVBPublicDataError("Fișierul zilnic BVB nu poate fi citit") from exc
    required = {
        "Symbol",
        "Market",
        "Volume",
        "Value",
        "Open",
        "Low",
        "High",
        "Close",
    }
    if not required.issubset(raw.columns):
        raise BVBPublicDataError("Fișierul zilnic BVB nu conține coloanele OHLCV")

    frame = raw[list(required)].copy()
    frame["Symbol"] = frame["Symbol"].astype(str).str.strip().str.upper()
    frame["Market"] = frame["Market"].astype(str).str.strip().str.upper()
    for column in ("Open", "Low", "High", "Close", "Volume", "Value"):
        frame[column] = _numeric(frame[column])
    frame = frame[
        frame["Symbol"].str.fullmatch(r"[A-Z0-9]{1,12}", na=False)
        & frame["Open"].gt(0)
        & frame["Low"].gt(0)
        & frame["High"].gt(0)
        & frame["Close"].gt(0)
        & frame["High"].ge(frame[["Open", "Close", "Low"]].max(axis=1))
        & frame["Low"].le(frame[["Open", "Close", "High"]].min(axis=1))
    ].copy()
    if frame.empty:
        return pd.DataFrame(columns=CACHE_COLUMNS)

    market_priority = {
        "REGS": 0,
        "XRS1": 1,
        "XRSI": 2,
        "ATS": 3,
        "DEALS": 9,
    }
    frame["_priority"] = frame["Market"].map(market_priority).fillna(5)
    frame = (
        frame.sort_values(
            ["Symbol", "_priority", "Volume"],
            ascending=[True, True, False],
        )
        .drop_duplicates(subset=["Symbol"], keep="first")
        .drop(columns=["_priority"])
    )
    frame.insert(0, "Date", pd.Timestamp(trading_date).date().isoformat())
    return frame[CACHE_COLUMNS].reset_index(drop=True)


def fetch_daily_snapshot(trading_date, *, session=None, timeout=20):
    day = pd.Timestamp(trading_date).date()
    client = session or _session()
    response = (
        client.get(
            BVB_DAILY_URL,
            params={"day": day.strftime("%Y%m%d")},
            timeout=timeout,
        )
        if session is not None
        else _throttled_get(
            client,
            BVB_DAILY_URL,
            params={"day": day.strftime("%Y%m%d")},
            timeout=timeout,
        )
    )
    response.raise_for_status()
    return parse_daily_csv(response.content, day)


def _empty_cache():
    return pd.DataFrame(columns=CACHE_COLUMNS)


def _load_cache(cache_path):
    cache_key = os.path.abspath(cache_path)
    if cache_key in _CACHE_FRAMES:
        return _CACHE_FRAMES[cache_key].copy()
    if not os.path.exists(cache_path):
        frame = _empty_cache()
    else:
        try:
            frame = pd.read_csv(cache_path)
            if not set(CACHE_COLUMNS).issubset(frame.columns):
                frame = _empty_cache()
            else:
                frame = frame[CACHE_COLUMNS]
        except (OSError, ValueError, pd.errors.ParserError):
            frame = _empty_cache()
    _CACHE_FRAMES[cache_key] = frame.copy()
    return frame


def _save_cache(cache_path, frame):
    normalized = (
        frame[CACHE_COLUMNS]
        .drop_duplicates(subset=["Date", "Symbol"], keep="last")
        .sort_values(["Date", "Symbol"])
        .reset_index(drop=True)
    )
    temp_path = f"{cache_path}.tmp"
    normalized.to_csv(temp_path, index=False)
    os.replace(temp_path, cache_path)
    _CACHE_FRAMES[os.path.abspath(cache_path)] = normalized.copy()


def _candidate_dates(today, lookback_days):
    start = today - datetime.timedelta(days=int(lookback_days))
    dates = pd.bdate_range(start=start, end=today).date.tolist()
    return list(reversed(dates))


def _symbol_frame(cache, symbol):
    selected = cache[cache["Symbol"].astype(str).str.upper() == symbol].copy()
    if selected.empty:
        return pd.DataFrame()
    selected["Date"] = pd.to_datetime(selected["Date"], errors="coerce")
    for column in ("Open", "High", "Low", "Close", "Volume"):
        selected[column] = pd.to_numeric(selected[column], errors="coerce")
    selected = (
        selected.dropna(subset=["Date", "Open", "High", "Low", "Close"])
        .drop_duplicates(subset=["Date"], keep="last")
        .sort_values("Date")
        .set_index("Date")
    )
    return selected[["Open", "High", "Low", "Close", "Volume"]]


def fetch_history(
    symbol,
    *,
    cache_path=DEFAULT_CACHE_FILE,
    session=None,
    timeout=20,
    now=None,
    min_observations=DEFAULT_MIN_OBSERVATIONS,
    max_age_days=DEFAULT_MAX_AGE_DAYS,
    lookback_days=DEFAULT_LOOKBACK_DAYS,
    max_consecutive_errors=DEFAULT_MAX_CONSECUTIVE_ERRORS,
):
    """Returnează OHLCV BVB, completând incremental cache-ul public zilnic."""
    bvb_symbol = normalize_symbol(symbol)
    if not bvb_symbol:
        raise BVBPublicDataError("Simbol BVB lipsă")
    current_date = (
        pd.Timestamp(now).date()
        if now is not None
        else datetime.datetime.now().astimezone().date()
    )
    cache_key = os.path.abspath(cache_path)
    cache = _load_cache(cache_path)
    existing_dates = set(cache.get("Date", pd.Series(dtype=str)).astype(str))
    symbol_history = _symbol_frame(cache, bvb_symbol)
    source_errors = []
    consecutive_errors = 0
    downloaded_days = 0
    initial_cache_empty = cache.empty

    if initial_cache_empty and cache_key not in _UNAVAILABLE_CACHE_KEYS:
        print(
            "  [BVB public] Se construiește cache-ul istoric zilnic; "
            "prima rulare poate dura aproximativ un minut..."
        )

    candidates = (
        []
        if cache_key in _UNAVAILABLE_CACHE_KEYS
        else _candidate_dates(current_date, lookback_days)
    )
    requested_dates = _REQUESTED_DATES.setdefault(cache_key, set())
    refresh_dates = {
        trading_date
        for trading_date in candidates[:2]
        if trading_date.isoformat() not in requested_dates
    }
    for trading_date in candidates:
        date_text = trading_date.isoformat()
        enough_history = len(symbol_history) >= int(min_observations)
        if (
            date_text in existing_dates
            and trading_date not in refresh_dates
        ):
            if enough_history:
                break
            continue
        if date_text in requested_dates:
            continue
        requested_dates.add(date_text)
        try:
            daily = fetch_daily_snapshot(
                trading_date,
                session=session,
                timeout=timeout,
            )
        except (requests.RequestException, BVBPublicDataError) as exc:
            source_errors.append(str(exc))
            consecutive_errors += 1
            if consecutive_errors >= int(max_consecutive_errors):
                _UNAVAILABLE_CACHE_KEYS.add(cache_key)
                print(
                    "  [BVB public] Sursa nu răspunde; oprim backfillul "
                    f"după {consecutive_errors} erori consecutive."
                )
                break
            continue
        consecutive_errors = 0
        downloaded_days += 1
        cache = cache[cache["Date"].astype(str) != date_text]
        if not daily.empty:
            cache = pd.concat([cache, daily], ignore_index=True)
        existing_dates.add(date_text)
        symbol_history = _symbol_frame(cache, bvb_symbol)
        if downloaded_days % 10 == 0:
            if not cache.empty:
                _save_cache(cache_path, cache)
            print(
                f"  [BVB public] Backfill: {downloaded_days} zile "
                f"descărcate, {len(symbol_history)}/{min_observations} "
                f"ședințe pentru {bvb_symbol}."
            )
        if (
            len(symbol_history) >= int(min_observations)
            and trading_date not in refresh_dates
        ):
            break

    if not cache.empty:
        _save_cache(cache_path, cache)
    symbol_history = _symbol_frame(cache, bvb_symbol)
    if len(symbol_history) < int(min_observations):
        detail = f"; ultima eroare: {source_errors[-1]}" if source_errors else ""
        raise BVBPublicDataError(
            f"Istoric public BVB insuficient pentru {bvb_symbol} "
            f"({len(symbol_history)} ședințe){detail}"
        )
    latest_date = symbol_history.index[-1].date()
    age_days = (current_date - latest_date).days
    if age_days > int(max_age_days):
        raise BVBPublicStaleDataError(
            f"ultima ședință pentru {bvb_symbol} este din "
            f"{latest_date.isoformat()}"
        )
    return symbol_history, {
        "symbol": f"{bvb_symbol}.RO",
        "data_provider": "BVB CSV public zilnic (fără autentificare)",
        "data_broker": "BVB public",
        "fetched_at": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(),
        "market_data": {
            "close": float(symbol_history["Close"].iloc[-1]),
            "volume": float(symbol_history["Volume"].iloc[-1]),
            "as_of": latest_date.isoformat(),
        },
        "execution_brokers": ["Tradeville"],
        "ibkr_data_only": False,
    }
