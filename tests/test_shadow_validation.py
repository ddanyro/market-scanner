import datetime as dt
import json

import pandas as pd

import evaluate_shadow_forward
import merge_shadow_ledgers
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
    assert row["options"]["cohort"] == "OPTIONS_UNAVAILABLE"


def test_snapshot_preserves_metadata_and_raw_options_provenance():
    row = shadow_validation.build_snapshot([candidate(
        country="US", exchange="NASDAQ", security_type="STK",
        contract_id=265598,
        market_metadata_source="IBKR_MCP_SEARCH_CONTRACTS",
        implied_volatility=0.31, iv_percentile=0.82,
        options_collection_selected=True,
        options_data_available=True,
        options_cohort="OPTIONS_AVAILABLE",
        options_context={
            "available": True, "score_available": True,
            "data_quality": "complete", "fetched_at": "2026-09-08T09:59:00Z",
            "expirations": ["2026-09-18"],
            "contracts": [{
                "side": "call", "strike": 100, "bid": 2, "ask": 2.2,
                "volume": 120, "open_interest": 500,
            }],
        },
    )], {}, recorded_at="2026-09-08T10:00:00Z")["predictions"][0]
    assert row["instrument_metadata"] == {
        "country": "US", "exchange": "NASDAQ", "security_type": "STK",
        "currency": "USD", "contract_id": 265598,
        "source": "IBKR_MCP_SEARCH_CONTRACTS",
    }
    assert row["options"]["option_volume"] == 120
    assert row["options"]["open_interest"] == 500
    assert row["options"]["sampled_bid_ask"][0]["ask"] == 2.2
    assert row["options"]["fetched_at"] == "2026-09-08T09:59:00Z"


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
    assert loaded[1]["previous_snapshot_hash"] == loaded[0]["content_hash"]


def test_hash_chain_detects_snapshot_tampering(tmp_path):
    path = tmp_path / "ledger.jsonl"
    shadow_validation.append_snapshot(
        [candidate()], {}, "2026-09-08T10:00:00Z", "portfolio", path
    )
    payload = json.loads(path.read_text())
    payload["predictions"][0]["raw_score"] = 99
    path.write_text(json.dumps(payload) + "\n")
    try:
        shadow_validation.load_ledger(path)
    except ValueError as exc:
        assert "Invalid snapshot hash" in str(exc)
    else:
        raise AssertionError("tampered ledger was accepted")


def test_concurrent_legacy_ledgers_are_merged_by_snapshot_id(tmp_path):
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    output = tmp_path / "merged.jsonl"
    base = shadow_validation.build_snapshot(
        [candidate()], {}, "2026-09-08T10:00:00Z", "portfolio"
    )
    # Legacy rows have no chain dependency and model the existing ledger data.
    base["schema"] = "market-scanner.shadow-prediction.v1"
    base.pop("content_hash", None)
    base.pop("previous_snapshot_hash", None)
    left = json.loads(json.dumps(base))
    right = json.loads(json.dumps(base))
    left.update(snapshot_id="left", recorded_at="2026-09-08T10:01:00Z")
    right.update(snapshot_id="right", recorded_at="2026-09-08T10:02:00Z")
    left["predictions"][0]["recorded_at"] = left["recorded_at"]
    right["predictions"][0]["recorded_at"] = right["recorded_at"]
    first.write_text(json.dumps(left) + "\n")
    second.write_text(json.dumps(left) + "\n" + json.dumps(right) + "\n")
    merged = merge_shadow_ledgers.merge_ledgers([first, second])
    merge_shadow_ledgers.write_merged(output, merged)
    assert [row["snapshot_id"] for row in shadow_validation.load_ledger(output)] == [
        "left", "right",
    ]


def test_hash_validation_accepts_concurrent_children_of_known_parent(tmp_path):
    path = tmp_path / "branched.jsonl"
    root = shadow_validation.build_snapshot(
        [candidate()], {}, "2026-09-08T10:00:00Z", "portfolio"
    )
    children = []
    for timestamp, symbol in (
        ("2026-09-08T10:01:00Z", "LEFT"),
        ("2026-09-08T10:02:00Z", "RIGHT"),
    ):
        child = shadow_validation.build_snapshot(
            [candidate(symbol=symbol)], {}, timestamp, "portfolio"
        )
        child["previous_snapshot_hash"] = root["content_hash"]
        child["content_hash"] = shadow_validation._content_hash(child)
        child["snapshot_id"] = child["content_hash"][:24]
        children.append(child)
    path.write_text("".join(
        json.dumps(item) + "\n" for item in [root, *children]
    ))
    assert len(shadow_validation.load_ledger(path)) == 3


def test_locked_holdout_partition_is_preregistered():
    policy = shadow_validation.load_policy()
    assert shadow_validation.sample_partition("2026-12-31T23:00:00Z", policy) == "calibration"
    assert shadow_validation.sample_partition("2027-01-01T00:00:00Z", policy) == "holdout_locked"


def test_signal_day_uses_market_timezone():
    snapshot = shadow_validation.build_snapshot(
        [candidate()], {}, recorded_at="2026-09-09T00:30:00Z"
    )
    row = snapshot["predictions"][0]
    assert row["entry"]["market_timezone"] == "America/New_York"
    flat = evaluate_shadow_forward.flatten_ledger([snapshot])
    assert str(flat.iloc[0].signal_day.date()) == "2026-09-08"


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


def test_missing_spread_does_not_become_zero_cost():
    snapshot = shadow_validation.build_snapshot(
        [candidate(spread_pct=None)], {}, recorded_at="2026-09-08T10:00:00Z"
    )
    flat = evaluate_shadow_forward.flatten_ledger([snapshot])
    assert evaluate_shadow_forward._cost_pct(flat.iloc[0]) is None


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
