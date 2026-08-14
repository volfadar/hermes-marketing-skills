# Angka resmi per platform

Semua dari halaman dokumentasi platformnya sendiri, dibuka langsung,
**diverifikasi 12 Agustus 2026**. Versi mesinnya di `data/platforms.yaml`.

```bash
python3 lib/advisor.py platforms
python3 lib/advisor.py sources --id ig-content-publishing
```

---

## Instagram

**Sumber:** [Instagram Platform — Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing)

| | |
|---|---|
| Kuota publish | *"Instagram accounts are limited to 100 API-published posts within a 24-hour moving period"* |
| Jenis akun | **Akun profesional saja** (Business/Creator). Akun pribadi tidak bisa. |
| Media | gambar, video, reel, story, carousel |
| Carousel | *"limited to 10 images, videos, or a mix of the two"* |
| Format gambar | *"JPEG is the only image format supported"* — MPO dan JPS tidak |
| Tidak didukung | shopping tag · filter · alt text untuk reel dan story |

**Yang tidak tertulis besar-besar tapi penting:** carousel dipotong mengikuti
**gambar pertama** (default 1:1). Jadi urutan gambar menentukan cropping
semuanya. Kalau gambar pertama potret dan sisanya lanskap, hasilnya berantakan.

"24-hour moving period" = bukan reset tengah malam. Hitung 24 jam terakhir.

Instagram mendukung label konten AI dan branded content lewat API. Pakai kalau
relevan — itu menaikkan kepercayaan, bukan menurunkan.

---

## Threads

**Sumber:** [Threads API overview](https://developers.facebook.com/documentation/threads/overview)

| | |
|---|---|
| Post | 250 per 24 jam |
| Reply | **1.000** per 24 jam |
| Teks | 500 karakter |
| Carousel | 2–20 item |

Perbandingan 250 post vs 1.000 reply memberi tahu sesuatu tentang untuk apa
platform ini dirancang. Kalau strategimu di Threads adalah menerbitkan, kamu
memakainya melawan arahnya.

**Catatan komunitas:** publish gambar lewat penjadwal pihak ketiga sering gagal
walau publish teks jalan (Postiz #1364). Kalau Threads penting untukmu, uji
gambar secara khusus.

---

## X (Twitter)

**Sumber:** [X API pay-per-usage pricing](https://docs.x.com/x-api/getting-started/pricing)

| | |
|---|---|
| Post: Create | **$0,015** per request |
| Post: Create (with URL) | **$0,200** per request |

Ini membalik anggapan yang masih beredar luas bahwa memposting ke X butuh
langganan $100–200/bulan.

| Volume | Tanpa URL | Dengan URL |
|---|---|---|
| 20 post/bulan | $0,30 | $4,00 |
| 100 post/bulan | $1,50 | $20,00 |
| 300 post/bulan | $4,50 | $60,00 |

**Post dengan URL 13x lebih mahal.** Itu bukan sekadar angka anggaran — itu
alasan teknis untuk menaruh link di bio atau di reply, bukan di post utama.
Kebetulan itu juga yang direkomendasikan orang untuk jangkauan.

**Aturan otomasi X:** scripting situs non-API dapat berujung **penangguhan
permanen**. Berlaku untuk Jalur E dan F.

---

## Facebook Page

**Sumber:** Meta Graph API (Pages)

Berbagi domain operasional dengan Instagram — satu proses review Meta menutup
keduanya. Kalau kamu sudah mengurus IG, Facebook hampir gratis untuk ditambah.

Halaman (Page), bukan profil pribadi.

---

## TikTok dan LinkedIn — sengaja kosong

`data/platforms.yaml` menandai keduanya **BELUM DIVERIFIKASI**.

Halaman dokumentasinya tidak dibuka di sesi verifikasi ini, jadi tidak ada
angka yang ditulis. Yang diketahui secara umum:

- TikTok: Content Posting API ada, butuh akun bisnis dan aplikasi yang lolos audit
- LinkedIn: Marketing/Share API ada, butuh Company Page dan aplikasi terdaftar

Jangan mengutip angka untuk keduanya dari halaman ini. Buka dokumentasinya,
lalu perbarui `data/platforms.yaml` dengan tanggal verifikasi baru.

**Kenapa ini dibiarkan kosong dan bukan diisi dari ingatan:** skill yang
mengarang satu angka akan diragukan seluruh isinya oleh orang pertama yang
mengeceknya. Kosong itu jujur; salah itu mahal.
