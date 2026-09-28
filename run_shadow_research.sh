#!/bin/bash
# Standalone research only: no Git sync, dashboard rebuild or publication.
set -euo pipefail
cd "$(dirname "$0")"
source "./update_git_sync.sh"
load_shadow_r2_config
if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi
exec "$PYTHON_BIN" -u run_shadow_maintenance.py "$@"
