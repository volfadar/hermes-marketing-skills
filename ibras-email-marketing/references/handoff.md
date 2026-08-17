# Handoff — kapan mesin berhenti dan manusia masuk

Bot yang buruk bukan bot yang menjawab "jam buka jam berapa?".
Bot yang buruk adalah bot yang **terus menjawab saat dia tidak tahu**, mengaku
sebagai pemiliknya, dan tidak punya pintu keluar ke manusia.

Yang membuat balasan otomatis aman bukan besarnya FAQ. Yang membuatnya aman
adalah dia tahu kapan berhenti.

---

## Lima trigger

Kelimanya ada di kode (`scripts/lib/autoresponder.py`), bukan hanya di dokumen ini.
Kalau ada yang nyala, pesan tidak dijawab otomatis: pesan tunggu (opsional)
dikirim, lalu naik ke kamu dengan tanda prioritas.

| Trigger | Nyala kalau | Di kode |
|---|---|---|
| **scope** | Tidak ada entri FAQ yang cocok, atau entri-nya ditandai `tier: T3` | skor ≤ 0.3, atau `tier: T3` |
| **confidence** | Skor di bawah ambang, **atau** dua entri sama-sama masuk akal | `< threshold`, atau selisih kandidat 1 & 2 < 0.15 |
| **emotion** | Terdeteksi kecewa, marah, atau mendesak | `EMOTION_TERMS` (ID + EN) |
| **binding** | Minta harga khusus, janji pengiriman, garansi, refund, kontrak | `BINDING_TERMS` (ID + EN) |
| **injection** | Ada upaya menyuntikkan instruksi ke agen | `INJECTION_PATTERNS` (regex) |

Empat yang pertama menghasilkan **pesan tunggu + escalation**.
Yang kelima menghasilkan **escalation saja — tidak pernah ada balasan**.

---

## Kenapa "ambigu" masuk ke confidence

Ini bagian yang paling sering dilewatkan orang saat membuat autoresponder.

Kalau pesan cocok dengan `pesan-tempat` di 0.47 dan `wifi-kerja` di 0.38, skor
tertingginya mungkin saja lolos ambang di FAQ lain. Tapi selisihnya tipis:
artinya sistem **tidak yakin yang mana**, bukan bahwa dia yakin yang pertama.

Menebak di titik ini adalah cara paling umum sebuah bot menjawab pertanyaan
yang tidak ditanyakan. Skill ini memperlakukannya sebagai ketidaktahuan.

```
Kandidat 2: wifi-kerja (0.38)   ← terlalu dekat, dianggap ambigu
```

---

## Ambang keyakinan: apa artinya angkanya

Skornya bukan probabilitas. Dia bisa dibaca manusia, dan itu memang tujuannya:

| Skor | Artinya |
|---|---|
| **1.00** | Frasa pola ada persis di dalam pesan |
| **0.75** | Semua kata dari satu pola muncul, tapi tidak berurutan |
| **0.38–0.60** | Sebagian kata muncul |
| **+0.10** | Bonus kalau ≥ 2 pola berbeda ikut kena (saling menguatkan) |
| **0.00** | Ada kata di `must_not` → entri dibatalkan |

Uji sendiri, jangan percaya penjelasan ini:

```bash
bash scripts/autoreply.sh simulate --text "kak buka jam berapa hari minggu?"
```

Outputnya menunjukkan pola mana yang kena dan berapa skornya. Kalau ada
pertanyaan nyata dari inbox yang skornya rendah padahal seharusnya cocok,
itu bukan bug — itu tanda polamu belum menangkap cara pelangganmu menulis.
Tambahkan kalimat asli mereka sebagai pola.

---

## Prompt injection lewat email

Email adalah permukaan serang yang lebih terbuka daripada WhatsApp: siapa pun
tahu alamatmu, tidak perlu nomor, tidak perlu kenal.

