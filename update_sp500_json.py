import requests
import pandas as pd
import json
import io

url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
try:
    print(f"Fetching S&P 500 list from {url}...")
    r = requests.get(url)
    if r.status_code == 200:
        df = pd.read_csv(io.StringIO(r.text))
        tickers = df['Symbol'].tolist()
        # Clean tickers for yfinance (e.g. BRK.B -> BRK-B)
        tickers = [t.replace('.', '-') for t in tickers]
        
        # Save to JSON
        output_file = 'sp500_tickers.json'
        with open(output_file, 'w') as f:
            json.dump(tickers, f)
        print(f"✅ Successfully saved {len(tickers)} tickers to {output_file}")
        print(f"Sample: {tickers[:5]} ... {tickers[-5:]}")
    else:
        print(f"❌ Failed to fetch CSV: {r.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
