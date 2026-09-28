import copy
import datetime as dt
import pytest

import pandas as pd

import evaluate_technical_events_forward as validation
import technical_events_shadow


def technical_payload():
    event = {
        "type": "BREAKOUT",
        "name": "price breakout above resistance",
        "direction": "BULLISH",
        "timestamp": "2026-09-08T00:00:00",
        "timeframe": "SHORT_TERM",
        "strength": 80,
        "recency_factor": 1.0,
        "effective_strength": 80,
        "age_sessions": 0,
        "confirmation_status": "CONFIRMED",
    }
    return {
        "affects_baseline": False,
        "affects_enhanced": False,
        "data_as_of": "2026-09-08T00:00:00",
        "overall_event_score": 75,
        "overall_direction": "BULLISH",
        "confidence": 82,
        "bullish_events": 1,
        "bearish_events": 0,
        "events": [event],
        "input_provenance": {"source": "test", "future_outcomes_present": False},
        "timeframes": {
            "SHORT_TERM": {"event_score": 80, "direction": "BULLISH"},
            "INTERMEDIATE_TERM": {"event_score": 70, "direction": "BULLISH"},
            "LONG_TERM": {"event_score": 65, "direction": "BULLISH"},
        },
    }


def snapshot():
    return technical_events_shadow.build_snapshot(
        [{
            "Ticker": "AAA", "Price_Native": 100, "Currency": "USD",
            "Market": "SUA", "Sector": "Technology", "Decision": "BUY",
            "Technical_Events": technical_payload(),
        }],
        {"AAA": {"technical_score": 60, "market": "SUA", "sector": "Technology"}},
        recorded_at="2026-09-08T20:00:00Z",
        run_mode="all",
        state={"us_market_regime": {
            "market_stage": "creștere confirmată", "vix": 18,
        }},
    )


class FakeTicker:
    def __init__(self, _ticker):
        pass

    def history(self, **_kwargs):
        index = pd.date_range("2026-09-08", periods=70, freq="B", tz="UTC")
        close = pd.Series(range(100, 170), dtype=float)
        return pd.DataFrame({
            "Close": close.to_numpy(),
            "Adj Close": close.to_numpy(),
            "High": (close + 2).to_numpy(),
            "Low": (close - 2).to_numpy(),
        }, index=index)


def test_snapshot_captures_regime_and_existing_technical_score():
    value = snapshot()
    row = value["predictions"][0]
    assert value["market_regime"]["vix"] == 18
    assert value["input_data_provenance"]["forward_outcomes_present"] is False
    assert row["existing_technical_score"] == 60
    assert row["data_as_of"] == "2026-09-08T00:00:00"
    assert row["history_ticker"] == "AAA"


def test_flatten_extracts_all_timeframes_and_simulated_score():
    flat = validation.flatten_ledger([snapshot()])
    row = flat.iloc[0]
    assert row.short_event_score == 80
    assert row.intermediate_event_score == 70
    assert row.long_event_score == 65
    assert row.timeframe_agreement == "all_three_bullish"
    assert row.simulated_equal_weight_score == 67.5
    assert row.trend_regime == "bullish"
    assert row.volatility_regime == "low_volatility"


def test_history_symbol_uses_exchange_qualified_contract_alias():
    value = snapshot()
    value["predictions"][0]["ticker"] = "3USL"
    value["predictions"][0].pop("history_ticker", None)
    flat = validation.flatten_ledger(
        [value], history_symbol_aliases={"3USL": "3USL.MI"}
    )
    assert flat.iloc[0].ticker == "3USL"
    assert flat.iloc[0].history_ticker == "3USL.MI"
    assert flat.iloc[0].history_ticker_source == "instrument_metadata"


def test_spearman_correlation_does_not_require_scipy():
    left = pd.Series([10, 20, 20, 40, 50], dtype=float)
    right = pd.Series([1, 2, 2, 4, 5], dtype=float)
    assert validation._correlation(left, right, method="spearman") == 1.0


