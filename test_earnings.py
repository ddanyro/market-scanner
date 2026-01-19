
import yfinance as yf
import datetime

def check_earnings(ticker_symbol):
    print(f"Checking earnings for {ticker_symbol}...")
    try:
        t = yf.Ticker(ticker_symbol)
        # Try different methods
        cal = t.calendar
        print("Calendar:", cal)
        
        # Check next earnings date
        if isinstance(cal, dict) and 'Earnings Date' in cal:
             print("Earnings Date (dict):", cal['Earnings Date'])
        elif hasattr(cal, 'get'):
             print("Earnings Date (get):", cal.get('Earnings Date'))
        
    except Exception as e:
        print(f"Error: {e}")

check_earnings("NVDA")
check_earnings("AAPL")
