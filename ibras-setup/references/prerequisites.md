# Prasyarat — apa yang dibutuhkan tiap skill, dan apa yang rusak tanpanya

Semua angka dan klaim di bawah punya sumber dan tanggal baca. Kalau kamu membaca
ini jauh setelah tanggalnya, buka ulang halamannya — versi berubah.

## Inti (semua skill)

| Komponen | Cek | Rusaknya seperti apa |
|---|---|---|
| `hermes` di PATH | `hermes --version` | tidak ada yang jalan |
| `python3` | `python3 -V` | script profil, ledger, copycheck mati |
| PyYAML | `python3 -c "import yaml"` | profil tidak kebaca; skill lain "lupa" harga |
| `model.default` di `config.yaml` | lihat bawah | **`404 tool-use`** — terlihat seperti skill rusak |

`model.default` kosong adalah kegagalan yang paling menyesatkan: pesan errornya
tidak menyebut model sama sekali, jadi orang membongkar skill-nya.

```bash
hermes setup --portal    # OAuth, tanpa API key
# atau
hermes model             # pakai key sendiri
```

## Browser / CDP

Dibutuhkan `ibras-cloakserve-research`, dan oleh `ibras-brand-strategy-coach`
untuk cek harga pasar. Hermes mencari endpoint CDP di `ws://127.0.0.1:9222`.

**Rantainya tiga langkah, dan melewatkan salah satu = browser mati:**

```
pasang biner  →  jalankan dengan --remote-debugging-port=9222  →  wire-hermes.sh
```

### Jalur A — cloakserve (butuh Docker, disarankan)

Fingerprint-nya `Asia/Jakarta` + `id-ID`, jadi SERP dan harga yang keluar versi
Indonesia. Untuk skill yang tugasnya menilai pasar Indonesia, itu bukan detail.

```bash
bash ~/.hermes/skills/ibras-cloakserve-research/scripts/start.sh
bash ~/.hermes/skills/ibras-cloakserve-research/scripts/wire-hermes.sh --port 9222
```

### Jalur B — Chromium langsung (tanpa Docker)

```bash
npx playwright install chromium
CHROME=$(find ~/.cache/ms-playwright -name chrome -type f | head -1)
nohup "$CHROME" --headless=new --no-sandbox --remote-debugging-port=9222 \
  --lang=id-ID --user-data-dir=/tmp/cdp-profile >/tmp/chrome-cdp.log 2>&1 &
bash ~/.hermes/skills/ibras-cloakserve-research/scripts/wire-hermes.sh --port 9222
```

### Dua jebakan, dua-duanya ditemukan pada instalasi nyata

1. **Instalasi setengah jadi terlihat berhasil.** Ditemukan
   `~/.cache/ms-playwright/chromium-1208/chrome-linux64/` lengkap dengan `ABOUT`,
   `WidevineCdm`, `MEIPreload` — dan **tanpa file `chrome`**. Cek binernya:
   `find ~/.cache/ms-playwright -name chrome -type f | head -1`
2. **Memasang tanpa menjalankan dan me-wire = tetap mati.** Gejalanya bukan error:
   agent melaporkan *"halamannya keblokir"* untuk halaman yang mengembalikan
   HTTP 200. Yang sebenarnya terjadi, isinya di-render JavaScript dan `curl` cuma
   dapat kerangka kosong.

## WhatsApp — WAHA

**WAHA Plus sudah dilebur ke WAHA Core sejak versi 2026.6.1.** Semua fitur yang
dulu berbayar — sesi tanpa batas, pesan multimedia, semua storage, security
bawaan — sekarang ada di image publik `devlikeapro/waha`. Tidak ada lagi image
`devlikeapro/waha-plus`, tidak perlu `docker login`, tidak perlu Patron key.

> Sumber: <https://waha.devlike.pro/docs/how-to/waha-plus/> — dibaca 20 Agustus 2026.
> Halaman itu menulis: *"Starting from version 2026.6.1, all features that used to
> be in WAHA Plus … are available in WAHA Core - 100% free and open source"* dan
> *"There's no separate Plus image anymore - just use `devlikeapro/waha`."*

Proyeknya minta dukungan sukarela lewat tier Community $5/bln di Patreon/Boosty,
dan halaman itu menyebut tier tersebut **tidak memberi perk apa pun** — semuanya
tetap gratis. Jadi jangan sampaikan ke peserta seolah ada yang harus dibayar.

```bash
bash scripts/waha.sh          # tarik image, jalankan, verifikasi, tulis config
```

Sambungkan nomornya sendiri lewat `http://127.0.0.1:3000/dashboard` → scan QR →
status `WORKING`. Skill tidak akan pernah memulai sesi atau mengirim untukmu.

## Email — SMTP

`ibras-email-marketing` butuh Gmail App Password 16 digit (2FA harus aktif dulu),
atau SMTP lain. `bash scripts/smtp.sh` memandu, membaca passwordnya dengan input
tersembunyi.

**Jangan pernah menaruh key atau password di command line** — argv terbaca proses
lain di mesin yang sama.

## Config opsional lain

| Skill | Butuh | Tanpa itu |
|---|---|---|
| `ibras-content-creator` | pillars + voice profile | konten generik, suara bukan suaramu |
| `ibras-email-marketing` | `business/faq.yaml` | mode balas tidak bisa jalan |
| `ibras-social-publishing` | — | jalan apa adanya |

## Isolasi beberapa Hermes home

Semua script menghormati urutan `HERMES_BUSINESS_DIR` → `HERMES_HOME` → default.
Satu mesin dengan beberapa home yang salah setel pernah membuat tiga sesi pemilik
usaha berbeda menulis ke `profile.yaml` yang sama. Tidak ada pesan error untuk itu.

```bash
python3 ~/.hermes/skills/ibras-brand-strategy-coach/scripts/lib/profile.py path
```
