#!/usr/bin/env bash
# doctor.sh — diagnose WAHA connectivity + skill setup.
set -uo pipefail
CFG_DIR="${WAHA_CONFIG_DIR:-$HOME/.waha-marketing}"
CFG="$CFG_DIR/config.env"

PASS=0; WARN=0; FAIL=0
ok()   { PASS=$((PASS+1));  printf '  \033[1;32m✓\033[0m %s\n' "$1"; }
p_warn(){ WARN=$((WARN+1));  printf '  \033[1;33m⚠\033[0m %s\n' "$1"; }
p_fail(){ FAIL=$((FAIL+1));  printf '  \033[1;31m✗\033[0m %s\n' "$1"; }
hdr()  { printf '\n\033[1;36m━━ %s ━━\033[0m\n' "$1"; }

hdr "1. Config"
if [[ -f "$CFG" ]]; then
  ok "Config file: $CFG"
  # shellcheck disable=SC1090
  source "$CFG"
  [[ -n "${WAHA_URL:-}" ]] && ok "WAHA_URL set" || p_fail "WAHA_URL kosong"
  [[ -n "${WAHA_API_KEY:-}" ]] && ok "WAHA_API_KEY set (hidden)" || p_fail "WAHA_API_KEY kosong"
  [[ -n "${WAHA_SESSION:-}" ]] && ok "WAHA_SESSION: $WAHA_SESSION" || p_warn "WAHA_SESSION kosong (default 'default')"
else
  p_fail "Config tidak ada di $CFG. Run: bash scripts/initialize.sh --url ... --key ..."
fi

hdr "2. Connectivity"
if [[ -n "${WAHA_URL:-}" && -n "${WAHA_API_KEY:-}" ]]; then
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "${WAHA_URL}/health" \
         -H "X-Api-Key: ${WAHA_API_KEY}" --max-time 10 || echo "000")
  if [[ "$CODE" == "200" ]]; then ok "WAHA server reachable (health 200)"
  else p_fail "WAHA health check gagal (HTTP $CODE). Cek URL/key/network."; fi

  # Session status
  if [[ -n "${WAHA_SESSION:-}" ]]; then
    STATUS=$(curl -s "${WAHA_URL}/api/sessions/${WAHA_SESSION}" \
             -H "X-Api-Key: ${WAHA_API_KEY}" --max-time 10 2>/dev/null | \
             python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null || echo "?")
    if [[ "$STATUS" == "WORKING" ]]; then ok "Session '$WAHA_SESSION': WORKING"
    else p_fail "Session '$WAHA_SESSION' status: $STATUS (butuh scan QR / restart)"; fi
  fi
fi

hdr "3. Dependencies"
command -v curl >/dev/null && ok "curl available" || p_fail "curl tidak ada"
command -v python3 >/dev/null && ok "python3 available" || p_fail "python3 tidak ada (dibutuhkan lib/broadcast.py)"
command -v docker >/dev/null && p_warn "docker available (tidak wajib — WAHA di-host terpisah)" || ok "docker tidak diperlukan di sini"

hdr "4. Broadcast readiness"
[[ -f "${CFG_DIR}/state/sent.json" ]] && ok "State file ada (cooldown tracking aktif)" || p_warn "State belum ada (akan dibuat saat broadcast pertama)"
[[ -f "/tmp/waha-broadcast-halt" ]] && p_fail "HALT file ada (/tmp/waha-broadcast-halt) — broadcast tidak akan jalan sampai dihapus" || ok "Tidak ada HALT file"

hdr "5. Lapisan bersama (profil, cek copy, catatan)"
SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for f in profile.py copycheck.py ledger.py handoff.py; do
  if [[ -f "$SKILL_ROOT/lib/$f" ]]; then ok "lib/$f ada"
  else p_fail "lib/$f hilang — jalankan: bash shared/sync.sh"; fi
done
# An empty profile is normal and must never read as a failure: every tool here
# works without one. It only means promos will be generic, which is worth
# saying out loud once.
if PROF_OUT="$(python3 "$SKILL_ROOT/lib/profile.py" check 2>&1)"; then
  if python3 "$SKILL_ROOT/lib/profile.py" get sikap.kenapa_aku >/dev/null 2>&1; then
    ok "Profil usaha terisi ($(echo "$PROF_OUT" | tr -d '\n' | sed 's/^ *//'))"
  else
    p_warn "Profil belum punya 'sikap' — promo bakal generik. Isi lewat brand-strategy-coach."
  fi
else
  p_fail "profile.yaml rusak: $PROF_OUT"
fi

printf '\n\033[1;36m━━ Ringkasan ━━\033[0m  \033[1;32m%d OK\033[0m  \033[1;33m%d warn\033[0m  \033[1;31m%d fail\033[0m\n' "$PASS" "$WARN" "$FAIL"
[[ "$FAIL" -gt 0 ]] && exit 1
exit 0
