#!/usr/bin/env python3
"""Replay local BVB closes; report signal frequency, not strategy performance."""

import argparse
from collections import Counter
from datetime import datetime, time, timezone
import json
import math
from pathlib import Path
import statistics
import sys


# The command reads local data and emits JSON only, including when run directly.
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
WARMUP = 200
HORIZONS = (5, 10, 20)


def normalize_series(dates, closes):
    """Reject ambiguous ordering/alignment instead of inventing trading sessions."""
    if not isinstance(dates, list) or not isinstance(closes, list):
        raise ValueError('dates and closes must both be lists')
    if len(dates) != len(closes):
        raise ValueError('dates and closes must have identical lengths')
    if len(closes) < WARMUP:
        raise ValueError('at least 200 dated closes are required')
    normalized_dates = []
    normalized_closes = []
    previous = None
    for date_value, close in zip(dates, closes):
        try:
            date = datetime.strptime(str(date_value), '%Y-%m-%d').date()
        except ValueError as error:
            raise ValueError('session dates must use YYYY-MM-DD') from error
        if previous is not None and date <= previous:
            raise ValueError('session dates must be unique and strictly increasing')
        if isinstance(close, bool):
            raise ValueError('closes must be finite positive numbers')
        try:
            close = float(close)
        except (TypeError, ValueError) as error:
            raise ValueError('closes must be finite positive numbers') from error
        if not math.isfinite(close) or close <= 0:
            raise ValueError('closes must be finite positive numbers')
        normalized_dates.append(date.isoformat())
        normalized_closes.append(close)
        previous = date
    return normalized_dates, normalized_closes


def load_local_series(path):
    """Accept a dashboard snapshot, a proxy row, or explicit dates/closes JSON."""
    with Path(path).open(encoding='utf-8') as source:
        data = json.load(source)
    if not isinstance(data, dict):
        raise ValueError('input must be a JSON object')
    row = data.get('bvb_proxy', data)
    if not isinstance(row, dict):
        raise ValueError('bvb_proxy must be a JSON object')
    return normalize_series(
        row.get('Chart_Dates', row.get('dates')),
        row.get('Chart_History', row.get('closes')),
    )


def sequential_snapshots(dates, closes):
    """Match calculate_rsi: Wilder EWM alpha=1/14, adjust=False, first delta=0."""
    average_gain = 0.0
    average_loss = 0.0
    alpha = 1.0 / 14
    for index, price in enumerate(closes):
        delta = price - closes[index - 1] if index else 0.0
        average_gain = (1 - alpha) * average_gain + alpha * max(delta, 0.0)
        average_loss = (1 - alpha) * average_loss + alpha * max(-delta, 0.0)
        if index + 1 < WARMUP:
            continue
        if average_loss > 0:
            rsi = 100 - 100 / (1 + average_gain / average_loss)
        else:
            rsi = 100.0 if average_gain > 0 else None
        yield {
            'index': index,
            'date': dates[index],
            'price': price,
            'sma10': statistics.fmean(closes[index - 9:index + 1]),
            'sma50': statistics.fmean(closes[index - 49:index + 1]),
            'sma200': statistics.fmean(closes[index - 199:index + 1]),
            'rsi': rsi,
        }


def legacy_bvb_buy(snapshot):
    """Freeze the original BVB entry rule, including its missing-RSI behavior."""
    return (
        snapshot['price'] >= snapshot['sma200']
        and snapshot['price'] >= snapshot['sma10']
        and (snapshot['rsi'] is None or 45 <= snapshot['rsi'] < 70)
    )


def forward_return_summary(closes, indices, horizon, roundtrip_cost_bps):
    """Forward close returns are labels, never inputs to a signal decision."""
    outcomes = [
        (closes[index + horizon] / closes[index] - 1) * 100
        for index in indices if index + horizon < len(closes)
    ]
    cost_percentage_points = roundtrip_cost_bps / 100.0
    return {
        'horizon_sessions': horizon,
        'available_outcomes': len(outcomes),
        'missing_future_outcomes': len(indices) - len(outcomes),
        'mean_proxy_close_return_pct': (
            round(statistics.fmean(outcomes), 6) if outcomes else None
        ),
        'median_proxy_close_return_pct': (
            round(statistics.median(outcomes), 6) if outcomes else None
        ),
        'mean_less_hypothetical_roundtrip_cost_pct': (
            round(statistics.fmean(outcomes) - cost_percentage_points, 6)
            if outcomes else None
        ),
    }


