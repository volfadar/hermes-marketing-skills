#!/usr/bin/env bash
# audit.sh — review past content performance + lessons.
# Usage: bash audit.sh [--month] <stats-file.csv>
set -euo pipefail
PERIOD="week"
FILE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --week) PERIOD="week"; shift ;;
    --month) PERIOD="month"; shift ;;
    *) FILE="$1"; shift ;;
  esac
done

if [[ -z "$FILE" ]]; then
  echo "Usage: bash audit.sh <stats.csv> [--week|--month]"
  echo ""
  echo "Stats CSV format:"
  echo "  date,platform,topic,format,reach,engagement,clicks,saves"
  echo "  2026-08-01,instagram,brewing tips,reel,1240,85,12,34"
  echo ""
  echo "Export dari Meta Business Suite / TikTok Analytics / YouTube Studio."
  exit 1
fi

[[ ! -f "$FILE" ]] && { echo "File tidak ada: $FILE"; exit 1; }

CONTENT=$(cat "$FILE")
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE=$(awk 'BEGIN{p=0} /^---$/{p=1; next} p{print}' "$SCRIPT_DIR/templates/audit.txt")
PROMPT="${TEMPLATE//<STATS>/$CONTENT}"
PROMPT="${PROMPT//<PERIOD>/$PERIOD}"

echo "$PROMPT"
