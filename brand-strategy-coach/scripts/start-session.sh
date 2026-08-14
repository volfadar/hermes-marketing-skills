#!/usr/bin/env bash
# start-session.sh — initialize Hermes as strategic coach, start Stage 1.
# Usage: bash start-session.sh [--user <name>]
set -euo pipefail
USER="${USER_NAME:-peserta}"
[[ "${1:-}" == "--user" ]] && USER="$2"

CFG_DIR="${BRAND_COACH_DIR:-$HOME/.brand-coach}"
PROFILE_DIR="$CFG_DIR/profiles"
mkdir -p "$PROFILE_DIR"

# Init profile
PROFILE="$PROFILE_DIR/$USER.json"
if [[ ! -f "$PROFILE" ]]; then
  cat > "$PROFILE" <<EOF
{
  "user": "$USER",
  "schema_version": 3,
  "started_at": "$(date -Iseconds 2>/dev/null || echo unknown)",
  "current_stage": 1,
  "goal": null,
  "talent": null,
  "background": null,
  "positioning": null,
  "tools": null,
  "funnel": null,
  "dossier": {
    "cv": {
      "status": "pending",
      "summary": null,
      "roles": [],
      "skills": [],
      "education": []
    },
    "portfolio": {
      "status": "pending",
      "work_samples": []
    },
    "interview": [],
    "proof_ledger": [],
    "access": {
      "audiences": [],
      "relationships": [],
      "channels": [],
      "assets": []
    },
    "constraints": {
      "refuse": [],
      "cap": [],
      "access": [],
      "permission": []
    },
    "proof_gap": false,
    "unknowns": []
  },
  "economics": {
    "budget": null,
    "time": null,
    "team": null,
    "price": null,
    "gross_margin": null,
    "cash_cycle": null,
    "repeat_rate": null,
    "capacity": null,
    "payback_window": null
  },
  "goal_fit": {
    "needs": null,
    "needs_by": null,
    "plan_yields": null,
    "gap": null,
    "stated_to_user": false
  },
  "research": {
    "as_of": null,
    "brief": null,
    "_source_shape": {
      "url": "",
      "status": "opened | opened_empty | search_result | ai_summary",
      "is_search_page": false,
      "fetched_at": "",
      "supports": ""
    },
    "sources": [],
    "facts": [],
    "inferences": [],
    "contradictions": [],
    "unknowns": []
  },
  "evidence_ledger": [],
  "experiments": [],
  "decisions": [],
  "retracted": [],
  "backlog": []
}
EOF
  echo "✓ Profile baru: $PROFILE"
else
  echo "✓ Profile ada: $PROFILE (lanjut)"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE=$(cat "$SCRIPT_DIR/templates/stage1-temu-bakat.txt")
PROMPT="${TEMPLATE//<USER>/$USER}"

echo ""
echo "=== Hermes Strategic Coach — Stage 1 (Temu Bakat) ==="
echo ""
echo "Paste ke Hermes:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PROMPT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Setelah Stage 1 selesai + peserta konfirmasi, jalankan:"
echo "  bash scripts/save-profile.sh stage1  # untuk save talent"
echo "  bash scripts/stage2.sh               # lanjut Stage 2"
