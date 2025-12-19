import yfinance as yf
import pandas as pd
import argparse
import sys
import datetime
import time
import os
import requests
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
import math
import yfinance as yf
# New imports for encryption
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from base64 import b64encode
import json
from market_scanner_analysis import generate_market_analysis  # Import modul analiză

STATE_FILE = "dashboard_state.json"
MARKET_HISTORY_FILE = "market_history.json"

def encrypt_for_js(data, password):
    """Criptează datele (JSON string) folosind AES-CBC compatibil cu CryptoJS."""
    # 1. Generate Salt and Key
    salt = get_random_bytes(16)
    # Key derivation: PBKDF2 using SHA256 (default for many) or SHA1. 
    # CryptoJS default PBKDF2 uses SHA1! We must match. Or specify SHA256 in JS.
    # Let's use SHA256 for better security and specify it in JS.
    from Crypto.Hash import SHA256
    key = PBKDF2(password, salt, dkLen=32, count=1000, hmac_hash_module=SHA256)
    
    # 2. Encrypt
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    
    # 3. Return format
    return json.dumps({
        "salt": b64encode(salt).decode('utf-8'),
        "iv": b64encode(iv).decode('utf-8'),
        "ciphertext": b64encode(ciphertext).decode('utf-8')
    })

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_finviz_data(ticker):
    """Preia datele fundamentale de pe Finviz (Target, ATR, Volatility)."""
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
        
        return data
    except Exception as e:
        print(f"  ⚠ Eroare Finviz pentru {ticker}: {str(e)[:50]}")
        return data

def load_portfolio(filename='portfolio.csv'):
    """Încarcă portofoliul din CSV."""
    if not os.path.exists(filename):
        print(f"Fișierul {filename} nu a fost găsit.")
        return pd.DataFrame()
    
    df = pd.read_csv(filename)
    # Normalizează coloanele (lowercase) pentru a evita KeyErrors
    df.columns = [c.strip().lower() for c in df.columns]
    return df

def load_watchlist(filename='watchlist.txt'):
    """Încarcă lista de tickere de urmărit."""
    if not os.path.exists(filename):
        print(f"Fișierul {filename} nu a fost găsit.")
        return []
    
    with open(filename, 'r') as f:
        tickers = [line.strip().upper() for line in f if line.strip()]
    return list(set(tickers))

def calculate_atr(df, period=14):
    """Calculează Average True Range (ATR)."""
    if len(df) < period + 1:
        return None
    
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)
    
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr

def calculate_rsi(df, period=14):
    """Calculează RSI."""
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_sma(df, period):
    """Calculează Simple Moving Average."""
    return df['Close'].rolling(window=period).mean()

def get_vix_data():
    """Descarcă datele pentru VIX (volatilitate)."""
    try:
        vix = yf.Ticker("^VIX")
        hist = vix.history(period="5d")
        if hist.empty:
            return None
        current_vix = hist['Close'].iloc[-1]
        return current_vix
    except Exception as e:
        print(f"Eroare la preluarea VIX: {e}")
        return None

# The original HISTORY_FILE definition was here, now it's MARKET_HISTORY_FILE at the top.
# import json # This import is already at the top.

# HISTORY_FILE = "market_history.json" # This is now MARKET_HISTORY_FILE at the top.

