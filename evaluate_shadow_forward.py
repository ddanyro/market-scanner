"""Forward-only evaluator for the immutable Enhanced shadow ledger.

Outcomes may be added after a horizon matures, but signal-time prices,
features, portfolio exposure, option availability, weights and thresholds are
never reconstructed or changed.  Calibration and locked holdout are always
reported separately.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

import shadow_validation


HORIZONS = (1, 5, 10, 20, 60)
BUCKETS = [0, 50, 60, 70, 75, 80, 85, 90, float("inf")]
BUCKET_LABELS = ["0-49", "50-59", "60-69", "70-74", "75-79", "80-84", "85-89", "90+"]
OUTPUT_DIR = Path("analysis/shadow_forward_validation")


def _number(value, default=None):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def flatten_ledger(snapshots):
    rows = []
    for snapshot in snapshots:
        for prediction in snapshot.get("predictions", []):
            row = {
                "snapshot_id": snapshot.get("snapshot_id"),
                "recorded_at": snapshot.get("recorded_at"),
                "sample_partition": snapshot.get("sample_partition"),
                "policy_hash": snapshot.get("policy_hash"),
                "symbol": prediction.get("symbol"),
                "market": prediction.get("market"),
                "sector": prediction.get("sector"),
                "baseline_score": prediction.get("baseline_score"),
                "raw_score": prediction.get("raw_score"),
                "portfolio_fit": prediction.get("portfolio_fit_observed"),
                "adjusted_score": prediction.get("adjusted_score_observed_fit"),
                "baseline_decision": prediction.get("baseline_decision"),
                "enhanced_decision": prediction.get("enhanced_decision_shadow"),
                "entry_price": prediction.get("entry", {}).get("price"),
                "entry_source": prediction.get("entry", {}).get("source"),
                "execution_eligible": prediction.get("entry", {}).get("fresh_for_execution"),
                "data_age_hours": prediction.get("entry", {}).get("data_age_hours"),
                "currency": prediction.get("entry", {}).get("currency"),
                "options_available": prediction.get("options", {}).get("data_available"),
                "options_cohort": prediction.get("options", {}).get("cohort"),
                "portfolio_fit_available": prediction.get("portfolio", {}).get("available"),
                "market_regime": snapshot.get("market_regime", {}).get("market_stage"),
                "vix": snapshot.get("market_regime", {}).get("vix"),
                "hypothetical_units": prediction.get("portfolio", {}).get("hypothetical_units"),
                "sector_etf": prediction.get("benchmarks", {}).get("sector", {}).get("ticker"),
                "cash_yield_pct": prediction.get("benchmarks", {}).get("cash", {}).get("annual_yield_pct"),
                "costs": prediction.get("costs") or {},
                "benchmarks": prediction.get("benchmarks") or {},
            }
            components = prediction.get("components") or {}
            for component in shadow_validation.COMPONENTS:
                row[component] = components.get(component)
            rows.append(row)
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame["signal_day"] = pd.to_datetime(
            frame.recorded_at, utc=True
        ).dt.tz_convert(None).dt.normalize()
        # Legacy rows recorded before quote-freshness was added remain valid
        # immutable observations, but cannot be treated as executable signals.
        frame["execution_eligible"] = frame["execution_eligible"].fillna(False).astype(bool)
        frame["options_available"] = frame["options_available"].fillna(False).astype(bool)
        frame["portfolio_fit_available"] = frame["portfolio_fit_available"].fillna(False).astype(bool)
    return frame


def _download_history(ticker, start, end, ticker_factory=yf.Ticker):
    history = ticker_factory(ticker).history(
        start=start, end=end, interval="1d", auto_adjust=False, actions=False
    )
    if history is None or history.empty or "Close" not in history:
        return pd.DataFrame()
    frame = history.copy()
    frame.index = pd.to_datetime(frame.index, utc=True).tz_convert(None).normalize()
    adjusted = frame.get("Adj Close", frame["Close"]).astype(float)
    adjustment_factor = adjusted / frame["Close"].astype(float)
    frame = pd.DataFrame({
        "close": frame["Close"].astype(float),
        "adjusted": adjusted,
        "high": frame.get("High", frame["Close"]).astype(float) * adjustment_factor,
        "low": frame.get("Low", frame["Close"]).astype(float) * adjustment_factor,
    }).dropna(subset=["close", "adjusted"])
    return frame[~frame.index.duplicated(keep="last")].sort_index()


def _adjusted_entry(stored_entry, signal_day, history):
    prior = history[history.index <= signal_day]
    if prior.empty or stored_entry is None or stored_entry <= 0:
        return None
    reference = prior.iloc[-1]
    if reference["close"] <= 0:
        return None
    return stored_entry * reference["adjusted"] / reference["close"]


def _cost_pct(row):
    assumptions = row.costs if isinstance(row.costs, dict) else {}
    entry = _number(row.entry_price)
    units = _number(row.hypothetical_units)
    if not entry or entry <= 0 or not units or units <= 0:
        return None
    notional = entry * units
    commission = 2 * max(
        _number(assumptions.get("minimum_commission_per_order"), 1.0),
        units * _number(assumptions.get("commission_per_share"), 0.005),
    ) / notional * 100
    captured_spread = _number(assumptions.get("spread_pct_at_signal"), 0.0)
    # Entry at the captured ask already pays the entry-side spread relative
    # to the later close series. Charge only an estimated exit half-spread;
    # a last-price entry must pay both sides explicitly.
    spread = (
        captured_spread / 2
        if row.entry_source == "ask_at_signal" else captured_spread
    )
    slippage = 2 * _number(assumptions.get("slippage_bps_per_side"), 5.0) / 100
    fx = (
        _number(assumptions.get("round_trip_fx_conversions_assumed"), 0)
        * _number(assumptions.get("fx_bps_per_conversion"), 3.0) / 100
    )
    return commission + spread + slippage + fx


def _path_metrics(entry, future):
    returns = future.adjusted / entry - 1
    running_peak = future.adjusted.cummax()
    drawdowns = future.adjusted / running_peak - 1
    return {
        "gross_return_pct": returns.iloc[-1] * 100,
        "mae_pct": (future.low.min() / entry - 1) * 100,
        "mfe_pct": (future.high.max() / entry - 1) * 100,
        "path_max_drawdown_pct": drawdowns.min() * 100,
        "path_volatility_pct": returns.diff().std(ddof=1) * math.sqrt(252) * 100
        if len(returns) > 2 else None,
    }


def label_matured_predictions(frame, now=None, ticker_factory=yf.Ticker):
    if frame.empty:
        return frame
    now = now or dt.datetime.now(dt.timezone.utc)
    result = frame.copy()
    result["signal_day"] = pd.to_datetime(result.recorded_at, utc=True).dt.tz_convert(None).dt.normalize()
    start = (result.signal_day.min() - pd.Timedelta(days=10)).date().isoformat()
    end = (pd.Timestamp(now).tz_convert(None) + pd.Timedelta(days=2)).date().isoformat()
    needed = set(result.symbol.dropna().astype(str)) | {"SPY", "QQQ"}
    needed |= set(result.sector_etf.dropna().astype(str))
    histories = {}
    for ticker in sorted(needed):
        try:
            histories[ticker] = _download_history(ticker, start, end, ticker_factory)
        except Exception:
            histories[ticker] = pd.DataFrame()
    for horizon in HORIZONS:
        for column in (
            "gross_return_pct", "net_return_pct", "total_cost_pct", "mae_pct",
            "mfe_pct", "path_max_drawdown_pct", "path_volatility_pct",
            "spy_return_pct", "qqq_return_pct", "sector_return_pct",
            "cash_return_pct", "gross_alpha_spy_pct", "net_alpha_spy_pct",
            "gross_alpha_qqq_pct", "net_alpha_qqq_pct",
            "gross_alpha_sector_pct", "net_alpha_sector_pct",
            "gross_alpha_cash_pct", "net_alpha_cash_pct",
        ):
            result[f"{column}_{horizon}d"] = np.nan
        result[f"outcome_status_{horizon}d"] = "pending"
    for index, row in result.iterrows():
        history = histories.get(str(row.symbol), pd.DataFrame())
        if history.empty:
            for horizon in HORIZONS:
                result.at[index, f"outcome_status_{horizon}d"] = "missing_history"
            continue
        entry = _adjusted_entry(_number(row.entry_price), row.signal_day, history)
        future = history[history.index > row.signal_day]
        for horizon in HORIZONS:
            if entry is None:
                result.at[index, f"outcome_status_{horizon}d"] = "missing_entry"
                continue
            if len(future) < horizon:
                continue
            window = future.iloc[:horizon]
            metrics = _path_metrics(entry, window)
            for key, value in metrics.items():
                result.at[index, f"{key}_{horizon}d"] = value
            cost = _cost_pct(row)
            result.at[index, f"total_cost_pct_{horizon}d"] = cost
            if cost is not None:
                result.at[index, f"net_return_pct_{horizon}d"] = metrics["gross_return_pct"] - cost
            benchmark_returns = {}
            for label, ticker in (("spy", "SPY"), ("qqq", "QQQ"), ("sector", row.sector_etf)):
                benchmark = histories.get(str(ticker), pd.DataFrame()) if ticker else pd.DataFrame()
                stored = row.benchmarks.get(label, {}) if isinstance(row.benchmarks, dict) else {}
                benchmark_entry = _adjusted_entry(
                    _number(stored.get("price")), row.signal_day, benchmark
                ) if not benchmark.empty else None
                benchmark_future = benchmark[benchmark.index > row.signal_day] if not benchmark.empty else benchmark
                value = (
                    (benchmark_future.iloc[horizon - 1].adjusted / benchmark_entry - 1) * 100
                    if benchmark_entry and len(benchmark_future) >= horizon else None
                )
                benchmark_returns[label] = value
                result.at[index, f"{label}_return_pct_{horizon}d"] = value
            cash_yield = _number(row.cash_yield_pct)
            cash_return = (
                ((1 + cash_yield / 100) ** (horizon / 252) - 1) * 100
                if cash_yield is not None else None
            )
            result.at[index, f"cash_return_pct_{horizon}d"] = cash_return
            gross = metrics["gross_return_pct"]
            net = result.at[index, f"net_return_pct_{horizon}d"]
            for label in ("spy", "qqq", "sector"):
                benchmark_return = benchmark_returns.get(label)
                if benchmark_return is not None:
                    result.at[index, f"gross_alpha_{label}_pct_{horizon}d"] = gross - benchmark_return
                    if pd.notna(net):
                        result.at[index, f"net_alpha_{label}_pct_{horizon}d"] = net - benchmark_return
            if cash_return is not None:
                result.at[index, f"gross_alpha_cash_pct_{horizon}d"] = gross - cash_return
                if pd.notna(net):
                    result.at[index, f"net_alpha_cash_pct_{horizon}d"] = net - cash_return
            result.at[index, f"outcome_status_{horizon}d"] = "matured"
    return result


def _aggregate(values):
    series = pd.Series(values).dropna().astype(float)
    gains = series[series > 0]
    losses = series[series < 0]
    return {
        "n": len(series),
        "mean": series.mean() if len(series) else np.nan,
        "median": series.median() if len(series) else np.nan,
        "win_rate": (series > 0).mean() * 100 if len(series) else np.nan,
        "average_gain": gains.mean() if len(gains) else np.nan,
        "average_loss": losses.mean() if len(losses) else np.nan,
        "expectancy": series.mean() if len(series) else np.nan,
    }


def component_analysis_table(labelled):
    """Out-of-sample association and conservative incremental-R² diagnostics."""
    rows = []
    components = list(shadow_validation.COMPONENTS)
    for partition in ("calibration", "holdout_locked"):
        sample = labelled[labelled.sample_partition == partition]
        for horizon in HORIZONS:
            target = f"net_alpha_spy_pct_{horizon}d"
            numeric = sample[components + [target]].apply(pd.to_numeric, errors="coerce")
            correlations = numeric[components].corr().abs()
            for component in components:
                pair = numeric[[component, target]].dropna()
                peers = correlations.loc[component].drop(component, errors="ignore").dropna()
                incremental_r2 = np.nan
                complete = numeric.dropna()
                # Avoid reporting unstable multivariate attribution on tiny samples.
                if len(complete) >= max(30, len(components) + 5):
                    y = complete[target].to_numpy(float)
                    full_x = np.column_stack([
                        np.ones(len(complete)), complete[components].to_numpy(float)
                    ])
                    reduced_components = [name for name in components if name != component]
                    reduced_x = np.column_stack([
                        np.ones(len(complete)), complete[reduced_components].to_numpy(float)
                    ])
                    total = np.square(y - y.mean()).sum()
                    if total > 0:
                        full_residual = y - full_x @ np.linalg.lstsq(full_x, y, rcond=None)[0]
                        reduced_residual = y - reduced_x @ np.linalg.lstsq(reduced_x, y, rcond=None)[0]
                        full_r2 = 1 - np.square(full_residual).sum() / total
                        reduced_r2 = 1 - np.square(reduced_residual).sum() / total
                        incremental_r2 = full_r2 - reduced_r2
                rows.append({
                    "partition": partition,
                    "horizon": horizon,
                    "component": component,
                    "n": len(pair),
                    "pearson_forward_alpha": pair[component].corr(pair[target]) if len(pair) >= 3 else np.nan,
                    "spearman_forward_alpha": pair[component].corr(pair[target], method="spearman") if len(pair) >= 3 else np.nan,
                    "max_abs_component_correlation": peers.max() if len(peers) else np.nan,
                    "incremental_r2": incremental_r2,
                })
    return pd.DataFrame(rows)


def portfolio_fit_table(labelled):
    sample = labelled.copy()
    sample["portfolio_fit_cohort"] = "other_observed"
    sample.loc[~sample.portfolio_fit_available, "portfolio_fit_cohort"] = "missing"
    sample.loc[(sample.raw_score >= 75) & (sample.portfolio_fit < 50), "portfolio_fit_cohort"] = "raw_high_fit_weak"
    sample.loc[(sample.raw_score >= 50) & (sample.raw_score < 75) & (sample.portfolio_fit >= 70), "portfolio_fit_cohort"] = "raw_medium_fit_good"
    rows = []
    for (partition, cohort), group in sample.groupby(
        ["sample_partition", "portfolio_fit_cohort"], dropna=False
    ):
        row = {
            "partition": partition, "cohort": cohort, "predictions": len(group),
            "raw_score_mean": group.raw_score.mean(),
            "adjusted_score_mean": group.adjusted_score.mean(),
        }
        for horizon in HORIZONS:
            row.update({
                f"net_alpha_spy_{horizon}d_{key}": value
                for key, value in _aggregate(group[f"net_alpha_spy_pct_{horizon}d"]).items()
            })
        rows.append(row)
    return pd.DataFrame(rows)


def decision_disagreement_table(labelled):
    different = labelled[
        labelled.baseline_decision.fillna("") != labelled.enhanced_decision.fillna("")
    ].copy()
    columns = [
        "snapshot_id", "recorded_at", "sample_partition", "symbol",
        "baseline_decision", "enhanced_decision", "raw_score", "portfolio_fit",
        "adjusted_score",
    ] + [f"net_alpha_spy_pct_{horizon}d" for horizon in HORIZONS]
    return different.reindex(columns=columns)


def performance_tables(labelled):
    rows = []
    buckets = []
    for partition in ("calibration", "holdout_locked"):
        sample = labelled[labelled.sample_partition == partition]
        for horizon in HORIZONS:
            for metric in (
                "gross_return_pct", "net_return_pct", "spy_return_pct",
                "qqq_return_pct", "sector_return_pct", "cash_return_pct",
                "gross_alpha_spy_pct", "net_alpha_spy_pct",
                "net_alpha_qqq_pct", "net_alpha_sector_pct",
                "net_alpha_cash_pct",
            ):
                column = f"{metric}_{horizon}d"
                rows.append({"partition": partition, "horizon": horizon, "metric": metric, **_aggregate(sample[column])})
            for score_name, score_column in (("baseline", "baseline_score"), ("raw", "raw_score"), ("adjusted", "adjusted_score")):
                labels = pd.cut(sample[score_column], BUCKETS, labels=BUCKET_LABELS, right=False)
                for bucket in BUCKET_LABELS:
                    subset = sample[labels == bucket]
                    buckets.append({
                        "partition": partition, "horizon": horizon,
                        "score": score_name, "bucket": bucket,
                        **_aggregate(subset[f"net_alpha_spy_pct_{horizon}d"]),
                    })
    return pd.DataFrame(rows), pd.DataFrame(buckets)


def model_performance_table(labelled):
    rows = []
    selectors = {
        "baseline_buy": lambda sample: sample.execution_eligible & (sample.baseline_decision == "BUY"),
        "enhanced_raw_75": lambda sample: sample.execution_eligible & (sample.raw_score >= 75),
        "enhanced_adjusted_75": lambda sample: sample.execution_eligible & (sample.adjusted_score >= 75),
    }
    for partition in ("calibration", "holdout_locked"):
        sample = labelled[labelled.sample_partition == partition]
        for horizon in HORIZONS:
            for model, selector in selectors.items():
                selected = sample[selector(sample)]
                row = {
                    "partition": partition, "horizon": horizon,
                    "model": model,
                }
                for metric in (
                    "gross_return_pct", "net_return_pct", "net_alpha_spy_pct",
                    "net_alpha_qqq_pct", "net_alpha_sector_pct",
                    "net_alpha_cash_pct", "mae_pct", "mfe_pct",
                    "path_max_drawdown_pct",
                ):
                    values = selected[f"{metric}_{horizon}d"]
                    summary = _aggregate(values)
                    row[f"{metric}_n"] = summary["n"]
                    row[f"{metric}_mean"] = summary["mean"]
                    row[f"{metric}_win_rate"] = summary["win_rate"]
                rows.append(row)
    return pd.DataFrame(rows)


def options_control_table(labelled):
    rows = []
    for partition in ("calibration", "holdout_locked"):
        sample = labelled[labelled.sample_partition == partition]
        for cohort, group in sample.groupby("options_cohort", dropna=False):
            row = {
                "partition": partition, "options_cohort": cohort,
                "predictions": len(group),
                "baseline_score_mean": group.baseline_score.mean(),
                "raw_score_mean": group.raw_score.mean(),
                "portfolio_fit_coverage_pct": group.portfolio_fit_available.mean() * 100,
            }
            for horizon in HORIZONS:
                values = group[f"net_alpha_spy_pct_{horizon}d"]
                row[f"net_alpha_spy_{horizon}d_n"] = values.notna().sum()
                row[f"net_alpha_spy_{horizon}d_mean"] = values.mean()
            rows.append(row)
    return pd.DataFrame(rows)


def regime_table(labelled):
    rows = []
    for partition in ("calibration", "holdout_locked"):
        sample = labelled[labelled.sample_partition == partition]
        for regime, group in sample.groupby("market_regime", dropna=False):
            for model, selected in (
                ("baseline_buy", group[group.execution_eligible & (group.baseline_decision == "BUY")]),
                ("enhanced_raw_75", group[group.execution_eligible & (group.raw_score >= 75)]),
                ("enhanced_adjusted_75", group[group.execution_eligible & (group.adjusted_score >= 75)]),
            ):
                summary = _aggregate(selected["net_alpha_spy_pct_20d"])
                rows.append({
                    "partition": partition, "market_regime": regime,
                    "model": model, **summary,
                })
    return pd.DataFrame(rows)


def risk_table(labelled):
    rows = []
    for partition in ("calibration", "holdout_locked"):
        sample = labelled[labelled.sample_partition == partition]
        selectors = (
            ("baseline", sample.baseline_decision == "BUY"),
            ("enhanced_raw", sample.raw_score >= 75),
            ("enhanced_adjusted", sample.adjusted_score >= 75),
        )
        for model, selector in selectors:
            selected = sample[sample.execution_eligible & selector]
            daily = selected.groupby("signal_day")["net_alpha_spy_pct_20d"].mean().dropna() / 100
            if len(daily):
                equity = (1 + daily).cumprod()
                drawdown = equity / equity.cummax() - 1
                volatility = daily.std(ddof=1) * math.sqrt(252)
                downside_daily = daily[daily < 0].std(ddof=1)
                sharpe = daily.mean() / daily.std(ddof=1) * math.sqrt(252) if daily.std(ddof=1) > 0 else np.nan
                sortino = daily.mean() / downside_daily * math.sqrt(252) if downside_daily and downside_daily > 0 else np.nan
            else:
                drawdown = pd.Series(dtype=float)
                volatility = sharpe = sortino = np.nan
            rows.append({
                "partition": partition, "model": model, "days": len(daily),
                "max_drawdown_pct": drawdown.min() * 100 if len(drawdown) else np.nan,
                "annualized_volatility_pct": volatility * 100 if pd.notna(volatility) else np.nan,
                "approx_sharpe": sharpe, "approx_sortino": sortino,
            })
    return pd.DataFrame(rows)


def write_report(labelled, performance, model_performance, buckets, risk,
                 options_control, regimes, components, portfolio_fit,
                 disagreements, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    coverage = []
    for partition in ("calibration", "holdout_locked"):
        sample = labelled[labelled.sample_partition == partition]
        coverage.append({
            "partition": partition, "predictions": len(sample),
            "execution_eligible_pct": sample.execution_eligible.mean() * 100 if len(sample) else np.nan,
            "options_pct": sample.options_available.mean() * 100 if len(sample) else np.nan,
            "portfolio_fit_pct": sample.portfolio_fit_available.mean() * 100 if len(sample) else np.nan,
            **{f"matured_{h}d": int((sample[f'outcome_status_{h}d'] == 'matured').sum()) for h in HORIZONS},
        })
    coverage = pd.DataFrame(coverage)
    def markdown(frame):
        if frame.empty:
            return "_No observations._"
        text = frame.to_csv(index=False).strip().splitlines()
        return "```csv\n" + "\n".join(text) + "\n```"
    holdout_matured = int((
        (labelled.sample_partition == "holdout_locked")
        & (labelled.get("outcome_status_20d", pd.Series(dtype=str)) == "matured")
    ).sum())
    verdict = "CONTINUE SHADOW" if holdout_matured < 100 else "CONTINUE SHADOW"
    report = f"""# Enhanced Scoring forward validation

