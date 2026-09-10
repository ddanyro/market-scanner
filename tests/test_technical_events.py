import json

import numpy as np
import pandas as pd

import enhanced_scoring
import merge_shadow_ledgers
import technical_events
import technical_events_shadow


def frame_from_close(values, volume=None):
    close = np.asarray(values, dtype=float)
    index = pd.date_range("2025-01-01", periods=len(close), freq="B")
    return pd.DataFrame({
        "Open": close - 0.1,
        "High": close + 0.5,
        "Low": close - 0.5,
        "Close": close,
        "Volume": np.asarray(volume if volume is not None else np.full(len(close), 1000), dtype=float),
    }, index=index)


TEST_CONFIG = {
    "SHORT_TERM": technical_events.TimeframeConfig(60, 3, 8, 2, 20, 6, 3),
}


def event_names(result):
    return {item["name"] for item in result["events"]}


def test_bullish_crossover_and_momentum_are_detected():
    values = [12] * 30 + list(np.linspace(12, 9, 10)) + list(np.linspace(9, 16, 20))
    result = technical_events.analyze(frame_from_close(values), timeframe_config=TEST_CONFIG)
    names = event_names(result)
    assert "bullish SMA crossover" in names
    assert "MACD bullish crossover" in names or "bullish momentum reversal" in names
    assert result["affects_baseline"] is False
    assert result["affects_enhanced"] is False


def test_breakout_and_volume_confirmation_are_detected():
    base = 100 + np.sin(np.linspace(0, 8 * np.pi, 59)) * 3
    values = [*base, 106.0]
    volume = [1000] * 59 + [3000]
    result = technical_events.analyze(
        frame_from_close(values, volume), timeframe_config=TEST_CONFIG
    )
    names = event_names(result)
    assert "price breakout above resistance" in names
    assert "volume-confirmed breakout" in names


def test_breakdown_is_detected():
    base = 100 + np.sin(np.linspace(0, 8 * np.pi, 59)) * 3
    result = technical_events.analyze(
        frame_from_close([*base, 94.0]), timeframe_config=TEST_CONFIG
    )
    assert "breakdown below support" in event_names(result)


def test_support_resistance_uses_clustered_confirmed_swings():
    values = 100 + np.sin(np.linspace(0, 10 * np.pi, 80)) * 5
    levels = technical_events.support_resistance(
        frame_from_close(values), TEST_CONFIG["SHORT_TERM"]
    )
    assert levels["available"] is True
    assert levels["support_levels"]
    assert levels["resistance_levels"]
    assert levels["nearest_support"] < values[-1] < levels["nearest_resistance"]
    assert levels["breakout_threshold"] > 0


def test_recency_decay_has_documented_half_life():
    assert technical_events.recency_factor(0, 10) == 1
    assert technical_events.recency_factor(10, 10) == 0.5
    assert technical_events.recency_factor(20, 10) == 0.25


def test_multi_timeframe_conflicts_are_explicit():
    assert technical_events.conflict_description({
        "SHORT_TERM": "BEARISH",
        "INTERMEDIATE_TERM": "BULLISH",
        "LONG_TERM": "BULLISH",
    }) == "SHORT-TERM PULLBACK INSIDE LONG-TERM BULL TREND"
    assert technical_events.conflict_description({
        "SHORT_TERM": "BULLISH",
        "INTERMEDIATE_TERM": "BEARISH",
        "LONG_TERM": "BEARISH",
    }) == "SHORT-TERM RALLY INSIDE LONG-TERM BEAR TREND"


def test_missing_data_is_neutral_and_explicit():
    result = technical_events.analyze(pd.DataFrame())
    assert result["available"] is False
    assert result["overall_direction"] == "NEUTRAL"
    assert result["confidence"] == 0


def test_benchmark_alignment_accepts_mixed_timezones():
    stock = frame_from_close(np.linspace(90, 110, 60))
    benchmark = frame_from_close(np.linspace(100, 105, 60))
    benchmark.index = benchmark.index.tz_localize("America/New_York")
    result = technical_events.analyze(
        stock, benchmark, timeframe_config=TEST_CONFIG
    )
    assert result["available"] is True


def test_short_pullback_does_not_erase_long_structural_uptrend():
    rising = np.linspace(75, 120, 300)
    pullback = np.linspace(120, 112, 20)
    result = technical_events.analyze(frame_from_close([*rising, *pullback]))

    short = result["timeframes"]["SHORT_TERM"]
    long = result["timeframes"]["LONG_TERM"]
    assert short["direction"] == "BEARISH"
    assert long["direction"] == "BULLISH"
    assert long["structural_direction"] == "BULLISH"
    assert result["conflict"] == "MIXED SIGNALS ACROSS TIMEFRAMES"


