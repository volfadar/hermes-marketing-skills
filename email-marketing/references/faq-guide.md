# Membuat `faq.yaml` dari inbox nyata

FAQ yang dikarang di ruang rapat akan meleset. FAQ yang disalin dari inbox
akan bekerja. Perbedaannya bukan kepintaran — perbedaannya adalah kata-kata
yang benar-benar dipakai pelangganmu.

---

## Prosedur (45 menit, sekali seumur hidup)

### 1. Ambil bahan mentahnya

```bash
bash scripts/mail.sh list --limit 100 --json > /tmp/inbox-100.json
```

Atau lebih baik lagi, buka folder yang benar-benar berisi pertanyaan pelanggan
kalau kamu sudah memisahkannya dengan label.

### 2. Kelompokkan dengan tangan

Tulis di kertas. Serius — layar membuatmu terlalu cepat menggeneralisasi.
Yang dicari: pertanyaan yang muncul **≥ 3 kali** dalam 100 email.

Biasanya untuk usaha kecil hasilnya 5–9 kelompok, dan 5 teratas menutup
50–70% dari seluruh pertanyaan masuk. Itu angka yang layak dikejar. Menutup
100% bukan tujuan dan tidak pernah tercapai.

### 3. Salin kata-kata mereka, bukan kata-katamu

Ini langkah yang paling menentukan.

**Salah** — bahasamu sendiri:
```yaml
patterns:
  - "jam operasional"
  - "waktu buka toko"
```

**Benar** — kalimat asli dari inbox:
```yaml
patterns:
  - "jam buka"
  - "buka jam berapa"
  - "masih buka ga"
  - "hari minggu buka"
  - "bukanya jam brp"
  - "opening hours"
```

Pelanggan tidak menulis "jam operasional". Mereka menulis "bukanya jam brp".
Kalau polamu tidak menampung salah ketik dan singkatan, skornya akan rendah
dan semuanya naik ke kamu — otomasinya jadi tidak ada gunanya.

### 4. Tulis jawabannya seperti kamu menulisnya sendiri

**Salah:**
> Terima kasih atas pertanyaan Anda. Kami dengan senang hati menginformasikan
> bahwa jam operasional kami adalah sebagai berikut.

**Benar:**
> Halo! Kami buka setiap hari 07.00–21.00 WIB. Dapur terakhir order 20.30.

Pelanggan lamamu kenal cara kamu menulis. Balasan yang tiba-tiba terdengar
seperti perusahaan asuransi adalah cara tercepat memberi tahu mereka bahwa
kamu sudah diganti mesin.

### 5. Beri tier yang jujur

Tanya satu hal untuk tiap entri:

> **Kalau jawaban ini salah, apa yang terjadi?**

| Jawabannya | Tier |
|---|---|
| Orang datang di jam yang salah, kecewa sebentar | T2 |
| Kamu terikat pada harga yang belum kamu hitung | **T3** |
| Ada yang mengambil keputusan kesehatan/keuangan | T2 + `disclaimer:` |
| Kamu tidak bisa membayangkan jawabannya salah | T2 |

### 6. Periksa

```bash
bash scripts/autoreply.sh validate
```

Yang dicari `validate`:
- entri dengan pola < 3 → gampang meleset
- jawaban < 30 karakter → biasanya belum selesai ditulis
- pola yang sama di dua entri → keduanya akan saling menurunkan skor
- entri yang menyentuh hal mengikat tapi tier-nya bukan T3

### 7. Uji dengan pertanyaan nyata

```bash
bash scripts/autoreply.sh simulate --text "bukanya jam brp ya kak?"
bash scripts/autoreply.sh simulate --text "bisa buat 30 orang gak?"
```

Ambil 10 email asli dari inbox, jalankan satu per satu. Yang skornya rendah
padahal seharusnya cocok → tambahkan kalimat aslinya sebagai pola.

### 8. Ukur cakupannya sebelum menyalakan apa pun

```bash
bash scripts/autoreply.sh scan
```

Baris terakhirnya:

```
  12/30 (40%) bisa dijawab otomatis dengan FAQ sekarang.
```

Kalau angkanya 10%, jangan salahkan tool-nya — FAQ-mu belum menutup inbox.
Kalau angkanya 40–60%, itu wajar dan sudah berguna. Kalau 90%, curigai
ambangmu terlalu rendah.

---

## Struktur file

```yaml
meta:
  business: "Nama Bisnis"
  owner_name: "Nama Kamu"
  confidence_threshold: 0.75      # 0.60 longgar · 0.75 disarankan · 0.85 ketat
  auto_reply_cooldown_hours: 12
  daily_auto_cap: 40
  business_hours: "07:00-21:00"   # kosongkan untuk 24 jam
  disclosure: "..."               # wajib diisi
  holding_message: "..."          # tidak menjanjikan apa pun
  signature: "..."

entries:
  - id: nama-unik                 # wajib
    tier: T2                      # T2 (otomatis) atau T3 (selalu draft)
    disclaimer: health            # opsional: health|finance|legal|income
    patterns:                     # wajib, minimal 3, pakai kalimat asli
      - "..."
    must_not:                     # opsional, membatalkan entri ini
      - "..."
    answer: |                     # wajib
      ...
```

### `must_not` untuk apa

Membatalkan entri saat ada kata yang menandakan pertanyaan berbeda meski
polanya mirip.

```yaml
- id: ongkir
  patterns: ["berapa ongkir", "ongkos kirim"]
  must_not: ["luar negeri", "internasional"]   # itu urusan lain, biar naik ke kamu
```

---

## Merawatnya

FAQ bukan dokumen sekali jadi.

| Kapan | Lakukan |
|---|---|
| Tiap minggu, 10 menit | Baca `escalations.jsonl`. Pertanyaan yang naik 3× minggu ini = kandidat entri baru |
| Tiap kali harga berubah | Cari entri yang menyebut angka. Balasan otomatis dengan harga lama lebih buruk daripada tidak ada balasan |
| Tiap kali ada komplain soal balasan | Jalankan `simulate` dengan teks aslinya. Lihat kenapa lolos |
| Tiap 3 bulan | `validate` ulang; hapus entri yang tidak pernah kena |

Entri yang tidak pernah kena dalam 3 bulan bukan bukti FAQ-mu lengkap —
biasanya itu bukti kamu mengarang pertanyaan yang tidak ada.
