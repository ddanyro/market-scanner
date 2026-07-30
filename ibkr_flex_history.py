"""Extract and persist daily IBKR NAV/cash history from Activity Flex XML.

The module accepts only reporting data already returned by the configured Flex
Query. Missing NAV or cash sections are reported as unavailable; values are
never reconstructed from positions or invented.
"""

import datetime
import json
import os
import re


HISTORY_LIMIT = 366
BASE_CURRENCY_LABELS = {
    'BASE',
    'BASE_SUMMARY',
    'BASE CURRENCY',
    'BASE_CURRENCY',
}


def _tag(element):
    return str(element.tag).rsplit('}', 1)[-1]


def _attribute(element, *names):
    attributes = {
        str(key).lower(): value for key, value in (element.attrib or {}).items()
    }
    for name in names:
        value = attributes.get(str(name).lower())
        if value not in (None, ''):
            return value
    return None


def _number(value):
    if value in (None, ''):
        return None
    try:
        number = float(str(value).replace(',', ''))
    except (TypeError, ValueError):
        return None
    return number if abs(number) < 1e100 else None


def _normalise_date(value):
    raw = str(value or '').strip().split(';', 1)[0]
    digits = re.sub(r'[^0-9]', '', raw)
    if len(digits) >= 8:
        digits = digits[:8]
        try:
            return datetime.datetime.strptime(digits, '%Y%m%d').strftime(
                '%Y-%m-%d'
            )
        except ValueError:
            pass
    try:
        return datetime.date.fromisoformat(raw[:10]).isoformat()
    except (TypeError, ValueError):
        return ''


def _history_points(points, value_key, max_points=HISTORY_LIMIT):
    merged = {}
    for point in points or []:
        if not isinstance(point, dict):
            continue
        date_value = _normalise_date(point.get('date'))
        value = _number(point.get(value_key))
        currency = str(point.get('currency', '')).strip().upper()
        if not date_value or value is None or not currency:
            continue
        merged[(date_value, currency)] = {
            'date': date_value,
            value_key: round(value, 2),
            'currency': currency,
            'source': str(point.get('source', '')).strip(),
        }
    return [
        merged[key] for key in sorted(merged)
    ][-max(1, int(max_points)):]


def _extract_statement(statement):
    account_id = str(_attribute(statement, 'accountId') or '').strip()
    report_date = _normalise_date(
        _attribute(statement, 'toDate', 'reportDate', 'date')
    )
    base_currency = ''
    nav_by_date = {}
    cash_by_date = {}
    cash_by_currency = {}
    ending_nav = None
    ending_cash = None

    for element in statement.iter():
        tag = _tag(element)
        lowered_tag = tag.lower()

        if lowered_tag == 'accountinformation':
            base_currency = str(
                _attribute(element, 'baseCurrency', 'currency') or ''
            ).strip().upper()
            if not account_id:
                account_id = str(
                    _attribute(element, 'accountId') or ''
                ).strip()
            continue

        if lowered_tag == 'changeinnav':
            nav_value = _number(
                _attribute(
                    element,
                    'endingValue',
                    'endingNAV',
                    'endNAV',
                    'total',
                )
            )
            if nav_value is not None:
                ending_nav = nav_value
                if report_date:
                    nav_by_date[report_date] = nav_value
            continue

        if lowered_tag == 'cashreportcurrency':
            currency = str(
                _attribute(element, 'currency') or ''
            ).strip().upper()
            cash_value = _number(
                _attribute(
                    element,
                    'endingCash',
                    'endingSettledCash',
                    'cash',
                )
            )
            if cash_value is None:
                continue
            if currency in BASE_CURRENCY_LABELS:
                ending_cash = cash_value
                if report_date:
                    cash_by_date[report_date] = cash_value
            elif currency:
                cash_by_currency[currency] = cash_value
            continue

        # "Net Asset Value (NAV) Summary In Base" exposes one row per
        # reportDate. IBKR has used several closely related XML tag names, so
        # identify the row by its NAV-shaped tag and required dated total.
        compact_tag = re.sub(r'[^a-z]', '', lowered_tag)
        is_nav_summary = 'netassetvalue' in compact_tag
        if not is_nav_summary:
            continue
        point_date = _normalise_date(
            _attribute(element, 'reportDate', 'date', 'asOfDate')
        )
        nav_value = _number(
            _attribute(
                element,
                'total',
                'totalNAV',
                'netAssetValue',
                'endingValue',
                'endingNAV',
            )
        )
        if point_date and nav_value is not None:
            nav_by_date[point_date] = nav_value
            if not report_date or point_date >= report_date:
                ending_nav = nav_value
        cash_value = _number(
            _attribute(element, 'cash', 'totalCash', 'endingCash')
        )
        if point_date and cash_value is not None:
            cash_by_date[point_date] = cash_value
            if not report_date or point_date >= report_date:
                ending_cash = cash_value

    return {
        'account_id': account_id,
        'report_date': report_date,
        'base_currency': base_currency,
        'ending_nav': ending_nav,
        'ending_cash': ending_cash,
        'cash_by_currency': cash_by_currency,
        'nav_by_date': nav_by_date,
        'cash_by_date': cash_by_date,
    }


