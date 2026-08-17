#!/usr/bin/env bash
# repurpose.sh — one long-form → N platform-specific drafts. NEVER identical text.
# Usage: bash repurpose.sh <source-file> [--platforms all|instagram,tiktok,x,linkedin,blog]
set -euo pipefail
SOURCE="${1:-}"
PLATFORMS="${2:-all}"
[[ -z "$SOURCE" || ! -f "$SOURCE" ]] && {
  echo "Usage: bash repurpose.sh <source.md> [--platforms all|instagram,tiktok,x,linkedin,blog]"
  exit 1
}
[[ "$1" == "--platforms" ]] && { PLATFORMS="$2"; SOURCE=""; }  # rare arg order

# Read source (cap to avoid context bloat)
CONTENT=$(head -c 8000 "$SOURCE")

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE=$(awk 'BEGIN{p=0} /^---$/{p=1; next} p{print}' "$SCRIPT_DIR/templates/repurpose.txt")
PROMPT="${TEMPLATE//<SOURCE>/$CONTENT}"
PROMPT="${PROMPT//<PLATFORMS>/$PLATFORMS}"

echo "=== Repurpose: $(basename "$SOURCE") → $PLATFORMS ==="
echo ""
echo "Paste this prompt to Hermes:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PROMPT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠  Output adalah DRAFT. Review, edit yang tidak terdengar seperti kamu, post native."
echo "⚠  Jangan copy-paste identical text antar platform (algoritma penalti + audience fatigue)."
