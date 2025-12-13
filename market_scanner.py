import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import os
import sys
from market_scanner_analysis import generate_market_analysis  # Import modul analiză
import time
import csv
import requests
from bs4 import BeautifulSoup

def get_finviz_target(ticker):
    """Preia price target-ul de pe Finviz prin scraping direct."""
    try:
        # Elimină sufixe pentru tickere europene (de ex: .DE)
        clean_ticker = ticker.split('.')[0]
        
        url = f"https://finviz.com/quote.ashx?t={clean_ticker}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Găsim tabelul cu datele fundamentale
        # Target Price este într-un td cu textul "Target Price" urmat de valoare
        rows = soup.find_all('tr', class_='table-dark-row')
        
        for row in rows:
            cells = row.find_all('td')
            for i, cell in enumerate(cells):
                if 'Target Price' in cell.get_text():
                    # Următorul cell conține valoarea
                    if i + 1 < len(cells):
                        target_text = cells[i + 1].get_text().strip()
                        if target_text and target_text != '-':
                            # Curăță și convertește
                            target = float(target_text.replace('$', '').replace(',', ''))
                            return target
        
        return None
    except Exception as e:
        print(f"  ⚠ Eroare Finviz pentru {ticker}: {str(e)[:50]}")
        return None

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

import json

HISTORY_FILE = "market_history.json"

