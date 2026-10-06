"""Currency-safe volatility inputs for the dashboard (no network requests)."""

import math
from datetime import date


def positive_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def historical_ranges(bars):
    """Daily high/low range %, and its 5/21-session means (not Finviz data).

    Uses the latest bars as supplied, including a possibly in-progress session.
    Ratios are currency invariant. Never skip a bad bar to fill a window.
    """
    result = {'Vol_D': None, 'Vol_W': None, 'Vol_M': None, 'Vol_As_Of': None}
    if not isinstance(bars, list) or not bars:
        return result
    window = bars[-21:]
    dates = [bar.get('date') for bar in window if isinstance(bar, dict) and bar.get('date')]
    if dates:
        try:
            parsed = [date.fromisoformat(value) for value in dates]
        except (TypeError, ValueError):
            return result
        if any(left >= right for left, right in zip(parsed, parsed[1:])):
            return result
    ranges = []
    for bar in window:
        value = None
        if isinstance(bar, dict):
            high, low = (positive_number(bar.get(key)) for key in ('high', 'low'))
            if high and low and low <= high:
                ratio = (high - low) / low * 100
                if math.isfinite(ratio):
                    value = ratio
        ranges.append(value)
    for key, count in (('Vol_D', 1), ('Vol_W', 5), ('Vol_M', 21)):
        tail = ranges[-count:]
        if len(tail) == count and all(value is not None for value in tail):
            result[key] = round(sum(tail) / count, 4)
    if isinstance(window[-1], dict) and ranges[-1] is not None:
        result['Vol_As_Of'] = window[-1].get('date') or None
    return result


def volatility_payload(item):
    price = positive_number(item.get('Price_Native'))
    # Finviz covers US listings; never mix a foreign instrument with a US namesake.
    currency = item.get('Currency')
    use_finviz = not isinstance(currency, str) or currency in ('', 'USD')
    atr = positive_number(item.get('Finviz_ATR')) if use_finviz else None
    source = 'Finviz' if atr else None
    if atr is None:
        atr = positive_number(item.get('ATR_Native'))
        price_eur = (positive_number(item.get('Current_Price'))
                     or positive_number(item.get('Price')))
        native_per_eur = price / price_eur if price and price_eur else None
        if not native_per_eur and item.get('Currency') == 'EUR':
            native_per_eur = 1.0
        if atr is None and native_per_eur:
            # Legacy snapshots store ATR_14 and chart OHLC in EUR.
            atr_eur = positive_number(item.get('ATR_14'))
            if atr_eur is None:
                bars = item.get('Chart_OHLC')
                if isinstance(bars, list) and len(bars) >= 15:
                    window = bars[-15:]
                    ranges = []
                    for previous, bar in zip(window, window[1:]):
                        if not isinstance(previous, dict) or not isinstance(bar, dict):
                            break
                        high = positive_number(bar.get('high'))
                        low = positive_number(bar.get('low'))
                        close = positive_number(previous.get('close'))
                        if not all((high, low, close)) or high < low:
                            break
                        ranges.append(max(high - low, abs(high - close), abs(low - close)))
                    if len(ranges) == 14:
                        atr_eur = positive_number(sum(ranges) / 14)
            if atr_eur:
                atr = positive_number(atr_eur * native_per_eur)
        source = 'Istoric prețuri' if atr else None
    atr_pct = positive_number(atr / price * 100) if atr and price else None
    history = historical_ranges(item.get('Chart_OHLC'))
    provider = item.get('Market_Data_Source')
    history_source = 'Calculat OHLC' + (f' · {provider}' if isinstance(provider, str) and provider else '')
    sources = {'Vol_D_Source': history_source if history['Vol_D'] is not None else None}
    for key in ('Vol_W', 'Vol_M'):
        finviz = positive_number(item.get(key)) if use_finviz else None
        sources[key + '_Source'] = 'Finviz' if finviz is not None else (
            history_source if history[key] is not None else None)
        if finviz is not None:
            history[key] = finviz
    vol_w, vol_m = history['Vol_W'], history['Vol_M']
    available = [v for v in (atr_pct, vol_w, vol_m) if v is not None]
    return {
        'Price_Native': price,
        'ATR_Val': round(atr, 4) if atr else None,
        'ATR_Pct': round(atr_pct, 4) if atr_pct else None,
        'ATR_Source': source,
        **history,
        **sources,
        'Trail_Larg': round(max(available) * 3, 4) if available else 0,
    }
