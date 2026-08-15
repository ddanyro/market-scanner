#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

REMOTE_NAME="origin"
BRANCH_NAME="main"
WORKFLOW_FILE="update_dashboard.yml"

GENERATED_FILES=(
    "bvb_daily_cache.csv"
    "dashboard_state.json"
    "index.html"
    "portfolio.csv"
    "portfolio.json"
    "tws_account.enc.json"
    "tws_account_risk.json"
)

log_step() {
    printf '\n=== %s ===\n' "$1"
}

if ! command -v git >/dev/null 2>&1; then
    echo "Eroare: git nu este instalat sau nu este disponibil în PATH." >&2
    exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
    echo "Eroare: GitHub CLI (gh) nu este instalat sau nu este disponibil în PATH." >&2
    exit 1
fi

CURRENT_BRANCH="$(git symbolic-ref --quiet --short HEAD || true)"
if [ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]; then
    echo "Eroare: scriptul trebuie rulat pe ramura $BRANCH_NAME; ramura curentă este ${CURRENT_BRANCH:-detached HEAD}." >&2
    exit 1
fi

if [ -d "$(git rev-parse --git-path rebase-merge)" ] || [ -d "$(git rev-parse --git-path rebase-apply)" ]; then
    echo "Eroare: există deja un rebase în desfășurare. Rezolvă-l înainte de update_portfolio.sh." >&2
    exit 1
fi

log_step "Sincronizare inițială cu GitHub"
git pull --rebase --autostash "$REMOTE_NAME" "$BRANCH_NAME"

if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi

log_step "Actualizare portofoliu"
"$PYTHON_BIN" -u market_scanner.py --mode portfolio --tws

log_step "Pregătire fișiere generate"
FILES_TO_ADD=()
for generated_file in "${GENERATED_FILES[@]}"; do
    if [ -e "$generated_file" ]; then
        FILES_TO_ADD+=("$generated_file")
    fi
done

if [ "${#FILES_TO_ADD[@]}" -gt 0 ]; then
    git add -- "${FILES_TO_ADD[@]}"
fi

if git diff --cached --quiet; then
    echo "Nu există fișiere generate modificate pentru commit."
else
    COMMIT_TIME="$(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "Update portfolio snapshot ${COMMIT_TIME}"

    # O actualizare automată poate ajunge pe main cât timp rulează scannerul.
    # Rebase-ul păstrează commitul local mai nou pentru fișierele generate.
    git pull --rebase -X theirs "$REMOTE_NAME" "$BRANCH_NAME"
    git push "$REMOTE_NAME" "$BRANCH_NAME"
fi

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
