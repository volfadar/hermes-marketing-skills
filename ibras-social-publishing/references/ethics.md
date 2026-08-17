# Etika & hukum — publishing media sosial

> Bukan nasihat hukum. Ringkasan aturan yang berlaku plus konsekuensi yang
> sudah terjadi pada orang lain.

---

## Syarat layanan platform, ringkas

| Platform | Yang tertulis | Berlaku untuk jalur |
|---|---|---|
| Instagram | melarang akses atau pengumpulan otomatis tanpa izin tertulis Meta | E (abu-abu), F (melanggar) |
| X | scripting situs non-API dapat berujung **penangguhan permanen** | E (abu-abu), F (melanggar) |
| Meta Graph / Threads API | diizinkan, dengan kuota tertulis | C, D |

Jalur A dan B tidak menyentuh aturan ini sama sekali.

Yang perlu jujur diakui tentang Jalur E: argumennya adalah kamu memakai browser
sungguhan dengan sesi yang kamu login sendiri, dan **manusia yang menekan
tombol terakhir** — itu praktis pemakaian jarak jauh, bukan otomasi akun.
Argumen itu berhenti berlaku pada detik langkah manusianya dihapus.

---

## UU PDP (UU No. 27/2022)

Berlaku sejak masa transisi berakhir **17 Oktober 2024**.

| Hal | Isi |
|---|---|
| Sanksi administratif | sampai **2% pendapatan tahunan** |
| Notifikasi kebocoran | **3×24 jam** |
| Tanggung jawab | pengendali data tetap bertanggung jawab **walau pemrosesan dilakukan pihak ketiga** |

Relevan untuk publishing di dua tempat:

1. **Kalau kamu memakai SaaS (Jalur B):** data audiens dan kalender kontenmu
   diproses pihak ketiga. Itu boleh — tapi kamu tetap pengendalinya, dan "saya
   cuma pakai tool gratis" bukan pembelaan.

2. **Kalau kamu scraping komentar/DM untuk analisis (sering di Jalur F):** kamu
   sedang mengumpulkan data pribadi orang. Menyimpannya di VPS-mu berarti kamu
   yang bertanggung jawab kalau bocor, termasuk kewajiban lapor 3×24 jam.

Sisi baik self-host (Jalur C/D): arsip, kalender, dan data audiens tidak keluar
dari server kamu. Itu bukan omongan pemasaran — itu bisa ditunjukkan.

Catatan jujurnya: kalau Hermes memakai model lewat API pihak ketiga untuk
menulis caption, isi draft **memang** dikirim ke penyedia model itu. Kalau kamu
ingin klaim "data tidak keluar" berlaku sepenuhnya, modelnya harus lokal.
Ketahui mana yang kamu jalankan sebelum mengatakannya ke orang.

---

## Disclosure

Dua hal yang tidak dinegosiasikan di seluruh repo ini:

**1. Kalau akun menerbitkan tanpa manusia membaca tiap post, bio-nya harus
mengatakan itu.**

Bukan karena ada aturan yang mewajibkan (belum, untuk kebanyakan platform).
Tapi karena orang yang tahu sedang membaca hasil mesin jauh lebih pemaaf
daripada orang yang merasa dibohongi. Yang kedua menceritakannya ke orang lain.

Instagram bahkan menyediakan label konten AI lewat API. Pakai kalau relevan.

**2. Disclaimer topik terregulasi tidak bisa dicopot.**

Kesehatan, penghasilan, hukum, keuangan. Ini melindungi pembaca, yang bukan
bagian dari perhitungan risiko bisnismu.

---

## Yang tidak boleh diposting

- Klaim kesehatan atau penghasilan tanpa dasar
- Testimoni yang tidak pernah diberikan
- Angka yang tidak punya asal-usul (jalankan
  `python3 scripts/check-numbers.py <draft>`)
- Konten SARA, kebencian, dewasa
- Meniru merek atau orang lain
- Urgensi palsu ("tinggal 3!") kalau tidak benar tinggal 3

---

## Engagement automation — bagian yang paling sering disalahpahami

Dua hal berbeda yang sering disebut dengan nama yang sama:

| | Status |
|---|---|
| Auto-comment / auto-DM ke orang asing untuk cari jangkauan | **Ini yang merusak.** Terlihat seperti spam karena memang spam. Efeknya negatif bahkan saat angkanya naik |
| Auto-reply FAQ di kolom komentar/DM sendiri, dengan batas dan jalan keluar ke manusia | **Sah dan berguna**, dengan bentuk yang sama seperti di skill email: cakupan tertutup, ambang keyakinan, lima trigger handoff, kill switch, audit log |

Yang kedua bentuknya sudah ada di `ibras-email-marketing/references/handoff.md`
dan bisa dipakai ulang untuk komentar/DM. Yang membuatnya aman bukan besarnya
FAQ — tapi bahwa dia berhenti di tempat yang benar.

---

## Kontrak diri

> "Setiap post yang keluar dari akun saya, saya bertanggung jawab atas isinya —
> termasuk yang saya tidak baca. Kalau saya tidak sanggup membaca semuanya,
> saya turunkan volumenya, bukan menaikkan otomasinya."
