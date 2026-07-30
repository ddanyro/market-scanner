"""Read-only client for the IBKR Client Portal Web API.

Retail accounts authenticate through the locally running Client Portal Gateway.
This module deliberately exposes no order-placement or account-mutation methods.
"""

import datetime
import json
import os
import urllib.parse
import warnings

import requests
import urllib3


DEFAULT_BASE_URL = 'https://localhost:5000/v1/api'
SUMMARY_FIELDS = {
    'NetLiquidation': ('netliquidation', 'netliquidationvalue'),
    'EquityWithLoanValue': ('equitywithloanvalue',),
    'TotalCashValue': ('totalcashvalue', 'totalcashbalance'),
    'SettledCash': ('settledcash',),
    'AvailableFunds': ('availablefunds',),
    'BuyingPower': ('buyingpower',),
    'ExcessLiquidity': ('excessliquidity',),
    'InitMarginReq': ('initmarginreq', 'initialmargin'),
    'MaintMarginReq': ('maintmarginreq', 'maintmargin'),
    'GrossPositionValue': ('grosspositionvalue',),
    'Cushion': ('cushion',),
}


class IBKRWebAPIError(RuntimeError):
    """Raised when the local Gateway cannot provide a usable read-only reply."""


def _is_loopback_url(url):
    hostname = (urllib.parse.urlparse(url).hostname or '').lower()
    return hostname in {'localhost', '127.0.0.1', '::1'}


def _number(value):
    if isinstance(value, dict):
        value = value.get('amount', value.get('value'))
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if abs(result) < 1e100 else None


def _summary_value(summary, aliases):
    lowered = {str(key).lower(): value for key, value in (summary or {}).items()}
    for alias in aliases:
        value = _number(lowered.get(alias.lower()))
        if value is not None:
            return value
    return None


def _ratio_band(numerator, denominator):
    if numerator is None or denominator is None or denominator <= 0:
        return 'indisponibil'
    ratio = numerator / denominator * 100
    if ratio < 5:
        return 'sub 5%'
    if ratio < 15:
        return '5-15%'
    if ratio < 30:
        return '15-30%'
    if ratio < 50:
        return '30-50%'
    return 'peste 50%'


class IBKRWebAPIClient:
    """Minimal read-only wrapper around the local Client Portal Gateway."""

    def __init__(self, base_url=None, timeout=8, verify_ssl=None, session=None):
        self.base_url = (
            base_url or os.environ.get('IBKR_WEB_API_URL') or DEFAULT_BASE_URL
        ).rstrip('/')
        self.timeout = timeout
        if verify_ssl is None:
            verify_ssl = not _is_loopback_url(self.base_url)
        if not verify_ssl and not _is_loopback_url(self.base_url):
            raise ValueError('TLS verification may be disabled only for loopback URLs')
        self.verify_ssl = bool(verify_ssl)
        self.session = session or requests.Session()

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            with warnings.catch_warnings():
                if not self.verify_ssl:
                    warnings.simplefilter(
                        'ignore', urllib3.exceptions.InsecureRequestWarning
                    )
                response = self.session.request(
                    method,
                    url,
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                    **kwargs,
                )
        except requests.RequestException as exc:
            raise IBKRWebAPIError(f'Gateway IBKR indisponibil: {exc}') from exc
        if response.status_code >= 400:
            raise IBKRWebAPIError(
                f'IBKR Web API HTTP {response.status_code} pentru {path}'
            )
        try:
            return response.json()
        except ValueError as exc:
            raise IBKRWebAPIError(
                f'IBKR Web API a returnat JSON invalid pentru {path}'
            ) from exc

    def validate_session(self):
        payload = self._request('GET', '/sso/validate')
        return bool(payload.get('RESULT', payload.get('result', False)))

    def get_accounts(self):
        payload = self._request('GET', '/portfolio/accounts')
        if not isinstance(payload, list):
            raise IBKRWebAPIError('Lista conturilor IBKR are format invalid')
        return payload

    def get_summary(self, account_id):
        return self._request('GET', f'/portfolio/{account_id}/summary')

    def get_ledger(self, account_id):
        return self._request('GET', f'/portfolio/{account_id}/ledger')

    def get_positions(self, account_id, max_pages=20):
        positions = []
        for page in range(max_pages):
            payload = self._request(
                'GET', f'/portfolio/{account_id}/positions/{page}'
            )
            if not isinstance(payload, list):
                raise IBKRWebAPIError('Pozițiile IBKR au format invalid')
            positions.extend(payload)
            if not payload:
                break
        return positions

    def get_all_periods(self, account_ids):
        return self._request(
            'POST',
            '/pa/allperiods',
            json={'acctIds': list(account_ids)},
        )


def _normalise_nav_history(payload, account_ids):
    """Extract the longest daily NAV series returned by PortfolioAnalyst."""
    candidates = []
    for account_id in account_ids:
        account_data = (payload or {}).get(account_id, {})
        for period in ('1Y', 'YTD', '1M', '7D', '1D'):
            period_data = account_data.get(period, {})
            dates = period_data.get('dates', [])
            nav_values = period_data.get('nav', period_data.get('navs', []))
            if isinstance(nav_values, dict):
                nav_values = nav_values.get('data', nav_values.get('navs', []))
            if not isinstance(dates, list) or not isinstance(nav_values, list):
                continue
            points = []
            for date_value, nav_value in zip(dates, nav_values):
                number = _number(nav_value)
                if number is None or not str(date_value).strip():
                    continue
                points.append({
                    'date': str(date_value),
                    'nav': round(number, 2),
                    'currency': str(
                        account_data.get('baseCurrency', '')
                    ).upper(),
                })
            if points:
                candidates.append(points)
                break
    return max(candidates, key=len) if candidates else []


