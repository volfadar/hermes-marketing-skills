# Contoh pemakaian

Semua contoh di sini bisa dijalankan apa adanya setelah `initialize.sh`.

---

## Sehari-hari

```bash
# Pagi: apa yang masuk semalam
bash scripts/mail.sh list --unread --limit 20

# Baca satu
bash scripts/mail.sh read 18432

# Cari (sintaks Gmail)
bash scripts/mail.sh search "from:supplier newer_than:14d has:attachment"
bash scripts/mail.sh search "subject:invoice is:unread"
bash scripts/mail.sh search "label:klien older_than:90d"

# Seluruh percakapan, bukan satu pesan
bash scripts/mail.sh thread 18432
```

## Merapikan inbox

```bash
# Beri label lalu keluarkan dari INBOX
bash scripts/mail.sh label 18432 --add "Klien/2026" --confirm
bash scripts/mail.sh archive 18432 --confirm

# Buang (masih bisa dikembalikan 30 hari)
bash scripts/mail.sh trash 18432 --confirm
bash scripts/mail.sh restore 18432 --confirm

# Hapus permanen — tidak ada undo
bash scripts/mail.sh delete 18432 --permanent --confirm
```

## Menulis

```bash
# Draft dulu (paling sering ini yang kamu mau)
bash scripts/mail.sh draft --in-reply-to 18432 --body-file /tmp/balasan.txt --confirm

# Balas langsung, threading benar
bash scripts/mail.sh reply 18432 --body-file /tmp/balasan.txt --quote --confirm

# Email baru dengan lampiran
bash scripts/mail.sh send \
  --to klien@perusahaan.com \
  --subject "Penawaran laundry karyawan 80 kg/minggu — Laundry Mbak Sri" \
  --body-file /tmp/penawaran.txt \
  --attach /tmp/penawaran.pdf \
  --signature ~/.hermes/business/signature.txt \
  --confirm

# Teruskan ke tim
bash scripts/mail.sh forward 18432 --to tim@bisnis.com --body "Tolong dicek ya" --confirm
```

---

## Balasan otomatis, dari nol

```bash
# 1. Siapkan FAQ
mkdir -p ~/.hermes/business
cp templates/faq.example.yaml ~/.hermes/business/faq.yaml
$EDITOR ~/.hermes/business/faq.yaml

# 2. Periksa
bash scripts/autoreply.sh validate

# 3. Uji tanpa menyentuh mailbox
bash scripts/autoreply.sh simulate --text "bukanya jam brp kak?"

# 4. Lihat cakupan di inbox nyata (tidak mengirim apa pun)
bash scripts/autoreply.sh scan

# 5. Seminggu pertama: draft saja
bash scripts/autoreply.sh respond --mode draft --confirm

# 6. Setelah drafnya terbukti benar: kirim otomatis untuk FAQ saja
bash scripts/autoreply.sh respond --mode faq --confirm --holding

# 7. Lihat apa yang sudah dikirim
bash scripts/autoreply.sh log --today
```

---

## Mode blind (Hermes yang menulis, semua dikirim)

Alurnya: Hermes membaca triage, menulis jawaban, lalu responder yang mengirim
dengan semua rem tetap terpasang.

```bash
# 1. Hermes ambil triage-nya
bash scripts/autoreply.sh scan --json > /tmp/triage.json

# 2. Hermes menulis jawaban ke file (ini yang dikerjakan agen, bukan skrip)
cat > /tmp/jawaban.json <<'JSON'
[
  {"uid": "18432", "body": "Halo Bu Rina, betul kami buka Minggu 07.00-21.00..."},
  {"uid": "18433", "body": "Terima kasih, untuk 30 orang kami siapkan meja panjang..."}
]
JSON

# 3. Kirim
bash scripts/autoreply.sh respond --mode blind \
  --answers-file /tmp/jawaban.json \
  --i-understand-blind-mode --confirm
```

Tanpa `--i-understand-blind-mode`, perintah itu hanya mencetak peringatannya
lalu berhenti. Peringatan itu muncul sekali; setelah kamu memutuskan, dia tidak
mengungkitnya lagi.

---

## Cron: pola yang masuk akal

```cron
# 06:00 — ringkasan inbox semalam ke Telegram. T1: agen → kamu. Aman.
0 6 * * * cd ~/.hermes/skills/email-marketing && \
  bash scripts/autoreply.sh scan --json > ~/.hermes/business/triage-pagi.json

# Tiap 30 menit jam kerja — jawab FAQ, sisanya kirim ke HP kamu. T2.
*/30 7-21 * * * cd ~/.hermes/skills/email-marketing && \
  bash scripts/autoreply.sh respond --mode faq --confirm --holding \
    --notify-cmd 'bash ~/bin/notif-telegram.sh {msg}'

# 21:30 — ringkasan hari ini
30 21 * * * cd ~/.hermes/skills/email-marketing && \
  bash scripts/autoreply.sh log --today >> ~/.hermes/business/laporan-email.log
```

Tiga catatan tentang cron di sini:

1. **Mulai dari `--mode draft` di cron juga.** Cron yang mengirim di minggu
   pertama adalah cara termahal untuk menemukan FAQ yang salah.
2. **Batas jam.** `7-21` bukan sekadar rapi — balasan otomatis jam 2 pagi
   terlihat persis seperti apa adanya.
3. **`emergency-halt.sh` mengalahkan cron.** Cron tetap jalan, tapi setiap
   pengiriman berhenti selama file HALT ada. Itu rem yang tidak perlu kamu
   ingat cara mematikan cron-nya.

---

## Format `--answers-file`

```json
[
  {"uid": "18432", "body": "isi balasan lengkap"},
  {"uid": "18433", "body": "isi balasan lengkap"}
]
```

Yang ditambahkan skill ini di atas `body` kamu:
- disclaimer wajib (kalau entri FAQ-nya menandai `disclaimer:`)
- `meta.disclosure`
- `meta.signature`
- header `Auto-Submitted: auto-replied`
- threading `In-Reply-To` + `References`

---

## Menggabungkan dengan skill lain di repo ini

```bash
# Cek klaim angka di draft sebelum dikirim
python3 scripts/check-numbers.py /tmp/penawaran.txt

# Orang yang sama, dua kanal — jangan hitung dua kali kalau kamu
# punya batas kontak harian
bash ../waha-marketing/scripts/waha.sh contacts --limit 50
bash scripts/mail.sh search "from:pelanggan@x.com newer_than:7d"
```

Aturan lintas kanal dari `hermes-discipline.md` berlaku di sini juga: kalau
kamu bilang "maksimal 5 pesan hati-hati sehari", itu **5 total** — bukan 5 per
kanal.
