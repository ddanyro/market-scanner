import copy
import json

import market_utils


def configure_files(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(market_utils, "STATE_FILE", "dashboard_state.json")
    monkeypatch.setattr(
        market_utils, "TECHNICAL_EVENTS_STATE_FILE", "technical_events_state.json"
    )


def test_technical_events_are_externalized_and_hydrated(monkeypatch, tmp_path):
    configure_files(monkeypatch, tmp_path)
    state = {
        "watchlist": [{
            "Ticker": "NVDA", "Decision": "WAIT", "Consensus": "BUY",
            "Technical_Events": {"overall_event_score": 72, "events": [{"type": "BREAKOUT"}]},
        }],
        "portfolio": [{
            "Symbol": "MU",
            "Technical_Events": {"overall_event_score": 61},
        }],
        "external_buy_research": [{
            "Ticker": "NVDA",
            "Technical_Events": {"overall_event_score": 75},
        }],
    }
    original = copy.deepcopy(state)

    market_utils.save_state(state)

    assert state == original
    stored = json.loads((tmp_path / "dashboard_state.json").read_text())
    assert "Technical_Events" not in stored["watchlist"][0]
    assert stored["watchlist"][0]["Technical_Events_Ref"] == "watchlist:NVDA"
    dedicated = json.loads((tmp_path / "technical_events_state.json").read_text())
    assert dedicated["sections"]["watchlist"]["NVDA"]["overall_event_score"] == 72
    assert dedicated["sections"]["external_buy_research"]["NVDA"]["overall_event_score"] == 75

    loaded = market_utils.load_state()
    assert loaded["watchlist"][0]["Technical_Events"]["overall_event_score"] == 72
    assert loaded["portfolio"][0]["Technical_Events"]["overall_event_score"] == 61


def test_sectioned_exports_do_not_duplicate_technical_events(monkeypatch, tmp_path):
    configure_files(monkeypatch, tmp_path)
    market_utils.save_state({
        "watchlist": [{
            "Ticker": "NVDA", "Decision": "BUY", "Consensus": "STRONG BUY",
            "Sparkline": [1, 2], "Technical_Events": {"events": [1, 2, 3]},
        }],
        "portfolio": [{
            "Symbol": "NVDA", "Sparkline": [1],
            "Technical_Events": {"events": [1]},
        }],
    })
    for filename in (
        "portfolio.json", "watchlist_buy.json", "watchlist_compact.json",
        "watchlist_a_d.json", "watchlist_e_h.json", "watchlist_i_l.json",
        "watchlist_m_p.json", "watchlist_q_t.json", "watchlist_u_z.json",
    ):
        assert "Technical_Events" not in (tmp_path / filename).read_text()


def test_legacy_inline_state_loads_without_companion(monkeypatch, tmp_path):
    configure_files(monkeypatch, tmp_path)
    legacy = {"watchlist": [{
        "Ticker": "NVDA", "Technical_Events": {"overall_event_score": 70},
    }]}
    (tmp_path / "dashboard_state.json").write_text(json.dumps(legacy))
    assert market_utils.load_state() == legacy
