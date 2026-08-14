# Menyambungkan Gmail ke Hermes (IMAP + SMTP)

Semua angka dan kutipan di halaman ini diambil dari dokumentasi resmi Google
dan **diverifikasi 12 Agustus 2026**. Kalau Google mengubahnya, halaman ini
salah — cek ulang linknya sebelum mengajarkan ke orang.

---

## Kenapa App Password, bukan password akun

Google: *"An app password is a 16-digit passcode that gives a less secure app or
device permission to access your Google Account."*
([support.google.com/mail/answer/185833](https://support.google.com/mail/answer/185833))

Syaratnya, dari halaman yang sama:

| Syarat | Detail |
|---|---|
| 2-Step Verification | **Wajib aktif.** *"App passwords can only be used with accounts that have 2-Step Verification turned on."* |
| Bukan akun kantor/sekolah | Tidak bisa dipakai kalau *"You're logged into a work, school, or organizational account"* |
| Bukan Advanced Protection | Tidak tersedia kalau Advanced Protection aktif |
| Bukan security-key-only | Tidak tersedia kalau 2SV-nya hanya security key |
| Dibuat di | <https://myaccount.google.com/apppasswords> |

Dua hal yang perlu kamu tahu sebelum memakai jalur ini:

1. **Google sendiri tidak merekomendasikannya.** Kutipan langsung: *"App passwords
   aren't recommended and are unnecessary in most cases."* Mereka mengarahkan ke
   "Sign in with Google" (OAuth). App password tetap jalan dan tetap jalur
   termudah untuk skrip di VPS — tapi kamu memakai pintu yang pemiliknya bilang
   sebaiknya jangan dipakai. Itu fakta yang layak kamu tahu, bukan alasan untuk
   tidak memakainya.
2. **Ganti password akun = semua app password mati.** *"App passwords revoked
   after password change."* Kalau suatu hari Hermes tiba-tiba tidak bisa login,
   ini penyebab nomor satu. Bikin ulang, jalankan `initialize.sh` lagi.

### Kalau akunmu Google Workspace (domain sendiri)

Akun organisasi sering **tidak bisa** membuat app password sama sekali —
tergantung kebijakan admin. Kalau tombolnya tidak ada:

- Minta admin mengizinkan, **atau**
- Pakai OAuth 2.0 (`--provider other` dengan token, di luar cakupan skill ini), **atau**
- Pakai penyedia email lain untuk alamat operasional (Zoho, Fastmail, mailbox.org
  semuanya mendukung app password IMAP/SMTP tanpa drama).

Jangan buang waktu berjam-jam melawan kebijakan admin. Pilih jalur ketiga.

---

## Pengaturan server

```
IMAP   imap.gmail.com   port 993   SSL/TLS
SMTP   smtp.gmail.com   port 587   STARTTLS   ← default skill ini
SMTP   smtp.gmail.com   port 465   SSL/TLS    ← alternatif, kalau 587 diblokir
```

`initialize.sh` sudah mengisi ini otomatis untuk `--provider gmail` dan
`--provider workspace`.

Halaman bantuan Gmail menyebut *"IMAP access is always turned on in Gmail"* —
jadi tidak ada lagi tombol "enable IMAP" yang perlu dicari (itu instruksi lama
yang masih beredar di banyak tutorial).

---

## Setup, langkah demi langkah

```bash
# 1. Aktifkan 2-Step Verification (kalau belum)
#    https://myaccount.google.com/signinoptions/two-step-verification

# 2. Buat App Password
#    https://myaccount.google.com/apppasswords
#    Namanya bebas, mis. "hermes-vps". Google menampilkan 16 karakter
#    dengan spasi, seperti:  abcd efgh ijkl mnop

# 3. Sambungkan
bash scripts/initialize.sh \
  --email kamu@gmail.com \
  --app-password "abcd efgh ijkl mnop" \
  --name "Nama Bisnis Kamu"
```

Spasinya boleh ikut disalin — `initialize.sh` membuangnya sendiri. Ini penyebab
error paling sering nomor dua setelah salah pakai password akun.

---

## Batas kirim — angka resmi

Kalau kamu melewati batas ini, akun **tidak bisa mengirim sampai 24 jam**.
Tidak ada banding, tinggal tunggu.

### Akun @gmail.com pribadi

Dari [support.google.com/mail/answer/22839](https://support.google.com/mail/answer/22839):
batas terpicu pada *"more than 500 recipients in a single email and or more than
500 emails sent in a day"*, dan *"you should be able to send emails again within
1 to 24 hours."*

### Google Workspace

Dari [knowledge.workspace.google.com — Gmail sending limits](https://knowledge.workspace.google.com/admin/gmail/gmail-sending-limits-in-google-workspace):

| Batas | Angka |
|---|---|
| Pesan per hari | **2.000** (500 untuk akun trial) |
| Penerima per pesan (via API) | 500 |
| **Penerima per pesan via SMTP/POP/IMAP** | **100** ← ini jalur yang dipakai skill ini |
| Penerima eksternal per hari | 3.000 |
| Kalau lewat | *"users can't send new messages for up to 24 hours"* |

**Yang penting untuk skill ini:** jalur SMTP/IMAP punya batas penerima
per-pesan **paling ketat** (100), bukan 500 seperti yang sering dikutip orang.
`mailbox.py` memberi peringatan lunak di atas 25 penerima — bukan karena 25
adalah batasnya, tapi karena di atas itu kamu sudah tidak sedang menulis email,
kamu sedang melakukan broadcast, dan broadcast punya aturan mainnya sendiri
(baca `deliverability.md`).

---

## Kalau login ditolak

| Gejala | Penyebab paling sering |
|---|---|
| `IMAP login ditolak` / `SMTPAuthenticationError 535` | Pakai password akun, bukan App Password 16 digit |
| Tadinya jalan, sekarang tidak | Password akun baru diganti → app password dicabut otomatis |
| Tombol app password tidak ada | 2SV belum aktif, atau akun Workspace yang dikunci admin |
| Timeout di port 587 | Provider/VPS memblokir SMTP keluar → coba `--smtp-port 465` |
| Berhasil login, folder aneh | Bahasa antarmuka non-Inggris; `mailbox.py` memakai flag SPECIAL-USE jadi seharusnya tetap benar. Cek `bash scripts/mail.sh folders` |

Diagnosa cepat: `bash scripts/doctor.sh`

---

## Keamanan file config

`~/.hermes-email/config.env` berisi app password dalam bentuk teks biasa,
`chmod 600`. Konsekuensinya, tanpa dibungkus bahasa halus:

- Siapa pun yang bisa jadi root di VPS itu bisa membaca isi email kamu.
- Backup VPS yang tidak terenkripsi ikut membawa password itu.
- Jangan pernah `git add` folder ini.

Ini trade-off yang sama dengan menyimpan API key mana pun di server sendiri.
Bedanya, yang dipertaruhkan di sini adalah seluruh isi kotak surat bisnismu.
Kalau VPS-nya dipakai bersama orang lain, pakai alamat email operasional yang
terpisah dari email pribadi/administratif kamu.

Cabut aksesnya kapan saja, tanpa mengganti password akun:
<https://myaccount.google.com/apppasswords> → hapus app password "hermes-vps".
