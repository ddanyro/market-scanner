import requests
import pandas as pd
from io import StringIO
import datetime
import yfinance as yf
import numpy as np
import json
import os
import re
import html
import hashlib
import math
import tempfile
import urllib.parse
from bs4 import BeautifulSoup


def _utc_now_naive():
    """UTC fără timezone pentru compatibilitate cu cache-urile istorice naive."""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


ECONOMIC_CALENDAR_CACHE = os.path.join(tempfile.gettempdir(), "antigravity_economic_calendar_cache.json")
AI_CALENDAR_CACHE = os.path.join(tempfile.gettempdir(), "antigravity_ai_calendar_cache.json")
BVB_CALENDAR_URL = "https://www.bvb.ro/FinancialInstruments/SelectedData/FinancialCalendar"
CALENDAR_SOURCE_URL = "https://economic-calendar.tradingview.com/events"
TVBETETF_HOLDINGS_URL = (
    "https://www.patriafonduri.ro/fonduri/patria-etfbet/investitiile-fondului"
)
TVBETETF_ISSUER_SYMBOLS = {
    'BANCA TRANSILVANIA': 'TLV.RO',
    'OMV PETROM': 'SNP.RO',
    'S.N.G.N. ROMGAZ': 'SNG.RO',
    'S.P.E.E.H. HIDROELECTRICA': 'H2O.RO',
    'BRD - GROUPE SOCIETE GENERALE': 'BRD.RO',
    'S.N.T.G.N. TRANSGAZ': 'TGN.RO',
    'SOCIETATEA ENERGETICA ELECTRICA': 'EL.RO',
    'DIGI COMMUNICATIONS': 'DIGI.RO',
    'MEDLIFE': 'M.RO',
    'S.N. NUCLEARELECTRICA': 'SNN.RO',
    'C.N.T.E.E. TRANSELECTRICA': 'TEL.RO',
    'PREMIER ENERGY': 'PE.RO',
    'ONE UNITED PROPERTIES': 'ONE.RO',
    'FONDUL PROPRIETATEA': 'FP.RO',
    'AQUILA PART PROD COM': 'AQ.RO',
    'CRIS-TIM FAMILY HOLDING': 'CFH.RO',
    'TRANSPORT TRADE SERVICES': 'TTS.RO',
    'ANTIBIOTICE': 'ATB.RO',
    'TERAPLAST': 'TRP.RO',
    'SPHERA FRANCHISE GROUP': 'SFG.RO',
}
US_SECTOR_ETFS = {
    'Technology': 'XLK',
    'Financial Services': 'XLF',
    'Energy': 'XLE',
    'Healthcare': 'XLV',
    'Industrials': 'XLI',
    'Consumer Cyclical': 'XLY',
    'Consumer Defensive': 'XLP',
    'Utilities': 'XLU',
    'Real Estate': 'XLRE',
    'Basic Materials': 'XLB',
    'Communication Services': 'XLC',
}

EVENT_RULES = {
    'inflation': {
        'keys': ('cpi', 'ppi', 'inflation', 'inflaț', 'hicp'),
        'what': 'Măsoară inflația și presiunile asupra prețurilor, influențând așteptările privind dobânzile.',
        'higher': 'bearish',
        'sectors': 'Tech și companiile cu evaluări ridicate sunt sensibile; băncile pot beneficia doar dacă economia rămâne solidă.'
    },
    'rates': {
        'keys': ('fomc', 'fed ', 'ecb', 'interest rate', 'deposit facility', 'bnr', 'dobând'),
        'what': 'Decizia și tonul băncii centrale schimbă costul capitalului și evaluarea activelor.',
        'higher': 'bearish',
        'sectors': 'Tech, imobiliarele și utilitățile sunt sensibile la randamente; băncile au un impact mixt.'
    },
    'growth': {
        'keys': ('gdp', 'pib', 'retail', 'industrial production', 'producția industrială', 'durable goods'),
        'what': 'Arată ritmul activității economice și cererea pentru bunuri și servicii.',
        'higher': 'bullish',
        'sectors': 'Industria, consumul și energia tind să reacționeze mai puternic la surprize de creștere.'
    },
    'jobs': {
        'keys': ('nonfarm', 'payroll', 'unemployment', 'șomaj', 'jobless', 'claims', 'employment'),
        'what': 'Descrie rezistența pieței muncii, consumul viitor și presiunile salariale.',
        'higher': 'mixed',
        'sectors': 'Consumul beneficiază de ocupare solidă, dar dobânzile pot apăsa sectoarele de creștere.'
    },
    'activity': {
        'keys': ('pmi', 'ism', 'manufacturing', 'services', 'confidence', 'sentiment'),
        'what': 'Este un indicator rapid al expansiunii, comenzilor și încrederii din economie.',
        'higher': 'bullish',
        'sectors': 'Industria, transporturile și consumul ciclic sunt de regulă cele mai expuse.'
    },
    'fiscal_fx': {
        'keys': ('deficit', 'rating', 'eur/ron', 'ron', 'bond', 'randament', 'treasury'),
        'what': 'Afectează prima de risc, costul finanțării statului și fluxurile de capital.',
        'higher': 'bearish',
        'sectors': 'Băncile și companiile îndatorate sunt sensibile la randamente; importatorii sunt sensibili la un leu mai slab.'
    },
    'corporate': {
        'keys': ('rezultate financiare', 'raport anual', 'dividend', 'ex-data', 'aga', 'teleconferinta', 'teleconferința'),
        'what': 'Este un eveniment al emitentului și poate schimba așteptările privind profitul sau distribuțiile.',
        'higher': 'mixed',
        'sectors': 'Impactul este în primul rând asupra emitentului, nu automat asupra întregului indice BET.'
    }
}

EVENT_DESCRIPTIONS = {
    'CPI': EVENT_RULES['inflation']['what'],
    'FOMC': EVENT_RULES['rates']['what'],
    'GDP': EVENT_RULES['growth']['what'],
    'Nonfarm': EVENT_RULES['jobs']['what'],
    'Unemployment': EVENT_RULES['jobs']['what'],
    'PMI': EVENT_RULES['activity']['what'],
    'BNR': EVENT_RULES['rates']['what'],
}

def get_event_impact(event_name):
    rule = _event_rule(event_name)
    if rule:
        return rule['what']
    return "Indicator economic. Poate genera volatilitate intraday."

def _event_rule(event_name):
    lowered = (event_name or '').lower()
    for rule in EVENT_RULES.values():
        if any(key in lowered for key in rule['keys']):
            return rule
    return None

def _parse_event_date(value):
    if not value:
        return None
    try:
        clean = str(value).replace('Z', '+00:00')
        parsed = datetime.datetime.fromisoformat(clean)
        if parsed.tzinfo:
            parsed = parsed.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return parsed
    except (TypeError, ValueError):
        try:
            return datetime.datetime.strptime(str(value)[:10], '%Y-%m-%d')
        except (TypeError, ValueError):
            return None

def _country_label(item):
    raw = str(item.get('country') or item.get('countryCode') or item.get('currency') or '').upper()
    title = str(item.get('title', '')).lower()
    if raw in ('RO', 'ROU', 'RON', 'ROMANIA') or any(x in title for x in ('romania', 'romanian', 'bnr')):
        return 'România'
    if raw in ('US', 'USA', 'USD', 'UNITED STATES'):
        return 'SUA'
    return 'Europa'

def _normalise_macro_event(item, now):
    title = str(item.get('title') or item.get('name') or '').strip()
    event_dt = _parse_event_date(item.get('date') or item.get('datetime'))
    if not title or not event_dt:
        return None
    rule = _event_rule(title)
    importance = item.get('importance') or item.get('impact') or 'medie'
    return {
        'id': str(item.get('id') or f"macro:{title}:{event_dt.isoformat()}"),
        'name': title,
        'country': _country_label(item),
        'category': next((name for name, candidate in EVENT_RULES.items() if candidate is rule), 'macro'),
        'datetime': event_dt.isoformat(),
        'time': event_dt.strftime('%H:%M'),
        'timezone': 'UTC',
        'week': event_dt.strftime('%d %b %Y'),
        'importance': str(importance),
        'actual': item.get('actual'),
        'forecast': item.get('forecast'),
        'previous': item.get('previous'),
        'status': 'past' if event_dt <= now else 'upcoming',
        'source': 'TradingView Economic Calendar',
        'source_url': CALENDAR_SOURCE_URL,
        'desc': rule['what'] if rule else get_event_impact(title),
    }

_MONTHS_RO = {
    'ianuarie': 1, 'februarie': 2, 'martie': 3, 'aprilie': 4, 'mai': 5, 'iunie': 6,
    'iulie': 7, 'august': 8, 'septembrie': 9, 'octombrie': 10, 'noiembrie': 11, 'decembrie': 12
}

def _parse_bvb_calendar_html(content, now):
    """Parsează calendarul public BVB fără să inventeze evenimente lipsă."""
    soup = BeautifulSoup(content, 'html.parser')
    lines = [re.sub(r'\s+', ' ', value).strip() for value in soup.stripped_strings]
    date_re = re.compile(r'^(\d{1,2})\s+(' + '|'.join(_MONTHS_RO) + r')\s+(\d{4})$', re.I)
    events = []
    current_date = None
    skip = {'calendar financiar', 'toate evenimentele viitoare', 'toate', 'segment bursa'}
    for line in lines:
        match = date_re.match(line)
        if match:
            current_date = datetime.datetime(
                int(match.group(3)), _MONTHS_RO[match.group(2).lower()], int(match.group(1)), 9, 0
            )
            continue
        if not current_date or line.lower() in skip or ' - ' not in line:
            continue
        symbol, description = line.split(' - ', 1)
        symbol = symbol.strip().split()[0] if symbol.strip() else 'BVB'
        if len(symbol) > 12 or len(description) < 4:
            continue
        name = f"{symbol} — {description.strip()}"
        events.append({
            'id': f"bvb:{symbol}:{current_date.date().isoformat()}:{description[:40]}",
            'name': name,
            'country': 'România',
            'category': 'corporate',
            'datetime': current_date.isoformat(),
            'time': '09:00',
            'timezone': 'Europe/Bucharest',
            'week': current_date.strftime('%d %b %Y'),
            'importance': 'companie',
            'actual': None,
            'forecast': None,
            'previous': None,
            'status': 'past' if current_date <= now else 'upcoming',
            'source': 'Bursa de Valori București',
            'source_url': BVB_CALENDAR_URL,
            'desc': EVENT_RULES['corporate']['what'],
        })
        current_date = None
    return events


def _parse_tvbetetf_holdings_html(content):
    """Extrage coșul zilnic publicat de Patria, fără ponderi presupuse."""
    soup = BeautifulSoup(content, 'html.parser')
    text = ' '.join(soup.stripped_strings)
    date_match = re.search(
        r'Co[sș]\s+de\s+emitere-rascumparare\s+la\s+data\s+de\s+(\d{2}-\d{2}-\d{4})',
        text,
        re.I,
    )
    as_of = None
    if date_match:
        try:
            as_of = datetime.datetime.strptime(
                date_match.group(1), '%d-%m-%Y'
            ).date().isoformat()
        except ValueError:
            pass
    holdings = []
    for row in soup.select('tr'):
        cells = [
            re.sub(r'\s+', ' ', cell.get_text(' ', strip=True)).strip()
            for cell in row.select('th,td')
        ]
        if len(cells) < 3:
            continue
        issuer = cells[0].upper()
        symbol = TVBETETF_ISSUER_SYMBOLS.get(issuer)
        weight_match = re.search(r'(\d+(?:[.,]\d+)?)\s*%', cells[-1])
        if not symbol or not weight_match:
            continue
        holdings.append({
            'symbol': symbol,
            'issuer': cells[0],
            'weight_pct': float(weight_match.group(1).replace(',', '.')),
        })
    return {
        'as_of': as_of,
        'source': 'Patria Asset Management',
        'source_url': TVBETETF_HOLDINGS_URL,
        'holdings': holdings,
    } if holdings else None


def fetch_tvbetetf_holdings(cached=None, request_session=requests):
    """Preia structura efectivă TVBETETF sau păstrează ultimul cache valid."""
    try:
        response = request_session.get(
            TVBETETF_HOLDINGS_URL,
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=15,
        )
        response.raise_for_status()
        parsed = _parse_tvbetetf_holdings_html(response.text)
        if parsed:
            parsed['fetched_at'] = datetime.datetime.now().isoformat(
                timespec='seconds'
            )
            return parsed
    except (requests.RequestException, ValueError, TypeError, AttributeError):
        pass
    return cached if isinstance(cached, dict) else None


def fetch_us_sector_rotation(cached=None, ticker_factory=yf.Ticker):
    """Măsoară rotația SUA față de SPY; păstrează cache-ul dacă datele lipsesc."""
    try:
        histories = {}
        for ticker in ['SPY'] + list(US_SECTOR_ETFS.values()):
            history = ticker_factory(ticker).history(
                period='6mo', interval='1d', auto_adjust=True
            )
            if history is None or history.empty or 'Close' not in history:
                raise ValueError(f'Istoric indisponibil pentru {ticker}')
            histories[ticker] = history['Close'].dropna().astype(float)
        spy = histories['SPY']

        def period_return(series, sessions):
            if len(series) <= sessions:
                return None
            return (float(series.iloc[-1]) / float(series.iloc[-sessions - 1]) - 1) * 100

        spy_1m = period_return(spy, 21)
        spy_3m = period_return(spy, 63)
        if spy_1m is None or spy_3m is None:
            raise ValueError('Istoric SPY insuficient')
        sectors = {}
        for sector, ticker in US_SECTOR_ETFS.items():
            close = histories[ticker]
            return_1m = period_return(close, 21)
            return_3m = period_return(close, 63)
            if return_1m is None or return_3m is None:
                continue
            sma50 = float(close.tail(50).mean())
            above_sma50 = float(close.iloc[-1]) >= sma50
            relative_1m = return_1m - spy_1m
            relative_3m = return_3m - spy_3m
            if above_sma50 and relative_1m > 1 and relative_3m > 2:
                status = 'lider'
                size_factor = 1.0
            elif (not above_sma50) or (
                relative_1m < -1 and relative_3m < 0
            ):
                status = 'în deteriorare'
                size_factor = 0.5
            else:
                status = 'neutru'
                size_factor = 0.8
            sectors[sector] = {
                'etf': ticker,
                'status': status,
                'return_1m_pct': round(return_1m, 2),
                'return_3m_pct': round(return_3m, 2),
                'relative_1m_vs_spy_pct': round(relative_1m, 2),
                'relative_3m_vs_spy_pct': round(relative_3m, 2),
                'above_sma50': above_sma50,
                'size_factor': size_factor,
            }
        if not sectors:
            raise ValueError('Niciun sector valid')
        return {
            'as_of': datetime.datetime.now().isoformat(timespec='seconds'),
            'benchmark': 'SPY',
            'benchmark_return_1m_pct': round(spy_1m, 2),
            'benchmark_return_3m_pct': round(spy_3m, 2),
            'sectors': sectors,
            'source': 'Yahoo Finance market data',
        }
    except Exception:
        return cached if isinstance(cached, dict) else None

