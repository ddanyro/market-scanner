#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

if [ "$(uname -s)" != "Darwin" ] || ! command -v security >/dev/null 2>&1; then
    echo "Eroare: acest configurator necesită macOS Keychain." >&2
    exit 1
fi

KEYCHAIN_ACCOUNT="market-scanner"

read -r -s -p "Cloudflare Account ID: " R2_ACCOUNT_ID
printf '\n'
read -r -s -p "R2 Access Key ID: " R2_ACCESS_KEY_ID
printf '\n'
read -r -s -p "R2 Secret Access Key: " R2_SECRET_ACCESS_KEY
printf '\n'

if [ -z "$R2_ACCOUNT_ID" ] || [ -z "$R2_ACCESS_KEY_ID" ] || [ -z "$R2_SECRET_ACCESS_KEY" ]; then
    echo "Eroare: toate cele trei valori sunt obligatorii." >&2
    exit 1
fi

security add-generic-password -U -a "$KEYCHAIN_ACCOUNT" \
    -s market-scanner-cloudflare-account-id -w "$R2_ACCOUNT_ID" >/dev/null
security add-generic-password -U -a "$KEYCHAIN_ACCOUNT" \
    -s market-scanner-shadow-r2-access-key-id -w "$R2_ACCESS_KEY_ID" >/dev/null
security add-generic-password -U -a "$KEYCHAIN_ACCOUNT" \
    -s market-scanner-shadow-r2-secret-access-key -w "$R2_SECRET_ACCESS_KEY" >/dev/null

unset R2_ACCOUNT_ID R2_ACCESS_KEY_ID R2_SECRET_ACCESS_KEY

source ./update_git_sync.sh
load_shadow_r2_config

if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi

"$PYTHON_BIN" shadow_parquet_store.py probe
echo "R2 local este configurat și verificat prin macOS Keychain."
