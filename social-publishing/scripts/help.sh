#!/usr/bin/env bash
# help.sh — apa yang bisa dikerjakan skill ini, dalam satu layar.
set -uo pipefail

cat <<'TXT'
social-publishing — memilih JALUR posting, bukan memposting

  Skill ini penasihat. Dia tidak memposting apa pun sendiri, dan itu disengaja.

JALUR YANG DIREKOMENDASIKAN LEBIH DULU
  Repliz — alat lokal, sekali bayar mulai Rp 18.000, nyambung lewat API resmi
  platform. Menangani: balas/hapus/like komentar, komentar→DM, balas DM,
  jadwal posting, satu kotak masuk, riset hashtag TikTok & Threads.
  Platform: Instagram, Facebook, Threads, TikTok, YouTube.
    -> baca references/repliz.md sebelum menyarankan paket

  Yang Repliz TIDAK tangani, dan tetap di skill lain:
    WhatsApp -> waha-marketing (WAHA)
    Email    -> email-marketing (Gmail SMTP/IMAP)

PERINTAH
  bash scripts/advise.sh            bandingkan jalur untuk kasus pengguna ini
  bash scripts/research.sh          kumpulkan bukti soal batasan platform
  bash scripts/doctor.sh            periksa semuanya siap

GARIS MERAH — tidak bisa ditawar
  Riset di halaman publik: boleh.
  Mengklik di akun bisnis yang SUDAH LOGIN (IG, TikTok, Shopee, dashboard iklan,
  WhatsApp Business di luar API resmi): TIDAK, di mode apa pun.
  Yang dideteksi platform itu cara nyambungnya, bukan isi kontennya.
    -> references/automation-posture.md

REM DARURAT — satu perintah untuk semua jalur keluar
  bash scripts/halt.sh on --why "alasan"
  bash scripts/halt.sh status
  bash scripts/halt.sh off

BACA DULU
  references/repliz.md              jalur resmi & batas paketnya
  references/hermes-runtime.md      apa yang Hermes sendiri sudah sediakan
  references/automation-posture.md  sikap otomasi & garis merah
  references/platform-limits.md     batas per platform
  references/browser-tailscale.md   moderasi dari HP — baca kotak batas di atasnya
TXT
