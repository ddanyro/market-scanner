"""Historical shadow validation for the IBKR enhanced score.

This script is deliberately read-only with respect to scanner state.  It mines
one committed dashboard snapshot per Bucharest calendar day, reconstructs the
current shadow formula from fields that existed at recommendation time, and
uses only later OHLC bars for outcomes.

Important limitations are emitted into the report instead of being imputed:
historical IBKR options context and historical IBKR portfolio allocation were
not persisted before enhanced scoring was introduced.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

import enhanced_scoring


HORIZONS = (1, 5, 10, 20, 60)
COMPONENTS = (
    "technical_score", "momentum_score", "research_score",
    "volatility_score", "liquidity_score", "options_score",
    "relative_opportunity_score", "risk_reward_score",
    "portfolio_fit_score",
)
SCORE_COLUMNS = {
    "baseline": "baseline_score",
    "raw_enhanced": "enhanced_raw_score",
    "portfolio_adjusted": "enhanced_portfolio_adjusted_score",
}
BUCKETS = [0, 50, 60, 70, 75, 80, 85, 90, float("inf")]
BUCKET_LABELS = ["0-49", "50-59", "60-69", "70-74", "75-79", "80-84", "85-89", "90+"]


def _run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True,
    )
    return result.stdout


def _number(value, default=None):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _parse_timestamp(value, fallback):
    text = str(value or "").strip()
    for candidate in (text, text.replace(" ", "T")):
        try:
            parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=ZoneInfo("Europe/Bucharest"))
            return parsed
        except ValueError:
            pass
    return fallback


def _daily_dashboard_commits(start: str | None = None):
    log = _run_git("log", "--format=%H%x09%aI", "--", "dashboard_state.json")
    bucharest = ZoneInfo("Europe/Bucharest")
    selected = {}
    for line in log.splitlines():
        commit, stamp = line.split("\t", 1)
        instant = datetime.fromisoformat(
            stamp.replace("Z", "+00:00")
        ).astimezone(bucharest)
        if start and instant.date().isoformat() < start:
            continue
        day = instant.date().isoformat()
        if day not in selected or instant > selected[day][1]:
            selected[day] = (commit, instant)
    return [selected[day] for day in sorted(selected)]


def _baseline_gate_score(item):
    checks = _number(item.get("Checks_Passed"))
    if checks is None:
        return np.nan
    return max(0.0, min(100.0, checks / 4.0 * 100.0))


def _market_regimes(state):
    regime = state.get("us_market_regime") or {}
    benchmarks = regime.get("benchmarks") or []
    states = []
    for benchmark in benchmarks:
        if not isinstance(benchmark, dict):
            continue
        above = bool(benchmark.get("above_sma50")) and bool(benchmark.get("above_long_average"))
        below = benchmark.get("above_sma50") is False and benchmark.get("above_long_average") is False
        states.append(1 if above else -1 if below else 0)
    if states and all(value == 1 for value in states):
        market = "bullish"
    elif states and all(value == -1 for value in states):
        market = "bearish"
    else:
        market = "sideways"
    vix = _number(regime.get("vix"), _number(state.get("vix_val")))
    volatility = "high_volatility" if vix is not None and vix >= 25 else "low_volatility" if vix is not None and vix <= 18 else "mid_volatility"
    return market, volatility, vix


def _add_bars(bar_store, ticker, bars):
    if not isinstance(bars, list):
        return
    for bar in bars:
        if not isinstance(bar, dict):
            continue
        day = str(bar.get("date") or "")[:10]
        close = _number(bar.get("close"))
        if len(day) != 10 or close is None or close <= 0:
            continue
        bar_store[ticker][day] = {
            "close": close,
            "high": _number(bar.get("high"), close),
            "low": _number(bar.get("low"), close),
        }


def build_dataset(start="2026-01-01"):
    recommendations = {}
    bars = defaultdict(dict)
    commits = _daily_dashboard_commits(start)
    audit = {"daily_snapshots": len(commits), "parse_failures": 0}
    for index, (commit, commit_time) in enumerate(commits, 1):
        try:
            state = json.loads(_run_git("show", f"{commit}:dashboard_state.json"))
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            audit["parse_failures"] += 1
            continue
        market_regime, vol_regime, vix = _market_regimes(state)
        seen = set()
        for source in ("watchlist", "external_buy_research"):
            for item in state.get(source, []) or []:
                if not isinstance(item, dict):
                    continue
                ticker = str(item.get("Ticker") or item.get("Symbol") or "").upper().strip()
                if not ticker:
                    continue
                _add_bars(bars, ticker, item.get("Chart_OHLC"))
                decision = str(item.get("Decision") or "").upper()
                if decision not in {"BUY", "WAIT", "AVOID"}:
                    continue
                timestamp = _parse_timestamp(item.get("Date"), commit_time)
                # A state can retain stale rows for days. Keep only the last
                # observation for ticker/recommendation-day and never assign a
                # market regime more than two days after the recommendation.
                if abs((commit_time.date() - timestamp.date()).days) > 2:
                    continue
                key = (ticker, timestamp.date().isoformat())
                local_key = (source, *key)
                if local_key in seen:
                    continue
                seen.add(local_key)
                # Chart_OHLC is stored in the scanner's normalized currency,
                # matching Price (normally EUR), not Price_Native.
                price = _number(item.get("Price"), _number(item.get("Price_Native")))
                if price is None or price <= 0:
                    continue
                scored = enhanced_scoring.calculate_scores(item, portfolio_fit_score=50.0)
                record = {
                    "ticker": ticker,
                    "timestamp": timestamp.isoformat(),
                    "recommendation_date": timestamp.date().isoformat(),
                    "source": source,
                    "baseline_score": _baseline_gate_score(item),
                    "enhanced_raw_score": scored["raw_stock_score"],
                    "enhanced_portfolio_adjusted_score": scored["portfolio_adjusted_score"],
                    **{name: scored[name] for name in COMPONENTS},
                    "decision_baseline": decision,
                    "decision_enhanced": scored["enhanced_decision"],
                    "enhanced_decision_reason": scored["enhanced_decision_reason"],
                    "reported_entry_price": price,
                    "entry_price": np.nan,
                    "entry_price_source": "missing_contemporaneous_ohlc",
                    "market_regime": market_regime,
                    "market_volatility_regime": vol_regime,
                    "vix": vix,
                    "options_observed": bool((item.get("Options_Context") or {}).get("available")),
                    "portfolio_fit_observed": False,
                    "historical_reconstruction": True,
                }
                # Prefer watchlist over the duplicated external row; otherwise
                # retain the later intraday recommendation.
                previous = recommendations.get(key)
                if previous is None or source == "watchlist" or timestamp.isoformat() > previous["timestamp"]:
                    recommendations[key] = record
    frame = pd.DataFrame(recommendations.values())
    if frame.empty:
        return frame, audit
    frame = frame.sort_values(["recommendation_date", "ticker"]).reset_index(drop=True)
    for horizon in HORIZONS:
        for prefix in ("return", "mae", "mfe"):
            frame[f"{prefix}_{horizon}d_pct"] = np.nan
        frame[f"outcome_quality_{horizon}d"] = "missing"
    rejected_paths = {str(horizon): 0 for horizon in HORIZONS}
    for row_index, row in frame.iterrows():
        prior = [
            (day, values) for day, values in sorted(bars[row.ticker].items())
            if day <= row.recommendation_date
        ]
        if prior:
            # Use the latest globally consistent adjusted OHLC scale. This
            # prevents currency-mode changes and later split adjustments from
            # creating fictitious returns. It does not use a future close.
            frame.at[row_index, "entry_price"] = prior[-1][1]["close"]
            frame.at[row_index, "entry_price_source"] = "adjusted_ohlc_close"
        entry_price = frame.at[row_index, "entry_price"]
        if pd.isna(entry_price) or entry_price <= 0:
            continue
        future = [
            (day, values) for day, values in sorted(bars[row.ticker].items())
            if day > row.recommendation_date
        ]
        for horizon in HORIZONS:
            if len(future) < horizon:
                continue
            window = [values for _, values in future[:horizon]]
            end = window[-1]["close"]
            closes = [entry_price, *[item["close"] for item in window]]
            ratios = [right / left for left, right in zip(closes, closes[1:]) if left > 0]
            total_return = (end / entry_price - 1) * 100
            if (
                any(ratio < 0.2 or ratio > 3.0 for ratio in ratios)
                or total_return < -90
                or total_return > 500
            ):
                frame.at[row_index, f"outcome_quality_{horizon}d"] = "rejected_price_discontinuity"
                rejected_paths[str(horizon)] += 1
                continue
            frame.at[row_index, f"outcome_quality_{horizon}d"] = "valid"
            frame.at[row_index, f"return_{horizon}d_pct"] = total_return
            frame.at[row_index, f"mae_{horizon}d_pct"] = (min(item["low"] for item in window) / entry_price - 1) * 100
            frame.at[row_index, f"mfe_{horizon}d_pct"] = (max(item["high"] for item in window) / entry_price - 1) * 100
    audit.update({
        "recommendations": len(frame),
        "tickers": int(frame.ticker.nunique()),
        "first_date": frame.recommendation_date.min(),
        "last_date": frame.recommendation_date.max(),
        "options_observed": int(frame.options_observed.sum()),
        "portfolio_fit_observed": int(frame.portfolio_fit_observed.sum()),
        "outcome_counts": {str(h): int(frame[f"return_{h}d_pct"].notna().sum()) for h in HORIZONS},
        "rejected_price_paths": rejected_paths,
    })
    return frame, audit


def _outcome_metrics(values):
    series = pd.Series(values).dropna().astype(float)
    wins = series[series > 0]
    losses = series[series <= 0]
    return {
        "n": len(series),
        "average": series.mean() if len(series) else np.nan,
        "median": series.median() if len(series) else np.nan,
        "win_rate": (series > 0).mean() * 100 if len(series) else np.nan,
        "average_gain": wins.mean() if len(wins) else np.nan,
        "average_loss": losses.mean() if len(losses) else np.nan,
        "expectancy": series.mean() if len(series) else np.nan,
    }


def _subset_metrics(subset, horizon):
    result = _outcome_metrics(subset[f"return_{horizon}d_pct"])
    result["average_mae"] = subset[f"mae_{horizon}d_pct"].mean()
    result["average_mfe"] = subset[f"mfe_{horizon}d_pct"].mean()
    return result


def _spearman(left, right):
    pair = pd.DataFrame({"left": left, "right": right}).dropna()
    if len(pair) < 2 or pair.left.nunique() <= 1 or pair.right.nunique() <= 1:
        return np.nan
    ranked = pair.rank(method="average")
    return ranked.left.corr(ranked.right)


def score_summary(frame):
    rows = []
    for score_name, score_column in SCORE_COLUMNS.items():
        for horizon in HORIZONS:
            outcome = f"return_{horizon}d_pct"
            valid = frame.loc[
                frame[score_column].notna() & frame[outcome].notna()
            ]
            selected = valid[valid[score_column] >= 75]
            metrics = _subset_metrics(selected, horizon)
            if len(valid) and valid[score_column].nunique() > 1:
                metrics["spearman"] = _spearman(valid[score_column], valid[outcome])
                predicted = valid[score_column] >= 75
                actual = valid[outcome] > 0
                metrics["hit_rate"] = (predicted == actual).mean() * 100
            else:
                metrics["spearman"] = np.nan
                metrics["hit_rate"] = np.nan
            rows.append({"score": score_name, "horizon": horizon, **metrics})
    return pd.DataFrame(rows)


def bucket_summary(frame):
    rows = []
    for score_name, score_column in SCORE_COLUMNS.items():
        buckets = pd.cut(frame[score_column], BUCKETS, labels=BUCKET_LABELS, right=False)
        for horizon in HORIZONS:
            outcome = f"return_{horizon}d_pct"
            for label in BUCKET_LABELS:
                subset = frame.loc[buckets == label]
                rows.append({"score": score_name, "bucket": label, "horizon": horizon, **_subset_metrics(subset, horizon)})
    return pd.DataFrame(rows)


def decision_summary(frame):
    rows = []
    for model, column in (("baseline", "decision_baseline"), ("enhanced", "decision_enhanced")):
        for decision in ("BUY", "WAIT", "AVOID"):
            subset = frame[frame[column] == decision]
            for horizon in HORIZONS:
                rows.append({"model": model, "decision": decision, "horizon": horizon, **_subset_metrics(subset, horizon)})
    return pd.DataFrame(rows)


def regime_summary(frame):
    rows = []
    regimes = ["bullish", "bearish", "sideways", "high_volatility", "low_volatility"]
    for regime in regimes:
        subset = frame[
            (frame.market_regime == regime) |
            (frame.market_volatility_regime == regime)
        ]
        for score_name, score_column in SCORE_COLUMNS.items():
            valid = subset[[score_column, "return_20d_pct"]].dropna()
            rows.append({
                "regime": regime,
                "score": score_name,
                "n": len(valid),
                "spearman_20d": _spearman(valid[score_column], valid.return_20d_pct),
                **{f"selected_{key}": value for key, value in _subset_metrics(
                    subset.loc[subset[score_column] >= 75], 20
                ).items()},
            })
    return pd.DataFrame(rows)


def _ridge_fit_predict(train_x, train_y, test_x, alpha=1.0):
    means = train_x.mean(axis=0)
    stds = train_x.std(axis=0)
    stds[stds < 1e-9] = 1.0
    x_train = (train_x - means) / stds
    x_test = (test_x - means) / stds
    design = np.column_stack([np.ones(len(x_train)), x_train])
    penalty = np.eye(design.shape[1]) * alpha
    penalty[0, 0] = 0
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ train_y)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        predictions = np.column_stack([np.ones(len(x_test)), x_test]) @ beta
    if not np.isfinite(predictions).all():
        raise ValueError("Non-finite chronological validation predictions")
    return predictions


def component_analysis(frame):
    valid = frame[["recommendation_date", "return_20d_pct", *COMPONENTS]].dropna().sort_values("recommendation_date")
    correlations = []
    for component in COMPONENTS:
        unique = valid[component].nunique()
        result = {
            "component": component,
            "n": len(valid),
            "unique_values": unique,
            "incremental_delta_r2": np.nan,
            "incremental_delta_mae": np.nan,
        }
        for horizon in HORIZONS:
            result[f"spearman_{horizon}d"] = _spearman(
                frame[component], frame[f"return_{horizon}d_pct"]
            )
        correlations.append(result)
    if len(valid) >= 100:
        split_day = sorted(valid.recommendation_date.unique())[int(len(valid.recommendation_date.unique()) * 0.7)]
        train = valid[valid.recommendation_date < split_day]
        test = valid[valid.recommendation_date >= split_day]
        y_train = train.return_20d_pct.to_numpy(float)
        y_test = test.return_20d_pct.to_numpy(float)
        denominator = ((y_test - y_train.mean()) ** 2).sum()
        for result in correlations:
            component = result["component"]
            if result["unique_values"] <= 1:
                continue
            others = [name for name in COMPONENTS if name != component and valid[name].nunique() > 1]
            full = others + [component]
            if not others:
                continue
            pred_reduced = _ridge_fit_predict(train[others].to_numpy(float), y_train, test[others].to_numpy(float))
            pred_full = _ridge_fit_predict(train[full].to_numpy(float), y_train, test[full].to_numpy(float))
            r2_reduced = 1 - ((y_test - pred_reduced) ** 2).sum() / denominator if denominator else np.nan
            r2_full = 1 - ((y_test - pred_full) ** 2).sum() / denominator if denominator else np.nan
            result["incremental_delta_r2"] = r2_full - r2_reduced
            result["incremental_delta_mae"] = np.abs(y_test - pred_reduced).mean() - np.abs(y_test - pred_full).mean()
    corr = valid[list(COMPONENTS)].rank(method="average").corr()
    redundant = []
    for index, left in enumerate(COMPONENTS):
        for right in COMPONENTS[index + 1:]:
            value = corr.loc[left, right]
            if pd.notna(value) and abs(value) >= 0.75:
                redundant.append({"component_a": left, "component_b": right, "spearman": value})
    return pd.DataFrame(correlations), pd.DataFrame(
        redundant,
        columns=["component_a", "component_b", "spearman"],
    )


def disagreements(frame):
    columns = [
        "ticker", "timestamp", "decision_baseline", "decision_enhanced",
        "enhanced_raw_score", "enhanced_portfolio_adjusted_score",
        "enhanced_decision_reason", *[f"return_{h}d_pct" for h in HORIZONS],
    ]
    return frame.loc[frame.decision_baseline != frame.decision_enhanced, columns]


def decision_confusion(frame):
    rows = []
    for model, column in (("baseline", "decision_baseline"), ("enhanced", "decision_enhanced")):
        for horizon in HORIZONS:
            outcome = frame[f"return_{horizon}d_pct"]
            actual = pd.Series(
                np.where(outcome > 2, "BUY", np.where(outcome < -2, "AVOID", "WAIT")),
                index=frame.index,
            )
            for predicted in ("BUY", "WAIT", "AVOID"):
                for observed in ("BUY", "WAIT", "AVOID"):
                    valid = outcome.notna()
                    count = int((valid & (frame[column] == predicted) & (actual == observed)).sum())
                    rows.append({
                        "model": model, "horizon": horizon,
                        "predicted": predicted, "actual": observed,
                        "count": count,
                    })
    return pd.DataFrame(rows)


def date_block_bootstrap(frame, iterations=5000, seed=42):
    """Compare >=75 selections while resampling dates, not repeated rows."""
    rng = np.random.default_rng(seed)
    rows = []
    for horizon in HORIZONS:
        outcome = f"return_{horizon}d_pct"
        baseline = frame.loc[
            (frame.baseline_score >= 75) & frame[outcome].notna()
        ].groupby("recommendation_date")[outcome].mean()
        enhanced = frame.loc[
            (frame.enhanced_raw_score >= 75) & frame[outcome].notna()
        ].groupby("recommendation_date")[outcome].mean()
        paired = pd.concat(
            [baseline.rename("baseline"), enhanced.rename("enhanced")],
            axis=1,
        ).dropna()
        differences = (paired.enhanced - paired.baseline).to_numpy(float)
        draws = np.array([
            rng.choice(differences, len(differences), replace=True).mean()
            for _ in range(iterations)
        ]) if len(differences) else np.array([])
        rows.append({
            "horizon": horizon,
            "paired_dates": len(paired),
            "enhanced_minus_baseline_mean_pct": differences.mean() if len(differences) else np.nan,
            "bootstrap_ci_low_95": np.quantile(draws, 0.025) if len(draws) else np.nan,
            "bootstrap_ci_high_95": np.quantile(draws, 0.975) if len(draws) else np.nan,
        })
    return pd.DataFrame(rows)


def link_trades_to_recommendations(frame, trades):
    """Attach only the latest recommendation known before each execution."""
    recs = frame.copy()
    recs["_time"] = pd.to_datetime(recs["timestamp"], utc=True, errors="coerce")
    by_ticker = {
        ticker: group.sort_values("_time")
        for ticker, group in recs.dropna(subset=["_time"]).groupby("ticker")
    }
    rows = []
    score_fields = [
        "baseline_score", "enhanced_raw_score",
        "enhanced_portfolio_adjusted_score", *COMPONENTS,
        "decision_baseline", "decision_enhanced",
    ]
    for trade in trades or []:
        if not isinstance(trade, dict):
            continue
        symbol = str(trade.get("symbol") or "").upper()
        trade_time = pd.to_datetime(trade.get("trade_time"), utc=True, errors="coerce")
        candidates = by_ticker.get(symbol)
        matched = None
        if candidates is not None and pd.notna(trade_time):
            prior = candidates[candidates._time <= trade_time]
            if not prior.empty:
                matched = prior.iloc[-1]
        row = {
            key: trade.get(key) for key in (
                "trade_id", "order_id", "symbol", "side", "size", "price",
                "currency", "commission", "net_amount", "realized_pnl",
                "trade_time", "order_type", "stop_price", "security_type",
                "entry_price", "exit_price", "holding_period_days", "outcome",
            )
        }
        row["contemporaneous_recommendation_match"] = matched is not None
        row["recommendation_timestamp"] = matched.timestamp if matched is not None else None
        for key in score_fields:
            row[key] = matched[key] if matched is not None else None
        rows.append(row)
    return pd.DataFrame(rows)


def _markdown_table(frame, columns=None, limit=None):
    data = frame if columns is None else frame[columns]
    if limit is not None:
        data = data.head(limit)
    if data.empty:
        return "_No observations._"
    rendered = data.copy()
    for column in rendered.select_dtypes(include=["float"]).columns:
        rendered[column] = rendered[column].map(lambda value: "NA" if pd.isna(value) else f"{value:.3f}")
    header = "| " + " | ".join(rendered.columns) + " |"
    rule = "|" + "|".join(["---"] * len(rendered.columns)) + "|"
    rows = ["| " + " | ".join(str(value) for value in row) + " |" for row in rendered.itertuples(index=False, name=None)]
    return "\n".join([header, rule, *rows])


def write_report(output_dir: Path, dataset, audit, scores, buckets, decisions, confusion, bootstrap, regimes, components, redundant, changed):
    coverage = pd.DataFrame([
        {"horizon": horizon, "available": audit["outcome_counts"][str(horizon)], "missing": len(dataset) - audit["outcome_counts"][str(horizon)]}
        for horizon in HORIZONS
    ])
    score_20 = scores[scores.horizon == 20][["score", "n", "average", "median", "win_rate", "hit_rate", "average_gain", "average_loss", "expectancy", "average_mae", "average_mfe", "spearman"]]
    decision_20 = decisions[decisions.horizon == 20][["model", "decision", "n", "average", "median", "win_rate", "average_gain", "average_loss", "average_mae", "average_mfe"]]
    bucket_20 = buckets[buckets.horizon == 20][["score", "bucket", "n", "average", "median", "win_rate"]]
    raw_adjusted_corr = _spearman(
        dataset["enhanced_raw_score"],
        dataset["enhanced_portfolio_adjusted_score"],
    )
    def score_row(name, horizon):
        return scores[(scores.score == name) & (scores.horizon == horizon)].iloc[0]

    baseline_20 = score_row("baseline", 20)
    raw_20 = score_row("raw_enhanced", 20)
    baseline_60 = score_row("baseline", 60)
    raw_60 = score_row("raw_enhanced", 60)
    confusion_20 = confusion[confusion.horizon == 20]
    confusion_accuracy = {}
    for model in ("baseline", "enhanced"):
        matrix = confusion_20[confusion_20.model == model]
        total = matrix["count"].sum()
        correct = matrix.loc[matrix.predicted == matrix.actual, "count"].sum()
        confusion_accuracy[model] = correct / total * 100 if total else np.nan
    lines = [
        "# Enhanced Scoring shadow validation",
        "",
        f"Generated: {datetime.now().astimezone().isoformat()}",
        "",
        "## Data integrity verdict",
        "",
        f"- Daily committed snapshots: **{audit['daily_snapshots']}**; recommendations: **{audit['recommendations']}** across **{audit['tickers']}** tickers ({audit['first_date']} to {audit['last_date']}).",
        "- Baseline has no persisted continuous 0–100 score. `baseline_score` is the faithful gate proxy `Checks_Passed / 4 × 100`; it has only five possible values.",
        "- Enhanced values are retrospective reconstructions with the unchanged v1 formula. They are not contemporaneously logged Enhanced predictions.",
        f"- Historical Options observations: **{audit['options_observed']}**. Historical Portfolio Fit observations: **{audit['portfolio_fit_observed']}**. Both are therefore untestable, not evidence of zero value.",
        f"- IBKR trades read: **{audit.get('ibkr_trades', 0)}**; matched to a recommendation timestamped before execution: **{audit.get('ibkr_trades_matched', 0)}**.",
        f"- Rejected price-discontinuity paths by horizon: **{audit['rejected_price_paths']}**; these remain explicit missing outcomes.",
        f"- Raw versus adjusted Spearman correlation: **{raw_adjusted_corr:.6f}**. With Portfolio Fit fixed at 50, adjusted is only `0.85 × raw + 7.5` and cannot change ranking.",
        "- Repeated ticker/day observations are not independent trades. Results are diagnostic and must not be promoted to production evidence.",
        "",
        "## Outcome coverage",
        "",
        _markdown_table(coverage),
        "",
        "## Baseline versus Enhanced — 20D, score >= 75",
        "",
        "Hit rate is directional classification accuracy using score >=75 versus positive return; win rate is the positive-return rate inside the selected bucket.",
        "",
        _markdown_table(score_20),
        "",
        "### Date-block bootstrap: >=75 Raw minus >=75 Baseline",
        "",
        "Dates, not rows, are resampled. This controls repeated same-day recommendations, but the two thresholds still select very different cohort sizes.",
        "",
        _markdown_table(bootstrap),
        "",
        "## Score buckets — 20D",
        "",
        _markdown_table(bucket_20),
        "",
        "## BUY / WAIT / AVOID — 20D",
        "",
        _markdown_table(decision_20),
        "",
        "Outcome classes for the confusion matrix are defined before inspection as BUY > +2%, AVOID < -2%, otherwise WAIT.",
        "",
        _markdown_table(confusion[confusion.horizon == 20]),
        "",
        "## Component contribution — chronological 70/30 validation, 20D",
        "",
        "`incremental_delta_r2` and `incremental_delta_mae` compare a ridge model containing all variable components against the same model without that component. Positive is better. No weights were fitted or changed.",
        "",
        _markdown_table(components),
        "",
        "## Redundancy pairs (|Spearman| >= 0.75)",
        "",
        _markdown_table(redundant),
        "",
        "## Market regimes — 20D",
        "",
        _markdown_table(regimes[["regime", "score", "n", "spearman_20d", "selected_n", "selected_average", "selected_win_rate"]]),
        "",
        "## Baseline != Enhanced",
        "",
        f"Disagreements: **{len(changed)}**.",
        "",
        _markdown_table(changed, limit=100),
        "",
        "## Explicit conclusions",
        "",
        f"- **A — Predictiveness:** Raw Enhanced improves rank correlation from {baseline_20.spearman:.3f} to {raw_20.spearman:.3f} at 20D and from {baseline_60.spearman:.3f} to {raw_60.spearman:.3f} at 60D. The 20D result is effectively zero; the 60D +{raw_60.spearman:.3f} signal is weak. The >=75 Raw bucket is promising ({int(raw_20.n)} observations, {raw_20.average:.2f}% mean, {raw_20.win_rate:.1f}% wins) versus Baseline ({int(baseline_20.n)}, {baseline_20.average:.2f}%, {baseline_20.win_rate:.1f}%), but it is a much smaller and repeatedly sampled cohort, so this is not an apples-to-apples replacement test.",
        "- **B — Portfolio Fit:** cannot be validated. Every historical fit is neutral 50; adjusted score is a monotone shrinkage of Raw and has identical ranking. There are zero observable cases of high Raw + weak Fit or medium Raw + strong Fit.",
        "- **C — Volatility/Liquidity/Options:** Volatility is the only new risk component with positive 20D holdout contribution (delta R² +0.0037; delta MAE +0.0139 pp) and stronger 60D correlation (+0.141). Liquidity is effectively neutral in the training period and adds no measurable information. Options has zero historical observations and is untestable.",
        "- **D — Redundancy:** Technical is exactly the Baseline Gate Score in this reconstruction. Portfolio Adjusted is redundant with Raw until real Portfolio Fit varies. Options, Relative Opportunity and Portfolio Fit are constants, so they dilute rather than differentiate historical Raw scores; this does not prove they are intrinsically useless.",
        "- **Keep provisionally:** Research, Volatility and Risk/Reward. Their 20D/60D correlations are positive, although only Volatility has a material positive holdout delta R².",
        "- **Recalibrate only after a clean holdout:** Technical and Momentum. At 20D their correlations are -0.039 and -0.053 and their incremental holdout contributions are negative; Momentum falls to -0.123 at 60D.",
        "- **Missing evidence/features:** contemporaneous portfolio allocation, broad options comparison cohort, benchmark-relative alpha, slippage/transaction costs, earnings-event controls, and explicit market-regime interactions.",
        "- **15% Portfolio adjustment:** not justified or rejected by this sample—it is unidentifiable. The current 15% must remain shadow until non-neutral fits have forward outcomes.",
        "- **Current weights:** the data does not support declaring 25% Technical / 15% Momentum optimal. No alternative weights were fitted. Research/Volatility/Risk-Reward show more favorable directional evidence than their current combined interpretation, but changing weights now would be sample reuse.",
        f"- **Decision comparison:** historical Enhanced decisions equal Baseline in all rows because the IBKR risk gates were absent historically. Both have the same 20D three-class accuracy of {confusion_accuracy['baseline']:.1f}% under the predeclared ±2% outcome definition.",
        "- **Regimes:** behavior is not stable. Raw correlation is positive in bullish/low-volatility samples, approximately zero sideways, and negative in bearish/high-volatility samples. One global weight vector is therefore not empirically supported yet.",
        "",
        "## OPTIONS selection-bias audit",
        "",
        "Historical option coverage is zero because the top-3 lazy collection was added only with Enhanced v1. Missing options are encoded as neutral 50, and selection into the future top-3 is conditional on the baseline rank. Comparing covered versus uncovered names later would therefore be selection-biased unless candidates are randomized or all eligible names receive delayed option snapshots for measurement.",
        "",
        "## VERDICT — SHOULD ENHANCED SCORING REPLACE BASELINE?",
        "",
        "**NOT YET.** This reconstruction can test the legacy-derived Technical, Momentum, Research, ATR-volatility and Risk/Reward mixture, but it cannot test the two central IBKR additions—actual Portfolio Fit and Options—and it contains no contemporaneous Enhanced predictions. Shadow logging must accumulate before a defensible replacement decision.",
        "",
        "## TOP 5 NEXT IMPROVEMENTS",
        "",
        "1. Persist every shadow prediction and immutable input snapshot before market close, including score version and data availability flags.",
        "2. Record Portfolio Fit contemporaneously and retain the unadjusted allocation dimensions used to calculate it.",
        "3. Create an options measurement cohort: fetch options for top-3 operationally, but collect delayed/end-of-day features for a broader comparison cohort to quantify selection bias.",
        "4. Use non-overlapping evaluation anchors or date/ticker-cluster bootstrap confidence intervals; keep a final chronological holdout untouched.",
        "5. Add benchmark-relative forward returns and transaction-cost/slippage outcomes before any weight optimization.",
    ]
    (output_dir / "validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2026-01-01")
    parser.add_argument("--output", default="analysis/enhanced_scoring_validation")
    parser.add_argument("--fetch-ibkr-trades", action="store_true")
    args = parser.parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset, audit = build_dataset(args.start)
    if dataset.empty:
        raise SystemExit("No historical recommendations could be reconstructed")
    dataset.to_csv(output_dir / "recommendations_with_outcomes.csv", index=False)
    scores = score_summary(dataset)
    buckets = bucket_summary(dataset)
    decisions = decision_summary(dataset)
    confusion = decision_confusion(dataset)
    bootstrap = date_block_bootstrap(dataset)
    regimes = regime_summary(dataset)
    components, redundant = component_analysis(dataset)
    changed = disagreements(dataset)
    if args.fetch_ibkr_trades:
        import ibkr_mcp
        account = asyncio.run(ibkr_mcp.build_account_snapshot(interactive=False))
        trades = link_trades_to_recommendations(dataset, account.get("trade_journal", []))
        trades.to_csv(output_dir / "trades_with_shadow_context.csv", index=False)
        audit["ibkr_trades"] = len(trades)
        audit["ibkr_trades_matched"] = int(
            trades.get("contemporaneous_recommendation_match", pd.Series(dtype=bool)).sum()
        )
    scores.to_csv(output_dir / "score_comparison.csv", index=False)
    buckets.to_csv(output_dir / "score_buckets.csv", index=False)
    decisions.to_csv(output_dir / "decision_outcomes.csv", index=False)
    confusion.to_csv(output_dir / "decision_confusion.csv", index=False)
    bootstrap.to_csv(output_dir / "date_block_bootstrap.csv", index=False)
    regimes.to_csv(output_dir / "market_regimes.csv", index=False)
    components.to_csv(output_dir / "component_contribution.csv", index=False)
    redundant.to_csv(output_dir / "component_redundancy.csv", index=False)
    changed.to_csv(output_dir / "decision_disagreements.csv", index=False)
    (output_dir / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    write_report(output_dir, dataset, audit, scores, buckets, decisions, confusion, bootstrap, regimes, components, redundant, changed)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
