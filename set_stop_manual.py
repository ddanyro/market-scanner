
import pandas as pd
import os

PORTFOLIO_FILE = '/Users/danieldragomir/antigravity/portfolio.csv'

# Manual current prices
updates = {
    'LQQ.PA': 1760.78,
    'TVBETETF.RO': 9.24
}

if os.path.exists(PORTFOLIO_FILE):
    df = pd.read_csv(PORTFOLIO_FILE)
    
    for sym, price in updates.items():
        mask = df['Symbol'] == sym
        if mask.any():
            print(f"Setting {sym} Stop to {price}")
            df.loc[mask, 'Trail_Stop'] = price
            df.loc[mask, 'Trail_Pct'] = 0
            
    df.to_csv(PORTFOLIO_FILE, index=False)
    print("Updated Stops manual.")