Generated: {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}

## Data coverage

{markdown(coverage)}

## Gross, net and benchmark alpha

{markdown(performance)}

## Baseline versus Enhanced

{markdown(model_performance)}

## Risk-adjusted event-study metrics

{markdown(risk)}

## Score buckets — net alpha versus SPY

{markdown(buckets)}

## Options availability/control cohort

{markdown(options_control)}

Availability is reported separately from the formula value. Missing options
data is never classified as an observed score of 50.

## Portfolio Fit cohorts

{markdown(portfolio_fit)}

## Component contribution and redundancy

{markdown(components)}

Incremental R² is intentionally withheld until at least 30 complete matured
observations are available; this avoids unstable attribution on tiny samples.

## Baseline / Enhanced decision disagreements

{markdown(disagreements)}

## Market regimes

{markdown(regimes)}

## Method constraints

- Signal entry is the ask captured at signal time, otherwise the captured last price.
- No later price is permitted to replace signal entry.
- Later adjusted-price factors may mechanically normalize splits/dividends.
- Costs include estimated IBKR commission, captured spread, estimated slippage and FX.
- Calibration and locked holdout are never pooled for threshold or weight selection.
- This evaluator does not optimize weights and cannot change BUY/WAIT/AVOID.

## Preliminary verdict

