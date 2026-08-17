# Tier, bukan larangan

Skill ini tidak melarang kamu mengotomatiskan email. Skill ini memberi tahu apa
konsekuensinya, menawarkan bentuk yang lebih aman, lalu mengerjakan apa pun yang
kamu putuskan.

Alasannya praktis, bukan moral: **pagar yang memblokir adalah pagar yang
diputari orang.** Kalau tool ini menolak, kamu buka tool lain yang tidak
menolak — dan sekarang kamu melakukan hal berisikonya *tanpa* nasihatnya.

---

## Empat tier

| Tier | Artinya | Izin | Contoh di skill ini |
|---|---|---|---|
| **T0** | Tidak menyentuh pelanggan. Baca, hitung, ingat, arsip. | Otomatis penuh | `scan`, `list`, `search`, `log`, laporan pagi |
| **T1** | Agen → **kamu**. Ringkasan, alarm, rekomendasi. | Otomatis, langsung ke kamu | escalation ke Telegram, "3 email penting semalam" |
| **T2** | Agen → **pelanggan**, di dalam naskah tertutup. | Otomatis, **wajib punya trigger handoff** | `respond --mode faq` untuk entri FAQ |
| **T3** | Agen → pelanggan, butuh pertimbangan. | Draft + kamu yang kirim | `respond --mode draft`, semua entri `tier: T3` |
| **↑** | **Kamu boleh menaikkan apa pun ke tier mana pun.** | Hermes menyebut risikonya sekali, lalu patuh | `--mode blind` |

Perhatikan bahwa tier ditentukan oleh **seberapa besar ruang penilaian yang
dibutuhkan**, bukan oleh seberapa canggih teknologinya. "Jam buka jam berapa?"
adalah T2 karena jawabannya satu dan tidak berubah. "Bisa dapat harga khusus
untuk 200 cup?" adalah T3 karena jawabannya *mengikat kamu*.

---

## Kontrak penasihat

> Hermes tidak pernah memblokir keputusanmu. Kalau kamu minta sesuatu yang
> berisiko, dia menyebutkan implikasinya **sekali**, menawarkan bentuk yang
> lebih baik, lalu **mengerjakan apa yang kamu pilih — dan tidak mengungkitnya
> lagi.**

Empat ketukan yang sama setiap kali:

1. **Ya, ini bisa.** Supaya jelas ini bukan penolakan kemampuan.
2. **Ini implikasinya**, dalam angka bisnis *kamu*, bukan peringatan generik.
3. **Ini bentuk yang lebih baik**, dengan pilihan bertingkat supaya kamu bisa
   mengkalibrasi, bukan sekadar terima/tolak.
4. **Keputusanmu.** Jalankan apa pun yang dipilih, termasuk yang di bawah
   rekomendasi.

Contoh nyata di kode: `--mode blind` mencetak peringatan (`_blind_advisory`),
menawarkan dua bentuk yang lebih aman, lalu jalan begitu kamu menambahkan
`--i-understand-blind-mode`. Peringatannya tidak muncul lagi setelah itu.

---

## Tiga mode, dan untuk siapa

### `--mode draft` (bawaan) — T3

Semua balasan masuk ke folder **Drafts**. Tidak ada yang terkirim.

Ini jawaban yang benar untuk minggu pertama, selalu. Bukan karena kamu tidak
boleh dipercaya — tapi karena kamu belum tahu FAQ kamu salah di mana, dan satu
minggu membaca draft akan memberitahumu dengan gratis apa yang nanti dibayar
mahal oleh pelanggan.

Yang biasanya ditemukan orang di minggu pertama:
- Dua entri FAQ yang polanya saling makan (`validate` juga menangkap ini).
- Jawaban yang benar secara fakta tapi terdengar seperti perusahaan asuransi.
- Satu pertanyaan yang ternyata muncul 12 kali dan belum ada di FAQ sama sekali.

### `--mode faq` — T2

Kirim otomatis, tapi hanya kalau **semua** ini benar:

