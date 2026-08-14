#!/usr/bin/env bash
# research.sh — cari di seluruh riset yang sudah dikompilasi ke dalam skill ini.
#
# Ini yang membuat Hermes bisa menjawab "kata risetnya gimana soal X?" tanpa
# harus membaca ulang tiga laporan ratusan halaman tiap kali ditanya.
#
#   bash research.sh "postiz"
#   bash research.sh "banned"
#   bash research.sh "AGPL"
#   bash research.sh "instagrapi" --limit 20
#
# Yang dicari: data/*.yaml + references/*.md di dalam skill ini.
#
# Kalau kamu butuh laporan aslinya (bukan ringkasannya), file-nya ada di root
# repo workshop:
#   hermes-openclaw-social-automation-deep-research-2026-08-11.md   (Laporan A)
#   deep-research-social-automation-hermes-openclaw.md              (Laporan C)
#   01-Hermes-OpenClaw-Social-Automation.pdf                        (Laporan B — bahan ajar, bukan sumber)
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

case "${1:-}" in
  -h|--help|help|"")
    sed -n '2,20p' "$0"
    exit 0
    ;;
esac

exec python3 "$SKILL_DIR/lib/advisor.py" search "$@"
