#!/usr/bin/env bash
# calendar.sh — build a content calendar (markdown table).
# Usage: bash calendar.sh --weeks 2 --platform instagram [--ratio 5:1]
set -euo pipefail
WEEKS=2
PLATFORM="instagram"
RATIO="5:1"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --weeks) WEEKS="$2"; shift 2 ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    --ratio) RATIO="$2"; shift 2 ;;
    *) echo "Unknown: $1" >&2; exit 2 ;;
  esac
done

CFG_DIR="${CONTENT_CREATOR_DIR:-$HOME/.content-creator}"
PILLARS_FILE="$CFG_DIR/pillars.json"
if [[ ! -f "$PILLARS_FILE" ]]; then
  echo "✗ Set pillars dulu: bash scripts/pillars.sh"
  exit 1
fi
PILLARS=$(python3 -c "import json; print(', '.join(json.load(open('$PILLARS_FILE'))['pillars']))")

DAYS=$((WEEKS * 7))
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE=$(awk 'BEGIN{p=0} /^---$/{p=1; next} p{print}' "$SCRIPT_DIR/templates/calendar.txt")
PROMPT="${TEMPLATE//<WEEKS>/$WEEKS}"
PROMPT="${PROMPT//<PLATFORM>/$PLATFORM}"
PROMPT="${PROMPT//<RATIO>/$RATIO}"
PROMPT="${PROMPT//<PILLARS>/$PILLARS}"
PROMPT="${PROMPT//<DAYS>/$DAYS}"

echo "$PROMPT"
