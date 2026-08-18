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

## Bukti bahwa platform sudah memutuskan

**LinkedIn 2026**: Flagged 40%+ post panjang sebagai AI-written, sekarang
suppress kategori tersebut. Reach halaman company turun 60-66%. Personal
profile dapat ~65% feed allocation — platform sengaja route ke manusia.

**TikTok 2026**: Eksplisit mengutamakan "authentic human creators" atas
AI-generated content. Watch time + completion rate + rewatch > raw views.
Posting volume tinggi konten low-signal = reach turun.

**YouTube 2026**: Demonetizing AI-slop channels massal. Policy: AI tools
tidak dilarang, tapi konten *tanpa human creative input* di-demonetize.

**Instagram/X**: Shadowban untuk automation/bot behavior. Beli followers =
engagement rate mati, algoritma death spiral.

**Klarna (2025 cautionary tale)**: Unicorn replace 700 human CS dengan AI,
klaim $10M hemat. Lalu **U-turn publik**, rehire human. CEO: "customers
like talking to people." Bahkan unicorn sadar bot kehilangan trust.

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
4. **30 post lemah < 3 post kuat.** Reach turun kalau volume naik tapi
   sinyalnya rendah.

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

## Pola yang benar: Hermes DRAFT → Telegram untuk review → manusia post native

```bash
# Hermes kerja tiap Senin pagi: riset + draft konten mingguan
hermes cron add "0 9 * * 1" "Pakai skill ibras-content-creator: ideate 5 konten dari pillars + riset tren minggu ini. Draft tiap konten untuk Instagram. Kirim DRAFT ke Telegram untuk saya review. JANGAN auto-publish ke Instagram." --name "Draft konten mingguan" --deliver telegram
```

Senin pagi kamu bangun, buka Telegram, ada 5 draft. Review saat ngopi,
edit yang off-voice, pilih 3 yang post hari itu. Native. Manusia.

## Kalau kamu MAU auto-post (meskipun kami tidak recommend)

Skill ini tidak akan membantu. Tapi kalau kamu tetap mau, gunakan tools
yang **native/sanctioned** oleh platform:
- **Meta Business Suite** (Instagram + Facebook scheduling official)
- **Buffer / Later / Hootsuite** (official partners)
- **TikTok Studio** (native scheduling)
- **YouTube Studio** (native scheduling)

Tools ini pakai **API resmi** platform, bukan unofficial. Masih ada risk
kalau kontennya AI-slop, tapi setidaknya tidak kena-ban untuk "connection method".

## Test filosofi (tanya diri sendiri)

Sebelum generate konten, tanya:
1. **Tujuan konten ini apa?** (brand awareness? engage? sell? — kalau tidak jelas, skip)
2. **Apa saya akan post ini kalau tidak ada AI?** (kalau tidak, mungkin tidak perlu)
3. **Apa value untuk audience?** (kalau tidak ada value, ini noise)
4. **Apa ini terdengar seperti saya, atau seperti AI?** (edit kalau perlu)

4 ini = filter sederhana yang lebih efektif daripada autopilot manapun.