def _load_calendar_cache(now):
    try:
        with open(ECONOMIC_CALENDAR_CACHE, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
        events = payload.get('events', [])
        valid_events = [
            event for event in events
            if now - datetime.timedelta(days=7) <= _parse_event_date(event.get('datetime')) <= now + datetime.timedelta(days=10)
        ]
        return _select_calendar_events(valid_events)
    except (OSError, ValueError, TypeError):
        return []

def _save_calendar_cache(events):
    try:
        temp_path = ECONOMIC_CALENDAR_CACHE + '.tmp'
        with open(temp_path, 'w', encoding='utf-8') as handle:
            json.dump({'updated_at': _utc_now_naive().isoformat(), 'events': events}, handle, ensure_ascii=False)
        os.replace(temp_path, ECONOMIC_CALENDAR_CACHE)
    except OSError:
        pass

def _importance_rank(event):
    value = str(event.get('importance', '')).lower()
    if value in ('high', '3', '1', '1.0') or 'ridicat' in value:
        return 3
    if value in ('medium', 'medie', '2', '0') or 'mediu' in value:
        return 2
    if event.get('category') == 'corporate':
        return 1
    return 0

def _select_calendar_events(events):
    """Păstrează calendarul lizibil și echilibrat între regiuni și perioade."""
    selected = []
    for status in ('past', 'upcoming'):
        for country in ('România', 'SUA', 'Europa'):
            candidates = [
                event for event in events
                if event.get('status') == status and event.get('country') == country
                and event.get('category') != 'corporate'
            ]
            candidates.sort(key=lambda event: (-_importance_rank(event), event['datetime']))
            selected.extend(candidates[:3])
        corporate = [
            event for event in events
            if event.get('status') == status and event.get('category') == 'corporate'
        ]
        corporate.sort(key=lambda event: event['datetime'])
        selected.extend(corporate[:3])
    return sorted(selected, key=lambda event: event['datetime'])

def get_economic_events(now=None, request_session=requests):
    """Evenimente reale SUA/Europa/România și calendar corporativ BVB, pe intervalul -7/+10 zile."""
    now = now or _utc_now_naive()
    start = now - datetime.timedelta(days=7)
    end = now + datetime.timedelta(days=10)
    fetched = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json',
            'Origin': 'https://www.tradingview.com',
            'Referer': 'https://www.tradingview.com/'
        }
        params = {
            'from': start.strftime("%Y-%m-%dT00:00:00.000Z"),
            'to': end.strftime("%Y-%m-%dT23:59:59.000Z"),
            'countries': ','.join(['US', 'EU', 'RO']),
            'minImportance': 1,
        }
        response = request_session.get(
            CALENDAR_SOURCE_URL,
            headers=headers,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        for item in response.json().get('result', []):
            event = _normalise_macro_event(item, now)
            if event and _event_rule(event['name']):
                fetched.append(event)
    except (requests.RequestException, ValueError, TypeError, AttributeError):
        pass

    try:
        response = request_session.get(BVB_CALENDAR_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        fetched.extend(_parse_bvb_calendar_html(response.text, now))
    except (requests.RequestException, ValueError, TypeError, AttributeError):
        pass

    unique = {}
    for event in fetched:
        event_dt = _parse_event_date(event.get('datetime'))
        if event_dt and start <= event_dt <= end:
            unique[event['id']] = event
    events = _select_calendar_events(list(unique.values()))
    if events:
        _save_calendar_cache(events)
        return events
    return _load_calendar_cache(now)

def _number(value):
    if value is None or value == '':
        return None
    match = re.search(r'-?\d+(?:[.,]\d+)?', str(value).replace(' ', ''))
    return float(match.group(0).replace(',', '.')) if match else None

def _deterministic_event_analysis(event):
    rule = _event_rule(event.get('name')) or EVENT_RULES.get(event.get('category'))
    base = {
        'verdict': 'Date insuficiente',
        'confidence': 'scăzută',
        'mechanism': event.get('desc') or get_event_impact(event.get('name', '')),
        'us_impact': 'Impactul depinde de abaterea față de consens și de regimul dobânzilor.',
        'eu_impact': 'Impactul depinde de reacția dobânzilor, monedei euro și apetitului global pentru risc.',
        'bvb_impact': 'Impactul se poate transmite prin sentiment, EUR/RON, randamente și fluxuri de capital.',
        'sectors': rule['sectors'] if rule else 'Sensibilitatea diferă între sectoare.',
        'horizon': 'intraday–câteva zile',
        'reversal': 'Verdictul se poate inversa dacă piața anticipase deja rezultatul.',
    }
    if event.get('category') == 'corporate':
        base.update({
            'verdict': 'Neutru',
            'confidence': 'scăzută',
            'us_impact': 'Nesemnificativ pentru indicii SUA.',
            'eu_impact': 'Nesemnificativ pentru indicii europeni.',
            'bvb_impact': 'Impact în primul rând asupra emitentului; efectul asupra BET depinde de ponderea sa.',
        })
        return base
    actual, forecast = _number(event.get('actual')), _number(event.get('forecast'))
    if event.get('status') == 'upcoming':
        base.update({
            'verdict': 'Mixt',
            'confidence': 'scăzută',
            'mechanism': f"{base['mechanism']} Peste, conform sau sub estimări pot produce reacții diferite.",
        })
        return base
    if actual is None or forecast is None or not rule:
        return base
    higher = actual > forecast
    direction = rule['higher']
    if direction == 'mixed':
        verdict = 'Mixt'
    elif (direction == 'bullish' and higher) or (direction == 'bearish' and not higher):
        verdict = 'Bullish probabil'
    else:
        verdict = 'Bearish probabil'
    base['verdict'] = verdict
    base['confidence'] = 'medie'
    base['mechanism'] += f" Valoarea actuală este {'peste' if higher else 'sub'} consens."
    return base

def _event_fingerprint(event):
    relevant = {
        key: event.get(key) for key in
        ('id', 'name', 'datetime', 'status', 'actual', 'forecast', 'previous')
    }
    encoded = json.dumps(relevant, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()

def _load_ai_calendar_cache():
    try:
        with open(AI_CALENDAR_CACHE, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}

def _save_ai_calendar_cache(cache):
    try:
        temp_path = AI_CALENDAR_CACHE + '.tmp'
        with open(temp_path, 'w', encoding='utf-8') as handle:
            json.dump(cache, handle, ensure_ascii=False)
        os.replace(temp_path, AI_CALENDAR_CACHE)
    except OSError:
        pass

OPENAI_ANALYSIS_MODEL = 'gpt-5.6-sol'
OPENAI_ANALYSIS_REASONING = {'effort': 'max', 'mode': 'pro'}
OPENAI_PORTFOLIO_REASONING = {'effort': 'high'}
PORTFOLIO_AI_CACHE_VERSION = 16
PORTFOLIO_EVIDENCE_CACHE_HOURS = 12
ACTIONABLE_BUY_VERDICTS = {'Candidat valid', 'Pregătit la trigger'}
SEC_TICKER_MAP_URL = 'https://www.sec.gov/files/company_tickers.json'
SEC_SUBMISSIONS_URL = 'https://data.sec.gov/submissions/CIK{cik:010d}.json'


def _extract_openai_response_text(payload):
    """Extrage textul din Responses API; acceptă și forma veche pentru cache/teste."""
    output_text = payload.get('output_text')
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()
    for output_item in payload.get('output', []):
        if not isinstance(output_item, dict):
            continue
        for content_item in output_item.get('content', []):
            if not isinstance(content_item, dict):
                continue
            text = content_item.get('text')
            if isinstance(text, str) and text.strip():
                return text.strip()
    try:
        return payload['choices'][0]['message']['content']
    except (KeyError, IndexError, TypeError):
        raise ValueError('Răspuns OpenAI fără text utilizabil')


def _safe_number(value, default=0.0):
    try:
        number = float(value)
        return number if math.isfinite(number) else default
    except (TypeError, ValueError):
        return default


def _execution_currency(candidate):
    currency = str(
        candidate.get('execution_currency')
        or candidate.get('currency')
        or ''
    ).strip().upper()
    if currency:
        return currency
    symbol = str(candidate.get('symbol') or '').upper()
    if symbol.endswith('.RO'):
        return 'RON'
    if symbol in {'LQQ.PA', 'LQQ.FR', 'FR.LQQ'}:
        return 'EUR'
    return 'USD'


def _eur_per_native(candidate):
    explicit = _safe_number(candidate.get('eur_per_native'))
    if explicit > 0:
        return explicit
    price_eur = _safe_number(candidate.get('price_eur'))
    price_native = _safe_number(candidate.get('price_native'))
    if price_eur > 0 and price_native > 0:
        return price_eur / price_native
    return 1.0


def _execution_value(candidate, native_field, eur_field):
    native_value = _safe_number(candidate.get(native_field))
    if native_value > 0:
        return native_value
    eur_value = _safe_number(candidate.get(eur_field))
    eur_per_native = _eur_per_native(candidate)
    if eur_value > 0 and eur_per_native > 0:
        return eur_value / eur_per_native
    return eur_value


def _format_execution_money(value, currency):
    numeric = _safe_number(value)
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


def _normalize_tws_account_data(account_data, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    result = {
        'source': 'TWS / IBKR API',
        'fetched_at': None,
        'age_hours': None,
        'stale': True,
        'accounts': [],
        'risk_flags': [],
        'privacy_mode': 'exact',
    }
    if not isinstance(account_data, dict):
        result['risk_flags'].append('Sumarul cash/marjă TWS nu este disponibil')
        return result
    if account_data.get('privacy_mode') == 'bands_only':
        result['privacy_mode'] = 'bands_only'
    fetched_at = account_data.get('fetched_at')
    result['fetched_at'] = fetched_at
    try:
        fetched = datetime.datetime.fromisoformat(str(fetched_at).replace('Z', '+00:00'))
        if fetched.tzinfo is None:
            fetched = fetched.replace(tzinfo=datetime.timezone.utc)
        age_hours = max((now - fetched.astimezone(datetime.timezone.utc)).total_seconds() / 3600, 0)
        result['age_hours'] = round(age_hours, 2)
        result['stale'] = age_hours > 24
    except (TypeError, ValueError):
        result['risk_flags'].append('Timestampul sumarului TWS este invalid')

    raw_accounts = account_data.get('accounts', [])
    if result['privacy_mode'] == 'bands_only':
        raw_accounts = account_data.get('sanitized_accounts', [])
    for raw_account in raw_accounts:
        if not isinstance(raw_account, dict):
            continue
        if result['privacy_mode'] == 'bands_only':
            sanitized = {
                'label': str(raw_account.get('label', f"Cont {len(result['accounts']) + 1}")),
                'base_currency': str(raw_account.get('base_currency', 'BASE')),
                'cash_currencies': [
                    str(currency) for currency in raw_account.get('cash_currencies', [])
                ],
                'cash_pct_band': str(raw_account.get('cash_pct_band', 'indisponibil')),
                'maintenance_margin_pct_band': str(
                    raw_account.get('maintenance_margin_pct_band', 'indisponibil')
                ),
                'available_funds_status': str(
                    raw_account.get('available_funds_status', 'indisponibil')
                ),
                'buying_power_status': str(
                    raw_account.get('buying_power_status', 'indisponibil')
                ),
                'excess_liquidity_status': str(
                    raw_account.get('excess_liquidity_status', 'indisponibil')
                ),
                'cushion_band': str(raw_account.get('cushion_band', 'indisponibil')),
            }
            result['accounts'].append(sanitized)
            if sanitized['available_funds_status'] == 'zero/negativ':
                result['risk_flags'].append('Available Funds este zero sau negativ')
            if sanitized['excess_liquidity_status'] == 'zero/negativ':
                result['risk_flags'].append('Excess Liquidity este zero sau negativ')
            if sanitized['cushion_band'] == 'sub 15%':
                result['risk_flags'].append('Cushion TWS este sub 15%')
            if sanitized['maintenance_margin_pct_band'] == 'peste 50%':
                result['risk_flags'].append(
                    'Marja de menținere depășește 50% din Net Liquidation'
                )
            if sanitized['cash_pct_band'] == 'sub 5%':
                result['risk_flags'].append(
                    'Cash-ul de bază este sub 5% din Net Liquidation'
                )
            continue
        raw_summary = raw_account.get('summary', {})
        summary = {
            key: _safe_number(raw_summary.get(key), None)
            for key in (
                'NetLiquidation', 'TotalCashValue', 'SettledCash', 'AvailableFunds',
                'BuyingPower', 'ExcessLiquidity', 'InitMarginReq', 'MaintMarginReq',
                'GrossPositionValue', 'CostBasis', 'RelativeProfit', 'Cushion',
            )
        }
        summary = {key: value for key, value in summary.items() if value is not None}
        cash_by_currency = {
            str(currency): _safe_number(value)
            for currency, value in raw_account.get('cash_by_currency', {}).items()
            if _safe_number(value, None) is not None
        }
        net_liquidation = summary.get('NetLiquidation', 0)
        total_cash = summary.get('TotalCashValue', 0)
        margin_requirement = summary.get('MaintMarginReq', 0)
        result['accounts'].append({
            'label': str(raw_account.get('label', f"Cont {len(result['accounts']) + 1}")),
            'source': str(raw_account.get('source', account_data.get('source', result['source']))),
            'base_currency': str(raw_account.get('base_currency', 'BASE')),
            'summary': summary,
            'cash_by_currency': cash_by_currency,
            'cash_pct_of_net_liquidation': (
                round(total_cash / net_liquidation * 100, 2) if net_liquidation > 0 else None
            ),
            'maintenance_margin_pct': (
                round(margin_requirement / net_liquidation * 100, 2)
                if net_liquidation > 0 else None
            ),
        })
        if summary.get('AvailableFunds', 1) <= 0:
            result['risk_flags'].append('Available Funds este zero sau negativ')
        if summary.get('ExcessLiquidity', 1) <= 0:
            result['risk_flags'].append('Excess Liquidity este zero sau negativ')
        if summary.get('Cushion') is not None and summary['Cushion'] < 0.15:
            result['risk_flags'].append('Cushion TWS este sub 15%')
        if net_liquidation > 0 and margin_requirement / net_liquidation > 0.5:
            result['risk_flags'].append('Marja de menținere depășește 50% din Net Liquidation')
        if net_liquidation > 0 and total_cash / net_liquidation < 0.05:
            result['risk_flags'].append('Cash-ul de bază este sub 5% din Net Liquidation')

    if result['stale']:
        result['risk_flags'].append('Datele cash/marjă TWS sunt mai vechi de 24 de ore')
    if not result['accounts']:
        result['risk_flags'].append('TWS nu a returnat un sumar de cont utilizabil')
    result['risk_flags'] = list(dict.fromkeys(result['risk_flags']))
    return result


def _market_series_summary(label, series, source):
    """Rezumat compact al direcției pieței, fără a inventa perioade lipsă."""
    values = [
        _safe_number(value, None) for value in (series or [])
        if _safe_number(value, None) is not None and _safe_number(value, None) > 0
    ]
    if not values:
        return None

    def period_return(offset):
        if len(values) <= offset or values[-offset - 1] <= 0:
            return None
        return round((values[-1] / values[-offset - 1] - 1) * 100, 2)

    return {
        'label': label,
        'source': source,
        'latest': round(values[-1], 2),
        'change_1d_pct': period_return(1),
        'change_1m_pct': period_return(20),
        'change_3m_pct': period_return(min(59, len(values) - 1)),
    }


def build_portfolio_market_context(portfolio_df, market_indicators=None):
    """Contextul piețelor relevante pozițiilor: SUA și România/BVB."""
    market_indicators = market_indicators or {}
    markets = {}
    spx = _market_series_summary(
        'S&P 500', market_indicators.get('SPX', {}).get('history', []),
        'Indice SUA',
    )
    nasdaq = _market_series_summary(
        'Nasdaq Composite', market_indicators.get('NASDAQ', {}).get('history', []),
        'Indice SUA',
    )
    us_benchmarks = [item for item in (spx, nasdaq) if item]
    if us_benchmarks:
        markets['SUA'] = {
            'benchmarks': us_benchmarks,
            'applies_to': [
                str(row.get('Symbol', '')).upper()
                for _, row in portfolio_df.iterrows()
                if not str(row.get('Symbol', '')).upper().endswith('.RO')
            ],
        }

    if portfolio_df is not None and not portfolio_df.empty:
        bvb_rows = portfolio_df[
            portfolio_df['Symbol'].astype(str).str.upper().str.endswith('.RO')
        ] if 'Symbol' in portfolio_df.columns else pd.DataFrame()
        if not bvb_rows.empty:
            proxy_row = bvb_rows.iloc[0]
            bvb_proxy = _market_series_summary(
                'TVBETETF (proxy BET-TR)',
                proxy_row.get('Chart_History', proxy_row.get('Sparkline', [])),
                'ETF care urmărește piața principală BVB; folosit ca proxy, nu ca indice oficial',
            )
            if bvb_proxy:
                markets['România / BVB'] = {
                    'benchmarks': [bvb_proxy],
                    'applies_to': [
                        str(row.get('Symbol', '')).upper()
                        for _, row in bvb_rows.iterrows()
                    ],
                }
    return markets


def build_us_market_regime(market_indicators=None, economic_phase=None):
    """Clasifică trendul SUA și ciclul fără să completeze date inexistente."""
    indicators = market_indicators or {}
    benchmarks = []
    for key in ('SPX', 'NASDAQ'):
        values = [
            _safe_number(value, None)
            for value in indicators.get(key, {}).get('history', [])
        ]
        values = [value for value in values if value is not None and value > 0]
        if len(values) < 50:
            continue
        latest = values[-1]
        sma50 = sum(values[-50:]) / 50
        long_window = min(len(values), 200)
        long_average = sum(values[-long_window:]) / long_window
        benchmarks.append({
            'symbol': key, 'latest': latest, 'sma50': sma50,
            'long_average': long_average, 'long_window_days': long_window,
            'above_sma50': latest >= sma50,
            'above_long_average': latest >= long_average,
        })
    vix = _safe_number(indicators.get('VIX', {}).get('value'), None)
    phase = str(economic_phase or 'Date insuficiente')
    if not benchmarks:
        trend, trend_factor = 'date insuficiente', 0.6
    elif all(
        item['above_sma50'] and item['above_long_average']
        for item in benchmarks
    ):
        trend, trend_factor = 'creștere confirmată', 1.0
    elif all(item['above_long_average'] for item in benchmarks):
        trend, trend_factor = 'corecție într-un trend ascendent', 0.75
    elif all(not item['above_long_average'] for item in benchmarks):
        trend, trend_factor = 'trend descendent', 0.45
    else:
        trend, trend_factor = 'piață mixtă', 0.65
    phase_factor = {
        'Recovery': 0.9, 'Expansion': 1.0, 'Slowdown': 0.7,
        'Recession': 0.45,
    }.get(phase, 0.6)
    if vix is not None and vix >= 30:
        trend_factor = min(trend_factor, 0.4)
    favored = {
        'Recovery': {'Financial Services', 'Industrials', 'Consumer Cyclical', 'Technology'},
        'Expansion': {'Technology', 'Industrials', 'Consumer Cyclical', 'Communication Services'},
        'Slowdown': {'Healthcare', 'Consumer Defensive', 'Utilities'},
        'Recession': {'Healthcare', 'Consumer Defensive', 'Utilities'},
    }.get(phase, set())
    unfavored = {
        'Slowdown': {'Consumer Cyclical', 'Industrials'},
        'Recession': {'Financial Services', 'Consumer Cyclical', 'Industrials'},
    }.get(phase, set())
    return {
        'economic_phase': phase,
        'market_stage': trend,
        'size_factor': round(min(trend_factor, phase_factor), 2),
        'vix': vix,
        'benchmarks': benchmarks,
        'sector_fit': {
            sector: (
                'favorizat' if sector in favored
                else 'nefavorizat' if sector in unfavored
                else 'neutru'
            )
            for sector in US_SECTOR_ETFS
        },
    }


def build_portfolio_risk_snapshot(portfolio_df, orders_df=None, account_data=None,
                                  market_context=None, etf_holdings=None,
                                  sector_rotation=None, us_market_regime=None):
    """Normalizează numai datele necesare evaluării riscului, fără valori inventate."""
    if portfolio_df is None or portfolio_df.empty:
        return {
            'as_of': datetime.datetime.now().isoformat(timespec='seconds'),
            'positions': [],
            'portfolio': {},
            'account_liquidity': _normalize_tws_account_data(account_data),
            'market_context': market_context or {},
        }

    orders_df = orders_df if orders_df is not None else pd.DataFrame()
    total_value = sum(max(_safe_number(row.get('Current_Value')), 0) for _, row in portfolio_df.iterrows())
    positions = []

    for _, row in portfolio_df.iterrows():
        symbol = str(row.get('Symbol', '')).strip().upper()
        shares = max(_safe_number(row.get('Shares')), 0)
        price = _safe_number(row.get('Current_Price'))
        buy_price = _safe_number(row.get('Buy_Price'))
        target = _safe_number(row.get('Target'))
        suggested_stop = _safe_number(row.get('Suggested_Stop'))
        current_value = max(_safe_number(row.get('Current_Value')), 0)
        price_native = _safe_number(row.get('Price_Native'))
        atr_native = _safe_number(row.get('Finviz_ATR'))
        atr_pct = (atr_native / price_native * 100) if price_native > 0 and atr_native > 0 else 0
        volatility_candidates = [
            value for value in (atr_pct, _safe_number(row.get('Vol_W')), _safe_number(row.get('Vol_M')))
            if value > 0
        ]
        volatility_reference_pct = max(volatility_candidates) if volatility_candidates else 0

        active_stops = []
        if not orders_df.empty and 'Symbol' in orders_df.columns:
            symbol_orders = orders_df[
                orders_df['Symbol'].astype(str).str.upper() == symbol
            ]
            if 'Action' in symbol_orders.columns:
                symbol_orders = symbol_orders[
                    symbol_orders['Action'].astype(str).str.upper() == 'SELL'
                ]
            conversion_rate = 1.0
            if price_native > 0 and price > 0:
                conversion_rate = price / price_native
            for _, order in symbol_orders.iterrows():
                stop_native = 0.0
                for column in ('Calculated_Stop', 'Stop_Price', 'Aux_Price'):
                    candidate = _safe_number(order.get(column))
                    if 0 < candidate < 1e10:
                        stop_native = candidate
                        break
                if stop_native <= 0:
                    continue
                quantity = max(_safe_number(order.get('Total_Qty', order.get('Quantity'))), 0)
                active_stops.append({
                    'value': round(stop_native * conversion_rate, 4),
                    'quantity': quantity,
                    'order_type': str(order.get('OrderType', 'necunoscut')),
                })

        if not active_stops:
            fallback_stop = _safe_number(row.get('Trail_Stop_IBKR'))
            if fallback_stop <= 0:
                fallback_stop = _safe_number(row.get('Trail_Stop'))
            if fallback_stop > 0:
                active_stops.append({
                    'value': fallback_stop,
                    'quantity': shares,
                    'order_type': 'agregat',
                })

        covered_quantity = min(sum(item['quantity'] for item in active_stops), shares) if shares > 0 else 0
        primary_stop = max((item['value'] for item in active_stops), default=0)
        stop_distance_pct = ((price - primary_stop) / price * 100) if price > 0 and primary_stop > 0 else None
        suggested_distance_pct = ((price - suggested_stop) / price * 100) if price > 0 and suggested_stop > 0 else None
        target_upside_pct = ((target - price) / price * 100) if price > 0 and target > 0 else None
        reward_risk = None
        if target > price and primary_stop > 0 and primary_stop < price:
            reward_risk = (target - price) / (price - primary_stop)

        flags = []
        if not active_stops:
            flags.append('Fără ordin stop activ identificat')
        elif shares > 0 and covered_quantity + 1e-9 < shares:
            flags.append(f"Stopurile acoperă doar {covered_quantity:g} din {shares:g} acțiuni")
        if primary_stop >= price > 0:
            flags.append('Stopul este la sau peste prețul curent; ordinul trebuie verificat')
        if stop_distance_pct is not None and volatility_reference_pct > 0:
            if stop_distance_pct < volatility_reference_pct:
                flags.append('Stop posibil prea strâns față de volatilitatea observată')
            elif stop_distance_pct > volatility_reference_pct * 3:
                flags.append('Stop posibil prea larg față de volatilitatea observată')
        if reward_risk is not None and reward_risk < 1.5:
            flags.append('Raport recompensă/risc sub 1,5 la stopul activ')
        if str(row.get('Sell_Decision', '')).upper() in {'EXIT', 'REDUCE'}:
            flags.append(f"Decizia existentă este {str(row.get('Sell_Decision')).upper()}")
        if bool(row.get('Earnings_Danger')):
            flags.append('Catalizator de rezultate apropiat; stopul poate să nu limiteze un gap')
        weight_pct = (current_value / total_value * 100) if total_value > 0 else None
        if weight_pct is not None and weight_pct > 25:
            flags.append('Concentrare peste 25% din valoarea portofoliului')

        positions.append({
            'symbol': symbol,
            'broker': str(row.get('Broker', '')).strip() or (
                'Tradeville' if symbol.endswith('.RO') else 'IBKR'
            ),
            'market': 'România / BVB' if symbol.endswith('.RO') else 'SUA',
            'sector': str(row.get('Sector', '')).strip() or None,
            'industry': str(row.get('Industry', '')).strip() or None,
            'shares': shares,
            'current_price_eur': price or None,
            'buy_price_eur': buy_price or None,
            'profit_pct': _safe_number(row.get('Profit_Pct')),
            'current_value_eur': round(current_value, 2),
            'portfolio_weight_pct': round(weight_pct, 2) if weight_pct is not None else None,
            'active_stops': active_stops,
            'stop_coverage_pct': round(covered_quantity / shares * 100, 2) if shares > 0 else None,
            'primary_stop_eur': primary_stop or None,
            'suggested_stop_eur': suggested_stop or None,
            'stop_distance_pct': round(stop_distance_pct, 2) if stop_distance_pct is not None else None,
            'suggested_stop_distance_pct': round(suggested_distance_pct, 2) if suggested_distance_pct is not None else None,
            'volatility_reference_pct': round(volatility_reference_pct, 2) if volatility_reference_pct > 0 else None,
            'target_eur': target or None,
            'target_upside_pct': round(target_upside_pct, 2) if target_upside_pct is not None else None,
            'reward_risk_to_target': round(reward_risk, 2) if reward_risk is not None else None,
            'decision': str(row.get('Sell_Decision', 'HOLD')),
            'decision_reason': str(row.get('Sell_Reason', ''))[:600],
            'trend': str(row.get('Trend', '')),
            'rsi': _safe_number(row.get('RSI')) or None,
            'relative_strength_vs_spx_pct': _safe_number(row.get('RS_vs_SPX')) or None,
            'earnings_risk': bool(row.get('Earnings_Danger')),
            'data_flags': flags,
        })

    snapshot = {
        'as_of': datetime.datetime.now().isoformat(timespec='seconds'),
        'portfolio': {
            'position_count': len(positions),
            'total_value_eur': round(total_value, 2),
            'positions_without_stop': sum(not item['active_stops'] for item in positions),
            'positions_with_incomplete_stop_coverage': sum(
                item['stop_coverage_pct'] is not None and item['stop_coverage_pct'] < 100
                for item in positions
            ),
        },
        'account_liquidity': _normalize_tws_account_data(account_data),
        'market_context': market_context or {},
        'us_sector_rotation': sector_rotation or {},
        'us_market_regime': us_market_regime or {},
        'positions': positions,
    }
    if isinstance(etf_holdings, dict) and etf_holdings.get('holdings'):
        etf_position = next(
            (
                item for item in positions
                if item['symbol'] in {'TVBETETF', 'TVBETETF.RO'}
            ),
            None,
        )
        etf_value = _safe_number(
            (etf_position or {}).get('current_value_eur')
        )
        direct_values = {
            item['symbol']: _safe_number(item.get('current_value_eur'))
            for item in positions
        }
        lookthrough = []
        for holding in etf_holdings['holdings']:
            symbol = str(holding.get('symbol', '')).upper()
            weight_pct = _safe_number(holding.get('weight_pct'))
            indirect_value = etf_value * weight_pct / 100
            direct_value = direct_values.get(symbol, 0)
            lookthrough.append({
                'symbol': symbol,
                'issuer': holding.get('issuer'),
                'etf_weight_pct': round(weight_pct, 4),
                'indirect_exposure_eur': round(indirect_value, 2),
                'direct_exposure_eur': round(direct_value, 2),
                'combined_exposure_eur': round(
                    indirect_value + direct_value, 2
                ),
                'combined_portfolio_weight_pct': round(
                    (indirect_value + direct_value) / total_value * 100, 2
                ) if total_value > 0 else None,
            })
        snapshot['tvbetetf_lookthrough'] = {
            'as_of': etf_holdings.get('as_of'),
            'source': etf_holdings.get('source'),
            'source_url': etf_holdings.get('source_url'),
            'etf_position_value_eur': round(etf_value, 2),
            'holdings': lookthrough,
        }
    return snapshot


def _portfolio_snapshot_fingerprint(snapshot):
    account_liquidity = snapshot.get('account_liquidity', {})
    stable = {
        'version': PORTFOLIO_AI_CACHE_VERSION,
        'portfolio': snapshot.get('portfolio', {}),
        'positions': snapshot.get('positions', []),
        'account_liquidity': {
            'privacy_mode': account_liquidity.get('privacy_mode'),
            'fetched_at': account_liquidity.get('fetched_at'),
            'accounts': account_liquidity.get('accounts', []),
        },
        'market_context': snapshot.get('market_context', {}),
        'buy_candidates': snapshot.get('buy_candidates', []),
        'economic_calendar': snapshot.get('economic_calendar', []),
        'tvbetetf_lookthrough': snapshot.get('tvbetetf_lookthrough', {}),
        'us_sector_rotation': snapshot.get('us_sector_rotation', {}),
        'us_market_regime': snapshot.get('us_market_regime', {}),
    }
    return hashlib.sha256(
        json.dumps(stable, sort_keys=True, ensure_ascii=False).encode('utf-8')
    ).hexdigest()


def _size_buy_candidates(snapshot):
    """Dimensionare prudentă, separată pentru fiecare broker eligibil."""
    candidates = [dict(item) for item in snapshot.get('buy_candidates', [])]
    total_portfolio_value = _safe_number(
        snapshot.get('portfolio', {}).get('total_value_eur')
    )
    lookthrough_by_symbol = {
        str(item.get('symbol', '')).upper(): item
        for item in snapshot.get('tvbetetf_lookthrough', {}).get('holdings', [])
    }
    direct_values = {
        str(item.get('symbol', '')).upper(): _safe_number(
            item.get('current_value_eur')
        )
        for item in snapshot.get('positions', [])
    }
    sector_rotation = snapshot.get('us_sector_rotation', {}).get('sectors', {})
    us_market_regime = snapshot.get('us_market_regime', {})
    direct_sector_values = {}
    direct_industry_values = {}
    for position in snapshot.get('positions', []):
        if position.get('market') != 'SUA':
            continue
        sector = str(position.get('sector') or 'Necunoscut')
        direct_sector_values[sector] = (
            direct_sector_values.get(sector, 0)
            + _safe_number(position.get('current_value_eur'))
        )
        industry = str(position.get('industry') or 'Necunoscut')
        direct_industry_values[industry] = (
            direct_industry_values.get(industry, 0)
            + _safe_number(position.get('current_value_eur'))
        )
    for candidate in candidates:
        symbol = str(candidate.get('symbol', '')).upper()
        execution_currency = _execution_currency(candidate)
        candidate['execution_currency'] = execution_currency
        candidate['entry_native'] = round(
            _execution_value(candidate, 'entry_native', 'entry_eur'), 4
        )
        candidate['stop_native'] = round(
            _execution_value(candidate, 'stop_native', 'stop_eur'), 4
        )
        candidate['target_native'] = round(
            _execution_value(candidate, 'target_native', 'target_eur'), 4
        )
        overlap = lookthrough_by_symbol.get(symbol, {})
        etf_weight = _safe_number(overlap.get('etf_weight_pct'))
        indirect = _safe_number(overlap.get('indirect_exposure_eur'))
        direct = direct_values.get(symbol, 0)
        candidate.update({
            'tvbetetf_weight_pct': round(etf_weight, 4),
            'indirect_exposure_eur': round(indirect, 2),
            'direct_exposure_eur': round(direct, 2),
            'combined_pretrade_exposure_eur': round(indirect + direct, 2),
            'combined_pretrade_portfolio_weight_pct': round(
                (indirect + direct) / total_portfolio_value * 100, 2
            ) if total_portfolio_value > 0 else None,
            'lookthrough_source_date': snapshot.get(
                'tvbetetf_lookthrough', {}
            ).get('as_of'),
        })
        if etf_weight >= 12:
            candidate['overlap_size_factor'] = 0.35
            candidate['overlap_risk'] = 'ridicat'
        elif etf_weight >= 6:
            candidate['overlap_size_factor'] = 0.55
            candidate['overlap_risk'] = 'mediu'
        elif etf_weight >= 3:
            candidate['overlap_size_factor'] = 0.75
            candidate['overlap_risk'] = 'moderat'
        else:
            candidate['overlap_size_factor'] = 1.0
            candidate['overlap_risk'] = 'redus'
        if candidate.get('market') == 'SUA':
            sector = str(candidate.get('sector') or 'Necunoscut')
            rotation = sector_rotation.get(sector, {})
            candidate.update({
                'sector_rotation_status': rotation.get(
                    'status', 'date insuficiente'
                ),
                'sector_etf': rotation.get('etf'),
                'sector_relative_1m_vs_spy_pct': rotation.get(
                    'relative_1m_vs_spy_pct'
                ),
                'sector_relative_3m_vs_spy_pct': rotation.get(
                    'relative_3m_vs_spy_pct'
                ),
                'sector_rotation_size_factor': _safe_number(
                    rotation.get('size_factor')
                ) or 0.6,
                'existing_sector_exposure_eur': round(
                    direct_sector_values.get(sector, 0), 2
                ),
                'existing_industry_exposure_eur': round(
                    direct_industry_values.get(
                        str(candidate.get('industry') or 'Necunoscut'), 0
                    ),
                    2,
                ),
                'us_market_stage': us_market_regime.get(
                    'market_stage', 'date insuficiente'
                ),
                'us_economic_phase': us_market_regime.get(
                    'economic_phase', 'Date insuficiente'
                ),
                'market_regime_size_factor': _safe_number(
                    us_market_regime.get('size_factor')
                ) or 0.6,
                'cycle_fit': us_market_regime.get('sector_fit', {}).get(
                    sector, candidate.get('cycle_fit', 'neutru')
                ),
            })
    liquidity = snapshot.get('account_liquidity', {})
    if liquidity.get('privacy_mode') != 'exact':
        for candidate in candidates:
            candidate['sizing_status'] = 'indisponibil'
            candidate['sizing_reason'] = 'Soldurile exacte ale brokerului nu sunt disponibile.'
            candidate['sizing_by_broker'] = []
        return candidates

    accounts = liquidity.get('accounts', [])
    broker_weights = {}
    for position in snapshot.get('positions', []):
        broker = str(position.get('broker') or '')
        broker_weights[broker] = (
            broker_weights.get(broker, 0)
            + _safe_number(position.get('portfolio_weight_pct'))
        )

    allocations_by_broker = {}
    for candidate in candidates:
        brokers = candidate.get('eligible_brokers')
        if not isinstance(brokers, list) or not brokers:
            brokers = ['Tradeville'] if candidate.get('market') == 'România / BVB' else ['IBKR']
        candidate['sizing_by_broker'] = []
        for broker in brokers:
            allocations_by_broker.setdefault(str(broker), []).append(candidate)

    for broker, broker_candidates in allocations_by_broker.items():
        account = next(
            (
                item for item in accounts
                if broker.lower() in (
                    str(item.get('label', '')) + ' ' + str(item.get('source', ''))
                ).lower()
            ),
            None,
        )
        if not account:
            for candidate in broker_candidates:
                candidate['sizing_by_broker'].append({
                    'broker': broker,
                    'sizing_status': 'indisponibil',
                    'sizing_reason': f'Soldul {broker} nu este disponibil.',
                })
            continue

        summary = account.get('summary', {})
        net_liquidation = _safe_number(summary.get('NetLiquidation'))
        available_funds = _safe_number(summary.get('AvailableFunds'))
        total_cash = _safe_number(summary.get('TotalCashValue'))
        usable_cash = min(
            value for value in (available_funds, total_cash)
            if value > 0
        ) if available_funds > 0 and total_cash > 0 else max(available_funds, total_cash)
        concentrated = broker_weights.get(broker, 0) > 40
        risk_pct_nav = 0.002 if broker == 'Tradeville' else 0.0025
        max_pct_nav = 0.02 if broker == 'Tradeville' else 0.03
        if concentrated:
            risk_pct_nav *= 0.5
            max_pct_nav *= 0.5

        preliminary = []
        for candidate in broker_candidates:
            entry = _safe_number(candidate.get('entry_eur'))
            stop = _safe_number(candidate.get('stop_eur'))
            stop_risk_pct = (
                (entry - stop) / entry if entry > 0 and 0 < stop < entry else 0
            )
            risk_budget = net_liquidation * risk_pct_nav
            risk_size = risk_budget / stop_risk_pct if stop_risk_pct > 0 else 0
            cash_cap = usable_cash * 0.05
            nav_cap = net_liquidation * max_pct_nav
            conditional_amount = min(
                value for value in (risk_size, cash_cap, nav_cap)
                if value > 0
            ) if risk_size > 0 and cash_cap > 0 and nav_cap > 0 else 0
            if candidate.get('earnings_risk'):
                conditional_amount *= 0.5
            if 'bearish' in str(candidate.get('trend', '')).lower():
                conditional_amount *= 0.6
            conditional_amount *= _safe_number(
                candidate.get('overlap_size_factor')
            ) or 1.0
            if candidate.get('market') == 'SUA':
                conditional_amount *= _safe_number(
                    candidate.get('sector_rotation_size_factor')
                ) or 0.6
                conditional_amount *= _safe_number(
                    candidate.get('market_regime_size_factor')
                ) or 0.6
                conditional_amount *= {
                    'favorizat': 1.0, 'neutru': 0.8, 'nefavorizat': 0.55,
                }.get(candidate.get('cycle_fit'), 0.8)
            liquidity_cap = _safe_number(
                candidate.get('liquidity_position_cap_eur')
            )
            candidate['liquidity_cap_applied'] = bool(
                candidate.get('market') == 'România / BVB'
                and liquidity_cap > 0
                and conditional_amount > liquidity_cap
            )
            if (
                candidate.get('market') == 'România / BVB'
                and liquidity_cap > 0
            ):
                conditional_amount = min(conditional_amount, liquidity_cap)
            preliminary.append((candidate, conditional_amount, stop_risk_pct))

        aggregate_cap = min(usable_cash * 0.15, net_liquidation * 0.12)
        preliminary_total = sum(amount for _, amount, _ in preliminary)
        scale = min(1.0, aggregate_cap / preliminary_total) if preliminary_total > 0 else 0
        sector_allocated = {}
        industry_allocated = {}
        for candidate, amount, stop_risk_pct in preliminary:
            entry = _safe_number(candidate.get('entry_eur'))
            amount *= scale
            if candidate.get('market') == 'SUA':
                sector = str(candidate.get('sector') or 'Necunoscut')
                existing_sector = direct_sector_values.get(sector, 0)
                sector_cap = net_liquidation * 0.10
                remaining_sector_capacity = max(
                    sector_cap
                    - existing_sector
                    - sector_allocated.get(sector, 0),
                    0,
                )
                amount = min(amount, remaining_sector_capacity)
                industry = str(candidate.get('industry') or 'Necunoscut')
                if industry != 'Necunoscut':
                    industry_cap = net_liquidation * 0.05
                    remaining_industry_capacity = max(
                        industry_cap
                        - direct_industry_values.get(industry, 0)
                        - industry_allocated.get(industry, 0),
                        0,
                    )
                    amount = min(amount, remaining_industry_capacity)
            units = int(amount / entry) if entry > 0 else 0
            amount = units * entry
            if candidate.get('market') == 'SUA':
                sector_allocated[sector] = (
                    sector_allocated.get(sector, 0) + amount
                )
                if industry != 'Necunoscut':
                    industry_allocated[industry] = (
                        industry_allocated.get(industry, 0) + amount
                    )
            execution_currency = _execution_currency(candidate)
            eur_per_native = _eur_per_native(candidate)
            candidate['sizing_by_broker'].append({
                'broker': broker,
                'broker_available_cash_eur': round(usable_cash, 2),
                'broker_available_cash_native_equivalent': round(
                    usable_cash / eur_per_native, 2
                ),
                'execution_currency': execution_currency,
                'broker_net_liquidation_eur': round(net_liquidation, 2),
                'conditional_amount_eur': round(amount, 2),
                'conditional_amount_native': round(
                    amount / eur_per_native, 2
                ),
                'conditional_units': units,
                'risk_to_stop_pct': round(stop_risk_pct * 100, 2),
                'sizing_status': 'condițional' if amount > 0 else 'indisponibil',
                'sizing_reason': (
                    (
                        'Limitat de riscul până la stop, cash, NAV, concentrarea '
                        'existentă și capacitatea rulajului BVB/AeRO.'
                        if candidate.get('market') == 'România / BVB'
                        and _safe_number(
                            candidate.get('liquidity_position_cap_eur')
                        ) > 0
                        else
                        'Limitat de riscul până la stop, cash, NAV și concentrarea existentă.'
                    )
                    if amount > 0 else 'Stopul sau soldul nu permit o dimensionare verificabilă.'
                ),
            })
    for candidate in candidates:
        rows = candidate.get('sizing_by_broker') or []
        if rows:
            candidate.update(rows[0])
    return candidates


def _clean_evidence_item(item):
    if not isinstance(item, dict):
        return None
    url = str(item.get('url', '')).strip()
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != 'https' or not parsed.netloc:
        return None
    source_id = str(item.get('source_id', '')).strip()
    title = str(item.get('title', '')).strip()
    if not source_id or not title:
        return None
    return {
        'source_id': source_id[:100],
        'symbol': str(item.get('symbol', '')).strip().upper()[:30],
        'title': title[:500],
        'url': url[:1500],
        'date': str(item.get('date', '')).strip()[:30],
        'publisher': str(item.get('publisher', '')).strip()[:200],
        'source_type': str(item.get('source_type', 'știre')).strip()[:80],
        'official': bool(item.get('official')),
    }


def _evidence_cache_is_fresh(cached):
    if not isinstance(cached, dict) or not cached.get('fetched_at'):
        return False
    try:
        fetched = datetime.datetime.fromisoformat(cached['fetched_at'].replace('Z', '+00:00'))
        if fetched.tzinfo is not None:
            fetched = fetched.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return _utc_now_naive() - fetched < datetime.timedelta(hours=PORTFOLIO_EVIDENCE_CACHE_HOURS)
    except (TypeError, ValueError):
        return False


def _fetch_yahoo_company_news(symbol, session):
    encoded_symbol = urllib.parse.quote(symbol, safe='.-^')
    url = f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={encoded_symbol}&region=US&lang=en-US'
    response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=12)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    items = []
    for index, node in enumerate(root.findall('./channel/item')[:5]):
        title_node = node.find('title')
        link_node = node.find('link')
        date_node = node.find('pubDate')
        if title_node is None or link_node is None:
            continue
        item = _clean_evidence_item({
            'source_id': f'{symbol}-news-{index + 1}',
            'symbol': symbol,
            'title': title_node.text or '',
            'url': link_node.text or '',
            'date': date_node.text if date_node is not None else '',
            'publisher': 'Yahoo Finance RSS',
            'source_type': 'știre financiară',
            'official': False,
        })
        if item:
            items.append(item)
    return items


def _fetch_sec_ticker_map(session):
    response = session.get(
        SEC_TICKER_MAP_URL,
        headers={'User-Agent': 'MarketScanner risk dashboard admin@marketscanner.local'},
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    return {
        str(entry.get('ticker', '')).upper(): int(entry['cik_str'])
        for entry in payload.values()
        if isinstance(entry, dict) and entry.get('ticker') and entry.get('cik_str') is not None
    }


def _fetch_sec_filings(symbol, cik, session):
    response = session.get(
        SEC_SUBMISSIONS_URL.format(cik=cik),
        headers={'User-Agent': 'MarketScanner risk dashboard admin@marketscanner.local'},
        timeout=15,
    )
    response.raise_for_status()
    recent = response.json().get('filings', {}).get('recent', {})
    accepted_forms = {'10-K', '10-Q', '8-K', '6-K', '20-F', '40-F', 'DEF 14A'}
    items = []
    forms = recent.get('form', [])
    for index, form in enumerate(forms):
        if form not in accepted_forms:
            continue
        accession = str(recent.get('accessionNumber', [''])[index])
        document = str(recent.get('primaryDocument', [''])[index])
        filing_date = str(recent.get('filingDate', [''])[index])
        if not accession or not document:
            continue
        accession_compact = accession.replace('-', '')
        url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{accession_compact}/{document}'
        item = _clean_evidence_item({
            'source_id': f'{symbol}-sec-{accession_compact}',
            'symbol': symbol,
            'title': f'Depunere SEC {form}',
            'url': url,
            'date': filing_date,
            'publisher': 'U.S. Securities and Exchange Commission',
            'source_type': f'raport oficial {form}',
            'official': True,
        })
        if item:
            items.append(item)
        if len(items) >= 4:
            break
    return items


def _bvb_calendar_evidence(symbol, calendar_events):
    base_symbol = symbol.upper().replace('.RO', '')
    items = []
    for event in calendar_events or []:
        event_name = str(event.get('name', ''))
        if base_symbol not in event_name.upper():
            continue
        item = _clean_evidence_item({
            'source_id': f"{symbol}-bvb-{event.get('id', len(items))}",
            'symbol': symbol,
            'title': event_name,
            'url': event.get('source_url', BVB_CALENDAR_URL),
            'date': event.get('datetime', ''),
            'publisher': 'Bursa de Valori București',
            'source_type': 'calendar/raportare oficială BVB',
            'official': True,
        })
        if item:
            items.append(item)
    return items[:4]


def collect_portfolio_evidence(snapshot, cached=None, request_session=None, now=None):
    """Colectează metadate verificabile; la eroare păstrează ultimul cache valid."""
    now = now or _utc_now_naive()
    symbols = [
        item['symbol']
        for item in (
            list(snapshot.get('positions', []))
            + list(snapshot.get('buy_candidates', []))
        )
        if item.get('symbol')
    ]
    symbols = list(dict.fromkeys(symbols))
    cached_has_cross_market_sec = any(
        str(item.get('symbol', '')).upper().endswith('.RO')
        and '-sec-' in str(item.get('source_id', '')).lower()
        for item in (cached or {}).get('items', [])
        if isinstance(item, dict)
    )
    if _evidence_cache_is_fresh(cached) and not cached_has_cross_market_sec:
        cached_symbols = set(cached.get('symbols', []))
        if cached_symbols == set(symbols):
            return cached

    session = request_session or requests.Session()
    previous_items = [
        clean for clean in (_clean_evidence_item(item) for item in (cached or {}).get('items', []))
        if (
            clean
            and not (
                clean['symbol'].endswith('.RO')
                and '-sec-' in clean['source_id'].lower()
            )
        )
    ]
    items = []
    sec_map = {}
    try:
        sec_map = _fetch_sec_ticker_map(session)
    except (requests.RequestException, ValueError, TypeError, KeyError):
        pass

    calendar_events = []
    try:
        calendar_events = get_economic_events(now=datetime.datetime.now(), request_session=session)
    except (requests.RequestException, ValueError, TypeError, KeyError):
        pass

    for symbol in symbols:
        try:
            items.extend(_fetch_yahoo_company_news(symbol, session))
        except (requests.RequestException, ValueError, TypeError, ET.ParseError):
            pass
        sec_symbol = symbol.split('.')[0]
        if not symbol.upper().endswith('.RO') and sec_symbol in sec_map:
            try:
                items.extend(_fetch_sec_filings(symbol, sec_map[sec_symbol], session))
            except (requests.RequestException, ValueError, TypeError, KeyError, IndexError):
                pass
        if symbol.endswith('.RO'):
            items.extend(_bvb_calendar_evidence(symbol, calendar_events))

    if not items:
        items = previous_items
    unique = {}
    for item in items:
        unique[item['source_id']] = item
    return {
        'fetched_at': now.isoformat(timespec='seconds'),
        'symbols': symbols,
        'items': list(unique.values())[:60],
        'status': 'actualizat' if items and items != previous_items else (
            'cache păstrat' if items else 'indisponibil'
        ),
    }


def _position_calendar_effects(snapshot):
    """Produce un context minim verificabil chiar dacă modelul omite calendarul."""
    events = snapshot.get('economic_calendar', [])
    reference_dt = _parse_event_date(snapshot.get('as_of')) or datetime.datetime.now()

    def event_is_upcoming(event):
        status = str(event.get('status', '')).lower()
        if status in {'upcoming', 'future', 'viitor'}:
            return True
        if status in {'past', 'trecut'}:
            return False
        event_dt = _parse_event_date(event.get('datetime'))
        return bool(event_dt and event_dt > reference_dt)

    def event_sort_key(event):
        event_dt = _parse_event_date(event.get('datetime'))
        return event_dt or datetime.datetime.min

    effects = {}
    for position in snapshot.get('positions', []):
        symbol = position['symbol']
        market = position.get('market')
        country_priority = (
            {'SUA': 0}
            if market == 'SUA'
            else {'România': 0, 'Europa': 1}
        )
        relevant = [
            event for event in events
            if event.get('country') in country_priority
        ]
        if not relevant:
            effects[symbol] = (
                "Nu sunt disponibile evenimente economice relevante în fereastra calendarului; "
                "stopul se evaluează din preț, volatilitate și știrile companiei."
            )
            continue
        upcoming = sorted(
            (event for event in relevant if event_is_upcoming(event)),
            key=lambda event: (
                country_priority.get(event.get('country'), 9),
                event_sort_key(event),
            ),
        )[:3]
        if upcoming:
            labels = [
                f"{event.get('name', 'Eveniment')} "
                f"({event.get('datetime', 'dată indisponibilă')})"
                for event in upcoming
            ]
            region_note = (
                "Evenimentele din România au prioritate; cele europene sunt "
                "incluse numai pentru transmiterea prin dobânzi, EUR/RON și sentiment. "
                if market != 'SUA'
                else ''
            )
            effects[symbol] = (
                "Evenimente viitoare relevante: " + "; ".join(labels) + ". "
                + region_note
                + "Pot crește volatilitatea; nu lărgi stopul înaintea publicării."
            )
            continue
        recent = sorted(relevant, key=event_sort_key, reverse=True)[:3]
        labels = [
            f"{event.get('name', 'Eveniment')} ({event.get('datetime', 'dată indisponibilă')})"
            for event in recent
        ]
        effects[symbol] = (
            "Evenimente recente deja publicate: " + "; ".join(labels)
            + ". Nu mai reprezintă un risc viitor de publicare; evaluează reacția "
            "deja produsă în preț și nu modifica stopul doar din cauza lor."
        )
    return effects


def _candidate_calendar_effects(snapshot):
    """Aplică aceeași validare temporală și candidaților de cumpărare."""
    candidate_snapshot = {
        'as_of': snapshot.get('as_of'),
        'economic_calendar': snapshot.get('economic_calendar', []),
        'positions': [
            {
                'symbol': candidate.get('symbol'),
                'market': candidate.get('market'),
            }
            for candidate in snapshot.get('buy_candidates', [])
            if candidate.get('symbol')
        ],
    }
    return _position_calendar_effects(candidate_snapshot)


def _validate_buy_recommendations(
    raw_items, candidate_symbols, evidence_ids=None,
    candidate_calendar_effects=None, require_complete=False,
):
    """Validează recomandările BUY și poate impune acoperirea fiecărui candidat."""
    candidate_symbols = candidate_symbols or set()
    evidence_ids = evidence_ids or set()
    allowed_buy_verdicts = {
        'Candidat valid', 'Pregătit la trigger', 'Foarte aproape',
        'Urmărește', 'Evită', 'Așteaptă',
    }
    buy_recommendations = []
    for raw in raw_items or []:
        if not isinstance(raw, dict):
            continue
        symbol = str(raw.get('symbol', '')).strip().upper()
        verdict = str(raw.get('verdict', '')).strip()
        if symbol not in candidate_symbols or verdict not in allowed_buy_verdicts:
            continue
        item = {'symbol': symbol, 'verdict': verdict}
        for field in (
            'market', 'why_now', 'market_effect', 'news_effect',
            'calendar_effect', 'main_risk',
        ):
            value = raw.get(field)
            if (
                field == 'calendar_effect'
                and (candidate_calendar_effects or {}).get(symbol)
            ):
                value = candidate_calendar_effects[symbol]
            if not isinstance(value, str) or not value.strip():
                break
            item[field] = value.strip()[:700]
        else:
            item['source_ids'] = [
                str(source_id) for source_id in raw.get('source_ids', [])
                if str(source_id) in evidence_ids
            ][:5]
            buy_recommendations.append(item)
    if require_complete:
        returned_symbols = [item['symbol'] for item in buy_recommendations]
        if (
            len(returned_symbols) != len(candidate_symbols)
            or set(returned_symbols) != set(candidate_symbols)
        ):
            missing = sorted(set(candidate_symbols) - set(returned_symbols))
            raise ValueError(
                'Răspuns AI incomplet pentru candidați'
                + (f": {', '.join(missing)}" if missing else '')
            )
    return buy_recommendations


def _validate_portfolio_ai_result(
    result, symbols, evidence_ids=None, candidate_symbols=None,
    calendar_effects=None, candidate_calendar_effects=None,
    require_complete_candidates=False,
):
    allowed_severity = {'critic', 'ridicat', 'mediu', 'scăzut', 'informativ'}
    evidence_ids = evidence_ids or set()
    clean_items = []
    for raw in result.get('priorities', [])[:12]:
        if not isinstance(raw, dict):
            continue
        symbol = str(raw.get('symbol', '')).strip().upper()
        severity = str(raw.get('severity', '')).strip().lower()
        if symbol not in symbols or severity not in allowed_severity:
            continue
        item = {'symbol': symbol, 'severity': severity}
        for field in ('issue', 'evidence', 'action', 'why', 'review_trigger', 'confidence'):
            value = raw.get(field)
            if not isinstance(value, str) or not value.strip():
                break
            item[field] = value.strip()[:900]
        else:
            raw_source_ids = raw.get('source_ids', [])
            item['source_ids'] = [
                str(source_id) for source_id in raw_source_ids
                if str(source_id) in evidence_ids
            ][:5]
            clean_items.append(item)
    if not clean_items:
        raise ValueError('Răspuns AI fără priorități valide')
    overview = str(result.get('portfolio_overview', '')).strip()[:1600]
    if not overview:
        raise ValueError('Răspuns AI fără rezumat valid')
    market_read = str(result.get('market_read', '')).strip()[:1200]
    if not market_read:
        raise ValueError('Răspuns AI fără context de piață')
    allowed_actions = {'Menține', 'Protejează profitul', 'Redu', 'Ieși', 'Urmărește atent'}
    position_actions = []
    for raw in result.get('position_actions', []):
        if not isinstance(raw, dict):
            continue
        symbol = str(raw.get('symbol', '')).strip().upper()
        action = str(raw.get('action', '')).strip()
        if symbol not in symbols or action not in allowed_actions:
            continue
        plain_reason = str(raw.get('plain_reason', '')).strip()[:500]
        raw_calendar_effect = str(raw.get('calendar_effect', '')).strip()
        deterministic_calendar_effect = str(
            (calendar_effects or {}).get(symbol, '')
        ).strip()
        calendar_effect = (
            deterministic_calendar_effect
            if deterministic_calendar_effect
            else raw_calendar_effect
        )[:500]
        next_check = str(raw.get('next_check', '')).strip()[:400]
        if plain_reason and calendar_effect and next_check:
            position_actions.append({
                'symbol': symbol,
                'broker': str(raw.get('broker', '')).strip()[:40],
                'action': action,
                'plain_reason': plain_reason,
                'calendar_effect': calendar_effect,
                'next_check': next_check,
            })
    if not position_actions:
        raise ValueError('Răspuns AI fără acțiuni clare pe poziții')
    buy_recommendations = _validate_buy_recommendations(
        result.get('buy_recommendations', []),
        candidate_symbols or set(),
        evidence_ids,
        candidate_calendar_effects,
        require_complete=require_complete_candidates,
    )
    return {
        'portfolio_overview': overview,
        'market_read': market_read,
        'position_actions': position_actions,
        'priorities': clean_items,
        'buy_recommendations': buy_recommendations,
    }


def _render_portfolio_ai_html(snapshot, result=None, source_label='Reguli de risc'):
    severity_colors = {
        'critic': '#b91c1c', 'ridicat': '#dc2626', 'mediu': '#d97706',
        'scăzut': '#2563eb', 'informativ': '#64748b',
    }
    if result:
        cards = []
        evidence_lookup = {
            evidence['source_id']: evidence
            for position in snapshot.get('positions', [])
            for evidence in position.get('evidence', [])
        }
        for item in result['priorities']:
            color = severity_colors[item['severity']]
            source_links = []
            for source_id in item.get('source_ids', []):
                evidence = evidence_lookup.get(source_id)
                if not evidence:
                    continue
                official_label = 'oficial' if evidence['official'] else 'presă'
                source_links.append(
                    f"<a href='{html.escape(evidence['url'], quote=True)}' target='_blank' "
                    f"rel='noopener noreferrer' style='color:var(--primary-purple);'>"
                    f"{html.escape(evidence['title'])} · {html.escape(evidence['date'])} · {official_label}</a>"
                )
            sources_html = (
                f"<p style='margin:5px 0;color:var(--text-secondary);'><b>Surse relevante:</b> "
                + ' | '.join(source_links) + "</p>"
                if source_links else ''
            )
            cards.append(
                "<details style='background:var(--bg-white);border:1px solid var(--border-light);"
                f"border-left:4px solid {color};border-radius:var(--radius-sm);padding:14px 16px;'>"
                f"<summary style='cursor:pointer;font-weight:700;color:var(--text-primary);'>"
                f"{html.escape(item['symbol'])} · {html.escape(item['issue'])}"
                f"<span style='float:right;color:{color};font-size:12px;text-transform:uppercase;'>"
                f"{html.escape(item['severity'])}</span></summary>"
                f"<p style='margin:10px 0 5px;color:var(--text-secondary);'><b>Dovezi:</b> {html.escape(item['evidence'])}</p>"
                f"<p style='margin:5px 0;color:var(--text-secondary);'><b>Acțiune de verificat:</b> {html.escape(item['action'])}</p>"
                f"<p style='margin:5px 0;color:var(--text-secondary);'><b>De ce:</b> {html.escape(item['why'])}</p>"
                f"<p style='margin:5px 0;color:var(--text-secondary);'><b>Reevaluare:</b> {html.escape(item['review_trigger'])}</p>"
                f"<p style='margin:5px 0;color:var(--text-secondary);'><b>Încredere:</b> {html.escape(item['confidence'])}</p>"
                f"{sources_html}"
                "</details>"
            )
        overview = html.escape(result['portfolio_overview'])
        market_read_html = html.escape(result['market_read'])
        action_colors = {
            'Menține': '#2563eb',
            'Protejează profitul': '#16a34a',
            'Redu': '#d97706',
            'Ieși': '#dc2626',
            'Urmărește atent': '#7c3aed',
        }
        position_action_cards = []
        for item in result['position_actions']:
            action_color = action_colors.get(item['action'], '#64748b')
            position_action_cards.append(
                "<div style='background:var(--bg-white);border:1px solid var(--border-light);"
                f"border-top:4px solid {action_color};border-radius:var(--radius-sm);padding:13px 15px;flex:1;min-width:240px;'>"
                f"<div style='display:flex;justify-content:space-between;gap:10px;'>"
                f"<b>{html.escape(item['symbol'])} · {html.escape(item['broker'])}</b>"
                f"<span style='color:{action_color};font-weight:700;'>{html.escape(item['action'])}</span></div>"
                f"<p style='margin:8px 0 5px;color:var(--text-secondary);'>{html.escape(item['plain_reason'])}</p>"
                f"<p style='margin:5px 0;font-size:12px;color:var(--text-secondary);'><b>Calendar:</b> "
                f"{html.escape(item['calendar_effect'])}</p>"
                f"<p style='margin:0;font-size:12px;color:var(--text-secondary);'><b>Urmărește:</b> "
                f"{html.escape(item['next_check'])}</p></div>"
            )
    else:
        cards = []
        market_read_html = 'Contextul pieței nu este disponibil momentan.'
        position_action_cards = []
        for position in snapshot.get('positions', []):
            for flag in position.get('data_flags', []):
                cards.append(
                    "<div style='background:var(--bg-white);border:1px solid var(--border-light);"
                    "border-left:4px solid #d97706;border-radius:var(--radius-sm);padding:14px 16px;'>"
                    f"<b>{html.escape(position['symbol'])}</b> · {html.escape(flag)}</div>"
                )
        overview = (
            'Analiza AI nu este disponibilă momentan. Sunt afișate controalele deterministe '
            'calculate exclusiv din datele portofoliului și ordinele active.'
        )
    if not cards:
        cards.append(
            "<div style='color:var(--text-secondary);padding:12px 0;'>"
            "Nu au fost identificate alerte din datele disponibile. Absența alertelor nu elimină riscul.</div>"
        )
    summary = snapshot.get('portfolio', {})
    liquidity = snapshot.get('account_liquidity', {})
    account_cards = []
    balance_labels = (
        ('NetLiquidation', 'Valoare totală / NAV'),
        ('GrossPositionValue', 'Valoare dețineri'),
        ('CostBasis', 'Cost investiție'),
        ('RelativeProfit', 'Profit relativ'),
        ('TotalCashValue', 'Cash total'),
        ('SettledCash', 'Cash decontat'),
        ('AvailableFunds', 'Fonduri disponibile'),
        ('BuyingPower', 'Putere de cumpărare'),
        ('ExcessLiquidity', 'Exces de lichiditate'),
        ('InitMarginReq', 'Marjă inițială'),
        ('MaintMarginReq', 'Marjă de menținere'),
    )
    if liquidity.get('privacy_mode') == 'exact':
        for account in liquidity.get('accounts', []):
            base_currency = html.escape(str(account.get('base_currency', '')))
            raw_summary = account.get('summary', {})
            balance_rows = []
            for key, label in balance_labels:
                if key not in raw_summary:
                    continue
                balance_rows.append(
                    "<div style='display:flex;justify-content:space-between;gap:18px;'>"
                    f"<span>{html.escape(label)}</span>"
                    f"<b>{_safe_number(raw_summary.get(key)):,.2f} {base_currency}</b></div>"
                )
            if 'Cushion' in raw_summary:
                balance_rows.append(
                    "<div style='display:flex;justify-content:space-between;gap:18px;'>"
                    "<span>Cushion</span>"
                    f"<b>{_safe_number(raw_summary.get('Cushion')) * 100:.2f}%</b></div>"
                )
            cash_rows = [
                "<div style='display:flex;justify-content:space-between;gap:18px;'>"
                f"<span>Cash {html.escape(str(currency))}</span>"
                f"<b>{_safe_number(value):,.2f} {html.escape(str(currency))}</b></div>"
                for currency, value in account.get('cash_by_currency', {}).items()
            ]
            account_cards.append(
                "<div style='background:var(--bg-white);border:1px solid var(--border-light);"
                "border-radius:var(--radius-sm);padding:14px 16px;min-width:280px;flex:1;'>"
                f"<b>{html.escape(str(account.get('label', 'Cont broker')))}</b>"
                f"<div style='font-size:11px;color:var(--text-secondary);margin:3px 0 10px;'>"
                f"{html.escape(str(account.get('source', liquidity.get('source', ''))))} · "
                f"{html.escape(str(liquidity.get('fetched_at', 'dată indisponibilă')))}</div>"
                "<div style='display:grid;gap:5px;color:var(--text-secondary);font-size:13px;'>"
                + ''.join(balance_rows + cash_rows) + "</div></div>"
            )
    accounts_html = (
        "<details open style='margin:16px 0;'>"
        "<summary style='cursor:pointer;font-weight:700;color:var(--text-primary);'>"
        "Solduri brute brokeri</summary>"
        "<div style='display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;'>"
        + ''.join(account_cards) + "</div></details>"
        if account_cards else ''
    )
    return (
        "<section id='portfolio-ai-analysis' style='margin:30px 0;background:var(--light-purple-bg);"
        "border:1px solid var(--border-light);border-radius:var(--radius-md);padding:22px;'>"
        "<div style='display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap;'>"
        "<div><h3 style='margin:0;color:var(--primary-purple);'>Analiză AI — controlul riscului pentru swing trading</h3>"
        f"<p style='margin:8px 0 0;color:var(--text-secondary);line-height:1.55;'>{overview}</p></div>"
        f"<span style='font-size:12px;color:var(--text-secondary);'>Sursă analiză: {html.escape(source_label)}</span></div>"
        "<div style='background:var(--bg-white);border-left:4px solid var(--primary-purple);"
        "border-radius:var(--radius-sm);padding:13px 15px;margin:16px 0;'>"
        "<b>Ce fac piețele relevante</b>"
        f"<p style='margin:6px 0 0;color:var(--text-secondary);line-height:1.5;'>{market_read_html}</p></div>"
        "<div style='display:flex;gap:12px;flex-wrap:wrap;margin:16px 0;'>"
        + ''.join(position_action_cards) + "</div>"
        "<div style='display:flex;gap:10px;flex-wrap:wrap;margin:16px 0;'>"
        f"<span style='background:var(--bg-white);padding:7px 10px;border-radius:14px;'>Poziții: <b>{int(summary.get('position_count', 0))}</b></span>"
        f"<span style='background:var(--bg-white);padding:7px 10px;border-radius:14px;'>Fără stop: <b>{int(summary.get('positions_without_stop', 0))}</b></span>"
        f"<span style='background:var(--bg-white);padding:7px 10px;border-radius:14px;'>Acoperire incompletă: <b>{int(summary.get('positions_with_incomplete_stop_coverage', 0))}</b></span>"
        "</div>" + accounts_html
        + "<div style='display:grid;gap:10px;'>" + ''.join(cards) + "</div>"
        "<p style='font-size:11px;color:var(--text-secondary);margin:14px 0 0;'>"
        "Instrument de control, nu promisiune de randament și nu recomandare personalizată. "
        "Stopurile nu garantează prețul de execuție, în special la gap-uri sau lichiditate redusă.</p></section>"
    )


def _buy_recommendation_history_key(symbol, verdict, candidate):
    levels = [
        round(_safe_number(candidate.get(field)), 4)
        for field in ('entry_eur', 'stop_eur', 'target_eur')
    ]
    return '|'.join([str(symbol).upper(), str(verdict)] + [
        f'{value:.4f}' for value in levels
    ])


def update_buy_recommendation_history(
    previous_history, result, candidates, recorded_at=None, limit=120,
):
    """Păstrează numai semnalele executabile, fără a le confunda cu cele curente."""
    recorded_at = recorded_at or datetime.datetime.now().isoformat(
        timespec='seconds'
    )
    candidates_by_symbol = {
        str(item.get('symbol', '')).upper(): item
        for item in (candidates or [])
        if item.get('symbol')
    }
    history = [
        dict(item) for item in (previous_history or [])
        if isinstance(item, dict) and item.get('history_key')
    ]
    by_key = {item['history_key']: item for item in history}
    latest_by_symbol = {
        str(item.get('symbol', '')).upper(): item
        for item in (result or {}).get('buy_recommendations', [])
        if item.get('symbol')
    }
    for item in history:
        if item.get('is_current'):
            item['is_current'] = False
            item['closed_at'] = recorded_at
            replacement = latest_by_symbol.get(
                str(item.get('symbol', '')).upper()
            )
            if replacement:
                item['closed_verdict'] = str(
                    replacement.get('verdict') or 'Reevaluat'
                )
                item['closed_reason'] = str(
                    replacement.get('why_now')
                    or replacement.get('main_risk')
                    or ''
                )[:700]

    for recommendation in (result or {}).get('buy_recommendations', []):
        symbol = str(recommendation.get('symbol', '')).upper()
        verdict = str(recommendation.get('verdict', ''))
        candidate = candidates_by_symbol.get(symbol)
        if verdict not in ACTIONABLE_BUY_VERDICTS or not candidate:
            continue
        history_key = _buy_recommendation_history_key(
            symbol, verdict, candidate
        )
        snapshot = {
            'history_key': history_key,
            'symbol': symbol,
            'company_name': str(candidate.get('company_name') or ''),
            'market': str(
                candidate.get('market') or recommendation.get('market') or '-'
            ),
            'verdict': verdict,
            'action_label': (
                'Cumpărare acum'
                if verdict == 'Candidat valid'
                else 'Ordin la trigger'
            ),
            'entry_eur': round(_safe_number(candidate.get('entry_eur')), 4),
            'stop_eur': round(_safe_number(candidate.get('stop_eur')), 4),
            'target_eur': round(_safe_number(candidate.get('target_eur')), 4),
            'execution_currency': _execution_currency(candidate),
            'entry_native': round(
                _execution_value(candidate, 'entry_native', 'entry_eur'), 4
            ),
            'stop_native': round(
                _execution_value(candidate, 'stop_native', 'stop_eur'), 4
            ),
            'target_native': round(
                _execution_value(candidate, 'target_native', 'target_eur'), 4
            ),
            'rr_ratio': round(_safe_number(candidate.get('rr_ratio')), 3),
            'eligible_brokers': list(candidate.get('eligible_brokers') or []),
            'why_now': str(recommendation.get('why_now') or '')[:700],
            'main_risk': str(recommendation.get('main_risk') or '')[:700],
            'is_current': True,
            'closed_at': None,
            'closed_verdict': None,
            'closed_reason': None,
            'last_seen_at': recorded_at,
        }
        sizing_rows = []
        eur_per_native = _eur_per_native(candidate)
        for sizing in candidate.get('sizing_by_broker') or []:
            sizing_rows.append({
                'broker': str(sizing.get('broker') or '-'),
                'conditional_amount_eur': round(
                    _safe_number(sizing.get('conditional_amount_eur')), 2
                ),
                'execution_currency': str(
                    sizing.get('execution_currency')
                    or _execution_currency(candidate)
                ),
                'conditional_amount_native': round(
                    _safe_number(sizing.get('conditional_amount_native'))
                    or (
                        _safe_number(sizing.get('conditional_amount_eur'))
                        / eur_per_native
                    ),
                    2,
                ),
                'conditional_units': int(
                    _safe_number(sizing.get('conditional_units'))
                ),
            })
        snapshot['sizing_by_broker'] = sizing_rows
        if history_key in by_key:
            first_seen = by_key[history_key].get(
                'first_seen_at', recorded_at
            )
            by_key[history_key].update(snapshot)
            by_key[history_key]['first_seen_at'] = first_seen
        else:
            snapshot['first_seen_at'] = recorded_at
            history.append(snapshot)
            by_key[history_key] = snapshot

    history.sort(
        key=lambda item: (
            bool(item.get('is_current')),
            str(item.get('last_seen_at') or ''),
        ),
        reverse=True,
    )
    return history[:limit]


def update_buy_recommendation_history_from_cache(
    previous_history, cached_analysis, fallback_candidates=None, limit=120,
):
    """Arhivează rezultatul anterior înainte ca un cache nou să-l înlocuiască."""
    if not isinstance(cached_analysis, dict):
        return list(previous_history or [])
    cached_result = cached_analysis.get('result')
    if not isinstance(cached_result, dict):
        return list(previous_history or [])
    cached_candidates = cached_analysis.get('buy_candidates')
    if not isinstance(cached_candidates, list) or not cached_candidates:
        cached_candidates = list(fallback_candidates or [])
    return update_buy_recommendation_history(
        previous_history,
        cached_result,
        cached_candidates,
        recorded_at=cached_analysis.get('generated_at'),
        limit=limit,
    )


def _buy_recommendation_marker_labels(history):
    """Numerotează stabil recomandările fiecărui simbol în ordine cronologică."""
    grouped = {}
    for item in history or []:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get('symbol') or '').upper()
        history_key = str(item.get('history_key') or '')
        if symbol and history_key:
            grouped.setdefault(symbol, []).append(item)
    labels = {}
    for items in grouped.values():
        ordered = sorted(
            items,
            key=lambda item: (
                str(item.get('first_seen_at') or ''),
                str(item.get('last_seen_at') or ''),
                str(item.get('history_key') or ''),
            ),
        )
        for index, item in enumerate(ordered, start=1):
            labels[str(item['history_key'])] = f'C{index}'
    return labels


def _format_ro_datetime(value):
    """Formatează timestampurile ISO pentru interfața în limba română."""
    text = str(value or '').strip()
    if not text:
        return '-'
    try:
        parsed = datetime.datetime.fromisoformat(
            text.replace('Z', '+00:00')
        )
    except ValueError:
        return text
    has_time = 'T' in text or ' ' in text
    return parsed.strftime(
        '%d.%m.%Y %H:%M' if has_time else '%d.%m.%Y'
    )


def _render_buy_recommendation_history(history, candidates=None):
    if not history:
        return ''
    marker_labels = _buy_recommendation_marker_labels(history)
    candidates_by_symbol = {
        str(candidate.get('symbol') or '').upper(): candidate
        for candidate in (candidates or [])
    }
    rows = []
    for item in history:
        symbol = str(item.get('symbol') or '').upper()
        marker_label = marker_labels.get(
            str(item.get('history_key') or ''),
            'C?',
        )
        status = 'Activă' if item.get('is_current') else 'Încheiată'
        status_color = '#16a34a' if item.get('is_current') else '#64748b'
        current_candidate = candidates_by_symbol.get(
            str(item.get('symbol') or '').upper()
        )
        execution_currency = str(
            item.get('execution_currency')
            or (
                _execution_currency(current_candidate)
                if current_candidate else 'EUR'
            )
        ).upper()
        history_eur_per_native = (
            _eur_per_native(current_candidate)
            if current_candidate else 1.0
        )

        def history_native(native_field, eur_field):
            native_value = _safe_number(item.get(native_field))
            if native_value > 0:
                return native_value
            return (
                _safe_number(item.get(eur_field))
                / history_eur_per_native
            )

        sizing_text = ' · '.join(
            f"{row.get('broker', '-')}: "
            + _format_execution_money(
                row.get('conditional_amount_native')
                or (
                    _safe_number(row.get('conditional_amount_eur'))
                    / history_eur_per_native
                ),
                row.get('execution_currency') or execution_currency,
            )
            + (
                f" / {int(row.get('conditional_units') or 0)} unități"
                if int(row.get('conditional_units') or 0) else ''
            )
            for row in item.get('sizing_by_broker') or []
        )
        closed_reason_html = ''
        if not item.get('is_current') and (
            item.get('closed_verdict') or item.get('closed_reason')
        ):
            closed_at = _format_ro_datetime(item.get('closed_at'))
            closed_label = (
                f"Retrasă după reevaluare la {closed_at}"
                if closed_at != '-'
                else "Retrasă după reevaluare"
            )
            closed_reason_html = (
                f"<br><b>{html.escape(closed_label)}:</b> "
                f"{html.escape(str(item.get('closed_verdict') or '-'))}"
                + (
                    f" — {html.escape(str(item.get('closed_reason')))}"
                    if item.get('closed_reason') else ''
                )
            )
        rows.append(
            "<details style='background:var(--bg-white);border:1px solid "
            "var(--border-light);border-radius:var(--radius-sm);padding:11px 13px;'>"
            f"<summary style='cursor:pointer;font-weight:700;'>"
            f"{html.escape(symbol)} · "
            f"{html.escape(str(item.get('action_label') or ''))}"
            f"<span style='float:right;color:{status_color};'>{status}</span>"
            "</summary>"
            "<div style='font-size:13px;line-height:1.55;margin-top:8px;'>"
            f"<b>Prima apariție:</b> {html.escape(_format_ro_datetime(item.get('first_seen_at')))}"
            f" · <b>Ultima confirmare:</b> {html.escape(_format_ro_datetime(item.get('last_seen_at')))}"
            f"<br><b>Niveluri:</b> entry "
            f"{_format_execution_money(history_native('entry_native', 'entry_eur'), execution_currency)}"
            f" · stop {_format_execution_money(history_native('stop_native', 'stop_eur'), execution_currency)}"
            f" · target {_format_execution_money(history_native('target_native', 'target_eur'), execution_currency)}"
            f" · R:R {float(item.get('rr_ratio') or 0):.2f}"
            "<br>"
            f"<a href='#' data-symbol='{html.escape(symbol, quote=True)}' "
            "onclick=\"openBuyRecommendationDetail(this.dataset.symbol);return false;\" "
            "style='color:var(--primary-purple);font-weight:700;text-decoration:none;'>"
            f"📈 Grafic OHLC · marcaj {html.escape(marker_label)}</a>"
            + (
                f"<br><b>Dimensionare la momentul recomandării:</b> "
                f"{html.escape(sizing_text)}" if sizing_text else ''
            )
            + f"<br><b>Motiv:</b> {html.escape(str(item.get('why_now') or '-'))}"
            f"<br><b>Risc:</b> {html.escape(str(item.get('main_risk') or '-'))}"
            + closed_reason_html
            + "</div></details>"
        )
    return (
        "<details open style='margin-top:18px;background:rgba(255,255,255,.55);"
        "border:1px solid var(--border-light);border-radius:var(--radius-sm);"
        "padding:13px 15px;'>"
        f"<summary style='cursor:pointer;font-weight:700;'>Istoric recomandări executabile ({len(history)})</summary>"
        "<p style='color:var(--text-secondary);font-size:12px;line-height:1.45;'>"
        "Istoricul păstrează semnalele care au fost cândva „Cumpărare acum” "
        "sau „Ordin la trigger”. O intrare încheiată nu mai este o recomandare curentă."
        "</p><div style='display:grid;gap:8px;'>"
        + ''.join(rows) + "</div></details>"
    )


def render_buy_recommendations_html(
    result, candidates, evidence_cache=None, bvb_universe_stats=None,
    us_universe_stats=None, recommendation_history=None,
):
    """Carduri BUY stricte, validate AI cu știri, piață și calendar."""
    candidates_by_symbol = {
        str(item.get('symbol', '')).upper(): item for item in (candidates or [])
    }
    recommendations_by_symbol = {
        str(item.get('symbol', '')).upper(): item
        for item in (result or {}).get('buy_recommendations', [])
        if str(item.get('symbol', '')).upper() in candidates_by_symbol
    }
    recommendations = []
    for symbol, candidate in candidates_by_symbol.items():
        recommendation = recommendations_by_symbol.get(symbol)
        if not recommendation:
            recommendation = {
                'symbol': symbol,
                'market': candidate.get('market') or '-',
                'verdict': 'Neanalizat',
                'why_now': (
                    'Candidatul a trecut selecția deterministă, dar nu a primit încă '
                    'o validare AI pentru datele curente.'
                ),
                'market_effect': 'Contextul curent nu a fost încă validat de AI.',
                'news_effect': 'Știrile și rapoartele nu au fost încă validate de AI.',
                'calendar_effect': 'Calendarul curent nu a fost încă validat de AI.',
                'main_risk': (
                    'Nu deschide poziția până la finalizarea validării curente. '
                    'Aceasta nu este o respingere a candidatului.'
                ),
                'source_ids': [],
            }
        if (
            candidate.get('requires_watchlist_filters', True)
            and not candidate.get('strict_eligible', True)
        ):
            recommendation = dict(recommendation)
            recommendation['verdict'] = 'Așteaptă'
            recommendation['main_risk'] = (
                'LQQ este verificat la fiecare rulare, dar nu trece acum toate '
                'condițiile BUY + consensus Buy/Strong Buy + R:R ≥ 3.'
            )
        recommendations.append(recommendation)
    visible_recommendations = [
        item for item in recommendations
        if (
            item.get('verdict') in ACTIONABLE_BUY_VERDICTS
            or str(item.get('symbol', '')).upper() == 'LQQ.PA'
        )
    ]
    evidence_lookup = {
        str(item.get('source_id')): item
        for item in (evidence_cache or {}).get('items', [])
    }
    if not candidates_by_symbol:
        body = (
            "<p style='color:var(--text-secondary);margin:0;'>"
            "Nu există momentan acțiuni care să treacă simultan filtrele BUY, "
            "consensus Buy/Strong Buy și R:R de minimum 3. Universurile SUA și BVB "
            "rămân în cercetare și vor fi adăugate în watchlist numai după scanare.</p>"
        )
    else:
        cards = []
        represented_markets = set()
        for item in visible_recommendations:
            symbol = str(item['symbol']).upper()
            candidate = candidates_by_symbol[symbol]
            verdict = item['verdict']
            action_label = (
                'Cumpărare acum'
                if verdict == 'Candidat valid'
                else 'Ordin la trigger'
                if verdict == 'Pregătit la trigger'
                else 'LQQ monitorizat'
            )
            represented_markets.add(str(candidate.get('market') or item.get('market', '')))
            color = (
                '#16a34a' if verdict == 'Candidat valid'
                else '#2563eb' if verdict == 'Pregătit la trigger'
                else '#d97706' if verdict in {'Foarte aproape', 'Urmărește', 'Așteaptă'}
                else '#64748b' if verdict == 'Neanalizat'
                else '#dc2626'
            )
            execution_currency = _execution_currency(candidate)
            entry_value = _execution_value(
                candidate, 'entry_native', 'entry_eur'
            )
            stop_value = _execution_value(
                candidate, 'stop_native', 'stop_eur'
            )
            target_value = _execution_value(
                candidate, 'target_native', 'target_eur'
            )
            sizing_rows = candidate.get('sizing_by_broker') or [{
                key: candidate.get(key) for key in (
                    'broker', 'broker_available_cash_eur', 'broker_net_liquidation_eur',
                    'broker_available_cash_native_equivalent',
                    'conditional_amount_eur', 'conditional_amount_native',
                    'conditional_units', 'risk_to_stop_pct', 'sizing_status',
                    'sizing_reason', 'execution_currency',
                )
            }]
            sizing_html = []
            for sizing in sizing_rows:
                sizing_currency = str(
                    sizing.get('execution_currency')
                    or execution_currency
                ).upper()
                conditional_amount = _safe_number(
                    sizing.get('conditional_amount_native')
                )
                if conditional_amount <= 0:
                    eur_per_native = _eur_per_native(candidate)
                    conditional_amount = (
                        _safe_number(sizing.get('conditional_amount_eur'))
                        / eur_per_native
                    )
                cash_equivalent = _safe_number(
                    sizing.get('broker_available_cash_native_equivalent')
                )
                if cash_equivalent <= 0:
                    eur_per_native = _eur_per_native(candidate)
                    cash_equivalent = (
                        _safe_number(sizing.get('broker_available_cash_eur'))
                        / eur_per_native
                    )
                filters_allow_action = (
                    not candidate.get('requires_watchlist_filters', True)
                    or candidate.get('strict_eligible', True)
                )
                immediate_buy = (
                    verdict == 'Candidat valid' and filters_allow_action
                )
                trigger_order = (
                    verdict == 'Pregătit la trigger' and filters_allow_action
                )
                displayed_amount = (
                    conditional_amount
                    if immediate_buy or trigger_order else 0
                )
                displayed_units = (
                    int(sizing.get('conditional_units') or 0)
                    if displayed_amount > 0 else 0
                )
                broker = str(sizing.get('broker') or '-')
                if immediate_buy:
                    sizing_title = 'sumă orientativă pentru cumpărare acum'
                    execution_note = (
                        'Semnalul este executabil la nivelul indicat; verifică '
                        'prețul și spreadul înainte de ordin.'
                    )
                elif trigger_order:
                    sizing_title = 'buget pentru ordin condiționat la trigger'
                    execution_note = (
                        'Nu cumpăra la piață înainte de trigger; ordinul se '
                        'execută numai după atingerea nivelului de intrare.'
                    )
                else:
                    sizing_title = 'sumă de cumpărat acum'
                    execution_note = (
                        'LQQ rămâne monitorizat, dar nu are acum semnal executabil.'
                    )
                sizing_html.append(
                    "<div style='background:var(--light-purple-bg);border-radius:var(--radius-sm);"
                    "padding:10px 12px;margin:8px 0;font-size:13px;'>"
                    f"<b>{html.escape(broker)} — {sizing_title}:</b> "
                    f"{html.escape(_format_execution_money(displayed_amount, sizing_currency))}"
                    + (
                        f" · aproximativ {displayed_units} unități"
                        if displayed_units else ''
                    )
                    + f"<br><span style='color:var(--text-secondary);'>"
                    f"{html.escape(execution_note)} Cash utilizabil echivalent: "
                    f"{html.escape(_format_execution_money(cash_equivalent, sizing_currency))}; "
                    f"risc până la stop {float(sizing.get('risk_to_stop_pct') or 0):.2f}%."
                    "</span></div>"
                )
            if (
                not candidate.get('requires_watchlist_filters', True)
                or candidate.get('strict_eligible', True)
            ):
                if verdict == 'Neanalizat':
                    why_now = item['why_now']
                else:
                    why_now = (
                        (
                            f"Ideea a fost găsită prin cercetare externă și nu este "
                            f"supusă filtrului watchlistului. "
                            if candidate.get('candidate_source') == 'external_research'
                            else
                            f"Scannerul confirmă BUY, consensus {candidate.get('consensus')}, "
                            f"R:R {float(candidate.get('rr_ratio') or 0):.2f}. "
                        )
                        + f"Nivelul urmărit este "
                        f"{_format_execution_money(entry_value, execution_currency)}, "
                        f"iar verdictul AI este "
                        f"{verdict.lower()} după verificarea contextului. "
                        + str(item.get('why_now') or '')
                    )
            else:
                why_now = (
                    "LQQ este analizat obligatoriu la fiecare rulare, dar acum nu "
                    "îndeplinește simultan toate condițiile necesare cumpărării."
                )
            source_links = []
            for source_id in item.get('source_ids', []):
                source = evidence_lookup.get(str(source_id))
                if source:
                    source_links.append(
                        f"<a href='{html.escape(source['url'], quote=True)}' target='_blank' "
                        f"rel='noopener noreferrer'>{html.escape(source['title'])}</a>"
                    )
            sources_html = (
                "<p style='margin:7px 0 0;font-size:12px;'><b>Surse:</b> "
                + " | ".join(source_links) + "</p>"
                if source_links else ''
            )
            overlap_html = ''
            if candidate.get('market') == 'România / BVB':
                observations = int(
                    float(candidate.get('liquidity_observations_20d') or 0)
                )
                active_days = int(float(candidate.get('active_days_20d') or 0))
                median_turnover = float(
                    candidate.get('median_turnover_20d_ron') or 0
                )
                relative_volume = candidate.get('relative_volume_20d')
                liquidity_cap = float(
                    candidate.get('liquidity_position_cap_eur') or 0
                )
                liquidity_cap_native = (
                    liquidity_cap / _eur_per_native(candidate)
                    if liquidity_cap > 0 else 0
                )
                liquidity_details = (
                    f"{median_turnover:,.0f} RON mediană/ședință"
                    if median_turnover > 0 else
                    "istoric de rulaj în curs de completare"
                )
                if observations:
                    liquidity_details += (
                        f" · {active_days}/{observations} ședințe active"
                    )
                if relative_volume is not None:
                    liquidity_details += (
                        f" · volum curent {float(relative_volume):.2f}× mediana"
                    )
                if liquidity_cap > 0:
                    liquidity_details += (
                        " · plafon orientativ al ordinului "
                        f"{_format_execution_money(liquidity_cap_native, execution_currency)}"
                    )
                overlap_html = (
                    "<div style='background:#fff7ed;border-radius:var(--radius-sm);"
                    "padding:9px 12px;margin:8px 0;font-size:13px;'>"
                    "<b>Expunere portofoliu înainte de cumpărare (normalizată în EUR):</b> "
                    f"€{float(candidate.get('direct_exposure_eur') or 0):,.2f} direct + "
                    f"€{float(candidate.get('indirect_exposure_eur') or 0):,.2f} prin TVBETETF"
                    f" · total €{float(candidate.get('combined_pretrade_exposure_eur') or 0):,.2f}. "
                    f"Pondere în ETF: {float(candidate.get('tvbetetf_weight_pct') or 0):.2f}%"
                    f" · suprapunere {html.escape(str(candidate.get('overlap_risk') or 'necunoscută'))}."
                    "<br><b>Lichiditate locală:</b> "
                    f"{html.escape(str(candidate.get('bvb_market_segment') or 'segment necunoscut'))}"
                    f" · {html.escape(liquidity_details)}"
                    f" · {html.escape(str(candidate.get('liquidity_status') or 'date insuficiente'))}. "
                    f"{html.escape(str(candidate.get('liquidity_reason') or ''))}"
                    "</div>"
                )
            elif candidate.get('market') == 'SUA':
                relative_1m = candidate.get('sector_relative_1m_vs_spy_pct')
                relative_3m = candidate.get('sector_relative_3m_vs_spy_pct')
                overlap_html = (
                    "<div style='background:#eff6ff;border-radius:var(--radius-sm);"
                    "padding:9px 12px;margin:8px 0;font-size:13px;'>"
                    f"<b>Rotație sectorială:</b> "
                    f"{html.escape(str(candidate.get('sector') or 'Sector necunoscut'))} · "
                    f"{html.escape(str(candidate.get('sector_rotation_status') or 'date insuficiente'))}"
                    + (
                        f" · vs SPY: {float(relative_1m):+.2f}% la 1 lună, "
                        f"{float(relative_3m):+.2f}% la 3 luni"
                        if relative_1m is not None and relative_3m is not None
                        else ''
                    )
                    + f". Expunere existentă în sector (normalizată în EUR): "
                    f"€{float(candidate.get('existing_sector_exposure_eur') or 0):,.2f}."
                    f"<br><b>Regim SUA:</b> "
                    f"{html.escape(str(candidate.get('us_market_stage') or 'date insuficiente'))}"
                    f" · ciclu {html.escape(str(candidate.get('us_economic_phase') or 'date insuficiente'))}"
                    f" · sector {html.escape(str(candidate.get('cycle_fit') or 'neutru'))}."
                    "</div>"
                )
            data_age = candidate.get('data_age_hours')
            data_as_of = str(candidate.get('data_as_of') or '').strip()
            freshness_text = (
                f"actualizate acum {float(data_age):.1f} ore"
                if data_age is not None
                else "actualizare curentă confirmată de scanner"
            )
            if data_as_of:
                freshness_text += f" · data pieței {data_as_of}"
            level_basis = ' · '.join(
                str(value).strip()
                for value in (
                    candidate.get('trigger_basis'),
                    candidate.get('target_basis'),
                )
                if str(value or '').strip()
            )
            validation_details_html = (
                "<p style='margin:6px 0;font-size:12px;color:var(--text-secondary);'>"
                f"<b>Validarea nivelurilor:</b> {html.escape(freshness_text)}"
                + (
                    f" · {html.escape(level_basis)}"
                    if level_basis else ''
                )
                + "</p>"
            )
            cards.append(
                "<details style='background:var(--bg-white);border:1px solid var(--border-light);"
                f"border-left:4px solid {color};border-radius:var(--radius-sm);padding:14px 16px;'>"
                f"<summary style='cursor:pointer;font-weight:700;'>{html.escape(symbol)} · "
                f"{html.escape(str(candidate.get('company_name') or ''))}"
                f"<span style='float:right;color:{color};'>{html.escape(action_label)}</span></summary>"
                "<div style='display:flex;gap:12px;flex-wrap:wrap;margin:10px 0;font-size:13px;'>"
                f"<span><b>Piața instrumentului:</b> {html.escape(item['market'])}</span>"
                f"<span><b>Disponibil prin:</b> {html.escape(', '.join(candidate.get('eligible_brokers') or []))}</span>"
                f"<span><b>Moneda ordinului:</b> {html.escape(execution_currency)}</span>"
                f"<span><b>Consensus:</b> {html.escape(str(candidate.get('consensus')))}</span>"
                f"<span><b>R:R:</b> {float(candidate.get('rr_ratio') or 0):.2f}</span>"
                f"<span><b>Entry:</b> {html.escape(_format_execution_money(entry_value, execution_currency))}</span>"
                f"<span><b>Stop:</b> {html.escape(_format_execution_money(stop_value, execution_currency))}</span>"
                f"<span><b>Target:</b> {html.escape(_format_execution_money(target_value, execution_currency))}</span>"
                f"<a href='#' data-symbol='{html.escape(symbol, quote=True)}' "
                "onclick=\"openBuyRecommendationDetail(this.dataset.symbol);return false;\" "
                "style='color:var(--primary-purple);font-weight:700;text-decoration:none;'>"
                "📈 Grafic mare OHLC</a></div>"
                + overlap_html
                + ''.join(sizing_html)
                + validation_details_html
                + f"<p style='margin:6px 0;'><b>De ce acum:</b> {html.escape(why_now)}</p>"
                f"<p style='margin:6px 0;'><b>Piața:</b> {html.escape(item['market_effect'])}</p>"
                f"<p style='margin:6px 0;'><b>Știri:</b> {html.escape(item['news_effect'])}</p>"
                f"<p style='margin:6px 0;'><b>Calendar:</b> {html.escape(item['calendar_effect'])}</p>"
                f"<p style='margin:6px 0;'><b>Risc principal:</b> {html.escape(item['main_risk'])}</p>"
                f"{sources_html}</details>"
            )
        market_notices = []
        if 'SUA' not in represented_markets:
            market_notices.append(
                "<p style='margin:0;color:var(--text-secondary);'><b>SUA:</b> "
                "niciun candidat nu a trecut toate filtrele și validarea AI.</p>"
            )
        if 'România / BVB' not in represented_markets:
            market_notices.append(
                "<p style='margin:0;color:var(--text-secondary);'><b>România / BVB:</b> "
                "universul local este cercetat separat de watchlist; numai ideile validate "
                "sunt promovate ulterior în watchlist și în recomandări.</p>"
            )
        if 'Europa / Nasdaq-100' not in represented_markets:
            market_notices.append(
                "<p style='margin:0;color:var(--text-secondary);'><b>LQQ:</b> "
                "este verificat obligatoriu la fiecare rulare pentru IBKR și Tradeville.</p>"
            )
        notices_html = (
            "<div style='display:grid;gap:5px;margin-bottom:12px;'>"
            + ''.join(market_notices) + "</div>"
            if market_notices else ''
        )
        validated_count = len(recommendations_by_symbol)
        actionable_count = sum(
            item.get('verdict') in ACTIONABLE_BUY_VERDICTS
            for item in recommendations
        )
        validation_html = (
            "<p style='margin:0 0 12px;color:var(--text-secondary);font-size:13px;'>"
            f"Validare AI curentă: <b>{validated_count}</b> din "
            f"<b>{len(recommendations)}</b> candidați · sugestii executabile: "
            f"<b>{actionable_count}</b>. Restul verdicturilor sunt ascunse din "
            "lista de cumpărare."
            "</p>"
        )
        if not cards:
            cards.append(
                "<p style='color:var(--text-secondary);margin:0;'>"
                "Nu există momentan o sugestie executabilă. LQQ va reapărea "
                "automat aici la următoarea analiză disponibilă.</p>"
            )
        body = (
            notices_html + validation_html
            + "<div style='display:grid;gap:10px;'>" + ''.join(cards) + "</div>"
        )
    bvb_coverage_html = ''
    if bvb_universe_stats:
        bvb_coverage_html = (
            "<p style='margin:0 0 15px;color:var(--text-secondary);font-size:13px;'>"
            f"Univers BVB/AeRO descoperit: "
            f"<b>{int(bvb_universe_stats.get('discovered') or 0)}</b> simboluri · "
            f"analiză profundă disponibilă pentru "
            f"<b>{int(bvb_universe_stats.get('deep_scanned') or 0)}</b> · "
            f"lot rotativ/rulare: {int(bvb_universe_stats.get('batch_size') or 0)}."
            "</p>"
        )
    us_coverage_html = ''
    if us_universe_stats:
        us_coverage_html = (
            "<p style='margin:0 0 15px;color:var(--text-secondary);font-size:13px;'>"
            f"Univers SUA descoperit: <b>{int(us_universe_stats.get('discovered') or 0)}</b> "
            f"simboluri · analiză profundă disponibilă pentru "
            f"<b>{int(us_universe_stats.get('deep_scanned') or 0)}</b> · "
            f"lot rotativ/rulare: {int(us_universe_stats.get('batch_size') or 0)}."
            "</p>"
        )
    return (
        "<section style='margin:28px 0;background:var(--light-purple-bg);"
        "border:1px solid var(--border-light);border-radius:var(--radius-md);padding:22px;'>"
        "<h3 style='margin:0 0 8px;color:var(--primary-purple);'>"
        "Sugestii executabile de cumpărare — SUA, BVB și LQQ</h3>"
        "<p style='margin:0 0 15px;color:var(--text-secondary);'>"
        "Sunt afișate numai „Cumpărare acum” și „Ordin la trigger”. "
        "Primul permite evaluarea unei intrări la nivelul indicat; al doilea permite "
        "pregătirea unui ordin condiționat, fără cumpărare la piață înainte de trigger. "
        "LQQ rămâne vizibil permanent pentru monitorizare. Validarea AI ține cont "
        "de știri, piață și calendar. Nivelurile și bugetul sunt afișate în moneda "
        "ordinului: USD pentru SUA, RON pentru BVB și EUR pentru LQQ; verifică "
        "întotdeauna prețul și spreadul înaintea ordinului.</p>"
        + bvb_coverage_html + us_coverage_html + body
        + _render_buy_recommendation_history(recommendation_history, candidates)
        + "</section>"
    )


def generate_portfolio_ai_analysis(portfolio_df, orders_df=None, cached=None, cached_evidence=None,
                                   request_session=None, account_data=None, market_context=None,
                                   buy_candidates=None, etf_holdings=None,
                                   sector_rotation=None, us_market_regime=None):
    """Generează o analiză structurată și cache-uibilă, apoi returnează HTML sigur."""
    snapshot = build_portfolio_risk_snapshot(
        portfolio_df,
        orders_df,
        account_data=account_data,
        market_context=market_context,
        etf_holdings=etf_holdings,
        sector_rotation=sector_rotation,
        us_market_regime=us_market_regime,
    )
    snapshot['buy_candidates'] = list(buy_candidates or [])
    snapshot['buy_candidates'] = _size_buy_candidates(snapshot)
    evidence_cache = collect_portfolio_evidence(
        snapshot, cached=cached_evidence, request_session=request_session
    )
    evidence_by_symbol = {}
    for evidence in evidence_cache.get('items', []):
        evidence_by_symbol.setdefault(evidence['symbol'], []).append(evidence)
    for position in snapshot['positions']:
        position['evidence'] = evidence_by_symbol.get(position['symbol'], [])
    for candidate in snapshot['buy_candidates']:
        candidate['evidence'] = evidence_by_symbol.get(candidate['symbol'], [])
    try:
        events = get_economic_events(
            now=datetime.datetime.now(), request_session=request_session or requests
        )
        snapshot['economic_calendar'] = [
            {
                'name': event.get('name'),
                'country': event.get('country'),
                'datetime': event.get('datetime'),
                'importance': event.get('importance'),
                'status': event.get('status'),
                'category': event.get('category'),
                'actual': event.get('actual'),
                'forecast': event.get('forecast'),
                'previous': event.get('previous'),
                'expected_impact': _deterministic_event_analysis(event),
            }
            for event in events
            if _importance_rank(event) == 3
        ][:20]
    except (requests.RequestException, OSError, ValueError, TypeError, KeyError):
        snapshot['economic_calendar'] = []
    evidence_ids = {
        evidence['source_id'] for evidence in evidence_cache.get('items', [])
    }
    calendar_effects = _position_calendar_effects(snapshot)
    candidate_calendar_effects = _candidate_calendar_effects(snapshot)
    fingerprint = _portfolio_snapshot_fingerprint(snapshot)
    if (
        isinstance(cached, dict)
        and cached.get('version') == PORTFOLIO_AI_CACHE_VERSION
        and cached.get('fingerprint') == fingerprint
    ):
        try:
            result = _validate_portfolio_ai_result(
                cached.get('result', {}),
                {item['symbol'] for item in snapshot['positions']},
                evidence_ids,
                {item['symbol'] for item in snapshot['buy_candidates']},
                calendar_effects,
                candidate_calendar_effects,
                require_complete_candidates=True,
            )
            return (
                _render_portfolio_ai_html(snapshot, result, 'OpenAI · cache'),
                cached,
                evidence_cache,
                {'status': 'cache_valid', 'message': 'Analiză AI validă preluată din cache.'},
            )
        except (ValueError, TypeError):
            pass

    openai_key = os.environ.get('OPENAI_API_KEY', '')
    if not openai_key and os.path.exists('openai_key.txt'):
        try:
            with open('openai_key.txt', 'r') as handle:
                openai_key = handle.read().strip()
        except OSError:
            pass
    if not openai_key or not snapshot['positions']:
        reason = 'missing_key' if not openai_key else 'empty_portfolio'
        return (
            _render_portfolio_ai_html(snapshot),
            None,
            evidence_cache,
            {'status': reason, 'message': 'Cheia OpenAI sau pozițiile nu sunt disponibile.'},
        )

    request_payload = {
        'as_of': snapshot['as_of'],
        'objective': (
            'Recomandare practică pentru un portofoliu long de swing trading. Spune clar ce merită '
            'făcut acum și ce trebuie urmărit; nu promite randamente și nu inventa date.'
        ),
        'rules': [
            'Scrie rezumatul principal în limbaj simplu, maximum 4 propoziții; nu repeta soldurile, ponderile, stopurile și indicatorii care sunt deja afișați în detalii.',
            'Rezumatul principal trebuie să răspundă la: care este riscul cel mai important acum, ce acțiune generală este prudentă și ce ar schimba recomandarea.',
            'Folosește market_context pentru a explica separat dacă piața SUA și piața România/BVB ajută sau încurcă pozițiile aferente.',
            'TVBETETF este doar proxy pentru BET-TR; spune asta clar și nu îl prezenta drept indice oficial.',
            'Folosește tvbetetf_lookthrough pentru expunerea indirectă la fiecare emitent BVB și evaluează expunerea combinată directă plus cea prin ETF.',
            'Respectă maparea position.broker și position.market. Nu asocia JPM sau UPBD cu Tradeville și nu asocia TVBETETF.RO cu IBKR.',
            'Pentru fiecare poziție dă o singură acțiune clară și un singur lucru observabil de urmărit.',
            'Evită jargonul precum NAV, Cushion, ATR, R/R sau Excess Liquidity în rezumatul principal; aceste noțiuni pot apărea numai în detalii.',
            'Verifică existența și acoperirea cantitativă a ordinelor stop.',
            'Evaluează stopurile în contextul ATR/volatilității, trendului, targetului și riscului de gap.',
            'Pentru fiecare position_action folosește economic_calendar și piața poziției: SUA pentru acțiunile americane, România/BVB plus evenimente europene pentru acțiunile românești.',
            'Explică separat în calendar_effect dacă evenimentele apropiate susțin păstrarea stopului, cer prudență, justifică reducerea înaintea unui gap sau nu sunt disponibile.',
            'Nu lărgi stopul doar pentru că urmează un eveniment. Dacă riscul de gap este ridicat, preferă reducerea expunerii, protejarea profitului sau așteptarea confirmării.',
            'Nu considera automat stopul propus corect și nu recomanda mutarea stopului în jos pentru a evita o ieșire.',
            'Semnalează contradicțiile dintre HOLD/REDUCE/EXIT, trend, momentum și protecția activă.',
            'Evaluează concentrarea și raportul recompensă/risc numai când există date suficiente.',
            'Evaluează separat cash-ul, expunerea, Available Funds, Buying Power, Excess Liquidity, Cushion și marja fiecărui cont de broker.',
            'Pentru snapshotul manual Tradeville folosește numai câmpurile disponibile și menționează data lui; nu presupune marjă sau Buying Power dacă lipsesc.',
            'Nu dubla expunerea: reconciliază pozițiile cu brokerul lor înainte de a compara portofoliul cu NAV.',
            'Nu trata un sold într-o monedă ca fiind direct comparabil cu altă monedă și nu face conversii nesupuse.',
            'Dacă datele TWS sunt mai vechi de 24 de ore, menționează vechimea și nu formula o acțiune executabilă.',
            'Când privacy_mode=bands_only, folosește numai intervalele furnizate și nu estima soldurile exacte.',
            'Când privacy_mode=exact, folosește valorile TWS pentru a calcula și evalua cash/NAV, expunere/NAV, marjă/NAV și bufferul contului.',
            'Poți reproduce soldurile brute ale brokerilor când sunt relevante; păstrează obligatoriu moneda fiecărei valori.',
            'Nu afirma că NAV sau expunerea nu pot fi evaluate dacă privacy_mode=exact și valorile necesare există.',
            'Semnalează riscul de cash negativ, buffer redus, marjă ridicată sau putere de cumpărare insuficientă.',
            'Separă controlul de preț de invalidarea tezei și cere reevaluare la catalizatori.',
            'Folosește știrile și rapoartele numai când sunt relevante pentru risc sau teză.',
            'Acordă prioritate surselor oficiale; nu prezenta o știre de presă drept declarație a companiei.',
            'Citează exclusiv source_id existente în date și menționează conflictele dintre surse.',
            'Acțiunile trebuie formulate ca verificări: plasează/revizuiește/menține/strânge doar condiționat.',
            'Pentru buy_candidates verifică dacă știrile, piața și calendarul economic susțin intrarea acum; filtrele tehnice singure nu sunt suficiente.',
            'Pentru candidații BVB folosește tvbetetf_weight_pct, indirect_exposure_eur, direct_exposure_eur și overlap_risk. Preferă diversificarea și cere dovezi mai puternice înainte de a dubla componentele dominante ale TVBETETF.',
            'Pentru fiecare candidat BVB folosește bvb_market_segment, liquidity_status, median_turnover_20d_ron, active_days_20d, relative_volume_20d și liquidity_position_cap_eur. Nu transforma un vârf de volum dintr-o singură zi într-un semnal de lichiditate persistentă.',
            'Nu valida o intrare BVB când liquidity_status este insuficientă sau date insuficiente. Pentru AeRO presupune risc mai mare de spread și slippage, iar suma deterministă nu poate depăși liquidity_position_cap_eur.',
            'Pentru candidații SUA folosește us_sector_rotation și câmpurile sector_rotation_status, relative față de SPY și existing_sector_exposure_eur. Preferă liderii confirmați și cere dovezi mai puternice pentru sectoarele în deteriorare.',
            'Pentru candidații SUA folosește și us_market_regime: market_stage, economic_phase, cycle_fit și size_factor. Explică simplu dacă piața este în creștere, corecție, încetinire sau recesiune și nu contrazice dimensionarea deterministă.',
            'Nu concentra recomandările SUA: limita deterministă este maximum două idei pe sector, maximum o idee pe industrie cunoscută, maximum 10% din NAV IBKR pe sector și 5% pe industrie după includerea expunerii existente.',
            'Calendarul candidaților este validat determinist: evenimentele trecute nu pot fi descrise ca riscuri viitoare de publicare.',
            'Nu recomanda și nu inventa simboluri care nu există în buy_candidates.',
            'Pentru candidate_source=watchlist, strict_eligible arată dacă instrumentul a trecut BUY + Buy/Strong Buy + R:R minimum 3; dacă este false, verdictul trebuie să fie Așteaptă.',
            'Pentru candidate_source=external_research, nu aplica filtrul watchlistului și nu respinge simbolul doar fiindcă există deja în watchlist. Evaluează independent calitatea, catalizatorii, știrile, piața, calendarul, entry/stop/target și riscul.',
            'Pentru orice recomandare de cumpărare, folosește în text execution_currency și nivelurile entry_native, stop_native și target_native. Acțiunile SUA se discută în USD, cele BVB în RON, iar LQQ în EUR. Câmpurile *_eur sunt exclusiv pentru normalizarea internă a riscului și nu trebuie citate ca niveluri de ordin.',
            'Un candidat extern poate primi Candidat valid sau Pregătit la trigger numai dacă data_fresh=true, entry_eur, stop_eur și target_eur respectă stop < entry < target, iar rr_ratio este cel puțin external_min_rr (în prezent 1,8). Dacă datele sunt vechi sau nivelurile sunt incoerente, verdictul trebuie să fie Așteaptă și investiția acum zero.',
            'Pentru BVB, absența unui consens de analiști nu invalidează singură un candidat extern. Cere însă niveluri tehnice verificabile și lichiditate locală eligibilă; nu inventa un consens.',
            'Folosește level_source, trigger_basis și target_basis. Când target_basis spune că ținta este un plan tehnic de risc, prezint-o ca nivel de administrare a tranzacției, nu ca țintă de analist.',
            'Dacă prețul curent a depășit deja clar un trigger de breakout, nu recomanda urmărirea prețului. Cere o bază nouă ori un nou trigger, exceptând cazul în care nivelurile actualizate confirmă că intrarea nu este extinsă.',
            'Pentru cercetarea externă folosește trepte clare: Candidat valid numai pentru intrare imediată; Pregătit la trigger când există un prag apropiat; Foarte aproape când mai lipsește o confirmare; Urmărește pentru o idee utilă dar prematură; Evită când riscul domină.',
            'Pregătit la trigger înseamnă că se poate pregăti un ordin condiționat la entry_eur, nu că instrumentul trebuie cumpărat imediat la piață. Spune clar ce nivel trebuie atins înaintea execuției.',
            'Pentru verdicturile diferite de Candidat valid, investiția acum este zero. În why_now spune în limbaj simplu triggerul sau confirmarea necesară folosind exclusiv nivelurile primite.',
            'Păstrează acoperire echilibrată: dacă există candidați, include idei relevante atât pentru SUA, cât și pentru România/BVB; nu lăsa o singură piață să ocupe toate rezultatele.',
            'Include fiecare simbol din buy_candidates exact o dată în buy_recommendations; nu omite candidați și nu adăuga alții.',
            'Dacă strict_eligible=true și entry_eur este pozitiv, nu afirma că lipsesc semnalul BUY sau nivelul de intrare.',
            'Dimensionarea din buy_candidates este calculată determinist și separat pe broker în sizing_by_broker. Nu modifica și nu inventa sumele, unitățile sau cash-ul brokerilor.',
            'Un verdict Așteaptă înseamnă investiție acum zero; suma condițională poate fi folosită numai după dispariția riscului menționat și reconfirmarea semnalului.',
            'Nu promite îmbunătățirea randamentului lunar. Prioritizează limitarea pierderii, evitarea concentrării și păstrarea cash-ului pentru oportunități confirmate.',
            'Un eveniment macroeconomic general apropiat nu blochează automat toate cumpărările din piața respectivă. Pentru un setup solid folosește dimensionarea prudentă deja calculată sau Pregătit la trigger; folosește Așteaptă când riscul este specific emitentului (de exemplu rezultate) ori când combinația dintre calendar, piață și setup face probabil un gap greu de controlat.',
        ],
        'required_json': {
            'portfolio_overview': 'maximum 4 propoziții clare, fără repetarea detaliilor tehnice',
            'market_read': 'context separat și clar pentru SUA și România/BVB și efectul asupra pozițiilor',
            'position_actions': [{
                'symbol': 'un simbol existent',
                'broker': 'brokerul exact din poziție',
                'action': 'Menține|Protejează profitul|Redu|Ieși|Urmărește atent',
                'plain_reason': 'motiv practic, fără jargon',
                'calendar_effect': 'efectul evenimentelor economice apropiate asupra acțiunii și stopului',
                'next_check': 'un singur prag sau eveniment observabil',
            }],
            'buy_recommendations': [{
                'symbol': 'un simbol existent în buy_candidates',
                'market': 'SUA, România / BVB sau Europa / Nasdaq-100',
                'verdict': 'Candidat valid|Pregătit la trigger|Foarte aproape|Urmărește|Evită|Așteaptă',
                'why_now': 'de ce merită analizat acum',
                'market_effect': 'cum ajută sau încurcă piața relevantă',
                'news_effect': 'efectul știrilor/rapoartelor disponibile sau lipsa lor',
                'calendar_effect': 'riscul/opțiunea din calendarul economic',
                'main_risk': 'prima condiție care invalidează ideea',
                'source_ids': ['surse exacte din buy_candidates[].evidence'],
            }],
            'priorities': [{
                'symbol': 'un simbol existent',
                'severity': 'critic|ridicat|mediu|scăzut|informativ',
                'issue': 'problema',
                'evidence': 'valorile exacte disponibile sau date lipsă',
                'action': 'acțiune de verificat',
                'why': 'mecanismul riscului',
                'review_trigger': 'condiție observabilă de reevaluare',
                'confidence': 'ridicată|medie|scăzută și motiv',
                'source_ids': ['zero sau mai mulți identificatori exacți din data.positions[].evidence'],
            }],
        },
        'data': snapshot,
    }
    output_schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'portfolio_overview': {'type': 'string'},
            'market_read': {'type': 'string'},
            'position_actions': {
                'type': 'array',
                'minItems': 1,
                'maxItems': 12,
                'items': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'symbol': {'type': 'string'},
                        'broker': {'type': 'string'},
                        'action': {
                            'type': 'string',
                            'enum': [
                                'Menține', 'Protejează profitul', 'Redu', 'Ieși',
                                'Urmărește atent',
                            ],
                        },
                        'plain_reason': {'type': 'string'},
                        'calendar_effect': {'type': 'string'},
                        'next_check': {'type': 'string'},
                    },
                    'required': [
                        'symbol', 'broker', 'action', 'plain_reason',
                        'calendar_effect', 'next_check',
                    ],
                },
            },
            'buy_recommendations': {
                'type': 'array',
                'minItems': 0,
                'maxItems': 16,
                'items': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'symbol': {'type': 'string'},
                        'market': {'type': 'string'},
                        'verdict': {
                            'type': 'string',
                            'enum': [
                                'Candidat valid', 'Pregătit la trigger',
                                'Foarte aproape', 'Urmărește', 'Evită', 'Așteaptă',
                            ],
                        },
                        'why_now': {'type': 'string'},
                        'market_effect': {'type': 'string'},
                        'news_effect': {'type': 'string'},
                        'calendar_effect': {'type': 'string'},
                        'main_risk': {'type': 'string'},
                        'source_ids': {'type': 'array', 'items': {'type': 'string'}},
                    },
                    'required': [
                        'symbol', 'market', 'verdict', 'why_now', 'market_effect',
                        'news_effect', 'calendar_effect', 'main_risk', 'source_ids',
                    ],
                },
            },
            'priorities': {
                'type': 'array',
                'minItems': 1,
                'maxItems': 12,
                'items': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'symbol': {'type': 'string'},
                        'severity': {
                            'type': 'string',
                            'enum': ['critic', 'ridicat', 'mediu', 'scăzut', 'informativ'],
                        },
                        'issue': {'type': 'string'},
                        'evidence': {'type': 'string'},
                        'action': {'type': 'string'},
                        'why': {'type': 'string'},
                        'review_trigger': {'type': 'string'},
                        'confidence': {'type': 'string'},
                        'source_ids': {'type': 'array', 'items': {'type': 'string'}},
                    },
                    'required': [
                        'symbol', 'severity', 'issue', 'evidence', 'action', 'why',
                        'review_trigger', 'confidence', 'source_ids',
                    ],
                },
            },
        },
        'required': [
            'portfolio_overview', 'market_read', 'position_actions',
            'buy_recommendations', 'priorities',
        ],
    }
    attempts = [
        {
            'reasoning': OPENAI_PORTFOLIO_REASONING,
            'timeout': 180,
            'verbosity': 'low',
            'max_output_tokens': 16000,
        },
        {
            'reasoning': {'effort': 'medium'},
            'timeout': 120,
            'verbosity': 'low',
            'max_output_tokens': 12000,
        },
    ]
    diagnostics = []
    for attempt_number, attempt in enumerate(attempts, start=1):
        response_payload = {}
        try:
            response = requests.post(
                'https://api.openai.com/v1/responses',
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {openai_key}'},
                json={
                    'model': OPENAI_ANALYSIS_MODEL,
                    'reasoning': attempt['reasoning'],
                    'max_output_tokens': attempt['max_output_tokens'],
                    'text': {
                        'format': {
                            'type': 'json_schema',
                            'name': 'portfolio_risk_analysis',
                            'strict': True,
                            'schema': output_schema,
                        },
                        'verbosity': attempt['verbosity'],
                    },
                    'input': [
                        {'role': 'system', 'content': (
                            'Ești un consilier de risc pentru swing trading long. Răspunzi în română '
                            'clară, directă și ușor de înțeles. Pui concluzia înaintea detaliilor. '
                            'Folosești numai datele primite și explici explicit orice lipsă.'
                        )},
                        {'role': 'user', 'content': json.dumps(request_payload, ensure_ascii=False)},
                    ],
                },
                timeout=attempt['timeout'],
            )
            if response.status_code >= 400:
                diagnostics.append({
                    'attempt': attempt_number,
                    'type': 'http_error',
                    'http_status': response.status_code,
                })
                continue
            response_payload = response.json()
            result = _validate_portfolio_ai_result(
                json.loads(_extract_openai_response_text(response_payload)),
                {item['symbol'] for item in snapshot['positions']},
                evidence_ids,
                {item['symbol'] for item in snapshot['buy_candidates']},
                calendar_effects,
                candidate_calendar_effects,
                require_complete_candidates=True,
            )
            new_cache = {
                'version': PORTFOLIO_AI_CACHE_VERSION,
                'fingerprint': fingerprint,
                'generated_at': snapshot['as_of'],
                'result': result,
                'buy_candidates': snapshot['buy_candidates'],
            }
            diagnostic = {
                'status': 'success',
                'attempt': attempt_number,
                'model': OPENAI_ANALYSIS_MODEL,
                'reasoning': attempt['reasoning'],
            }
            return (
                _render_portfolio_ai_html(snapshot, result, f'OpenAI · {OPENAI_ANALYSIS_MODEL}'),
                new_cache,
                evidence_cache,
                diagnostic,
            )
        except requests.Timeout:
            diagnostics.append({'attempt': attempt_number, 'type': 'timeout'})
        except requests.RequestException as error:
            diagnostics.append({
                'attempt': attempt_number,
                'type': 'connection_error',
                'error_class': type(error).__name__,
            })
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            diagnostic_item = {
                'attempt': attempt_number,
                'type': 'invalid_response',
                'error_class': type(error).__name__,
                'detail': str(error)[:240],
            }
            if isinstance(response_payload, dict):
                if response_payload.get('status'):
                    diagnostic_item['response_status'] = response_payload['status']
                incomplete = response_payload.get('incomplete_details')
                if isinstance(incomplete, dict) and incomplete.get('reason'):
                    diagnostic_item['incomplete_reason'] = incomplete['reason']
            diagnostics.append(diagnostic_item)

    # Un răspuns unic poate deveni prea mare când sunt analizate simultan
    # pozițiile și până la 15 idei BUY. Recuperăm analiza în loturi mici,
    # păstrând aceeași schemă strictă și cerând fiecare simbol exact o dată.
    recovery_attempts = [
        {
            'reasoning': {'effort': 'medium'},
            'timeout': 120,
            'verbosity': 'low',
            'max_output_tokens': 8000,
        },
        {
            'reasoning': {'effort': 'low'},
            'timeout': 90,
            'verbosity': 'low',
            'max_output_tokens': 6000,
        },
    ]

    def recover_candidate_batch(batch, batch_label):
        batch_snapshot = dict(snapshot)
        batch_snapshot['buy_candidates'] = list(batch)
        batch_payload = dict(request_payload)
        batch_payload['data'] = batch_snapshot
        batch_payload['objective'] = (
            request_payload['objective']
            + ' Această cerere este un lot de recuperare: analizează fiecare '
              'candidat BUY primit exact o dată.'
        )
        batch_symbols = {
            item['symbol'] for item in batch if item.get('symbol')
        }
        for retry_number, retry in enumerate(recovery_attempts, start=1):
            response_payload = {}
            try:
                response = requests.post(
                    'https://api.openai.com/v1/responses',
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {openai_key}',
                    },
                    json={
                        'model': OPENAI_ANALYSIS_MODEL,
                        'reasoning': retry['reasoning'],
                        'max_output_tokens': retry['max_output_tokens'],
                        'text': {
                            'format': {
                                'type': 'json_schema',
                                'name': 'portfolio_risk_analysis_recovery',
                                'strict': True,
                                'schema': output_schema,
                            },
                            'verbosity': retry['verbosity'],
                        },
                        'input': [
                            {
                                'role': 'system',
                                'content': (
                                    'Ești un consilier de risc pentru swing trading long. '
                                    'Răspunzi în română clară și exclusiv în schema JSON cerută. '
                                    'Analizezi fiecare candidat primit exact o dată.'
                                ),
                            },
                            {
                                'role': 'user',
                                'content': json.dumps(
                                    batch_payload, ensure_ascii=False
                                ),
                            },
                        ],
                    },
                    timeout=retry['timeout'],
                )
                if response.status_code >= 400:
                    diagnostics.append({
                        'attempt': batch_label,
                        'retry': retry_number,
                        'type': 'http_error',
                        'http_status': response.status_code,
                    })
                    continue
                response_payload = response.json()
                return _validate_portfolio_ai_result(
                    json.loads(_extract_openai_response_text(response_payload)),
                    {item['symbol'] for item in snapshot['positions']},
                    evidence_ids,
                    batch_symbols,
                    calendar_effects,
                    {
                        symbol: candidate_calendar_effects.get(symbol, '')
                        for symbol in batch_symbols
                    },
                    require_complete_candidates=True,
                )
            except requests.Timeout:
                diagnostics.append({
                    'attempt': batch_label,
                    'retry': retry_number,
                    'type': 'timeout',
                })
            except requests.RequestException as error:
                diagnostics.append({
                    'attempt': batch_label,
                    'retry': retry_number,
                    'type': 'connection_error',
                    'error_class': type(error).__name__,
                })
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
                diagnostic_item = {
                    'attempt': batch_label,
                    'retry': retry_number,
                    'type': 'invalid_response',
                    'error_class': type(error).__name__,
                    'detail': str(error)[:240],
                }
                if isinstance(response_payload, dict):
                    if response_payload.get('status'):
                        diagnostic_item['response_status'] = response_payload['status']
                    incomplete = response_payload.get('incomplete_details')
                    if isinstance(incomplete, dict) and incomplete.get('reason'):
                        diagnostic_item['incomplete_reason'] = incomplete['reason']
                diagnostics.append(diagnostic_item)
        return None

    candidates = list(snapshot['buy_candidates'])
    recovery_batches = [
        candidates[index:index + 4]
        for index in range(0, len(candidates), 4)
    ] or [[]]
    recovered_core = None
    recovered_by_symbol = {}
    failed_batches = []
    for batch_index, batch in enumerate(recovery_batches, start=1):
        batch_result = recover_candidate_batch(
            batch, f'batch-{batch_index}'
        )
        if not batch_result:
            failed_batches.append(batch)
            continue
        if recovered_core is None:
            recovered_core = dict(batch_result)
            recovered_core['buy_recommendations'] = []
        for item in batch_result['buy_recommendations']:
            recovered_by_symbol[item['symbol']] = item

    # Dacă un lot nu a putut fi validat, îl spargem pe simboluri individuale.
    for failed_batch in failed_batches:
        for candidate in failed_batch:
            symbol = candidate.get('symbol')
            single_result = recover_candidate_batch(
                [candidate], f'symbol-{symbol}'
            )
            if not single_result:
                continue
            if recovered_core is None:
                recovered_core = dict(single_result)
                recovered_core['buy_recommendations'] = []
            for item in single_result['buy_recommendations']:
                recovered_by_symbol[item['symbol']] = item

    expected_candidate_symbols = [
        item['symbol'] for item in candidates if item.get('symbol')
    ]
    if (
        recovered_core is not None
        and set(recovered_by_symbol) == set(expected_candidate_symbols)
    ):
        recovered_core['buy_recommendations'] = [
            recovered_by_symbol[symbol]
            for symbol in expected_candidate_symbols
        ]
        new_cache = {
            'version': PORTFOLIO_AI_CACHE_VERSION,
            'fingerprint': fingerprint,
            'generated_at': snapshot['as_of'],
            'result': recovered_core,
            'buy_candidates': snapshot['buy_candidates'],
        }
        diagnostic = {
            'status': 'success_recovered',
            'model': OPENAI_ANALYSIS_MODEL,
            'mode': 'batched',
            'batch_count': len(recovery_batches),
            'attempts': diagnostics,
            'message': (
                'Răspunsul mare nu a fost valid; analiza a fost refăcută '
                'în loturi și acoperă toți candidații.'
            ),
        }
        return (
            _render_portfolio_ai_html(
                snapshot, recovered_core,
                f'OpenAI · {OPENAI_ANALYSIS_MODEL} · loturi validate',
            ),
            new_cache,
            evidence_cache,
            diagnostic,
        )

    diagnostic = {
        'status': 'failed',
        'model': OPENAI_ANALYSIS_MODEL,
        'attempts': diagnostics,
        'message': 'Apelurile OpenAI au eșuat; este afișat fallback-ul determinist.',
    }
    return _render_portfolio_ai_html(snapshot), None, evidence_cache, diagnostic


