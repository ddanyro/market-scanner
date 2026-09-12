#!/bin/bash
# Shared Git synchronization for local scanner update scripts. Source this file.

SYNC_REMOTE_NAME="${SYNC_REMOTE_NAME:-origin}"
SYNC_BRANCH_NAME="${SYNC_BRANCH_NAME:-main}"
ORDER_CACHE_PASSWORD_FILE="${PORTFOLIO_ORDER_CACHE_PASSWORD_FILE:-.portfolio_order_cache_password}"

SYNC_GENERATED_FILES=(
    "analysis/technical_events_validation/coverage.csv"
    "analysis/technical_events_validation/direction_analysis.csv"
    "analysis/technical_events_validation/event_observations.csv.gz"
    "analysis/technical_events_validation/event_types.csv"
    "analysis/technical_events_validation/integrity_report.json"
    "analysis/technical_events_validation/labelled_predictions.csv.gz"
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
    "technical_events_predictions.jsonl.gz"
    "technical_events_state.json.gz"
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
    "watchlist_details.json"
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
        return 1
    fi

    printf 'PIN-ul portofoliului remote (va fi salvat local, în afara Git): ' >&2
    IFS= read -r -s PORTFOLIO_ORDER_CACHE_PASSWORD
    printf '\n' >&2
    if [ -z "$PORTFOLIO_ORDER_CACHE_PASSWORD" ]; then
        echo "Eroare: PIN-ul remote nu poate fi gol." >&2
        return 1
    fi

    umask 077
    printf '%s\n' "$PORTFOLIO_ORDER_CACHE_PASSWORD" > "$ORDER_CACHE_PASSWORD_FILE"
    chmod 600 "$ORDER_CACHE_PASSWORD_FILE"
    export PORTFOLIO_ORDER_CACHE_PASSWORD
    echo "Cheia snapshotului a fost salvată local în $ORDER_CACHE_PASSWORD_FILE (ignorat de Git)."
}

load_shadow_r2_config() {
    local config_file="${SHADOW_R2_ENV_FILE:-.shadow_r2_env}"
    if [ -f "$config_file" ]; then
        # The file is local-only, chmod 600, and contains simple export lines.
        # shellcheck disable=SC1090
        source "$config_file"
    fi
    local keychain_account="market-scanner"
    if [ "$(uname -s)" = "Darwin" ] && command -v security >/dev/null 2>&1; then
        if [ -z "${SHADOW_R2_ACCOUNT_ID:-${CLOUDFLARE_ACCOUNT_ID:-}}" ]; then
            SHADOW_R2_ACCOUNT_ID="$(security find-generic-password -a "$keychain_account" -s market-scanner-cloudflare-account-id -w 2>/dev/null || true)"
        fi
        if [ -z "${SHADOW_R2_ACCESS_KEY_ID:-}" ]; then
            SHADOW_R2_ACCESS_KEY_ID="$(security find-generic-password -a "$keychain_account" -s market-scanner-shadow-r2-access-key-id -w 2>/dev/null || true)"
        fi
        if [ -z "${SHADOW_R2_SECRET_ACCESS_KEY:-}" ]; then
            SHADOW_R2_SECRET_ACCESS_KEY="$(security find-generic-password -a "$keychain_account" -s market-scanner-shadow-r2-secret-access-key -w 2>/dev/null || true)"
        fi
    fi
    export SHADOW_R2_ACCOUNT_ID="${SHADOW_R2_ACCOUNT_ID:-${CLOUDFLARE_ACCOUNT_ID:-}}"
    export SHADOW_R2_ACCESS_KEY_ID="${SHADOW_R2_ACCESS_KEY_ID:-}"
    export SHADOW_R2_SECRET_ACCESS_KEY="${SHADOW_R2_SECRET_ACCESS_KEY:-}"
    export SHADOW_R2_BUCKET="${SHADOW_R2_BUCKET:-market-scanner-shadow}"
    export SHADOW_R2_PREFIX="${SHADOW_R2_PREFIX:-market-scanner-shadow/v1}"
    export SHADOW_R2_REQUIRED="${SHADOW_R2_REQUIRED:-true}"
}

