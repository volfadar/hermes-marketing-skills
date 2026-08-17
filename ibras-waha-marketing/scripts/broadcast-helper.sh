#!/usr/bin/env bash
# broadcast-helper.sh — wrapper for scripts/lib/broadcast.py that loads config and
# provides sane defaults. This is the SAFE broadcast entry point.
#
# Usage:
#   bash broadcast-helper.sh --contacts list.csv --templates msg.txt --dry-run
#   bash broadcast-helper.sh --contacts list.csv --templates msg.txt --i-confirm-optin --yes
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CFG_DIR="${WAHA_CONFIG_DIR:-$HOME/.waha-marketing}"
CFG="$CFG_DIR/config.env"

[[ -f "$CFG" ]] || { echo "Run scripts/initialize.sh first." >&2; exit 1; }
# shellcheck disable=SC1090
source "$CFG"

# Default account age if not specified
ACCT_AGE="${WAHA_ACCOUNT_AGE_DAYS:-30}"

exec python3 "${SCRIPT_DIR}/scripts/lib/broadcast.py" \
  --waha-url "$WAHA_URL" \
  --api-key "$WAHA_API_KEY" \
  --session "$WAHA_SESSION" \
  --account-age-days "$ACCT_AGE" \
  "$@"
