# Sampai ke inbox, bukan ke spam

Email punya masalah yang tidak dimiliki WhatsApp: **kamu bisa mengirim dengan
sukses dan tetap tidak dibaca**, karena SMTP bilang OK sementara Gmail penerima
menaruhnya di Spam tanpa memberitahu siapa pun.

Semua angka di bawah diverifikasi 12 Agustus 2026 dari dokumentasi Google.

---

## Aturan Google untuk SEMUA pengirim (berlaku sejak 1 Februari 2024)

Dari [Email sender guidelines](https://support.google.com/a/answer/81126):

| Aturan | Kutipan |
|---|---|
| Autentikasi | *"Set up SPF or DKIM email authentication for your sending domains"* |
| DNS | *"Ensure that sending domains or IPs have valid forward and reverse DNS records"* |
| Enkripsi | *"Use a TLS connection for transmitting email"* |
| Spam rate | *"Keep spam rates reported in Postmaster Tools below 0.3%"* |
| Format | *"Format messages according to the Internet Message Format standard, RFC 5322"* |

**Kalau kamu mengirim dari `@gmail.com` lewat `smtp.gmail.com`, SPF/DKIM sudah
diurus Google.** Itu satu keuntungan nyata dari jalur ini yang jarang disebut.

Kalau kamu memakai domain sendiri (`kamu@bisnismu.com`), SPF/DKIM/DMARC adalah
tanggung jawabmu, dan tanpa itu email bisnismu akan makin sering masuk spam.

---

## Aturan tambahan untuk bulk sender

Ambang: **lebih dari 5.000 pesan per hari ke akun Gmail.**

| Aturan | Detail |
|---|---|
| SPF **dan** DKIM | Keduanya, bukan salah satu |
| DMARC | Harus ada; policy boleh `p=none` |
| Alignment | *"the domain in the sender's From: header must be aligned with either the SPF domain or the DKIM domain"* |
| One-click unsubscribe | *"Marketing messages and subscribed messages must support one-click unsubscribe"* |
| Spam rate | Di bawah **0.30%**; Google menyarankan menjaga di bawah **0.10%** |

Header one-click yang diminta (RFC 8058):

```
List-Unsubscribe: <https://domainmu.com/unsubscribe/abc123>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

`mailbox.py send --unsubscribe-url https://...` memasang keduanya.

**Konteks jujur untuk pembaca workshop ini:** kalau bisnismu warung kopi atau
usaha rumahan dengan 600 kontak, kamu tidak akan pernah menyentuh 5.000/hari.
Aturan bulk tidak berlaku untukmu. Yang berlaku adalah baris terakhir tabel
pertama — spam rate — dan itu ditentukan oleh apakah orang menekan tombol
"Report spam", bukan oleh volume.

---

## Spam rate 0.3% dalam angka yang bisa kamu rasakan

0.3% dari 600 penerima = **2 orang**.

Dua orang menekan "Report spam" dan reputasi pengirimmu rusak untuk semua
penerima berikutnya — termasuk email transaksional yang sah, konfirmasi
pesanan, invoice.

Itu sebabnya pertanyaan "boleh tidak kirim ke 600 kontak" bukan pertanyaan
teknis. Secara teknis: boleh, di bawah batas 2.000/hari Workspace. Secara
praktis: dua orang yang tidak merasa pernah mendaftar bisa membuat email
bisnismu tidak sampai lagi selama berbulan-bulan.

---

## Apa yang membuat orang menekan "Report spam"

Bukan isi emailnya. Hampir selalu salah satu dari tiga ini:

1. **Mereka tidak ingat pernah mendaftar.** Jarak antara opt-in dan email
   pertama terlalu jauh, atau opt-in-nya tidak pernah benar-benar terjadi.
2. **Tidak jelas cara berhenti.** Kalau tombol unsubscribe susah dicari,
   "Report spam" adalah tombol berhenti yang tersedia.
3. **Frekuensinya berubah tanpa pemberitahuan.** Dari sebulan sekali jadi
   tiga kali seminggu.

Ketiganya bisa dicegah dengan menulis, di email pertama, dari mana kamu dapat
alamat mereka. Transparansi ini menurunkan report rate, bukan menaikkannya.

---

## Praktik yang berlaku di skala kecil

| Praktik | Kenapa |
|---|---|
| Satu email = satu penerima di `To:` | Penerima berjajar di `To:` berarti mereka saling melihat alamat email satu sama lain — dan itu insiden data pribadi, bukan sekadar kurang rapi |
| Kalau harus banyak, pakai `--bcc` | Minimum yang bisa diterima |
| Reply-to thread yang benar | `mailbox.py reply` memasang `In-Reply-To` + `References`. Balasan yang memutus thread terlihat seperti mesin |
| Plain text lebih dulu | Email teks biasa dari usaha kecil lebih jarang masuk spam daripada HTML penuh gambar |
| Jangan kirim tengah malam | Bukan soal spam filter, soal orangnya |
| Alamat operasional terpisah | Kalau reputasinya rusak, email pribadi/administratif kamu tidak ikut |

---

## Kalau email kamu mulai masuk spam

Urutan diagnosa, dari yang paling sering:

1. **Cek Postmaster Tools** (butuh domain sendiri):
   <https://postmaster.google.com> — lihat spam rate dan reputasi domain.
2. **Kirim tes ke akun Gmail lain**, buka "Show original", cek baris
   `SPF: PASS` / `DKIM: PASS` / `DMARC: PASS`.
3. **Berhenti mengirim broadcast**, lanjutkan hanya email 1-ke-1 selama 2 minggu.
   Reputasi membaik dengan perilaku normal, tidak dengan permintaan banding.
4. **Audit daftar kontakmu.** Kalau kamu tidak bisa menunjukkan kapan dan di
   mana seseorang memberi izin, dia tidak seharusnya ada di daftar itu.

Tidak ada tombol banding untuk reputasi pengirim. Yang ada hanya waktu dan
perilaku yang berubah.

---

## Batas kirim (ringkas)

| | Per hari | Penerima/pesan lewat SMTP |
|---|---|---|
| `@gmail.com` pribadi | 500 | 500 |
| Google Workspace | 2.000 (500 kalau trial) | **100** |

Lewat batas = tidak bisa kirim **sampai 24 jam**. Sumber dan kutipan lengkap:
`gmail-setup.md`.
