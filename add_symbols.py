import pandas as pd
import os

new_symbols = [
    "TEM", "ABSI", "CRDO", "POET", "GPCR", "ALT", "ATI", "IOSP", "GPS", "HBI", "LEVI", "BTDR"
]

# Remove internal duplicates while preserving order for logging
unique_new_symbols = []
for s in new_symbols:
    if s not in unique_new_symbols:
        unique_new_symbols.append(s)

# Update watchlist.txt
txt_file = 'watchlist.txt'
if os.path.exists(txt_file):
    with open(txt_file, 'r') as f:
        existing_txt = [line.strip().upper() for line in f if line.strip()]
    
    missing_txt = [s for s in unique_new_symbols if s not in existing_txt]
    if missing_txt:
        with open(txt_file, 'a') as f:
            for s in missing_txt:
                f.write(f"{s}\n")
        print(f"Added to watchlist.txt ({len(missing_txt)} symbols): {missing_txt}")
    else:
        print("All symbols already in watchlist.txt")

# Update watchlist.csv
csv_file = 'watchlist.csv'
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    if 'symbol' in df.columns:
        existing_csv = df['symbol'].str.upper().tolist()
        missing_csv = [s for s in unique_new_symbols if s not in existing_csv]
        
        if missing_csv:
            new_rows = pd.DataFrame({'symbol': missing_csv})
            df = pd.concat([df, new_rows], ignore_index=True)
            df.to_csv(csv_file, index=False)
            print(f"Added to watchlist.csv ({len(missing_csv)} symbols): {missing_csv}")
        else:
            print("All symbols already in watchlist.csv")
    else:
        print("No 'symbol' column in watchlist.csv")
