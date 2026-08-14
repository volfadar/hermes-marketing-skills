#!/usr/bin/env bash
# install.sh — pasang skill pemasaran Hermes ke Hermes home mana pun.
#
# Di repo ini nama folder sudah = nama skill, jadi cukup disalin.
# (Di repo pengembangan folder bernama `skill-<nama>`; Hermes hanya
# menemukan skill tanpa prefiks itu. Installer ini yang menjaga
# konsistensinya di sini.)
#
#   bash installer/install.sh                      # pasang semua 7 skill
#   bash installer/install.sh --only email-marketing,social-publishing
#   bash installer/install.sh --list               # daftar + status
#   bash installer/install.sh --home /path/hermes  # Hermes home lain
#   bash installer/install.sh --with-guard         # pasang juga artifact-guard hook
#
# Idempoten: jalan ulang = update (versi lama diganti, data di
# ~/.hermes/business tidak pernah disentuh).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS=(brand-strategy-coach cloakserve-research content-creator
        email-marketing marketing-orchestrator social-publishing
        waha-marketing)

HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
ONLY=()
WITH_GUARD=0
MODE=install

die() { echo "ERROR: $*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --only)       IFS=',' read -ra ONLY <<< "$2"; shift 2 ;;
    --home)       HOME_DIR="$2"; shift 2 ;;
    --list)       MODE=list; shift ;;
    --with-guard) WITH_GUARD=1; shift ;;
    -h|--help)    sed -n '2,14p' "$0"; exit 0 ;;
    *)            die "argumen tidak dikenal: $1 (lihat --help)" ;;
  esac
done

installed() { [[ -d "$HOME_DIR/skills/$1" ]]; }

if [[ "$MODE" == list ]]; then
  printf "%-24s %-9s %s\n" "SKILL" "STATUS" "DESKRIPSI"
  for s in "${SKILLS[@]}"; do
    desc=$(awk '/^description:/{sub(/^description: */,""); print; exit}' "$ROOT/$s/SKILL.md" | cut -c1-60)
    if installed "$s"; then st="terpasang"; else st="-"; fi
    printf "%-24s %-9s %s…\n" "$s" "$st" "$desc"
  done
  exit 0
fi

SELECTED=()
if [[ ${#ONLY[@]} -gt 0 ]]; then
  for want in "${ONLY[@]}"; do
    want="${want#skill-}"
    [[ " ${SKILLS[*]} " == *" $want "* ]] || die "skill tidak dikenal: $want (pilihan: ${SKILLS[*]})"
    SELECTED+=("$want")
  done
else
  SELECTED=("${SKILLS[@]}")
fi

[[ -d "$HOME_DIR" ]] || [[ "$(basename "$HOME_DIR")" == ".hermes" ]] \
  || die "$HOME_DIR bukan tampak seperti Hermes home. Pakai --home <dir> yang benar."
mkdir -p "$HOME_DIR/skills"

ok=0
for s in "${SELECTED[@]}"; do
  src="$ROOT/$s"
  dst="$HOME_DIR/skills/$s"
  [[ -f "$src/SKILL.md" ]] || { echo "  ✗ $s: SKILL.md tidak ada di $src"; continue; }
  rm -rf "$dst.new"
  cp -R "$src" "$dst.new"
  find "$dst.new" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
  find "$dst.new" -name '*.pyc' -delete 2>/dev/null || true
  chmod +x "$dst.new"/scripts/* 2>/dev/null || true
  chmod +x "$dst.new"/hooks/*   2>/dev/null || true
  if installed "$s"; then verb="diperbarui"; else verb="terpasang"; fi
  rm -rf "$dst" && mv "$dst.new" "$dst"
  echo "  ✓ $s — $verb"
  ok=$((ok+1))
done
[[ $ok -gt 0 ]] || die "tidak ada skill yang terpasang"

# Verifikasi lewat Hermes sendiri kalau binary-nya ada
if command -v hermes >/dev/null 2>&1; then
  missing=0
  for s in "${SELECTED[@]}"; do
    if ! HERMES_HOME="$HOME_DIR" hermes skills list 2>/dev/null | grep -q "$s"; then
      echo "  ✗ $s tidak terlihat oleh 'hermes skills list'" >&2
      missing=$((missing+1))
    fi
  done
  [[ $missing -eq 0 ]] && echo "Verifikasi: $ok skill terlihat di 'hermes skills list'."
else
  echo "Catatan: 'hermes' tidak ada di PATH — lewati verifikasi otomatis."
fi

# pyyaml dibutuhkan lib/profile.py (fail-open tanpa itu, tapi lebih baik ada)
if ! python3 -c "import yaml" >/dev/null 2>&1; then
  echo "Saran: pip3 install pyyaml  (untuk membaca profile.yaml)"
fi

if [[ $WITH_GUARD -eq 1 ]]; then
  guard="$ROOT/marketing-orchestrator/scripts/install-guard.sh"
  if [[ -f "$guard" ]]; then
    HOME_DIR="$HOME_DIR" bash "$guard" --home "$HOME_DIR" \
      || echo "  ! artifact-guard gagal dipasang — skill tetap jalan, hanya tanpa hook" >&2
  fi
else
  echo "Opsional: jalan ulang dengan --with-guard untuk pasang hook artifact-guard."
fi

echo
echo "Selesai: $ok skill di $HOME_DIR/skills/"
echo "Coba:    hermes -z 'Aku jual kue lapis lewat WhatsApp, mau mulai jualan lagi setelah 6 bulan rehat. Mulai dari mana?'"
echo "Panduan lengkap + prompt siap-tempel: README.md"
