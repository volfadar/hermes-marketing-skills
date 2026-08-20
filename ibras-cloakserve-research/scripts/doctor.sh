#!/usr/bin/env bash
# doctor.sh — full diagnostic. Run this when anything is broken.
# Usage: bash doctor.sh [--brief]
set -uo pipefail
PORT="${CLOAKSERVE_PORT:-9222}"
CONTAINER_NAME="${CLOAKSERVE_CONTAINER:-cloakserve}"
HERMES_HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
CFG="${HERMES_HOME_DIR}/config.yaml"
BRIEF="${1:-}"

PASS=0; WARN=0; FAIL=0
p_ok()   { PASS=$((PASS+1));  [[ "$BRIEF" != "--brief" ]] && printf '  \033[1;32m✓\033[0m %s\n' "$1"; }
p_warn() { WARN=$((WARN+1));  printf '  \033[1;33m⚠\033[0m %s\n' "$1"; }
p_fail() { FAIL=$((FAIL+1));  printf '  \033[1;31m✗\033[0m %s\n' "$1"; }
hdr()    { [[ "$BRIEF" != "--brief" ]] && printf '\n\033[1;36m━━ %s ━━\033[0m\n' "$1"; }

hdr "1. Docker"
if command -v docker >/dev/null 2>&1; then
  p_ok "Docker: $(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',')"
  if docker info >/dev/null 2>&1; then p_ok "Docker daemon: jalan"
  else p_fail "Docker daemon tidak jalan — start Docker Desktop"; fi
elif curl -sf --max-time 3 "http://127.0.0.1:${PORT:-9222}/json/version" >/dev/null 2>&1; then
  # CDP sudah hidup lewat jalur lain (Chromium langsung). Docker cuma salah satu
  # dari dua rute; menandainya gagal padahal browsernya jalan itu alarm palsu.
  p_warn "Docker tidak ada, tapi CDP sudah hidup lewat jalur lain — tidak masalah"
  p_warn "  (cloakserve punya fingerprint Asia/Jakarta + id-ID; jalur langsung tidak)"
else
  p_fail "Docker tidak terinstall, dan tidak ada CDP di port ${PORT:-9222} — https://docker.com"
fi

hdr "2. Container cloakserve"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "${CONTAINER_NAME}"; then
  STATUS=$(docker inspect -f '{{.State.Status}}' "${CONTAINER_NAME}" 2>/dev/null)
  UPTIME=$(docker inspect -f '{{.State.StartedAt}}' "${CONTAINER_NAME}" 2>/dev/null | cut -dT -f1)
  p_ok "Container ${CONTAINER_NAME}: ${STATUS} (sejak ${UPTIME})"
else
  if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -qx "${CONTAINER_NAME}"; then
    p_fail "Container ada tapi STOPPED. Start: bash $(dirname "$0")/start.sh"
  else
    p_warn "Container belum dibuat. Run: bash $(dirname "$0")/initialize.sh"
  fi
fi

hdr "3. CDP endpoint (port ${PORT})"
if VER=$(curl -sf --max-time 3 "http://127.0.0.1:${PORT}/json/version" 2>/dev/null); then
  BROWSER=$(printf '%s' "$VER" | python3 -c "import sys,json;print(json.load(sys.stdin).get('Browser','?'))" 2>/dev/null)
  UA=$(printf '%s' "$VER" | python3 -c "import sys,json;print(json.load(sys.stdin).get('User-Agent','?'))" 2>/dev/null)
  p_ok "CDP reachable — ${BROWSER}"
  p_ok "User-Agent: ${UA}"
else
  p_fail "CDP endpoint port ${PORT} tidak reachable"
  echo "    Kemungkinan: container masih booting (tunggu 60s), atau port bentrok."
  echo "    Cek log: docker logs ${CONTAINER_NAME}"
fi

hdr "4. Hermes config"
if command -v hermes >/dev/null 2>&1; then p_ok "Hermes: $(hermes --version 2>/dev/null | head -1)"
else p_warn "Hermes tidak di PATH"; fi
if [[ -f "$CFG" ]]; then
  if grep -q "cdp_url" "$CFG" 2>/dev/null; then
    p_ok "browser.cdp_url ter-set di ${CFG}"
  else
    p_warn "browser.cdp_url BELUM ter-set. Run: bash $(dirname "$0")/wire-hermes.sh"
  fi
  # Baca nilainya, jangan cocokkan nama vendor. Versi lama grep untuk
  # deepseek|claude|gpt|gemini|nous, jadi model yang sah tapi di luar daftar itu
  # dilaporkan "hilang" pada instalasi yang sebenarnya benar — dan doctor yang
  # gagal di instalasi sehat mengajari orang mengabaikan doctor.
  MODEL_DEFAULT="$(python3 - "$CFG" <<'PYEOF' 2>/dev/null
import sys, yaml
try: c = yaml.safe_load(open(sys.argv[1])) or {}
except Exception: c = {}
print(((c.get("model") or {}).get("default") or "").strip())
PYEOF
)"
  if [[ -n "$MODEL_DEFAULT" ]]; then
    p_ok "model.default ter-set: ${MODEL_DEFAULT}"
  else
    p_fail "model.default hilang/kosong — Hermes akan error 404 tool-use. Edit ${CFG}:"
    echo "    model:"
    echo "      default: \"deepseek/deepseek-v4-flash-0731\""
    echo "      provider: \"openrouter\""
  fi
else
  p_fail "Config tidak ada: ${CFG}"
fi

hdr "5. Tailscale (opsional)"
if command -v tailscale >/dev/null 2>&1; then
  if tailscale status >/dev/null 2>&1; then
    EXIT=$(tailscale status --json 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin).get('ExitNodeStatus',{}).get('Online',False))" 2>/dev/null || echo "?")
    p_ok "Tailscale up — exit node active: ${EXIT}"
  else
    p_warn "Tailscale terinstall tapi belum up. Run: sudo tailscale up"
  fi
else
  p_warn "Tailscale tidak terinstall (opsional)"
fi

hdr "6. Environment checks"
[[ -w /var/run/docker.sock ]] && p_ok "Docker socket accessible" || p_warn "Docker socket permission mungkin butuh sudo/user group"
command -v python3 >/dev/null 2>&1 && p_ok "python3 available" || p_warn "python3 tidak ada (diperlukan beberapa script)"
command -v curl >/dev/null 2>&1 && p_ok "curl available" || p_warn "curl tidak ada"

# Summary
printf '\n\033[1;36m━━ Ringkasan ━━\033[0m  \033[1;32m%d OK\033[0m  \033[1;33m%d warn\033[0m  \033[1;31m%d fail\033[0m\n' "$PASS" "$WARN" "$FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  echo "Perbaiki yang ✗ di atas, lalu re-run: bash $(dirname "$0")/doctor.sh"
  exit 1
fi
exit 0
