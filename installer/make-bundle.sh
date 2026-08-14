#!/usr/bin/env bash
# make-bundle.sh — bangun zip distribusi untuk peserta workshop.
#
#   bash installer/make-bundle.sh
#   → dist/hermes-marketing-skills-YYYYMMDD.zip (+ .sha256)
#
# Isi zip: folder hermes-marketing-skills/ berisi 7 skill, installer
# (install/uninstall saja), dan README.md. Alat maintainer (audit,
# sync-from-source, make-bundle, MAINTENANCE.md) tidak ikut — peserta
# tidak membutuhkannya.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(date +%Y%m%d)"
NAME="hermes-marketing-skills-$VERSION"
DIST="$ROOT/dist"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# Gerbang: jangan pernah membungkus repo yang bocor.
bash "$ROOT/installer/audit.sh"

mkdir -p "$DIST" "$STAGE/$NAME"

for s in brand-strategy-coach cloakserve-research content-creator \
         email-marketing marketing-orchestrator social-publishing waha-marketing; do
  cp -R "$ROOT/$s" "$STAGE/$NAME/$s"
done
mkdir -p "$STAGE/$NAME/installer"
cp "$ROOT/installer/install.sh" "$ROOT/installer/uninstall.sh" "$STAGE/$NAME/installer/"
cp "$ROOT/README.md" "$STAGE/$NAME/"

find "$STAGE" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
find "$STAGE" -name '*.pyc' -delete 2>/dev/null || true
find "$STAGE/$NAME" -path '*/scripts/*' -type f -exec chmod +x {} +
find "$STAGE/$NAME" -path '*/hooks/*' -type f -exec chmod +x {} +
chmod +x "$STAGE/$NAME/installer/"*.sh

rm -f "$DIST/$NAME.zip"
( cd "$STAGE" && zip -qr "$DIST/$NAME.zip" "$NAME" )

if command -v sha256sum >/dev/null 2>&1; then
  ( cd "$DIST" && sha256sum "$NAME.zip" > "$NAME.zip.sha256" )
fi

size=$(du -h "$DIST/$NAME.zip" | cut -f1)
echo "Bundel: $DIST/$NAME.zip ($size, 7 skill)"
echo "Bagikan file zip ini ke peserta (WhatsApp / Drive / USB)."
