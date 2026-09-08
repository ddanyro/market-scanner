import enhanced_scoring
import market_scanner_analysis as analysis


def test_enhanced_score_keeps_baseline_and_exposes_components():
    result = enhanced_scoring.calculate_scores({
        "Decision": "BUY",
        "Checks_Passed": 4,
        "RSI": 58,
        "RS_vs_SPX": 8,
        "Consensus": "Buy",
        "Analysts": 15,
        "Price": 100,
        "ATR_14": 2,
        "Historical_Vol": 0.22,
        "Avg_90D_USD_Volume": 50_000_000,
        "Spread_Pct": 0.08,
        "RR_Ratio": 3,
    })
    assert result["current_decision"] == "BUY"
    assert result["enhanced_decision"] == "BUY"
    assert result["technical_score"] == 100
    assert 0 <= result["raw_stock_score"] <= 100
    assert result["enhanced_stop"] == 96.0
    assert result["score_version"] == "ibkr-enhanced-v1-shadow"


def test_extreme_risk_only_downgrades_shadow_decision():
    result = enhanced_scoring.calculate_scores({
        "Decision": "BUY",
        "Checks_Passed": 4,
        "Price": 100,
        "ATR_14": 9,
        "Historical_Vol": 0.80,
        "Implied_Volatility": 1.1,
        "IV_Percentile": 0.96,
        "Avg_90D_USD_Volume": 25_000,
        "Spread_Pct": 2.2,
        "RR_Ratio": 3,
    }, portfolio_fit_score=20)
    assert result["current_decision"] == "BUY"
    assert result["enhanced_decision"] == "WAIT"
    assert "spread" in result["enhanced_decision_reason"]
    assert "Portfolio Concentration Penalty" in result["enhanced_decision_reason"]


def test_missing_optional_ibkr_data_is_neutral_not_failure():
    result = enhanced_scoring.calculate_scores({
        "Decision": "WAIT", "Checks_Passed": 3, "RR_Ratio": 2,
    })
    assert result["liquidity_score"] == 50
    assert result["options_score"] == 50
    assert result["portfolio_fit_score"] == 50
    assert result["enhanced_decision"] == "WAIT"
    assert result["options_score_observed"] is None
    assert result["raw_stock_score_availability_adjusted"] != result["raw_stock_score"]


def test_ibkr_allocation_is_flattened_for_portfolio_fit():
    result = analysis._normalize_ibkr_allocation({
        "realtime": True,
        "currency": "EUR",
        "allocations": {
            "SECTOR": {
                "long_positions": {
                    "items": [{"name": "Technology", "weight": 0.22}]
                }
            },
            "COUNTRY": {
                "long_positions": {
                    "items": [{"name": "United States", "weight": 0.65}]
                }
            },
        },
    })
    assert result["realtime"] is True
    assert result["dimensions"]["SECTOR"]["Technology"] == 0.22


def test_portfolio_fit_can_be_recalculated_after_hypothetical_purchase():
    before = analysis._portfolio_fit_from_weights(0.06, 0.18, 0.18)
    after = analysis._portfolio_fit_from_weights(0.09, 0.21, 0.21)
    assert before == 95
    assert after == 80


def test_options_open_interest_contributes_when_observed():
    common = {
        "available": True, "average_spread_pct": 2,
        "quoted_contract_ratio": 1,
    }
    neutral = enhanced_scoring.options_score({"Options_Context": common})
    bearish = enhanced_scoring.options_score({
        "Options_Context": {**common, "put_call_open_interest_ratio": 2.5}
    })
    assert bearish < neutral


def test_trade_journal_links_only_prior_recommendations():
    trades = [{
        "symbol": "AAPL", "side": "BUY",
        "trade_time": "2026-08-10T10:00:00+00:00",
    }]
    history = [{
        "symbol": "AAPL", "first_seen_at": "2026-08-09T10:00:00+00:00",
        "raw_stock_score": 78, "portfolio_adjusted_score": 74,
        "portfolio_fit_score": 52, "volatility_regime": "calm",
        "score_version": "ibkr-enhanced-v1-shadow",
        "stop_native": 190, "target_native": 240,
    }, {
        "symbol": "AAPL", "first_seen_at": "2026-08-11T10:00:00+00:00",
        "portfolio_adjusted_score": 99,
    }]
    linked = analysis.link_trade_journal_to_recommendations(trades, history)
    assert linked[0]["initial_score"] == 74
    assert linked[0]["stop_price"] == 190
    assert linked[0]["portfolio_state_at_entry"]["score_version"] == "ibkr-enhanced-v1-shadow"


def test_account_performance_keeps_returns_and_drawdown():
    result = analysis._normalize_ibkr_performance({
        "portfolio_measure": "TWR",
        "accounts": {"U1": {"periods": {
            "1M": {
                "cps": [0, 0.05, 0.02],
                "nav": [100, 105, 102],
                "dates": ["20260801", "20260815", "20260831"],
            }
        }}},
    })
    assert result["method"] == "TWR"
    assert result["periods"]["1M"]["return_pct"] == 2.0
    assert result["periods"]["1M"]["max_drawdown_pct"] == -2.857
