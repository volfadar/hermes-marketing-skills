#!/usr/bin/env bash
# autoreply.sh — wrapper untuk scripts/lib/autoresponder.py.
#
# URUTAN YANG DISARANKAN (bukan aturan — kamu boleh langsung ke mana pun):
#
#   1. bash autoreply.sh validate
#      Periksa faq.yaml. Cari entri yang polanya terlalu sedikit atau bentrok.
#
#   2. bash autoreply.sh simulate --text "kak buka jam berapa?"
#      Uji satu pertanyaan tanpa menyentuh mailbox. Ini alat belajar terbaik:
#      kamu lihat skor keyakinannya, pola mana yang kena, trigger apa yang nyala.
#
#   3. bash autoreply.sh scan
#      Triage inbox nyata. Berapa persen yang sebenarnya tertutup FAQ kamu?
#      Kalau jawabannya 10%, FAQ-nya belum siap — bukan tool-nya yang salah.
#
#   4. bash autoreply.sh respond --mode draft --confirm
#      Semua balasan masuk ke folder Drafts. Tidak ada yang terkirim.
#      Jalankan begini SEMINGGU. Baca drafnya tiap pagi. Kamu akan menemukan
#      dua-tiga jawaban yang salah — itu murah sekarang, mahal nanti.
#
#   5. bash autoreply.sh respond --mode faq --confirm
#      Baru kirim otomatis, hanya untuk yang lolos ambang dan tanpa trigger.
#      Sisanya naik ke kamu.
#
#   bash autoreply.sh respond --mode blind --answers-file jawaban.json \
#        --i-understand-blind-mode --confirm
#      Kirim apa adanya tanpa ambang. Bisa. Bacalah peringatannya sekali.
#
#   bash autoreply.sh log --today       apa saja yang sudah dikirim otomatis
#
# Hentikan semuanya kapan saja:  bash scripts/emergency-halt.sh
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${HERMES_EMAIL_CONFIG_DIR:-${HERMES_HOME:-$HOME}/.hermes-email}/config.env"

case "${1:-}" in
  -h|--help|help|"")
    sed -n '2,32p' "$0"
    exit 0
    ;;
esac

if [[ ! -f "$CFG" ]]; then
  echo "Belum ada config di $CFG" >&2
  echo "Jalankan dulu: bash scripts/initialize.sh --email ... --app-password ..." >&2
  exit 1
fi

exec python3 "$SKILL_DIR/scripts/lib/autoresponder.py" "$@"
