#!/usr/bin/env bash
# ideate.sh — generate content ideas from pillars + optional trend research.
# Usage: bash ideate.sh [--week|--month] [--platform instagram|tiktok|youtube|x|linkedin|blog]
set -euo pipefail
PERIOD="week"
PLATFORM="instagram"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --week) PERIOD="week"; shift ;;
    --month) PERIOD="month"; shift ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    *) echo "Unknown: $1" >&2; exit 2 ;;
  esac
done

CFG_DIR="${CONTENT_CREATOR_DIR:-$HOME/.content-creator}"
PILLARS_FILE="$CFG_DIR/pillars.json"
N=$([[ "$PERIOD" == "week" ]] && echo "10" || echo "30")

if [[ ! -f "$PILLARS_FILE" ]]; then
  echo "✗ Belum set pillars. Run: bash scripts/pillars.sh \"p1, p2, p3\""
  exit 1
fi

PILLARS=$(python3 -c "import json; print(', '.join(json.load(open('$PILLARS_FILE'))['pillars']))")

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# Use the ideation template, substitute placeholders
TEMPLATE=$(awk 'BEGIN{p=0} /^---$/{p=1; next} p{print}' "$SCRIPT_DIR/templates/ideation.txt")
PROMPT="${TEMPLATE//<PILLARS>/$PILLARS}"
PROMPT="${PROMPT//<PERIOD>/$PERIOD}"
PROMPT="${PROMPT//<PLATFORM>/$PLATFORM}"
PROMPT="${PROMPT//<N>/$N}"

echo "=== Ideation: $N ideas for $PLATFORM ($PERIOD) ==="
echo "Pillars: $PILLARS"
echo ""
echo "Paste this prompt to Hermes:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PROMPT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Tip: kalau punya skill ibras-cloakserve-research, tambah riset tren dulu:"
echo "  bash ~/.hermes/skills/ibras-cloakserve-research/scripts/research.sh \"<niche> tren\" --template niche-trend"
