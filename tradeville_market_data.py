"""Date OHLCV publice Tradeville pentru instrumentele listate la BVB.

Modulul este un fallback de piață, nu o sursă de recomandări. El validează
strict răspunsul public Tradeville și respinge seriile fără tranzacții recente.
"""

import datetime
import json
import math
import re
import threading
import time
from io import StringIO

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


TRADEVILLE_CHART_URL = "https://mbl.tradeville.ro/cmd/graficdata"
TRADEVILLE_LIST_URL = "https://tradeville.ro/actiuni/actiuni-listare-bursa"
# Ultima listă validă citită din pagina publică Tradeville la 28.07.2026.
# Este folosită numai când pagina listei este temporar blocată/indisponibilă.
LAST_VALID_LISTED_SYMBOLS = frozenset({
    "AAG", "ALR", "ALT", "ALU", "AQ", "ARM", "AROBS", "ARS", "ARTE",
    "ATB", "BCM", "BIO", "BKBETETF", "BNET", "BRD", "BRK", "BRM",
    "BTBETRETF", "BTF", "BUCV", "BVB", "CAOR", "CBC", "CFH", "CMCM",
    "CMF", "CMP", "CNTE", "COMI", "COTE", "CRC", "DIGI", "EAI", "EBS",
    "ECT", "EFO", "EL", "ELGS", "ELGSR01", "ELJ", "ELMA", "ENP", "EVER",
    "FP", "GIBEFETF", "GREEN", "H2O", "IARV", "ICBETNETF", "ICCROETF",
    "ICGROETF", "ICSLOETF", "IMP", "INFINITY", "LION", "LONG", "M",
    "MCAB", "MECF", "MFC", "NAPO", "OIL", "ONE", "PBK", "PE", "PPL",
    "PREB", "PREH", "PTENGETF", "PTR", "RMAH", "ROC1", "ROCE", "RPH",
    "RRC", "SAFE", "SFG", "SMTL", "SNG", "SNN", "SNO", "SNP", "SOCP",
    "STK", "STZ", "TBK", "TBM", "TEL", "TGN", "TLV", "TRANSI", "TRIP",
    "TRP", "TTS", "TVBETETF", "UAM", "UZT", "VESY", "VNC", "WINE",
})
DEFAULT_MAX_AGE_DAYS = 10
DEFAULT_MIN_OBSERVATIONS = 60
_RETRY_SESSION = None
_LISTED_SYMBOLS = None
_REQUEST_LOCK = threading.Lock()
_LAST_REQUEST_AT = 0.0
MIN_REQUEST_INTERVAL_SECONDS = 1.0


class TradevilleDataError(ValueError):
    """Răspuns Tradeville absent, invalid sau insuficient."""


class TradevilleStaleDataError(TradevilleDataError):
    """Instrument fără tranzacții suficient de recente pentru analiză."""


def normalize_bvb_symbol(symbol):
    normalized = str(symbol or "").strip().upper()
    return normalized[:-3] if normalized.endswith(".RO") else normalized


def _finite_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _retry_session():
    """Reîncearcă erorile temporare de DNS/conexiune fără a inventa date."""
    global _RETRY_SESSION
    if _RETRY_SESSION is None:
        retry = Retry(
            total=3,
            connect=3,
            read=2,
            status=2,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            raise_on_status=False,
        )
        _RETRY_SESSION = requests.Session()
        _RETRY_SESSION.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://tradeville.ro/",
        })
        adapter = HTTPAdapter(max_retries=retry)
        _RETRY_SESSION.mount("https://", adapter)
        _RETRY_SESSION.mount("http://", adapter)
    return _RETRY_SESSION


def _throttled_get(client, *args, **kwargs):
    """Evită blocarea sursei publice prin cereri prea apropiate."""
    global _LAST_REQUEST_AT
    with _REQUEST_LOCK:
        elapsed = time.monotonic() - _LAST_REQUEST_AT
        remaining = MIN_REQUEST_INTERVAL_SECONDS - elapsed
        if remaining > 0:
            time.sleep(remaining)
        try:
            return client.get(*args, **kwargs)
        finally:
            _LAST_REQUEST_AT = time.monotonic()


def parse_listed_symbols(html):
    """Extrage simbolurile din lista publică Tradeville BVB/AeRO."""
    symbols = {
        match.upper()
        for match in re.findall(
            r'href=["\'](?:https?://[^"\']+)?/actiuni/([A-Za-z0-9]{1,12})',
            str(html or ""),
            flags=re.IGNORECASE,
        )
    }
    if len(symbols) < 20:
        raise TradevilleDataError(
            "Lista publică Tradeville nu conține suficiente simboluri"
        )
    return symbols


def fetch_listed_symbols(*, session=None, timeout=15):
    """Încarcă o singură dată universul public Tradeville din rularea curentă."""
    global _LISTED_SYMBOLS
    if session is None and _LISTED_SYMBOLS is not None:
        return set(_LISTED_SYMBOLS)
    client = session or _retry_session()
    try:
        response = (
            client.get(TRADEVILLE_LIST_URL, timeout=timeout)
            if session is not None
            else _throttled_get(client, TRADEVILLE_LIST_URL, timeout=timeout)
        )
        response.raise_for_status()
        symbols = parse_listed_symbols(response.text)
    except (requests.RequestException, TradevilleDataError):
        symbols = set(LAST_VALID_LISTED_SYMBOLS)
    if session is None:
        _LISTED_SYMBOLS = set(symbols)
    return symbols


