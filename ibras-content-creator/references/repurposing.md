# Repurposing — Hub and Spoke Method

> 1 konten panjang → N konten pendek per platform. **Tapi DISTINCT, bukan identical.**

## Prinsip dasar

**Hub** = 1 konten substantif (blog post 1500 kata, video YouTube 10 menit,
podcast 30 menit). Ini investasi konten terbesar.

**Spoke** = N potongan kecil yang tarik **klaim berbeda** dari hub, untuk
platform berbeda. Bukan summarize — **extract distinct angle** per spoke.

## Kenapa "distinct" bukan "identical"?

1. **Algoritma penalti** identical crosspost (LinkedIn, TikTok, IG detect).
2. **Audience fatigue** — follower yang sama lihat 5x konten yang sama = unfollow.
3. **Format beda** — yang work di TikTok (visual hook 3 detik) ≠ work di LinkedIn (300 kata take).
4. **Reach multiplier** — distinct variant reach audience berbeda.

## Workflow repurposing (1 hub → 8-10 spokes)

```
HUB: 1 video YouTube 10 menit "Cara Milih Biji Kopi Specialty"
  │
  ├── SPOKE 1: TikTok 30s — hook "3 tanda biji kopi sudah stale"
  ├── SPOKE 2: IG Reels 15s — visual demo "lihat warna biji, cium aroma"
  ├── SPOKE 3: IG Carousel 7 slide — "5 kriteria biji specialty (vs komersial)"
  ├── SPOKE 4: X Thread 7 tweet — "Thread: apa yang membuat kopi 'specialty'? Saya jelasin"
  ├── SPOKE 5: LinkedIn 250 kata — "Pelajaran memilih supplier dari pengalaman beli biji"
  ├── SPOKE 6: IG Story 3 frame — poll "Kamu pernah beli biji stale? YES/NO"
  ├── SPOKE 7: Blog 500 kata SEO — "Cara milih biji kopi specialty (panduan pemula)"
  ├── SPOKE 8: Newsletter section 150 kata — "Minggu ini: tips milih biji"
  └── SPOKE 9: TikTok stitch/comment reply — jawab pertanyaan comment spesifik
```

9 spokes, masing-masing **angle berbeda**, dari 1 hub. Reach: TikTok audience
+ IG + X + LinkedIn + blog search + email list. Semua dari 1 investasi utama.

## Cara extract spokes yang distinct

Untuk tiap spoke, tanya: **apa angle yang RELEVAN untuk platform ini?**

| Platform | Angle umum |
|---|---|
| TikTok/Reels | Visual demo, contrarian hook, "stop doing X" |
| IG Carousel | Step-by-step, listicle, saveable |
| X Thread | Hot take, contrarian, story progression |
| LinkedIn | Profesional lesson, B2B angle, career insight |
| Blog | SEO-driven comprehensive, evergreen |
| Newsletter | Curated, personal note |

Contoh konkret dari hub "Cara Milih Biji":
- TikTok: **Visual** — "Lihat 3 hal ini sebelum beli biji" (demo close-up)
- X Thread: **Story** — "Saya pernah beli biji 'specialty' Rp 200rb ternyata fake. Ini cara ceknya."
- LinkedIn: **Lesson** — "3 prinsip memilih supplier yang saya pelajari dari beli biji 3 tahun"
- Blog: **Comprehensive** — "Panduan lengkap milih biji kopi specialty 2026 (15 hal cek)"

**Distinct angle** = reach audience berbeda + tidak bored.

## Tools di skill ini

```bash
# Repurpose 1 source ke multi-platform (auto-generate distinct variants)
bash scripts/repurpose.sh ~/content/blog-post.md --platforms all

# Atau specific platforms
bash scripts/repurpose.sh ~/content/video-transcript.md --platforms instagram,tiktok,x
```

Script generate draft per platform dengan instruction eksplisit "DISTINCT, bukan identical".

## Cadence repurposing

Jangan publish semua spokes di hari yang sama. Distribusikan:

| Hari | Spoke | Alasan |
|---|---|---|
| Senin | TikTok (hook) | Awal minggu, reach |
| Selasa | IG Reels | Audience IG aktif |
| Rabu | X Thread | Mid-week engagement |
| Kamis | LinkedIn | Professional slot |
| Jumat | IG Carousel | Saveable content weekend |
| Sabtu | IG Story poll | Light engagement |
| Minggu | Blog/Newsletter | Long-form weekend read |

1 hub = konten 1 minggu. Investasi 4-6 jam buat hub → 7 hari konten.

## Metric: "leverage ratio"

Leverage = (jumlah spokes sukses) / (jam investasi hub).

- 1 hub 4 jam → 7 spokes, 4 perform = ratio 1.0 (sehat)
- 1 hub 4 jam → 7 spokes, 1 perform = ratio 0.25 (evaluasi angle)
- 1 hub 4 jam → 7 spokes, 7 perform = ratio 1.75 (great, replicate)

Track di audit bulanan: spoke mana yang paling konsisten perform?

## Anti-pattern

- ❌ **Summarize** semua spokes = konten redundant
- ❌ **Copy-paste** caption antar platform
- ❌ **Post semua spokes sekaligus** (audience flooded)
- ❌ **Hub tidak substantial** — kalau hub tipis, spokes juga tipis
- ❌ **Spoke tanpa angle** — "repurpose untuk X" tanpa pikir kenapa X
