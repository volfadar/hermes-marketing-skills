#!/usr/bin/env bash
# voice-profile.sh — extract brand voice from 3-5 existing content samples.
# Saves extracted profile to ~/.hermes/memories/USER.md (or prints for review).
#
# Usage: bash voice-profile.sh <samples-dir> [--print-only]
set -euo pipefail
SRC="${1:-}"
PRINT_ONLY="no"
[[ "${2:-}" == "--print-only" ]] && PRINT_ONLY="yes"

usage() {
  cat <<'TXT'
Usage: bash voice-profile.sh <folder | file | ->

  folder   berisi tulisanmu (ekstensi apa pun, asal teks)
  file     satu file saja juga boleh
  -        tempel teksnya langsung, akhiri dengan Ctrl-D

Sumber yang dipakai, dari yang paling kaya ke yang paling seadanya:
  1. postingan lama                  .txt .md .html — kalau ada
  2. export chat WhatsApp            Chat > Ekspor chat > Tanpa media
  3. transkrip voice note            .vtt .srt, atau ketik ulang seadanya
  4. balasanmu ke pelanggan          copy-paste 10-20 chat terakhir
  5. caption yang pernah kamu tulis  walau cuma tiga

Belum pernah posting sama sekali bukan penghalang — nomor 2 sampai 4 itu tulisanmu
juga, dan justru lebih jujur daripada caption yang sudah dipoles.
TXT
}

[[ -z "$SRC" ]] && { usage; exit 1; }

TMP_IN=""
# Harus selalu balik 0: perintah terakhir di dalam trap menentukan exit code
# skripnya, jadi `[[ -n "" ]]` di sini diam-diam mengubah sukses jadi gagal.
cleanup() { [[ -n "$TMP_IN" ]] && rm -rf "$TMP_IN"; return 0; }
trap cleanup EXIT

if [[ "$SRC" == "-" ]]; then
  TMP_IN="$(mktemp -d)"
  cat > "$TMP_IN/tempelan.txt"
  [[ -s "$TMP_IN/tempelan.txt" ]] || { echo "Tidak ada teks yang ditempel."; exit 1; }
  SRC="$TMP_IN"
fi

if [[ -f "$SRC" ]]; then
  SAMPLES="$SRC"
elif [[ -d "$SRC" ]]; then
  # Terima file teks apa pun, bukan cuma .txt/.md. Versi lama menolak export chat
  # WhatsApp dan transkrip voice note — padahal SKILL.md sendiri menyebut keduanya
  # sebagai sumber yang sah, dan bagi orang yang belum pernah posting itulah satu-
  # satunya tulisan yang dia punya.
  SAMPLES="$(find "$SRC" -maxdepth 1 -type f -size -2M 2>/dev/null \
    | while IFS= read -r f; do
        case "$(basename "$f")" in .*) continue ;; esac
        if file -b --mime-type "$f" 2>/dev/null | grep -qE '^text/|json|xml'; then echo "$f"
        elif LC_ALL=C grep -qIm1 . "$f" 2>/dev/null; then echo "$f"; fi
      done | head -10)"
else
  echo "Bukan file atau folder: $SRC"; echo; usage; exit 1
fi

if [[ -z "$SAMPLES" ]]; then
  echo "Tidak ada teks yang bisa dibaca di: $SRC"
  echo
  usage
  exit 1
fi
N=$(echo "$SAMPLES" | wc -l)
echo "Ketemu $N sumber teks"
[[ "$N" -lt 3 ]] && echo "  (cuma $N — profilnya jadi kasar. 3-5 lebih baik, tapi tetap jalan.)"

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
