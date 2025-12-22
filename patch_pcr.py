
import re

file_path = 'market_scanner_analysis.py'

with open(file_path, 'r') as f:
    content = f.read()

# Definim noua logică de fallback pentru PCR folosind SPY Options
new_fallback = """
        if not pcr_hist.empty:
            data['PCR_Value'] = pcr_hist['Close'].iloc[-1]
            data['Chart_PCR'] = pcr_hist['Close'].iloc[-60:].fillna(0).tolist()
        else:
            # Fallback: Calculate from SPY Options (Real-time Proxy)
            try:
                print("    -> PCR Tickers failed. Calculating from SPY Options chain...")
                spy = yf.Ticker("SPY")
                exps = spy.options
                if exps:
                    # Aggregate volume from first 2 expirations for better liquidity representation
                    total_c = 0
                    total_p = 0
                    for date in exps[:2]:
                        opt = spy.option_chain(date)
                        total_c += opt.calls['volume'].fillna(0).sum()
                        total_p += opt.puts['volume'].fillna(0).sum()
                    
                    if total_c > 0:
                        ratio = total_p / total_c
                        data['PCR_Value'] = ratio
                        data['Chart_PCR'] = [ratio] * 60 # Flat line representation for today
                        print(f"    -> Calculated SPY Option PCR: {ratio:.2f} (Vol: {total_p:.0f}/{total_c:.0f})")
                    else:
                        raise ValueError("No option volume")
                else:
                    raise ValueError("No expirations found")
            except Exception as opt_e:
                print(f"    ⚠ PCR Options Fallback failed: {opt_e}")
                data['PCR_Value'] = 0.8
                data['Chart_PCR'] = []
"""

# Regex pentru a înlocui blocul vechi if/else din secțiunea PCR
# Căutăm pattern-ul unde verificăm pcr_hist.empty
pattern = re.compile(r"if not pcr_hist\.empty:.*?else:.*?print\(\"  ⚠ PCR Data not found \(Yahoo\)\.\"\)", re.DOTALL)

# Verificăm dacă găsim pattern-ul (poate varia indentarea, așa că folosim o bucată mai mică sau replace direct)
# Mai sigur: Căutam blocul "if not pcr_hist.empty:" și înlocuim până la sfârșitul else-ului din acel bloc.

# Deoarece regex multiline e fragil, voi folosi o înlocuire string fixă a părții cunoscute.
target_block = """        if not pcr_hist.empty:
            data['PCR_Value'] = pcr_hist['Close'].iloc[-1]
            # Chart data (last 60)
            subset = pcr_hist['Close'].iloc[-60:]
            data['Chart_PCR'] = subset.fillna(0).tolist()
        else:
             data['PCR_Value'] = 0.8 # Neutral placeholder
             data['Chart_PCR'] = []
             print("  ⚠ PCR Data not found (Yahoo).")"""

if target_block in content:
    new_content = content.replace(target_block, new_fallback)
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("Succes: Logica PCR a fost actualizată.")
else:
    # Încercăm o căutare mai relaxată (poate spațiile diferă)
    print("Atenție: Blocul exact nu a fost găsit. Încercăm înlocuire manuală...")
    # ... logică alternativă dacă e nevoie ...
    # Voi afișa o parte din conținut pentru debug dacă eșuează
    start_idx = content.find("if not pcr_hist.empty:")
    if start_idx != -1:
         print(f"Found at {start_idx}. Context:\n{content[start_idx:start_idx+200]}")
    else:
         print("Blocul 'if not pcr_hist.empty:' nu a fost găsit deloc.")

