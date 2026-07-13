#!/usr/bin/env python3
import sys
import json
import os
import subprocess
import traceback
import pandas as pd

DASHBOARD_STATE_PATH = '/Users/danieldragomir/antigravity/dashboard_state.json'
WATCHLIST_CSV_PATH = '/Users/danieldragomir/antigravity/watchlist.csv'
WATCHLIST_JSON_PATH = '/Users/danieldragomir/antigravity/watchlist.json'

def log(msg):
    """Log to stderr to avoid corrupting the stdio stdout channel."""
    sys.stderr.write(f"[Server] {msg}\n")
    sys.stderr.flush()

def load_state():
    if not os.path.exists(DASHBOARD_STATE_PATH):
        return {}
    try:
        with open(DASHBOARD_STATE_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        log(f"Error loading state: {e}")
        return {}

def send_response(id_val, result=None, error=None):
    res = {
        "jsonrpc": "2.0",
        "id": id_val
    }
    if error is not None:
        res["error"] = error
    else:
        res["result"] = result
        
    try:
        msg = json.dumps(res)
        sys.stdout.write(msg + "\n")
        sys.stdout.flush()
    except Exception as e:
        log(f"Error sending response: {e}")

def handle_initialize(req_id, params):
    log("Handling initialize request...")
    result = {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "market-scanner-mcp",
            "version": "1.0.0"
        }
    }
    send_response(req_id, result)

def handle_tools_list(req_id):
    log("Listing tools...")
    tools = [
        {
            "name": "get_market_indicators",
            "description": "Fetch current VIX, Economic Cycle, exchange rates, and market indices indicators.",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_watchlist_tickers",
            "description": "Get scanned watchlist stocks with optional filters.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Filter by ticker symbol (e.g. WFC)"},
                    "sector": {"type": "string", "description": "Filter by sector (e.g. Financial Services)"},
                    "consensus": {"type": "string", "description": "Filter by consensus rating (e.g. Buy, Strong Buy)"},
                    "decision": {"type": "string", "description": "Filter by trading decision (e.g. BUY, AVOID)"},
                    "trend": {"type": "string", "description": "Filter by trend status (e.g. Strong Bullish)"},
                    "strategy": {"type": "string", "description": "Filter by strategy (e.g. Breakout)"},
                    "min_analysts": {"type": "integer", "description": "Minimum analyst count"},
                    "min_rr": {"type": "number", "description": "Minimum Risk/Reward ratio"}
                }
            }
        },
        {
            "name": "get_portfolio",
            "description": "Get current portfolio positions, buy prices, Stops, and profit/loss details.",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "add_watchlist_symbol",
            "description": "Add a new stock symbol to the scanner watchlist.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "The stock symbol to add (e.g. AAPL)"}
                },
                "required": ["symbol"]
            }
        },
        {
            "name": "remove_watchlist_symbol",
            "description": "Remove a stock symbol from the watchlist.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "The stock symbol to remove (e.g. AAPL)"}
                },
                "required": ["symbol"]
            }
        },
        {
            "name": "run_scanner",
            "description": "Trigger the background portfolio/all scanner run.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["portfolio", "all"], "default": "portfolio", "description": "Scan mode"}
                }
            }
        }
    ]
    send_response(req_id, {"tools": tools})