def test_forward_outcomes_use_only_sessions_strictly_after_signal():
    original = snapshot()
    immutable = copy.deepcopy(original)
    flat = validation.flatten_ledger([original])
    labelled = validation.label_forward_outcomes(
        flat,
        now=dt.datetime(2027, 1, 1, tzinfo=dt.timezone.utc),
        ticker_factory=FakeTicker,
    )
    row = labelled.iloc[0]
    # Entry is 100 at T; first eligible close is 101 on the next session.
    assert round(row.return_pct_1d, 8) == 1.0
    assert round(row.mae_pct_1d, 8) == -1.0
    assert round(row.mfe_pct_1d, 8) == 3.0
    assert round(row.return_pct_5d, 8) == 5.0
    assert row.outcome_status_60d == "matured"
    assert original == immutable


def test_forward_outcomes_reports_history_and_labelling_progress():
    class Progress:
        def __init__(self):
            self.messages = []

        def emit(self, message, **_kwargs):
            self.messages.append(message)

    progress = Progress()
    flat = validation.flatten_ledger([snapshot()])
    validation.label_forward_outcomes(
        flat,
        now=dt.datetime(2027, 1, 1, tzinfo=dt.timezone.utc),
        ticker_factory=FakeTicker,
        progress=progress,
    )
    assert any("Istoric prețuri 1/1" in item for item in progress.messages)
    assert any("Etichetare rezultate 1/1" in item for item in progress.messages)


def test_pending_horizon_is_explicit_when_not_matured():
    flat = validation.flatten_ledger([snapshot()])
    labelled = validation.label_forward_outcomes(
        flat,
        now=dt.datetime(2026, 9, 10, tzinfo=dt.timezone.utc),
        ticker_factory=FakeTicker,
    )
    # The fake provider returns future rows; defensive clipping must prevent
    # those rows from maturing a longer horizon.
    assert labelled.iloc[0].outcome_status_1d == "matured"
    assert labelled.iloc[0].outcome_status_5d == "pending"


def test_all_requested_analysis_tables_are_generated():
    flat = validation.flatten_ledger([snapshot()])
    labelled = validation.label_forward_outcomes(
        flat,
        now=dt.datetime(2027, 1, 1, tzinfo=dt.timezone.utc),
        ticker_factory=FakeTicker,
    )
    tables = validation.generate_analysis(labelled)
    assert set(validation.EVENT_TYPES).issubset(set(tables["event_types"].event_type))
    assert "all_three_bullish" in set(tables["agreement"].timeframe_agreement)
    assert "breakout_above_resistance" in set(
        tables["support_resistance"].support_resistance_event
    )
    score_row = tables["score_buckets"].query(
        "feature == 'overall_event_score' and bucket == '70-79' and horizon == 1"
    ).iloc[0]
    assert score_row.n == 1
    assert round(score_row.average_return, 8) == 1.0
    direction_row = tables["directions"].query(
        "timeframe == 'OVERALL' and direction == 'BULLISH' and horizon == 1"
    ).iloc[0]
    assert direction_row.directional_hit_rate == 100
    event_row = tables["event_types"].query(
        "event_type == 'BREAKOUT' and horizon == 1"
    ).iloc[0]
    assert event_row.directional_hit_rate == 100


def test_small_sample_verdict_is_insufficient_data():
    flat = validation.flatten_ledger([snapshot()])
    labelled = validation._add_pending_columns(flat)
    tables = validation.generate_analysis(labelled)
    result, reason = validation.verdict(labelled, tables["score_comparison"])
    assert result == "INSUFFICIENT DATA"
    assert "0/100" in reason


def test_offline_empty_report_is_supported(tmp_path):
    labelled = validation._add_pending_columns(validation.flatten_ledger([]))
    tables = validation.generate_analysis(labelled)
    report, result = validation.write_report(labelled, tables, [], tmp_path)
    assert result == "INSUFFICIENT DATA"
    assert "TECHNICAL EVENTS VALIDATION REPORT" in report
    assert (tmp_path / "technical_events_validation_report.md").exists()


