import requests
import xml.etree.ElementTree as ET
import pandas as pd
import os
import time
from datetime import datetime

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
    print("=== Sincronizare IBKR... ===")
    
    positions = []
    # Strategie:
    # 1. Verificăm dacă avem date recente din TWS (tws_positions.csv).
    # 2. Dacă da, le folosim (PRIMARY).
    # 3. Dacă nu, apelăm Flex Service (BACKUP).
    
    TWS_FILE_POS = 'tws_positions.csv'
    use_tws_primary = False
    
    if os.path.exists(TWS_FILE_POS):
        # Verificăm vechimea
        mtime = os.path.getmtime(TWS_FILE_POS)
        age = time.time() - mtime
        if age < 600: # 10 minute
            print(f"  -> Găsit fișier TWS recent ({int(age)}s). Folosim ca Sursă PRIMARĂ.")
            use_tws_primary = True
        else:
            print(f"  -> Fișier TWS vechi ({int(age)}s). Încercăm Flex (Backup).")
    
    if use_tws_primary:
        try:
             tdf = pd.read_csv(TWS_FILE_POS)
             for _, r in tdf.iterrows():
                  invest = float(r['Shares']) * float(r['Buy_Price'])
                  positions.append({
                      'Symbol': str(r['Symbol']),
                      'Shares': float(r['Shares']),
                      'Buy_Price': float(r['Buy_Price']), 
                      'Current_Price': float(r['Buy_Price']), 
                      'Current_Value': invest,
                      'Profit': 0, # Calculat mai târziu în market scanner
                      'Profit_Pct': 0,
                      'Investment': invest,
                      'Trail_Pct': 0,
                      'Trail_Stop_IBKR': 0
                  })
             print(f"  -> Încărcate {len(positions)} poziții din TWS.")
        except Exception as ex:
             print(f"Eroare citire TWS Backup: {ex}. Revert to Flex.")
             use_tws_primary = False
             positions = []

    need_flex_pos = not use_tws_primary
    need_flex_stats = False
    
    # Check stats freshness
    try:
        s_file = 'ib_stats.json'
        if os.path.exists(s_file):
            if time.time() - os.path.getmtime(s_file) > 1000: # Refresh if older than ~15 mins (Logic: TWS doesn't provide it, so we need Flex often if TWS is running)
                need_flex_stats = True
        else:
            need_flex_stats = True
    except: need_flex_stats = True

    if need_flex_pos or need_flex_stats:
        print(f"  -> Executare Flex Service... (Pos: {need_flex_pos}, Stats: {need_flex_stats})")
        # Flex Logic Here (Indentat sau lăsat în flow)
        # Încercăm din Env Vars (pentru GitHub Actions) sau Config File (Local)
        token = os.environ.get('IBKR_TOKEN')
        query_id = os.environ.get('IBKR_QUERY_ID')
        
        if not token or not query_id:
            token, query_id = load_config()
        
        if not token or not query_id:
            print(f"⚠️ Lipsă configurație Flex. (Backup indisponibil)")
            # Dacă TWS a eșuat și Flex nu e configurat, nu avem date.
        else:
            # --- FLEX DOWNLOAD LOGIC ---
            print(f"Solicitare raport Flex (Query ID: {query_id})...")
            
            # (Păstrăm logica de download, dar doar dacă use_tws_primary e False)
            # Acesta e un bloc mare de cod.
            # Pentru a nu duplicat mult cod în replace, voi insera un return sau wrap.
            
            # Logică Flex existentă (rescrisă pentru replace curat)
            # URL 1: Init Request
            base_req_url = "https://ndcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest"
            req_url = f"{base_req_url}?t={token}&q={query_id}&v=3"
            
            xml_root = None
            orders_map = {} # Initialize orders_map for Flex
            try:
                headers = {'User-Agent': 'Java/1.8.0_202'}
                r = requests.get(req_url, headers=headers, timeout=15)
                try:
                    xml_root = ET.fromstring(r.content)
                except ET.ParseError:
                    print(f"Eroare parse XML Flex Init: {r.text[:100]}")
                    xml_root = None
                
                if xml_root is not None:
                    status = xml_root.find('Status')
                    if status is not None and status.text == 'Success':
                        ref_code = xml_root.find('ReferenceCode').text
                        base_dl_url = xml_root.find('Url').text
                        print(f"Raport generat. Ref: {ref_code}. Așteptăm...")
                        time.sleep(5)
                        
                        dl_url = f"{base_dl_url}?q={ref_code}&t={token}&v=3"
                        
                        max_retries = 20
                        retry_delay = 5
                        root_dl = None

                        for attempt in range(max_retries):
                            try:
                                r = requests.get(dl_url, headers=headers, timeout=30)
                                try:
                                    root_dl = ET.fromstring(r.content)
                                except ET.ParseError:
                                    print("Eroare parse XML raport (retry)...")
                                    time.sleep(retry_delay)
                                    continue
                                
                                if root_dl.tag == 'FlexQueryResponse':
                                    print(f"Raport descărcat cu succes (FlexQueryResponse received).")
                                    break
                                    
                                status_attr = root_dl.get('status') 
                                err_code_elem = root_dl.find('ErrorCode')
                                
                                if status_attr == 'Success':
                                    print(f"Raport descărcat cu succes (Attempt {attempt+1}).")
                                    break
                                
                                err_code = err_code_elem.text if err_code_elem is not None else ""
                                err_msg_elem = root_dl.find('ErrorMessage')
                                err_msg = err_msg_elem.text if err_msg_elem is not None else "Unknown"
                                
                                if err_code in ['1003', '1018', '1019', '1022']:
                                    print(f"  ... Raport în procesare ({err_msg} - {err_code}). Așteptăm {retry_delay}s...")
                                    time.sleep(retry_delay)
                                    retry_delay = min(retry_delay + 2, 20) # Backoff
                                else:
                                    print(f"Eroare descărcare IBKR: {err_msg} (Code: {err_code})")
                                    root_dl = None # Indicate failure
                                    break
                                    
                            except Exception as e:
                                print(f"Eroare request download: {e}. Retry...")
                                time.sleep(retry_delay)
                        
                        if root_dl is None or (root_dl.get('status') != 'Success' and root_dl.tag != 'FlexQueryResponse'):
                            print("Timeout așteptare raport IBKR.")
                        else:
                            # Parse Active Orders (pentru Trail Stop)
                            for order in root_dl.iter('Order'):
                                try:
                                    sym = order.get('symbol')
                                    if not sym: continue
                                    if ' ' in sym: sym = sym.replace(' ', '.')
                                    
                                    order_type = order.get('orderType', '').upper()
                                    if 'TRAIL' in order_type:
                                        trail_pct = float(order.get('trailingPercent', 0))
                                        stop_price = float(order.get('stopPrice', 0))
                                        
                                        if trail_pct > 0:
                                            orders_map[sym] = {'trail_pct': trail_pct, 'trail_stop': stop_price}
                                            print(f"  → Găsit Ordin TRAIL pentru {sym}: {trail_pct}% (Stop: {stop_price})")
                                except Exception as e:
                                    pass # print(f"Err parse order: {e}") 

                            # Parse Open Positions
                            for pos in root_dl.iter('OpenPosition'):
                                if not need_flex_pos: break
                                sym = pos.get('symbol')
                                if not sym: continue
                                
                                try:
                                    qty = float(pos.get('position', 0))
                                    if qty == 0: continue
                                    
                                    avg_cost = float(pos.get('costBasisPrice', 0))
                                    if avg_cost == 0: avg_cost = float(pos.get('avgPrice', 0))
                                    
                                    mkt_price = float(pos.get('markPrice', 0))
                                    if mkt_price == 0: mkt_price = float(pos.get('closePrice', 0))
                                    
                                    mkt_val = float(pos.get('marketValue', 0))
                                    unreal_pnl = float(pos.get('unrealizedPNL', 0))
                                    
                                    invest = qty * avg_cost
                                    
                                    trail_data = orders_map.get(sym, {})
                                    
                                    item = {
                                        'Symbol': sym,
                                        'Shares': qty,
                                        'Buy_Price': avg_cost, 
                                        'Current_Price': mkt_price,
                                        'Current_Value': mkt_val,
                                        'Profit': unreal_pnl,
                                        'Profit_Pct': 0, # Recalculated later
                                        'Investment': invest,
                                        'Trail_Pct': trail_data.get('trail_pct', 0),
                                        'Trail_Stop_IBKR': trail_data.get('trail_stop', 0)
                                    }
                                    positions.append(item)
                                except ValueError:
                                    pass
                            

                            
                            # === Parse Performance Stats (MTD/YTD) ===
                            ib_stats = {}
                            
                            # Tag corect detectat: MTDYTDPerformanceSummary -> Children: MTDYTDPerformanceSummaryUnderlying
                            # Trebuie să sumăm tot pentru că vine defalcat per simbol
                            total_mtd = 0.0
                            total_ytd = 0.0
                            found_stats = False
                            
                            for summary in root_dl.iter('MTDYTDPerformanceSummary'):
                                for child in summary:
                                    try:
                                        # Flex include un rând de TOTAL care are simbolul gol
                                        # Trebuie să luăm doar acel rând, altfel dublăm suma (sumând și componentele)
                                        sym = child.get('symbol', '')
                                        
                                        if not sym:
                                            # Acesta este rândul de TOTAL
                                            mtd = float(child.get('mtmMTD', 0))
                                            ytd = float(child.get('mtmYTD', 0))
                                            
                                            total_mtd = mtd
                                            total_ytd = ytd
                                            found_stats = True
                                            print(f"  -> Found TOTAL Row: MTD={mtd}, YTD={ytd}")
                                    except: pass
                            
                            if found_stats:
                                ib_stats = {
                                    'mtd_val': total_mtd,
                                    'ytd_val': total_ytd,
                                    'updated': datetime.now().strftime('%Y-%m-%d %H:%M')
                                }
                                print(f"  -> Statistici Extrase (Sum): MTD={total_mtd:,.2f}, YTD={total_ytd:,.2f}")
                                
                                import json
                                with open('ib_stats.json', 'w') as f:
                                    json.dump(ib_stats, f)
                                    
                    else:
                        err = xml_root.find('ErrorMessage')
                        code = xml_root.find('ErrorCode')
                        msg = err.text if err is not None else "Unknown Error"
                        err_code = code.text if code is not None else "?"
                        print(f"Eroare IBKR Flex: {msg} (Code: {err_code})")
            except Exception as e:
                print(f"Eroare conexiune API: {e}")

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
    
    # Creare DataFrame
    new_df = pd.DataFrame(positions)
    
    # === Integrare TWS Orders (Live Stops) ===
    TWS_ORDERS_FILE = 'tws_orders.csv'
    if os.path.exists(TWS_ORDERS_FILE):
        print(f"Integrare date ordine live din {TWS_ORDERS_FILE}...")
        try:
            tws_df = pd.read_csv(TWS_ORDERS_FILE)
            # Mapăm Symbol -> Stop/Trail
            # Presupunem că un simbol are un singur ordin active de tip Sell (Stop). Luăm primul găsit.
            
            for _, row in tws_df.iterrows():
                t_sym = str(row.get('Symbol', ''))
                t_stop = float(row.get('Calculated_Stop', 0))
                t_pct = float(row.get('Trail_Pct', 0))
                
                # Căutăm în new_df și updatăm
                mask = new_df['Symbol'] == t_sym
                if mask.any():
                    if t_stop > 0:
                        new_df.loc[mask, 'Trail_Stop_IBKR'] = t_stop
                        # Putem actualiza si 'Trail_Stop' generic daca vrem sa suprascriem manualul? 
                        # Mai bine lasam Trail_Stop_IBKR separat si il decidem la afisare sau merge.
                    if t_pct > 0:
                        new_df.loc[mask, 'Trail_Pct'] = t_pct
        except Exception as e:
            print(f"Eroare procesare TWS Orders: {e}")

        
        # Merge cu preferințele locale (CSV vechi)
        
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



if __name__ == "__main__":
    sync_ibkr()