def load_market_history():
    if os.path.exists(MARKET_HISTORY_FILE):
        try:
            with open(MARKET_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_market_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Eroare salvare istoric: {e}")

def get_market_indicators():
    """Preia indicatori volum și sentiment, cu persistență locală."""
    indicators = {}
    history_db = load_market_history()
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Lista de indicatori cu ticker-ele lor Yahoo Finance și thresholds
    tickers_map = {
        'VIX3M': '^VIX3M',      # VIX pe 3 luni
        'VIX': '^VIX',          # VIX standard
        'VIX1D': '^VIX1D',      # VIX 1 zi (dacă există)
        'VIX9D': '^VIX9D',      # VIX 9 zile
        'VXN': '^VXN',          # Nasdaq VIX
        'LTV': '^LTV',          # CBOE Left Tail Volatility
        'SKEW': '^SKEW',        # CBOE SKEW
        'MOVE': '^MOVE',        # MOVE Index (bond volatility)
        'GVZ': '^GVZ',          # Gold Volatility
        'OVX': '^OVX',          # Oil Volatility
        'SPX': '^GSPC',         # S&P 500
    }
    
    # Thresholds (aceleași ca înainte, le păstrăm)
    thresholds = {
        'VIX3M': (14, 20), 'VIX': (15, 20), 'VIX1D': (12, 30), 'VIX9D': (12, 18), 'VXN': (15, 25),
        'LTV': (10, 13), 'SKEW': (135, 150), 'MOVE': (80, 120), 'GVZ': (17, 22), 'OVX': (25, 35),
        'SPX': (None, None)
    }
    
    # Definițiile nivelelor (copiate din codul existent pentru consistență)
    threshold_levels = {
        'VIX3M': [(14, 'perfect 14'), (20, '14 normal 20'), (30, '20 tensiune 30'), (999, '30 panica')],
        'VIX': [(15, 'perfect 15'), (20, '15 normal 20'), (30, '20 teama 30'), (999, '30 panica')],
        'VIX1D': [(12, 'perfect 12'), (30, '12 normal 30'), (999, '30 panica')],
        'VIX9D': [(12, 'perfect 12'), (18, '12 normal 18'), (25, '18 teama 25'), (999, '25 panica')],
        'VXN': [(15, 'perfect 15'), (25, '15 normal 25'), (35, '25 teama 35'), (999, '35 panica')],
        'LTV': [(10, 'perfect 10'), (13, '10 normal 13'), (999, '13 panica')],
        'SKEW': [(100, 'perfect 100'), (120, '100 precaut/vix/ltv 120'), (135, '120 usor ridicat/vix/ltv 135'), (150, '135 teama 150'), (999, '150 panica')],
        'MOVE': [(80, 'perfect 80'), (120, '80 moderat 120'), (150, '120 teama 150'), (999, '150 panica')],
        'GVZ': [(17, 'perfect 22'), (22, '17 teama 22'), (999, '22 panica')],
        'OVX': [(25, 'perfect 25'), (35, '25 teama 35'), (999, '35 panica')],
    }
    
    for name, ticker in tickers_map.items():
        try:
            time.sleep(0.5)
            data = yf.Ticker(ticker)
            # Încercăm să luăm istoric scurt pentru update, sau lung dacă nu avem local
            hist = data.history(period="35d")
            
            current_val = None
            
            # 1. Update Persistent History
            if not hist.empty:
                # Iterăm prin ultimele zile și le adăugăm în DB
                # Yahoo returnează index datetime, convertim la string YYYY-MM-DD
                for date_idx, row in hist.iterrows():
                    d_str = date_idx.strftime('%Y-%m-%d')
                    val = float(row['Close'])
                    if not pd.isna(val):
                        # Init list if needed
                        if name not in history_db: history_db[name] = []
                        
                        # Check exist
                        existing = next((x for x in history_db[name] if x['date'] == d_str), None)
                        if existing:
                            existing['value'] = val
                        else:
                            history_db[name].append({'date': d_str, 'value': val})
                
                # Sort și Trim (ultimele 60 zile)
                if name in history_db:
                    history_db[name].sort(key=lambda x: x['date'])
                    history_db[name] = history_db[name][-60:]
            
            # 2. Folosim datele din History DB pentru afișare
            if name in history_db and history_db[name]:
                data_points = [x['value'] for x in history_db[name]]
                current = data_points[-1]
                
                if len(data_points) >= 2:
                    change = current - data_points[-2]
                else:
                    change = 0.0
                
                sparkline_data = data_points[-30:] # Last 30 points
                
                # Logică Status/Descriere
                if name in threshold_levels:
                    levels = threshold_levels[name]
                    description = levels[-1][1]
                    status = "Panic"
                    for threshold, desc in levels:
                        if current < threshold:
                            description = desc
                            if 'perfect' in desc.lower(): status = "Perfect"
                            elif 'normal' in desc.lower() or 'precaut' in desc.lower() or 'ridicat' in desc.lower() or 'moderat' in desc.lower(): status = "Normal"
                            elif 'tensiune' in desc.lower() or 'teama' in desc.lower(): status = "Tension"
                            else: status = "Panic"
                                
                            break
                else:
                    status = "Normal"
                    description = ""
                
                indicators[name] = {
                    'value': round(current, 2),
                    'change': round(change, 2),
                    'status': status,
                    'description': description,
                    'sparkline': sparkline_data
                }
            else:
                print(f"  ⚠ {name}: Nu există date (nici Yahoo, nici Local)")
                
        except Exception as e:
            print(f"  ⚠ Eroare {name}: {str(e)[:40]}")
    
    # Salvarea istoricului actualizat
    save_market_history(history_db)
    
    # Crypto Fear & Greed Index (separat, dar îl putem adăuga și pe el în DB dacă vrem, momentan e ok așa)
    try:
        # Cerem ultimele 35 de zile pentru istoric
        response = requests.get('https://api.alternative.me/fng/?limit=35', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                current_data = data['data'][0]
                value = int(current_data['value'])
                classification = current_data['value_classification']  # Extreme Fear, Fear, Neutral, Greed, Extreme Greed
                
                # Determinăm status și description
                # Determinăm status și description (User Formula)
                if value < 24:
                    status = 'Panic'
                    description = 'panica 24'
                elif value < 49:
                    status = 'Tension'
                    description = '24 frica 49'
                elif value < 74:
                    status = 'Normal'
                    description = '49 lacomie 74'
                else:
                    status = 'Perfect'
                    description = '74 lacomie extrema'
                
                # Change (diferența față de ziua precedentă)
                if len(data['data']) > 1:
                    prev_value = int(data['data'][1]['value'])
                    change = value - prev_value
                else:
                    change = 0
                
                # Sparkline data (ultimele 30 zile, inversat pentru cronologie vechi->nou)
                sparkline_raw = data['data'][:30]
                sparkline_data = [int(item['value']) for item in sparkline_raw][::-1]
                
                indicators['Crypto Fear'] = {
                    'value': value,
                    'change': change,
                    'status': status,
                    'description': description,
                    'sparkline': sparkline_data
                }
    except Exception as e:
        print(f"  ⚠ Eroare Crypto Fear: {str(e)[:40]}")
    
    return indicators

def get_macro_explanations():
    """Generează secțiunea de explicații pentru indicatori macroeconomici."""
    return """
    <div class="macro-explainer" style="background: #222; padding: 20px; border-radius: 8px; margin-top: 20px; border: 1px solid #444; color: #e0e0e0;">
        <h3 style="color: #4db6ac; border-bottom: 1px solid #555; padding-bottom: 10px; margin-top: 0;">📚 Glosar: Indicatori Macroeconomici Cheie & Impact</h3>
        <p style="font-size: 0.9rem; color: #aaa; margin-bottom: 20px;">Ghid pentru înțelegerea evenimentelor din Calendarul Economic.</p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            
            <!-- Building Permits -->
            <div class="macro-card" style="background: #2d2d2d; padding: 15px; border-radius: 6px; border: 1px solid #333;">
                <h4 style="color: #ffb74d; margin-top: 0;">🏗️ Building Permits (Autorizații Construcție)</h4>
                <p style="font-size: 0.9rem;"><strong>Ce este:</strong> Un indicator "leading" (anticipativ) care arată cererea viitoare în sectorul imobiliar.</p>
                <p style="font-size: 0.9rem; margin-bottom: 0;"><strong>Impact Piață:</strong> 
                   <br><span style="color: #4caf50;">Cifre Mari:</span> Economie robustă, încredere consumatori.
                   <br><span style="color: #f44336;">Cifre Mici:</span> Semnal de recesiune (construcțiile sunt primele afectate de dobânzi mari).
                </p>
            </div>

            <!-- CPI -->
            <div class="macro-card" style="background: #2d2d2d; padding: 15px; border-radius: 6px; border: 1px solid #333;">
                <h4 style="color: #ef5350; margin-top: 0;">🔥 CPI (Consumer Price Index)</h4>
                <p style="font-size: 0.9rem;"><strong>Ce este:</strong> Măsura principală a inflației (coșul de cumpărături). Cel mai urmărit indicator de către Fed.</p>
                <p style="font-size: 0.9rem; margin-bottom: 0;"><strong>Impact Piață:</strong> 
                   <br><span style="color: #f44336;">Peste Așteptări:</span> Fed crește dobânzile -> Acțiunile (Tech) scad, USD crește.
                   <br><span style="color: #4caf50;">Sub Așteptări:</span> Fed poate tăia dobânzile -> Raliu pe burse.
                </p>
            </div>

            <!-- NFP -->
            <div class="macro-card" style="background: #2d2d2d; padding: 15px; border-radius: 6px; border: 1px solid #333;">
                <h4 style="color: #64b5f6; margin-top: 0;">👥 NFP (Non-Farm Payrolls)</h4>
                <p style="font-size: 0.9rem;"><strong>Ce este:</strong> Numărul de joburi noi create în SUA (lunar). Arată sănătatea motorului economic.</p>
                <p style="font-size: 0.9rem; margin-bottom: 0;"><strong>Impact Piață:</strong> 
                   <br><span style="color: #4caf50;">Joburi Multe:</span> Economie puternică (dar risc de inflație).
                   <br><span style="color: #f44336;">Joburi Puține:</span> Risc de recesiune -> Fed trebuie să taie dobânzile.
                </p>
            </div>
            
             <!-- FOMC -->
            <div class="macro-card" style="background: #2d2d2d; padding: 15px; border-radius: 6px; border: 1px solid #333;">
                <h4 style="color: #ba68c8; margin-top: 0;">🏛️ FOMC (Ședința Fed)</h4>
                <p style="font-size: 0.9rem;"><strong>Ce este:</strong> Decizia privind dobânda de referință. "Costul banilor".</p>
                <p style="font-size: 0.9rem; margin-bottom: 0;"><strong>Impact Piață:</strong> 
                   <br>Dobânzi Mari = Lichiditate scăzută = Acțiuni jos.
                   <br>Pivot (Tăiere) = Lichiditate = Acțiuni sus (Moon).
                </p>
            </div>

        </div>
    </div>
    """

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
        # EURRON=X -> 1 EUR = x RON
        # EURUSD=X -> 1 EUR = x USD
        # EURGBP=X -> 1 EUR = x GBP
        tickers = "EURRON=X EURUSD=X EURGBP=X"
        data = yf.download(tickers, period="5d", progress=False)
        
        if not data.empty:
            # Handle MultiIndex columns if present
            if isinstance(data.columns, pd.MultiIndex):
                # We want 'Close' prices
                df = data['Close']
            else:
                df = data

            last = df.iloc[-1]
            
            # 1 EUR = val RON => 1 RON = 1/val EUR
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

def process_portfolio_ticker(row, vix_value, rates):
    """Procesează un ticker din portofoliu cu date de ownership (Conversie EUR)."""
    try:
        ticker = row.get('symbol', 'UNKNOWN').upper()
        shares = float(row.get('shares', 0))
        buy_price_native = float(row.get('buy_price', 0))
        # Default trail_pct to 15 if missing
        trail_pct = float(row.get('trail_pct', 15))
        
        print(f"Procesare: {ticker}")
        
        # Detect Currency
        currency = 'USD' # Default
        if '.RO' in ticker: currency = 'RON'
        elif '.PA' in ticker or '.DE' in ticker or '.AS' in ticker: currency = 'EUR'
        elif '.L' in ticker: currency = 'GBP'
        
        rate = rates.get(currency, rates['USD'])
        if currency == 'EUR': rate = 1.0
        
        # Convert Buy Price to EUR
        buy_price = buy_price_native * rate
        
        # Ia target-ul DOAR de pe Finviz (USD usually)
        finviz_data = get_finviz_data(ticker)
        target_usd = finviz_data.get('Target')
        
        target = None
        if target_usd:
            # Finviz e mereu USD? Nu neapărat. Dar pt US stocks da.
            # Dacă e stoc european, Finviz poate lipsi sau e în moneda locală?
            # Presupunem că Finviz dă în aceeași monedă ca ticker-ul (dacă îl găsește).
            target = target_usd * rate
            print(f"  → Target Finviz: €{target:.2f} (calc)")
        else:
            print(f"  → Target: N/A")
            
        # Volatility Data
        finviz_atr = finviz_data.get('ATR')
        vol_w = finviz_data.get('VolW') 
        vol_m = finviz_data.get('VolM')
        
        time.sleep(2)
        df = yf.download(ticker, period="1y", progress=False)
        
        # Retry with European suffixes if base ticker fails (common for IBKR ETFs like SXRZ)
        if df.empty:
            suffixes = ['.DE', '.PA', '.L', '.AS', '.MI', '.MC']
            print(f"  ⚠️ Ticker {ticker} not found. Trying suffixes...")
            for s in suffixes:
                alt_ticker = f"{ticker}{s}"
                print(f"    Trying {alt_ticker}...")
                time.sleep(1)
                df_alt = yf.download(alt_ticker, period="1y", progress=False)
                if not df_alt.empty:
                    print(f"    ✅ Found data for {alt_ticker}!")
                    df = df_alt
                    # Update currency based on new suffix
                    if '.DE' in s or '.PA' in s or '.AS' in s or '.MI' in s or '.MC' in s:
                        currency = 'EUR'
                    elif '.L' in s:
                        currency = 'GBP'
                    
                    # Update rate
                    rate = rates.get(currency, rates['USD'])
                    if currency == 'EUR': rate = 1.0
                    
                    # Also re-check Finviz target with new ticker? No, Finviz uses US tickers mostly.
                    break
        
        if df.empty:
            print(f"  ⚠️ Nu există date Yahoo Finance pentru {ticker} (nici cu sufixe) - folosim date parțiale din IBKR")
            # Returnăm date parțiale bazate pe informațiile din IBKR
            current_price = buy_price  # Fallback: presupunem că prețul curent = buy price
            investment = buy_price * shares
            current_value = current_price * shares
            profit = 0.0
            profit_pct = 0.0
            
            # Target și profit maxim
            if target:
                # Avem target de la Finviz
                max_profit = (target - buy_price) * shares
                target_display = round(target, 2)
            else:
                # Fără date Yahoo și fără target Finviz -> Nu estimăm
                max_profit = None
                target_display = None
            
            result = {
                'Symbol': ticker,
                'Shares': int(shares),
                'Current_Price': round(current_price, 2),
                'Buy_Price': round(buy_price, 2),
                'Target': target_display,
                'Trail_Stop': round(buy_price * 0.85, 2),  # Default 15% trailing
                'Suggested_Stop': round(buy_price * 0.90, 2),  # Conservative
                'Trail_Pct': trail_pct,
                'Investment': round(investment, 2),
                'Current_Value': round(current_value, 2),
                'Profit': round(profit, 2),
                'Profit_Pct': round(profit_pct, 2),
                'Max_Profit': round(max_profit, 2) if max_profit else None,
                'Status': 'N/A',
                'RSI': 0,
                'RSI_Status': 'N/A',
                'Trend': 'No Data',
                'VIX_Tag': 'Normal',
                'Sparkline': [],
                'Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            return result
        
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df.columns = df.columns.droplevel(1)
            except:
                pass
        
        # Fetch detailed info from Yahoo (Consensus) - Inserted Logic
        consensus = "-"
        analysts_count = 0
        try:
           yt = yf.Ticker(ticker)
           info = yt.info
           # Dacă info e gol sau fail
           if info:
               consensus = info.get('recommendationKey', '-').replace('_', ' ').title()
               analysts_count = info.get('numberOfAnalystOpinions', 0)
        except Exception as e:
           # print(f"  Warning: Could not fetch info for {ticker}: {e}")
           pass

        df['ATR'] = calculate_atr(df)
        df['RSI'] = calculate_rsi(df)
        df['SMA_50'] = calculate_sma(df, 50)
        df['SMA_200'] = calculate_sma(df, 200)
        
        last_row = df.iloc[-1]
        
        current_price_native = get_scalar(last_row['Close'])
        current_price = current_price_native * rate # EUR
        
        # Convert ATR for stops
        last_atr_native = get_scalar(last_row['ATR'])
        if pd.isna(last_atr_native): last_atr_native = 0.0
        last_atr = last_atr_native * rate # EUR
        
        last_rsi = get_scalar(last_row['RSI'])
        sma_50 = get_scalar(last_row['SMA_50']) * rate
        sma_200 = get_scalar(last_row['SMA_200']) * rate
        
        # Extrage ultimele 30 zile pentru sparkline (conversie si aici? nu, trendul e la fel, dar valorile difera)
        # Sparkline e doar vizual, nu contează scara, dar hai să convertim pt consistență dacă afișăm tooltip
        sparkline_data = df['Close'].tail(30).tolist()
        sparkline_data = [round(float(x) * rate, 2) for x in sparkline_data if not pd.isna(x)]
        
        # Calcule pentru portofoliu (Toate în EUR)
        current_value = current_price * shares
        investment = buy_price * shares
        profit = current_value - investment
        profit_pct = ((current_price - buy_price) / buy_price) * 100 if buy_price != 0 else 0
        
        # Stop loss logic: Prioritate Manual > IBKR Order > Calculated
        trail_stop_manual = float(row.get('trail_stop', 0))
        trail_stop_ibkr = float(row.get('trail_stop_ibkr', 0))
        
        if trail_stop_manual > 0:
            # Avem stop manual setat în CSV (deja în moneda potrivită sau EUR dacă userul a pus direct)
            # Dacă tickerul e EUR (SXRZ.DE), rate e 1. Deci input 252.1 devine 252.1.
            trail_stop_price = trail_stop_manual * rate
        elif trail_stop_ibkr > 0:
            # Avem stop din IBKR Orders (dacă ar merge Flex)
            trail_stop_price = trail_stop_ibkr * rate
        elif trail_pct > 0:
            # Fallback: calculăm dinamic din procent
            trail_stop_price = current_price * (1 - trail_pct / 100)
        else:
            trail_stop_price = 0 # Disabled/N/A
        
        # Suggested Stop bazat pe ATR (2x ATR sub preț curent)
        suggested_stop_atr = current_price - (2 * last_atr)
        
        # Target Price: Finviz (prioritate) sau Estimare Tehnică
        if target:
            # Avem target de la Finviz
            max_profit = (target - buy_price) * shares
            target_display = round(target, 2)
            target_source = "Finviz"
        else:
            # Estimare tehnică când nu avem target Finviz
            technical_target = None
            
            # Metodă 1: 52-week high (rezistență majoră)
            high_52w = df['High'].tail(252).max() * rate  # ~252 zile = 1 an trading
            
            # Metodă 2: ATR-based target (doar dacă trendul e bullish)
            atr_target = None
            if current_price > sma_200:  # Trend bullish
                atr_target = current_price + (3 * last_atr)  # Optimist: +3 ATR
            
            # Alegem cel mai bun target tehnic
            if atr_target and high_52w:
                # Dacă avem ambele, luăm maximul (mai optimist)
                technical_target = max(atr_target, high_52w)
                target_source = "Technical (ATR+52W)"
            elif high_52w:
                technical_target = high_52w
                target_source = "Technical (52W High)"
            elif atr_target:
                technical_target = atr_target
                target_source = "Technical (ATR)"
            
            # Validare: target-ul trebuie să fie > current price
            if technical_target and technical_target > current_price:
                target = technical_target
                max_profit = (target - buy_price) * shares
                target_display = round(target, 2)
                print(f"  → Target {target_source}: €{target_display:.2f}")
            else:
                # Nu putem estima un target valid
                max_profit = None
                target_display = None
                target_source = "N/A"
        
        # VIX Interpretation
        vix_regime = "Normal"
        if vix_value and vix_value > 20: vix_regime = "Ridicat"
        if vix_value and vix_value > 30: vix_regime = "Extrem"

        # RSI Interpretation
        rsi_status = "Neutral"
        if last_rsi > 70: rsi_status = "Overbought"
        elif last_rsi < 30: rsi_status = "Oversold"
        
        # Trend Interpretation
        trend = "Neutral"
        if current_price > sma_200:
            if current_price > sma_50:
                trend = "Strong Bullish"
            else:
                trend = "Bullish Pullback"
        elif current_price < sma_200:
            if current_price < sma_50:
                trend = "Strong Bearish"
            else:
                trend = "Bearish Rally"

        result = {
            'Symbol': ticker,
            'Shares': int(shares),
            'Current_Price': round(current_price, 2),
            'Price_Native': round(current_price_native, 2),
            'Buy_Price': round(buy_price, 2),
            'Target': target_display,  # None dacă nu există
            'Trail_Stop': round(trail_stop_price, 2),
            'Suggested_Stop': round(suggested_stop_atr, 2),
            'Finviz_ATR': finviz_atr,
            'Vol_W': vol_w,
            'Vol_M': vol_m,
            'Trail_Pct': trail_pct,
            'Investment': round(investment, 2),
            'Current_Value': round(current_value, 2),
            'Profit': round(profit, 2),
            'Profit_Pct': round(profit_pct, 2),
            'Max_Profit': round(max_profit, 2) if max_profit else None,
            'Consensus': consensus,
            'Analysts': analysts_count,
            'Status': rsi_status,  # RSI Status (Overbought/Oversold/Neutral)
            'RSI': round(last_rsi, 2),  # Păstrat pentru Watchlist
            'RSI_Status': rsi_status,
            'Trend': trend,
            'VIX_Tag': vix_regime,
            'Sparkline': sparkline_data,
            'Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return result
        
    except Exception as e:
        print(f"Eroare procesare {row.get('symbol', '?')}: {e}")
        return None

def process_watchlist_ticker(ticker, vix_value, rates):
    """Procesează un ticker din watchlist (fără date de ownership)."""
    try:
        time.sleep(2)
        
        # Detect Currency
        currency = 'USD'
        if '.RO' in ticker: currency = 'RON'
        elif '.PA' in ticker or '.DE' in ticker or '.AS' in ticker: currency = 'EUR'
        elif '.L' in ticker: currency = 'GBP'
        
        rate = rates.get(currency, rates['USD'])
        if currency == 'EUR': rate = 1.0
        
        df = yf.download(ticker, period="1y", progress=False)
        
        if df.empty:
            print(f"Nu există date pentru {ticker}")
            return None
        
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df.columns = df.columns.droplevel(1)
            except:
                pass
            
        df['ATR'] = calculate_atr(df)
        df['RSI'] = calculate_rsi(df)
        df['SMA_50'] = calculate_sma(df, 50)
        df['SMA_200'] = calculate_sma(df, 200)
        
        # Extrage ultimele 30 zile pentru sparkline
        sparkline_data = df['Close'].tail(30).tolist()
        sparkline_data = [round(float(x) * rate, 2) for x in sparkline_data if not pd.isna(x)]
        
        last_row = df.iloc[-1]
        
        last_close_native = get_scalar(last_row['Close']) 
        last_close = last_close_native * rate
        last_atr = get_scalar(last_row['ATR']) * rate
        if pd.isna(last_atr): last_atr = 0.0
        
        last_rsi = get_scalar(last_row['RSI'])
        sma_50 = get_scalar(last_row['SMA_50']) * rate
        sma_200 = get_scalar(last_row['SMA_200']) * rate
        
        # Preluare Target din Finviz
        # Preluare date din Finviz (Target + Volatility)
        target_val = None
        finviz_atr = None
        vol_w = None
        vol_m = None
        
        try:
            finviz_data = get_finviz_data(ticker)
            target_usd = finviz_data.get('Target')
            finviz_atr = finviz_data.get('ATR')
            vol_w = finviz_data.get('VolW')
            vol_m = finviz_data.get('VolM')
            
            if target_usd:
                target_val = target_usd * rate
        except Exception:
            pass

        stop_loss_dist = 2 * last_atr
        suggested_stop = last_close - stop_loss_dist
        
        vix_regime = "Normal"
        if vix_value and vix_value > 20: vix_regime = "Ridicat"
        if vix_value and vix_value > 30: vix_regime = "Extrem"

        rsi_status = "Neutral"
        if last_rsi > 70: rsi_status = "Overbought"
        elif last_rsi < 30: rsi_status = "Oversold"
        
        trend = "Neutral"
        if last_close > sma_200:
            if last_close > sma_50:
                trend = "Strong Bullish"
            else:
                trend = "Bullish Pullback"
        elif last_close < sma_200:
            if last_close < sma_50:
                trend = "Strong Bearish"
            else:
                trend = "Bearish Rally"

        if target_val and last_close > 0:
            pct_to_target = ((target_val - last_close) / last_close) * 100
        else:
            pct_to_target = None

        # Fetch detailed info from Yahoo
        consensus = "-"
        analysts_count = 0
        industry = "-"
        
        try:
           # Folosim yf.Ticker pentru info detaliat
           yt = yf.Ticker(ticker)
           info = yt.info
           consensus = info.get('recommendationKey', '-').replace('_', ' ').title() # ex: Strong Buy
           analysts_count = info.get('numberOfAnalystOpinions', 0)
           industry = info.get('industry', '-')
           sector = info.get('sector', '-')
           # Scurtăm industria dacă e prea lungă
           if len(industry) > 20: industry = industry[:17] + "..."
        except:
           pass

        result = {
            'Ticker': ticker,
            'Price': round(last_close, 2),
            'Price_Native': round(last_close_native, 2),
            'Target': round(target_val, 2) if target_val else None,
            'Pct_To_Target': round(pct_to_target, 2) if pct_to_target is not None else None,
            'Consensus': consensus,
            'Analysts': analysts_count,
            'Industry': industry,
            'Sector': sector,
            'Trend': trend,
            'RSI': round(last_rsi, 2),
            'RSI_Status': rsi_status,
            'ATR_14': round(last_atr, 2),
            'Finviz_ATR': finviz_atr,
            'Vol_W': vol_w,
            'Vol_M': vol_m,
            'Stop_Loss': round(suggested_stop, 2),
            'SMA_50': round(sma_50, 2),
            'SMA_200': round(sma_200, 2),
            'VIX_Tag': vix_regime,
            'Sparkline': sparkline_data,
            'Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return result
        
    except Exception as e:
        print(f"Eroare procesare {ticker}: {e}")
        return None
    except Exception as e:
        print(f"Eroare procesare {ticker}: {e}")
        return None

# --- Economic Cycle Logic ---
def determine_economic_cycle():
    """
    Deduce faza economică bazată pe Yield Curve și Market Trend.
    Phases: Recovery -> Expansion -> Slowdown -> Recession
    """
    try:
        # 1. Market Trend (SP500)
        spx = yf.Ticker("^GSPC")
        hist = spx.history(period="1y")
        if hist.empty: return "Expansion", "Slowdown" # Default safe
        
        price = hist['Close'].iloc[-1]
        sma_200 = hist['Close'].mean() # Approx SMA200 (using 1y avg)
        
        market_trend = "Bull" if price > sma_200 else "Bear"
        
        # 2. Yield Curve (10Y - 3M) -> Proxy for Recession prob
        # ^TNX = 10 Year Yield (index format, e.g. 4.50)
        # ^IRX = 13 Week Yield (index format)
        tnx = yf.Ticker("^TNX").history(period="5d")
        irx = yf.Ticker("^IRX").history(period="5d")
        
        if not tnx.empty and not irx.empty:
            y10 = tnx['Close'].iloc[-1]
            y3m = irx['Close'].iloc[-1]
            spread = y10 - y3m
        else:
            spread = 0.5 # Default normal
            
        # Logic Matrix
        phase = "Expansion"
        
        if market_trend == "Bear":
            if spread < -0.5: phase = "Recession"
            else: phase = "Slowdown"
        else:
            # Bull Market
            if spread < 0: 
                phase = "Late Expansion" # Or Slowdown warning
            elif spread > 1.2: # Steep curve
                phase = "Recovery"
            else:
                phase = "Expansion"
                
        # Simplify to 4 phases
        if phase == "Late Expansion": phase = "Slowdown"
        
        # Next Phase Logic
        cycle_order = ["Recovery", "Expansion", "Slowdown", "Recession"]
        try:
            curr_idx = cycle_order.index(phase)
            next_phase = cycle_order[(curr_idx + 1) % 4]
        except:
            next_phase = "Unknown"
            
        print(f"Economic Cycle: {phase} (Spread: {spread:.2f}, Trend: {market_trend})")
        return phase, next_phase
        
    except Exception as e:
        print(f"Error determining cycle: {e}")
        return "Expansion", "Slowdown"

def assess_stock_fitness(sector, phase):
    """
    Verifică dacă sectorul este favorizat în faza dată.
    """
    if not sector: return "N/A"
    
    # Mapping simplificat Yahoo Finance Sectors -> Cycle
    # Recovery: Materials, Real Estate, Industrials, Financials, Cons Cyclical
    # Expansion: Tech, Industrials, Financials, Communication, Cons Cyclical
    # Slowdown: Energy, Healthcare, Cons Defensive (Staples), Utilities
    # Recession: Utilities, Cons Defensive, Healthcare
    
    favored = []
    if phase == "Recovery":
        favored = ["Basic Materials", "Real Estate", "Industrials", "Financial Services", "Consumer Cyclical"]
    elif phase == "Expansion":
        favored = ["Technology", "Industrials", "Financial Services", "Communication Services", "Consumer Cyclical"]
    elif phase == "Slowdown":
        favored = ["Energy", "Healthcare", "Consumer Defensive", "Utilities"]
    elif phase == "Recession":
        favored = ["Utilities", "Consumer Defensive", "Healthcare"]
        
    for fav in favored:
        if fav in sector: return "✅" # Good Fit
    
    return "⚠️" # Caution/Neutral
def generate_html_dashboard(portfolio_df, watchlist_df, market_indicators, filename="index.html", full_state=None):
    if full_state is None: full_state = {}
    """Generează dashboard HTML cu 2 tab-uri și indicatori de piață."""
    
    css = """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #e0e0e0; padding: 20px; }
        h1 { text-align: center; color: #4dabf7; margin-bottom: 10px; }
        .meta { text-align: center; margin-bottom: 30px; color: #888; font-size: 0.9rem; }
        
        /* Tabs */
        /* Header & Menu */
        .header-bar { display: flex; align-items: center; background-color: #2d2d2d; padding: 15px 20px; border-radius: 10px; margin-bottom: 20px; position: relative; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
        .hamburger { font-size: 24px; cursor: pointer; color: #4dabf7; margin-right: 20px; user-select: none; padding: 5px; }
        .app-title { font-size: 1.5rem; font-weight: bold; color: #e0e0e0; flex-grow: 1; }
        
        .menu-dropdown { 
            position: absolute; top: 70px; left: 20px; background-color: #333; border-radius: 8px; 
            box-shadow: 0 8px 20px rgba(0,0,0,0.6); display: none; z-index: 1000; min-width: 220px; overflow: hidden; border: 1px solid #444;
        }
        .menu-dropdown.show { display: block; animation: slideDown 0.2s ease-out; }
        
        .menu-item { padding: 15px 20px; cursor: pointer; color: #e0e0e0; border-bottom: 1px solid #444; transition: background 0.2s; font-size: 1rem; display: flex; align-items: center; gap: 10px; }
        .menu-item:hover { background-color: #4dabf7; color: white; }
        .menu-item:last-child { border-bottom: none; }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; animation: fadeIn 0.4s; }
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        
        table { width: 100%; border-collapse: collapse; margin-top: 0; box-shadow: none; background-color: #2d2d2d; }
        .table-container { width: 100%; overflow-x: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.3); border-radius: 8px; margin-top: 20px; }
        
        th, td { padding: 12px 10px; text-align: left; border-bottom: 1px solid #444; font-size: 0.85rem; white-space: nowrap; vertical-align: middle; }
        th { background-color: #333; color: #fff; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; position: sticky; top: 0; z-index: 5; }
        tr:hover { background-color: #3a3a3a; }
        
        .positive { color: #4caf50; font-weight: bold; }
        .negative { color: #f44336; font-weight: bold; }
        
        .trend-Strong-Bullish { color: #4caf50; font-weight: bold; }
        .trend-Bullish-Pullback { color: #81c784; }
        .trend-Strong-Bearish { color: #f44336; font-weight: bold; }
        .trend-Bearish-Rally { color: #e57373; }
        
        .rsi-Overbought { color: #ff9800; font-weight: bold; }
        .rsi-Oversold { color: #2196f3; font-weight: bold; }

        .edit-input { width: 80px; text-align: right; }
        input[data-field="trail_pct"] { width: 45px !important; }
        
        .vix-Ridicat { color: #ff9800; }
        .vix-Extrem { color: #f44336; font-weight: bold; }
        
        .footer { margin-top: 40px; text-align: center; font-size: 0.8rem; color: #666; }
        
        .summary { display: flex; justify-content: space-around; margin-bottom: 30px; flex-wrap: wrap; }
        .summary-card { background-color: #2d2d2d; padding: 20px; border-radius: 10px; min-width: 200px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 5px; }
        .summary-card h3 { color: #888; font-size: 0.9rem; margin-bottom: 10px; }
        .summary-card .value { font-size: 1.8rem; font-weight: bold; }
        
        .sparkline-container { width: 80px; height: 30px; }
    </style>
    """
    
    vix_val = portfolio_df.iloc[0]['VIX_Tag'] if not portfolio_df.empty else watchlist_df.iloc[0]['VIX_Tag'] if not watchlist_df.empty else 'N/A'
    vix_cls = vix_val if vix_val != 'N/A' else 'Normal'
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calcul Timestamp IBKR File
    pf_file = "portfolio.csv"
    if os.path.exists(pf_file):
        mt = os.path.getmtime(pf_file)
        ibkr_last_update = datetime.datetime.fromtimestamp(mt).strftime('%Y-%m-%d %H:%M:%S')
    else:
        ibkr_last_update = "N/A"

    # Calculăm totalurile pentru sumar
    total_investment = portfolio_df['Investment'].sum() if not portfolio_df.empty else 0
    total_value = portfolio_df['Current_Value'].sum() if not portfolio_df.empty else 0
    total_profit = portfolio_df['Profit'].sum() if not portfolio_df.empty else 0

    # Recalculăm Max Profit și P/L la Stop iterând
    total_max_profit = 0
    total_pl_at_stop = 0
    total_pos_profit = 0      # Count positions > 0 profit
    total_pos_stop_profit = 0 # Count positions > 0 P/L at Stop
    
    if not portfolio_df.empty:
        for _, row in portfolio_df.iterrows():
            if row['Profit'] > 0:
                total_pos_profit += 1
                
            # Max Profit (old logic, replaced by direct sum from df)
            # if row['Target'] and pd.notna(row['Target']):
            #      mp = (row['Target'] - row['Buy_Price']) * row['Shares']
            #      total_max_profit += mp
            
            # P/L la Stop (old logic, replaced by direct sum from df)
            # if row['Trail_Stop'] and pd.notna(row['Trail_Stop']) and row['Trail_Stop'] > 0:
            #      pls = (row['Trail_Stop'] - row['Buy_Price']) * row['Shares']
            #      total_pl_at_stop += pls
            #      if pls > 0:
            #          total_pos_stop_profit += 1

    # Calcul totaluri portofoliu
    total_investment = portfolio_df['Investment'].sum() if not portfolio_df.empty else 0
    total_value = portfolio_df['Current_Value'].sum() if not portfolio_df.empty else 0
    total_profit = portfolio_df['Profit'].sum() if not portfolio_df.empty else 0
    portfolio_df['Max_Profit'] = pd.to_numeric(portfolio_df['Max_Profit'], errors='coerce').fillna(0)
    total_max_profit = portfolio_df['Max_Profit'].sum() if not portfolio_df.empty else 0
    
    # Calc P/L la Stop
    total_pl_at_stop = 0
    total_pos_stop_profit = 0
    if not portfolio_df.empty:
        for _, r in portfolio_df.iterrows():
            if r['Trail_Stop'] and r['Trail_Stop'] > 0:
                 diff = (r['Trail_Stop'] - r['Buy_Price']) * r['Shares']
                 total_pl_at_stop += diff
                 if diff > 0:
                     total_pos_stop_profit += 1
    
    total_profit_pct = ((total_value - total_investment) / total_investment * 100) if total_investment > 0 else 0

    # Citire IBKR Stats (MTD/YTD)
    ib_mtd = 0
    ib_ytd = 0
    has_stats = False
    if os.path.exists('ib_stats.json'):
         try:
             with open('ib_stats.json') as f:
                 st = json.load(f)
                 ib_mtd = st.get('mtd_val', 0)
                 ib_ytd = st.get('ytd_val', 0)
                 has_stats = True
         except: pass

    # Citire parolă
    # Pe GitHub Actions ignorăm password.txt pentru securitate
    is_github = os.environ.get('GITHUB_ACTIONS') == 'true'
    password = "1234" # Default fallback
    
    if 'PORTFOLIO_PASSWORD' in os.environ:
        password = os.environ['PORTFOLIO_PASSWORD']
    elif not is_github and os.path.exists("password.txt"):
        try:
            with open("password.txt", "r") as f:
                password = f.read().strip()
        except: pass

    html_head = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="300">
        <title>Market Scanner Dashboard</title>
        
        <!-- DataTables & jQuery -->
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        
        {css}
        <style>
            /* DataTables Dark Mode Overrides */
            .dataTables_wrapper .dataTables_length, 
            .dataTables_wrapper .dataTables_filter, 
            .dataTables_wrapper .dataTables_info, 
            .dataTables_wrapper .dataTables_paginate {{
                color: #e0e0e0 !important;
                margin-bottom: 15px;
            }}
            .dataTables_wrapper .dataTables_filter input {{
                background-color: #2d2d2d;
                color: #fff;
                border: 1px solid #444;
                padding: 5px;
                border-radius: 4px;
            }}
            table.dataTable tbody tr {{
                background-color: #2d2d2d;
                color: #e0e0e0;
            }}
            table.dataTable tbody tr.even {{
                background-color: #2d2d2d;
            }}
            table.dataTable.hover tbody tr:hover, table.dataTable.display tbody tr:hover {{
                background-color: #3a3a3a !important;
            }}
            table.dataTable thead th, table.dataTable tfoot th {{
                border-bottom: 1px solid #555;
            }}
            table.dataTable.no-footer {{
                border-bottom: 1px solid #444;
            }}
            /* Hide sorting icons if they clash or let them be */
        </style>
    """
    
    # JS Block (Raw String to avoid f-string syntax errors with { })
    html_head += """
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <!-- CryptoJS for AES Decryption -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
        
        <script>
            // Variabila cu datele criptate va fi injectată aici de Python
            // const ENCRYPTED_DATA = { ... }; 
            


            function unlockPortfolio() {
                const input = document.getElementById('pf-pass').value;
                if (!input) return;
                
                try {
                    // Decrypt
                    // ENCRYPTED_DATA is defined below in the body/script injection
                    if (typeof ENCRYPTED_DATA === 'undefined') {
                        alert('Eroare: Datele criptate lipsesc.');
                        return;
                    }
                    
                    const salt = CryptoJS.enc.Base64.parse(ENCRYPTED_DATA.salt);
                    const iv = CryptoJS.enc.Base64.parse(ENCRYPTED_DATA.iv);
                    const ciphertext = ENCRYPTED_DATA.ciphertext;
                    
                    // Derive Key matches Python PBKDF2 (SHA256, 1000 iter, 32 bytes)
                    const key = CryptoJS.PBKDF2(input, salt, { 
                        keySize: 256/32, 
                        iterations: 1000,
                        hasher: CryptoJS.algo.SHA256
                    });
                    
                    const decrypted = CryptoJS.AES.decrypt(ciphertext, key, { 
                        iv: iv, 
                        padding: CryptoJS.pad.Pkcs7,
                        mode: CryptoJS.mode.CBC
                    });
                    
                    const strData = decrypted.toString(CryptoJS.enc.Utf8);
                    
                    if (!strData) {
                        alert('Parolă Incorectă (Decriptare eșuată)');
                    } else {
                        const data = JSON.parse(strData);
                        renderPortfolio(data);
                        
                        document.getElementById('portfolio-lock').style.display = 'none';
                        document.getElementById('portfolio-data').style.display = 'block';
                        sessionStorage.setItem('pf_auth', 'true'); // Optional: store flag, but can't store password safely
                        // Store decrypted data? No, keep in memory.
                    }
                } catch (e) {
                    console.error(e);
                    alert('Parolă Incorectă sau Eroare Decriptare.');
                }
            }
            
            function renderPortfolio(data) {
                // 1. Destroy existing DataTable FIRST (if any)
                if (typeof $ !== 'undefined' && $.fn.DataTable) {
                    if ($.fn.DataTable.isDataTable('#portfolio-table')) {
                        $('#portfolio-table').DataTable().destroy();
                    }
                }
                
                // 2. Populate Table Body
                const tbody = document.getElementById('portfolio-rows-body');
                if (tbody) tbody.innerHTML = data.html;
                
                // 3. Init Charts
                initCharts(data.sparklines);
                
                // 4. Re-Init DataTables
                if (typeof $ !== 'undefined' && $.fn.DataTable) {
                    try {
                        $('#portfolio-table').DataTable({
                            destroy: true,
                            paging: false,
                            searching: true,
                            info: false,
                            order: [] // Preserve order from Python
                        });
                    } catch(e) { console.error("DataTable Init Error: ", e); }
                }
            }
            
            function initCharts(sparklines) {
                if (!sparklines) return;
                
                Object.keys(sparklines).forEach(function(sparkId) {
                    const ctx = document.getElementById(sparkId);
                    if (!ctx) return;
                    
                    const dataPoints = sparklines[sparkId];
                    if (!dataPoints || dataPoints.length === 0) return;
                    
                    // Logică colorare (replicată din Python logic, dar simplificată aici)
                    // Stock logic: Up = Green
                    const isUp = dataPoints[dataPoints.length - 1] >= dataPoints[0];
                    const color = isUp ? '#4caf50' : '#f44336';
                    
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: Array(dataPoints.length).fill(''),
                            datasets: [{
                                data: dataPoints,
                                borderColor: color,
                                borderWidth: 1.5,
                                fill: false,
                                pointRadius: 0,
                                tension: 0.1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { display: false }, tooltip: { enabled: false } },
                            scales: { x: { display: false }, y: { display: false } }
                        }
                    });
                });
            }
            
            // Auto unlock if dev mode? No.
        </script>
    """
    
    # Continue HTML (f-string again for {timestamp})
    html_head += f"""
    </head>
    <body>
    
    <!-- Header cu Hamburger -->
    <div class="header-bar">
    <div class="hamburger" onclick="toggleMenu()">☰</div>
        <div class="app-title">Market Scanner</div>
        <div style="font-size: 0.8rem; color: #888;">Generated: {timestamp}</div>
        
        <div id="navMenu" class="menu-dropdown">
            <div class="menu-item" onclick="switchTab('portfolio')">💼 Portofoliu Activ</div>
            <div class="menu-item" onclick="switchTab('market')">📊 Market Overview</div>
            <div class="menu-item" onclick="switchTab('watchlist')">👀 Watchlist</div>
            <div class="menu-item" onclick="switchTab('volatility')">📉 Volatility Calc</div>
        </div>
    </div>
        
        <div id="portfolio" class="tab-content">
            
            <!-- LOCK SCREEN Local -->
            <div id="portfolio-lock" style="text-align: center; padding: 60px; background: #252526; border-radius: 10px; margin-top: 20px;">
                <div style="font-size: 3rem; margin-bottom: 20px;">🔒</div>
                <h3 style="color: #e0e0e0; margin-bottom: 20px;">Secțiune Protejată</h3>
                <input type="password" id="pf-pass" style="padding: 10px; font-size: 1.2rem; text-align: center; width: 150px; border-radius: 5px; border: 1px solid #555; background: #333; color: white; letter-spacing: 5px;" placeholder="PIN" onkeyup="if(event.key==='Enter') unlockPortfolio()">
                <button onclick="unlockPortfolio()" style="padding: 10px 20px; font-size: 1.2rem; background: #4dabf7; color: white; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px;">Unlock</button>
            </div>
            
            <!-- ACTUAL DATA (Hidden) -->
            <div id="portfolio-data" style="display: none;">
                <div class="summary">
                    <div class="summary-card">
                        <h3>Total Investment</h3>
                        <div class="value">€{total_investment:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Current Value</h3>
                        <div class="value">€{total_value:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Positions on Profit</h3>
                        <div class="value" style="color: #4caf50;">{total_pos_profit}/{len(portfolio_df)}</div>
                    </div>
                    <div class="summary-card">
                        <h3>P&L at Stop Positive</h3>
                        <div class="value" style="color: #4caf50;">{total_pos_stop_profit}/{len(portfolio_df)}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Total Profit</h3>
                        <div class="value {'positive' if total_profit >= 0 else 'negative'}">€{total_profit:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>ROI</h3>
                        <div class="value {'positive' if total_profit_pct >= 0 else 'negative'}">{total_profit_pct:.2f}%</div>
                    </div>
                    <div class="summary-card">
                        <h3>Max Potential Profit</h3>
                        <div class="value {'positive' if total_max_profit > 0 else ''}" style="color: #4dabf7;">€{total_max_profit:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Total P/L la Stop</h3>
                        <div class="value {'positive' if total_pl_at_stop >= 0 else 'negative'}">€{total_pl_at_stop:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>IBKR MTD</h3>
                        <div class="value {'positive' if ib_mtd >= 0 else 'negative'}" title="Actualizat via Flex">€{ib_mtd:,.2f}</div>
                    </div>
                </div>
            
            <div style="text-align: right; color: #888; font-size: 0.8rem; margin-bottom: 10px; padding-right: 10px;">
                📅 Last IBKR/Data Update: <strong>{ibkr_last_update}</strong>
            </div>
            
            <div class="table-container">
            <table id="portfolio-table">
                <thead>
                    <tr>
                        <th style="width: 80px;">Simbol</th>
                        <th>Acțiuni</th>
                        <th>Preț Cumpărare</th>
                        <th>Preț Curent</th>
                        <th>Grafic</th>
                        <th>Target</th>
                        <th>% Mid</th>
                        <th>Consensus</th>
                        <th>Analysts</th>
                        <th>Trail %</th>
                        <th># Stop</th>
                        <th>Suggested Stop</th>
                        <th>Investiție</th>
                        <th>Valoare</th>
                        <th>Profit</th>
                        <th>% Profit</th>
                        <th>P/L la Stop</th>
                        <th>Max Profit</th>
                        <th>Status</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody id="portfolio-rows-body">
                    <!-- Rows will be injected by JS after decryption -->
    """
    
    # Portfolio rows generation (for encryption)
    portfolio_rows_html = ""
    sparkline_data = {}
    
    chart_id = 0
    for _, row in portfolio_df.iterrows():
        trend_cls = row['Trend'].replace(' ', '-')
        rsi_cls = row['RSI_Status']
        status_cls = row['Status']
        profit_cls = 'positive' if row['Profit'] >= 0 else 'negative'
        
        if row['Target'] and pd.notna(row['Target']):
            pct_to_target = ((row['Target'] - row['Current_Price']) / row['Current_Price']) * 100
            target_display = f"€{row['Target']:.2f}"
            pct_display = f"{pct_to_target:.1f}%"
            max_profit_display = f"€{row['Max_Profit']:,.2f}" if row['Max_Profit'] and pd.notna(row['Max_Profit']) else "N/A"
        else:
            pct_to_target = 0
            target_display = "N/A"
            pct_display = "N/A"
            max_profit_display = "N/A"
        
        sparkline_id = f"spark_{chart_id}"
        chart_id += 1
        
        # Save sparkline data for JS
        sparkline_data[sparkline_id] = row['Sparkline']
        
        # P/L la Stop Calc
        pl_at_stop_display = "-"
        pl_at_stop_class = ""
        if row['Trail_Stop'] and pd.notna(row['Trail_Stop']) and row['Trail_Stop'] > 0:
            pl_at_stop = (row['Trail_Stop'] - row['Buy_Price']) * row['Shares']
            pl_at_stop_display = f"€{pl_at_stop:,.2f}"
            pl_at_stop_class = "positive" if pl_at_stop > 0 else "negative"
        
        target_val = row['Target'] if row['Target'] and pd.notna(row['Target']) else ""
        if isinstance(target_val, (int, float)): target_val = f"{target_val:.2f}"
        
        trail_pct_val = row['Trail_Pct'] if pd.notna(row['Trail_Pct']) else 0
        trail_stop_val = row['Trail_Stop'] if row['Trail_Stop'] and pd.notna(row['Trail_Stop']) and row['Trail_Stop'] > 0 else ""
        if isinstance(trail_stop_val, (int, float)): trail_stop_val = f"{trail_stop_val:.2f}"

        # Consensus
        cons = row.get('Consensus', '-')
        cons_style = ""
        if 'Buy' in str(cons): cons_style = 'color: #4caf50; font-weight: bold;'
        elif 'Sell' in str(cons): cons_style = 'color: #f44336; font-weight: bold;'
        analysts = row.get('Analysts', 0)

        # Build Row HTML string (NO html_head += here)
        portfolio_rows_html += f"""
                    <tr id="row-{row['Symbol']}" data-price="{row['Current_Price']}" data-buy="{row['Buy_Price']}" data-shares="{row['Shares']}">
                        <td><strong>{row['Symbol']}</strong></td>
                        <td>{row['Shares']}</td>
                        <td>€{row['Buy_Price']:.2f}</td>
                        <td>€{row['Current_Price']:.2f}</td>
                        <td><canvas id="{sparkline_id}" class="sparkline-container"></canvas></td>
                        
                        <!-- TARGET -->
                        <td>{target_display}</td>
                        <td class="{'positive' if pct_to_target > 0 else 'negative' if row['Target'] else ''}">{pct_display}</td>
                        
                        <!-- Consensus -->
                        <td style="{cons_style}">{cons}</td>
                        <td>{analysts}</td>

                        <!-- Trail % -->
                        <td>{trail_pct_val:.1f}%</td>
                        
                        <!-- Trail Stop -->
                        <td>{f"€{trail_stop_val}" if isinstance(trail_stop_val, (int, float)) or (isinstance(trail_stop_val, str) and trail_stop_val) else "-"}</td>
                        
                        <td>€{row['Suggested_Stop']:.2f}</td>
                        <td>€{row['Investment']:,.2f}</td>
                        <td>€{row['Current_Value']:,.2f}</td>
                        <td class="{profit_cls}">€{row['Profit']:,.2f}</td>
                        <td class="{profit_cls}">{row['Profit_Pct']:.2f}%</td>
                        
                        <!-- P/L la Stop -->
                        <td class="{pl_at_stop_class}">{pl_at_stop_display}</td>
                        
                        <!-- Max Profit -->
                        <td id="cell-{row['Symbol']}-maxprofit">{max_profit_display}</td>
                        
                        <td class="rsi-{status_cls}">{row['Status']}</td>
                        <td class="trend-{trend_cls}">{row['Trend']}</td>
                    </tr>
        """
        
    # Encrypt Data
    full_pf_data = {
        "html": portfolio_rows_html,
        "sparklines": sparkline_data
    }
    # Use password variable (should be defined)
    if not password: password = "1234" # Fallback
    
    # print(f"  Encrypting Portfolio with password: {password}")
    encrypted_blob = encrypt_for_js(json.dumps(full_pf_data), password)
    
    html_head += f"""
                </tbody>
            </table>
            </div> <!-- End table-container -->
            
            <!-- Encrypted Data Injection -->
            <script>
                const ENCRYPTED_DATA = {encrypted_blob};
            </script>
            
        </div> <!-- End portfolio-data -->
        </div> <!-- End portfolio Tab -->
        
        <!-- TAB MARKET (NOU) -->
        <div id="market" class="tab-content active">
            <h3 style="color: #4dabf7; margin-bottom: 20px; text-align: center;">📊 Indicatori de Piață</h3>
            <div style="background-color: #2d2d2d; padding: 20px; border-radius: 10px; overflow-x: auto;">
                <table style="width: 100%; background-color: transparent; box-shadow: none;">
                    <thead>
                        <tr style="border-bottom: 2px solid #444;">
    """
    
    # Ordinea indicatorilor
    indicator_order = ['VIX3M', 'VIX', 'VIX1D', 'VIX9D', 'VXN', 'LTV', 'SKEW', 'MOVE', 'Crypto Fear', 'GVZ', 'OVX', 'SPX']
    
    # Mapping Display Names
    display_map = {
        'VIX3M': 'VIX Futures (3M)',
        'VIX': 'VIX Spot',
        'VIX1D': 'VIX 1D',
        'VIX9D': 'VIX 9D'
    }
    
    # Header row
    for name in indicator_order:
        if name in market_indicators:
            disp_name = display_map.get(name, name)
            html_head += f"""
                            <th style="min-width: 80px; text-align: center; padding: 8px; font-size: 0.75rem;">{disp_name}</th>"""
    
    html_head += """
                        </tr>
                        <tr style="border-bottom: 1px solid #444;">
    """
    
    # Sub-header descrieri
    for name in indicator_order:
        if name in market_indicators:
            desc = market_indicators[name].get('description', '')
            html_head += f"""
                            <th style="text-align: center; padding: 5px; font-size: 0.65rem; color: #888; font-weight: normal;">{desc}</th>"""
    
    html_head += """
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
    """
    
    # Sparklines
    for idx, name in enumerate(indicator_order):
        if name in market_indicators:
            spark_id = f"spark_ind_{name}"
            html_head += f"""
                            <td style="text-align: center; padding: 5px; height: 50px;"><canvas id="{spark_id}" style="width: 100%; height: 100%;"></canvas></td>"""
    
    html_head += """
                        </tr>
                        <tr>
    """
    
    # Valorile curente
    for name in indicator_order:
        if name in market_indicators:
            value = market_indicators[name].get('value', 'N/A')
            status = market_indicators[name].get('status', 'Normal')
            
            # Colorare bazată pe status (4 nivele)
            if status == 'Perfect':
                color = '#4caf50'
            elif status == 'Normal':
                color = '#e0e0e0'
            elif status == 'Tension':
                color = '#ff9800'
            elif status == 'Panic':
                color = '#f44336'
            else:
                color = '#e0e0e0'
            
            html_head += f"""
                            <td style="text-align: center; padding: 10px; font-size: 1rem; font-weight: bold; color: {color};">{value}</td>"""
    
    html_head += """
                        </tr>
                        <tr>
    """
    
    # Schimbările
    for name in indicator_order:
        if name in market_indicators:
            change = market_indicators[name].get('change', 0)
            
            # Colorare inversă (stock logic vs volatility logic)
            if name == 'SPX' or name == 'Crypto Fear':
                if change > 0:
                    change_color = '#4caf50'
                    arrow = '↑'
                elif change < 0:
                    change_color = '#f44336'
                    arrow = '↓'
                else:
                    change_color = '#888'
                    arrow = ''
            else:
                # Volatility logic (Up = Bad)
                if change > 0:
                    change_color = '#f44336'
                    arrow = '↑'
                elif change < 0:
                    change_color = '#4caf50'
                    arrow = '↓'
                else:
                    change_color = '#888'
                    arrow = ''
            
            html_head += f"""
                            <td style="text-align: center; padding: 5px; font-size: 0.75rem; color: {change_color};">{arrow} {abs(change):.2f}</td>"""
    
    html_head += """
                        </tr>
                    </tbody>
                </table>
            </div>
    """
    
    # Adăugăm analiza AI (News + Calendar)
    # Adăugăm analiza AI (News + Calendar)
    # Load existing AI summary from state (if any)
    cached_ai = full_state.get('last_ai_summary', None)
    
    # Generare analiză piață (returnează HTML + Raw Text)
    market_analysis_html, new_ai_text, ai_score = generate_market_analysis(market_indicators, cached_ai)
    
    # Save new AI text to state if successfully generated
    if new_ai_text:
         full_state['last_ai_summary'] = new_ai_text
         print("  -> Rezumat AI salvat în cache (dashboard_state).")
    
    html_head += market_analysis_html

    # Adăugăm Explicații Macro (Glosar) - ULTIMUL
    html_head += get_macro_explanations()
    
    html_head += f"""
        </div>
        
        <div id="watchlist" class="tab-content">
            
            <!-- Filters -->
            <div class="filters-container" style="margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 15px; background: #2d2d2d; padding: 15px; border-radius: 8px; border: 1px solid #444;">
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 0.8rem; margin-bottom: 5px; color: #aaa;">Consensus</label>
                    <select id="filter-consensus" style="padding: 5px; background: #444; color: #fff; border: none; border-radius: 4px;">
                        <option value="">All</option>
                        <option value="Strong Buy">Strong Buy</option>
                        <option value="Buy">Buy</option>
                        <option value="Hold">Hold</option>
                        <option value="Sell">Sell</option>
                    </select>
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 0.8rem; margin-bottom: 5px; color: #aaa;">Min Analysts</label>
                    <input type="number" id="filter-analysts" placeholder="0" style="padding: 5px; background: #444; color: #fff; border: none; border-radius: 4px; width: 100px;">
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 0.8rem; margin-bottom: 5px; color: #aaa;">Min Target %</label>
                    <input type="number" id="filter-target-pct" placeholder="0" step="any" style="padding: 5px; background: #444; color: #fff; border: none; border-radius: 4px; width: 100px;">
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 0.8rem; margin-bottom: 5px; color: #aaa;">Trend</label>
                    <select id="filter-trend" style="padding: 5px; background: #444; color: #fff; border: none; border-radius: 4px; width: 120px;">
                        <option value="">All</option>
                        <option value="Strong Bullish">Strong Bullish</option>
                        <option value="Bullish Pullback">Bullish Pullback</option>
                        <option value="Bearish Rally">Bearish Rally</option>
                        <option value="Strong Bearish">Strong Bearish</option>
                        <option value="Neutral">Neutral</option>
                    </select>
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 0.8rem; margin-bottom: 5px; color: #aaa;">Status</label>
                    <select id="filter-status" style="padding: 5px; background: #444; color: #fff; border: none; border-radius: 4px; width: 100px;">
                        <option value="">All</option>
                        <option value="Oversold">Oversold</option>
                        <option value="Overbought">Overbought</option>
                        <option value="Neutral">Neutral</option>
                    </select>
                </div>
            </div>


            <h3 style="color: #4dabf7; margin-bottom: 20px; text-align: center;">👀 Watchlist</h3>
            <div class="table-container">
            <table id="watchlist-table">
                <thead>
                    <tr>
                        <th style="width: 80px;">Simbol</th>
                        <th>Preț</th>
                        <th>Grafic</th>
                        <th>Target</th>
                        <th>To Target</th>
                        <th>Consensus</th>
                        <th>Analysts</th>
                        <th>Sector</th>
                        <th>Trend</th>
                        <th style="color: #4caf50;">{full_state.get('eco_phase', 'Cycle')}</th>
                        <th style="color: #4dabf7;">{full_state.get('eco_next_phase', 'Next')} (Next)</th>
                        <th>RSI</th>
                        <th>Status</th>
                        <th>ATR</th>
                        <th>Stop Loss</th>
                        <th>SMA 50</th>
                        <th>SMA 200</th>
                        <th>Schimbare</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Watchlist rows
    watch_chart_id = 0
    if not watchlist_df.empty:
        for idx, row in watchlist_df.iterrows():
            trend_cls = row['Trend'].replace(' ', '-')
            rsi_cls = row['RSI_Status']
            
            # Target display logic
            target_val = row.get('Target')
            target_display = "-"
            if target_val:
                 if isinstance(target_val, (int, float)):
                     target_display = f"€{target_val:.2f}"
                 else:
                     target_display = str(target_val)
            
            # Pct Target Logic
            pct_target_val = row.get('Pct_To_Target')
            pct_display = "-"
            pct_class = ""
            if pct_target_val is not None:
                 pct_display = f"{pct_target_val:.2f}%"
                 pct_class = "positive" if pct_target_val > 0 else "negative"

            # Consensus color
            cons = row.get('Consensus', '-')
            cons_style = ""
            if 'Buy' in cons: cons_style = 'color: #4caf50; font-weight: bold;'
            elif 'Sell' in cons: cons_style = 'color: #f44336; font-weight: bold;'
            
            analysts = row.get('Analysts', 0)
            industry = row.get('Industry', '-')
            
            spark_wl_id = f"spark_wl_{watch_chart_id}"
            watch_chart_id += 1

            # Change % logic
            change = 0.0
            spark_data = row.get('Sparkline', [])
            if isinstance(spark_data, list) and len(spark_data) > 1:
                change = ((spark_data[-1] - spark_data[-2]) / spark_data[-2]) * 100
                
            change_color = '#aaa'
            arrow = ''
            if change > 0:
                change_color = '#4caf50'; arrow = '▲'
            elif change < 0:
                change_color = '#f44336'; arrow = '▼'

            # Calc Fitness
            eco_phase = full_state.get('eco_phase', 'Expansion')
            eco_next = full_state.get('eco_next_phase', 'Slowdown')
            sector = row.get('Sector', row.get('Industry', '-'))
            
            fit_now = assess_stock_fitness(sector, eco_phase)
            fit_next = assess_stock_fitness(sector, eco_next)

            html_head += f"""
                    <tr>
                        <td><strong>{row['Ticker']}</strong></td>
                        <td>€{row['Price']:.2f}</td>
                        <td><canvas id="{spark_wl_id}" class="sparkline-container"></canvas></td>
                        <td>{target_display}</td>
                        <td class="{pct_class}">{pct_display}</td>
                        <td style="{cons_style}">{cons}</td>
                        <td>{analysts}</td>
                        <td style="font-size: 0.8rem; color: #aaa;">{sector}</td>
                        <td class="trend-{trend_cls}">{row['Trend']}</td>
                        <td style="text-align: center;">{fit_now}</td>
                        <td style="text-align: center;">{fit_next}</td>
                        <td>{row['RSI']:.0f}</td>
                        <td class="rsi-{rsi_cls}">{row['RSI_Status']}</td>
                        <td>{row['ATR_14']:.2f}</td>
                        <td>€{row['Stop_Loss']:.2f}</td>
                        <td>€{row['SMA_50']:.2f}</td>
                        <td>€{row['SMA_200']:.2f}</td>
                        <td style="text-align: center; padding: 5px; font-size: 0.75rem; color: {change_color};">{arrow} {abs(change):.2f}%</td>
                    </tr>
            """
        

    
    # --- VOLATILITY DATA & TAB GENERATION ---
    vol_map = {}
    
    # Helper to clean/convert
    def get_val(d, k, default=0):
        v = d.get(k)
        try: return float(v) if v is not None else default
        except: return default

    # Merge Data
    all_items = []
    if not watchlist_df.empty: all_items.extend(watchlist_df.to_dict('records'))
    if not portfolio_df.empty: all_items.extend(portfolio_df.to_dict('records'))
    
    for item in all_items:
        sym = item.get('Ticker', item.get('Symbol'))
        if not sym: continue
        
        price = get_val(item, 'Current_Price') or get_val(item, 'Price')
        price_native = get_val(item, 'Price_Native')
        atr = get_val(item, 'Finviz_ATR') or get_val(item, 'ATR_14')
        
        # ATR percentage must be calculated using base currency price
        atr_pct = (atr / price_native * 100) if price_native and atr else 0
        
        vol_map[sym] = {
            'Price_Native': round(price_native, 2) if price_native else 0,
            'ATR_Val': round(atr, 2),
            'ATR_Pct': round(atr_pct, 2),
            'Vol_W': get_val(item, 'Vol_W'),
            'Vol_M': get_val(item, 'Vol_M')
        }
        
    vol_json = json.dumps(vol_map)
    
    # Watchlist Closures
    html_footer = """
                </tbody>
            </table>
            </div>
        </div>

        <!-- Volatility Tab -->
        <div id="volatility" class="tab-content">
             <h3 style="color: #ba68c8; text-align: center; margin-bottom: 20px;">📉 Volatility Calculator</h3>
             <div style="background: #2d2d2d; padding: 20px; border-radius: 10px; max-width: 500px; margin: 0 auto; border: 1px solid #444;">
                 <label style="color: #aaa; margin-bottom: 5px; display: block;">Search Symbol (Portfolio & Watchlist)</label>
                 <input list="vol-tickers" id="vol-input" oninput="calcVolatility()" placeholder="Type symbol..." 
                        style="width: 100%; padding: 12px; margin-bottom: 20px; background: #333; color: white; border: 1px solid #555; border-radius: 5px; font-size: 1rem;">
                 <datalist id="vol-tickers">
    """ + "".join([f'<option value="{k}">' for k in sorted(vol_map.keys())]) + """
                 </datalist>
                 
                 <div id="vol-results" style="display: none;">
                      <table style="width: 100%; border-collapse: collapse; color: #ddd;">
                          <tr style="border-bottom: 1px solid #444;">
                                <th style="text-align: left; padding: 10px;">Metric</th>
                                <th style="text-align: right; padding: 10px;">Value</th>
                          </tr>
                          <tr>
                                <td style="padding: 10px;">Price (Base Currency)</td>
                                <td id="res-price-native" style="text-align: right; font-weight: bold; color: #4caf50;">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px;">ATR (14) Value</td>
                                <td id="res-atr-val" style="text-align: right; font-weight: bold; color: #ccc;">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px;">ATR (14) Volatility</td>
                                <td id="res-atr" style="text-align: right; font-weight: bold; color: #4dabf7;">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px;">Weekly Volatility</td>
                                <td id="res-week" style="text-align: right; font-weight: bold; color: #ff9800;">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px;">Monthly Volatility</td>
                                <td id="res-month" style="text-align: right; font-weight: bold;">-</td>
                          </tr>
                      </table>
                      
                      
                      <!-- Suggested Stop & Buy (ATR-based) -->
                      <div style="margin-top: 20px; padding: 15px; background: #1e1e1e; border-radius: 8px; border: 1px solid #555;">
                          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                              <div>
                                  <div style="color: #aaa; font-size: 0.85rem; margin-bottom: 5px;">💡 Suggested Stop (2×ATR)</div>
                                  <div id="suggested-stop" style="font-size: 1.1rem; font-weight: bold; color: #f44336;">-</div>
                              </div>
                              <div>
                                  <div style="color: #aaa; font-size: 0.85rem; margin-bottom: 5px;">🎯 Suggested Buy (2×ATR)</div>
                                  <div id="suggested-buy" style="font-size: 1.1rem; font-weight: bold; color: #4caf50;">-</div>
                              </div>
                          </div>
                      </div>
                      
                      <!-- Trailing Stop Calculations -->
                      <h4 style="color: #ba68c8; margin-top: 30px; margin-bottom: 15px; text-align: center;">📊 Trailing Stop Levels</h4>
                      <table style="width: 100%; border-collapse: collapse; color: #ddd; margin-top: 10px;">
                          <tr style="border-bottom: 1px solid #444;">
                                <th style="text-align: left; padding: 10px;">Strategy</th>
                                <th style="text-align: right; padding: 10px;">Volatility %</th>
                                <th style="text-align: right; padding: 10px;">Stop Sell</th>
                                <th style="text-align: right; padding: 10px;">Stop Buy</th>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: #f44336;">🔴 LARG (Loose)</td>
                                <td id="vol-larg" style="text-align: right; font-weight: bold;">-</td>
                                <td id="stop-larg-sell" style="text-align: right; font-weight: bold; color: #f44336;">-</td>
                                <td id="stop-larg-buy" style="text-align: right; font-weight: bold; color: #4caf50;">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: #ff9800;">🟠 MEDIU (Medium)</td>
                                <td id="vol-mediu" style="text-align: right; font-weight: bold;">-</td>
                                <td id="stop-mediu-sell" style="text-align: right; font-weight: bold; color: #f44336;">-</td>
                                <td id="stop-mediu-buy" style="text-align: right; font-weight: bold; color: #4caf50;">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: #4caf50;">🟢 STRÂNS (Tight)</td>
                                <td id="vol-strans" style="text-align: right; font-weight: bold;">-</td>
                                <td id="stop-strans-sell" style="text-align: right; font-weight: bold; color: #f44336;">-</td>
                                <td id="stop-strans-buy" style="text-align: right; font-weight: bold; color: #4caf50;">-</td>
                          </tr>
                      </table>
                 </div>
             </div>
             
             <script>
                const volData = """ + vol_json + """;
                function calcVolatility() {
                    const val = document.getElementById('vol-input').value.toUpperCase();
                    const resDiv = document.getElementById('vol-results');
                    if (volData[val]) {
                         const d = volData[val];
                         const price = d.Price_Native;
                         const atrPct = d.ATR_Pct;
                         const volW = d.Vol_W;
                         const volM = d.Vol_M;
                         
                         // Display basic metrics
                         document.getElementById('res-price-native').innerText = price;
                         document.getElementById('res-atr-val').innerText = d.ATR_Val;
                         document.getElementById('res-atr').innerText = atrPct + '%';
                         document.getElementById('res-week').innerText = volW + '%';
                         document.getElementById('res-month').innerText = volM + '%';
                         
                         // Calculate and display Suggested Stop & Buy (Price ± 2×ATR)
                         const suggestedStop = price - (2 * d.ATR_Val);
                         const suggestedBuy = price + (2 * d.ATR_Val);
                         document.getElementById('suggested-stop').innerText = suggestedStop.toFixed(2);
                         document.getElementById('suggested-buy').innerText = suggestedBuy.toFixed(2);
                         
                         // Calculate trailing stop levels
                         const vols = [atrPct, volW, volM].filter(v => v > 0);
                         
                         if (vols.length > 0 && price > 0) {
                             // LARG: MAX × 3
                             const volLarg = Math.max(...vols) * 3;
                             const stopLargSell = price * (1 - volLarg / 100);
                             const stopLargBuy = price * (1 + volLarg / 100);
                             
                             // MEDIU: AVG × 2
                             const volMediu = (vols.reduce((a, b) => a + b, 0) / vols.length) * 2;
                             const stopMediuSell = price * (1 - volMediu / 100);
                             const stopMediuBuy = price * (1 + volMediu / 100);
                             
                             // STRÂNS: MIN × 1.5
                             const volStrans = Math.min(...vols) * 1.5;
                             const stopStransSell = price * (1 - volStrans / 100);
                             const stopStransBuy = price * (1 + volStrans / 100);
                             
                             // Display results
                             document.getElementById('vol-larg').innerText = volLarg.toFixed(2) + '%';
                             document.getElementById('stop-larg-sell').innerText = stopLargSell.toFixed(2);
                             document.getElementById('stop-larg-buy').innerText = stopLargBuy.toFixed(2);
                             
                             document.getElementById('vol-mediu').innerText = volMediu.toFixed(2) + '%';
                             document.getElementById('stop-mediu-sell').innerText = stopMediuSell.toFixed(2);
                             document.getElementById('stop-mediu-buy').innerText = stopMediuBuy.toFixed(2);
                             
                             document.getElementById('vol-strans').innerText = volStrans.toFixed(2) + '%';
                             document.getElementById('stop-strans-sell').innerText = stopStransSell.toFixed(2);
                             document.getElementById('stop-strans-buy').innerText = stopStransBuy.toFixed(2);
                         }
                         
                         resDiv.style.display = 'block';
                    } else {
                         resDiv.style.display = 'none';
                    }
                }
             </script>
        </div>
        
        <div class="footer">
            Auto-generated by Antigravity Market Scanner
        </div>
    </div> <!-- END dashboard-content -->

        <script>
            $(document).ready(function() {
                var table = $('#portfolio-table, #watchlist-table').DataTable({
                    paging: false,
                    ordering: true,
                    info: false,
                    searching: true,
                    order: [] 
                });
                
                // Custom filtering function
                $.fn.dataTable.ext.search.push(
                    function(settings, data, dataIndex) {
                        if (settings.nTable.id !== 'watchlist-table') return true;

                        var consensus = $('#filter-consensus').val();
                        var minAnalysts = parseFloat($('#filter-analysts').val());
                        var minTarget = parseFloat($('#filter-target-pct').val());
                        var trend = $('#filter-trend').val();
                        var status = $('#filter-status').val();

                        // Indices: 5: Consensus, 6: Analysts, 8: Trend, 12: Status
                        var rowTargetPct = parseFloat(data[4].replace('%', '')) || -9999;
                        var rowConsensus = data[5] || "";
                        var rowAnalysts = parseFloat(data[6]) || 0;
                        var rowTrend = data[8] || "";
                        var rowStatus = data[12] || "";

                        if (consensus && !rowConsensus.includes(consensus)) return false;
                        if (!isNaN(minAnalysts) && rowAnalysts < minAnalysts) return false;
                        if (!isNaN(minTarget) && rowTargetPct < minTarget) return false;
                        if (trend && !rowTrend.includes(trend)) return false;
                        if (status && !rowStatus.includes(status)) return false;

                        return true;
                    }
                );

                // Event listener to redraw on input change
                $('#filter-consensus, #filter-analysts, #filter-target-pct, #filter-trend, #filter-status').change(function() {
                    table.draw();
                });
                $('#filter-analysts, #filter-target-pct').keyup(function() {
                     table.draw();
                });
            });

            function toggleMenu() {
                document.getElementById('navMenu').classList.toggle('show');
            }
            
            // Close menu when clicking outside
            window.onclick = function(event) {
                if (!event.target.matches('.hamburger')) {
                    var dropdowns = document.getElementsByClassName("menu-dropdown");
                    for (var i = 0; i < dropdowns.length; i++) {
                        var openDropdown = dropdowns[i];
                        if (openDropdown.classList.contains('show')) {
                            openDropdown.classList.remove('show');
                        }
                    }
                }
            }

            function switchTab(tabId) {
                // Hide all contents
                var contents = document.getElementsByClassName('tab-content');
                for (var i = 0; i < contents.length; i++) {
                    contents[i].classList.remove('active');
                }
                
                // Show selected
                document.getElementById(tabId).classList.add('active');
            }
            
            // Sparkline charts data
            const sparklineData = {
    """
    
    # Adăugăm datele pentru sparklines PORTFOLIO
    for idx, row in portfolio_df.iterrows():
        sparkline_id = f"spark_{idx}"
        sparkline_values = row['Sparkline']
        html_footer += f"""
                '{sparkline_id}': {sparkline_values},
        """
        
    # Adăugăm datele pentru sparklines WATCHLIST
    if not watchlist_df.empty:
        watch_chart_id = 0
        for idx, row in watchlist_df.iterrows():
            spark_wl_id = f"spark_wl_{watch_chart_id}"
            watch_chart_id += 1
            spark_values = row.get('Sparkline', [])
            html_footer += f"""
                '{spark_wl_id}': {spark_values},
            """
            
    # Adăugăm datele pentru sparklines INDICATORI
    for name in market_indicators:
        if 'sparkline' in market_indicators[name]:
            spark_id = f"spark_ind_{name}"
            spark_values = market_indicators[name]['sparkline']
            html_footer += f"""
                '{spark_id}': {spark_values},
            """
    
    html_footer += """
            };
            
            // Create sparkline charts
            window.addEventListener('load', function() {
                Object.keys(sparklineData).forEach(function(sparkId) {
                    const ctx = document.getElementById(sparkId);
                    if (!ctx) return;
                    
                    const data = sparklineData[sparkId];
                    
                    // Logică colorare:
                    // Default (Stocks, SPX, Crypto): Up = Green, Down = Red
                    // Inversed (VIX, etc): Up = Red (Bad), Down = Green (Good)
                    
                    let isInversed = false;
                    if (sparkId.startsWith('spark_ind_')) {
                         // Dacă e indicator si NU e SPX si NU e Crypto Fear -> Inversed
                         if (!sparkId.includes('SPX') && !sparkId.includes('Crypto Fear')) {
                             isInversed = true;
                         }
                    }
                    
                    const isUp = data[data.length - 1] >= data[0];
                    let color;
                    
                    if (isInversed) {
                        color = isUp ? '#f44336' : '#4caf50';
                    } else {
                        color = isUp ? '#4caf50' : '#f44336';
                    }
                    
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: Array(data.length).fill(''),
                            datasets: [{
                                data: data,
                                borderColor: color,
                                borderWidth: 1.5,
                                fill: false,
                                pointRadius: 0,
                                tension: 0.1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false },
                                tooltip: { enabled: false }
                            },
                            scales: {
                                x: { display: false },
                                y: { display: false }
                            }
                        }
                    });
                });
            });
        </script>
    </body>
    </html>
    """
    
    full_html = html_head + html_footer
    
    with open(filename, 'w') as f:
        f.write(full_html)
    print(f"Dashboard HTML generat: {os.path.abspath(filename)}")

import ib_sync  # Modul sincronizare IBKR

def update_portfolio_data(state, rates, vix_val):
    """Actualizează datele de portofoliu și le salvează în state."""
    print("\n=== Actualizare Portofoliu ===")
    
    # 0. Sincronizare IBKR
    try:
        ib_sync.sync_ibkr()
    except Exception as e:
        print(f"Sincronizare IBKR a eșuat sau nu este disponibilă: {e}")
        
    portfolio_data = load_portfolio()
    portfolio_results = []
    
    if not portfolio_data.empty:
        print(f"Procesare {len(portfolio_data)} poziții...")
        for _, row in portfolio_data.iterrows():
            print(f"  > {row['symbol']}")
            data = process_portfolio_ticker(row, vix_val, rates)
            if data:
                portfolio_results.append(data)
    
    state['portfolio'] = portfolio_results
    return state

def update_watchlist_data(state, rates, vix_val):
    """Actualizează datele din watchlist și le salvează în state."""
    print("\n=== Actualizare Watchlist ===")
    watchlist_tickers = load_watchlist()
    watchlist_results = []
    
    if watchlist_tickers:
        print(f"Procesare {len(watchlist_tickers)} tickere...")
        for ticker in watchlist_tickers:
            print(f"  > {ticker}")
            data = process_watchlist_ticker(ticker, vix_val, rates)
            if data:
                watchlist_results.append(data)
    
    state['watchlist'] = watchlist_results
    return state

def main():
    parser = argparse.ArgumentParser(description="Antigravity Market Scanner")
    parser.add_argument('--mode', choices=['all', 'portfolio', 'watchlist', 'html-only'], default='all', help='Select update mode')
    parser.add_argument('--tws', action='store_true', help='Try fetching active orders from local TWS (requires ib_insync)')
    args = parser.parse_args()
    
    # Auto-enable TWS if local (not GitHub Actions) to prioritize live data
    if not os.environ.get('GITHUB_ACTIONS'):
        if not args.tws:
            print("Mediu Local detectat: Activare automată TWS Sync.")
            args.tws = True
    
    print(f"=== Rulează Market Scanner [Mod: {args.mode}] ===\n")
    
    # 1. Încărcăm starea anterioară
    state = load_state()

    # 1. Update Portfolio Data
    if args.mode in ['all', 'portfolio']:
        # Optional TWS Sync
        if args.tws:
             try:
                 import ib_tws_sync
                 ib_tws_sync.fetch_active_orders()
                 
                 # Apply TWS Orders to Local CSV immediately
                 if os.path.exists('tws_orders.csv') and os.path.exists('portfolio.csv'):
                     print("Applying TWS Orders to portfolio.csv...")
                     p_df = pd.read_csv('portfolio.csv')
                     t_df = pd.read_csv('tws_orders.csv')
                     
                     changed = False
                     for _, row in t_df.iterrows():
                         sym = str(row.get('Symbol', ''))
                         stop = float(row.get('Calculated_Stop', 0))
                         pct = float(row.get('Trail_Pct', 0))
                         
                         mask = p_df['Symbol'] == sym
                         if mask.any():
                             if stop > 0:
                                 p_df.loc[mask, 'Trail_Stop'] = stop # Update direct Trail_Stop
                                 changed = True
                             if pct > 0:
                                 p_df.loc[mask, 'Trail_Pct'] = pct
                                 changed = True
                     
                     if changed:
                         p_df.to_csv('portfolio.csv', index=False)
                         print("Portfolio CSV updated with live orders.")

                 # Apply TWS Positions to Local CSV (Sync Size & Entry)
                 if os.path.exists('tws_positions.csv'):
                     print("Merging TWS Positions (Shares/AvgPrice) into portfolio.csv...")
                     try:
                         pos_df = pd.read_csv('tws_positions.csv')
                         # Load portfolio again to be fresh
                         p_df = pd.read_csv('portfolio.csv') if os.path.exists('portfolio.csv') else pd.DataFrame(columns=['Symbol', 'Shares', 'Buy_Price', 'Currency', 'Trail_Pct', 'Trail_Stop'])
                         
                         p_changed = False
                         
                         # 1. Update Existing & Add New
                         for _, row in pos_df.iterrows():
                             sym = str(row.get('Symbol', ''))
                             shares = float(row.get('Shares', 0))
                             price = float(row.get('Buy_Price', 0))
                             curr = str(row.get('Currency', 'USD'))
                             
                             if shares == 0: continue # Ignore closed
                             
                             mask = p_df['Symbol'] == sym
                             if mask.any():
                                 # Update existing
                                 current_shares = float(p_df.loc[mask, 'Shares'].values[0])
                                 current_price = float(p_df.loc[mask, 'Buy_Price'].values[0])
                                 
                                 # Update only if different
                                 if abs(current_shares - shares) > 0.0001 or abs(current_price - price) > 0.01:
                                      p_df.loc[mask, 'Shares'] = shares
                                      p_df.loc[mask, 'Buy_Price'] = price
                                      # p_df.loc[mask, 'Currency'] = curr # Optional
                                      p_changed = True
                                      print(f"  Updated {sym}: {shares} shares @ {price}")
                             else:
                                 # Add New Position
                                 new_row = {
                                     'Symbol': sym, 
                                     'Shares': shares, 
                                     'Buy_Price': price, 
                                     'Currency': curr,
                                     'Trail_Pct': 15,    # Default
                                     'Trail_Stop': 0, 
                                     'Investment': shares * price 
                                 }
                                 # Align columns
                                 for col in p_df.columns:
                                     if col not in new_row: new_row[col] = 0
                                     
                                 p_df = pd.concat([p_df, pd.DataFrame([new_row])], ignore_index=True)
                                 p_changed = True
                                 print(f"  Added New Pos {sym}: {shares} shares @ {price}")

                         # 2. (Optional) Mark closed positions? 
                         # For now, we only update active TWS positions. We don't delete positions not in TWS to be safe.
                         
                         if p_changed:
                             p_df.to_csv('portfolio.csv', index=False)
                             print("Portfolio CSV positions synchronized.")
                             
                     except Exception as e:
                         print(f"Error merging TWS positions: {e}")
                         
             except ImportError:
                 print("Cannot import ib_tws_sync. Skipping TWS sync.")
             except Exception as e:
                 print(f"TWS Sync Error: {e}")

        # IBKR Flex / Manual Sync
        if not ib_sync.sync_ibkr(): # Dacă sync eșuează, folosim datele vechi + prices
             print("Sync IBKR eșuat sau config lipsă. Se folosesc datele locale existente pentru cantități.")
        
        # Procesare Portfolio Tickers (Price update) = load_state()
    
    # 2. Actualizăm datele globale (Rates, Indicators, VIX) DOAR dacă nu suntem în html-only
    # Le salvăm și pe ele în state pentru consistență
    rates = state.get('rates', {'EUR': 1.0, 'USD': 0.95, 'RON': 0.20, 'GBP': 1.15})
    market_indicators = state.get('market_indicators', {})
    vix_val = state.get('vix_val', None)
    
    if args.mode != 'html-only':
        print("=== Actualizare Date Globale ===")
        rates = get_exchange_rates()
        state['rates'] = rates
        
        market_indicators = get_market_indicators()
        state['market_indicators'] = market_indicators
        
        vix_val = get_vix_data()
        if vix_val:
            state['vix_val'] = vix_val
            print(f"VIX: {vix_val:.2f}")
        else:
            print("VIX indisponibil, folosim valoarea anterioară.")
            
        # Economic Cycle
        curr_phase, next_phase = determine_economic_cycle()
        state['eco_phase'] = curr_phase
        state['eco_next_phase'] = next_phase
    
    # 3. Actualizări Secționale
    if args.mode in ['all', 'portfolio']:
        state = update_portfolio_data(state, rates, vix_val)
        
    if args.mode in ['all', 'watchlist']:
        state = update_watchlist_data(state, rates, vix_val)
        
    # 4. Salvare Stare
    save_state(state)
    print("\nStarea dashboard-ului a fost salvată.")
    
    # 5. Generare HTML din State
    # Convertim listele de dict-uri înapoi în DataFrame pentru funcția existentă
    portfolio_df = pd.DataFrame(state.get('portfolio', []))
    watchlist_df = pd.DataFrame(state.get('watchlist', []))
    
    # Verificăm indicatorii (s-ar putea să fie None în state inițial)
    indicators_data = state.get('market_indicators', {})
    
    print("\n=== Generare Dashboard HTML ===")
    generate_html_dashboard(portfolio_df, watchlist_df, indicators_data, "index.html", state)

if __name__ == "__main__":
    main()
