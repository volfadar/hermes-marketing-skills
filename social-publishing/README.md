# social-publishing

Hermes skill untuk memilih **jalur publishing media sosial** dari riset yang
sudah dikompilasi — enam jalur, dari manual sampai API tidak resmi, masing-masing
dengan biaya terverifikasi, kuota resmi, kerugian, dan alternatif yang lebih aman.

**Menasihati, tidak menerbitkan.** Tidak ada jalur yang dilarang di sini.

## Install

```bash
cp -R social-publishing ~/.hermes/skills/social-publishing
pip3 install pyyaml
```

Tidak ada API key, tidak ada akun, tidak ada koneksi keluar. Skill ini offline.

## Pemakaian

```bash
# Enam jalur, ringkas
bash scripts/advise.sh options

# Urutkan sesuai keadaanmu
bash scripts/advise.sh recommend \
  --budget 5 --platforms instagram,threads \
  --skill 2 --volume 4 --account-value high

# Satu jalur, lengkap dengan kerugiannya
bash scripts/advise.sh show selfhost-scheduler

# Bandingkan
bash scripts/advise.sh compare official-api selfhost-scheduler

# Angka resmi per platform
bash scripts/advise.sh platforms

# Dari mana setiap klaim berasal
bash scripts/advise.sh sources

# Cari di seluruh riset
bash scripts/research.sh "banned"
bash scripts/research.sh "AGPL"

# Periksa isi skill (data valid? sumber kedaluwarsa?)
bash scripts/doctor.sh
```

## Enam jalur

| ID | Biaya | Risiko | ToS | Skill |
|---|---|---|---|---|
| `manual-native` | gratis | tidak ada | sesuai | 1/5 |
| `saas-scheduler` | $0–30/bln | tidak ada | sesuai | 1/5 |
| `official-api` | $0–10/bln | rendah | sesuai | 4/5 |
| `selfhost-scheduler` | $4–15/bln | rendah | sesuai | 3/5 |
| `browser-tailscale` | $4–8/bln | sedang | abu-abu | 4/5 |
| `unofficial-api` | gratis–$30/bln | sangat tinggi | melanggar | 3/5 |

## Dua pertanyaan sebelum tabel apa pun

1. **Kalau akun ini hilang besok pagi, apa yang terjadi pada omzet bulan depan?**
2. **Berapa post per minggu yang benar-benar tayang bulan lalu?**

Jawaban kedua hampir selalu 3–5x lebih kecil dari yang orang kira, dan itu
mengubah rekomendasinya.

## Dokumen

- `SKILL.md` — manifest + prosedur
- `references/jalur.md` — enam jalur lengkap
- `references/research-digest.md` — tiga laporan riset dibandingkan
- `references/platform-limits.md` — angka resmi + kutipannya
- `references/publishing-architecture.md` — arsitektur kalau Hermes benar-benar publish
- `references/browser-tailscale.md` — setup browser jarak jauh + moderasi dari HP
- `references/tiers.md` — T0–T3, dan kenapa "AI slop" itu soal teknik
- `references/ethics.md` — ToS, UU PDP, disclosure
- `templates/pilot-2-minggu.md` — uji sebelum mempercayakan jadwal ke mesin
- `templates/decision-record.md` — catat kenapa kamu memilih jalur itu

## Data

`data/options.yaml` · `data/platforms.yaml` · `data/sources.yaml`

Semua angka membawa URL dan tanggal verifikasinya. `doctor.sh` memberi
peringatan kalau ada sumber yang sudah lewat 90 hari.

## Lisensi

MIT.
