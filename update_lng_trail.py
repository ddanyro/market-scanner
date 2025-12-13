
import pandas as pd
import os

PORTFOLIO_FILE = '/Users/danieldragomir/antigravity/portfolio.csv'

if os.path.exists(PORTFOLIO_FILE):
    df = pd.read_csv(PORTFOLIO_FILE)
    
    mask = df['Symbol'] == 'LNG'
    if mask.any():
        print(f"Updating LNG: Trail 7.6%, Stop 178.58")
        df.loc[mask, 'Trail_Pct'] = 7.6
        df.loc[mask, 'Trail_Stop'] = 178.58
        df.to_csv(PORTFOLIO_FILE, index=False)
        print("Updated.")
    else:
        print("LNG not found.")
