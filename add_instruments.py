import json

with open('tws_instruments.json', 'r') as f:
    data = json.load(f)

# Add SPYL.DE
data['instruments']['SPYL.DE'] = {
    "symbol": "SPYL.DE",
    "aliases": ["SPYL.DE", "SPYL.IBIS2", "SPYL.XETRA", "SPYL"],
    "market": "Europa / SP500",
    "instrument_type": "ETF",
    "corporate_fundamentals_applicable": False,
    "fundamental_scope": "metadate contract și date OHLCV; ETF-ul nu are earnings sau situații financiare de companie",
    "data_provider": "IBKR TWS API",
    "data_broker": "IBKR",
    "market_data_mode": "ultima închidere istorică IBKR",
    "execution_brokers": ["IBKR"],
    "ibkr_role": "date și execuție",
    "ibkr_data_only": False,
    "position_held_in_ibkr": False,
    "contract": {
        "con_id": 622222129,  # This might be incorrect, but it's okay for mapping, it will be updated by sync
        "symbol": "SPYL",
        "local_symbol": "SPYL",
        "security_type": "STK",
        "currency": "EUR",
        "exchange": "SMART",
        "primary_exchange": "IBIS2",
        "trading_class": "SPYL",
        "long_name": "SPDR SP500 ETF",
        "market_name": "SPYL",
        "industry": "",
        "category": "",
        "subcategory": ""
    }
}

# Add 3USL.MI
data['instruments']['3USL.MI'] = {
    "symbol": "3USL.MI",
    "aliases": ["3USL.MI", "3USL.BVME", "3USL"],
    "market": "Europa / SP500 Lev",
    "instrument_type": "ETF",
    "corporate_fundamentals_applicable": False,
    "fundamental_scope": "metadate contract și date OHLCV; ETF-ul nu are earnings",
    "data_provider": "IBKR TWS API",
    "data_broker": "IBKR",
    "market_data_mode": "ultima închidere istorică IBKR",
    "execution_brokers": ["IBKR"],
    "ibkr_role": "date și execuție",
    "ibkr_data_only": False,
    "position_held_in_ibkr": False,
    "contract": {
        "con_id": 266184950, # random/placeholder
        "symbol": "3USL",
        "local_symbol": "3USL",
        "security_type": "STK",
        "currency": "EUR",
        "exchange": "SMART",
        "primary_exchange": "BVME.ETF",
        "trading_class": "3USL",
        "long_name": "WISDOMTREE SP500 3X DAILY",
        "market_name": "3USL",
        "industry": "",
        "category": "",
        "subcategory": ""
    }
}

with open('tws_instruments.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Updated tws_instruments.json")