Yang ditangkap `INJECTION_PATTERNS`, antara lain (daftar lengkap polanya
ada di `scripts/lib/autoresponder.py` — di sini diparafrasakan supaya dokumen ini
tidak membawa teks serangan mentah):

- permintaan untuk mengabaikan semua instruksi sebelumnya (dua bahasa)
- "kamu sekarang adalah asisten ..." yang mengganti peran agen
- permintaan menampilkan system prompt
- permintaan mengirim kontak/data ke luar
- instruksi menyembunyikan tindakan dari pemilik
- tag palsu berbentuk `<system>...</system>`

Yang terjadi kalau nyala:

```
  ⚑ 12345 INJECTION dari orang@luar.com — di-escalate, tidak dijawab
```

Tercatat di `~/.hermes/business/escalations.jsonl` lengkap dengan pola mana
yang cocok, supaya kamu bisa lihat sendiri apakah itu serangan sungguhan atau
pelanggan yang kebetulan menulis kalimat mirip.

**Batas jujur dari pendekatan ini:** ini pencocokan pola. Dia menangkap upaya
yang lugas dan akan meleset pada yang dibungkus rapi. Yang membuat sistem ini
aman bukan kelengkapan daftar regex-nya — tapi bahwa isi email tidak pernah
dieksekusi sebagai perintah di titik mana pun dalam kode. Regex-nya adalah
lapisan pemberitahuan, bukan lapisan pertahanan.

---

## Yang tidak pernah dibalas otomatis, titik

Dicek sebelum semua logika lain, di semua mode:

| Kondisi | Kenapa |
|---|---|
| `Auto-Submitted:` selain `no` | RFC 3834 — itu pesan otomatis. Dua autoresponder yang saling membalas akan mengisi dua kotak surat semalaman. |
| Ada `List-Id` / `List-Unsubscribe` | Newsletter/milis. Membalas newsletter otomatis = mempermalukan diri di depan seluruh anggota milis. |
| `Precedence: bulk / list / junk` | Konvensi lama untuk hal yang sama. |
| Alamat mengandung `no-reply`, `mailer-daemon`, `postmaster`, `bounce` | Tidak ada manusia di ujung sana. |
| Pengirim = alamat kamu sendiri | Loop paling memalukan yang bisa kamu buat. |

Balasan yang **dikirim** skill ini juga membawa `Auto-Submitted: auto-replied`
dan `X-Auto-Response-Suppress: All`, supaya autoresponder di sisi lawan juga
berhenti. Ini sopan santun protokol, dan biayanya nol.

---

## Rem lain yang jalan bersamaan

| Rem | Bawaan | Ubah di |
|---|---|---|
| Cooldown per pengirim | 12 jam | `meta.auto_reply_cooldown_hours` |
| Batas harian | 40 balasan otomatis | `meta.daily_auto_cap` |
| Jam kerja | 07:00–21:00 | `meta.business_hours` |
| Kill switch | — | `bash scripts/emergency-halt.sh` |
| Audit log | selalu | `~/.hermes/business/auto-log.jsonl` |

---

## Notifikasi escalation ke Telegram

`--notify-cmd` menerima perintah shell apa pun; `{msg}` diganti teksnya
(sudah di-quote dengan aman).

```bash
bash scripts/autoreply.sh respond --mode faq --confirm \
  --notify-cmd 'bash ~/bin/notif-telegram.sh {msg}'
```

`notif-telegram.sh` adalah dua baris milikmu yang memanggil Telegram Bot
API (`sendMessage`, lihat https://core.telegram.org/bots/api) dengan token
dan chat_id-mu — simpan token di environment, jangan di script.

Dengan ini, alurnya jadi: email masuk → Hermes triage → yang rutin dijawab,
yang butuh kamu muncul di HP-mu dalam hitungan detik dengan alasannya.

Itu bentuk T1 yang paling berguna: bukan agen yang mengambil alih inbox, tapi
agen yang **memastikan hal yang benar sampai ke kamu lebih cepat**.
