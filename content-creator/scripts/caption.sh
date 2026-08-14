#!/usr/bin/env bash
# caption.sh — single caption draft in your voice.
# Usage: bash caption.sh "<topic>" --platform instagram [--hook story|question|list|contrarian]
set -euo pipefail
TOPIC="${1:-}"
PLATFORM="instagram"
HOOK="story"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform) PLATFORM="$2"; shift 2 ;;
    --hook) HOOK="$2"; shift 2 ;;
    *) TOPIC="$1"; shift ;;
  esac
done
[[ -z "$TOPIC" ]] && { echo "Usage: bash caption.sh \"<topic>\" --platform X"; exit 1; }

CFG_DIR="${CONTENT_CREATOR_DIR:-$HOME/.content-creator}"
PILLARS_FILE="$CFG_DIR/pillars.json"
PILLARS=""
[[ -f "$PILLARS_FILE" ]] && PILLARS=$(python3 -c "import json; print(', '.join(json.load(open('$PILLARS_FILE'))['pillars']))")

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE=$(awk 'BEGIN{p=0} /^---$/{p=1; next} p{print}' "$SCRIPT_DIR/templates/caption.txt")
PROMPT="${TEMPLATE//<TOPIC>/$TOPIC}"
PROMPT="${PROMPT//<PLATFORM>/$PLATFORM}"
PROMPT="${PROMPT//<HOOK>/$HOOK}"
PROMPT="${PROMPT//<PILLARS>/$PILLARS}"

echo "$PROMPT"
