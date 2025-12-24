#!/bin/bash
# ===========================================
# LOCAL CRON: Sincronizare TWS + Push Date
# Rulează orar pentru a prelua date live din TWS
# GitHub Actions va genera dashboard-ul ulterior
# NU rulează dacă TWS nu e deschis
# ===========================================

cd /Users/danieldragomir/antigravity

# Verifică dacă TWS e deschis (verifică portul 7497)
if ! nc -z 127.0.0.1 7497 2>/dev/null; then
    echo "=== $(date '+%Y-%m-%d %H:%M:%S') - TWS nu e deschis. Skip. ===" >> dashboard.log
    exit 0
fi

echo "=== $(date '+%Y-%m-%d %H:%M:%S') - Sincronizare TWS ===" >> dashboard.log

# Sincronizare TWS (ordine active + poziții) + Merge în portfolio.csv
/usr/bin/python3 -c "
import sys
import os
import pandas as pd

sys.path.insert(0, '.')

try:
    import ib_tws_sync
    ib_tws_sync.fetch_active_orders()
except Exception as e:
    print(f'TWS Sync Error: {e}')
    exit(1)

# Merge TWS Orders -> portfolio.csv (Trail_Pct, Trail_Stop)
if os.path.exists('tws_orders.csv') and os.path.exists('portfolio.csv'):
    print('Merging TWS Orders into portfolio.csv...')
    p_df = pd.read_csv('portfolio.csv')
    t_df = pd.read_csv('tws_orders.csv')
    
    changed = False
    for _, row in t_df.iterrows():
        sym = str(row.get('Symbol', ''))
        stop = float(row.get('Calculated_Stop', 0))
        pct = float(row.get('Trail_Pct', 0))
        
        mask = p_df['Symbol'] == sym
        if mask.any():
            if stop > 0:
                p_df.loc[mask, 'Trail_Stop'] = stop
                changed = True
            if pct > 0:
                p_df.loc[mask, 'Trail_Pct'] = pct
                changed = True
    
    if changed:
        p_df.to_csv('portfolio.csv', index=False)
        print('  -> portfolio.csv actualizat cu Trail_Pct/Trail_Stop din TWS.')
    else:
        print('  -> Nicio modificare necesară.')
" >> dashboard.log 2>&1

# Resetează fișierele de dashboard la versiunea din remote (evită conflicte)
git checkout origin/main -- dashboard_state.json index.html market_history.json 2>/dev/null || true

# Pull ultimele modificări
git pull origin main >> dashboard.log 2>&1 || true

# Adaugă fișierele TWS + portfolio actualizat
git add tws_orders.csv tws_positions.csv portfolio.csv 2>/dev/null

# Commit doar dacă sunt modificări
if ! git diff --cached --quiet; then
    git commit -m "Auto-sync TWS data $(date '+%Y-%m-%d %H:%M')" >> dashboard.log 2>&1
    git push origin main >> dashboard.log 2>&1
    echo "  -> Date sincronizate cu succes." >> dashboard.log
else
    echo "  -> Nicio modificare în date." >> dashboard.log
fi

echo "=== Sincronizare completă ===" >> dashboard.log
