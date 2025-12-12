import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import os
import time

def load_tickers(filename='tickers.txt'):
    """Încarcă lista de tickere dintr-un fișier text."""
    if not os.path.exists(filename):
        print(f"Fișierul {filename} nu a fost găsit. Se folosește o listă default.")
        return ['SPY', 'QQQ', 'AAPL', 'NVDA']
    
    with open(filename, 'r') as f:
        # Curăță spațiile și liniile goale
        tickers = [line.strip().upper() for line in f if line.strip()]
    return list(set(tickers)) # Elimină duplicatele

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
        # Luăm ultimele date
        hist = vix.history(period="5d")
        if hist.empty:
            return None
        current_vix = hist['Close'].iloc[-1]
        return current_vix
    except Exception as e:
        print(f"Eroare la preluarea VIX: {e}")
        return None

def process_ticker(ticker, vix_value):
    """Procesează un singur ticker și returnează datele."""
    try:
        time.sleep(2) # Delay mai mare (2 secunde) pentru a evita erorile de DNS/rețea
        
        # Descarcă date pentru ultimul an (necesar pentru SMA 200)
        # Nu folosim session custom
        df = yf.download(ticker, period="1y", progress=False)
        
        if df.empty:
            print(f"Nu există date pentru {ticker}")
            return None
        
        # Corecție pentru MultiIndex columns dacă există
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df.columns = df.columns.droplevel(1)
            except:
                pass
            
        # Calcule indicatori
        df['ATR'] = calculate_atr(df)
        df['RSI'] = calculate_rsi(df)
        df['SMA_50'] = calculate_sma(df, 50)
        df['SMA_200'] = calculate_sma(df, 200)
        
        # Preluăm ultimele valori
        last_row = df.iloc[-1]
        
        # Helper pt scalari
        def get_scalar(series_val, default=0.0):
            try:
                if hasattr(series_val, 'item'):
                    return series_val.item()
                return float(series_val)
            except:
                return default

        last_close = get_scalar(last_row['Close'])
        last_atr = get_scalar(last_row['ATR'])
        last_rsi = get_scalar(last_row['RSI'])
        sma_50 = get_scalar(last_row['SMA_50'])
        sma_200 = get_scalar(last_row['SMA_200'])
        
        if pd.isna(last_atr): last_atr = 0.0
        
        # --- Interpretări ---
        
        # Stop Loss sugerat
        stop_loss_dist = 2 * last_atr
        suggested_stop = last_close - stop_loss_dist
        
        # VIX Interpretation
        vix_regime = "Normal"
        if vix_value and vix_value > 20: vix_regime = "Ridicat"
        if vix_value and vix_value > 30: vix_regime = "Extrem"

        # RSI Interpretation
        rsi_status = "Neutral"
        if last_rsi > 70: rsi_status = "Overbought"
        elif last_rsi < 30: rsi_status = "Oversold"
        
        # Trend Interpretation (SMA Strategy)
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

