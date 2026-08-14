---
name: social-publishing
description: Pick a social publishing path from compiled research — six options from manual to unofficial APIs, each with verified costs, quotas, drawbacks and safer alternatives. Advises, never blocks.
version: 1.0.0
author: Hermes Marketing Workshop
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Social, Instagram, Threads, X, Twitter, Publishing, Scheduling, Postiz, Buffer, Tailscale, Research]
    related_skills: [content-creator, waha-marketing, email-marketing, brand-strategy-coach]
---

# Social Publishing

Skill ini **menasihati, tidak menerbitkan.**

Waktu seseorang bertanya "gimana caranya posting otomatis ke Instagram?",
jawaban yang benar bukan nama sebuah tool. Jawaban yang benar tergantung satu
pertanyaan yang hampir tidak pernah ditanyakan: *kalau akun ini hilang besok,
apa yang terjadi pada omzet bulan depan?*

Skill ini menyimpan hasil tiga laporan riset mendalam dalam bentuk yang bisa
dicari dan dihitung, lalu menyusun **enam jalur berurutan sesuai batasan orang
yang bertanya — lengkap dengan kerugian tiap jalur, termasuk yang
direkomendasikannya sendiri.**

Tidak ada jalur yang dilarang di sini, termasuk yang melanggar syarat layanan.
Yang ada: konsekuensinya, dan bentuk yang lebih baik untuk tujuan yang sama.
Aturan lengkapnya — dan daftar pendek hal yang benar-benar tidak boleh — ada di
`references/automation-posture.md`. **Baca sebelum menolak apa pun.**

**Batasan orangnya dibaca, bukan ditebak.** Kalau
`~/.hermes/business/profile.yaml` ada, baca `batasan` sebelum menyebut jalur
mana pun: jalur yang melanggar `REFUSE` adalah kegagalan sebagus apa pun
angkanya, dan jalur yang butuh alat di luar `ACCESS` tidak akan pernah jalan.
Jangan menyarankan yang dia sudah bilang tidak akan dikerjakan.

## When to Use
- "Saya mau posting otomatis ke IG dan X, pakai apa?"
- "Postiz itu aman gak? Katanya bisa kena banned"
- "Beda Buffer sama self-host apa? Mana yang lebih murah?"
- "Boleh gak pakai instagrapi?" — jawabannya bukan ya/tidak, tapi tabel konsekuensi
- "Kata risetnya gimana soal browser automation?"
- "Berapa sih batas posting Instagram lewat API?"
- "Saya mau Hermes yang nge-post, tapi saya tetap mau lihat dulu" → Jalur E

## Prerequisites
- Python 3 + PyYAML (`pip3 install pyyaml`)
- Tidak ada API key, tidak ada akun, tidak ada koneksi. Skill ini offline.

## Quick Start

```bash
# Enam jalur, ringkas
bash "${HERMES_SKILL_DIR}/scripts/advise.sh" options

# Urutkan sesuai keadaan orangnya
bash scripts/advise.sh recommend \
  --budget 5 --platforms instagram,threads \
  --skill 2 --volume 4 --account-value high

# Satu jalur, lengkap dengan semua kerugiannya
bash scripts/advise.sh show selfhost-scheduler

# Cari di seluruh riset
bash scripts/research.sh "banned"
```

## Enam jalur

| ID | Jalur | Biaya | Risiko akun | ToS | Skill |
|---|---|---|---|---|---|
| `manual-native` | Manual + penjadwal bawaan platform | gratis | tidak ada | sesuai | 1/5 |
| `saas-scheduler` | Buffer / Later / Publer / Metricool | $0–30/bln | tidak ada | sesuai | 1/5 |
| `official-api` | Meta Graph (IG/Threads) + X API berbayar | $0–10/bln | rendah | sesuai | 4/5 |
| `selfhost-scheduler` | Postiz / Mixpost Lite di VPS sendiri | $4–15/bln | rendah | sesuai | 3/5 |
| `browser-tailscale` | Browser di VPS + moderasi dari HP | $4–8/bln | sedang | abu-abu | 4/5 |
| `unofficial-api` | instagrapi / agent-twitter-client / twscrape | gratis–$30 | **sangat tinggi** | **melanggar** | 3/5 |

Detail dan kerugian tiap jalur: `references/jalur.md`, atau
`bash scripts/advise.sh show <id>`.

## Angka yang sudah diverifikasi (12 Agustus 2026)