def test_main_writes_labelled_dataset_as_gzip(monkeypatch, tmp_path):
    monkeypatch.setattr(
        validation.technical_events_shadow,
        "load_ledger",
        lambda _path, **_kwargs: [],
    )
    (tmp_path / "event_observations.csv").write_text("legacy,large\n")
    monkeypatch.setattr(
        "sys.argv", ["evaluate_technical_events_forward.py", "--offline", "--output", str(tmp_path)]
    )
    validation.main()
    output = tmp_path / "labelled_predictions.csv.gz"
    assert output.exists()
    assert output.read_bytes()[:2] == b"\x1f\x8b"
    events_output = tmp_path / "event_observations.csv.gz"
    assert events_output.exists()
    assert events_output.read_bytes()[:2] == b"\x1f\x8b"
    assert not (tmp_path / "event_observations.csv").exists()


def test_incremental_matches_cold_and_reuses_outcomes(tmp_path, monkeypatch):
    flat = validation.flatten_ledger([snapshot()])
    now = dt.datetime(2027, 1, 1, tzinfo=dt.timezone.utc)
    cold = validation.label_forward_outcomes(flat, now=now, ticker_factory=FakeTicker)
    path = tmp_path / 'outcomes.sqlite'
    first = validation.label_forward_outcomes(flat, now=now, ticker_factory=FakeTicker, cache_path=path)
    pd.testing.assert_frame_equal(cold, first)
    def unexpected(*args, **kwargs):
        raise AssertionError('unchanged outcome must not be recalculated')
    monkeypatch.setattr(validation, '_calculate_outcomes', unexpected)
    # Network must not be touched on same-day resume either.
    second = validation.label_forward_outcomes(flat, now=now, ticker_factory=unexpected, cache_path=path)
    pd.testing.assert_frame_equal(first, second)


def test_incremental_pending_matures_and_changed_entry_invalidates(tmp_path):
    flat = validation.flatten_ledger([snapshot()])
    path = tmp_path / 'outcomes.sqlite'
    early = validation.label_forward_outcomes(flat, now='2026-09-10', ticker_factory=FakeTicker, cache_path=path)
    assert early.iloc[0].outcome_status_5d == 'pending'
    late = validation.label_forward_outcomes(flat, now='2026-09-16', ticker_factory=FakeTicker, cache_path=path)
    assert late.iloc[0].return_pct_5d == pytest.approx(5)
    flat['entry_price'] = 50
    changed = validation.label_forward_outcomes(flat, now='2026-09-16', ticker_factory=FakeTicker, cache_path=path)
    assert changed.iloc[0].return_pct_5d == pytest.approx(110)


def test_completed_symbols_survive_interruption(tmp_path):
    flat = validation.flatten_ledger([snapshot()])
    second = flat.copy()
    second['history_ticker'] = 'BBB'
    flat = pd.concat([flat, second], ignore_index=True)
    path = tmp_path / 'outcomes.sqlite'
    class Interrupted(FakeTicker):
        def __init__(self, ticker):
            if ticker == 'BBB':
                raise KeyboardInterrupt()
    with pytest.raises(KeyboardInterrupt):
        validation.label_forward_outcomes(flat, now='2027-01-01', ticker_factory=Interrupted, cache_path=path)
    reads = []
    def resumed(ticker):
        reads.append(ticker)
        return FakeTicker(ticker)
    result = validation.label_forward_outcomes(flat, now='2027-01-01', ticker_factory=resumed, cache_path=path)
    assert reads == ['BBB']
    assert list(result.return_pct_5d.round(5)) == [5, 5]


def test_missing_history_is_retried_on_resume(tmp_path):
    flat = validation.flatten_ledger([snapshot()])
    path = tmp_path / 'outcomes.sqlite'
    class Missing(FakeTicker):
        def history(self, **kwargs):
            return pd.DataFrame()
    first = validation.label_forward_outcomes(flat, now='2027-01-01', ticker_factory=Missing, cache_path=path)
    assert first.iloc[0].outcome_status_1d == 'missing_history'
    second = validation.label_forward_outcomes(flat, now='2027-01-01', ticker_factory=FakeTicker, cache_path=path)
    assert second.iloc[0].return_pct_1d == pytest.approx(1)


