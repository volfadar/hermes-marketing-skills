# Philosophy — apa yang benar-benar dihukum platform, dan apa yang tidak

> AI membantu produksi, manusia yang engage. Tapi baca dulu bedanya, karena
> versi lama halaman ini menggabungkan dua hal yang berbeda dan hasilnya
> jadi larangan yang salah sasaran.

**Dua hal yang sering dianggap sama, padahal beda jauh:**

| | Dihukum platform? |
|---|---|
| Menjadwalkan post yang **kamu tulis dan kamu setujui** | **Tidak.** Meta Business Suite, Creator Studio, dan hampir semua tool resmi memang untuk ini. |
| Membanjiri feed dengan konten AI **tanpa ada yang membaca dulu** | **Ya.** Ini yang disuppress LinkedIn dan didemonetisasi YouTube. |

Yang dihukum itu **volume tanpa review**, bukan **jadwal**. Bukti di bawah
semuanya tentang yang pertama, dan tidak satu pun tentang orang yang
menjadwalkan tiga post yang sudah dia baca sendiri.

Jadi posisi skill ini: **sebutkan konsekuensinya, tawarkan bentuk yang lebih
baik, lalu kerjakan pilihannya.** Baca `references/automation-posture.md` —
aturannya sama untuk semua skill di workshop ini.

## Klaim platform harus dicek, bukan diwariskan

Aturan platform, batas format, dan perilaku distribusi berubah. Karena itu skill
ini tidak memakai persentase reach, durasi, cadence, atau klaim "algoritma pasti
menghukum X" sebagai hukum universal. Saat keputusan bergantung pada aturan
platform, cek dokumentasi resmi terkini. Saat keputusan bergantung pada performa,
pakai account insights dan hasil uji akun pengguna sendiri.

Pisahkan tiga risiko: kualitas konten yang tidak direview, metode koneksi yang
melanggar aturan, dan format yang tidak cocok dengan pembeli. Ketiganya punya
solusi berbeda; jangan menyimpulkan bahwa semua penjadwalan atau semua konten
berbantu AI otomatis dihukum.

## Kenapa default-nya draft dulu (bukan larangan, tapi urutan)

1. **Kualitas.** Draft AI kadang salah suara, salah fakta, atau salah nada.
   Minggu pertama selalu ketemu dua-tiga yang meleset — dan itu murah kalau
   ketahuan sekarang, mahal kalau sudah tayang.
2. **Pola identik lintas platform = sinyal bot.** Ini soal isinya sama persis,
   bukan soal terjadwalnya. `repurpose.sh` bikin varian yang beda per platform.
3. **API tidak resmi = risiko akun**, dan itu risiko yang beda dari
   penjadwalan. Jalur resmi (Meta Business Suite, Buffer) menjadwalkan tanpa
   risiko itu sama sekali — lihat `ibras-social-publishing` untuk tujuh jalur
   beserta kerugiannya masing-masing.
4. **Volume mengikuti kapasitas review dan bukti akun.** Tambahan post hanya
   berguna bila kualitas dan sinyal bisnisnya tetap terjaga.

**Kalau dia sudah tahu semua ini dan tetap mau menjadwalkan otomatis:**
kerjakan. Tawarkan bentuk yang paling aman untuk tujuan yang sama — jalur
resmi, jadwal jarang, draft dikirim ke dia dulu satu jam sebelum tayang — lalu
ikuti keputusannya. Sebut sekali, jangan diulang tiap giliran.

## Yang skill ini LAKUKAN

- ✅ Ideasi (pilihan, manusia pilih)
- ✅ Draft konten (manusia review + edit)
- ✅ Repurpose ke multi-platform (variant berbeda, bukan identical)
- ✅ Kalender (manusia pilih slot realistis)
- ✅ Voice profile extraction (manusia confirm)
- ✅ Audit performa (analitik untuk keputusan manusia)
- ✅ Cron untuk **draft** yang dikirim ke Telegram untuk review

## Yang skill ini TIDAK lakukan

- ❌ Auto-post ke platform apapun
- ❌ Auto-comment di post orang lain
- ❌ Auto-DM (engagement manual wajib)
- ❌ Generate 100 caption tanpa strategi
- ❌ Schedule auto-publish via cron
- ❌ Integrasi platform API langsung (auto-post vector)

## Pola yang benar: Hermes DRAFT → review pemilik → jalur publish yang dipilih

```bash
# Contoh saja: pengguna menentukan jadwal, kanal pembeli, dan jumlah sesuai kapasitas
hermes cron add "<jadwal-pengguna>" "Pakai skill ibras-content-creator. Buat draft untuk <kanal-pembeli> dari bahan dan kapasitas yang sudah saya tetapkan. Kirim untuk review; jangan publish." --name "Draft konten" --deliver telegram
```

Pada waktu yang pengguna pilih, draft masuk ke kanal review. Pemilik memeriksa
fakta, voice, harga, dan kesiapan aset sebelum memilih mana yang layak publish.

## Kalau kamu MAU auto-post (meskipun kami tidak recommend)

Skill ini tidak akan membantu. Tapi kalau kamu tetap mau, gunakan tools
yang **native/sanctioned** oleh platform:
- **Meta Business Suite** (Instagram + Facebook scheduling official)
- **Buffer / Later / Hootsuite** (official partners)
- **TikTok Studio** (native scheduling)
- **YouTube Studio** (native scheduling)

Pilih jalur berdasarkan aturan platform terkini, kebutuhan approval, biaya, dan
kapasitas. Lihat `ibras-social-publishing` untuk membandingkan tujuh jalur.

## Test filosofi (tanya diri sendiri)

Sebelum generate konten, tanya:
1. **Tujuan konten ini apa?** (brand awareness? engage? sell? — kalau tidak jelas, skip)
2. **Apa saya akan post ini kalau tidak ada AI?** (kalau tidak, mungkin tidak perlu)
3. **Apa value untuk audience?** (kalau tidak ada value, ini noise)
4. **Apa ini terdengar seperti saya, atau seperti AI?** (edit kalau perlu)

4 ini = filter sederhana yang lebih efektif daripada autopilot manapun.
