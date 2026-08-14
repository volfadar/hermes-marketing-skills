# Broadcast Guide — Cara Bikin Broadcast Sehat

> **Baca `anti-ban.md` dulu.** Ini panduan operasional, bukan safety briefing.

## Kapan broadcast cocok (dan kapan tidak)

**✅ Cocok:**
- Update produk ke pelanggan yang eksplisit opt-in "mau info via WA"
- Pengingat appointment (kalau mereka booking)
- Follow-up post-purchase ("gimana produknya?")
- Undangan event ke yang sudah daftar
- Newsletter ringan (1x/minggu, value dulu)

**❌ Tidak cocok:**
- Cold outreach ke lead yang belum consent WA
- Promo harian ke list besar (spam probability tinggi)
- "Testing" broadcast ke 100 orang untuk lihat response
- Broadcast di luar jam kerja (tengah malam)
- Produk yang sama persis 5x seminggu

## Format CSV kontak

```csv
phone,name,opt_in,opt_in_source,labels
6281234567890,Andi,yes,landing-form-2026-08,customer
6281234567891,Budi,yes,wa-reply-yes,lead
6281234567892,Citra,yes,checkout-consent,customer,vip
```

**Kolom wajib:** `phone`, `opt_in` (yes/no).
**Opsional:** `name` (untuk personalisasi `{name}`), `opt_in_source` (audit trail), `labels`.

**Aturan:** `lib/broadcast.py` SKIP baris dengan `opt_in != yes`. Bukan saran — hard rule di skill ini.

## Format template pesan

`templates.txt` — satu pesan per baris. Pakai `{name}` untuk personalisasi:

```text
Halo {name}, ini update dari Kopi Senja. Minggu ini ada biji single origin Toraja baru, stok terbatas. Boleh kirim detailnya?
Hai {name}, cuma mau kabarin kalau po senja special kita weekend ini full. Next batch Senin depan ya — mau kami reserve 1 buat {name}?
{name}, selamat siang! Ada promo buy 1 get 1 untuk member, hari ini aja sampai jam 9 malem. Mau?
```

**Aturan penulisan:**
- ✅ Minimal 5 variant (skill estimate risk kalau <3)
- ✅ Pakai `{name}` di tiap variant
- ✅ Pertanyaan di akhir (ajak reply, bukan CTA pushy)
- ✅ Pendek (1-3 kalimat). Orang baca WA cepat
- ❌ Jangan identik dengan yang km kirim minggu lalu
- ❌ Jangan pakai link kecuali memang perlu (kurangi spam-flag)
- ❌ Jangan ALL CAPS, jangan emoji spam (max 1-2)

## Alur broadcast lengkap

### 1. Persiapan (sehari sebelum)
```bash
# Pastikan WAHA connected
bash scripts/doctor.sh

# Review list kontak
# Hitung: sudah opt-in semua? Berapa banyak? Umur akun berapa hari?
```

### 2. Dry-run (validasi plan tanpa kirim)
```bash
bash scripts/broadcast-helper.sh \
  --contacts customers.csv \
  --templates promo-mingguan.txt \
  --dry-run
```

Output:
```
Contacts total:     85
  Opted-in:         85
  No opt-in (skip): 0
Message templates: 5 (rotation)
Est. duration:     ~52 min
Spam risk:          LOW

DRY RUN — no messages will be sent.
  [1] 628xxx (Andi): "Halo Andi, ini update dari Kopi Senja..."
  ...
```

**Kalau `Spam risk: HIGH/BLOCK`:** jangan lanjut. Reduce list, age account, add variants.

### 3. Actually send (double confirmation)
```bash
bash scripts/broadcast-helper.sh \
  --contacts customers.csv \
  --templates promo-mingguan.txt \
  --i-confirm-optin
# Akan minta konfirmasi: ketik nama session untuk proceed
```

### 4. Monitor
- Lihat log real-time (printed ke stderr)
- Kalau muncul `HTTP 463` → BATAL. Halt. Baca anti-ban.md.
- Kalau ada error individual (network, dll) → log, lanjut

### 5. Emergency stop (kalau perlu)
```bash
bash scripts/emergency-halt.sh
# Broadcast stop di next message boundary
```

### 6. Setelah selesai
- Review state: `~/.waha-marketing/state/sent.json` (siapa dapat apa, kapan)
- Tunggu reply. Pertanyaan berulang (harga/ongkir/jam buka) boleh dijawab otomatis lewat FAQ; komplain, janji uang, dan klaim kesehatan selalu naik ke pemiliknya.
- 24 jam kemudian: cek ada berapa yang reply/block/report.

## Broadcast scheduling (cron Hermes)

**Yang BENAR (route output ke kamu untuk review, BUKAN auto-broadcast):**
```bash
hermes cron add "0 10 * * 1" "Draft broadcast WA mingguan untuk list customer (CSV di ~/waha/customers.csv). Pilih 1 dari 5 template di ~/waha/templates.txt secara random, personalisasi {name}, dan tampilkan 5 preview untuk saya review. JANGAN auto-send. Hanya draft." --name "Draft broadcast WA mingguan" --deliver telegram
```

**Yang SALAH (auto-broadcast tanpa review = banned):**
```bash
# JANGAN LAKUKAN INI
hermes cron add "0 10 * * *" "kirim promo ke semua customer via WAHA" --deliver ...
```

## Opt-in collection (cara benar dapat list)

**Sumber opt-in yang sah:**
1. **Landing page form** dengan checkbox eksplisit "Saya mau info via WA"
2. **WA reply keyword** — broadcast "Ketuk YES untuk join update" → mereka reply YES
3. **Checkout consent** — checkbox di form pembelian
4. **Event workshop** — form pendaftaran dengan checkbox
5. **Lead magnet** — download PDF, consent WA di form

**Yang bukan opt-in (jangan masukkan ke CSV):**
- Kartu nama dari networking event
- Daftar peserta event yang tidak consent WA
- Nomor dari grup WA tanpa consent personal
- Lead LinkedIn/email yang belum consent WA eksplisit

## Opt-out mechanism (wajib)

Di tiap broadcast, kasih cara keluar:
- "Balik STOP kalau mau berhenti"
- Atau "Reply 'unsubscribe' untuk keluar dari list"

Kalau ada yang STOP:
1. Hapus dari CSV aktif
2. Add ke blacklist (`opt_out.csv`)
3. **JANGAN pernah** kirim lagi ke nomor itu

## Metrik post-broadcast (yang penting)

| Metrik | Target sehat | Bahaya |
|---|---|---|
| Reply rate | > 5% | < 1% = list dingin / content tidak relevan |
| Block rate | < 1% | > 3% = masalah serius, hentikan |
| Report-as-spam | 0 | ≥ 1 = review content dan opt-in source |
| Opt-out rate | < 5% | > 10% = terlalu sering / content tidak valuable |

**Kalau block/report rate tinggi:** STOP broadcast 2 minggu. Audit list, content, frequency.

## Split testing (tips)

Rotate template bukan cuma untuk anti-ban — juga untuk A/B test:
- Template A: 50% kontak
- Template B: 50% kontak
- Bandingkan reply rate

`lib/broadcast.py` rotate otomatis (`templates[i % len(templates)]`). Untuk A/B strict, buat 2 CSV dan jalankan di hari berbeda.
