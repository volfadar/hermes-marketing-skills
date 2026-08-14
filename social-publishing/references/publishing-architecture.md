# Arsitektur publishing — kalau Hermes benar-benar menerbitkan

Halaman ini untuk Jalur C (API resmi) dan Jalur D (self-host). Kalau kamu di
Jalur A atau B, kamu tidak butuh ini.

Isinya diambil dari Laporan A, laporan riset yang paling bagus arsitekturnya
di repo ini — 32 kutipan primer platform, nol blog vendor.

---

## Bentuknya: agen merencanakan, antrian kecil yang mengeksekusi

Kesalahan yang paling umum adalah membiarkan model bahasa memanggil API publish
langsung. Yang salah bukan idenya — yang salah adalah tidak ada tempat untuk
menyimpan "apakah ini sudah terkirim?".

```
Hermes                    Antrian (SQLite/file)         Adapter resmi
──────                    ────────────────────          ─────────────
menulis draft   ────►     draft
                            │  kamu approve dari Telegram
                            ▼
                          approved
                            │  waktunya tiba
                            ▼
                          due
                            │  satu worker mengambil
                            ▼
                          leased  ─────────────────►    POST /media_publish
                            │                             │
                            │  ◄──────────────────────────┘
                            ▼
                          executed
                            │  cek ulang: post-nya benar-benar ada?
                            ▼
                          verified
```

Enam status, dan tiap perpindahan tercatat. Yang penting bukan jumlah
statusnya — yang penting adalah **`leased` dan `verified` itu ada**.

---

## `leased` — kenapa perlu

Tanpa status `leased`, dua worker (atau satu worker yang di-restart) bisa
mengambil pekerjaan yang sama. Hasilnya post ganda.

Postiz issue **#832** adalah persis kelas kegagalan ini: *"Continuous Reposting
Loop for Standalone Instagram Integration - Risk! Account flagged"*. Loop
repost membuat akun ditandai.

Bentuk minimalnya:

```sql
UPDATE queue SET status='leased', leased_by=?, leased_until=?
WHERE id=? AND status='due' AND (leased_until IS NULL OR leased_until < ?);
-- kalau 0 baris berubah, worker lain sudah mengambilnya. Jangan lanjut.
```

---

## Idempotency key — kenapa lebih penting lagi

Jaringan gagal di tempat yang paling merepotkan: **setelah** platform menerima
post, **sebelum** kamu menerima jawabannya. Kamu retry, dan sekarang ada dua
post.

Solusinya: setiap item antrian punya kunci unik yang stabil, dan kunci itu
disimpan bersama ID post yang dikembalikan platform.

```
idem_key = sha256(akun + isi_caption + hash_gambar + slot_waktu)[:16]
```

Sebelum mengirim: cek apakah `idem_key` ini sudah punya `platform_post_id`.
Kalau sudah, jangan kirim — ambil hasilnya dari catatan.

Ini yang membedakan sistem publishing dari skrip yang kebetulan jalan.

---

## `verified` — jangan percaya HTTP 200

Postiz issue **#1724** (post IG tersangkut di `QUEUE`) dan **#1259** (post
terjadwal terlewat padahal "Post Now" jalan) menunjukkan hal yang sama: status
internal antrian bisa mengatakan sesuatu yang tidak terjadi di platform.

Jadi langkah terakhir bukan "API mengembalikan 200". Langkah terakhir adalah:
**ambil post-nya lagi dari platform dan pastikan dia ada.**

```
GET /{ig-media-id}?fields=id,permalink,timestamp
```

Kalau tidak ada setelah 60 detik → tandai `failed`, beri tahu pemilik, jangan
retry otomatis. Retry otomatis pada kegagalan yang tidak dipahami adalah cara
membuat #832 terjadi.

---

## Kuota, dihitung sebelum dijadwalkan

| Platform | Kuota | Sumber |
|---|---|---|
| Instagram | 100 post / 24 jam bergerak | Meta Content Publishing |
| Threads | 250 post + 1.000 reply / 24 jam | Threads API overview |
| X | tidak ada kuota — ada tagihan: $0,015/post, $0,200 dengan URL | X pricing |

"24-hour moving period" berarti bukan reset tengah malam. Hitung post dalam 24
jam terakhir, bukan hari kalender.

Untuk X, kuotanya diganti biaya. Itu mengubah pertanyaannya dari "boleh berapa
kali?" jadi "berapa yang mau kamu bayar?" — dan post dengan URL 13x lebih mahal,
yang seharusnya mengubah cara kamu menulis.

---

## Uji dua minggu, dengan kriteria angka

Jangan ajarkan atau andalkan jalur publishing yang belum diuji. Laporan A
menyertakan bentuk ujinya, dan skill ini memakainya
(`templates/pilot-2-minggu.md`).

Kriteria lulus, ditentukan **sebelum** mulai:

| Ukuran | Ambang lulus |
|---|---|
| Post terjadwal yang benar-benar tayang | ≥ 95% |
| Post ganda | **0** |
| Post yang tayang tapi tidak terverifikasi | 0 |
| Intervensi manual yang tidak direncanakan | ≤ 2 dalam 2 minggu |
| Peringatan/pembatasan akun | **0** |

Kalau ada satu saja yang tidak lulus, jangan naikkan volumenya. Perbaiki dulu
atau turun satu jalur.

Angka-angka ini ditulis sebelum uji dimulai supaya kamu tidak menawar dengan
dirimu sendiri di hari ke-13.

---

## Yang tetap dipegang manusia

Dari Laporan A dan dari issue OpenClaw #56897 (*instruksi di `SKILL.md` bukan
penegakan*):

| Keputusan | Siapa |
|---|---|
| Apa yang ditulis | Hermes menulis draft |
| Apakah ini layak tayang | **Manusia**, sekali klik |
| Kapan tayang | Antrian, dari jadwal yang disetujui |
| Apakah benar tayang | Kode, lewat verifikasi |
| Apa yang dilakukan saat gagal | **Manusia**, karena retry buta itu berbahaya |

Baris terakhir yang paling sering dilewati. Sistem yang retry sendiri saat
gagal terlihat lebih canggih dan justru itulah yang membuat akun ditandai.