def _enrich_events_with_ai(events, indicators):
    """O singură cerere JSON pentru calendar; eșecul păstrează analiza deterministă."""
    analyses = {event['id']: _deterministic_event_analysis(event) for event in events}
    ai_cache = _load_ai_calendar_cache()
    pending = []
    for event in events:
        cached = ai_cache.get(_event_fingerprint(event))
        if isinstance(cached, dict) and cached.get('verdict') in {
            'Bullish probabil', 'Bearish probabil', 'Mixt', 'Neutru', 'Date insuficiente'
        }:
            analyses[event['id']].update(cached)
        else:
            pending.append(event)
    openai_key = os.environ.get('OPENAI_API_KEY', '')
    if not openai_key and os.path.exists('openai_key.txt'):
        try:
            with open('openai_key.txt', 'r') as handle:
                openai_key = handle.read().strip()
        except OSError:
            pass
    if not openai_key or not pending:
        return analyses
    compact_events = [{
        key: event.get(key) for key in
        ('id', 'name', 'country', 'category', 'datetime', 'status', 'actual', 'forecast', 'previous')
    } for event in pending[:24]]
    prompt = {
        'language': 'ro',
        'instruction': (
            'Analizează prudent evenimentele. Nu inventa date. Separă impactul probabil asupra '
            'SUA, Europei și BVB. Pentru evenimente viitoare explică scenariile peste/conform/sub consens. '
            'Pentru evenimente corporative BVB nu generaliza la întreaga piață.'
        ),
        'allowed_verdicts': ['Bullish probabil', 'Bearish probabil', 'Mixt', 'Neutru', 'Date insuficiente'],
        'required_fields': ['id', 'verdict', 'confidence', 'mechanism', 'us_impact', 'eu_impact',
                            'bvb_impact', 'sectors', 'horizon', 'reversal'],
        'context': {
            'VIX': indicators.get('VIX', {}).get('value'),
            'SPX': indicators.get('SPX', {}).get('value'),
            'NASDAQ': indicators.get('NASDAQ', {}).get('value'),
        },
        'events': compact_events,
    }
    try:
        response = requests.post(
            'https://api.openai.com/v1/responses',
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {openai_key}'},
            json={
                'model': OPENAI_ANALYSIS_MODEL,
                'reasoning': OPENAI_ANALYSIS_REASONING,
                'text': {'format': {'type': 'json_object'}, 'verbosity': 'medium'},
                'input': [
                    {'role': 'system', 'content': 'Ești un analist macro prudent. Răspunzi exclusiv JSON: {"events": [...]}.'},
                    {'role': 'user', 'content': json.dumps(prompt, ensure_ascii=False)}
                ],
            },
            timeout=180,
        )
        response.raise_for_status()
        parsed = json.loads(_extract_openai_response_text(response.json()))
        allowed = {'Bullish probabil', 'Bearish probabil', 'Mixt', 'Neutru', 'Date insuficiente'}
        for item in parsed.get('events', []):
            event_id = str(item.get('id', ''))
            if event_id not in analyses or item.get('verdict') not in allowed:
                continue
            clean = analyses[event_id].copy()
            for field in clean:
                value = item.get(field)
                if isinstance(value, str) and value.strip():
                    clean[field] = value.strip()[:1200]
            analyses[event_id] = clean
        for event in pending[:24]:
            ai_cache[_event_fingerprint(event)] = analyses[event['id']]
        _save_ai_calendar_cache(ai_cache)
    except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError):
        pass
    return analyses

