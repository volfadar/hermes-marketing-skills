#!/usr/bin/env bash
# start.sh — launch the CloakBrowser CDP multiplexer (cloakserve) in Docker.
# Idempotent. Default fingerprint: Asia/Jakarta, id-ID.
# Usage: bash start.sh [--port 9222] [--fingerprint-seed <name>] [--no-indonesia]
set -euo pipefail
PORT="${CLOAKSERVE_PORT:-9222}"
SEED="${CLOAKSERVE_FINGERPRINT:-}"
CONTAINER_NAME="${CLOAKSERVE_CONTAINER:-cloakserve}"
IMAGE="cloakhq/cloakbrowser:latest"
TZ_FLAG="--fingerprint-timezone=Asia/Jakarta"
LOCALE_FLAG="--fingerprint-locale=id-ID"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    --fingerprint-seed) SEED="$2"; shift 2 ;;
    --no-indonesia) TZ_FLAG=""; LOCALE_FLAG=""; shift ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Already running? short-circuit.
if curl -sf --max-time 3 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
  echo "cloakserve: ALREADY RUNNING on port ${PORT}"
  echo "cdp_url: ws://127.0.0.1:${PORT}"
  exit 0
fi

docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

SEED_FLAG=""; [[ -n "${SEED}" ]] && SEED_FLAG="--fingerprint=${SEED}"

# Auto-pull if image missing
docker image inspect "${IMAGE}" >/dev/null 2>&1 || docker pull "${IMAGE}" >/dev/null

echo "cloakserve: starting (first run downloads ~150MB stealth Chromium)..."
docker run -d \
  --name "${CONTAINER_NAME}" \
  -p "${PORT}:9222" \
  --shm-size=1g \
  --restart=unless-stopped \
  "${IMAGE}" \
  cloakserve --port=9222 ${TZ_FLAG} ${LOCALE_FLAG} ${SEED_FLAG} >/dev/null

echo "cloakserve: waiting for CDP endpoint on port ${PORT}..."
READY=""
for i in $(seq 1 90); do
  if curl -sf --max-time 2 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
    READY="1"; break
  fi
  sleep 2
done

if [[ -z "${READY}" ]]; then
  echo "cloakserve: FAILED to become ready in 180s. Container logs:" >&2
  docker logs "${CONTAINER_NAME}" 2>&1 | tail -20 >&2
  echo "Run: bash $(dirname "$0")/doctor.sh" >&2
  exit 1
fi

echo "cloakserve: RUNNING on port ${PORT}"
echo "cdp_url: ws://127.0.0.1:${PORT}"
echo "Connect Hermes: bash $(dirname "$0")/wire-hermes.sh"
