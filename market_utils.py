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
            
        # 3. Watchlist cu decizii active de BUY și Consens Buy / Strong Buy
        buy_watchlist = []
        for item in state.get("watchlist", []):
            decision = str(item.get("Decision", "")).upper()
            consensus = str(item.get("Consensus", "")).upper()
            if "BUY" in decision and "BUY" in consensus:
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
                    item_copy = dict(item)
                    item_copy.pop("Sparkline", None)
                    grouped_watchlists[group_name].append(item_copy)
                    placed = True
                    break
            if not placed:
                item_copy = dict(item)
                item_copy.pop("Sparkline", None)
                grouped_watchlists["A_D"].append(item_copy)
                
        for group_name, watchlist_subset in grouped_watchlists.items():
            filename = f"watchlist_{group_name.lower()}.json"
            with open(filename, "w") as f:
                json.dump(watchlist_subset, f, indent=2)
            
    except Exception as e:
        print(f"⚠️ Eroare la salvarea fișierelor secționate JSON: {e}")