shadow_r2_is_configured() {
    [ -n "${SHADOW_R2_ACCOUNT_ID:-}" ] && \
    [ -n "${SHADOW_R2_ACCESS_KEY_ID:-}" ] && \
    [ -n "${SHADOW_R2_SECRET_ACCESS_KEY:-}" ] && \
    [ -n "${SHADOW_R2_BUCKET:-}" ]
}

shadow_r2_is_primary() {
    shadow_r2_is_configured && \
    case "${SHADOW_R2_REQUIRED:-false}" in
        1|true|TRUE|yes|YES|on|ON) return 0 ;;
        *) return 1 ;;
    esac
}

runtime_r2_pull() {
    if shadow_r2_is_configured; then
        echo "Verific starea runtime din Cloudflare R2..."
        "$(sync_python_bin)" runtime_r2_store.py pull
    else
        echo "Avertisment: R2 runtime nu este configurat; folosesc fișierele locale." >&2
    fi
}

runtime_r2_push() {
    if shadow_r2_is_configured; then
        "$(sync_python_bin)" runtime_r2_store.py push --publish-loader
    else
        echo "Avertisment: R2 runtime nu este configurat; păstrez fișierele locale." >&2
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
    # Keep the append-only Technical Events history, but rotate it into
    # immutable shards before Git sees a blob near GitHub's 50 MB warning.
    "$(sync_python_bin)" -c \
        'import technical_events_shadow; technical_events_shadow.rotate_ledger()'
    local files_to_add=()
    local generated_file
    for generated_file in "${SYNC_GENERATED_FILES[@]}"; do
        if shadow_r2_is_primary; then
            case "$generated_file" in
                shadow_predictions.jsonl|technical_events_predictions.jsonl.gz|dashboard_state.json|watchlist_compact.json|watchlist_details.json|analysis/technical_events_validation/labelled_predictions.csv.gz|analysis/technical_events_validation/event_observations.csv.gz)
                    continue
                    ;;
            esac
        fi
        if [ -e "$generated_file" ]; then
            files_to_add+=("$generated_file")
        fi
    done
    if ! shadow_r2_is_primary; then
        for generated_file in technical_events_predictions.archive-*.jsonl.gz; do
            if [ -e "$generated_file" ]; then
                files_to_add+=("$generated_file")
            fi
        done
    fi
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
    remote_ledger="$(mktemp "${TMPDIR:-/tmp}/market-scanner-technical-ledger.XXXXXX.gz")"
    if git show "$SYNC_REMOTE_NAME/$SYNC_BRANCH_NAME:technical_events_predictions.jsonl.gz" \
        > "$remote_ledger" 2>/dev/null; then
        "$(sync_python_bin)" merge_shadow_ledgers.py \
            technical_events_predictions.jsonl.gz "$remote_ledger" \
            --kind technical --output technical_events_predictions.jsonl.gz
    else
        rm -f -- "$remote_ledger"
        remote_ledger="$(mktemp "${TMPDIR:-/tmp}/market-scanner-technical-ledger.XXXXXX")"
        if git show "$SYNC_REMOTE_NAME/$SYNC_BRANCH_NAME:technical_events_predictions.jsonl" \
            > "$remote_ledger" 2>/dev/null; then
            "$(sync_python_bin)" merge_shadow_ledgers.py \
                technical_events_predictions.jsonl.gz "$remote_ledger" \
                --kind technical --output technical_events_predictions.jsonl.gz
        fi
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
    technical_ledger_before="$(git hash-object technical_events_predictions.jsonl.gz 2>/dev/null || true)"
    if ! shadow_r2_is_primary; then
        git_sync_merge_remote_ledger
        git_sync_merge_remote_technical_ledger
    fi
    local ledger_after
    ledger_after="$(git hash-object shadow_predictions.jsonl 2>/dev/null || true)"
    local technical_ledger_after
    technical_ledger_after="$(git hash-object technical_events_predictions.jsonl.gz 2>/dev/null || true)"
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
    runtime_r2_push
    if shadow_r2_is_configured; then
        "$(sync_python_bin)" shadow_parquet_store.py flush
    fi
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