def _render_event_value(label, value):
    shown = '—' if value is None or value == '' else html.escape(str(value))
    return f"<span style='margin-right:12px;'><b>{label}:</b> {shown}</span>"

def _render_calendar(events, indicators):
    if not events:
        return (
            "<div style='margin-top:32px;border-top:2px solid var(--border-light);padding-top:24px;'>"
            "<h4 style='color:var(--primary-purple);font-size:18px;font-weight:700;'>CALENDAR ECONOMIC — SUA, EUROPA ȘI BVB</h4>"
            "<div style='background:var(--light-purple-bg);padding:16px 20px;border-radius:var(--radius-sm);"
            "color:var(--text-secondary);'>Datele calendarului nu sunt disponibile momentan. Nu au fost generate evenimente fictive.</div></div>"
        )
    analyses = _enrich_events_with_ai(events, indicators)
    groups = [('past', 'Ultimele 7 zile'), ('upcoming', 'Următoarele 10 zile')]
    colors = {
        'Bullish probabil': '#2e7d32', 'Bearish probabil': '#c62828',
        'Mixt': '#ef6c00', 'Neutru': '#546e7a', 'Date insuficiente': '#757575'
    }
    output = (
        "<div style='margin-top:32px;border-top:2px solid var(--border-light);padding-top:24px;'>"
        "<h4 style='color:var(--primary-purple);font-size:18px;font-weight:700;margin-bottom:20px;"
        "text-transform:uppercase;letter-spacing:.5px;'>Calendar economic — SUA, Europa și BVB</h4>"
    )
    for status, title in groups:
        selected = [event for event in events if event.get('status') == status]
        output += f"<h5 style='font-size:16px;color:var(--text-primary);margin:18px 0 10px;'>{title}</h5>"
        if not selected:
            output += "<div style='color:var(--text-secondary);padding:10px 0;'>Niciun eveniment disponibil în interval.</div>"
            continue
        output += "<div style='display:grid;gap:12px;'>"
        for event in selected:
            analysis = analyses[event['id']]
            verdict = analysis['verdict']
            event_name = html.escape(event['name'])
            country = html.escape(event['country'])
            source_url = html.escape(event['source_url'], quote=True)
            source = html.escape(event['source'])
            values = (
                _render_event_value('Actual', event.get('actual')) +
                _render_event_value('Estimare', event.get('forecast')) +
                _render_event_value('Anterior', event.get('previous'))
            )
            details = ''.join(
                f"<p style='margin:7px 0;'><b>{label}:</b> {html.escape(str(analysis[field]))}</p>"
                for label, field in (
                    ('Mecanism', 'mechanism'), ('SUA — S&P 500 / Nasdaq', 'us_impact'),
                    ('Europa — STOXX 600 / DAX', 'eu_impact'), ('România — BET / BET-TR', 'bvb_impact'),
                    ('Sectoare', 'sectors'), ('Orizont', 'horizon'), ('Ce poate inversa verdictul', 'reversal')
                )
            )
            output += f"""
            <div style="background:var(--light-purple-bg);border-left:4px solid {colors[verdict]};padding:16px 20px;border-radius:var(--radius-sm);">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
                    <div><strong style="color:var(--text-primary);font-size:15px;">{event_name}</strong>
                    <div style="font-size:12px;color:var(--text-secondary);margin-top:4px;">{country} · {html.escape(event['week'])} {html.escape(event['time'])} {html.escape(event.get('timezone', 'UTC'))} · impact {html.escape(event['importance'])}</div></div>
                    <span style="color:white;background:{colors[verdict]};padding:4px 9px;border-radius:12px;font-size:12px;font-weight:700;">{verdict} · încredere {html.escape(analysis['confidence'])}</span>
                </div>
                <div style="font-size:13px;color:var(--text-secondary);margin-top:10px;">{values}</div>
                <details style="margin-top:10px;color:var(--text-secondary);font-size:13px;line-height:1.5;">
                    <summary style="cursor:pointer;color:var(--primary-purple);font-weight:700;">Explicație și scenarii</summary>
                    <div style="padding-top:8px;">{details}
                    <p style="margin:7px 0;"><b>Sursă:</b> <a href="{source_url}" target="_blank" rel="noopener noreferrer">{source}</a></p></div>
                </details>
            </div>"""
        output += "</div>"
    return output + (
        "<p style='font-size:11px;color:var(--text-secondary);margin-top:12px;'>"
        "Interpretări probabilistice, nu recomandări de tranzacționare.</p></div>"
    )

