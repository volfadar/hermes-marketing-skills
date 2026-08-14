#!/usr/bin/env bash
# stage2.sh — Background Interview (after Stage 1 confirmed).
# Usage: bash stage2.sh [--user <name>]
set -euo pipefail
USER="${USER_NAME:-peserta}"
[[ "${1:-}" == "--user" ]] && USER="$2"

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE=$(cat "$SCRIPT_DIR/templates/stage2-background.txt")
PROMPT="${TEMPLATE//<USER>/$USER}"

echo "=== Stage 2: Background Interview ==="
echo ""
echo "Paste ke Hermes:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PROMPT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
