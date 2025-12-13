
import pandas as pd
import os

PORTFOLIO_FILE = '/Users/danieldragomir/antigravity/portfolio.csv'

updates = {
    'AMPX': {'pct': 33.00, 'stop': 8.41},
    'AMZN': {'pct': 8.10, 'stop': 213.58},
    'APLD': {'pct': 34.50, 'stop': 22.83},
    'DNN': {'pct': 17.00, 'stop': 2.37},
    'DVLT': {'pct': 30.00, 'stop': 1.33},
    'FCX': {'pct': 11.70, 'stop': 43.14},
    'LNG': {'pct': 6.50, 'stop': 195.59},
    'MARA': {'pct': 27.00, 'stop': 9.38},
    'MELI': {'pct': 11.40, 'stop': 1896.48},
    'META': {'pct': 8.40, 'stop': 619.85},
    'MSFT': {'pct': 6.50, 'stop': 460.30},
    'MSTR': {'pct': 26.00, 'stop': 146.80},
    'NVDA': {'pct': 12.00, 'stop': 165.44},
    'ORCL': {'pct': 18.00, 'stop': 184.75},
    'QBTS': {'pct': 32.00, 'stop': 19.80},
    'SMR': {'pct': 37.00, 'stop': 14.46},
    'SXRZ': {'pct': 12.00, 'stop': 295.8898},
    'TE': {'pct': 48.10, 'stop': 3.65},
    'TSM': {'pct': 10.00, 'stop': 282.58},
    'URG': {'pct': 30.00, 'stop': 1.00},
    'UUUU': {'pct': 28.00, 'stop': 11.97},
    # Tradeville symbols in CSV might be with suffix or without depending on how they are stored
    'TVBETETF.RO': {'pct': 0.00, 'stop': 9.2392},
    'LQQ.PA': {'pct': 20.00, 'stop': 1664.8575}
}

if os.path.exists(PORTFOLIO_FILE):
    df = pd.read_csv(PORTFOLIO_FILE)
    print(f"Loaded portfolio with {len(df)} rows.")
    
    # Ensure columns exist
    if 'Trail_Pct' not in df.columns: df['Trail_Pct'] = 0.0
    if 'Trail_Stop' not in df.columns: df['Trail_Stop'] = 0.0
    
    # Update logic
    for sym, data in updates.items():
        # Try finding symbol case-insensitive
        mask = df['Symbol'].str.upper() == sym.upper()
        
        # Special handling for SXRZ (maybe just SXRZ without .DE in portfolio file)
        if not mask.any() and '.' in sym:
             base = sym.split('.')[0]
             mask = df['Symbol'].str.upper() == base.upper()
        
        if mask.any():
            print(f"Updating {sym} -> Trail {data['pct']}%, Stop {data['stop']}")
            df.loc[mask, 'Trail_Pct'] = data['pct']
            df.loc[mask, 'Trail_Stop'] = data['stop']
        else:
            print(f"Warning: Symbol {sym} not found in portfolio.csv")

    df.to_csv(PORTFOLIO_FILE, index=False)
    print("Portfolio updated successfully.")
else:
    print("Portfolio file not found.")