import os
import xml.etree.ElementTree as ET

def get_market_news():
    """Fetch Top Market News from Yahoo RSS and return detailed list."""
    try:
        url = "https://finance.yahoo.com/news/rssindex"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code != 200: return []
        
        root = ET.fromstring(resp.content)
        items = []
        count = 0
        for item in root.findall('./channel/item'):
            title = item.find('title').text
            link = item.find('link').text
            desc = item.find('description').text if item.find('description') is not None else ""
            items.append({'title': title, 'link': link, 'desc': desc})
            count += 1
            if count >= 6: break
        return items
    except Exception as e:
        print(f"News Error: {e}")
        return []


def _generate_news_and_ai_summary_html(news_items, indicators, cached_summary=None):
    """
    Generează secțiunea de știri și analiză AI.
    Returnează (full_html, ai_summary_text, sentiment_score)
    """
    try:
        # 1. Header
        news_html = "<div class='news-section' style='background: var(--bg-white); padding: 24px; border-radius: var(--radius-md); margin-top: 24px; border: 1px solid var(--border-light); box-shadow: var(--shadow-sm);'>"
        news_html += "<strong style='color: var(--primary-purple); font-size: 18px; font-weight: 700; display: block; margin-bottom: 16px;'>Market News Overview</strong>"
        
        ai_summary_html = ""
        ai_raw_text = ""
        ai_sentiment_score = 50 # Default Neutral
        openai_key = ""
        
        # Load Key
        if os.path.exists("openai_key.txt"):
            try:
                with open("openai_key.txt", "r") as f:
                    openai_key = f.read().strip()
            except: pass
            
        if not openai_key:
            openai_key = os.environ.get("OPENAI_API_KEY", "")
            
        if openai_key and news_items:
            try:
                print("Generare rezumat AI (OpenAI)...")
                # Construct Prompt
                news_text = "\n".join([f"- {item['title']}: {item['desc']}" for item in news_items[:10]])
                
                # Context din indicatori pentru AI
                vix_val = indicators.get('VIX', {}).get('value', 'N/A')
                spx_val = indicators.get('SPX', {}).get('value', 'N/A')
                
                prompt = (
                    f"Analizează următoarele știri financiare și indicatori de piață pentru a determina sentimentul general.\n"
                    f"Context Tehnic: VIX={vix_val}, SPX={spx_val}.\n\n"
                    f"Știri Recente:\n{news_text}\n\n"
                    f"Te rog să răspunzi EXACT în următorul format:\n"
                    f"SENTIMENT_SCORE: <un număr între 0 și 100, unde 0=Extreme Bearish, 50=Neutral, 100=Extreme Bullish>\n"
                    f"REZUMAT_HTML: <un rezumat succint (max 150 cuvinte) în format HTML (fără tag-uri <html> sau <body>, doar <p>, <b>, <ul> etc.), în limba ROMÂNĂ, analizând riscurile și oportunitățile.>\n"
                )
                
                # OpenAI Request logic
                url = "https://api.openai.com/v1/responses"
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {openai_key}"}
                payload = {
                    "model": OPENAI_ANALYSIS_MODEL,
                    "reasoning": OPENAI_ANALYSIS_REASONING,
                    "text": {"verbosity": "medium"},
                    "input": [{"role": "system", "content": "Ești un analist financiar expert. Răspunde strict în formatul cerut."}, {"role": "user", "content": prompt}]
                }
                
                resp = requests.post(url, headers=headers, json=payload, timeout=180)
                
                if resp.status_code == 200:
                    data = resp.json()
                    content = _extract_openai_response_text(data)
                    ai_raw_text = content
                    
                    # Parsing Response
                    score_line = [l for l in content.split('\n') if 'SENTIMENT_SCORE:' in l]
                    if score_line:
                        try:
                            score_str = score_line[0].split(':')[1].strip()
                            ai_sentiment_score = int(float(score_str))
                        except:
                            ai_sentiment_score = 50
                    
                    # Extract Summary HTML (everything after SENTIMENT_SCORE line)
                    summary_part = content
                    if 'REZUMAT_HTML:' in content:
                        summary_part = content.split('REZUMAT_HTML:')[1].strip()
                    elif 'SENTIMENT_SCORE:' in content:
                         parts = content.split('\n')
                         summary_part = "\n".join([p for p in parts if 'SENTIMENT_SCORE' not in p]).strip()

                    ai_summary_html = f"<div style='color: var(--text-primary); font-size: 15px; line-height: 1.6; background: var(--light-purple-bg); padding: 16px; border-radius: var(--radius-sm); margin-bottom: 16px; border-left: 3px solid var(--primary-purple);'><strong style='color: var(--primary-purple);'>Analiză OpenAI:</strong><br>{summary_part}</div>"
                elif resp.status_code == 429:
                    ai_summary_html = "<div style='color:orange'><strong>Eroare OpenAI (429):</strong> Rate Limit.</div>"
                else:
                    ai_summary_html = f"<div style='color:red'>Eroare OpenAI: {resp.status_code}</div>"
                    print(f"  OpenAI Error: {resp.status_code}")

            except Exception as e:
                print(f"  Eroare request OpenAI: {e}")
                ai_summary_html = f"<div style='color:red'>Eroare conexiune OpenAI: {str(e)[:50]}</div>"
        
        elif not openai_key:
             # Check for Cached Summary
             if cached_summary:
                  print("  -> Folosim rezumat AI din cache.")
                  # Try to extract previous score if saved in raw text, otherwise default
                  if 'SENTIMENT_SCORE:' in cached_summary:
                      try:
                          ai_sentiment_score = int(float(cached_summary.split('SENTIMENT_SCORE:')[1].split()[0]))
                      except: pass
                  
                  summary_display = cached_summary
                  if 'REZUMAT_HTML:' in cached_summary:
                       summary_display = cached_summary.split('REZUMAT_HTML:')[1].strip()

                  ai_summary_html = f"<div style='color: var(--text-primary); font-size: 15px; line-height: 1.6; background: var(--light-purple-bg); padding: 16px; border-radius: var(--radius-sm); margin-bottom: 16px; border-left: 3px solid var(--primary-purple);'><strong style='color: var(--primary-purple);'>Analiză OpenAI (Cached):</strong><br>{summary_display}</div>"
                  ai_raw_text = cached_summary
             else:
                  ai_summary_html = "<div style='color:orange'>Lipsă cheie OpenAI și lipsă cache.</div>"

        # ... Assemble HTML ...
        if ai_summary_html: news_html += ai_summary_html
        
        # Sources
        news_html += "<div style='font-size: 0.8rem; color: #888; margin-top: 10px;'>Surse: "
        for n in news_items[:3]:
             news_html += f"<a href='{n['link']}' target='_blank' style='color: #aaa; text-decoration: none; margin-right: 10px;'>{n['title'][:20]}...</a>"
        news_html += "</div>"
        news_html += "</div>" # Close news-section
        
        return news_html, ai_raw_text, ai_sentiment_score

    except Exception as e:
        print(f"Gen Market Analysis Error: {e}")
        return "<div>Error generating analysis</div>", "", 50

