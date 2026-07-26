import asyncio
import datetime
import json
import os
import pandas as pd
import sys

# Încercăm să importăm ib_insync, dacă nu există, ieșim silențios (e opțional)
try:
    from ib_insync import IB, Stock, Forex, Crypto
    HAS_IB_INSYNC = True
except ImportError:
    print("Modulul 'ib_insync' nu este instalat. TWS Sync indisponibil.")
    HAS_IB_INSYNC = False

def fetch_active_orders(output_file='tws_orders.csv'):
    """
    Se conectează la TWS local (Port 7497 sau 4001 Gateway) și extrage ordinele active (Stop, Trail).
    """
    if not HAS_IB_INSYNC:
        print("Eroare: ib_insync lipsă.")
        return False

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
        ib.reqAllOpenOrders() # Cere update de la server
        ib.sleep(1) # Așteaptă procesarea
        
        # ib.openTrades() returnează lista curentă de obiecte Trade (cached)
        open_trades = ib.openTrades()
        
        print(f"Găsite {len(open_trades)} ordine active în TWS.")
        
        orders_data = [] # Initialize list
        
        for t in open_trades:
            contract = t.contract
            order = t.order
            
            # Filtrare doar ordine interesante (Stop, Trail)
            if order.orderType in ['TRAIL', 'STP', 'STP LMT', 'LMT']:
                sym = contract.symbol
                if contract.currency != 'USD':
                    # Poate un sufix?
                    pass
                
                def clean_val(v):
                    if v is None or v > 1e20:
                        return 0.0
                    return float(v)

                lmt_price = clean_val(order.lmtPrice)
                aux_price = clean_val(order.auxPrice)
                trail_stop_price = clean_val(order.trailStopPrice)
                trail_pct = clean_val(order.trailingPercent)

                # Extragere date
                data = {
                    'Symbol': sym,
                    'OrderType': order.orderType,
                    'Action': order.action, # BUY/SELL
                    'Total_Qty': order.totalQuantity,
                    'Aux_Price': aux_price,
                    'Limit_Price': lmt_price,
                    'Stop_Price': trail_stop_price if order.orderType == 'TRAIL' else (aux_price if order.orderType in ['STP', 'STP LMT'] else 0.0),
                    'Trail_Pct': trail_pct,
                }
                
                # Corecție Stop Price
                # La Trail, 'trailStopPrice' e prețul trigger curent calculat de server.
                # Dacă e STP simplu, e 'auxPrice'.
                
                calc_stop = 0.0
                if order.orderType == 'TRAIL':
                    calc_stop = trail_stop_price
                elif order.orderType in ['STP', 'STP LMT']:
                    calc_stop = aux_price
                
                data['Calculated_Stop'] = calc_stop
                
                orders_data.append(data)
                print(f"  -> {sym}: {order.orderType} (Stop: {calc_stop})")

        if orders_data:
            df = pd.DataFrame(orders_data)
            df.to_csv(output_file, index=False)
            print(f"Salvat tws_orders.csv cu {len(orders_data)} înregistrări.")
        else:
            print("Niciun ordin relevant găsit.")
            
        # === Extragere Poziții (Portofoliu Backup) ===
        # Folosim asta dacă Flex Query dă date vechi (T-1)
        positions = ib.positions()
        print(f"Găsite {len(positions)} poziții deschise în TWS.")
        
        # Încercăm să obținem prețurile curente din portofoliul live
        prices_map = {}
        try:
            portfolio = ib.portfolio()
            for item in portfolio:
                if item.contract and item.contract.conId:
                    prices_map[item.contract.conId] = clean_val(item.marketPrice)
            print(f"  -> Extrase prețuri live pentru {len(prices_map)} poziții din portofoliu TWS.")
        except Exception as p_ex:
            print(f"  -> Avertisment la citirea prețurilor live din portofoliu TWS: {p_ex}")
            
        pos_data = []
        for p in positions:
            if p.position == 0: continue
            
            c = p.contract
            # Convert Symbol (ex: BRK B -> BRK.B)
            sym = c.symbol.replace(' ', '.')
            
            current_price = prices_map.get(c.conId, 0.0)
            
            pos_data.append({
                'Symbol': sym,
                'Shares': p.position,
                'Buy_Price': p.avgCost,
                'Current_Price': current_price,
                'Currency': c.currency
            })
            print(f"  -> Pos: {sym} x {p.position} (Preț curent TWS: {current_price})")
            
        if pos_data:
            pdf = pd.DataFrame(pos_data)
            pdf.to_csv('tws_positions.csv', index=False)
            print(f"Salvat tws_positions.csv cu {len(pos_data)} poziții.")
        else:
            print("Nicio poziție deschisă găsită.")

        # === Extragere sumar cont (cash, lichiditate și marjă) ===
        try:
            summary_tags = {
                'NetLiquidation', 'TotalCashValue', 'SettledCash', 'AvailableFunds',
                'BuyingPower', 'ExcessLiquidity', 'InitMarginReq', 'MaintMarginReq',
                'GrossPositionValue', 'Cushion',
            }
            summary_rows = ib.accountSummary()
            value_rows = ib.accountValues()
            account_ids = sorted({
                str(item.account) for item in list(summary_rows) + list(value_rows)
                if getattr(item, 'account', None)
            })
            accounts = []

            def parse_account_value(value):
                try:
                    number = float(value)
                    return number if abs(number) < 1e100 else None
                except (TypeError, ValueError):
                    return None

            for account_index, account_id in enumerate(account_ids, start=1):
                base_values = {}
                base_currency = None
                for item in value_rows:
                    if (
                        str(getattr(item, 'account', '')) == account_id
                        and str(getattr(item, 'tag', '')) == 'BaseCurrency'
                    ):
                        candidate = str(getattr(item, 'value', '')).strip()
                        if candidate:
                            base_currency = candidate
                            break
                if base_currency is None:
                    for item in summary_rows:
                        if (
                            str(getattr(item, 'account', '')) == account_id
                            and str(getattr(item, 'tag', '')) == 'NetLiquidation'
                        ):
                            candidate = str(getattr(item, 'currency', '')).strip()
                            if candidate not in ('', 'BASE'):
                                base_currency = candidate
                                break
                for item in summary_rows:
                    if str(getattr(item, 'account', '')) != account_id:
                        continue
                    tag = str(getattr(item, 'tag', ''))
                    currency = str(getattr(item, 'currency', ''))
                    if tag not in summary_tags:
                        continue
                    value = parse_account_value(getattr(item, 'value', None))
                    if value is None:
                        continue
                    if currency in ('BASE', '', base_currency) or tag == 'Cushion':
                        base_values[tag] = value

                cash_by_currency = {}
                for item in value_rows:
                    if str(getattr(item, 'account', '')) != account_id:
                        continue
                    tag = str(getattr(item, 'tag', ''))
                    currency = str(getattr(item, 'currency', ''))
                    if tag not in ('CashBalance', 'TotalCashBalance') or currency in ('BASE', ''):
                        continue
                    value = parse_account_value(getattr(item, 'value', None))
                    if value is not None:
                        cash_by_currency[currency] = value

                if base_values or cash_by_currency:
                    accounts.append({
                        'label': f'Cont {len(accounts) + 1}',
                        'base_currency': base_currency or 'BASE',
                        'summary': base_values,
                        'cash_by_currency': cash_by_currency,
                    })

            account_payload = {
                'fetched_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'source': 'TWS / IBKR API',
                'accounts': accounts,
            }
            with open('tws_account.json', 'w', encoding='utf-8') as handle:
                json.dump(account_payload, handle, ensure_ascii=False, indent=2)
            print(f"Salvat tws_account.json cu sumar pentru {len(accounts)} cont(uri).")

            portfolio_password = os.environ.get('PORTFOLIO_PASSWORD', '')
            if not portfolio_password and os.path.exists('password.txt'):
                try:
                    with open('password.txt', 'r', encoding='utf-8') as handle:
                        portfolio_password = handle.read().strip()
                except OSError:
                    portfolio_password = ''
            if portfolio_password:
                import market_security
                encrypted_account = market_security.encrypt_for_js(
                    json.dumps(account_payload, ensure_ascii=False),
                    portfolio_password,
                )
                with open('tws_account.enc.json', 'w', encoding='utf-8') as handle:
                    handle.write(encrypted_account)
                print("Salvat tws_account.enc.json (snapshot criptat pentru sincronizare).")
            else:
                print("  -> Snapshotul TWS nu a fost criptat: PORTFOLIO_PASSWORD indisponibil.")

            def ratio_band(numerator, denominator):
                if denominator is None or denominator <= 0 or numerator is None:
                    return 'indisponibil'
                ratio_pct = numerator / denominator * 100
                if ratio_pct < 5:
                    return 'sub 5%'
                if ratio_pct < 15:
                    return '5-15%'
                if ratio_pct < 30:
                    return '15-30%'
                if ratio_pct < 50:
                    return '30-50%'
                return 'peste 50%'

            sanitized_accounts = []
            for account in accounts:
                summary = account.get('summary', {})
                net_liquidation = summary.get('NetLiquidation')
                sanitized_accounts.append({
                    'label': account.get('label'),
                    'base_currency': account.get('base_currency'),
                    'cash_currencies': sorted(account.get('cash_by_currency', {}).keys()),
                    'cash_pct_band': ratio_band(summary.get('TotalCashValue'), net_liquidation),
                    'maintenance_margin_pct_band': ratio_band(
                        summary.get('MaintMarginReq'), net_liquidation
                    ),
                    'available_funds_status': (
                        'pozitiv' if summary.get('AvailableFunds', 0) > 0 else 'zero/negativ'
                    ),
                    'buying_power_status': (
                        'pozitiv' if summary.get('BuyingPower', 0) > 0 else 'zero/negativ'
                    ),
                    'excess_liquidity_status': (
                        'pozitiv' if summary.get('ExcessLiquidity', 0) > 0 else 'zero/negativ'
                    ),
                    'cushion_band': (
                        'sub 15%' if summary.get('Cushion', 0) < 0.15
                        else '15-30%' if summary.get('Cushion', 0) < 0.30
                        else 'peste 30%'
                    ),
                })
            sanitized_payload = {
                'fetched_at': account_payload['fetched_at'],
                'source': 'TWS / IBKR API',
                'privacy_mode': 'bands_only',
                'sanitized_accounts': sanitized_accounts,
            }
            with open('tws_account_risk.json', 'w', encoding='utf-8') as handle:
                json.dump(sanitized_payload, handle, ensure_ascii=False, indent=2)
            print("Salvat tws_account_risk.json (categorii fără solduri exacte).")
        except Exception as account_ex:
            print(f"  -> Avertisment la citirea sumarului de cont TWS: {account_ex}")

    except Exception as e:
        print(f"Eroare extragere ordine TWS: {e}")
    finally:
        ib.disconnect()
        
if __name__ == "__main__":
    fetch_active_orders()