def _existing_account(existing, account_id):
    accounts = list((existing or {}).get('accounts', []))
    for account in accounts:
        if str(account.get('account_id', '')).strip() == account_id:
            return account
    return accounts[0] if len(accounts) == 1 else {}


def build_flex_account_snapshot(root, existing=None, observed_at=None):
    """Merge exact Flex NAV/cash fields into the existing account snapshot."""
    statements = [
        element for element in root.iter()
        if _tag(element).lower() == 'flexstatement'
    ]
    extracted = [_extract_statement(statement) for statement in statements]
    extracted = [
        item for item in extracted
        if item['ending_nav'] is not None
        or item['ending_cash'] is not None
        or item['nav_by_date']
        or item['cash_by_date']
    ]
    if not extracted:
        return None

    existing = dict(existing or {})
    accounts = []
    nav_points = list(existing.get('nav_history', []))
    cash_points = list(existing.get('cash_history', []))

    for item in extracted:
        previous = dict(
            _existing_account(existing, item['account_id']) or {}
        )
        base_currency = (
            item['base_currency']
            or str(previous.get('base_currency', '')).strip().upper()
        )
        if not base_currency:
            continue
        summary = dict(previous.get('summary', {}) or {})
        if item['ending_nav'] is not None:
            summary['NetLiquidation'] = round(item['ending_nav'], 2)
        if item['ending_cash'] is not None:
            summary['TotalCashValue'] = round(item['ending_cash'], 2)

        cash_by_currency = dict(previous.get('cash_by_currency', {}) or {})
        cash_by_currency.update({
            key: round(value, 2)
            for key, value in item['cash_by_currency'].items()
        })
        accounts.append({
            **previous,
            'account_id': item['account_id']
            or str(previous.get('account_id', '')).strip(),
            'label': 'IBKR',
            'source': 'IBKR Flex Web Service',
            'base_currency': base_currency,
            'summary': summary,
            'cash_by_currency': cash_by_currency,
        })
        nav_points.extend({
            'date': date_value,
            'nav': value,
            'currency': base_currency,
            'source': 'IBKR Flex Web Service',
        } for date_value, value in item['nav_by_date'].items())
        cash_points.extend({
            'date': date_value,
            'cash': value,
            'currency': base_currency,
            'source': 'IBKR Flex Web Service',
        } for date_value, value in item['cash_by_date'].items())

    if not accounts:
        return None

    timestamp = observed_at or datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()
    return {
        **existing,
        'fetched_at': timestamp,
        'source': 'IBKR Flex Web Service',
        'accounts': accounts,
        'nav_history': _history_points(nav_points, 'nav'),
        'cash_history': _history_points(cash_points, 'cash'),
    }


def load_existing_snapshot(
    output_file='tws_account.json',
    encrypted_output='tws_account.enc.json',
    password=None,
):
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as handle:
                payload = json.load(handle)
            if isinstance(payload, dict):
                return payload
        except (OSError, ValueError):
            pass

    account_password = (
        password
        or os.environ.get('TWS_ACCOUNT_PASSWORD', '')
        or os.environ.get('PORTFOLIO_PASSWORD', '')
    )
    if not account_password or not os.path.exists(encrypted_output):
        return {}
    try:
        import market_security
        with open(encrypted_output, 'r', encoding='utf-8') as handle:
            encrypted = json.load(handle)
        decrypted = market_security.decrypt_from_js(
            encrypted,
            account_password,
        )
        payload = json.loads(decrypted)
        return payload if isinstance(payload, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def persist_flex_account_snapshot(
    root,
    output_file='tws_account.json',
    encrypted_output='tws_account.enc.json',
    risk_output='tws_account_risk.json',
    password=None,
    observed_at=None,
):
    """Persist Flex history using the dashboard's existing encrypted schema."""
    existing = load_existing_snapshot(
        output_file=output_file,
        encrypted_output=encrypted_output,
        password=password,
    )
    snapshot = build_flex_account_snapshot(
        root,
        existing=existing,
        observed_at=observed_at,
    )
    if snapshot is None:
        return None

    import ibkr_web_api
    return ibkr_web_api.persist_account_snapshot(
        snapshot,
        output_file=output_file,
        encrypted_output=encrypted_output,
        risk_output=risk_output,
        password=password,
    )