def generate_market_analysis(indicators, cached_ai_summary=None):
    """Generează o analiză de piață Hibridă (Algoritmică Multi-Factor + AI)."""
    try:
        # 1. Extragere Valori (Safe)
        def get_val(name):
            try: return float(indicators.get(name, {}).get('value', 0))
            except: return 0
            
        def get_spark(name):
            try: return indicators.get(name, {}).get('sparkline', [])
            except: return []

        vix = get_val('VIX')
        vix3m = get_val('VIX3M')
        skew = get_val('SKEW')
        move = get_val('MOVE')
        
        # 2. Market News & AI Sentiment
        news_items = get_market_news()
        news_html, ai_summary_raw, ai_score = _generate_news_and_ai_summary_html(news_items, indicators, cached_ai_summary)
        
        # 3. Calcul Scor Algoritmic (0-100, unde 100 = Bullish Perfect)
        # Factori Refined:
        # - VIX (Weight 15%): Panic check
        # - VIX Structure (Weight 10%): Contango check
        # - SKEW (Weight 5%): Tail Risk
        # - MOVE (Weight 5%): Bond Vol
        # - SPX Trend (Weight 30%): Price Action & Momentum (SMA20 + 5d Return)
        # - AI Sentiment (Weight 35%): Fundamental/News Context
        
        algo_score = 0
        total_weight = 0
        
        # --- VIX Score (Inverse) ---
        # 10-15: 100pts
        # 15-20: 75pts
        # 20-25: 50pts
        # 25-30: 25pts
        # >30: 0pts
        vix_s = 0
        if vix > 0:
            if vix < 15: vix_s = 100
            elif vix < 20: vix_s = 75
            elif vix < 25: vix_s = 50
            elif vix < 30: vix_s = 25
            else: vix_s = 0
            algo_score += vix_s * 0.15
            total_weight += 0.15
            
        # --- Term Structure (Contango vs Backwardation) ---
        # VIX3M / VIX > 1.1 -> Bullish (100)
        # 1.0 - 1.1 -> Neutral (50)
        # < 1.0 -> Bearish (0)
        if vix > 0 and vix3m > 0:
            ratio = vix3m / vix
            ts_s = 0
            if ratio > 1.1: ts_s = 100
            elif ratio > 1.0: ts_s = 50
            else: ts_s = 0
            algo_score += ts_s * 0.10
            total_weight += 0.10
            
        # --- SKEW ---
        # > 145 -> Bearish (Black Swan Risk) -> 20pts
        # 115-135 -> Normal Bullish -> 90pts
        if skew > 0:
            skew_s = 50
            if skew > 145: skew_s = 25
            elif skew > 135: skew_s = 50
            elif 115 <= skew <= 135: skew_s = 90
            else: skew_s = 80
            algo_score += skew_s * 0.05
            total_weight += 0.05
        
        # --- MOVE (Bond Vol) ---
        # < 100 -> Bullish (100)
        # 100-120 -> Neutral (50)
        # > 120 -> Bearish (0)
        if move > 0:
            move_s = 50
            if move < 100: move_s = 100
            elif move > 125: move_s = 0
            algo_score += move_s * 0.05
            total_weight += 0.05

        # --- Market Indices Trend (SPX + NASDAQ) ---
        # Calculate trend for both SPX and NASDAQ, then average
        indices_scores = []
        
        for index_name in ['SPX', 'NASDAQ']:
            index_points = get_spark(index_name)
            score_trend = 50  # Default neutral
            
            if index_points and len(index_points) >= 20:
                last = index_points[-1]
                # SMA 20 (Short Term)
                sma_20 = sum(index_points[-20:]) / 20
                # Momentum (5 days)
                idx_5d = -5 if len(index_points) >= 5 else 0
                mom_5d = (last / index_points[idx_5d]) - 1 if index_points[idx_5d] > 0 else 0
                 
                if last > sma_20:
                     if mom_5d > -0.01: score_trend = 100  # Uptrend solid
                     else: score_trend = 60  # Uptrend but recent pullback
                else:
                     # Sub SMA20
                     if mom_5d < -0.02: score_trend = 0  # Strong Downtrend
                     else: score_trend = 25  # Weak/Correction
                
                indices_scores.append(score_trend)
            elif index_points:
                # Fallback if less than 20 points
                indices_scores.append(50)
        
        # Average the scores from both indices
        if indices_scores:
            avg_index_score = sum(indices_scores) / len(indices_scores)
            algo_score += avg_index_score * 0.30
            total_weight += 0.30
            
        # --- AI Sentiment ---
        if ai_score >= 0: 
            algo_score += ai_score * 0.35
            total_weight += 0.35
            
        # Final Norm
        if total_weight > 0:
            final_score = algo_score / total_weight
        else:
            final_score = 50 # Fallback
            
        # Interpretare
        prob_up = int(final_score)
        prob_down = 100 - prob_up
        
        conclusion = "Neutral"
        color = "#e0e0e0"
        if final_score >= 65: 
            conclusion = "Bullish"
            color = "#4caf50"
        elif final_score <= 35: 
            conclusion = "Bearish"
            color = "#f44336"
            
        # Detalii Factori Text (Simplificat)
        # Eliminăm VIX și SKEW din afișare vizuală (sunt deja sus), păstrăm doar Term Structure și AI Sentiment cu explicații.
        factors_html = f"""
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-top: 15px;'>
            
            <div style='background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #444;'>
                <div style='font-size: 0.75rem; color: #aaa; margin-bottom: 2px;'>Analiză VIX Futures (Term Structure)</div>
                <div style='font-weight: bold; font-size: 1.1rem; color: {"#fc5c65" if (vix>0 and vix3m/vix<1) else "#26de81"}'>{(vix3m/vix if vix>0 else 0):.2f}</div>
                <div style='font-size: 0.65rem; color: #888; margin-top: 4px; line-height: 1.2;'>
                    Raport VIX Futures (3M) / VIX Spot.<br>
                    <span style='color: #26de81;'>> 1.1 (Contango)</span> = Normal/Bullish<br>
                    <span style='color: #fc5c65;'>< 1.0 (Backwardation)</span> = Panică/Bearish
                </div>
            </div>

            <div style='background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #444;'>
                <div style='font-size: 0.75rem; color: #aaa; margin-bottom: 2px;'>AI Market Sentiment</div>
                <div style='font-weight: bold; font-size: 1.1rem; color: {"#4caf50" if ai_score>60 else "#f44336" if ai_score<40 else "#fbbf24"}'>{ai_score}/100</div>
                <div style='font-size: 0.65rem; color: #888; margin-top: 4px; line-height: 1.2;'>
                    Analiză semantică știri.<br>
                    <span style='color: #4caf50;'>> 60</span> = Știri Pozitive<br>
                    <span style='color: #f44336;'>< 40</span> = Știri Negative
                </div>
            </div>
            
        </div>
        <div style='font-size: 0.7rem; color: #666; margin-top: 8px; text-align: center;'>
            *Scorul "Verdict Sistem" include și factori invizibili aici: VIX Level, MOVE Index (Bond Vol) și SKEW (Black Swan Risk), afișați în secțiunea "Indicatori".
        </div>
        """

        # 4. Calendar economic real: ultimele 7 zile + următoarele 10 zile.
        events_list = get_economic_events()
        events_html = _render_calendar(events_list, indicators)

        # Formatare HTML Final 
        html = f"""
        <div style="margin-top: 32px; background-color: var(--bg-white); border-radius: var(--radius-md); border: 1px solid var(--border-light); overflow: hidden; box-shadow: var(--shadow-sm); animation: fadeIn 0.8s ease-out 0.6s backwards;">
            <div style="background: linear-gradient(135deg, var(--primary-purple) 0%, var(--dark-purple) 100%); padding: 16px 20px; border-bottom: 1px solid var(--border-light); display: flex; align-items: center;">

                <h3 style="margin: 0; font-size: 20px; font-weight: 700; color: white;">Market Cortex - Multi-Factor Analysis</h3>
            </div>
            <div style="padding: 20px;">
                
                <!-- Probabilități Section -->
                <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 15px;">
                    <div style="flex: 1; min-width: 200px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px;">
                        <div style="font-size: 0.8rem; color: #888; margin-bottom: 5px;">Probabilitate Direcție (Agregată)</div>
                        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.85rem;">
                            <span style="color: #4caf50;">Bullish: <strong>{prob_up}%</strong></span>
                            <span style="color: #f44336;">Bearish: <strong>{prob_down}%</strong></span>
                        </div>
                        <div style="width: 100%; height: 6px; background: #555; margin-top: 5px; border-radius: 3px; overflow: hidden; display: flex;">
                            <div style="width: {prob_up}%; background: #4caf50; height: 100%;"></div>
                            <div style="width: {prob_down}%; background: #f44336; height: 100%;"></div>
                        </div>
                    </div>
                    
                    <div style="flex: 1; padding: 5px;">
                        <span style="font-weight: bold; color: #888; font-size: 0.9rem;">Verdict Sistem: </span>
                        <span style="font-size: 1.2rem; font-weight: bold; color: {color};">{conclusion}</span>
                        {factors_html}
                    </div>
                </div>

                {news_html}
                {events_html}
            </div>
        </div>
        """
        return html, ai_summary_raw, ai_score
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<div style='color: red;'>Eroare generare analiză: {e}</div>", "", 50


def check_market_structure_break(hist):
    """
    Checks for Market Structure Break (Rule #4).
    Logic: Lower High (PH2 < PH1) AND Break of Intervening Swing Low (SL).
    Returns: (is_active, debug_msg)
    """
    try:
        highs = hist['High'].values
        lows = hist['Low'].values
        dates = hist.index
        n = len(highs)
        
        pivots_high = [] # (index, price)
        # Scan last 120 days backwards
        scan_start = max(0, n - 120)
        window = 10
        
        # Naive pivot detection: Local Max in +/- window
        for i in range(scan_start, n - 1): # Exclude very last bar for pivot confirmation usually, but naive ok
            # Check left
            left_ok = True
            for k in range(1, window + 1):
                if i - k >= 0 and highs[i - k] > highs[i]:
                    left_ok = False
                    break
            if not left_ok: continue
            
            # Check right (limited by current data)
            right_ok = True
            for k in range(1, window + 1):
                if i + k < n and highs[i + k] > highs[i]:
                    right_ok = False
                    break
            
            if left_ok and right_ok:
                pivots_high.append((i, highs[i]))

        # We need at least 2 highs
        if len(pivots_high) < 2:
            return False, "Not enough pivots (Need 2+ PH)"

        ph2_idx, ph2_price = pivots_high[-1] # Most recent
        ph1_idx, ph1_price = pivots_high[-2] # Previous

        # 1. Check for Lower High
        if ph2_price < ph1_price:
            # 2. Find lowest Low between PH1 and PH2
            sl_price = 999999
            sl_idx = -1
            for k in range(ph1_idx, ph2_idx + 1):
                if lows[k] < sl_price:
                    sl_price = lows[k]
                    sl_idx = k
            
            # 3. Check if Current Price broke below SL
            current_price = hist['Close'].iloc[-1]
            
            # Debug info
            # debug_msg = f"LH ({ph2_price:.0f}<{ph1_price:.0f}) + SL Break ({current_price:.0f}<{sl_price:.0f})"
            
            if current_price < sl_price:
                 return True, f"MS Break: LH({ph2_price:.0f}<{ph1_price:.0f}) + SL Break(Now {current_price:.0f}<{sl_price:.0f})"
            else:
                 return False, f"No Break: LH({ph2_price:.0f}<{ph1_price:.0f}) but Holding SL({sl_price:.0f})"
        else:
            return False, f"Uptrend Structure: PH2({ph2_price:.0f}) > PH1({ph1_price:.0f})"

    except Exception as e:
        return False, f"Error Rule #4: {e}"

# --- SWING TRADING COMPONENT ---

TIDE_CACHE_FILE = "market_tide_cache.json"

def get_finviz_market_tide():
    """
    Scrapes Finviz Home Page for Market Tide data with caching:
    - Advancing vs Declining
    - New Highs vs New Lows
    - Above vs Below SMA50/SMA200
    
    Caches data when valid (non-zero Adv/Dec) and falls back to cache when market is closed.
    """
    url = "https://finviz.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://finviz.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    
    # Load cache
    cached_data = None
    cache_timestamp = None
    if os.path.exists(TIDE_CACHE_FILE):
        try:
            with open(TIDE_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                cached_data = cache.get('data')
                cache_timestamp = cache.get('timestamp')
        except:
            pass
    
    tide_data = {}
    
    try:
        # Increase timeout to 10s to avoid flakes
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code != 200:
            print(f"    ⚠️ Finviz Home Page Error: {r.status_code}")
            # Return cached data if available
            if cached_data:
                print(f"    → Using cached tide data from {cache_timestamp}")
                return cached_data
            return None
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Find all market stats blocks
        stats_divs = soup.find_all('div', class_='market-stats')
        
        for div in stats_divs:
            # Helper to extract value in parenthesis or plain number
            def extract_val(param_text):
                # Matches: "23.3% (68)" -> 68, "(3391) 61.2%" -> 3391
                match = re.search(r'\((\d+)\)', param_text)
                if match:
                    return int(match.group(1))
                return None
                
            labels_left = div.find('div', class_='market-stats_labels_left')
            labels_right = div.find('div', class_='market-stats_labels_right')
            
            if labels_left and labels_right:
                left_ps = labels_left.find_all('p')
                right_ps = labels_right.find_all('p')
                
                if len(left_ps) >= 2 and len(right_ps) >= 2:
                    label_l = left_ps[0].get_text(strip=True)
                    val_l_str = left_ps[1].get_text(strip=True)
                    val_l = extract_val(val_l_str)
                    
                    val_r_str = right_ps[1].get_text(strip=True)
                    val_r = extract_val(val_r_str)
                    
                    if val_l is not None and val_r is not None:
                        full_div_text = div.get_text()
                        if "Advancing" in label_l:
                            tide_data['Advancing'] = val_l
                            tide_data['Declining'] = val_r
                        elif "New High" in label_l:
                            tide_data['NewHighs'] = val_l
                            tide_data['NewLows'] = val_r
                        elif "SMA50" in full_div_text:
                            tide_data['SMA50_Above'] = val_l
                            tide_data['SMA50_Below'] = val_r
                        elif "SMA200" in full_div_text:
                            tide_data['SMA200_Above'] = val_l
                            tide_data['SMA200_Below'] = val_r
        
        # Check if we got valid Adv/Dec data (non-zero)
        adv = tide_data.get('Advancing', 0)
        dec = tide_data.get('Declining', 0)
        
        if adv > 0 or dec > 0:
            # Valid data, save to cache
            tide_data['_cached_at'] = datetime.datetime.now().isoformat()
            try:
                with open(TIDE_CACHE_FILE, 'w') as f:
                    json.dump({'data': tide_data, 'timestamp': tide_data['_cached_at']}, f)
                print(f"    ✅ Market Tide data cached (Adv: {adv}, Dec: {dec})")
            except Exception as e:
                print(f"    ⚠️ Failed to save tide cache: {e}")
            return tide_data
        else:
            # Market closed, use cache if available
            if cached_data:
                print(f"    → Market closed, using cached tide data from {cache_timestamp}")
                return cached_data
            else:
                print(f"    ⚠️ Market closed and no cache available")
                return tide_data
                            
    except Exception as e:
        print(f"    ⚠️ Error scraping Finviz Home: {e}")
        # Return cached data if available
        if cached_data:
            print(f"    → Using cached tide data due to error")
            return cached_data
        return None

finviz_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_finviz_count(filter_type):
    """Get count of S&P 500 stocks above a moving average from Finviz"""
    url = f'https://finviz.com/screener.ashx?v=111&f=idx_sp500,ta_{filter_type}_pa'
    try:
        r = requests.get(url, headers=finviz_headers, timeout=5) # Short timeout
        match = re.search(r'(\d+)\s*Total', r.text)
        if match:
            return int(match.group(1)), 505
    except:
        pass
    return None, 505

def get_fallback_breadth():
    """Fallback: Calculate breadth using Top ~400 US Stocks + Sector ETFs via Yahoo Finance"""
    
    # Try to load expanded list from JSON
    full_list = []
    json_file = "sp500_tickers.json"
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                full_list = json.load(f)
            print(f"    -> Loaded {len(full_list)} tickers from {json_file}")
        except Exception as e:
            print(f"    ⚠️ Error loading {json_file}: {e}")
    
    # Fallback to hardcoded list if JSON missing/empty
    if not full_list:
            # 1. Sector ETFs (Base)
        etfs = ['XLK', 'XLF', 'XLV', 'XLY', 'XLP', 'XLE', 'XLI', 'XLB', 'XLU', 'XLC', 'XLRE']
        # 2. Magnificent 7 + Big Tech
        tech = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'AVGO', 'AMD', 'CRM', 'ADBE', 'NFLX', 'INTC', 'QCOM', 'TXN', 'ORCL', 'CSCO']
        # 3. Financials
        fin = ['JPM', 'BAC', 'WFC', 'V', 'MA', 'GS', 'MS', 'BLK', 'AXP', 'C']
        # 4. Healthcare
        health = ['LLY', 'UNH', 'JNJ', 'MRK', 'ABBV', 'PFE', 'TMO', 'ABT', 'BMY', 'CVS']
        # 5. Consumer
        cons = ['WMT', 'PG', 'COST', 'KO', 'PEP', 'HD', 'MCD', 'NKE', 'SBUX', 'DIS', 'PM', 'MO']
        # 6. Industrial / Energy / Others
        ind = ['CAT', 'DE', 'XOM', 'CVX', 'GE', 'UPS', 'BA', 'LMT', 'HON', 'UNP', 'RTX', 'MMM']
        
        full_list = list(set(etfs + tech + fin + health + cons + ind))
        print(f"    -> Using hardcoded fallback ({len(full_list)} tickers)")

    try:
        # Batch download for speed
        # period='6mo' is enough for SMA50. For SMA200 we need ~1y (252 trading days)
        # Split huge list into chunks of 100 to avoid URL length issues or timeouts
        chunk_size = 100
        all_tickers = list(set(full_list))
        total_tickers = len(all_tickers)
        
        # Setup master dataframe
        frames = []
        
        # Single massive download is usually fine for <500 tickers in yfinance
        df = yf.download(all_tickers, period="1y", progress=False, auto_adjust=True)['Close']
        
        if df.empty: return None
        
        # Get latest prices
        current_prices = df.iloc[-1]
        
        # Calculate SMAs
        sma50 = df.rolling(window=50).mean().iloc[-1]
        sma200 = df.rolling(window=200).mean().iloc[-1]
        
        count_50 = 0
        count_200 = 0
        valid_count = 0
        
        for ticker in all_tickers:
            if ticker in current_prices and not pd.isna(current_prices[ticker]):
                price = current_prices[ticker]
                mav50 = sma50.get(ticker, 0)
                mav200 = sma200.get(ticker, 0)
                
                # Only count if we have valid SMA data (not NaN)
                if pd.notna(mav50) and pd.notna(mav200) and mav50 > 0:
                    valid_count += 1
                    if price > mav50: count_50 += 1
                    if price > mav200: count_200 += 1
        
        return {
            'above_50': count_50,
            'above_200': count_200,
            'total': valid_count,
            'source': f'Top {valid_count} US Stocks'
        }
    except Exception as e:
        print(f"Error fetching Fallback Breadth: {e}")
        return None


def get_swing_trading_data(data=None):
    """ Fetches data for Swing Trading Analysis including historical context. """
    if data is None: data = {}
    
    # 1. SPX Data
    try:
        spx = yf.Ticker("^GSPC")
        hist = spx.history(period="2y") 
        if not hist.empty:
            hist = hist.dropna(subset=['Close'])
            current_price = hist['Close'].iloc[-1]
            hist['SMA10'] = hist['Close'].rolling(window=10).mean()
            hist['SMA50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA200'] = hist['Close'].rolling(window=200).mean()
            
            data['SPX_Price'] = current_price
            data['SPX_SMA10'] = hist['SMA10'].iloc[-1]
            data['SPX_SMA50'] = hist['SMA50'].iloc[-1]
            data['SPX_SMA200'] = hist['SMA200'].iloc[-1]
            
            # RSI(14) calculation
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            hist['RSI'] = 100 - (100 / (1 + rs))
            data['SPX_RSI'] = hist['RSI'].iloc[-1]

            # Weekly RSI (SPX)
            try:
                weekly_spx = hist['Close'].resample('W').last()
                delta_w = weekly_spx.diff()
                gain_w = (delta_w.where(delta_w > 0, 0)).rolling(window=14).mean()
                loss_w = (-delta_w.where(delta_w < 0, 0)).rolling(window=14).mean()
                rs_w = gain_w / loss_w
                rsi_w = 100 - (100 / (1 + rs_w))
                data['SPX_RSI_Weekly'] = rsi_w.iloc[-1]
            except Exception as e:
                print(f"    ⚠️ Error calc Weekly RSI (SPX): {e}")
                data['SPX_RSI_Weekly'] = data['SPX_RSI'] # Fallback
            
            lookback = 60
            subset = hist.iloc[-lookback:]
            
            data['Chart_SPX'] = {
                'labels': [d.strftime('%m-%d') for d in subset.index],
                'price': subset['Close'].fillna(0).tolist(),
                'sma10': subset['SMA10'].fillna(0).tolist(),
                'sma50': subset['SMA50'].fillna(0).tolist(),
                'sma200': subset['SMA200'].fillna(0).tolist(),
                'rsi': subset['RSI'].fillna(50).tolist()
            }
            
            # --- RULE #4: MARKET STRUCTURE BREAK ANALYSIS ---
            active, debug = check_market_structure_break(hist)
            data['Rule4_Active'] = active
            data['Rule4_Debug'] = debug
            print(f"    -> Rule #4 Analysis: {debug} -> Active: {active}")

    except Exception as e:
        print(f"Error Swing Data (SPX): {e}")

    # 1b. Nasdaq (NDX) Data - "Motorul" pieței tech
    try:
        ndx = yf.Ticker("^NDX")
        hist_ndx = ndx.history(period="2y")
        if not hist_ndx.empty:
            hist_ndx = hist_ndx.dropna(subset=['Close'])
            ndx_price = hist_ndx['Close'].iloc[-1]
            hist_ndx['SMA10'] = hist_ndx['Close'].rolling(window=10).mean()
            hist_ndx['SMA50'] = hist_ndx['Close'].rolling(window=50).mean()
            hist_ndx['SMA200'] = hist_ndx['Close'].rolling(window=200).mean()
            
            data['NDX_Price'] = ndx_price
            data['NDX_SMA10'] = hist_ndx['SMA10'].iloc[-1]
            data['NDX_SMA50'] = hist_ndx['SMA50'].iloc[-1]
            data['NDX_SMA200'] = hist_ndx['SMA200'].iloc[-1]
            
            # RSI(14) calculation for NDX
            delta_ndx = hist_ndx['Close'].diff()
            gain_ndx = (delta_ndx.where(delta_ndx > 0, 0)).rolling(window=14).mean()
            loss_ndx = (-delta_ndx.where(delta_ndx < 0, 0)).rolling(window=14).mean()
            rs_ndx = gain_ndx / loss_ndx
            hist_ndx['RSI'] = 100 - (100 / (1 + rs_ndx))
            data['NDX_RSI'] = hist_ndx['RSI'].iloc[-1]

            # Weekly RSI (NDX)
            try:
                weekly_ndx = hist_ndx['Close'].resample('W').last()
                delta_w_ndx = weekly_ndx.diff()
                gain_w_ndx = (delta_w_ndx.where(delta_w_ndx > 0, 0)).rolling(window=14).mean()
                loss_w_ndx = (-delta_w_ndx.where(delta_w_ndx < 0, 0)).rolling(window=14).mean()
                rs_w_ndx = gain_w_ndx / loss_w_ndx
                rsi_w_ndx = 100 - (100 / (1 + rs_w_ndx))
                data['NDX_RSI_Weekly'] = rsi_w_ndx.iloc[-1]
            except Exception as e:
                print(f"    ⚠️ Error calc Weekly RSI (NDX): {e}")
                data['NDX_RSI_Weekly'] = data['NDX_RSI'] # Fallback
            
            lookback = 60
            subset_ndx = hist_ndx.iloc[-lookback:]
            
            data['Chart_NDX'] = {
                'labels': [d.strftime('%m-%d') for d in subset_ndx.index],
                'price': subset_ndx['Close'].fillna(0).tolist(),
                'sma10': subset_ndx['SMA10'].fillna(0).tolist(),
                'sma50': subset_ndx['SMA50'].fillna(0).tolist(),
                'sma200': subset_ndx['SMA200'].fillna(0).tolist(),
                'rsi': subset_ndx['RSI'].fillna(50).tolist()
            }
            print(f"    -> NDX fetched (Price: {ndx_price:.0f}, SMA200: {data['NDX_SMA200']:.0f}, RSI: {data['NDX_RSI']:.1f})")
    except Exception as e:
        print(f"Error Swing Data (NDX): {e}")

    # 1c. VIX Volatility Data
    try:
        vix = yf.Ticker("^VIX")
        hist_vix = vix.history(period="6mo")
        if not hist_vix.empty:
            hist_vix = hist_vix.dropna(subset=['Close'])
            vix_current = hist_vix['Close'].iloc[-1]
            data['VIX_Current'] = vix_current
            data['VIX_SMA20'] = hist_vix['Close'].rolling(window=20).mean().iloc[-1]
            
            # Calculate percentile (how current VIX compares to last 6 months)
            vix_percentile = (hist_vix['Close'] < vix_current).sum() / len(hist_vix) * 100
            data['VIX_Percentile'] = vix_percentile
            
            lookback = 60
            subset_vix = hist_vix.iloc[-lookback:]
            
            data['Chart_VIX'] = {
                'labels': [d.strftime('%m-%d') for d in subset_vix.index],
                'values': subset_vix['Close'].fillna(20).tolist()
            }
            print(f"    -> VIX fetched (Current: {vix_current:.1f}, Percentile: {vix_percentile:.0f}%)")
    except Exception as e:
        print(f"Error Swing Data (VIX): {e}")

    # 1d. SKEW (Tail Risk / Black Swan Index)
    try:
        skew_ticker = yf.Ticker("^SKEW")
        hist_skew = skew_ticker.history(period="3mo")
        if not hist_skew.empty:
            hist_skew = hist_skew.dropna(subset=['Close'])
            skew_current = hist_skew['Close'].iloc[-1]
            data['SKEW_Current'] = skew_current
            data['SKEW_SMA20'] = hist_skew['Close'].rolling(window=20).mean().iloc[-1]
            print(f"    -> SKEW fetched (Current: {skew_current:.1f})")
    except Exception as e:
        print(f"Error Swing Data (SKEW): {e}")




    # 1e. Market Breadth Analysis
    try:
        sp500_total = 505  # Approximate S&P 500 count
        
        # 1e. Market Breadth Full Tide (from Finviz Home)
        try:
            tide = get_finviz_market_tide()
            if tide:
                data['Market_Tide'] = tide
                print(f"    -> Market Tide: Adv {tide.get('Advancing', '?')}/{tide.get('Declining', '?')}, Highs {tide.get('NewHighs', '?')}/{tide.get('NewLows', '?')}")
        except Exception as e:
            print(f"    ⚠️ Error fetching Market Tide: {e}")

        # Try Finviz First
        res_200 = get_finviz_count('sma200')
        res_50 = get_finviz_count('sma50')
        
        above_200 = res_200[0] if res_200 else None
        above_50 = res_50[0] if res_50 else None
        
        breadth_source = "Finviz"
        
        # Fallback if Finviz fails
        if above_50 is None:
            print("    ⚠️ Finviz blocked/failed. Using Fallback list...")
            fallback_data = get_fallback_breadth()
            if fallback_data and fallback_data['total'] > 0:
                above_50 = fallback_data['above_50']
                above_200 = fallback_data['above_200']
                sp500_total = fallback_data['total']
                breadth_source = fallback_data['source']
        
        if above_200 is not None:
            breadth_pct_200 = (above_200 / sp500_total) * 100
            data['Breadth_200_Pct'] = breadth_pct_200
            data['Breadth_200_Above'] = above_200
        
        if above_50 is not None:
            breadth_pct_50 = (above_50 / sp500_total) * 100
            data['Breadth_Pct'] = breadth_pct_50
            data['Breadth_Above'] = above_50
            data['Breadth_Total'] = sp500_total
            data['Breadth_Source'] = breadth_source
            
            # --- BREADTH DIVERGENCE ANALYSIS ---
            # Classify rally quality based on SMA50 vs SMA200 participation gap
            if above_200 is not None and 'Breadth_200_Pct' in data: # Check if breadth_pct_200 was calculated
                divergence = breadth_pct_50 - data['Breadth_200_Pct']
                
                if abs(divergence) <= 5:
                    quality = "Rally Solid (Aligned)"
                    quality_color = "#4caf50"  # Green
                elif divergence > 15:
                    quality = "Rally Fresh (Climbing fast, watch exhaustion)"
                    quality_color = "#ff9800"  # Orange
                elif divergence < -15:
                    quality = "Correction in Bull Market (dip opportunity)"
                    quality_color = "#f44336"  # Red
                else:
                    quality = "Rally Mixed"
                    quality_color = "#2196f3"  # Blue
                
                data['Breadth_Quality'] = quality
                data['Breadth_Quality_Color'] = quality_color
                data['Breadth_Divergence'] = divergence
                print(f"    -> Breadth Quality: {quality} (Divergence: {divergence:+.1f}%)")
            
            print(f"    -> Breadth ({breadth_source}) fetched: {above_50}/{sp500_total} above SMA50 ({breadth_pct_50:.0f}%)")
    except Exception as e:
        print(f"Error Swing Data (Breadth): {e}")

    # 2. Fear & Greed AND PCR from CNN
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://edition.cnn.com',
            'Origin': 'https://edition.cnn.com'
        }
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", headers=headers, timeout=10)
        pcr_fetched_from_cnn = False
        
        if r.status_code == 200:
            j = r.json()
            
            # F&G Logic
            data['FG_Score'] = j.get('fear_and_greed', {}).get('score', 50)
            data['FG_Rating'] = j.get('fear_and_greed', {}).get('rating', 'neutral')
            hist = j.get('fear_and_greed_historical', {}).get('data', [])
            if hist:
                sorted_hist = sorted(hist, key=lambda x: x['x'])
                data['Chart_FG'] = [item['y'] for item in sorted_hist[-60:]]
                
                # F&G SMA5 Logic (Trend Detection)
                # Calculate SMA5 on full history
                fg_series = pd.Series([item['y'] for item in sorted_hist])
                if len(fg_series) >= 5:
                    fg_sma5 = fg_series.rolling(window=5).mean().iloc[-1]
                    data['FG_SMA5'] = float(fg_sma5)
                    print(f"    -> Trend F&G: Score {data['FG_Score']:.0f} vs SMA5 {fg_sma5:.1f}")
            else:
                data['Chart_FG'] = [data['FG_Score']] * 60
                
            # PCR Logic from CNN (Priority)
            if 'put_call_options' in j:
                 try:
                     pcr_list = j['put_call_options'].get('data', [])
                     if pcr_list:
                         sorted_pcr = sorted(pcr_list, key=lambda x: x['x'])
                         last_item = sorted_pcr[-1]
                         data['PCR_Value'] = last_item['y']
                         data['Chart_PCR'] = [item['y'] for item in sorted_pcr[-60:]]
                         
                         # Calculate MA10
                         pcr_vals = [item['y'] for item in sorted_pcr[-70:]] # Get a bit more for rolling window
                         if len(pcr_vals) >= 10:
                             ma_series = pd.Series(pcr_vals).rolling(window=10).mean().iloc[-1]
                             data['PCR_MA10'] = float(ma_series)
                             
                             # Generate MA10 Series for Chart
                             # Need to align with Chart_PCR (last 60)
                             # So we compute rolling on full history then slice last 60
                             full_series = pd.Series([item['y'] for item in sorted_pcr])
                             ma_full = full_series.rolling(window=10).mean()
                             data['Chart_PCR_MA10'] = ma_full.iloc[-60:].fillna(0).tolist()
                             
                         pcr_fetched_from_cnn = True
                         print(f"    -> PCR fetched from CNN (Value: {data['PCR_Value']:.2f}, MA10: {data.get('PCR_MA10', 'N/A')})")
                 except Exception as e:
                     print(f"Error parsing CNN PCR: {e}")

    except Exception as e:
        print(f"Error Swing Data (CNN): {e}")
        if 'FG_Score' not in data:
            data['FG_Score'] = 50; data['FG_Rating'] = 'neutral'; data['Chart_FG'] = []

    # 3. PCR Fallback (Only if CNN failed)
    if not data.get('PCR_Value'):
        try:
            # Try Yahoo Tickers
            tickers = ['^CPC', '^PCR', '^PCX']
            pcr_found = False
            for t in tickers:
                try:
                    temp = yf.Ticker(t).history(period="3mo")
                    if not temp.empty:
                        temp = temp.dropna(subset=['Close'])
                        data['PCR_Value'] = temp['Close'].iloc[-1]
                        data['Chart_PCR'] = temp['Close'].iloc[-60:].tolist()
                        pcr_found = True
                        break
                except: continue
                
            if not pcr_found: # Fallback SPY Options
                try:
                    spy = yf.Ticker("SPY")
                    exps = spy.options
                    if exps:
                        total_c = 0; total_p = 0
                        for date in exps[:2]:
                            opt = spy.option_chain(date)
                            total_c += opt.calls['volume'].fillna(0).sum()
                            total_p += opt.puts['volume'].fillna(0).sum()
                        if total_c > 0:
                            data['PCR_Value'] = total_p / total_c
                            print(f"    -> Calculated SPY Option PCR: {data['PCR_Value']:.2f}")
                except Exception as opt_e:
                    print(f"    PCR Fallback failed: {opt_e}")
                    data['PCR_Value'] = 0.8
                    data['Chart_PCR'] = []
        except Exception:
            pass

    return data

