# Ringkasan riset — apa yang sebenarnya diketahui, dan seberapa yakin

Skill ini dibangun dari tiga laporan riset mendalam yang ada di repo ini,
dikerjakan agen berbeda dengan tujuan yang sama. Halaman ini adalah hasil
membandingkan ketiganya, bukan penggabungan begitu saja — karena satu di
antaranya salah pada premis utamanya.

Cari di seluruh riset ini kapan saja:

```bash
bash scripts/research.sh "postiz"
bash scripts/research.sh "banned"
python3 scripts/lib/advisor.py sources
```

---

## Tiga laporan, dan cara membedakan yang berguna

| | Laporan A | Laporan B | Laporan C |
|---|---|---|---|
| Bentuk | Arsitektur adapter | Narasi "SaaS sudah mati" | Peta lanskap |
| Kutipan primer platform | 32 | **0** | banyak, dengan legenda keyakinan |
| Blog vendor | 0 | ~20 | ditandai sebagai vendor |
| Isi utama | skema intent, siklus `draft→approved→due→leased→execute→verify`, idempotency, uji coba 2 minggu dengan kriteria angka | "API resmi terlalu mahal, lewati saja: cookie hijacking, instagrapi, proxy residensial" | taksonomi 7 keluarga, ~200 klaim ditandai 🟢🟡🟠🔴, bagian yang membantah rekomendasinya sendiri |

### Temuan yang menentukan

Laporan B berdiri di atas satu premis: X API "sering menghabiskan $100 per
bulan". Halaman harga X sendiri mengatakan **$0,015 per post** ($0,200 kalau
ada URL). Catatan kaki B untuk klaim itu mengarah ke blog sebuah vendor yang
menjual jembatan X seharga $11,99/bulan — produk yang kemudian
direkomendasikan B dengan menyebut namanya.

Laporan C, secara terpisah, sudah menandai sumber yang sama sebagai tidak
bisa diandalkan.

**Konsekuensinya untuk skill ini:** B tidak dipakai sebagai sumber sama sekali.
Dia tetap disimpan di repo sebagai bahan ajar — contoh riset yang terdengar
sangat meyakinkan dan isinya kosong.

### Lima tanda yang bisa kamu pakai ulang

Ini yang membedakan B dari A dan C, dan polanya berlaku umum:

1. **Nol kutipan primer.** Semua angka berasal dari orang yang menceritakan angka.
2. **Sumber yang berkepentingan.** Klaim harga bersumber dari penjual alternatifnya.
3. **Tidak ada angka yang bisa dicek.** "Sering", "banyak", "kebanyakan orang".
4. **Tidak ada bagian yang membantah dirinya sendiri.** C punya; A punya daftar
   6 hal yang mungkin dia klaim berlebihan; B tidak punya keraguan sama sekali.
5. **Nada percaya diri berbanding terbalik dengan bukti.** Ini yang paling
   berbahaya, karena terasa seperti keahlian.

---

## Yang disepakati A dan C — perlakukan sebagai sudah selesai

Kalau dua laporan yang metodenya berbeda sampai ke kesimpulan yang sama, itu
titik paling kuat yang kita punya.

1. **Ada jalur resmi yang murah, dan kebanyakan orang tidak tahu.**
   Meta Graph untuk IG/Threads gratis. X $0,015 per post. Anggapan "$100/bulan"
   sudah kedaluwarsa.

2. **Penjadwal self-host adalah rekomendasi utama untuk audiens seperti ini.**
   Postiz di VPS $4–5. C bahkan menuliskan persona workshop ini di tabel
   keputusannya sendiri: *"Hermes/OpenClaw operator (workshop attendee)"* →
   self-hosted Postiz + langkah approve manusia.

3. **Otomasi browser bagus untuk demo, buruk untuk dipakai.**
   Rapuh pada selector, login wall, captcha, sesi. Bukan arsitektur publishing.

4. **Manusia di tengah adalah fitur, bukan kompromi.**
   Bahkan pembuat otomasi penuh memasangnya sendiri secara sukarela — pola
   "AI menulis → antrian approval di Telegram → publish" muncul berulang.

5. **Yang rusak biasanya scheduler-nya, bukan API-nya.**
   Ini temuan yang paling praktis di seluruh riset. Lihat bagian berikutnya.

---

## Bukti kegagalan (bagian yang biasanya dilewati orang)

Semua judul issue di bawah sudah dicek satu per satu lewat GitHub API pada
2026-08-11 — bukan dikutip dari ringkasan orang lain.

### Postiz — penjadwalnya, bukan API-nya

