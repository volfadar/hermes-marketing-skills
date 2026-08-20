#!/usr/bin/env bash
# smtp.sh — guided Gmail App Password setup for ibras-email-marketing.
# The password is read with hidden input and passed via env. It never appears
# on a command line, because argv is visible to every process on the machine.
set -uo pipefail

SK="${HERMES_HOME:-$HOME/.hermes}/skills"
INIT="$SK/ibras-email-marketing/scripts/initialize.sh"
[[ -f "$INIT" ]] || { echo "✗ ibras-email-marketing belum terpasang."; exit 1; }

cat <<'TXT'
Gmail App Password — 16 digit, bukan password akunmu.

  1. nyalakan 2FA:            https://myaccount.google.com/security
  2. buat App Password:       https://myaccount.google.com/apppasswords
  3. salin 16 karakternya (spasi boleh ikut, nanti dibuang)

Kalau akunmu Google Workspace dan menu App Password tidak muncul, adminnya
mematikan fitur itu — minta admin, atau pakai SMTP lain.
TXT

read -r -p $'\nAlamat Gmail: ' EMAIL
[[ -n "$EMAIL" ]] || { echo "✗ email kosong"; exit 1; }
read -r -s -p "App Password (tidak akan tampil): " APP_PW; echo
APP_PW="${APP_PW// /}"
[[ ${#APP_PW} -eq 16 ]] || echo "  ⚠ panjangnya ${#APP_PW}, biasanya 16 — lanjut saja, verifikasi di bawah yang menentukan"

EMAIL="$EMAIL" APP_PASSWORD="$APP_PW" bash "$INIT" --email "$EMAIL" --app-password "$APP_PW"
rc=$?
unset APP_PW
[[ $rc -eq 0 ]] && echo "✓ selesai — cek: bash $SK/ibras-email-marketing/scripts/doctor.sh" \
                || echo "✗ initialize gagal (rc=$rc). Password salah, atau 2FA belum aktif."
exit $rc