**{verdict}**

Promotion requires positive and robust **net excess return**, acceptable
expectancy/drawdown and consistency across regimes in the locked holdout.
"""
    (output_dir / "forward_validation_report.md").write_text(report, encoding="utf-8")
    coverage.to_csv(output_dir / "coverage.csv", index=False)
    performance.to_csv(output_dir / "performance.csv", index=False)
    buckets.to_csv(output_dir / "score_buckets_forward.csv", index=False)
    risk.to_csv(output_dir / "risk_metrics.csv", index=False)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", default=str(shadow_validation.LEDGER_PATH))
    parser.add_argument("--output", default=str(OUTPUT_DIR))
    parser.add_argument("--offline", action="store_true", help="Generate pending coverage without downloading outcomes")
    args = parser.parse_args()
    flat = flatten_ledger(shadow_validation.load_ledger(args.ledger))
    labelled = flat if args.offline or flat.empty else label_matured_predictions(flat)
    if flat.empty:
        shadow_validation.generate_readiness_report(
            Path(args.output) / "forward_validation_report.md", args.ledger
        )
        return
    if args.offline:
        pending_columns = {}
        for horizon in HORIZONS:
            pending_columns[f"outcome_status_{horizon}d"] = "pending"
            for prefix in (
                "gross_return_pct", "net_return_pct", "total_cost_pct",
                "mae_pct", "mfe_pct", "path_max_drawdown_pct",
                "path_volatility_pct", "spy_return_pct", "qqq_return_pct",
                "sector_return_pct", "cash_return_pct",
                "gross_alpha_spy_pct", "net_alpha_spy_pct",
                "gross_alpha_qqq_pct", "net_alpha_qqq_pct",
                "gross_alpha_sector_pct", "net_alpha_sector_pct",
                "gross_alpha_cash_pct", "net_alpha_cash_pct",
            ):
                pending_columns[f"{prefix}_{horizon}d"] = np.nan
        labelled = pd.concat(
            [labelled, pd.DataFrame(pending_columns, index=labelled.index)],
            axis=1,
        )
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    labelled.to_csv(output / "labelled_predictions.csv", index=False)
    performance, buckets = performance_tables(labelled)
    model_performance = model_performance_table(labelled)
    options_control = options_control_table(labelled)
    regimes = regime_table(labelled)
    risk = risk_table(labelled)
    components = component_analysis_table(labelled)
    portfolio_fit = portfolio_fit_table(labelled)
    disagreements = decision_disagreement_table(labelled)
    write_report(
        labelled, performance, model_performance, buckets, risk,
        options_control, regimes, components, portfolio_fit, disagreements,
        output,
    )
    model_performance.to_csv(output / "model_performance.csv", index=False)
    options_control.to_csv(output / "options_control.csv", index=False)
    regimes.to_csv(output / "market_regimes_forward.csv", index=False)
    components.to_csv(output / "component_analysis.csv", index=False)
    portfolio_fit.to_csv(output / "portfolio_fit_analysis.csv", index=False)
    disagreements.to_csv(output / "decision_disagreements.csv", index=False)


if __name__ == "__main__":
    main()
