
import pandas as pd
import os

PORTFOLIO_FILE = '/Users/danieldragomir/antigravity/portfolio.csv'

# LQQ is EUR, put direct.
# TVBETETF is RON, convert EUR target (8.00) back to RON (approx 40).
# Assuming 1 RON = 0.20 EUR. 8 / 0.2 = 40.

updates = {
    'LQQ.PA': 1454.40,
    'TVBETETF.RO': 40.00 # RON
}

if os.path.exists(PORTFOLIO_FILE):
    df = pd.read_csv(PORTFOLIO_FILE)
    
    for sym, val in updates.items():
        mask = df['Symbol'] == sym
        if mask.any():
            print(f"Setting {sym} Stop to {val}")
            df.loc[mask, 'Trail_Stop'] = val
            df.loc[mask, 'Trail_Pct'] = 0
            
    df.to_csv(PORTFOLIO_FILE, index=False)
    print("Updated manual stops.")
