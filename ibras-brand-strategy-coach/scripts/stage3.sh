#!/usr/bin/env bash
# stage3.sh — Brand Positioning & Product Choice
set -euo pipefail
USER="${USER_NAME:-peserta}"
[[ "${1:-}" == "--user" ]] && USER="$2"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE=$(cat "$SCRIPT_DIR/templates/stage3-positioning.txt")
PROMPT="${TEMPLATE//<USER>/$USER}"
echo "=== Stage 3: Brand Positioning ==="
echo ""
echo "$PROMPT"
