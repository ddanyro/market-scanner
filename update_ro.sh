#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f "${SHADOW_R2_ENV_FILE:-.shadow_r2_env}" ]; then
    # shellcheck disable=SC1090
    source "${SHADOW_R2_ENV_FILE:-.shadow_r2_env}"
fi

if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -u market_scanner.py --mode ro
