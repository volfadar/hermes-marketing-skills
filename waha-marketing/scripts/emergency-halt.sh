#!/usr/bin/env bash
# emergency-halt.sh — SHIM ke tombol berhenti bersama.
#
# Dulu file ini cuma menyentuh /tmp/waha-broadcast-halt, dan itu punya dua masalah:
# tidak menghentikan email (tombolnya beda, namanya beda), dan hilang saat komputer
# di-restart — jadi sistem yang sudah dihentikan bisa jalan lagi sendiri.
#
# Sekarang satu perintah menghentikan semuanya, dan bertahan setelah restart.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "${1:-on}" in
  --resume|off|--off) exec bash "$HERE/halt.sh" off ;;
  status|--status)    exec bash "$HERE/halt.sh" status ;;
  *)                  exec bash "$HERE/halt.sh" on --why "emergency-halt.sh (waha)" ;;
esac
