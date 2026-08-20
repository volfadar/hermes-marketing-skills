#!/usr/bin/env bash
# doctor.sh — check skill setup.
set -uo pipefail
CFG_DIR="${CONTENT_CREATOR_DIR:-$HOME/.content-creator}"
PASS=0; WARN=0; FAIL=0
ok()   { PASS=$((PASS+1));  printf '  \033[1;32m✓\033[0m %s\n' "$1"; }
p_warn(){ WARN=$((WARN+1));  printf '  \033[1;33m⚠\033[0m %s\n' "$1"; }
p_fail(){ FAIL=$((FAIL+1));  printf '  \033[1;31m✗\033[0m %s\n' "$1"; }

printf '\n\033[1;36m━━ 1. Config ━━\033[0m\n'
[[ -d "$CFG_DIR" ]] && ok "Config dir: $CFG_DIR" || { p_fail "Config dir tidak ada. Run pillars.sh."; }

printf '\n\033[1;36m━━ 2. Pillars ━━\033[0m\n'
if [[ -f "$CFG_DIR/pillars.json" ]]; then
  ok "Pillars set"
  python3 -c "import json; d=json.load(open('$CFG_DIR/pillars.json')); print('  ', len(d['pillars']), 'pillars:', ', '.join(d['pillars']))" 2>/dev/null
else
  p_fail "Belum set pillars. Run: bash scripts/pillars.sh \"p1, p2, p3\""
fi

printf '\n\033[1;36m━━ 3. Voice profile ━━\033[0m\n'
MEM="${HERMES_HOME:-$HOME/.hermes}/memories/USER.md"
if [[ -f "$MEM" ]] && grep -qi "voice\|tone\|brand" "$MEM" 2>/dev/null; then
  ok "Voice profile terdeteksi di $MEM"
else
  p_warn "Voice profile belum ada — output bakal terdengar generik"
  echo "      belum pernah posting? pakai export chat WA atau balasanmu ke pelanggan:"
  echo "      bash scripts/voice-profile.sh <folder|file|->"
fi

printf '\n\033[1;36m━━ 4. Dependencies ━━\033[0m\n'
command -v hermes >/dev/null && ok "Hermes: $(hermes --version 2>/dev/null | head -1)" || p_warn "Hermes tidak di PATH"
command -v python3 >/dev/null && ok "python3" || p_fail "python3 diperlukan"

printf '\n\033[1;36m━━ 5. Related skills ━━\033[0m\n'
SKILLS="${HERMES_HOME:-$HOME/.hermes}/skills"
[[ -d "$SKILLS/ibras-cloakserve-research" ]] && ok "ibras-cloakserve-research available (for trend research)" || p_warn "ibras-cloakserve-research tidak terinstall (opsional, untuk riset tren)"
[[ -d "$SKILLS/ibras-waha-marketing" ]] && ok "ibras-waha-marketing available (for WA list building)" || p_warn "ibras-waha-marketing tidak terinstall (opsional)"

printf '\n\033[1;36m━━ Ringkasan ━━\033[0m  \033[1;32m%d OK\033[0m  \033[1;33m%d warn\033[0m  \033[1;31m%d fail\033[0m\n' "$PASS" "$WARN" "$FAIL"
[[ "$FAIL" -gt 0 ]] && exit 1
exit 0
