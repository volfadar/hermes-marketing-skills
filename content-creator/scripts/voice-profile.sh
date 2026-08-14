#!/usr/bin/env bash
# voice-profile.sh — extract brand voice from 3-5 existing content samples.
# Saves extracted profile to ~/.hermes/memories/USER.md (or prints for review).
#
# Usage: bash voice-profile.sh <samples-dir> [--print-only]
set -euo pipefail
DIR="${1:-}"
PRINT_ONLY="no"
[[ "${2:-}" == "--print-only" ]] && PRINT_ONLY="yes"

[[ -z "$DIR" || ! -d "$DIR" ]] && {
  echo "Usage: bash voice-profile.sh <samples-dir>"
  echo "  samples-dir = folder with 3-5 .txt/.md files of your existing posts"
  exit 1
}

# Collect samples
SAMPLES=$(ls "$DIR"/*.{txt,md} 2>/dev/null | head -10)
[[ -z "$SAMPLES" ]] && { echo "No .txt/.md samples in $DIR"; exit 1; }
N=$(echo "$SAMPLES" | wc -l)
echo "Found $N samples in $DIR"

# Build a prompt that asks Hermes to extract voice attributes
read -r -d '' PROMPT <<EOF || true
Kamu asisten voice-profile. Baca sampel konten ini dari seorang creator dan ekstrak profil suaranya.

Sampel:
EOF

while IFS= read -r f; do
  PROMPT+="

--- $(basename "$f") ---
$(cat "$f")"
done <<< "$SAMPLES"

PROMPT+="

Ekstrak atribut voice ini (output sebagai bullet points, Bahasa Indonesia):
1. **Tone** (mis. santai, energik, formal, ironis, gentle)
2. **Kosakata khas** (3-5 kata/frase yang sering dipakai)
3. **Kosakata yang dihindari** (jika terlihat — mis. tidak pakai 'revolusioner', 'game-changer')
4. **Struktur kalimat** (pendek/panjang, pertanyaan di akhir, dll)
5. **Penggunaan emoji** (jarang/sedang/banyak, jenis yang dipakai)
6. **CTA khas** (cara mereka ajak engage — soft/hard, contoh)
7. **Sudut pandang** (mis. first-person 'saya', 'kita', impersonal)
8. **Tanda tangan** (sign-off, catchphrase, jika ada)

Output: ringkasan 8 poin di atas, 200-300 kata. Saya akan review dan simpan ke USER.md memory Hermes."

if [[ "$PRINT_ONLY" == "yes" ]]; then
  echo "$PROMPT"
  exit 0
fi

# Run via Hermes
if command -v hermes >/dev/null 2>&1; then
  echo "Running voice extraction via Hermes..."
  hermes chat -q "$PROMPT" 2>&1 | tail -50
  echo ""
  echo "=== Voice profile extracted. Review output above. ==="
  echo "To save to memory (so future content inherits your voice):"
  echo "  1. Copy the 8-point summary"
  echo "  2. Run: hermes"
  echo "  3. Type: 'Save this as my brand voice profile in USER.md:'"
  echo "  4. Paste the summary"
else
  echo "Hermes not found. Here's the prompt to paste manually:"
  echo "================================================================"
  echo "$PROMPT"
fi
