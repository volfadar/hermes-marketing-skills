#!/usr/bin/env bash
# tailscale-setup.sh — interactive. Routes cloakserve through the user's OWN phone
# (Tailscale exit node) so public research egresses from a real Indonesian residential IP.
#
# OPTIONAL. Only for research reliability (geo-accurate Indonesia results).
# It is the user's OWN connection on their OWN phone — NOT a purchased proxy, NOT deception.
# ALWAYS ask the human before running. This script double-confirms.
set -euo pipefail

cat <<INTRO
==============================================================
 Tailscale Exit Node — route cloakserve through your own phone
==============================================================

What this does:
  1. Installs Tailscale on this machine.
  2. You install the Tailscale app on your phone (iOS/Android).
  3. Your phone advertises itself as an "exit node".
  4. This machine routes outbound traffic through your phone.
  5. cloakserve browses from your real residential ID IP.

Pros:
  - Riset marketplace/SERP muncul seperti user Indonesia asli.
  - Gratis (Tailscale personal tier). End-to-end encrypted.
  - Ini koneksi MILIK SENDIRI di HP SENDIRI — bukan proxy belian.

Cons:
  - Pakai kuota HP saat aktif (matikan kalau tidak dipakai).
  - Butuh install app Tailscale di HP + akun gratis (~5 menit sekali).
  - Sedikit tambahan latency.

Ethics: ini HANYA untuk riset publik. Tidak untuk bypass login, paywall,
ToS, atau sistem anti-fraud. CloakBrowser + Tailscale = lapisan reliabilitas,
bukan alat penipuan.

INTRO

read -r -p "Lanjut? Ketik 'yes': " ANS
[[ "$ANS" == "yes" ]] || { echo "Dibatalkan. Tidak ada perubahan."; exit 0; }

echo ""
echo "=== Step 1: Install Tailscale di mesin ini ==="
if command -v tailscale >/dev/null 2>&1; then
  echo "tailscale sudah terinstall: $(tailscale version 2>/dev/null | head -1)"
else
  echo "Install via script resmi..."
  curl -fsSL https://tailscale.com/install.sh | sh
fi

echo ""
echo "=== Step 2: Authenticate mesin ini ==="
echo "Buka URL yang muncul di browser, login dengan akun Tailscale kamu."
sudo tailscale up || tailscale up
echo "Mesin ini sekarang di tailnet kamu. IP: $(tailscale ip -4 2>/dev/null || echo '?')"

echo ""
echo "=== Step 3: Setup HP sebagai exit node ==="
cat <<PHONE
Di HP kamu:
  1. Install Tailscale app (iOS: App Store / Android: Play Store).
  2. Login dengan akun yang SAMA.
  3. iOS: Settings -> "Run Exit Node" -> enable.
     Android: menu tiga titik -> "Run as exit node" -> enable.
  4. Di komputer, buka https://login.tailscale.com/admin/machines,
     cari HP kamu, buka setting, APPROVE sebagai exit node.

Setelah di-approve, kamu lihat nama HP kamu di list mesin.
PHONE

echo ""
read -r -p "Paste nama HP di Tailscale (contoh: 'iphone-andi') atau kosongkan untuk list: " PHONE
if [[ -z "$PHONE" ]]; then
  echo "=== Mesin di tailnet kamu ==="
  tailscale status | tail -n +2
  read -r -p "Nama HP: " PHONE
fi
[[ -z "$PHONE" ]] && {
  echo "Tidak ada nama HP — skip aktivasi. Nanti bisa jalankan:"
  echo "  sudo tailscale up --exit-node=<nama-hp>"
  exit 0
}

echo ""
echo "=== Step 4: Route traffic mesin ini lewat HP ==="
sudo tailscale up --accept-routes --exit-node="${PHONE}" || \
  tailscale up --accept-routes --exit-node="${PHONE}"

echo ""
echo "=== Verifikasi ==="
EGRESS=$(curl -s --max-time 8 https://api.ipify.org 2>/dev/null || echo "?")
echo "IP egress sekarang: ${EGRESS}  (harus IP residensial Indonesia HP kamu)"

echo ""
echo "Selesai. Restart cloakserve supaya browser pakai route baru:"
echo "  bash $(dirname "$0")/stop.sh && bash $(dirname "$0")/start.sh"
echo ""
echo "Untuk MEMATIKAN exit node nanti:"
echo "  sudo tailscale up --exit-node="