def test_history_revision_invalidates_cached_mature_outcome(tmp_path):
    flat = validation.flatten_ledger([snapshot()])
    path = tmp_path / 'outcomes.sqlite'
    validation.label_forward_outcomes(flat, now='2027-01-01', ticker_factory=FakeTicker, cache_path=path)
    class Revised(FakeTicker):
        def history(self, **kwargs):
            history = super().history(**kwargs)
            history.iloc[1, history.columns.get_loc('Adj Close')] = 110
            return history
    result = validation.label_forward_outcomes(flat, now='2027-01-02', ticker_factory=Revised, cache_path=path)
    assert result.iloc[0].return_pct_1d == pytest.approx(10)


def test_completed_horizons_reused_when_history_only_extends(tmp_path, monkeypatch):
    flat = validation.flatten_ledger([snapshot()])
    path = tmp_path / 'outcomes.sqlite'
    validation.label_forward_outcomes(flat, now='2027-01-01', ticker_factory=FakeTicker, cache_path=path)
    def unexpected(*args):
        raise AssertionError('mature horizon unchanged')
    monkeypatch.setattr(validation, '_calculate_outcomes', unexpected)
    result = validation.label_forward_outcomes(flat, now='2027-01-02', ticker_factory=FakeTicker, cache_path=path)
    assert result.iloc[0].return_pct_60d == pytest.approx(60)


def test_same_day_new_session_refreshes_pending_results(tmp_path):
    flat = validation.flatten_ledger([snapshot()])
    class Morning(FakeTicker):
        def history(self, **kwargs):
            return super().history(**kwargs).iloc[:1]
    path = tmp_path / 'outcomes.sqlite'
    early = validation.label_forward_outcomes(flat, now='2026-09-09T08:00:00Z', ticker_factory=Morning, cache_path=path)
    assert early.iloc[0].outcome_status_1d == 'pending'
    late = validation.label_forward_outcomes(flat, now='2026-09-09T21:00:00Z', ticker_factory=FakeTicker, cache_path=path)
    assert late.iloc[0].return_pct_1d == pytest.approx(1)


def test_explicit_price_refresh_bypasses_cache_in_same_hour(tmp_path):
    flat = validation.flatten_ledger([snapshot()])
    class Morning(FakeTicker):
        def history(self, **kwargs):
            return super().history(**kwargs).iloc[:1]
    path = tmp_path / 'outcomes.sqlite'
    validation.label_forward_outcomes(flat, now='2026-09-09T21:00:00Z', ticker_factory=Morning, cache_path=path)
    fresh = validation.label_forward_outcomes(flat, now='2026-09-09T21:01:00Z', ticker_factory=FakeTicker,
                                             cache_path=path, refresh_prices=True)
    assert fresh.iloc[0].return_pct_1d == pytest.approx(1)


def test_interrupted_export_preserves_previous_completed_report(tmp_path, monkeypatch):
    monkeypatch.setattr(validation.technical_events_shadow, 'load_ledger', lambda *a, **kw: [])
    monkeypatch.setattr('sys.argv', ['evaluate_technical_events_forward.py', '--offline', '--output', str(tmp_path)])
    labelled = tmp_path / 'labelled_predictions.csv.gz'
    report = tmp_path / 'technical_events_validation_report.md'
    marker = tmp_path / 'integrity_report.json'
    for path in (labelled, report, marker):
        path.write_bytes(b'previous completed output')
    original = pd.DataFrame.to_csv
    calls = []
    def interrupted(frame, path, *args, **kwargs):
        calls.append(path)
        if len(calls) == 2:
            raise RuntimeError('interrupted')
        return original(frame, path, *args, **kwargs)
    monkeypatch.setattr(pd.DataFrame, 'to_csv', interrupted)
    with pytest.raises(RuntimeError, match='interrupted'):
        validation.main()
    # Nest private exports under the requested output so the supervisor's
    # cleanup also removes incomplete exports after a hard child termination.
    assert all(path.is_relative_to(tmp_path) for path in calls)
    for path in (labelled, report, marker):
        assert path.read_bytes() == b'previous completed output'