def parse_chart_payload(
    payload,
    *,
    now=None,
    max_age_days=DEFAULT_MAX_AGE_DAYS,
    min_observations=DEFAULT_MIN_OBSERVATIONS,
):
    """Transformă răspunsul ``graficdata`` într-un DataFrame OHLCV valid."""
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise TradevilleDataError("Răspunsul Tradeville nu este JSON") from exc
    if not isinstance(payload, dict):
        raise TradevilleDataError("Răspuns Tradeville invalid")

    csv_text = payload.get("data")
    if not isinstance(csv_text, str) or not csv_text.strip():
        raise TradevilleDataError("Istoricul Tradeville este gol")

    try:
        frame = pd.read_csv(StringIO(csv_text))
    except Exception as exc:
        raise TradevilleDataError("Istoricul Tradeville nu poate fi citit") from exc

    normalized_columns = {
        str(column).strip().lower(): column for column in frame.columns
    }
    required = {
        "data": "Date",
        "deschide": "Open",
        "maxim": "High",
        "minim": "Low",
        "last": "Close",
    }
    if not set(required).issubset(normalized_columns):
        raise TradevilleDataError("Lipsesc coloane OHLC Tradeville")

    selected = pd.DataFrame()
    for source_name, target_name in required.items():
        selected[target_name] = frame[normalized_columns[source_name]]
    volume_column = normalized_columns.get("volum")
    selected["Volume"] = frame[volume_column] if volume_column else 0

    selected["Date"] = pd.to_datetime(selected["Date"], errors="coerce")
    for column in ("Open", "High", "Low", "Close", "Volume"):
        selected[column] = pd.to_numeric(selected[column], errors="coerce")
    selected = (
        selected.dropna(subset=["Date", "Open", "High", "Low", "Close"])
        .drop_duplicates(subset=["Date"], keep="last")
        .sort_values("Date")
    )
    selected = selected[
        (selected["Open"] > 0)
        & (selected["High"] > 0)
        & (selected["Low"] > 0)
        & (selected["Close"] > 0)
        & (selected["High"] >= selected[["Open", "Close", "Low"]].max(axis=1))
        & (selected["Low"] <= selected[["Open", "Close", "High"]].min(axis=1))
    ]
    selected["Volume"] = selected["Volume"].fillna(0).clip(lower=0)
    if len(selected) < int(min_observations):
        raise TradevilleDataError(
            f"Istoric Tradeville insuficient ({len(selected)} observații)"
        )

    current_time = now or datetime.datetime.now(datetime.timezone.utc)
    if isinstance(current_time, datetime.date) and not isinstance(
        current_time, datetime.datetime
    ):
        current_date = current_time
    else:
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=datetime.timezone.utc)
        current_date = current_time.date()
    latest_date = selected["Date"].iloc[-1].date()
    age_days = (current_date - latest_date).days
    if age_days < -1:
        raise TradevilleDataError(
            f"Istoricul Tradeville conține o dată viitoare ({latest_date})"
        )
    if age_days > int(max_age_days):
        raise TradevilleStaleDataError(
            f"ultima tranzacție este din {latest_date.isoformat()} "
            f"({age_days} zile vechime)"
        )

    return selected.set_index("Date")[
        ["Open", "High", "Low", "Close", "Volume"]
    ]


def fetch_history(
    symbol,
    *,
    session=None,
    timeout=15,
    now=None,
    max_age_days=DEFAULT_MAX_AGE_DAYS,
    min_observations=DEFAULT_MIN_OBSERVATIONS,
):
    """Descarcă și validează istoricul Tradeville pentru un simbol BVB."""
    bvb_symbol = normalize_bvb_symbol(symbol)
    if not bvb_symbol:
        raise TradevilleDataError("Simbol BVB lipsă")
    listed_symbols = fetch_listed_symbols(
        session=session,
        timeout=timeout,
    )
    if bvb_symbol not in listed_symbols:
        raise TradevilleDataError(
            f"{bvb_symbol} nu apare în lista publică Tradeville"
        )
    client = session or _retry_session()
    request_kwargs = {
        "params": {"simbol": bvb_symbol, "lat": ""},
        "timeout": timeout,
    }
    response = (
        client.get(TRADEVILLE_CHART_URL, **request_kwargs)
        if session is not None
        else _throttled_get(client, TRADEVILLE_CHART_URL, **request_kwargs)
    )
    response.raise_for_status()
    try:
        payload = response.json()
    except (ValueError, json.JSONDecodeError) as exc:
        raise TradevilleDataError("Răspunsul Tradeville nu este JSON") from exc
    frame = parse_chart_payload(
        payload,
        now=now,
        max_age_days=max_age_days,
        min_observations=min_observations,
    )
    return frame, {
        "symbol": f"{bvb_symbol}.RO",
        "data_provider": "Tradeville public market data",
        "data_broker": "Tradeville",
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "market_data": {
            "close": _finite_number(frame["Close"].iloc[-1]),
            "volume": _finite_number(frame["Volume"].iloc[-1]),
            "as_of": frame.index[-1].date().isoformat(),
        },
        "execution_brokers": ["Tradeville"],
        "ibkr_data_only": False,
    }
