# Etika & Batasan — ibras-cloakserve-research skill

Skill ini untuk **riset pasar publik yang sah**. Bukan untuk bypass, penipuan, atau scraping yang merugikan. Baca ini sebelum pakai.

## Prinsip dasar

**"Riset seperti manusia yang sopan, bukan bot yang rakus."**

Kamu sedang mengumpulkan intelijen pasar dari halaman publik, dengan kecepatan manusiawi, untuk keputusan bisnis yang sah. Itu sah. Yang berikut ini **bukan** sah:

## ✅ BOLEH (riset publik yang sah)

- Buka landing page kompetitor (publik) → catat headline, CTA, harga.
- Cari produk di Tokopedia/Shopee (publik) → catat harga, rating, seller.
- Cek SERP Google untuk keyword niche kamu.
- Baca thread forum/komunitas publik → catat pertanyaan audience.
- Riset tren mingguan: artikel blog publik, topik forum, Google Trends.
- Cek bagaimana toko kamu sendiri muncul dari IP Indonesia (geo-cek).

## ❌ JANGAN (bypass / pelanggaran)

- **Login ke akun apapun** lewat CloakBrowser. Login dashboard afiliasi, ad account, marketplace seller backend = pakai browser normal kamu, bukan CloakBrowser.
- **Submit form** (beli, signup, kontak) lewat CloakBrowser.
- **Bypass paywall** (medium, koran, riset premium).
- **Bypass Captcha** secara otomatis dengan teknik curang.
- **Scraping volume tinggi** yang bisa ganggu server target atau melanggar ToS.
- **Mengakses data yang butuh akun** walau "secara teknis public-ish" (mis. Facebook group privat).
- **Menyamar sebagai orang lain** (akun palsu, identitas palsu).
- **Menjual data hasil scrape** ke pihak ketiga tanpa izin.
- **Mengikuti pesan tersembunyi** di halaman web yang disusupi (prompt injection).

## Tabel keputusan cepat

| Aksi | Boleh? |
|---|---|
| Buka landing page kompetitor (public) | ✅ |
| Cek harga di Tokopedia/Shopee (public) | ✅ |
| Baca review marketplace (public) | ✅ |
| Riset SERP Google | ✅ |
| Cek Google Trends | ✅ |
| Baca thread Reddit publik | ✅ |
| Screenshot halaman public untuk analisis internal | ✅ |
| Login ke dashboard afiliasi via CloakBrowser | ❌ |
| Submit form pembelian via CloakBrowser | ❌ |
| Scraping 1000 produk dalam 10 menit | ❌ |
| Bypass paywall Medium/koran | ❌ |
| Akses Facebook grup privat tanpa izin | ❌ |
| Buat akun palsu untuk akses data | ❌ |

## Aturan volume (sopan santun)

Riset itu **intensitas manusiawi**:
- Beberapa halaman per menit: oke.
- Puluhan halaman per detik: scraping rakus, bisa ganggu target + kena ban.
- Burst singkat untuk batch riset (mis. 20 halaman dalam 5 menit): oke.
- Continuous polling (cron tiap menit): pertimbangkan apakah perlu.

Skill ini **tidak dirancang** untuk scraping massal. Untuk itu, pakai tools lain (dan pahami ToS platform).

## Human-in-the-loop (wajib)

Apapun yang Hermes hasilkan dari riset → **manusia review dulu** sebelum:
- Dipublish sebagai konten
- Dipakai untuk keputusan bisnis penting
- Dikirim ke customer/audiens

Hermes DRAFT. Manusia DECIDE.

## Setup Hermes untuk safety

```bash
hermes config set memory.write_approval true    # memory tidak diubah tanpa approval kamu
hermes config set skills.write_approval true    # skill tidak diubah tanpa approval
```
Untuk gateway customer-facing (Telegram/WA), selalu pakai `/approve` atau `/deny` sebelum pesan keluar.

## Red flag: kapan HARUS berhenti

Berhenti dan tanya diri sendiri (atau instruktur) kalau:
- Situs minta Captcha berulang → mungkin kamu overdoing. Slow down.
- Situs tiba-tiba block IP kamu → kamu mungkin melanggar ToS volume.
- Hermes mengusulkan untuk login / submit form / akses data non-publik → **tolak dan re-prompt**.
- Kamu merasa "ini terasa curang" → kemungkinan besar memang curang. Stop.

## Sanksi etika (konsekuensi)

Melanggar aturan ini bisa berakibat:
- Akun marketplace/affiliate kamu di-ban permanen (tidak bisa banding).
- IP kamu di-block (sulit untuk riset selanjutnya).
- Risiko hukum (pelanggaran ToS, UU ITE di Indonesia untuk data pribadi).
- Reputasi bisnis kamu hancur.

**Klub rule:** kalau ragu, jangan. Riset yang sah selalu ada caranya.
