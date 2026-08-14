#!/usr/bin/env bash
# stage4.sh — Tool Integration
set -euo pipefail
USER="${USER_NAME:-peserta}"
[[ "${1:-}" == "--user" ]] && USER="$2"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE=$(cat "$SCRIPT_DIR/templates/stage4-tools.txt")
PROMPT="${TEMPLATE//<USER>/$USER}"
echo "=== Stage 4: Tool Integration ==="
echo ""
echo "$PROMPT"
