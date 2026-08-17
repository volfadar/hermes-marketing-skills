#!/usr/bin/env bash
# help.sh — apa yang dikerjakan skill ini, dalam satu layar.
set -uo pipefail

cat <<'TXT'
ibras-marketing-orchestrator — memutuskan skill mana yang jalan, dan urutannya

  Skill ini TIDAK menulis, TIDAK meriset, TIDAK mengirim. Begitu kamu sedang
  menulis copy, kamu sudah keluar dari skill ini.

LANGKAH PERTAMA, SELALU
  bash scripts/status.sh        rem · profil · yang belum selesai · antrean · job

RUTE
  belum ada harga di `fakta`        -> ibras-brand-strategy-coach Stage 1 (90 detik)
  ada produk, copy-nya generik      -> ibras-brand-strategy-coach Stage 2b saja (~15 mnt)
  benar-benar memilih arah          -> positioning lab penuh (sebut kalau ini yang dipakai)
  butuh bukti dari luar             -> ibras-cloakserve-research (halaman publik saja)
  komentar/DM/jadwal IG·FB·TikTok·YT·Threads -> Repliz (dibeli, bukan dibangun)
  WhatsApp                          -> ibras-waha-marketing (Repliz tidak menyentuh WA)
  email                             -> ibras-email-marketing (Repliz tidak menyentuh email)
  mau jalan sendiri tiap pagi       -> python3 scripts/lib/watch.py create
  datang lagi besok pagi            -> python3 scripts/lib/ledger.py open

SEBELUM MENULIS SCRIPT APA PUN — urutan ini wajib
  1. Hermes sudah punya?   penjadwal, notepad, monitor-mode, biaya, kartu izin
  2. Alat yang sudah dibayar sudah punya?   Repliz: komentar, DM, jadwal, inbox
  3. Baru bangun sendiri.

MENUTUP SESI — selalu sama
  python3 scripts/lib/ledger.py show     apa yang jam ini hasilkan
  satu NAMA untuk besok          bukan daftar tugas
  satu baris panen               "tadi 3 orang nanya halal — aku catat ya"

BACA DULU
  references/hermes-discipline.md   sembilan aturan, tidak bisa ditawar
  references/hermes-runtime.md      apa yang host-nya sudah sediakan
  references/tools-mapping.md       tool mana untuk pekerjaan mana
  references/repliz.md              jalur resmi komentar/DM/jadwal
  references/automation-posture.md  sikap otomasi & garis merah computer-use
TXT
