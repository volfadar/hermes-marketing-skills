# Browser di VPS + Tailscale — moderasi dari HP

> ## ⚠️ Batas yang berlaku sejak Agustus 2026 — baca sebelum lanjut
>
> **Browser di halaman ini untuk KAMU.** Layar yang kamu buka dari HP, dan kamu
> yang mengklik. **Ini bukan browser untuk agen.**
>
> Sejak Juli–Agustus 2026 dua hal berubah di Hermes: browser/computer-use jadi
> **backend default**, dan driver-nya **terpasang otomatis** saat install. Artinya
> satu profil browser yang sudah login ke akun bisnis adalah benda paling
> berbahaya yang bisa ada di VPS-mu — bukan karena seseorang membobolnya, tapi
> karena sekarang ada agen di mesin yang sama yang **bisa** menggerakkannya.
>
> **Aturannya:**
>
> | | Profil browser |
> |---|---|
> | **Moderasi manusia** (halaman ini) | boleh login ke akun bisnis · **tidak pernah** dipakai agen |
> | **Riset agen** | profil terpisah · **tidak pernah** login ke akun bisnis apa pun |
>
> Pakai `--user-data-dir` yang **berbeda** untuk keduanya, dan jangan pernah
> menukarnya. Kalau agen dan moderasi berbagi satu profil, satu kalimat yang
> nyasar dari halaman yang di-scrape bisa berujung klik di akun aslimu.
>
> **Kalau yang kamu butuhkan cuma balas komentar dan jadwal posting** untuk IG /
> FB / TikTok / YouTube / Threads: **jangan bangun ini.** Pakai Jalur B2
> (`references/repliz.md`) — jalur resmi, mulai Rp 18.000, tanpa satu pun sesi
> login yang perlu kamu jaga. Halaman ini untuk sisa kasus yang benar-benar
> tidak punya jalur resmi.

Jalur ini ada untuk satu situasi: **platform yang tidak punya API publish, tapi
kamu tetap ingin Hermes mengerjakan bagian yang membosankan.**

Bentuknya bukan "bot yang posting". Bentuknya: browser jarak jauh yang
disiapkan agen, diputuskan manusia.

```
Hermes (di VPS)                      Kamu (di HP, di mana saja)
──────────────────                   ──────────────────────────
buka composer
isi caption dari draft
unggah gambar
BERHENTI                    ──────►  notifikasi Telegram + screenshot
                                     buka layar VPS lewat Tailscale
                                     periksa: caption benar? gambar benar?
                                     akun benar?
                            ◄──────  kamu yang klik "Post"
catat ke arsip
```

Yang membuat ini masuk akal adalah baris "BERHENTI". Hilangkan baris itu dan
kamu punya Jalur F dengan kerapuhan ekstra.

---

## Kenapa Tailscale, bukan port terbuka

Alternatifnya adalah membuka VNC/noVNC ke internet lewat IP publik VPS. Jangan.
Itu berarti sesi browser yang sudah login ke akun bisnismu bisa dijangkau siapa
pun yang memindai port.

Tailscale membuat jaringan privat antara HP kamu dan VPS. Layar browser itu
hanya ada di jaringan itu. Tidak ada port yang terbuka ke internet, tidak ada
password yang bisa ditebak dari luar.

Gratis untuk pemakaian pribadi, dan setup-nya sekitar 10 menit.

---

## Setup

### 1. Tailscale di VPS dan HP

```bash
# di VPS: pasang Tailscale mengikuti panduan resmi
# https://tailscale.com/download (pilih distro VPS-mu)
sudo tailscale up
# ikuti link login yang muncul

# di HP: pasang aplikasi Tailscale, login dengan akun yang sama
```

Cek keduanya sudah saling melihat:

```bash
tailscale status
```

Catat nama VPS-nya (mis. `hermes-vps`). Itu yang kamu pakai, bukan IP publik.

### 2. Browser dengan layar yang bisa dilihat

```bash
sudo apt install -y xvfb x11vnc chromium-browser novnc websockify

# layar virtual
Xvfb :99 -screen 0 1280x900x24 &
export DISPLAY=:99

# browser MODERASI — profil persisten, boleh login, HANYA disentuh manusia.
# Nama direktorinya sengaja eksplisit: kalau suatu hari kamu (atau agen) melihat
# path ini di sebuah perintah, itu tanda ada yang salah.
chromium-browser --user-data-dir=$HOME/.hermes/browser-profile-MANUSIA \
                 --no-first-run --window-size=1280,900 &

# Profil RISET untuk agen dibuat terpisah dan TIDAK PERNAH login ke akun bisnis:
#   --user-data-dir=$HOME/.hermes/browser-profile-riset
# Jangan pernah menukar keduanya, dan jangan pernah mengarahkan agen ke profil
# di atas. Satu profil login yang bisa disentuh agen sudah cukup untuk kehilangan
# akun yang dibangun bertahun-tahun.

# jembatan VNC → web, HANYA di alamat Tailscale
x11vnc -display :99 -forever -shared -localhost &
websockify --web=/usr/share/novnc 6080 localhost:5900 &
```

