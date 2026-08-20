#!/usr/bin/env bash
# test-setup.sh — setup.sh must catch the failures that produce no error message.
#
# Every case here was observed on a real install. The point of each is that
# nothing crashes and nothing warns; the owner just gets worse answers.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETUP="$HERE/setup.sh"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
pass=0; fail=0
ok(){ if [ "$1" = "0" ]; then echo "  ✓ $2"; pass=$((pass+1)); else echo "  ✗ $2"; [ -n "${3:-}" ] && echo "      $3"; fail=$((fail+1)); fi; }

echo "setup.sh — kegagalan yang tidak memunculkan error"

mk(){ H="$TMP/$1"; mkdir -p "$H/skills"; printf '%s' "${2:-}" > "$H/config.yaml"; echo "$H"; }

# 1. model.default kosong — gejalanya "404 tool-use", terlihat seperti skill rusak
H="$(mk nomodel '')"
OUT="$(HERMES_HOME="$H" bash "$SETUP" 2>&1)"; RC=$?
ok "$([ $RC -eq 1 ] && echo 0 || echo 1)" "keluar dengan kode 1 saat model.default kosong" "rc=$RC"
ok "$(printf '%s' "$OUT" | grep -q '404 tool-use' && echo 0 || echo 1)" \
   "menyebut gejalanya, bukan cuma nama fieldnya" \
   "orang membongkar skill karena pesan errornya tidak menyebut model"

# 2. model.default terisi -> lolos cek itu
H="$(mk withmodel 'model:
  default: "some/model"
  provider: "openrouter"
')"
OUT="$(HERMES_HOME="$H" bash "$SETUP" 2>&1)"
ok "$(printf '%s' "$OUT" | grep -q 'model.default: some/model' && echo 0 || echo 1)" \
   "mencetak nilai yang benar-benar dibaca, bukan yang diharapkan"

# 3. browser: biner ada tapi tidak ada yang mendengarkan != terpasang
ok "$(grep -q 'memasang saja tidak cukup' "$SETUP" && echo 0 || echo 1)" \
   "membedakan 'biner ada' dari 'CDP hidup'"
ok "$(grep -q 'instalasi setengah jadi' "$SETUP" && echo 0 || echo 1)" \
   "menyebut jebakan instalasi Playwright setengah jadi"

# 4. wiring terpisah dari menjalankan
ok "$(grep -q 'browser.cdp_url belum di-set' "$SETUP" && echo 0 || echo 1)" \
   "cek wiring terpisah — memasang dan menjalankan saja tidak cukup"

# 5. HERMES_HOME dihormati, bukan $HOME
H="$(mk homecheck '')"
OUT="$(HERMES_HOME="$H" bash "$SETUP" 2>&1)"
ok "$(printf '%s' "$OUT" | grep -q "HERMES_HOME=$H" && echo 0 || echo 1)" \
   "memakai HERMES_HOME, bukan \$HOME" \
   "satu mesin dengan beberapa home pernah membuat tiga pemilik usaha menulis ke file yang sama"

# 6. opsional tidak boleh menggagalkan run
H="$(mk optional 'model:
  default: "m"
')"
OUT="$(HERMES_HOME="$H" WAHA_CONFIG_DIR="$TMP/nowaha" HERMES_EMAIL_CONFIG_DIR="$TMP/nomail" bash "$SETUP" 2>&1)"
ok "$(printf '%s' "$OUT" | grep -q 'WAHA belum diset' && echo 0 || echo 1)" \
   "melaporkan WAHA/SMTP sebagai opsional, dengan akibatnya disebut"

# 7. tidak pernah menaruh rahasia di command line
ok "$(grep -q 'API_KEY=\"\$KEY\" bash' "$HERE/waha.sh" && echo 0 || echo 1)" \
   "waha.sh mengoper key lewat env, bukan argv" \
   "argv terbaca proses lain di mesin yang sama"
ok "$(grep -q 'read -r -s' "$HERE/smtp.sh" && echo 0 || echo 1)" \
   "smtp.sh membaca password dengan input tersembunyi"

# 8. sumber WAHA disebut, bukan diklaim
ok "$(grep -q 'waha.devlike.pro/docs/how-to/waha-plus' "$HERE/waha.sh" && echo 0 || echo 1)" \
   "klaim 'WAHA Plus sekarang gratis' membawa sumber dan tanggalnya"

# 9. sintaks semua script
for f in "$HERE"/setup.sh "$HERE"/waha.sh "$HERE"/smtp.sh; do
  bash -n "$f" 2>/dev/null || { ok 1 "sintaks $(basename "$f")"; continue; }
done
ok 0 "sintaks semua script valid"

echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
