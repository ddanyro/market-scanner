#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
source "./update_git_sync.sh"

if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi

git_sync_start "update_all.sh"
load_shadow_r2_config
load_order_cache_password

sync_log_step "Actualizare completă"
"$PYTHON_BIN" -u market_scanner.py --mode all --tws

sync_log_step "Evaluare forward shadow"
if ! "$PYTHON_BIN" -u evaluate_shadow_forward.py; then
    echo "Avertisment: evaluarea outcome-urilor nu a reușit; snapshotul rămâne valid." >&2
fi

sync_log_step "Validare forward Technical Events"
if ! "$PYTHON_BIN" -u evaluate_technical_events_forward.py; then
    echo "Avertisment: validarea Technical Events nu a reușit; ledgerul immutable rămâne valid." >&2
fi

git_sync_finish "Update complete snapshot"
