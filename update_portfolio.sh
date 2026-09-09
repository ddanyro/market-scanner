#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
source "./update_git_sync.sh"

WORKFLOW_FILE="update_dashboard.yml"
ORDER_CACHE_PASSWORD_FILE="${PORTFOLIO_ORDER_CACHE_PASSWORD_FILE:-.portfolio_order_cache_password}"

log_step() {
    printf '\n=== %s ===\n' "$1"
}

load_order_cache_password() {
    if [ -n "${PORTFOLIO_ORDER_CACHE_PASSWORD:-}" ]; then
        export PORTFOLIO_ORDER_CACHE_PASSWORD
        return
    fi

    if [ -f "$ORDER_CACHE_PASSWORD_FILE" ]; then
        IFS= read -r PORTFOLIO_ORDER_CACHE_PASSWORD < "$ORDER_CACHE_PASSWORD_FILE"
        if [ -n "$PORTFOLIO_ORDER_CACHE_PASSWORD" ]; then
            export PORTFOLIO_ORDER_CACHE_PASSWORD
            return
        fi
    fi

    if [ ! -t 0 ]; then
        echo "Eroare: lipsește cheia comună pentru snapshotul ordinelor IBKR." >&2
        echo "Rulează scriptul o dată într-un terminal interactiv pentru configurare." >&2
        exit 1
    fi

    printf 'PIN-ul portofoliului remote (va fi salvat local, în afara Git): ' >&2
    IFS= read -r -s PORTFOLIO_ORDER_CACHE_PASSWORD
    printf '\n' >&2
    if [ -z "$PORTFOLIO_ORDER_CACHE_PASSWORD" ]; then
        echo "Eroare: PIN-ul remote nu poate fi gol." >&2
        exit 1
    fi

    umask 077
    printf '%s\n' "$PORTFOLIO_ORDER_CACHE_PASSWORD" > "$ORDER_CACHE_PASSWORD_FILE"
    chmod 600 "$ORDER_CACHE_PASSWORD_FILE"
    export PORTFOLIO_ORDER_CACHE_PASSWORD
    echo "Cheia snapshotului a fost salvată local în $ORDER_CACHE_PASSWORD_FILE (ignorat de Git)."
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
