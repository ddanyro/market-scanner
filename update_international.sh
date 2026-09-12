#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
source "./update_git_sync.sh"

if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi

git_sync_start "update_international.sh"
load_shadow_r2_config
runtime_r2_pull
load_order_cache_password

sync_log_step "Actualizare internațională"
"$PYTHON_BIN" -u market_scanner.py --mode international

sync_log_step "Mentenanță periodică shadow"
if ! "$PYTHON_BIN" -u run_shadow_maintenance.py; then
    echo "Avertisment: mentenanța shadow nu a reușit; snapshoturile rămân valide." >&2
fi

git_sync_finish "Update international snapshot"