def load_market_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
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
        'VIX': [(15, 'perfect 15'), (20, '15 normal 20'), (30, '20 tensiune 30'), (999, '30 panica')],
        'VIX1D': [(12, 'perfect 12'), (30, '12 normal 30'), (50, '30 tensiune 50'), (999, '50 panica')],
        'VIX9D': [(12, 'perfect 12'), (18, '12 normal 18'), (25, '18 tensiune 25'), (999, '25 panica')],
        'VXN': [(15, 'perfect 15'), (25, '15 normal 25'), (35, '25 tensiune 35'), (999, '35 panica')],
        'LTV': [(10, 'perfect 10'), (13, '10 normal 13'), (20, '13 tensiune 20'), (999, '20 panica')],
        'SKEW': [(135, 'low 135'), (150, '135 normal 150'), (165, '150 tensiune 165'), (999, '165 panica')],
        'MOVE': [(80, 'perfect 80'), (120, '80 normal 120'), (150, '120 tensiune 150'), (999, '150 panica')],
        'GVZ': [(17, 'perfect 17'), (22, '17 normal 22'), (30, '22 tensiune 30'), (999, '30 panica')],
        'OVX': [(25, 'perfect 25'), (35, '25 normal 35'), (50, '35 tensiune 50'), (999, '50 panica')],
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
                            elif 'normal' in desc.lower(): status = "Normal"
                            elif 'tensiune' in desc.lower(): status = "Tension"
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
                if value < 25:
                    status = 'Extreme Fear'
                    description = '0-24 extreme fear'
                elif value < 50:
                    status = 'Fear'
                    description = '25-49 fear'
                elif value < 75:
                    status = 'Greed'
                    description = '50-74 greed'
                else:
                    status = 'Extreme Greed'
                    description = '75-100 extreme greed'
                
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
        target_usd = get_finviz_target(ticker)
        target = None
        if target_usd:
            # Finviz e mereu USD? Nu neapărat. Dar pt US stocks da.
            # Dacă e stoc european, Finviz poate lipsi sau e în moneda locală?
            # Presupunem că Finviz dă în aceeași monedă ca ticker-ul (dacă îl găsește).
            target = target_usd * rate
            print(f"  → Target Finviz: €{target:.2f} (calc)")
        else:
            print(f"  → Target: N/A")
        
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
            'Buy_Price': round(buy_price, 2),
            'Target': target_display,  # None dacă nu există
            'Trail_Stop': round(trail_stop_price, 2),
            'Suggested_Stop': round(suggested_stop_atr, 2),
            'Trail_Pct': trail_pct,
            'Investment': round(investment, 2),
            'Current_Value': round(current_value, 2),
            'Profit': round(profit, 2),
            'Profit_Pct': round(profit_pct, 2),
            'Max_Profit': round(max_profit, 2) if max_profit else None,
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
        
        last_row = df.iloc[-1]
        
        last_close = get_scalar(last_row['Close']) * rate
        last_atr = get_scalar(last_row['ATR']) * rate
        if pd.isna(last_atr): last_atr = 0.0
        
        last_rsi = get_scalar(last_row['RSI'])
        sma_50 = get_scalar(last_row['SMA_50']) * rate
        sma_200 = get_scalar(last_row['SMA_200']) * rate
        
        # Preluare Target din Finviz
        target_val = None
        try:
            target_usd = get_finviz_target(ticker)
            if target_usd:
                target_val = target_usd * rate
            else:
                # Fallback: estimate from info if possible, but scraping logic is main.
                # yf info logic is slow, better skip if scraping fails.
                pass
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

        result = {
            'Ticker': ticker,
            'Price': round(last_close, 2),
            'Target': round(target_val, 2) if target_val else None,
            'Trend': trend,
            'RSI': round(last_rsi, 2),
            'RSI_Status': rsi_status,
            'ATR_14': round(last_atr, 2),
            'Stop_Loss': round(suggested_stop, 2),
            'SMA_50': round(sma_50, 2),
            'SMA_200': round(sma_200, 2),
            'VIX_Tag': vix_regime,
            'Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return result
        
    except Exception as e:
        print(f"Eroare procesare {ticker}: {e}")
        return None

def generate_html_dashboard(portfolio_df, watchlist_df, market_indicators, filename="index.html"):
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

    # Calculăm totalurile pentru sumar
    total_investment = portfolio_df['Investment'].sum() if not portfolio_df.empty else 0
    total_value = portfolio_df['Current_Value'].sum() if not portfolio_df.empty else 0
    total_profit = portfolio_df['Profit'].sum() if not portfolio_df.empty else 0
    
    # Recalculăm Max Profit și P/L la Stop iterând
    total_max_profit = 0
    total_pl_at_stop = 0
    
    if not portfolio_df.empty:
        for _, row in portfolio_df.iterrows():
            # Max Profit
            if row['Target'] and pd.notna(row['Target']):
                 mp = (row['Target'] - row['Buy_Price']) * row['Shares']
                 total_max_profit += mp
            
            # P/L la Stop
            if row['Trail_Stop'] and pd.notna(row['Trail_Stop']) and row['Trail_Stop'] > 0:
                 # Trail_Stop e deja convertit în EUR în dataframe? Verificăm process_portfolio_ticker.
                 # Da, e convertit.
                 pls = (row['Trail_Stop'] - row['Buy_Price']) * row['Shares']
                 total_pl_at_stop += pls

    total_profit_pct = ((total_value - total_investment) / total_investment * 100) if total_investment > 0 else 0

    # Citire parolă
    password = "1234"
    if os.path.exists("password.txt"):
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
        {css}
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <script>
            const APP_PASS = "{password}";
            
            function unlockPortfolio() {{
                const input = document.getElementById('pf-pass').value;
                if (input === APP_PASS) {{
                    document.getElementById('portfolio-lock').style.display = 'none';
                    document.getElementById('portfolio-data').style.display = 'block';
                    sessionStorage.setItem('pf_auth', 'true');
                }} else {{
                    alert('PIN Incorect');
                }}
            }}
            
            function checkPortfolioAuth() {{
                if (sessionStorage.getItem('pf_auth') === 'true') {{
                    document.getElementById('portfolio-lock').style.display = 'none';
                    document.getElementById('portfolio-data').style.display = 'block';
                }}
            }}
            
            // Inplace editing removed as per user request
            // Just portfolio check
            window.addEventListener('load', checkPortfolioAuth);
        </script>
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
                </div>
            
            
            <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Simbol</th>
                        <th>Acțiuni</th>
                        <th>Preț Cumpărare</th>
                        <th>Preț Curent</th>
                        <th>Grafic</th>
                        <th>Target</th>
                        <th>% Mid</th>
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
                <tbody>
    """
    
    # Portfolio rows
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
            pct_to_target = 0  # Initialize to avoid UnboundLocalError
            target_display = "N/A"
            pct_display = "N/A"
            max_profit_display = "N/A"
        
        sparkline_id = f"spark_{chart_id}"
        chart_id += 1
        
        # P/L la Stop Calc
        pl_at_stop_display = "-"
        pl_at_stop_class = ""
        if row['Trail_Stop'] and pd.notna(row['Trail_Stop']) and row['Trail_Stop'] > 0:
            pl_at_stop = (row['Trail_Stop'] - row['Buy_Price']) * row['Shares']
            pl_at_stop_display = f"€{pl_at_stop:,.2f}"
            pl_at_stop_class = "positive" if pl_at_stop > 0 else "negative"
        
        # Prepare values for inputs (handle N/A or strings)
        target_val = row['Target'] if row['Target'] and pd.notna(row['Target']) else ""
        if isinstance(target_val, (int, float)): target_val = f"{target_val:.2f}"
        
        trail_pct_val = row['Trail_Pct'] if pd.notna(row['Trail_Pct']) else 0
        
        trail_stop_val = row['Trail_Stop'] if row['Trail_Stop'] and pd.notna(row['Trail_Stop']) and row['Trail_Stop'] > 0 else ""
        if isinstance(trail_stop_val, (int, float)): trail_stop_val = f"{trail_stop_val:.2f}"

        html_head += f"""
                    <tr id="row-{row['Symbol']}" data-price="{row['Current_Price']}" data-buy="{row['Buy_Price']}" data-shares="{row['Shares']}">
                        <td><strong>{row['Symbol']}</strong></td>
                        <td>{row['Shares']}</td>
                        <td>€{row['Buy_Price']:.2f}</td>
                        <td>€{row['Current_Price']:.2f}</td>
                        <td><canvas id="{sparkline_id}" class="sparkline-container"></canvas></td>
                        
                        <!-- TARGET (Static/Auto) -->
                        <td>{target_display}</td>
                        
                        <td class="{'positive' if pct_to_target > 0 else 'negative' if row['Target'] else ''}">{pct_display}</td>
                        
                        <!-- Trail % (Static) -->
                        <td>{trail_pct_val:.1f}%</td>
                        
                        <!-- Trail Stop (Static) -->
                        <td>{f"€{trail_stop_val}" if isinstance(trail_stop_val, (int, float)) or (isinstance(trail_stop_val, str) and trail_stop_val) else "-"}</td>
                        
                        <td>€{row['Suggested_Stop']:.2f}</td>
                        <td>€{row['Investment']:,.2f}</td>
                        <td>€{row['Current_Value']:,.2f}</td>
                        <td class="{profit_cls}">€{row['Profit']:,.2f}</td>
                        <td class="{profit_cls}">{row['Profit_Pct']:.2f}%</td>
                        
                        <!-- P/L la Stop -->
                        <td class="{pl_at_stop_class}">{pl_at_stop_display}</td>
                        
                        <!-- MAX PROFIT (Recalculated via JS) -->
                        <td id="cell-{row['Symbol']}-maxprofit">{max_profit_display}</td>
                        
                        <td class="rsi-{status_cls}">{row['Status']}</td>
                        <td class="trend-{trend_cls}">{row['Trend']}</td>
                    </tr>
        """
        
    html_head += """
                </tbody>
            </table>
            </div> <!-- End table-container -->
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
    
    # Header row
    for name in indicator_order:
        if name in market_indicators:
            html_head += f"""
                            <th style="min-width: 80px; text-align: center; padding: 8px; font-size: 0.75rem;">{name}</th>"""
    
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
    
    # Adăugăm analiza AI
    html_head += generate_market_analysis(market_indicators)
    
    html_head += """
        </div>
        
        <div id="watchlist" class="tab-content">
            <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Price</th>
                        <th>Target</th>
                        <th>Trend</th>
                        <th>RSI</th>
                        <th>Status</th>
                        <th>ATR</th>
                        <th>Suggested Stop</th>
                        <th>SMA 50</th>
                        <th>SMA 200</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Watchlist rows
    # Trebuie să ne asigurăm că 'Target' există în DataFrame
    # process_watchlist_ticker returnează 'Target' în dict?
    # Verificăm: result = {'Ticker': ..., 'Target': target_display ...} - Da.
    
    for _, row in watchlist_df.iterrows():
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
        
        html_head += f"""
                    <tr>
                        <td><strong>{row['Ticker']}</strong></td>
                        <td>€{row['Price']:.2f}</td>
                        <td>{target_display}</td>
                        <td class="trend-{trend_cls}">{row['Trend']}</td>
                        <td>{row['RSI']:.0f}</td>
                        <td class="rsi-{rsi_cls}">{row['RSI_Status']}</td>
                        <td>{row['ATR_14']:.2f}</td>
                        <td>€{row['Stop_Loss']:.2f}</td>
                        <td>€{row['SMA_50']:.2f}</td>
                        <td>€{row['SMA_200']:.2f}</td>
                    </tr>
        """
        
    html_footer = """
                </tbody>
            </table>
            </div>
        </div>
        
        <div class="footer">
            Auto-generated by Antigravity Market Scanner
        </div>
    </div> <!-- END dashboard-content -->

        <script>
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

def main():
    print("=== Market Scanner (Portfolio + Watchlist) ===\n")
    
    # 0. Sincronizare IBKR (Opțional, doar local)
    try:
        ib_sync.sync_ibkr()
    except Exception as e:
        print(f"Sincronizare IBKR a eșuat sau nu este disponibilă: {e}")
    
    # 1.5 Preluare Curs Valutar
    print("\n=== Preluare Curs Valutar ===")
    rates = get_exchange_rates()

    # 1. Obținem indicatorii de piață
    print("\n=== Preluare Indicatori de Piață ===")
    market_indicators = get_market_indicators()
    
    # 2. Obținem VIX global
    vix_val = get_vix_data()
    if vix_val:
        print(f"VIX curent: {vix_val:.2f}")
    else:
        print("Atenție: VIX indisponibil")
        vix_val = None
    
    # 3. Procesăm Portfolio
    portfolio_data = load_portfolio()
    portfolio_results = []
    
    if not portfolio_data.empty:
        print(f"\n=== Procesare Portfolio ({len(portfolio_data)} poziții) ===")
        for _, row in portfolio_data.iterrows():
            print(f"Procesare: {row['symbol']}")
            data = process_portfolio_ticker(row, vix_val, rates)
            if data:
                portfolio_results.append(data)
    
    # 4. Procesăm Watchlist
    watchlist_tickers = load_watchlist()
    watchlist_results = []
    
    if watchlist_tickers:
        print(f"\n=== Procesare Watchlist ({len(watchlist_tickers)} tickere) ===")
        for ticker in watchlist_tickers:
            print(f"Procesare: {ticker}")
            data = process_watchlist_ticker(ticker, vix_val, rates)
            if data:
                watchlist_results.append(data)
    
    # 5. Generăm rapoartele
    if portfolio_results or watchlist_results:
        portfolio_df = pd.DataFrame(portfolio_results) if portfolio_results else pd.DataFrame()
        watchlist_df = pd.DataFrame(watchlist_results) if watchlist_results else pd.DataFrame()
        
        # Salvăm CSV-urile
        if not portfolio_df.empty:
            portfolio_df.to_csv('portfolio_analysis.csv', index=False)
            print(f"\nPortfolio salvat în 'portfolio_analysis.csv'")
        
        if not watchlist_df.empty:
            watchlist_df.to_csv('watchlist_analysis.csv', index=False)
            print(f"Watchlist salvat în 'watchlist_analysis.csv'")
        
        # Generăm HTML
        generate_html_dashboard(portfolio_df, watchlist_df, market_indicators, "index.html")
        
        # Previzualizare
        if not portfolio_df.empty:
            print("\n=== Portfolio Preview ===")
            print(portfolio_df[['Symbol', 'Shares', 'Current_Price', 'Profit', 'Profit_Pct']].head())
        
        if not watchlist_df.empty:
            print("\n=== Watchlist Preview ===")
            print(watchlist_df[['Ticker', 'Price', 'Trend', 'RSI']].head())
    else:
        print("Nu s-au generat rezultate.")

if __name__ == "__main__":
    main()
