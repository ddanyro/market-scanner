import pandas as pd
import requests

def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    try:
        # Use simple headers, Wikipedia usually allows this
        tables = pd.read_html(url)
        # The first table is usually the S&P 500 list
        df = tables[0]
        tickers = df['Symbol'].tolist()
        
        # Clean tickers (e.g. BRK.B -> BRK-B for yfinance)
        tickers = [t.replace('.', '-') for t in tickers]
        return tickers
    except Exception as e:
        print(f"Error: {e}")
        return []

tickers = get_sp500_tickers()
print(f"Fetched {len(tickers)} tickers.")
print(f"Sample: {tickers[:10]}")
