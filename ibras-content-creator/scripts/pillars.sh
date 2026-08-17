#!/usr/bin/env bash
# pillars.sh — set 3-5 content pillars. Saves to ~/.content-creator/pillars.json
# Usage: bash pillars.sh "pillar1, pillar2, pillar3"
set -euo pipefail
INPUT="${1:-}"
[[ -z "$INPUT" ]] && {
  echo "Usage: bash pillars.sh \"pillar1, pillar2, pillar3\""
  echo ""
  echo "Content pillars = 3-5 tema utama yang brand kamu ingin dikenal."
  echo "Contoh (kopi specialty): \"kopi specialty, manual brew pemula, behind the scenes, tips hemat\""
  exit 1
}

CFG_DIR="${CONTENT_CREATOR_DIR:-$HOME/.content-creator}"
mkdir -p "$CFG_DIR"

# Parse comma-separated
python3 - "$INPUT" "$CFG_DIR/pillars.json" <<'PY'
import sys, json
raw, path = sys.argv[1], sys.argv[2]
pillars = [p.strip() for p in raw.split(",") if p.strip()]
if len(pillars) < 3 or len(pillars) > 7:
    print(f"⚠️  {len(pillars)} pillars (idealnya 3-5). Lanjut tapi pertimbangkan reduksi.", file=sys.stderr)
data = {"pillars": pillars, "set_at": __import__("datetime").datetime.now().isoformat()}
with open(path, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"✓ {len(pillars)} pillars saved to {path}:")
for i, p in enumerate(pillars, 1):
    print(f"  {i}. {p}")
PY

echo ""
echo "Next: bash scripts/ideate.sh --week --platform instagram"
