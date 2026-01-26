import yfinance as yf
from market_scanner import process_watchlist_ticker

def test_company_name(ticker):
    print(f"Testing {ticker}...")
    try:
        # Mock rates and vix since process_watchlist_ticker needs them
        res = process_watchlist_ticker(ticker, 20.0, {'USD': 1.0, 'EUR': 0.9, 'RON': 0.2})
        if res:
            name = res.get('Company_Name')
            print(f"  Result Name: '{name}'")
            if not name:
                print("  FAILURE: Name is empty")
            else:
                print("  SUCCESS: Name found")
        else:
            print("  FAILURE: No result returned")
    except Exception as e:
        print(f"  ERROR: {e}")

if __name__ == "__main__":
    test_company_name("AAPL")
    test_company_name("SXRZ") # Should fallback to SXRZ.DE
    test_company_name("ESS")  # One from user screenshot
