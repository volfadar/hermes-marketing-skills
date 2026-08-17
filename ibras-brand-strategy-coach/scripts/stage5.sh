#!/usr/bin/env bash
# stage5.sh — Funnel Design (final stage)
set -euo pipefail
USER="${USER_NAME:-peserta}"
[[ "${1:-}" == "--user" ]] && USER="$2"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE=$(cat "$SCRIPT_DIR/templates/stage5-funnel.txt")
PROMPT="${TEMPLATE//<USER>/$USER}"
echo "=== Stage 5: Funnel Design ==="
echo ""
echo "$PROMPT"
