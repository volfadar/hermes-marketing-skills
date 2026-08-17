#!/usr/bin/env bash
# halt.sh — tombol berhenti. Satu perintah, semua jalur keluar.
#
# Menggantikan dua tombol lama yang tidak saling kenal:
#   skill-ibras-waha-marketing/scripts/emergency-halt.sh   (/tmp/waha-broadcast-halt)
#   skill-ibras-email-marketing/scripts/emergency-halt.sh  (/tmp/hermes-email-halt)
#
# Keduanya masih jalan dan masih dibaca, tapi yang ini menghentikan semuanya
# sekaligus dan bertahan setelah komputer di-restart.
#
#   bash halt.sh                      # sedang berhenti atau tidak?
#   bash halt.sh on --why "salah kirim"
#   bash halt.sh off
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB="$HERE/lib/halt.py"
[[ -f "$LIB" ]] || LIB="$HERE/../../shared/scripts/lib/halt.py"

if [[ ! -f "$LIB" ]]; then
  echo "FATAL: halt.py tidak ditemukan di $LIB" >&2
  echo "Tombol berhenti tidak boleh gagal diam-diam. Perbaiki dulu sebelum mengirim apa pun." >&2
  exit 2
fi

exec python3 "$LIB" "$@"
