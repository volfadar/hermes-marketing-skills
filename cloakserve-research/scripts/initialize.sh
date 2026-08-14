#!/usr/bin/env bash
# initialize.sh — ONE entry point. Sets up everything: deps check → start → wire → smoke test.
# Idempotent and safe to re-run. This is what users (and the agent) call after `skills install`.
#
# Usage:
#   bash initialize.sh                    # full setup, ask about Tailscale at the end
#   bash initialize.sh --skip-tailscale   # full setup, don't even mention Tailscale
#   bash initialize.sh --force            # tear down existing + fresh setup
#   bash initialize.sh --no-indonesia     # don't pre-seed Asia/Jakarta fingerprint
set -euo pipefail

PORT="${CLOAKSERVE_PORT:-9222}"
CONTAINER_NAME="${CLOAKSERVE_CONTAINER:-cloakserve}"
IMAGE="cloakhq/cloakbrowser:latest"
HERMES_HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
CFG="${HERMES_HOME_DIR}/config.yaml"

SKIP_TS="no"
FORCE="no"
TZ_FLAG="--fingerprint-timezone=Asia/Jakarta"
LOCALE_FLAG="--fingerprint-locale=id-ID"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-tailscale) SKIP_TS="yes"; shift ;;
    --force) FORCE="yes"; shift ;;
    --no-indonesia) TZ_FLAG=""; LOCALE_FLAG=""; shift ;;
    --port) PORT="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Pretty headers
section() { printf '\n\033[1;36m━━ %s ━━\033[0m\n' "$1"; }
ok()      { printf '  \033[1;32m✓\033[0m %s\n' "$1"; }
warn()    { printf '  \033[1;33m⚠\033[0m %s\n' "$1"; }
fail()    { printf '  \033[1;31m✗\033[0m %s\n' "$1"; }
die()     { fail "$1"; exit 1; }

section "1/5  Cek dependency"

# --- Docker ---
if command -v docker >/dev/null 2>&1; then
  ok "Docker: $(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',')"
else
  fail "Docker tidak ketemu."
  echo "    Install dulu: https://www.docker.com/products/docker-desktop"
  echo "    Setelah itu jalankan ulang: bash ${0##*/}"
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  die "Docker daemon tidak jalan. Start Docker Desktop dulu, lalu re-run."
fi

# --- Hermes ---
if command -v hermes >/dev/null 2>&1; then
  ok "Hermes: $(hermes --version 2>/dev/null | head -1)"
else
  warn "Hermes tidak di PATH. Skill masih bisa setup browser, tapi auto-wire dilewati."
  warn "Install Hermes: lihat https://hermes-agent.nousresearch.com/docs/getting-started/quickstart"
fi

# --- Optional Tailscale awareness (do not require) ---
TS_INSTALLED="no"
if command -v tailscale >/dev/null 2>&1; then
  TS_INSTALLED="yes"; ok "Tailscale terinstall (opsional, untuk exit node HP sendiri)"
else
  ok "Tailscale: tidak ada (opsional — lihat references/faq.md kalau mau riset Indonesia akurat)"
fi

# --- Hermes config dir ---
mkdir -p "${HERMES_HOME_DIR}"
touch "${CFG}"

section "2/5  Pull image CloakBrowser (sekali saja, ~150MB)"
if docker image inspect "${IMAGE}" >/dev/null 2>&1 && [[ "$FORCE" != "yes" ]]; then
  ok "Image sudah ada, skip pull"
else
  if ! docker pull "${IMAGE}" >/dev/null 2>&1; then
    die "Gagal pull image. Cek koneksi internet / login Docker Hub."
  fi
  ok "Image siap"
fi

section "3/5  Start cloakserve (Docker container)"
# Tear down if --force, or if a stale container exists
if [[ "$FORCE" == "yes" ]] || docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
fi

if curl -sf --max-time 3 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
  ok "cloakserve sudah jalan di port ${PORT}"
else
  printf '  Memulai container (download stealth Chromium pertama kali ~2-5 menit)...\n'
  if ! docker run -d \
      --name "${CONTAINER_NAME}" \
      -p "${PORT}:9222" \
      --shm-size=1g \
      --restart=unless-stopped \
      "${IMAGE}" \
      cloakserve --port=9222 ${TZ_FLAG} ${LOCALE_FLAG} >/dev/null 2>&1; then
    die "Gagal start container. Lihat: docker logs ${CONTAINER_NAME}"
  fi
  # Wait for the inner Chromium to expose CDP
  printf '  Menunggu CDP endpoint siap'
  READY=""
  for i in $(seq 1 90); do
    if curl -sf --max-time 2 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
      READY="1"; break
    fi
    printf '.'; sleep 2
  done
  echo
  [[ -n "$READY" ]] || die "cloakserve tidak siap dalam 3 menit. Lihat: docker logs ${CONTAINER_NAME}"
  ok "cloakserve jalan di port ${PORT}"
fi

# Report what fingerprint it presents as
UA_RAW=$(curl -sf "http://127.0.0.1:${PORT}/json/version" 2>/dev/null || echo "{}")
UA=$(printf '%s' "$UA_RAW" | python3 -c "import sys,json;print(json.load(sys.stdin).get('User-Agent','?'))" 2>/dev/null || echo "?")
ok "User-Agent fingerprint: ${UA}"

section "4/5  Wire Hermes ke CDP endpoint"
# Always call the dedicated wire script (it's idempotent and preserves other config)
bash "$(dirname "$0")/wire-hermes.sh" --port "${PORT}" --quiet || warn "wire-hermes.sh gagal — Hermes bisa masih di-wire manual"

section "5/5  Smoke test"
# Confirm CDP + verify Hermes config has cdp_url
if curl -sf --max-time 3 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
  ok "CDP endpoint reachable di port ${PORT}"
else
  die "CDP endpoint tidak reachable"
fi
if grep -q "cdp_url" "${CFG}" 2>/dev/null; then
  ok "Hermes config: browser.cdp_url ter-set"
else
  warn "Hermes config: cdp_url belum ter-set (wire mungkin gagal). Run: bash wire-hermes.sh"
fi

# Final doctor summary
printf '\n'
bash "$(dirname "$0")/doctor.sh" --brief 2>/dev/null || true

# Tailscale prompt
if [[ "$SKIP_TS" != "yes" && "$TS_INSTALLED" != "yes" ]]; then
  printf '\n\033[1;36m━━ Opsional: Tailscale exit node (riset Indonesia akurat) ━━\033[0m\n'
  cat <<TS
  Untuk riset marketplace/SERP yang akurat dari perspektif Indonesia, kamu bisa
  route traffic cloakserve lewat HP-mu sendiri (residential IP) pakai Tailscale.
  Ini OPSIONAL dan butuh setup 5 menit + akun Tailscale gratis.

  Pros:  hasil riset muncul seperti yang dilihat user Indonesia asli.
  Cons:  pakai kuota HP saat aktif; butuh install app di HP.

  Setup kapan saja: bash $(dirname "$0")/tailscale-setup.sh
TS
fi

printf '\n\033[1;32m━━ Selesai ━━\033[0m\n'
cat <<DONE
  cloakserve: running on port ${PORT}
  Hermes:     wired to ${PORT}
  Next:       buka Hermes, pakai prompt dari templates/ untuk riset.
              Contoh: bash $(dirname "$0")/research.sh "kopi arabika"
  Stop:       bash $(dirname "$0")/stop.sh
  Diagnosa:   bash $(dirname "$0")/doctor.sh
DONE
