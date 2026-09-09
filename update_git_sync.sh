#!/bin/bash
# Shared Git synchronization for local scanner update scripts. Source this file.

SYNC_REMOTE_NAME="${SYNC_REMOTE_NAME:-origin}"
SYNC_BRANCH_NAME="${SYNC_BRANCH_NAME:-main}"

SYNC_GENERATED_FILES=(
    "analysis/technical_events_validation/coverage.csv"
    "analysis/technical_events_validation/direction_analysis.csv"
    "analysis/technical_events_validation/event_observations.csv"
    "analysis/technical_events_validation/event_types.csv"
    "analysis/technical_events_validation/integrity_report.json"
    "analysis/technical_events_validation/labelled_predictions.csv"
    "analysis/technical_events_validation/market_regimes.csv"
    "analysis/technical_events_validation/predictive_power.csv"
    "analysis/technical_events_validation/recency_analysis.csv"
    "analysis/technical_events_validation/score_buckets.csv"
    "analysis/technical_events_validation/score_comparison.csv"
    "analysis/technical_events_validation/support_resistance_events.csv"
    "analysis/technical_events_validation/technical_events_validation_report.md"
    "analysis/technical_events_validation/timeframe_agreement.csv"
    "analysis/shadow_forward_validation/collection_coverage.json"
    "analysis/shadow_forward_validation/component_analysis.csv"
    "analysis/shadow_forward_validation/coverage.csv"
    "analysis/shadow_forward_validation/decision_disagreements.csv"
    "analysis/shadow_forward_validation/decision_matrix.csv"
    "analysis/shadow_forward_validation/forward_validation_report.md"
    "analysis/shadow_forward_validation/labelled_predictions.csv"
    "analysis/shadow_forward_validation/integrity_report.json"
    "analysis/shadow_forward_validation/market_regimes_forward.csv"
    "analysis/shadow_forward_validation/model_performance.csv"
    "analysis/shadow_forward_validation/options_control.csv"
    "analysis/shadow_forward_validation/performance.csv"
    "analysis/shadow_forward_validation/portfolio_fit_analysis.csv"
    "analysis/shadow_forward_validation/readiness_report.md"
    "analysis/shadow_forward_validation/risk_metrics.csv"
    "analysis/shadow_forward_validation/score_buckets_forward.csv"
    "bvb_daily_cache.csv"
    "dashboard_state.json"
    "historical_returns.json"
    "index.html"
    "market_history.json"
    "market_indicators.json"
    "market_tide_cache.json"
    "portfolio.csv"
    "portfolio.json"
    "push/firebase/firebase-messaging-sw.js"
    "scan_results.csv"
    "scan_results_enhanced.csv"
    "shadow_predictions.jsonl"
    "technical_events_predictions.jsonl"
    "technical_events_state.json"
    "sp500_tickers.json"
    "tradeville_account.enc.json"
    "tradeville_orders.csv"
    "tradeville_portfolio.csv"
    "tws_account.enc.json"
    "tws_account_risk.json"
    "tws_instruments.json"
    "watchlist.csv"
    "watchlist.json"
    "watchlist_a_d.json"
    "watchlist_buy.json"
    "watchlist_compact.json"
    "watchlist_e_h.json"
    "watchlist_i_l.json"
    "watchlist_m_p.json"
    "watchlist_q_t.json"
    "watchlist_u_z.json"
)

sync_log_step() {
    printf '\n=== %s ===\n' "$1"
}

sync_python_bin() {
    if [ -n "${PYTHON_BIN:-}" ]; then
        printf '%s\n' "$PYTHON_BIN"
    elif [ -x ".venv/bin/python" ]; then
        printf '%s\n' ".venv/bin/python"
    else
        printf '%s\n' "python3"
    fi
}

git_sync_assert_ready() {
    local caller_name="${1:-update script}"
    if ! command -v git >/dev/null 2>&1; then
        echo "Eroare: git nu este disponibil în PATH." >&2
        return 1
    fi
    local current_branch
    current_branch="$(git symbolic-ref --quiet --short HEAD || true)"
    if [ "$current_branch" != "$SYNC_BRANCH_NAME" ]; then
        echo "Eroare: $caller_name trebuie rulat pe $SYNC_BRANCH_NAME; ramura curentă este ${current_branch:-detached HEAD}." >&2
        return 1
    fi
    if [ -d "$(git rev-parse --git-path rebase-merge)" ] || \
       [ -d "$(git rev-parse --git-path rebase-apply)" ]; then
        echo "Eroare: există deja un rebase în desfășurare." >&2
        return 1
    fi
}

