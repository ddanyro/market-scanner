"""Date OHLCV publice Tradeville pentru instrumentele listate la BVB.

Modulul este un fallback de piață, nu o sursă de recomandări. El validează
strict răspunsul public Tradeville și respinge seriile fără tranzacții recente.
"""

import datetime
import json
import math
from io import StringIO

import pandas as pd
import requests


TRADEVILLE_CHART_URL = "https://mbl.tradeville.ro/cmd/graficdata"
DEFAULT_MAX_AGE_DAYS = 10
DEFAULT_MIN_OBSERVATIONS = 60


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
    client = session or requests
    response = client.get(
        TRADEVILLE_CHART_URL,
        params={"simbol": bvb_symbol, "lat": ""},
        timeout=timeout,
        headers={"User-Agent": "Antigravity-Market-Scanner/1.0"},
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
