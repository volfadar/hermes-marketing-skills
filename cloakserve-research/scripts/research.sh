#!/usr/bin/env bash
# research.sh — convenience wrapper to run a research task through the skill.
# Starts cloakserve if needed, ensures wiring, then prints a ready-to-paste prompt.
#
# Usage:
#   bash research.sh "kopi arabika"               # uses default marketplace prompt
#   bash research.sh "kopi arabika" --template competitor-marketplace
#   bash research.sh --list                        # list available templates
#   bash research.sh --print competitor-marketplace "kopi arabika"   # just print the prompt
#
# This does NOT execute the prompt itself — it preps infra + gives you the prompt
# to paste into Hermes. (You stay in control of what gets researched.)
set -euo pipefail

PORT="${CLOAKSERVE_PORT:-9222}"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES_DIR="${SCRIPT_DIR}/templates"
CDP_URL="ws://127.0.0.1:${PORT}"

# --list: enumerate templates
if [[ "${1:-}" == "--list" ]]; then
  echo "Template prompt yang tersedia:"
  for f in "${TEMPLATES_DIR}"/*.txt; do
    [[ -f "$f" ]] || continue
    NAME=$(basename "$f" .txt)
    DESC=$(sed -n 's/^# description: //p' "$f" | head -1)
    printf '  %-28s %s\n' "$NAME" "${DESC:-}"
  done
  exit 0
fi

# --print: just render a template, no infra
if [[ "${1:-}" == "--print" ]]; then
  TEMPLATE="${2:-competitor-marketplace}"
  QUERY="${3:-<QUERY>}"
  FILE="${TEMPLATES_DIR}/${TEMPLATE}.txt"
  [[ -f "$FILE" ]] || { echo "Template tidak ada: $TEMPLATE. Run: $0 --list" >&2; exit 1; }
  # Skip the leading comment lines, substitute placeholders
  awk 'BEGIN{p=0} /^---$/{p=1; next} p{print}' "$FILE" | \
    sed "s|<QUERY>|${QUERY}|g; s|<CDP_URL>|${CDP_URL}|g; s|<SKILL_DIR>|${SCRIPT_DIR}|g"
  exit 0
fi

# Default flow: positional args
QUERY="${1:-}"
TEMPLATE="${2:-}"
[[ -n "$QUERY" && "$QUERY" == --* ]] && { TEMPLATE="$QUERY"; QUERY="${2:-}"; }
TEMPLATE="${TEMPLATE#--template}"
TEMPLATE="${TEMPLATE:-competitor-marketplace}"

if [[ -z "$QUERY" ]]; then
  cat <<USAGE
Usage:
  bash $0 "<query>"                     # riset pakai template default
  bash $0 "<query>" --template <name>   # pakai template tertentu
  bash $0 --list                        # lihat semua template
  bash $0 --print <name> "<query>"      # print prompt aja tanpa infra

Contoh:
  bash $0 "kopi arabika"
  bash $0 "kopi arabika" --template competitor-marketplace
USAGE
  exit 0
fi

# Prep infra (idempotent)
echo ">>> Memastikan cloakserve jalan..."
bash "${SCRIPT_DIR}/scripts/start.sh" --port "${PORT}" >/dev/null 2>&1 || true
bash "${SCRIPT_DIR}/scripts/wire-hermes.sh" --port "${PORT}" --quiet >/dev/null 2>&1 || true

echo ">>> Prompt siap (copy ke Hermes):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
bash "$0" --print "${TEMPLATE}" "${QUERY}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Tip: untuk riset non-marketplace, run: bash $0 --list"
