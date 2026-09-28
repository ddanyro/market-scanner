#!/bin/bash
# Standalone research; synchronize completed online reports only.
set -euo pipefail
cd "$(dirname "$0")"
source "./update_git_sync.sh"
load_shadow_r2_config
if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi
git_sync_assert_ready run_shadow_research.sh
command -v gh >/dev/null || { echo "Eroare: gh este necesar pentru sincronizare." >&2; exit 1; }
SHADOW_RESEARCH_COMPLETION_FILE="$(mktemp)"
export SHADOW_RESEARCH_COMPLETION_FILE
trap 'rm -f -- "$SHADOW_RESEARCH_COMPLETION_FILE"' EXIT
"$PYTHON_BIN" -u run_shadow_maintenance.py "$@"
if [ -s "$SHADOW_RESEARCH_COMPLETION_FILE" ]; then
    git_sync_research_finish
else
    echo "Nu există cercetare online nouă finalizată; fără sincronizare."
fi
