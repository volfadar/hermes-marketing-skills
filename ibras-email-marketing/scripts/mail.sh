#!/usr/bin/env bash
# mail.sh — wrapper tipis untuk scripts/lib/mailbox.py. Ini pintu masuk sehari-hari.
#
# BACA (aman, tidak mengubah apa pun):
#   bash mail.sh stats                          ringkasan semua folder
#   bash mail.sh folders                        daftar folder/label
#   bash mail.sh list --unread --limit 20       yang belum dibaca
#   bash mail.sh list --from klien@x.com        dari orang tertentu
#   bash mail.sh read 12345                     baca satu email lengkap
#   bash mail.sh search "from:tokopedia newer_than:7d"   sintaks Gmail
#   bash mail.sh thread 12345                   seluruh percakapan
#
# TULIS (DRY RUN dulu; tambahkan --confirm untuk benar-benar jalan):
#   bash mail.sh draft --to a@b.com --subject "Halo" --body-file d.txt --confirm
#   bash mail.sh reply 12345 --body-file balasan.txt --confirm
#   bash mail.sh send --to a@b.com --subject "Penawaran" --body-file p.txt --confirm
#   bash mail.sh forward 12345 --to tim@kantor.com --confirm
#   bash mail.sh mark 12345 --read --confirm
#   bash mail.sh label 12345 --add "Klien/2026" --confirm
#   bash mail.sh move 12345 --to "Arsip" --confirm
#   bash mail.sh archive 12345 --confirm        keluar dari INBOX, tidak hilang
#   bash mail.sh trash 12345 --confirm          ke Trash, bisa dikembalikan
#   bash mail.sh restore 12345 --confirm        kembalikan dari Trash
#   bash mail.sh delete 12345 --permanent --confirm    TIDAK ADA UNDO
#
# Tambahkan --json ke perintah baca kalau outputnya untuk diproses Hermes.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${HERMES_EMAIL_CONFIG_DIR:-$HOME/.hermes-email}/config.env"

case "${1:-}" in
  -h|--help|help|"")
    sed -n '2,30p' "$0"
    exit 0
    ;;
esac

if [[ ! -f "$CFG" ]]; then
  echo "Belum ada config di $CFG" >&2
  echo "Jalankan dulu: bash scripts/initialize.sh --email ... --app-password ..." >&2
  exit 1
fi

exec python3 "$SKILL_DIR/scripts/lib/mailbox.py" "$@"
