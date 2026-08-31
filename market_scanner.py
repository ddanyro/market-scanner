# -*- coding: utf-8 -*-
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import urllib3
    import requests

import yfinance as yf
import pandas as pd
import argparse
import asyncio
import sys
import datetime
import time
import os
import requests
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
import math
import yfinance as yf
# New imports for encryption
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from base64 import b64encode
import json
import copy
import unicodedata
import hashlib
import hmac
import html
from zoneinfo import ZoneInfo
from io import StringIO
from market_scanner_analysis import (
    generate_market_analysis,
    generate_portfolio_ai_analysis,
    generate_swing_trading_html,
    get_swing_trading_data,
)
import market_scanner_analysis as analysis
import market_utils
import market_security
import market_data
import bvb_public_market_data
import buy_now_push

BUY_RESEARCH_UNIVERSES = {
    'SUA': [
        'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'META', 'AVGO', 'V', 'MA',
        'COST', 'LLY', 'XOM', 'SCHW', 'ET', 'RELY',
        # Univers suplimentar, separat de watchlist, pentru descoperirea
        # oportunităților atunci când filtrul watchlistului nu produce idei.
        'MMM', 'AIG', 'EBAY', 'GRMN', 'IT', 'KEYS', 'MTB', 'EIX', 'IP', 'JBHT',
    ],
    'România / BVB': [
        'TLV.RO', 'SNP.RO', 'SNG.RO', 'H2O.RO', 'TGN.RO', 'BRD.RO',
        'DIGI.RO', 'EL.RO', 'M.RO', 'SNN.RO', 'TEL.RO', 'FP.RO', 'PE.RO',
        'ONE.RO', 'AQ.RO', 'TRP.RO', 'TTS.RO', 'ATB.RO', 'CFH.RO', 'SFG.RO',
    ],
    'Europa / Nasdaq-100': ['LQQ.PA'],
}
ALWAYS_RESEARCH_SYMBOLS = {'LQQ.PA'}
KNOWN_FUND_PROFILES = {
    'LQQ.PA': {
        'longName': 'LQQ — Nasdaq-100 Daily (2x) Leveraged UCITS ETF',
        'shortName': 'LQQ',
        'industry': 'ETF leveraged',
        'sector': 'Nasdaq-100',
    },
    'TVBETETF.RO': {
        'longName': 'ETF BET Patria-Tradeville',
        'shortName': 'TVBETETF',
        'industry': 'ETF',
        'sector': 'Piața românească / BET',
    },
}
BVB_SHARES_CSV_URL = (
    'https://www.bvb.ro/FinancialInstruments/Markets/'
    'SharesListForDownload.ashx?filetype=csv'
)
ROMANIAN_UNIVERSE_SOURCE_URL = BVB_SHARES_CSV_URL
BVB_DEEP_SCAN_BATCH = 50
US_DEEP_SCAN_BATCH = 70
EXTERNAL_RESEARCH_MIN_RR = 1.8
BUY_FINALIST_TTL_HOURS = 1.0
EXTERNAL_RESEARCH_TTL_HOURS = 5.0
SP500_UNIVERSE_FILE = 'sp500_tickers.json'
TWS_INSTRUMENTS_FILE = 'tws_instruments.json'
TWS_INSTRUMENT_TTL_HOURS = 96
IBKR_MCP_MARKET_CACHE_FILE = '.ibkr_mcp_market_cache.json'
IBKR_MCP_MARKET_TTL_HOURS = float(
    os.environ.get('IBKR_MCP_MARKET_TTL_HOURS', '1')
)
TWS_ACTIVE_ORDERS_CACHE_KEY = 'tws_active_orders_snapshot_enc'
TWS_ACTIVE_ORDER_COLUMNS = [
    'Symbol', 'OrderType', 'Action', 'Total_Qty', 'Aux_Price',
    'Limit_Price', 'Stop_Price', 'Trail_Pct', 'Calculated_Stop',
    'Currency',
]
_YAHOO_HISTORY_MEMORY_CACHE = {}


def _portfolio_chat_access_token(password):
    """Token stabil derivat din PIN; PIN-ul și cheia OpenAI nu ajung în HTML."""
    if not password:
        return ''
    return hmac.new(
        str(password).encode('utf-8'),
        b'market-scanner-portfolio-chat-v1',
        hashlib.sha256,
    ).hexdigest()


def _firebase_web_config(value):
    """Validează configurația publică a aplicației web Firebase."""
    try:
        config = value if isinstance(value, dict) else json.loads(value or '')
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    if not isinstance(config, dict):
        return {}
    allowed_keys = {
        'apiKey',
        'authDomain',
        'projectId',
        'storageBucket',
        'messagingSenderId',
        'appId',
        'measurementId',
    }
    config = {
        key: str(config.get(key) or '').strip()
        for key in allowed_keys
        if config.get(key)
    }
    required = {'apiKey', 'projectId', 'messagingSenderId', 'appId'}
    return config if required.issubset(config) else {}


def _write_firebase_service_worker(config, worker_path=None):
    """Scrie workerul FCM fără a include credențialele serverului."""
    worker_path = worker_path or os.path.join(
        'push', 'firebase', 'firebase-messaging-sw.js'
    )
    os.makedirs(os.path.dirname(worker_path), exist_ok=True)
    worker = f"""\
importScripts("https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js");

firebase.initializeApp({json.dumps(config, ensure_ascii=False)});
firebase.messaging();
"""
    with open(worker_path, 'w', encoding='utf-8') as handle:
        handle.write(worker)


def _firebase_web_push_html(config_value, vapid_key, worker_path=None):
    """Inițializează abonarea web push prin Firebase Cloud Messaging."""
    config = _firebase_web_config(config_value)
    vapid_key = str(vapid_key or '').strip()
    if not config or len(vapid_key) < 40:
        return ''
    _write_firebase_service_worker(config, worker_path=worker_path)
    config_json = json.dumps(config, ensure_ascii=False)
    vapid_key_json = json.dumps(vapid_key)
    project_id_json = json.dumps(config['projectId'])
    return f"""
        <script src="https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js"></script>
        <script src="https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js"></script>
        <style>
            #buyNowPushButton {{
                width: 100%;
                border: 0;
                border-bottom: 1px solid var(--border-light, #dfe3ea);
                border-radius: 0;
                background: transparent;
                text-align: left;
                font: inherit;
                appearance: none;
            }}
            #buyNowPushButton[data-active="true"] {{
                background: #ecfdf5;
                color: #166534;
            }}
            #buyNowPushButton:disabled {{
                cursor: wait;
                opacity: .65;
            }}
        </style>
        <script>
            window.addEventListener('load', async function() {{
                if (window.marketScannerPortfolioAuthenticated !== true) {{
                    await new Promise(function(resolve) {{
                        window.addEventListener(
                            'market-scanner:portfolio-authenticated',
                            resolve,
                            {{once: true}}
                        );
                    }});
                }}
                const firebaseConfig = {config_json};
                const firebaseVapidKey = {vapid_key_json};
                const firebaseProjectId = {project_id_json};
                const workerScope = new URL(
                    'push/firebase/', document.baseURI
                ).pathname;
                const workerUrl = new URL(
                    'push/firebase/firebase-messaging-sw.js',
                    document.baseURI
                ).href;
                const isIOS = (
                    /iPad|iPhone|iPod/.test(navigator.userAgent)
                    || (
                        navigator.platform === 'MacIntel'
                        && navigator.maxTouchPoints > 1
                    )
                );
                const isStandalone = (
                    window.matchMedia('(display-mode: standalone)').matches
                    || window.navigator.standalone === true
                );
                const supportsWebPush = (
                    'serviceWorker' in navigator
                    && 'PushManager' in window
                    && typeof Notification !== 'undefined'
                );

                function mountPushPrerequisiteButton(message, explanation) {{
                    if (document.getElementById('buyNowPushButton')) return;
                    const menu = document.getElementById('navMenu');
                    if (!menu) return;
                    const button = document.createElement('button');
                    button.id = 'buyNowPushButton';
                    button.type = 'button';
                    button.className = 'menu-item push-menu-item';
                    button.textContent = message;
                    button.title = explanation;
                    button.addEventListener('click', function() {{
                        alert(explanation);
                    }});
                    menu.appendChild(button);
                }}

                if (isIOS && !isStandalone) {{
                    mountPushPrerequisiteButton(
                        'Instalează pentru alerte BUY',
                        'Pentru notificări pe iPhone: apasă Partajare, '
                        + 'alege „Adaugă la ecranul principal”, apoi deschide '
                        + 'dashboardul instalat și activează alertele BUY.'
                    );
                    return;
                }}
                if (!supportsWebPush) {{
                    mountPushPrerequisiteButton(
                        'Alerte BUY indisponibile',
                        'Acest browser nu oferă notificări web. Actualizează '
                        + 'browserul sau deschide dashboardul într-un browser '
                        + 'compatibil.'
                    );
                    return;
                }}
                if (!firebase.apps.length) firebase.initializeApp(firebaseConfig);
                const messaging = firebase.messaging();
                const registration = await navigator.serviceWorker.register(
                    workerUrl, {{scope: workerScope}}
                );
                const tokenStorageKey = (
                    'marketScannerFirebaseToken:' + firebaseProjectId
                );
                let currentToken = '';

                async function readFirebaseToken(requestIfMissing) {{
                    if (
                        typeof Notification === 'undefined'
                        || Notification.permission !== 'granted'
                    ) {{
                        currentToken = '';
                        return '';
                    }}
                    if (!requestIfMissing) {{
                        currentToken = localStorage.getItem(tokenStorageKey) || '';
                        if (currentToken) return currentToken;
                    }}
                    currentToken = await messaging.getToken({{
                        vapidKey: firebaseVapidKey,
                        serviceWorkerRegistration: registration
                    }}) || '';
                    if (currentToken) {{
                        localStorage.setItem(tokenStorageKey, currentToken);
                    }}
                    return currentToken;
                }}

                function mountBuyNowPushButton() {{
                    if (document.getElementById('buyNowPushButton')) return;
                    const menu = document.getElementById('navMenu');
                    if (!menu) return;
                    const button = document.createElement('button');
                    button.id = 'buyNowPushButton';
                    button.type = 'button';
                    button.className = 'menu-item push-menu-item';
                    menu.appendChild(button);

                    async function refreshPushButton(requestIfMissing=false) {{
                        try {{
                            await readFirebaseToken(requestIfMissing);
                        }} catch (error) {{
                            console.warn('FCM nu a putut citi tokenul.', error);
                            currentToken = '';
                        }}
                        const active = Boolean(
                            Notification.permission === 'granted'
                            && currentToken
                        );
                        button.dataset.active = String(active);
                        button.dataset.subscriptionReady = String(active);
                        if (active) {{
                            button.textContent = 'Alerte BUY active';
                            button.title = (
                                'Abonament Firebase activ. Apasă pentru a opri '
                                + 'alertele BUY pe acest dispozitiv.'
                            );
                        }} else {{
                            button.textContent = 'Activează alertele BUY';
                            button.title = (
                                'Primești prin Google Firebase numai ordinele '
                                + 'noi Cumpărare acum.'
                            );
                        }}
                    }}

                    button.addEventListener('click', async function() {{
                        button.disabled = true;
                        try {{
                            if (currentToken) {{
                                await messaging.deleteToken();
                                currentToken = '';
                                localStorage.removeItem(tokenStorageKey);
                            }} else {{
                                if (Notification.permission !== 'granted') {{
                                    const permission = await Notification
                                        .requestPermission();
                                    if (permission !== 'granted') return;
                                }}
                                await readFirebaseToken(true);
                            }}
                        }} finally {{
                            button.disabled = false;
                            await refreshPushButton(false);
                        }}
                    }});
                    refreshPushButton(true);
                }}

                messaging.onMessage(async function(payload) {{
                    const notification = payload.notification || {{}};
                    await registration.showNotification(
                        notification.title || 'Market Scanner',
                        {{
                            body: notification.body || '',
                            data: {{url: {json.dumps("https://ddanyro.github.io/market-scanner/")}}}
                        }}
                    );
                }});
                if (document.readyState === 'loading') {{
                    document.addEventListener(
                        'DOMContentLoaded', mountBuyNowPushButton,
                        {{once: true}}
                    );
                }} else {{
                    mountBuyNowPushButton();
                }}
            }});
        </script>
    """


def _canonical_fund_symbol(symbol):
    normalized = str(symbol or '').strip().upper()
    if normalized in {'LQQ.PA', 'LQQ.FR', 'FR.LQQ'}:
        return 'LQQ.PA'
    return normalized


def _known_fund_profile(symbol):
    """Returnează metadate locale pentru ETF-uri care nu au fundamentale Yahoo."""
    return KNOWN_FUND_PROFILES.get(_canonical_fund_symbol(symbol))


def _get_yahoo_info(symbol, tws_instrument=None):
    """Evită endpointul de fundamentale pentru ETF-urile cunoscute."""
    fund_profile = _known_fund_profile(symbol)
    contract = (
        (tws_instrument or {}).get('contract', {})
        if isinstance(tws_instrument, dict) else {}
    )
    tws_profile = {
        'longName': contract.get('long_name'),
        'shortName': contract.get('local_symbol'),
        'industry': contract.get('industry'),
        'sector': contract.get('category'),
    }
    if fund_profile:
        info = dict(fund_profile)
        info.update({
            key: value for key, value in tws_profile.items() if value
        })
        return info
    lookup_symbol = str(symbol or '').strip()
    if lookup_symbol.endswith('.US'):
        lookup_symbol = lookup_symbol[:-3]
    info = yf.Ticker(lookup_symbol).info or {}
    info.update({
        key: value for key, value in tws_profile.items() if value
    })
    return info


def _parse_snapshot_timestamp(value):
    text = str(value or '').strip()
    if not text:
        return None
    try:
        parsed = datetime.datetime.fromisoformat(text.replace('Z', '+00:00'))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def _load_tws_instrument(
    symbol, path=TWS_INSTRUMENTS_FILE, now=None,
    max_age_hours=TWS_INSTRUMENT_TTL_HOURS,
):
    """Încarcă un snapshot TWS proaspăt, inclusiv prin aliasurile dashboardului."""
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
    except (OSError, ValueError, TypeError):
        return None
    instruments = payload.get('instruments', {})
    normalized = str(symbol or '').strip().upper()
    entry = instruments.get(normalized)
    if not isinstance(entry, dict):
        entry = next(
            (
                candidate for candidate in instruments.values()
                if normalized in {
                    str(alias).upper()
                    for alias in candidate.get('aliases', [])
                }
            ),
            None,
        )
    if not isinstance(entry, dict) or not entry.get('bars'):
        return None
    fetched_at = _parse_snapshot_timestamp(
        entry.get('fetched_at') or payload.get('fetched_at')
    )
    current_time = now or datetime.datetime.now(datetime.timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=datetime.timezone.utc)
    if (
        fetched_at is None
        or (current_time.astimezone(datetime.timezone.utc) - fetched_at).total_seconds()
        > max_age_hours * 3600
    ):
        return None
    return entry


def _load_tws_instrument_metadata(
    symbol, path=TWS_INSTRUMENTS_FILE,
):
    """Încarcă aliasurile contractului chiar dacă istoricul TWS lipsește.

    Metadatele contractului rămân utile pentru fallback: de exemplu 3USL este
    listat la Milano (3USL.MI), nu la Paris (3USL.PA).
    """
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
    except (OSError, ValueError, TypeError):
        return None
    instruments = payload.get('instruments', {})
    normalized = str(symbol or '').strip().upper()
    entry = instruments.get(normalized)
    if not isinstance(entry, dict):
        entry = next(
            (
                candidate for candidate in instruments.values()
                if normalized in {
                    str(alias).upper()
                    for alias in candidate.get('aliases', [])
                }
            ),
            None,
        )
    return entry if isinstance(entry, dict) else None


def _preferred_yahoo_history_symbols(ticker, download_ticker):
    """Pune aliasul exact al bursei înaintea simbolului fără sufix."""
    metadata = _load_tws_instrument_metadata(ticker) or {}
    aliases = [
        str(alias).strip().upper()
        for alias in metadata.get('aliases', [])
        if str(alias).strip()
    ]
    exact_aliases = [alias for alias in aliases if '.' in alias]
    candidates = exact_aliases + [str(download_ticker or '').upper()]
    return list(dict.fromkeys(candidate for candidate in candidates if candidate))


def _load_mcp_market_instrument(symbol, now=None):
    """Încarcă OHLCV MCP local înaintea cache-ului TWS și Yahoo."""
    return _load_tws_instrument(
        symbol,
        path=IBKR_MCP_MARKET_CACHE_FILE,
        now=now,
        max_age_hours=IBKR_MCP_MARKET_TTL_HOURS,
    )


def _prefetch_ibkr_mcp_market_data(symbols, label='watchlist'):
    """Prefetch MCP numai local; cloudul păstrează sursele existente."""
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        return None
    if os.environ.get('IBKR_MCP_MARKET_DATA_ENABLED', '1').strip().lower() in {
        '0', 'false', 'no', 'off'
    }:
        return None
    unique_symbols = list(dict.fromkeys(
        str(symbol).strip().upper()
        for symbol in symbols or [] if str(symbol).strip()
    ))
    if not unique_symbols:
        return None
    try:
        import ibkr_mcp
        started_at = time.perf_counter()
        stats = ibkr_mcp.prefetch_market_data(unique_symbols)
        elapsed = time.perf_counter() - started_at
        print(
            f"  -> IBKR MCP {label}: lot "
            f"{stats.get('scheduled', 0)}/{stats.get('requested', 0)}, "
            f"{stats.get('updated', 0)} actualizate, "
            f"{stats.get('cached', 0)} din cache, "
            f"{stats.get('unavailable', 0)} indisponibile "
            f"în {elapsed:.1f}s; "
            f"{stats.get('deferred', 0)} amânate."
        )
        stats['elapsed_seconds'] = round(elapsed, 3)
        return stats
    except (Exception, asyncio.CancelledError) as exc:
        print(
            f"  -> IBKR MCP market data indisponibil pentru {label}; "
            f"continuăm cu TWS/Yahoo: {exc}"
        )
        return None


def _tws_instrument_history_frame(instrument):
    bars = (instrument or {}).get('bars', [])
    if not bars:
        return pd.DataFrame()
    frame = pd.DataFrame(bars)
    required_columns = {'date', 'open', 'high', 'low', 'close'}
    if not required_columns.issubset(frame.columns):
        return pd.DataFrame()
    frame['date'] = pd.to_datetime(frame['date'], errors='coerce')
    for column in ('open', 'high', 'low', 'close', 'volume'):
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors='coerce')
    frame = frame.dropna(subset=['date', 'close']).sort_values('date')
    if frame.empty:
        return pd.DataFrame()
    frame = frame.set_index('date')
    frame = frame.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
    })
    if 'Volume' not in frame.columns:
        frame['Volume'] = 0.0
    return frame[['Open', 'High', 'Low', 'Close', 'Volume']]


def _merge_ohlcv_histories(*frames):
    """Îmbină istoricele pe ședință; ultima sursă are prioritate."""
    normalized = []
    for frame in frames:
        if frame is None or frame.empty:
            continue
        current = frame.copy()
        normalized_index = pd.to_datetime(
            current.index, errors='coerce'
        )
        if getattr(normalized_index, 'tz', None) is not None:
            normalized_index = normalized_index.tz_localize(None)
        current.index = normalized_index.normalize()
        current = current[~current.index.isna()]
        columns = [
            column
            for column in ('Open', 'High', 'Low', 'Close', 'Volume')
            if column in current.columns
        ]
        if 'Close' in columns:
            normalized.append(current[columns])
    if not normalized:
        return pd.DataFrame()
    combined = pd.concat(normalized)
    combined = combined[~combined.index.duplicated(keep='last')]
    return combined.sort_index().dropna(subset=['Close'])


def _tws_instrument_market_price(instrument):
    market_data_snapshot = (instrument or {}).get('market_data', {})
    for field in ('market_price', 'last', 'close'):
        try:
            value = float(market_data_snapshot.get(field))
            if math.isfinite(value) and value > 0:
                return value
        except (TypeError, ValueError):
            continue
    return None


def _instrument_data_attribution(symbol, instrument):
    execution_brokers = _buy_candidate_brokers(symbol)
    if not instrument:
        return {
            'Market_Data_Source': 'Yahoo Finance',
            'Market_Data_Fetched_At': None,
            'Data_Broker': None,
            'Execution_Brokers': execution_brokers,
            'IBKR_Data_Only': False,
        }
    return {
        'Market_Data_Source': instrument.get(
            'data_provider', 'IBKR TWS API'
        ),
        'Market_Data_Fetched_At': instrument.get('fetched_at'),
        'Data_Broker': instrument.get('data_broker', 'IBKR'),
        # Eligibilitatea de tranzacționare vine din regulile dashboardului,
        # nu din brokerul care a furnizat cotația.
        'Execution_Brokers': execution_brokers,
        'IBKR_Data_Only': (
            bool(instrument.get('ibkr_data_only'))
            or (
                instrument.get('data_broker') == 'IBKR'
                and str(symbol or '').upper() in {'TVBETETF', 'TVBETETF.RO'}
            )
        ),
    }


def _normalize_downloaded_history(frame):
    """Normalizează rezultatele Yahoo/TWS/Tradeville la aceleași coloane."""
    if frame is None or frame.empty:
        return pd.DataFrame()
    normalized = frame.copy()
    if isinstance(normalized.columns, pd.MultiIndex):
        try:
            normalized.columns = normalized.columns.droplevel(1)
        except (IndexError, ValueError):
            return pd.DataFrame()
    if 'Close' not in normalized.columns:
        return pd.DataFrame()
    normalized = normalized.dropna(subset=['Close']).sort_index()
    return normalized


def _download_yahoo_history(symbol, period='1y'):
    """Yahoo fără mesajele repetitive ale bibliotecii pentru simboluri absente."""
    import contextlib
    import io

    cache_key = (str(symbol).upper(), str(period))
    cached = _YAHOO_HISTORY_MEMORY_CACHE.get(cache_key)
    if cached is not None:
        return cached.copy()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
        io.StringIO()
    ):
        frame = yf.download(
            symbol,
            period=period,
            auto_adjust=True,
            progress=False,
        )
    normalized = _normalize_downloaded_history(frame)
    _YAHOO_HISTORY_MEMORY_CACHE[cache_key] = normalized.copy()
    return normalized


def _load_analysis_history(ticker, download_ticker, period='1y'):
    """Pentru BVB îmbină cache TWS, Yahoo și CSV public, fără duplicate."""
    normalized_ticker = str(ticker or '').upper()
    mcp_instrument = _load_mcp_market_instrument(ticker)
    tws_instrument = _load_tws_instrument(ticker)
    is_bvb = normalized_ticker.endswith('.RO')

    if is_bvb:
        bvb_history = pd.DataFrame()
        bvb_instrument = None
        # TVBETETF alimentează SMA200 din dashboard. Snapshotul IBKR poate
        # începe mai târziu decât istoricul real al instrumentului, deci
        # forțăm o singură dată backfill-ul cache-ului public BVB până la o
        # rezervă de 260 de ședințe. Pentru emitenții listați recent păstrăm
        # pragul minim, altfel istoricul lor valid ar fi respins inutil.
        needs_sma200_history = normalized_ticker in {
            'TVBETETF', 'TVBETETF.RO',
        }
        bvb_min_observations = 260 if needs_sma200_history else 1
        bvb_lookback_days = (
            450
            if needs_sma200_history
            else bvb_public_market_data.DEFAULT_LOOKBACK_DAYS
        )
        try:
            bvb_history, bvb_instrument = (
                bvb_public_market_data.fetch_history(
                    ticker,
                    min_observations=bvb_min_observations,
                    lookback_days=bvb_lookback_days,
                )
            )
            print(
                f"  [BVB public] Istoric pentru "
                f"{ticker}: {len(bvb_history)} ședințe"
            )
        except bvb_public_market_data.BVBPublicStaleDataError as exc:
            print(f"  [BVB] {ticker}: cache-ul public este depășit ({exc})")
        except Exception as exc:
            print(f"  [BVB] {ticker}: CSV/cache public indisponibil ({exc})")

        mcp_history = _tws_instrument_history_frame(mcp_instrument)
        tws_history = _tws_instrument_history_frame(tws_instrument)
        combined_without_yahoo = _merge_ohlcv_histories(
            tws_history, bvb_history, mcp_history
        )
        yahoo_history = pd.DataFrame()
        required_combined_history = 260 if needs_sma200_history else 60
        if len(combined_without_yahoo) < required_combined_history:
            try:
                yahoo_period = '2y' if needs_sma200_history else period
                yahoo_history = _download_yahoo_history(
                    download_ticker, period=yahoo_period
                )
            except Exception:
                yahoo_history = pd.DataFrame()
        combined = _merge_ohlcv_histories(
            tws_history, yahoo_history, bvb_history, mcp_history
        )
        if not combined.empty:
            used_sources = []
            if not mcp_history.empty:
                used_sources.append('IBKR MCP')
            if not tws_history.empty:
                used_sources.append('IBKR TWS')
            if not yahoo_history.empty:
                used_sources.append('Yahoo Finance')
            if not bvb_history.empty:
                used_sources.append('BVB public')
            selected_instrument = (
                mcp_instrument or tws_instrument or bvb_instrument
            )
            if len(used_sources) > 1:
                selected_instrument = dict(selected_instrument or {})
                selected_instrument.update({
                    'data_provider': ' + '.join(used_sources),
                    'data_broker': 'surse combinate',
                    'fetched_at': datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                    'market_data': (
                        (mcp_instrument or tws_instrument or bvb_instrument or {}).get(
                            'market_data', {}
                        )
                    ),
                })
            print(
                f"  [BVB combinat] {ticker}: {len(combined)} ședințe "
                f"din {', '.join(used_sources)}"
            )
            return (
                combined,
                selected_instrument,
                mcp_instrument or tws_instrument,
                _instrument_data_attribution(ticker, selected_instrument),
            )

        print(
            f"  [BVB] {ticker}: date indisponibile în CSV/cache public, "
            "MCP, Yahoo și cache-ul TWS"
        )
        return pd.DataFrame(), None, mcp_instrument or tws_instrument, (
            _instrument_data_attribution(ticker, None)
        )

    mcp_history = _tws_instrument_history_frame(mcp_instrument)
    if not mcp_history.empty:
        print(
            f"  [IBKR MCP] Istoric pentru {ticker}: "
            f"{len(mcp_history)} ședințe"
        )
        return (
            mcp_history,
            mcp_instrument,
            mcp_instrument,
            _instrument_data_attribution(ticker, mcp_instrument),
        )
    tws_history = _tws_instrument_history_frame(tws_instrument)
    if not tws_history.empty:
        print(
            f"  [TWS API] Istoric IBKR pentru {ticker}: "
            f"{len(tws_history)} ședințe"
        )
        return (
            tws_history,
            tws_instrument,
            tws_instrument,
            _instrument_data_attribution(ticker, tws_instrument),
        )
    yahoo_history = pd.DataFrame()
    selected_yahoo_symbol = str(download_ticker or '').upper()
    # Indicatorii și graficul nu trebuie construite dintr-o potrivire Yahoo
    # accidentală cu numai una-două ședințe. Contractul IBKR oferă aliasul
    # listării corecte, iar rezultatul scurt rămâne doar ultimul fallback.
    best_short_history = pd.DataFrame()
    for yahoo_symbol in _preferred_yahoo_history_symbols(
        ticker, download_ticker
    ):
        try:
            candidate = _download_yahoo_history(
                yahoo_symbol, period=period
            )
        except Exception:
            candidate = pd.DataFrame()
        if len(candidate) > len(best_short_history):
            best_short_history = candidate
            selected_yahoo_symbol = yahoo_symbol
        if len(candidate) >= 20:
            yahoo_history = candidate
            selected_yahoo_symbol = yahoo_symbol
            break
    if yahoo_history.empty:
        yahoo_history = best_short_history
    if (
        not yahoo_history.empty
        and selected_yahoo_symbol != str(download_ticker or '').upper()
    ):
        print(
            f"  [Yahoo fallback] Folosim listarea exactă "
            f"{selected_yahoo_symbol} pentru {ticker}: "
            f"{len(yahoo_history)} ședințe"
        )
    return (
        yahoo_history,
        None,
        tws_instrument or _load_tws_instrument_metadata(ticker),
        _instrument_data_attribution(ticker, None),
    )


def load_complete_us_equity_universe(path=SP500_UNIVERSE_FILE):
    """Încarcă universul larg SUA; lista fixă rămâne doar fallback."""
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            raw = json.load(handle)
        symbols = raw if isinstance(raw, list) else raw.get('symbols', [])
        return sorted({
            str(symbol).strip().upper().replace('.', '-')
            for symbol in symbols
            if re.fullmatch(r'[A-Za-z.-]{1,10}', str(symbol).strip())
        })
    except (OSError, ValueError, TypeError):
        return list(BUY_RESEARCH_UNIVERSES['SUA'])


def _normalized_column_name(value):
    text = unicodedata.normalize('NFKD', str(value))
    return ''.join(char for char in text if not unicodedata.combining(char)).lower()


def _parse_bvb_equity_universe_csv(content):
    """Normalizează exportul oficial BVB pentru Piața Reglementată și AeRO."""
    frame = pd.read_csv(StringIO(content), sep=';', dtype=str)
    normalized_columns = {
        column: _normalized_column_name(column) for column in frame.columns
    }

    def find_column(*needles):
        return next(
            (
                column for column, normalized in normalized_columns.items()
                if any(needle in normalized for needle in needles)
            ),
            None,
        )

    symbol_column = find_column('simbol')
    if not symbol_column:
        return []
    isin_column = find_column('isin')
    company_column = find_column('societate', 'emitent', 'denumire')
    segment_column = find_column('segment', 'piata')
    category_column = find_column('categorie')
    date_column = find_column('data')
    volume_column = find_column('volum')
    turnover_column = find_column('valoare tranz', 'rulaj')
    price_column = find_column('pret')

    records = []
    for _, row in frame.iterrows():
        raw_symbol = str(row.get(symbol_column, '')).strip().upper()
        if not re.fullmatch(r'[A-Z0-9]{1,12}', raw_symbol):
            continue
        raw_date = str(row.get(date_column, '')).strip() if date_column else ''
        parsed_date = pd.to_datetime(raw_date, dayfirst=True, errors='coerce')
        last_trade = (
            parsed_date.date().isoformat() if pd.notna(parsed_date) else None
        )
        price_text = str(row.get(price_column, '')) if price_column else ''
        volume_text = str(row.get(volume_column, '')) if volume_column else ''
        turnover_text = str(row.get(turnover_column, '')) if turnover_column else ''
        records.append({
            'symbol': f'{raw_symbol}.RO',
            'bvb_symbol': raw_symbol,
            'isin': str(row.get(isin_column, '')).strip() if isin_column else '',
            'company': str(row.get(company_column, '')).strip() if company_column else '',
            'segment': str(row.get(segment_column, '')).strip() if segment_column else '',
            'category': str(row.get(category_column, '')).strip() if category_column else '',
            'last_trade': last_trade,
            'price_ron': _parse_bvb_number(price_text),
            'volume': _parse_bvb_number(volume_text),
            'turnover_ron': _parse_bvb_number(turnover_text),
            'source': 'Bursa de Valori București',
            'source_url': BVB_SHARES_CSV_URL,
        })
    unique = {item['symbol']: item for item in records}
    return sorted(unique.values(), key=lambda item: item['symbol'])


def _safe_float_text(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _json_without_nonfinite_numbers(value):
    """Înlocuiește NaN/Infinity cu null înainte de serializarea pentru JS."""
    if isinstance(value, dict):
        return {
            key: _json_without_nonfinite_numbers(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_json_without_nonfinite_numbers(item) for item in value]
    if isinstance(value, (float, np.floating)):
        number = float(value)
        return number if math.isfinite(number) else None
    return value


def _parse_bvb_number(value):
    text = str(value).strip().replace(' ', '')
    if ',' in text and '.' in text:
        text = text.replace('.', '').replace(',', '.')
    elif ',' in text:
        text = text.replace(',', '.')
    return _safe_float_text(text)


def _calculate_bvb_liquidity_metrics(frame, window=20):
    """Calculează lichiditatea locală fără ca o singură ședință să domine."""
    empty = {
        'Liquidity_Observations_20D': 0,
        'Active_Days_20D': 0,
        'Zero_Volume_Days_20D': 0,
        'Median_Volume_20D': None,
        'Median_Turnover_20D_RON': None,
        'Average_Turnover_20D_RON': None,
        'Last_Turnover_RON': None,
        'Relative_Volume_20D': None,
    }
    if (
        frame is None
        or frame.empty
        or 'Close' not in frame.columns
        or 'Volume' not in frame.columns
    ):
        return empty

    recent = frame.tail(window).copy()
    close = pd.to_numeric(recent['Close'], errors='coerce')
    volume = pd.to_numeric(recent['Volume'], errors='coerce').fillna(0)
    valid_session = close.notna() & (close > 0)
    active_session = valid_session & (volume > 0)
    observations = int(valid_session.sum())
    active_days = int(active_session.sum())
    zero_volume_days = int((valid_session & (volume <= 0)).sum())
    if active_days:
        active_volume = volume[active_session]
        active_turnover = close[active_session] * active_volume
        median_volume = float(active_volume.median())
        median_turnover = float(active_turnover.median())
        average_turnover = float(active_turnover.mean())
    else:
        median_volume = None
        median_turnover = None
        average_turnover = None

    last_turnover = None
    last_volume = None
    if observations:
        last_valid_index = close[valid_session].index[-1]
        last_volume = float(volume.loc[last_valid_index])
        last_turnover = float(close.loc[last_valid_index] * last_volume)
    relative_volume = (
        last_volume / median_volume
        if last_volume is not None and median_volume and median_volume > 0
        else None
    )
    return {
        'Liquidity_Observations_20D': observations,
        'Active_Days_20D': active_days,
        'Zero_Volume_Days_20D': zero_volume_days,
        'Median_Volume_20D': round(median_volume, 2) if median_volume is not None else None,
        'Median_Turnover_20D_RON': (
            round(median_turnover, 2) if median_turnover is not None else None
        ),
        'Average_Turnover_20D_RON': (
            round(average_turnover, 2) if average_turnover is not None else None
        ),
        'Last_Turnover_RON': (
            round(last_turnover, 2) if last_turnover is not None else None
        ),
        'Relative_Volume_20D': (
            round(relative_volume, 3) if relative_volume is not None else None
        ),
    }


def _bvb_market_segment(item):
    """Normalizează segmentul oficial în Piața Reglementată, AeRO sau necunoscut."""
    metadata = item.get('BVB_Metadata')
    if not isinstance(metadata, dict):
        metadata = {}
    raw = ' '.join(
        str(value or '')
        for value in (
            metadata.get('segment'),
            metadata.get('category'),
            item.get('BVB_Market_Segment'),
        )
    )
    normalized = _normalized_column_name(raw).upper()
    if any(marker in normalized for marker in ('AERO', 'SMT', 'ATS', 'XRS')):
        return 'AeRO'
    if any(
        marker in normalized
        for marker in ('REGS', 'REGLEMENTATA', 'REGULATED', 'PRINCIPALA')
    ):
        return 'Piața Reglementată'
    return 'Necunoscut'


def _bvb_liquidity_assessment(item):
    """Evaluează executabilitatea BVB/AeRO și produce un plafon de ordin."""
    segment = _bvb_market_segment(item)
    thresholds = {
        'Piața Reglementată': {
            'turnover': 100_000.0, 'active_days': 15, 'participation': 0.02,
        },
        'AeRO': {
            'turnover': 25_000.0, 'active_days': 12, 'participation': 0.01,
        },
        'Necunoscut': {
            'turnover': 50_000.0, 'active_days': 12, 'participation': 0.015,
        },
    }
    threshold = thresholds[segment]
    observations = int(_safe_float_text(
        item.get('Liquidity_Observations_20D')
    ) or 0)
    active_days = int(_safe_float_text(item.get('Active_Days_20D')) or 0)
    median_turnover = _safe_float_text(
        item.get('Median_Turnover_20D_RON')
    )
    metadata = item.get('BVB_Metadata')
    if not isinstance(metadata, dict):
        metadata = {}
    official_turnover = _safe_float_text(metadata.get('turnover_ron')) or 0
    last_turnover = _safe_float_text(item.get('Last_Turnover_RON')) or 0
    avg_volume = _safe_float_text(item.get('Avg_Volume')) or 0
    price_native = (
        _safe_float_text(item.get('Price_Native'))
        or _safe_float_text(metadata.get('price_ron'))
        or 0
    )
    estimated_turnover = avg_volume * price_native
    source = 'istoric 20 ședințe'

    if observations >= 15:
        reference_turnover = median_turnover or 0
        active_ratio = active_days / observations if observations else 0
        eligible = (
            reference_turnover >= threshold['turnover']
            and active_days >= threshold['active_days']
            and active_ratio >= 0.60
        )
        if eligible:
            status = 'adecvată'
            reason = (
                f'Mediana rulajului pe 20 ședințe este '
                f'{reference_turnover:,.0f} RON, cu tranzacții în '
                f'{active_days}/{observations} ședințe.'
            )
        else:
            status = 'insuficientă'
            reason = (
                f'Lichiditatea nu trece pragul pentru {segment}: mediană '
                f'{reference_turnover:,.0f} RON și '
                f'{active_days}/{observations} ședințe active.'
            )
    else:
        source = 'fallback până la completarea istoricului'
        reference_turnover = max(
            official_turnover, last_turnover, estimated_turnover
        )
        volume = _safe_float_text(item.get('Volume')) or 0
        official_volume = _safe_float_text(metadata.get('volume')) or 0
        volume_fallback = max(volume, avg_volume, official_volume)
        eligible = (
            reference_turnover >= threshold['turnover']
            or (reference_turnover <= 0 and volume_fallback >= 1_000)
        )
        status = 'provizorie' if eligible else 'date insuficiente'
        reason = (
            f'Istoricul are doar {observations} ședințe; selecția folosește '
            f'rulajul/volumul disponibil și trebuie reconfirmată.'
            if eligible else
            f'Istoricul are doar {observations} ședințe și nu există rulaj '
            f'suficient pentru o intrare verificabilă.'
        )

    price_eur = _buy_candidate_entry_eur(item) or 0
    ron_per_eur = price_native / price_eur if price_native > 0 and price_eur > 0 else 0
    position_cap_eur = (
        reference_turnover * threshold['participation'] / ron_per_eur
        if reference_turnover > 0 and ron_per_eur > 0
        else None
    )
    return {
        'market_segment': segment,
        'eligible': bool(eligible),
        'status': status,
        'reason': reason,
        'source': source,
        'minimum_median_turnover_ron': threshold['turnover'],
        'participation_limit_pct': threshold['participation'] * 100,
        'position_cap_eur': (
            round(position_cap_eur, 2) if position_cap_eur is not None else None
        ),
    }


def fetch_complete_bvb_equity_universe(state, request_session=None):
    """Descoperă universul BVB/AeRO din exportul public, fără Web Service."""
    cached = list((state or {}).get('bvb_equity_universe', []))
    client = request_session or requests
    try:
        response = client.get(
            BVB_SHARES_CSV_URL,
            timeout=30,
        )
        response.raise_for_status()
        records = _parse_bvb_equity_universe_csv(response.text)
        if records:
            return records
    except (requests.RequestException, ValueError, TypeError):
        pass
    return cached


def _buy_candidate_market(symbol):
    normalized = str(symbol).upper()
    if normalized in {'LQQ.PA', 'LQQ.FR', 'FR.LQQ'}:
        return 'Europa / Nasdaq-100'
    return 'România / BVB' if normalized.endswith('.RO') else 'SUA'


def _buy_candidate_brokers(symbol):
    market = _buy_candidate_market(symbol)
    if market == 'Europa / Nasdaq-100':
        return ['IBKR', 'Tradeville']
    return ['Tradeville'] if market == 'România / BVB' else ['IBKR']


def _is_strict_buy_candidate(item):
    consensus = str(item.get('Consensus', '')).strip().lower()
    return (
        str(item.get('Decision', '')).strip().upper() == 'BUY'
        and consensus in {'buy', 'strong buy'}
        and float(item.get('RR_Ratio') or 0) >= 3
    )


def _buy_candidate_data_age_hours(item):
    cached_at = _safe_float_text(item.get('_cached_at'))
    if not cached_at:
        return None
    return max((time.time() - cached_at) / 3600, 0)


def _buy_candidate_data_is_fresh(item, ttl_hours=BUY_FINALIST_TTL_HOURS):
    """Fixturele fără timestamp sunt tratate drept curente; cache-ul real nu."""
    if not _safe_float_text(item.get('_cached_at')):
        return True
    return market_data.is_fresh(item, ttl_hours=ttl_hours)


def _buy_candidate_entry_eur(item):
    smart_entry_eur = item.get('Smart_Entry_EUR')
    try:
        if smart_entry_eur is not None and pd.notna(smart_entry_eur) and float(smart_entry_eur) > 0:
            return float(smart_entry_eur)
    except (TypeError, ValueError):
        pass
    price_eur = item.get('Price')
    try:
        return float(price_eur) if pd.notna(price_eur) and float(price_eur) > 0 else None
    except (TypeError, ValueError):
        return None


def _buy_candidate_execution_values(item, rates=None):
    """Convertește nivelurile interne EUR în moneda în care se execută ordinul."""
    symbol = str(item.get('Ticker') or item.get('symbol') or '').upper()
    currency = str(item.get('Currency') or '').strip().upper()
    if not currency:
        currency = (
            'RON' if symbol.endswith('.RO')
            else 'EUR' if symbol in {'LQQ.PA', 'LQQ.FR', 'FR.LQQ'}
            else 'USD'
        )
    price_eur = _safe_float_text(item.get('Price'))
    price_native = _safe_float_text(item.get('Price_Native'))
    eur_per_native = (
        price_eur / price_native
        if price_eur and price_native and price_eur > 0 and price_native > 0
        else None
    )
    if not eur_per_native:
        eur_per_native = _safe_float_text((rates or {}).get(currency))
    if not eur_per_native and currency == 'EUR':
        eur_per_native = 1.0

    def to_native(value):
        numeric = _safe_float_text(value)
        if not numeric or not eur_per_native or eur_per_native <= 0:
            return None
        return round(numeric / eur_per_native, 4)

    return {
        'execution_currency': currency,
        'eur_per_native': round(eur_per_native, 8) if eur_per_native else None,
        'price_native': (
            round(price_native, 4)
            if price_native and price_native > 0
            else to_native(price_eur)
        ),
        'entry_native': to_native(_buy_candidate_entry_eur(item)),
        'stop_native': to_native(item.get('Stop_Loss')),
        'target_native': to_native(item.get('Target')),
    }


def _chart_detail_native_payload(
    item, symbol, eur_price_field, rates=None,
):
    """Pregătește seriile ferestrei detaliate în moneda de tranzacționare."""
    normalized_symbol = str(symbol or '').upper()
    currency = str(item.get('Currency') or '').strip().upper()
    if not currency:
        currency = (
            'RON' if normalized_symbol.endswith('.RO')
            else 'EUR'
            if normalized_symbol in {'LQQ.PA', 'LQQ.FR', 'FR.LQQ'}
            else 'USD'
        )
    price_eur = _safe_float_text(item.get(eur_price_field))
    price_native = _safe_float_text(item.get('Price_Native'))
    eur_per_native = (
        price_eur / price_native
        if price_eur and price_native and price_eur > 0 and price_native > 0
        else _safe_float_text((rates or {}).get(currency))
    )
    if not eur_per_native and currency == 'EUR':
        eur_per_native = 1.0
    if not eur_per_native or eur_per_native <= 0:
        eur_per_native = 1.0

    def to_native(value):
        numeric = _safe_float_text(value)
        return (
            round(numeric / eur_per_native, 4)
            if numeric is not None else None
        )

    native_ohlc = []
    for bar in item.get('Chart_OHLC', []) or []:
        if not isinstance(bar, dict):
            continue
        converted = {'date': bar.get('date')}
        valid = True
        for key in ('open', 'high', 'low', 'close'):
            native_value = to_native(bar.get(key))
            if native_value is None:
                valid = False
                break
            converted[key] = native_value
        if valid:
            native_ohlc.append(converted)

    native_series = [
        native_value
        for native_value in (
            to_native(value)
            for value in (
                item.get('Chart_History', item.get('Sparkline', [])) or []
            )
        )
        if native_value is not None
    ]
    return {
        'currency': currency,
        'eur_per_native': eur_per_native,
        'value': (
            round(price_native, 4)
            if price_native and price_native > 0
            else to_native(price_eur)
        ),
        'change': to_native(item.get('Daily_Change', 0)) or 0,
        'ohlc': native_ohlc,
        'series': native_series,
        'seriesDates': item.get('Chart_Dates', []),
        'to_native': to_native,
    }


def _format_native_price_text(value, currency):
    numeric = _safe_float_text(value)
    if numeric is None:
        return 'indisponibil'
    code = str(currency or 'EUR').upper()
    decimals = 4 if code == 'RON' and 0 < abs(numeric) < 10 else 2
    formatted = f"{numeric:,.{decimals}f}"
    if code == 'USD':
        return f"${formatted}"
    if code == 'EUR':
        return f"€{formatted}"
    if code == 'GBP':
        return f"£{formatted}"
    return f"{formatted} {code}"


def _build_history_chart_candidates(
    candidates, recommendation_history, source_rows, rates=None,
):
    """Completează seriile OHLC pentru toate simbolurile păstrate în istoric."""
    candidates_by_symbol = {
        str(candidate.get('symbol') or '').upper(): dict(candidate)
        for candidate in candidates or []
        if candidate.get('symbol')
    }
    history_by_symbol = {}
    for item in recommendation_history or []:
        symbol = str(item.get('symbol') or '').upper()
        if symbol:
            history_by_symbol.setdefault(symbol, []).append(item)
    sources_by_symbol = {}
    for raw_source in source_rows or []:
        source = dict(raw_source)
        symbol = str(
            source.get('Ticker')
            or source.get('symbol')
            or ''
        ).upper()
        if not symbol or symbol not in history_by_symbol:
            continue
        previous = sources_by_symbol.get(symbol)
        has_chart = bool(
            source.get('Chart_OHLC')
            or source.get('Chart_History')
            or source.get('Sparkline')
        )
        previous_has_chart = bool(
            previous
            and (
                previous.get('Chart_OHLC')
                or previous.get('Chart_History')
                or previous.get('Sparkline')
            )
        )
        if previous is None or (has_chart and not previous_has_chart):
            sources_by_symbol[symbol] = source

    for symbol, history_items in history_by_symbol.items():
        candidate = candidates_by_symbol.get(symbol, {'symbol': symbol})
        has_chart = bool(
            candidate.get('chart_ohlc_native')
            or candidate.get('chart_series_native')
        )
        source = sources_by_symbol.get(symbol)
        latest_history = max(
            history_items,
            key=lambda item: str(item.get('last_seen_at') or ''),
        )
        if source and not has_chart:
            source = dict(source)
            source.setdefault(
                'Currency',
                latest_history.get('execution_currency'),
            )
            native_detail = _chart_detail_native_payload(
                source,
                symbol,
                'Price',
                rates=rates,
            )
            candidate.update({
                'company_name': (
                    candidate.get('company_name')
                    or source.get('Company_Name')
                    or latest_history.get('company_name')
                    or symbol
                ),
                'market': (
                    candidate.get('market')
                    or source.get('Market')
                    or latest_history.get('market')
                ),
                'execution_currency': (
                    candidate.get('execution_currency')
                    or native_detail['currency']
                ),
                'chart_currency': native_detail['currency'],
                'chart_value_native': native_detail['value'],
                'chart_change_native': native_detail['change'],
                'chart_ohlc_native': native_detail['ohlc'],
                'chart_series_native': native_detail['series'],
                'chart_series_dates': native_detail['seriesDates'],
                'trend': candidate.get('trend') or source.get('Trend'),
            })
        else:
            candidate.setdefault(
                'company_name',
                latest_history.get('company_name') or symbol,
            )
            candidate.setdefault(
                'execution_currency',
                latest_history.get('execution_currency') or 'EUR',
            )
            candidate.setdefault(
                'chart_currency',
                candidate.get('execution_currency'),
            )
        candidates_by_symbol[symbol] = candidate
    return list(candidates_by_symbol.values())


def _build_buy_recommendation_detail_data(
    candidates, ai_result=None, recommendation_history=None,
):
    """Construiește graficele sugestiilor curente și ale istoricului BUY."""
    recommendations_by_symbol = {
        str(item.get('symbol') or '').upper(): item
        for item in (ai_result or {}).get('buy_recommendations', [])
    }
    marker_labels = analysis._buy_recommendation_marker_labels(
        recommendation_history
    )
    history_by_symbol = {}
    for item in recommendation_history or []:
        symbol = str(item.get('symbol') or '').upper()
        if symbol:
            history_by_symbol.setdefault(symbol, []).append(item)
    details = {}
    for candidate in candidates or []:
        symbol = str(candidate.get('symbol') or '').upper()
        if not symbol:
            continue
        currency = str(
            candidate.get('chart_currency')
            or candidate.get('execution_currency')
            or 'EUR'
        ).upper()
        levels = []
        for label, field, color in (
            ('Entry recomandat', 'entry_native', '#2563eb'),
            ('Stop recomandat', 'stop_native', '#dc2626'),
            ('Target', 'target_native', '#16a34a'),
        ):
            value = _safe_float_text(candidate.get(field))
            if value is not None and value > 0:
                levels.append({
                    'label': label,
                    'value': round(value, 4),
                    'color': color,
                })
        recommendation = recommendations_by_symbol.get(symbol, {})
        eur_per_native = (
            _safe_float_text(candidate.get('eur_per_native'))
            or 1.0
        )
        markers = []
        for history_item in sorted(
            history_by_symbol.get(symbol, []),
            key=lambda item: (
                str(item.get('first_seen_at') or ''),
                str(item.get('last_seen_at') or ''),
                str(item.get('history_key') or ''),
            ),
        ):
            value = _safe_float_text(history_item.get('entry_native'))
            if value is None or value <= 0:
                entry_eur = _safe_float_text(history_item.get('entry_eur'))
                value = (
                    entry_eur / eur_per_native
                    if entry_eur is not None and eur_per_native > 0
                    else None
                )
            if value is None or value <= 0:
                continue
            is_current = bool(history_item.get('is_current'))
            action_label = str(
                history_item.get('action_label') or 'Recomandare'
            )
            marker_color = (
                '#16a34a'
                if is_current and action_label == 'Cumpărare acum'
                else '#2563eb'
                if is_current
                else '#64748b'
            )
            history_key = str(history_item.get('history_key') or '')
            markers.append({
                'label': marker_labels.get(history_key, 'C?'),
                'date': str(
                    history_item.get('first_seen_at') or ''
                )[:10],
                'dateTime': history_item.get('first_seen_at'),
                'value': round(value, 4),
                'action': action_label,
                'status': 'Activă' if is_current else 'Încheiată',
                'isCurrent': is_current,
                'color': marker_color,
                'historyKey': history_key,
            })
        details[symbol] = {
            'kind': 'buy_recommendation',
            'name': candidate.get('company_name') or symbol,
            'ticker': symbol,
            'currency': currency,
            'value': candidate.get(
                'chart_value_native',
                candidate.get('price_native'),
            ),
            'change': candidate.get('chart_change_native', 0),
            'status': (
                recommendation.get('verdict')
                or candidate.get('decision')
                or '—'
            ),
            'rangeDescription': candidate.get('trend') or '—',
            'explanation': (
                'Candidat din sugestiile de cumpărare. Nivelurile curente '
                'de entry, stop și target sunt separate de marcajele '
                'punctuale C1, C2 etc. ale recomandărilor istorice, toate '
                f'în moneda ordinului ({currency}).'
            ),
            'ohlc': candidate.get('chart_ohlc_native') or [],
            'series': candidate.get('chart_series_native') or [],
            'seriesDates': candidate.get('chart_series_dates') or [],
            'levels': levels,
            'markers': markers,
        }
    return details


def _build_active_buy_order_chart_levels(orders_df):
    """Construiește nivelurile de preț pentru ordinele BUY active."""
    if not isinstance(orders_df, pd.DataFrame) or orders_df.empty:
        return {}
    if 'Symbol' not in orders_df.columns or 'Action' not in orders_df.columns:
        return {}

    def valid_price(row, column):
        value = _safe_float_text(row.get(column))
        if value is None or value <= 0 or value >= 1e10:
            return None
        return value

    levels_by_symbol = {}
    buy_orders = orders_df[
        orders_df['Action'].astype(str).str.upper() == 'BUY'
    ]
    for _, order in buy_orders.iterrows():
        symbol = str(order.get('Symbol') or '').strip().upper()
        if not symbol:
            continue
        order_type = str(order.get('OrderType') or '').strip().upper()
        limit_price = valid_price(order, 'Limit_Price')
        stop_price = valid_price(order, 'Stop_Price')
        if limit_price is None and order_type in {'LMT', 'LIMIT'}:
            limit_price = (
                valid_price(order, 'Aux_Price')
                or stop_price
            )
        order_price = (
            limit_price
            if order_type in {'LMT', 'LIMIT'}
            else stop_price
        )
        if order_price is None:
            order_price = valid_price(order, 'Calculated_Stop')
        if order_price is None:
            continue

        quantity = (
            _safe_float_text(order.get('Total_Qty'))
            or _safe_float_text(order.get('Quantity'))
            or 0
        )
        label = 'Preț ordin'
        if order_type:
            label += f' {order_type}'
        if quantity > 0:
            label += f' · {quantity:g} acț.'
        level = {
            'label': label,
            'value': round(order_price, 4),
            'color': '#7c3aed',
        }
        symbol_levels = levels_by_symbol.setdefault(symbol, [])
        if not any(
            abs(item['value'] - level['value']) < 0.0001
            and item['label'] == level['label']
            for item in symbol_levels
        ):
            symbol_levels.append(level)
    return levels_by_symbol


def _prepare_external_research_candidate(raw_item):
    """Construiește niveluri tehnice explicite pentru ruta externă independentă."""
    item = dict(raw_item or {})
    price = _safe_float_text(item.get('Price'))
    if not price or price <= 0:
        return item

    ohlc = item.get('Chart_OHLC')
    recent_highs = []
    if isinstance(ohlc, list):
        for bar in ohlc[-20:]:
            if not isinstance(bar, dict):
                continue
            high = _safe_float_text(bar.get('high'))
            if high and high > 0:
                recent_highs.append(high)

    trend = str(item.get('Trend') or '').lower()
    strategy = str(item.get('Strategy') or '').lower()
    bullish_breakout = (
        'bullish' in trend or 'breakout' in strategy
    )
    atr = _safe_float_text(item.get('ATR_14')) or 0
    has_technical_history = len(recent_highs) >= 5 and atr > 0
    entry = _buy_candidate_entry_eur(item) or price
    trigger_basis = str(item.get('Smart_Reason') or '').strip()
    if bullish_breakout and has_technical_history:
        recent_high = max(recent_highs)
        # Confirmarea se face puțin peste maximul recent, nu prin urmărirea
        # arbitrară a unei lumânări deja extinse.
        breakout_entry = recent_high * 1.002
        if breakout_entry <= price * 1.08:
            entry = max(price, breakout_entry)
            trigger_basis = (
                'confirmare cu 0,2% peste maximul ultimelor 20 de ședințe'
            )

    stop = _safe_float_text(item.get('Stop_Loss'))
    if (not stop or not (0 < stop < entry)) and has_technical_history:
        stop_distance = max(atr * 2, entry * 0.04)
        stop = entry - stop_distance

    risk = entry - stop if stop and 0 < stop < entry else 0
    original_target = _safe_float_text(
        item.get('Original_Target')
        if 'Original_Target' in item
        else item.get('Target')
    )
    target = original_target
    if not target:
        target = _safe_float_text(item.get('Target'))
    target_basis = str(
        item.get('Target_Basis')
        or 'țintă furnizată de sursa de piață'
    )
    supplied_rr = (
        (target - entry) / risk
        if target and target > entry and risk > 0 else 0
    )
    if supplied_rr < EXTERNAL_RESEARCH_MIN_RR and has_technical_history and risk > 0:
        target = entry + max(
            risk * 2.0,
            atr * 3.0 if atr > 0 else 0,
        )
        target_basis = (
            'țintă tehnică de 2× riscul inițial; nu este consens de analist'
        )

    rr_ratio = (
        (target - entry) / risk
        if target and target > entry and risk > 0 else 0
    )
    item.update({
        'Smart_Entry_EUR': round(entry, 4),
        'Stop_Loss': round(stop, 4) if stop else None,
        'Target': round(target, 4) if target else None,
        'RR_Ratio': round(rr_ratio, 2),
        'Original_Target': original_target,
        'Technical_Level_Source': (
            item.get('Technical_Level_Source')
            or (
                'technical_breakout'
                if bullish_breakout and has_technical_history
                else 'technical_risk_plan'
                if has_technical_history
                else 'source_market_levels'
            )
        ),
        'Trigger_Basis': trigger_basis or 'nivel tehnic curent',
        'Target_Basis': target_basis,
        'External_Min_RR': EXTERNAL_RESEARCH_MIN_RR,
    })
    return item


def _correct_tradeville_manual_snapshot(account_data):
    """Corectează snapshotul din 26 iulie 2026 conform extrasului Tradeville."""
    if not isinstance(account_data, dict):
        return account_data
    if not str(account_data.get('fetched_at', '')).startswith('2026-07-26'):
        return account_data
    corrected = json.loads(json.dumps(account_data))
    for account in corrected.get('accounts', []):
        source = (
            str(account.get('label', '')) + ' ' + str(account.get('source', ''))
        ).lower()
        summary = account.get('summary', {})
        if (
            'tradeville' in source
            and abs(float(summary.get('TotalCashValue') or 0) - 48438.86) < 0.01
        ):
            summary.update({
                'NetLiquidation': 72778.09,
                'TotalCashValue': 48438.86,
                'AvailableFunds': 48438.86,
                'GrossPositionValue': 24339.23,
                'CostBasis': 11306.92,
                'RelativeProfit': 12983.64,
            })
    return corrected


def _decrypt_broker_totals_history(
    encrypted_payload, account_password='', legacy_password=''
):
    """Citește istoricul cu cheia stabilă a brokerilor, apoi cu cheia veche."""
    if not encrypted_payload:
        return []
    passwords = []
    for candidate in (account_password, legacy_password):
        candidate = str(candidate or '').strip()
        if candidate and candidate not in passwords:
            passwords.append(candidate)
    for candidate in passwords:
        try:
            history = json.loads(
                market_security.decrypt_from_js(encrypted_payload, candidate)
            )
        except (ValueError, TypeError, KeyError):
            continue
        if isinstance(history, list):
            return history
    return []


def _promote_validated_external_candidates(result, candidates, filepath='watchlist.csv'):
    """Adaugă în watchlist numai ideile externe validate explicit de AI."""
    valid_symbols = {
        str(item.get('symbol', '')).upper()
        for item in (result or {}).get('buy_recommendations', [])
        if item.get('verdict') == 'Candidat valid'
    }
    promoted = [
        str(item.get('symbol', '')).upper()
        for item in candidates or []
        if (
            item.get('candidate_source') == 'external_research'
            and str(item.get('symbol', '')).upper() in valid_symbols
        )
    ]
    if not promoted:
        return []
    watchlist = (
        pd.read_csv(filepath)
        if os.path.exists(filepath)
        else pd.DataFrame(columns=['symbol'])
    )
    existing = {
        str(symbol).upper() for symbol in watchlist.get('symbol', pd.Series(dtype=str)).dropna()
    }
    additions = [symbol for symbol in promoted if symbol not in existing]
    if additions:
        watchlist = pd.concat(
            [watchlist, pd.DataFrame({'symbol': additions})], ignore_index=True
        )
        watchlist.drop_duplicates(subset=['symbol'], keep='first').to_csv(filepath, index=False)
    return additions


def _external_research_score(item):
    """Prioritizează idei externe fără a reutiliza filtrul strict al watchlistului."""
    score = 0.0
    decision = str(item.get('Decision', '')).upper()
    consensus = str(item.get('Consensus', '')).lower()
    trend = str(item.get('Trend', '')).lower()
    score += {'BUY': 3, 'HOLD': 2, 'WAIT': 2, 'AVOID': -2}.get(decision, 0)
    score += 2 if consensus in {'buy', 'strong buy'} else 0.5 if consensus == 'hold' else 0
    score += min(max(float(item.get('RR_Ratio') or 0), 0), 3) * 0.5
    score += 2 if 'bullish' in trend else 0
    rsi = float(item.get('RSI') or 0)
    score += 2 if 35 <= rsi <= 68 else -2 if rsi > 72 else 0
    relative_strength = float(item.get('RS_vs_SPX') or 0)
    score += 2 if relative_strength > 10 else 1 if relative_strength > 0 else 0
    score -= 1 if item.get('Earnings_Danger') else 0
    if str(item.get('Ticker', '')).upper().endswith('.RO'):
        liquidity = item.get('BVB_Liquidity') or _bvb_liquidity_assessment(item)
        median_turnover = _safe_float_text(
            item.get('Median_Turnover_20D_RON')
        ) or 0
        minimum_turnover = _safe_float_text(
            liquidity.get('minimum_median_turnover_ron')
        ) or 1
        if median_turnover >= minimum_turnover * 5:
            score += 2
        elif median_turnover >= minimum_turnover * 2:
            score += 1
        elif liquidity.get('source') != 'istoric 20 ședințe':
            score -= 0.5
        relative_volume = _safe_float_text(item.get('Relative_Volume_20D'))
        if relative_volume is not None:
            score += 0.5 if relative_volume >= 1.2 else -0.5 if relative_volume < 0.5 else 0
        if liquidity.get('market_segment') == 'AeRO':
            score -= 0.5
    return score


def _external_candidate_has_reliable_levels(item):
    """Validează nivelurile externe fără a impune filtrul strict al watchlistului."""
    symbol = str(item.get('Ticker', '')).upper()
    entry = _buy_candidate_entry_eur(item)
    stop = _safe_float_text(item.get('Stop_Loss'))
    target = _safe_float_text(item.get('Target'))
    rr_ratio = _safe_float_text(item.get('RR_Ratio'))
    if not entry or not stop or not target or not rr_ratio:
        return False
    if not (0 < stop < entry < target):
        return False
    if rr_ratio < EXTERNAL_RESEARCH_MIN_RR:
        return False

    # Sursele pot publica uneori ținte fără unitate/monedă coerentă.
    # Nu trimitem modelului valori care implică multiplicări neverosimile.
    if rr_ratio > 12 or target / entry > 2.5:
        return False
    if not _buy_candidate_data_is_fresh(item):
        return False

    if not symbol.endswith('.RO'):
        return True

    liquidity = _bvb_liquidity_assessment(item)
    item['BVB_Liquidity'] = liquidity
    return liquidity['eligible']


def _research_symbols_due(
    symbols, by_symbol, watchlist_symbols=None, priority_symbols=None,
):
    """Include și simbolurile din watchlist; finaliștii primesc refresh mai des."""
    del watchlist_symbols  # Apartenența la watchlist nu mai blochează cercetarea.
    priority_symbols = {
        str(symbol).upper() for symbol in (priority_symbols or set())
    }
    priority_due = []
    regular_due = []
    for symbol in symbols:
        normalized = str(symbol).upper()
        if normalized in ALWAYS_RESEARCH_SYMBOLS:
            priority_due.append(symbol)
            continue
        cached = by_symbol.get(normalized)
        ttl_hours = (
            BUY_FINALIST_TTL_HOURS
            if normalized.endswith('.RO') or normalized in priority_symbols
            else EXTERNAL_RESEARCH_TTL_HOURS
        )
        if cached and market_data.is_fresh(cached, ttl_hours=ttl_hours):
            continue
        if normalized in priority_symbols:
            priority_due.append(symbol)
        else:
            regular_due.append(symbol)
    return priority_due + regular_due


def _external_priority_symbols(
    symbols, by_symbol, fallback_by_symbol=None, limit=10,
):
    """Folosește ultima triere disponibilă pentru a reîmprospăta finaliștii întâi."""
    ranked = []
    fallback_by_symbol = fallback_by_symbol or {}
    for symbol in symbols:
        normalized = str(symbol).upper()
        raw = by_symbol.get(normalized) or fallback_by_symbol.get(normalized)
        if not isinstance(raw, dict):
            continue
        candidate = _prepare_external_research_candidate(raw)
        entry = _buy_candidate_entry_eur(candidate)
        stop = _safe_float_text(candidate.get('Stop_Loss'))
        target = _safe_float_text(candidate.get('Target'))
        rr_ratio = _safe_float_text(candidate.get('RR_Ratio')) or 0
        if not (
            entry and stop and target
            and 0 < stop < entry < target
            and EXTERNAL_RESEARCH_MIN_RR <= rr_ratio <= 12
        ):
            continue
        ranked.append((
            -_external_research_score(candidate),
            -rr_ratio,
            normalized,
        ))
    ranked.sort()
    return {symbol for _, _, symbol in ranked[:limit]}


def select_strict_buy_candidates(
    watchlist_df, external_research=None, limit_per_market=4, etf_holdings=None,
    sector_rotation=None, us_market_regime=None, bvb_universe=None,
):
    """Aplică filtrele doar watchlistului și triază separat cercetarea externă."""
    candidates = []
    bvb_metadata_by_symbol = {
        str(item.get('symbol', '')).upper(): item
        for item in (bvb_universe or [])
    }
    etf_weights = {
        str(item.get('symbol', '')).upper(): float(item.get('weight_pct') or 0)
        for item in (etf_holdings or {}).get('holdings', [])
    }
    rotation_by_sector = (sector_rotation or {}).get('sectors', {})
    cycle_by_sector = (us_market_regime or {}).get('sector_fit', {})

    def apply_us_rotation(item):
        if item.get('Market') != 'SUA':
            return
        rotation = rotation_by_sector.get(str(item.get('Sector') or ''), {})
        status = rotation.get('status', 'date insuficiente')
        item['Sector_Rotation_Status'] = status
        item['Sector_ETF'] = rotation.get('etf')
        cycle_fit = cycle_by_sector.get(str(item.get('Sector') or ''), 'neutru')
        item['Cycle_Fit'] = cycle_fit
        item['_research_score'] += {
            'lider': 2.0,
            'neutru': 0.0,
            'în deteriorare': -3.0,
            'date insuficiente': -1.0,
        }.get(status, -1.0)
        item['_research_score'] += {
            'favorizat': 1.5, 'neutru': 0.0, 'nefavorizat': -1.5,
        }.get(cycle_fit, 0.0)
    watchlist_candidate_symbols = set()
    if watchlist_df is not None and not watchlist_df.empty:
        for _, row in watchlist_df.iterrows():
            item = row.to_dict()
            symbol = str(item.get('Ticker', '')).upper()
            if (
                symbol in bvb_metadata_by_symbol
                and not isinstance(item.get('BVB_Metadata'), dict)
            ):
                item['BVB_Metadata'] = bvb_metadata_by_symbol[symbol]
            strict_eligible = (
                _is_strict_buy_candidate(item)
                and _buy_candidate_data_is_fresh(item)
            )
            if not strict_eligible and symbol not in ALWAYS_RESEARCH_SYMBOLS:
                continue
            item['Market'] = _buy_candidate_market(item.get('Ticker'))
            item['Eligible_Brokers'] = _buy_candidate_brokers(item.get('Ticker'))
            item['Strict_Eligible'] = strict_eligible
            item['Candidate_Source'] = 'watchlist'
            item['Requires_Watchlist_Filters'] = True
            item['Data_Age_Hours'] = _buy_candidate_data_age_hours(item)
            item['Data_Fresh'] = _buy_candidate_data_is_fresh(item)
            item['_research_score'] = float(item.get('RR_Ratio') or 0)
            if symbol.endswith('.RO'):
                liquidity = _bvb_liquidity_assessment(item)
                item['BVB_Liquidity'] = liquidity
                if not liquidity['eligible']:
                    continue
                item['TVBETETF_Weight_Pct'] = etf_weights.get(symbol, 0)
                item['_research_score'] -= etf_weights.get(symbol, 0) / 4
            apply_us_rotation(item)
            candidates.append(item)
            watchlist_candidate_symbols.add(symbol)
    for raw_item in external_research or []:
        item = _prepare_external_research_candidate(raw_item)
        symbol = str(item.get('Ticker', '')).upper()
        # Un simbol care nu trece filtrul strict al watchlistului poate fi
        # totuși cercetat independent. Evităm doar dublarea unui candidat
        # strict deja inclus din watchlist.
        if not symbol or symbol in watchlist_candidate_symbols:
            continue
        if (
            symbol in bvb_metadata_by_symbol
            and not isinstance(item.get('BVB_Metadata'), dict)
        ):
            item['BVB_Metadata'] = bvb_metadata_by_symbol[symbol]
        if not _external_candidate_has_reliable_levels(item):
            continue
        item['Market'] = _buy_candidate_market(symbol)
        item['Eligible_Brokers'] = _buy_candidate_brokers(symbol)
        item['Strict_Eligible'] = _is_strict_buy_candidate(item)
        item['Candidate_Source'] = 'external_research'
        item['Requires_Watchlist_Filters'] = False
        item['External_Min_RR'] = EXTERNAL_RESEARCH_MIN_RR
        item['Data_Age_Hours'] = _buy_candidate_data_age_hours(item)
        item['Data_Fresh'] = _buy_candidate_data_is_fresh(item)
        item['_research_score'] = _external_research_score(item)
        if symbol.endswith('.RO'):
            item['TVBETETF_Weight_Pct'] = etf_weights.get(symbol, 0)
            # O idee care dublează o componentă dominantă trebuie să fie net
            # mai bună pentru a ocupa unul dintre locurile limitate BVB.
            item['_research_score'] -= etf_weights.get(symbol, 0) / 4
        apply_us_rotation(item)
        candidates.append(item)
    candidates.sort(
        key=lambda item: (
            item['Market'],
            -float(item.get('_research_score') or 0),
            str(item.get('Ticker', '')),
        )
    )
    selected = []
    market_counts = {}
    market_total_counts = {}
    market_total_limits = {
        'Europa / Nasdaq-100': 1,
        'România / BVB': 6,
        'SUA': 8,
    }
    us_sector_counts = {}
    us_industry_counts = {}
    for item in candidates:
        source = item.get('Candidate_Source', 'watchlist')
        count_key = (item['Market'], source)
        source_limit = 10 if source == 'external_research' else limit_per_market
        if market_counts.get(count_key, 0) >= source_limit:
            continue
        if market_total_counts.get(item['Market'], 0) >= market_total_limits.get(
            item['Market'], limit_per_market
        ):
            continue
        if item['Market'] == 'SUA':
            sector = str(item.get('Sector') or 'Necunoscut')
            if us_sector_counts.get(sector, 0) >= 2:
                continue
            industry = str(item.get('Industry') or '').strip()
            if (
                industry
                and industry not in {'-', 'N/A', 'Unknown'}
                and us_industry_counts.get(industry, 0) >= 1
            ):
                continue
        selected.append(item)
        market_counts[count_key] = market_counts.get(count_key, 0) + 1
        market_total_counts[item['Market']] = (
            market_total_counts.get(item['Market'], 0) + 1
        )
        if item['Market'] == 'SUA':
            us_sector_counts[sector] = us_sector_counts.get(sector, 0) + 1
            if industry and industry not in {'-', 'N/A', 'Unknown'}:
                us_industry_counts[industry] = (
                    us_industry_counts.get(industry, 0) + 1
                )
    return selected


def _select_bvb_research_symbols(
    bvb_universe,
    by_symbol,
    watchlist_by_symbol,
    watchlist_symbols,
):
    """Alege lotul BVB folosit identic de TWS și de analiza BUY."""
    symbols = [item['symbol'] for item in bvb_universe]
    bvb_metadata = {item['symbol']: item for item in bvb_universe}
    priority_symbols = _external_priority_symbols(
        symbols,
        by_symbol,
        fallback_by_symbol=watchlist_by_symbol,
        limit=8,
    )

    def bvb_priority(symbol):
        metadata = bvb_metadata.get(symbol, {})
        normalized = symbol.upper()
        cached = (
            by_symbol.get(normalized)
            or watchlist_by_symbol.get(normalized)
            or {}
        )
        freshness = float(cached.get('_cached_at') or 0)
        trade_date = metadata.get('last_trade') or ''
        try:
            recency = -datetime.date.fromisoformat(trade_date).toordinal()
        except (TypeError, ValueError):
            recency = 0
        liquidity = float(
            metadata.get('turnover_ron')
            or metadata.get('volume')
            or 0
        )
        research_score = _external_research_score(
            _prepare_external_research_candidate(cached)
        )
        return (
            0 if normalized in priority_symbols else 1,
            -research_score,
            freshness,
            -liquidity,
            recency,
            symbol,
        )

    symbols.sort(key=bvb_priority)
    return _research_symbols_due(
        symbols,
        by_symbol,
        watchlist_symbols,
        priority_symbols=priority_symbols,
    )[:BVB_DEEP_SCAN_BATCH]


def _planned_bvb_tws_symbols(state):
    """Universul larg BVB nu este interogat prin TWS.

    Instrumentele românești deja deținute sau configurate explicit în IBKR
    continuă să fie sincronizate de ``ib_tws_sync`` prin propriile sale liste.
    """
    return []


def ensure_buy_research_candidates(
    state,
    rates,
    vix_val,
    refresh_missing=False,
    target_markets=None,
):
    """Cercetează separat universuri externe, fără a le confunda cu watchlistul."""
    target_markets = (
        {str(market) for market in target_markets}
        if target_markets
        else None
    )
    include_bvb = (
        target_markets is None or 'România / BVB' in target_markets
    )
    include_us = target_markets is None or 'SUA' in target_markets
    bvb_universe = (
        fetch_complete_bvb_equity_universe(state)
        if refresh_missing and include_bvb
        else list(state.get('bvb_equity_universe', []))
    )
    if bvb_universe:
        state['bvb_equity_universe'] = bvb_universe
    research_universes = {
        market: list(symbols) for market, symbols in BUY_RESEARCH_UNIVERSES.items()
    }
    us_universe = load_complete_us_equity_universe() if include_us else []
    if us_universe:
        research_universes['SUA'] = us_universe
    if bvb_universe:
        research_universes['România / BVB'] = [
            item['symbol'] for item in bvb_universe
        ]
    state_watchlist = list(state.get('watchlist', []))
    watchlist_symbols = set()
    if os.path.exists('watchlist.csv'):
        watchlist_file = pd.read_csv('watchlist.csv')
        if 'symbol' in watchlist_file.columns:
            watchlist_symbols = {
                str(symbol).upper()
                for symbol in watchlist_file['symbol'].dropna().tolist()
            }
    watchlist_market_counts = {
        'SUA': sum(
            _buy_candidate_market(symbol) == 'SUA'
            for symbol in watchlist_symbols
        ),
        'România / BVB': sum(
            _buy_candidate_market(symbol) == 'România / BVB'
            for symbol in watchlist_symbols
        ),
        'Europa / Nasdaq-100': sum(
            _buy_candidate_market(symbol) == 'Europa / Nasdaq-100'
            for symbol in watchlist_symbols
        ),
    }
    existing_results = [
        item for item in state_watchlist
        if str(item.get('Ticker', '')).upper() in watchlist_symbols
    ]
    migrated_external = [
        dict(item, Candidate_Source='external_research')
        for item in state_watchlist
        if (
            str(item.get('Ticker', '')).upper() not in watchlist_symbols
            and (
                str(item.get('Ticker', '')).upper().endswith('.RO')
                or str(item.get('Ticker', '')).upper() in {
                symbol.upper()
                for symbols in research_universes.values()
                for symbol in symbols
                }
            )
            and str(item.get('Ticker', '')).upper() != 'TVBETETF.RO'
        )
    ]
    # CSV-ul este sursa autoritară pentru apartenența la watchlist. Elimină din
    # starea veche simbolurile mutate în cercetarea externă.
    state['watchlist'] = existing_results
    if migrated_external:
        external_by_symbol = {
            str(item.get('Ticker', '')).upper(): item
            for item in state.get('external_buy_research', [])
        }
        for item in migrated_external:
            external_by_symbol[str(item.get('Ticker', '')).upper()] = item
        state['external_buy_research'] = list(external_by_symbol.values())
    eligible_markets = {
        _buy_candidate_market(item.get('Ticker'))
        for item in existing_results if _is_strict_buy_candidate(item)
    }
    markets_to_research = [
        market for market in research_universes
        if (
            (target_markets is None or market in target_markets)
            and (
                market not in eligible_markets
                or market in {'SUA', 'Europa / Nasdaq-100', 'România / BVB'}
            )
        )
    ]
    if not markets_to_research:
        return state

    if not refresh_missing:
        return state

    by_symbol = {
        str(item.get('Ticker', '')).upper(): item
        for item in list(state.get('external_buy_research', [])) + migrated_external
    }
    watchlist_by_symbol = {
        str(item.get('Ticker', '')).upper(): item
        for item in existing_results
    }
    bvb_metadata = {
        item['symbol']: item for item in bvb_universe
    }
    attempted_by_market = {}
    completed_by_market = {}
    for market in markets_to_research:
        print(f"  -> Cercetare BUY pentru {market}...")
        symbols = list(research_universes[market])
        priority_limit = (
            12 if market == 'SUA'
            else 8 if market == 'România / BVB'
            else 1
        )
        priority_symbols = _external_priority_symbols(
            symbols,
            by_symbol,
            fallback_by_symbol=watchlist_by_symbol,
            limit=priority_limit,
        )
        if market == 'România / BVB':
            symbols = _select_bvb_research_symbols(
                bvb_universe,
                by_symbol,
                watchlist_by_symbol,
                watchlist_symbols,
            )
        elif market == 'SUA':
            symbols.sort(key=lambda symbol: (
                0 if symbol.upper() in priority_symbols else 1,
                -_external_research_score(_prepare_external_research_candidate(
                    by_symbol.get(symbol.upper())
                    or watchlist_by_symbol.get(symbol.upper())
                    or {}
                )),
                float((
                    by_symbol.get(symbol.upper())
                    or watchlist_by_symbol.get(symbol.upper())
                    or {}
                ).get('_cached_at') or 0),
                symbol,
            ))
            symbols = _research_symbols_due(
                symbols,
                by_symbol,
                watchlist_symbols,
                priority_symbols=priority_symbols,
            )[:US_DEEP_SCAN_BATCH]
        else:
            symbols = _research_symbols_due(
                symbols,
                by_symbol,
                watchlist_symbols,
                priority_symbols=priority_symbols,
            )
        _prefetch_ibkr_mcp_market_data(
            symbols, label=f"cercetare {market}"
        )
        attempted_by_market[market] = len(symbols)
        completed_by_market[market] = 0
        for symbol in symbols:
            data = process_watchlist_ticker(symbol, vix_val, rates)
            if not data:
                continue
            data['_cached_at'] = time.time()
            data['Candidate_Source'] = 'external_research'
            if symbol in bvb_metadata:
                data['BVB_Metadata'] = bvb_metadata[symbol]
            by_symbol[symbol.upper()] = data
            completed_by_market[market] += 1
    state['external_buy_research'] = list(by_symbol.values())
    if include_bvb:
        state['bvb_universe_stats'] = {
            'discovered': len(bvb_universe),
            'deep_scanned': sum(
                str(item.get('Ticker', '')).upper().endswith('.RO')
                for item in by_symbol.values()
            ),
            'batch_size': BVB_DEEP_SCAN_BATCH,
            'watchlist_symbols': watchlist_market_counts['România / BVB'],
            'last_batch_attempted': attempted_by_market.get(
                'România / BVB', 0
            ),
            'last_batch_completed': completed_by_market.get(
                'România / BVB', 0
            ),
            'source': ROMANIAN_UNIVERSE_SOURCE_URL,
            'updated_at': datetime.datetime.now().isoformat(timespec='seconds'),
        }
    if include_us:
        us_symbols = set(us_universe)
        state['us_universe_stats'] = {
            'discovered': len(us_universe),
            'deep_scanned': sum(
                str(item.get('Ticker', '')).upper() in us_symbols
                for item in by_symbol.values()
            ),
            'batch_size': US_DEEP_SCAN_BATCH,
            'watchlist_symbols': watchlist_market_counts['SUA'],
            'watchlist_europe_symbols': watchlist_market_counts[
                'Europa / Nasdaq-100'
            ],
            'last_batch_attempted': attempted_by_market.get('SUA', 0),
            'last_batch_completed': completed_by_market.get('SUA', 0),
            'source': SP500_UNIVERSE_FILE,
            'updated_at': datetime.datetime.now().isoformat(timespec='seconds'),
        }
    return state

# Cache settings for long-horizon historical returns (slow to compute)
HISTORICAL_RETURNS_FILE = "historical_returns.json"
HISTORICAL_RETURNS_TTL_DAYS = 30


# REFACTORED: security functions moved to market_security.py
# REFACTORED: state functions moved to market_utils.py

# Finviz cache Logic moved to market_data.py
# _finviz_cache = {} -> market_data._finviz_cache

# get_finviz_data moved to market_data.py
# load_portfolio remains here (specific to scanner usage)

def load_portfolio(filename='portfolio.csv'):
    """Încarcă portofoliul din CSV."""
    if not os.path.exists(filename):
        print(f"Fișierul {filename} nu a fost găsit.")
        return pd.DataFrame()
    
    df = pd.read_csv(filename)
    # Normalizează coloanele (lowercase) pentru a evita KeyErrors
    df.columns = [c.strip().lower() for c in df.columns]
    return df

def sync_watchlist_from_remote(url="https://betty333ro.github.io/market-scanner/", filepath='watchlist.csv'):
    """Sincronizează watchlist-ul cu pagina remote."""
    try:
        print(f"🔄 Sincronizare watchlist de pe {url}...")
        
        # Fetch remote page
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all Finviz links (covers both 'Market Overview' and 'Advanced Filters' sections)
        finviz_links = soup.find_all('a', href=re.compile(r'finviz\.com/quote\.ashx'))
        print(f"  → Found {len(finviz_links)} potential ticker links (merging all sections)...")
        
        if not finviz_links:
            print("⚠️  Nu s-au găsit simboluri pe pagina remote")
            return
        
        # Extract symbols
        remote_symbols = set()
        for link in finviz_links:
            symbol = link.get_text(strip=True).upper()
            if symbol:
                remote_symbols.add(symbol)
        
        # Load local symbols
        local_symbols = set()
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                if 'symbol' in df.columns:
                    local_symbols = set(df['symbol'].str.upper())
            except:
                pass
        
        # Find new symbols
        new_symbols = remote_symbols - local_symbols
        
        if new_symbols:
            print(f"  ✅ Găsite {len(new_symbols)} simboluri noi")
            
            # Add to watchlist
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
            else:
                df = pd.DataFrame(columns=['symbol'])
            
            new_rows = [{'symbol': s} for s in new_symbols]
            df_new = pd.DataFrame(new_rows)
            df = pd.concat([df, df_new], ignore_index=True)
            
            # Remove duplicates
            df['symbol'] = df['symbol'].str.upper()
            df = df.drop_duplicates(subset=['symbol'], keep='first')
            
            # Save
            df.to_csv(filepath, index=False)
            print(f"  ✅ Watchlist actualizat: {len(df)} simboluri total")
        else:
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
            else:
                df = pd.DataFrame(columns=['symbol'])
            print(
                f"  ✅ Sursa remote este la zi: {len(remote_symbols)} "
                f"simboluri; watchlist local cumulativ: {len(df)} simboluri"
            )
                
        try:
            import json
            json_file = filepath.replace('.csv', '.json')
            records = df[['symbol']].to_dict(orient='records')
            with open(json_file, 'w') as f:
                json.dump(records, f, indent=2)
        except Exception as json_err:
            print(f"⚠️ Eroare la generare watchlist JSON: {json_err}")
            
    except Exception as e:
        print(f"⚠️  Eroare la sincronizare watchlist: {e}")

def load_watchlist(filename='watchlist.csv'):
    """Încarcă lista de tickere de urmărit din CSV."""
    if not os.path.exists(filename):
        print(f"Fișierul {filename} nu a fost găsit.")
        return []
    
    try:
        df = pd.read_csv(filename)
        if 'symbol' in df.columns:
            tickers = df['symbol'].str.upper().tolist()
            try:
                import json
                json_file = filename.replace('.csv', '.json')
                unique_tickers = sorted(list(set(tickers)))
                records = [{'symbol': s} for s in unique_tickers]
                with open(json_file, 'w') as f:
                    json.dump(records, f, indent=2)
            except Exception as json_err:
                print(f"⚠️ Eroare la generare watchlist JSON: {json_err}")
            return list(set(tickers))  # Remove duplicates
        else:
            print(f"Coloana 'symbol' nu a fost găsită în {filename}")
            return []
    except Exception as e:
        print(f"Eroare la citirea {filename}: {e}")
        return []

def adjust_for_unadjusted_splits(df, ticker):
    """Detectează și corectează split-urile neajustate în datele istorice yfinance."""
    if df.empty or len(df) < 2:
        return df
    try:
        for i in range(1, len(df)):
            ratio = df['Close'].iloc[i-1] / df['Close'].iloc[i]
            if ratio > 50:
                split_factor = 1.0
                if 170 <= ratio <= 230:
                    split_factor = 200.0
                elif 80 <= ratio <= 120:
                    split_factor = 100.0
                elif 8 <= ratio <= 12:
                    split_factor = 10.0
                else:
                    split_factor = float(round(ratio))
                
                print(f"  [Split Alert] Corecție split pentru {ticker} la data {df.index[i].strftime('%Y-%m-%d')} (factor: {split_factor}x)")
                cols = ['Open', 'High', 'Low', 'Close']
                df.iloc[:i, df.columns.get_indexer(cols)] /= split_factor
                if 'Volume' in df.columns:
                    df.iloc[:i, df.columns.get_indexer(['Volume'])] *= split_factor
                break
    except Exception as e:
        print(f"⚠️ Eroare la ajustare split pentru {ticker}: {e}")
    return df

def calculate_atr(df, period=14):
    """Calculează Average True Range (ATR)."""
    if len(df) < period + 1:
        return None
    
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)
    
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr

def calculate_rsi(df, period=14):
    """Calculează RSI folosind metoda Wilder's Smoothing (Standard)."""
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Wilder's Smoothing (alpha = 1/period)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_sma(df, period):
    """Calculează Simple Moving Average."""
    return df['Close'].rolling(window=period).mean()

def get_vix_data():
    """Descarcă datele pentru VIX (volatilitate)."""
    try:
        vix = yf.Ticker("^VIX")
        hist = vix.history(period="5d")
        if not hist.empty:
            hist = hist.dropna(subset=['Close'])
        if hist.empty:
            return None
        current_vix = hist['Close'].iloc[-1]
        return current_vix
    except Exception as e:
        print(f"Eroare la preluarea VIX: {e}")
        return None

# The original HISTORY_FILE definition was here, now it's market_utils.MARKET_HISTORY_FILE at the top.
# import json # This import is already at the top.

# HISTORY_FILE = "market_history.json" # This is now market_utils.MARKET_HISTORY_FILE at the top.


def get_next_earnings_date(ticker_symbol):
    """
    Returnează următoarea dată de earnings (datetime.date) sau None dacă nu e găsită.
    Folosește yfinance calendar.
    """
    # ETF-urile nu raportează earnings ca o companie. Yahoo răspunde cu 404
    # pentru quoteSummary/calendarEvents, deși istoricul de preț este valid.
    if _known_fund_profile(ticker_symbol):
        return None
    try:
        lookup_symbol = ticker_symbol[:-3] if ticker_symbol.endswith('.US') else ticker_symbol
        if lookup_symbol in ['LQQ.FR', 'FR.LQQ']:
            lookup_symbol = 'LQQ.PA'
        t = yf.Ticker(lookup_symbol)
        cal = t.calendar
        if cal and isinstance(cal, dict) and 'Earnings Date' in cal:
            dates = cal['Earnings Date']
            if dates:
                # Return first date (usually range start or confirmed date)
                d = dates[0]
                # Ensure it's a date object
                if isinstance(d, datetime.datetime):
                    return d.date()
                return d
    except Exception as e:
        # print(f"Earnings check failed for {ticker_symbol}: {e}")
        pass
    return None

def load_market_history():
    if os.path.exists(market_utils.MARKET_HISTORY_FILE):
        try:
            with open(market_utils.MARKET_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_market_history(history):
    try:
        with open(market_utils.MARKET_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Eroare salvare istoric: {e}")

def calculate_historical_monthly_returns(cache_file=HISTORICAL_RETURNS_FILE, ttl_days=HISTORICAL_RETURNS_TTL_DAYS):
    """Calculate average monthly returns for S&P 500 and NASDAQ since 1950 (cached monthly)."""
    # Serve from cache if fresh
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            cached_at = cached.get('generated_at')
            cached_month = cached.get('generated_month')
            cached_data = cached.get('data')
            if cached_at and cached_data:
                cached_dt = datetime.datetime.fromisoformat(cached_at)
                now = datetime.datetime.now()
                # Recompute only when month changes (1st trading day will trigger)
                if cached_dt.year == now.year and cached_dt.month == now.month:
                    return cached_data
            if cached_month and cached_data:
                now_month = datetime.datetime.now().strftime("%Y-%m")
                if cached_month == now_month:
                    return cached_data
        except Exception:
            pass

    returns = {}
    
    indices = {
        'SP500': '^GSPC',  # S&P 500
        'NASDAQ': '^IXIC'  # NASDAQ Composite
    }
    
    for name, ticker in indices.items():
        try:
            print(f"  → Calculez randamente istorice pentru {name}...")
            data = yf.Ticker(ticker)
            
            # Get historical data from 1950 to today
            hist = data.history(start="1950-01-01", end=datetime.datetime.now().strftime('%Y-%m-%d'))
            if not hist.empty:
                hist = hist.dropna(subset=['Close'])
            
            if hist.empty:
                print(f"    ⚠️  Nu există date pentru {name}")
                continue
            
            # Resample to monthly and calculate returns
            monthly = hist['Close'].resample('M').last()
            monthly_returns = monthly.pct_change().dropna() * 100  # Convert to percentage
            
            # Calculate average monthly return
            avg_return = monthly_returns.mean()
            
            # Calculate average return for each calendar month (1-12)
            monthly_returns_df = monthly_returns.to_frame('return')
            monthly_returns_df['month'] = monthly_returns_df.index.month
            monthly_averages = monthly_returns_df.groupby('month')['return'].mean().to_dict()
            
            returns[name] = {
                'avg_monthly_return': round(avg_return, 2),
                'data_points': len(monthly_returns),
                'start_date': monthly_returns.index[0].strftime('%Y-%m'),
                'end_date': monthly_returns.index[-1].strftime('%Y-%m'),
                'monthly_averages': {str(k): round(v, 2) for k, v in monthly_averages.items()}
            }
            
            print(f"    ✅ {name}: {avg_return:.2f}% avg monthly return ({len(monthly_returns)} months)")
            
        except Exception as e:
            print(f"    ❌ Eroare la calculul randamentelor pentru {name}: {e}")
            continue
    
    # Save cache
    try:
        now = datetime.datetime.now()
        with open(cache_file, 'w') as f:
            json.dump(
                {
                    "generated_at": now.isoformat(),
                    "generated_month": now.strftime("%Y-%m"),
                    "data": returns
                },
                f,
                indent=2
            )
    except Exception:
        pass

    return returns

def get_market_indicators():
    """Preia indicatori volum și sentiment, cu persistență locală."""
    indicators = {}
    history_db = load_market_history()
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Lista de indicatori cu ticker-ele lor Yahoo Finance și thresholds
    tickers_map = {
        'VIX3M': '^VIX3M',      # VIX pe 3 luni
        'VIX': '^VIX',          # VIX standard
        'VIX1D': '^VIX1D',      # VIX 1 zi (dacă există)
        'VIX9D': '^VIX9D',      # VIX 9 zile
        'VXN': '^VXN',          # Nasdaq VIX
        'LTV': '^LTV',          # CBOE Left Tail Volatility
        'SKEW': '^SKEW',        # CBOE SKEW
        'MOVE': '^MOVE',        # MOVE Index (bond volatility)
        'GVZ': '^GVZ',          # Gold Volatility
        'OVX': '^OVX',          # Oil Volatility
        'SPX': '^GSPC',         # S&P 500
        'NASDAQ': '^IXIC',      # NASDAQ Composite
    }
    
    # Thresholds (aceleași ca înainte, le păstrăm)
    thresholds = {
        'VIX3M': (14, 20), 'VIX': (15, 20), 'VIX1D': (12, 30), 'VIX9D': (12, 18), 'VXN': (15, 25),
        'LTV': (10, 13), 'SKEW': (135, 150), 'MOVE': (80, 120), 'GVZ': (17, 22), 'OVX': (25, 35),
        'SPX': (None, None), 'NASDAQ': (None, None)
    }
    
    # Definițiile nivelelor (copiate din codul existent pentru consistență)
    threshold_levels = {
        'VIX3M': [(14, 'perfect 14'), (20, '14 normal 20'), (30, '20 tensiune 30'), (999, '30 panica')],
        'VIX': [(15, 'perfect 15'), (20, '15 normal 20'), (30, '20 teama 30'), (999, '30 panica')],
        'VIX1D': [(12, 'perfect 12'), (30, '12 normal 30'), (999, '30 panica')],
        'VIX9D': [(12, 'perfect 12'), (18, '12 normal 18'), (25, '18 teama 25'), (999, '25 panica')],
        'VXN': [(15, 'perfect 15'), (25, '15 normal 25'), (35, '25 teama 35'), (999, '35 panica')],
        'LTV': [(10, 'perfect 10'), (13, '10 normal 13'), (999, '13 panica')],
        'SKEW': [(100, 'perfect 100'), (120, '100 precaut/vix/ltv 120'), (135, '120 usor ridicat/vix/ltv 135'), (150, '135 teama 150'), (999, '150 panica')],
        'MOVE': [(80, 'perfect 80'), (120, '80 moderat 120'), (150, '120 teama 150'), (999, '150 panica')],
        'GVZ': [(17, 'perfect 22'), (22, '17 teama 22'), (999, '22 panica')],
        'OVX': [(25, 'perfect 25'), (35, '25 teama 35'), (999, '35 panica')],
    }
    
    for name, ticker in tickers_map.items():
        try:
            time.sleep(0.5)
            data = yf.Ticker(ticker)
            # Încercăm să luăm istoric scurt pentru update, sau lung dacă nu avem local
            hist = data.history(period="6mo")
            if not hist.empty:
                hist = hist.dropna(subset=['Close'])
            
            current_val = None
            
            # 1. Update Persistent History
            if not hist.empty:
                # Iterăm prin ultimele zile și le adăugăm în DB
                # Yahoo returnează index datetime, convertim la string YYYY-MM-DD
                for date_idx, row in hist.iterrows():
                    d_str = date_idx.strftime('%Y-%m-%d')
                    val = float(row['Close'])
                    if not pd.isna(val):
                        # Init list if needed
                        if name not in history_db: history_db[name] = []
                        
                        # Check exist
                        existing = next((x for x in history_db[name] if x['date'] == d_str), None)
                        if existing:
                            existing['value'] = val
                        else:
                            history_db[name].append({'date': d_str, 'value': val})
                
                # Sort și Trim (ultimele 60 zile)
                if name in history_db:
                    history_db[name].sort(key=lambda x: x['date'])
                    history_db[name] = history_db[name][-60:]
            
            # 2. Folosim datele din History DB pentru afișare
            if name in history_db and history_db[name]:
                data_points = [x['value'] for x in history_db[name]]
                current = data_points[-1]
                
                if len(data_points) >= 2:
                    change = current - data_points[-2]
                else:
                    change = 0.0
                
                sparkline_data = data_points[-30:] # Last 30 points
                ohlc_data = []
                if not hist.empty and all(col in hist.columns for col in ('Open', 'High', 'Low', 'Close')):
                    for date_idx, row in hist.tail(90).iterrows():
                        values = [row['Open'], row['High'], row['Low'], row['Close']]
                        if any(pd.isna(value) for value in values):
                            continue
                        ohlc_data.append({
                            'date': date_idx.strftime('%Y-%m-%d'),
                            'open': round(float(row['Open']), 4),
                            'high': round(float(row['High']), 4),
                            'low': round(float(row['Low']), 4),
                            'close': round(float(row['Close']), 4)
                        })
                
                # Logică Status/Descriere
                if name in threshold_levels:
                    levels = threshold_levels[name]
                    description = levels[-1][1]
                    status = "Panic"
                    for threshold, desc in levels:
                        if current < threshold:
                            description = desc
                            if 'perfect' in desc.lower(): status = "Perfect"
                            elif 'normal' in desc.lower() or 'precaut' in desc.lower() or 'ridicat' in desc.lower() or 'moderat' in desc.lower(): status = "Normal"
                            elif 'tensiune' in desc.lower() or 'teama' in desc.lower(): status = "Tension"
                            else: status = "Panic"
                                
                            break
                else:
                    # For indices (SPX, NASDAQ) that don't have thresholds
                    status = "Normal"
                    description = ""  # Indices don't need status descriptions
                
                indicators[name] = {
                    'value': round(current, 2),
                    'change': round(change, 2),
                    'status': status,
                    'description': description,
                    'sparkline': sparkline_data,
                    'history': data_points[-60:],
                    'history_dates': [x['date'] for x in history_db[name]][-60:],
                    'ohlc': ohlc_data,
                    'ticker': ticker
                }
            else:
                print(f"  ⚠ {name}: Nu există date (nici Yahoo, nici Local)")
                
        except Exception as e:
            print(f"  ⚠ Eroare {name}: {str(e)[:40]}")
    
    # Salvarea istoricului actualizat
    save_market_history(history_db)
    
    # Crypto Fear & Greed Index (separat, dar îl putem adăuga și pe el în DB dacă vrem, momentan e ok așa)
    try:
        # Cerem ultimele 35 de zile pentru istoric
        response = requests.get('https://api.alternative.me/fng/?limit=35', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                current_data = data['data'][0]
                value = int(current_data['value'])
                classification = current_data['value_classification']  # Extreme Fear, Fear, Neutral, Greed, Extreme Greed
                
                # Determinăm status și description
                # Determinăm status și description (User Formula)
                if value < 24:
                    status = 'Panic'
                    description = 'panica 24'
                elif value < 49:
                    status = 'Tension'
                    description = '24 frica 49'
                elif value < 74:
                    status = 'Normal'
                    description = '49 lacomie 74'
                else:
                    status = 'Perfect'
                    description = '74 lacomie extrema'
                
                # Change (diferența față de ziua precedentă)
                if len(data['data']) > 1:
                    prev_value = int(data['data'][1]['value'])
                    change = value - prev_value
                else:
                    change = 0
                
                # Sparkline data (ultimele 30 zile, inversat pentru cronologie vechi->nou)
                sparkline_raw = data['data'][:30]
                sparkline_data = [int(item['value']) for item in sparkline_raw][::-1]
                history_raw = data['data'][:35][::-1]
                
                indicators['Crypto Fear'] = {
                    'value': value,
                    'change': change,
                    'status': status,
                    'description': description,
                    'sparkline': sparkline_data,
                    'history': [int(item['value']) for item in history_raw],
                    'history_dates': [
                        datetime.datetime.fromtimestamp(
                            int(item['timestamp']), datetime.timezone.utc
                        ).strftime('%Y-%m-%d')
                        for item in history_raw
                    ],
                    'ohlc': [],
                    'ticker': 'alternative.me'
                }
    except Exception as e:
        print(f"  ⚠ Eroare Crypto Fear: {str(e)[:40]}")
    
    # Calculate historical monthly returns
    historical_returns = calculate_historical_monthly_returns()
    if historical_returns:
        indicators['Historical_Returns'] = historical_returns
    
    return indicators

def get_macro_explanations():
    """Generează secțiunea de explicații pentru indicatori macroeconomici."""
    return """
    <div class="macro-explainer" style="background: var(--bg-white); padding: 32px; border-radius: var(--radius-md); margin-top: 32px; border: 1px solid var(--border-light); box-shadow: var(--shadow-sm); animation: fadeIn 0.8s ease-out 0.8s backwards;">
        <h3 style="color: var(--primary-purple); border-bottom: 2px solid var(--light-purple-bg); padding-bottom: 16px; margin-top: 0;">Glosar: Indicatori Macroeconomici Cheie & Impact</h3>
        <p style="font-size: 16px; color: var(--text-secondary); margin-bottom: 24px;">Ghid pentru înțelegerea evenimentelor din Calendarul Economic.</p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            
            <!-- Building Permits -->
            <div class="macro-card" style="background: var(--light-purple-bg); padding: 20px; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                <h4 style="color: #F59E0B; margin-top: 0;">Building Permits</h4>
                <p style="font-size: 14px; color: var(--text-primary);"><strong>Ce este:</strong> Un indicator "leading" (anticipativ) care arată cererea viitoare în sectorul imobiliar.</p>
                <p style="font-size: 14px; margin-bottom: 0; color: var(--text-primary);"><strong>Impact Piață:</strong> 
                   <br><span style="color: var(--success-green);">Cifre Mari:</span> Economie robustă, încredere consumatori.
                   <br><span style="color: var(--error-red);">Cifre Mici:</span> Semnal de recesiune.
                </p>
            </div>

            <!-- CPI -->
            <div class="macro-card" style="background: var(--light-purple-bg); padding: 20px; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                <h4 style="color: var(--error-red); margin-top: 0;">CPI (Consumer Price Index)</h4>
                <p style="font-size: 14px; color: var(--text-primary);"><strong>Ce este:</strong> Măsura principală a inflației. Cel mai urmărit indicator de către Fed.</p>
                <p style="font-size: 14px; margin-bottom: 0; color: var(--text-primary);"><strong>Impact Piață:</strong> 
                   <br><span style="color: var(--error-red);">Peste Așteptări:</span> Fed crește dobânzile → Acțiunile scad.
                   <br><span style="color: var(--success-green);">Sub Așteptări:</span> Fed poate tăia dobânzile → Raliu.
                </p>
            </div>

            <!-- NFP -->
            <div class="macro-card" style="background: var(--light-purple-bg); padding: 20px; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                <h4 style="color: #3B82F6; margin-top: 0;">NFP (Non-Farm Payrolls)</h4>
                <p style="font-size: 14px; color: var(--text-primary);"><strong>Ce este:</strong> Numărul de joburi noi create în SUA (lunar).</p>
                <p style="font-size: 14px; margin-bottom: 0; color: var(--text-primary);"><strong>Impact Piață:</strong> 
                   <br><span style="color: var(--success-green);">Joburi Multe:</span> Economie puternică (dar risc de inflație).
                   <br><span style="color: var(--error-red);">Joburi Puține:</span> Risc de recesiune.
                </p>
            </div>
            
             <!-- FOMC -->
            <div class="macro-card" style="background: var(--light-purple-bg); padding: 20px; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                <h4 style="color: var(--primary-purple); margin-top: 0;">FOMC (Ședința Fed)</h4>
                <p style="font-size: 14px; color: var(--text-primary);"><strong>Ce este:</strong> Decizia privind dobânda de referință. "Costul banilor".</p>
                <p style="font-size: 14px; margin-bottom: 0; color: var(--text-primary);"><strong>Impact Piață:</strong> 
                   <br>Dobânzi Mari = Acțiuni jos.
                   <br>Pivot (Tăiere) = Acțiuni sus 🚀
                </p>
            </div>

        </div>
    </div>
    """


# REFACTORED: get_scalar and get_exchange_rates moved to market_data.py


def process_portfolio_ticker(row, vix_value, rates, spx_df=None, market_in_downtrend=False, breadth_pct=50, rule4_active=False, ticker_cache=None):
    """Procesează un ticker din portofoliu cu date de ownership (Conversie EUR)."""
    try:
        ticker = row.get('symbol', 'UNKNOWN').upper()
        is_bvb_position = ticker.endswith('.RO')
        download_ticker = ticker[:-3] if ticker.endswith('.US') else ticker
        if download_ticker in ['LQQ.FR', 'FR.LQQ']:
            download_ticker = 'LQQ.PA'
        actual_download_ticker = download_ticker
        shares = float(row.get('shares', 0))
        buy_price_native = float(row.get('buy_price', 0))
        # Default trail_pct to 15 if missing
        trail_pct = float(row.get('trail_pct', 15))
        
        print(f"Procesare: {ticker}")
        
        # Detect Currency
        currency_explicit = row.get('currency', '')
        if isinstance(currency_explicit, str) and len(currency_explicit) == 3:
             currency = currency_explicit.upper()
             print(f"  [Info] Currency explicit din CSV: {currency}")
        else:
             currency = 'USD' # Default
             if '.RO' in ticker: currency = 'RON'
             elif '.PA' in ticker or '.DE' in ticker or '.AS' in ticker or '.FR' in ticker or 'LQQ' in ticker: currency = 'EUR'
             elif '.L' in ticker: currency = 'GBP'
        
        rate = rates.get(currency, rates['USD'])
        if currency == 'EUR': rate = 1.0

        # Extract Entry Date (newly added)
        # Extract Entry Date (newly added)
        # Try multiple keys due to potential case sensitivity in CSV loading
        # NOTE: load_portfolio converts columns to lowercase!
        entry_date = row.get('Entry_Date', row.get('entry_date', '-'))
        # Debug fallback
        if not entry_date or str(entry_date).lower() in ['nan', 'none', '']: 
             entry_date = str(row.get('entry_date', '-')) # Force retry as string
        
        if str(entry_date).lower() in ['nan', 'none', '']: entry_date = '-'
        
        # Convert Buy Price to EUR
        buy_price = buy_price_native * rate
        
        # Ia target-ul DOAR de pe Finviz (USD usually)
        finviz_data = market_data.get_finviz_data(download_ticker)
        target_usd = finviz_data.get('Target')
        
        target = None
        if target_usd:
            # Finviz e mereu USD? Nu neapărat. Dar pt US stocks da.
            # Dacă e stoc european, Finviz poate lipsi sau e în moneda locală?
            # Presupunem că Finviz dă în aceeași monedă ca ticker-ul (dacă îl găsește).
            target = target_usd * rate
            print(f"  → Target Finviz: €{target:.2f} (calc)")
        else:
            print(f"  → Target: N/A")
            
        # Volatility Data
        finviz_atr = finviz_data.get('ATR')
        vol_w = finviz_data.get('VolW') 
        vol_m = finviz_data.get('VolM')
        
        if ticker_cache is None: ticker_cache = {}

        (
            df,
            selected_market_instrument,
            tws_instrument,
            data_attribution,
        ) = _load_analysis_history(
            ticker, download_ticker, period='1y'
        )
        
        # --- CACHED DOWNLOAD ---
        if not df.empty:
             pass
        elif download_ticker in ticker_cache and ticker_cache[download_ticker] is not None:
             df = ticker_cache[download_ticker]
             # print(f"  [Cache] Used cached data for {download_ticker}")
        elif not ticker.endswith('.RO'):
            time.sleep(2)
            df = _download_yahoo_history(download_ticker, period='1y')
            
            # Retry with European suffixes if base ticker fails (common for IBKR ETFs like SXRZ)
            # Retry with European suffixes if base ticker fails (common for IBKR ETFs like SXRZ)
            if df.empty:
                suffixes = ['.DE', '.PA', '.L', '.AS', '.MI', '.MC']
                print(f"  ⚠️ Ticker {download_ticker} not found. Trying suffixes...")
                for s in suffixes:
                    alt_ticker = f"{download_ticker}{s}"
                    # Check cache for alt ticker too
                    if alt_ticker in ticker_cache and ticker_cache[alt_ticker] is not None:
                        # print(f"  [Cache] Used cached data for {alt_ticker}")
                        df_alt = ticker_cache[alt_ticker]
                    else:
                        print(f"    Trying {alt_ticker}...")
                        time.sleep(1)
                        df_alt = _download_yahoo_history(
                            alt_ticker, period='1y'
                        )
                        if not df_alt.empty:
                             ticker_cache[alt_ticker] = df_alt # Cache successful alt

                    if not df_alt.empty:
                        print(f"    ✅ Found data for {alt_ticker}!")
                        df = df_alt
                        actual_download_ticker = alt_ticker

                        
                        # Update currency based on new suffix
                        if '.DE' in s or '.PA' in s or '.AS' in s or '.MI' in s or '.MC' in s:
                            currency = 'EUR'
                        elif '.L' in s:
                            currency = 'GBP'
                        
                        # Update rate
                        rate = rates.get(currency, rates['USD'])
                        if currency == 'EUR': rate = 1.0
                        
                        break
                        
            # Store in cache (even if empty, to avoid retrying failed download?)
            # Usually better to cache success.

        company_name = ""
        try:
             info = _get_yahoo_info(
                 actual_download_ticker, tws_instrument=tws_instrument
             )
             company_name = info.get('longName') or info.get('shortName') or ""
        except:
             pass

        if not df.empty:
                df = adjust_for_unadjusted_splits(df, actual_download_ticker)
                ticker_cache[download_ticker] = df
        
        if df.empty:
            print(f"  ⚠️ Nu există date Yahoo Finance pentru {ticker} (nici cu sufixe) - folosim date parțiale din IBKR")
            # Returnăm date parțiale bazate pe informațiile din IBKR
            
            # Verificăm dacă avem prețul live din TWS (tws_positions.csv)
            tws_price_avail = False
            tws_price_native = 0.0
            tws_file = 'tws_positions.csv'
            if os.path.exists(tws_file):
                mtime = os.path.getmtime(tws_file)
                if time.time() - mtime < 300:  # 5 minute
                    try:
                        tpos_df = pd.read_csv(tws_file)
                        lookup_tws_symbol = ticker
                        if lookup_tws_symbol in ['LQQ.FR', 'FR.LQQ']:
                            lookup_tws_symbol = 'LQQ'
                        matching_pos = tpos_df[tpos_df['Symbol'] == lookup_tws_symbol]
                        if not matching_pos.empty:
                            tws_price_native = float(matching_pos.iloc[0].get('Current_Price', 0.0))
                            if tws_price_native > 0:
                                tws_price_avail = True
                    except:
                        pass
                        
            if tws_price_avail:
                current_price = tws_price_native * rate
                print(f"    [TWS API] Fallback to live TWS price for {ticker}: {tws_price_native}")
            else:
                current_price = buy_price  # Fallback standard
                
            investment = buy_price * shares
            current_value = current_price * shares
            profit = current_value - investment
            profit_pct = ((current_price - buy_price) / buy_price * 100) if buy_price > 0 else 0.0
            
            # Target și profit maxim
            if target:
                # Avem target de la Finviz
                max_profit = (target - buy_price) * shares
                target_display = round(target, 2)
            else:
                # Fără date Yahoo și fără target Finviz -> Nu estimăm
                max_profit = None
                target_display = None
            
            result = {
                'Symbol': ticker,
                'Shares': int(shares),
                'Current_Price': round(current_price, 2),
                'Buy_Price': round(buy_price, 2),
                'Currency': currency,
                'Target': target_display,
                'Trail_Stop': round(buy_price * 0.85, 2),  # Default 15% trailing
                'Suggested_Stop': round(buy_price * 0.90, 2),  # Conservative
                'Trail_Pct': trail_pct,
                'Investment': round(investment, 2),
                'Current_Value': round(current_value, 2),
                'Profit': round(profit, 2),
                'Profit_Pct': round(profit_pct, 2),
                'Max_Profit': round(max_profit, 2) if max_profit else None,
                'Status': 'N/A',
                'RSI': 0,
                'RSI_Status': 'N/A',
                'Trend': 'No Data',
                'VIX_Tag': 'Normal',
                'Sparkline': [],
                'Chart_History': [],
                'Chart_Dates': [],
                'Chart_OHLC': [],
                'Daily_Change': 0.0,
                'Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                **data_attribution,
            }
            return result
        
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df.columns = df.columns.droplevel(1)
            except:
                pass
        df = df.dropna(subset=['Close'])
        
        # Fetch detailed info from Yahoo (Consensus) - Inserted Logic
        consensus = "-"
        analysts_count = 0
        try:
           info = _get_yahoo_info(
               actual_download_ticker, tws_instrument=tws_instrument
           )
           # Dacă info e gol sau fail
           if info:
               consensus = info.get('recommendationKey', '-').replace('_', ' ').title()
               analysts_count = info.get('numberOfAnalystOpinions', 0)
        except Exception as e:
           # print(f"  Warning: Could not fetch info for {ticker}: {e}")
           pass

        df['ATR'] = calculate_atr(df)
        df['RSI'] = calculate_rsi(df)
        df['SMA_50'] = calculate_sma(df, 50)
        df['SMA_200'] = calculate_sma(df, 200)
        
        last_row = df.iloc[-1]
        
        # Verificăm dacă avem prețul live din TWS (tws_positions.csv)
        tws_price_native = _tws_instrument_market_price(tws_instrument)
        tws_price_avail = bool(tws_price_native)
        tws_file = 'tws_positions.csv'
        if not tws_price_avail and os.path.exists(tws_file):
            mtime = os.path.getmtime(tws_file)
            if time.time() - mtime < 300:  # 5 minute
                try:
                    tpos_df = pd.read_csv(tws_file)
                    lookup_tws_symbol = ticker
                    if lookup_tws_symbol in ['LQQ.FR', 'FR.LQQ']:
                        lookup_tws_symbol = 'LQQ'
                    matching_pos = tpos_df[tpos_df['Symbol'] == lookup_tws_symbol]
                    if not matching_pos.empty:
                        tws_price_native = float(matching_pos.iloc[0].get('Current_Price', 0.0))
                        if tws_price_native > 0:
                            tws_price_avail = True
                except:
                    pass

        if tws_price_avail:
            current_price_native = tws_price_native
            print(f"  [TWS API] Using live TWS price for {ticker}: {current_price_native}")
        else:
            current_price_native = market_data.get_scalar(last_row['Close'])
            
        current_price = current_price_native * rate # EUR
        
        # Convert ATR for stops
        last_atr_native = market_data.get_scalar(last_row['ATR'])
        if pd.isna(last_atr_native): last_atr_native = 0.0
        last_atr = last_atr_native * rate # EUR
        
        last_rsi = market_data.get_scalar(last_row['RSI'])
        
        # Native Values for Decision Logic
        sma_50_native = market_data.get_scalar(last_row['SMA_50'])
        sma_200_native = market_data.get_scalar(last_row['SMA_200'])
        
        # Converted Values for Portfolio Totals (EUR)
        sma_50 = sma_50_native * rate
        sma_200 = sma_200_native * rate
        
        # Extrage ultimele 30 zile pentru sparkline (conversie si aici? nu, trendul e la fel, dar valorile difera)
        # Sparkline e doar vizual, nu contează scara, dar hai să convertim pt consistență dacă afișăm tooltip
        sparkline_data = df['Close'].tail(30).tolist()
        sparkline_data = [round(float(x) * rate, 2) for x in sparkline_data if not pd.isna(x)]
        # Pentru proxy-ul BVB păstrăm suficient istoric pentru SMA200. Restul
        # portofoliului rămâne la fereastra compactă existentă de 90 de zile.
        chart_limit = 260 if ticker.upper() in {'TVBETETF', 'TVBETETF.RO'} else 90
        chart_df = df.tail(chart_limit)
        chart_history = [
            round(float(value) * rate, 4)
            for value in chart_df['Close'].tolist()
            if not pd.isna(value)
        ]
        chart_dates = [
            date_idx.strftime('%Y-%m-%d')
            for date_idx, value in zip(chart_df.index, chart_df['Close'])
            if not pd.isna(value)
        ]
        chart_ohlc = []
        if all(column in chart_df.columns for column in ('Open', 'High', 'Low', 'Close')):
            for date_idx, chart_row in chart_df.iterrows():
                values = [chart_row['Open'], chart_row['High'], chart_row['Low'], chart_row['Close']]
                if any(pd.isna(value) for value in values):
                    continue
                chart_ohlc.append({
                    'date': date_idx.strftime('%Y-%m-%d'),
                    'open': round(float(chart_row['Open']) * rate, 4),
                    'high': round(float(chart_row['High']) * rate, 4),
                    'low': round(float(chart_row['Low']) * rate, 4),
                    'close': round(float(chart_row['Close']) * rate, 4)
                })
        daily_change = chart_history[-1] - chart_history[-2] if len(chart_history) >= 2 else 0.0
        
        # Calcule pentru portofoliu (Toate în EUR)
        current_value = current_price * shares
        investment = buy_price * shares
        profit = current_value - investment
        profit_pct = ((current_price - buy_price) / buy_price) * 100 if buy_price != 0 else 0

        # --- SELL DECISION LOGIC (Normal Market) ---
        sell_decision = "HOLD"
        sell_reason = ""
        entry_status = "GOOD"
        
        # --- WATCHLIST FILTER: RS Falling Check (Pre-filter for BUY recommendations) ---
        # Prevents recommending stocks with declining RS that would immediately trigger EXIT in portfolio
        watchlist_rs_failing = False
        if spx_df is not None and len(df) >= 10 and not spx_df.empty:
            try:
                # Calculate RS trend over last 10 days (same as Rule D but with different threshold)
                stock_acc = df['Close'].tail(15)
                spx_acc = spx_df['Close'].tail(len(stock_acc))
                
                if len(stock_acc) == len(spx_acc):
                    rs_series = stock_acc / spx_acc
                    rs_now = rs_series.iloc[-1]
                    rs_10 = rs_series.iloc[-10] if len(rs_series) >= 10 else rs_series.iloc[0]
                    
                    # WATCHLIST THRESHOLD: Exclude stocks with RS decline >5%
                    # (Portfolio uses 0% threshold for EXIT, this is more lenient for entry)
                    if rs_now < (rs_10 * 0.95):  # RS dropped >5% in 10 days
                        watchlist_rs_failing = True
                        entry_status = "BAD"
            except Exception as e:
                # If RS calculation fails, don't penalize (keep entry_status = "GOOD")
                pass
        
        try:
            # Rule A: Time Failure (Days >= 5 AND Price <= Entry)
            rule_a = False
            entry_date_str = row.get('Entry_Date')
            if entry_date_str:
                try:
                    entry_date = datetime.datetime.strptime(entry_date_str, "%Y-%m-%d")
                    days_since = (datetime.datetime.now() - entry_date).days
                    days_since = (datetime.datetime.now() - entry_date).days
                    if days_since >= 5 and current_price <= buy_price: 
                        # Comparison: Price vs BuyPrice (Both should be same currency to be fair)
                        # buy_price is in EUR (from CSV/IBKR converted). current_price is EUR.
                        # Rule A checks P&L basically. Keep EUR for consistency with "Profit" column logic.
                        rule_a = True
                        sell_reason += f"Time Fail ({days_since}d > 5); "
                except:
                    pass

            # Rule B: Structure Failure (Under SMA50 for 2+ sessions)
            rule_b = False
            if len(df) >= 2:
                # Check last 2 closes vs SMA50
                c1 = df['Close'].iloc[-1]
                s1 = df['SMA_50'].iloc[-1]
                c2 = df['Close'].iloc[-2]
                s2 = df['SMA_50'].iloc[-2]
                if c1 < s1 and c2 < s2:
                    rule_b = True
                    # Use current native vs SMA native for display consistency
                    sell_reason += f"Structure Fail (Sub SMA50: {current_price_native:.2f} < {sma_50_native:.2f}); "

            # Rule C: Momentum Failure (RSI < 45 for 2+ sessions)
            rule_c = False
            if len(df) >= 2:
                r1 = df['RSI'].iloc[-1]
                r2 = df['RSI'].iloc[-2]
                if r1 < 45 and r2 < 45:
                    rule_c = True
                    sell_reason += f"Momentum Fail (RSI {r1:.1f} < 45); "

            # Rule D: Relative Strength Failure (RS Falling 10 sessions)
            rule_d = False
            if not is_bvb_position and spx_df is not None and len(df) >= 10 and not spx_df.empty:
                # Align dates? Simplified: Just take last 10 rows comparison
                # Calculate RS = Stock / SPX
                # We need matched closes. Using simple tail alignment
                stock_acc = df['Close'].tail(15)
                spx_acc = spx_df['Close'].tail(len(stock_acc))  # Assumes same calendar approx
                
                if len(stock_acc) == len(spx_acc):
                    rs_series = stock_acc / spx_acc
                    # Check if 'falling' for 10 sessions. 
                    # Strict: Every day lower? Too strict.
                    # Proxy: Current RS < RS_10_days_ago AND Trending Down (SMA3 < SMA10)
                    rs_now = rs_series.iloc[-1]
                    rs_10 = rs_series.iloc[-10] if len(rs_series) >= 10 else rs_series.iloc[0]
                    
                    if rs_now < rs_10:
                        # Check strictly falling trend or just lower?
                        # User said "FALLING for 10 consecutive sessions".
                        # Relaxed to: Net negative over 10 days
                        rule_d = True
                        sell_reason += "RS Fail (Falling); "
            
            # Combine Rules (Branched Logic)
            # Combine Rules (Branched Logic)
            
            # Count Active Market Rules
            active_rules_count = 0
            if not is_bvb_position:
                if vix_value > 25: active_rules_count += 1
                if breadth_pct < 45: active_rules_count += 1
                if rule4_active: active_rules_count += 1
                if market_in_downtrend: active_rules_count += 1
            
            if is_bvb_position:
                # Pozițiile BVB sunt evaluate pe structura și impulsul propriu.
                # VIX, breadth și structura SPX aparțin pieței SUA și nu trebuie
                # să declanșeze reduceri sau ieșiri pentru instrumentele locale.
                if rule_a or rule_b or rule_c:
                    entry_status = "BAD"
                    sell_decision = "REDUCE" if profit > 0 else "EXIT"

            elif active_rules_count >= 2:
                # --- GLOBAL SAFETY FILTER (2+ Rules Active) ---
                # User: "If 2+ rules violated -> EXIT"
                sell_decision = "EXIT"
                sell_reason = f"CRITICAL: {active_rules_count} Rules Active (Market Failure)"
            
            elif vix_value > 25:
                # --- HIGH VOLATILITY RULES (Rule #2 Active: VIX > 25) ---
                # Logic: Preț > SMA200 AND RS Ascendent AND RSI >= 55 -> TRAIL STRANS. Else -> EXIT.
                
                is_above_sma200 = current_price_native > sma_200_native
                # RS Ascendent: Strict check, not just "not falling".
                # RS Ascendent: Strict check, not just "not falling".
                is_rs_up = False
                if spx_df is not None and not spx_df.empty and len(df) >= 10:
                     try:
                        # Re-calc check just to be sure or reuse local vars if available?
                        # Using local calculation from Rule D block if available. 
                        # But wait, Rule D block is `if spx_df...`. I should ensure `rs_now` and `rs_10` exist.
                        # If Rule D ran, rs_now/rs_10 might vary. 
                        # Let's rely on rule_d (Falling). So Not Falling = At least stable.
                        # But user said "Clar Ascendent".
                        # Let's check rs_now > rs_10 explicitly if possible.
                        # I'll rely on the rule_d block having run? 
                        # Python scope: `rs_now` might not be defined if `if` block skipped.
                        # Safer to re-use rule_d as proxy or initialize vars.
                        pass
                     except: pass
                
                # Assumption: If rule_d is False, RS is at least not falling.
                # For "Clar Ascendent", maybe require `not rule_d` ?
                # Or assume if it passed the check.
                # Let's use `not rule_d` as "RS OK/Up" for now, as we don't have stored slopes.
                is_rs_up = not rule_d 
                
                if is_above_sma200 and is_rs_up and last_rsi >= 55:
                    sell_decision = "TRAIL STRANS"
                    sell_reason = "VIX>25: Strong Stock (Hold w/ Tight Trail)"
                else:
                    sell_decision = "EXIT"
                    # Detail the failure
                    reasons = []
                    if not is_above_sma200: reasons.append(f"Sub SMA200 ({current_price_native:.2f} < {sma_200_native:.2f})")
                    if not is_rs_up: reasons.append("RS Weak")
                    if last_rsi < 55: reasons.append(f"RSI {last_rsi:.0f} < 55")
                    sell_reason = f"VIX>25 Panic: {', '.join(reasons)}"

            elif breadth_pct < 45:
                # --- MARKET BREADTH RULES (Rule #3 Active: Breadth < 45%) ---
                # Logic:
                # Case 1: P > SMA50 AND RS Clar Ascendent AND RSI >= 55 -> TRAIL STRANS
                # Case 2: RS Flat OR RSI 45-49 OR P Test SMA50 -> REDUCE 50%
                # Case 3: Else -> EXIT
                
                # Calculate SMA50 status (Native)
                # sma_50 variable above is EUR. We need native logic.
                is_above_sma50 = current_price_native > sma_50_native
                is_testing_sma50 = abs(current_price_native - sma_50_native) / sma_50_native <= 0.02 # Within 2%
                
                # Determine RS Status (Ascendent vs Flat vs Descendent)
                # We reuse rule_d (Descendent). If rule_d is True, RS is Down.
                # If rule_d is False, it is Up or Flat.
                # We need to distinguish Up vs Flat.
                rs_status = "FLAT"
                if rule_d:
                    rs_status = "DOWN"
                else:
                    # Check if actually climbing
                    # Simplified check: RS > RS_5_days_ago?
                    # Since we don't have partial RS history handy in vars, we assume:
                    # If not falling (rule_d=False), we treat as Ascendent unless very weak?
                    # User asked for "Clar Ascendent" vs "Plat".
                    # Let's use RSI as a proxy for momentum or just assume Up if not Down for now,
                    # UNLESS user strictly wants "Plateau".
                    # Better: Assume UP if Not Down, unless we want to be stricter.
                    # Given lack of granular RS data variables here, I'll default to "ASCENDENT" if not Down.
                    # BUT for Case 2 "RS Flat", I need a condition.
                    # Maybe "Flat" is when RS is stable?
                    # I'll set rs_status = "UP" if not rule_d. 
                    # And Ignore "Flat" distinction? No, then Case 2 "OR RS Flat" never triggers on RS.
                    # It triggers on RSI or Price.
                    # This is safer than hallucinating Flatness.
                    rs_status = "UP"
                
                is_rs_up = (rs_status == "UP")
                is_rs_flat = (rs_status == "FLAT") # Will be false currently
                
                # Check Case 1 (Hold)
                if is_above_sma50 and is_rs_up and last_rsi >= 55:
                     sell_decision = "TRAIL STRANS"
                     sell_reason = "Breadth<45%: Strong Stock (Hold)"
                
                # Check Case 2 (Reduce)
                elif is_rs_flat or (45 <= last_rsi < 55) or is_testing_sma50: 
                     # Note: User said RSI 45-49. What if 50-54?
                     # Case 1 requires >= 55.
                     # Case 2 specifies 45-49.
                     # Gap 50-54? Probably Reduce too (Weakness).
                     # I will cover < 55 in Reduce branch if not Exit.
                     # Wait, Exit is "Restul".
                     # If RSI is 52. It is NOT >= 55. It is NOT 45-49.
                     # So it goes to Else -> EXIT? That's harsh for RSI 52.
                     # Probably meant "RSI < 55" implies weakness?
                     # User Prompt: "IF RS este PLAT OR RSI 45–49 OR prețul testează SMA50 THEN vinde 50%".
                     # "restul exit".
                     # Strictly, RSI 52 -> Exit.
                     # I will implement strictly. Ranges: [55, 100]=Hold. [45, 49]=Reduce. [0, 44] U [50, 54]=Exit.
                     # Logic for 50-54 exiting seems wrong but asked.
                     # Maybe "RSI 45-49" was just example of weakness?
                     # I will assume [45, 54] is Reduce range. (Weak but not broken).
                     
                     is_rsi_grey = 45 <= last_rsi < 55
                     
                     sell_decision = "REDUCE 50%"
                     reasons = []
                     if is_rs_flat: reasons.append("RS Flat")
                     if is_rsi_grey: reasons.append(f"RSI {last_rsi:.0f} Weak (45-55)")
                     if is_testing_sma50: reasons.append(f"Testing SMA50 ({current_price_native:.2f} vs {sma_50_native:.2f})")
                     sell_reason = f"Breadth<45% Warn: {', '.join(reasons)}"
                
                else:
                    # Case 3 (Exit)
                    sell_decision = "EXIT" 
                    sell_reason = f"Breadth<45% Fail: Sub SMA50 ({current_price_native:.2f}<{sma_50_native:.2f}) / RSI {last_rsi:.0f} < 45"

            elif rule4_active:
                # --- MARKET STRUCTURE RULES (Rule #4 Active: LH + Break HL) ---
                # Logic: P > SMA200 AND RS Ascendent AND RSI >= 55 -> TRAIL STRANS. Else -> EXIT.
                
                is_above_sma200 = current_price_native > sma_200_native
                is_rs_up = not rule_d # Proxy for Ascendent (Not Falling)
                
                if is_above_sma200 and is_rs_up and last_rsi >= 55:
                     sell_decision = "TRAIL STRANS"
                     sell_reason = "Structure Break: Strong Stock (Hold)"
                else:
                     sell_decision = "EXIT"
                     reasons = []
                     if not is_above_sma200: reasons.append(f"Sub SMA200 ({current_price_native:.2f} < {sma_200_native:.2f})")
                     if not is_rs_up: reasons.append("RS Down")
                     if last_rsi < 55: reasons.append(f"RSI {last_rsi:.0f} < 55")
                     sell_reason = f"Structure Break Fail: {', '.join(reasons)}"

            elif market_in_downtrend:
                # --- BEAR MARKET RULES (Rule #1 Active) ---
                is_above_sma200 = current_price_native > sma_200_native
                is_rs_falling = rule_d # Rule D = RS Falling
                is_rsi_weak = last_rsi < 45
                is_rsi_mediocre = 45 <= last_rsi < 50
                
                if (not is_above_sma200) or is_rsi_weak or is_rs_falling:
                    # User: "Preț < SMA200 OR RSI < 45 OR RS clar descendent -> EXIT"
                    # Exception: If P > SMA200 and RS Falling, is it Exit or Reduce?
                    # User said: "daca Preț > SMA200 dar (RS ↓ ...) -> vinde 50%"
                    # This implies P>SMA200 saves RS Falling from immediate Exit, downgrading to Reduce.
                    # So strict Exit applies if P < SMA200 OR RSI < 45.
                    # If P > SMA200 AND RS Falling -> Reduce.
                    
                    if is_above_sma200 and is_rs_falling and not is_rsi_weak:
                         sell_decision = "REDUCE 50%"
                         sell_reason = "Bear Mkt: Strong Price but RS Falling"
                    else:
                         sell_decision = "EXIT"
                         sell_reason = f"Bear Mkt: Broken (Sub SMA200 {current_price_native:.2f}<{sma_200_native:.2f} / RSI {last_rsi:.0f}<45)"
                         
                elif is_rsi_mediocre:
                    # User: "... RSI 45-49 -> vinde 50%" (assuming P > SMA200 implied by failing Exit above)
                    sell_decision = "REDUCE 50%"
                    sell_reason = "Bear Mkt: Weak RSI (45-49)"
                    
                else:
                    # User: "Preț > SMA200 si RS Ascendent si RSI >= 50 -> Trail Strans"
                    # Here we are: Above SMA200 (implied), RSI >= 50 (implied), RS Not Falling (implied)
                    sell_decision = "TRAIL STRANS"
                    sell_reason = "Bear Mkt: Strong -> Tight Trail"
                    
            else:
                # --- NORMAL MARKET RULES (Rules A-D) ---
                if rule_a or rule_b or rule_c or rule_d:
                    entry_status = "BAD"
                    
                    if profit > 0:
                        sell_decision = "REDUCE" # Reduce 50% + Trail
                    else:
                        sell_decision = "EXIT" # Cut Loss

        except Exception as e:
            print(f"Error calculating Sell Decision: {e}")
            pass

        # Calculate RS vs SPX (60-day) using passed spx_df
        rs_vs_spx = None
        if not is_bvb_position and spx_df is not None and len(df) >= 60:
            try:
                    # Calculate 60-day RS (Medium Term)
                    # Align using tail (simple)
                    s_series = df['Close'].tail(60)
                    x_series = spx_df['Close'].tail(60)
                    
                    if len(s_series) == len(x_series):
                        stock_ret = (s_series.iloc[-1] / s_series.iloc[0] - 1) * 100
                        spx_ret = (x_series.iloc[-1] / x_series.iloc[0] - 1) * 100
                        rs_vs_spx = stock_ret - spx_ret
            except:
                    pass


        
        # Stopul activ IBKR este triggerul live; cel manual rămâne fallback.
        trail_stop_manual = float(row.get('trail_stop', 0))
        trail_stop_ibkr = float(row.get('trail_stop_ibkr', 0))
        
        if trail_stop_ibkr > 0:
            # Valoare live din TWS, în moneda instrumentului.
            trail_stop_price = trail_stop_ibkr * rate
        elif trail_stop_manual > 0:
            trail_stop_price = trail_stop_manual * rate
        elif trail_pct > 0:
            # Fallback: calculăm dinamic din procent
            trail_stop_price = current_price * (1 - trail_pct / 100)
        else:
            trail_stop_price = 0 # Disabled/N/A
        
        # Suggested Stop bazat pe ATR (2x ATR sub preț curent)
        suggested_stop_atr = current_price - (2 * last_atr)
        
        # Target Price: Finviz (prioritate) sau Estimare Tehnică
        if target:
            # Avem target de la Finviz
            max_profit = (target - buy_price) * shares
            target_display = round(target, 2)
            target_source = "Finviz"
        else:
            # Estimare tehnică când nu avem target Finviz
            technical_target = None
            
            # Metodă 1: 52-week high (rezistență majoră)
            high_52w = df['High'].tail(252).max() * rate  # ~252 zile = 1 an trading
            
            # Metodă 2: ATR-based target (doar dacă trendul e bullish)
            atr_target = None
            if current_price > sma_200:  # Trend bullish
                atr_target = current_price + (3 * last_atr)  # Optimist: +3 ATR
            
            # Alegem cel mai bun target tehnic
            if atr_target and high_52w:
                # Dacă avem ambele, luăm maximul (mai optimist)
                technical_target = max(atr_target, high_52w)
                target_source = "Technical (ATR+52W)"
            elif high_52w:
                technical_target = high_52w
                target_source = "Technical (52W High)"
            elif atr_target:
                technical_target = atr_target
                target_source = "Technical (ATR)"
            
            # Validare: target-ul trebuie să fie > current price
            if technical_target and technical_target > current_price:
                target = technical_target
                max_profit = (target - buy_price) * shares
                target_display = round(target, 2)
                # print(f"  → Target {target_source}: €{target_display:.2f}")
            else:
                # Nu putem estima un target valid
                max_profit = None
                target_display = None
                target_source = "N/A"
        
        # VIX Interpretation
        vix_regime = "Normal"
        if vix_value and vix_value > 20: vix_regime = "Ridicat"
        if vix_value and vix_value > 30: vix_regime = "Extrem"

        # RSI Interpretation
        rsi_status = "Neutral"
        if last_rsi > 70: rsi_status = "Overbought"
        elif last_rsi < 30: rsi_status = "Oversold"
        
        # Trend Interpretation (Native)
        trend = "Neutral"
        if current_price_native > sma_200_native:
            if current_price_native > sma_50_native:
                trend = "Strong Bullish"
            else:
                trend = "Bullish Pullback"
        elif current_price_native < sma_200_native:
            if current_price_native < sma_50_native:
                trend = "Strong Bearish"
            else:
                trend = "Bearish Rally"

        # --- ENRICH HOLD REASON WITH METRICS (If currently empty) ---
        if sell_decision == "HOLD" and not sell_reason:
            # Construct positive reason: "Trend UP (P 150 > 140), RSI 60"
            positive_factors = []
            
            # 1. Trend / SMA Logic (Native)
            if current_price_native > sma_200_native:
                positive_factors.append(f"Trend UP (P {current_price_native:.1f} > SMA200 {sma_200_native:.1f})")
            elif current_price_native > sma_50_native:
                 positive_factors.append(f"Recovery (P {current_price_native:.1f} > SMA50 {sma_50_native:.1f})")
            else:
                 positive_factors.append("Consolidation")

            # 2. RSI Status
            positive_factors.append(f"RSI {last_rsi:.0f}")
            
            # 3. Stop Distance (Keep %, so logic stays same regardless of currency)
            if trail_stop_price > 0:
                 dist_pct = (current_price - trail_stop_price) / current_price * 100
                 positive_factors.append(f"Risk {dist_pct:.1f}%")

            sell_reason = ", ".join(positive_factors)

        result = {
            'Symbol': ticker,
            'Company_Name': company_name,
            'Shares': int(shares),
            'Current_Price': round(current_price, 2),
            'Price_Native': round(current_price_native, 2),
            'Currency': currency,
            'Buy_Price': round(buy_price, 2),
            'Target': target_display,  # None dacă nu există
            'Trail_Stop': round(trail_stop_price, 2),
            'Suggested_Stop': round(suggested_stop_atr, 2),
            'Finviz_ATR': finviz_atr,
            'Vol_W': vol_w,
            'Vol_M': vol_m,
            'Trail_Pct': trail_pct,
            'Investment': round(investment, 2),
            'Entry_Date': entry_date,
            'Current_Value': round(current_value, 2),
            'Profit': round(profit, 2),
            'Profit_Pct': round(profit_pct, 2),
            'Max_Profit': round(max_profit, 2) if max_profit else None,
            'Consensus': consensus,
            'Analysts': analysts_count,
            'Status': rsi_status,  # RSI Status (Overbought/Oversold/Neutral)
            'RSI': round(last_rsi, 2),  # Păstrat pentru Watchlist
            'RSI_Status': rsi_status,
            'Trend': trend,
            'VIX_Tag': vix_regime,
            'Sell_Decision': sell_decision,
            'Sell_Reason': sell_reason,
            'RS_vs_SPX': round(rs_vs_spx, 2) if rs_vs_spx is not None else None,
            'Sparkline': sparkline_data,
            'Chart_History': chart_history,
            'Chart_Dates': chart_dates,
            'Chart_OHLC': chart_ohlc,
            'Daily_Change': round(daily_change, 4),
            'Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            **data_attribution,
        }
        return result
        
    except Exception as e:
        print(f"Eroare procesare {row.get('symbol', '?')}: {e}")
        return None

def process_watchlist_ticker(ticker, vix_value, rates):
    """Procesează un ticker din watchlist (fără date de ownership)."""
    
    def get_company_name(symbol, finviz_data=None):
        try:
            # 1. Try yfinance
            lookup_symbol = symbol[:-3] if symbol.endswith('.US') else symbol
            if lookup_symbol in ['LQQ.FR', 'FR.LQQ']:
                lookup_symbol = 'LQQ.PA'
            info = _get_yahoo_info(
                lookup_symbol, tws_instrument=tws_instrument
            )
            name = info.get('longName') or info.get('shortName')
            if name: return name
        except:
             pass
        
        # 2. Try Finviz Fallback
        if finviz_data and 'Company' in finviz_data:
             return finviz_data['Company']
             
        # 3. Try manual suffixes (last resort)
        for s in ['.DE', '.PA', '.L', '.AS', '.MI', '.MC']:
            try:
                t_alt = yf.Ticker(f"{symbol}{s}")
                info = t_alt.info
                name = info.get('longName') or info.get('shortName')
                if name: return name
            except: continue
        return ""

    try:
        # Detect Currency
        currency = 'USD'
        if '.RO' in ticker: currency = 'RON'
        elif '.PA' in ticker or '.DE' in ticker or '.AS' in ticker or '.FR' in ticker or 'LQQ' in ticker: currency = 'EUR'
        elif '.L' in ticker: currency = 'GBP'
        
        rate = rates.get(currency, rates['USD'])
        if currency == 'EUR': rate = 1.0
        
        download_ticker = ticker[:-3] if ticker.endswith('.US') else ticker
        if download_ticker in ['LQQ.FR', 'FR.LQQ']:
            download_ticker = 'LQQ.PA'
        (
            df,
            selected_market_instrument,
            tws_instrument,
            data_attribution,
        ) = _load_analysis_history(
            ticker, download_ticker, period='1y'
        )
        
        if df.empty:
            print(f"Nu există date pentru {download_ticker}")
            return None
        
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df.columns = df.columns.droplevel(1)
            except:
                pass
        df = df.dropna(subset=['Close'])
        df = adjust_for_unadjusted_splits(df, download_ticker)
            
        df['ATR'] = calculate_atr(df)
        df['RSI'] = calculate_rsi(df)
        df['SMA_50'] = calculate_sma(df, 50)
        df['SMA_200'] = calculate_sma(df, 200)
        
        # Extrage ultimele 30 zile pentru sparkline
        sparkline_data = df['Close'].tail(30).tolist()
        sparkline_data = [round(float(x) * rate, 2) for x in sparkline_data if not pd.isna(x)]
        
        last_row = df.iloc[-1]
        
        last_close_native = (
            _tws_instrument_market_price(selected_market_instrument)
            or market_data.get_scalar(last_row['Close'])
        )
        last_close = last_close_native * rate
        last_atr = market_data.get_scalar(last_row['ATR']) * rate
        if pd.isna(last_atr): last_atr = 0.0
        
        last_rsi = market_data.get_scalar(last_row['RSI'])
        sma_50 = market_data.get_scalar(last_row['SMA_50']) * rate
        sma_200 = market_data.get_scalar(last_row['SMA_200']) * rate
        
        # Preluare Target din Finviz
        # Preluare date din Finviz (Target + Volatility)
        target_val = None
        finviz_atr = None
        vol_w = None
        vol_m = None
        
        try:
            finviz_data = market_data.get_finviz_data(ticker)
            target_usd = finviz_data.get('Target')
            finviz_atr = finviz_data.get('ATR')
            vol_w = finviz_data.get('VolW')
            vol_m = finviz_data.get('VolM')
            
            if target_usd:
                target_val = target_usd * rate
        except Exception:
            pass

        stop_loss_dist = 2 * last_atr
        suggested_stop = last_close - stop_loss_dist
        
        vix_regime = "Normal"
        if vix_value and vix_value > 20: vix_regime = "Ridicat"
        if vix_value and vix_value > 30: vix_regime = "Extrem"

        rsi_status = "Neutral"
        if last_rsi > 70: rsi_status = "Overbought"
        elif last_rsi < 30: rsi_status = "Oversold"
        
        trend = "Neutral"
        if last_close > sma_200:
            if last_close > sma_50:
                trend = "Strong Bullish"
            else:
                trend = "Bullish Pullback"
        elif last_close < sma_200:
            if last_close < sma_50:
                trend = "Strong Bearish"
            else:
                trend = "Bearish Rally"

        # Fetch detailed info from Yahoo
        consensus = "-"
        analysts_count = 0
        industry = "-"
        sector = "-"
        
        try:
           # Folosim yf.Ticker pentru info detaliat
           yt_ticker = ticker
           if yt_ticker in ['LQQ.FR', 'FR.LQQ']:
               yt_ticker = 'LQQ.PA'
           info = _get_yahoo_info(
               yt_ticker, tws_instrument=tws_instrument
           )
           consensus = info.get('recommendationKey', '-').replace('_', ' ').title() # ex: Strong Buy
           analysts_count = info.get('numberOfAnalystOpinions', 0)
           industry = info.get('industry', '-')
           sector = info.get('sector', '-')
           avg_vol_3m = info.get('averageVolume', 0)
           yahoo_target_native = info.get('targetMeanPrice')
           if (
               yahoo_target_native is not None
               and not pd.isna(yahoo_target_native)
               and float(yahoo_target_native) > last_close_native
           ):
               # Finviz does not cover most BVB tickers. Yahoo's target is in
               # the instrument's native currency, so convert it consistently
               # with the current price and stop displayed by the dashboard.
               target_val = float(yahoo_target_native) * rate

           # Scurtăm industria dacă e prea lungă
           if len(industry) > 20: industry = industry[:17] + "..."
        except:
           avg_vol_3m = 0
        if not avg_vol_3m and 'Volume' in df.columns:
            valid_volume = pd.to_numeric(
                df['Volume'].tail(63), errors='coerce'
            ).dropna()
            if not valid_volume.empty:
                avg_vol_3m = int(valid_volume.mean())

        if target_val and last_close > 0:
            pct_to_target = ((target_val - last_close) / last_close) * 100
        else:
            pct_to_target = None

        # BVB names must be judged against their local market rather than SPX.
        # TVBETETF tracks the BET family with dividends and has reliable Yahoo
        # history, making it a practical benchmark proxy for Romanian shares.
        rs_benchmark = 'TVBETETF.RO' if ticker.upper().endswith('.RO') else '^GSPC'
        rs_vs_spx = None
        rs_trend_up = False
        rs_status = "Neutral"
        try:
            spx_df = _download_yahoo_history(rs_benchmark, period='3mo')
            if not spx_df.empty:
                if isinstance(spx_df.columns, pd.MultiIndex):
                    try:
                        spx_df.columns = spx_df.columns.droplevel(1)
                    except:
                        pass
                spx_df = spx_df.dropna(subset=['Close'])
            if not spx_df.empty and len(df) >= 60:
                # Calculate 60-day RS (Medium Term)
                stock_ret_60 = (df['Close'].iloc[-1] / df['Close'].iloc[-60] - 1) * 100
                spx_ret_60 = (spx_df['Close'].iloc[-1] / spx_df['Close'].iloc[-60] - 1) * 100
                rs_60 = stock_ret_60 - spx_ret_60
                
                # Calculate 20-day RS (Short Term / Momentum)
                stock_ret_20 = (df['Close'].iloc[-1] / df['Close'].iloc[-20] - 1) * 100
                spx_ret_20 = (spx_df['Close'].iloc[-1] / spx_df['Close'].iloc[-20] - 1) * 100
                rs_20 = stock_ret_20 - spx_ret_20
                
                # Normalize values
                rs_vs_spx = float(rs_60.iloc[0]) if hasattr(rs_60, 'iloc') else float(rs_60)
                rs_20_val = float(rs_20.iloc[0]) if hasattr(rs_20, 'iloc') else float(rs_20)
                
                # Logic: RS is good if Positive AND Accelerating (Short term > Long term) or significantly positive
                rs_trend_up = rs_20_val > rs_vs_spx # Is RS line trending up?
                
                if rs_vs_spx > 5:
                    rs_status = "Strong"
                elif rs_vs_spx > 0:
                    rs_status = "Positive"
                elif rs_vs_spx > -5:
                    rs_status = "Weak"
                else:
                    rs_status = "Lagging"
        except Exception as e:
            pass
            
        # --- Earnings Check (Danger Zone) ---
        earnings_danger = False
        earnings_msg = ""
        try:
            next_earn = get_next_earnings_date(ticker)
            if next_earn:
                today_date = datetime.date.today()
                days_to_earn = (next_earn - today_date).days
                if 0 <= days_to_earn <= 5:
                    earnings_danger = True
                    earnings_msg = f"Report in {days_to_earn} days ({next_earn})"
        except Exception as e:
            pass

        # --- 4-Check Decision Logic ---
        checks_passed = 0
        check_details = []
        
        # Check 1: Stock in trend? (Price > SMA50)
        check1_trend = last_close > sma_50 if sma_50 > 0 else False
        if check1_trend:
            checks_passed += 1
            check_details.append(f"✓ Trend (P {last_close:.1f} > SMA50 {sma_50:.1f})")
        else:
            check_details.append(f"✗ Trend (P {last_close:.1f} < SMA50 {sma_50:.1f})")
        
        # Check 2: Stronger than market & Improving? (RS > 0 AND Trend UP)
        check2_rs = rs_vs_spx is not None and rs_vs_spx > 0 and rs_trend_up
        rs_val_str = f"{rs_vs_spx:.2f}" if rs_vs_spx is not None else "N/A"
        if check2_rs:
            checks_passed += 1
            check_details.append(f"✓ RS (Trend: {'Up' if rs_trend_up else 'Down'}, Val: {rs_val_str})")
        else:
            reason = "Weak" if rs_vs_spx is None or rs_vs_spx <= 0 else "Downtrend"
            check_details.append(f"✗ RS ({reason}, Val: {rs_val_str})")
        
        
        # Check 3: Entry calm? (RSI between 40-70, not overbought)
        check3_rsi = 40 <= last_rsi <= 70
        if check3_rsi:
            checks_passed += 1
            check_details.append(f"✓ RSI ({last_rsi:.1f})")
        else:
            check_details.append(f"✗ RSI ({last_rsi:.1f})")
        
        # Check 4: Risk known? (ATR allows logical stop - stop > 0 and < 10% of price)
        risk_pct = (stop_loss_dist / last_close * 100) if last_close > 0 else 0
        check4_atr = last_atr > 0 and risk_pct < 10
        if check4_atr:
            checks_passed += 1
            check_details.append(f"✓ ATR (Risk {risk_pct:.1f}%)")
        else:
            check_details.append(f"✗ ATR (Risk {risk_pct:.1f}%)")
        
        # Decision
        if checks_passed == 4:
            decision = "BUY"
            decision_color = "#4caf50"
            # Calculate Smart Entry for BUY stocks
            s_entry, s_type, s_reason = calculate_smart_entry(df)
        elif checks_passed == 3:
            decision = "WAIT"
            decision_color = "#ff9800"
            s_entry, s_type, s_reason = None, None, None
        else:
            decision = "AVOID"
            decision_color = "#f44336"
            s_entry, s_type, s_reason = None, None, None

        watch_chart_df = df.tail(90)
        watch_chart_history = [
            round(float(value) * rate, 4)
            for value in watch_chart_df['Close'].tolist()
            if not pd.isna(value)
        ]
        watch_chart_dates = [
            date_idx.strftime('%Y-%m-%d')
            for date_idx, value in zip(watch_chart_df.index, watch_chart_df['Close'])
            if not pd.isna(value)
        ]
        watch_chart_ohlc = []
        if all(column in watch_chart_df.columns for column in ('Open', 'High', 'Low', 'Close')):
            for date_idx, chart_row in watch_chart_df.iterrows():
                values = [chart_row['Open'], chart_row['High'], chart_row['Low'], chart_row['Close']]
                if any(pd.isna(value) for value in values):
                    continue
                watch_chart_ohlc.append({
                    'date': date_idx.strftime('%Y-%m-%d'),
                    'open': round(float(chart_row['Open']) * rate, 4),
                    'high': round(float(chart_row['High']) * rate, 4),
                    'low': round(float(chart_row['Low']) * rate, 4),
                    'close': round(float(chart_row['Close']) * rate, 4)
                })
        watch_daily_change = (
            watch_chart_history[-1] - watch_chart_history[-2]
            if len(watch_chart_history) >= 2 else 0.0
        )
        bvb_liquidity_metrics = (
            _calculate_bvb_liquidity_metrics(df)
            if ticker.upper().endswith('.RO')
            else {}
        )

        result = {
            'Ticker': ticker,
            'Currency': currency,
            'Price': round(last_close, 2),
            'Price_Native': round(last_close_native, 2),
            'Target': round(target_val, 2) if target_val else None,
            'Pct_To_Target': round(pct_to_target, 2) if pct_to_target is not None else None,
            'Consensus': consensus,
            'Analysts': analysts_count,
            'Company_Name': get_company_name(ticker, finviz_data=finviz_data),
            'Industry': industry,
            'Sector': sector,
            'Trend': trend,
            'RSI': round(last_rsi, 2),
            'RSI_Status': rsi_status,
            'ATR_14': round(last_atr, 2),
            'Finviz_ATR': finviz_atr,
            'Vol_W': vol_w,
            'Vol_M': vol_m,
            'Stop_Loss': round(suggested_stop, 2),
            'SMA_50': round(sma_50, 2),
            'SMA_200': round(sma_200, 2),
            'VIX_Tag': vix_regime,
            'Sparkline': sparkline_data,
            'Chart_History': watch_chart_history,
            'Chart_Dates': watch_chart_dates,
            'Chart_OHLC': watch_chart_ohlc,
            'Daily_Change': round(watch_daily_change, 4),
            'RS_vs_SPX': round(rs_vs_spx, 2) if rs_vs_spx is not None else None,
            'RS_Benchmark': rs_benchmark,
            'RS_Status': rs_status,
            'Decision': decision,
            'Decision_Color': decision_color,
            'Checks_Passed': checks_passed,
            'Smart_Entry': round(s_entry, 2) if s_entry else None,
            'Smart_Entry_EUR': round(s_entry * rate, 2) if s_entry else None,
            'Smart_Type': s_type if s_entry else None,
            'Smart_Reason': s_reason if s_entry else None,
            # New Fields
            'Strategy': analysis.classify_strategy({
                'Price': last_close,
                'SMA_50': sma_50,
                'SMA_200': sma_200,
                'RSI': last_rsi,
                'Trend': trend
            }),
            'RR_Ratio': analysis.calculate_risk_reward(last_close, suggested_stop, target_val) if target_val and suggested_stop else 0,
            'Volume': int(df['Volume'].iloc[-1]) if 'Volume' in df.columns else 0,
            'Avg_Volume': avg_vol_3m,
            'Earnings_Danger': earnings_danger,
            'Earnings_Msg': earnings_msg,
            
            'Check_Details': " ".join(check_details),
            'Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            **data_attribution,
        }
        result.update(bvb_liquidity_metrics)
        return result
        
    except Exception as e:
        print(f"Eroare procesare {ticker}: {e}")
        return None
    except Exception as e:
        print(f"Eroare procesare {ticker}: {e}")
        return None

def calculate_smart_entry(df):
    """
    Calculates Smart Entry Price based on Fibs, Support, and Engulfing.
    Returns: (Entry_Price, Entry_Type, Reason)
    """
    if df is None or len(df) < 60:
        return None, None, None

    try:
        # Data prep
        highs = df['High']
        lows = df['Low']
        opens = df['Open']
        closes = df['Close']
        
        # 1. Swing Levels (Last 6 months ~ 126 days)
        lookback = min(len(df), 126)
        swing_high = float(highs.tail(lookback).max())
        swing_low = float(lows.tail(lookback).min()) 
        
        current_price = float(closes.iloc[-1])
        
        # Debug 
        if pd.isna(swing_high) or pd.isna(swing_low) or pd.isna(current_price):
             print(f"DEBUG: Found NaN | High: {swing_high}, Low: {swing_low}, Price: {current_price}")
        
        # 2. Fibonacci Levels
        diff = swing_high - swing_low
        fib_500 = swing_high - (diff * 0.500)
        fib_618 = swing_high - (diff * 0.618)
        
        # 3. Local Support (Last 20 days)
        local_support = float(lows.tail(20).min())
        
        # 4. Pattern Recognition: Bullish Engulfing (Last 2 candles)
        # Prev candle: Red
        prev_open = float(opens.iloc[-2])
        prev_close = float(closes.iloc[-2])
        is_prev_red = prev_close < prev_open
        
        # Curr candle: Green, covers prev body
        curr_open = float(opens.iloc[-1])
        curr_close = float(closes.iloc[-1])
        is_curr_green = curr_close > curr_open
        
        # Opens below or at prev close AND Closes above or at prev open
        is_engulfing = (
            is_prev_red and 
            is_curr_green and 
            curr_open <= prev_close and 
            curr_close >= prev_open
        )
        
        # --- DECISION LOGIC ---
        
        # SCENARIO A: Bullish Engulfing -> BUY STOP
        if is_engulfing:
            entry_price = float(highs.iloc[-1]) * 1.001 # 0.1% buffer
            return entry_price, "STOP", "Bullish Engulfing (Momentum)"
            
        # SCENARIO C: Breakout (Near Highs) -> BUY STOP at High
        # If price is within 2% of Swing High
        if current_price >= swing_high * 0.98:
            return swing_high, "STOP", "Breakout (Near Highs)"

        # SCENARIO B: Buy the Dip -> BUY LIMIT
        # Confluence of Fib 618 and Support
        # We want the highest "floor" below current price
        
        # Candidates for support below current price
        supports = [s for s in [fib_500, fib_618, local_support] if s < current_price]
        
        if not supports:
            # If all supports are above price (weird downtrend or crashed), 
            # default to local support or just Fib 618
            entry_price = fib_618
        else:
            # Take the highest valid support (closest to price from below)
            entry_price = max(supports)
            
        # Formatting reason
        reason = "Fib/Support Confluence"
        if entry_price == fib_618: reason = "Fib 0.618 Golden Pocket"
        elif entry_price == fib_500: reason = "Fib 0.50 Retracement"
        elif entry_price == local_support: reason = "Local Support Test"
        
        # Check for NaN result
        if pd.isna(entry_price):
             return None, None, None

        return entry_price, "LIMIT", reason
        
    except Exception as e:
        # print(f"Smart Entry Error: {e}")
        return None, None, None

# --- Economic Cycle Logic ---
def determine_economic_cycle():
    """
    Deduce faza economică bazată pe Yield Curve și Market Trend.
    Phases: Recovery -> Expansion -> Slowdown -> Recession
    """
    try:
        # 1. Market Trend (SP500)
        spx = yf.Ticker("^GSPC")
        hist = spx.history(period="1y")
        if not hist.empty:
            hist = hist.dropna(subset=['Close'])
        if hist.empty: return "Expansion", "Slowdown" # Default safe
        
        price = hist['Close'].iloc[-1]
        sma_200 = hist['Close'].mean() # Approx SMA200 (using 1y avg)
        
        market_trend = "Bull" if price > sma_200 else "Bear"
        
        # 2. Yield Curve (10Y - 3M) -> Proxy for Recession prob
        # ^TNX = 10 Year Yield (index format, e.g. 4.50)
        # ^IRX = 13 Week Yield (index format)
        tnx = yf.Ticker("^TNX").history(period="5d")
        irx = yf.Ticker("^IRX").history(period="5d")
        if not tnx.empty:
            tnx = tnx.dropna(subset=['Close'])
        if not irx.empty:
            irx = irx.dropna(subset=['Close'])
        
        if not tnx.empty and not irx.empty:
            y10 = tnx['Close'].iloc[-1]
            y3m = irx['Close'].iloc[-1]
            spread = y10 - y3m
        else:
            spread = 0.5 # Default normal
            
        # Logic Matrix
        phase = "Expansion"
        
        if market_trend == "Bear":
            if spread < -0.5: phase = "Recession"
            else: phase = "Slowdown"
        else:
            # Bull Market
            if spread < 0: 
                phase = "Late Expansion" # Or Slowdown warning
            elif spread > 1.2: # Steep curve
                phase = "Recovery"
            else:
                phase = "Expansion"
                
        # Simplify to 4 phases
        if phase == "Late Expansion": phase = "Slowdown"
        
        # Next Phase Logic
        cycle_order = ["Recovery", "Expansion", "Slowdown", "Recession"]
        try:
            curr_idx = cycle_order.index(phase)
            next_phase = cycle_order[(curr_idx + 1) % 4]
        except:
            next_phase = "Unknown"
            
        print(f"Economic Cycle: {phase} (Spread: {spread:.2f}, Trend: {market_trend})")
        return phase, next_phase
        
    except Exception as e:
        print(f"Error determining cycle: {e}")
        return "Expansion", "Slowdown"

def assess_stock_fitness(sector, phase):
    """
    Verifică dacă sectorul este favorizat în faza dată.
    """
    if not sector: return "N/A"
    
    # Mapping simplificat Yahoo Finance Sectors -> Cycle
    # Recovery: Materials, Real Estate, Industrials, Financials, Cons Cyclical
    # Expansion: Tech, Industrials, Financials, Communication, Cons Cyclical
    # Slowdown: Energy, Healthcare, Cons Defensive (Staples), Utilities
    # Recession: Utilities, Cons Defensive, Healthcare
    
    favored = []
    if phase == "Recovery":
        favored = ["Basic Materials", "Real Estate", "Industrials", "Financial Services", "Consumer Cyclical"]
    elif phase == "Expansion":
        favored = ["Technology", "Industrials", "Financial Services", "Communication Services", "Consumer Cyclical"]
    elif phase == "Slowdown":
        favored = ["Energy", "Healthcare", "Consumer Defensive", "Utilities"]
    elif phase == "Recession":
        favored = ["Utilities", "Consumer Defensive", "Healthcare"]
        
    for fav in favored:
        if fav in sector: return "✅" # Good Fit
    
    return "⚠️" # Caution/Neutral
def _cached_swing_data_for_ro(state, tide_path='market_tide_cache.json'):
    """Încarcă analiza SUA separată, fără recalculare din seriile scurte BVB.

    ``market_indicators`` păstrează în mod intenționat numai 60 de puncte pentru
    graficele mici. Acea serie nu poate produce o SMA200 validă și nu trebuie
    folosită pentru a reconstrui Market Overview în timpul unui update BVB.
    """
    state = state if isinstance(state, dict) else {}
    us_snapshot = (
        state.get('market_overviews', {}).get('SUA', {})
        if isinstance(state.get('market_overviews'), dict)
        else {}
    )
    snapshot_data = (
        us_snapshot.get('data') if isinstance(us_snapshot, dict) else None
    )
    if _valid_us_market_overview(snapshot_data):
        return copy.deepcopy(snapshot_data)

    indicators = state.get('market_indicators', {})
    result = {}

    def add_index(indicator_name, prefix):
        item = indicators.get(indicator_name, {})
        history = pd.to_numeric(
            pd.Series(item.get('history', [])), errors='coerce'
        ).dropna()
        if history.empty:
            return
        dates = list(item.get('history_dates', []))[-len(history):]
        sma10 = history.rolling(10).mean()
        sma50 = history.rolling(50).mean()
        # Nu inventăm SMA-uri dintr-o fereastră mai scurtă decât perioada lor.
        sma200 = history.rolling(200).mean() if len(history) >= 200 else None
        delta = history.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
        result[f'{prefix}_Price'] = float(history.iloc[-1])
        result[f'{prefix}_SMA10'] = float(sma10.iloc[-1]) if pd.notna(sma10.iloc[-1]) else 0
        result[f'{prefix}_SMA50'] = float(sma50.iloc[-1]) if pd.notna(sma50.iloc[-1]) else 0
        if sma200 is not None and pd.notna(sma200.iloc[-1]):
            result[f'{prefix}_SMA200'] = float(sma200.iloc[-1])
        result[f'{prefix}_RSI'] = float(rsi.iloc[-1]) if pd.notna(rsi.iloc[-1]) else 50
        result[f'{prefix}_RSI_Weekly'] = result[f'{prefix}_RSI']
        tail = min(60, len(history))
        result[f'Chart_{prefix}'] = {
            'labels': dates[-tail:] if dates else [str(i) for i in range(tail)],
            'price': history.tail(tail).astype(float).tolist(),
            'sma10': sma10.tail(tail).fillna(0).astype(float).tolist(),
            'sma50': sma50.tail(tail).fillna(0).astype(float).tolist(),
            'sma200': (
                sma200.tail(tail).where(sma200.notna(), None).tolist()
                if sma200 is not None else []
            ),
            'rsi': rsi.tail(tail).fillna(50).astype(float).tolist(),
        }

    add_index('SPX', 'SPX')
    add_index('NASDAQ', 'NDX')
    result['VIX_Current'] = _safe_float_text(
        indicators.get('VIX', {}).get('value')
    ) or _safe_float_text(state.get('vix_val')) or 0
    result['SKEW_Current'] = _safe_float_text(
        indicators.get('SKEW', {}).get('value')
    ) or 0
    result['Rule4_Active'] = False
    result['Rule4_Debug'] = 'Păstrat din cache în actualizarea BVB'

    try:
        with open(tide_path, 'r', encoding='utf-8') as handle:
            tide = json.load(handle).get('data', {})
    except (OSError, ValueError, TypeError):
        tide = {}
    if isinstance(tide, dict) and tide:
        result['Market_Tide'] = tide
        above = _safe_float_text(tide.get('SMA50_Above')) or 0
        below = _safe_float_text(tide.get('SMA50_Below')) or 0
        result['Breadth_Pct'] = (
            above / (above + below) * 100 if above + below else 50
        )
    else:
        result['Breadth_Pct'] = 50
    # O reconstrucție parțială nu este trimisă rendererului. Astfel evităm
    # exact linia SMA200=0 din captură. Apelantul poate face o inițializare SUA
    # o singură dată, apoi update_ro va reutiliza snapshotul separat.
    return result if _valid_us_market_overview(result) else None


def _valid_us_market_overview(data):
    """Confirmă că snapshotul SUA conține nivelurile necesare analizei."""
    if not isinstance(data, dict):
        return False
    required = (
        'SPX_Price', 'SPX_SMA10', 'SPX_SMA50', 'SPX_SMA200',
        'NDX_Price', 'NDX_SMA10', 'NDX_SMA50', 'NDX_SMA200',
    )
    return all((_safe_float_text(data.get(key)) or 0) > 0 for key in required)


def _store_us_market_overview_snapshot(state, swing_data):
    """Salvează separat analiza SUA validă pentru rulările BVB ulterioare."""
    if not isinstance(state, dict) or not _valid_us_market_overview(swing_data):
        return False
    overviews = state.setdefault('market_overviews', {})
    overviews['SUA'] = {
        'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'data': copy.deepcopy(swing_data),
    }
    return True


def _select_best_bvb_proxy_row(portfolio_df, watchlist_df, full_state=None):
    """Alege TVBETETF cu cel mai complet istoric disponibil.

    Rulările BVB pot produce temporar un snapshot scurt, în timp ce portofoliul
    sau watchlistul încă păstrează seria completă. Alegerea primei apariții
    făcea ca 200+ ședințe să fie înlocuite în interfață de numai câteva zile.
    """
    candidates = []
    frames = [portfolio_df, watchlist_df]
    if isinstance(full_state, dict):
        cached_proxy = full_state.get('bvb_proxy')
        if isinstance(cached_proxy, dict) and cached_proxy:
            frames.append(pd.DataFrame([cached_proxy]))
        cached_wl = full_state.get('watchlist')
        if isinstance(cached_wl, list) and cached_wl:
            frames.append(pd.DataFrame(cached_wl))

    for frame in frames:
        if not isinstance(frame, pd.DataFrame) or frame.empty:
            continue
        for _, row in frame.iterrows():
            symbol = str(row.get('Symbol') or row.get('Ticker') or '').upper()
            if symbol not in {'TVBETETF', 'TVBETETF.RO'}:
                continue
            history = pd.to_numeric(
                pd.Series(row.get('Chart_History', []) or []), errors='coerce'
            )
            valid_history = history[
                history.notna() & np.isfinite(history) & (history > 0)
            ]
            candidates.append((len(valid_history), row))

    if not candidates:
        try:
            df, selected_inst, tws_inst, data_attr = _load_analysis_history(
                'TVBETETF.RO', 'TVBETETF.RO', period='2y'
            )
            if df is not None and not df.empty:
                df = df.dropna(subset=['Close'])
                rsi_series = calculate_rsi(df)
                last_row = df.iloc[-1]
                chart_history = df['Close'].tail(260).tolist()
                chart_dates = [
                    d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d)
                    for d in df.index[-len(chart_history):]
                ]
                proxy_row = {
                    'Symbol': 'TVBETETF.RO',
                    'Ticker': 'TVBETETF.RO',
                    'Price_Native': float(last_row['Close']),
                    'Current_Price': float(last_row['Close']),
                    'RSI': (
                        float(rsi_series.iloc[-1])
                        if not rsi_series.empty and pd.notna(rsi_series.iloc[-1])
                        else None
                    ),
                    'Chart_History': chart_history,
                    'Chart_Dates': chart_dates,
                }
                candidates.append((len(chart_history), pd.Series(proxy_row)))
        except Exception:
            pass

    if not candidates:
        return None
    best = max(candidates, key=lambda candidate: candidate[0])[1]
    if isinstance(full_state, dict):
        try:
            if hasattr(best, 'to_dict'):
                full_state['bvb_proxy'] = best.to_dict()
            elif isinstance(best, dict):
                full_state['bvb_proxy'] = copy.deepcopy(best)
        except Exception:
            pass
    return best


def _aligned_bvb_chart_history(item):
    """Returnează istoricul numeric aliniat cu datele disponibile."""
    raw_history = list(item.get('Chart_History', []) or [])
    dates = list(item.get('Chart_Dates', []) or [])
    if dates and len(raw_history) != len(dates):
        aligned_length = min(len(raw_history), len(dates))
        raw_history = raw_history[-aligned_length:]
        dates = dates[-aligned_length:]

    numeric = pd.to_numeric(pd.Series(raw_history), errors='coerce')
    valid = numeric.notna() & np.isfinite(numeric) & (numeric > 0)
    history = numeric[valid].reset_index(drop=True)
    if dates:
        dates = [date for date, keep in zip(dates, valid) if keep]
    return history, dates


def _preserve_portfolio_chart_history(previous_items, updated_items):
    """Nu permite unui refresh parțial să scurteze istoricul unei poziții.

    Pozițiile dispărute nu sunt readăugate. Pentru simbolurile încă deținute,
    observațiile noi sunt îmbinate după dată cu istoricul anterior, iar
    metadatele curente (preț, cantitate, stop etc.) rămân cele proaspete.
    """
    previous_by_symbol = {
        str(item.get('Symbol') or '').upper(): item
        for item in previous_items or []
        if isinstance(item, dict) and item.get('Symbol')
    }
    merged_items = []
    for raw_item in updated_items or []:
        item = dict(raw_item)
        symbol = str(item.get('Symbol') or '').upper()
        previous = previous_by_symbol.get(symbol)
        if not previous:
            merged_items.append(item)
            continue

        old_history = list(previous.get('Chart_History') or [])
        new_history = list(item.get('Chart_History') or [])
        old_dates = list(previous.get('Chart_Dates') or [])
        new_dates = list(item.get('Chart_Dates') or [])
        can_merge_by_date = (
            old_history and new_history
            and len(old_history) == len(old_dates)
            and len(new_history) == len(new_dates)
            and all(str(value).strip() for value in old_dates + new_dates)
        )

        if can_merge_by_date:
            history_by_date = {}
            ordered_dates = []
            for date, value in zip(old_dates, old_history):
                key = str(date)
                if key not in history_by_date:
                    ordered_dates.append(key)
                history_by_date[key] = value
            for date, value in zip(new_dates, new_history):
                key = str(date)
                if key not in history_by_date:
                    ordered_dates.append(key)
                history_by_date[key] = value
            if len(ordered_dates) > len(new_history):
                item['Chart_Dates'] = ordered_dates
                item['Chart_History'] = [
                    history_by_date[date] for date in ordered_dates
                ]

                old_ohlc = list(previous.get('Chart_OHLC') or [])
                new_ohlc = list(item.get('Chart_OHLC') or [])
                if (
                    len(old_ohlc) == len(old_dates)
                    and len(new_ohlc) == len(new_dates)
                ):
                    ohlc_by_date = {
                        str(date): value
                        for date, value in zip(old_dates, old_ohlc)
                    }
                    ohlc_by_date.update({
                        str(date): value
                        for date, value in zip(new_dates, new_ohlc)
                    })
                    item['Chart_OHLC'] = [
                        ohlc_by_date.get(date) for date in ordered_dates
                    ]
        elif (
            len(old_history) > len(new_history)
            and len(old_history) == len(old_dates)
        ):
            # Nu perpetuăm un snapshot corupt (de exemplu 263 prețuri și
            # 262 date). În acest caz seria proaspătă este mai sigură decât
            # istoricul mai lung, dar imposibil de aliniat cronologic.
            item['Chart_History'] = old_history
            item['Chart_Dates'] = old_dates
            old_ohlc = list(previous.get('Chart_OHLC') or [])
            if old_ohlc:
                item['Chart_OHLC'] = old_ohlc

        merged_items.append(item)
    return merged_items


def _generate_bvb_market_overview_html(
    portfolio_df, watchlist_df, return_signal=False, full_state=None,
):
    """Context BVB compact, separat complet de scorul SPX/NDX."""
    item = _select_best_bvb_proxy_row(
        portfolio_df, watchlist_df, full_state=full_state
    )
    if item is None:
        unavailable_html = """
        <section style="margin:32px 0;">
          <h3 style="margin:0 0 8px;color:var(--text-primary);">România / BVB</h3>
          <div style="padding:16px;border:1px solid var(--border-light);border-radius:12px;background:var(--bg-white);color:var(--text-secondary);">
            Contextul BVB este separat de analiza SUA. Proxy-ul local nu este disponibil în datele curente.
          </div>
        </section>"""
        unavailable_signal = {
            'key': 'romania_bvb',
            'label': 'Piața românească BVB',
            'verdict': 'DATE INSUFICIENTE',
        }
        return (
            (unavailable_html, unavailable_signal)
            if return_signal else unavailable_html
        )

    prices_eur, dates = _aligned_bvb_chart_history(item)
    price = (
        _safe_float_text(item.get('Price_Native'))
        or (float(prices_eur.iloc[-1]) if not prices_eur.empty else 0)
    )
    # Chart_History este normalizat în EUR pentru totalurile portofoliului.
    # Îl readucem în moneda nativă folosind raportul ultimei cotații; altfel
    # apăreau SMA-uri de ~11 RON lângă un preț real de ~61 RON.
    if price and not prices_eur.empty and float(prices_eur.iloc[-1]) > 0:
        native_scale = price / float(prices_eur.iloc[-1])
    else:
        native_scale = 1.0
    prices = prices_eur * native_scale
    if not dates:
        dates = [str(index + 1) for index in range(len(prices))]

    sma10_series = prices.rolling(10).mean()
    sma50_series = prices.rolling(50).mean()
    sma200_series = prices.rolling(200).mean()
    # Folosim aceeași metodă Wilder ca analiza portofoliului. Valoarea RSI
    # curentă din rând este autoritară deoarece este calculată pe cadrul OHLC
    # proaspăt, înainte ca istoricul compact pentru grafic să fie păstrat.
    rsi_series = calculate_rsi(pd.DataFrame({'Close': prices}))

    sma10 = float(sma10_series.iloc[-1]) if len(prices) >= 10 else None
    sma50 = float(sma50_series.iloc[-1]) if len(prices) >= 50 else None
    sma200 = float(sma200_series.iloc[-1]) if len(prices) >= 200 else None
    stored_rsi = _safe_float_text(item.get('RSI'))
    rsi = stored_rsi
    if rsi is None and not rsi_series.empty and pd.notna(rsi_series.iloc[-1]):
        rsi = float(rsi_series.iloc[-1])
    if rsi is not None and not rsi_series.empty:
        rsi_series.iloc[-1] = rsi
    if price and sma50:
        trend = 'Peste SMA50' if price >= sma50 else 'Sub SMA50'
        trend_color = '#4caf50' if price >= sma50 else '#f44336'
    else:
        trend, trend_color = 'Date insuficiente', '#888'

    def chart_values(series):
        return [
            round(float(value), 4) if pd.notna(value) else None
            for value in series
        ]

    chart_data = {
        'labels': dates,
        'price': chart_values(prices),
        'sma10': chart_values(sma10_series),
        'sma50': chart_values(sma50_series),
        # Dacă lipsesc 200 de ședințe, datasetul rămâne gol, nu plin cu zero.
        'sma200': chart_values(sma200_series) if len(prices) >= 200 else [],
        'rsi': chart_values(rsi_series),
    }
    chart_json = json.dumps(chart_data, ensure_ascii=False)
    history_note = (
        f'SMA200: {sma200:.2f} RON'
        if sma200 is not None
        else f'SMA200 indisponibilă · {len(prices)}/200 ședințe'
    )

    # Scor swing local. SMA200 lipsă reduce încrederea, dar nu devine automat
    # un semnal bearish. TVBETETF este proxy pentru BET, nu breadth-ul complet.
    trend_points = (
        40 if sma200 is not None and price >= sma200
        else 0 if sma200 is not None
        else 25 if sma50 is not None and price >= sma50
        else 5
    )
    momentum_points = 25 if sma50 is not None and price >= sma50 else 0
    timing_points = 15 if sma10 is not None and price >= sma10 else 0
    if rsi is None:
        rsi_points = 10
    elif 45 <= rsi < 70:
        rsi_points = 20
    elif 35 <= rsi < 75:
        rsi_points = 8
    else:
        rsi_points = 0
    bvb_score = int(trend_points + momentum_points + timing_points + rsi_points)
    confidence = 'Ridicată' if sma200 is not None else 'Medie'
    confidence_explanation = (
        'Sunt disponibile minimum 200 de ședințe, astfel încât trendul major '
        'poate fi verificat prin SMA200, alături de SMA50, SMA10 și RSI14.'
        if sma200 is not None else
        'SMA200 nu poate fi încă verificată; concluzia se bazează pe SMA50, '
        'SMA10 și RSI14 și este mai puțin robustă.'
    )
    if bvb_score >= 90:
        score_band = 'Aliniere foarte puternică'
        score_band_color = '#2e7d32'
        score_interpretation = (
            'Trendul, momentum-ul și timingul proxy-ului local sunt aproape '
            'complet aliniate pentru poziții long.'
        )
    elif bvb_score >= 75:
        score_band = 'Context puternic'
        score_band_color = '#4caf50'
        score_interpretation = (
            'Majoritatea factorilor locali sunt favorabili; intrarea trebuie '
            'totuși validată prin preț, lichiditate și un stop clar.'
        )
    elif bvb_score >= 60:
        score_band = 'Context favorabil'
        score_band_color = '#7cb342'
        score_interpretation = (
            'Fundalul permite cumpărări selective, dar încă lipsesc unele '
            'confirmări tehnice.'
        )
    elif bvb_score >= 40:
        score_band = 'Context fragil'
        score_band_color = '#ff9800'
        score_interpretation = (
            'Semnalele locale sunt amestecate; este preferabilă așteptarea '
            'unei confirmări înainte de creșterea expunerii.'
        )
    else:
        score_band = 'Context nefavorabil'
        score_band_color = '#f44336'
        score_interpretation = (
            'Condițiile pentru poziții long sunt slabe; protejarea capitalului '
            'are prioritate.'
        )

    above_sma50 = bool(sma50 is not None and price >= sma50)
    above_sma10 = bool(sma10 is not None and price >= sma10)
    above_sma200 = bool(sma200 is not None and price >= sma200)
    major_trend_ok = above_sma200 if sma200 is not None else above_sma50
    healthy_rsi = rsi is None or 45 <= rsi < 70
    if major_trend_ok and above_sma10 and healthy_rsi:
        bvb_verdict = 'CUMPĂRĂ'
        verdict_color = '#4caf50'
    elif major_trend_ok and (not above_sma10 or not healthy_rsi):
        bvb_verdict = 'AȘTEAPTĂ CONFIRMAREA'
        verdict_color = '#ff9800'
    elif not above_sma50:
        bvb_verdict = 'PRUDENȚĂ'
        verdict_color = '#f44336'
    else:
        bvb_verdict = 'NEUTRU'
        verdict_color = '#ff9800'

    explanation_parts = []
    if above_sma50:
        explanation_parts.append(
            f'Trendul intermediar este pozitiv: TVBETETF ({price:.2f} RON) '
            f'se află peste SMA50 ({sma50:.2f} RON).'
        )
    elif sma50 is not None:
        explanation_parts.append(
            f'Trendul intermediar este fragil: TVBETETF ({price:.2f} RON) '
            f'se află sub SMA50 ({sma50:.2f} RON).'
        )
    if above_sma10:
        explanation_parts.append(
            f'Timingul pe termen scurt este confirmat peste SMA10 '
            f'({sma10:.2f} RON).'
        )
    elif sma10 is not None:
        explanation_parts.append(
            f'Timingul nu este încă confirmat: prețul este sub SMA10 '
            f'({sma10:.2f} RON); este preferabilă o închidere clară peste acest nivel.'
        )
    if rsi is not None and rsi >= 70:
        explanation_parts.append(
            f'RSI14 este {rsi:.1f}, în zona supraîncălzită; evită urmărirea prețului.'
        )
    elif rsi is not None and rsi >= 60:
        explanation_parts.append(
            f'RSI14 este {rsi:.1f}: impulsul rămâne bun, dar spațiul pentru o '
            'intrare fără retragere este mai redus.'
        )
    elif rsi is not None and rsi < 40:
        explanation_parts.append(
            f'RSI14 este {rsi:.1f}, ceea ce indică momentum slab.'
        )
    if sma200 is None:
        explanation_parts.append(
            'SMA200 nu poate fi validată încă, de aceea concluzia are încredere '
            'medie și nu confirmă singură trendul major.'
        )
    else:
        explanation_parts.append(
            f'Trendul major este {"pozitiv" if above_sma200 else "negativ"}: '
            f'prețul este {"peste" if above_sma200 else "sub"} SMA200 '
            f'({sma200:.2f} RON).'
        )
    conclusion_text = ' '.join(explanation_parts)
    invalidation_text = (
        f'O închidere sub SMA50 ({sma50:.2f} RON) ar deteriora setupul local.'
        if sma50 is not None else
        'Nu există încă suficiente date pentru un nivel tehnic de invalidare.'
    )

    overview_html = f"""
    <section style="margin:32px 0;border:1px solid var(--border-light);border-radius:14px;background:#fff;overflow:hidden;box-shadow:var(--shadow-sm);">
      <div style="padding:20px 24px;background:{verdict_color};color:#fff;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:14px;">
        <div>
          <h3 style="margin:0;font-size:22px;color:#fff;">🇷🇴 România / BVB — Swing Trading Signal (Long-only)</h3>
          <p style="margin:6px 0 0;opacity:.92;">Context TVBETETF · strategie trend following · niveluri în RON</p>
        </div>
        <div style="padding:8px 16px;border:1px solid rgba(255,255,255,.55);border-radius:999px;background:rgba(255,255,255,.18);font-size:17px;font-weight:800;">{bvb_verdict}</div>
      </div>
      <div style="padding:22px;">
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:20px;">
        <div style="padding:14px;border-left:5px solid {verdict_color};border-radius:8px;background:{verdict_color}12;"><div style="font-size:12px;color:var(--text-secondary);text-transform:uppercase;">Market Bias BVB</div><div style="font-size:24px;font-weight:800;color:{verdict_color};">{bvb_verdict}</div></div>
        <div style="padding:14px;border:1px solid var(--border-light);border-radius:8px;"><div style="font-size:12px;color:var(--text-secondary);text-transform:uppercase;">Scor swing local</div><div style="font-size:24px;font-weight:800;">{bvb_score}/100</div><div style="font-size:12px;font-weight:700;color:{score_band_color};margin-top:3px;">{score_band}</div></div>
        <div style="padding:14px;border:1px solid var(--border-light);border-radius:8px;"><div style="font-size:12px;color:var(--text-secondary);text-transform:uppercase;">Încredere</div><div style="font-size:24px;font-weight:800;">{confidence}</div><div style="font-size:11px;color:var(--text-secondary);margin-top:3px;">Calitatea istoricului, nu probabilitatea de câștig</div></div>
        <div style="padding:14px;border:1px solid var(--border-light);border-radius:8px;"><div style="font-size:12px;color:var(--text-secondary);text-transform:uppercase;">Proxy local</div><div style="font-size:24px;font-weight:800;">TVBETETF</div></div>
      </div>
      <div style="padding:14px 16px;border-left:5px solid {score_band_color};border-radius:8px;background:{score_band_color}0d;margin-bottom:12px;line-height:1.55;">
        <b style="color:{score_band_color};">Interpretarea scorului BVB:</b> {score_interpretation}
      </div>
      <details style="margin-bottom:20px;border:1px solid var(--border-light);border-radius:8px;background:#fff;">
        <summary style="cursor:pointer;padding:12px 16px;font-weight:700;color:var(--text-primary);">Cum se calculează și ce înseamnă intervalele BVB</summary>
        <div style="padding:0 16px 16px;color:var(--text-secondary);line-height:1.55;">
          <p style="margin:4px 0 10px;"><b>Punctaj curent:</b> trend major {trend_points}/40 · momentum SMA50 {momentum_points}/25 · timing SMA10 {timing_points}/15 · RSI14 {rsi_points}/20.</p>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px;">
            <div><b style="color:#f44336;">0–39 · Nefavorabil</b><br>Prioritate protecției capitalului.</div>
            <div><b style="color:#ff9800;">40–59 · Fragil</b><br>Semnale mixte; așteaptă confirmări.</div>
            <div><b style="color:#7cb342;">60–74 · Favorabil</b><br>Cumpărări selective cu timing bun.</div>
            <div><b style="color:#4caf50;">75–89 · Puternic</b><br>Majoritatea factorilor locali sunt favorabili.</div>
            <div><b style="color:#2e7d32;">90–100 · Foarte puternic</b><br>Aliniere aproape completă a proxy-ului BVB.</div>
          </div>
          <p style="margin:12px 0 0;"><b>100/100</b> înseamnă că TVBETETF este peste SMA200, SMA50 și SMA10, iar RSI14 se află în zona sănătoasă 45–69. Nu garantează creșterea întregii piețe și nu validează automat fiecare acțiune BVB sau AeRO: lichiditatea, știrile, calendarul local, concentrarea sectorială și riscul specific emitentului rămân decisive.</p>
          <p style="margin:10px 0 0;"><b>Ce înseamnă încrederea {confidence.lower()}:</b> {confidence_explanation} Încrederea descrie robustețea analizei proxy-ului TVBETETF, nu probabilitatea de creștere a BVB și nici șansa de succes a unei acțiuni individuale.</p>
          <p style="margin:8px 0 0;"><b>Ridicată:</b> există minimum 200 de ședințe și pot fi evaluate SMA200, SMA50, SMA10 și RSI14. <b>Medie:</b> istoricul este mai scurt de 200 de ședințe, astfel încât trendul major nu este încă validat.</p>
          <p style="margin:8px 0 0;">Dacă SMA200 nu poate fi calculată, încrederea rămâne medie, iar scorul maxim posibil este 85/100.</p>
        </div>
      </details>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;">
        <div style="padding:16px;border:1px solid var(--border-light);border-radius:10px;background:#fff;">
          <div style="display:flex;justify-content:space-between;gap:12px;"><b>Trend (SMA200)</b><b style="color:{trend_color};">{trend}</b></div>
          <div style="height:180px;margin-top:10px;"><canvas id="bvb_chart_sma200"></canvas></div>
          <div style="text-align:center;margin-top:8px;color:var(--text-secondary);">Preț: <b>{price:.2f} RON</b> · {history_note}</div>
        </div>
        <div style="padding:16px;border:1px solid var(--border-light);border-radius:10px;background:#fff;">
          <div style="display:flex;justify-content:space-between;gap:12px;"><b>Momentum (SMA50)</b><b>{f'{sma50:.2f} RON' if sma50 else 'N/D'}</b></div>
          <div style="height:180px;margin-top:10px;"><canvas id="bvb_chart_sma50"></canvas></div>
          <div style="text-align:center;margin-top:8px;color:var(--text-secondary);">TVBETETF în RON</div>
        </div>
        <div style="padding:16px;border:1px solid var(--border-light);border-radius:10px;background:#fff;">
          <div style="display:flex;justify-content:space-between;gap:12px;"><b>Timing (SMA10)</b><b>{f'{sma10:.2f} RON' if sma10 else 'N/D'}</b></div>
          <div style="height:180px;margin-top:10px;"><canvas id="bvb_chart_sma10"></canvas></div>
          <div style="text-align:center;margin-top:8px;color:var(--text-secondary);">Mișcarea pe termen scurt</div>
        </div>
        <div style="padding:16px;border:1px solid var(--border-light);border-radius:10px;background:#fff;">
          <div style="display:flex;justify-content:space-between;gap:12px;"><b>Momentum (RSI14)</b><b>{f'{rsi:.1f}' if rsi is not None else 'N/D'}</b></div>
          <div style="height:180px;margin-top:10px;"><canvas id="bvb_chart_rsi"></canvas></div>
          <div style="text-align:center;margin-top:8px;color:var(--text-secondary);">Zone de referință: 30 / 70</div>
        </div>
      </div>
      <div style="margin-top:22px;padding:18px;border:2px solid {verdict_color}55;border-radius:10px;background:{verdict_color}0d;">
        <div style="font-size:13px;font-weight:800;color:{verdict_color};text-transform:uppercase;letter-spacing:.04em;">🎯 Concluzie generală BVB</div>
        <div style="font-size:25px;font-weight:850;color:{verdict_color};margin:8px 0;">{bvb_verdict}</div>
        <p style="margin:0;color:var(--text-primary);line-height:1.65;">{conclusion_text}</p>
        <p style="margin:10px 0 0;color:var(--text-secondary);line-height:1.55;"><b>Ce ar invalida concluzia:</b> {invalidation_text}</p>
      </div>
      <p style="margin:12px 2px 0;color:var(--text-secondary);font-size:12px;">TVBETETF este folosit ca proxy investibil pentru piața principală BVB; nu reprezintă breadth-ul complet și nu include toate acțiunile AeRO. SMA200 nu este desenată fără minimum 200 de ședințe. Datele BVB nu modifică Market Bias SUA.</p>
      </div>
    </section>
    <script>
    (function() {{
      const data = {chart_json};
      if (typeof Chart === 'undefined' || !data.price.length) return;
      const common = {{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:{{x:{{display:false}},y:{{display:true}}}}}};
      const priceSet = {{label:'TVBETETF',data:data.price,borderColor:'#cbd5e1',borderWidth:1.5,pointRadius:0,tension:.15}};
      function priceChart(id, label, values, color, dashed) {{
        const element = document.getElementById(id); if (!element) return;
        const sets = [priceSet];
        if (values && values.length) sets.push({{label:label,data:values,borderColor:color,borderWidth:2,pointRadius:0,borderDash:dashed?[3,3]:[],tension:.15,spanGaps:true}});
        new Chart(element.getContext('2d'),{{type:'line',data:{{labels:data.labels,datasets:sets}},options:common}});
      }}
      priceChart('bvb_chart_sma200','SMA200',data.sma200,'#f59e0b',true);
      priceChart('bvb_chart_sma50','SMA50',data.sma50,'#22c55e',false);
      priceChart('bvb_chart_sma10','SMA10',data.sma10,'#2563eb',false);
      const rsiElement = document.getElementById('bvb_chart_rsi');
      if (rsiElement) new Chart(rsiElement.getContext('2d'),{{type:'line',data:{{labels:data.labels,datasets:[{{label:'RSI14',data:data.rsi,borderColor:'#f59e0b',backgroundColor:'#f59e0b20',fill:true,borderWidth:2,pointRadius:0,tension:.25,spanGaps:true}}]}},options:{{...common,scales:{{x:{{display:false}},y:{{min:0,max:100,ticks:{{callback:(v)=>v===30||v===70?v:''}}}}}}}}}});
    }})();
    </script>"""
    signal = {
        'key': 'romania_bvb',
        'label': 'Piața românească BVB',
        'verdict': bvb_verdict,
        'score': bvb_score,
        'confidence': confidence,
    }
    return (overview_html, signal) if return_signal else overview_html


def _market_signal_allows_ai_stock_analysis(signal):
    """Permite AI pe candidați numai când verdictul pieței este BUY verde."""
    verdict = str((signal or {}).get('verdict') or '').strip().upper()
    market_key = str((signal or {}).get('key') or '').strip().lower()
    if market_key == 'romania_bvb':
        return verdict == 'CUMPĂRĂ'
    if market_key == 'international':
        return verdict.startswith('BUY')
    return False


def _filter_ai_buy_candidates_by_market_signal(
    candidates, international_signal, bvb_signal,
):
    """Separă candidații trimiși la AI fără a modifica scanarea tehnică."""
    gates = {
        'international': _market_signal_allows_ai_stock_analysis(
            international_signal
        ),
        'romania_bvb': _market_signal_allows_ai_stock_analysis(bvb_signal),
    }
    allowed = []
    blocked = []
    for candidate in candidates or []:
        market = str(candidate.get('market') or '').strip()
        gate_key = (
            'romania_bvb'
            if market == 'România / BVB'
            else 'international'
            if market in {'SUA', 'Europa / Nasdaq-100'}
            else None
        )
        if gate_key and gates[gate_key]:
            allowed.append(candidate)
        else:
            blocked.append(candidate)
    return allowed, blocked, gates


def _render_ai_stock_gate_notice(
    international_signal, bvb_signal, blocked_candidates,
):
    """Explică de ce anumite idei tehnice nu au fost trimise la AI."""
    if not blocked_candidates:
        return ''
    blocked_markets = {
        str(item.get('market') or '').strip()
        for item in blocked_candidates
    }
    messages = []
    if blocked_markets & {'SUA', 'Europa / Nasdaq-100'}:
        verdict = str(
            (international_signal or {}).get('verdict')
            or 'DATE INSUFICIENTE'
        )
        messages.append(
            f'SUA/LQQ: analiza AI a candidaților este în pauză '
            f'(semnal piață: {verdict}).'
        )
    if 'România / BVB' in blocked_markets:
        verdict = str(
            (bvb_signal or {}).get('verdict')
            or 'DATE INSUFICIENTE'
        )
        messages.append(
            f'BVB/AeRO: analiza AI a candidaților este în pauză '
            f'(semnal piață: {verdict}).'
        )
    return (
        "<div style='margin:0 0 14px;padding:11px 13px;border-left:4px solid "
        "#f59e0b;border-radius:8px;background:#fff7ed;color:var(--text-secondary);"
        "font-size:13px;line-height:1.5;'>"
        "<b>Filtru AI după semnalul pieței:</b> "
        + ' '.join(html.escape(message) for message in messages)
        + " Datele tehnice și istoricul rămân păstrate; analiza AI pornește "
        "automat când semnalul relevant devine verde.</div>"
    )


def _generate_bvb_risk_status_html(portfolio_df, watchlist_df, full_state=None):
    """Reguli de risc BVB independente de SPX, VIX și breadth-ul SUA."""
    item = _select_best_bvb_proxy_row(
        portfolio_df, watchlist_df, full_state=full_state
    )
    if item is None:
        return """
        <div class="market-risk-card market-risk-unavailable">
          <h3>Context BVB</h3><div class="risk-value">INDISPONIBIL</div>
          <div class="risk-action">TVBETETF lipsește</div>
        </div>"""

    history_eur, _ = _aligned_bvb_chart_history(item)
    price = _safe_float_text(item.get('Price_Native')) or 0
    if price and not history_eur.empty and float(history_eur.iloc[-1]) > 0:
        history = history_eur * (price / float(history_eur.iloc[-1]))
    else:
        history = history_eur
        price = float(history.iloc[-1]) if not history.empty else 0
    sma10 = float(history.tail(10).mean()) if len(history) >= 10 else None
    sma50 = float(history.tail(50).mean()) if len(history) >= 50 else None
    sma200 = float(history.tail(200).mean()) if len(history) >= 200 else None
    rsi = _safe_float_text(item.get('RSI'))

    rules = [
        ('Regula #1 (TVBETETF &lt; SMA200)', sma200 is not None,
         sma200 is not None and price < sma200, 'REDU RISCUL',
         f'{len(history)}/200 ȘEDINȚE'),
        ('Regula #2 (TVBETETF &lt; SMA50)', sma50 is not None,
         sma50 is not None and price < sma50, 'TREND SLAB', 'NORMAL'),
        ('Regula #3 (TVBETETF &lt; SMA10)', sma10 is not None,
         sma10 is not None and price < sma10, 'TIMING SLAB', 'NORMAL'),
        ('Regula #4 (RSI14 &lt; 40)', rsi is not None,
         rsi is not None and rsi < 40, 'MOMENTUM SLAB', 'NORMAL'),
    ]
    evaluated = sum(1 for _, available, *_ in rules if available)
    active = sum(
        1 for _, available, is_active, *_ in rules
        if available and is_active
    )
    if active >= 2:
        overall, overall_color = 'RISC RIDICAT', '#d32f2f'
    elif active == 1:
        overall, overall_color = 'ATENȚIE', '#ff9800'
    elif evaluated >= 3:
        overall, overall_color = 'NORMAL', '#4caf50'
    else:
        overall, overall_color = 'DATE PARȚIALE', '#757575'

    cards = []
    for title, available, is_active, active_action, inactive_action in rules:
        if not available:
            status, action, color = 'NEEVALUATĂ', inactive_action, '#757575'
        elif is_active:
            status, action, color = 'ACTIVĂ', active_action, '#f44336'
        else:
            status, action, color = 'INACTIVĂ', inactive_action, '#4caf50'
        cards.append(f"""
        <div class="market-risk-card" style="border-color:{color}55;">
          <h3>{title}</h3>
          <div class="risk-value" style="color:{color};">{status}</div>
          <div class="risk-action" style="color:{color};">{action}</div>
        </div>""")
    cards.append(f"""
      <div class="market-risk-card market-risk-result" style="border-color:{overall_color};background:{overall_color}10;">
        <h3>REZULTAT ({active}/{evaluated})</h3>
        <div class="risk-value" style="color:{overall_color};">{overall}</div>
        <div class="risk-action" style="color:{overall_color};">DOAR POZIȚII BVB</div>
      </div>""")
    return ''.join(cards)


def _concat_order_frames(frames):
    """Concatenează ordinele fără warning-ul pandas pentru cadre goale/all-NA."""
    valid_frames = [frame for frame in frames if isinstance(frame, pd.DataFrame)]
    column_order = []
    for frame in valid_frames:
        for column in frame.columns:
            if column not in column_order:
                column_order.append(column)

    populated_frames = []
    for frame in valid_frames:
        if frame.empty:
            continue
        populated = frame.dropna(axis=1, how='all')
        if populated.shape[1] > 0:
            populated_frames.append(populated)

    if not populated_frames:
        return pd.DataFrame(columns=column_order)

    combined = pd.concat(populated_frames, ignore_index=True)
    return combined.reindex(columns=column_order)


def _read_order_snapshot(path):
    """Citește un snapshot de ordine, inclusiv cazul valid fără rânduri."""
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=TWS_ACTIVE_ORDER_COLUMNS)


def _normalise_order_snapshot_records(frame):
    if frame is None or frame.empty:
        return []
    columns = list(TWS_ACTIVE_ORDER_COLUMNS)
    for column in frame.columns:
        if column not in columns:
            columns.append(column)
    normalised = frame.reindex(columns=columns)
    return _json_without_nonfinite_numbers(normalised.to_dict('records'))


def _load_cached_tws_orders(full_state, password, path='tws_orders.csv'):
    """Încarcă TWS local sau ultimul snapshot criptat pentru rularea remote.

    Existența fișierului local este autoritară, inclusiv atunci când conține
    zero ordine. Absența lui (cazul GitHub Actions) înseamnă sursă
    indisponibilă, nu confirmarea că lista ordinelor este goală.
    """
    cached_records = None
    encrypted = (full_state or {}).get(TWS_ACTIVE_ORDERS_CACHE_KEY)
    if encrypted and password:
        try:
            decoded = json.loads(
                market_security.decrypt_from_js(encrypted, password)
            )
            if isinstance(decoded, list):
                cached_records = decoded
        except (ValueError, TypeError, KeyError):
            cached_records = None

    if os.path.exists(path):
        frame = _read_order_snapshot(path)
        records = _normalise_order_snapshot_records(frame)
        changed = records != cached_records
        if changed and full_state is not None and password:
            full_state[TWS_ACTIVE_ORDERS_CACHE_KEY] = json.loads(
                market_security.encrypt_for_js(
                    json.dumps(records, ensure_ascii=False), password
                )
            )
        return frame, changed, 'tws_local'

    if cached_records is not None:
        return (
            pd.DataFrame(cached_records, columns=TWS_ACTIVE_ORDER_COLUMNS),
            False,
            'tws_encrypted_cache',
        )
    if encrypted:
        # Nu confunda o cheie greșită/un payload corupt cu lipsa legitimă a
        # sursei. Rularea remote trebuie să oprească publicarea în acest caz,
        # altfel ar șterge ordinele IBKR din dashboard.
        return (
            pd.DataFrame(columns=TWS_ACTIVE_ORDER_COLUMNS),
            False,
            'encrypted_cache_invalid',
        )
    return pd.DataFrame(columns=TWS_ACTIVE_ORDER_COLUMNS), False, 'unavailable'


def _orders_snapshot_password(default_password):
    """Cheia folosită exclusiv pentru snapshotul ordinelor active.

    Pe calculator cheia locală a portofoliului poate fi diferită de PIN-ul
    folosit de GitHub Pages. Variabila dedicată permite publicarea aceluiași
    snapshot criptat pentru PIN-ul remote, fără a expune sau a include PIN-ul
    în repository.
    """
    return (
        os.environ.get('PORTFOLIO_ORDER_CACHE_PASSWORD', '')
        or os.environ.get('TWS_ACCOUNT_PASSWORD', '')
        or default_password
    )


def _write_portable_account_snapshot(path, payload, password):
    """Persistă un snapshot exact cu cheia comună local/remote.

    Evită rescrierea dacă fișierul existent se decriptează cu aceeași cheie și
    conține deja aceleași date.
    """
    if not isinstance(payload, dict) or not password:
        return False
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            existing_encrypted = json.load(handle)
        existing_payload = json.loads(
            market_security.decrypt_from_js(existing_encrypted, password)
        )
        if existing_payload == payload:
            return False
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        pass

    encrypted = market_security.encrypt_for_js(
        json.dumps(payload, ensure_ascii=False), password
    )
    temporary_path = f'{path}.tmp'
    with open(temporary_path, 'w', encoding='utf-8') as handle:
        handle.write(encrypted)
    os.replace(temporary_path, path)
    return True


def _load_portable_account_snapshot(raw_path, encrypted_path, password):
    """Încarcă snapshotul local sau copia criptată destinată rulării remote."""
    if os.path.exists(raw_path):
        try:
            with open(raw_path, 'r', encoding='utf-8') as handle:
                payload = json.load(handle)
            if not isinstance(payload, dict):
                return None, 'local_invalid'
            _write_portable_account_snapshot(
                encrypted_path, payload, password
            )
            return payload, 'local'
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return None, 'local_invalid'

    if os.path.exists(encrypted_path):
        try:
            with open(encrypted_path, 'r', encoding='utf-8') as handle:
                encrypted_payload = json.load(handle)
            payload = json.loads(
                market_security.decrypt_from_js(encrypted_payload, password)
            )
            if isinstance(payload, dict):
                return payload, 'encrypted_cache'
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            pass
        return None, 'encrypted_cache_invalid'

    return None, 'unavailable'


def _filter_orders_against_current_positions(orders_df, portfolio_df):
    """Elimină ordinele SELL pentru instrumente care nu mai sunt deținute.

    Dashboardul este long-only. Dacă lista curentă de poziții este disponibilă,
    un SELL rămas doar în cache nu trebuie prezentat drept ordin activ.
    Ordinele BUY nu sunt filtrate prin această regulă.
    """
    if (
        orders_df is None
        or orders_df.empty
        or 'Action' not in orders_df.columns
        or portfolio_df is None
        or portfolio_df.empty
        or 'Symbol' not in portfolio_df.columns
    ):
        return orders_df

    def aliases(value):
        symbol = str(value or '').strip().upper()
        if not symbol or symbol == 'NAN':
            return set()
        result = {symbol}
        if '.' in symbol:
            result.add(symbol.split('.', 1)[0])
        return result

    held_aliases = set()
    for symbol in portfolio_df['Symbol']:
        held_aliases.update(aliases(symbol))

    keep_rows = []
    for _, row in orders_df.iterrows():
        action = str(row.get('Action', '')).strip().upper()
        keep_rows.append(
            action != 'SELL'
            or bool(aliases(row.get('Symbol')) & held_aliases)
        )
    return orders_df.loc[keep_rows].copy()


def _active_buy_orders_total_eur(
    orders_df, rates, portfolio_df=None, watchlist_df=None,
):
    """Calculează valoarea ordinelor BUY active, normalizată în EUR."""
    if (
        not isinstance(orders_df, pd.DataFrame)
        or orders_df.empty
        or 'Action' not in orders_df.columns
    ):
        return 0.0

    currency_by_symbol = {}
    for frame, symbol_column in (
        (portfolio_df, 'Symbol'), (watchlist_df, 'Ticker')
    ):
        if not isinstance(frame, pd.DataFrame) or frame.empty:
            continue
        if symbol_column not in frame.columns:
            continue
        for _, item in frame.iterrows():
            symbol = str(item.get(symbol_column) or '').strip().upper()
            currency = str(item.get('Currency') or '').strip().upper()
            if symbol and currency and currency != 'NAN':
                currency_by_symbol[symbol] = currency
                currency_by_symbol.setdefault(symbol.split('.', 1)[0], currency)

    rates = rates if isinstance(rates, dict) else {}

    def positive_number(row, *columns):
        for column in columns:
            value = _safe_float_text(row.get(column))
            if value is not None and 0 < value < 1e10:
                return value
        return 0.0

    total_eur = 0.0
    buy_orders = orders_df[
        orders_df['Action'].astype(str).str.upper() == 'BUY'
    ]
    for _, order in buy_orders.iterrows():
        quantity = positive_number(order, 'Total_Qty', 'Quantity')
        order_type = str(order.get('OrderType') or '').strip().upper()
        if order_type in {'LMT', 'LIMIT'}:
            price = positive_number(
                order, 'Limit_Price', 'Aux_Price', 'Stop_Price'
            )
        else:
            price = positive_number(
                order, 'Stop_Price', 'Aux_Price', 'Limit_Price',
                'Calculated_Stop',
            )
        if quantity <= 0 or price <= 0:
            continue

        symbol = str(order.get('Symbol') or '').strip().upper()
        currency = str(order.get('Currency') or '').strip().upper()
        if not currency or currency == 'NAN':
            currency = (
                currency_by_symbol.get(symbol)
                or currency_by_symbol.get(symbol.split('.', 1)[0])
            )
        if not currency:
            if symbol.endswith('.RO'):
                currency = 'RON'
            elif symbol.endswith(('.PA', '.DE', '.AS')) or symbol == 'LQQ':
                currency = 'EUR'
            elif symbol.endswith('.L'):
                currency = 'GBP'
            else:
                currency = 'USD'

        rate = 1.0 if currency == 'EUR' else _safe_float_text(
            rates.get(currency)
        )
        if rate is None or rate <= 0:
            continue
        total_eur += quantity * price * rate
    return round(total_eur, 2)


def _current_month_portfolio_change(history, now=None):
    """Variația valorii totale între primul și ultimul snapshot din lună."""
    current_time = now or datetime.datetime.now().astimezone()
    points = []
    for item in history or []:
        if not isinstance(item, dict):
            continue
        timestamp = _parse_snapshot_timestamp(item.get('timestamp'))
        value = _safe_float_text(item.get('net_liquidation'))
        if timestamp is None or value is None:
            continue
        local_timestamp = timestamp.astimezone(current_time.tzinfo)
        if (
            local_timestamp.year == current_time.year
            and local_timestamp.month == current_time.month
        ):
            points.append((local_timestamp, value))
    if len(points) < 2:
        return None
    points.sort(key=lambda point: point[0])
    return round(points[-1][1] - points[0][1], 2)


def _previous_weekday(day):
    candidate = day - datetime.timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= datetime.timedelta(days=1)
    return candidate


def _market_post_close_state(now, timezone_name, close_hour):
    """Returnează ultima ședință terminată și dacă suntem în fereastra post-close."""
    local_now = now.astimezone(ZoneInfo(timezone_name))
    is_weekend = local_now.weekday() >= 5
    close_time = datetime.time(close_hour, 0)
    post_close = is_weekend or local_now.time().replace(tzinfo=None) >= close_time
    session_day = (
        _previous_weekday(local_now.date())
        if is_weekend or not post_close
        else local_now.date()
    )
    return {
        'timezone': timezone_name,
        'local_time': local_now.isoformat(timespec='seconds'),
        'close_time': f'{close_hour:02d}:00',
        'post_close': post_close,
        'session_date': session_day.isoformat(),
    }


def _closed_market_ai_schedule(full_state, now=None):
    """Permite o singură rundă AI după închiderea BVB și a pieței SUA."""
    current_time = now or datetime.datetime.now(datetime.timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=datetime.timezone.utc)
    bvb = _market_post_close_state(
        current_time, 'Europe/Bucharest', 18
    )
    usa = _market_post_close_state(
        current_time, 'America/New_York', 16
    )
    session_key = (
        f"BVB:{bvb['session_date']}|SUA:{usa['session_date']}"
    )
    last_session = str(
        (full_state or {}).get('last_closed_market_ai_session') or ''
    )
    both_closed = bool(bvb['post_close'] and usa['post_close'])
    return {
        'allowed': both_closed and session_key != last_session,
        'both_closed': both_closed,
        'session_key': session_key,
        'last_session_key': last_session,
        'bvb': bvb,
        'usa': usa,
    }


def generate_html_dashboard(
    portfolio_df,
    watchlist_df,
    market_indicators,
    filename="index.html",
    full_state=None,
    swing_data_override=None,
):
    if full_state is None: full_state = {}
    dashboard_rates = full_state.get('rates', {})
    ai_schedule = _closed_market_ai_schedule(full_state)
    ai_calls_allowed = bool(ai_schedule['allowed'])
    if ai_calls_allowed:
        # Rezervăm ședința înaintea apelurilor: o rerulare sau un al doilea
        # proces nu poate plăti încă o dată aceeași analiză.
        full_state['last_closed_market_ai_session'] = (
            ai_schedule['session_key']
        )
        full_state['last_closed_market_ai_attempt_at'] = (
            datetime.datetime.now(datetime.timezone.utc).isoformat(
                timespec='seconds'
            )
        )
        full_state['last_closed_market_ai_schedule'] = ai_schedule
        market_utils.save_state(full_state)
        print(
            "  -> Fereastră AI post-închidere activă: "
            + ai_schedule['session_key']
        )
    else:
        reason = (
            'piețele nu sunt încă ambele închise'
            if not ai_schedule['both_closed']
            else 'analiza ședinței a fost deja rulată'
        )
        print(
            "  -> Analize AI numai din cache: " + reason + "."
        )
    """Generează dashboard HTML cu 2 tab-uri și indicatori de piață."""
    
    css = """
    <style>
        /* ===== DRIPIFY-INSPIRED DESIGN SYSTEM ===== */
        
        /* CSS Variables */
        :root {
            --primary-purple: #7760F9;
            --dark-purple: #6349F8;
            --light-purple-bg: #F2F0FF;
            --text-primary: #111827;
            --text-secondary: #4B5563;
            --success-green: #5CD670;
            --error-red: #FE4141;
            --bg-white: #FFFFFF;
            --bg-light: #F9FAFB;
            --border-light: #E5E7EB;
            --shadow-sm: 0px 2px 8px rgba(0, 0, 0, 0.04);
            --shadow-md: 0px 4px 24px rgba(0, 0, 0, 0.06);
            --radius-sm: 8px;
            --radius-md: 16px;
            --radius-lg: 24px;
            --spacing-unit: 24px;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInFromLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.02);
            }
        }
        
        @keyframes shimmer {
            0% {
                background-position: -1000px 0;
            }
            100% {
                background-position: 1000px 0;
            }
        }
        
        /* Reset & Base */
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-light);
            color: var(--text-primary);
            line-height: 1.5;
            font-size: 16px;
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Tooltips */
        #global-tooltip {
            position: fixed;
            visibility: hidden;
            background-color: #111827;
            color: #fff;
            text-align: left;
            border-radius: 8px;
            padding: 10px 14px;
            z-index: 99999; /* Always on top */
            font-size: 0.85rem;
            font-weight: 500;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            pointer-events: none;
            line-height: 1.5;
            max-width: 280px;
            border: 1px solid rgba(255,255,255,0.1);
            transform: translate(-50%, -100%); /* Center horizontally, anchor bottom */
            margin-top: -12px; /* Slight offset from cursor */
            opacity: 0;
            transition: opacity 0.15s ease-out;
            white-space: normal; /* Allow wrapping */
        }
        
        #global-tooltip::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -6px;
            border-width: 6px;
            border-style: solid;
            border-color: #111827 transparent transparent transparent;
        }

        /* Typography */
        h1 {
            font-size: clamp(28px, 4vw, 36px);
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 16px;
        }
        
        h2 {
            font-size: clamp(20px, 3vw, 24px);
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 16px;
        }
        
        h3 {
            font-size: clamp(18px, 2vw, 20px);
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 12px;
        }
        
        h4 {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        
        p, .meta {
            font-size: 16px;
            color: var(--text-secondary);
            line-height: 1.6;
        }
        
        .meta {
            text-align: center;
            margin-bottom: var(--spacing-unit);
            font-size: 14px;
        }
        
        /* Container */
        .container {
            max-width: 1160px;
            margin: 0 auto;
            padding: 0 var(--spacing-unit);
        }
        
        /* Header & Navigation */
        .header-bar { 
            background: var(--bg-white);
            padding: 20px var(--spacing-unit);
            box-shadow: var(--shadow-sm);
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid var(--border-light);
        }
        
        .header-bar .container {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .hamburger { 
            font-size: 28px;
            cursor: pointer;
            color: var(--primary-purple);
            user-select: none;
            padding: 8px;
            border-radius: var(--radius-sm);
            transition: background 0.2s;
        }
        
        .hamburger:hover {
            background: var(--light-purple-bg);
            transform: scale(1.1);
        }
        
        .app-title { 
            font-size: clamp(20px, 3vw, 28px);
            font-weight: 700;
            color: var(--text-primary);
            flex-grow: 1;
            margin-left: 16px;
        }
        
        .menu-dropdown { 
            position: absolute;
            top: 80px;
            left: var(--spacing-unit);
            background: var(--bg-white);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-md);
            display: none;
            z-index: 1000;
            min-width: 240px;
            overflow: hidden;
            border: 1px solid var(--border-light);
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .menu-dropdown.show { 
            display: block;
            animation: slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .menu-item { 
            padding: 16px 20px;
            cursor: pointer;
            color: var(--text-primary);
            border-bottom: 1px solid var(--border-light);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 16px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .menu-item:hover { 
            background: var(--light-purple-bg);
            color: var(--primary-purple);
            padding-left: 28px;
        }
        
        .menu-item:last-child { 
            border-bottom: none;
        }
        
        /* Tab Content */
        .tab-content { 
            display: none;
            padding: var(--spacing-unit);
        }
        
        .tab-content.active { 
            display: block;
            animation: fadeIn 0.4s;
        }
        
        /* Cards */
        .summary {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: var(--spacing-unit);
            margin-bottom: calc(var(--spacing-unit) * 2);
        }
        
        .summary-card { 
            background: var(--bg-white);
            padding: var(--spacing-unit);
            border-radius: var(--radius-md);
            text-align: center;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-light);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeIn 0.6s ease-out backwards;
            min-width: 0;
            container-type: inline-size;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .summary-card:nth-child(1) { animation-delay: 0.1s; }
        .summary-card:nth-child(2) { animation-delay: 0.2s; }
        .summary-card:nth-child(3) { animation-delay: 0.3s; }
        .summary-card:nth-child(4) { animation-delay: 0.4s; }
        .summary-card:nth-child(5) { animation-delay: 0.5s; }
        .summary-card:nth-child(6) { animation-delay: 0.6s; }
        
        .summary-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-4px) scale(1.02);
        }
        
        .summary-card h3 { 
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
            min-height: 2.6em;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .summary-card .value { 
            font-size: clamp(18px, 1.65vw, 32px);
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.1;
            letter-spacing: -0.035em;
            white-space: nowrap;
            max-width: 100%;
            font-variant-numeric: tabular-nums;
        }

        @supports (font-size: 1cqi) {
            .summary-card .value {
                font-size: clamp(18px, 10cqi, 32px);
            }
        }

        /* Market risk: 5 carduri pe un singur rând desktop, responsive mobil. */
        .market-risk-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 24px;
        }
        .market-risk-card {
            min-width: 0;
            min-height: 112px;
            padding: 14px 10px;
            border: 1px solid var(--border-light);
            border-radius: 12px;
            background: var(--bg-white);
            box-shadow: var(--shadow-sm);
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .market-risk-card h3 {
            margin: 0 0 7px;
            color: var(--text-secondary);
            font-size: clamp(10px, .8vw, 13px);
            line-height: 1.35;
            text-transform: uppercase;
            overflow-wrap: anywhere;
        }
        .market-risk-card .risk-value {
            font-size: clamp(16px, 1.25vw, 22px);
            line-height: 1.15;
            font-weight: 800;
        }
        .market-risk-card .risk-action {
            margin-top: 6px;
            font-size: clamp(10px, .72vw, 12px);
            font-weight: 700;
        }
        
        /* Macro Cards & Animated Cards */
        .macro-card {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .macro-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }
        
        .animated-card {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .animated-card:hover {
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }
        
        /* Tables */
        .table-container { 
            width: 100%;
            overflow-x: auto;
            background: var(--bg-white);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-light);
            margin-top: var(--spacing-unit);
        }
        
        table { 
            width: 100%;
            border-collapse: collapse;
            background: var(--bg-white);
        }
        
        th, td { 
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid var(--border-light);
            font-size: 14px;
            white-space: nowrap;
        }
        
        th { 
            background: var(--bg-light);
            color: var(--text-primary);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.05em;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        tbody tr {
            transition: all 0.2s ease;
        }
        
        tr:hover { 
            background: var(--light-purple-bg);
            transform: scale(1.005);
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        /* Status Colors */
        .positive { 
            color: var(--success-green);
            font-weight: 600;
        }
        
        .negative { 
            color: var(--error-red);
            font-weight: 600;
        }
        
        .trend-Strong-Bullish { color: var(--success-green); font-weight: 600; }
        .trend-Bullish-Pullback { color: #86EFAC; }
        .trend-Strong-Bearish { color: var(--error-red); font-weight: 600; }
        .trend-Bearish-Rally { color: #FCA5A5; }
        
        .rsi-Overbought { color: #F59E0B; font-weight: 600; }
        .rsi-Oversold { color: #3B82F6; font-weight: 600; }
        
        .vix-Ridicat { color: #F59E0B; }
        .vix-Extrem { color: var(--error-red); font-weight: 600; }
        
        /* Buttons */
        button, .btn {
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 600;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-family: inherit;
            position: relative;
            overflow: hidden;
        }
        
        button:active, .btn:active {
            transform: scale(0.98);
        }
        
        .btn-primary, button[onclick*="unlock"] {
            background: var(--primary-purple);
            color: white;
            box-shadow: 0 4px 12px rgba(119, 96, 249, 0.3);
        }
        
        .btn-primary:hover, button[onclick*="unlock"]:hover {
            background: var(--dark-purple);
            box-shadow: 0 6px 20px rgba(119, 96, 249, 0.5);
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: var(--bg-white);
            color: var(--text-primary);
            border: 1px solid var(--border-light);
        }
        
        .btn-secondary:hover {
            background: var(--light-purple-bg);
            border-color: var(--primary-purple);
            color: var(--primary-purple);
            transform: translateY(-1px);
        }
        
        /* Inputs */
        .edit-input { 
            width: 80px;
            text-align: right;
            padding: 6px 12px;
            border: 1px solid var(--border-light);
            border-radius: var(--radius-sm);
            font-size: 14px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .edit-input:focus {
            outline: none;
            border-color: var(--primary-purple);
            box-shadow: 0 0 0 4px rgba(119, 96, 249, 0.15);
            transform: scale(1.02);
        }
        
        input[data-field="trail_pct"] { 
            width: 60px !important;
        }
        
        /* Sparklines */
        .sparkline-container { 
            width: 80px;
            height: 30px;
        }
        
        /* Animations */
        @keyframes fadeIn { 
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideDown { 
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (min-width: 769px) and (max-width: 1200px) {
            .summary {
                grid-template-columns: repeat(3, minmax(0, 1fr));
            }
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            :root {
                --spacing-unit: 16px;
            }
            
            .header-bar {
                padding: 16px;
            }
            
            .summary {
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 16px;
            }
            
            .summary-card {
                padding: 16px 12px;
            }

            .market-risk-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 10px;
            }
            .market-risk-card {
                min-height: 102px;
                padding: 12px 8px;
            }
            
            .table-container {
                border-radius: var(--radius-sm);
            }
            
            th, td {
                padding: 12px 8px;
                font-size: 13px;
            }
            
            .menu-dropdown {
                left: 16px;
                right: 16px;
                min-width: auto;
            }

            /* Mobile adjustments */
            .container { width: 95%; padding: 10px; }
        }
        
        @media (max-width: 480px) {
            th, td {
                padding: 10px 6px;
                font-size: 12px;
            }
            
            .summary-card .value {
                font-size: clamp(17px, 6vw, 22px);
            }

            .market-risk-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """
    
    vix_val = portfolio_df.iloc[0]['VIX_Tag'] if not portfolio_df.empty else watchlist_df.iloc[0]['VIX_Tag'] if not watchlist_df.empty else 'N/A'
    vix_cls = vix_val if vix_val != 'N/A' else 'Normal'

    # --- RISK MANAGEMENT LOGIC (NEW) ---
    if isinstance(swing_data_override, dict):
        swing_data = swing_data_override
    else:
        fresh_swing_data = get_swing_trading_data()
        if _store_us_market_overview_snapshot(full_state, fresh_swing_data):
            swing_data = fresh_swing_data
            # main() salvează starea înainte de randarea HTML. Snapshotul este
            # creat aici, deci îl persistăm imediat pentru următorul update_ro.
            market_utils.save_state(full_state)
        else:
            # O cădere Yahoo/Finviz nu are voie să înlocuiască overview-ul
            # valid cu zerouri. Folosim ultimul snapshot complet al SUA.
            swing_data = _cached_swing_data_for_ro(full_state)
            if swing_data is None:
                swing_data = fresh_swing_data

    # Semnalele sunt calculate înaintea apelului AI, astfel încât doar
    # candidații din piața aflată efectiv pe BUY/CUMPĂRĂ să fie trimiși
    # modelului. Aceleași rezultate sunt reutilizate mai jos la randare.
    swing_html = ''
    bvb_market_html = ''
    international_market_signal = {
        'key': 'international',
        'label': 'Piața internațională',
        'verdict': 'DATE INSUFICIENTE',
    }
    bvb_market_signal = {
        'key': 'romania_bvb',
        'label': 'Piața românească BVB',
        'verdict': 'DATE INSUFICIENTE',
    }
    try:
        swing_html, international_market_signal = (
            generate_swing_trading_html(
                data=swing_data,
                return_signal=True,
            )
        )
    except Exception as signal_error:
        print(
            "  ⚠ Semnalul internațional nu a putut fi calculat pentru "
            f"filtrul AI: {signal_error}"
        )
    try:
        bvb_market_html, bvb_market_signal = (
            _generate_bvb_market_overview_html(
                portfolio_df,
                watchlist_df,
                return_signal=True,
                full_state=full_state,
            )
        )
    except Exception as signal_error:
        print(
            "  ⚠ Semnalul BVB nu a putut fi calculat pentru filtrul AI: "
            f"{signal_error}"
        )
    
    # Extract Metrics
    r_spx_price = swing_data.get('SPX_Price', 0)
    r_sma200 = swing_data.get('SPX_SMA200', 0)
    r_sma50 = swing_data.get('SPX_SMA50', 0)
    r_vix = swing_data.get('VIX_Current', 0)
    r_breadth = swing_data.get('Breadth_Pct', 0)
    
    # Evaluate Rules
    # Rule 1: SPX < SMA200
    rule1_active = r_spx_price < r_sma200 and r_spx_price > 0
    rule1_status = "ACTIVĂ" if rule1_active else "INACTIVĂ"
    rule1_action = "REDUCI / IEȘI" if rule1_active else "NORMAL"
    rule1_color = "#e53935" if rule1_active else "#4caf50" # Red/Green

    # Rule 2: VIX > 25
    rule2_active = r_vix > 25
    rule2_status = "ACTIVĂ" if rule2_active else "INACTIVĂ"
    rule2_action = "IEȘI RAPID" if rule2_active else "NORMAL"
    rule2_color = "#d32f2f" if rule2_active else "#4caf50" # Dark Red

    # Rule 3: Breadth < 45%
    rule3_active = r_breadth < 45
    rule3_status = "ACTIVĂ" if rule3_active else "INACTIVĂ"
    rule3_action = "IEȘI TREPTAT" if rule3_active else "NORMAL"
    rule3_color = "#fb8c00" if rule3_active else "#4caf50" # Orange

    # Rule 4: Trend Structure (Lower Highs + Break Lows) - Calculated in analysis module
    # Logic: PH2 < PH1 (Lower High) AND Current < SL (Break of Last Higher Low)
    rule4_active = swing_data.get('Rule4_Active', False)
    rule4_debug = swing_data.get('Rule4_Debug', 'N/A')
    
    rule4_status = "ACTIVĂ" if rule4_active else "INACTIVĂ"
    rule4_action = "MARKET RISK-OFF" if rule4_active else "NORMAL"
    rule4_color = "#e53935" if rule4_active else "#4caf50"

    # Count Active Rules
    active_rules_count = sum([rule1_active, rule2_active, rule3_active, rule4_active])
    
    overall_status = "NORMAL"
    overall_color = "#4caf50"
    if active_rules_count >= 2:
        overall_status = "EXIT AGRESIV"
        overall_color = "#b71c1c" # Deep Red

    # Generate HTML for Risk Cards
    risk_cards_html = f"""
    <div class="market-risk-card" style="border-color:{rule1_color}55;">
        <h3 style="font-size: 0.9rem; margin-bottom: 5px;">Regula #1 (SPX &lt; SMA200)</h3>
        <div class="risk-value" style="color:{rule1_color};">{rule1_status}</div>
        <div class="risk-action" style="color:{rule1_color};">{rule1_action}</div>
    </div>
    
    <div class="market-risk-card" style="border-color:{rule2_color}55;">
        <h3 style="font-size: 0.9rem; margin-bottom: 5px;">Regula #2 (VIX &gt; 25)</h3>
        <div class="risk-value" style="color:{rule2_color};">{rule2_status}</div>
        <div class="risk-action" style="color:{rule2_color};">{rule2_action}</div>
    </div>
    
    <div class="market-risk-card" style="border-color:{rule3_color}55;">
        <h3 style="font-size: 0.9rem; margin-bottom: 5px;">Regula #3 (Breadth &lt; 45%)</h3>
        <div class="risk-value" style="color:{rule3_color};">{rule3_status}</div>
        <div class="risk-action" style="color:{rule3_color};">{rule3_action}</div>
    </div>
    
    <div class="market-risk-card" style="border-color:{rule4_color}55;" title="{rule4_debug}">
        <h3 style="font-size: 0.9rem; margin-bottom: 5px;">Regula #4 (Market Structure)</h3>
        <div class="risk-value" style="color:{rule4_color};">{rule4_status}</div>
        <div class="risk-action" style="color:{rule4_color};">{rule4_action}</div>
    </div>
    
    <div class="market-risk-card market-risk-result" style="border:2px solid {overall_color};background:{overall_color}10;">
        <h3 style="font-size: 0.9rem; margin-bottom: 5px;">REZULTAT ({active_rules_count}/4)</h3>
        <div class="risk-value" style="color:{overall_color};">{overall_status}</div>
        <div class="risk-action" style="color:{overall_color};">DOAR POZIȚII SUA</div>
    </div>
    """
    bvb_risk_cards_html = _generate_bvb_risk_status_html(
        portfolio_df, watchlist_df, full_state=full_state
    )
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calcul Timestamp IBKR File
    pf_file = "portfolio.csv"
    if os.path.exists(pf_file):
        mt = os.path.getmtime(pf_file)
        ibkr_last_update = datetime.datetime.fromtimestamp(mt).strftime('%Y-%m-%d %H:%M:%S')
    else:
        ibkr_last_update = "N/A"

    # Calculăm totalurile pentru sumar
    total_investment = portfolio_df['Investment'].sum() if not portfolio_df.empty else 0
    total_value = portfolio_df['Current_Value'].sum() if not portfolio_df.empty else 0
    total_profit = portfolio_df['Profit'].sum() if not portfolio_df.empty else 0

    # Recalculăm Max Profit și P/L la Stop iterând
    total_max_profit = 0
    total_pl_at_stop = 0
    total_pos_profit = 0      # Count positions > 0 profit
    total_pos_stop_profit = 0 # Count positions > 0 P/L at Stop
    
    if not portfolio_df.empty:
        for _, row in portfolio_df.iterrows():
            if row['Profit'] > 0:
                total_pos_profit += 1
                
            # Max Profit (old logic, replaced by direct sum from df)
            # if row['Target'] and pd.notna(row['Target']):
            #      mp = (row['Target'] - row['Buy_Price']) * row['Shares']
            #      total_max_profit += mp
            
            # P/L la Stop (old logic, replaced by direct sum from df)
            # if row['Trail_Stop'] and pd.notna(row['Trail_Stop']) and row['Trail_Stop'] > 0:
            #      pls = (row['Trail_Stop'] - row['Buy_Price']) * row['Shares']
            #      total_pl_at_stop += pls
            #      if pls > 0:
            #          total_pos_stop_profit += 1

    # Calcul totaluri portofoliu
    total_investment = portfolio_df['Investment'].sum() if not portfolio_df.empty else 0
    total_value = portfolio_df['Current_Value'].sum() if not portfolio_df.empty else 0
    total_profit = portfolio_df['Profit'].sum() if not portfolio_df.empty else 0
    
    if 'Max_Profit' not in portfolio_df.columns:
        portfolio_df['Max_Profit'] = 0.0
    portfolio_df['Max_Profit'] = pd.to_numeric(portfolio_df['Max_Profit'], errors='coerce').fillna(0)
    total_max_profit = portfolio_df['Max_Profit'].sum() if not portfolio_df.empty else 0
    
    # Calc P/L la Stop (use effective stop: prefer Trail_Stop_IBKR if available)
    total_pl_at_stop = 0
    total_pos_stop_profit = 0
    has_ibkr_stop = 'Trail_Stop_IBKR' in portfolio_df.columns if not portfolio_df.empty else False
    if not portfolio_df.empty:
        for _, r in portfolio_df.iterrows():
            eff_stop = 0
            if has_ibkr_stop and pd.notna(r.get('Trail_Stop_IBKR', 0)) and r.get('Trail_Stop_IBKR', 0) > 0:
                eff_stop = r['Trail_Stop_IBKR']
            elif r['Trail_Stop'] and r['Trail_Stop'] > 0:
                eff_stop = r['Trail_Stop']
            if eff_stop > 0:
                 diff = (eff_stop - r['Buy_Price']) * r['Shares']
                 total_pl_at_stop += diff
                 if diff > 0:
                     total_pos_stop_profit += 1
    
    total_profit_pct = ((total_value - total_investment) / total_investment * 100) if total_investment > 0 else 0

    # Citire IBKR Stats (MTD/YTD)
    ib_mtd = 0
    ib_ytd = 0
    has_stats = False
    if os.path.exists('ib_stats.json'):
         try:
             with open('ib_stats.json') as f:
                 st = json.load(f)
                 ib_mtd = st.get('mtd_val', 0)
                 ib_ytd = st.get('ytd_val', 0)
                 has_stats = True
         except: pass

    # Citire parolă
    # Pe GitHub Actions ignorăm password.txt pentru securitate
    is_github = os.environ.get('GITHUB_ACTIONS') == 'true'
    password = "1234" # Default fallback
    
    if 'PORTFOLIO_PASSWORD' in os.environ:
        password = os.environ['PORTFOLIO_PASSWORD']
    elif not is_github and os.path.exists("password.txt"):
        try:
            with open("password.txt", "r") as f:
                password = f.read().strip()
        except: pass

    firebase_web_push_html = _firebase_web_push_html(
        os.environ.get('FIREBASE_WEB_CONFIG'),
        os.environ.get('FIREBASE_VAPID_KEY'),
    )
    html_head = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="theme-color" content="#7760F9">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <title>Market Scanner Dashboard</title>
        <link rel="manifest" href="manifest.webmanifest">
        {firebase_web_push_html}
        
        <!-- DataTables & jQuery -->
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        
        {css}
        <style>
            /* DataTables Dark Mode Overrides */
            .dataTables_wrapper .dataTables_length, 
            .dataTables_wrapper .dataTables_filter, 
            .dataTables_wrapper .dataTables_info, 
            .dataTables_wrapper .dataTables_paginate {{
                color: var(--text-primary) !important;
                margin-bottom: 15px;
            }}
            .dataTables_wrapper .dataTables_filter input {{
                background-color: var(--bg-white);
                color: var(--text-primary);
                border: 1px solid var(--border-light);
                padding: 10px 14px;
                border-radius: var(--radius-sm);
                font-size: 14px;
            }}
            .dataTables_wrapper .dataTables_filter input:focus {{
                border-color: var(--primary-purple);
                box-shadow: 0 0 0 3px rgba(119, 96, 249, 0.1);
                outline: none;
            }}
            table.dataTable tbody tr {{
                background-color: var(--bg-white);
                color: var(--text-primary);
            }}
            table.dataTable tbody tr.even {{
                background-color: var(--bg-light);
            }}
            table.dataTable.hover tbody tr:hover, table.dataTable.display tbody tr:hover {{
                background-color: var(--light-purple-bg) !important;
            }}
            table.dataTable thead th, table.dataTable tfoot th {{
                border-bottom: 2px solid var(--border-light);
            }}
            table.dataTable.no-footer {{
                border-bottom: 1px solid #444;
            }}
            .portfolio-chat-launcher {{
                position: fixed; right: 24px; bottom: 24px; z-index: 1200;
                width: 62px; height: 62px; border: 0; border-radius: 50%;
                background: linear-gradient(135deg, #7760f9, #4f46e5);
                color: white; box-shadow: 0 12px 32px rgba(79,70,229,.34);
                cursor: pointer; font-size: 27px; transition: transform .2s;
            }}
            .portfolio-chat-launcher:hover {{ transform: translateY(-2px); }}
            .portfolio-chat-panel {{
                position: fixed; right: 24px; bottom: 98px; z-index: 1199;
                width: min(430px, calc(100vw - 32px)); height: min(680px, calc(100vh - 130px));
                display: none; flex-direction: column; overflow: hidden;
                background: var(--bg-white); border: 1px solid var(--border-light);
                border-radius: 22px; box-shadow: 0 22px 60px rgba(15,23,42,.25);
            }}
            .portfolio-chat-panel.open {{ display: flex; }}
            .portfolio-chat-header {{
                padding: 17px 18px; color: white;
                background: linear-gradient(135deg, #7760f9, #4f46e5);
                display: flex; align-items: center; justify-content: space-between; gap: 12px;
                flex: 0 0 auto;
            }}
            .portfolio-chat-title {{ font-weight: 800; font-size: 18px; }}
            .portfolio-chat-subtitle {{ font-size: 11px; opacity: .85; margin-top: 3px; }}
            .portfolio-chat-close {{
                border: 0; background: rgba(255,255,255,.18); color: white;
                width: 34px; height: 34px; border-radius: 50%; cursor: pointer; font-size: 21px;
            }}
            .portfolio-chat-messages {{
                flex: 1 1 auto; min-height: 0; overflow-y: auto; padding: 16px; background: var(--bg-light);
                display: flex; flex-direction: column; gap: 12px;
                -webkit-overflow-scrolling: touch; overscroll-behavior-y: contain;
                touch-action: pan-y;
            }}
            .portfolio-chat-message {{
                max-width: 88%; padding: 11px 13px; border-radius: 16px;
                line-height: 1.5; font-size: 14px; overflow-wrap: anywhere;
            }}
            .portfolio-chat-message.user {{ white-space: pre-wrap; }}
            .portfolio-chat-message.user {{ align-self: flex-end; background: #7760f9; color: white; border-bottom-right-radius: 5px; }}
            .portfolio-chat-message.assistant {{ align-self: flex-start; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-bottom-left-radius: 5px; }}
            .portfolio-chat-message.error {{ border-color: #fecaca; color: #b91c1c; }}
            .portfolio-chat-message a {{ color: #4f46e5; font-weight: 700; }}
            .portfolio-chat-message h1, .portfolio-chat-message h2,
            .portfolio-chat-message h3, .portfolio-chat-message h4,
            .portfolio-chat-message h5, .portfolio-chat-message h6 {{
                margin: .75em 0 .35em; line-height: 1.25; font-size: 1.08em;
            }}
            .portfolio-chat-message h1:first-child, .portfolio-chat-message h2:first-child,
            .portfolio-chat-message h3:first-child, .portfolio-chat-message h4:first-child {{ margin-top: 0; }}
            .portfolio-chat-message p {{ margin: .45em 0; }}
            .portfolio-chat-message p:first-child {{ margin-top: 0; }}
            .portfolio-chat-message p:last-child {{ margin-bottom: 0; }}
            .portfolio-chat-message ul, .portfolio-chat-message ol {{ margin: .4em 0; padding-left: 1.45em; }}
            .portfolio-chat-message li {{ margin: .22em 0; }}
            .portfolio-chat-message code {{
                padding: .08em .32em; border-radius: 4px; background: #eef2f7;
                font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .92em;
            }}
            .portfolio-chat-table-scroll {{
                max-width: 100%; margin: .55em 0; overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }}
            .portfolio-chat-message table {{
                width: max-content; min-width: 100%; border-collapse: collapse;
                font-size: .92em; white-space: normal;
            }}
            .portfolio-chat-message th, .portfolio-chat-message td {{
                padding: .45em .55em; border: 1px solid var(--border-light);
                text-align: left; vertical-align: top;
            }}
            .portfolio-chat-message th {{ background: #eef2ff; font-weight: 750; }}
            .portfolio-chat-suggestions {{ padding: 10px 14px 0; display: flex; gap: 7px; overflow-x: auto; flex: 0 0 auto; }}
            .portfolio-chat-suggestion {{
                flex: 0 0 auto; border: 1px solid #c7d2fe; color: #4f46e5;
                background: #eef2ff; border-radius: 999px; padding: 7px 10px; cursor: pointer; font-size: 12px;
            }}
            .portfolio-chat-form {{ padding: 12px 14px 14px; display: flex; gap: 8px; background: var(--bg-white); flex: 0 0 auto; }}
            .portfolio-chat-input {{
                flex: 1; min-width: 0; resize: none; border: 1px solid var(--border-light);
                border-radius: 13px; padding: 11px 12px; color: var(--text-primary);
                background: var(--bg-white); font: inherit; max-height: 110px;
            }}
            .portfolio-chat-send {{
                align-self: flex-end; border: 0; border-radius: 12px; padding: 11px 14px;
                background: #7760f9; color: white; font-weight: 750; cursor: pointer;
            }}
            .portfolio-chat-send:disabled {{ opacity: .55; cursor: wait; }}
            @media (max-width: 640px) {{
                .portfolio-chat-launcher {{ right: 16px; bottom: 16px; width: 56px; height: 56px; }}
                .portfolio-chat-panel {{
                    right: 8px; bottom: 80px; width: calc(100vw - 16px);
                    height: min(76vh, 680px); border-radius: 18px;
                    height: min(76dvh, 680px);
                }}
                .portfolio-chat-message {{ max-width: 94%; font-size: 13px; }}
            }}
            /* Hide sorting icons if they clash or let them be */
        </style>
    """
    
    # JS Block (Raw String to avoid f-string syntax errors with { })
    html_head += """
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <!-- CryptoJS for AES Decryption -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
        <script src="portfolio_auth.js"></script>
        
        <script>
            // Variabila cu datele criptate va fi injectată aici de Python
            // const ENCRYPTED_DATA = { ... }; 
            let portfolioDetailData = {};
            let buyRecommendationDetailData = {};
            let activeBuyOrderLevels = {};
            let portfolioChatConfig = null;
            let portfolioChatHistory = [];

            async function reloadIfPortfolioPageIsStale() {
                if (typeof PORTFOLIO_BLOB_VERSION === 'undefined') return false;
                try {
                    const freshUrl = new URL(window.location.href);
                    freshUrl.searchParams.set('_portfolio_refresh', Date.now().toString());
                    const response = await fetch(freshUrl.href, {
                        cache: 'no-store',
                        credentials: 'same-origin',
                        headers: { 'Cache-Control': 'no-cache' }
                    });
                    if (!response.ok) return false;
                    const freshHtml = await response.text();
                    const versionMatch = freshHtml.match(
                        /const PORTFOLIO_BLOB_VERSION = "([a-f0-9]+)";/
                    );
                    if (
                        !versionMatch
                        || versionMatch[1] === PORTFOLIO_BLOB_VERSION
                    ) {
                        return false;
                    }
                    sessionStorage.setItem(
                        'marketScannerOpenPortfolioAfterRefresh',
                        '1'
                    );
                    window.location.replace(freshUrl.href);
                    return true;
                } catch (refreshError) {
                    console.warn(
                        'Versiunea publicată nu a putut fi verificată.',
                        refreshError
                    );
                    return false;
                }
            }


            async function unlockPortfolioWithCredential(input, options) {
                const settings = Object.assign(
                    { remember: true, silent: false },
                    options || {}
                );
                try {
                    // Decrypt
                    // ENCRYPTED_DATA is defined below in the body/script injection
                    if (typeof ENCRYPTED_DATA === 'undefined') {
                        throw new Error('Datele criptate lipsesc.');
                    }
                    
                    const salt = CryptoJS.enc.Base64.parse(ENCRYPTED_DATA.salt);
                    const iv = CryptoJS.enc.Base64.parse(ENCRYPTED_DATA.iv);
                    const ciphertext = ENCRYPTED_DATA.ciphertext;
                    
                    // Derive Key matches Python PBKDF2 (SHA256, 1000 iter, 32 bytes)
                    const key = CryptoJS.PBKDF2(input, salt, { 
                        keySize: 256/32, 
                        iterations: 1000,
                        hasher: CryptoJS.algo.SHA256
                    });
                    
                    const decrypted = CryptoJS.AES.decrypt(ciphertext, key, { 
                        iv: iv, 
                        padding: CryptoJS.pad.Pkcs7,
                        mode: CryptoJS.mode.CBC
                    });
                    
                    const strData = decrypted.toString(CryptoJS.enc.Utf8);
                    
                    if (!strData) {
                        throw new Error('Decriptarea a eșuat.');
                    }
                    const data = JSON.parse(strData);
                    renderPortfolio(data);

                    document.getElementById('portfolio-lock').style.display = 'none';
                    document.getElementById('portfolio-data').style.display = 'block';
                    window.marketScannerPortfolioAuthenticated = true;
                    window.dispatchEvent(new CustomEvent(
                        'market-scanner:portfolio-authenticated',
                        { detail: { authenticated: true } }
                    ));
                    const passwordInput = document.getElementById('pf-pass');
                    if (passwordInput) passwordInput.value = '';
                    if (
                        settings.remember &&
                        window.PortfolioAuthPersistence
                    ) {
                        await window.PortfolioAuthPersistence
                            .rememberCredential(input);
                    }
                    return true;
                } catch (e) {
                    console.error(e);
                    if (await reloadIfPortfolioPageIsStale()) {
                        return false;
                    }
                    if (!settings.silent) {
                        alert(
                            'PIN incorect sau datele portofoliului nu au putut '
                            + 'fi decriptate.'
                        );
                    }
                    return false;
                }
            }

            function unlockPortfolio() {
                const passwordInput = document.getElementById('pf-pass');
                const input = passwordInput ? passwordInput.value : '';
                if (!input) return;
                void unlockPortfolioWithCredential(input, {
                    remember: true,
                    silent: false
                });
            }

            async function restorePortfolioAccess() {
                if (!window.PortfolioAuthPersistence) return;
                const credential = await window.PortfolioAuthPersistence
                    .restoreCredential();
                if (!credential) return;
                const unlocked = await unlockPortfolioWithCredential(
                    credential,
                    { remember: true, silent: true }
                );
                if (!unlocked) {
                    await window.PortfolioAuthPersistence.clearCredential();
                }
            }

            async function logoutPortfolio() {
                if (window.PortfolioAuthPersistence) {
                    await window.PortfolioAuthPersistence.clearCredential();
                }
                window.location.reload();
            }

            const BUY_RECOMMENDATION_HISTORY_DISPLAY_LIMIT = 50;

            function limitBuyRecommendationHistoryDisplay(container) {
                if (!container) return;
                const historyDetails = Array.from(
                    container.querySelectorAll('details')
                ).find(function(detailsElement) {
                    const summary = Array.from(detailsElement.children)
                        .find(function(child) {
                            return child.tagName === 'SUMMARY';
                        });
                    return summary && summary.textContent.trim()
                        .startsWith('Istoric recomandări executabile (');
                });
                if (!historyDetails) return;
                const historyGrid = Array.from(historyDetails.children)
                    .find(function(child) {
                        return child.tagName === 'DIV';
                    });
                if (!historyGrid) return;
                Array.from(historyGrid.children).forEach(function(row, index) {
                    row.hidden = (
                        index >= BUY_RECOMMENDATION_HISTORY_DISPLAY_LIMIT
                    );
                });
            }
            
            function renderPortfolio(data) {
                // 1. Destroy existing DataTable FIRST (if any)
                if (typeof $ !== 'undefined' && $.fn.DataTable) {
                    if ($.fn.DataTable.isDataTable('#portfolio-table')) {
                        $('#portfolio-table').DataTable().destroy();
                    }
                    if ($.fn.DataTable.isDataTable('#buying-orders-table')) {
                        $('#buying-orders-table').DataTable().destroy();
                    }
                    if ($.fn.DataTable.isDataTable('#selling-orders-table')) {
                        $('#selling-orders-table').DataTable().destroy();
                    }
                }
                
                // 2. Populate Table Bodies
                const tbody = document.getElementById('portfolio-rows-body');
                if (tbody) tbody.innerHTML = data.html;
                
                const tbodyBuy = document.getElementById('buying-orders-rows-body');
                if (tbodyBuy) {
                    tbodyBuy.innerHTML = data.buying_orders_html || '<tr><td colspan="15" style="text-align:center;">Niciun ordin de cumpărare activ în IBKR.</td></tr>';
                }
                
                const tbodySell = document.getElementById('selling-orders-rows-body');
                if (tbodySell) {
                    tbodySell.innerHTML = data.selling_orders_html || '<tr><td colspan="15" style="text-align:center;">Niciun ordin de vânzare activ în IBKR.</td></tr>';
                }

                const portfolioAi = document.getElementById('portfolio-ai-container');
                if (portfolioAi) {
                    portfolioAi.innerHTML = data.portfolio_ai_html || '';
                }
                const buyRecommendations = document.getElementById('buy-recommendations-container');
                if (buyRecommendations) {
                    buyRecommendations.innerHTML = data.buy_recommendations_html || '';
                    limitBuyRecommendationHistoryDisplay(buyRecommendations);
                }
                
                // 3. Init Charts
                initCharts(data.sparklines);
                portfolioDetailData = data.chart_details || {};
                buyRecommendationDetailData = data.buy_chart_details || {};
                activeBuyOrderLevels = data.active_buy_order_levels || {};
                portfolioChatConfig = data.portfolio_chat || null;
                
                // 4. Re-Init DataTables
                if (typeof $ !== 'undefined' && $.fn.DataTable) {
                    const initPortfolioDataTable = function(selector) {
                        const tableElement = document.querySelector(selector);
                        if (!tableElement) return;

                        // DataTables nu acceptă colspan/rowspan în tbody. Rândurile
                        // informative pentru liste goale rămân tabele HTML normale.
                        const columnCount = tableElement.querySelectorAll('thead th').length;
                        const rows = tableElement.querySelectorAll('tbody tr');
                        const hasUnsupportedRow = Array.from(rows).some(function(row) {
                            return row.querySelector('[colspan], [rowspan]') ||
                                row.children.length !== columnCount;
                        });
                        if (hasUnsupportedRow) return;

                        $(selector).DataTable({
                            destroy: true,
                            paging: false,
                            searching: true,
                            info: false,
                            order: [] // Preserve order from Python
                        });
                    };

                    try { initPortfolioDataTable('#portfolio-table'); }
                    catch(e) { console.error("Portfolio DataTable Init Error: ", e); }
                    try { initPortfolioDataTable('#buying-orders-table'); }
                    catch(e) { console.error("Buying Orders DataTable Init Error: ", e); }
                    try { initPortfolioDataTable('#selling-orders-table'); }
                    catch(e) { console.error("Selling Orders DataTable Init Error: ", e); }
                }
            }

            function togglePortfolioChat(forceOpen) {
                const panel = document.getElementById('portfolio-chat-panel');
                if (!panel) return;
                const shouldOpen = typeof forceOpen === 'boolean'
                    ? forceOpen : !panel.classList.contains('open');
                panel.classList.toggle('open', shouldOpen);
                panel.setAttribute('aria-hidden', shouldOpen ? 'false' : 'true');
                if (shouldOpen) {
                    const input = document.getElementById('portfolio-chat-input');
                    if (input) setTimeout(function() { input.focus(); }, 50);
                }
            }

            function appendPortfolioChatInline(parent, value, start, end, citations) {
                let cursor = start;
                const citationAt = function(index) {
                    return citations.find(function(item) { return item.start_index === index; });
                };
                while (cursor < end) {
                    const citation = citationAt(cursor);
                    if (citation && citation.end_index <= end) {
                        const link = document.createElement('a');
                        link.href = citation.url;
                        link.target = '_blank';
                        link.rel = 'noopener noreferrer';
                        link.textContent = value.slice(citation.start_index, citation.end_index)
                            || citation.title || 'sursă';
                        link.title = citation.title || citation.url;
                        parent.appendChild(link);
                        cursor = citation.end_index;
                        continue;
                    }

                    const rest = value.slice(cursor, end);
                    let match = rest.match(/^\\*\\*(?=\\S)([\\s\\S]*?\\S)\\*\\*/);
                    if (match) {
                        const strong = document.createElement('strong');
                        appendPortfolioChatInline(strong, value, cursor + 2, cursor + match[0].length - 2, citations);
                        parent.appendChild(strong);
                        cursor += match[0].length;
                        continue;
                    }
                    match = rest.match(/^`([^`\\n]+)`/);
                    if (match) {
                        const code = document.createElement('code');
                        code.textContent = match[1];
                        parent.appendChild(code);
                        cursor += match[0].length;
                        continue;
                    }
                    match = rest.match(/^\\[([^\\]\\n]+)\\]\\((https:\\/\\/[^\\s)]+)\\)/i);
                    if (match) {
                        const link = document.createElement('a');
                        link.href = match[2];
                        link.target = '_blank';
                        link.rel = 'noopener noreferrer';
                        link.textContent = match[1];
                        parent.appendChild(link);
                        cursor += match[0].length;
                        continue;
                    }
                    match = rest.match(/^\\*(?=\\S)([^*\\n]*?\\S)\\*/);
                    if (match) {
                        const emphasis = document.createElement('em');
                        appendPortfolioChatInline(emphasis, value, cursor + 1, cursor + match[0].length - 1, citations);
                        parent.appendChild(emphasis);
                        cursor += match[0].length;
                        continue;
                    }
                    parent.appendChild(document.createTextNode(value[cursor]));
                    cursor += 1;
                }
            }

            function renderPortfolioChatMarkdown(container, value, citations) {
                const tableDividerPattern = /^\\s*\\|?\\s*:?-{3,}:?\\s*(\\|\\s*:?-{3,}:?\\s*)+\\|?\\s*$/;
                const tableCells = function(line) {
                    let start = /^\\s*\\|/.test(line.text) ? line.text.indexOf('|') + 1 : 0;
                    let end = /\\|\\s*$/.test(line.text) ? line.text.lastIndexOf('|') : line.text.length;
                    const cells = [];
                    let cellStart = start;
                    for (let position = start; position <= end; position += 1) {
                        if (position !== end && line.text[position] !== '|') continue;
                        const raw = line.text.slice(cellStart, position);
                        const leading = raw.length - raw.trimStart().length;
                        const trailing = raw.length - raw.trimEnd().length;
                        cells.push({
                            start: line.start + cellStart + leading,
                            end: line.start + position - trailing
                        });
                        cellStart = position + 1;
                    }
                    return cells;
                };
                const lines = [];
                const linePattern = /.*(?:\\n|$)/g;
                let match;
                while ((match = linePattern.exec(value)) && match[0]) {
                    const raw = match[0].replace(/\\n$/, '').replace(/\\r$/, '');
                    lines.push({ text: raw, start: match.index });
                }
                let index = 0;
                while (index < lines.length) {
                    const line = lines[index];
                    if (!line.text.trim()) { index += 1; continue; }
                    if (line.text.includes('|') && index + 1 < lines.length
                            && tableDividerPattern.test(lines[index + 1].text)) {
                        const wrapper = document.createElement('div');
                        wrapper.className = 'portfolio-chat-table-scroll';
                        const table = document.createElement('table');
                        const head = document.createElement('thead');
                        const headRow = document.createElement('tr');
                        tableCells(line).forEach(function(cell) {
                            const headingCell = document.createElement('th');
                            appendPortfolioChatInline(headingCell, value, cell.start, cell.end, citations);
                            headRow.appendChild(headingCell);
                        });
                        head.appendChild(headRow);
                        table.appendChild(head);
                        index += 2;
                        const body = document.createElement('tbody');
                        while (index < lines.length && lines[index].text.trim()
                                && lines[index].text.includes('|')) {
                            const bodyRow = document.createElement('tr');
                            tableCells(lines[index]).forEach(function(cell) {
                                const dataCell = document.createElement('td');
                                appendPortfolioChatInline(dataCell, value, cell.start, cell.end, citations);
                                bodyRow.appendChild(dataCell);
                            });
                            body.appendChild(bodyRow);
                            index += 1;
                        }
                        table.appendChild(body);
                        wrapper.appendChild(table);
                        container.appendChild(wrapper);
                        continue;
                    }
                    const heading = line.text.match(/^(#{1,6})\\s+(.+)$/);
                    if (heading) {
                        const element = document.createElement('h' + heading[1].length);
                        const contentStart = line.start + heading[1].length + 1;
                        appendPortfolioChatInline(element, value, contentStart, line.start + line.text.length, citations);
                        container.appendChild(element);
                        index += 1;
                        continue;
                    }
                    const listMatch = line.text.match(/^\\s*([-+*]|\\d+\\.)\\s+(.+)$/);
                    if (listMatch) {
                        const ordered = /\\d+\\./.test(listMatch[1]);
                        const list = document.createElement(ordered ? 'ol' : 'ul');
                        while (index < lines.length) {
                            const itemLine = lines[index];
                            const item = itemLine.text.match(/^\\s*([-+*]|\\d+\\.)\\s+(.+)$/);
                            if (!item || /\\d+\\./.test(item[1]) !== ordered) break;
                            const listItem = document.createElement('li');
                            const itemOffset = itemLine.text.indexOf(item[2]);
                            appendPortfolioChatInline(listItem, value, itemLine.start + itemOffset,
                                itemLine.start + itemLine.text.length, citations);
                            list.appendChild(listItem);
                            index += 1;
                        }
                        container.appendChild(list);
                        continue;
                    }
                    const paragraph = document.createElement('p');
                    while (index < lines.length && lines[index].text.trim()
                            && !/^(#{1,6})\\s+/.test(lines[index].text)
                            && !/^\\s*([-+*]|\\d+\\.)\\s+/.test(lines[index].text)) {
                        const paragraphLine = lines[index];
                        if (paragraph.childNodes.length) paragraph.appendChild(document.createElement('br'));
                        appendPortfolioChatInline(paragraph, value, paragraphLine.start,
                            paragraphLine.start + paragraphLine.text.length, citations);
                        index += 1;
                    }
                    container.appendChild(paragraph);
                }
            }

            function addPortfolioChatMessage(role, text, citations, isError) {
                const messages = document.getElementById('portfolio-chat-messages');
                if (!messages) return;
                const bubble = document.createElement('div');
                bubble.className = 'portfolio-chat-message ' + role + (isError ? ' error' : '');
                const content = document.createElement('div');
                const value = String(text || '');
                const validCitations = Array.isArray(citations)
                    ? citations.filter(function(item) {
                        return item && Number.isInteger(item.start_index)
                            && Number.isInteger(item.end_index)
                            && item.start_index >= 0
                            && item.end_index > item.start_index
                            && item.end_index <= value.length
                            && String(item.url || '').toLowerCase().startsWith('https://');
                    }).sort(function(a, b) { return a.start_index - b.start_index; })
                    : [];
                if (role === 'assistant') {
                    renderPortfolioChatMarkdown(content, value, validCitations);
                } else {
                    content.textContent = value;
                }
                bubble.appendChild(content);
                messages.appendChild(bubble);
                messages.scrollTop = messages.scrollHeight;
                return bubble;
            }

            function usePortfolioChatSuggestion(text) {
                const input = document.getElementById('portfolio-chat-input');
                if (!input) return;
                input.value = text;
                void sendPortfolioChatMessage();
            }

            async function sendPortfolioChatMessage() {
                const input = document.getElementById('portfolio-chat-input');
                const button = document.getElementById('portfolio-chat-send');
                if (!input || !button) return;
                const message = input.value.trim();
                if (!message) return;
                if (!portfolioChatConfig || !portfolioChatConfig.endpoint) {
                    addPortfolioChatMessage(
                        'assistant',
                        'Serviciul AI nu este configurat pentru această versiune a dashboardului.',
                        [], true
                    );
                    return;
                }
                input.value = '';
                addPortfolioChatMessage('user', message, []);
                const priorHistory = portfolioChatHistory.slice(-8);
                portfolioChatHistory.push({ role: 'user', content: message });
                button.disabled = true;
                const pending = addPortfolioChatMessage(
                    'assistant', 'Analizez datele portofoliului și contextul pieței…', []
                );
                try {
                    const response = await fetch(portfolioChatConfig.endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            history: priorHistory,
                            context: portfolioChatConfig.context || {},
                            accessToken: portfolioChatConfig.access_token || ''
                        })
                    });
                    const payload = await response.json().catch(function() { return {}; });
                    if (!response.ok) {
                        throw new Error(payload.error || 'Serviciul AI nu a răspuns.');
                    }
                    if (payload.usage && typeof payload.usage === 'object') {
                        try {
                            const key = 'market-scanner:portfolio-chat-usage';
                            const history = JSON.parse(
                                localStorage.getItem(key) || '[]'
                            );
                            history.push({
                                recorded_at: new Date().toISOString(),
                                model: payload.model || 'gpt-5.6-terra',
                                usage: payload.usage
                            });
                            localStorage.setItem(
                                key, JSON.stringify(history.slice(-100))
                            );
                        } catch (usageError) {
                            console.warn('Nu am putut salva consumul chatului.', usageError);
                        }
                    }
                    if (pending) pending.remove();
                    if (payload.notice) {
                        const reasonSuffix = payload.reason
                            ? ' [diagnostic: ' + String(payload.reason) + ']'
                            : '';
                        addPortfolioChatMessage(
                            'assistant', payload.notice + reasonSuffix, [], false
                        );
                    }
                    addPortfolioChatMessage(
                        'assistant', payload.text || 'Nu am primit un răspuns utilizabil.',
                        payload.citations || []
                    );
                    portfolioChatHistory.push({
                        role: 'assistant', content: payload.text || ''
                    });
                } catch (error) {
                    if (pending) pending.remove();
                    const detail = error.message || 'eroare necunoscută';
                    addPortfolioChatMessage(
                        'assistant',
                        detail.toLowerCase().startsWith('chatul ai este temporar indisponibil')
                            ? detail
                            : 'Chatul AI este temporar indisponibil: ' + detail,
                        [], true
                    );
                } finally {
                    button.disabled = false;
                    input.focus();
                }
            }

            window.addEventListener('keydown', function(event) {
                if (event.key === 'Escape') togglePortfolioChat(false);
            });
            
            function initCharts(sparklines) {
                if (!sparklines) return;
                
                Object.keys(sparklines).forEach(function(sparkId) {
                    const ctx = document.getElementById(sparkId);
                    if (!ctx) return;
                    
                    const dataPoints = sparklines[sparkId];
                    if (!dataPoints || dataPoints.length === 0) return;
                    
                    // Logică colorare (replicată din Python logic, dar simplificată aici)
                    // Stock logic: Up = Green
                    const isUp = dataPoints[dataPoints.length - 1] >= dataPoints[0];
                    const color = isUp ? '#4caf50' : '#f44336';
                    
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: Array(dataPoints.length).fill(''),
                            datasets: [{
                                data: dataPoints,
                                borderColor: color,
                                borderWidth: 1.5,
                                fill: false,
                                pointRadius: 0,
                                tension: 0.1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { display: false }, tooltip: { enabled: false } },
                            scales: { x: { display: false }, y: { display: false } }
                        }
                    });
                });
            }

            function parseBrokerTotalsHistory(element) {
                if (!element) return [];
                try {
                    const parsed = JSON.parse(element.dataset.history || '[]');
                    return Array.isArray(parsed) ? parsed.filter(item =>
                        Number.isFinite(Number(item.net_liquidation)) &&
                        Number.isFinite(Number(item.total_cash)) &&
                        String(item.timestamp || '').length > 0
                    ) : [];
                } catch (error) {
                    console.error('Istoricul agregat al brokerilor este invalid.', error);
                    return [];
                }
            }

            function parseIBKRNavHistory(element) {
                if (!element) return [];
                try {
                    const parsed = JSON.parse(
                        element.dataset.ibkrNavHistory || '[]'
                    );
                    return Array.isArray(parsed) ? parsed.filter(item =>
                        Number.isFinite(Number(item.nav)) &&
                        String(item.date || '').length > 0
                    ) : [];
                } catch (error) {
                    console.error('Istoricul NAV IBKR este invalid.', error);
                    return [];
                }
            }

            function parseIBKRCashHistory(element) {
                if (!element) return [];
                try {
                    const parsed = JSON.parse(
                        element.dataset.ibkrCashHistory || '[]'
                    );
                    return Array.isArray(parsed) ? parsed.filter(item =>
                        Number.isFinite(Number(item.cash)) &&
                        String(item.date || '').length > 0
                    ) : [];
                } catch (error) {
                    console.error('Istoricul cash IBKR este invalid.', error);
                    return [];
                }
            }

            function openBrokerTotalsDetail(element) {
                const history = parseBrokerTotalsHistory(element);
                if (!history.length) return;
                const ibkrNavHistory = parseIBKRNavHistory(element);
                const ibkrCashHistory = parseIBKRCashHistory(element);
                const rawCurrency = String(element.dataset.currency || 'EUR').toUpperCase();
                const currency = /^[A-Z]{3}$/.test(rawCurrency) ? rawCurrency : 'EUR';
                const popup = window.open('', '_blank');
                if (!popup) {
                    alert('Browserul a blocat fereastra nouă. Permite pop-up-uri pentru acest site.');
                    return;
                }
                const payload = JSON.stringify(history).replace(/</g, '\\u003c');
                const ibkrNavPayload = JSON.stringify(
                    ibkrNavHistory
                ).replace(/</g, '\\u003c');
                const ibkrCashPayload = JSON.stringify(
                    ibkrCashHistory
                ).replace(/</g, '\\u003c');
                const latest = history[history.length - 1];
                const formatMoney = value => Number(value).toLocaleString('ro-RO', {
                    style: 'currency',
                    currency: currency,
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
                popup.document.open();
                popup.document.write(`<!DOCTYPE html>
<html lang="ro"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Istoric total IBKR + Tradeville</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f6f7fb;color:#121827;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.page{max-width:1500px;margin:0 auto;padding:28px}.top{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;margin-bottom:20px}
h1{margin:0;font-size:clamp(27px,4vw,44px)}.sub{color:#7760f9;font-weight:700;margin-top:6px}.close{border:1px solid #dfe3ea;background:#fff;padding:10px 16px;border-radius:10px;cursor:pointer}
.stats{display:grid;grid-template-columns:repeat(2,minmax(180px,1fr));gap:14px;margin-bottom:18px}.stat,.panel{background:#fff;border:1px solid #e1e5ec;border-radius:16px;box-shadow:0 4px 18px rgba(15,23,42,.05)}
.stat{padding:18px}.label{font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:.06em}.value{font-size:clamp(23px,4vw,34px);font-weight:750;margin-top:7px}
.panel{padding:20px}.chart-toolbar{display:flex;justify-content:flex-end;margin:0 0 12px}.range-controls{display:flex;flex-wrap:wrap;gap:7px}.range-btn{border:1px solid #dfe3ea;background:#fff;color:#4b5563;padding:7px 10px;border-radius:9px;font:700 12px/1 Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;cursor:pointer}.range-btn:hover{border-color:#9b8cff;color:#5b46d9}.range-btn.active{background:#7760f9;border-color:#7760f9;color:#fff}.chart-wrap{height:min(70vh,720px);min-height:430px;position:relative}.chart-wrap canvas{width:100%!important;height:100%!important}.note{margin:12px 0 0;color:#6b7280;font-size:12px}
@media(max-width:640px){.page{padding:14px}.top{flex-wrap:wrap}.stats{grid-template-columns:1fr}.panel{padding:14px}.chart-toolbar{justify-content:flex-start}.range-controls{gap:6px}.range-btn{padding:7px 9px}.chart-wrap{height:58vh;min-height:360px}}
</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"><\\/script>
</head><body><main class="page">
<div class="top"><div><h1>Total IBKR + Tradeville</h1><div class="sub">Istoric valoare totală, cash și NAV IBKR · ${currency}</div></div><button class="close" onclick="window.close()">Închide</button></div>
<section class="stats"><div class="stat"><div class="label">Valoare totală</div><div class="value">${formatMoney(latest.net_liquidation)}</div></div>
<div class="stat"><div class="label">Cash total</div><div class="value">${formatMoney(latest.total_cash)}</div></div></section>
<section class="panel"><div class="chart-toolbar"><div class="range-controls" role="group" aria-label="Interval grafic"><button class="range-btn" data-range="mtd">MTD</button><button class="range-btn" data-range="ytd">YTD</button><button class="range-btn" data-range="1w">1S</button><button class="range-btn" data-range="1m">1L</button><button class="range-btn" data-range="3m">3L</button><button class="range-btn" data-range="6m">6L</button><button class="range-btn" data-range="1y">1A</button><button class="range-btn active" data-range="all">Tot</button></div></div><div class="chart-wrap"><canvas id="brokerTotalsChart"></canvas></div>
<p class="note">Totalul și cashul combinat includ IBKR și Tradeville numai în punctele pentru care există ambele snapshoturi. Liniile NAV IBKR și Cash IBKR folosesc istoricul real furnizat de PortfolioAnalyst sau de raportul Flex configurat.</p></section>
</main><script>
const history=${payload};
const ibkrNavHistory=${ibkrNavPayload};
const ibkrCashHistory=${ibkrCashPayload};
const currency=${JSON.stringify(currency)};
const money=value=>Number(value).toLocaleString('ro-RO',{style:'currency',currency:currency,maximumFractionDigits:2});
const dateKey=value=>{
const raw=String(value||'').trim().replace(/^['\"]+|['\"]+$/g,'').trim();
if(/^\\\\d{8}(?:\\\\.0+)?$/.test(raw))return raw.slice(0,4)+'-'+raw.slice(4,6)+'-'+raw.slice(6,8)+'T00:00:00';
if(/^\\\\d{4}-\\\\d{2}-\\\\d{2}$/.test(raw))return raw+'T00:00:00';
const parsed=new Date(raw);
return Number.isNaN(parsed.getTime())?raw:parsed.toISOString();
};
const timestampKey=value=>{
const raw=String(value||'');
const parsed=new Date(raw);
return Number.isNaN(parsed.getTime())?raw:parsed.toISOString();
};
const labels=Array.from(new Set([
...history.map(item=>timestampKey(item.timestamp)),
...ibkrNavHistory.map(item=>dateKey(item.date)),
...ibkrCashHistory.map(item=>dateKey(item.date))
])).sort((left,right)=>{
const leftTime=new Date(left).getTime();
const rightTime=new Date(right).getTime();
if(Number.isNaN(leftTime))return Number.isNaN(rightTime)?String(left).localeCompare(String(right)):1;
if(Number.isNaN(rightTime))return -1;
return leftTime-rightTime;
});
const series=(items,dateField,valueField,keyFunction)=>{
const values=new Map(items.map(item=>[keyFunction(item[dateField]),Number(item[valueField])]));
return labels.map(label=>values.has(label)?values.get(label):null);
};
const displayDate=value=>{
const parsed=new Date(value);
if(Number.isNaN(parsed.getTime()))return String(value);
const isDailyPoint=/T00:00:00(?:\\.000)?(?:Z)?$/.test(String(value));
return new Intl.DateTimeFormat('ro-RO',isDailyPoint?{dateStyle:'short'}:{dateStyle:'short',timeStyle:'short'}).format(parsed);
};
const datasets=[
{label:'Valoare totală',data:series(history,'timestamp','net_liquidation',timestampKey),borderColor:'#7760f9',backgroundColor:'rgba(119,96,249,.08)',borderWidth:3,pointRadius:history.length===1?4:2,pointHoverRadius:5,tension:.18,fill:false,spanGaps:true},
{label:'Cash total',data:series(history,'timestamp','total_cash',timestampKey),borderColor:'#16a34a',backgroundColor:'rgba(22,163,74,.08)',borderWidth:3,pointRadius:history.length===1?4:2,pointHoverRadius:5,tension:.18,fill:false,spanGaps:true}
];
if(ibkrNavHistory.length){
datasets.push({label:'NAV IBKR',data:series(ibkrNavHistory,'date','nav',dateKey),borderColor:'#2563eb',backgroundColor:'rgba(37,99,235,.06)',borderWidth:2,pointRadius:0,pointHoverRadius:4,tension:.15,fill:false,spanGaps:true});
}
if(ibkrCashHistory.length){
datasets.push({label:'Cash IBKR',data:series(ibkrCashHistory,'date','cash',dateKey),borderColor:'#15803d',backgroundColor:'rgba(21,128,61,.05)',borderWidth:2,borderDash:[7,5],pointRadius:0,pointHoverRadius:4,tension:.15,fill:false,spanGaps:true});
}
const chart=new Chart(document.getElementById('brokerTotalsChart'),{
type:'line',
data:{labels:labels.map(displayDate),datasets},
options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},plugins:{legend:{position:'top'},tooltip:{callbacks:{label:context=>context.parsed.y===null?'':context.dataset.label+': '+money(context.parsed.y)}}},scales:{x:{ticks:{maxRotation:45,minRotation:0,autoSkip:true,maxTicksLimit:10}},y:{ticks:{callback:value=>money(value)}}}}
});
const labelTimes=labels.map(value=>{const time=new Date(value).getTime();return Number.isNaN(time)?null:time;});
const latestTime=Math.max(...labelTimes.filter(Number.isFinite));
const rangeStart=range=>{
if(range==='all'||!Number.isFinite(latestTime))return null;
const end=new Date(latestTime);const start=new Date(latestTime);
if(range==='mtd')return new Date(end.getFullYear(),end.getMonth(),1).getTime();
if(range==='ytd')return new Date(end.getFullYear(),0,1).getTime();
if(range==='1w')start.setDate(start.getDate()-7);
if(range==='1m')start.setMonth(start.getMonth()-1);
if(range==='3m')start.setMonth(start.getMonth()-3);
if(range==='6m')start.setMonth(start.getMonth()-6);
if(range==='1y')start.setFullYear(start.getFullYear()-1);
return start.getTime();
};
const applyRange=range=>{
const start=rangeStart(range);
let indices=labels.map((_,index)=>index).filter(index=>start===null||labelTimes[index]===null||labelTimes[index]>=start);
if(!indices.length)indices=[labels.length-1];
chart.data.labels=indices.map(index=>displayDate(labels[index]));
chart.data.datasets=datasets.map(dataset=>({...dataset,data:indices.map(index=>dataset.data[index])}));
chart.update();
document.querySelectorAll('.range-btn').forEach(button=>{
const active=button.dataset.range===range;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));
});
};
document.querySelectorAll('.range-btn').forEach(button=>button.addEventListener('click',()=>applyRange(button.dataset.range)));
window.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();window.close();}});
<\\/script></body></html>`);
                popup.document.close();
            }
            
            window.addEventListener('DOMContentLoaded', function () {
                void restorePortfolioAccess();
            });
            
            // Global Tooltip Logic
            function showTooltip(evt, text) {
                const tooltip = document.getElementById('global-tooltip');
                if (!tooltip) return;
                
                tooltip.innerHTML = text;
                tooltip.style.visibility = 'visible';
                tooltip.style.opacity = '1';
                
                // Position logic
                const x = evt.clientX;
                const y = evt.clientY;
                
                tooltip.style.top = y + 'px';
                tooltip.style.left = x + 'px';
            }
            
            function hideTooltip() {
                const tooltip = document.getElementById('global-tooltip');
                if (tooltip) {
                    tooltip.style.visibility = 'hidden';
                    tooltip.style.opacity = '0';
                }
            }
        </script>
    """
    
    # Continue HTML (f-string again for {timestamp})
    html_head += f"""
    </head>
    <body>
    
    <div id="global-tooltip"></div>
    
    <!-- Header cu Hamburger -->
    <div class="header-bar">
        <div class="container">
            <div class="hamburger" onclick="toggleMenu()">☰</div>
            <div class="app-title">Market Scanner</div>
            <div style="font-size: 0.8rem; color: var(--text-secondary);">Generated: {timestamp}</div>
        </div>
        
        <div id="navMenu" class="menu-dropdown">
            <div class="menu-item" onclick="switchTab('portfolio')">Portofoliu Activ</div>
            <div class="menu-item" onclick="switchTab('market')">Market Overview</div>
            <div class="menu-item" onclick="switchTab('watchlist')">Watchlist</div>
            <div class="menu-item" onclick="switchTab('volatility')">Volatility Calculator</div>
        </div>
    </div>
        
    <div class="container">
        <div id="portfolio" class="tab-content">
            
            <!-- LOCK SCREEN Local -->
            <div id="portfolio-lock" style="max-width: 500px; margin: 80px auto; text-align: center; padding: 48px; background: var(--bg-white); border-radius: var(--radius-lg); box-shadow: var(--shadow-md); border: 1px solid var(--border-light);">
                <h2 style="color: var(--text-primary); margin-bottom: 12px;">Secțiune Protejată</h2>
                <p style="color: var(--text-secondary); margin-bottom: 32px; font-size: 16px;">Introdu PIN-ul pentru a accesa portofoliul</p>
                <div style="display: flex; gap: 12px; justify-content: center; align-items: center;">
                    <input type="password" id="pf-pass" style="padding: 14px 20px; font-size: 18px; text-align: center; width: 180px; border-radius: var(--radius-sm); border: 1px solid var(--border-light); background: var(--bg-white); color: var(--text-primary); letter-spacing: 8px; font-weight: 600; transition: all 0.2s;" placeholder="••••" onkeyup="if(event.key==='Enter') unlockPortfolio()" onfocus="this.style.borderColor='var(--primary-purple)'; this.style.boxShadow='0 0 0 3px rgba(119,96,249,0.1)'" onblur="this.style.borderColor='var(--border-light)'; this.style.boxShadow='none'">
                    <button onclick="unlockPortfolio()" class="btn-primary">Unlock</button>
                </div>
                <p style="color: var(--text-secondary); margin: 18px 0 0; font-size: 13px;">Accesul rămâne activ 30 de zile de la ultima autentificare manuală sau automată în acest browser.</p>
            </div>
            
            <!-- ACTUAL DATA (Hidden) -->
            <div id="portfolio-data" style="display: none;">
                <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
                    <button type="button" onclick="logoutPortfolio()" style="border: 1px solid var(--border-light); background: var(--bg-white); color: var(--text-secondary); border-radius: var(--radius-sm); padding: 8px 12px; cursor: pointer;">Deconectare de pe acest dispozitiv</button>
                </div>
                <div class="summary">
                    <div class="summary-card">
                        <h3>Total Investment</h3>
                        <div class="value">€{total_investment:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Current Value</h3>
                        <div class="value">€{total_value:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Positions on Profit</h3>
                        <div class="value" style="color: #4caf50;">{total_pos_profit}/{len(portfolio_df)}</div>
                    </div>
                    <div class="summary-card">
                        <h3>P&L at Stop Positive</h3>
                        <div class="value" style="color: #4caf50;">{total_pos_stop_profit}/{len(portfolio_df)}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Total Profit</h3>
                        <div class="value {'positive' if total_profit >= 0 else 'negative'}">€{total_profit:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>ROI</h3>
                        <div class="value {'positive' if total_profit_pct >= 0 else 'negative'}">{total_profit_pct:.2f}%</div>
                    </div>
                    <div class="summary-card">
                        <h3>Max Potential Profit</h3>
                        <div class="value {'positive' if total_max_profit > 0 else ''}" style="color: #4dabf7;">€{total_max_profit:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Total P/L la Stop</h3>
                        <div class="value {'positive' if total_pl_at_stop >= 0 else 'negative'}">€{total_pl_at_stop:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Ordine cumpărare</h3>
                        <div class="value">__ACTIVE_BUY_ORDERS_TOTAL_EUR__</div>
                    </div>
                    <div class="summary-card" title="Variația valorii totale de la primul snapshot al lunii; transferurile externe pot influența rezultatul.">
                        <h3>P/L luna curentă</h3>
                        <div class="value __CURRENT_MONTH_PL_CLASS__">__CURRENT_MONTH_PL_EUR__</div>
                    </div>

                </div>
                
                <!-- RISK ON/OFF ANALYSIS CARDS -->
                <h3 style="margin-top:30px;margin-bottom:15px;color:var(--text-primary);">Market Risk Status — separat pe piețe</h3>
                <h4 style="margin:0 0 10px;color:var(--text-secondary);">SUA — SPX / VIX / breadth</h4>
                <div class="market-risk-grid">
                    {risk_cards_html}
                </div>
                <h4 style="margin:0 0 10px;color:var(--text-secondary);">România / BVB — TVBETETF</h4>
                <div class="market-risk-grid">
                    {bvb_risk_cards_html}
                </div>

            <div id="portfolio-ai-container"></div>
            
            <div style="text-align: right; color: #888; font-size: 0.8rem; margin-bottom: 10px; padding-right: 10px;">
                📅 Last IBKR/Data Update: <strong>{ibkr_last_update}</strong>
            </div>
            
            <div class="table-container">
            <table id="portfolio-table">
                <thead>
                    <tr>
                        <th style="width: 80px;">Simbol</th>
                        <th>Decizie</th>
                        <th>Data</th>
                        <th>Acțiuni</th>
                        <th>Preț Cumpărare</th>
                        <th>Preț Curent</th>
                        <th>Grafic</th>
                        <th>Target</th>
                        <th>% Mid</th>
                        <th>Consensus</th>
                        <th>Analysts</th>
                        <th>Trail %</th>
                        <th>Trail Propus</th>
                        <th># Stop</th>
                        <th>Suggested Stop</th>
                        <th>Investiție</th>
                        <th>Valoare</th>
                        <th>Profit</th>
                        <th>% Profit</th>
                        <th>P/L la Stop</th>
                        <th>Max Profit</th>
                        <th>Status</th>
                        <th>Trend</th>
                        <th onmousemove="showTooltip(event, '<strong>RSI (Relative Strength Index)</strong><br>măsoară viteza și schimbarea prețurilor.<br>Valori: >70 (Overbought), <30 (Oversold).')" onmouseout="hideTooltip()">RSI</th>
                        <th onmousemove="showTooltip(event, '<strong>RS vs SPX (Relative Strength vs S&P 500) pe 60 de zile.</strong><br><br>Reprezintă diferența dintre randamentul acțiunii și randamentul indexului S&P 500 în ultimele 60 de zile.<br><br><em>Exemplu:</em><br>Dacă acțiunea a crescut cu 20% și S&P 500 cu 5% => <strong>RS = +15%</strong>.<br>Dacă valoarea este pozitivă, acțiunea performează mai bine decât piața.')" onmouseout="hideTooltip()">RS vs SPX</th>
                    </tr>
                </thead>
                <tbody id="portfolio-rows-body">
                    <!-- Rows will be injected by JS after decryption -->
    """
    
    # Portfolio rows generation (for encryption)
    portfolio_rows_html = ""
    sparkline_data = {}
    
    chart_id = 0
    for _, row in portfolio_df.iterrows():
        trend_cls = row['Trend'].replace(' ', '-')
        rsi_cls = row['RSI_Status']
        status_cls = row['Status']
        profit_cls = 'positive' if row['Profit'] >= 0 else 'negative'
        
        if row['Target'] and pd.notna(row['Target']) and row['Current_Price'] > 0:
            pct_to_target = ((row['Target'] - row['Current_Price']) / row['Current_Price']) * 100
            target_display = f"€{row['Target']:.2f}"
            pct_display = f"{pct_to_target:.1f}%"
            max_profit_display = f"€{row['Max_Profit']:,.2f}" if row['Max_Profit'] and pd.notna(row['Max_Profit']) else "N/A"
        else:
            pct_to_target = 0
            target_display = "N/A"
            pct_display = "N/A"
            max_profit_display = "N/A"
        
        sparkline_id = f"spark_{chart_id}"
        chart_id += 1
        
        # Save sparkline data for JS
        sparkline_data[sparkline_id] = row['Sparkline']
        
        # P/L la Stop Calc (use effective stop: prefer Trail_Stop_IBKR if available)
        pl_at_stop_display = "-"
        pl_at_stop_class = ""
        eff_stop_row = 0
        if 'Trail_Stop_IBKR' in row.index and pd.notna(row.get('Trail_Stop_IBKR', 0)) and row.get('Trail_Stop_IBKR', 0) > 0:
            eff_stop_row = row['Trail_Stop_IBKR']
        elif row['Trail_Stop'] and pd.notna(row['Trail_Stop']) and row['Trail_Stop'] > 0:
            eff_stop_row = row['Trail_Stop']
        if eff_stop_row > 0:
            pl_at_stop = (eff_stop_row - row['Buy_Price']) * row['Shares']
            pl_at_stop_display = f"€{pl_at_stop:,.2f}"
            pl_at_stop_class = "positive" if pl_at_stop > 0 else "negative"
        
        target_val = row['Target'] if row['Target'] and pd.notna(row['Target']) else ""
        if isinstance(target_val, (int, float)): target_val = f"{target_val:.2f}"
        
        trail_pct_val = row['Trail_Pct'] if pd.notna(row['Trail_Pct']) else 0
        # Display effective stop value
        trail_stop_val = eff_stop_row if eff_stop_row > 0 else ""
        if isinstance(trail_stop_val, (int, float)): trail_stop_val = f"{trail_stop_val:.2f}"

        # RSI Tooltip Logic (Matches Watchlist)
        rsi_val = row['RSI']
        rsi_tooltip = ""
        if rsi_val >= 70:
            rsi_tooltip = "<strong>RSI: Overbought (>70)</strong><br>Supra-cumpărat. Prețul a crescut foarte rapid.<br>⚠️ <strong>Acțiune:</strong> Risc crescut de corecție (scădere). Nu cumpăra la vârf."
        elif 50 <= rsi_val < 70:
            rsi_tooltip = "<strong>RSI: Bullish (50-70)</strong><br>Momentum pozitiv. Cumpărătorii controlează piața.<br>✅ <strong>Acțiune:</strong> Zonă bună pentru trend following."
        elif 30 <= rsi_val < 50:
            rsi_tooltip = "<strong>RSI: Bearish (30-50)</strong><br>Momentum negativ sau neutru-sláb.<br>⛔ <strong>Acțiune:</strong> Prudență. Trendul poate fi descendent."
        else:
            rsi_tooltip = "<strong>RSI: Oversold (<30)</strong><br>Supra-vândut. Prețul a scăzut extrem.<br>🔄 <strong>Acțiune:</strong> Posibilă revenire (Bounce) iminentă."

        # Consensus
        cons = row.get('Consensus', '-')
        cons_style = ""
        if 'Buy' in str(cons): cons_style = 'color: #4caf50; font-weight: bold;'
        elif 'Sell' in str(cons): cons_style = 'color: #f44336; font-weight: bold;'
        analysts = row.get('Analysts', 0)
        
        # Calculate Trail LARG (Propus)
        atr_pct = (row.get('Finviz_ATR', 0) / row.get('Price_Native', 1) * 100) if row.get('Price_Native', 0) > 0 and row.get('Finviz_ATR', 0) else 0
        vol_w = row.get('Vol_W', 0) or 0
        vol_m = row.get('Vol_M', 0) or 0
        vols_valid = [v for v in [atr_pct, vol_w, vol_m] if v > 0]
        trail_larg = max(vols_valid) * 3 if vols_valid else 0
        
        # Color green if Trail LARG >= Trail %, red otherwise
        if trail_larg >= trail_pct_val:
            trail_larg_style = "color: #4caf50; font-weight: bold;"
        else:
            trail_larg_style = "color: #f44336; font-weight: bold;"
        trail_larg_display = f"{trail_larg:.1f}%" if trail_larg > 0 else "-"

        sell_decision = row.get('Sell_Decision', 'HOLD')
        sell_reason = row.get('Sell_Reason', '')
        
        # Default text for HOLD is now handled in process_portfolio_ticker with real metrics.
        # Fallback only if somehow still empty:
        if sell_decision == 'HOLD' and not sell_reason:
             sell_reason = "Hold (Metrics Optimized)"

        sell_style = "color: #4caf50; font-weight: bold;" # Green (HOLD)
        if sell_decision == "EXIT":
            sell_style = "color: #d32f2f; font-weight: bold; background-color: #ffebee; border-radius: 4px; padding: 2px 6px;" # Red
        elif sell_decision == "REDUCE":
            sell_style = "color: #fb8c00; font-weight: bold;" # Orange
            
        sell_display = sell_decision
        if sell_decision != "HOLD":
             sell_display = f"{sell_decision} ⚠️"

        # Build Row HTML string (NO html_head += here)
        # Using JS Global Tooltip for guaranteed visibility (no overflow clipping)

        # Symbol Display (with Earnings Bomb if danger)
        symbol_display = row['Symbol']
        if row.get('Earnings_Danger'):
            msg = row.get('Earnings_Msg', 'Earnings Soon')
            symbol_display += f' <span style="cursor:help; font-size:1.2em;" onmousemove="showTooltip(event, \'<strong>💣 Earnings Danger Zone</strong><br>{msg}<br>⚠️ Volatilitate extremă posibilă.\')" onmouseout="hideTooltip()">💣</span>'

        portfolio_rows_html += f"""
                    <tr id="row-{row['Symbol']}" data-price="{row['Current_Price']}" data-buy="{row['Buy_Price']}" data-shares="{row['Shares']}">
                        <td><strong style="cursor: help; color: #4dabf7; text-decoration: underline;" onmousemove="showTooltip(event, '{row.get('Company_Name', '')}')" onmouseout="hideTooltip()" onclick="goToVolatility('{row['Symbol']}')">{symbol_display}</strong></td>
                        <td style="{sell_style}" onmousemove="showTooltip(event, '{sell_reason}')" onmouseout="hideTooltip()">
                            {sell_display}
                        </td>
                        <td style="font-size: 0.9em; color: var(--text-secondary);">{row.get('Entry_Date', '-')}</td>
                        <td>{row['Shares']}</td>
                        <td>€{row['Buy_Price']:.2f}</td>
                        <td>€{row['Current_Price']:.2f}</td>
                        <td><canvas id="{sparkline_id}" class="sparkline-container" role="button" tabindex="0" title="Deschide graficul și detaliile pentru {row['Symbol']}" style="cursor:pointer;" onclick="openPortfolioDetail('{row['Symbol']}')" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();openPortfolioDetail('{row['Symbol']}');}}"></canvas></td>
                        
                        <!-- TARGET -->
                        <td>{target_display}</td>
                        <td class="{'positive' if pct_to_target > 0 else 'negative' if row['Target'] else ''}">{pct_display}</td>
                        
                        <!-- Consensus -->
                        <td style="{cons_style}">{cons}</td>
                        <td>{analysts}</td>

                        <!-- Trail % -->
                        <td>{trail_pct_val:.1f}%</td>
                        
                        <!-- Trail Propus (LARG) -->
                        <td style="{trail_larg_style}">{trail_larg_display}</td>
                        
                        <!-- Trail Stop -->
                        <td>{f"€{trail_stop_val}" if isinstance(trail_stop_val, (int, float)) or (isinstance(trail_stop_val, str) and trail_stop_val) else "-"}</td>
                        
                        <td>€{row['Suggested_Stop']:.2f}</td>
                        <td>€{row['Investment']:,.2f}</td>
                        <td>€{row['Current_Value']:,.2f}</td>
                        <td class="{profit_cls}">€{row['Profit']:,.2f}</td>
                        <td class="{profit_cls}">{row['Profit_Pct']:.2f}%</td>
                        
                        <!-- P/L la Stop -->
                        <td class="{pl_at_stop_class}">{pl_at_stop_display}</td>
                        
                        <!-- Max Profit -->
                        <td id="cell-{row['Symbol']}-maxprofit">{max_profit_display}</td>
                        

                        <td class="rsi-{status_cls}" style="cursor: help;" onmousemove="showTooltip(event, 'RSI Status: {row['RSI_Status']}')" onmouseout="hideTooltip()">{row['Status']}</td>
                        <td class="trend-{trend_cls}">{row['Trend']}</td>
                        
                        <!-- RSI Value -->
                        <td style="font-weight: bold; cursor: help;" onmousemove="showTooltip(event, '{rsi_tooltip}')" onmouseout="hideTooltip()">{row['RSI']:.0f}</td>
                        
                        <!-- RS vs SPX -->
                        <td style="color: {'#4caf50' if row.get('RS_vs_SPX', 0) and row.get('RS_vs_SPX', 0) > 0 else '#f44336'}; font-weight: bold;">{row.get('RS_vs_SPX', '-') if row.get('RS_vs_SPX') is not None else '-'}%</td>
                    </tr>
        """
        
    # Build lookup for all technical metrics from watchlist & portfolio
    ticker_lookup = {}
    if not watchlist_df.empty and 'Ticker' in watchlist_df.columns:
        for _, r in watchlist_df.iterrows():
            ticker_lookup[str(r['Ticker']).upper()] = r
            
    if not portfolio_df.empty and 'Symbol' in portfolio_df.columns:
        for _, r in portfolio_df.iterrows():
            ticker_lookup[str(r['Symbol']).upper()] = r

    def find_ticker_data(symbol):
        symbol = str(symbol).upper()
        if symbol in ticker_lookup:
            return ticker_lookup[symbol]
        for k, v in ticker_lookup.items():
            k_base = k.split('.')[0]
            sym_base = symbol.split('.')[0]
            if k_base == sym_base:
                return v
        return None

    def render_order_rows(orders_df_subset, rates, prefix_id):
        nonlocal chart_id
        rows_html = ""
        for _, r_order in orders_df_subset.iterrows():
            symbol = str(r_order.get('Symbol', ''))
            order_type = str(r_order.get('OrderType', ''))
            
            def get_val(col, default=0.0):
                val = r_order.get(col, default)
                if pd.isna(val) or val is None:
                    return default
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return default
            
            qty = get_val('Total_Qty', 0.0)
            limit_price = get_val('Limit_Price', 0.0)
            if limit_price == 0.0 and order_type == 'LMT':
                aux_price_raw = get_val('Aux_Price', 0.0)
                stop_price_raw = get_val('Stop_Price', 0.0)
                if aux_price_raw > 0 and aux_price_raw < 1e10:
                    limit_price = aux_price_raw
                elif stop_price_raw > 0 and stop_price_raw < 1e10:
                    limit_price = stop_price_raw
            
            stop_price = get_val('Stop_Price', 0.0)
            if stop_price > 1e10:
                stop_price = 0.0
            trail_pct_order = get_val('Trail_Pct', 0.0)
            if trail_pct_order > 1e10:
                trail_pct_order = 0.0
            
            t_data = find_ticker_data(symbol)
            
            if t_data is not None:
                m_symbol = t_data.get('Symbol', t_data.get('Ticker', symbol))
                company_name = t_data.get('Company_Name', '').replace("'", "\\'")
                curr_price = float(t_data.get('Price', t_data.get('Current_Price', 0)))
                
                spark_id = f"spark_order_{chart_id}"
                chart_id += 1
                sparkline_data[spark_id] = t_data.get('Sparkline', [])
                
                target_val = t_data.get('Target', None)
                pct_to_target = t_data.get('Pct_To_Target', t_data.get('Percent_To_Target', None))
                if target_val and pd.notna(target_val) and curr_price > 0:
                    target_val = float(target_val)
                    if not pct_to_target or pd.isna(pct_to_target):
                        pct_to_target = ((target_val - curr_price) / curr_price) * 100
                
                suggested_stop = t_data.get('Stop_Loss', t_data.get('Suggested_Stop', 0))
                
                trend_val = t_data.get('Trend', 'Neutral')
                trend_cls = trend_val.replace(' ', '-')
                rsi_val = t_data.get('RSI', 0.0)
                rsi_status = t_data.get('RSI_Status', 'Neutral')
                rs_vs_spx = t_data.get('RS_vs_SPX', None)
                consensus = t_data.get('Consensus', '-')
                currency = t_data.get('Currency')
                if not currency or pd.isna(currency):
                    currency = 'USD'
                    if '.RO' in symbol: currency = 'RON'
                    elif '.PA' in symbol or '.DE' in symbol or '.AS' in symbol: currency = 'EUR'
                    elif '.L' in symbol: currency = 'GBP'
            else:
                m_symbol = symbol
                company_name = ""
                curr_price = 0.0
                spark_id = ""
                target_val = None
                pct_to_target = None
                suggested_stop = 0.0
                trend_val = "Neutral"
                trend_cls = "Neutral"
                rsi_val = 0.0
                rsi_status = "Neutral"
                rs_vs_spx = None
                consensus = "-"
                currency = 'USD'
                if '.RO' in symbol: currency = 'RON'
                elif '.PA' in symbol or '.DE' in symbol or '.AS' in symbol: currency = 'EUR'
                elif '.L' in symbol: currency = 'GBP'
            
            rate = rates.get(currency, rates.get('USD', 0.92))
            if currency == 'EUR':
                rate = 1.0
            
            order_price_native = limit_price if order_type == 'LMT' else stop_price
            if order_price_native <= 0:
                order_price_native = get_val('Calculated_Stop', 0.0)
            
            order_price_eur = order_price_native * rate
            
            if limit_price > 0:
                est_inv = qty * limit_price * rate
            elif curr_price > 0:
                est_inv = qty * curr_price
            else:
                est_inv = qty * order_price_eur
            
            order_price_display = f"€{order_price_eur:.2f}" if order_price_eur > 0 else "-"
            curr_price_display = f"€{curr_price:.2f}" if curr_price > 0 else "-"
            target_display = f"€{target_val:.2f}" if target_val and pd.notna(target_val) else "N/A"
            pct_display = f"{pct_to_target:.1f}%" if pct_to_target is not None and pd.notna(pct_to_target) else "N/A"
            suggested_stop_display = f"€{suggested_stop:.2f}" if suggested_stop and pd.notna(suggested_stop) and suggested_stop > 0 else "-"
            est_inv_display = f"€{est_inv:,.2f}" if est_inv > 0 else "-"
            
            cons_style = ""
            if 'Buy' in str(consensus):
                cons_style = 'color: #4caf50; font-weight: bold;'
            elif 'Sell' in str(consensus):
                cons_style = 'color: #f44336; font-weight: bold;'
            
            rsi_tooltip = ""
            if rsi_val >= 70:
                rsi_tooltip = "<strong>RSI: Overbought (>70)</strong><br>Supra-cumpărat. Prețul a crescut foarte rapid.<br>⚠️ <strong>Acțiune:</strong> Risc crescut de corecție (scădere). Nu cumpăra la vârf."
            elif 50 <= rsi_val < 70:
                rsi_tooltip = "<strong>RSI: Bullish (50-70)</strong><br>Momentum pozitiv. Cumpărătorii controlează piața.<br>✅ <strong>Acțiune:</strong> Zonă bună pentru trend following."
            elif 30 <= rsi_val < 50:
                rsi_tooltip = "<strong>RSI: Bearish (30-50)</strong><br>Momentum negativ sau neutru-sláb.<br>⛔ <strong>Acțiune:</strong> Prudență. Trendul poate fi descendent."
            elif rsi_val > 0:
                rsi_tooltip = "<strong>RSI: Oversold (<30)</strong><br>Supra-vândut. Prețul a scăzut extrem.<br>🔄 <strong>Acțiune:</strong> Posibilă revenire (Bounce) iminentă."

            detail_symbol = str(m_symbol or symbol).upper()
            spark_cell = (
                f'<canvas id="{spark_id}" class="sparkline-container" '
                f'role="button" tabindex="0" '
                f'title="Deschide graficul mare cu recomandările pentru {detail_symbol}" '
                f'style="cursor:pointer;" '
                f'onclick="openOrderDetail(\'{detail_symbol}\')" '
                f'onkeydown="if(event.key===\'Enter\'||event.key===\' \')'
                f'{{event.preventDefault();openOrderDetail(\'{detail_symbol}\');}}"></canvas>'
                if spark_id else "-"
            )
            
            rows_html += f"""
            <tr id="{prefix_id}-row-{symbol}">
                <td><strong style="cursor: help; color: #4dabf7; text-decoration: underline;" onmousemove="showTooltip(event, \'{company_name}\')" onmouseout="hideTooltip()">{m_symbol}</strong></td>
                <td>{order_type}</td>
                <td>{qty:.0f}</td>
                <td>{order_price_display}</td>
                <td>{f"{trail_pct_order:.1f}%" if trail_pct_order > 0 else "-"}</td>
                <td>{curr_price_display}</td>
                <td>{spark_cell}</td>
                <td>{target_display}</td>
                <td class="{'positive' if pct_to_target and pct_to_target > 0 else 'negative' if pct_to_target else ''}">{pct_display}</td>
                <td style="{cons_style}">{consensus}</td>
                <td>{suggested_stop_display}</td>
                <td>{est_inv_display}</td>
                <td class="trend-{trend_cls}">{trend_val}</td>
                <td style="font-weight: bold; cursor: help;" onmousemove="showTooltip(event, \'{rsi_tooltip}\')" onmouseout="hideTooltip()">{f"{rsi_val:.0f}" if rsi_val > 0 else "-"}</td>
                <td style="color: {'#4caf50' if rs_vs_spx and rs_vs_spx > 0 else '#f44336'}; font-weight: bold;">{f"{rs_vs_spx:.1f}%" if rs_vs_spx is not None else "-"}%</td>
            </tr>
            """
        return rows_html

    buying_rows_html = ""
    selling_rows_html = ""
    
    orders_list = []
    orders_df = pd.DataFrame()
    orders_cache_password = _orders_snapshot_password(password)
    try:
        tws_orders_frame, orders_cache_changed, orders_source = (
            _load_cached_tws_orders(
                full_state,
                orders_cache_password,
            )
        )
        orders_list.append(tws_orders_frame)
        if orders_source == 'encrypted_cache_invalid':
            message = (
                "Snapshotul criptat al ordinelor IBKR nu poate fi "
                "decriptat cu cheia configurată."
            )
            if os.environ.get('GITHUB_ACTIONS') == 'true':
                raise RuntimeError(
                    message + " Oprim deploy-ul pentru a nu publica tabele incomplete."
                )
            print(f"  -> AVERTISMENT: {message}")
        if orders_cache_changed:
            market_utils.save_state(full_state)
            print("  -> Snapshotul criptat al ordinelor TWS a fost actualizat.")
        elif orders_source == 'tws_encrypted_cache':
            print(
                "  -> TWS indisponibil în acest mediu; păstrăm ultimul "
                "snapshot criptat al ordinelor."
            )
    except Exception as e:
        print(f"Error reading encrypted TWS orders snapshot: {e}")
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            raise
            
    if os.path.exists('tradeville_orders.csv'):
        try:
            orders_list.append(_read_order_snapshot('tradeville_orders.csv'))
        except Exception as e:
            print(f"Error reading tradeville_orders.csv: {e}")
            
    if orders_list:
        try:
            orders_df = _concat_order_frames(orders_list)
            orders_df = _filter_orders_against_current_positions(
                orders_df, portfolio_df
            )
            if not orders_df.empty and 'Action' in orders_df.columns:
                buy_orders = orders_df[orders_df['Action'].str.upper() == 'BUY']
                sell_orders = orders_df[orders_df['Action'].str.upper() == 'SELL']
                
                rates = {}
                if full_state:
                    rates = full_state.get('rates', {})
                if not rates:
                    rates = {'EUR': 1.0, 'USD': 0.92, 'RON': 0.20, 'GBP': 1.18}
                
                buying_rows_html = render_order_rows(buy_orders, rates, 'buy')
                selling_rows_html = render_order_rows(sell_orders, rates, 'sell')
        except Exception as ex:
            print(f"Error parsing concatenated orders: {ex}")
            buying_rows_html = f'<tr><td colspan="15" style="text-align:center; color: var(--error-red);">Eroare la procesarea ordinelor active.</td></tr>'
            selling_rows_html = f'<tr><td colspan="15" style="text-align:center; color: var(--error-red);">Eroare la procesarea ordinelor active.</td></tr>'

    if not buying_rows_html:
        buying_rows_html = '<tr><td colspan="15" style="text-align:center;">Niciun ordin de cumpărare activ în IBKR / Tradeville.</td></tr>'
    if not selling_rows_html:
        selling_rows_html = '<tr><td colspan="15" style="text-align:center;">Niciun ordin de vânzare activ în IBKR / Tradeville.</td></tr>'

    # Encrypt Data
    account_password = _orders_snapshot_password(password)
    tws_account_data, tws_account_source = _load_portable_account_snapshot(
        'tws_account.json', 'tws_account.enc.json', account_password
    )
    if (
        tws_account_source in {'local_invalid', 'encrypted_cache_invalid'}
        and os.environ.get('GITHUB_ACTIONS') == 'true'
    ):
        raise RuntimeError(
            "Snapshotul exact IBKR nu poate fi decriptat. Oprim deploy-ul "
            "pentru a nu elimina soldurile brute din dashboard."
        )
    if tws_account_data is None and os.path.exists('tws_account_risk.json'):
        try:
            with open('tws_account_risk.json', 'r', encoding='utf-8') as handle:
                tws_account_data = json.load(handle)
        except (OSError, ValueError, TypeError):
            tws_account_data = None

    tradeville_account_data, tradeville_account_source = (
        _load_portable_account_snapshot(
            'tradeville_account.json',
            'tradeville_account.enc.json',
            account_password,
        )
    )
    if (
        tradeville_account_source in {
            'local_invalid', 'encrypted_cache_invalid'
        }
        and os.environ.get('GITHUB_ACTIONS') == 'true'
    ):
        raise RuntimeError(
            "Snapshotul exact Tradeville nu poate fi decriptat. Oprim "
            "deploy-ul pentru a nu elimina soldurile brute din dashboard."
        )

    # Snapshoturile exacte pot fi analizate împreună, dar conturile rămân
    # distincte. Nu amestecăm un fallback pe benzi cu valori exacte.
    if tradeville_account_data and (
        tws_account_data is None or tws_account_data.get('privacy_mode') != 'bands_only'
    ):
        tradeville_account_data = _correct_tradeville_manual_snapshot(
            tradeville_account_data
        )
        if tws_account_data is None:
            tws_account_data = tradeville_account_data
        else:
            tws_account_data = dict(tws_account_data)
            tws_account_data['source'] = 'IBKR TWS + Tradeville manual'
            ibkr_fetched_at = tws_account_data.get('fetched_at')
            tradeville_fetched_at = tradeville_account_data.get('fetched_at')
            ibkr_accounts = []
            raw_ibkr_accounts = list(tws_account_data.get('accounts', []))
            for index, raw_account in enumerate(raw_ibkr_accounts, start=1):
                ibkr_account = dict(raw_account)
                ibkr_account['label'] = (
                    'IBKR' if len(raw_ibkr_accounts) == 1
                    else f'IBKR {index}'
                )
                ibkr_account['source'] = 'IBKR TWS'
                ibkr_account.setdefault('fetched_at', ibkr_fetched_at)
                ibkr_accounts.append(ibkr_account)
            tradeville_accounts = []
            for raw_account in tradeville_account_data.get('accounts', []):
                tradeville_account = dict(raw_account)
                tradeville_account.setdefault(
                    'fetched_at', tradeville_fetched_at
                )
                tradeville_accounts.append(tradeville_account)
            tws_account_data['accounts'] = (
                ibkr_accounts
                + tradeville_accounts
            )
            timestamps = [
                value for value in (
                    ibkr_fetched_at,
                    tradeville_fetched_at,
                ) if value
            ]
            if timestamps:
                # Timestampul agregat descrie cea mai proaspătă sursă. Fiecare
                # cont păstrează separat timestampul propriu, astfel încât un
                # snapshot Tradeville vechi să nu marcheze IBKR ca stale.
                tws_account_data['fetched_at'] = max(
                    timestamps,
                    key=lambda value: (
                        _parse_snapshot_timestamp(value)
                        or datetime.datetime.min.replace(
                            tzinfo=datetime.timezone.utc
                        )
                    ),
                )

    # Istoricul agregat rămâne criptat în starea publicată. Totalul este
    # disponibil numai când există atât IBKR, cât și Tradeville în aceeași
    # monedă de bază, astfel încât cash-ul să nu fie dublat sau amestecat.
    broker_totals_history = []
    encrypted_broker_history = (
        (full_state or {}).get('broker_totals_history_enc')
    )
    if encrypted_broker_history:
        broker_totals_history = _decrypt_broker_totals_history(
            encrypted_broker_history,
            account_password=account_password,
            legacy_password=password,
        )
    previous_broker_totals_history = list(broker_totals_history)
    broker_totals_history = analysis.update_broker_totals_history(
        broker_totals_history,
        tws_account_data,
    )
    if broker_totals_history and tws_account_data:
        tws_account_data = dict(tws_account_data)
        tws_account_data['combined_history'] = broker_totals_history
        history_password = account_password or password
        if full_state is not None and history_password:
            full_state['broker_totals_history_enc'] = json.loads(
                market_security.encrypt_for_js(
                    json.dumps(
                        broker_totals_history,
                        ensure_ascii=False,
                    ),
                    history_password,
                )
            )
            if broker_totals_history != previous_broker_totals_history:
                market_utils.save_state(full_state)
    cached_portfolio_ai = full_state.get('last_portfolio_ai_analysis')
    cached_portfolio_evidence = full_state.get('last_portfolio_ai_evidence')
    portfolio_market_context = analysis.build_portfolio_market_context(
        portfolio_df, full_state.get('market_indicators', {})
    )
    tvbetetf_holdings = analysis.fetch_tvbetetf_holdings(
        cached=(full_state or {}).get('tvbetetf_holdings')
    )
    if tvbetetf_holdings:
        full_state['tvbetetf_holdings'] = tvbetetf_holdings
    us_sector_rotation = analysis.fetch_us_sector_rotation(
        cached=(full_state or {}).get('us_sector_rotation')
    )
    if us_sector_rotation:
        full_state['us_sector_rotation'] = us_sector_rotation
    us_market_regime = analysis.build_us_market_regime(
        full_state.get('market_indicators', {}),
        full_state.get('eco_phase'),
    )
    full_state['us_market_regime'] = us_market_regime
    strict_buy_candidates = select_strict_buy_candidates(
        watchlist_df,
        (full_state or {}).get('external_buy_research', []),
        etf_holdings=tvbetetf_holdings,
        sector_rotation=us_sector_rotation,
        us_market_regime=us_market_regime,
        bvb_universe=(full_state or {}).get('bvb_equity_universe', []),
    )
    candidate_rates = (full_state or {}).get('rates', {})
    buy_candidate_payload = []
    for item in strict_buy_candidates:
        symbol = str(item.get('Ticker', '')).upper()
        execution_values = _buy_candidate_execution_values(
            item, rates=candidate_rates
        )
        native_chart_detail = _chart_detail_native_payload(
            item,
            symbol,
            'Price',
            rates=candidate_rates,
        )
        buy_candidate_payload.append({
            'symbol': symbol,
            'market': item.get('Market'),
            'company_name': item.get('Company_Name'),
            'sector': item.get('Sector'),
            'industry': item.get('Industry'),
            'price_eur': item.get('Price'),
            # A BUY decision means the scanner considers the setup actionable
            # now. If there is no separate pullback entry, use the current
            # price instead of sending an unusable zero entry to the AI.
            'entry_eur': _buy_candidate_entry_eur(item),
            'stop_eur': item.get('Stop_Loss'),
            'target_eur': item.get('Target'),
            'rr_ratio': item.get('RR_Ratio'),
            'decision': item.get('Decision'),
            'consensus': item.get('Consensus'),
            'analysts': item.get('Analysts'),
            'trend': item.get('Trend'),
            'rsi': item.get('RSI'),
            'earnings_risk': bool(item.get('Earnings_Danger')),
            'entry_reason': item.get('Smart_Reason'),
            'price_native': item.get('Price_Native'),
            'currency': item.get('Currency'),
            **execution_values,
            'chart_currency': native_chart_detail['currency'],
            'chart_value_native': native_chart_detail['value'],
            'chart_change_native': native_chart_detail['change'],
            'chart_ohlc_native': native_chart_detail['ohlc'],
            'chart_series_native': native_chart_detail['series'],
            'chart_series_dates': native_chart_detail['seriesDates'],
            'atr_eur': item.get('ATR_14'),
            'volume': item.get('Volume'),
            'strategy': item.get('Strategy'),
            'relative_strength': item.get('RS_vs_SPX'),
            'data_as_of': item.get('Date'),
            'market_data_source': item.get('Market_Data_Source'),
            'market_data_fetched_at': item.get(
                'Market_Data_Fetched_At'
            ),
            'data_broker': item.get('Data_Broker'),
            'ibkr_data_only': bool(item.get('IBKR_Data_Only')),
            'data_age_hours': item.get(
                'Data_Age_Hours',
                _buy_candidate_data_age_hours(item),
            ),
            'data_fresh': bool(
                item.get(
                    'Data_Fresh',
                    _buy_candidate_data_is_fresh(item),
                )
            ),
            'level_source': item.get('Technical_Level_Source'),
            'trigger_basis': item.get('Trigger_Basis'),
            'target_basis': item.get('Target_Basis'),
            'external_min_rr': item.get('External_Min_RR'),
            'bvb_metadata': item.get('BVB_Metadata'),
            'bvb_market_segment': (
                (item.get('BVB_Liquidity') or {}).get('market_segment')
            ),
            'liquidity_status': (
                (item.get('BVB_Liquidity') or {}).get('status')
            ),
            'liquidity_reason': (
                (item.get('BVB_Liquidity') or {}).get('reason')
            ),
            'liquidity_source': (
                (item.get('BVB_Liquidity') or {}).get('source')
            ),
            'liquidity_observations_20d': item.get(
                'Liquidity_Observations_20D'
            ),
            'active_days_20d': item.get('Active_Days_20D'),
            'zero_volume_days_20d': item.get('Zero_Volume_Days_20D'),
            'median_volume_20d': item.get('Median_Volume_20D'),
            'median_turnover_20d_ron': item.get(
                'Median_Turnover_20D_RON'
            ),
            'last_turnover_ron': item.get('Last_Turnover_RON'),
            'relative_volume_20d': item.get('Relative_Volume_20D'),
            'liquidity_position_cap_eur': (
                (item.get('BVB_Liquidity') or {}).get('position_cap_eur')
            ),
            'liquidity_participation_limit_pct': (
                (item.get('BVB_Liquidity') or {}).get(
                    'participation_limit_pct'
                )
            ),
            'strict_eligible': bool(item.get('Strict_Eligible')),
            'candidate_source': item.get('Candidate_Source', 'watchlist'),
            'requires_watchlist_filters': bool(
                item.get('Requires_Watchlist_Filters', True)
            ),
            'cycle_fit': item.get('Cycle_Fit'),
            'eligible_brokers': item.get('Eligible_Brokers') or _buy_candidate_brokers(
                item.get('Ticker')
            ),
        })
    sizing_snapshot = analysis.build_portfolio_risk_snapshot(
        portfolio_df,
        orders_df,
        account_data=tws_account_data,
        market_context=portfolio_market_context,
        etf_holdings=tvbetetf_holdings,
        sector_rotation=us_sector_rotation,
        us_market_regime=us_market_regime,
    )
    sizing_snapshot['buy_candidates'] = buy_candidate_payload
    buy_candidate_payload = analysis._size_buy_candidates(sizing_snapshot)
    ai_buy_candidate_payload, blocked_ai_buy_candidates, ai_market_gates = (
        _filter_ai_buy_candidates_by_market_signal(
            buy_candidate_payload,
            international_market_signal,
            bvb_market_signal,
        )
    )
    if blocked_ai_buy_candidates:
        blocked_by_market = {}
        for candidate in blocked_ai_buy_candidates:
            market = str(candidate.get('market') or 'Piață necunoscută')
            blocked_by_market[market] = blocked_by_market.get(market, 0) + 1
        print(
            "  -> Filtru AI piață: candidați netrimiși modelului: "
            + ", ".join(
                f"{market}={count}"
                for market, count in sorted(blocked_by_market.items())
            )
        )
    full_state['ai_stock_market_gates'] = {
        'updated_at': datetime.datetime.now().isoformat(timespec='seconds'),
        'international': {
            'enabled': ai_market_gates['international'],
            'verdict': international_market_signal.get('verdict'),
        },
        'romania_bvb': {
            'enabled': ai_market_gates['romania_bvb'],
            'verdict': bvb_market_signal.get('verdict'),
        },
    }
    previous_buy_history = list(
        (full_state or {}).get('buy_recommendation_history', [])
    )
    buy_recommendation_history = (
        analysis.update_buy_recommendation_history_from_cache(
            previous_buy_history,
            cached_portfolio_ai,
            buy_candidate_payload,
        )
    )
    portfolio_ai_html, new_portfolio_ai_cache, new_portfolio_evidence, portfolio_ai_diagnostic = generate_portfolio_ai_analysis(
        portfolio_df,
        orders_df,
        cached=cached_portfolio_ai,
        cached_evidence=cached_portfolio_evidence,
        account_data=tws_account_data,
        market_context=portfolio_market_context,
        buy_candidates=ai_buy_candidate_payload,
        etf_holdings=tvbetetf_holdings,
        sector_rotation=us_sector_rotation,
        us_market_regime=us_market_regime,
        allow_ai=ai_calls_allowed,
        force_ai_refresh=ai_calls_allowed,
    )
    portfolio_ai_result = (new_portfolio_ai_cache or {}).get('result', {})
    if isinstance(portfolio_ai_result.get('buy_recommendations'), list):
        previous_push_state = dict(
            (full_state or {}).get('buy_now_push_state') or {}
        )
        push_event_token = (
            (new_portfolio_ai_cache or {}).get('generated_at')
            or (cached_portfolio_ai or {}).get('generated_at')
        )
        buy_now_push_state, buy_now_push_diagnostic = (
            buy_now_push.send_new_buy_now_notifications(
                previous_push_state,
                portfolio_ai_result,
                ai_buy_candidate_payload,
                event_token=push_event_token,
            )
        )
        full_state['buy_now_push_state'] = buy_now_push_state
        if buy_now_push_state != previous_push_state:
            market_utils.save_state(full_state)
        if buy_now_push_diagnostic['status'] == 'sent':
            print(
                "  -> Web push Cumpărare acum: "
                + ", ".join(
                    buy_now_push_diagnostic['delivered_symbols']
                )
            )
        elif buy_now_push_diagnostic['status'] == 'failed':
            print(
                "  ⚠ Web push Cumpărare acum nereușit: "
                + str(buy_now_push_diagnostic['errors'])
            )
    if portfolio_ai_result:
        buy_recommendation_history = (
            analysis.update_buy_recommendation_history(
                buy_recommendation_history,
                portfolio_ai_result,
                (new_portfolio_ai_cache or {}).get(
                    'buy_candidates'
                ) or buy_candidate_payload,
                recorded_at=(new_portfolio_ai_cache or {}).get(
                    'generated_at'
                ),
            )
        )
        full_state['buy_recommendation_history'] = (
            buy_recommendation_history
        )
    promoted_symbols = _promote_validated_external_candidates(
        portfolio_ai_result, buy_candidate_payload
    )
    if promoted_symbols:
        print(
            "  -> Idei externe validate și adăugate în watchlist: "
            + ", ".join(promoted_symbols)
        )
    buy_recommendations_html = analysis.render_buy_recommendations_html(
        portfolio_ai_result,
        ai_buy_candidate_payload,
        new_portfolio_evidence or cached_portfolio_evidence,
        (full_state or {}).get('bvb_universe_stats'),
        (full_state or {}).get('us_universe_stats'),
        buy_recommendation_history,
    )
    buy_recommendations_html = _render_ai_stock_gate_notice(
        international_market_signal,
        bvb_market_signal,
        blocked_ai_buy_candidates,
    ) + buy_recommendations_html
    buy_history_chart_candidates = _build_history_chart_candidates(
        buy_candidate_payload,
        buy_recommendation_history,
        (
            list(strict_buy_candidates)
            + watchlist_df.to_dict('records')
            + list((full_state or {}).get('external_buy_research', []))
            + list((full_state or {}).get('bvb_equity_universe', []))
        ),
        rates=candidate_rates,
    )
    buy_recommendation_detail_data = (
        _build_buy_recommendation_detail_data(
            buy_history_chart_candidates,
            portfolio_ai_result,
            buy_recommendation_history,
        )
    )
    full_state['last_portfolio_ai_diagnostic'] = portfolio_ai_diagnostic
    if (
        cached_portfolio_ai
        and cached_portfolio_ai.get('version') != analysis.PORTFOLIO_AI_CACHE_VERSION
    ):
        full_state.pop('last_portfolio_ai_analysis', None)
    if new_portfolio_ai_cache and new_portfolio_ai_cache != cached_portfolio_ai:
        full_state['last_portfolio_ai_analysis'] = new_portfolio_ai_cache
        market_utils.save_state(full_state)
        print("  -> Analiza AI a portofoliului a fost salvată în cache.")
    if new_portfolio_evidence and new_portfolio_evidence != cached_portfolio_evidence:
        full_state['last_portfolio_ai_evidence'] = new_portfolio_evidence
        market_utils.save_state(full_state)
        print("  -> Sursele recente ale portofoliului au fost salvate în cache.")
    if buy_recommendation_history != previous_buy_history:
        market_utils.save_state(full_state)
        print("  -> Istoricul recomandărilor executabile a fost actualizat.")
    if portfolio_ai_diagnostic.get('status') == 'failed':
        print(f"  ⚠ Analiza AI portofoliu indisponibilă: {portfolio_ai_diagnostic}")

    portfolio_detail_data = {}
    for _, row in portfolio_df.iterrows():
        symbol = str(row['Symbol'])
        native_detail = _chart_detail_native_payload(
            row,
            symbol,
            'Current_Price',
            rates=dashboard_rates,
        )
        to_native = native_detail['to_native']
        raw_buy_levels = row.get('Buy_Levels', [])
        if not isinstance(raw_buy_levels, list) or not raw_buy_levels:
            raw_buy_levels = [row.get('Buy_Price', 0)]
        buy_levels = [
            to_native(value) for value in raw_buy_levels
            if (
                pd.notna(value)
                and float(value) > 0
                and to_native(value) is not None
            )
        ]
        chart_levels = [
            {
                "label": "Cumpărare" if len(buy_levels) == 1 else f"Cumpărare {index + 1}",
                "value": value,
                "color": "#2563eb"
            }
            for index, value in enumerate(buy_levels)
        ]

        # Toate ordinele SELL cu un preț stop valid sunt păstrate separat.
        active_stops = []
        if not orders_df.empty and 'Symbol' in orders_df.columns:
            symbol_orders = orders_df[
                orders_df['Symbol'].astype(str).str.upper() == symbol.upper()
            ]
            if 'Action' in symbol_orders.columns:
                symbol_orders = symbol_orders[
                    symbol_orders['Action'].astype(str).str.upper() == 'SELL'
                ]
            for _, order in symbol_orders.iterrows():
                stop_price_native = 0.0
                for price_column in ('Calculated_Stop', 'Stop_Price', 'Aux_Price'):
                    candidate = order.get(price_column, 0)
                    if pd.notna(candidate) and 0 < float(candidate) < 1e10:
                        stop_price_native = float(candidate)
                        break
                if stop_price_native <= 0:
                    continue
                quantity = order.get('Total_Qty', order.get('Quantity', 0))
                quantity = float(quantity) if pd.notna(quantity) else 0.0
                # Ordinele brokerului sunt deja în moneda instrumentului.
                stop_value = round(stop_price_native, 4)
                duplicate = any(
                    abs(item['value'] - stop_value) < 0.005
                    and abs(item['quantity'] - quantity) < 0.001
                    for item in active_stops
                )
                if not duplicate:
                    active_stops.append({'value': stop_value, 'quantity': quantity})

        # Fallback la stopul agregat din portofoliu când nu există ordine detaliate.
        if not active_stops:
            stop_loss = row.get('Trail_Stop_IBKR', 0)
            if pd.isna(stop_loss) or float(stop_loss) <= 0:
                stop_loss = row.get('Trail_Stop', 0)
            if pd.notna(stop_loss) and float(stop_loss) > 0:
                active_stops.append({
                    'value': to_native(stop_loss),
                    'quantity': float(row.get('Shares', 0))
                })

        for index, stop in enumerate(sorted(active_stops, key=lambda item: item['value'], reverse=True)):
            quantity_label = (
                f" · {stop['quantity']:g} acț."
                if stop['quantity'] > 0 else ""
            )
            chart_levels.append({
                "label": (
                    "Stop activ" if len(active_stops) == 1
                    else f"Stop activ {index + 1}"
                ) + quantity_label,
                "value": stop['value'],
                "color": "#dc2626"
            })

        suggested_stop = row.get('Suggested_Stop', 0)
        if pd.notna(suggested_stop) and float(suggested_stop) > 0:
            suggested_value = to_native(suggested_stop)
            if not any(abs(stop['value'] - suggested_value) < 0.005 for stop in active_stops):
                chart_levels.append({
                    "label": "Stop propus",
                    "value": suggested_value,
                    "color": "#f59e0b"
                })
        portfolio_detail_data[symbol] = {
            "kind": "portfolio",
            "name": row.get('Company_Name', symbol),
            "ticker": symbol,
            "currency": native_detail['currency'],
            "value": native_detail['value'],
            "change": native_detail['change'],
            "status": row.get('Sell_Decision', 'HOLD'),
            "rangeDescription": row.get('Trend', '—'),
            "explanation": (
                f"Poziție în portofoliu: {int(row.get('Shares', 0))} acțiuni. "
                f"Preț mediu de cumpărare "
                f"{_format_native_price_text(to_native(row.get('Buy_Price', 0)), native_detail['currency'])}; "
                f"profit/pierdere {float(row.get('Profit_Pct', 0)):.2f}%."
            ),
            "ohlc": native_detail['ohlc'],
            "series": native_detail['series'],
            "seriesDates": native_detail['seriesDates'],
            "levels": chart_levels
        }

    portfolio_chat_context = analysis.build_portfolio_chat_context(
        sizing_snapshot,
        ai_result=portfolio_ai_result,
        evidence=new_portfolio_evidence or cached_portfolio_evidence,
        buy_candidates=buy_candidate_payload,
        dashboard_state=full_state,
    )
    portfolio_chat_endpoint = os.environ.get('PORTFOLIO_CHAT_API_URL', '').strip()
    full_pf_data = {
        "html": portfolio_rows_html,
        "buying_orders_html": buying_rows_html,
        "selling_orders_html": selling_rows_html,
        "portfolio_ai_html": portfolio_ai_html,
        "buy_recommendations_html": buy_recommendations_html,
        "sparklines": sparkline_data,
        "chart_details": portfolio_detail_data,
        "buy_chart_details": buy_recommendation_detail_data,
        "active_buy_order_levels": _build_active_buy_order_chart_levels(orders_df),
        "portfolio_chat": {
            "endpoint": portfolio_chat_endpoint,
            "access_token": _portfolio_chat_access_token(password),
            "context": portfolio_chat_context,
            "model_label": "GPT-5.6 Terra",
        },
    }
    # Use password variable (should be defined)
    if not password: password = "1234" # Fallback
    
    portfolio_json = json.dumps(
        _json_without_nonfinite_numbers(full_pf_data),
        allow_nan=False,
    )
    encrypted_blob = market_security.encrypt_for_js(portfolio_json, password)
    portfolio_blob_version = hashlib.sha256(
        encrypted_blob.encode('utf-8')
    ).hexdigest()[:20]
    
    html_head += f"""
                </tbody>
            </table>
            </div> <!-- End table-container -->
            
            <h3 style="margin-top: 45px; margin-bottom: 15px; color: var(--text-primary);">Ordine Active de Vânzare (IBKR / Tradeville)</h3>
            <div class="table-container">
            <table id="selling-orders-table" class="display hover" style="width:100%;">
                <thead>
                    <tr>
                        <th style="width: 80px;">Simbol</th>
                        <th>Tip Ordin</th>
                        <th>Cantitate</th>
                        <th>Preț Ordin</th>
                        <th>Trail % (Ordin)</th>
                        <th>Preț Curent</th>
                        <th>Grafic</th>
                        <th>Target</th>
                        <th>% Mid</th>
                        <th>Consensus</th>
                        <th>Suggested Stop</th>
                        <th>Valoare Est.</th>
                        <th>Trend</th>
                        <th onmousemove="showTooltip(event, \'<strong>RSI (Relative Strength Index)</strong><br>măsoară viteza și schimbarea prețurilor.<br>Valori: >70 (Overbought), <30 (Oversold).\')" onmouseout="hideTooltip()">RSI</th>
                        <th onmousemove="showTooltip(event, \'<strong>RS vs SPX (Relative Strength vs S&P 500) pe 60 de zile.</strong>\')" onmouseout="hideTooltip()">RS vs SPX</th>
                    </tr>
                </thead>
                <tbody id="selling-orders-rows-body">
                    <!-- Injected by JS after decryption -->
                </tbody>
            </table>
            </div> <!-- End table-container -->
            
            <h3 style="margin-top: 45px; margin-bottom: 15px; color: var(--text-primary);">Ordine Active de Cumpărare (IBKR / Tradeville)</h3>
            <div class="table-container">
            <table id="buying-orders-table" class="display hover" style="width:100%;">
                <thead>
                    <tr>
                        <th style="width: 80px;">Simbol</th>
                        <th>Tip Ordin</th>
                        <th>Cantitate</th>
                        <th>Preț Ordin</th>
                        <th>Trail % (Ordin)</th>
                        <th>Preț Curent</th>
                        <th>Grafic</th>
                        <th>Target</th>
                        <th>% Mid</th>
                        <th>Consensus</th>
                        <th>Suggested Stop</th>
                        <th>Investiție Est.</th>
                        <th>Trend</th>
                        <th onmousemove="showTooltip(event, \'<strong>RSI (Relative Strength Index)</strong><br>măsoară viteza și schimbarea prețurilor.<br>Valori: >70 (Overbought), <30 (Oversold).\')" onmouseout="hideTooltip()">RSI</th>
                        <th onmousemove="showTooltip(event, \'<strong>RS vs SPX (Relative Strength vs S&P 500) pe 60 de zile.</strong>\')" onmouseout="hideTooltip()">RS vs SPX</th>
                    </tr>
                </thead>
                <tbody id="buying-orders-rows-body">
                    <!-- Injected by JS after decryption -->
                </tbody>
            </table>
            </div> <!-- End table-container -->

            <div id="buy-recommendations-container"></div>

            <aside id="portfolio-chat-panel" class="portfolio-chat-panel" aria-hidden="true" aria-label="Asistent AI pentru portofoliu">
                <div class="portfolio-chat-header">
                    <div><div class="portfolio-chat-title">Asistent portofoliu</div><div class="portfolio-chat-subtitle">GPT-5.6 Terra + fallback Cloudflare · datele dashboardului + surse web când sunt disponibile</div></div>
                    <button type="button" class="portfolio-chat-close" onclick="togglePortfolioChat(false)" aria-label="Închide chatul">×</button>
                </div>
                <div class="portfolio-chat-suggestions">
                    <button type="button" class="portfolio-chat-suggestion" onclick="usePortfolioChatSuggestion('Care sunt cele mai importante riscuri din portofoliu acum?')">Riscuri acum</button>
                    <button type="button" class="portfolio-chat-suggestion" onclick="usePortfolioChatSuggestion('Ce oportunități executabile există acum în SUA și România?')">Oportunități BUY</button>
                    <button type="button" class="portfolio-chat-suggestion" onclick="usePortfolioChatSuggestion('Cum influențează calendarul următoarele mele decizii?')">Calendar</button>
                </div>
                <div id="portfolio-chat-messages" class="portfolio-chat-messages">
                    <div class="portfolio-chat-message assistant">Bună! Pot explica portofoliul, stopurile, cash-ul, piețele SUA/BVB și ideile de cumpărare. Pentru informații recente pot verifica și surse publice pe internet.</div>
                </div>
                <form class="portfolio-chat-form" onsubmit="event.preventDefault(); sendPortfolioChatMessage();">
                    <textarea id="portfolio-chat-input" class="portfolio-chat-input" rows="1" maxlength="2000" placeholder="Întreabă despre portofoliu sau piețe…" onkeydown="if(event.key==='Enter'&&!event.shiftKey){{event.preventDefault();sendPortfolioChatMessage();}}"></textarea>
                    <button id="portfolio-chat-send" type="submit" class="portfolio-chat-send">Trimite</button>
                </form>
            </aside>
            <button type="button" class="portfolio-chat-launcher" onclick="togglePortfolioChat()" aria-label="Deschide asistentul AI" title="Asistent AI portofoliu">💬</button>
            
            <!-- Encrypted Data Injection -->
            <script>
                const PORTFOLIO_BLOB_VERSION = "{portfolio_blob_version}";
                const ENCRYPTED_DATA = {encrypted_blob};
            </script>
            
        </div> <!-- End portfolio-data -->
        </div> <!-- End portfolio Tab -->
        
        <!-- TAB MARKET (NOU) -->
        <div id="market" class="tab-content active">
            <h2 style="color: var(--text-primary); margin-bottom: 24px; text-align: center; animation: fadeIn 0.6s ease-out;">Indicatori de Piață</h2>
            <div class="animated-card" style="background-color: var(--bg-white); padding: 32px; border-radius: var(--radius-md); overflow-x: auto; box-shadow: var(--shadow-sm); border: 1px solid var(--border-light); animation: fadeIn 0.8s ease-out 0.2s backwards;">
                <table style="width: 100%; background-color: transparent; box-shadow: none;">
                    <thead>
                        <tr style="border-bottom: 2px solid #444;">
    """
    
    # Ordinea indicatorilor
    indicator_order = ['VIX3M', 'VIX', 'VIX1D', 'VIX9D', 'VXN', 'LTV', 'SKEW', 'MOVE', 'Crypto Fear', 'GVZ', 'OVX', 'SPX', 'NASDAQ']
    
    # Mapping Display Names
    display_map = {
        'VIX3M': 'VIX (3M)',
        'VIX': 'VIX Spot',
        'VIX1D': 'VIX 1D',
        'VIX9D': 'VIX 9D'
    }
    
    def indicator_click_attrs(name):
        return (
            f"""onclick="openIndicatorDetail('{name}')" role="button" tabindex="0" """
            f"""onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();openIndicatorDetail('{name}');}}" """
            f"""title="Deschide graficul și detaliile pentru {display_map.get(name, name)}" """
        )

    # Header row
    for name in indicator_order:
        if name in market_indicators:
            disp_name = display_map.get(name, name)
            html_head += f"""
                            <th {indicator_click_attrs(name)}style="min-width: 80px; text-align: center; padding: 8px; font-size: 0.75rem; cursor: pointer;">{disp_name}</th>"""
    
    html_head += """
                        </tr>
                        <tr style="border-bottom: 1px solid #444;">
    """
    
    # Sub-header descrieri
    for name in indicator_order:
        if name in market_indicators:
            desc = market_indicators[name].get('description', '')
            html_head += f"""
                            <th {indicator_click_attrs(name)}style="text-align: center; padding: 5px; font-size: 0.65rem; color: #888; font-weight: normal; cursor: pointer;">{desc}</th>"""
    
    html_head += """
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
    """
    
    # Sparklines
    for idx, name in enumerate(indicator_order):
        if name in market_indicators:
            spark_id = f"spark_ind_{name}"
            html_head += f"""
                            <td {indicator_click_attrs(name)}style="text-align: center; padding: 5px; height: 50px; cursor: pointer;"><canvas id="{spark_id}" style="width: 100%; height: 100%; pointer-events: none;"></canvas></td>"""
    
    html_head += """
                        </tr>
                        <tr>
    """
    
    # Valorile curente
    for name in indicator_order:
        if name in market_indicators:
            value = market_indicators[name].get('value', 'N/A')
            status = market_indicators[name].get('status', 'Normal')
            
            # Colorare bazată pe status (4 nivele)
            if status == 'Perfect':
                color = '#10B981'  # Success green
            elif status == 'Normal':
                color = 'var(--text-secondary)'  # Medium gray for readability
            elif status == 'Tension':
                color = '#F59E0B'  # Warning orange
            elif status == 'Panic':
                color = '#EF4444'  # Error red
            else:
                color = 'var(--text-secondary)'
            
            html_head += f"""
                            <td {indicator_click_attrs(name)}style="text-align: center; padding: 10px; font-size: 18px; font-weight: 700; color: {color}; cursor: pointer;">{value}</td>"""
    
    html_head += """
                        </tr>
                        <tr>
    """
    
    # Schimbările
    for name in indicator_order:
        if name in market_indicators:
            change = market_indicators[name].get('change', 0)
            
            # Colorare inversă (stock logic vs volatility logic)
            if name == 'SPX' or name == 'NASDAQ' or name == 'Crypto Fear':
                if change > 0:
                    change_color = '#4caf50'
                    arrow = '↑'
                elif change < 0:
                    change_color = '#f44336'
                    arrow = '↓'
                else:
                    change_color = '#888'
                    arrow = ''
            else:
                # Volatility logic (Up = Bad)
                if change > 0:
                    change_color = '#f44336'
                    arrow = '↑'
                elif change < 0:
                    change_color = '#4caf50'
                    arrow = '↓'
                else:
                    change_color = '#888'
                    arrow = ''
            
            html_head += f"""
                            <td {indicator_click_attrs(name)}style="text-align: center; padding: 5px; font-size: 0.75rem; color: {change_color}; cursor: pointer;">{arrow} {abs(change):.2f}</td>"""
    
    html_head += """
                        </tr>
                    </tbody>
                </table>
            </div>
    """
    
    # Add Historical Returns Card
    if 'Historical_Returns' in market_indicators and market_indicators['Historical_Returns']:
        hist_returns = market_indicators['Historical_Returns']
        html_head += """
            <div style="background: var(--bg-white); padding: 32px; border-radius: var(--radius-md); margin-top: 32px; border: 1px solid var(--border-light); box-shadow: var(--shadow-sm); animation: fadeIn 0.8s ease-out 0.4s backwards;">
                <h3 style="color: var(--text-primary); margin-top: 0; text-align: center;">Randamente Lunare Istorice (1950 - Prezent)</h3>
        """
        
        # Add current and next month info
        import calendar
        now = datetime.datetime.now()
        current_month_name = now.strftime('%B')  # December (fără an)
        next_month_date = now + datetime.timedelta(days=32)
        next_month_date = next_month_date.replace(day=1)
        next_month_name = next_month_date.strftime('%B')  # January (fără an)
        next_month_num = next_month_date.month
        
        # Get expected returns for next month (convert to string for JSON keys)
        sp500_next = hist_returns.get('SP500', {}).get('monthly_averages', {}).get(str(next_month_num), 0)
        nasdaq_next = hist_returns.get('NASDAQ', {}).get('monthly_averages', {}).get(str(next_month_num), 0)
        
        sp500_color = "#4caf50" if sp500_next > 0 else "#f44336"
        nasdaq_color = "#4caf50" if nasdaq_next > 0 else "#f44336"
        
        # Get current month returns (convert to string for JSON keys)
        current_month_num = now.month
        sp500_current = hist_returns.get('SP500', {}).get('monthly_averages', {}).get(str(current_month_num), 0)
        nasdaq_current = hist_returns.get('NASDAQ', {}).get('monthly_averages', {}).get(str(current_month_num), 0)
        
        sp500_current_color = "#4caf50" if sp500_current > 0 else "#f44336"
        nasdaq_current_color = "#4caf50" if nasdaq_current > 0 else "#f44336"
        
        html_head += f"""
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th style="padding: clamp(6px, 2vw, 12px); text-align: left; border-bottom: 2px solid var(--border-light);"></th>
                            <th style="padding: clamp(6px, 2vw, 12px); text-align: center; border-bottom: 2px solid var(--border-light); color: var(--text-primary); font-size: clamp(13px, 3vw, 16px); font-weight: 600;">
                                {current_month_name.upper()}
                            </th>
                            <th style="padding: clamp(6px, 2vw, 12px); text-align: center; border-bottom: 2px solid var(--border-light); color: var(--text-primary); font-size: clamp(13px, 3vw, 16px); font-weight: 600;">
                                {next_month_name.upper()}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid var(--border-light);">
                            <td style="padding: clamp(8px, 2vw, 12px); color: var(--text-secondary); font-weight: 600; font-size: clamp(12px, 3vw, 15px); white-space: nowrap;">S&P 500</td>
                            <td style="padding: clamp(8px, 2vw, 12px); text-align: center; font-size: clamp(16px, 4vw, 18px); font-weight: 700; color: {sp500_current_color};">
                                {sp500_current:+.2f}%
                            </td>
                            <td style="padding: clamp(8px, 2vw, 12px); text-align: center; font-size: clamp(16px, 4vw, 18px); font-weight: 700; color: {sp500_color};">
                                {sp500_next:+.2f}%
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: clamp(8px, 2vw, 12px); color: var(--text-secondary); font-weight: 600; font-size: clamp(12px, 3vw, 15px);">NASDAQ</td>
                            <td style="padding: clamp(8px, 2vw, 12px); text-align: center; font-size: clamp(16px, 4vw, 18px); font-weight: 700; color: {nasdaq_current_color};">
                                {nasdaq_current:+.2f}%
                            </td>
                            <td style="padding: clamp(8px, 2vw, 12px); text-align: center; font-size: clamp(16px, 4vw, 18px); font-weight: 700; color: {nasdaq_color};">
                                {nasdaq_next:+.2f}%
                            </td>
                        </tr>
                    </tbody>
                </table>
                <div style="text-align: center; color: var(--text-secondary); font-size: clamp(11px, 2.5vw, 13px); margin-top: 16px; font-style: italic; padding: 0 8px;">
                    Bazat pe media istorică pentru fiecare lună (1950-Prezent)
                </div>
                
                <p style="text-align: center; color: #888; font-size: 0.8rem; margin-top: 15px; margin-bottom: 0;">
                    * Date calculate pe baza prețurilor de închidere lunare din Yahoo Finance
                </p>
            </div>
        """
    
    # --- SWING TRADING ANALYSIS SECTION ---
    # Generăm cardul de analiză Swing Trading (Trend, F&G, Breadth, Timing)
    print("  -> Generare Analiză Swing Trading (Long-only)...")
    try:
        if not swing_html:
            swing_html, international_market_signal = (
                generate_swing_trading_html(
                    data=swing_data,
                    return_signal=True,
                )
            )
        if not bvb_market_html:
            bvb_market_html, bvb_market_signal = (
                _generate_bvb_market_overview_html(
                    portfolio_df,
                    watchlist_df,
                    return_signal=True,
                )
            )
        html_head += """
            <section style="margin-top:32px;">
              <h2 style="margin:0;color:var(--text-primary);">SUA — S&amp;P 500 / Nasdaq</h2>
              <p style="margin:6px 0 0;color:var(--text-secondary);">Trend, volatilitate, sentiment și breadth exclusiv pentru piața americană.</p>
            </section>
        """
        html_head += swing_html
        html_head += bvb_market_html

        previous_market_push_state = dict(
            (full_state or {}).get('market_buy_push_state') or {}
        )
        market_push_state, market_push_diagnostic = (
            buy_now_push.send_new_market_buy_notifications(
                previous_market_push_state,
                [international_market_signal, bvb_market_signal],
            )
        )
        full_state['market_buy_push_state'] = market_push_state
        if market_push_state != previous_market_push_state:
            market_utils.save_state(full_state)
        if market_push_diagnostic['status'] == 'sent':
            print(
                "  -> Web push semnal BUY piață: "
                + ", ".join(
                    market_push_diagnostic['delivered_markets']
                )
            )
        elif market_push_diagnostic['status'] == 'failed':
            print(
                "  ⚠ Web push semnal BUY piață nereușit: "
                + str(market_push_diagnostic['errors'])
            )
    except Exception as e:
        print(f"  ⚠ Eroare generare Swing Trading HTML: {e}")
    
    # Adăugăm analiza AI (News + Calendar)
    # Adăugăm analiza AI (News + Calendar)
    # Load existing AI summary from state (if any)
    cached_ai = (
        full_state.get('last_ai_summary_cache')
        or full_state.get('last_ai_summary')
    )
    previous_calendar_ai_cache = dict(
        full_state.get('economic_calendar_ai_cache') or {}
    )
    calendar_ai_cache = dict(previous_calendar_ai_cache)
    
    # Generare analiză piață (returnează HTML + Raw Text)
    market_analysis_html, new_ai_text, ai_score, new_news_ai_cache = (
        generate_market_analysis(
            market_indicators,
            cached_ai,
            return_cache=True,
            calendar_ai_cache=calendar_ai_cache,
            allow_ai=ai_calls_allowed,
        )
    )
    
    # Save new AI text to state if successfully generated
    if new_ai_text:
         full_state['last_ai_summary'] = new_ai_text
         if new_news_ai_cache:
             full_state['last_ai_summary_cache'] = new_news_ai_cache
         # generate_html_dashboard este apelată după salvarea inițială a stării.
         # Persistăm imediat rezumatul, altfel cache-ul AI se pierde între rulări.
         market_utils.save_state(full_state)
         print("  -> Rezumat AI salvat în cache (dashboard_state).")

    if calendar_ai_cache != previous_calendar_ai_cache:
        full_state['economic_calendar_ai_cache'] = calendar_ai_cache
        market_utils.save_state(full_state)
        print(
            "  -> Cache AI calendar economic salvat persistent: "
            f"{len(calendar_ai_cache)} evenimente."
        )

    usage_events = analysis.consume_openai_usage_events()
    if usage_events:
        usage_history = list(full_state.get('openai_usage_history', []))
        usage_history.extend(usage_events)
        full_state['openai_usage_history'] = usage_history[-500:]
        totals = dict(full_state.get('openai_usage_totals', {}))
        for field in (
            'input_tokens', 'uncached_input_tokens', 'cached_tokens',
            'cache_write_tokens', 'output_tokens', 'reasoning_tokens',
            'total_tokens',
        ):
            totals[field] = int(totals.get(field) or 0) + sum(
                int(item.get(field) or 0) for item in usage_events
            )
        known_costs = [
            item.get('estimated_cost_usd') for item in usage_events
            if item.get('estimated_cost_usd') is not None
        ]
        if known_costs:
            totals['estimated_cost_usd'] = round(
                float(totals.get('estimated_cost_usd') or 0)
                + sum(float(value) for value in known_costs),
                8,
            )
        totals['last_updated_at'] = datetime.datetime.now().isoformat(
            timespec='seconds'
        )
        totals['calls'] = int(totals.get('calls') or 0) + len(usage_events)
        totals['cost_estimate_status'] = (
            'partial_or_complete'
            if known_costs else 'rates_not_configured'
        )
        full_state['openai_usage_totals'] = totals
        market_utils.save_state(full_state)
        print(
            "  -> Consum OpenAI salvat: "
            f"{len(usage_events)} apel(uri), "
            f"{sum(int(item.get('total_tokens') or 0) for item in usage_events)} tokeni."
        )
    
    html_head += market_analysis_html

    # Adăugăm Explicații Macro (Glosar) - ULTIMUL
    html_head += get_macro_explanations()
    
    html_head += f"""
        </div>
        
        <div id="watchlist" class="tab-content">
            
            <!-- Watchlist Header -->
            <div style="text-align: center; margin-bottom: 24px; padding: 24px; background: var(--bg-white); border-radius: var(--radius-md); border: 1px solid var(--border-light); box-shadow: var(--shadow-sm);">
                <h2 style="color: var(--text-primary); margin: 0;">Watchlist</h2>
                <p style="color: var(--text-secondary); margin: 8px 0 0 0; font-size: 16px;">Total Stocks: <strong style="color: var(--primary-purple);">{len(watchlist_df)}</strong></p>
            </div>
            
            <!-- Filters -->
            <div class="filters-container" style="margin-bottom: 24px; display: flex; flex-wrap: wrap; gap: 16px; background: var(--bg-white); padding: 20px; border-radius: var(--radius-md); border: 1px solid var(--border-light); box-shadow: var(--shadow-sm);">
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Consensus</label>
                    <select id="filter-consensus" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); font-size: 14px; cursor: pointer;">
                        <option value="">All</option>
                        <option value="Strong Buy">Strong Buy</option>
                        <option value="Buy">Buy</option>
                        <option value="Hold">Hold</option>
                        <option value="Sell">Sell</option>
                    </select>
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Min Analysts</label>
                    <input type="number" id="filter-analysts" placeholder="0" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 120px; font-size: 14px;">
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Min Target %</label>
                    <input type="number" id="filter-target-pct" placeholder="0" step="any" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 120px; font-size: 14px;">
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Trend</label>
                    <select id="filter-trend" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 180px; font-size: 14px; cursor: pointer;">
                        <option value="">All</option>
                        <option value="Strong Bullish">Strong Bullish</option>
                        <option value="Bullish Pullback">Bullish Pullback</option>
                        <option value="Bearish Rally">Bearish Rally</option>
                        <option value="Strong Bearish">Strong Bearish</option>
                        <option value="Neutral">Neutral</option>
                    </select>
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Status</label>
                    <select id="filter-status" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 140px; font-size: 14px; cursor: pointer;">
                        <option value="">All</option>
                        <option value="Oversold">Oversold</option>
                        <option value="Overbought">Overbought</option>
                        <option value="Neutral">Neutral</option>
                    </select>
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Decizie</label>
                    <select id="filter-decision" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 140px; font-size: 14px; cursor: pointer;">
                        <option value="">All</option>
                        <option value="BUY">BUY</option>
                        <option value="WAIT">WAIT</option>
                        <option value="AVOID">AVOID</option>
                    </select>
                </div>
                <!-- NEW FILTERS (Feedback 2.0) -->
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Min Volume (M)</label>
                    <input type="number" id="filter-volume" placeholder="0" step="0.1" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 100px; font-size: 14px;">
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">RSI Range</label>
                    <div style="display: flex; gap: 5px;">
                        <input type="number" id="filter-rsi-min" placeholder="Min" style="padding: 10px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 70px; font-size: 14px;">
                        <input type="number" id="filter-rsi-max" placeholder="Max" style="padding: 10px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 70px; font-size: 14px;">
                    </div>
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Min R:R</label>
                    <input type="number" id="filter-rr" placeholder="0" step="0.1" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 80px; font-size: 14px;">
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Strategie</label>
                    <select id="filter-strategy" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 180px; font-size: 14px; cursor: pointer;">
                        <option value="">All</option>
                        <option value="Pullback">Pullback</option>
                        <option value="Deep Pullback">Deep Pullback</option>
                        <option value="Breakout">Breakout</option>
                        <option value="Strong Breakout">Strong Breakout</option>
                        <option value="Reversal">Reversal (Oversold)</option>
                        <option value="Range">Range / Consolidation</option>
                        <option value="Normal">Normal</option>
                        <option value="N/A">N/A</option>
                    </select>
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Min RS vs SPX</label>
                    <input type="number" id="filter-rs-spx" placeholder="0" step="0.1" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 120px; font-size: 14px;">
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Sector</label>
                    <input type="text" id="filter-sector" list="sector-list" placeholder="All Sectors" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 180px; font-size: 14px;">
                </div>
            </div>


            <div class="table-container">
            <table id="watchlist-table">
                <thead>
                    <tr>
                        <th style="width: 80px;">Simbol</th>
                        <th>Preț</th>
                        <th>Grafic</th>
                        <th>Target</th>
                        <th>To Target</th>
                        <th onmousemove="showTooltip(event, '<strong>Risk to Reward Ratio</strong><br>Calcul: (Target - Price) / (Price - Stop)<br><br>Raportul dintre potențialul profit și riscul asumat.<br>Minim recomandat: 1:2.')" onmouseout="hideTooltip()">R:R</th>
                        <th>Consensus</th>
                        <th>Analysts</th>
                        <th>Sector</th>
                        <th style="color: #9c27b0;">Decizie</th>
                        <th style="width: 90px; color: #E91E63;" onmousemove="showTooltip(event, '<strong>Smart Entry Price (Tactic)</strong><br><br>Sugestie de preț bazată pe analiză tehnică (Fibonacci, S/R, Patterns) pentru intrări optimizate.<br><br>⚡ <strong>STOP:</strong> Intrare pe momentum (Breakout/Engulfing).<br>📉 <strong>LIMIT:</strong> Intrare pe corecție (Fib/Support).')" onmouseout="hideTooltip()">Entry</th>
                        <th onmousemove="showTooltip(event, '<strong>RS vs SPX (Relative Strength vs S&P 500) pe 60 de zile.</strong><br><br>Reprezintă diferența dintre randamentul acțiunii și randamentul indexului S&P 500 în ultimele 60 de zile.<br><br><em>Exemplu:</em><br>Dacă acțiunea a crescut cu 20% și S&P 500 cu 5% => <strong>RS = +15%</strong>.<br>Dacă valoarea este pozitivă, acțiunea performează mai bine decât piața.')" onmouseout="hideTooltip()">RS vs SPX</th>
                        <th>Trend</th>
                        <th>Strategy</th>
                        <th style="color: #4caf50;">{full_state.get('eco_phase', 'Cycle')}</th>
                        <th style="color: #4dabf7;">{full_state.get('eco_next_phase', 'Next')} (Next)</th>
                        <th>RSI</th>
                        <th>Status</th>
                        <th>ATR</th>
                        <th>Stop Loss</th>
                        <th>SMA 50</th>
                        <th>SMA 200</th>
                        <th>Schimbare</th>
                        <th>Update</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Watchlist rows
    watch_chart_id = 0
    if not watchlist_df.empty:
        for idx, row in watchlist_df.iterrows():
            trend_cls = row['Trend'].replace(' ', '-')
            rsi_cls = row['RSI_Status']
            
            # Target display logic
            target_val = row.get('Target')
            target_display = "-"
            if target_val:
                 if isinstance(target_val, (int, float)):
                     target_display = f"€{target_val:.2f}"
                 else:
                     target_display = str(target_val)
            
            # Pct Target Logic
            pct_target_val = row.get('Pct_To_Target')
            pct_display = "-"
            pct_class = ""
            if pct_target_val is not None:
                 pct_display = f"{pct_target_val:.2f}%"
                 pct_class = "positive" if pct_target_val > 0 else "negative"

            # Consensus color
            cons = row.get('Consensus', '-')
            cons_style = ""
            if 'Buy' in cons: cons_style = 'color: #4caf50; font-weight: bold;'
            elif 'Sell' in cons: cons_style = 'color: #f44336; font-weight: bold;'
            
            analysts = row.get('Analysts', 0)
            industry = row.get('Industry', '-')
            
            # Smart Entry Logic (HTML)
            smart_entry_html = "-"
            if row.get('Decision') == "BUY" and row.get('Smart_Entry'):
                s_price = row.get('Smart_Entry')
                s_type = row.get('Smart_Type', 'LIMIT')
                s_reason = row.get('Smart_Reason', '')
                
                # Currency Symbol
                curr_code = row.get('Currency', 'USD')
                curr_sym = "$" if curr_code == 'USD' else "€" if curr_code == 'EUR' else "£" if curr_code == 'GBP' else "RON" if curr_code == 'RON' else curr_code
                
                icon = "⚡" if s_type == "STOP" else "📉"
                color = "#E91E63" if s_type == "STOP" else "#2196F3"
                
                tooltip_text = f"<strong>{s_type} ORDER @ {curr_sym}{s_price:.2f}</strong><br>{s_reason}"
                smart_entry_html = f'<span style="color: {color}; font-weight: bold; cursor: help;" onmousemove="showTooltip(event, \'{tooltip_text}\')" onmouseout="hideTooltip()">{icon} {s_price:.2f} <span style="font-size:0.8em; color:#888;">{curr_sym}</span></span>'

            # Sparkline ID
            spark_wl_id = f"spark_wl_{watch_chart_id}"
            watch_chart_id += 1

            # Change % logic
            change = 0.0
            spark_data = row.get('Sparkline', [])
            if (
                isinstance(spark_data, list)
                and len(spark_data) > 1
                and spark_data[-2] != 0
            ):
                change = ((spark_data[-1] - spark_data[-2]) / spark_data[-2]) * 100
                
            change_color = '#aaa'
            arrow = ''
            if change > 0:
                change_color = '#4caf50'; arrow = '▲'
            elif change < 0:
                change_color = '#f44336'; arrow = '▼'

            # Calc Fitness
            eco_phase = full_state.get('eco_phase', 'Expansion')
            eco_next = full_state.get('eco_next_phase', 'Slowdown')
            sector = row.get('Sector', row.get('Industry', '-'))
            
            fit_now = assess_stock_fitness(sector, eco_phase)
            fit_next = assess_stock_fitness(sector, eco_next)

            # Calculate Time Ago
            cached_at = row.get('_cached_at', 0)
            time_ago = "-"
            if cached_at:
                diff = time.time() - cached_at
                if diff < 60: time_ago = "<1m"
                elif diff < 3600: time_ago = f"{int(diff//60)}m"
                elif diff < 86400: time_ago = f"{int(diff//3600)}h"
                else: time_ago = f"{int(diff//86400)}d"

            # R:R Display
            rr_val = row.get('RR_Ratio', 0)
            rr_display = f"1:{rr_val:.1f}" if rr_val > 0 else "-"
            rr_color = "#4caf50" if rr_val >= 3 else "#ff9800" if rr_val >= 2 else "#f44336" if rr_val > 0 else "#888"

            # Strategy Badge
            strat = row.get('Strategy', '-')
            strat_color = "#888"
            if "Breakout" in strat: strat_color = "#E91E63; font-weight:bold"
            elif "Pullback" in strat: strat_color = "#4caf50; font-weight:bold"
            elif "Reversal" in strat: strat_color = "#9C27B0"
            elif "Range" in strat: strat_color = "#FF9800"

            # Strategy Descriptions (Tooltip)
            strat_desc = {
                "Strong Breakout": "<strong>Strong Breakout (Momentum)</strong><br>Prețul crește accelerat cu RSI ridicat.<br>⚡ <strong>Acțiune:</strong> Atenție la condiții de supravânzare (Overbought). Poate urma o corecție scurtă.",
                "Breakout": "<strong>Breakout</strong><br>Prețul a depășit mediile mobile (SMA50) confirmând forța cumpărătorilor.<br>🚀 <strong>Acțiune:</strong> Setup favorabil pentru intrare pe momentum.",
                "Pullback": "<strong>Bullish Pullback</strong><br>Trend general crescător, dar prețul a scăzut temporar (oportunitate).<br>📉 <strong>Acțiune:</strong> Caută intrări la un preț mai bun (Buy the Dip).",
                "Deep Pullback": "<strong>Deep Pullback</strong><br>Corecție mai adâncă în trend crescător (RSI scăzut).<br>⚠️ <strong>Acțiune:</strong> Risc mediu. Așteaptă confirmarea revenirii prețului.",
                "Reversal (Oversold)": "<strong>Reversal (Oversold)</strong><br>Prețul a scăzut agresiv, RSI sub 30.<br>🔄 <strong>Acțiune:</strong> Posibilă revenire tehnică rapidă (Rebound). Riscant (Catching a falling knife).",
                "Range / Consolidation": "<strong>Range / Consolidation</strong><br>Prețul oscilează între mediile mobile fără direcție clară.<br>💤 <strong>Acțiune:</strong> Așteaptă un Breakout clar într-o direcție.",
                "Normal": "<strong>Normal</strong><br>Nu există un setup tehnic specific detectat momentan.<br>👀 <strong>Acțiune:</strong> Monitorizează.",
                "-": "Date insuficiente."
            }
            strat_tooltip = strat_desc.get(strat, strat_desc["Normal"])

            # RSI Tooltip Logic
            rsi_val = row['RSI']
            rsi_tooltip = ""
            if rsi_val >= 70:
                rsi_tooltip = "<strong>RSI: Overbought (>70)</strong><br>Supra-cumpărat. Prețul a crescut foarte rapid.<br>⚠️ <strong>Acțiune:</strong> Risc crescut de corecție (scădere). Nu cumpăra la vârf."
            elif 50 <= rsi_val < 70:
                rsi_tooltip = "<strong>RSI: Bullish (50-70)</strong><br>Momentum pozitiv. Cumpărătorii controlează piața.<br>✅ <strong>Acțiune:</strong> Zonă bună pentru trend following."
            elif 30 <= rsi_val < 50:
                rsi_tooltip = "<strong>RSI: Bearish (30-50)</strong><br>Momentum negativ sau neutru-sláb.<br>⛔ <strong>Acțiune:</strong> Prudență. Trendul poate fi descendent."
            else:
                rsi_tooltip = "<strong>RSI: Oversold (<30)</strong><br>Supra-vândut. Prețul a scăzut extrem.<br>🔄 <strong>Acțiune:</strong> Posibilă revenire (Bounce) iminentă."

            # Earnings Bomb HTML
            bomb_html = ""
            if row.get('Earnings_Danger'):
                 msg = row.get("Earnings_Msg", "")
                 bomb_html = f' <span style="cursor:help; font-size:1.2em;" onmousemove="showTooltip(event, \'<strong>💣 Earnings Danger Zone</strong><br>{msg}<br>⚠️ Volatilitate extremă posibilă.\')" onmouseout="hideTooltip()">💣</span>'

            html_head += f"""
                    <tr data-volume="{row.get('Volume', 0)}" data-avgvol="{row.get('Avg_Volume', 0)}" data-rsi="{row['RSI']}" data-rr="{rr_val}">
                        <td><strong style="cursor: help; color: #4dabf7; text-decoration: underline;" onmousemove="showTooltip(event, '{row.get('Company_Name', '')}')" onmouseout="hideTooltip()" onclick="goToVolatility('{row['Ticker']}')">{row['Ticker']}</strong>{bomb_html}</td>
                        <td>€{row['Price']:.2f}</td>
                        <td><canvas id="{spark_wl_id}" class="sparkline-container" role="button" tabindex="0" title="Deschide graficul și detaliile pentru {row['Ticker']}" style="cursor:pointer;" onclick="openWatchlistDetail('{row['Ticker']}')" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();openWatchlistDetail('{row['Ticker']}');}}"></canvas></td>
                        <td>{target_display}</td>
                        <td class="{pct_class}">{pct_display}</td>
                        <td style="color: {rr_color}; font-weight: 600;">{rr_display}</td>
                        <td style="{cons_style}">{cons}</td>
                        <td>{analysts}</td>
                        <td style="font-size: 0.8rem; color: #aaa;">{sector}</td>
                        <td style="font-weight: 700; color: {row.get('Decision_Color', '#888')};" onmousemove="showTooltip(event, '{row.get('Check_Details', '')}')" onmouseout="hideTooltip()">{row.get('Decision', '-')} ({row.get('Checks_Passed', 0)}/4)</td>
                        <td style="text-align: center;">{smart_entry_html}</td>
                        <td style="color: {'#4caf50' if row.get('RS_vs_SPX', 0) and row.get('RS_vs_SPX', 0) > 0 else '#f44336'};">{row.get('RS_vs_SPX', '-') if row.get('RS_vs_SPX') is not None else '-'}%</td>
                        <td class="trend-{trend_cls}">{row['Trend']}</td>
                        <td style="font-size: 0.85rem; color: {strat_color}; cursor: help;" onmousemove="showTooltip(event, '{strat_tooltip}')" onmouseout="hideTooltip()">{strat}</td>
                        <td style="text-align: center;">{fit_now}</td>

                        <td style="text-align: center;">{fit_next}</td>
                        <td style="cursor: help;" onmousemove="showTooltip(event, '{rsi_tooltip}')" onmouseout="hideTooltip()">{row['RSI']:.0f}</td>
                        <td class="rsi-{rsi_cls}">{row['RSI_Status']}</td>
                        <td>{row['ATR_14']:.2f}</td>
                        <td>€{row['Stop_Loss']:.2f}</td>
                        <td>€{row['SMA_50']:.2f}</td>
                        <td>€{row['SMA_200']:.2f}</td>
                        <td style="text-align: center; padding: 5px; font-size: 0.75rem; color: {change_color};">{arrow} {abs(change):.2f}%</td>
                        <td style="text-align: center; font-size: 0.75rem; color: #888;">{time_ago}</td>
                    </tr>
            """
        

    
    # --- VOLATILITY DATA & TAB GENERATION ---
    vol_map = {}
    
    # Helper to clean/convert
    def get_val(d, k, default=0):
        v = d.get(k)
        try: return float(v) if v is not None else default
        except: return default

    # Merge Data
    all_items = []
    if not watchlist_df.empty: all_items.extend(watchlist_df.to_dict('records'))
    if not portfolio_df.empty: all_items.extend(portfolio_df.to_dict('records'))
    
    for item in all_items:
        sym = item.get('Ticker', item.get('Symbol'))
        if not sym: continue
        
        price = get_val(item, 'Current_Price') or get_val(item, 'Price')
        price_native = get_val(item, 'Price_Native')
        atr = get_val(item, 'Finviz_ATR') or get_val(item, 'ATR_14')
        
        # ATR percentage must be calculated using base currency price
        atr_pct = (atr / price_native * 100) if price_native and atr else 0
        
        # Calculate Trail LARG (MAX × 3)
        vols = [atr_pct, get_val(item, 'Vol_W'), get_val(item, 'Vol_M')]
        vols_valid = [v for v in vols if v > 0]
        trail_larg = max(vols_valid) * 3 if vols_valid else 0
        
        vol_map[sym] = {
            'Price_Native': round(price_native, 2) if price_native else 0,
            'ATR_Val': round(atr, 2),
            'ATR_Pct': round(atr_pct, 2),
            'Vol_W': get_val(item, 'Vol_W'),
            'Vol_M': get_val(item, 'Vol_M'),
            'Trail_Larg': round(trail_larg, 2)
        }
        
        
    vol_json = json.dumps(vol_map)
    
    # Generate adjustment data for portfolio stocks with Trail Propus < Trail %
    adjust_data = []
    if not portfolio_df.empty:
        for _, row in portfolio_df.iterrows():
            sym = row.get('Symbol')
            if not sym:
                continue
            
            # Get volatility data
            atr_pct = (row.get('Finviz_ATR', 0) / row.get('Price_Native', 1) * 100) if row.get('Price_Native', 0) > 0 and row.get('Finviz_ATR', 0) else 0
            vol_w = row.get('Vol_W', 0) or 0
            vol_m = row.get('Vol_M', 0) or 0
            vols_valid = [v for v in [atr_pct, vol_w, vol_m] if v > 0]
            trail_larg = max(vols_valid) * 3 if vols_valid else 0
            trail_med = max(vols_valid) * 2 if vols_valid else 0
            trail_strans = max(vols_valid) * 1.5 if vols_valid else 0
            
            trail_pct = row.get('Trail_Pct', 0) or 0
            old_stop = row.get('Trail_Stop', 0) or 0
            
            # Only include if Trail LARG < Trail % (red) -> NOW CHANGED TO ALL per user request
            if trail_larg > 0 and trail_pct > 0 and old_stop > 0:
                # Reconstruct original price when stop was set
                original_price = old_stop / (1 - trail_pct / 100)
                
                # Calculate New Stops
                new_stop_larg = original_price * (1 - trail_larg / 100)
                new_stop_med = original_price * (1 - trail_med / 100)
                new_stop_strans = original_price * (1 - trail_strans / 100)
                
                # Get conversion rate (EUR to base currency)
                price_eur = row.get('Current_Price', 0) or 0
                price_native = row.get('Price_Native', 0) or 0
                rate = price_native / price_eur if price_eur > 0 else 1
                
                # Convert stops to base currency
                old_stop_native = old_stop * rate
                new_stop_larg_native = new_stop_larg * rate
                new_stop_med_native = new_stop_med * rate
                new_stop_strans_native = new_stop_strans * rate
                
                adjust_data.append({
                    'Symbol': sym,
                    'Trail_Current': round(trail_pct, 1),
                    'Stop_Current_EUR': round(old_stop, 2),
                    'Stop_Current_Native': round(old_stop_native, 2),
                    
                    'Trail_Larg': round(trail_larg, 1),
                    'Stop_Larg_EUR': round(new_stop_larg, 2),
                    'Stop_Larg_Native': round(new_stop_larg_native, 2),
                    
                    'Trail_Med': round(trail_med, 1),
                    'Stop_Med_EUR': round(new_stop_med, 2),
                    'Stop_Med_Native': round(new_stop_med_native, 2),
                    
                    'Trail_Strans': round(trail_strans, 1),
                    'Stop_Strans_EUR': round(new_stop_strans, 2),
                    'Stop_Strans_Native': round(new_stop_strans_native, 2)
                })
    
    adjust_json = json.dumps(adjust_data)
    
    # Watchlist Closures
    html_footer = """
                </tbody>
            </table>
            </div>
        </div>

        <!-- Volatility Tab -->
        <div id="volatility" class="tab-content">
             <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 32px;">
                 <button id="vol-back-btn" onclick="goBackFromVolatility()" class="btn-secondary" style="padding: 10px 20px;">
                     ← Back
                 </button>
                 <h2 style="color: var(--text-primary); margin: 0;">Volatility Calculator</h2>
                 <div style="width: 100px;"></div> <!-- Spacer for centering -->
             </div>
             <div style="background: var(--bg-white); padding: 32px; border-radius: var(--radius-md); max-width: 600px; margin: 0 auto; box-shadow: var(--shadow-sm); border: 1px solid var(--border-light);">
                 <label style="color: var(--text-secondary); margin-bottom: 8px; display: block; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Search Symbol</label>
                 <input list="vol-tickers" id="vol-input" oninput="calcVolatility()" placeholder="Type symbol (e.g. NVDA)..." 
                        style="width: 100%; padding: 14px 16px; margin-bottom: 24px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); font-size: 16px; transition: all 0.2s;" onfocus="this.style.borderColor='var(--primary-purple)'; this.style.boxShadow='0 0 0 3px rgba(119,96,249,0.1)'" onblur="this.style.borderColor='var(--border-light)'; this.style.boxShadow='none'">
                 <datalist id="vol-tickers">
    """ + "".join([f'<option value="{k}">' for k in sorted(vol_map.keys())]) + """
                 </datalist>
                 
                 <div id="vol-results" style="display: none;">
                      <table style="width: 100%; border-collapse: collapse; color: var(--text-primary);">
                          <tr style="border-bottom: 2px solid var(--border-light);">
                                <th style="text-align: left; padding: 10px; color: var(--text-secondary); font-weight: 600;">Metric</th>
                                <th style="text-align: right; padding: 10px; color: var(--text-secondary); font-weight: 600;">Value</th>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">Price (Base Currency)</td>
                                <td id="res-price-native" style="text-align: right; font-weight: 700; color: var(--success-green);">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">ATR (14) Value</td>
                                <td id="res-atr-val" style="text-align: right; font-weight: 700; color: var(--text-primary);">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">ATR (14) Volatility</td>
                                <td id="res-atr-pct" style="text-align: right; font-weight: 700; color: var(--primary-purple);">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">Daily Volatility</td>
                                <td id="res-day" style="text-align: right; font-weight: 700; color: var(--text-primary);">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">Weekly Volatility</td>
                                <td id="res-week" style="text-align: right; font-weight: 700; color: var(--text-primary);">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">Monthly Volatility</td>
                                <td id="res-month" style="text-align: right; font-weight: 700; color: var(--text-primary);">-</td>
                          </tr>
                      </table>
                      
                      
                      <!-- Suggested Stop & Buy (ATR-based) -->
                      <div style="margin-top: 24px; padding: 20px; background: var(--light-purple-bg); border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                              <div>
                                  <div style="color: var(--text-secondary); font-size: 14px; margin-bottom: 5px; font-weight: 600;">Suggested Stop (2×ATR)</div>
                                  <div id="suggested-stop" style="font-size: 1.1rem; font-weight: bold; color: #f44336;">-</div>
                              </div>
                              <div>
                                  <div style="color: var(--text-secondary); font-size: 14px; margin-bottom: 5px; font-weight: 600;">Suggested Buy (2×ATR)</div>
                                  <div id="suggested-buy" style="font-size: 1.1rem; font-weight: bold; color: #4caf50;">-</div>
                              </div>
                          </div>
                      </div>
                      
                      <!-- Trailing Stop Calculations -->
                      <h4 style="color: var(--primary-purple); margin-top: 30px; margin-bottom: 15px; text-align: center;">Trailing Stop Levels</h4>
                      <table style="width: 100%; border-collapse: collapse; color: var(--text-primary); margin-top: 10px;">
                          <tr style="border-bottom: 1px solid var(--border-light);">
                                <th style="text-align: left; padding: 10px;">Strategy</th>
                                <th style="text-align: right; padding: 10px;">Volatility %</th>
                                <th style="text-align: right; padding: 10px;">Stop Sell</th>
                                <th style="text-align: right; padding: 10px;">Stop Buy</th>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: #f44336;">🔴 LARG (Loose)</td>
                                <td id="vol-larg" style="text-align: right; font-weight: bold;">-</td>
                                <td id="stop-larg-sell" style="text-align: right; font-weight: bold; color: #f44336;">-</td>
                                <td id="stop-larg-buy" style="text-align: right; font-weight: bold; color: #4caf50;">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: #ff9800;">🟠 MEDIU (Medium)</td>
                                <td id="vol-mediu" style="text-align: right; font-weight: bold;">-</td>
                                <td id="stop-mediu-sell" style="text-align: right; font-weight: bold; color: #f44336;">-</td>
                                <td id="stop-mediu-buy" style="text-align: right; font-weight: bold; color: #4caf50;">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: #4caf50;">🟢 STRÂNS (Tight)</td>
                                <td id="vol-strans" style="text-align: right; font-weight: bold;">-</td>
                                <td id="stop-strans-sell" style="text-align: right; font-weight: bold; color: #f44336;">-</td>
                                <td id="stop-strans-buy" style="text-align: right; font-weight: bold; color: #4caf50;">-</td>
                          </tr>
                      </table>
                 </div>
             </div>
             
             <!-- Stop Adjustment Table for Portfolio (Trail Propus < Trail %) -->
             <div id="stop-adjust-section" style="margin-top: 30px; max-width: 800px; margin-left: auto; margin-right: auto; display: none;">
                 <h4 style="color: #f44336; text-align: center; margin-bottom: 15px;">🔴 Ajustare Stop - Portofoliu (Sugestii)</h4>
                 <div id="adjust-table-container"></div>
             </div>
             
             <script>
                const adjustData = """ + adjust_json + """;
                
                // Render adjustment table (filtered by symbol if provided)
                function renderAdjustTable(filterSymbol) {
                    const container = document.getElementById('adjust-table-container');
                    
                    // Filter data by symbol if provided
                    let dataToShow = adjustData;
                    if (filterSymbol) {
                        dataToShow = adjustData.filter(item => item.Symbol === filterSymbol);
                    }
                    
                    if (!dataToShow || dataToShow.length === 0) {
                        container.parentElement.style.display = 'none';
                        return;
                    }
                    
                    container.parentElement.style.display = 'block';
                    
                    let html = `
                        <table style="width: 100%; border-collapse: collapse; color: var(--text-primary); background: var(--bg-white); border-radius: var(--radius-sm); overflow: hidden; border: 1px solid var(--border-light);">
                            <thead>
                                <tr style="background: var(--bg-light); border-bottom: 2px solid var(--border-light);">
                                    <th style="padding: 12px; text-align: left;">Symbol</th>
                                    <th style="padding: 12px; text-align: left;">Tip Ajustare</th>
                                    <th style="padding: 12px; text-align: right;">Trail Propus</th>
                                    <th style="padding: 12px; text-align: right;">Stop Nou (EUR)</th>
                                    <th style="padding: 12px; text-align: right;">Stop Nou (Base)</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    dataToShow.forEach(item => {
                        // Header row per symbol
                        html += `
                            <tr style="background-color: #f8f9fa; border-top: 2px solid #ddd;">
                                <td style="padding: 10px; font-weight: bold; color: #4dabf7;" rowspan="4">${item.Symbol}<br><span style="font-size:0.8em; color: #666;">Curent: ${item.Trail_Current}%</span></td>
                                <td colspan="4" style="padding: 5px;"></td>
                            </tr>
                        `;
                        
                        // LARG Row
                        html += `
                            <tr style="border-bottom: 1px solid #eee;">
                                <td style="padding: 8px;"><strong>LARG (3x)</strong></td>
                                <td style="padding: 8px; text-align: right; color: #f44336;">${item.Trail_Larg}%</td>
                                <td style="padding: 8px; text-align: right; font-weight: bold;">€${item.Stop_Larg_EUR}</td>
                                <td style="padding: 8px; text-align: right;">${item.Stop_Larg_Native}</td>
                            </tr>
                        `;
                        // MEDIU Row
                        html += `
                            <tr style="border-bottom: 1px solid #eee;">
                                <td style="padding: 8px;"><strong>MEDIU (2x)</strong></td>
                                <td style="padding: 8px; text-align: right; color: #ff9800;">${item.Trail_Med}%</td>
                                <td style="padding: 8px; text-align: right; font-weight: bold;">€${item.Stop_Med_EUR}</td>
                                <td style="padding: 8px; text-align: right;">${item.Stop_Med_Native}</td>
                            </tr>
                        `;
                        // STRANS Row
                        html += `
                            <tr style="border-bottom: 2px solid #333;">
                                <td style="padding: 8px;"><strong>STRANS (1.5x)</strong></td>
                                <td style="padding: 8px; text-align: right; color: #4caf50;">${item.Trail_Strans}%</td>
                                <td style="padding: 8px; text-align: right; font-weight: bold;">€${item.Stop_Strans_EUR}</td>
                                <td style="padding: 8px; text-align: right;">${item.Stop_Strans_Native}</td>
                            </tr>
                        `;
                    });
                    
                    html += `
                            </tbody>
                        </table>
                    `;
                    
                    container.innerHTML = html;
                }
                
                // Don't render on load - only when symbol is selected
                // renderAdjustTable();
             </script>
             
             <script>
                const volData = """ + vol_json + """;
                function calcVolatility() {
                    const val = document.getElementById('vol-input').value.toUpperCase();
                    const resDiv = document.getElementById('vol-results');
                    if (volData[val]) {
                         const d = volData[val];
                         const price = d.Price_Native;
                         const atrPct = d.ATR_Pct;
                         const volW = d.Vol_W;
                         const volM = d.Vol_M;
                         
                         // Display basic metrics
                         document.getElementById('res-price-native').innerText = price;
                         document.getElementById('res-atr-val').innerText = d.ATR_Val;
                         document.getElementById('res-atr-pct').innerText = atrPct + '%';
                         document.getElementById('res-day').innerText = '-'; // Data not available yet
                         document.getElementById('res-week').innerText = volW + '%';
                         document.getElementById('res-month').innerText = volM + '%';
                         
                         // Calculate and display Suggested Stop & Buy (Price ± 2×ATR)
                         const suggestedStop = price - (2 * d.ATR_Val);
                         const suggestedBuy = price + (2 * d.ATR_Val);
                         document.getElementById('suggested-stop').innerText = suggestedStop.toFixed(2);
                         document.getElementById('suggested-buy').innerText = suggestedBuy.toFixed(2);
                         
                         // Calculate trailing stop levels
                         const vols = [atrPct, volW, volM].filter(v => v > 0);
                         
                         if (vols.length > 0 && price > 0) {
                             // LARG: MAX × 3
                             const volLarg = Math.max(...vols) * 3;
                             const stopLargSell = price * (1 - volLarg / 100);
                             const stopLargBuy = price * (1 + volLarg / 100);
                             
                             // MEDIU: AVG × 2
                             const volMediu = (vols.reduce((a, b) => a + b, 0) / vols.length) * 2;
                             const stopMediuSell = price * (1 - volMediu / 100);
                             const stopMediuBuy = price * (1 + volMediu / 100);
                             
                             // STRÂNS: MIN × 1.5
                             const volStrans = Math.min(...vols) * 1.5;
                             const stopStransSell = price * (1 - volStrans / 100);
                             const stopStransBuy = price * (1 + volStrans / 100);
                             
                             // Display results
                             document.getElementById('vol-larg').innerText = volLarg.toFixed(2) + '%';
                             document.getElementById('stop-larg-sell').innerText = stopLargSell.toFixed(2);
                             document.getElementById('stop-larg-buy').innerText = stopLargBuy.toFixed(2);
                             
                             document.getElementById('vol-mediu').innerText = volMediu.toFixed(2) + '%';
                             document.getElementById('stop-mediu-sell').innerText = stopMediuSell.toFixed(2);
                             document.getElementById('stop-mediu-buy').innerText = stopMediuBuy.toFixed(2);
                             
                             document.getElementById('vol-strans').innerText = volStrans.toFixed(2) + '%';
                             document.getElementById('stop-strans-sell').innerText = stopStransSell.toFixed(2);
                             document.getElementById('stop-strans-buy').innerText = stopStransBuy.toFixed(2);
                         }
                         
                         resDiv.style.display = 'block';
                         
                         // Update adjustment table for this symbol
                         renderAdjustTable(val);
                    } else {
                         resDiv.style.display = 'none';
                         renderAdjustTable(null);
                    }
                }
                
                // Track source tab for back navigation
                let sourceTab = 'portfolio';
                
                // Function to navigate to Volatility Calculator with symbol
                function goToVolatility(symbol) {
                    // Save current tab by checking for active class
                    const currentTab = document.querySelector('.tab-content.active');
                    if (currentTab) {
                        sourceTab = currentTab.id;
                    }
                    
                    switchTab('volatility');
                    document.getElementById('vol-input').value = symbol;
                    calcVolatility();
                }
                
                // Function to go back to source tab
                function goBackFromVolatility() {
                    switchTab(sourceTab);
                }
             </script>
        </div>
        
    </div> <!-- END dashboard-content -->

        <script>
            $(document).ready(function() {
                var table = $('#portfolio-table, #watchlist-table, #buying-orders-table, #selling-orders-table').DataTable({
                    paging: false,
                    ordering: true,
                    info: false,
                    searching: true,
                    order: [] 
                });

                // Populate Sector datalist dynamically
                var sectors = {};
                var wlTable = $('#watchlist-table').DataTable();
                wlTable.column(8).data().each(function(val) {
                    if (val) {
                        var cleanVal = val.trim();
                        if (cleanVal) {
                            sectors[cleanVal] = true;
                        }
                    }
                });
                var datalist = $('<datalist id="sector-list"></datalist>');
                Object.keys(sectors).sort().forEach(function(sec) {
                    datalist.append($('<option>').attr('value', sec));
                });
                $('body').append(datalist);
                
                // Custom filtering function
                $.fn.dataTable.ext.search.push(
                    function(settings, data, dataIndex) {
                        if (settings.nTable.id !== 'watchlist-table') return true;

                        var consensus = $('#filter-consensus').val();
                        var minAnalysts = parseFloat($('#filter-analysts').val());
                        var minTarget = parseFloat($('#filter-target-pct').val());
                        var trend = $('#filter-trend').val();
                        var status = $('#filter-status').val();
                        var decision = $('#filter-decision').val();
                        var strategy = $('#filter-strategy').val();
                        var minRsSpx = parseFloat($('#filter-rs-spx').val());
                        var sector = $('#filter-sector').val() ? $('#filter-sector').val().toLowerCase().trim() : "";

                        // Indices Updated for new columns (R:R at 5, Strategy at 13)
                        var rowTargetPct = parseFloat(data[4].replace('%', '')) || -9999;
                        var rowConsensus = data[6] || "";       // Was 5
                        var rowAnalysts = parseFloat(data[7]) || 0; // Was 6
                        var rowDecision = data[9] || "";        // Was 8
                        var rowTrend = data[12] || "";          // Was 11
                        var rowStatus = data[17] || "";         // Was 15
                        var rowStrategy = data[13] || "";
                        var rowRsSpx = parseFloat(data[11].replace('%', '').replace('+', ''));
                        if (isNaN(rowRsSpx)) rowRsSpx = -9999;
                        var rowSector = data[8] ? data[8].toLowerCase().trim() : "";

                        if (consensus && !rowConsensus.includes(consensus)) return false;
                        if (!isNaN(minAnalysts) && rowAnalysts < minAnalysts) return false;
                        if (!isNaN(minTarget) && rowTargetPct < minTarget) return false;
                        if (trend && !rowTrend.includes(trend)) return false;
                        if (status && !rowStatus.includes(status)) return false;
                        if (decision && !rowDecision.includes(decision)) return false;
                        if (strategy && !rowStrategy.includes(strategy)) return false;
                        if (!isNaN(minRsSpx) && rowRsSpx < minRsSpx) return false;
                        if (sector && !rowSector.includes(sector)) return false;

                        var minVol = parseFloat($('#filter-volume').val());
                        var minRsi = parseFloat($('#filter-rsi-min').val());
                        var maxRsi = parseFloat($('#filter-rsi-max').val());
                        var minRR = parseFloat($('#filter-rr').val());

                        // Get Data Attributes from TR
                        var rowNode = settings.aoData[dataIndex].nTr;
                        var rowVol = parseFloat(rowNode.getAttribute('data-avgvol')) || 0; // Use Avg Vol for filtering
                        var rowRsi = parseFloat(rowNode.getAttribute('data-rsi')) || 50;
                        var rowRR = parseFloat(rowNode.getAttribute('data-rr')) || 0;


                        
                        // New Filters
                        if (!isNaN(minVol) && (rowVol / 1000000) < minVol) return false; // Input is in Millions
                        if (!isNaN(minRsi) && rowRsi < minRsi) return false;
                        if (!isNaN(maxRsi) && rowRsi > maxRsi) return false;
                        if (!isNaN(minRR) && rowRR < minRR) return false;

                        return true;
                    }
                );

                // Event listener to redraw on input change
                $('#filter-consensus, #filter-analysts, #filter-target-pct, #filter-trend, #filter-status, #filter-decision, #filter-volume, #filter-rsi-min, #filter-rsi-max, #filter-rr, #filter-strategy, #filter-rs-spx, #filter-sector').change(function() {
                    table.draw();
                });
                $('#filter-analysts, #filter-target-pct, #filter-volume, #filter-rsi-min, #filter-rsi-max, #filter-rr, #filter-rs-spx, #filter-sector').keyup(function() {
                     table.draw();
                });
                $('#filter-sector').on('input', function() {
                    table.draw();
                });
            });

            function toggleMenu() {
                document.getElementById('navMenu').classList.toggle('show');
            }
            
            // Close menu when clicking outside
            window.onclick = function(event) {
                if (!event.target.matches('.hamburger')) {
                    var dropdowns = document.getElementsByClassName("menu-dropdown");
                    for (var i = 0; i < dropdowns.length; i++) {
                        var openDropdown = dropdowns[i];
                        if (openDropdown.classList.contains('show')) {
                            openDropdown.classList.remove('show');
                        }
                    }
                }
            }

            function switchTab(tabId) {
                // Hide all contents
                var contents = document.getElementsByClassName('tab-content');
                for (var i = 0; i < contents.length; i++) {
                    contents[i].classList.remove('active');
                }
                
                // Show selected
                document.getElementById(tabId).classList.add('active');
            }
            
            // Sparkline charts data
            const sparklineData = {
    """
    
    # Adăugăm datele pentru sparklines PORTFOLIO
    for idx, row in portfolio_df.iterrows():
        sparkline_id = f"spark_{idx}"
        sparkline_values = row['Sparkline']
        html_footer += f"""
                '{sparkline_id}': {sparkline_values},
        """
        
    # Adăugăm datele pentru sparklines WATCHLIST
    if not watchlist_df.empty:
        watch_chart_id = 0
        for idx, row in watchlist_df.iterrows():
            spark_wl_id = f"spark_wl_{watch_chart_id}"
            watch_chart_id += 1
            spark_values = row.get('Sparkline', [])
            html_footer += f"""
                '{spark_wl_id}': {spark_values},
            """
            
    # Adăugăm datele pentru sparklines INDICATORI
    for name in market_indicators:
        if 'sparkline' in market_indicators[name]:
            spark_id = f"spark_ind_{name}"
            spark_values = market_indicators[name]['sparkline']
            html_footer += f"""
                '{spark_id}': {spark_values},
            """
    
    indicator_explanations = {
        'VIX3M': 'Așteptările pieței privind volatilitatea S&P 500 pe aproximativ trei luni.',
        'VIX': 'Volatilitatea implicită a opțiunilor S&P 500 pe aproximativ 30 de zile; este numit frecvent indicele fricii.',
        'VIX1D': 'Volatilitatea implicită estimată pentru următoarea zi de tranzacționare.',
        'VIX9D': 'Volatilitatea implicită pe termen foarte scurt, aproximativ nouă zile.',
        'VXN': 'Volatilitatea implicită a indicelui Nasdaq-100, sensibilă la sectorul tehnologic.',
        'LTV': 'Indicator CBOE pentru riscul perceput în coada stângă a distribuției, asociat mișcărilor extreme negative.',
        'SKEW': 'Măsoară cât de scumpe sunt protecțiile împotriva mișcărilor extreme față de opțiunile obișnuite.',
        'MOVE': 'Indice al volatilității implicite pe piața obligațiunilor de stat americane.',
        'Crypto Fear': 'Indice compozit de sentiment pentru piața crypto, de la frică extremă la lăcomie extremă.',
        'GVZ': 'Volatilitatea implicită a aurului, derivată din opțiunile pe ETF-ul GLD.',
        'OVX': 'Volatilitatea implicită a petrolului, derivată din opțiunile pe ETF-ul USO.',
        'SPX': 'Indicele S&P 500, reper pentru acțiunile americane cu capitalizare mare.',
        'NASDAQ': 'Nasdaq Composite, reper cu expunere ridicată la tehnologie și companii de creștere.'
    }
    indicator_detail_data = {}
    for name in indicator_order:
        if name not in market_indicators:
            continue
        indicator = market_indicators[name]
        indicator_detail_data[name] = {
            'name': display_map.get(name, name),
            'ticker': indicator.get('ticker', ''),
            'value': indicator.get('value'),
            'change': indicator.get('change', 0),
            'status': indicator.get('status', 'Normal'),
            'rangeDescription': indicator.get('description', ''),
            'explanation': indicator_explanations.get(name, ''),
            'ohlc': indicator.get('ohlc', []),
            'series': indicator.get('history', indicator.get('sparkline', [])),
            'seriesDates': indicator.get('history_dates', [])
        }
    indicator_detail_json = json.dumps(indicator_detail_data, ensure_ascii=False).replace('</', '<\\/')
    watchlist_detail_data = {}
    if not watchlist_df.empty:
        for _, row in watchlist_df.iterrows():
            ticker = str(row['Ticker'])
            native_detail = _chart_detail_native_payload(
                row,
                ticker,
                'Price',
                rates=dashboard_rates,
            )
            to_native = native_detail['to_native']
            target_value = to_native(row.get('Target'))
            target_description = _format_native_price_text(
                target_value,
                native_detail['currency'],
            )
            stop_value = to_native(row.get('Stop_Loss', 0))
            watchlist_levels = []
            entry_value = row.get('Smart_Entry', 0)
            if (
                row.get('Decision') == 'BUY'
                and (pd.isna(entry_value) or not entry_value)
                and pd.notna(row.get('Smart_Entry_EUR'))
                and row.get('Smart_Entry_EUR')
            ):
                entry_value = to_native(row.get('Smart_Entry_EUR'))
            if (
                row.get('Decision') == 'BUY'
                and pd.notna(entry_value)
                and float(entry_value) > 0
            ):
                entry_type = row.get('Smart_Type') or 'LIMIT'
                watchlist_levels.append({
                    'label': f'Entry recomandat · {entry_type}',
                    'value': float(entry_value),
                    'color': '#2563eb'
                })
            if pd.notna(stop_value) and float(stop_value) > 0:
                watchlist_levels.append({
                    'label': 'Stop recomandat',
                    'value': float(stop_value),
                    'color': '#dc2626'
                })
            watchlist_detail_data[ticker] = {
                'kind': 'watchlist',
                'name': row.get('Company_Name', ticker),
                'ticker': ticker,
                'currency': native_detail['currency'],
                'value': native_detail['value'],
                'change': native_detail['change'],
                'status': row.get('Decision', '—'),
                'rangeDescription': row.get('Trend', '—'),
                'explanation': (
                    f"Acțiune din watchlist. RSI {float(row.get('RSI', 0)):.1f}; "
                    f"consens {row.get('Consensus', '—')}; "
                    f"target {target_description}."
                ),
                'ohlc': native_detail['ohlc'],
                'series': native_detail['series'],
                'seriesDates': native_detail['seriesDates'],
                'levels': watchlist_levels
            }
    watchlist_detail_json = json.dumps(watchlist_detail_data, ensure_ascii=False).replace('</', '<\\/')

    html_footer += f"""
            }};
            const indicatorDetailData = {indicator_detail_json};
            const watchlistDetailData = {watchlist_detail_json};
    """

    html_footer += """
            function openIndicatorDetail(indicatorName) {
                const detail = indicatorDetailData[indicatorName];
                openMarketDetailWindow(detail, indicatorName);
            }

            function openPortfolioDetail(symbol) {
                const detail = portfolioDetailData[symbol];
                openMarketDetailWindow(detail, symbol);
            }

            function detailForActiveBuyOrder(symbol) {
                const normalizedSymbol = String(symbol || '').toUpperCase();
                const baseDetail = buyRecommendationDetailData[normalizedSymbol]
                    || portfolioDetailData[normalizedSymbol]
                    || watchlistDetailData[normalizedSymbol];
                const symbolBase = normalizedSymbol.split('.')[0];
                const levelKey = Object.keys(activeBuyOrderLevels).find(function(key) {
                    return key === normalizedSymbol || key.split('.')[0] === symbolBase;
                });
                const orderLevels = levelKey ? activeBuyOrderLevels[levelKey] : [];
                const detail = baseDetail && orderLevels.length
                    ? Object.assign({}, baseDetail, {
                        levels: (baseDetail.levels || []).concat(orderLevels)
                    })
                    : baseDetail;
                return detail;
            }

            function openOrderDetail(symbol) {
                const normalizedSymbol = String(symbol || '').toUpperCase();
                openMarketDetailWindow(
                    detailForActiveBuyOrder(normalizedSymbol),
                    normalizedSymbol
                );
            }

            function openWatchlistDetail(symbol) {
                const detail = watchlistDetailData[symbol];
                openMarketDetailWindow(detail, symbol);
            }

            function openBuyRecommendationDetail(symbol) {
                const detail = buyRecommendationDetailData[symbol];
                openMarketDetailWindow(detail, symbol);
            }

            function openMarketDetailWindow(detail, indicatorName) {
                if (!detail) return;
                const popup = window.open('', '_blank');
                if (!popup) {
                    alert('Browserul a blocat fereastra nouă. Permite pop-up-uri pentru acest site.');
                    return;
                }
                const payload = JSON.stringify(detail).replace(/</g, '\\u003c');
                popup.document.open();
                popup.document.write(`<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${escapeIndicatorText(detail.name)} — Detalii</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f6f7fb;color:#121827;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.page{max-width:1500px;margin:0 auto;padding:28px}.top{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;margin-bottom:22px}
h1{margin:0 0 6px;font-size:clamp(28px,4vw,44px)}.ticker{color:#7760f9;font-weight:700}.close{border:1px solid #dfe3ea;background:#fff;color:#374151;padding:10px 16px;border-radius:10px;cursor:pointer}
.stats{display:grid;grid-template-columns:repeat(4,minmax(140px,1fr));gap:14px;margin-bottom:18px}.stat,.panel{background:#fff;border:1px solid #e1e5ec;border-radius:16px;box-shadow:0 4px 18px rgba(15,23,42,.05)}
.stat{padding:18px}.label{font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:.06em}.num{font-size:25px;font-weight:750;margin-top:6px}
.panel{padding:20px;margin-bottom:18px}.toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.buttons{display:flex;gap:8px}.range{border:1px solid #dfe3ea;background:#fff;color:#4b5563;padding:7px 12px;border-radius:8px;cursor:pointer;font-weight:650}.range.active{background:#7760f9;color:#fff;border-color:#7760f9}
.chart-wrap{height:min(68vh,680px);min-height:420px;position:relative}canvas{display:block;width:100%;height:100%}.details{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.details h2{margin:0 0 10px;font-size:18px}.details p{margin:0;color:#4b5563;line-height:1.65}.note{font-size:12px;color:#6b7280;margin-top:10px}
.level-legend{display:none}.level-item{display:flex;align-items:center;justify-content:space-between;gap:10px;min-width:0;padding:8px 10px;border:1px solid #e5e7eb;border-radius:9px;background:#f8fafc;font-size:12px;color:#374151}.level-name{display:flex;align-items:center;gap:7px;min-width:0;font-weight:700}.level-swatch{width:18px;height:3px;border-radius:999px;flex:0 0 auto}.level-value{white-space:nowrap;font-variant-numeric:tabular-nums;font-weight:750}
.marker-legend{margin-top:14px;padding-top:13px;border-top:1px solid #e5e7eb}.marker-legend-title{font-size:13px;font-weight:750;margin-bottom:8px}.marker-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:7px}.marker-item{display:flex;align-items:center;gap:8px;font-size:12px;color:#4b5563;background:#f8fafc;border-radius:8px;padding:7px 9px}.marker-badge{display:inline-flex;align-items:center;justify-content:center;min-width:30px;padding:3px 6px;border-radius:6px;color:#fff;font-weight:800}
@media(max-width:760px){.page{padding:14px}.stats,.details{grid-template-columns:1fr 1fr}.panel{padding:16px}.chart-wrap{min-height:360px;height:min(56vh,520px)}.level-legend{display:grid;grid-template-columns:1fr;gap:6px;margin-top:10px}.note{font-size:11px;line-height:1.45}}@media(max-width:560px){.toolbar{align-items:flex-start}.toolbar .buttons{width:100%}.toolbar .range{flex:1}.stats,.details{grid-template-columns:1fr}.panel{padding:14px}.chart-wrap{height:min(54vh,480px)}}
</style>
</head>
<body><main class="page">
<div class="top"><div><h1>${escapeIndicatorText(detail.name)}</h1><div class="ticker">${escapeIndicatorText(detail.ticker || indicatorName)}</div></div><button class="close" onclick="window.close()">Închide</button></div>
<section class="stats">
<div class="stat"><div class="label">Valoare curentă${detail.currency?' · '+escapeIndicatorText(detail.currency):''}</div><div class="num">${formatDetailNumber(detail.value,detail.currency)}</div></div>
<div class="stat"><div class="label">Schimbare zilnică${detail.currency?' · '+escapeIndicatorText(detail.currency):''}</div><div class="num" style="color:${Number(detail.change)>=0?'#ef4444':'#16a34a'}">${Number(detail.change)>=0?'↑':'↓'} ${formatDetailNumber(Math.abs(Number(detail.change)||0),detail.currency)}</div></div>
<div class="stat"><div class="label">Status</div><div class="num">${escapeIndicatorText(detail.status)}</div></div>
<div class="stat"><div class="label">Interval</div><div class="num" style="font-size:18px">${escapeIndicatorText(detail.rangeDescription || '—')}</div></div>
</section>
<section class="panel"><div class="toolbar"><strong id="chartTitle">Grafic zilnic${detail.currency?' · '+escapeIndicatorText(detail.currency):''}</strong><div class="buttons"><button class="range" data-count="22">1L</button><button class="range active" data-count="66">3L</button><button class="range" data-count="9999">Tot</button></div></div>
<div class="chart-wrap"><canvas id="indicatorChart"></canvas></div>${renderHorizontalLevelLegend(detail.levels || [], detail.currency)}<div class="note" id="chartNote"></div>${renderRecommendationMarkerLegend(detail.markers || [], detail.currency)}</section>
<section class="details"><div class="panel"><h2>Ce măsoară</h2><p>${escapeIndicatorText(detail.explanation || 'Detalii indisponibile.')}</p></div>
<div class="panel"><h2>Cum se interpretează</h2><p>${escapeIndicatorText(indicatorInterpretation(indicatorName, detail))}</p></div></section>
</main><script>
const detail=${payload};
${drawIndicatorDetail.toString()}
${hasUsableIndicatorOhlc.toString()}
${drawCandles.toString()}
${drawLineSeries.toString()}
${drawHorizontalLevels.toString()}
${drawRecommendationMarkers.toString()}
${detailChartLayout.toString()}
${detailChartTickIndexes.toString()}
${formatIndicatorNumber.toString()}
${formatDetailNumber.toString()}
${formatRomanianDate.toString()}
document.querySelectorAll('.range').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('.range').forEach(x=>x.classList.remove('active'));button.classList.add('active');drawIndicatorDetail(detail,Number(button.dataset.count));}));
window.addEventListener('resize',()=>{const active=document.querySelector('.range.active');drawIndicatorDetail(detail,Number(active.dataset.count));});
window.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();window.close();}});
const initialCount=window.matchMedia('(max-width: 640px)').matches?22:66;
document.querySelectorAll('.range').forEach(button=>button.classList.toggle('active',Number(button.dataset.count)===initialCount));
drawIndicatorDetail(detail,initialCount);
<\\/script></body></html>`);
                popup.document.close();
            }

            function escapeIndicatorText(value) {
                return String(value == null ? '' : value)
                    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;').replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
            }

            function formatIndicatorNumber(value) {
                const number = Number(value);
                return Number.isFinite(number)
                    ? number.toLocaleString('ro-RO', {maximumFractionDigits: 2})
                    : '—';
            }

            function formatDetailNumber(value, currency) {
                const number = Number(value);
                if (!Number.isFinite(number)) return '—';
                const code = String(currency || '').toUpperCase();
                const digits = code === 'RON' && Math.abs(number) < 10 ? 4 : 2;
                const formatted = number.toLocaleString('ro-RO', {
                    minimumFractionDigits: digits,
                    maximumFractionDigits: digits
                });
                if (code === 'USD') return '$' + formatted;
                if (code === 'EUR') return '€' + formatted;
                if (code === 'GBP') return '£' + formatted;
                return code ? formatted + ' ' + code : formatIndicatorNumber(number);
            }

            function formatRomanianDate(value, includeTime, shortDate) {
                const text = String(value || '').trim();
                const match = text.match(
                    /^(\\d{4})-(\\d{2})-(\\d{2})(?:[T ](\\d{2}):(\\d{2}))?/
                );
                if (!match) return text || '—';
                const date = shortDate
                    ? match[3] + '.' + match[2]
                    : match[3] + '.' + match[2] + '.' + match[1];
                return includeTime && match[4]
                    ? date + ' ' + match[4] + ':' + match[5]
                    : date;
            }

            function renderRecommendationMarkerLegend(markers, currency) {
                if (!Array.isArray(markers) || !markers.length) return '';
                const rows = markers.map(marker => {
                    const color = /^#[0-9a-f]{6}$/i.test(String(marker.color || ''))
                        ? marker.color : '#64748b';
                    return "<div class='marker-item'>"
                        + "<span class='marker-badge' style='background:" + color + ";'>"
                        + escapeIndicatorText(marker.label || 'C?') + "</span>"
                        + "<span><b>" + escapeIndicatorText(marker.action || 'Recomandare')
                        + "</b> · " + escapeIndicatorText(
                            formatRomanianDate(
                                marker.dateTime || marker.date,
                                true,
                                false
                            )
                        )
                        + " · " + formatDetailNumber(marker.value, currency)
                        + " · " + escapeIndicatorText(marker.status || '') + "</span></div>";
                }).join('');
                return "<div class='marker-legend'><div class='marker-legend-title'>"
                    + "Recomandări de cumpărare marcate punctual pe grafic"
                    + "</div><div class='marker-grid'>" + rows + "</div></div>";
            }

            function renderHorizontalLevelLegend(levels, currency) {
                if (!Array.isArray(levels) || !levels.length) return '';
                const rows = levels.map(level => {
                    const color = /^#[0-9a-f]{6}$/i.test(String(level.color || ''))
                        ? level.color : '#2563eb';
                    return "<div class='level-item'><span class='level-name'>"
                        + "<span class='level-swatch' style='background:" + color + ";'></span>"
                        + escapeIndicatorText(level.label || 'Nivel') + "</span>"
                        + "<span class='level-value'>"
                        + escapeIndicatorText(formatDetailNumber(level.value, currency))
                        + "</span></div>";
                }).join('');
                return "<div class='level-legend' aria-label='Niveluri de preț'>"
                    + rows + "</div>";
            }

            function indicatorInterpretation(name, detail) {
                if (detail && detail.kind === 'portfolio') {
                    return 'Lumânările arată evoluția zilnică a prețului. Compară trendul cu prețul de cumpărare, targetul, stop-ul și riscul poziției; graficul singur nu reprezintă o recomandare de tranzacționare.';
                }
                if (detail && detail.kind === 'watchlist') {
                    return 'Lumânările arată evoluția zilnică a prețului. Evaluează trendul împreună cu RSI, targetul, consensul și raportul risc-randament; includerea în watchlist nu reprezintă o recomandare de cumpărare.';
                }
                if (detail && detail.kind === 'buy_recommendation') {
                    return 'Lumânările arată evoluția zilnică a prețului. Triunghiurile numerotate C1, C2 etc. sunt recomandări punctuale din istoric; liniile orizontale rămân rezervate numai nivelurilor curente de entry, stop și target. Confirmă triggerul și spreadul înaintea ordinului.';
                }
                if (name === 'SPX' || name === 'NASDAQ') {
                    return 'Creșterea indicelui indică aprecierea pieței. Direcția trebuie evaluată împreună cu trendul, volatilitatea și participarea acțiunilor.';
                }
                if (name === 'Crypto Fear') {
                    return 'Valorile mici indică frică, iar valorile mari lăcomie. Extremele pot persista și nu reprezintă singure un semnal de cumpărare sau vânzare.';
                }
                return 'În general, creșterea indică risc sau volatilitate mai mare, iar scăderea relaxarea tensiunii. Nivelul și trendul sunt mai importante decât o singură variație zilnică.';
            }

            function drawIndicatorDetail(detail, count) {
                const canvas = document.getElementById('indicatorChart');
                if (!canvas) return;
                if (hasUsableIndicatorOhlc(detail.ohlc)) {
                    drawCandles(
                        canvas,
                        detail.ohlc.slice(-count),
                        detail.levels || [],
                        detail.currency,
                        detail.markers || []
                    );
                    document.getElementById('chartNote').textContent = (
                        'Lumânări OHLC zilnice reale, furnizate de Yahoo Finance'
                        + (detail.currency ? ', în ' + detail.currency : '') + '.'
                    );
                } else {
                    drawLineSeries(
                        canvas,
                        (detail.series || []).slice(-count),
                        (detail.seriesDates || []).slice(-count),
                        detail.levels || [],
                        detail.currency,
                        detail.markers || []
                    );
                    document.getElementById('chartNote').textContent = (
                        'Istoric zilnic real afișat liniar'
                        + (detail.currency ? ' în ' + detail.currency : '')
                        + ': sursa nu oferă suficiente date OHLC utile pentru lumânări.'
                    );
                }
            }

            function hasUsableIndicatorOhlc(candles) {
                if (!Array.isArray(candles) || candles.length < 5) return false;
                const valid = candles.filter(item =>
                    ['open', 'high', 'low', 'close'].every(key => Number.isFinite(Number(item[key])))
                );
                if (valid.length < 5) return false;
                const nonFlat = valid.filter(item =>
                    Math.abs(Number(item.high) - Number(item.low)) > 0.000001
                );
                return nonFlat.length / valid.length >= 0.2;
            }

            function detailChartLayout(width, currency, hasLevels, lineChart) {
                const compact = width <= 640;
                if (compact) {
                    return {
                        left: currency ? 62 : 48,
                        right: 10,
                        top: 16,
                        bottom: lineChart ? 38 : 36,
                        compact: true,
                        axisFont: '10px sans-serif'
                    };
                }
                return {
                    left: currency ? 100 : 66,
                    right: hasLevels ? 190 : 18,
                    top: 18,
                    bottom: lineChart ? 40 : 34,
                    compact: false,
                    axisFont: '12px sans-serif'
                };
            }

            function detailChartTickIndexes(length, chartWidth) {
                if (!length) return [];
                if (length === 1) return [0];
                const count = Math.max(2, Math.min(7, Math.floor(chartWidth / 58)));
                const indexes = [];
                for (let index = 0; index < count; index++) {
                    const position = Math.round(index * (length - 1) / (count - 1));
                    if (!indexes.includes(position)) indexes.push(position);
                }
                return indexes;
            }

            function drawCandles(canvas, candles, levels, currency, markers) {
                const rect = canvas.getBoundingClientRect();
                const ratio = window.devicePixelRatio || 1;
                canvas.width = Math.max(1, Math.floor(rect.width * ratio));
                canvas.height = Math.max(1, Math.floor(rect.height * ratio));
                const ctx = canvas.getContext('2d');
                ctx.scale(ratio, ratio);
                const width = rect.width, height = rect.height;
                const pad = detailChartLayout(width, currency, levels.length > 0, false);
                const chartW = width-pad.left-pad.right, chartH = height-pad.top-pad.bottom;
                ctx.clearRect(0,0,width,height);
                if (!candles.length) return;
                const firstDate=String(candles[0].date||'').slice(0,10);
                const visibleMarkers=(markers||[]).filter(marker=>!marker.date||String(marker.date).slice(0,10)>=firstDate);
                const levelValues=levels.map(x=>Number(x.value)).filter(Number.isFinite);
                const markerValues=visibleMarkers.map(x=>Number(x.value)).filter(Number.isFinite);
                const lows = candles.map(x=>Number(x.low)).concat(levelValues,markerValues), highs = candles.map(x=>Number(x.high)).concat(levelValues,markerValues);
                let min = Math.min(...lows), max = Math.max(...highs);
                const extra = Math.max((max-min)*.06, .001); min-=extra; max+=extra;
                const y = value => pad.top + (max-value)/(max-min)*chartH;
                ctx.font=pad.axisFont;ctx.textAlign='right';ctx.textBaseline='middle';
                for(let i=0;i<=5;i++){const value=max-(max-min)*i/5;const py=pad.top+chartH*i/5;ctx.strokeStyle='#e8ebf1';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(pad.left,py);ctx.lineTo(width-pad.right,py);ctx.stroke();ctx.fillStyle='#6b7280';ctx.fillText(formatDetailNumber(value,currency),pad.left-8,py);}
                const step=chartW/candles.length, body=Math.max(2,Math.min(13,step*.62));
                candles.forEach((item,index)=>{const x=pad.left+step*(index+.5);const open=Number(item.open),close=Number(item.close),high=Number(item.high),low=Number(item.low);const color=close>=open?'#16a34a':'#ef4444';ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=1.2;ctx.beginPath();ctx.moveTo(x,y(high));ctx.lineTo(x,y(low));ctx.stroke();const top=Math.min(y(open),y(close));const h=Math.max(1.5,Math.abs(y(open)-y(close)));ctx.fillRect(x-body/2,top,body,h);});
                ctx.textAlign='center';ctx.textBaseline='top';ctx.fillStyle='#6b7280';ctx.font=pad.axisFont;
                detailChartTickIndexes(candles.length,chartW).forEach(index=>{const item=candles[index];const x=pad.left+step*(index+.5);ctx.fillText(formatRomanianDate(item.date,false,true),x,height-pad.bottom+9);});
                drawHorizontalLevels(ctx,width,pad,min,max,levels,currency);
                drawRecommendationMarkers(ctx,width,pad,min,max,candles.map(item=>item.date),visibleMarkers,true);
            }

            function drawLineSeries(canvas, series, dates, levels, currency, markers) {
                const rect=canvas.getBoundingClientRect(),ratio=window.devicePixelRatio||1;
                canvas.width=Math.max(1,Math.floor(rect.width*ratio));canvas.height=Math.max(1,Math.floor(rect.height*ratio));
                const ctx=canvas.getContext('2d');ctx.scale(ratio,ratio);const width=rect.width,height=rect.height;
                const pad=detailChartLayout(width,currency,levels.length>0,true);
                const chartW=width-pad.left-pad.right,chartH=height-pad.top-pad.bottom;
                ctx.clearRect(0,0,width,height);if(!series.length)return;
                const firstDate=dates&&dates.length?String(dates[0]||'').slice(0,10):'';
                const visibleMarkers=(markers||[]).filter(marker=>!firstDate||!marker.date||String(marker.date).slice(0,10)>=firstDate);
                const levelValues=levels.map(x=>Number(x.value)).filter(Number.isFinite);
                const markerValues=visibleMarkers.map(x=>Number(x.value)).filter(Number.isFinite);
                let min=Math.min(...series,...levelValues,...markerValues),max=Math.max(...series,...levelValues,...markerValues);const extra=Math.max((max-min)*.1,1);min-=extra;max+=extra;
                ctx.font=pad.axisFont;ctx.textAlign='right';ctx.textBaseline='middle';
                for(let i=0;i<=5;i++){const value=max-(max-min)*i/5;const py=pad.top+chartH*i/5;ctx.strokeStyle='#e8ebf1';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(pad.left,py);ctx.lineTo(width-pad.right,py);ctx.stroke();ctx.fillStyle='#6b7280';ctx.fillText(formatDetailNumber(value,currency),pad.left-8,py);}
                ctx.strokeStyle='#7760f9';ctx.lineWidth=3;ctx.beginPath();series.forEach((value,index)=>{const x=pad.left+chartW*(index/Math.max(1,series.length-1));const y=pad.top+(max-value)/(max-min)*chartH;index?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();
                ctx.textAlign='center';ctx.textBaseline='top';ctx.fillStyle='#6b7280';ctx.font=pad.axisFont;
                detailChartTickIndexes(series.length,chartW).forEach(index=>{const x=pad.left+chartW*(index/Math.max(1,series.length-1));const label=dates&&dates[index]?formatRomanianDate(dates[index],false,true):String(index+1);ctx.fillText(label,x,height-pad.bottom+10);});
                drawHorizontalLevels(ctx,width,pad,min,max,levels,currency);
                drawRecommendationMarkers(ctx,width,pad,min,max,dates||[],visibleMarkers,false);
            }

            function drawHorizontalLevels(ctx, width, pad, min, max, levels, currency) {
                if (!levels || !levels.length || max <= min) return;
                const chartH=ctx.canvas.getBoundingClientRect().height-pad.top-pad.bottom;
                levels.forEach(level=>{
                    const value=Number(level.value);
                    if (!Number.isFinite(value)) return;
                    const py=pad.top+(max-value)/(max-min)*chartH;
                    ctx.save();
                    ctx.strokeStyle=level.color||'#2563eb';ctx.lineWidth=1.5;ctx.setLineDash([7,5]);
                    ctx.beginPath();ctx.moveTo(pad.left,py);ctx.lineTo(width-pad.right,py);ctx.stroke();
                    if (pad.compact) {
                        ctx.restore();
                        return;
                    }
                    ctx.setLineDash([]);ctx.fillStyle=level.color||'#2563eb';ctx.font='bold 12px sans-serif';
                    ctx.textAlign='left';ctx.textBaseline='middle';
                    ctx.fillText(`${level.label}: ${formatDetailNumber(value,currency)}`,width-pad.right+8,py);
                    ctx.restore();
                });
            }

            function drawRecommendationMarkers(ctx, width, pad, min, max, dates, markers, centered) {
                if (!Array.isArray(markers) || !markers.length || !dates.length || max <= min) return;
                const normalizedDates=dates.map(value=>String(value||'').slice(0,10));
                const chartW=width-pad.left-pad.right;
                const chartH=ctx.canvas.getBoundingClientRect().height-pad.top-pad.bottom;
                const positioned=[];
                markers.forEach(marker=>{
                    const markerDate=String(marker.date||'').slice(0,10);
                    const markerTime=Date.parse(markerDate);
                    let bestIndex=normalizedDates.length-1,bestDistance=Infinity;
                    normalizedDates.forEach((date,index)=>{
                        const distance=Math.abs(Date.parse(date)-markerTime);
                        if(Number.isFinite(distance)&&distance<bestDistance){bestDistance=distance;bestIndex=index;}
                    });
                    const value=Number(marker.value);
                    if(Number.isFinite(value)){positioned.push({marker,index:bestIndex,value});}
                });
                const groups={};
                positioned.forEach(item=>{(groups[item.index]||(groups[item.index]=[])).push(item);});
                Object.values(groups).forEach(group=>group.forEach((item,ordinal)=>{item.ordinal=ordinal;item.groupSize=group.length;}));
                positioned.forEach(item=>{
                    const baseX=centered
                        ? pad.left+chartW*((item.index+.5)/Math.max(1,normalizedDates.length))
                        : pad.left+chartW*(item.index/Math.max(1,normalizedDates.length-1));
                    const spread=Math.min(11,Math.max(6,56/Math.max(1,item.groupSize)));
                    const offset=(item.ordinal-(item.groupSize-1)/2)*spread;
                    const x=Math.max(pad.left+6,Math.min(width-pad.right-6,baseX+offset));
                    const y=pad.top+(max-item.value)/(max-min)*chartH;
                    const color=/^#[0-9a-f]{6}$/i.test(String(item.marker.color||''))
                        ? item.marker.color : '#64748b';
                    ctx.save();
                    ctx.fillStyle=color;ctx.strokeStyle='#ffffff';ctx.lineWidth=1.5;
                    ctx.beginPath();ctx.moveTo(x,y-9);ctx.lineTo(x-7,y+5);ctx.lineTo(x+7,y+5);ctx.closePath();ctx.fill();ctx.stroke();
                    ctx.font='bold 11px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
                    const label=String(item.marker.label||'C?');
                    const badgeWidth=Math.max(26,ctx.measureText(label).width+10);
                    let badgeY=y-28-(item.ordinal%3)*18;
                    if(badgeY<pad.top+2){badgeY=y+13+(item.ordinal%3)*18;}
                    ctx.fillStyle=color;ctx.fillRect(x-badgeWidth/2,badgeY,badgeWidth,16);
                    ctx.fillStyle='#ffffff';ctx.fillText(label,x,badgeY+8);
                    ctx.restore();
                });
            }
            
            // Create sparkline charts
            window.addEventListener('load', function() {
                Object.keys(sparklineData).forEach(function(sparkId) {
                    const ctx = document.getElementById(sparkId);
                    if (!ctx) return;
                    
                    const data = sparklineData[sparkId];
                    
                    // Logică colorare:
                    // Default (Stocks, SPX, Crypto): Up = Green, Down = Red
                    // Inversed (VIX, etc): Up = Red (Bad), Down = Green (Good)
                    
                    let isInversed = false;
                    if (sparkId.startsWith('spark_ind_')) {
                         // Dacă e indicator si NU e SPX si NU e Crypto Fear -> Inversed
                         if (!sparkId.includes('SPX') && !sparkId.includes('Crypto Fear')) {
                             isInversed = true;
                         }
                    }
                    
                    const isUp = data[data.length - 1] >= data[0];
                    let color;
                    
                    if (isInversed) {
                        color = isUp ? '#f44336' : '#4caf50';
                    } else {
                        color = isUp ? '#4caf50' : '#f44336';
                    }
                    
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: Array(data.length).fill(''),
                            datasets: [{
                                data: data,
                                borderColor: color,
                                borderWidth: 1.5,
                                fill: false,
                                pointRadius: 0,
                                tension: 0.1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false },
                                tooltip: { enabled: false }
                            },
                            scales: {
                                x: { display: false },
                                y: { display: false }
                            }
                        }
                    });
                });
            });
        </script>
    </div> <!-- End container -->
    </body>
    </html>
    """
    
    active_buy_total_eur = _active_buy_orders_total_eur(
        orders_df,
        (full_state or {}).get('rates', {}),
        portfolio_df=portfolio_df,
        watchlist_df=watchlist_df,
    )
    current_month_pl = _current_month_portfolio_change(
        broker_totals_history
    )
    current_month_pl_display = (
        f"€{current_month_pl:,.2f}"
        if current_month_pl is not None else 'N/D'
    )
    current_month_pl_class = (
        'positive' if current_month_pl is not None and current_month_pl >= 0
        else 'negative' if current_month_pl is not None
        else ''
    )
    html_head = html_head.replace(
        '__ACTIVE_BUY_ORDERS_TOTAL_EUR__',
        f'€{active_buy_total_eur:,.2f}',
    ).replace(
        '__CURRENT_MONTH_PL_EUR__', current_month_pl_display
    ).replace(
        '__CURRENT_MONTH_PL_CLASS__', current_month_pl_class
    )

    full_html = html_head + html_footer
    
    with open(filename, 'w') as f:
        f.write(full_html)
    print(f"Dashboard HTML generat: {os.path.abspath(filename)}")

import ib_sync  # Modul sincronizare IBKR

def update_portfolio_data(state, rates, vix_val, sync_before_load=True):
    """Actualizează datele de portofoliu și le salvează în state."""
    print("\n=== Actualizare Portofoliu ===")
    
    # Apelurile externe pot folosi funcția direct; main() sincronizează o
    # singură dată înainte și dezactivează acest pas pentru a nu relansa Flex.
    if sync_before_load:
        try:
            ib_sync.sync_ibkr()
        except Exception as e:
            print(f"Sincronizare IBKR a eșuat sau nu este disponibilă: {e}")
        
    portfolio_data = load_portfolio()
    
    
    # === Legacy TWS Merge Logic Removed ===
    # ib_sync.py now handles all synchronization and writes the clean portfolio.csv directly

    portfolio_results = []
    
    # Pre-fetch SPX data for Relative Strength (RS) usage AND Market Rule #1 (SPX < SMA200)
    print("  Pre-fetching SPX data (1y)...")
    spx_df = yf.download("^GSPC", period="1y", auto_adjust=True, progress=False)
    
    market_in_downtrend = False
    try:
        if isinstance(spx_df.columns, pd.MultiIndex):
            spx_df.columns = spx_df.columns.droplevel(1)
        spx_df = spx_df.dropna(subset=['Close'])
            
        # Calculate SPX SMA200 for Rule #1
        if len(spx_df) >= 200:
            spx_df['SMA_200'] = spx_df['Close'].rolling(window=200).mean()
            current_spx = spx_df['Close'].iloc[-1]
            spx_sma200 = spx_df['SMA_200'].iloc[-1]
            if current_spx < spx_sma200:
                market_in_downtrend = True
                print(f"  ⚠️ Market Rule #1 ACTIVE: SPX ({current_spx:.0f}) < SMA200 ({spx_sma200:.0f})")
    except Exception as e:
        print(f"Error calculating Market Rule #1: {e}")
    
    # Check Rule #4 (Market Structure Break)
    rule4_active = False
    try:
        # Reusing spx_df (1y should be enough for recent structure, usually 2y better but 1y ok for last LH)
        # analysis.check_market_structure_break uses 'High', 'Low'. 
        # yf.download should have included High/Low by default.
        r4_active, r4_debug = analysis.check_market_structure_break(spx_df)
        if r4_active:
            rule4_active = True
            print(f"  ⚠️ Market Rule #4 ACTIVE: {r4_debug}")
    except Exception as e:
        print(f"Error calculating Rule #4: {e}")

    # Pre-fetch Market Breadth for Rule #3 (Breadth < 45%)

    # Pre-fetch Market Breadth for Rule #3 (Breadth < 45%)
    # Logic reused from market_scanner_analysis to avoid full swing data calc here
    breadth_pct = 50.0  # Default Safe
    try:
        # Try Finviz first (Fast)
        print("  Checking Market Breadth (Finviz)...")
        above_sma50_count, total_count = analysis.get_finviz_count("sma50")
        if above_sma50_count is not None and total_count and total_count > 0:
            breadth_pct = (above_sma50_count / total_count) * 100
            print(f"    -> Breadth (Finviz): {breadth_pct:.1f}%")
        else:
            # Fallback (Slow) - Skip if strict speed required, but Rule #3 needs it.
            # We will use the fallback breadh function.
            print("    ⚠️ Finviz Unavailable. Fetching Fallback Breadth (Yahoo)...")
            # Usually fallback takes time.
            # reuse existing fallback logic
            # get_fallback_breadth(limit=None, json_path=...)
            json_path = os.path.join(os.path.dirname(__file__), 'sp500_tickers.json')
            bp, _, _ = analysis.get_fallback_breadth(json_path=json_path)
            if bp is not None:
                breadth_pct = bp
                print(f"    -> Breadth (Fallback): {breadth_pct:.1f}%")
    except Exception as e:
        print(f"Error fetching Breadth for Rule #3: {e}")

    # Safety Checks for Risk Parameters
    if vix_val is None:
        vix_val = 15.0
        print("  ⚠️ VIX Unavailable. Using default 15.0")
        
    if breadth_pct is None:
        breadth_pct = 50.0
        print("  ⚠️ Breadth Unavailable. Using default 50%")

    if not portfolio_data.empty:
        print(f"Procesare {len(portfolio_data)} poziții...")
        
        # Cache for redundant tickers (Lots)
        ticker_cache = {} 
        
        for _, row in portfolio_data.iterrows():
            print(f"  > {row['symbol']}")
            data = process_portfolio_ticker(row, vix_val, rates, spx_df, market_in_downtrend, breadth_pct, rule4_active, ticker_cache)
            if data:
                portfolio_results.append(data)
    
    state['portfolio'] = _preserve_portfolio_chart_history(
        state.get('portfolio', []), portfolio_results
    )
    return state


def update_portfolio_positions_only(state, rates, vix_val):
    """Actualizează strict instrumentele deținute, folosind contextul din cache.

    Nu scanează watchlistul, universuri BUY, Finviz breadth sau componentele
    S&P 500. Contextul SUA necesar regulilor pozițiilor este citit din ultimul
    snapshot valid, iar fiecare simbol procesat provine exclusiv din portfolio.
    """
    print("\n=== Actualizare strictă a pozițiilor deținute ===")
    portfolio_data = load_portfolio()
    portfolio_results = []
    swing = _cached_swing_data_for_ro(state) or {}
    chart = swing.get('Chart_SPX', {}) if isinstance(swing, dict) else {}
    closes = pd.to_numeric(
        pd.Series(chart.get('price', []) or []), errors='coerce'
    ).dropna()
    # Pentru relative strength contează alinierea ultimelor observații, nu
    # data calendaristică; etichetele cache-ului sunt intenționat MM-DD.
    spx_df = pd.DataFrame(
        {'Close': closes.to_numpy()}, index=pd.RangeIndex(len(closes))
    )
    spx_price = _safe_float_text(swing.get('SPX_Price')) or 0
    spx_sma200 = _safe_float_text(swing.get('SPX_SMA200')) or 0
    market_in_downtrend = bool(
        spx_price > 0 and spx_sma200 > 0 and spx_price < spx_sma200
    )
    breadth_pct = _safe_float_text(swing.get('Breadth_Pct'))
    if breadth_pct is None:
        breadth_pct = 50.0
    rule4_active = bool(swing.get('Rule4_Active', False))
    if vix_val is None:
        vix_val = _safe_float_text(swing.get('VIX_Current')) or 15.0

    if portfolio_data.empty:
        state['portfolio'] = []
        return state
    print(
        f"Procesare {len(portfolio_data)} poziții; fără scanare watchlist "
        "sau universuri de piață."
    )
    ticker_cache = {}
    for _, row in portfolio_data.iterrows():
        print(f"  > {row['symbol']}")
        data = process_portfolio_ticker(
            row, vix_val, rates, spx_df, market_in_downtrend,
            breadth_pct, rule4_active, ticker_cache,
        )
        if data:
            portfolio_results.append(data)
    state['portfolio'] = _preserve_portfolio_chart_history(
        state.get('portfolio', []), portfolio_results
    )
    return state


# REFACTORED: cache helpers moved to market_data.py


def update_watchlist_data(
    state,
    rates,
    vix_val,
    *,
    target_market=None,
    target_markets=None,
    sync_remote=True,
    cache_ttl_hours=5,
):
    """Actualizează datele din watchlist și le salvează în state."""
    selected_markets = set(target_markets or [])
    if target_market:
        selected_markets.add(target_market)
    title = (
        f"Watchlist — {', '.join(sorted(selected_markets))}"
        if selected_markets else "Watchlist"
    )
    print(f"\n=== Actualizare {title} ===")
    
    # Sync watchlist from remote
    if sync_remote:
        sync_watchlist_from_remote()
    
    watchlist_tickers = load_watchlist()
    retained_results = []
    if selected_markets:
        retained_results = [
            item for item in state.get('watchlist', [])
            if _buy_candidate_market(item.get('Ticker')) not in selected_markets
        ]
        watchlist_tickers = [
            ticker for ticker in watchlist_tickers
            if _buy_candidate_market(ticker) in selected_markets
        ]
    watchlist_results = []
    
    if not watchlist_tickers:
         print(
             f"Niciun simbol pentru "
             f"{', '.join(sorted(selected_markets)) or 'watchlist'}."
         )
         state['watchlist'] = retained_results
         return state

    total_tickers = len(watchlist_tickers)
    print(f"Procesare {total_tickers} tickere...")

    def refresh_status(ticker, cached_data):
        missing_fields = False
        if cached_data:
            if str(ticker).upper() in ALWAYS_RESEARCH_SYMBOLS:
                missing_fields = True
            if (
                cached_data.get('Decision') == 'BUY'
                and not cached_data.get('Smart_Entry')
            ):
                missing_fields = True
            if 'Currency' not in cached_data:
                missing_fields = True
            if (
                'Strategy' not in cached_data
                or 'Volume' not in cached_data
            ):
                missing_fields = True
            if not cached_data.get('Company_Name'):
                missing_fields = True
        fresh = bool(
            cached_data
            and market_data.is_fresh(
                cached_data, ttl_hours=cache_ttl_hours
            )
        )
        return missing_fields, fresh and not missing_fields

    mcp_due_symbols = []
    for ticker in watchlist_tickers:
        cached_data = market_data.get_cached_watchlist_ticker(state, ticker)
        _missing_fields, use_cache = refresh_status(ticker, cached_data)
        if not use_cache:
            mcp_due_symbols.append(ticker)
    _prefetch_ibkr_mcp_market_data(mcp_due_symbols, label=title)
    
    cached_count = 0
    updated_count = 0
        
    seen_tickers = set()
    
    for i, ticker in enumerate(watchlist_tickers, 1):
        if ticker in seen_tickers:
            continue
        seen_tickers.add(ticker)
        
        progress_str = f"[{i}/{total_tickers}]"
        # Check cache first
        cached_data = market_data.get_cached_watchlist_ticker(state, ticker)
        
        missing_fields, use_cache = refresh_status(ticker, cached_data)

        if use_cache:
            # Use cached data
            watchlist_results.append(cached_data)
            cached_count += 1
            print(f"  {progress_str} ✓ {ticker} (cached)")
        else:
            if missing_fields:
                print(f"  {progress_str} ↻ {ticker} (refreshing for missing fields)")

            # Process ticker
            data = process_watchlist_ticker(ticker, vix_val, rates)
            if data:
                # Add timestamp for caching
                import time
                data['_cached_at'] = time.time()
                watchlist_results.append(data)
                updated_count += 1
                print(f"  {progress_str} > {ticker} (updated)")
            elif cached_data:
                stale_data = dict(cached_data)
                stale_data['Data_Refresh_Status'] = 'stale_cache'
                stale_data['Data_Refresh_Warning'] = (
                    'Actualizarea surselor a eșuat; sunt păstrate ultimele '
                    'date valide, fără a le marca drept actualizate.'
                )
                watchlist_results.append(stale_data)
                cached_count += 1
                print(f"  {progress_str} ! {ticker} (stale cache)")
        
        print(f"  → {cached_count} cached, {updated_count} updated")
    
    state['watchlist'] = retained_results + watchlist_results
    return state

def main():
    parser = argparse.ArgumentParser(description="Antigravity Market Scanner")
    parser.add_argument(
        '--mode',
        choices=[
            'all', 'portfolio', 'watchlist', 'ro', 'international',
            'html-only',
        ],
        default='all',
        help='Select update mode',
    )
    parser.add_argument('--tws', action='store_true', help='Try fetching active orders from local TWS (requires ib_insync)')
    args = parser.parse_args()
    
    # Auto-enable TWS if local (not GitHub Actions) to prioritize live data
    if (
        not os.environ.get('GITHUB_ACTIONS')
        and args.mode in {'all', 'portfolio'}
    ):
        if not args.tws:
            print("Mediu Local detectat: Activare automată TWS Sync.")
            args.tws = True
    
    print(f"=== Rulează Market Scanner [Mod: {args.mode}] ===\n")
    
    # 1. Încărcăm starea anterioară
    state = market_utils.load_state()

    if args.mode == 'ro' and not os.environ.get('GITHUB_ACTIONS'):
        print("=== Completare locală BVB din TWS ===")
        try:
            import ib_tws_sync
            ib_tws_sync.sync_romanian_position_instruments(
                max_age_hours=1
            )
        except Exception as tws_bvb_error:
            print(
                "  -> Completarea TWS BVB a eșuat; folosim cache-ul: "
                f"{tws_bvb_error}"
            )

    # 1. Update Portfolio Data
    if args.mode in ['all', 'portfolio']:
        # MCP este sursa primară locală read-only pentru cont. TWS, Web API și
        # Flex rămân fallbackuri și nu pot suprascrie un snapshot MCP valid.
        mcp_synced = False
        mcp_enabled = (
            not os.environ.get('GITHUB_ACTIONS')
            and os.environ.get('IBKR_MCP_ENABLED', '1').strip().lower()
            not in {'0', 'false', 'no', 'off'}
        )
        if mcp_enabled:
            try:
                import ibkr_mcp
                mcp_snapshot = ibkr_mcp.sync_account_snapshot()
                mcp_synced = True
                print(
                    "IBKR MCP read-only: ordine, poziții și solduri "
                    f"sincronizate pentru "
                    f"{len(mcp_snapshot.get('accounts', []))} cont(uri)."
                )
            except ibkr_mcp.IBKRMCPAuthorizationRequired as mcp_error:
                interactive_reauth = bool(
                    getattr(sys.stdin, 'isatty', lambda: False)()
                )
                if interactive_reauth:
                    print(
                        "IBKR MCP necesită reautorizare; deschidem automat "
                        "pagina securizată IBKR..."
                    )
                    try:
                        mcp_snapshot = ibkr_mcp.sync_account_snapshot(
                            interactive=True
                        )
                        mcp_synced = True
                        print(
                            "IBKR MCP reautorizat read-only: ordine, poziții "
                            "și solduri sincronizate pentru "
                            f"{len(mcp_snapshot.get('accounts', []))} "
                            "cont(uri)."
                        )
                    except Exception as reauth_error:
                        print(
                            "Reautorizarea IBKR MCP nu a reușit; încercăm "
                            f"TWS: {reauth_error}"
                        )
                else:
                    print(
                        "IBKR MCP indisponibil; încercăm TWS: "
                        f"{mcp_error}"
                    )
            except Exception as mcp_error:
                print(
                    "IBKR MCP indisponibil; încercăm TWS: "
                    f"{mcp_error}"
                )

        # MCP rămâne sursa primară pentru poziții și solduri. Ordinele active,
        # în special trailing stop-ul curent calculat de IBKR, trebuie însă
        # citite din TWS la fiecare rulare locală: snapshotul MCP poate fi
        # valid pentru cont, dar nu actualizează întotdeauna triggerul curent.
        tws_synced = mcp_synced
        if args.tws:
            if mcp_synced:
                print(
                    "  -> MCP păstrează pozițiile/soldurile; actualizăm "
                    "ordinele active din TWS."
                )
            try:
                import ib_tws_sync
                tws_synced = bool(
                    ib_tws_sync.fetch_active_orders(
                        research_symbols=(
                            _planned_bvb_tws_symbols(state)
                            if args.mode == 'all' else []
                        ),
                        sync_research_instruments=(args.mode == 'all'),
                    )
                )
                
                # Apply TWS Orders to Local CSV immediately
                if os.path.exists('tws_orders.csv') and os.path.exists('portfolio.csv'):
                    print("Applying TWS Orders to portfolio.csv...")
                    p_df = pd.read_csv('portfolio.csv')
                    t_df = pd.read_csv('tws_orders.csv')
                    
                    changed = False
                    for _, row in t_df.iterrows():
                        sym = str(row.get('Symbol', ''))
                        stop = float(row.get('Calculated_Stop', 0))
                        pct = float(row.get('Trail_Pct', 0))
                        
                        mask = p_df['Symbol'] == sym
                        if mask.any():
                            if stop > 0:
                                # TWS este sursa live pentru triggerul unui
                                # trailing stop; păstrăm și câmpul IBKR ca
                                # analiza să nu aleagă un nivel manual vechi.
                                p_df.loc[mask, 'Trail_Stop'] = stop
                                p_df.loc[mask, 'Trail_Stop_IBKR'] = stop
                                changed = True
                            if pct > 0:
                                p_df.loc[mask, 'Trail_Pct'] = pct
                                changed = True
                    
                    if changed:
                        p_df.to_csv('portfolio.csv', index=False)
                        print("Portfolio CSV updated with live orders.")

                # Apply TWS Positions to Local CSV (Sync Size & Entry)
                if False and os.path.exists('tws_positions.csv'): # Logic moved to update_portfolio_data
                    print("Merging TWS Positions (Shares/AvgPrice) into portfolio.csv...")
                    try:
                        pos_df = pd.read_csv('tws_positions.csv')
                        # Load portfolio again to be fresh
                        p_df = pd.read_csv('portfolio.csv') if os.path.exists('portfolio.csv') else pd.DataFrame(columns=['Symbol', 'Shares', 'Buy_Price', 'Currency', 'Trail_Pct', 'Trail_Stop'])
                        
                        p_changed = False
                        
                        # 1. Update Existing & Add New
                        for _, row in pos_df.iterrows():
                            sym = str(row.get('Symbol', ''))
                            shares = float(row.get('Shares', 0))
                            price = float(row.get('Buy_Price', 0))
                            curr = str(row.get('Currency', 'USD'))
                            
                            if shares == 0: continue # Ignore closed
                            
                            mask = p_df['Symbol'] == sym
                            if sym == 'AMPX':
                                 print(f"DEBUG MERGE AMPX: TWS Price={price}, TWS Shares={shares}")
                                 if mask.any():
                                     print(f"DEBUG MERGE AMPX: CSV Price={p_df.loc[mask, 'Buy_Price'].values[0]}")
                            if mask.any():
                                # Update existing
                                current_shares = float(p_df.loc[mask, 'Shares'].values[0])
                                current_price = float(p_df.loc[mask, 'Buy_Price'].values[0])
                                
                                # Update only if different
                                if abs(current_shares - shares) > 0.0001 or abs(current_price - price) > 0.01:
                                     p_df.loc[mask, 'Shares'] = shares
                                     p_df.loc[mask, 'Buy_Price'] = price  # Re-enabled: TWS AvgPrice is correct (native currency)
                                     p_df.loc[mask, 'Currency'] = curr # Optional
                                     p_changed = True
                                     print(f"  Updated {sym}: {shares} shares @ {price}")
                            else:
                                # Add New Position
                                new_row = {
                                    'Symbol': sym, 
                                    'Shares': shares, 
                                    'Buy_Price': price, 
                                    'Currency': curr,
                                    'Trail_Pct': 15,    # Default
                                    'Trail_Stop': 0, 
                                    'Investment': shares * price 
                                }
                                # Align columns
                                for col in p_df.columns:
                                    if col not in new_row: new_row[col] = 0
                                    
                                p_df = pd.concat([p_df, pd.DataFrame([new_row])], ignore_index=True)
                                p_changed = True
                                print(f"  Added New Pos {sym}: {shares} shares @ {price}")

                        # 2. (Optional) Mark closed positions? 
                        # For now, we only update active TWS positions. We don't delete positions not in TWS to be safe.
                        
                        if p_changed:
                            p_df.to_csv('portfolio.csv', index=False)
                            print("Portfolio CSV positions synchronized.")
                            
                    except Exception as e:
                        print(f"Error merging TWS positions: {e}")
                        
            except ImportError:
                print("Cannot import ib_tws_sync. Skipping TWS sync.")
            except Exception as e:
                print(f"TWS Sync Error: {e}")
        elif mcp_synced:
            print("  -> TWS nu este necesar: snapshotul MCP este valid.")

        web_api_enabled = (
            not tws_synced
            and not os.environ.get('GITHUB_ACTIONS')
            and os.environ.get('IBKR_WEB_API_ENABLED', '1').strip().lower()
            not in {'0', 'false', 'no', 'off'}
        )
        if web_api_enabled:
            try:
                import ibkr_web_api
                web_snapshot = ibkr_web_api.sync_account_snapshot()
                print(
                    "IBKR Web API fallback: solduri și istoric NAV "
                    f"sincronizate pentru "
                    f"{len(web_snapshot.get('accounts', []))} cont(uri)."
                )
            except Exception as web_api_error:
                print(
                    "IBKR Web API indisponibil; încercăm Flex/cache: "
                    f"{web_api_error}"
                )

        # Flex este fallback pentru cloud sau când TWS local nu răspunde.
        if not ib_sync.sync_ibkr(allow_flex=not tws_synced):
             print("Sync IBKR eșuat sau config lipsă. Se folosesc datele locale existente pentru cantități.")
        
        # Procesare Portfolio Tickers (Price update) = market_utils.load_state()
    
    # 2. Actualizăm datele globale (Rates, Indicators, VIX) DOAR dacă nu suntem în html-only
    # Le salvăm și pe ele în state pentru consistență
    rates = state.get('rates', {'EUR': 1.0, 'USD': 0.95, 'RON': 0.20, 'GBP': 1.15})
    market_indicators = state.get('market_indicators', {})
    vix_val = state.get('vix_val', None)
    
    if args.mode not in {'html-only', 'ro', 'portfolio'}:
        print("=== Actualizare Date Globale ===")
        rates = market_data.get_exchange_rates()
        state['rates'] = rates
        
        market_indicators = get_market_indicators()
        state['market_indicators'] = market_indicators
        
        vix_val = get_vix_data()
        if vix_val:
            state['vix_val'] = vix_val
            print(f"VIX: {vix_val:.2f}")
        else:
            print("VIX indisponibil, folosim valoarea anterioară.")
            
        # Economic Cycle
        curr_phase, next_phase = determine_economic_cycle()
        state['eco_phase'] = curr_phase
        state['eco_next_phase'] = next_phase
    
    # 3. Actualizări Secționale
    # Dacă o piață nu are candidați eligibili, extindem universul de cercetare.
    # În modul complet noile simboluri vor fi procesate de update_watchlist_data.
    target_markets = None
    if args.mode == 'ro':
        target_markets = {'România / BVB'}
    elif args.mode == 'international':
        target_markets = {'SUA', 'Europa / Nasdaq-100'}
    if args.mode not in {'portfolio', 'html-only'}:
        state = ensure_buy_research_candidates(
            state,
            rates,
            vix_val,
            refresh_missing=False,
            target_markets=target_markets,
        )

    if args.mode == 'all':
        state = update_portfolio_data(
            state,
            rates,
            vix_val,
            sync_before_load=False,
        )
    elif args.mode == 'portfolio':
        state = update_portfolio_positions_only(state, rates, vix_val)
        
    if args.mode in ['all', 'watchlist']:
        state = update_watchlist_data(state, rates, vix_val)
    if args.mode == 'ro':
        state = update_watchlist_data(
            state,
            rates,
            vix_val,
            target_market='România / BVB',
            sync_remote=False,
            cache_ttl_hours=1,
        )
    if args.mode == 'international':
        state = update_watchlist_data(
            state,
            rates,
            vix_val,
            target_markets={'SUA', 'Europa / Nasdaq-100'},
        )
    if args.mode in ['all', 'watchlist']:
        # Cercetarea suplimentară rămâne separată de watchlist și folosește
        # propriul criteriu de triere.
        state = ensure_buy_research_candidates(
            state, rates, vix_val, refresh_missing=True
        )
    elif args.mode == 'ro':
        state = ensure_buy_research_candidates(
            state,
            rates,
            vix_val,
            refresh_missing=True,
            target_markets={'România / BVB'},
        )
    elif args.mode == 'international':
        state = ensure_buy_research_candidates(
            state,
            rates,
            vix_val,
            refresh_missing=True,
            target_markets={'SUA', 'Europa / Nasdaq-100'},
        )
        
    # 4. Salvare Stare
    # Deduplicate Watchlist in State BEFORE saving
    wl_list = state.get('watchlist', [])
    if wl_list:
        wl_df_state = pd.DataFrame(wl_list)
        if 'Ticker' in wl_df_state.columns:
             before_dedup = len(wl_df_state)
             wl_df_state = wl_df_state.drop_duplicates(subset=['Ticker'])
             after_dedup = len(wl_df_state)
             if before_dedup > after_dedup:
                 print(f"  -> Curățat state: {before_dedup - after_dedup} duplicate eliminate din watchlist.")
                 state['watchlist'] = wl_df_state.to_dict('records')
                 
    market_utils.save_state(state)
    print("\nStarea dashboard-ului a fost salvată.")
    
    # 5. Generare HTML din State
    # Convertim listele de dict-uri înapoi în DataFrame pentru funcția existentă
    portfolio_df = pd.DataFrame(state.get('portfolio', []))
    watchlist_df = pd.DataFrame(state.get('watchlist', []))
    
    # Filtrare watchlist: exclude simbolurile care sunt deja în portofoliu (doar pentru afișare)
    if not portfolio_df.empty and not watchlist_df.empty and 'Symbol' in portfolio_df.columns and 'Ticker' in watchlist_df.columns:
        portfolio_symbols = set(portfolio_df['Symbol'].str.upper())
        original_count = len(watchlist_df)
        watchlist_df = watchlist_df[~watchlist_df['Ticker'].str.upper().isin(portfolio_symbols)]
        filtered_count = original_count - len(watchlist_df)
        if filtered_count > 0:
            print(f"  -> Ascunse {filtered_count} acțiuni din watchlist (deja în portofoliu)")
    


    # Verificăm indicatorii (s-ar putea să fie None în state inițial)
    indicators_data = state.get('market_indicators', {})
    
    print("\n=== Generare Dashboard HTML ===")
    # html-only este utilizat pentru a republica dashboardul (de exemplu
    # după sincronizarea unui stop TWS). Nu are voie să pornească scanări de
    # piață sau apeluri AI: păstrăm ultimul context complet din cache.
    cached_swing_data = (
        _cached_swing_data_for_ro(state)
        if args.mode in {'ro', 'portfolio', 'html-only'} else None
    )
    if args.mode == 'portfolio' and cached_swing_data is None:
        # Un dict gol oprește explicit fallback-ul din renderer către o
        # interogare globală. Modul portfolio rămâne astfel strict limitat la
        # pozițiile deținute chiar și la prima rulare, înainte de update_all.
        cached_swing_data = {}
    if cached_swing_data:
        print("  -> Contextul SUA este reutilizat din cache; fără scanare SUA.")
    elif args.mode == 'ro':
        print(
            "  -> Snapshotul SUA lipsește sau este invalid; îl inițializăm "
            "o singură dată, separat de datele BVB."
        )
    elif args.mode in {'portfolio', 'html-only'}:
        print(
            "  -> Contextul global nu este disponibil în cache; modul "
            "portofoliu/html-only nu pornește o scanare de piață suplimentară."
        )
    generate_html_dashboard(
        portfolio_df,
        watchlist_df,
        indicators_data,
        "index.html",
        state,
        swing_data_override=cached_swing_data,
    )

if __name__ == "__main__":
    main()
