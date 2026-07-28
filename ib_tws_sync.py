import asyncio
import datetime
import json
import math
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


RESEARCH_INSTRUMENTS = {
    'LQQ.PA': {
        'query_symbol': 'LQQ',
        'aliases': ['LQQ.PA', 'LQQ.FR', 'FR.LQQ'],
        'currency': 'EUR',
        'preferred_exchanges': ['SBF', 'SMART', 'EUREX'],
        'market': 'Europa / Nasdaq-100',
        'execution_brokers': ['IBKR', 'Tradeville'],
        'ibkr_role': 'date și execuție',
    },
    'TVBETETF.RO': {
        'query_symbol': 'TVBETETF',
        'aliases': ['TVBETETF.RO', 'TVBETETF'],
        'currency': 'RON',
        'preferred_exchanges': ['BVB', 'BUCHAREST', 'SMART'],
        'market': 'România / BVB',
        'execution_brokers': ['Tradeville'],
        'ibkr_role': 'doar sursă de date',
    },
}


def _finite_number(value):
    try:
        number = float(value)
        return number if math.isfinite(number) and abs(number) < 1e100 else None
    except (TypeError, ValueError):
        return None


def _contract_match_score(contract, config):
    """Prioritizează contractul exact, în moneda și piața configurate."""
    symbol = str(getattr(contract, 'symbol', '') or '').upper()
    local_symbol = str(getattr(contract, 'localSymbol', '') or '').upper()
    currency = str(getattr(contract, 'currency', '') or '').upper()
    sec_type = str(getattr(contract, 'secType', '') or '').upper()
    exchange_values = {
        str(getattr(contract, field, '') or '').upper()
        for field in ('exchange', 'primaryExchange')
    }
    expected_symbol = str(config.get('query_symbol', '')).upper()
    preferred_exchanges = {
        str(value).upper() for value in config.get('preferred_exchanges', [])
    }
    score = 0
    if symbol == expected_symbol:
        score += 40
    if local_symbol == expected_symbol:
        score += 35
    if currency == str(config.get('currency', '')).upper():
        score += 30
    if sec_type in {'STK', 'FUND'}:
        score += 15
    if exchange_values & preferred_exchanges:
        score += 20
    if _finite_number(getattr(contract, 'conId', None)):
        score += 5
    return score


def _resolve_research_contract(ib, config):
    descriptions = ib.reqMatchingSymbols(config['query_symbol']) or []
    contracts = [
        description.contract
        for description in descriptions
        if getattr(description, 'contract', None) is not None
    ]
    if contracts:
        contract = max(
            contracts,
            key=lambda candidate: _contract_match_score(candidate, config),
        )
    else:
        fallback_exchange = (
            config.get('preferred_exchanges') or ['SMART']
        )[0]
        contract = Stock(
            config['query_symbol'],
            fallback_exchange,
            config['currency'],
        )
        qualified = ib.qualifyContracts(contract) or []
        if qualified:
            contract = qualified[0]

    details = ib.reqContractDetails(contract) or []
    if not details:
        raise ValueError(
            f"Contract IBKR indisponibil pentru {config['query_symbol']}"
        )
    contract_id = getattr(contract, 'conId', None)
    detail = next(
        (
            item for item in details
            if getattr(getattr(item, 'contract', None), 'conId', None)
            == contract_id
        ),
        details[0],
    )
    return detail


def _serialize_contract_detail(detail):
    contract = detail.contract
    security_ids = {
        str(getattr(item, 'tag', '') or ''): str(
            getattr(item, 'value', '') or ''
        )
        for item in (getattr(detail, 'secIdList', None) or [])
        if getattr(item, 'tag', None)
    }
    return {
        'con_id': getattr(contract, 'conId', None),
        'symbol': getattr(contract, 'symbol', None),
        'local_symbol': getattr(contract, 'localSymbol', None),
        'security_type': getattr(contract, 'secType', None),
        'currency': getattr(contract, 'currency', None),
        'exchange': getattr(contract, 'exchange', None),
        'primary_exchange': getattr(contract, 'primaryExchange', None),
        'trading_class': getattr(contract, 'tradingClass', None),
        'long_name': getattr(detail, 'longName', None),
        'market_name': getattr(detail, 'marketName', None),
        'industry': getattr(detail, 'industry', None),
        'category': getattr(detail, 'category', None),
        'subcategory': getattr(detail, 'subcategory', None),
        'stock_type': getattr(detail, 'stockType', None),
        'valid_exchanges': getattr(detail, 'validExchanges', None),
        'time_zone': getattr(detail, 'timeZoneId', None),
        'trading_hours': getattr(detail, 'tradingHours', None),
        'liquid_hours': getattr(detail, 'liquidHours', None),
        'isin': security_ids.get('ISIN'),
    }


def _serialize_bar_date(value):
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    text = str(value or '').strip()
    for source_format in ('%Y%m%d', '%Y-%m-%d', '%Y%m%d %H:%M:%S'):
        try:
            return datetime.datetime.strptime(text, source_format).date().isoformat()
        except ValueError:
            continue
    return text[:10]


