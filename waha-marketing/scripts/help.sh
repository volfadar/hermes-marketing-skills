#!/usr/bin/env bash
# help.sh
cat <<HELP
waha-marketing — skill untuk WhatsApp marketing via WAHA
=========================================================

Setup:
  bash initialize.sh --url https://waha.example --key XXX [--session name]

Sehari-hari (read-only, aman):
  bash waha.sh status                         ringkasan akun + health
  bash waha.sh sessions [--all]               semua session
  bash waha.sh me                             info akun saya
  bash waha.sh groups [--limit 10]            list grup
  bash waha.sh group <groupId>                detail grup
  bash waha.sh group-participants <groupId>   anggota grup
  bash waha.sh contacts [--limit 20]          list kontak
  bash waha.sh check-exists <phone>           cek nomor di WhatsApp
  bash waha.sh labels                         list labels (Business)
  bash waha.sh chats [--limit 20]             chat terbaru
  bash waha.sh messages <chatId> [--limit 20] riwayat pesan

Tulis (HARUS --confirm, soft warning selalu):
  bash waha.sh send-seen <chatId> --confirm               mark read
  bash waha.sh send-text <chatId> "text" [--confirm]      kirim 1 pesan
  bash waha.sh label-chat <chatId> <labelId> --confirm    assign label

Broadcast (HUMANIZED, anti-ban, opt-in required):
  bash broadcast-helper.sh --contacts c.csv --templates m.txt --dry-run
  bash broadcast-helper.sh --contacts c.csv --templates m.txt --i-confirm-optin

Diagnostik & safety:
  bash doctor.sh                              full check
  bash emergency-halt.sh                      STOP broadcast yang berjalan

Dokumen di references/:
  anti-ban.md         CARA HINDARI BANNED (baca dulu sebelum broadcast)
  api-reference.md    daftar endpoint lengkap
  broadcast-guide.md  cara bikin broadcast yang sehat
  ethics.md           opt-in, etika, hukum
  examples.md         contoh CSV, template, webhook payload

⚠  INI PRODUKSI. Hanya kirim ke yang opt-in. Baca anti-ban.md.
HELP
