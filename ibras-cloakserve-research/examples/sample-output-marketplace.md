# Sample output — competitor-marketplace research

Contoh output realistis dari template `competitor-marketplace.txt` dengan
query "kopi arabika". Output ini dihasilkan dari pengujian sebenarnya dengan
deepseek-v4-flash-0731 + cloakserve + CDP.

## Prompt input

```
Riset kompetitor untuk niche "kopi arabika". Langkah:
1. Cek status: bash <SKILL_DIR>/scripts/status.sh
2. Pakai browser (CDP ws://127.0.0.1:9222) buka:
   https://www.tokopedia.com/search?st=product&q=kopi arabika
3. Ambil 5 produk teratas. Untuk masing-masing: nama produk, harga, nama toko,
   lokasi toko, rating, jumlah terjual.
4. Catat pola: range harga, strategi diskon (coret), kata kunci di judul.
Output dalam TABEL MARKDOWN rapi + 3 insight singkat di bawahnya.
Hanya riset publik. Tidak login, tidak form submission, tidak pembelian.
```

## Output Hermes (dalam ~36 detik)

| # | Produk | Harga | Toko | Lokasi | Rating | Terjual |
|---|---|---|---|---|---|---|
| 1 | BREVIA - Kopi Arabika Gunung Halu Candy Cloud Natural Process Coffee | Rp13.179 (coret Rp74.900, -82%) | breviacoffee | Jakarta Timur | 4.9 | 6rb+ |
| 2 | BIJI KOPI 100% FULL ARABICA Commercial Espresso - Sakha Coffee Roastery | Rp9.800 (coret Rp111.900, -91%) | Sakha Coffee Bali | Denpasar | 4.9 | 1rb+ |
| 3 | Kopi Arabika Gayo Guava Berry Natural Process | Rp13.009 | breviacoffee | Jakarta Timur | 5.0 | 3rb+ |
| 4 | KOPI GAYO ARABIKA ACEH PREMIUM (bubuk/bean espresso) | Rp5.000 (coret Rp60.000, -92%) | hancookstore | Medan | 4.8 | 6rb+ |
| 5 | ARUTALA — Kopi Arabika Toraja Tanah Perkebunan | Rp27.500 | arutala.id | Bandung | 4.9 | 500+ |

**3 insight:**

1. **Range harga sangat lebar** (Rp5.000–Rp27.500) dengan mayoritas menggunakan
   strategi "coret harga tinggi + diskon ekstrem" (82-92%). Ini taktik
   lead/upsell khas Tokopedia kopi — harga inti sebenarnya ~Rp10-15rb.
2. **Kata kunci di judul**: nama region/origin ("Gayo Aceh", "Toraja",
   "Gunung Halu") + process ("Natural", "Wine", "Honey") + format
   ("bubuk/bean espresso"). Ini sinyal audience specialty sudah paham origin.
3. **Seller konsentrasi**: 2 dari 5 top listings adalah `breviacoffee` (Jakarta
   Timur) → brand ini dominate keyword "arabika". Kompetisi ketat di seller
   Jakarta/Bali. **Peluang**: positioning sebagai specialty origin spesifik
   (Toraja/Java) yang belum di-cover.

**Catatan Hermes:**
> Saya hanya membuka halaman publik dan mengambil data yang diminta — tidak
> ada login, form submission, atau pembelian. Browser cloakserve masih berjalan
> di port 9222; beri tahu kalau mau saya lanjutkan riset lebih dalam atau
> langsung stop.

## Setelah ini (action items untuk MANUSIA)

Review output di atas, lalu putuskan:
- [ ] Produk mana yang positioning-nya mirip dengan brand saya? (kompetitor langsung)
- [ ] Range harga saya masuk akal? Atau perlu repositioning (premium vs budget)?
- [ ] Origin mana yang under-served? (peluang diferensiasi)
- [ ] 1 insight mana yang akan jadi konten pertama saya minggu ini?

**Jangan auto-act**. Hermes kasih data, kamu yang putuskan.
