# Uji dua minggu — sebelum mempercayakan jadwal ke mesin

Salin file ini ke `~/.hermes/business/pilot-sosial.md` dan isi.

Alasan uji ini ada: kegagalan paling mahal di seluruh riset repo ini adalah
kegagalan **scheduler**, dan scheduler tidak pernah rusak saat sedang ditonton.
Postiz #1259 — post terjadwal terlewat padahal "Post Now" jalan. Postiz #832 —
loop repost membuat akun ditandai.

---

## Isi dulu, sebelum mulai

| | |
|---|---|
| Jalur yang diuji | ☐ official-api ☐ selfhost-scheduler ☐ browser-tailscale |
| Akun yang dipakai | |
| **Akun ini bisa diganti?** | ☐ ya, seminggu ☐ tidak, ini kanal utama |
| Platform | |
| Tanggal mulai | |
| Tanggal selesai | |
| Volume selama uji | ____ post/minggu (pakai volume ASLI, bukan target) |

> Kalau kotak "tidak, ini kanal utama" dicentang, pertimbangkan menguji dengan
> akun kedua dulu. Uji yang mempertaruhkan aset yang tidak tergantikan bukan
> uji, itu taruhan.

---

## Kriteria lulus — tulis SEBELUM mulai

Ini ditulis di depan supaya kamu tidak menawar dengan dirimu sendiri di hari
ke-13.

| Ukuran | Ambang | Hasil |
|---|---|---|
| Post terjadwal yang benar-benar tayang | ≥ 95% | ____ % |
| Post ganda | **0** | ____ |
| Post yang tayang tapi tidak terverifikasi | 0 | ____ |
| Intervensi manual tak terencana | ≤ 2 | ____ |
| Peringatan / pembatasan akun | **0** | ____ |

**Satu saja tidak lulus → jangan naikkan volume.** Perbaiki, atau turun satu
jalur.

---

## Catatan harian

| Hari | Dijadwalkan | Tayang | Terverifikasi | Catatan |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |
| 9 | | | | |
| 10 | | | | |
| 11 | | | | |
| 12 | | | | |
| 13 | | | | |
| 14 | | | | |

**"Terverifikasi"** artinya kamu (atau kode) mengambil post itu lagi dari
platform dan memastikan dia ada. HTTP 200 dari API bukan verifikasi —
Postiz #1724 adalah post yang tersangkut di `QUEUE` sementara semuanya
terlihat baik-baik saja.

---

## Yang khusus diperiksa per jalur

**official-api**
- [ ] Token belum kedaluwarsa di akhir minggu kedua (kapan kedaluwarsanya? ____)
- [ ] Sisa kuota dihitung sebelum menjadwalkan, bukan setelah gagal
- [ ] Retry tidak pernah menghasilkan post kedua (uji dengan sengaja memutus jaringan)

**selfhost-scheduler**
- [ ] Post gambar diuji terpisah dari post teks (Threads: #1364)
- [ ] Reply/CTA terjadwal diuji terpisah dari post biasa (X: #1581)
- [ ] Server di-restart sekali di tengah uji — antrian tetap benar?
- [ ] Backup database antrian pernah dicoba dipulihkan, bukan cuma dibuat

**browser-tailscale**
- [ ] Berapa run yang gagal? ____ dari ____ (bandingkan dengan ~70% di #78602)
- [ ] Login masih bertahan di hari ke-14?
- [ ] Screenshot sampai ke HP setiap kali?
- [ ] Skrip benar-benar berhenti sebelum tombol publish — dibuktikan, bukan diasumsikan

---

## Kesimpulan

```
Tanggal: ____________

Lulus / Tidak lulus:  ____________

Kalau tidak lulus, yang gagal:
  ________________________________________________

Keputusan:
  ☐ lanjut ke produksi dengan volume ____/minggu
  ☐ ulangi uji setelah perbaikan: ____________
  ☐ turun ke jalur: ____________

Yang akan saya periksa tiap minggu setelah ini:
  ________________________________________________
```

Simpan hasilnya. Enam bulan lagi kamu akan ditanya (oleh dirimu sendiri)
kenapa memilih jalur ini, dan ingatanmu akan sudah berubah.