def test_long_term_excludes_fast_daily_oscillators_from_score():
    values = 100 + np.linspace(0, 20, 320) + np.sin(np.linspace(0, 30, 320)) * 3
    result = technical_events.analyze(frame_from_close(values))
    long = result["timeframes"]["LONG_TERM"]
    fast = [
        event for event in long["events"]
        if "RSI" in event["name"] or "MACD" in event["name"]
        or "momentum reversal" in event["name"]
    ]
    assert fast
    assert all(event["excluded_from_score"] is True for event in fast)
    assert all(event["scoring_effective_strength"] == 0 for event in fast)


def test_correlated_event_family_is_discounted_not_hidden():
    events = [
        {"name": "RSI deterioration", "type": "MOMENTUM", "direction": "BEARISH", "effective_strength": 60},
        {"name": "MACD bearish crossover", "type": "CROSSUNDER", "direction": "BEARISH", "effective_strength": 50},
    ]
    score, totals = technical_events._score_event_flow(events)
    assert totals["BEARISH"] == 77.5
    assert score == 0
    assert events[0]["correlation_discount"] == 1
    assert events[1]["correlation_discount"] == 0.35


def test_timeframe_score_exposes_reproducible_structural_formula():
    result = technical_events.analyze(frame_from_close(np.linspace(80, 120, 320)))
    for detail in result["timeframes"].values():
        weight = detail["structural_weight"]
        expected = weight * detail["structural_score"] + (1 - weight) * detail["recent_event_score"]
        assert detail["event_score"] == round(expected, 2)
        assert detail["score_formula"]


def test_technical_events_field_cannot_change_enhanced_score():
    item = {"Decision": "WAIT", "Checks_Passed": 3, "RSI": 55, "RS_vs_SPX": 5}
    before = enhanced_scoring.calculate_scores(item)
    after = enhanced_scoring.calculate_scores({
        **item, "Technical_Events": {"overall_event_score": 100}
    })
    assert before == after


def test_shadow_ledger_is_hash_chained_and_has_no_future_outcomes(tmp_path):
    path = tmp_path / "technical.jsonl.gz"
    analysis = technical_events.analyze(
        frame_from_close(np.linspace(90, 110, 60)), timeframe_config=TEST_CONFIG
    )
    row = {
        "Ticker": "AAA", "Price_Native": 110, "Currency": "USD",
        "Decision": "BUY", "Checks_Passed": 4, "Technical_Events": analysis,
    }
    technical_events_shadow.append_snapshot(
        [row], {}, run_mode="all", recorded_at="2026-09-09T12:00:00Z", path=path
    )
    technical_events_shadow.append_snapshot(
        [{**row, "Ticker": "BBB"}], {}, run_mode="all",
        recorded_at="2026-09-09T12:01:00Z", path=path,
    )
    ledger = technical_events_shadow.load_ledger(path)
    assert len(ledger) == 2
    assert ledger[1]["previous_snapshot_hash"] == ledger[0]["content_hash"]
    assert technical_events_shadow.validate_ledger(ledger) == []
    prediction = ledger[0]["predictions"][0]
    assert prediction["outcomes"]["status"] == "PENDING"
    assert all(value is None for value in prediction["outcomes"]["forward_returns"].values())


def test_tampered_shadow_snapshot_is_rejected(tmp_path):
    path = tmp_path / "technical.jsonl"
    result = technical_events.analyze(
        frame_from_close(np.linspace(90, 110, 60)), timeframe_config=TEST_CONFIG
    )
    technical_events_shadow.append_snapshot(
        [{"Ticker": "AAA", "Technical_Events": result}], {}, path=path
    )
    payload = json.loads(path.read_text())
    payload["predictions"][0]["technical_events_score"] = 99
    path.write_text(json.dumps(payload) + "\n")
    try:
        technical_events_shadow.load_ledger(path)
    except ValueError as exc:
        assert "invalid Technical Events hash" in str(exc)
    else:
        raise AssertionError("tampered Technical Events snapshot was accepted")


def test_technical_ledgers_merge_without_losing_observations(tmp_path):
    left = tmp_path / "left.jsonl.gz"
    right = tmp_path / "right.jsonl.gz"
    output = tmp_path / "merged.jsonl.gz"
    result = technical_events.analyze(
        frame_from_close(np.linspace(90, 110, 60)), timeframe_config=TEST_CONFIG
    )
    technical_events_shadow.append_snapshot(
        [{"Ticker": "AAA", "Technical_Events": result}], {},
        recorded_at="2026-09-09T12:00:00Z", path=left,
    )
    technical_events_shadow.append_snapshot(
        [{"Ticker": "BBB", "Technical_Events": result}], {},
        recorded_at="2026-09-09T12:01:00Z", path=right,
    )
    rows = merge_shadow_ledgers.merge_ledgers([left, right])
    merge_shadow_ledgers.write_merged(
        output, rows, validator=technical_events_shadow
    )
    assert len(technical_events_shadow.load_ledger(output)) == 2
