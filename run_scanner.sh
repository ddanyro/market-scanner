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

# Sincronizare TWS (ordine active + poziții)
/usr/bin/python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import ib_tws_sync
    ib_tws_sync.fetch_active_orders()
except Exception as e:
    print(f'TWS Sync Error: {e}')
" >> dashboard.log 2>&1

# Resetează fișierele de dashboard la versiunea din remote (evită conflicte)
git checkout origin/main -- dashboard_state.json index.html market_history.json 2>/dev/null || true

# Pull ultimele modificări
git pull origin main >> dashboard.log 2>&1 || true

# Adaugă DOAR fișierele TWS (nu dashboard-ul)
git add tws_orders.csv tws_positions.csv 2>/dev/null

# Commit doar dacă sunt modificări
if ! git diff --cached --quiet; then
    git commit -m "Auto-sync TWS data $(date '+%Y-%m-%d %H:%M')" >> dashboard.log 2>&1
    git push origin main >> dashboard.log 2>&1
    echo "  -> Date sincronizate cu succes." >> dashboard.log
else
    echo "  -> Nicio modificare în date." >> dashboard.log
fi

echo "=== Sincronizare completă ===" >> dashboard.log
