# FAQ — cloakserve-research skill

Pertanyaan yang sering muncul. Baca ini dulu sebelum `doctor.sh` atau troubleshooting.

## Q: Apa beda CloakBrowser dan cloakserve?

**CloakBrowser** = browser-nya. Chromium yang fingerprint-nya di-patch di level source code C++ (49 modifikasi) supaya antibot systems menilainya sebagai browser normal. Bentuknya: Python library (`pip install cloakbrowser`) + binary Chromium khusus (~150MB).

**cloakserve** = program pembungkus (sudah disertakan di Docker image resmi `cloakhq/cloakbrowser`, di `/usr/local/bin/cloakserve`). Dia menjalankan CloakBrowser dan menyajikannya sebagai **endpoint CDP di port 9222**. Hermes (atau program lain) connect via `connect_over_cdp("ws://localhost:9222")`.

**Analogi:** CloakBrowser = WordPress. cloakserve = web server yang menyajikan WordPress. Hermes = browser pengunjung yang mengakses situs.

Skill ini menjalankan **cloakserve** (bukan CloakBrowser langsung) supaya Hermes bisa pakai browser lewat CDP.

## Q: Kenapa harus pakai CloakBrowser, kenapa tidak browser biasa?

Karena banyak situs (Tokopedia, Shopee, situs ber-Captcha) memblock browser headless biasa. Chromium plain terdeteksi via fingerprint (canvas, WebGL, font list, navigator props). CloakBrowser menambal fingerprint ini di **source code C++** — bukan JS injection, bukan konfigurasi — jadi lolos bot detection dengan sah.

**Untuk apa:** riset pasar publik (kompetitor, harga, landing page) yang sulit dengan `curl` atau Playwright plain.

**Untuk BUKAN apa:** bypass login, paywall, ToS, atau sistem anti-fraud. Itu **dilarang** skill ini (lihat `ethics.md`).

## Q: Kenapa Tailscale? Bukannya sudah bisa tanpa?

Bisa. Tapi untuk riset yang **akurat dari perspektif Indonesia** (SERP Google versi ID, banner promo geo-specific, harga khusus region), datacenter IP luar Indonesia sering dapat hasil berbeda. Tailscale exit node ke HP kamu sendiri = egress dari IP residensial Indonesia, persis seperti user lokal.

Ini OPSIONAL. Riset tanpa Tailscale tetap bekerja, hanya mungkin kurang akurat geo-nya.

## Q: Apakah CloakBrowser + Tailscale = menipu situs?

Tidak. Dua-duanya untuk **reliabilitas riset publik**:
- CloakBrowser: agar situs tidak salah mengira kamu sebagai bot berbahaya (padahal kamu riset pasar yang sah).
- Tailscale: agar kamu dapat hasil riset dari perspektif geografis yang benar (Indonesia), bukan datacenter asing.

Kamu TIDAK:
- Menyamar sebagai orang lain (ini koneksi + identitas kamu sendiri).
- Mengakses konten yang tidak public.
- Melanggar ToS atau sistem anti-fraud.
- Scraping volume yang bisa ganggu target.

Kalau ragu, baca `ethics.md`.

## Q: Apakah ini akan membuat akun saya di-ban?

**Tidak**, selama kamu mengikuti aturan etika:
- ❌ Jangan pakai CloakBrowser untuk login ke dashboard afiliasi atau ad account. Login dari browser normal kamu.
- ❌ Jangan scraping 1000 halaman dalam 5 menit. Pelankan, lakukan riset secukupnya.
- ❌ Jangan submit form (beli, signup, dll.) melalui CloakBrowser.
- ✅ Riset landing page publik, SERP, halaman marketplace publik = aman.

## Q: Model `deepseek-v4-flash-0731` koq "bodoh"? Bisakah ganti?

Model ini **murah** (~$0.30/M token) tapi **lemah di multi-step abstrak**. Strategi skill ini:
1. **Script siap pakai** → kamu tidak perlu model yang bisa ngoding.
2. **Prompt eksplisit bertingkat** (lihat `templates/`) → model lemah bisa ikuti.
3. **Memory + skill** → workflow ter-store, tidak perlu di-re-explain.

Mau model lebih pintar? Set lewat `hermes config`: `model.default` = mis. `anthropic/claude-sonnet-4.5` (atau nous/hermes-4-pro, gpt-5, dll.), `model.provider` = `openrouter` (atau anthropic, openai, nous).
Tapi biaya naik 10-30x. Untuk riset pasar, deepseek-v4-flash **cukup** kalau pakai templates kami.

## Q: `initialize.sh` gagal di "Pull image CloakBrowser". Kenapa?

Biasanya salah satu:
1. **Internet lambat/tidak stabil.** Image + binary Chromium ~150MB. Coba ulang, pakai WiFi stabil.
2. **Docker Hub rate limit.** Login `docker login` atau tunggu 1 jam.
3. **Belum start Docker Desktop.** Buka Docker Desktop, tunggu sampai icon hijau, re-run.

`doctor.sh` akan mendeteksi dan memberi saran spesifik.

## Q: Hermes error "404 no endpoints found that support tool use". Kenapa?

Config kamu kehilangan `model.default`. Ini pernah jadi bug `wire-hermes.sh` versi awal — **sudah diperbaiki**. Solusi:

```bash
bash scripts/doctor.sh   # akan tunjukkan kalau model.default hilang
```
Atau set lewat `hermes config`: `model.default` = `deepseek/deepseek-v4-flash-0731`, `model.provider` = `openrouter`.

## Q: Bisakah setup tanpa Docker (install CloakBrowser langsung di Python)?

Bisa teknis (`pip install cloakbrowser && cloakbrowser install`), TAPI:
1. cloakserve (CDP multiplexer) **tidak ikut** di PyPI package — hanya ada di Docker image.
2. Tanpa cloakserve, Hermes tidak bisa connect via `browser.cdp_url` (karena tidak ada endpoint CDP yang disajikan).
3. Kamu harus tulis kode Python sendiri untuk pakai `cloakbrowser.launch()` — berat untuk non-teknis.

**Rekomendasi:** pakai Docker. Itu sebabnya skill ini default ke Docker.

## Q: Apakah ini gratis?

- **CloakBrowser**: free (free binary tier; Pro untuk fingerprint lebih banyak, $20/bln opsional).
- **Docker**: gratis.
- **Tailscale**: gratis untuk personal use (sampai 100 device).
- **Hermes**: gratis (open source).
- **Model AI (OpenRouter)**: deepseek-v4-flash ~$0.30/M token. Riset harian ~$0.05-0.20.
- **Total biaya bulanan realistis**: $2-10 tergantung intensitas riset.

Lihat `cost.md` untuk breakdown detail + strategi minimize.

## Q: Bagaimana cara uninstall?

```bash
bash scripts/stop.sh                            # stop container
docker rmi cloakhq/cloakbrowser:latest          # remove image
hermes skills uninstall cloakserve-research     # remove skill
# Hapus setting browser.cdp_url lewat `hermes config`
```
