import asyncio
import pandas as pd
import sys

# Încercăm să importăm ib_insync, dacă nu există, ieșim silențios (e opțional)
try:
    from ib_insync import IB, Stock, Forex, Crypto
except ImportError:
    print("Modulul 'ib_insync' nu este instalat. Pentru a extrage ordine din TWS, rulează: pip install ib_insync")
    sys.exit(0)

def fetch_active_orders(output_file='tws_orders.csv'):
    """
    Se conectează la TWS local (Port 7497 sau 4001 Gateway) și extrage ordinele active (Stop, Trail).
    """
    print("\n=== Conectare TWS pentru Ordine Active ===")
    ib = IB()
    
    ports = [7497, 4001, 7496] # Porturi standard TWS/Gateway
    connected = False
    
    for port in ports:
        try:
            # ClientID 0 sau 1. Folosim un ID random/fix pentru a nu intra în conflict
            ib.connect('127.0.0.1', port, clientId=99, timeout=2)
            print(f"Conectat la TWS pe portul {port}.")
            connected = True
            break
        except Exception:
            pass
            
    if not connected:
        print("Nu s-a putut conecta la TWS (verifică dacă e deschis și API enabled în Settings -> API -> Settings).")
        print("Sărim peste actualizarea ordinelor live.")
        return False

    try:
        # Request Toate Ordinele Deschise
        trades = ib.reqAllOpenOrders()
        # 'trades' este o listă de obiecte (Trade sau Order?) 
        # În ib_insync, reqAllOpenOrders returnează o listă de obiecte Order.
        # Dar pentru a avea și Contract, folosim reqOpenOrders care returnează (OpenOrder object)???
        # ib.reqAllOpenOrders() returnează [Order, Order...]
        
        # Mai bine folosim:
        client_orders = ib.reqOpenOrders() # Returnează o listă de obiecte Order (fără contract detalii full?)
        
        # O metodă mai bună în ib_insync pentru detalii complete:
        # ib.positions() -> Portofoliu
        # ib.orders() -> Doar ordinele curente ale sesiunii?
        # ib.reqAllOpenOrders() -> Toate de pe server.
        
        orders_data = []
        all_open = ib.reqAllOpenOrders()
        
        # Mapare contracte pentru a ști simbolul
        # reqAllOpenOrders returnează doar Order objects. Contractul e legat?
        # Nu. Metoda care returnează legătura e reqOpenOrders() care updatează starea internă?
        
        # Să folosim ib.openTrades() -> Returnează o listă de obiecte 'Trade' care conțin (contract, order, orderStatus).
        open_trades = ib.reqOpenTrades() # Aceasta e cea mai robustă.
        
        if not open_trades:
            # Poate nu a apucat să primească?
            ib.sleep(1)
            open_trades = ib.openTrades()
            
        print(f"Găsite {len(open_trades)} ordine active.")
        
        for t in open_trades:
            contract = t.contract
            order = t.order
            
            # Filtrare doar ordine interesante (Stop, Trail)
            if order.orderType in ['TRAIL', 'STP', 'STP LMT', 'LMT']:
                sym = contract.symbol
                if contract.currency != 'USD':
                    # Poate un sufix?
                    pass
                
                # Extragere date
                data = {
                    'Symbol': sym,
                    'OrderType': order.orderType,
                    'Action': order.action, # BUY/SELL
                    'Total_Qty': order.totalQuantity,
                    'Aux_Price': order.auxPrice, # Trail amount sau Stop offset
                    'Stop_Price': order.trailStopPrice if order.trailStopPrice else order.lmtPrice if order.lmtPrice else 0
                }
                
                # Dacă e Trail, avem trailingPercent?
                if order.trailingPercent:
                    data['Trail_Pct'] = order.trailingPercent
                
                # Corecție Stop Price
                # La Trail, 'trailStopPrice' e prețul trigger curent calculat de server.
                # Dacă e STP simplu, e 'auxPrice'.
                
                calc_stop = 0
                if order.orderType == 'TRAIL':
                    calc_stop = order.trailStopPrice
                elif order.orderType in ['STP', 'STP LMT']:
                    calc_stop = order.auxPrice
                
                data['Calculated_Stop'] = calc_stop
                
                orders_data.append(data)
                print(f"  -> {sym}: {order.orderType} (Stop: {calc_stop})")

        if orders_data:
            df = pd.DataFrame(orders_data)
            df.to_csv(output_file, index=False)
            print(f"Salvat tws_orders.csv cu {len(orders_data)} înregistrări.")
        else:
            print("Niciun ordin relevant găsit.")

    except Exception as e:
        print(f"Eroare extragere ordine TWS: {e}")
    finally:
        ib.disconnect()
        
if __name__ == "__main__":
    fetch_active_orders()
