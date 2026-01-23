# -*- coding: utf-8 -*-
import requests
import pandas as pd
import time
import yfinance as yf
from bs4 import BeautifulSoup

# Global Cache for Finviz Data
_finviz_cache = {}

def get_finviz_data(ticker):
    """Preia datele fundamentale de pe Finviz (Target, ATR, Volatility) cu caching."""
    if ticker in _finviz_cache:
        # print(f"  [Cache] Finviz data for {ticker}") # Uncomment for debugging cache hits
        return _finviz_cache[ticker]

    data = {'Target': None, 'ATR': None, 'VolW': None, 'VolM': None}
    try:
        # Elimină sufixe pentru tickere europene (de ex: .DE)
        clean_ticker = ticker.split('.')[0]
        
        url = f"https://finviz.com/quote.ashx?t={clean_ticker}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            _finviz_cache[ticker] = data # Cache empty data on failure
            return data
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Găsim tabelul cu datele fundamentale
        rows = soup.find_all('tr', class_='table-dark-row')
        
        for row in rows:
            cells = row.find_all('td')
            for i, cell in enumerate(cells):
                txt = cell.get_text()
                if i + 1 >= len(cells): continue
                
                val_txt = cells[i+1].get_text().strip()
                
                if 'Target Price' in txt:
                    try:
                        if val_txt and val_txt != '-':
                            data['Target'] = float(val_txt.replace('$', '').replace(',', ''))
                    except: pass
                elif 'ATR' in txt: # ATR defaults to ATR 14 in finviz
                     try:
                        if val_txt and val_txt != '-':
                             data['ATR'] = float(val_txt)
                     except: pass
                elif 'Volatility' in txt:
                     # Format: "1.50% 2.05%" (Week Month)
                     try:
                         parts = val_txt.split()
                         if len(parts) >= 2:
                             data['VolW'] = float(parts[0].replace('%', ''))
                             data['VolM'] = float(parts[1].replace('%', ''))
                     except: pass
        
        # Extract Company Name from Title (Format: "TICKER - Company Name Stock Price...")
        try:
            page_title = soup.title.string
            if page_title and '-' in page_title:
                # Split by first hyphen
                parts = page_title.split('-', 1)
                if len(parts) > 1:
                    # Take the part after hyphen, remove "Stock Price..."
                    company_part = parts[1].strip()
                    # Finviz title usually: "AAPL - Apple Inc. Stock Price..."
                    # We want "Apple Inc."
                    # Let's split by "Stock Price" or quote or just take the first meaningful chunk
                    # Simple heuristic: take everything until "Stock" or "Quote"
                    for stopper in ["Stock Price", "Quote", "|"]:
                        if stopper in company_part:
                            company_part = company_part.split(stopper)[0].strip()
                    
                    if company_part:
                         data['Company'] = company_part
        except Exception as e:
            # print(f"  [Debug] Helper Title parse error: {e}")
            pass
        
        _finviz_cache[ticker] = data
        return data
    except Exception as e:
        print(f"  ⚠ Eroare Finviz pentru {ticker}: {str(e)[:50]}")
        return data

def get_scalar(series_val, default=0.0):
    """Helper pentru extragerea valorilor scalare."""
    try:
        if hasattr(series_val, 'item'):
            return series_val.item()
        return float(series_val)
    except:
        return default

def get_exchange_rates():
    """Descarcă ratele de schimb pentru conversia la EUR."""
    rates = {'EUR': 1.0, 'USD': 0.95, 'RON': 0.20, 'GBP': 1.15}
    try:
        # Download exchange rates relative to EUR (EURXYZ=X)
        tickers = "EURRON=X EURUSD=X EURGBP=X"
        data = yf.download(tickers, period="5d", auto_adjust=True, progress=False)
        
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                df = data['Close']
            else:
                df = data

            last = df.iloc[-1]
            
            if 'EURRON=X' in last and not pd.isna(last['EURRON=X']):
                 val = float(last['EURRON=X'])
                 if val > 0: rates['RON'] = 1.0 / val
            
            if 'EURUSD=X' in last and not pd.isna(last['EURUSD=X']):
                 val = float(last['EURUSD=X'])
                 if val > 0: rates['USD'] = 1.0 / val
            
            if 'EURGBP=X' in last and not pd.isna(last['EURGBP=X']):
                 val = float(last['EURGBP=X'])
                 if val > 0: rates['GBP'] = 1.0 / val
            
            print(f"Rates: 1 RON={rates['RON']:.3f}€, 1 USD={rates['USD']:.3f}€")
    except Exception as e:
        print(f"Eroare curs valutar: {e}. Folosim fallback.")
    return rates

def get_cached_watchlist_ticker(state, ticker):
    """Returnează datele cached pentru un ticker din watchlist, dacă există."""
    for item in state.get('watchlist', []):
        if item.get('Ticker') == ticker:
            return item
    return None

def is_fresh(ticker_data, ttl_hours=5):
    """Verifică dacă datele ticker-ului sunt fresh (mai noi de TTL)."""
    cached_at = ticker_data.get('_cached_at')
    if not cached_at:
        return False
    age_hours = (time.time() - cached_at) / 3600
    return age_hours < ttl_hours
