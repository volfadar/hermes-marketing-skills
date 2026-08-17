#!/usr/bin/env bash
# status.sh — empat perintah yang harus dijalankan di awal TIAP sesi marketing.
#
# Ini yang membedakan "sesi kedua" dari "sesi pertama lagi". Dua puluh tiga sesi
# eval semuanya cold start; tidak satu pun menguji pemiliknya datang lagi besok
# pagi — padahal sesi itulah yang menentukan ini alat atau cuma demo.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB="$HERE/lib"

hr() { printf '%*s\n' 62 '' | tr ' ' '─'; }

echo "REM"
hr
if bash "$HERE/halt.sh" status 2>/dev/null; then :; else
  echo ""
  echo "  ⚠ Ada yang sedang dihentikan. Sebut ini ke pemiliknya SEBELUM"
  echo "    merencanakan apa pun yang perlu dikirim."
fi

echo ""
echo "YANG SUDAH DIKETAHUI (jangan ditanya ulang)"
hr
python3 "$LIB/profile.py" show 2>/dev/null || echo "  (profil belum ada — mulai dari fakta & harga)"

echo ""
echo "YANG BELUM SELESAI DARI SESI LALU"
hr
python3 "$LIB/ledger.py" open 2>/dev/null || echo "  kosong"

echo ""
echo "YANG SEDANG MENUNGGU DIJAWAB"
hr
python3 "$LIB/handoff.py" list 2>/dev/null || echo "  kosong"

echo ""
echo "KERJA TERJADWAL"
hr
python3 "$LIB/watch.py" list 2>/dev/null || echo "  kosong"

echo ""
hr
echo "Mulai dari orang yang menunggu, bukan dari konten ke 200 orang."