def replay_series(dates, closes, roundtrip_cost_bps, evaluator=None):
    dates, closes = normalize_series(dates, closes)
    if isinstance(roundtrip_cost_bps, bool):
        raise ValueError('roundtrip cost must be finite and non-negative')
    try:
        roundtrip_cost_bps = float(roundtrip_cost_bps)
    except (TypeError, ValueError) as error:
        raise ValueError('roundtrip cost must be finite and non-negative') from error
    if not math.isfinite(roundtrip_cost_bps) or roundtrip_cost_bps < 0:
        raise ValueError('roundtrip cost must be finite and non-negative')
    if evaluator is None:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from swing_model import evaluate_bvb
        evaluator = evaluate_bvb

    indices = {
        'legacy_buy': [],
        'regime_research_eligible': [],
        'continuation_research_only': [],
    }
    regime_counts = Counter()
    entry_counts = Counter()
    pullback_counts = Counter()
    continuation_counts = Counter()
    legacy_verdict_counts = Counter()
    for snapshot in sequential_snapshots(dates, closes):
        # Historical availability assumption: evaluate at this session's date,
        # not today's clock. This does not prove point-in-time data availability.
        session_time = datetime.combine(
            datetime.strptime(snapshot['date'], '%Y-%m-%d').date(),
            time(0), tzinfo=timezone.utc,
        )
        result = evaluator(
            price=snapshot['price'], sma10=snapshot['sma10'],
            sma50=snapshot['sma50'], sma200=snapshot['sma200'],
            rsi=snapshot['rsi'], observed_at=session_time.isoformat(),
            now=session_time,
        )
        regime_counts[result.get('regime', 'UNKNOWN')] += 1
        entry_counts[result.get('entry_status', 'UNKNOWN')] += 1
        pullback = (result.get('pullback') or {}).get('status', 'UNKNOWN')
        continuation = (result.get('continuation') or {}).get('status', 'UNKNOWN')
        pullback_counts[pullback] += 1
        continuation_counts[continuation] += 1
        legacy_verdict_counts[result.get('legacy_verdict', 'UNKNOWN')] += 1
        if legacy_bvb_buy(snapshot):
            indices['legacy_buy'].append(snapshot['index'])
        if result.get('research_allowed') is True:
            indices['regime_research_eligible'].append(snapshot['index'])
        if continuation == 'READY':
            indices['continuation_research_only'].append(snapshot['index'])

    evaluated = len(closes) - WARMUP + 1
    descriptions = {
        'legacy_buy': 'Original BVB proxy BUY rule; not an executed trade.',
        'regime_research_eligible': 'Candidate research allowed; not entry permission.',
        'continuation_research_only': 'Continuation READY in research mode; not promoted to live entry.',
    }
    cohorts = {}
    for name, selected in indices.items():
        cohorts[name] = {
            'description': descriptions[name],
            'sessions': len(selected),
            'frequency_pct': round(len(selected) / evaluated * 100, 4),
            'forward_returns': {
                str(horizon): forward_return_summary(
                    closes, selected, horizon, roundtrip_cost_bps,
                ) for horizon in HORIZONS
            },
        }
    return {
        'schema_version': 1,
        'scope': 'BVB / TVBETETF proxy; classification replay only',
        'observations': len(closes),
        'warmup_observations': WARMUP,
        'evaluated_sessions': evaluated,
        'evaluation_start': dates[WARMUP - 1],
        'evaluation_end': dates[-1],
        'roundtrip_cost_bps': roundtrip_cost_bps,
        'regime_counts': dict(regime_counts),
        'entry_status_counts': dict(entry_counts),
        'pullback_status_counts': dict(pullback_counts),
        'continuation_status_counts': dict(continuation_counts),
        'new_evaluator_legacy_verdict_counts': dict(legacy_verdict_counts),
        'cohorts': cohorts,
        'limitations': [
            'Reconstructed from current cached closes, not recorded historical verdicts or audited point-in-time data.',
            'Indicators use only the current and preceding closes; future closes are outcome labels only.',
            'Each historical snapshot assumes its session data was contemporaneously available.',
            'Forward return windows overlap, and cohorts overlap; observations are not independent trades.',
            'Horizons count supplied observations; completeness against the exchange calendar is not verified.',
            'Missing future outcomes are excluded and counted separately for every cohort and horizon.',
            'Returns describe the TVBETETF proxy, not individual BVB stocks or a full-market index.',
            'The cost adjustment subtracts one user-specified hypothetical roundtrip cost; no execution model is simulated.',
            'No trade PnL, win rate, exposure, drawdown, or validated investment performance is computed.',
            'Full US replay is unavailable without point-in-time daily sentiment and breadth history.',
            'Continuation remains research-only pending frozen-parameter out-of-sample trade validation.',
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--input', type=Path, default=ROOT / 'dashboard_state.json',
        help='Local JSON dashboard snapshot, proxy row, or dates/closes object.',
    )
    parser.add_argument(
        '--roundtrip-cost-bps', required=True, type=float,
        help='Explicit hypothetical roundtrip cost; use 0 for no cost adjustment.',
    )
    args = parser.parse_args(argv)
    try:
        dates, closes = load_local_series(args.input)
        report = replay_series(dates, closes, args.roundtrip_cost_bps)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2, allow_nan=False)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
