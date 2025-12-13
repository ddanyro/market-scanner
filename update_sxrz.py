
import pandas as pd
import os

PORTFOLIO_FILE = '/Users/danieldragomir/antigravity/portfolio.csv'

# Update just SXRZ with the precise EUR value
updates = {
    'SXRZ': {'pct': 12.00, 'stop': 252.10}
}

if os.path.exists(PORTFOLIO_FILE):
    df = pd.read_csv(PORTFOLIO_FILE)
    
    # Update logic
    for sym, data in updates.items():
        mask = df['Symbol'].str.upper() == sym.upper()
        if mask.any():
            print(f"Updating {sym} -> Trail {data['pct']}%, Stop {data['stop']}")
            df.loc[mask, 'Trail_Pct'] = data['pct']
            df.loc[mask, 'Trail_Stop'] = data['stop']

    df.to_csv(PORTFOLIO_FILE, index=False)
    print("SXRZ updated.")
