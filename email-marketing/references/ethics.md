# Etika & hukum — email marketing di Indonesia

> Ini bukan nasihat hukum. Ini ringkasan aturan yang berlaku plus konsekuensi
> praktis yang sudah terjadi pada bisnis lain.

---

## Prinsip

**Kirim ke orang yang minta dikirimi. Berhenti kalau mereka minta berhenti.**

Sama dengan aturan di `skill-waha-marketing/references/ethics.md`. Bedanya,
email punya satu jebakan tambahan: alamat email jauh lebih mudah didapat
daripada nomor WhatsApp, jadi godaan untuk mengumpulkannya jauh lebih besar.

---

## UU PDP (UU No. 27/2022) — yang relevan untuk kotak surat

Alamat email adalah data pribadi. Isi email berisi data pribadi orang lain.
Sekali kamu menyalakan skill ini, VPS kamu jadi tempat pemrosesan data pribadi.

| Hal | Isi |
|---|---|
| Masa transisi | Berakhir **17 Oktober 2024** — sudah lewat, aturannya berlaku penuh |
| Dasar pemrosesan | Butuh dasar yang sah; untuk pemasaran, praktisnya = persetujuan |
| Sanksi administratif | Sampai **2% pendapatan tahunan** |
| Notifikasi kebocoran | **3×24 jam** ke subjek data dan lembaga berwenang |
| Tanggung jawab | Pengendali data tetap bertanggung jawab **walau pemrosesan dilakukan pihak ketiga** |

Baris terakhir itu yang paling sering disalahpahami. "Saya cuma pakai tool
gratis" bukan pembelaan. Kamu pengendalinya.

**Sisi baiknya untuk arsitektur ini:** dengan Hermes self-hosted, isi kotak
suratmu tidak dikirim ke pihak ketiga mana pun untuk diproses. Tidak ada
vendor SaaS yang menyimpan salinan percakapan pelangganmu. Itu bukan omongan
pemasaran — itu perbedaan yang bisa kamu tunjukkan kalau ada yang bertanya.

Catatan yang jujur: kalau Hermes memakai model lewat API pihak ketiga untuk
menyusun jawaban, isi email **memang** dikirim ke penyedia model itu. Kalau
kamu ingin klaim "data tidak keluar" berlaku sepenuhnya, modelnya harus lokal.
Ketahui mana yang kamu jalankan sebelum mengatakannya ke pelanggan.

---

## Persetujuan yang sah, dan yang bukan

**Sah:**
- Isi formulir dengan kotak centang "kirimi saya info lewat email" (tidak
  tercentang di awal)
- Membalas email kamu dengan permintaan eksplisit untuk dikirimi update
- Persetujuan saat checkout, tercentang sendiri oleh pembeli
- Mendaftar acara dengan persetujuan email yang jelas

**Tidak sah:**
- Kartu nama yang kamu kumpulkan di pameran
- Alamat dari scraping LinkedIn/website
- Pembeli tiga tahun lalu yang tidak pernah setuju dikirimi newsletter
- Alamat `info@` perusahaan yang kamu temukan di Google
- Daftar yang dibeli, apa pun jaminan penjualnya
- "Mereka pasti tertarik"

Persetujuan untuk **transaksi** bukan persetujuan untuk **pemasaran**.
Orang yang memberi email untuk menerima invoice tidak sedang mendaftar
newsletter.

---

## Opt-out itu wajib

Setiap email pemasaran harus punya jalan keluar yang jelas. Untuk usaha kecil
yang mengirim dari Gmail, satu baris ini cukup dan lebih manusiawi daripada
tombol:

> Kalau tidak mau lagi dapat email seperti ini, balas dengan "STOP" — saya
> hapus hari itu juga.

Yang harus kamu lakukan saat ada yang minta berhenti:

1. Hapus dari daftar aktif **dalam 24 jam**
2. Simpan di daftar cegah (`opt_out.csv`) supaya tidak masuk lagi tanpa sengaja
3. Jangan pernah kirim lagi, walau dulu dia pernah setuju

Menghapus dari daftar aktif saja tidak cukup — tanpa daftar cegah, dia akan
masuk lagi saat kamu impor kontak berikutnya.

---

## Disclosure: bilang kalau ini otomatis

Skill ini memasang `meta.disclosure` di setiap balasan otomatis, dan itu
disengaja.

Alasannya bukan kepatuhan, tapi pengalaman yang berulang: **orang yang tahu
sedang bicara dengan asisten lalu dialihkan ke manusia jauh lebih tenang
daripada orang yang merasa dibohongi robot.** Yang kedua menceritakannya ke
orang lain.

Yang tidak boleh:
- Balasan otomatis yang ditandatangani seolah-olah kamu yang menulis
- "Maaf saya baru lihat pesannya" padahal itu mesin
- Persona palsu dengan nama orang yang tidak ada

Yang baik:
- "Balasan ini otomatis. Kalau butuh orangnya langsung, balas email ini."

---

## Isi yang tidak boleh dikirim

Sama dengan aturan WhatsApp, ditambah satu yang khas email:

- Penipuan/phishing — termasuk yang tidak sengaja terlihat seperti phishing
  (link pendek + urgensi + minta data = pola yang persis sama)
- Konten SARA, kebencian, dewasa
- Klaim kesehatan atau penghasilan tanpa dasar → lihat aturan disclaimer di
  `tiers.md`
- Meniru identitas orang atau merek lain di header `From:`

---

## Kontrak diri

Sebelum menyalakan balasan otomatis, tulis satu kalimat:

> "Saya [nama]. Balasan otomatis saya akan selalu menyebut dirinya otomatis,
> selalu punya jalan ke saya, dan hanya menjawab hal yang saya sendiri sudah
> tulis jawabannya. Kalau saya tidak yakin, mesinnya diam dan saya yang jawab."

Tempel di dekat meja kerja. Itu jangkar etismu, bukan file konfigurasi.
