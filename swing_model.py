"""Pure market regime / entry setup assessment. No orders or return forecasts.

The existing pullback timing is retained separately from research eligibility.
Continuation is an unvalidated research setup, never an execution permission.
96 hours is a data transport tolerance for weekends, not a trading parameter.
"""

from datetime import datetime, timezone
import math

MAX_DATA_AGE_HOURS = 96
REGIME_LABELS = {
    'FAVORABLE': 'FAVORABIL', 'SELECTIVE': 'SELECTIV',
    'DEFENSIVE': 'DEFENSIV', 'UNKNOWN': 'DATE INSUFICIENTE',
}


def _number(value, minimum=0, maximum=None, positive=False):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(result) or result < minimum or (positive and result <= 0):
        return None
    return result if maximum is None or result <= maximum else None


def _fresh(timestamp, now):
    if not timestamp:
        return False
    try:
        parsed = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        age = (now - parsed).total_seconds() / 3600
        return -1 <= age <= MAX_DATA_AGE_HOURS
    except (TypeError, ValueError, OverflowError):
        return False


def _now(value):
    result = value or datetime.now(timezone.utc)
    if isinstance(result, str):
        result = datetime.fromisoformat(result.replace('Z', '+00:00'))
    return result.replace(tzinfo=timezone.utc) if result.tzinfo is None else result


def _setup(status, reason):
    return {'status': status, 'reason': reason}


def _result(regime, pullback, continuation, verdict, issues, reason, *, incomplete=False):
    return {
        'schema': 'market-scanner.swing-regime.v1',
        'regime': regime, 'regime_label': REGIME_LABELS[regime],
        'research_allowed': regime in ('FAVORABLE', 'SELECTIVE'),
        'entry_status': pullback['status'],
        'entry_label': {'READY': 'SETUP PULLBACK CONFIRMAT', 'WAIT': 'AȘTEAPTĂ INTRAREA',
                        'UNKNOWN': 'DATE INSUFICIENTE'}[pullback['status']],
        'pullback': pullback, 'continuation': {**continuation, 'research_only': True},
        'legacy_verdict': verdict, 'reason': reason,
        'data_quality': {'status': 'UNKNOWN' if incomplete else 'PARTIAL' if issues else 'CURRENT',
                         'issues': issues, 'max_age_hours': MAX_DATA_AGE_HOURS},
        'validation_status': 'UNVALIDATED',
        'execution_permission': False,
        'instrument_rule': 'Regimul permite analiza, nu executarea. Fiecare acțiune necesită '
                           'trigger propriu, stop, risc/recompensă, lichiditate și cash verificate.',
    }


def evaluate_bvb(price, sma10, sma50, sma200, rsi, observed_at=None, now=None):
    now = _now(now)
    price, sma10, sma50, sma200 = [_number(v, positive=True) for v in (price, sma10, sma50, sma200)]
    rsi = _number(rsi, maximum=100)
    issues = []
    if any(v is None for v in (price, sma10, sma50, sma200)):
        issues.append('Lipsesc prețul sau mediile SMA10/50/200 valide.')
    if not _fresh(observed_at, now):
        issues.append('Cotația BVB este veche sau momentul observației lipsește.')
    if issues:
        unknown = _setup('UNKNOWN', 'Datele nu permit confirmarea regimului sau a intrării.')
        return _result('UNKNOWN', unknown, unknown, 'DATE INSUFICIENTE', issues,
                       unknown['reason'], incomplete=True)
    regime = 'DEFENSIVE' if price < sma200 else 'FAVORABLE' if price >= sma50 else 'SELECTIVE'
    if rsi is None:
        issues.append('RSI lipsește; nu confirmăm intrarea.')
        pullback = continuation = _setup('UNKNOWN', issues[-1])
        verdict = 'DATE INSUFICIENTE'
    else:
        ready = price >= sma200 and price >= sma10 and 45 <= rsi < 70
        pullback = _setup('READY' if ready else 'WAIT',
                         'Regula pullback: peste SMA200 și SMA10, RSI între 45 și 70 (exclusiv 70).')
        continuation = _setup('READY' if price >= max(sma200, sma50, sma10) and rsi >= 50 else 'WAIT',
                              'Candidat de continuare: peste SMA200/50/10 și RSI ≥50; '
                              'doar cercetare, fără confirmare automată de cumpărare.')
        verdict = ('CUMPĂRĂ' if ready else 'AȘTEAPTĂ CONFIRMAREA' if price >= sma200
                   else 'PRUDENȚĂ' if price < sma50 else 'NEUTRU')
    reason = ('Trendul major este deteriorat; protecția riscului are prioritate.' if regime == 'DEFENSIVE'
              else 'Trendul major permite analiza selectivă; timingul proxy-ului nu este trigger pentru toate acțiunile.')
    return _result(regime, pullback, continuation, verdict, issues, reason)


