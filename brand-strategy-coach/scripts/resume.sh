#!/usr/bin/env bash
# resume.sh — load latest profile, continue from current_stage.
# Usage: bash resume.sh [--user <name>]
set -euo pipefail
USER="${USER_NAME:-peserta}"
[[ "${1:-}" == "--user" ]] && USER="$2"

CFG_DIR="${BRAND_COACH_DIR:-$HOME/.brand-coach}"
PROFILE="$CFG_DIR/profiles/$USER.json"
[[ -f "$PROFILE" ]] || { echo "Profile tidak ada. Run start-session.sh dulu." >&2; exit 1; }

STAGE=$(python3 -c "import json; print(json.load(open('$PROFILE')).get('current_stage', 1))")
echo "=== Resume: $USER (current stage: $STAGE) ==="
echo ""
case "$STAGE" in
  1) bash "$(dirname "$0")/start-session.sh" --user "$USER" ;;
  2) bash "$(dirname "$0")/stage2.sh" --user "$USER" ;;
  3) bash "$(dirname "$0")/stage3.sh" --user "$USER" ;;
  4) bash "$(dirname "$0")/stage4.sh" --user "$USER" ;;
  5) bash "$(dirname "$0")/stage5.sh" --user "$USER" ;;
  *) echo "Stage tidak dikenali: $STAGE"; exit 1 ;;
esac
