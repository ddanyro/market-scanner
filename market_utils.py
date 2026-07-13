# -*- coding: utf-8 -*-
import os
import json

STATE_FILE = "dashboard_state.json"
MARKET_HISTORY_FILE = "market_history.json"

def load_state():
    """Încărcare state din fișier JSON."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_state(state):
    """Salvare state în fișier JSON."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
        
    # Salvare fișiere secționate mai mici pentru ChatGPT / Custom GPTs
    try:
        # 1. Portofoliu curat (fără sparkline)
        clean_portfolio = []
        for item in state.get("portfolio", []):
            item_copy = dict(item)
            item_copy.pop("Sparkline", None)
            clean_portfolio.append(item_copy)
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
            
        # 3. Watchlist cu decizii active de BUY
        buy_watchlist = []
        for item in state.get("watchlist", []):
            decision = str(item.get("Decision", "")).upper()
            if "BUY" in decision:
                item_copy = dict(item)
                item_copy.pop("Sparkline", None)
                buy_watchlist.append(item_copy)
        with open("watchlist_buy.json", "w") as f:
            json.dump(buy_watchlist, f, indent=2)
            
        # 4. Watchlist compact (toate elementele, fără sparklines pentru a reduce dimensiunea)
        compact_watchlist = []
        for item in state.get("watchlist", []):
            item_copy = dict(item)
            item_copy.pop("Sparkline", None)
            compact_watchlist.append(item_copy)
        with open("watchlist_compact.json", "w") as f:
            json.dump(compact_watchlist, f, indent=2)
            
    except Exception as e:
        print(f"⚠️ Eroare la salvarea fișierelor secționate JSON: {e}")

