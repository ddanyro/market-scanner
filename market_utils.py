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
