
import pandas as pd
import os

PORTFOLIO_FILE = '/Users/danieldragomir/antigravity/portfolio.csv'

if os.path.exists(PORTFOLIO_FILE):
    df = pd.read_csv(PORTFOLIO_FILE)
    
    mask = df['Symbol'] == 'LNG'
    if mask.any():
        print(f"Updating LNG Buy Price to 193.27")
        df.loc[mask, 'Buy_Price'] = 193.27
        df.to_csv(PORTFOLIO_FILE, index=False)
        print("Updated.")
    else:
        print("LNG not found.")
else:
    print("File not found")
