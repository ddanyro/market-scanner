#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
source "./update_git_sync.sh"
load_shadow_r2_config

if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -u market_scanner.py --mode ro
