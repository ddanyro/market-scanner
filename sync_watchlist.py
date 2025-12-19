#!/usr/bin/env python3
"""
Script to sync watchlist from remote GitHub Pages dashboard.
Since the remote dashboard uses encrypted data, this version accepts manual input.

Usage:
    python3 sync_watchlist.py
    
Then paste symbols from https://betty333ro.github.io/market-scanner/ (one per line)
"""

import pandas as pd
import os


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
        
        # Save
        df.to_csv(filepath, index=False)
        print(f"✅ Successfully added {len(new_symbols)} symbols to {filepath}")
        
        for symbol in sorted(new_symbols):
            print(f"  + {symbol}")
            
    except Exception as e:
        print(f"❌ Error adding symbols to watchlist: {e}")


def main():
    """Main sync function."""
    print("=" * 60)
    print("🔄 Watchlist Sync Tool")
    print("=" * 60)
    print("\n📋 Manual Input Mode")
    print("=" * 60)
    print("\nPlease visit: https://betty333ro.github.io/market-scanner/")
    print("\nSteps:")
    print("1. Open the Watchlist tab")
    print("2. Copy all symbols (one per line)")
    print("3. Paste them below")
    print("\nEnter symbols (one per line, press Ctrl+D or enter empty line twice to finish):")
    print("-" * 60)
    
    remote_symbols = []
    empty_count = 0
    
    try:
        while True:
            try:
                line = input().strip()
            except EOFError:
                break
                
            if not line:
                empty_count += 1
                if empty_count >= 2:
                    break
                continue
            empty_count = 0
            
            # Extract just the symbol (first word, uppercase)
            symbol = line.split()[0].upper()
            if symbol and symbol not in remote_symbols:
                remote_symbols.append(symbol)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return
    
    if not remote_symbols:
        print("\n❌ No symbols entered. Exiting.")
        return
    
    print(f"\n✅ Received {len(remote_symbols)} symbols")
    
    # Load local symbols
    local_symbols = load_local_watchlist()
    
    # Find missing symbols
    remote_set = set(remote_symbols)
    missing_symbols = remote_set - local_symbols
    
    if missing_symbols:
        print(f"\n🆕 Found {len(missing_symbols)} new symbols:")
        for symbol in sorted(missing_symbols):
            print(f"  • {symbol}")
        
        # Confirm before adding
        try:
            confirm = input("\nAdd these symbols to watchlist? (y/n): ").strip().lower()
            if confirm == 'y':
                add_symbols_to_watchlist(missing_symbols)
            else:
                print("❌ Cancelled")
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Cancelled")
    else:
        print("\n✅ Local watchlist is up to date!")
    
    print("\n" + "=" * 60)
    print("✨ Sync complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
