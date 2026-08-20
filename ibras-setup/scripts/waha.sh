#!/usr/bin/env bash
# waha.sh — run a local WAHA instance and hand it to ibras-waha-marketing.
#
# WAHA Plus merged into WAHA Core in v2026.6.1: one public image, every feature,
# no Patron key, no `docker login`.
#   https://waha.devlike.pro/docs/how-to/waha-plus/  (read 20 Aug 2026)
#
#   bash waha.sh                 start + verify + write config
#   bash waha.sh --port 3000
#   bash waha.sh --no-key        skip API key (local only, not for a public host)
set -uo pipefail

PORT="${WAHA_PORT:-3000}"
NAME="${WAHA_CONTAINER:-waha}"
IMAGE="devlikeapro/waha"
USE_KEY="yes"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    --no-key) USE_KEY="no"; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "arg tidak dikenal: $1" >&2; exit 2 ;;
  esac
done

command -v docker >/dev/null 2>&1 || {
  echo "✗ Docker tidak ada. WAHA butuh Docker."
  echo "  https://docs.docker.com/engine/install/"
  exit 1; }
docker info >/dev/null 2>&1 || {
  echo "✗ Docker terpasang tapi daemon-nya mati. Nyalakan Docker dulu."
  exit 1; }

if curl -sf --max-time 3 "http://127.0.0.1:${PORT}/api/version" >/dev/null 2>&1; then
  echo "✓ WAHA sudah jalan di port ${PORT}"
else
  KEY=""
  if [[ "$USE_KEY" == "yes" ]]; then
    KEY="$(python3 -c 'import secrets;print(secrets.token_urlsafe(24))')"
    echo "  API key dibuat otomatis (tidak pernah muncul di command line)."
  fi
  echo "  menarik ${IMAGE} …"
  docker pull "$IMAGE" >/dev/null 2>&1 || { echo "✗ gagal menarik image"; exit 1; }
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  if [[ -n "$KEY" ]]; then
    docker run -d --name "$NAME" --restart unless-stopped \
      -p "127.0.0.1:${PORT}:3000" -e "WHATSAPP_API_KEY=${KEY}" "$IMAGE" >/dev/null
  else
    docker run -d --name "$NAME" --restart unless-stopped \
      -p "127.0.0.1:${PORT}:3000" "$IMAGE" >/dev/null
  fi
  echo -n "  menunggu WAHA siap"
  for _ in $(seq 1 40); do
    curl -sf --max-time 2 "http://127.0.0.1:${PORT}/api/version" >/dev/null 2>&1 && break
    echo -n "."; sleep 2
  done; echo
  curl -sf --max-time 3 "http://127.0.0.1:${PORT}/api/version" >/dev/null 2>&1 || {
    echo "✗ WAHA tidak merespons. Lihat: docker logs $NAME --tail 40"; exit 1; }
  echo "✓ WAHA jalan — $(curl -sf http://127.0.0.1:${PORT}/api/version | head -c 120)"

  SK="${HERMES_HOME:-$HOME/.hermes}/skills"
  INIT="$SK/ibras-waha-marketing/scripts/initialize.sh"
  if [[ -f "$INIT" ]]; then
    # key passed via env, never on the command line — argv is world-readable
    if [[ -n "$KEY" ]]; then WAHA_URL="http://127.0.0.1:${PORT}" API_KEY="$KEY" bash "$INIT"
    else WAHA_URL="http://127.0.0.1:${PORT}" bash "$INIT"; fi
  else
    echo "  (skill ibras-waha-marketing belum terpasang — WAHA-nya sudah jalan)"
  fi
fi

cat <<TXT

Langkah terakhir ada di tangan kamu — sambungkan nomor WhatsApp:

  1. buka  http://127.0.0.1:${PORT}/dashboard
  2. start session, scan QR-nya dari WhatsApp di HP
  3. status harus jadi WORKING

Cek:  bash \${HERMES_HOME:-\$HOME/.hermes}/skills/ibras-waha-marketing/scripts/doctor.sh
Stop: docker stop ${NAME}     Log: docker logs ${NAME} --tail 40
TXT