def calculate_market_bias(data):
    """
    Calculates a Market Bias Score (0-100) based on Trend, Volatility, Sentiment, and Breadth.
    Returns: dict with score, verdict, label_color, breakdwon
    """
    score = 0
    max_score = 0
    breakdown = []

    # 1. Trend (40%) - SPX Price vs SMA200/SMA50
    spx_price = data.get('SPX_Price', 0)
    sma200 = data.get('SPX_SMA200', 0)
    sma50 = data.get('SPX_SMA50', 0)
    
    trend_score = 0
    if spx_price > sma200: trend_score += 50
    if spx_price > sma50: trend_score += 50
    
    score += trend_score * 0.4
    breakdown.append(f"Trend: {trend_score}% (Weight 40%)")

    # 2. Volatility (20%) - VIX Level
    vix = data.get('VIX_Current', 20)
    vol_score = 0
    if vix < 20: vol_score = 100
    elif vix < 25: vol_score = 50
    else: vol_score = 0 # Panic
    
    score += vol_score * 0.2
    breakdown.append(f"Volatility: {vol_score}% (Weight 20%)")

    # 3. Sentiment (20%) - F&G
    fg = data.get('FG_Score', 50)
    sent_score = 0
    if fg > 75: sent_score = 50 # Extreme Greed (Risk)
    elif fg > 55: sent_score = 100 # Greed (Good Trend)
    elif fg > 40: sent_score = 50 # Neutral
    else: sent_score = 0 # Fear
    
    score += sent_score * 0.2
    breakdown.append(f"Sentiment: {sent_score}% (Weight 20%)")

    # 4. Breadth (20%) - % > SMA50
    breadth = data.get('Breadth_Pct', 50)
    breadth_score = 0
    if breadth > 50: breadth_score = 100
    else: breadth_score = 0
    
    score += breadth_score * 0.2
    breakdown.append(f"Breadth: {breadth_score}% (Weight 20%)")

    # Final Verdict
    final_score = int(score)
    
    if final_score >= 60:
        verdict = "BULLISH"
        color = "#4caf50"
    elif final_score <= 40:
        verdict = "BEARISH"
        color = "#f44336"
    else:
        verdict = "NEUTRAL"
        color = "#ff9800"
        
    return {
        'score': final_score,
        'verdict': verdict,
        'color': color,
        'details': breakdown
    }