Buka dari HP: `http://hermes-vps:6080/vnc.html`

Perhatikan `-localhost` di `x11vnc` dan `localhost:5900` di `websockify`.
Keduanya memastikan VNC tidak terekspos ke luar; Tailscale yang menjadi
satu-satunya jalan masuk.

### 3. Login sekali, dengan tanganmu sendiri

Buka layar itu dari HP, login ke akun sosialmu **secara manual**. Selesaikan
2FA. Biarkan sesi tersimpan di profil browser.

Ini penting: **Hermes tidak pernah memegang passwordmu.** Dia memakai profil
browser yang sudah login. Kalau kamu ingin mencabut aksesnya, hapus foldernya:

```bash
rm -rf ~/.hermes/browser-profile
```

### 4. Hermes menyiapkan, tidak menerbitkan

Konvensi yang dipakai skill ini: setiap skrip browser berhenti sebelum tombol
publish, lalu mengirim screenshot.

```bash
# contoh bentuk — sesuaikan dengan tool browser yang kamu pakai
# (Playwright, browser-use, atau modul browser milik Hermes/OpenClaw)
#
#   1. goto composer
#   2. isi caption
#   3. unggah gambar
#   4. screenshot → /tmp/siap-post.png
#   5. kirim ke Telegram
#   6. EXIT. Tidak ada langkah klik publish di skrip ini.
```

Aturan yang membuat jalur ini aman ada di poin 6, dan poin 6 harus ada di
**kode**, bukan di catatan. Issue OpenClaw #56897 membahas persis ini:
instruksi di dokumen skill bukan penegakan.

---

## Kerugian, dengan buktinya

Semua dari issue tracker OpenClaw, judul dicek 2026-08-11:

| Masalah | Issue |
|---|---|
| Alur browser-cron IG/WhatsApp 5 menit: dilaporkan **~70% run gagal** | #78602 |
| Composer X menolak teks yang diketik program (kasus input Korea) | #54879 |
| Percakapan salah rute antar-akun | #41483 |
| Profil/sesi browser tidak stabil antar-run | #8824 |

Angka ~70% berasal dari satu operator dan isinya belum diverifikasi. Tapi
polanya konsisten dengan tiga issue lain, dan itu yang membuatnya layak
dipercaya sebagai gambaran umum: **ini rapuh.**

Yang akan rusak, urut dari yang paling sering:

1. **Selector berubah.** Platform mengganti markup tanpa pemberitahuan.
2. **Login wall / captcha muncul.** Biasanya setelah IP VPS terlihat mencurigakan.
3. **Sesi kedaluwarsa.** Kamu perlu login manual lagi.
4. **Composer menolak input.** Terutama editor `contenteditable` yang rumit.
5. **Disk penuh** karena screenshot menumpuk. Ini nyata dan memalukan.

Rencanakan untuk memperbaikinya sebulan sekali. Kalau itu terdengar
melelahkan, jalur ini bukan untukmu — dan itu jawaban yang sah.

---

## Status ToS

Abu-abu, dan condong ke tidak aman kalau kamu mengotomatiskan penuh.

- X: aturan otomasinya menyebut **scripting situs non-API dapat berujung
  penangguhan permanen**.
- Instagram: melarang akses atau pengumpulan otomatis tanpa izin tertulis Meta.

Argumen yang masuk akal untuk jalur ini: kamu memakai browser sungguhan, dengan
sesi yang kamu login sendiri, dan **manusia yang menekan tombol terakhir**.
Itu secara praktis adalah pemakaian jarak jauh, bukan otomasi akun.

Argumen itu berhenti berlaku pada detik kamu menghapus langkah manusianya.

---

## Kapan jalur ini benar

✓ Platformnya tidak punya API publish sama sekali
✓ Volume rendah (≤ 20/minggu) dan kamu memang akan melihat setiap satu
✓ Kamu tidak keberatan memperbaiki hal yang rusak sebulan sekali

## Kapan jelas salah

✗ Akunnya tidak tergantikan
✗ Kamu berharap ini jalan tanpa dijaga
✗ Kamu mengajarkannya ke 60 pemula dalam 3 jam — mereka akan pulang dengan
  sesuatu yang rusak dalam seminggu dan tidak tahu kenapa

---

## Yang sebenarnya berharga dari jalur ini

Bukan posting-nya.

Browser jarak jauh yang bisa kamu lihat dari HP juga berarti: Hermes bisa
membuka dashboard yang tidak punya API, mengambil screenshot laporan penjualan
tiap pagi, memeriksa apakah tokomu masih tampil di pencarian, atau membaca
komentar di post yang tidak bisa diakses lewat API.

Itu semua **membaca**, dan membaca jauh lebih jarang bermasalah daripada
menulis. Kalau kamu memasang jalur ini, pertimbangkan memakainya untuk itu
lebih dulu.
