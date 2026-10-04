"""Currency-safe volatility inputs for the dashboard (no network requests)."""

import math


def positive_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def volatility_payload(item):
    price = positive_number(item.get('Price_Native'))
    atr = positive_number(item.get('Finviz_ATR'))
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
    vol_w = positive_number(item.get('Vol_W'))
    vol_m = positive_number(item.get('Vol_M'))
    available = [v for v in (atr_pct, vol_w, vol_m) if v is not None]
    return {
        'Price_Native': price,
        'ATR_Val': round(atr, 4) if atr else None,
        'ATR_Pct': round(atr_pct, 4) if atr_pct else None,
        'ATR_Source': source,
        'Vol_W': vol_w,
        'Vol_M': vol_m,
        'Trail_Larg': round(max(available) * 3, 4) if available else 0,
    }