def generate_html_report(df, filename="dashboard.html"):
    """Generează un raport HTML stilizat."""
    
    # CSS separat (nu este f-string) pentru a evita conflictele cu acoladele
    css = """
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #e0e0e0; padding: 20px; }
        h1 { text-align: center; color: #4dabf7; }
        .meta { text-align: center; margin-bottom: 20px; color: #888; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); background-color: #2d2d2d; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #444; }
        th { background-color: #333; color: #fff; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; }
        tr:hover { background-color: #3a3a3a; }
        
        /* Trend Colors */
        .trend-Strong-Bullish { color: #4caf50; font-weight: bold; }
        .trend-Bullish-Pullback { color: #81c784; }
        .trend-Strong-Bearish { color: #f44336; font-weight: bold; }
        .trend-Bearish-Rally { color: #e57373; }
        
        /* RSI Colors */
        .rsi-Overbought { color: #ff9800; font-weight: bold; }
        .rsi-Oversold { color: #2196f3; font-weight: bold; }
        
        /* VIX Tag */
        .vix-Ridicat { color: #ff9800; }
        .vix-Extrem { color: #f44336; font-weight: bold; animation: pulse 2s infinite; }
        
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        
        .footer { margin-top: 40px; text-align: center; font-size: 0.8rem; color: #666; }
    </style>
    """
    
    # Construim HTML-ul
    # Folosim f-string doar acolo unde avem variabile
    vix_val = df.iloc[0]['VIX_Tag'] if not df.empty else 'N/A'
    vix_cls = vix_val if not df.empty else 'Normal'
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_head = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="300"> <!-- Refresh automat la 5 minute -->
        <title>Market Scanner Dashboard</title>
        {css}
        <!-- DataTables CSS for sorting -->
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css">
        <style>
             /* Override DataTables standard colors for dark mode */
             .dataTables_wrapper .dataTables_length, .dataTables_wrapper .dataTables_filter, .dataTables_wrapper .dataTables_info, .dataTables_wrapper .dataTables_processing, .dataTables_wrapper .dataTables_paginate {{
                color: #ccc !important;
             }}
             table.dataTable tbody tr {{ background-color: transparent; }}
        </style>
    </head>
    <body>
        <h1>Market Scanner Dashboard</h1>
        <div class="meta">Generated: {timestamp} | VIX Status: <span class="vix-{vix_cls}">{vix_val}</span></div>
        
        <table id="scannerTable">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Price</th>
                    <th>Trend</th>
                    <th>RSI</th>
                    <th>RSI Status</th>
                    <th>ATR (14)</th>
                    <th>Stop Loss</th>
                    <th>VIX Tag</th>
                </tr>
            </thead>
            <tbody>
    """
    
    html_rows = ""
    for _, row in df.iterrows():
        trend_cls = row['Trend'].replace(' ', '-')
        rsi_cls = row['RSI_Status']
        vix_c = row['VIX_Tag']
        
        html_rows += f"""
                <tr>
                    <td><strong>{row['Ticker']}</strong></td>
                    <td>{row['Price']}</td>
                    <td class="trend-{trend_cls}">{row['Trend']}</td>
                    <td>{row['RSI']}</td>
                    <td class="rsi-{rsi_cls}">{row['RSI_Status']}</td>
                    <td>{row['ATR_14']}</td>
                    <td>{row['Stop_Loss']}</td>
                    <td class="vix-{vix_c}">{row['VIX_Tag']}</td>
                </tr>
        """
        
    html_footer = """
            </tbody>
        </table>
        
        <div class="footer">
            Auto-generated by Antigravity Market Scanner
        </div>

        <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>
        <script>
            $(document).ready( function () {
                $('#scannerTable').DataTable({
                    "paging": false,
                    "order": [[ 2, "desc" ]] // Sort by Trend initially
                });
            } );
        </script>
    </body>
    </html>
    """
    
    full_html = html_head + html_rows + html_footer
    
    with open(filename, 'w') as f:
        f.write(full_html)
    print(f"Raport HTML generat: {os.path.abspath(filename)}")

def main():
    print("=== Market Scanner (Standard) ===")
    tickers = load_tickers()
    print(f"Se analizează {len(tickers)} tickere...")
    
    # 1. Obținem VIX global
    vix_val = get_vix_data()
    if vix_val:
        print(f"Valoarea curentă VIX: {vix_val:.2f}")
    else:
        print("Atentie: Nu s-a putut prelua VIX.")
    
    results = []
    
    # 2. Iterăm prin tickere
    for t in tickers:
        print(f"Procesare: {t}")
        data = process_ticker(t, vix_val)
        if data:
            results.append(data)
            
    # 3. Salvare rezultate
    if results:
        df_results = pd.DataFrame(results)
        
        # Ordonare coloane logică
        cols = ['Ticker', 'Price', 'Trend', 'RSI', 'RSI_Status', 
                'ATR_14', 'Stop_Loss', 'SMA_50', 'SMA_200', 'VIX_Tag', 'Date']
        
        final_cols = [c for c in cols if c in df_results.columns]
        df_results = df_results[final_cols]
        
        # Export CSV
        output_file = 'scan_results.csv'
        df_results.to_csv(output_file, index=False)
        print(f"\nSucces! Rezultatele au fost salvate în '{output_file}'")
        
        # Export HTML
        generate_html_report(df_results, "dashboard.html")
        
        # Afișare preview
        print("\nPreview:")
        print(df_results.head())
    else:
        print("Nu s-au generat rezultate.")

if __name__ == "__main__":
    main()
