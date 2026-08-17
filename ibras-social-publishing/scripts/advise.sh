#!/usr/bin/env bash
# advise.sh — pintu masuk untuk bertanya "sebaiknya saya pakai apa?"
#
#   bash advise.sh options                         semua jalur, ringkas
#   bash advise.sh show selfhost-scheduler         satu jalur + semua kerugiannya
#   bash advise.sh compare official-api selfhost-scheduler
#   bash advise.sh platforms                       angka resmi per platform
#   bash advise.sh sources                         dari mana setiap klaim berasal
#
#   bash advise.sh recommend \
#     --budget 5 \
#     --platforms instagram,threads \
#     --skill 2 \
#     --volume 4 \
#     --account-value high
#
# Tambahkan --json ke sebagian besar perintah untuk output yang diproses Hermes.
#
# Catatan: skill ini menasihati, tidak menerbitkan. Yang menerbitkan adalah
# jalur yang kamu pilih. Itu disengaja — keputusannya terlalu tergantung
# konteks untuk dipilihkan oleh sebuah skrip.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

case "${1:-}" in
  -h|--help|help|"")
    sed -n '2,22p' "$0"
    exit 0
    ;;
esac

exec python3 "$SKILL_DIR/scripts/lib/advisor.py" "$@"
