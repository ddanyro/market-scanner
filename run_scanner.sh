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

# Push doar fișierele de date (nu dashboard-ul)
git pull --rebase origin main >> dashboard.log 2>&1

git add portfolio.csv tws_orders.csv tws_positions.csv ib_stats.json 2>/dev/null
git commit -m "Auto-sync TWS data $(date '+%Y-%m-%d %H:%M')" >> dashboard.log 2>&1

git push origin main >> dashboard.log 2>&1

echo "=== Sincronizare completă ===" >> dashboard.log
