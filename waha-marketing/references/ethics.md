# Etika & Hukum — WhatsApp Marketing via WAHA

> Soft warning: ini bukan saran hukum formal. Tapi pelanggaran = risiko
> banned + potensi sanksi UU ITE Indonesia.

## Prinsip dasar

**"Kirim ke orang yang MEMINTA dikirim. Stop kalau mereka minta stop."**

## Opt-in: definisi eksplisit

**Opt-in SAH:**
- Orang tersebut secara aktif mengisi form dengan checkbox "saya mau info via WA"
- Reply ke WA kamu dengan keyword "YES" / "SUBSCRIBE"
- Consent di checkout produk: "kirim update via WA" (checked opt-in, bukan unchecked)
- Mendaftar event dengan consent WA eksplisit

**Opt-in TIDAK SAH (jangan dipakai):**
- Nomor dari business card yang kamu kumpulkan
- Lead dari scraping LinkedIn/Instagram
- Pembeli 3 tahun lalu yang tidak pernah consent newsletter
- Anggota grup WA publik (keanggotaan grup ≠ consent DM)
- "Mereka pasti tertarik" ( assumption tidak = consent)
- Email list yang consent untuk email, bukan WA

## Opt-out: wajib

Setiap broadcast HARUS punya cara keluar:
- "Balas STOP untuk berhenti"
- Atau "unsubscribe" link/reply

**Saat ada yang opt-out:**
1. Hapus dari list aktif segera (dalam 24 jam)
2. Simpan di blacklist (`opt_out.csv`) supaya tidak tak sengaja dikirim lagi
3. **Jangan pernah** kirim ke nomor itu lagi, walau mereka pernah opt-in

## UU ITE Indonesia (UU 19/2016, UU 11/2008)

**Pasal relevan:**
- Pasal 28(1): transmisi informasi yang melanggar kesusilaan
- Pasal 28(2): pemerasan/pengancaman kekerasan
- Pasal 27(3): fitnah dan penghinaan

**Praktik WA marketing bisa relevan kalau:**
- Kamu kirim konten yang melanggar kesusilaan → pidana
- Kamu kirim SARA/ujaran kebencian → pidana
- Kamu pakai data orang tanpa consent → masalah UU PDP (Pelindungan Data Pribadi, UU 27/2022)

**Best practice Indonesia:**
- Selalu disclose identitas (siapa kamu, brand apa)
- Hanya kirim di jam wajar (9am-9pm WIB)
- Bahasa sopan, tidak menekan
- Hanya ke yang opt-in eksplisit
- Opt-out mechanism wajib

## GDPR / international (kalau audience global)

Kalau audience kamu include orang di EU/UK:
- Perlu **explicit consent** (bukan pre-ticked box)
- Perlu **easy opt-out** di tiap pesan
- Perlu **privacy notice** yang jelas
- Hak untuk **request deletion** of their data

## Content yang DILARANG

❌ Jangan kirim via WA:
- Konten dewasa / SARA / ujaran kebencian
- Misinformasi / hoaks
- Penipuan / phishing / scam
- Spam multi-level marketing tanpa disclosure
- Produk ilegal / tertentu yang dilarang platform
- Promosi kompetisi tanpa aturan jelas
- Penghinaan / fitnah individu/brand lain

## Disclosure (rekomendasi)

Di broadcast pertama ke kontak baru, kasih tahu:
- Siapa kamu dan brand kamu
- Darimana kamu dapat nomor mereka (form mana, event mana)
- Cara opt-out

```text
Halo {name}, saya Andi dari Kopi Senja. Kamu dapat pesan ini karena
isi form di stand kami di event Pasar Seni Jogja kemarin. Saya akan
kirim update produk 1-2x sebulan. Kalau mau berhenti, balas STOP ya.
```

Transparansi ini justru meningkatkan trust dan menurunkan report rate.

## Kill-switch etis

Kalau:
- Kamu ragu apakah list ini benar-benar opt-in → **jangan broadcast**
- Kamu merasa content "agak spammy" → **rewrite atau skip**
- Reply rate turun drastis dari biasanya → **pause, audit**
- Ada report-as-spam → **stop, audit list, perbaiki**
- Akun di-shadow-restrict → **STOP semua outreach, baca anti-ban.md**

## Audit trail

Simpan bukti opt-in untuk setiap kontak:
- Source (form/event/keyword)
- Timestamp opt-in
- IP / user agent (kalau dari form)

`lib/broadcast.py` support `opt_in_source` field di CSV. Isi dengan sumber
spesifik. Kalau ada komplain/report, kamu bisa tunjukkan consent.

## Sanksi (selain banned)

- **Reputasi brand rusak** — 1 viral tweet "brand X spam WA" = masalah besar
- **Whistleblower platform** — WhatsApp punya tombol report yang mengglobal
- **Sanksi hukum** — UU PDP: denda sampai 2% pendapatan tahunan
- **Costumer trust** — sekali kena report, susah recover

## Kontrak diri (template)

Sebelum mulai WA marketing, tulis 1 kalimat komitmen:

> "Saya [nama], akan hanya kirim WA ke orang yang eksplisit opt-in.
> Saya akan kasih opt-out di tiap broadcast. Saya akan hentikan
> kalau ada yang minta berhenti. Saya tidak akan jadi spammer."

Tempel di depan meja kerja. Itu anchor etis kamu.
