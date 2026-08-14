#!/usr/bin/env bash
# help.sh — apa yang bisa dikerjakan skill ini, dalam satu layar.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cat <<'TXT'
email-marketing — kirim, baca, dan balas email lewat Gmail SMTP/IMAP

  Kenapa Gmail dan bukan alat lain: Repliz (alat komentar sosial yang kita pakai)
  TIDAK menyentuh email sama sekali. Jadi jalur email tetap di sini.

MULAI
  bash scripts/initialize.sh        pasang kredensial & cek koneksi
  bash scripts/doctor.sh            periksa semuanya siap

KERJA HARIAN
  bash scripts/mail.sh list         apa yang masuk
  bash scripts/mail.sh read <uid>   baca satu
  bash scripts/mail.sh send ...     kirim (butuh --confirm)
  bash scripts/mail.sh reply <uid>  balas satu

BALASAN OTOMATIS — bertahap, jangan langsung penuh
  bash scripts/autoreply.sh --mode draft   minggu pertama: semua masuk review kamu
  bash scripts/autoreply.sh --mode faq     cuma yang jawabannya sudah kamu tulis
  python3 lib/handoff.py list              antrean yang perlu kamu jawab sekali
  python3 lib/handoff.py answer 1 --text "..."   jawab, lalu masuk FAQ

REM DARURAT — satu perintah untuk SEMUA jalur (email, WhatsApp, job terjadwal)
  bash scripts/halt.sh on --why "alasan"
  bash scripts/halt.sh status
  bash scripts/halt.sh off

SEBELUM MENGIRIM APA PUN
  python3 lib/copycheck.py <draft>          lolos uji tukar?
  python3 scripts/check-numbers.py <draft>  tiap angka ada asalnya?

BACA DULU
  references/hermes-discipline.md   aturan yang tidak bisa ditawar
  references/hermes-runtime.md      apa yang Hermes sendiri sudah sediakan
  references/automation-posture.md  sikap soal otomasi & garis merah
  references/deliverability.md      supaya tidak masuk spam
TXT