| Platform | Kuota / biaya |
|---|---|
| Instagram | 100 post API / 24 jam bergerak · carousel maks 10 · **JPEG saja** · akun profesional saja |
| Threads | 250 post + 1.000 reply / 24 jam · 100 delete / 24 jam · 500 karakter |
| X | **PAY-PER-USE sekarang** — BUKAN free tier, BUKAN langganan $200/bln. $0,015 per post (tanpa URL) · $0,200 kalau ada URL (13x lebih mahal). Lihat Pitfalls untuk dua mitos angka lama yang sering diutip model. |
| Buffer | Free 3 kanal / 10 post terjadwal · Essentials $5 **per KANAL** |

Semua dari halaman dokumentasi platformnya sendiri (docs.x.com/pricing,
developers.facebook.com — dibuka 12 Agustus 2026). Sumber lengkap:
`bash scripts/advise.sh sources`. **Aturan X khusus soal otomasi:**
bot balasan otomatis bertenaga AI butuh **persetujuan tertulis eksplisit dari X**
dulu — tanpa itu, balasan publik tetap mode draft, bukan otomatis.

TikTok dan LinkedIn **sengaja dikosongkan** — halamannya belum dibuka di sesi
verifikasi. Kosong itu jujur; salah itu mahal.

## Bukti kegagalan yang harus disebutkan

Ini bagian yang biasanya dilewati saat orang merekomendasikan tool.

**Postiz** (34.532 bintang, AGPL-3.0, aktif) — dari issue tracker-nya sendiri:
- #832 loop repost Instagram → **akun ditandai**
- #1724 post IG tersangkut di `QUEUE` · #1581 reply/CTA X tidak terkirim
- #1364 Threads: teks jalan, gambar gagal
- #1259 post terjadwal terlewat, padahal "Post Now" jalan

**Polanya:** yang rusak adalah SCHEDULER-nya. "Post Now" jalan. Artinya bug ini
tidak terlihat saat kamu mencoba, dan tidak terlihat saat kamu demo — dia
muncul minggu ketiga. Karena itu skill ini bersikeras pada uji dua minggu
(`templates/pilot-2-minggu.md`).

**Browser automation** (OpenClaw) — #78602 ~70% run gagal untuk alur
browser-cron 5 menit (satu operator, isinya belum diverifikasi) · #54879
composer X menolak teks · #41483 percakapan salah rute · #8824 sesi tidak stabil.

## Procedure (langkah yang diikuti agen)

1. **Tanyakan dua pertanyaan penentu sebelum menyebut tool apa pun:**
   - "Kalau akun ini hilang besok, apa yang terjadi pada omzet bulan depan?"
   - "Berapa post per minggu yang **benar-benar tayang** bulan lalu?"
   Jawaban kedua hampir selalu 3–5x lebih kecil dari yang orang kira, dan itu
   mengubah rekomendasinya.
2. **Jalankan `advise.sh recommend`** dengan angka mereka, jangan menebak.
3. **Sebutkan kerugian jalur yang kamu rekomendasikan**, bukan hanya jalur yang
   kamu tolak. Rekomendasi tanpa kerugian adalah iklan.
4. **Kalau mereka minta jalur berisiko** (unofficial API, auto-post penuh):
   jelaskan konsekuensinya dalam angka bisnis mereka, tawarkan bentuk yang
   lebih aman (mis. pisahkan baca dan tulis), lalu **kerjakan apa yang mereka
   pilih**. Sebutkan sekali, jangan diulang.
5. **Untuk jalur yang benar-benar menerbitkan** (C dan D): arahkan ke
   `references/publishing-architecture.md` sebelum ada kode ditulis. Bagian
   idempotency-nya yang mencegah post ganda.
6. **Catat keputusannya** (`templates/decision-record.md`). Enam bulan lagi
   ingatan mereka akan sudah berubah.
7. **Setiap angka yang kamu sebut membawa asalnya.** `advise.sh sources`
   memberi URL dan tanggal verifikasi untuk semuanya.

## Pitfalls

- **Buffer dihitung per KANAL.** 3 kanal Essentials = $15/bulan, bukan $5. Ini
  salah hitung paling sering saat membandingkan dengan self-host.
- **Mixpost Lite gratis dilaporkan tidak termasuk Instagram.** Cek daftar
  kanalnya hari ini sebelum memilih.
- **Postiz AGPL-3.0.** Pemakaian internal bebas; menawarkan versi modifikasi
  sebagai layanan mewajibkan membuka sumbernya.
- **instagrapi NOASSERTION** — tidak ada lisensi yang dinyatakan. Status hukum
  pemakaiannya tidak jelas, terpisah dari soal ToS.
