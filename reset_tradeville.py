
import pandas as pd
import os

PORTFOLIO_FILE = '/Users/danieldragomir/antigravity/portfolio.csv'

updates = ['LQQ.PA', 'TVBETETF.RO']

if os.path.exists(PORTFOLIO_FILE):
    df = pd.read_csv(PORTFOLIO_FILE)
    
    for sym in updates:
        mask = df['Symbol'] == sym
        if mask.any():
            print(f"Resetting {sym} to Trail 0%, Stop 0")
            df.loc[mask, 'Trail_Pct'] = 0
            df.loc[mask, 'Trail_Stop'] = 0
            
    df.to_csv(PORTFOLIO_FILE, index=False)
    print("Reset complete.")
