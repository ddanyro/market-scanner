#!/usr/bin/env python3
"""
Script to sync watchlist from remote GitHub Pages dashboard.
Fetches symbols from https://betty333ro.github.io/market-scanner/ and adds missing ones to local watchlist.csv
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re


def fetch_remote_watchlist(url="https://betty333ro.github.io/market-scanner/"):
    """Fetch watchlist symbols from remote dashboard."""
    print(f"📡 Fetching watchlist from {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all Finviz links
        finviz_links = soup.find_all('a', href=re.compile(r'finviz\.com/quote\.ashx\?t='))
        
        if not finviz_links:
            print("❌ Could not find any Finviz links on remote page")
            return []
        
        symbols = []
        for link in finviz_links:
            # Extract symbol from link text
            symbol = link.get_text(strip=True)
            if symbol and symbol not in symbols:
                symbols.append(symbol.upper())
        
        print(f"✅ Found {len(symbols)} symbols in remote watchlist")
        return symbols
        
    except Exception as e:
        print(f"❌ Error fetching remote watchlist: {e}")
        return []


def load_local_watchlist(filepath='watchlist.csv'):
    """Load local watchlist symbols."""
    if not os.path.exists(filepath):
        print(f"⚠️  Local watchlist file not found: {filepath}")
        return set()
    
    try:
        df = pd.read_csv(filepath)
        if 'symbol' in df.columns:
            symbols = set(df['symbol'].str.upper())
            print(f"📋 Local watchlist has {len(symbols)} symbols")
            return symbols
        else:
            print("⚠️  'symbol' column not found in watchlist.csv")
            return set()
    except Exception as e:
        print(f"❌ Error loading local watchlist: {e}")
        return set()


def add_symbols_to_watchlist(new_symbols, filepath='watchlist.csv'):
    """Add new symbols to local watchlist.csv."""
    if not new_symbols:
        print("✅ No new symbols to add")
        return
    
    print(f"\n📝 Adding {len(new_symbols)} new symbols to watchlist...")
    
    try:
        # Load existing watchlist or create new DataFrame
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
        else:
            df = pd.DataFrame(columns=['symbol'])
        
        # Add new symbols
        new_rows = [{'symbol': symbol} for symbol in new_symbols]
        df_new = pd.DataFrame(new_rows)
        df = pd.concat([df, df_new], ignore_index=True)
        
        # Remove duplicates (case-insensitive)
        df['symbol'] = df['symbol'].str.upper()
        original_count = len(df)
        df = df.drop_duplicates(subset=['symbol'], keep='first')
        duplicates_removed = original_count - len(df)
        
        # Save
        df.to_csv(filepath, index=False)
        print(f"✅ Successfully added {len(new_symbols)} symbols to {filepath}")
        
        if duplicates_removed > 0:
            print(f"🧹 Removed {duplicates_removed} duplicate(s)")
        
        for symbol in sorted(new_symbols):
            print(f"  + {symbol}")
            
    except Exception as e:
        print(f"❌ Error adding symbols to watchlist: {e}")


def main():
    """Main sync function."""
    print("=" * 60)
    print("🔄 Watchlist Sync Tool")
    print("=" * 60)
    
    # Fetch remote symbols
    remote_symbols = fetch_remote_watchlist()
    
    if not remote_symbols:
        print("\n❌ No symbols fetched from remote. Exiting.")
        return
    
    # Load local symbols
    local_symbols = load_local_watchlist()
    
    # Find missing symbols
    remote_set = set(s.upper() for s in remote_symbols)
    missing_symbols = remote_set - local_symbols
    
    if missing_symbols:
        print(f"\n🆕 Found {len(missing_symbols)} new symbols:")
        for symbol in sorted(missing_symbols):
            print(f"  • {symbol}")
        
        # Add to local watchlist automatically
        add_symbols_to_watchlist(missing_symbols)
    else:
        print("\n✅ Local watchlist is up to date!")
    
    print("\n" + "=" * 60)
    print("✨ Sync complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