| Issue | Judul |
|---|---|
| #832 | *Continuous Reposting Loop for Standalone Instagram Integration - Risk! Account flagged* |
| #1724 | post Instagram tersangkut di status `QUEUE` |
| #1581 | reply/CTA X terjadwal tidak ikut terkirim |
| #1364 | Threads: publish teks jalan, publish gambar gagal |
| #1259 | post terjadwal terlewat, padahal "Post Now" jalan |

Baca #1259 dan #832 berdampingan. Polanya:

> **"Post Now" jalan. Yang dijadwalkan yang rusak.**

Itu bentuk kegagalan paling jahat yang bisa ada di alat penjadwalan, karena:

- kamu mencobanya, jalan, kamu percaya
- kamu demokan di depan orang, jalan
- lalu minggu ketiga ada post yang tidak tayang, dan kamu tidak tahu
- atau lebih buruk: #832 — dia mengulang post sampai akun ditandai

**Karena itu skill ini bersikeras pada uji dua minggu** (`templates/pilot-2-minggu.md`)
sebelum mempercayakan jadwal ke mesin. Bukan karena Postiz jelek — 34.532
bintang, push harian, aktif. Tapi karena kelas bug ini tidak muncul saat
sedang ditonton.

### Otomasi browser — OpenClaw

| Issue | Isi |
|---|---|
| #78602 | alur browser-cron IG/WhatsApp 5 menit: dilaporkan **~70% run gagal** |
| #54879 | composer X menolak teks yang diketik program (kasus input Korea) |
| #41483 | percakapan salah rute antar-akun |
| #8824 | profil/sesi browser tidak stabil |
| #56897 | usulan lapisan konfirmasi: *instruksi di `SKILL.md` bukan penegakan* |

Angka ~70% berasal dari satu operator dan **isinya belum diverifikasi** — yang
sudah dicek hanya bahwa issue-nya ada dan judulnya cocok. Perlakukan sebagai
anekdot serius, bukan statistik.

Issue #56897 layak dibaca sendiri. Intinya: menulis "jangan post tanpa
konfirmasi" di dokumen skill **bukan** penegakan. Kalau konfirmasi itu penting,
dia harus ada di lapisan eksekusi. Itu juga prinsip yang dipakai skill email di
repo ini — rem ada di kode, bukan di prosa.

---

## Angka repo (2026-08-11, lewat GitHub API)

| Repo | Bintang | Lisensi | Push terakhir |
|---|---|---|---|
| `openclaw/openclaw` | 385.950 | NOASSERTION | 2026-08-11 |
| `NousResearch/hermes-agent` | 228.988 | MIT | 2026-08-11 |
| `browser-use/browser-use` | 108.814 | MIT | 2026-08-11 |
| `gitroomhq/postiz-app` | 34.532 | **AGPL-3.0** | 2026-08-11 |
| `subzeroid/instagrapi` | 6.628 | NOASSERTION | 2026-08-11 |
| `nirholas/XActions` | 443 | Apache-2.0 | 2026-08-04 |

Dua baris yang penting dan sering dilewati:

- **Postiz AGPL-3.0.** Pemakaian internal: bebas. Tapi kalau kamu menawarkan
  Postiz yang sudah kamu modifikasi sebagai layanan ke klien, AGPL mewajibkan
  kamu menyediakan sumber modifikasinya. Untuk agensi kecil ini nyata.
- **instagrapi NOASSERTION.** Tidak ada lisensi yang dinyatakan. Status hukum
  pemakaiannya tidak jelas, terpisah dari soal ToS Instagram.

---

## Batas jujur dari verifikasi ini

Supaya tidak ada yang mengutip halaman ini melebihi isinya:

- Yang dicek dari kelima issue Postiz dan kelima issue OpenClaw adalah
  **keberadaan, status, dan judulnya** — bukan isi diskusinya. Jadi angka
  "~70% run gagal" belum diverifikasi isinya.
- Klaim "1 hashtag per post Threads" yang muncul di salah satu laporan
  **tidak ditemukan** di halaman Meta yang dibuka. Jangan diajarkan.
- Angka TikTok dan LinkedIn **sengaja dikosongkan** di `assets/data/platforms.yaml`
  karena halamannya belum dibuka di sesi verifikasi. Lebih baik kosong
  daripada diisi dari ingatan.

---

## Apa yang disumbangkan tiap laporan ke skill ini

| Laporan | Sumbangan |
|---|---|
| **A** | Arsitektur publishing (`references/publishing-architecture.md`), idempotency, uji 2 minggu dengan kriteria angka |
| **C** | Taksonomi jalur, legenda keyakinan 🟢🟡🟠🔴, routing per persona, bukti risiko |
| **B** | Bahan ajar: cara mengenali riset yang meyakinkan tapi kosong |
