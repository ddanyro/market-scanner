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

def sync_watchlist_from_remote(url="https://betty333ro.github.io/market-scanner/", filepath='watchlist.csv'):
    """Sincronizează watchlist-ul cu pagina remote."""
    try:
        print(f"🔄 Sincronizare watchlist de pe {url}...")
        
        # Fetch remote page
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all Finviz links
        finviz_links = soup.find_all('a', href=re.compile(r'finviz\.com/quote\.ashx\?t='))
        
        if not finviz_links:
            print("⚠️  Nu s-au găsit simboluri pe pagina remote")
            return
        
        # Extract symbols
        remote_symbols = set()
        for link in finviz_links:
            symbol = link.get_text(strip=True).upper()
            if symbol:
                remote_symbols.add(symbol)
        
        # Load local symbols
        local_symbols = set()
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                if 'symbol' in df.columns:
                    local_symbols = set(df['symbol'].str.upper())
            except:
                pass
        
        # Find new symbols
        new_symbols = remote_symbols - local_symbols
        
        if new_symbols:
            print(f"  ✅ Găsite {len(new_symbols)} simboluri noi")
            
            # Add to watchlist
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
            else:
                df = pd.DataFrame(columns=['symbol'])
            
            new_rows = [{'symbol': s} for s in new_symbols]
            df_new = pd.DataFrame(new_rows)
            df = pd.concat([df, df_new], ignore_index=True)
            
            # Remove duplicates
            df['symbol'] = df['symbol'].str.upper()
            df = df.drop_duplicates(subset=['symbol'], keep='first')
            
            # Save
            df.to_csv(filepath, index=False)
            print(f"  ✅ Watchlist actualizat: {len(df)} simboluri total")
        else:
            print(f"  ✅ Watchlist la zi ({len(remote_symbols)} simboluri)")
            
    except Exception as e:
        print(f"⚠️  Eroare la sincronizare watchlist: {e}")

def load_watchlist(filename='watchlist.csv'):
    """Încarcă lista de tickere de urmărit din CSV."""
    if not os.path.exists(filename):
        print(f"Fișierul {filename} nu a fost găsit.")
        return []
    
    try:
        df = pd.read_csv(filename)
        if 'symbol' in df.columns:
            tickers = df['symbol'].str.upper().tolist()
            return list(set(tickers))  # Remove duplicates
        else:
            print(f"Coloana 'symbol' nu a fost găsită în {filename}")
            return []
    except Exception as e:
        print(f"Eroare la citirea {filename}: {e}")
        return []

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

def calculate_historical_monthly_returns():
    """Calculate average monthly returns for S&P 500 and NASDAQ since 1950."""
    returns = {}
    
    indices = {
        'SP500': '^GSPC',  # S&P 500
        'NASDAQ': '^IXIC'  # NASDAQ Composite
    }
    
    for name, ticker in indices.items():
        try:
            print(f"  → Calculez randamente istorice pentru {name}...")
            data = yf.Ticker(ticker)
            
            # Get historical data from 1950 to today
            hist = data.history(start="1950-01-01", end=datetime.datetime.now().strftime('%Y-%m-%d'))
            
            if hist.empty:
                print(f"    ⚠️  Nu există date pentru {name}")
                continue
            
            # Resample to monthly and calculate returns
            monthly = hist['Close'].resample('M').last()
            monthly_returns = monthly.pct_change().dropna() * 100  # Convert to percentage
            
            # Calculate average monthly return
            avg_return = monthly_returns.mean()
            
            # Calculate average return for each calendar month (1-12)
            monthly_returns_df = monthly_returns.to_frame('return')
            monthly_returns_df['month'] = monthly_returns_df.index.month
            monthly_averages = monthly_returns_df.groupby('month')['return'].mean().to_dict()
            
            returns[name] = {
                'avg_monthly_return': round(avg_return, 2),
                'data_points': len(monthly_returns),
                'start_date': monthly_returns.index[0].strftime('%Y-%m'),
                'end_date': monthly_returns.index[-1].strftime('%Y-%m'),
                'monthly_averages': {str(k): round(v, 2) for k, v in monthly_averages.items()}
            }
            
            print(f"    ✅ {name}: {avg_return:.2f}% avg monthly return ({len(monthly_returns)} months)")
            
        except Exception as e:
            print(f"    ❌ Eroare la calculul randamentelor pentru {name}: {e}")
            continue
    
    return returns

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
    
    # Calculate historical monthly returns
    historical_returns = calculate_historical_monthly_returns()
    if historical_returns:
        indicators['Historical_Returns'] = historical_returns
    
    return indicators

