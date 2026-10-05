"""Stable position identity: an instrument may be held in several accounts."""
import hashlib
import json


def text(value):
    result = str(value).strip() if value is not None else ''
    return '' if result.lower() in {'nan', 'none', '<na>'} else result


def ownership(item):
    def field(name):
        return text(item.get(name)) or text(item.get(name.lower()))
    source = field('Order_Source') or field('Source')
    return {
        'Broker': field('Broker') or ('Tradeville' if source.lower().startswith('tradeville') else 'IBKR'),
        'Account': field('Account'),
        'Account_ID': field('Account_ID'),
    }


def position_key(item):
    owner = ownership(item)
    symbol = (text(item.get('Symbol')) or text(item.get('symbol'))).upper()
    account = owner['Account_ID'] or owner['Account']
    if not account and owner['Broker'].upper() == 'IBKR':
        return symbol  # Legacy IBKR snapshots have no account identifier.
    parts = [owner['Broker'].upper(), account, symbol]
    return 'POS_' + hashlib.sha256(json.dumps(parts).encode()).hexdigest()[:24].upper()


def account_label(item):
    owner = ownership(item)
    return ' · '.join(v for v in (owner['Broker'], owner['Account'] or owner['Account_ID']) if v)


def same_owner(position, order):
    left, right = ownership(position), ownership(order)
    if left['Broker'].upper() != right['Broker'].upper():
        return False
    if left['Account_ID'] and right['Account_ID']:
        return left['Account_ID'] == right['Account_ID']
    if left['Account'] and right['Account']:
        return left['Account'] == right['Account']
    return not (left['Account_ID'] or left['Account'] or right['Account_ID'] or right['Account'])