def build_account_snapshot(client=None):
    """Fetch current balances and one-year NAV history from the local Gateway."""
    client = client or IBKRWebAPIClient()
    if not client.validate_session():
        raise IBKRWebAPIError(
            'Sesiunea Client Portal Gateway nu este autentificată'
        )
    raw_accounts = client.get_accounts()
    accounts = []
    account_ids = []
    positions = []
    for raw_account in raw_accounts:
        account_id = str(
            raw_account.get('accountId') or raw_account.get('id') or ''
        ).strip()
        if not account_id:
            continue
        account_ids.append(account_id)
        summary_raw = client.get_summary(account_id)
        ledger_raw = client.get_ledger(account_id)
        base_currency = str(raw_account.get('currency', '')).upper() or 'BASE'
        base_ledger = ledger_raw.get('BASE', {}) if isinstance(ledger_raw, dict) else {}
        summary = {}
        for output_key, aliases in SUMMARY_FIELDS.items():
            value = _summary_value(summary_raw, aliases)
            if value is None:
                ledger_aliases = {
                    'NetLiquidation': ('netliquidationvalue',),
                    'TotalCashValue': ('cashbalance',),
                    'SettledCash': ('settledcash',),
                    'GrossPositionValue': ('stockmarketvalue',),
                }.get(output_key, ())
                value = _summary_value(base_ledger, ledger_aliases)
            if value is not None:
                summary[output_key] = value
        cash_by_currency = {}
        if isinstance(ledger_raw, dict):
            for currency, values in ledger_raw.items():
                code = str(currency).upper()
                if code == 'BASE' or not isinstance(values, dict):
                    continue
                cash = _number(values.get('cashbalance'))
                if cash is not None:
                    cash_by_currency[code] = cash
        account_positions = client.get_positions(account_id)
        for position in account_positions:
            item = dict(position)
            item['account_id'] = account_id
            positions.append(item)
        accounts.append({
            'account_id': account_id,
            'label': 'IBKR',
            'source': 'IBKR Client Portal Web API',
            'base_currency': base_currency,
            'summary': summary,
            'cash_by_currency': cash_by_currency,
        })
    if not accounts:
        raise IBKRWebAPIError('IBKR Web API nu a returnat niciun cont utilizabil')
    performance = client.get_all_periods(account_ids)
    return {
        'fetched_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source': 'IBKR Client Portal Web API',
        'accounts': accounts,
        'positions': positions,
        'nav_history': _normalise_nav_history(performance, account_ids),
    }


def _sanitised_snapshot(payload):
    accounts = []
    for account in payload.get('accounts', []):
        summary = account.get('summary', {})
        nav = _number(summary.get('NetLiquidation'))
        accounts.append({
            'label': account.get('label', 'IBKR'),
            'base_currency': account.get('base_currency', 'BASE'),
            'cash_currencies': sorted(account.get('cash_by_currency', {})),
            'cash_pct_band': _ratio_band(
                _number(summary.get('TotalCashValue')), nav
            ),
            'maintenance_margin_pct_band': _ratio_band(
                _number(summary.get('MaintMarginReq')), nav
            ),
            'available_funds_status': (
                'pozitiv' if (_number(summary.get('AvailableFunds')) or 0) > 0
                else 'zero/negativ'
            ),
        })
    return {
        'fetched_at': payload.get('fetched_at'),
        'source': payload.get('source'),
        'privacy_mode': 'bands_only',
        'sanitized_accounts': accounts,
    }


def persist_account_snapshot(
    payload,
    output_file='tws_account.json',
    encrypted_output='tws_account.enc.json',
    risk_output='tws_account_risk.json',
    password=None,
):
    """Persist an already validated snapshot for the existing dashboard."""
    with open(output_file, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    account_password = (
        password
        or os.environ.get('TWS_ACCOUNT_PASSWORD', '')
        or os.environ.get('PORTFOLIO_PASSWORD', '')
    )
    if not account_password and os.path.exists('password.txt'):
        try:
            with open('password.txt', 'r', encoding='utf-8') as handle:
                account_password = handle.read().strip()
        except OSError:
            account_password = ''
    if account_password:
        import market_security
        encrypted = market_security.encrypt_for_js(
            json.dumps(payload, ensure_ascii=False),
            account_password,
        )
        with open(encrypted_output, 'w', encoding='utf-8') as handle:
            handle.write(encrypted)

    with open(risk_output, 'w', encoding='utf-8') as handle:
        json.dump(
            _sanitised_snapshot(payload),
            handle,
            ensure_ascii=False,
            indent=2,
        )
    return payload


def sync_account_snapshot(
    client=None,
    output_file='tws_account.json',
    encrypted_output='tws_account.enc.json',
    risk_output='tws_account_risk.json',
    password=None,
):
    """Fetch and persist a schema-compatible snapshot for the dashboard."""
    payload = build_account_snapshot(client)
    return persist_account_snapshot(
        payload,
        output_file=output_file,
        encrypted_output=encrypted_output,
        risk_output=risk_output,
        password=password,
    )
