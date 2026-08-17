# Tier untuk media sosial — dan kenapa "AI slop" itu masalah teknis, bukan moral

Model tata kelola yang sama dengan skill email dan WhatsApp di repo ini.
Ringkasannya di sini, disesuaikan untuk publishing.

---

## Empat tier

| Tier | Artinya | Izin | Contoh |
|---|---|---|---|
| **T0** | Tidak menyentuh publik. Baca, hitung, arsip, draft. | Otomatis penuh | riset hashtag, cek pengulangan, kalender, arsip post |
| **T1** | Agen → **kamu**. | Otomatis, langsung ke kamu | "besok jadwal kosong", "post kemarin engagement-nya beda" |
| **T2** | Agen → **publik**, di dalam batas yang kamu tentukan. | Otomatis, wajib punya verifikasi + kuota + jalan mundur | publish post yang sudah kamu approve, di slot yang sudah kamu setujui |
| **T3** | Agen → publik, butuh pertimbangan. | Draft + kamu approve | caption baru, balasan komentar, apa pun yang bernada |
| **↑** | **Kamu boleh menaikkan apa pun.** | Hermes menyebut risikonya sekali, lalu patuh | auto-post penuh, auto-reply komentar |

Perhatikan bahwa **T2 di sini lebih sempit daripada T2 di skill email.**
Alasannya: email salah dibaca satu orang; post salah dibaca semua orang, dan
tangkapan layarnya hidup lebih lama daripada post-nya.

---

## Kontrak penasihat

> Hermes tidak memblokir keputusanmu. Kalau kamu minta sesuatu yang berisiko,
> dia menyebutkan implikasinya sekali, menawarkan bentuk yang lebih baik, lalu
> mengerjakan apa yang kamu pilih — dan tidak mengungkitnya lagi.

Kalau kamu minta "post otomatis tiap jam 9 pagi", jawabannya bukan "tidak
boleh". Jawabannya:

1. **Bisa** — lewat Jalur C atau D, ini arsitekturnya.
2. **Ini yang terjadi kalau salah:** kuota IG 100/24 jam, dan issue #832
   menunjukkan loop repost bisa membuat akun ditandai.
3. **Bentuk yang lebih baik:** approve batch mingguan sekali duduk (10 menit),
   lalu antrian yang menerbitkan. Kamu tetap tidak menyentuh HP tiap pagi, tapi
   tidak ada yang tayang tanpa pernah dibaca manusia.
4. **Keputusanmu.** Kalau tetap mau penuh otomatis, itu jalan — dengan
   verifikasi dan kuota tetap menyala.

---

## "AI slop" — kenapa ini soal teknik, bukan selera

Posisi workshop ini: konten yang diproduksi mesin tanpa penilaian manusia bisa
mendapat traffic, view, dan like, tapi tidak membangun kepercayaan. Dan
kepercayaan adalah satu-satunya hal yang membuat bisnis kecil bertahan saat
harganya bukan yang termurah.

Yang membuat itu bukan sekadar pendapat:

- **Kesalahan kecil menyebar lebih jauh daripada konten yang bagus.** Satu
  balasan otomatis yang salah nada ke orang yang sedang kecewa bisa jadi
  tangkapan layar yang beredar lebih lama daripada 200 post yang baik.
- **Orang bisa merasakan konten yang tidak ada orangnya.** Tidak selalu bisa
  menunjuk apa, tapi berhenti membalas.
- **Yang paling mahal tidak terlihat.** Orang yang kecewa jarang komplain.
  Mereka pergi diam-diam, dan kamu tidak pernah tahu berapa banyak.

**Tapi ini bukan alasan melarang otomasi.** Ini alasan menempatkannya di
tempat yang benar:

| Pantas diotomatiskan | Tidak pantas |
|---|---|
| Menyiapkan draft dari arsip dan suara brand | Memutuskan apa yang layak diucapkan |
| Menerbitkan yang sudah kamu approve, di jam yang tepat | Menulis balasan untuk orang yang kecewa |
| Memeriksa apakah post benar-benar tayang | Menilai apakah lelucon ini pantas hari ini |
| Mengingatkan kalau kalender kosong | Berkomentar di post orang lain untuk cari perhatian |
| Membaca tren, komentar, kompetitor | Berpura-pura jadi orang |

Kolom kiri itu banyak. Itu bukan sisa — itu sebagian besar pekerjaan.

---

## Yang tidak dinegosiasikan

Dua saja, dan keduanya melindungi orang yang tidak ikut memutuskan:

1. **Disclosure kalau ini akun otomatis.** Kalau sebuah akun menerbitkan tanpa
   manusia membaca tiap post, bio-nya harus mengatakan itu. Orang yang tahu
   sedang membaca hasil mesin jauh lebih pemaaf daripada orang yang merasa
   dibohongi.
2. **Disclaimer topik terregulasi tidak bisa dicopot.** Kesehatan, penghasilan,
   hukum, keuangan. Ini melindungi pembaca, bukan bisnismu.

Asimetri yang membenarkan keduanya: kamu bebas menerima risiko **untuk
bisnismu sendiri**. Kamu tidak boleh diam-diam menerima risiko **atas nama
orang lain**.

---

## Menaikkan tier

Tidak ada flag yang perlu ditambahkan di skill ini karena skill ini tidak
menerbitkan — dia menasihati. Yang menerbitkan adalah jalur yang kamu pilih.

Yang bisa dilakukan skill ini: menunjukkan urutan konsekuensinya sebelum kamu
memilih, dan mencatat keputusanmu supaya enam bulan lagi kamu ingat kenapa.

```bash
python3 scripts/lib/advisor.py recommend --budget 5 --risk high --account-value low
cp templates/decision-record.md ~/.hermes/business/keputusan-sosial.md
```

Catatan keputusan itu bagian yang paling sering dilewati dan paling berguna.
Yang mahal bukan memilih jalur yang salah — yang mahal adalah tidak ingat
kenapa kamu memilihnya, lalu mengulangi analisis yang sama setahun kemudian
dengan ingatan yang sudah berubah.
