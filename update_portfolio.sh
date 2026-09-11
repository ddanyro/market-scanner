#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
source "./update_git_sync.sh"

WORKFLOW_FILE="update_dashboard.yml"

log_step() {
    printf '\n=== %s ===\n' "$1"
}

if ! command -v gh >/dev/null 2>&1; then
    echo "Eroare: GitHub CLI (gh) nu este instalat sau nu este disponibil în PATH." >&2
    exit 1
fi

git_sync_start "update_portfolio.sh"

# Snapshotul ordinelor trebuie criptat local cu același PIN pe care GitHub
# Actions îl primește prin secretul PORTFOLIO_PASSWORD. Altfel rularea remote
# nu poate recupera ordinele IBKR și ar publica tabele incomplete.
load_order_cache_password

if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi

log_step "Actualizare portofoliu"
"$PYTHON_BIN" -u market_scanner.py --mode portfolio --tws

log_step "Evaluare forward shadow"
if ! "$PYTHON_BIN" -u evaluate_shadow_forward.py; then
    echo "Avertisment: evaluarea outcome-urilor nu a reușit; predicțiile contemporane au fost păstrate." >&2
fi

log_step "Validare forward Technical Events"
if ! "$PYTHON_BIN" -u evaluate_technical_events_forward.py; then
    echo "Avertisment: validarea Technical Events nu a reușit; ledgerul immutable a fost păstrat." >&2
fi

git_sync_finish "Update portfolio snapshot"

log_step "Pornire GitHub Actions"
gh workflow run "$WORKFLOW_FILE" -f update_mode=portfolio

LATEST_RUN_URL="$(
    gh run list \
        --workflow "$WORKFLOW_FILE" \
        --limit 1 \
        --json url \
        --jq '.[0].url' 2>/dev/null || true
)"

if [ -n "$LATEST_RUN_URL" ]; then
    echo "Workflow pornit: $LATEST_RUN_URL"
else
    echo "Workflowul GitHub Actions a fost pornit."
fi