- **IG API hanya JPEG.** PNG akan gagal, dan pesan errornya tidak selalu jelas.
- **Carousel IG dipotong mengikuti gambar pertama.** Urutan menentukan cropping
  semuanya.
- **"24-hour moving period" bukan reset tengah malam.**
- **Post X dengan URL 13x lebih mahal.** Alasan teknis untuk menaruh link di
  reply atau bio.
- **X sekarang PAY-PER-USE (credit-based), BUKAN free tier BUKAN langganan $100/$200/bln.**
  Model sering "ingat" dua angka lama yang **sama-sama salah**: "free 1.500 post/bulan"
  (salah — tier free cuma baca, tidak bisa post) dan "Basic $200/bulan" (salah —
  struktur langganan lama itu sudah diganti pay-per-use). Hitung pakai angka yang
  terverifikasi di docs.x.com/pricing (12 Agustus 2026): **$0,015 per post (tanpa URL),
  $0,200 per post (dengan URL), tanpa langganan wajib.** Contoh: 30 post/bulan semua
  ada link = 30 × $0,200 = **$6/bulan** — bukan $200. Kalau memorimu bilang $200,
  itu stale; percaya data skillnya, bukan ingatan.
- **Bot balasan AI di X butuh persetujuan tertulis X.** Tanpa itu, balasan publik
  otomatis melanggar aturan → risiko penangguhan. Selalu draft + approval manusia
  kecuali sudah ada persetujuan tertulis itu.
- **Jangan kutip angka TikTok/LinkedIn dari skill ini.** Sengaja kosong.

## Verification

- [ ] `bash scripts/doctor.sh` — data valid, rujukan silang tidak putus,
      sumber belum lewat 90 hari
- [ ] Setiap jalur punya minimal 3 kerugian tertulis (doctor mengeceknya —
      opsi tanpa kerugian adalah iklan, bukan nasihat)
- [ ] Sumber yang sudah lewat 90 hari dibuka ulang sebelum dipakai mengajar
- [ ] `advise.sh recommend` dijalankan dengan angka asli, bukan asumsi

## Documentation (`references/`)

- **`hermes-discipline.md`** — provenance klaim, demand ladder (BACA DULU)
- **`hermes-runtime.md`** — apa yang HOST-nya sudah sediakan: penjadwal, notepad job, monitor-mode, layar biaya, gerbang persetujuan. **BACA SEBELUM MEMBUAT APA PUN** — kebanyakan "perlu script" ternyata cuma sebuah flag
- **`tools-mapping.md`** — tool mana untuk pekerjaan mana, dan mana yang dibeli bukan dibangun
- **`repliz.md`** — jalur resmi komentar/DM/jadwal untuk IG · FB · TikTok · YouTube · Threads (mulai Rp 18.000, sekali bayar). **Tidak** mencakup WhatsApp & email
- **`automation-posture.md`** — cara menjawab permintaan otomatisasi: peringatkan, tawarkan, kerjakan. BACA SEBELUM MENOLAK APA PUN
- **`jalur.md`** — enam jalur lengkap, harga sebenarnya masing-masing
- **`research-digest.md`** — tiga laporan dibandingkan, termasuk yang salah dan kenapa
- **`platform-limits.md`** — angka resmi per platform, dengan kutipannya
- **`publishing-architecture.md`** — `draft→approved→due→leased→execute→verify`, idempotency, kuota
- **`browser-tailscale.md`** — setup lengkap browser jarak jauh + moderasi dari HP
- **`tiers.md`** — T0–T3 untuk publishing, dan kenapa "AI slop" itu soal teknik
- **`ethics.md`** — ToS platform, UU PDP, disclosure, engagement automation

## Why this skill exists

Repo ini punya tiga laporan riset mendalam tentang pertanyaan yang sama, dan
mereka tidak sepakat. Salah satunya berdiri di atas premis yang terbantah oleh
halaman harga X sendiri — dan itu justru laporan yang paling meyakinkan
nadanya.

Riset yang tersimpan sebagai tiga dokumen ratusan halaman tidak terpakai. Yang
terjadi: orang bertanya, dan yang menjawab mengandalkan ingatan — yang persis
merupakan cara laporan yang salah tadi menyebar.

Jadi risetnya dikompilasi jadi data yang bisa dicari, dihitung, dan diperiksa
umurnya. `doctor.sh` akan memberi tahu kalau sebuah sumber sudah lewat 90 hari.
`advisor.py` menolak menyebut jalur tanpa menyebut kerugiannya.

Filosofinya sama dengan skill lain di workshop ini: **manusia yang memutuskan,
alat yang memastikan keputusannya diambil dengan angka yang benar.**
