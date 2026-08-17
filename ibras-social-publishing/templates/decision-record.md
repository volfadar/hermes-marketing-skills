# Catatan keputusan — jalur publishing

Salin ke `~/.hermes/business/keputusan-sosial.md`.

Yang mahal bukan memilih jalur yang salah. Yang mahal adalah tidak ingat kenapa
kamu memilihnya, lalu mengulangi analisis yang sama setahun kemudian dengan
ingatan yang sudah berubah.

---

**Tanggal:** ____________
**Yang memutuskan:** ____________

## Dua pertanyaan

**1. Kalau akun ini hilang besok pagi, apa yang terjadi pada omzet bulan depan?**

```
```

**2. Berapa post per minggu yang benar-benar tayang bulan lalu?**
(bukan yang direncanakan — yang benar-benar tayang)

```
____ post/minggu
```

## Batasan yang dimasukkan ke advisor

```bash
python3 scripts/lib/advisor.py recommend \
  --budget ____ \
  --platforms ____________ \
  --skill ____ \
  --volume ____ \
  --account-value ____
```

Urutan yang keluar:

| # | Jalur | Skor |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |

## Yang dipilih

**Jalur:** ____________

**Kenapa jalur ini dan bukan yang di atasnya (kalau bukan #1):**

```
```

**Kerugian yang saya terima dengan sadar** (salin dari `advisor.py show <id>`):

- [ ]
- [ ]
- [ ]

**Yang saya lakukan untuk mengurangi kerugian itu:**

```
```

## Yang akan membuat saya mengubah keputusan ini

Tulis pemicunya sekarang, saat kepala masih dingin:

- [ ] Volume naik di atas ____ post/minggu
- [ ] Biaya melewati $____/bulan
- [ ] Akun kena peringatan/pembatasan
- [ ] Uji dua minggu tidak lulus (`pilot-2-minggu.md`)
- [ ] ____________________________________

## Tinjau ulang

**Tanggal tinjau berikutnya:** ____________ (saran: 3 bulan)

Yang diperiksa saat tinjau:
- angka di `assets/data/platforms.yaml` masih benar? (`bash scripts/doctor.sh` menandai
  sumber yang sudah lewat 90 hari)
- pemicu di atas ada yang kena?
- jalur yang tadinya kalah, sekarang menang? (jalankan `recommend` lagi)
