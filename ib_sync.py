import requests
import xml.etree.ElementTree as ET
import pandas as pd
import os
import time

PORTFOLIO_FILE = 'portfolio.csv'
CONFIG_FILE = 'ibkr_config.txt'

def load_config():
    """Citește Token-ul și Query ID-ul din fișierul de configurare."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                if len(lines) >= 2:
                    return lines[0], lines[1]
        except: pass
    return None, None

def sync_ibkr():
    """
    Sincronizează portofoliul folosind IBKR Flex Web Service (Metodă Cloud/API).
    Nu necesită TWS deschis.
    """
    print("=== Sincronizare IBKR (Flex Web Service) ===")
    
    # Încercăm din Env Vars (pentru GitHub Actions) sau Config File (Local)
    token = os.environ.get('IBKR_TOKEN')
    query_id = os.environ.get('IBKR_QUERY_ID')
    
    if not token or not query_id:
        token, query_id = load_config()
    
    if not token or not query_id:
        print(f"⚠️ Lipsă configurație Flex.")
        print(f"Pentru a activa sincronizarea automată:")
        print(f"1. Creează un Flex Query în IBKR Portal (Reports -> Flex Queries) pentru 'Open Positions'.")
        print(f"2. Activează Flex Web Service și generează un Token.")
        print(f"3. Creează fișierul '{CONFIG_FILE}' cu:")
        print("   TOKEN_LUNG_IBKR")
        print("   QUERY_ID_SCURT")
        return False
        
    print(f"Solicitare raport Flex (Query ID: {query_id})...")
    
    # URL 1: Init Request
    base_req_url = "https://ndcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest"
    req_url = f"{base_req_url}?t={token}&q={query_id}&v=3"
    
    try:
        headers = {'User-Agent': 'Java/1.8.0_202'} # User-Agent generic acceptat de IBKR
        r = requests.get(req_url, headers=headers, timeout=15)
        
        # Verificare răspuns XML
        try:
            root = ET.fromstring(r.content)
        except ET.ParseError:
            print(f"Eroare parse XML răspuns inițial: {r.text[:100]}")
            return False
            
        status = root.find('Status')
        
        if status is not None and status.text == 'Success':
            ref_code = root.find('ReferenceCode').text
            base_dl_url = root.find('Url').text
            print(f"Raport generat. Reference: {ref_code}. Așteptăm procesarea...")
        else:
            err = root.find('ErrorMessage')
            code = root.find('ErrorCode')
            msg = err.text if err is not None else "Unknown Error"
            err_code = code.text if code is not None else "?"
            print(f"Eroare IBKR Flex: {msg} (Code: {err_code})")
            return False
            
    except Exception as e:
        print(f"Eroare conexiune API: {e}")
        return False
        
    # Wait initially
    time.sleep(5)
    
    # URL 2: Download with Retry Loop
    dl_url = f"{base_dl_url}?q={ref_code}&t={token}&v=3"
    
    max_retries = 20
    retry_delay = 5
    
    root = None
    
    for attempt in range(max_retries):
        try:
            r = requests.get(dl_url, headers=headers, timeout=30)
            try:
                root = ET.fromstring(r.content)
            except ET.ParseError:
                print("Eroare parse XML raport (retry)...")
                time.sleep(retry_delay)
                continue
                
            # Verificare Status descărcare
            # Unele răspunsuri au Status ca atribut, altele ca element
            status_attr = root.get('status') 
            err_code_elem = root.find('ErrorCode')
            
            if status_attr == 'Success':
                print(f"Raport descărcat cu succes (Attempt {attempt+1}).")
                break
            
            # Verificăm erori specifice de "Not Ready"
            err_code = err_code_elem.text if err_code_elem is not None else ""
            err_msg_elem = root.find('ErrorMessage')
            err_msg = err_msg_elem.text if err_msg_elem is not None else "Unknown"
            
            if err_code in ['1003', '1018', '1019', '1022']:
                print(f"  ... Raport în procesare ({err_msg} - {err_code}). Așteptăm {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay + 2, 20) # Backoff
            else:
                # Eroare reală
                print(f"Eroare descărcare IBKR: {err_msg} (Code: {err_code})")
                
                # Uneori IBKR returnează Success dar XML-ul e dubios? Nu, ne bazăm pe status.
                # Dacă nu avem status Success și nici cod de wait, e fail.
                # Dar uneori XML-ul valid nu are status='Success' explicit? 
                # FlexStatementResponse are mereu status.
                return False
                
        except Exception as e:
            print(f"Eroare request download: {e}. Retry...")
            time.sleep(retry_delay)
            
    if root is None or root.get('status') != 'Success':
        print("Timeout așteptare raport IBKR.")
        return False
            
        # IBKR Flex XML Structure:
        # <FlexQueryResponse> -> <FlexStatements> -> <FlexStatement> -> <OpenPositions> -> <OpenPosition ... />
        
        # Parse Active Orders (pentru Trail Stop)
        orders_map = {}
        # Căutăm recursiv orice tag Order (necesită ca utilizatorul să includă 'Orders' în Flex Query)
        for order in root.iter('Order'):
            try:
                sym = order.get('symbol')
                if not sym: continue
                if ' ' in sym: sym = sym.replace(' ', '.')
                
                # Check for Trail
                order_type = order.get('orderType', '').upper()
                if 'TRAIL' in order_type:
                    # Trailing Percent
                    trail_pct = float(order.get('trailingPercent', 0))
                    
                    # Stop Price (Trigger)
                    # Flex attributes: 'auxPrice' (trail amount), 'stopPrice' (current trigger)
                    stop_price = float(order.get('stopPrice', 0))
                    
                    # Dacă avem procent, salvăm
                    if trail_pct > 0:
                        orders_map[sym] = {'trail_pct': trail_pct, 'trail_stop': stop_price}
                        print(f"  → Găsit Ordin TRAIL pentru {sym}: {trail_pct}% (Stop: {stop_price})")
            except Exception as e:
                # print(f"Err parse order: {e}") 
                pass

        positions = []
        # Căutăm recursiv orice tag OpenPosition
        for pos in root.iter('OpenPosition'):
            # Citim atributele. Numele atributelor depind de config-ul query-ului, 
            # dar de obicei sunt 'symbol', 'position', 'markPrice', 'costBasisPrice' (sau 'avgPrice')
            
            # Verificăm ce atribute avem disponibile (pentru debug)
            # print(pos.attrib) 
            
            sym = pos.get('symbol')
            if not sym: continue
            
            try:
                qty = float(pos.get('position', 0))
                if qty == 0: continue
                
                # Prețuri
                # Uneori e 'costBasisPrice', alteori 'avgPrice'
                avg_cost = float(pos.get('costBasisPrice', 0))
                if avg_cost == 0: avg_cost = float(pos.get('avgPrice', 0))
                
                mkt_price = float(pos.get('markPrice', 0))
                if mkt_price == 0: mkt_price = float(pos.get('closePrice', 0))
                
                mkt_val = float(pos.get('marketValue', 0))
                unreal_pnl = float(pos.get('unrealizedPNL', 0)) # sau 'fifoPnlUnrealized'
                
                # Gestionare simboluri cu spațiu (BRK B) sau "/"
                if ' ' in sym: sym = sym.replace(' ', '.')
                
                # Logică profit pct fallback
                calc_profit_pct = 0.0
                invest = qty * avg_cost
                if invest != 0:
                    calc_profit_pct = (unreal_pnl / invest) * 100
                
                # Verificăm dacă avem date de Trail din Orders
                trail_data = orders_map.get(sym, {})
                
                item = {
                    'Symbol': sym,
                    'Shares': qty,
                    'Buy_Price': avg_cost, 
                    'Current_Price': mkt_price,
                    'Current_Value': mkt_val,
                    'Profit': unreal_pnl,
                    'Profit_Pct': calc_profit_pct,
                    'Investment': invest,
                    'Trail_Pct': trail_data.get('trail_pct', 0),
                    'Trail_Stop_IBKR': trail_data.get('trail_stop', 0) # Salvăm explicit ca IBKR Stop
                }
                positions.append(item)
            except ValueError:
                continue
            
        # === Integrare Portofoliu Manual (Tradeville/Altele) ===
        MANUAL_FILE = 'tradeville_portfolio.csv'
        if os.path.exists(MANUAL_FILE):
             print(f"Adăugare poziții manuale din {MANUAL_FILE}...")
             try:
                 man_df = pd.read_csv(MANUAL_FILE)
                 for _, row in man_df.iterrows():
                     sym = str(row.get('Symbol', '')).strip()
                     if not sym or sym.lower() == 'nan': continue
                     
                     try:
                         qty = float(row.get('Shares', 0))
                         bp = float(row.get('Buy_Price', 0))
                         
                         # Verificăm dacă simbolul există deja (din IBKR) pt a nu duplica
                         exists = any(p['Symbol'] == sym for p in positions)
                         if exists:
                             print(f"  Info: Simbolul {sym} există deja în IBKR, se ignoră cel manual.")
                             continue
                         
                         item = {
                             'Symbol': sym,
                             'Shares': qty,
                             'Buy_Price': bp,
                             'Current_Price': 0.0,
                             'Current_Value': 0.0,
                             'Profit': 0.0,
                             'Profit_Pct': 0.0,
                             'Investment': qty * bp,
                             'Trail_Pct': float(row.get('Trail_Pct', 0)),
                             'Trail_Stop_IBKR': 0 # Manual nu are IBKR Stop
                         }
                         positions.append(item)
                     except: pass
             except Exception as e:
                 print(f"Eroare încărcare manual portfolio: {e}")

        if not positions:
            print("Nicio poziție găsită (nici în IBKR, nici manual).")
            # return False # Nu returnam False, poate e doar un portofoliu gol temporar
            
        print(f"Total poziții pentru analiză: {len(positions)}")
        
        # Creare DataFrame și Merge
        new_df = pd.DataFrame(positions)
        
        if os.path.exists(PORTFOLIO_FILE):
             try:
                print("Îmbinare cu preferințele locale...")
                old_df = pd.read_csv(PORTFOLIO_FILE)
                manual_cols = ['Symbol', 'Target', 'Max_Profit', 'Trail_Pct', 'Trail_Stop'] # Toate manualele persistă
                existing_cols = [c for c in manual_cols if c in old_df.columns]
                
                if existing_cols:
                    old_subset = old_df[existing_cols]
                    # Folosim suffixes pentru a identifica conflictele
                    merged_df = pd.merge(new_df, old_subset, on='Symbol', how='left', suffixes=('', '_old'))
                    
                    # Pentru fiecare coloană manuală, dacă există versiunea veche, o restaurăm (prioritate manual)
                    for col in existing_cols:
                        old_col_name = col + '_old'
                        if col in merged_df.columns and old_col_name in merged_df.columns:
                            # Preferăm valoarea veche (din CSV-ul persistent)
                            merged_df[col] = merged_df[old_col_name].combine_first(merged_df[col])
                            merged_df.drop(columns=[old_col_name], inplace=True)
                    
                    if 'Trail_Pct' in merged_df.columns:
                        merged_df['Trail_Pct'] = merged_df['Trail_Pct'].fillna(15)
                    new_df = merged_df
             except Exception as e:
                 print(f"Eroare merge, suprascriere: {e}")
        
        new_df.to_csv(PORTFOLIO_FILE, index=False)
        print("Portofoliu actualizat cu succes!")
        return True

    except Exception as e:
        print(f"Eroare procesare raport: {e}")
        return False

if __name__ == "__main__":
    sync_ibkr()
