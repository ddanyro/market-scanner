
import re
import datetime
import os
import json

code_path = 'market_scanner_analysis.py'
with open(code_path, 'r') as f:
    full_code = f.read()

# 1. New function definition
new_get_data = """def get_swing_trading_data():
    \"\"\" Fetches data for Swing Trading Analysis including historical context. \"\"\"
    data = {}
    
    # 1. SPX Data
    try:
        spx = yf.Ticker("^GSPC")
        hist = spx.history(period="2y") 
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            hist['SMA50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA200'] = hist['Close'].rolling(window=200).mean()
            
            data['SPX_Price'] = current_price
            data['SPX_SMA50'] = hist['SMA50'].iloc[-1]
            data['SPX_SMA200'] = hist['SMA200'].iloc[-1]
            
            lookback = 60
            subset = hist.iloc[-lookback:]
            
            data['Chart_SPX'] = {
                'labels': [d.strftime('%m-%d') for d in subset.index],
                'price': subset['Close'].fillna(0).tolist(),
                'sma50': subset['SMA50'].fillna(0).tolist(),
                'sma200': subset['SMA200'].fillna(0).tolist()
            }
    except Exception as e:
        print(f"Error Swing Data (SPX): {e}")

    # 2. Fear & Greed
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://edition.cnn.com/'}
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", headers=headers, timeout=5)
        if r.status_code == 200:
            j = r.json()
            data['FG_Score'] = j.get('fear_and_greed', {}).get('score', 50)
            data['FG_Rating'] = j.get('fear_and_greed', {}).get('rating', 'neutral')
            hist = j.get('fear_and_greed_historical', {}).get('data', [])
            if hist:
                sorted_hist = sorted(hist, key=lambda x: x['x'])
                data['Chart_FG'] = [item['y'] for item in sorted_hist[-60:]]
            else:
                data['Chart_FG'] = [data['FG_Score']] * 60
    except Exception as e:
        print(f"Error Swing Data (F&G): {e}")
        data['FG_Score'] = 50
        data['FG_Rating'] = 'neutral'
        data['Chart_FG'] = []

    # 3. PCR (Put/Call Ratio) - Persistence
    try:
        tickers = ['^CPC', '^PCR', '^PCX'] # Try real
        pcr_found = False
        for t in tickers:
            try:
                temp = yf.Ticker(t).history(period="3mo")
                if not temp.empty:
                    data['PCR_Value'] = temp['Close'].iloc[-1]
                    pcr_found = True
                    break
            except: continue
            
        if not pcr_found: # Fallback SPY
            try:
                spy = yf.Ticker("SPY")
                exps = spy.options
                if exps:
                    total_c = 0; total_p = 0
                    for date in exps[:2]:
                        opt = spy.option_chain(date)
                        total_c += opt.calls['volume'].fillna(0).sum()
                        total_p += opt.puts['volume'].fillna(0).sum()
                    if total_c > 0:
                        data['PCR_Value'] = total_p / total_c
                        print(f"    -> Calculated SPY Option PCR: {data['PCR_Value']:.2f}")
            except Exception as opt_e:
                print(f"    PCR Fallback failed: {opt_e}")

    except Exception as e:
        print(f"Error Swing Data (PCR): {e}")

    # Persistence Logic
    if 'PCR_Value' in data:
        try:
            hist_file = "market_history.json"
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            db = {}
            if os.path.exists(hist_file):
                with open(hist_file, 'r') as f:
                    try: db = json.load(f)
                    except: db = {}
            
            if 'PCR' not in db: db['PCR'] = {}
            db['PCR'][today] = float(data['PCR_Value'])
            
            with open(hist_file, 'w') as f:
                json.dump(db, f, indent=4)
            
            # Chart from History
            dates = sorted(db['PCR'].keys())
            chart_vals = [db['PCR'][d] for d in dates[-60:]]
            
            if len(chart_vals) < 2:
                data['Chart_PCR'] = [data['PCR_Value']] * 60
            else:
                data['Chart_PCR'] = chart_vals
                
        except Exception as e:
            print(f"Error saving PCR history: {e}")
            if 'Chart_PCR' not in data: data['Chart_PCR'] = [data.get('PCR_Value', 0.8)] * 60
    else:
        data['PCR_Value'] = 0.8
        data['Chart_PCR'] = []

    return data"""

# Replace function
full_code = re.sub(r'def get_swing_trading_data\(\):.*?def generate_swing_trading_html', 
                   new_get_data + '\n\ndef generate_swing_trading_html', 
                   full_code, flags=re.DOTALL)

# Replace Text Label
old_label = 'pcr_text = "Panică (PCR>1)" if panic_signal else "Normal"'
new_label = 'pcr_text = "OPORTUNITATE (Fear)" if panic_signal else "Normal"'
if old_label in full_code:
    full_code = full_code.replace(old_label, new_label)
else:
    # Try fuzzy match or fallback replacement regex if exact string mismatch
    full_code = re.sub(r'pcr_text = "Panică.*?"', 'pcr_text = "OPORTUNITATE (Fear)"', full_code)

with open(code_path, 'w') as f:
    f.write(full_code)

print("Patch applied successfully.")
