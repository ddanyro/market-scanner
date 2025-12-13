import pandas as pd
from ib_insync import *
import os
import datetime
import sys

PORTFOLIO_FILE = 'portfolio.csv'

def sync_ibkr():
    """
    Se conectează la IBKR TWS local și actualizează portfolio.csv.
    Returnează True dacă s-a actualizat, False altfel.
    """
    print("=== Verificare Conexiune IBKR (TWS) ===")
    ib = IB()
    connected = False
    
    # Lista de porturi posibile
    ports = [7496, 7497, 4001, 4002]
    
    for port in ports:
        try:
            # Puteți modifica clientId dacă aveți conflicte
            print(f"Încercare conectare la 127.0.0.1:{port}...")
            ib.connect('127.0.0.1', port, clientId=123, timeout=1)
            print(f"Conectat cu succes la portul {port}!")
            connected = True
            break
        except Exception as e:
             pass
    
    if not connected:
        print("Nu s-a putut stabili conexiunea cu TWS/Gateway.")
        print("Dacă dorești sincronizare live, asigură-te că TWS este deschis și API activat (Port 7496/7497).")
        return False

    print("Descărcare poziții din IBKR...")
    try:
        portfolio_items = ib.portfolio()
    except Exception as e:
        print(f"Eroare la citirea portofoliului: {e}")
        ib.disconnect()
        return False
    
    if not portfolio_items:
        print("Portofoliu IBKR este gol sau inaccesibil.")
        ib.disconnect()
        return False

    print(f"Găsite {len(portfolio_items)} poziții.")

    # Convertim la listă de dicționare
    new_data = []
    
    for pos in portfolio_items:
        # Filtrare: Păstrăm Stocks (STK) și eventual CFD/Crypto dacă doriți
        # Momentan focus pe STK
        if pos.contract.secType == 'STK':
            symbol = pos.contract.symbol
            # Gestionare simboluri speciale (ex: BRK.B)
            if ' ' in symbol: symbol = symbol.replace(' ', '.')
            
            row = {
                'Symbol': symbol,
                'Shares': float(pos.position),
                'Buy_Price': float(pos.averageCost),
                'Current_Price': float(pos.marketPrice),
                'Current_Value': float(pos.marketValue),
                'Profit': float(pos.unrealizedPNL),
                'Profit_Pct': (float(pos.unrealizedPNL) / (float(pos.position) * float(pos.averageCost)) * 100) if (pos.position > 0 and pos.averageCost > 0) else 0.0,
                'Investment': float(pos.position) * float(pos.averageCost)
            }
            new_data.append(row)
            
    ib.disconnect()
            
    if not new_data:
        print("Nicio acțiune (STK) găsită în portofoliu.")
        return False
        
    new_df = pd.DataFrame(new_data)
    
    # Merge cu CSV existent
    if os.path.exists(PORTFOLIO_FILE):
        try:
            print("Îmbinare cu datele locale (Target, Stop Loss)...")
            old_df = pd.read_csv(PORTFOLIO_FILE)
            
            # Identificăm coloanele de păstrat din vechiul CSV (cele care nu vin din IBKR)
            # Coloane IBKR: Symbol, Shares, Buy_Price, Current_Price, Current_Value, Profit, Profit_Pct, Investment
            # Coloane Manuale: Target, Trail_Pct, Trail_Stop, Suggested_Stop, Max_Profit, Status, Trend, RSI...
            
            # Vrem să păstrăm Target și setările de Stop
            manual_cols = ['Symbol', 'Target', 'Trail_Pct', 'Trail_Stop', 'Suggested_Stop', 'Max_Profit']
            existing_cols = [c for c in manual_cols if c in old_df.columns]
            
            if existing_cols:
                old_subset = old_df[existing_cols]
                # Facem merge pe Symbol
                merged_df = pd.merge(new_df, old_subset, on='Symbol', how='left')
                
                # Să ne asigurăm că NaN-urile sunt gestionate
                if 'Trail_Pct' in merged_df.columns:
                    merged_df['Trail_Pct'] = merged_df['Trail_Pct'].fillna(15) # Default 15% trailing
            else:
                merged_df = new_df
                
            merged_df.to_csv(PORTFOLIO_FILE, index=False)
            print("Portofoliu actualizat cu succes!")
            return True
            
        except Exception as e:
            print(f"Eroare la îmbinare CSV: {e}")
            new_df.to_csv(PORTFOLIO_FILE, index=False) # Fallback
            return True
    else:
        new_df.to_csv(PORTFOLIO_FILE, index=False)
        print("Creat portofoliu nou.")
        return True

if __name__ == "__main__":
    sync_ibkr()