def get_macro_explanations():
    """Generează secțiunea de explicații pentru indicatori macroeconomici."""
    return """
    <div class="macro-explainer" style="background: var(--bg-white); padding: 32px; border-radius: var(--radius-md); margin-top: 32px; border: 1px solid var(--border-light); box-shadow: var(--shadow-sm);">
        <h3 style="color: var(--primary-purple); border-bottom: 2px solid var(--light-purple-bg); padding-bottom: 16px; margin-top: 0;">Glosar: Indicatori Macroeconomici Cheie & Impact</h3>
        <p style="font-size: 16px; color: var(--text-secondary); margin-bottom: 24px;">Ghid pentru înțelegerea evenimentelor din Calendarul Economic.</p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            
            <!-- Building Permits -->
            <div class="macro-card" style="background: var(--light-purple-bg); padding: 20px; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                <h4 style="color: #F59E0B; margin-top: 0;">Building Permits</h4>
                <p style="font-size: 14px; color: var(--text-primary);"><strong>Ce este:</strong> Un indicator "leading" (anticipativ) care arată cererea viitoare în sectorul imobiliar.</p>
                <p style="font-size: 14px; margin-bottom: 0; color: var(--text-primary);"><strong>Impact Piață:</strong> 
                   <br><span style="color: var(--success-green);">Cifre Mari:</span> Economie robustă, încredere consumatori.
                   <br><span style="color: var(--error-red);">Cifre Mici:</span> Semnal de recesiune.
                </p>
            </div>

            <!-- CPI -->
            <div class="macro-card" style="background: var(--light-purple-bg); padding: 20px; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                <h4 style="color: var(--error-red); margin-top: 0;">CPI (Consumer Price Index)</h4>
                <p style="font-size: 14px; color: var(--text-primary);"><strong>Ce este:</strong> Măsura principală a inflației. Cel mai urmărit indicator de către Fed.</p>
                <p style="font-size: 14px; margin-bottom: 0; color: var(--text-primary);"><strong>Impact Piață:</strong> 
                   <br><span style="color: var(--error-red);">Peste Așteptări:</span> Fed crește dobânzile → Acțiunile scad.
                   <br><span style="color: var(--success-green);">Sub Așteptări:</span> Fed poate tăia dobânzile → Raliu.
                </p>
            </div>

            <!-- NFP -->
            <div class="macro-card" style="background: var(--light-purple-bg); padding: 20px; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                <h4 style="color: #3B82F6; margin-top: 0;">NFP (Non-Farm Payrolls)</h4>
                <p style="font-size: 14px; color: var(--text-primary);"><strong>Ce este:</strong> Numărul de joburi noi create în SUA (lunar).</p>
                <p style="font-size: 14px; margin-bottom: 0; color: var(--text-primary);"><strong>Impact Piață:</strong> 
                   <br><span style="color: var(--success-green);">Joburi Multe:</span> Economie puternică (dar risc de inflație).
                   <br><span style="color: var(--error-red);">Joburi Puține:</span> Risc de recesiune.
                </p>
            </div>
            
             <!-- FOMC -->
            <div class="macro-card" style="background: var(--light-purple-bg); padding: 20px; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                <h4 style="color: var(--primary-purple); margin-top: 0;">FOMC (Ședința Fed)</h4>
                <p style="font-size: 14px; color: var(--text-primary);"><strong>Ce este:</strong> Decizia privind dobânda de referință. "Costul banilor".</p>
                <p style="font-size: 14px; margin-bottom: 0; color: var(--text-primary);"><strong>Impact Piață:</strong> 
                   <br>Dobânzi Mari = Acțiuni jos.
                   <br>Pivot (Tăiere) = Acțiuni sus 🚀
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
        /* ===== DRIPIFY-INSPIRED DESIGN SYSTEM ===== */
        
        /* CSS Variables */
        :root {
            --primary-purple: #7760F9;
            --dark-purple: #6349F8;
            --light-purple-bg: #F2F0FF;
            --text-primary: #111827;
            --text-secondary: #4B5563;
            --success-green: #5CD670;
            --error-red: #FE4141;
            --bg-white: #FFFFFF;
            --bg-light: #F9FAFB;
            --border-light: #E5E7EB;
            --shadow-sm: 0px 2px 8px rgba(0, 0, 0, 0.04);
            --shadow-md: 0px 4px 24px rgba(0, 0, 0, 0.06);
            --radius-sm: 8px;
            --radius-md: 16px;
            --radius-lg: 24px;
            --spacing-unit: 24px;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInFromLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.02);
            }
        }
        
        @keyframes shimmer {
            0% {
                background-position: -1000px 0;
            }
            100% {
                background-position: 1000px 0;
            }
        }
        
        /* Reset & Base */
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-light);
            color: var(--text-primary);
            line-height: 1.5;
            font-size: 16px;
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Typography */
        h1 {
            font-size: clamp(28px, 4vw, 36px);
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 16px;
        }
        
        h2 {
            font-size: clamp(20px, 3vw, 24px);
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 16px;
        }
        
        h3 {
            font-size: clamp(18px, 2vw, 20px);
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 12px;
        }
        
        h4 {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        
        p, .meta {
            font-size: 16px;
            color: var(--text-secondary);
            line-height: 1.6;
        }
        
        .meta {
            text-align: center;
            margin-bottom: var(--spacing-unit);
            font-size: 14px;
        }
        
        /* Container */
        .container {
            max-width: 1160px;
            margin: 0 auto;
            padding: 0 var(--spacing-unit);
        }
        
        /* Header & Navigation */
        .header-bar { 
            background: var(--bg-white);
            padding: 20px var(--spacing-unit);
            box-shadow: var(--shadow-sm);
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid var(--border-light);
        }
        
        .header-bar .container {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .hamburger { 
            font-size: 28px;
            cursor: pointer;
            color: var(--primary-purple);
            user-select: none;
            padding: 8px;
            border-radius: var(--radius-sm);
            transition: background 0.2s;
        }
        
        .hamburger:hover {
            background: var(--light-purple-bg);
            transform: scale(1.1);
        }
        
        .app-title { 
            font-size: clamp(20px, 3vw, 28px);
            font-weight: 700;
            color: var(--text-primary);
            flex-grow: 1;
            margin-left: 16px;
        }
        
        .menu-dropdown { 
            position: absolute;
            top: 80px;
            left: var(--spacing-unit);
            background: var(--bg-white);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-md);
            display: none;
            z-index: 1000;
            min-width: 240px;
            overflow: hidden;
            border: 1px solid var(--border-light);
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .menu-dropdown.show { 
            display: block;
            animation: slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .menu-item { 
            padding: 16px 20px;
            cursor: pointer;
            color: var(--text-primary);
            border-bottom: 1px solid var(--border-light);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 16px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .menu-item:hover { 
            background: var(--light-purple-bg);
            color: var(--primary-purple);
            padding-left: 28px;
        }
        
        .menu-item:last-child { 
            border-bottom: none;
        }
        
        /* Tab Content */
        .tab-content { 
            display: none;
            padding: var(--spacing-unit);
        }
        
        .tab-content.active { 
            display: block;
            animation: fadeIn 0.4s;
        }
        
        /* Cards */
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: var(--spacing-unit);
            margin-bottom: calc(var(--spacing-unit) * 2);
        }
        
        .summary-card { 
            background: var(--bg-white);
            padding: var(--spacing-unit);
            border-radius: var(--radius-md);
            text-align: center;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-light);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeIn 0.6s ease-out backwards;
        }
        
        .summary-card:nth-child(1) { animation-delay: 0.1s; }
        .summary-card:nth-child(2) { animation-delay: 0.2s; }
        .summary-card:nth-child(3) { animation-delay: 0.3s; }
        .summary-card:nth-child(4) { animation-delay: 0.4s; }
        .summary-card:nth-child(5) { animation-delay: 0.5s; }
        .summary-card:nth-child(6) { animation-delay: 0.6s; }
        
        .summary-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-4px) scale(1.02);
        }
        
        .summary-card h3 { 
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
        }
        
        .summary-card .value { 
            font-size: clamp(28px, 4vw, 36px);
            font-weight: 700;
            color: var(--text-primary);
        }
        
        /* Tables */
        .table-container { 
            width: 100%;
            overflow-x: auto;
            background: var(--bg-white);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-light);
            margin-top: var(--spacing-unit);
        }
        
        table { 
            width: 100%;
            border-collapse: collapse;
            background: var(--bg-white);
        }
        
        th, td { 
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid var(--border-light);
            font-size: 14px;
            white-space: nowrap;
        }
        
        th { 
            background: var(--bg-light);
            color: var(--text-primary);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.05em;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        tbody tr {
            transition: all 0.2s ease;
        }
        
        tr:hover { 
            background: var(--light-purple-bg);
            transform: scale(1.005);
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        /* Status Colors */
        .positive { 
            color: var(--success-green);
            font-weight: 600;
        }
        
        .negative { 
            color: var(--error-red);
            font-weight: 600;
        }
        
        .trend-Strong-Bullish { color: var(--success-green); font-weight: 600; }
        .trend-Bullish-Pullback { color: #86EFAC; }
        .trend-Strong-Bearish { color: var(--error-red); font-weight: 600; }
        .trend-Bearish-Rally { color: #FCA5A5; }
        
        .rsi-Overbought { color: #F59E0B; font-weight: 600; }
        .rsi-Oversold { color: #3B82F6; font-weight: 600; }
        
        .vix-Ridicat { color: #F59E0B; }
        .vix-Extrem { color: var(--error-red); font-weight: 600; }
        
        /* Buttons */
        button, .btn {
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 600;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-family: inherit;
            position: relative;
            overflow: hidden;
        }
        
        button:active, .btn:active {
            transform: scale(0.98);
        }
        
        .btn-primary, button[onclick*="unlock"] {
            background: var(--primary-purple);
            color: white;
            box-shadow: 0 4px 12px rgba(119, 96, 249, 0.3);
        }
        
        .btn-primary:hover, button[onclick*="unlock"]:hover {
            background: var(--dark-purple);
            box-shadow: 0 6px 20px rgba(119, 96, 249, 0.5);
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: var(--bg-white);
            color: var(--text-primary);
            border: 1px solid var(--border-light);
        }
        
        .btn-secondary:hover {
            background: var(--light-purple-bg);
            border-color: var(--primary-purple);
            color: var(--primary-purple);
            transform: translateY(-1px);
        }
        
        /* Inputs */
        .edit-input { 
            width: 80px;
            text-align: right;
            padding: 6px 12px;
            border: 1px solid var(--border-light);
            border-radius: var(--radius-sm);
            font-size: 14px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .edit-input:focus {
            outline: none;
            border-color: var(--primary-purple);
            box-shadow: 0 0 0 4px rgba(119, 96, 249, 0.15);
            transform: scale(1.02);
        }
        
        input[data-field="trail_pct"] { 
            width: 60px !important;
        }
        
        /* Sparklines */
        .sparkline-container { 
            width: 80px;
            height: 30px;
        }
        
        /* Footer */
        .footer { 
            margin-top: calc(var(--spacing-unit) * 2);
            text-align: center;
            font-size: 14px;
            color: var(--text-secondary);
            padding: var(--spacing-unit);
        }
        
        /* Animations */
        @keyframes fadeIn { 
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideDown { 
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            :root {
                --spacing-unit: 16px;
            }
            
            .header-bar {
                padding: 16px;
            }
            
            .summary {
                grid-template-columns: 1fr;
                gap: 16px;
            }
            
            .summary-card {
                padding: 20px;
            }
            
            .table-container {
                border-radius: var(--radius-sm);
            }
            
            th, td {
                padding: 12px 8px;
                font-size: 13px;
            }
            
            .menu-dropdown {
                left: 16px;
                right: 16px;
                min-width: auto;
            }
        }
        
        @media (max-width: 480px) {
            th, td {
                padding: 10px 6px;
                font-size: 12px;
            }
            
            .summary-card .value {
                font-size: 28px;
            }
        }
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
                color: var(--text-primary) !important;
                margin-bottom: 15px;
            }}
            .dataTables_wrapper .dataTables_filter input {{
                background-color: var(--bg-white);
                color: var(--text-primary);
                border: 1px solid var(--border-light);
                padding: 10px 14px;
                border-radius: var(--radius-sm);
                font-size: 14px;
            }}
            .dataTables_wrapper .dataTables_filter input:focus {{
                border-color: var(--primary-purple);
                box-shadow: 0 0 0 3px rgba(119, 96, 249, 0.1);
                outline: none;
            }}
            table.dataTable tbody tr {{
                background-color: var(--bg-white);
                color: var(--text-primary);
            }}
            table.dataTable tbody tr.even {{
                background-color: var(--bg-light);
            }}
            table.dataTable.hover tbody tr:hover, table.dataTable.display tbody tr:hover {{
                background-color: var(--light-purple-bg) !important;
            }}
            table.dataTable thead th, table.dataTable tfoot th {{
                border-bottom: 2px solid var(--border-light);
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
        <div class="container">
            <div class="hamburger" onclick="toggleMenu()">☰</div>
            <div class="app-title">Market Scanner</div>
            <div style="font-size: 0.8rem; color: var(--text-secondary);">Generated: {timestamp}</div>
        </div>
        
        <div id="navMenu" class="menu-dropdown">
            <div class="menu-item" onclick="switchTab('portfolio')">Portofoliu Activ</div>
            <div class="menu-item" onclick="switchTab('market')">Market Overview</div>
            <div class="menu-item" onclick="switchTab('watchlist')">Watchlist</div>
            <div class="menu-item" onclick="switchTab('volatility')">Volatility Calculator</div>
        </div>
    </div>
        
    <div class="container">
        <div id="portfolio" class="tab-content">
            
            <!-- LOCK SCREEN Local -->
            <div id="portfolio-lock" style="max-width: 500px; margin: 80px auto; text-align: center; padding: 48px; background: var(--bg-white); border-radius: var(--radius-lg); box-shadow: var(--shadow-md); border: 1px solid var(--border-light);">
                <h2 style="color: var(--text-primary); margin-bottom: 12px;">Secțiune Protejată</h2>
                <p style="color: var(--text-secondary); margin-bottom: 32px; font-size: 16px;">Introdu PIN-ul pentru a accesa portofoliul</p>
                <div style="display: flex; gap: 12px; justify-content: center; align-items: center;">
                    <input type="password" id="pf-pass" style="padding: 14px 20px; font-size: 18px; text-align: center; width: 180px; border-radius: var(--radius-sm); border: 1px solid var(--border-light); background: var(--bg-white); color: var(--text-primary); letter-spacing: 8px; font-weight: 600; transition: all 0.2s;" placeholder="••••" onkeyup="if(event.key==='Enter') unlockPortfolio()" onfocus="this.style.borderColor='var(--primary-purple)'; this.style.boxShadow='0 0 0 3px rgba(119,96,249,0.1)'" onblur="this.style.borderColor='var(--border-light)'; this.style.boxShadow='none'">
                    <button onclick="unlockPortfolio()" class="btn-primary">Unlock</button>
                </div>
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
                        <th>Trail Propus</th>
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
        
        # Calculate Trail LARG (Propus)
        atr_pct = (row.get('Finviz_ATR', 0) / row.get('Price_Native', 1) * 100) if row.get('Price_Native', 0) > 0 and row.get('Finviz_ATR', 0) else 0
        vol_w = row.get('Vol_W', 0) or 0
        vol_m = row.get('Vol_M', 0) or 0
        vols_valid = [v for v in [atr_pct, vol_w, vol_m] if v > 0]
        trail_larg = max(vols_valid) * 3 if vols_valid else 0
        
        # Color green if Trail LARG >= Trail %, red otherwise
        if trail_larg >= trail_pct_val:
            trail_larg_style = "color: #4caf50; font-weight: bold;"
        else:
            trail_larg_style = "color: #f44336; font-weight: bold;"
        trail_larg_display = f"{trail_larg:.1f}%" if trail_larg > 0 else "-"

        # Build Row HTML string (NO html_head += here)
        portfolio_rows_html += f"""
                    <tr id="row-{row['Symbol']}" data-price="{row['Current_Price']}" data-buy="{row['Buy_Price']}" data-shares="{row['Shares']}">
                        <td><strong style="cursor: pointer; color: #4dabf7; text-decoration: underline;" onclick="goToVolatility('{row['Symbol']}')">{row['Symbol']}</strong></td>
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
                        
                        <!-- Trail Propus (LARG) -->
                        <td style="{trail_larg_style}">{trail_larg_display}</td>
                        
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
            <h2 style="color: var(--text-primary); margin-bottom: 24px; text-align: center;">Indicatori de Piață</h2>
            <div style="background-color: var(--bg-white); padding: 32px; border-radius: var(--radius-md); overflow-x: auto; box-shadow: var(--shadow-sm); border: 1px solid var(--border-light);">
                <table style="width: 100%; background-color: transparent; box-shadow: none;">
                    <thead>
                        <tr style="border-bottom: 2px solid #444;">
    """
    
    # Ordinea indicatorilor
    indicator_order = ['VIX3M', 'VIX', 'VIX1D', 'VIX9D', 'VXN', 'LTV', 'SKEW', 'MOVE', 'Crypto Fear', 'GVZ', 'OVX', 'SPX']
    
    # Mapping Display Names
    display_map = {
        'VIX3M': 'VIX (3M)',
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
                color = '#10B981'  # Success green
            elif status == 'Normal':
                color = 'var(--text-secondary)'  # Medium gray for readability
            elif status == 'Tension':
                color = '#F59E0B'  # Warning orange
            elif status == 'Panic':
                color = '#EF4444'  # Error red
            else:
                color = 'var(--text-secondary)'
            
            html_head += f"""
                            <td style="text-align: center; padding: 10px; font-size: 18px; font-weight: 700; color: {color};">{value}</td>"""
    
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
    
    # Add Historical Returns Card
    if 'Historical_Returns' in market_indicators and market_indicators['Historical_Returns']:
        hist_returns = market_indicators['Historical_Returns']
        html_head += """
            <div style="background: var(--bg-white); padding: 32px; border-radius: var(--radius-md); margin-top: 32px; border: 1px solid var(--border-light); box-shadow: var(--shadow-sm);">
                <h3 style="color: var(--text-primary); margin-top: 0; text-align: center;">Randamente Lunare Istorice (1950 - Prezent)</h3>
        """
        
        # Add current and next month info
        import calendar
        now = datetime.datetime.now()
        current_month_name = now.strftime('%B')  # December (fără an)
        next_month_date = now + datetime.timedelta(days=32)
        next_month_date = next_month_date.replace(day=1)
        next_month_name = next_month_date.strftime('%B')  # January (fără an)
        next_month_num = next_month_date.month
        
        # Get expected returns for next month (convert to string for JSON keys)
        sp500_next = hist_returns.get('SP500', {}).get('monthly_averages', {}).get(str(next_month_num), 0)
        nasdaq_next = hist_returns.get('NASDAQ', {}).get('monthly_averages', {}).get(str(next_month_num), 0)
        
        sp500_color = "#4caf50" if sp500_next > 0 else "#f44336"
        nasdaq_color = "#4caf50" if nasdaq_next > 0 else "#f44336"
        
        # Get current month returns (convert to string for JSON keys)
        current_month_num = now.month
        sp500_current = hist_returns.get('SP500', {}).get('monthly_averages', {}).get(str(current_month_num), 0)
        nasdaq_current = hist_returns.get('NASDAQ', {}).get('monthly_averages', {}).get(str(current_month_num), 0)
        
        sp500_current_color = "#4caf50" if sp500_current > 0 else "#f44336"
        nasdaq_current_color = "#4caf50" if nasdaq_current > 0 else "#f44336"
        
        html_head += f"""
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th style="padding: clamp(6px, 2vw, 12px); text-align: left; border-bottom: 2px solid var(--border-light);"></th>
                            <th style="padding: clamp(6px, 2vw, 12px); text-align: center; border-bottom: 2px solid var(--border-light); color: var(--text-primary); font-size: clamp(13px, 3vw, 16px); font-weight: 600;">
                                {current_month_name.upper()}
                            </th>
                            <th style="padding: clamp(6px, 2vw, 12px); text-align: center; border-bottom: 2px solid var(--border-light); color: var(--text-primary); font-size: clamp(13px, 3vw, 16px); font-weight: 600;">
                                {next_month_name.upper()}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid var(--border-light);">
                            <td style="padding: clamp(8px, 2vw, 12px); color: var(--text-secondary); font-weight: 600; font-size: clamp(12px, 3vw, 15px); white-space: nowrap;">S&P 500</td>
                            <td style="padding: clamp(8px, 2vw, 12px); text-align: center; font-size: clamp(16px, 4vw, 18px); font-weight: 700; color: {sp500_current_color};">
                                {sp500_current:+.2f}%
                            </td>
                            <td style="padding: clamp(8px, 2vw, 12px); text-align: center; font-size: clamp(16px, 4vw, 18px); font-weight: 700; color: {sp500_color};">
                                {sp500_next:+.2f}%
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: clamp(8px, 2vw, 12px); color: var(--text-secondary); font-weight: 600; font-size: clamp(12px, 3vw, 15px);">NASDAQ</td>
                            <td style="padding: clamp(8px, 2vw, 12px); text-align: center; font-size: clamp(16px, 4vw, 18px); font-weight: 700; color: {nasdaq_current_color};">
                                {nasdaq_current:+.2f}%
                            </td>
                            <td style="padding: clamp(8px, 2vw, 12px); text-align: center; font-size: clamp(16px, 4vw, 18px); font-weight: 700; color: {nasdaq_color};">
                                {nasdaq_next:+.2f}%
                            </td>
                        </tr>
                    </tbody>
                </table>
                <div style="text-align: center; color: var(--text-secondary); font-size: clamp(11px, 2.5vw, 13px); margin-top: 16px; font-style: italic; padding: 0 8px;">
                    Bazat pe media istorică pentru fiecare lună (1950-Prezent)
                </div>
                
                <p style="text-align: center; color: #888; font-size: 0.8rem; margin-top: 15px; margin-bottom: 0;">
                    * Date calculate pe baza prețurilor de închidere lunare din Yahoo Finance
                </p>
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
            
            <!-- Watchlist Header -->
            <div style="text-align: center; margin-bottom: 24px; padding: 24px; background: var(--bg-white); border-radius: var(--radius-md); border: 1px solid var(--border-light); box-shadow: var(--shadow-sm);">
                <h2 style="color: var(--text-primary); margin: 0;">Watchlist</h2>
                <p style="color: var(--text-secondary); margin: 8px 0 0 0; font-size: 16px;">Total Stocks: <strong style="color: var(--primary-purple);">{len(watchlist_df)}</strong></p>
            </div>
            
            <!-- Filters -->
            <div class="filters-container" style="margin-bottom: 24px; display: flex; flex-wrap: wrap; gap: 16px; background: var(--bg-white); padding: 20px; border-radius: var(--radius-md); border: 1px solid var(--border-light); box-shadow: var(--shadow-sm);">
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Consensus</label>
                    <select id="filter-consensus" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); font-size: 14px; cursor: pointer;">
                        <option value="">All</option>
                        <option value="Strong Buy">Strong Buy</option>
                        <option value="Buy">Buy</option>
                        <option value="Hold">Hold</option>
                        <option value="Sell">Sell</option>
                    </select>
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Min Analysts</label>
                    <input type="number" id="filter-analysts" placeholder="0" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 120px; font-size: 14px;">
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Min Target %</label>
                    <input type="number" id="filter-target-pct" placeholder="0" step="any" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 120px; font-size: 14px;">
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Trend</label>
                    <select id="filter-trend" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 180px; font-size: 14px; cursor: pointer;">
                        <option value="">All</option>
                        <option value="Strong Bullish">Strong Bullish</option>
                        <option value="Bullish Pullback">Bullish Pullback</option>
                        <option value="Bearish Rally">Bearish Rally</option>
                        <option value="Strong Bearish">Strong Bearish</option>
                        <option value="Neutral">Neutral</option>
                    </select>
                </div>
                <div style="display: flex; flex-direction: column;">
                    <label style="font-size: 14px; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Status</label>
                    <select id="filter-status" style="padding: 10px 14px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); width: 140px; font-size: 14px; cursor: pointer;">
                        <option value="">All</option>
                        <option value="Oversold">Oversold</option>
                        <option value="Overbought">Overbought</option>
                        <option value="Neutral">Neutral</option>
                    </select>
                </div>
            </div>


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
                        <td><strong style="cursor: pointer; color: #4dabf7; text-decoration: underline;" onclick="goToVolatility('{row['Ticker']}')">{row['Ticker']}</strong></td>
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
        
        # Calculate Trail LARG (MAX × 3)
        vols = [atr_pct, get_val(item, 'Vol_W'), get_val(item, 'Vol_M')]
        vols_valid = [v for v in vols if v > 0]
        trail_larg = max(vols_valid) * 3 if vols_valid else 0
        
        vol_map[sym] = {
            'Price_Native': round(price_native, 2) if price_native else 0,
            'ATR_Val': round(atr, 2),
            'ATR_Pct': round(atr_pct, 2),
            'Vol_W': get_val(item, 'Vol_W'),
            'Vol_M': get_val(item, 'Vol_M'),
            'Trail_Larg': round(trail_larg, 2)
        }
        
        
    vol_json = json.dumps(vol_map)
    
    # Generate adjustment data for portfolio stocks with Trail Propus < Trail %
    adjust_data = []
    if not portfolio_df.empty:
        for _, row in portfolio_df.iterrows():
            sym = row.get('Symbol')
            if not sym:
                continue
            
            # Get volatility data
            atr_pct = (row.get('Finviz_ATR', 0) / row.get('Price_Native', 1) * 100) if row.get('Price_Native', 0) > 0 and row.get('Finviz_ATR', 0) else 0
            vol_w = row.get('Vol_W', 0) or 0
            vol_m = row.get('Vol_M', 0) or 0
            vols_valid = [v for v in [atr_pct, vol_w, vol_m] if v > 0]
            trail_larg = max(vols_valid) * 3 if vols_valid else 0
            
            trail_pct = row.get('Trail_Pct', 0) or 0
            old_stop = row.get('Trail_Stop', 0) or 0
            
            # Only include if Trail LARG < Trail % (red)
            if trail_larg > 0 and trail_pct > 0 and trail_larg < trail_pct and old_stop > 0:
                # Reconstruct original price when stop was set
                # Price = Stop / (1 - Trail% / 100)
                original_price = old_stop / (1 - trail_pct / 100)
                
                # Apply new trail to original price
                # New Stop = Original Price × (1 - Trail LARG / 100)
                new_stop = original_price * (1 - trail_larg / 100)
                
                # Get conversion rate (EUR to base currency)
                price_eur = row.get('Current_Price', 0) or 0
                price_native = row.get('Price_Native', 0) or 0
                rate = price_native / price_eur if price_eur > 0 else 1
                
                # Convert stops to base currency
                old_stop_native = old_stop * rate
                new_stop_native = new_stop * rate
                
                adjust_data.append({
                    'Symbol': sym,
                    'Trail_Current': round(trail_pct, 1),
                    'Trail_Propus': round(trail_larg, 1),
                    'Stop_Current_EUR': round(old_stop, 2),
                    'Stop_Ajustat_EUR': round(new_stop, 2),
                    'Stop_Current_Native': round(old_stop_native, 2),
                    'Stop_Ajustat_Native': round(new_stop_native, 2)
                })
    
    adjust_json = json.dumps(adjust_data)
    
    # Watchlist Closures
    html_footer = """
                </tbody>
            </table>
            </div>
        </div>

        <!-- Volatility Tab -->
        <div id="volatility" class="tab-content">
             <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 32px;">
                 <button id="vol-back-btn" onclick="goBackFromVolatility()" class="btn-secondary" style="padding: 10px 20px;">
                     ← Back
                 </button>
                 <h2 style="color: var(--text-primary); margin: 0;">Volatility Calculator</h2>
                 <div style="width: 100px;"></div> <!-- Spacer for centering -->
             </div>
             <div style="background: var(--bg-white); padding: 32px; border-radius: var(--radius-md); max-width: 600px; margin: 0 auto; box-shadow: var(--shadow-sm); border: 1px solid var(--border-light);">
                 <label style="color: var(--text-secondary); margin-bottom: 8px; display: block; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Search Symbol</label>
                 <input list="vol-tickers" id="vol-input" oninput="calcVolatility()" placeholder="Type symbol (e.g. NVDA)..." 
                        style="width: 100%; padding: 14px 16px; margin-bottom: 24px; background: var(--bg-white); color: var(--text-primary); border: 1px solid var(--border-light); border-radius: var(--radius-sm); font-size: 16px; transition: all 0.2s;" onfocus="this.style.borderColor='var(--primary-purple)'; this.style.boxShadow='0 0 0 3px rgba(119,96,249,0.1)'" onblur="this.style.borderColor='var(--border-light)'; this.style.boxShadow='none'">
                 <datalist id="vol-tickers">
    """ + "".join([f'<option value="{k}">' for k in sorted(vol_map.keys())]) + """
                 </datalist>
                 
                 <div id="vol-results" style="display: none;">
                      <table style="width: 100%; border-collapse: collapse; color: var(--text-primary);">
                          <tr style="border-bottom: 2px solid var(--border-light);">
                                <th style="text-align: left; padding: 10px; color: var(--text-secondary); font-weight: 600;">Metric</th>
                                <th style="text-align: right; padding: 10px; color: var(--text-secondary); font-weight: 600;">Value</th>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">Price (Base Currency)</td>
                                <td id="res-price-native" style="text-align: right; font-weight: 700; color: var(--success-green);">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">ATR (14) Value</td>
                                <td id="res-atr-val" style="text-align: right; font-weight: 700; color: var(--text-primary);">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">ATR (14) Volatility</td>
                                <td id="res-atr-pct" style="text-align: right; font-weight: 700; color: var(--primary-purple);">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">Daily Volatility</td>
                                <td id="res-day" style="text-align: right; font-weight: 700; color: var(--text-primary);">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">Weekly Volatility</td>
                                <td id="res-week" style="text-align: right; font-weight: 700; color: var(--text-primary);">-</td>
                          </tr>
                          <tr>
                                <td style="padding: 10px; color: var(--text-secondary);">Monthly Volatility</td>
                                <td id="res-month" style="text-align: right; font-weight: 700; color: var(--text-primary);">-</td>
                          </tr>
                      </table>
                      
                      
                      <!-- Suggested Stop & Buy (ATR-based) -->
                      <div style="margin-top: 24px; padding: 20px; background: var(--light-purple-bg); border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
                          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                              <div>
                                  <div style="color: var(--text-secondary); font-size: 14px; margin-bottom: 5px; font-weight: 600;">Suggested Stop (2×ATR)</div>
                                  <div id="suggested-stop" style="font-size: 1.1rem; font-weight: bold; color: #f44336;">-</div>
                              </div>
                              <div>
                                  <div style="color: var(--text-secondary); font-size: 14px; margin-bottom: 5px; font-weight: 600;">Suggested Buy (2×ATR)</div>
                                  <div id="suggested-buy" style="font-size: 1.1rem; font-weight: bold; color: #4caf50;">-</div>
                              </div>
                          </div>
                      </div>
                      
                      <!-- Trailing Stop Calculations -->
                      <h4 style="color: var(--primary-purple); margin-top: 30px; margin-bottom: 15px; text-align: center;">Trailing Stop Levels</h4>
                      <table style="width: 100%; border-collapse: collapse; color: var(--text-primary); margin-top: 10px;">
                          <tr style="border-bottom: 1px solid var(--border-light);">
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
             
             <!-- Stop Adjustment Table for Portfolio (Trail Propus < Trail %) -->
             <div id="stop-adjust-section" style="margin-top: 30px; max-width: 800px; margin-left: auto; margin-right: auto;">
                 <h4 style="color: #f44336; text-align: center; margin-bottom: 15px;">🔴 Ajustare Stop - Portofoliu (Trail Propus < Trail %)</h4>
                 <div id="adjust-table-container"></div>
             </div>
             
             <script>
                const adjustData = """ + adjust_json + """;
                
                // Render adjustment table (filtered by symbol if provided)
                function renderAdjustTable(filterSymbol) {
                    const container = document.getElementById('adjust-table-container');
                    
                    // Filter data by symbol if provided
                    let dataToShow = adjustData;
                    if (filterSymbol) {
                        dataToShow = adjustData.filter(item => item.Symbol === filterSymbol);
                    }
                    
                    if (!dataToShow || dataToShow.length === 0) {
                        if (filterSymbol) {
                            container.innerHTML = '<p style="text-align: center; color: #aaa;">✅ Stop-ul pentru ' + filterSymbol + ' este OK</p>';
                        } else {
                            container.innerHTML = '<p style="text-align: center; color: #aaa;">✅ Toate stop-urile sunt OK</p>';
                        }
                        return;
                    }
                    
                    let html = `
                        <table style="width: 100%; border-collapse: collapse; color: var(--text-primary); background: var(--bg-white); border-radius: var(--radius-sm); overflow: hidden; border: 1px solid var(--border-light);">
                            <thead>
                                <tr style="background: var(--bg-light); border-bottom: 2px solid var(--border-light);">
                                    <th style="padding: 12px; text-align: left;">Symbol</th>
                                    <th style="padding: 12px; text-align: right;">Trail %</th>
                                    <th style="padding: 12px; text-align: right;">Trail Propus</th>
                                    <th style="padding: 12px; text-align: right;">Stop Curent (EUR)</th>
                                    <th style="padding: 12px; text-align: right;">Stop Ajustat (EUR)</th>
                                    <th style="padding: 12px; text-align: right;">Stop Curent (Base)</th>
                                    <th style="padding: 12px; text-align: right;">Stop Ajustat (Base)</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    dataToShow.forEach(item => {
                        html += `
                            <tr style="border-bottom: 1px solid #333;">
                                <td style="padding: 10px;"><strong style="color: #4dabf7;">${item.Symbol}</strong></td>
                                <td style="padding: 10px; text-align: right;">${item.Trail_Current}%</td>
                                <td style="padding: 10px; text-align: right; color: #f44336; font-weight: bold;">${item.Trail_Propus}%</td>
                                <td style="padding: 10px; text-align: right;">€${item.Stop_Current_EUR}</td>
                                <td style="padding: 10px; text-align: right; color: #4caf50; font-weight: bold;">€${item.Stop_Ajustat_EUR}</td>
                                <td style="padding: 10px; text-align: right;">${item.Stop_Current_Native}</td>
                                <td style="padding: 10px; text-align: right; color: #4caf50; font-weight: bold;">${item.Stop_Ajustat_Native}</td>
                            </tr>
                        `;
                    });
                    
                    html += `
                            </tbody>
                        </table>
                    `;
                    
                    container.innerHTML = html;
                }
                
                // Don't render on load - only when symbol is selected
                // renderAdjustTable();
             </script>
             
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
                         
                         // Update adjustment table for this symbol
                         renderAdjustTable(val);
                    } else {
                         resDiv.style.display = 'none';
                         renderAdjustTable(null);
                    }
                }
                
                // Track source tab for back navigation
                let sourceTab = 'portfolio';
                
                // Function to navigate to Volatility Calculator with symbol
                function goToVolatility(symbol) {
                    // Save current tab by checking for active class
                    const currentTab = document.querySelector('.tab-content.active');
                    if (currentTab) {
                        sourceTab = currentTab.id;
                    }
                    
                    switchTab('volatility');
                    document.getElementById('vol-input').value = symbol;
                    calcVolatility();
                }
                
                // Function to go back to source tab
                function goBackFromVolatility() {
                    switchTab(sourceTab);
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
    </div> <!-- End container -->
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
    
    # Sync watchlist from remote
    sync_watchlist_from_remote()
    
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
