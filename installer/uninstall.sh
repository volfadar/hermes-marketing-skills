#!/usr/bin/env bash
# uninstall.sh — hapus skill pemasaran dari Hermes home.
#
#   bash installer/uninstall.sh                  # hapus semua 7
#   bash installer/uninstall.sh --only email-marketing
#   bash installer/uninstall.sh --home /path/hermes
#
# Yang TIDAK disentuh: ~/.hermes/business/ (profile.yaml, FAQ, log kamu),
# config.yaml, dan hook artifact-guard kalau pernah dipasang --with-guard.
# Hook bisa dibiarkan (tidak berbuat apa-apa tanpa skill) atau dibuang
# manual dari blok `hooks:` di config.yaml.
set -euo pipefail

SKILLS=(brand-strategy-coach cloakserve-research content-creator
        email-marketing marketing-orchestrator social-publishing
        waha-marketing)

HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
ONLY=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --only) IFS=',' read -ra ONLY <<< "$2"; shift 2 ;;
    --home) HOME_DIR="$2"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "argumen tidak dikenal: $1" >&2; exit 2 ;;
  esac
done

SELECTED=()
if [[ ${#ONLY[@]} -gt 0 ]]; then
  for want in "${ONLY[@]}"; do
    SELECTED+=("${want#skill-}")
  done
else
  SELECTED=("${SKILLS[@]}")
fi

removed=0
for s in "${SELECTED[@]}"; do
  if [[ -d "$HOME_DIR/skills/$s" ]]; then
    rm -rf "$HOME_DIR/skills/$s"
    echo "  ✓ $s — dihapus"
    removed=$((removed+1))
  else
    echo "  - $s — tidak ada (sudah bersih)"
  fi
done

echo
echo "$removed skill dihapus dari $HOME_DIR/skills/"
[[ -d "$HOME_DIR/business" ]] && echo "Data bisnismu di $HOME_DIR/business/ tidak disentuh."