def generate_swing_trading_html(data=None):
    """ Generates HTML Card for Swing Trading with Explicit Numerical Values. """
    if data is None:
        data = get_swing_trading_data()
    
    # Extract SPX Data
    spx_price = data.get('SPX_Price', 0)
    sma_200 = data.get('SPX_SMA200', 0)
    sma_50 = data.get('SPX_SMA50', 0)
    sma_10 = data.get('SPX_SMA10', 0)
    
    # Extract NDX Data
    ndx_price = data.get('NDX_Price', 0)
    ndx_sma_200 = data.get('NDX_SMA200', 0)
    ndx_sma_50 = data.get('NDX_SMA50', 0)
    ndx_sma_10 = data.get('NDX_SMA10', 0)
    
    # Extract RSI Data
    spx_rsi = data.get('SPX_RSI', 50)
    ndx_rsi = data.get('NDX_RSI', 50)
    
    fg_score = data.get('FG_Score', 50)
    fg_sma5 = data.get('FG_SMA5', fg_score) # Default to score if no history
    fg_rating = str(data.get('FG_Rating', 'neutral')).capitalize()
    pcr_val = data.get('PCR_Value', 0.8) if data.get('PCR_Value') else 0.8
    pcr_ma10 = data.get('PCR_MA10', pcr_val) if data.get('PCR_MA10') else pcr_val
    
    # Chart Data JSON
    default_spx = {'labels': [], 'price': [], 'sma10': [], 'sma50': [], 'sma200': [], 'rsi': []}
    chart_spx_json = json.dumps(data.get('Chart_SPX', default_spx))
    chart_ndx_json = json.dumps(data.get('Chart_NDX', default_spx))
    chart_fg_json = json.dumps(data.get('Chart_FG', []))
    chart_pcr_json = json.dumps(data.get('Chart_PCR', []))
    chart_pcr_ma_json = json.dumps(data.get('Chart_PCR_MA10', []))
    
    # VIX Data
    vix_current = data.get('VIX_Current', 20)
    vix_sma20 = data.get('VIX_SMA20', 20)
    vix_percentile = data.get('VIX_Percentile', 50)
    default_vix = {'labels': [], 'values': []}
    chart_vix_json = json.dumps(data.get('Chart_VIX', default_vix))
    
    # VIX Interpretation (Volatility zones)
    if vix_current < 15:
        vix_zone = "COMPLAZENȚĂ"
        vix_color = "#ff9800"  # Orange - warning (too calm)
        vix_hint = "⚠️ Piață prea calmă - potențial de corecție"
    elif vix_current < 20:
        vix_zone = "NORMAL"
        vix_color = "#4caf50"  # Green
        vix_hint = "✅ Volatilitate normală"
    elif vix_current < 30:
        vix_zone = "FRICĂ"
        vix_color = "#2196f3"  # Blue - opportunity in bull
        vix_hint = "🎯 Frică = oportunitate (dacă trend bullish)"
    else:
        vix_zone = "PANICĂ"
        vix_color = "#f44336"  # Red
        vix_hint = "⛔ Volatilitate extremă - prudență maximă"
    
    # SKEW Interpretation (Tail Risk / Black Swan)
    skew_current = data.get('SKEW_Current', 120)
    if skew_current > 145:
        skew_zone = "EXTREM"
        skew_color = "#f44336"
        skew_hint = "🚨 Tail risk foarte ridicat!"
    elif skew_current > 130:
        skew_zone = "RIDICAT"
        skew_color = "#ff9800"
        skew_hint = "⚠️ Smart money cumpără protecție"
    elif skew_current >= 115:
        skew_zone = "NORMAL"
        skew_color = "#4caf50"
        skew_hint = "✅ Risc normal"
    else:
        skew_zone = "SCĂZUT"
        skew_color = "#4caf50"
        skew_hint = "✅ Fără semnale de tail risk"
    
    # Combined VIX + SKEW Risk Assessment
    vol_risk_warning = ""
    if vix_current < 15 and skew_current > 130:
        vol_risk_warning = "🚨 ATENȚIE: VIX scăzut + SKEW ridicat = setup pre-crash clasic!"
    elif vix_current > 30:
        vol_risk_warning = "⛔ VIX > 30: Panică în piață, prudență maximă!"
    elif skew_current > 145:
        vol_risk_warning = "🚨 SKEW extrem: Marii investitori anticipează crash!"
    elif vix_current < 15:
        vol_risk_warning = "⚠️ VIX scăzut: Complazență ridicată."
    elif skew_current > 130:
        vol_risk_warning = "⚠️ SKEW ridicat: Smart money cumpără protecție."
    
    # Market Breadth Interpretation (% stocks above SMA50)
    # Market Breadth Interpretation (% stocks above SMA50)
    # Check if data exists - explicit check to avoid defaults masking failure
    breadth_quality = None
    breadth_quality_color = "#9e9e9e"
    
    if 'Breadth_Pct' in data and data['Breadth_Pct'] is not None:
        breadth_pct = data['Breadth_Pct']
        breadth_above = data.get('Breadth_Above', 0)
        breadth_total = data.get('Breadth_Total', 505)
        breadth_200_above = data.get('Breadth_200_Above', 0)
        breadth_200_pct = data.get('Breadth_200_Pct', 0)
        
        if breadth_pct >= 70:
            breadth_zone = "SĂNĂTOS"
            breadth_color = "#4caf50"
            breadth_hint = "✅ Rally larg - participare bună"
            breadth_ok = True
        elif breadth_pct >= 50:
            breadth_zone = "NORMAL"
            breadth_color = "#4caf50"
            breadth_hint = "✅ Majoritate peste SMA50"
            breadth_ok = True
        elif breadth_pct >= 30:
            breadth_zone = "SLAB"
            breadth_color = "#ff9800"
            breadth_hint = "⚠️ Rally concentrat - puține acțiuni participă"
            breadth_ok = False
        else:
            breadth_zone = "PERICOL"
            breadth_color = "#f44336"
            breadth_hint = "⛔ Breath foarte slab - risc de crash"
            breadth_ok = False
            
        breadth_source = data.get('Breadth_Source', 'Finviz')
        breadth_title = f"Breadth ({breadth_source})"
        breadth_header = f"{breadth_pct:.0f}%"
        
        # Get quality analysis
        breadth_quality = data.get('Breadth_Quality', '')
        breadth_quality_color = data.get('Breadth_Quality_Color', breadth_color)
        
        # Update hint to show quality if available
        if breadth_quality:
            breadth_hint = f"<span style='color: {breadth_quality_color}; font-weight: 600;'>{breadth_quality}</span>"
        
        # Format subtext safely
        breadth_subtext = f"SMA50: {breadth_above:.0f}/{breadth_total:.0f} | SMA200: {breadth_200_above:.0f}/{breadth_total:.0f} ({breadth_200_pct:.0f}%)"
        
    else:
        # Data Missing / Fetch Failed - Show honest state
        breadth_zone = "OFFLINE"
        breadth_color = "#9e9e9e" # Grey
        breadth_hint = "⚠️ Date Finviz indisponibile (Blocat?)"
        breadth_ok = False
        breadth_header = "N/A"
        breadth_subtext = "Datele nu au putut fi preluate"
        breadth_title = "Breadth (Missing)"
        breadth_pct = 0 # Safe default for downstream logic checks

    # Also get Breadth_200 for display (legacy/unused logic below, but kept for context if needed later)
    # breadth_200_pct = data.get('Breadth_200_Pct', 50) 
    pass
    
    # RSI Interpretation is done AFTER trend analysis (context-aware) - see below

    # --- Analysis Logic SPX ---
    # SPX SMA Trend Logic
    trend_bullish = spx_price > sma_200
    trend_text = "BULLISH" if trend_bullish else "BEARISH"
    trend_color = "#4caf50" if trend_bullish else "#f44336"

    # Breadth Logic was handled above - DO NOT OVERWRITE with SPX Trend!
    # breadth_ok = spx_price > sma_50 # REMOVED (Conflicting with Finviz Breadth)
    # breadth_color = "#4caf50" if breadth_ok else "#ff9800" # REMOVED
    breadth_text = "PUTERNIC" if breadth_ok else "SLAB"

    # SPX SMA10 Short-term Timing
    spx_timing_ok = spx_price > sma_10 if sma_10 else True
    spx_timing_color = "#4caf50" if spx_timing_ok else "#f44336"
    spx_timing_text = "UP" if spx_timing_ok else "DOWN"

    # --- Analysis Logic NDX (Nasdaq - "Motorul" Tech) ---
    ndx_trend_bullish = ndx_price > ndx_sma_200 if ndx_sma_200 else True
    ndx_trend_text = "BULLISH" if ndx_trend_bullish else "BEARISH"
    ndx_trend_color = "#4caf50" if ndx_trend_bullish else "#f44336"

    ndx_momentum_ok = ndx_price > ndx_sma_50 if ndx_sma_50 else True
    ndx_momentum_color = "#4caf50" if ndx_momentum_ok else "#ff9800"
    ndx_momentum_text = "PUTERNIC" if ndx_momentum_ok else "SLAB"

    # NDX SMA10 Short-term Timing
    ndx_timing_ok = ndx_price > ndx_sma_10 if ndx_sma_10 else True
    ndx_timing_color = "#4caf50" if ndx_timing_ok else "#f44336"
    ndx_timing_text = "UP" if ndx_timing_ok else "DOWN"

    # --- RSI Context-Aware Interpretation ---
    # RSI = CONFIRMARE, nu semnal! Interpretarea depinde de trend.
    def interpret_rsi_with_context(rsi_val, is_bullish_trend):
        if is_bullish_trend:
            # În trend BULLISH: RSI 40-80 e normal, pullback 40-50 = oportunitate
            if rsi_val >= 80:
                return "EXTINS", "#ff9800", "⚠️ Supraextins - evită intrări noi"
            elif rsi_val >= 50:
                return "MOMENTUM OK", "#4caf50", "✅ Trend sănătos (40-80)"
            elif rsi_val >= 40:
                return "BUY DIP", "#2196f3", "🎯 Pullback ideal pentru intrare!"
            else:
                return "SLĂBIT", "#ff9800", "⚠️ Momentum sub 40 - atenție"
        else:
            # În trend BEARISH: orice RSI e un warning
            if rsi_val >= 70:
                return "BOUNCE", "#ff9800", "⚠️ Bounce temporar, nu trend"
            elif rsi_val >= 50:
                return "NEUTRU", "#ff9800", "⚠️ Bear market - risc crescut"
            else:
                return "SLAB", "#f44336", "⛔ Bear market + momentum slab"
    
    spx_rsi_text, spx_rsi_color, spx_rsi_hint = interpret_rsi_with_context(spx_rsi, trend_bullish)
    ndx_rsi_text, ndx_rsi_color, ndx_rsi_hint = interpret_rsi_with_context(ndx_rsi, ndx_trend_bullish)

    # Divergence Detection (SPX vs NDX)
    divergence = trend_bullish != ndx_trend_bullish
    divergence_warning = ""
    if divergence:
        if trend_bullish and not ndx_trend_bullish:
            divergence_warning = "⚠️ DIVERGENȚĂ: SPX bullish dar NDX bearish - Tech în pericol!"
        elif ndx_trend_bullish and not trend_bullish:
            divergence_warning = "⚠️ DIVERGENȚĂ: NDX bullish dar SPX bearish - Tech rezistă."

    if fg_score < 25: fg_zone = "Extreme Fear"; fg_color = "#4caf50" 
    elif fg_score < 45: fg_zone = "Fear"; fg_color = "#8bc34a"
    elif fg_score < 55: fg_zone = "Neutral"; fg_color = "#ff9800"
    elif fg_score < 75: fg_zone = "Greed"; fg_color = "#f44336"
    else: fg_zone = "Extreme Greed"; fg_color = "#d32f2f"

    if pcr_val > 1.0:
        pcr_text = "OPORTUNITATE (Fear)"
        pcr_color = "#4caf50"
        panic_signal = True
    elif pcr_val < 0.7:
        pcr_text = "GREED"
        pcr_color = "#f44336"
        panic_signal = False
    else:
        pcr_text = "NEUTRAL"
        pcr_color = "#ff9800"
        panic_signal = False
    
    verdict = "WAIT"
    verdict_color = "#ff9800"
    verdict_reason = ""
    verdict_expl = ""
    
    # Combined analysis: Both SPX and NDX must align for strong signals
    both_bullish = trend_bullish and ndx_trend_bullish
    both_momentum = breadth_ok and ndx_momentum_ok
    both_timing = spx_timing_ok and ndx_timing_ok  # SMA10 timing
    
    if both_bullish:
        if fg_score < 50:
            if both_timing:
                # F&G Trend Logic (Falling Knife vs Recovery)
                if fg_score < fg_sma5:
                    # Falling Knife
                    verdict = "WAIT DIP"
                    verdict_color = "#ff9800"
                    verdict_reason = "Frica în creștere (Falling Knife)"
                    verdict_expl = f"Deși suntem în zonă de frică ({fg_score:.0f}), sentimentul se deteriorează rapid (sub media de 5 zile: {fg_sma5:.0f}). Nu prinde cuțitul care cade. Așteaptă stabilizarea."
                else:
                    # Recovery / Bottom
                    verdict = "BUY"
                    verdict_color = "#4caf50"
                    verdict_reason = "Trend UP + Frica (Stabilizare)"
                    verdict_expl = f"Configurație ideală 'Buy the Dip'. Trendul este UP, iar sentimentul de frică ({fg_score:.0f}) începe să se stabilizeze (peste media de 5 zile: {fg_sma5:.0f}). Punct de intrare optim."
            else:
                verdict = "WAIT DIP"
                verdict_color = "#ff9800"
                verdict_reason = "Trend UP + Frica, dar SMA10 DOWN"
                verdict_expl = f"Trendul major e bullish și există frică, dar prețul e sub SMA10 (SPX: {spx_timing_text}, NDX: {ndx_timing_text}). Așteaptă revenire peste SMA10 pentru intrare."
        else:
            verdict = "WAIT"
            verdict_color = "#ff9800"
            verdict_reason = "Trend UP + Euforie"
            verdict_expl = (
                f"Trendul este pozitiv (Bull Market pe SPX și NDX), dar sentimentul actual ({fg_rating}, scor {fg_score:.0f}) nu oferă un punct de intrare sigur. "
                "Așteaptă o corecție sau creștere a fricii (PCR > 1.0)."
            )
    elif trend_bullish and not ndx_trend_bullish:
        verdict = "AVOID TECH"
        verdict_color = "#f44336"
        verdict_reason = "⚠️ Divergență: SPX UP dar NDX DOWN"
        verdict_expl = "SPX este bullish dar Nasdaq a căzut sub SMA200. Evită acțiunile de Tech/Growth - rotație sectorială în curs. Preferă sectoare defensive sau cash."
    elif ndx_trend_bullish and not trend_bullish:
        verdict = "TECH ONLY"
        verdict_color = "#ff9800"
        verdict_reason = "Divergență: NDX UP dar SPX DOWN"
        verdict_expl = "Nasdaq rezistă dar SPX este slab. Tech poate performa, dar riscul general este ridicat. Intrări selective doar pe liderii tech."
    else:
        verdict = "CASH"
        verdict_color = "#f44336"
        verdict_reason = "Trend DOWN (Bear Market)"
        verdict_expl = "Ambii indici (SPX și NDX) sunt sub SMA200. Statistic, pozițiile Long au rată mică de succes. Păstrează cash sau joacă defensiv."

    # 2b. Market Tide Breadth Check (Tie-breaker)
    tide = data.get('Market_Tide')
    if tide:
        adv = tide.get('Advancing', 0) or 0
        dec = tide.get('Declining', 0) or 0
        new_highs = tide.get('NewHighs', 0) or 0
        new_lows = tide.get('NewLows', 0) or 0
        
        # A. Internal Weakness (New Lows > New Highs)
        if new_lows > new_highs and both_bullish:
             verdict = "WAIT (INTERNAL ROT)"
             verdict_color = "#ff9800"
             verdict_reason = f"New Lows ({new_lows}) > Highs ({new_highs})"
             verdict_expl = f"Deși indicii principali arată bine, sub capotă piața sângerează ({new_lows} minime noi vs {new_highs} maxime). Această divergență precede adesea o corecție majoră. Fii precaut."
        
        # B. Panic Selling Verification (Falling Knife)
        elif verdict == "WAIT DIP" and "Falling Knife" in verdict_reason:
            if dec > 2 * adv:
                 verdict_expl += f" 📉 Confirmat de Market Breadth: {dec} acțiuni scad vs {adv} cresc. Vânzare generalizată."
            elif adv > dec:
                 # Divergence: Price down (Fear) but Breadth Up?
                 verdict_expl += f" ⚠️ Notă: Deși sentimentul e rău, Breadth-ul e pozitiv ({adv} > {dec}). Ar putea fi o sperietură falsă (dip buyable)."

    if panic_signal and both_bullish and both_timing:
        verdict += " (STRONG)"
        verdict_expl += " Panica semnalată de Put/Call confirmă un potențial minim local iminent."
    
    # Add VIX/SKEW risk warning to explanation
    if vol_risk_warning:
        verdict_expl += f" {vol_risk_warning}"
    
    # VIX panic overrides BUY signals
    if vix_current > 30 and verdict.startswith("BUY"):
        verdict = "WAIT (PANIC)"
        verdict_color = "#f44336"
        verdict_reason = "⛔ VIX > 30: Panică în piață"
        verdict_expl = "VIX peste 30 indică panică extremă. Chiar dacă condițiile de trend sunt favorabile, volatilitatea e prea mare. Așteaptă stabilizare."
    
    # Fake rally (breadth < 30%) blocks BUY signals
    if breadth_pct < 30 and verdict.startswith("BUY"):
        verdict = "WAIT (FAKE RALLY)"
        verdict_color = "#f44336"
        verdict_reason = f"⛔ Breadth {breadth_pct:.0f}%: Rally fals"
        verdict_expl = f"Doar {breadth_pct:.0f}% din acțiuni participă în rally. Indicele e tras de câțiva giganți. Risc mare de corecție bruscă."
    # Add breadth quality as confidence modifier
    elif breadth_quality and verdict.startswith("BUY"):
        if "Aligned" in breadth_quality:
            verdict += " (HIGH CONFIDENCE)"
            verdict_expl += f" ✅ {breadth_quality} - rally sustenabil, risc redus."
        elif "Fresh" in breadth_quality:
            verdict_expl += f" 🔥 {breadth_quality} - momentum puternic dar urmărește semnale de epuizare."
        elif "Correction" in breadth_quality:
            verdict_expl += f" 📉 {breadth_quality} - revenire după corecție, nivel de intrare potențial." 
    elif not breadth_ok and verdict.startswith("BUY"):
        verdict_expl += f" ⚠️ ATENȚIE BREADTH: Doar {breadth_pct:.0f}% din acțiuni participă - posibil fake rally!"
    
    # --- Individual SPX Verdict ---
    if trend_bullish:
        if fg_score < 50:
            if fg_score < fg_sma5:
                 spx_verdict = "WAIT DIP"
                 spx_verdict_color = "#ff9800"
                 spx_verdict_text = "Bull Market + Frică în creștere (Falling Knife). Așteaptă stabilizare."
            elif not spx_timing_ok:
                 spx_verdict = "WAIT DIP"
                 spx_verdict_color = "#ff9800"
                 spx_verdict_text = f"Bull + Frică (Stabilizare), dar sub SMA10. Așteaptă revenire peste SMA10."
            else:
                 spx_verdict = "BUY"
                 spx_verdict_color = "#4caf50"
                 spx_verdict_text = "Bull Market + Frică (Stabilizare) = Oportunitate."
        else:
            spx_verdict = "WAIT"
            spx_verdict_color = "#ff9800"
            spx_verdict_text = "Bull Market, dar euforie excesivă. Așteaptă corecție."
    else:
        spx_verdict = "CASH"
        spx_verdict_color = "#f44336"
        spx_verdict_text = "Bear Market (sub SMA200). Risc ridicat pentru poziții Long."
    
    # Add confirmation indicators to SPX conclusion
    spx_confirmations = []
    if spx_rsi >= 80:
        spx_confirmations.append(f"⚠️ RSI {spx_rsi:.0f} (supraextins)")
    elif spx_rsi >= 40 and spx_rsi < 50:
        spx_confirmations.append(f"🎯 RSI {spx_rsi:.0f} (Buy Dip)")
    
    if vol_risk_warning:
        spx_confirmations.append(vol_risk_warning)
    
    # Add breadth quality context instead of just weak participation
    breadth_quality = data.get('Breadth_Quality', '')
    if breadth_quality:
        if "Aligned" in breadth_quality:
            spx_confirmations.append(f"✅ {breadth_quality}")
        elif "Fresh" in breadth_quality:
            spx_confirmations.append(f"🔥 {breadth_quality}")
        elif "Correction" in breadth_quality:
            spx_confirmations.append(f"📉 {breadth_quality}")
        else:
            spx_confirmations.append(f"➖ {breadth_quality}")
    elif not breadth_ok:
        spx_confirmations.append(f"⚠️ Breadth {breadth_pct:.0f}% (participare slabă)")
    
    if spx_confirmations:
        spx_verdict_text += " | " + " | ".join(spx_confirmations)

    # --- SAFETY LOCK: Market Tide Override (SPX) ---
    if tide:
        t_nh = tide.get('NewHighs', 0) or 0
        t_nl = tide.get('NewLows', 0) or 0
        if t_nl > t_nh and spx_verdict in ["BUY", "WAIT DIP"]:
            spx_verdict = "WAIT (INTERNAL ROT)"
            spx_verdict_color = "#ff9800"
            spx_verdict_text = f"⛔ SAFETY LOCK: New Lows ({t_nl}) > Highs ({t_nh}). Piața sângerează intern. Ignoră semnalele Bullish."
    
    # --- Individual NDX Verdict ---
    if ndx_trend_bullish:
        if fg_score < 50:
            if fg_score < fg_sma5:
                ndx_verdict = "WAIT TECH"
                ndx_verdict_color = "#ff9800"
                ndx_verdict_text = "Tech Bullish + Frică în creștere. Risc de corecție mai adâncă."
            elif not ndx_timing_ok:
                ndx_verdict = "WAIT TECH"
                ndx_verdict_color = "#ff9800"
                ndx_verdict_text = f"Nasdaq bullish + Frică (Stabilizare), dar sub SMA10. Așteaptă revenire."
            else:
                ndx_verdict = "BUY TECH"
                ndx_verdict_color = "#4caf50"
                ndx_verdict_text = "Nasdaq bullish + Frică (Stabilizare) = oportunitate pe Growth/Tech."
        else:
            ndx_verdict = "HOLD TECH"
            ndx_verdict_color = "#ff9800"
            ndx_verdict_text = "Tech în trend ascendent, dar greed = riscant pentru intrări noi."
    else:
        ndx_verdict = "AVOID TECH"
        ndx_verdict_color = "#f44336"
        ndx_verdict_text = "Nasdaq sub SMA200. Acțiunile Tech/Growth sunt vulnerabile."
    
    # Add confirmation indicators to NDX conclusion
    ndx_confirmations = []
    if ndx_rsi >= 80:
        ndx_confirmations.append(f"⚠️ RSI {ndx_rsi:.0f} (supraextins)")
    elif ndx_rsi >= 40 and ndx_rsi < 50:
        ndx_confirmations.append(f"🎯 RSI {ndx_rsi:.0f} (Buy Dip)")
    
    if vol_risk_warning:
        ndx_confirmations.append(vol_risk_warning)
    
    # Add breadth quality context (same logic as SPX)
    if breadth_quality:
        if "Aligned" in breadth_quality:
            ndx_confirmations.append(f"✅ {breadth_quality}")
        elif "Fresh" in breadth_quality:
            ndx_confirmations.append(f"🔥 {breadth_quality}")
        elif "Correction" in breadth_quality:
            ndx_confirmations.append(f"📉 {breadth_quality}")
        else:
            ndx_confirmations.append(f"➖ {breadth_quality}")
    elif not breadth_ok:
        ndx_confirmations.append(f"⚠️ Breadth {breadth_pct:.0f}% (participare slabă)")
    
    if ndx_confirmations:
        ndx_verdict_text += " | " + " | ".join(ndx_confirmations)

    # --- Market Bias Calculation ---
    bias = calculate_market_bias(data)
    
    bias_html = f"""
    <div style="grid-column: 1 / -1; background: {bias['color']}22; border-left: 5px solid {bias['color']}; padding: 15px; border-radius: 5px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <div style="font-size: 0.8rem; color: #888; text-transform: uppercase; font-weight: bold;">Market Bias</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: {bias['color']}; letter-spacing: 1px;">{bias['verdict']}</div>
            <div style="font-size: 0.8rem; color: #aaa;">Score: {bias['score']}/100</div>
        </div>
        <div style="text-align: right; font-size: 0.75rem; color: #888; border-left: 1px solid rgba(255,255,255,0.1); padding-left: 15px;">
            {'<br>'.join(bias['details'])}
        </div>
    </div>
    """

    # --- SAFETY LOCK: Market Tide Override (NDX) ---
    if tide:
        t_nh = tide.get('NewHighs', 0) or 0
        t_nl = tide.get('NewLows', 0) or 0
        if t_nl > t_nh and ndx_verdict in ["BUY TECH", "WAIT TECH"]:
            ndx_verdict = "WAIT (INTERNAL ROT)"
            ndx_verdict_color = "#ff9800"
            ndx_verdict_text = f"⛔ SAFETY LOCK: New Lows ({t_nl}) > Highs ({t_nh}). Risk de corecție Tech. Așteaptă stabilizare."
    
    uid = str(int(datetime.datetime.now().timestamp()))

    # Logic for Market Tide HTML
    # Logic for Market Tide HTML
    tide_html = ""
    tide = data.get('Market_Tide') or {}
    
    # Defaults
    t_adv = 0; t_dec = 0; t_nh = 0; t_nl = 0
    t_adv_pct = 0; t_dec_pct = 0; t_nh_pct = 0; t_nl_pct = 0
    sma50_pct = 0; sma200_pct = 0
    tide_timestamp_str = ""
    t_label = "OFFLINE"
    t_color = "#9e9e9e"
    t_msg = "Date indisponibile (Finviz)"
    
    if tide:
        t_adv = tide.get('Advancing', 0) or 0
        t_dec = tide.get('Declining', 0) or 0
        total_issues = t_adv + t_dec
        t_adv_pct = (t_adv / total_issues * 100) if total_issues else 0
        t_dec_pct = (t_dec / total_issues * 100) if total_issues else 0
        
        t_nh = tide.get('NewHighs', 0) or 0
        t_nl = tide.get('NewLows', 0) or 0
        total_hl = t_nh + t_nl
        t_nh_pct = (t_nh / total_hl * 100) if total_hl else 0
        t_nl_pct = (t_nl / total_hl * 100) if total_hl else 0
        
        t_label = "NEUTRAL"
        t_color = "#ff9800"
        t_msg = "Piață Mixtă"
        
        if t_adv > t_dec and t_nh > t_nl:
             t_label = "BULLISH"
             t_color = "#4caf50"
             t_msg = "Piață Puternică"
        elif t_dec > t_adv and t_nl > t_nh:
             t_label = "BEARISH"
             t_color = "#f44336"
             t_msg = "Piață Slabă"
        elif t_nl > t_nh:
             t_label = "WEAKNESS"
             t_color = "#f44336"
             t_msg = "slăbiciune Internă"
        elif t_nh > t_nl and t_adv < t_dec:
             t_label = "DIVERGENCE"
             t_msg = "Divergență (Highs vs Breadth)"


        # Helper to safely parse int
        def safe_int_tide(val):
            try:
                if isinstance(val, str):
                    return int(val.replace(',', ''))
                return int(val)
            except:
                return 0

        # Create SMA50/SMA200 Percentages
        sma50_above = safe_int_tide(tide.get('SMA50_Above', '0'))
        sma50_below = safe_int_tide(tide.get('SMA50_Below', '0'))
        sma50_total = sma50_above + sma50_below
        sma50_pct = (sma50_above / sma50_total * 100) if sma50_total > 0 else 0
        
        sma200_above = safe_int_tide(tide.get('SMA200_Above', '0'))
        sma200_below = safe_int_tide(tide.get('SMA200_Below', '0'))
        sma200_total = sma200_above + sma200_below
        sma200_pct = (sma200_above / sma200_total * 100) if sma200_total > 0 else 0
        
        # Format cache timestamp
        tide_timestamp_str = ""
        if tide and '_cached_at' in tide:
            try:
                cached_time = datetime.datetime.fromisoformat(tide['_cached_at'])
                now = datetime.datetime.now()
                tide_timestamp_str = f" • Actualizat: {cached_time.strftime('%Y-%m-%d %H:%M')}"
            except:
                pass

    tide_html = f"""
        <!-- 8. MARKET TIDE CARD (FINVIZ FULL) -->
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <div>
                    <span style="font-weight: 600; color: #555;">🌊 Market Tide (Full US)</span>
                    <div style="font-size: 10px; color: #999;">Advance/Decline lines & New Highs/Lows</div>
                </div>
                <div style="text-align: right;">
                     <div style="font-weight: 800; color: {t_color};">{t_label}</div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <!-- Adv/Dec -->
                <div style="background: #fafafa; padding: 8px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 11px; color: #666; margin-bottom: 4px;">Advance / Decline</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px; font-weight: 700;">
                        <span style="color: #4caf50;">{t_adv} ({t_adv_pct:.0f}%)</span>
                        <span style="color: #f44336;">{t_dec} ({t_dec_pct:.0f}%)</span>
                    </div>
                    <div style="height: 4px; background: #eee; border-radius: 2px; margin-top: 4px; overflow: hidden; display: flex;">
                        <div style="width: {t_adv_pct}%; background: #4caf50;"></div>
                        <div style="width: {t_dec_pct}%; background: #f44336;"></div>
                    </div>
                </div>
                
                <!-- Highs/Lows -->
                <div style="background: #fafafa; padding: 8px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 11px; color: #666; margin-bottom: 4px;">New Highs / Lows</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px; font-weight: 700;">
                        <span style="color: #4caf50;">{t_nh} ({t_nh_pct:.0f}%)</span>
                        <span style="color: #f44336;">{t_nl} ({t_nl_pct:.0f}%)</span>
                    </div>
                    <div style="height: 4px; background: #eee; border-radius: 2px; margin-top: 4px; overflow: hidden; display: flex;">
                        <div style="width: {t_nh_pct}%; background: #4caf50;"></div>
                        <div style="width: {t_nl_pct}%; background: #f44336;"></div>
                    </div>
                </div>
                
                <!-- SMA 50 -->
                <div style="background: #fafafa; padding: 8px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 11px; color: #666; margin-bottom: 4px;">Above/Below SMA 50</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px; font-weight: 700;">
                        <span style="color: #4caf50;">{tide.get('SMA50_Above', 'N/A')} ({sma50_pct:.0f}%)</span>
                        <span style="color: #f44336;">{tide.get('SMA50_Below', 'N/A')} ({100-sma50_pct:.0f}%)</span>
                    </div>
                     <div style="height: 4px; background: #eee; border-radius: 2px; margin-top: 4px; overflow: hidden; display: flex;">
                        <div style="width: {sma50_pct}%; background: #4caf50;"></div>
                        <div style="width: {100-sma50_pct}%; background: #f44336;"></div>
                    </div>
                    <div style="font-size: 9px; color: #999; margin-top: 2px;">Data Available</div>
                </div>

                <!-- SMA 200 -->
                 <div style="background: #fafafa; padding: 8px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 11px; color: #666; margin-bottom: 4px;">Above/Below SMA 200</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px; font-weight: 700;">
                        <span style="color: #4caf50;">{tide.get('SMA200_Above', 'N/A')} ({sma200_pct:.0f}%)</span>
                        <span style="color: #f44336;">{tide.get('SMA200_Below', 'N/A')} ({100-sma200_pct:.0f}%)</span>
                    </div>
                     <div style="height: 4px; background: #eee; border-radius: 2px; margin-top: 4px; overflow: hidden; display: flex;">
                        <div style="width: {sma200_pct}%; background: #4caf50;"></div>
                        <div style="width: {100-sma200_pct}%; background: #f44336;"></div>
                    </div>
                     <div style="font-size: 9px; color: #999; margin-top: 2px;">Data Available</div>
                </div>
                
            </div>
            
            <div style="font-size: 11px; color: {t_color}; margin-top: 10px; text-align: center; font-weight: 500;">
                 {t_msg}
            </div>
            <div style="font-size: 9px; color: #888; margin-top: 4px; text-align: center;">
                Sursă: Finviz Home Page{tide_timestamp_str}
            </div>
        </div>
        """


    html = f"""
    <div style="margin: 32px 0; background: #fff; border-radius: 12px; border: 1px solid #e0e0e0; box-shadow: 0 4px 12px rgba(0,0,0,0.08); overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        
        <div style="background: {verdict_color}; padding: 16px 24px; color: white; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px;">
            <div>
                <h3 style="margin: 0; font-size: 18px; font-weight: 700;">🏦 Swing Trading Signal (Long-only)</h3>
                <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">Analiză Context SPX + NDX • Strategie Trend Following</div>
            </div>
            <div style="text-align: right;">
                 <div style="background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 16px; border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{verdict}</div>
            </div>
        </div>

        <div style="padding: 24px;">
            
            <!-- MARKET BIAS CARD -->
            {bias_html}
            
            <!-- SECTION 1: METRICS & CHARTS (4 Columns) -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-bottom: 32px;">
                
                <!-- 1. TREND CARD -->
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px; background: #fdfdfd; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #555;">Trend (SMA200)</span>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {trend_color};">{trend_text}</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 160px; width: 100%;">
                        <canvas id="chart_trend_{uid}"></canvas>
                    </div>
                    <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #f5f5f5; padding: 4px; border-radius: 4px;">
                        Preț: <b>{spx_price:.0f}</b> / <span style="color:#f9a825">SMA200: <b>{sma_200:.0f}</b></span>
                    </div>
                </div>

                <!-- 2. BREADTH CARD -->
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px; background: #fdfdfd; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #555;">Momentum (SMA50)</span>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {breadth_color};">{breadth_text}</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 160px; width: 100%;">
                        <canvas id="chart_breadth_{uid}"></canvas>
                    </div>
                    <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #f5f5f5; padding: 4px; border-radius: 4px;">
                        Preț: <b>{spx_price:.0f}</b> / <span style="color:#2e7d32">SMA50: <b>{sma_50:.0f}</b></span>
                    </div>
                </div>

                <!-- 2b. TIMING CARD (SMA10) -->
                <div style="border: 1px solid #e3f2fd; border-radius: 8px; padding: 16px; background: #f8fbff; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #555;">Timing (SMA10)</span>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {spx_timing_color};">{spx_timing_text}</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 160px; width: 100%;">
                        <canvas id="chart_timing_{uid}"></canvas>
                    </div>
                    <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #e3f2fd; padding: 4px; border-radius: 4px;">
                        Preț: <b>{spx_price:.0f}</b> / <span style="color:#1976d2">SMA10: <b>{sma_10:.0f}</b></span>
                    </div>
                </div>

                <!-- 3. SENTIMENT CARD -->
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px; background: #fdfdfd; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: 600; color: #555;">Sentiment (F&G)</span>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {fg_color};">{fg_zone} ({fg_score:.0f})</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 120px; width: 100%;">
                        <canvas id="chart_fg_{uid}"></canvas>
                    </div>
                    <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center;">
                        Scor: <b>{fg_score:.0f}</b> / 100
                    </div>
                </div>

                <!-- 4. TIMING CARD -->
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 16px; background: #fdfdfd; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>
                            <span style="font-weight: 600; color: #555;">Total PCR (CNN)</span>
                            <div style="font-size: 10px; color: #999;">Total Market Volume</div>
                        </div>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {pcr_color};">{pcr_text}</div>
                        </div>
                    </div>
                     <div style="position: relative; height: 120px; width: 100%;">
                        <canvas id="chart_pcr_{uid}"></canvas>
                    </div>
                    <div style="font-size: 16px; color: {pcr_color}; font-weight: 800; margin-top: 8px; text-align: center;">
                        {pcr_val:.2f}
                    </div>
                    <div style="font-size: 10px; color: #555; margin-top: 6px; text-align: center; display: flex; justify-content: center; gap: 16px;">
                        <span style="display: flex; align-items: center;"><span style="width: 12px; height: 3px; background: {pcr_color}; margin-right: 4px;"></span>Zilnic: <b style="margin-left: 2px;">{pcr_val:.2f}</b></span>
                        <span style="display: flex; align-items: center;"><span style="width: 12px; height: 2px; border-top: 2px dotted #999; margin-right: 4px;"></span>MA10: <b style="margin-left: 2px;">{pcr_ma10:.2f}</b></span>
                    </div>
                </div>

                <!-- 5. RSI MOMENTUM CARD (SPX) -->
                <div style="border: 1px solid #ffe0b2; border-radius: 8px; padding: 16px; background: #fff8e1; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>
                            <span style="font-weight: 600; color: #555;">Momentum (RSI14)</span>
                            <div style="font-size: 10px; color: #999;">Confirmation Signal</div>
                        </div>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {spx_rsi_color};">{spx_rsi_text}</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 100px; width: 100%;">
                        <canvas id="chart_rsi_{uid}"></canvas>
                    </div>
                    <div style="font-size: 14px; color: {spx_rsi_color}; font-weight: 800; margin-top: 8px; text-align: center;">
                        D: {spx_rsi:.1f} | W: {data.get('SPX_RSI_Weekly', 50):.1f}
                    </div>
                    <div style="font-size: 10px; color: #555; margin-top: 4px; text-align: center;">
                        {spx_rsi_hint}
                    </div>
                </div>

                <!-- 6. VIX VOLATILITY CARD -->
                <div style="border: 1px solid #ffcdd2; border-radius: 8px; padding: 16px; background: #fff5f5; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>
                            <span style="font-weight: 600; color: #555;">Volatilitate (VIX)</span>
                            <div style="font-size: 10px; color: #999;">Fear Index</div>
                        </div>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {vix_color};">{vix_zone}</div>
                        </div>
                    </div>
                    <div style="position: relative; height: 100px; width: 100%;">
                        <canvas id="chart_vix_{uid}"></canvas>
                    </div>
                    <div style="font-size: 14px; color: {vix_color}; font-weight: 800; margin-top: 8px; text-align: center;">
                        VIX: {vix_current:.1f}
                    </div>
                    <div style="font-size: 10px; color: #555; margin-top: 4px; text-align: center;">
                        {vix_hint}
                    </div>
                    <div style="font-size: 9px; color: #888; margin-top: 4px; text-align: center;">
                        Percentilă 6M: {vix_percentile:.0f}% | SMA20: {vix_sma20:.1f}
                    </div>
                </div>

                <!-- 7. SKEW TAIL RISK CARD -->
                <div style="border: 1px solid #e1bee7; border-radius: 8px; padding: 16px; background: #faf5fc; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>
                            <span style="font-weight: 600; color: #555;">Tail Risk (SKEW)</span>
                            <div style="font-size: 10px; color: #999;">Black Swan Index</div>
                        </div>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {skew_color};">{skew_zone}</div>
                        </div>
                    </div>
                    <div style="font-size: 24px; color: {skew_color}; font-weight: 800; margin: 16px 0; text-align: center;">
                        {skew_current:.0f}
                    </div>
                    <div style="font-size: 10px; color: #555; margin-top: 4px; text-align: center;">
                        {skew_hint}
                    </div>
                </div>

                <!-- 8. MARKET BREADTH CARD -->
                <div style="border: 1px solid #c8e6c9; border-radius: 8px; padding: 16px; background: #f1f8e9; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>
                            <span style="font-weight: 600; color: #555;">{breadth_title}</span>
                            <div style="font-size: 10px; color: #999;">Participare în Rally</div>
                        </div>
                        <div style="text-align: right;">
                             <div style="font-weight: 800; color: {breadth_color};">{breadth_zone}</div>
                        </div>
                    </div>
                    <div style="font-size: 28px; color: {breadth_color}; font-weight: 800; margin: 16px 0; text-align: center;">
                        {breadth_header}
                    </div>
                    <div style="font-size: 10px; color: #555; margin-top: 4px; text-align: center;">
                        {breadth_hint}
                    </div>
                    <div style="font-size: 9px; color: #888; margin-top: 4px; text-align: center;">
                        {breadth_subtext}
                    </div>
                </div>
            </div>

            <!-- MARKET TIDE CARD (Full Width) -->
            {tide_html}

            <!-- SECTION 1b: NASDAQ (Tech Motor) -->
            <div style="margin-bottom: 32px;">
                <div style="font-size: 14px; font-weight: 700; color: #7b1fa2; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid #e1bee7;">
                    📊 NASDAQ (NDX) — „Motorul" Tech
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px;">
                    
                    <!-- NDX TREND CARD -->
                    <div style="border: 1px solid #e1bee7; border-radius: 8px; padding: 16px; background: #faf5fc; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <div>
                                <span style="font-weight: 600; color: #555;">NDX Trend (SMA200)</span>
                                <div style="font-size: 10px; color: #999;">Nasdaq 100</div>
                            </div>
                            <div style="text-align: right;">
                                 <div style="font-weight: 800; color: {ndx_trend_color};">{ndx_trend_text}</div>
                            </div>
                        </div>
                        <div style="position: relative; height: 140px; width: 100%;">
                            <canvas id="chart_ndx_trend_{uid}"></canvas>
                        </div>
                        <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #f3e5f5; padding: 4px; border-radius: 4px;">
                            Preț: <b>{ndx_price:.0f}</b> / <span style="color:#f9a825">SMA200: <b>{ndx_sma_200:.0f}</b></span>
                        </div>
                    </div>

                    <!-- NDX MOMENTUM CARD -->
                    <div style="border: 1px solid #e1bee7; border-radius: 8px; padding: 16px; background: #faf5fc; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <div>
                                <span style="font-weight: 600; color: #555;">NDX Momentum (SMA50)</span>
                                <div style="font-size: 10px; color: #999;">Nasdaq 100</div>
                            </div>
                            <div style="text-align: right;">
                                 <div style="font-weight: 800; color: {ndx_momentum_color};">{ndx_momentum_text}</div>
                            </div>
                        </div>
                        <div style="position: relative; height: 140px; width: 100%;">
                            <canvas id="chart_ndx_momentum_{uid}"></canvas>
                        </div>
                        <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #f3e5f5; padding: 4px; border-radius: 4px;">
                            Preț: <b>{ndx_price:.0f}</b> / <span style="color:#2e7d32">SMA50: <b>{ndx_sma_50:.0f}</b></span>
                        </div>
                    </div>

                    <!-- NDX TIMING CARD (SMA10) -->
                    <div style="border: 1px solid #e1bee7; border-radius: 8px; padding: 16px; background: #faf5fc; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <div>
                                <span style="font-weight: 600; color: #555;">NDX Timing (SMA10)</span>
                                <div style="font-size: 10px; color: #999;">Nasdaq 100</div>
                            </div>
                            <div style="text-align: right;">
                                 <div style="font-weight: 800; color: {ndx_timing_color};">{ndx_timing_text}</div>
                            </div>
                        </div>
                        <div style="position: relative; height: 140px; width: 100%;">
                            <canvas id="chart_ndx_timing_{uid}"></canvas>
                        </div>
                        <div style="font-size: 12px; color: #555; margin-top: 8px; text-align: center; background: #f3e5f5; padding: 4px; border-radius: 4px;">
                            Preț: <b>{ndx_price:.0f}</b> / <span style="color:#1976d2">SMA10: <b>{ndx_sma_10:.0f}</b></span>
                        </div>
                    </div>

                    <!-- NDX RSI MOMENTUM CARD -->
                    <div style="border: 1px solid #e1bee7; border-radius: 8px; padding: 16px; background: #faf5fc; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <div>
                                <span style="font-weight: 600; color: #555;">NDX Momentum (RSI14)</span>
                                <div style="font-size: 10px; color: #999;">Confirmation Signal</div>
                            </div>
                            <div style="text-align: right;">
                                 <div style="font-weight: 800; color: {ndx_rsi_color};">{ndx_rsi_text}</div>
                            </div>
                        </div>
                        <div style="position: relative; height: 100px; width: 100%;">
                            <canvas id="chart_ndx_rsi_{uid}"></canvas>
                        </div>
                        <div style="font-size: 14px; color: {ndx_rsi_color}; font-weight: 800; margin-top: 8px; text-align: center;">
                            D: {ndx_rsi:.1f} | W: {data.get('NDX_RSI_Weekly', 50):.1f}
                        </div>
                        <div style="font-size: 10px; color: #555; margin-top: 4px; text-align: center;">
                            {ndx_rsi_hint}
                        </div>
                    </div>

                </div>
            </div>

            <!-- SECTION 2: ANALYSIS DETAILS -->
            <div style="border-top: 2px solid #f0f0f0; padding-top: 24px;">
                <h4 style="margin: 0 0 16px 0; color: {verdict_color}; font-size: 18px; text-transform: uppercase;">
                   ⚠️ Analiză: {verdict_reason}
                </h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                    
                    <!-- S&P 500 Analysis -->
                    <div style="background: #e3f2fd; padding: 16px; border-radius: 8px; border-left: 4px solid {spx_verdict_color};">
                        <div style="font-size: 11px; font-weight: bold; color: #1565c0; text-transform: uppercase; margin-bottom: 4px;">📈 S&P 500 (Corpul)</div>
                        <div style="font-size: 18px; font-weight: 800; color: {spx_verdict_color}; margin-bottom: 8px;">{spx_verdict}</div>
                        <div style="font-size: 12px; color: #333; margin-bottom: 6px;">
                            <b>Trend:</b> <span style="color:{trend_color}">{trend_text}</span> | <b>Momentum:</b> <span style="color:{breadth_color}">{breadth_text}</span>
                        </div>
                        <div style="font-size: 13px; color: #444; font-style: italic;">"{spx_verdict_text}"</div>
                    </div>

                    <!-- Nasdaq Analysis -->
                    <div style="background: #f3e5f5; padding: 16px; border-radius: 8px; border-left: 4px solid {ndx_verdict_color};">
                        <div style="font-size: 11px; font-weight: bold; color: #7b1fa2; text-transform: uppercase; margin-bottom: 4px;">🚀 NASDAQ (Motorul Tech)</div>
                        <div style="font-size: 18px; font-weight: 800; color: {ndx_verdict_color}; margin-bottom: 8px;">{ndx_verdict}</div>
                        <div style="font-size: 12px; color: #333; margin-bottom: 6px;">
                            <b>Trend:</b> <span style="color:{ndx_trend_color}">{ndx_trend_text}</span> | <b>Momentum:</b> <span style="color:{ndx_momentum_color}">{ndx_momentum_text}</span>
                        </div>
                        <div style="font-size: 13px; color: #444; font-style: italic;">"{ndx_verdict_text}"</div>
                    </div>

                    <!-- Combined Conclusion -->
                    <div style="background: {verdict_color}15; padding: 16px; border-radius: 8px; border: 2px solid {verdict_color}60; grid-column: 1 / -1;">
                        <div style="font-size: 11px; font-weight: bold; color: {verdict_color}; text-transform: uppercase; margin-bottom: 4px;">🎯 CONCLUZIE GENERALĂ</div>
                        <div style="font-size: 22px; font-weight: 800; color: {verdict_color}; margin-bottom: 8px;">{verdict}</div>
                        <div style="font-size: 14px; color: #333;">
                            {verdict_expl}
                        </div>
                    </div>

                </div>
            </div>

        </div>
    </div>

    <script>
    (function() {{
        const spxData = {chart_spx_json};
        const ndxData = {chart_ndx_json};
        const fgData = {chart_fg_json};
        const pcrData = {chart_pcr_json};
        const pcrMA = {chart_pcr_ma_json};
        const vixData = {chart_vix_json};

        if (typeof Chart !== 'undefined') {{
            new Chart(document.getElementById('chart_trend_{uid}').getContext('2d'), {{
                type: 'line',
                data: {{ labels: spxData.labels, datasets: [{{ label: 'Preț', data: spxData.price, borderColor: '#cad5e2', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA200', data: spxData.sma200, borderColor: '#fbc02d', borderWidth: 2, pointRadius: 0, borderDash: [2,2] }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
            }});
            new Chart(document.getElementById('chart_breadth_{uid}').getContext('2d'), {{
                type: 'line',
                data: {{ labels: spxData.labels, datasets: [{{ label: 'Preț', data: spxData.price, borderColor: '#cad5e2', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA50', data: spxData.sma50, borderColor: '#4caf50', borderWidth: 2, pointRadius: 0 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
            }});
            // SPX SMA10 Timing Chart
            new Chart(document.getElementById('chart_timing_{uid}').getContext('2d'), {{
                type: 'line',
                data: {{ labels: spxData.labels, datasets: [{{ label: 'Preț', data: spxData.price, borderColor: '#cad5e2', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA10', data: spxData.sma10, borderColor: '#1976d2', borderWidth: 2, pointRadius: 0 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
            }});
            new Chart(document.getElementById('chart_fg_{uid}').getContext('2d'), {{
                type: 'line',
                data: {{ labels: Array(fgData.length).fill(''), datasets: [{{ label: 'F&G', data: fgData, borderColor: '{fg_color}', backgroundColor: '{fg_color}20', fill: true, pointRadius: 0, tension: 0.4 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ min: 0, max: 100 }} }} }}
            }});
            new Chart(document.getElementById('chart_pcr_{uid}').getContext('2d'), {{
                type: 'line',
                data: {{ 
                    labels: Array(pcrData.length).fill(''), 
                    datasets: [
                        {{ label: 'PCR', data: pcrData, borderColor: '{pcr_color}', borderWidth: 1.5, pointRadius: 0, tension: 0.2 }},
                        {{ label: 'MA10', data: pcrMA, borderColor: '#999', borderWidth: 1, pointRadius: 0, borderDash: [2,2], tension: 0.2 }}
                    ] 
                }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }} }} }}
            }});
            
            // NDX Charts (Nasdaq - Purple theme)
            if (ndxData && ndxData.price && ndxData.price.length > 0) {{
                new Chart(document.getElementById('chart_ndx_trend_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ labels: ndxData.labels, datasets: [{{ label: 'Preț', data: ndxData.price, borderColor: '#d1c4e9', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA200', data: ndxData.sma200, borderColor: '#9c27b0', borderWidth: 2, pointRadius: 0, borderDash: [2,2] }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
                }});
                new Chart(document.getElementById('chart_ndx_momentum_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ labels: ndxData.labels, datasets: [{{ label: 'Preț', data: ndxData.price, borderColor: '#d1c4e9', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA50', data: ndxData.sma50, borderColor: '#7b1fa2', borderWidth: 2, pointRadius: 0 }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
                }});
                // NDX SMA10 Timing Chart
                new Chart(document.getElementById('chart_ndx_timing_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ labels: ndxData.labels, datasets: [{{ label: 'Preț', data: ndxData.price, borderColor: '#d1c4e9', borderWidth: 1.5, pointRadius: 0 }}, {{ label: 'SMA10', data: ndxData.sma10, borderColor: '#1976d2', borderWidth: 2, pointRadius: 0 }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: true }} }} }}
                }});
                // NDX RSI Chart
                new Chart(document.getElementById('chart_ndx_rsi_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ labels: ndxData.labels, datasets: [{{ label: 'RSI', data: ndxData.rsi, borderColor: '#9c27b0', backgroundColor: '#9c27b020', fill: true, borderWidth: 2, pointRadius: 0, tension: 0.3 }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ min: 0, max: 100, ticks: {{ callback: (v) => v === 30 || v === 70 ? v : '' }} }} }} }}
                }});
            }}
            
            // SPX RSI Chart
            if (spxData && spxData.rsi && spxData.rsi.length > 0) {{
                new Chart(document.getElementById('chart_rsi_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ labels: spxData.labels, datasets: [{{ label: 'RSI', data: spxData.rsi, borderColor: '#ff9800', backgroundColor: '#ff980020', fill: true, borderWidth: 2, pointRadius: 0, tension: 0.3 }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ min: 0, max: 100, ticks: {{ callback: (v) => v === 30 || v === 70 ? v : '' }} }} }} }}
                }});
            }}
            
            // VIX Chart with color zones
            if (vixData && vixData.values && vixData.values.length > 0) {{
                new Chart(document.getElementById('chart_vix_{uid}').getContext('2d'), {{
                    type: 'line',
                    data: {{ 
                        labels: vixData.labels, 
                        datasets: [{{ 
                            label: 'VIX', 
                            data: vixData.values, 
                            borderColor: '{vix_color}', 
                            backgroundColor: '{vix_color}20', 
                            fill: true, 
                            borderWidth: 2, 
                            pointRadius: 0, 
                            tension: 0.3 
                        }}] 
                    }},
                    options: {{ 
                        responsive: true, 
                        maintainAspectRatio: false, 
                        plugins: {{ legend: {{ display: false }} }}, 
                        scales: {{ 
                            x: {{ display: false }}, 
                            y: {{ min: 10, max: 40, ticks: {{ callback: (v) => [15, 20, 30].includes(v) ? v : '' }} }} 
                        }} 
                    }}
                }});
            }}
        }}
    }})();
    </script>
    """
    
    return html
def classify_strategy(data):
    """
    Classifies the trading setup based on Price, SMA, RSI, and Trend.
    Returns: 'Pullback', 'Breakout', 'Reversal', 'Range', or 'N/A'
    """
    try:
        price = data.get('Price', 0)
        sma50 = data.get('SMA_50', 0)
        sma200 = data.get('SMA_200', 0)
        rsi = data.get('RSI', 50)
        trend = data.get('Trend', 'Neutral')
        
        # Pullback: Bullish Trend + Correction
        # Logic: Uptrend (Price > 200), Price > SMA200, but RSI dipped (<55) and potentially < SMA10 (not checked here but implied)
        if "Bullish" in trend and price > sma200 and rsi < 55:
            if rsi < 45: return "Deep Pullback"
            return "Pullback"
            
        # Breakout: Strong Momentum
        # Logic: Price > SMA50, RSI Strong (>60), Trend is Bullish
        if "Bullish" in trend and price > sma50 and rsi > 60:
            if rsi > 70: return "Strong Breakout" # Watch for overbought
            return "Breakout"
            
        # Reversal: Oversold in downtrend or Divergence
        # Logic: RSI Oversold (<30)
        if rsi < 30:
            return "Reversal (Oversold)"
            
        # Range: Price trapped between SMAs or Low Volatility (implied)
        # Logic: Price between SMA50 and SMA200 (approximate consolidation)
        if (price > sma50 and price < sma200) or (price < sma50 and price > sma200):
            return "Range / Consolidation"
            
        return "Normal"
        
    except Exception as e:
        return "N/A"

def calculate_risk_reward(price, stop_loss, target):
    """
    Calculates R:R Ratio.
    Returns: float (e.g. 3.5 for 1:3.5) or 0 if invalid.
    """
    try:
        if not price or not stop_loss or not target:
            return 0
        
        risk = price - stop_loss
        reward = target - price
        
        if risk <= 0: return 0 # Stop is above price (invalid for Long)
        if reward <= 0: return 0 # Target is below price
        
        rr = reward / risk
        return round(rr, 2)
    except:
        return 0
