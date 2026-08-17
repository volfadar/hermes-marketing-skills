#!/usr/bin/env bash
# sync-from-source.sh — tarik skill terbaru dari repo pengembangan (workshop),
# bersihkan, lalu audit. Jalankan setiap kali skill berubah di sumber.
#
#   bash installer/sync-from-source.sh [/path/ke/hermes-for-marketing]
#
# Asumsi sumber: folder berisi skill-<nama>/ + shared/sync.sh yang sudah
# dijalankan (`bash shared/sync.sh` di sumber supaya salinan di dalam tiap
# skill segar). Setelah sinkron, README disesuaikan ke layout repo ini
# (tanpa prefiks skill-), lalu audit.sh menjadi gerbang terakhir.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${1:-$HOME/hermes-for-marketing}"

[[ -d "$SRC/shared" ]] || { echo "ERROR: $SRC bukan repo pengembangan (tidak ada shared/)" >&2; exit 1; }

( cd "$SRC" && bash shared/sync.sh --check >/dev/null \
  ) || { echo "ERROR: skill di sumber melenceng dari shared/ — jalan 'bash shared/sync.sh' di $SRC dulu." >&2; exit 1; }

for d in "$SRC"/skill-*/; do
  name="$(basename "$d")"; name="${name#skill-}"
  rm -rf "$HERE/$name.new"
  cp -R "$d" "$HERE/$name.new"
  find "$HERE/$name.new" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
  find "$HERE/$name.new" -name '*.pyc' -delete 2>/dev/null || true
  rm -rf "$HERE/$name" && mv "$HERE/$name.new" "$HERE/$name"
  echo "  ✓ $name"
done

# Sesuaikan instruksi install di README ke layout repo ini
python3 - <<'PY'
import re, pathlib
for readme in sorted(pathlib.Path('.').glob('*/README.md')):
    t = readme.read_text()
    t2 = re.sub(r'cp -[Rr] skill-([a-z-]+) ~/\.hermes/skills/\1', r'cp -R \1 ~/.hermes/skills/\1', t)
    t2 = t2.replace('hermes skills install https://github.com/<user>/skill-',
                    'hermes skills install <user>/hermes-marketing-skills/')
    if t2 != t:
        readme.write_text(t2)
        print('  ✓ README disesuaikan:', readme)
PY

python3 "$HERE/installer/update-hermes-manifests.py"
python3 "$HERE/installer/test-hermes-marketplace.py"
bash "$HERE/installer/audit.sh"
echo
echo "Sinkron selesai; manifest, kontrak Hermes Hub, dan audit lulus."
echo "Commit perubahan, lalu bangun bundel: bash installer/make-bundle.sh"