def handle_tool_call(req_id, name, arguments):
    log(f"Calling tool: {name} with args: {arguments}")
    state = load_state()
    
    if name == "get_market_indicators":
        indicators = {
            "rates": state.get("rates", {}),
            "market_indicators": state.get("market_indicators", {}),
            "vix_val": state.get("vix_val"),
            "eco_phase": state.get("eco_phase"),
            "eco_next_phase": state.get("eco_next_phase")
        }
        text = json.dumps(indicators, indent=2)
        send_response(req_id, {"content": [{"type": "text", "text": text}]})
        
    elif name == "get_watchlist_tickers":
        items = state.get("watchlist", [])
        
        # Apply filters
        symbol_f = arguments.get("symbol")
        sector_f = arguments.get("sector")
        consensus_f = arguments.get("consensus")
        decision_f = arguments.get("decision")
        trend_f = arguments.get("trend")
        strategy_f = arguments.get("strategy")
        min_analysts = arguments.get("min_analysts")
        min_rr = arguments.get("min_rr")
        
        filtered = []
        for item in items:
            # Check symbol
            if symbol_f and symbol_f.upper() != item.get("Ticker", "").upper():
                continue
            # Check sector
            if sector_f and sector_f.upper() not in item.get("Sector", "").upper():
                continue
            # Check consensus
            if consensus_f and consensus_f.upper() not in item.get("Consensus", "").upper():
                continue
            # Check decision
            if decision_f and decision_f.upper() not in item.get("Decision", "").upper():
                continue
            # Check trend
            if trend_f and trend_f.upper() not in item.get("Trend", "").upper():
                continue
            # Check strategy
            if strategy_f and strategy_f.upper() not in item.get("Strategy", "").upper():
                continue
            # Check min analysts
            if min_analysts is not None:
                try:
                    if int(item.get("Analysts", 0)) < int(min_analysts):
                        continue
                except:
                    pass
            # Check min R:R
            if min_rr is not None:
                try:
                    if float(item.get("RR_Ratio", 0.0)) < float(min_rr):
                        continue
                except:
                    pass
                    
            # Simplify item representation by stripping large Sparklines
            item_copy = dict(item)
            if "Sparkline" in item_copy:
                del item_copy["Sparkline"]
            filtered.append(item_copy)
            
        text = json.dumps(filtered, indent=2)
        send_response(req_id, {"content": [{"type": "text", "text": text}]})
        
    elif name == "get_portfolio":
        portfolio_items = state.get("portfolio", [])
        # Strip sparklines for compactness
        clean_items = []
        for item in portfolio_items:
            item_copy = dict(item)
            if "Sparkline" in item_copy:
                del item_copy["Sparkline"]
            clean_items.append(item_copy)
            
        text = json.dumps(clean_items, indent=2)
        send_response(req_id, {"content": [{"type": "text", "text": text}]})
        
    elif name == "add_watchlist_symbol":
        symbol = arguments.get("symbol", "").upper().strip()
        if not symbol:
            send_response(req_id, error={"code": -32602, "message": "Symbol cannot be empty"})
            return
            
        try:
            if os.path.exists(WATCHLIST_CSV_PATH):
                df = pd.read_csv(WATCHLIST_CSV_PATH)
            else:
                df = pd.DataFrame(columns=['symbol'])
                
            existing = [s.upper() for s in df['symbol'].dropna().astype(str).tolist()]
            if symbol in existing:
                msg = f"Symbol {symbol} is already in the watchlist."
            else:
                new_row = pd.DataFrame({'symbol': [symbol]})
                df = pd.concat([df, new_row], ignore_index=True)
                df['symbol'] = df['symbol'].str.upper()
                df = df.drop_duplicates(subset=['symbol'], keep='first')
                df.to_csv(WATCHLIST_CSV_PATH, index=False)
                
                # Write to json as well
                records = df[['symbol']].to_dict(orient='records')
                with open(WATCHLIST_JSON_PATH, 'w') as f:
                    json.dump(records, f, indent=2)
                msg = f"Successfully added {symbol} to watchlist."
                
            send_response(req_id, {"content": [{"type": "text", "text": msg}]})
        except Exception as e:
            send_response(req_id, error={"code": -32603, "message": f"Error updating watchlist: {e}"})
            
    elif name == "remove_watchlist_symbol":
        symbol = arguments.get("symbol", "").upper().strip()
        if not symbol:
            send_response(req_id, error={"code": -32602, "message": "Symbol cannot be empty"})
            return
            
        try:
            if not os.path.exists(WATCHLIST_CSV_PATH):
                send_response(req_id, error={"code": -32603, "message": "Watchlist file not found"})
                return
                
            df = pd.read_csv(WATCHLIST_CSV_PATH)
            df['symbol'] = df['symbol'].str.upper()
            original_len = len(df)
            df = df[df['symbol'] != symbol]
            
            if len(df) == original_len:
                msg = f"Symbol {symbol} was not found in the watchlist."
            else:
                df.to_csv(WATCHLIST_CSV_PATH, index=False)
                # Write to json
                records = df[['symbol']].to_dict(orient='records')
                with open(WATCHLIST_JSON_PATH, 'w') as f:
                    json.dump(records, f, indent=2)
                msg = f"Successfully removed {symbol} from watchlist."
                
            send_response(req_id, {"content": [{"type": "text", "text": msg}]})
        except Exception as e:
            send_response(req_id, error={"code": -32603, "message": f"Error updating watchlist: {e}"})
            
    elif name == "run_scanner":
        mode = arguments.get("mode", "portfolio")
        script = "./update_portfolio.sh" if mode == "portfolio" else "./update_all.sh"
        try:
            log(f"Launching {script} in background...")
            subprocess.Popen([script], shell=True, start_new_session=True)
            msg = f"Successfully launched {mode} scanner run in the background."
            send_response(req_id, {"content": [{"type": "text", "text": msg}]})
        except Exception as e:
            send_response(req_id, error={"code": -32603, "message": f"Error launching scanner: {e}"})
            
    else:
        send_response(req_id, error={"code": -32601, "message": f"Unknown tool: {name}"})

def main():
    log("Market Scanner MCP Server initialized.")
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            req = json.loads(line)
            method = req.get("method")
            req_id = req.get("id")
            
            if method == "initialize":
                handle_initialize(req_id, req.get("params", {}))
            elif method == "notifications/initialized":
                log("Initialized notification received.")
            elif method == "tools/list":
                handle_tools_list(req_id)
            elif method == "tools/call":
                params = req.get("params", {})
                handle_tool_call(req_id, params.get("name"), params.get("arguments", {}))
            else:
                if req_id is not None:
                    send_response(req_id, error={"code": -32601, "message": f"Method not found: {method}"})
        except Exception as e:
            log(f"Exception in main loop: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()