def _serialize_historical_bars(bars):
    serialized = []
    for bar in bars or []:
        values = {
            field: _finite_number(getattr(bar, field, None))
            for field in ('open', 'high', 'low', 'close', 'volume')
        }
        if any(values[field] is None for field in ('open', 'high', 'low', 'close')):
            continue
        serialized.append({
            'date': _serialize_bar_date(getattr(bar, 'date', None)),
            **values,
        })
    return serialized


def _load_instrument_cache(path):
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def fetch_research_instruments(
    ib, output_file='tws_instruments.json', instruments=None,
):
    """Extrage prin TWS date pentru analiză, independent de brokerul de execuție."""
    instruments = instruments or RESEARCH_INSTRUMENTS
    cached_payload = _load_instrument_cache(output_file)
    cached_instruments = cached_payload.get('instruments', {})
    fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = {}

    print("\n=== Date TWS pentru LQQ și ETF Patria-Tradeville ===")
    for dashboard_symbol, config in instruments.items():
        try:
            detail = _resolve_research_contract(ib, config)
            contract = detail.contract
            bars = ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr='1 Y',
                barSizeSetting='1 day',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1,
                keepUpToDate=False,
            )
            serialized_bars = _serialize_historical_bars(bars)
            if not serialized_bars:
                raise ValueError('Istoricul OHLCV IBKR este gol')

            latest_bar = serialized_bars[-1]
            # Ultima închidere IBKR este disponibilă fără abonamentul separat
            # necesar snapshoturilor live/delayed și nu blochează sincronizarea.
            market_data = {
                'market_price': None,
                'bid': None,
                'ask': None,
                'last': None,
                'close': latest_bar.get('close'),
                'volume': latest_bar.get('volume'),
                'as_of': latest_bar.get('date'),
            }
            result[dashboard_symbol] = {
                'symbol': dashboard_symbol,
                'aliases': list(config.get('aliases', [])),
                'market': config.get('market'),
                'instrument_type': 'ETF',
                'corporate_fundamentals_applicable': False,
                'fundamental_scope': (
                    'metadate contract și date OHLCV; ETF-ul nu are '
                    'earnings sau situații financiare de companie'
                ),
                'data_provider': 'IBKR TWS API',
                'data_broker': 'IBKR',
                'market_data_mode': 'ultima închidere istorică IBKR',
                'execution_brokers': list(
                    config.get('execution_brokers', [])
                ),
                'ibkr_role': config.get('ibkr_role'),
                'ibkr_data_only': (
                    'IBKR' not in config.get('execution_brokers', [])
                ),
                'fetched_at': fetched_at,
                'contract': _serialize_contract_detail(detail),
                'market_data': market_data,
                'bars': serialized_bars,
            }
            execution_text = ', '.join(config.get('execution_brokers', []))
            print(
                f"  -> {dashboard_symbol}: {len(serialized_bars)} zile IBKR; "
                f"execuție {execution_text}"
            )
        except Exception as exc:
            cached = cached_instruments.get(dashboard_symbol)
            if isinstance(cached, dict) and cached.get('bars'):
                cached = dict(cached)
                cached['cache_fallback'] = True
                cached['last_refresh_error'] = str(exc)
                result[dashboard_symbol] = cached
                print(
                    f"  -> {dashboard_symbol}: folosim ultimul cache TWS valid "
                    f"({exc})"
                )
            else:
                print(f"  -> {dashboard_symbol}: date TWS indisponibile ({exc})")

    if not result:
        return {}

    payload = {
        'fetched_at': fetched_at,
        'source': 'IBKR TWS API',
        'instruments': result,
    }
    with open(output_file, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    print(f"Salvat {output_file} cu {len(result)} instrumente.")
    return payload


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

        # Datele IBKR sunt folosite și pentru instrumente tranzacționate prin
        # alt broker. TVBETETF rămâne executabil exclusiv prin Tradeville.
        try:
            fetch_research_instruments(ib)
        except Exception as instrument_ex:
            print(
                "  -> Avertisment la sincronizarea instrumentelor TWS: "
                f"{instrument_ex}"
            )

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
                        'label': f'IBKR {len(accounts) + 1}',
                        'source': 'IBKR TWS',
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

            account_password = (
                os.environ.get('TWS_ACCOUNT_PASSWORD', '')
                or os.environ.get('PORTFOLIO_PASSWORD', '')
            )
            if not account_password and os.path.exists('password.txt'):
                try:
                    with open('password.txt', 'r', encoding='utf-8') as handle:
                        account_password = handle.read().strip()
                except OSError:
                    account_password = ''
            if account_password:
                import market_security
                encrypted_account = market_security.encrypt_for_js(
                    json.dumps(account_payload, ensure_ascii=False),
                    account_password,
                )
                with open('tws_account.enc.json', 'w', encoding='utf-8') as handle:
                    handle.write(encrypted_account)
                print("Salvat tws_account.enc.json (snapshot criptat pentru sincronizare).")
            else:
                print(
                    "  -> Snapshotul TWS nu a fost criptat: "
                    "TWS_ACCOUNT_PASSWORD/PORTFOLIO_PASSWORD indisponibil."
                )

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
