# -*- coding: utf-8 -*-
import os
import json

STATE_FILE = "dashboard_state.json"
MARKET_HISTORY_FILE = "market_history.json"
TECHNICAL_EVENTS_STATE_FILE = "technical_events_state.json"
TECHNICAL_EVENTS_SECTIONS = ("portfolio", "watchlist", "external_buy_research")


def _instrument_key(item):
    return str(item.get("Ticker") or item.get("Symbol") or "").upper()


def _split_technical_events(state):
    """Return a lightweight state plus a dedicated Technical Events payload."""
    lightweight = dict(state)
    payload = {
        "schema": "market-scanner.technical-events-state.v1",
        "sections": {},
    }
    for section in TECHNICAL_EVENTS_SECTIONS:
        cleaned_rows = []
        section_events = {}
        for item in state.get(section, []) or []:
            if not isinstance(item, dict):
                cleaned_rows.append(item)
                continue
            cleaned = dict(item)
            events = cleaned.pop("Technical_Events", None)
            key = _instrument_key(cleaned)
            if isinstance(events, dict) and key:
                section_events[key] = events
                cleaned["Technical_Events_Ref"] = f"{section}:{key}"
            cleaned_rows.append(cleaned)
        if section in state:
            lightweight[section] = cleaned_rows
        if section_events:
            payload["sections"][section] = section_events
    return lightweight, payload


def _hydrate_technical_events(state):
    if not os.path.exists(TECHNICAL_EVENTS_STATE_FILE):
        return state
    try:
        with open(TECHNICAL_EVENTS_STATE_FILE, "r") as handle:
            payload = json.load(handle)
    except (OSError, ValueError, TypeError):
        return state
    sections = payload.get("sections") if isinstance(payload, dict) else {}
    if not isinstance(sections, dict):
        return state
    for section in TECHNICAL_EVENTS_SECTIONS:
        section_events = sections.get(section) or {}
        if not isinstance(section_events, dict):
            continue
        for item in state.get(section, []) or []:
            if not isinstance(item, dict) or isinstance(item.get("Technical_Events"), dict):
                continue
            events = section_events.get(_instrument_key(item))
            if isinstance(events, dict):
                item["Technical_Events"] = events
    return state


def _lightweight_export_item(item):
    item_copy = dict(item)
    item_copy.pop("Sparkline", None)
    item_copy.pop("Technical_Events", None)
    return item_copy

def load_state():
    """Încărcare state din fișier JSON."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return _hydrate_technical_events(json.load(f))
        except:
            return {}
    return {}

def save_state(state):
    """Salvare state în fișier JSON."""
    lightweight_state, technical_events_state = _split_technical_events(state)
    with open(STATE_FILE, 'w') as f:
        json.dump(lightweight_state, f, indent=2)
    with open(TECHNICAL_EVENTS_STATE_FILE, 'w') as f:
        json.dump(technical_events_state, f, separators=(',', ':'), ensure_ascii=False)
        
    # Salvare fișiere secționate mai mici pentru ChatGPT / Custom GPTs
    try:
        # 1. Portofoliu curat (fără sparkline)
        clean_portfolio = []
        for item in state.get("portfolio", []):
            clean_portfolio.append(_lightweight_export_item(item))
        with open("portfolio.json", "w") as f:
            json.dump(clean_portfolio, f, indent=2)
            
        # 2. Indicatori macro și de piață
        indicators = {
            "rates": state.get("rates", {}),
            "market_indicators": state.get("market_indicators", {}),
            "vix_val": state.get("vix_val"),
            "eco_phase": state.get("eco_phase"),
            "eco_next_phase": state.get("eco_next_phase")
        }
        with open("market_indicators.json", "w") as f:
            json.dump(indicators, f, indent=2)
            
        # 3. Watchlist cu decizii active de BUY și Consens Buy / Strong Buy
        buy_watchlist = []
        for item in state.get("watchlist", []):
            decision = str(item.get("Decision", "")).upper()
            consensus = str(item.get("Consensus", "")).upper()
            if "BUY" in decision and "BUY" in consensus:
                buy_watchlist.append(_lightweight_export_item(item))
        with open("watchlist_buy.json", "w") as f:
            json.dump(buy_watchlist, f, indent=2)
            
        # 4. Watchlist compact (toate elementele, fără sparklines pentru a reduce dimensiunea)
        compact_watchlist = []
        for item in state.get("watchlist", []):
            compact_watchlist.append(_lightweight_export_item(item))
        with open("watchlist_compact.json", "w") as f:
            json.dump(compact_watchlist, f, indent=2)
            
        # 5. Watchlist-uri segmentate alfabetic (pentru a evita ResponseTooLargeError în ChatGPT)
        groups = {
            "A_D": ("A", "B", "C", "D"),
            "E_H": ("E", "F", "G", "H"),
            "I_L": ("I", "J", "K", "L"),
            "M_P": ("M", "N", "O", "P"),
            "Q_T": ("Q", "R", "S", "T"),
            "U_Z": ("U", "V", "W", "X", "Y", "Z")
        }
        grouped_watchlists = {g: [] for g in groups}
        
        for item in state.get("watchlist", []):
            ticker = str(item.get("Ticker", "")).upper()
            if not ticker:
                continue
            first_letter = ticker[0]
            placed = False
            for group_name, letters in groups.items():
                if first_letter in letters:
                    grouped_watchlists[group_name].append(
                        _lightweight_export_item(item)
                    )
                    placed = True
                    break
            if not placed:
                grouped_watchlists["A_D"].append(
                    _lightweight_export_item(item)
                )
                
        for group_name, watchlist_subset in grouped_watchlists.items():
            filename = f"watchlist_{group_name.lower()}.json"
            with open(filename, "w") as f:
                json.dump(watchlist_subset, f, indent=2)
            
    except Exception as e:
        print(f"⚠️ Eroare la salvarea fișierelor secționate JSON: {e}")
