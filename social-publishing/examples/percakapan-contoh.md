# Contoh percakapan — bagaimana skill ini dipakai dalam praktik

Empat situasi khas. Orang-orangnya karangan — sengaja dibikin tidak mirip
bisnis mana pun yang dipakai menguji Hermes, supaya tidak ada yang menyalinnya
sebagai kalau itu data pemiliknya. Yang penting bukan jawabannya —
yang penting urutannya: **dua pertanyaan dulu, baru tabel.**

---

## 1. Sri (Laundry Mbak Sri, Sidoarjo) — "mau posting otomatis ke IG"

**Sri:** Kak, saya mau IG saya auto-post aja. Capek tiap hari.

**Hermes:** Bisa. Sebelum saya sebut alat, dua hal dulu:

Kalau akun IG kamu hilang besok pagi, apa yang terjadi ke omzet bulan depan?

**Sri:** Ya mati sih. 200 kontak WA itu semuanya dari IG.

**Hermes:** Oke. Kedua — bulan lalu, berapa post yang **benar-benar tayang**?
Bukan yang direncanakan.

**Sri:** Hmm... 6 kali? Mungkin 5.

**Hermes:**

```bash
bash scripts/advise.sh recommend --budget 3 --platforms instagram \
  --skill 1 --volume 2 --account-value high
```

Urutan teratasnya jalur manual, dan itu jawaban yang benar untuk kamu — tapi
bukan karena kamu belum pantas yang canggih. Karena masalahnya bukan posting.

5 post sebulan itu ~1 per minggu. Otomasi menghemat mungkin 10 menit seminggu.
Yang bikin capek bukan menekan tombolnya — bikin caption-nya.

Jadi yang saya kerjakan: draft caption tiap Senin dari arsip post kamu yang
repeat-order-nya bagus, plus cek pengulangan supaya kamu tidak memakai pembuka
yang sama tiga minggu berturut-turut. Kamu tinggal baca, edit, tempel.

Risiko akun: nol. Dan akun kamu yang bawa 200 kontak itu tidak disentuh apa pun.

**Kalau nanti volumenya naik ke 15+/minggu, jalankan lagi perintahnya —
urutannya akan berubah sendiri.**

---

## 2. Bayu (konsultan pajak, Surabaya) — "Postiz aman gak?"

**Bayu:** Saya baca Postiz bagus. Tapi ada yang bilang bisa kena banned.

**Hermes:**

```bash
bash scripts/advise.sh show selfhost-scheduler
```

Yang bilang bisa kena banned itu benar, dan sumbernya issue tracker Postiz
sendiri — #832: *"Continuous Reposting Loop for Standalone Instagram
Integration - Risk! Account flagged"*. Loop repost, akun ditandai.