git_sync_start() {
    local caller_name="${1:-update script}"
    git_sync_assert_ready "$caller_name"
    sync_log_step "Sincronizare inițială cu GitHub"
    git pull --rebase --autostash "$SYNC_REMOTE_NAME" "$SYNC_BRANCH_NAME"
}

git_sync_stage_generated() {
    local files_to_add=()
    local generated_file
    for generated_file in "${SYNC_GENERATED_FILES[@]}"; do
        if [ -e "$generated_file" ]; then
            files_to_add+=("$generated_file")
        fi
    done
    if [ "${#files_to_add[@]}" -gt 0 ]; then
        git add -- "${files_to_add[@]}"
    fi
}

git_sync_merge_remote_ledger() {
    local remote_ledger
    remote_ledger="$(mktemp "${TMPDIR:-/tmp}/market-scanner-ledger.XXXXXX")"
    if git show "$SYNC_REMOTE_NAME/$SYNC_BRANCH_NAME:shadow_predictions.jsonl" \
        > "$remote_ledger" 2>/dev/null; then
        "$(sync_python_bin)" merge_shadow_ledgers.py \
            shadow_predictions.jsonl "$remote_ledger" \
            --output shadow_predictions.jsonl
    fi
    rm -f -- "$remote_ledger"
}

git_sync_merge_remote_technical_ledger() {
    local remote_ledger
    remote_ledger="$(mktemp "${TMPDIR:-/tmp}/market-scanner-technical-ledger.XXXXXX")"
    if git show "$SYNC_REMOTE_NAME/$SYNC_BRANCH_NAME:technical_events_predictions.jsonl" \
        > "$remote_ledger" 2>/dev/null; then
        "$(sync_python_bin)" merge_shadow_ledgers.py \
            technical_events_predictions.jsonl "$remote_ledger" \
            --kind technical --output technical_events_predictions.jsonl
    fi
    rm -f -- "$remote_ledger"
}

git_sync_refresh_shadow_reports() {
    local python_bin
    python_bin="$(sync_python_bin)"
    "$python_bin" -c \
        'import shadow_validation; shadow_validation.generate_readiness_report()'
    "$python_bin" evaluate_shadow_forward.py --offline
    "$python_bin" evaluate_technical_events_forward.py --offline
}

git_sync_integrate_remote() {
    git fetch "$SYNC_REMOTE_NAME" "$SYNC_BRANCH_NAME"
    if ! git merge-base --is-ancestor \
        "$SYNC_REMOTE_NAME/$SYNC_BRANCH_NAME" HEAD; then
        git rebase --autostash -X theirs "$SYNC_REMOTE_NAME/$SYNC_BRANCH_NAME"
    fi

    local ledger_before
    ledger_before="$(git hash-object shadow_predictions.jsonl 2>/dev/null || true)"
    local technical_ledger_before
    technical_ledger_before="$(git hash-object technical_events_predictions.jsonl 2>/dev/null || true)"
    git_sync_merge_remote_ledger
    git_sync_merge_remote_technical_ledger
    local ledger_after
    ledger_after="$(git hash-object shadow_predictions.jsonl 2>/dev/null || true)"
    local technical_ledger_after
    technical_ledger_after="$(git hash-object technical_events_predictions.jsonl 2>/dev/null || true)"
    if [ "$ledger_before" != "$ledger_after" ] || \
       [ "$technical_ledger_before" != "$technical_ledger_after" ]; then
        git_sync_refresh_shadow_reports
        git_sync_stage_generated
        git commit --amend --no-edit
    fi
}

git_sync_finish() {
    local commit_prefix="$1"
    sync_log_step "Pregătire și sincronizare finală"
    git_sync_stage_generated
    if git diff --cached --quiet; then
        echo "Nu există fișiere generate modificate pentru commit."
        return 0
    fi

    git commit -m "$commit_prefix $(date '+%Y-%m-%d %H:%M:%S')"

    local attempt
    for attempt in 1 2 3; do
        git_sync_integrate_remote
        if git push "$SYNC_REMOTE_NAME" "HEAD:$SYNC_BRANCH_NAME"; then
            echo "Sincronizare Git finalizată la încercarea $attempt."
            return 0
        fi
        echo "Remote-ul a avansat în timpul push-ului; reîncerc ($attempt/3)." >&2
    done
    echo "Eroare: push-ul nu a reușit după 3 încercări." >&2
    return 1
}
