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

# Gerbang: regenerasi manifest Hub, uji kontrak, lalu audit kebocoran.
python3 "$ROOT/installer/update-hermes-manifests.py"
python3 "$ROOT/installer/test-hermes-marketplace.py"
bash "$ROOT/installer/audit.sh"

mkdir -p "$DIST" "$STAGE/$NAME"

for s in ibras-brand-strategy-coach ibras-cloakserve-research ibras-content-creator \
         ibras-email-marketing ibras-marketing-orchestrator ibras-social-publishing ibras-waha-marketing; do
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
if command -v zip >/dev/null 2>&1; then
  ( cd "$STAGE" && zip -qr "$DIST/$NAME.zip" "$NAME" )
else
  python3 - "$STAGE" "$DIST/$NAME.zip" "$NAME" <<'PY'
import os, sys, zipfile
stage, out, name = sys.argv[1], sys.argv[2], sys.argv[3]
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _dirs, files in os.walk(os.path.join(stage, name)):
        for f in sorted(files):
            full = os.path.join(root, f)
            z.write(full, os.path.relpath(full, stage))
PY
fi

if command -v sha256sum >/dev/null 2>&1; then
  ( cd "$DIST" && sha256sum "$NAME.zip" > "$NAME.zip.sha256" )
elif command -v shasum >/dev/null 2>&1; then
  ( cd "$DIST" && shasum -a 256 "$NAME.zip" > "$NAME.zip.sha256" )
fi

size=$(du -h "$DIST/$NAME.zip" | cut -f1)
echo "Bundel: $DIST/$NAME.zip ($size, 7 skill)"
echo "Bagikan file zip ini ke peserta (WhatsApp / Drive / USB)."