def evaluate_international(data, now=None):
    data = data if isinstance(data, dict) else {}
    now = _now(now)
    issues = []
    indices = []
    for prefix in ('SPX', 'NDX'):
        values = [_number(data.get(f'{prefix}_{key}'), positive=True)
                  for key in ('Price', 'SMA10', 'SMA50', 'SMA200')]
        indices.append(values)
        if any(v is None for v in values):
            issues.append(f'{prefix}: preț sau medii lipsă/invalide.')
        if not _fresh(data.get(f'{prefix}_Observed_At'), now):
            issues.append(f'{prefix}: data cotației lipsește sau este veche.')
    vix = _number(data.get('VIX_Current'), positive=True)
    breadth = _number(data.get('Breadth_Pct'), maximum=100)
    if vix is None or not _fresh(data.get('VIX_Observed_At'), now):
        issues.append('VIX lipsește sau este vechi.')
    breadth_observed = data.get('Breadth_Observed_At')
    if breadth is None or not _fresh(breadth_observed or data.get('Breadth_Fetched_At'), now):
        issues.append('Breadth lipsește sau datele disponibile sunt vechi.')
    if issues:
        unknown = _setup('UNKNOWN', 'Date insuficiente pentru filtrul de piață.')
        return _result('UNKNOWN', unknown, unknown, 'DATE INSUFICIENTE', issues,
                       unknown['reason'], incomplete=True)

    major = [p > s200 for p, s10, s50, s200 in indices]
    timing = all(p > s10 for p, s10, s50, s200 in indices)
    intermediate = all(p > s50 for p, s10, s50, s200 in indices)
    if not any(major) or vix > 30 or breadth < 30:
        regime = 'DEFENSIVE'
    else:
        regime = 'FAVORABLE' if all(major) and intermediate and breadth >= 50 else 'SELECTIVE'
    if not breadth_observed:
        issues.append('Breadth: moment de preluare disponibil, momentul observației nu este furnizat.')
    tide = data.get('Market_Tide')
    tide = tide if isinstance(tide, dict) else {}
    highs, lows = (_number(tide.get(key)) for key in ('NewHighs', 'NewLows'))
    tide_fresh = _fresh(tide.get('observed_at') or tide.get('fetched_at') or tide.get('_cached_at'), now)
    tide_known = tide_fresh and highs is not None and lows is not None
    internal_weakness = tide_known and lows > highs
    if not tide_known:
        issues.append('Market Tide lipsește, este incomplet sau vechi; nu confirmă intrarea.')
    elif not tide.get('observed_at'):
        issues.append('Market Tide este o captură Finviz, nu o confirmare la închiderea ședinței.')
    if regime == 'FAVORABLE' and (internal_weakness or not tide_known or issues):
        regime = 'SELECTIVE'

    fg, fg_avg = (_number(data.get(key), maximum=100) for key in ('FG_Score', 'FG_SMA5'))
    sentiment_known = fg is not None and fg_avg is not None and _fresh(data.get('FG_Observed_At'), now)
    if not sentiment_known:
        issues.append('Sentimentul sau media sa lipsesc ori sunt vechi; pullback neconfirmat.')
    if regime == 'DEFENSIVE':
        verdict = 'CASH' if not any(major) else 'WAIT (PANIC)' if vix > 30 else 'WAIT (FAKE RALLY)'
        pullback = _setup('WAIT', 'Filtrul defensiv are prioritate față de timing.')
    elif not all(major):
        verdict = 'AVOID TECH' if major[0] else 'TECH ONLY'
        pullback = _setup('WAIT', 'Indicii nu sunt aliniați pe trendul major.')
    elif internal_weakness:
        verdict = 'WAIT (INTERNAL ROT)'
        pullback = _setup('WAIT', 'Minimele noi depășesc maximele; regula pullback rămâne prudentă.')
    elif not sentiment_known or not tide_known:
        verdict = 'DATE INSUFICIENTE'
        pullback = _setup('UNKNOWN', 'Nu există toate confirmările pentru pullback.')
    else:
        ready = timing and fg < 50 and fg >= fg_avg
        verdict = 'BUY' if ready else 'WAIT' if fg >= 50 else 'WAIT DIP'
        pullback = _setup('READY' if ready else 'WAIT',
                         'Pullback: indici peste SMA10, Fear & Greed sub 50 dar ≥ media de 5 zile.')
    rsi_values = [_number(data.get(f'{prefix}_RSI'), maximum=100) for prefix in ('SPX', 'NDX')]
    continuation = _setup(
        'UNKNOWN' if any(v is None for v in rsi_values) else
        'READY' if regime != 'DEFENSIVE' and all(major) and intermediate and timing
        and all(v >= 50 for v in rsi_values) else 'WAIT',
        'Candidat de continuare: indici peste SMA200/50/10 și RSI ≥50; sentimentul '
        'neutru nu îl exclude. Doar cercetare, fără BUY automat.')
    return _result(regime, pullback, continuation, verdict, issues,
                   'Regimul controlează cercetarea și riscul; intrarea fiecărei acțiuni se verifică separat.')
