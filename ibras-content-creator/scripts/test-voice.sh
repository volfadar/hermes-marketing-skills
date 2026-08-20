#!/usr/bin/env bash
# test-voice.sh — voice-profile.sh harus menerima tulisan yang benar-benar dimiliki
# orang yang belum pernah posting. SKILL.md sudah menjanjikan itu; skripnya dulu
# menolaknya, dan pengguna sasaran skill ini persis orang yang belum punya postingan.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V="$HERE/voice-profile.sh"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
pass=0; fail=0
ok(){ if [ "$1" = "0" ]; then echo "  ✓ $2"; pass=$((pass+1)); else echo "  ✗ $2"; [ -n "${3:-}" ] && echo "      $3"; fail=$((fail+1)); fi; }

echo "voice-profile.sh — sumber yang dimiliki pemula"

mkdir -p "$TMP/wa"
cat > "$TMP/wa/WhatsApp Chat with Bu Sri.txt" <<'EOF'
20/08/2026 09.12 - Bu Sri: mba keripiknya masih ada?
20/08/2026 09.14 - Aku: masih bu, balado sama original. mau berapa?
EOF
printf '20/08 - Aku: siap bu, sore aku anterin ya\n' > "$TMP/wa/chat-tanpa-ekstensi"

"$V" "$TMP/wa" --print-only >/dev/null 2>&1
ok "$([ $? -eq 0 ] && echo 0 || echo 1)" "menerima export chat WhatsApp sebagai sumber suara" \
   "dulu ditolak: hanya .txt/.md, padahal SKILL.md menyebut chat sebagai sumber sah"

"$V" "$TMP/wa/chat-tanpa-ekstensi" --print-only >/dev/null 2>&1
ok "$([ $? -eq 0 ] && echo 0 || echo 1)" "menerima file teks tanpa ekstensi"

"$V" "$TMP/wa/WhatsApp Chat with Bu Sri.txt" --print-only >/dev/null 2>&1
ok "$([ $? -eq 0 ] && echo 0 || echo 1)" "menerima satu file, bukan cuma folder"

printf 'ready kak, sore aku kirim\n' | "$V" - --print-only >/dev/null 2>&1
ok "$([ $? -eq 0 ] && echo 0 || echo 1)" "menerima teks yang ditempel lewat stdin"

OUT="$("$V" "$TMP/wa" --print-only 2>&1)"
ok "$(printf '%s' "$OUT" | grep -q 'keripiknya masih ada' && echo 0 || echo 1)" \
   "isi chatnya benar-benar masuk ke prompt, bukan cuma nama filenya"

mkdir -p "$TMP/kosong"
"$V" "$TMP/kosong" >/dev/null 2>&1
ok "$([ $? -eq 1 ] && echo 0 || echo 1)" "keluar 1 kalau tidak ada teks sama sekali"
OUT="$("$V" "$TMP/kosong" 2>&1)"
ok "$(printf '%s' "$OUT" | grep -qi 'chat' && echo 0 || echo 1)" \
   "pesan gagalnya menyebut sumber yang dia MUNGKIN punya, bukan cuma 'no samples'"

# binary tidak boleh ikut
printf '\x00\x01\x02binary\x00' > "$TMP/wa/foto.jpg"
OUT="$("$V" "$TMP/wa" --print-only 2>&1)"
ok "$(printf '%s' "$OUT" | grep -q 'foto.jpg' && echo 1 || echo 0)" "melewati file biner"

bash -n "$V" 2>/dev/null && ok 0 "sintaks valid" || ok 1 "sintaks valid"

echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
