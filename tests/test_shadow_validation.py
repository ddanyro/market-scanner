import datetime as dt
import json

import pandas as pd

import evaluate_shadow_forward
import shadow_validation


def candidate(**overrides):
    value = {
        "symbol": "AAA", "market": "SUA", "sector": "Technology",
        "decision": "BUY", "enhanced_decision": "BUY",
        "score_version": "ibkr-enhanced-v1-shadow",
        "technical_score": 75, "momentum_score": 70,
        "research_score": 65, "volatility_score": 60,
        "liquidity_score": 55, "options_score": 50,
        "relative_opportunity_score": 50, "risk_reward_score": 80,
        "raw_stock_score": 66, "portfolio_adjusted_score": 68,
        "price_native": 100, "ask": 101, "bid": 99,
        "spread_pct": 2, "execution_currency": "USD",
        "portfolio_fit_available": True,
        "portfolio_fit_observed_score": 80,
        "portfolio_fit_source": "IBKR_SECTOR+IBKR_COUNTRY",
        "ibkr_sector_weight_pct": 8,
        "hypothetical_sector_weight_after_pct": 10,
        "hypothetical_purchase_weight_pct": 2,
        "conditional_units": 10,
        "options_collection_eligible": True,
        "options_collection_selected": False,
        "options_data_available": False,
    }
    value.update(overrides)
    return value


def test_snapshot_preserves_observed_fit_and_explicit_missing_options():
    snapshot = shadow_validation.build_snapshot(
        [candidate()], {}, recorded_at="2026-09-08T10:00:00Z", run_mode="all"
    )
    row = snapshot["predictions"][0]
    assert snapshot["score_mode"] == "shadow"
    assert snapshot["authoritative_decision"] == "baseline"
    assert row["entry"]["price"] == 101
    assert row["entry"]["source"] == "ask_at_signal"
    assert row["portfolio"]["fit_score_observed"] == 80
    assert row["portfolio"]["formula_fallback_used"] is False
    assert row["options"]["observed_score"] is None
    assert row["options"]["neutral_fallback_explicit"] is True
    assert row["options"]["cohort"] == "eligible_control_without_options"


def test_missing_fit_is_not_serialized_as_real_50():
    row = shadow_validation.build_snapshot(
        [candidate(
            portfolio_fit_available=False,
            portfolio_fit_observed_score=None,
            portfolio_adjusted_score=61.1,
        )], {}, recorded_at="2026-09-08T10:00:00Z"
    )["predictions"][0]
    assert row["portfolio_fit_observed"] is None
    assert row["adjusted_score_observed_fit"] is None
    assert row["adjusted_score_formula"] == 61.1


def test_stale_quote_is_recorded_but_not_execution_eligible():
    snapshot = shadow_validation.build_snapshot(
        [candidate(data_age_hours=2.5)], {},
        recorded_at="2026-09-08T10:00:00Z",
    )
    assert snapshot["predictions"][0]["entry"]["fresh_for_execution"] is False
    flat = evaluate_shadow_forward.flatten_ledger([snapshot])
    assert bool(flat.iloc[0]["execution_eligible"]) is False


def test_append_only_ledger_round_trip(tmp_path):
    path = tmp_path / "ledger.jsonl"
    shadow_validation.append_snapshot(
        [candidate()], {}, "2026-09-08T10:00:00Z", "portfolio", path
    )
    shadow_validation.append_snapshot(
        [candidate(symbol="BBB")], {}, "2026-09-08T10:30:00Z", "portfolio", path
    )
    loaded = shadow_validation.load_ledger(path)
    assert len(loaded) == 2
    assert [item["predictions"][0]["symbol"] for item in loaded] == ["AAA", "BBB"]
    assert len(path.read_text().splitlines()) == 2


def test_locked_holdout_partition_is_preregistered():
    policy = shadow_validation.load_policy()
    assert shadow_validation.sample_partition("2026-12-31T23:00:00Z", policy) == "calibration"
    assert shadow_validation.sample_partition("2027-01-01T00:00:00Z", policy) == "holdout_locked"


class FakeTicker:
    def __init__(self, _symbol):
        pass

    def history(self, **_kwargs):
        index = pd.to_datetime(["2026-09-08", "2026-09-09", "2026-09-10"], utc=True)
        return pd.DataFrame({
            "Close": [100.0, 110.0, 121.0],
            "Adj Close": [100.0, 110.0, 121.0],
            "High": [101.0, 112.0, 123.0],
            "Low": [99.0, 108.0, 119.0],
        }, index=index)


def test_forward_label_uses_frozen_ask_not_future_close():
    snapshot = shadow_validation.build_snapshot(
        [candidate()], {
            "us_sector_rotation": {"benchmark_snapshots": {
                "SPY": {"ticker": "SPY", "price": 100, "available": True},
                "QQQ": {"ticker": "QQQ", "price": 100, "available": True},
            }}
        }, recorded_at="2026-09-08T10:00:00Z", run_mode="all"
    )
    flat = evaluate_shadow_forward.flatten_ledger([snapshot])
    labelled = evaluate_shadow_forward.label_matured_predictions(
        flat,
        now=dt.datetime(2026, 9, 12, tzinfo=dt.timezone.utc),
        ticker_factory=FakeTicker,
    )
    # Frozen ask=101; the first later close=110. A reconstructed entry of 100
    # would incorrectly produce 10%.
    assert round(labelled.iloc[0]["gross_return_pct_1d"], 6) == round((110 / 101 - 1) * 100, 6)
    assert labelled.iloc[0]["outcome_status_1d"] == "matured"


def test_cost_model_contains_commission_spread_slippage_and_fx():
    snapshot = shadow_validation.build_snapshot(
        [candidate()], {}, recorded_at="2026-09-08T10:00:00Z"
    )
    flat = evaluate_shadow_forward.flatten_ledger([snapshot])
    cost = evaluate_shadow_forward._cost_pct(flat.iloc[0])
    assert cost is not None
    assert cost > 1.0  # Exit half-spread plus commission, slippage and FX.
    assert cost < 2.0  # Entry at ask is not charged the entry spread twice.


def test_component_and_portfolio_diagnostics_do_not_invent_small_sample_signal():
    snapshot = shadow_validation.build_snapshot(
        [candidate(raw_stock_score=80, portfolio_fit_observed_score=30)], {},
        recorded_at="2026-09-08T10:00:00Z",
    )
    labelled = evaluate_shadow_forward.flatten_ledger([snapshot])
    for horizon in evaluate_shadow_forward.HORIZONS:
        labelled[f"net_alpha_spy_pct_{horizon}d"] = 1.0
    components = evaluate_shadow_forward.component_analysis_table(labelled)
    assert components.incremental_r2.isna().all()
    fit = evaluate_shadow_forward.portfolio_fit_table(labelled)
    assert fit.iloc[0]["cohort"] == "raw_high_fit_weak"