Empat issue lain yang perlu kamu tahu: post IG tersangkut di `QUEUE` (#1724),
reply/CTA X terjadwal tidak terkirim (#1581), Threads gambar gagal padahal teks
jalan (#1364), post terjadwal terlewat padahal "Post Now" jalan (#1259).

Perhatikan polanya: **yang rusak scheduler-nya, bukan API-nya.** "Post Now"
selalu jalan. Artinya kalau kamu coba, dia jalan. Kalau kamu demokan, dia jalan.
Yang rusak muncul minggu ketiga saat kamu sudah berhenti memperhatikan.

Itu bukan alasan tidak memakainya — 34.532 bintang, push harian, aktif dirawat.
Itu alasan **menguji dua minggu dengan post asli** sebelum mempercayakan jadwal.
Formatnya ada di `templates/pilot-2-minggu.md`, dengan kriteria lulus berupa
angka yang kamu tulis sebelum mulai, supaya kamu tidak menawar sendiri di hari
ke-13.

Satu lagi yang jarang disebut: lisensinya AGPL-3.0. Untuk pemakaianmu sendiri
tidak ada kewajiban apa pun. Tapi kamu punya 100+ klien UMKM — kalau suatu saat
kamu menawarkan Postiz yang sudah kamu modifikasi sebagai layanan ke mereka,
AGPL mewajibkan kamu menyediakan sumber modifikasinya.

---

## 3. "Boleh gak pakai instagrapi?"

**Hermes:** Bisa. Ini konsekuensinya, lalu keputusannya di kamu.

```bash
bash scripts/advise.sh show unofficial-api
```

Yang berubah kalau kamu memilih ini: melanggar ToS Instagram (mereka melarang
akses otomatis tanpa izin tertulis Meta) · kredensial akunmu tersimpan di
server, jadi VPS jebol = akun ikut · endpoint internal berubah tanpa
pemberitahuan · **tidak reversibel** — akun Instagram yang dibanned jarang
kembali dan tidak ada nomor yang bisa ditelepon · lisensinya NOASSERTION, jadi
status hukum pemakaiannya sendiri tidak jelas.

Pertanyaan yang menentukan bukan "aman atau tidak" — jawabannya jelas tidak.
Pertanyaannya: kalau akun ini hilang besok, apa yang terjadi ke omzet bulan
depan?

**Bentuk yang lebih aman untuk tujuan yang sama:**

Pisahkan baca dan tulis. Pakai jalur tidak resmi hanya untuk **membaca** data
publik — riset kompetitor, tren hashtag, analisis komentar. Pakai jalur resmi
untuk **menulis**.

Dua alasan ini bekerja: sebagian besar nilainya memang ada di sisi baca (yang
mengubah bisnis adalah tahu apa yang dicari orang, bukan hemat klik posting),
dan sisi baca jauh lebih jarang memicu blokir daripada sisi tulis.

Kalau kamu tetap mau menulis lewat jalur ini — akun terpisah, volume rendah,
jeda acak, dan siapkan diri kehilangan akunnya. Itu keputusanmu, dan saya
kerjakan.

---

## 4. Ratna (Katering Ratna, Semarang) — "saya mau lihat dulu sebelum tayang"

**Ratna:** Saya pengen Hermes yang nyiapin, tapi saya tetap mau lihat sebelum
tayang. Bisa?

**Hermes:** Itu persis Jalur E.

```bash
bash scripts/advise.sh show browser-tailscale
cat references/browser-tailscale.md
```

Bentuknya: Hermes buka composer di browser yang jalan di VPS, isi caption,
unggah gambar, lalu **berhenti**. Kirim screenshot ke Telegram kamu. Kamu buka
layar VPS itu dari HP lewat Tailscale, periksa, dan kamu yang klik post.

Hermes tidak pernah memegang passwordmu — dia memakai profil browser yang kamu
login sendiri sekali di awal. Mau cabut aksesnya? Hapus foldernya.

Kerugiannya besar dan harus kamu tahu: ini rapuh. Selector berubah, login wall
muncul, captcha muncul, sesi kedaluwarsa. Satu operator melaporkan ~70% run
gagal untuk alur browser-cron 5 menit. Rencanakan memperbaikinya sebulan sekali.

Dan status ToS-nya abu-abu — X menyebut scripting situs non-API bisa berujung
suspensi permanen. Yang membuat ini masih masuk akal adalah manusia di langkah
terakhir. Begitu langkah itu dihapus, kamu pindah ke jalur yang melanggar,
dengan kerapuhan ekstra.

**Satu saran yang mungkin lebih berguna daripada posting-nya:** browser jarak
jauh yang bisa kamu lihat dari HP juga bisa dipakai untuk membaca — screenshot
dashboard penjualan tiap pagi, cek apakah warungmu masih muncul di pencarian
Maps, baca komentar yang tidak bisa diakses lewat API. Itu semua membaca, dan
membaca jauh lebih jarang bermasalah daripada menulis.

Coba itu dulu seminggu. Kalau setup-nya bertahan, baru tambahkan bagian
posting-nya.