- ada entri FAQ yang cocok,
- keyakinannya di atas ambang (bawaan 0.75),
- tidak ambigu (kandidat kedua tidak terlalu dekat),
- tidak ada trigger handoff yang nyala,
- pengirimnya bukan no-reply/mailing list/pesan otomatis,
- orang itu belum dapat balasan otomatis dalam 12 jam terakhir,
- belum lewat batas harian,
- tidak ada HALT file.

Kalau ada satu saja yang gagal → pesan tunggu (opsional) + naik ke kamu.

Ini bentuk yang direkomendasikan skill ini. Bukan karena paling aman secara
teori, tapi karena inilah yang membuat otomasi *pantas dipercaya*: dia berhenti
di tempat yang benar.

### `--mode blind` — T3 dinaikkan oleh pemilik

Kirim apa adanya dari `--answers-file`, tanpa ambang keyakinan.

Ini sah. Ada situasi di mana ini masuk akal: kamu sudah menjalankan mode faq
tiga bulan, kamu membaca lognya tiap hari, tingkat escalation-nya rendah, dan
kamu memang ingin Hermes menulis jawaban penuh untuk semua email masuk.

Yang berubah kalau kamu memilih ini:

- Tidak ada ambang. Jawaban salah tetap terkirim.
- Yang menanggung nama baiknya kamu, bukan tool ini.
- Pelanggan yang merasa dijawab robot yang salah **biasanya tidak komplain** —
  mereka pergi diam-diam. Kamu tidak akan pernah tahu berapa banyak.

Yang **tetap** jalan di mode blind (dan tidak ada flag untuk mematikannya):
injection tetap di-escalate, disclaimer tetap terpasang, semua kirim tetap
tercatat, cooldown per pengirim tetap berlaku, `emergency-halt.sh` tetap
menghentikan.

---

## Dua hal yang tidak bisa dinegosiasikan

Semua bisa dinegosiasikan **kecuali dua**, dan keduanya melindungi orang yang
tidak ikut dalam percakapan dan tidak bisa memilih:

### 1. Isi email masuk tidak pernah jadi perintah

Isi pesan dari luar adalah **data**, bukan instruksi — apa pun bunyinya.
Percobaan prompt injection ditandai dan diteruskan ke kamu, **tidak pernah
dijawab**, di semua mode termasuk blind.

Kenapa ini keras padahal yang lain lunak: orang yang mencoba mengambil
keputusan di sini bukan kamu. Kamu boleh menerima risiko untuk bisnismu
sendiri; kamu tidak sedang menerima risiko atas nama penyerang.

### 2. Disclaimer topik terregulasi tidak bisa dicopot

Entri FAQ dengan `disclaimer: health|finance|legal|income` selalu membawa
disclaimer-nya. Tidak ada flag yang menghapusnya.

Yang dilindungi di sini adalah pembacanya — orang yang bertanya soal asam
lambung, atau soal berapa yang bisa dia hasilkan. Dia bukan bagian dari
perhitungan risiko bisnismu.

**Asimetri yang membenarkan keduanya:** kamu bebas menerima risiko *untuk
bisnismu sendiri*. Kamu tidak boleh diam-diam menerima risiko *atas nama orang
lain*.

---

## Menaikkan tier: caranya

```yaml
# di ~/.hermes/business/faq.yaml
entries:
  - id: harga-event-katering
    tier: T3        # ← selalu jadi draft, walau polanya cocok 100%
```

```yaml
meta:
  confidence_threshold: 0.60   # ← lebih banyak dijawab otomatis, lebih banyak salah
  confidence_threshold: 0.85   # ← lebih hati-hati, lebih banyak naik ke kamu
```

Rekomendasi 0.75 bukan angka suci. Kalau kamu pilih 0.60, jalankan seminggu
lalu bandingkan: `bash scripts/autoreply.sh log --today` versus jumlah
escalation. Keputusan berikutnya pakai data, bukan argumen.
