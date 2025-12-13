
import pandas as pd
import os

PORTFOLIO_FILE = '/Users/danieldragomir/antigravity/portfolio.csv'

updates = ['LQQ.PA', 'TVBETETF.RO']

if os.path.exists(PORTFOLIO_FILE):
    df = pd.read_csv(PORTFOLIO_FILE)
    
    # Ensure Current_Price is float
    # Note: Current_Price in CSV might be string or float depending on saves.
    # Usually pandas handles it.
    
    for sym in updates:
        mask = df['Symbol'] == sym
        if mask.any():
            # Get current price
            curr_price = df.loc[mask, 'Current_Price'].values[0]
            
            # If current price is missing/0, we might need to fetch it or use fallback
            if pd.isna(curr_price) or curr_price == 0:
                 # Hardcode fallbacks based on recent logs if needed, but let's try to use what's there
                 print(f"Warning: Current price for {sym} is {curr_price}. Skipping or setting 0.")
            else:
                 print(f"Setting {sym} Stop to Current Price: {curr_price}")
                 df.loc[mask, 'Trail_Stop'] = curr_price
                 df.loc[mask, 'Trail_Pct'] = 0
            
    df.to_csv(PORTFOLIO_FILE, index=False)
    print("Updated Stops to Current Price.")
