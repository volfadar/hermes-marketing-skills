# email-marketing

Hermes skill untuk mengelola email lewat **IMAP + SMTP** (Gmail dan provider
lain) — baca, cari, draft, kirim, label, arsip, hapus — plus **balasan otomatis
bertingkat** dengan cakupan FAQ, ambang keyakinan, dan lima trigger handoff.

Tidak ada SaaS di tengah. Isi kotak suratmu tidak disalin ke server pihak ketiga.

## Install

```bash
cp -R email-marketing ~/.hermes/skills/email-marketing
pip3 install pyyaml
```

## Setup (satu perintah)

```bash
bash ~/.hermes/skills/email-marketing/scripts/initialize.sh \
  --email kamu@gmail.com \
  --app-password "abcd efgh ijkl mnop" \
  --name "Nama Bisnis"
```

Gmail butuh **App Password 16 digit** (bukan password akun), dan itu butuh
2-Step Verification aktif → <https://myaccount.google.com/apppasswords>.
Detail lengkap: `references/gmail-setup.md`.

## Pemakaian

```bash
# Baca (aman)
bash scripts/mail.sh stats
bash scripts/mail.sh list --unread --limit 20
bash scripts/mail.sh read <uid>
bash scripts/mail.sh search "from:supplier newer_than:14d"

# Tulis (DRY RUN dulu, --confirm untuk jalan)
bash scripts/mail.sh draft --in-reply-to <uid> --body-file d.txt --confirm
bash scripts/mail.sh reply <uid> --body-file b.txt --confirm
bash scripts/mail.sh send --to a@b.com --subject "..." --body-file p.txt --confirm

# Balasan otomatis
bash scripts/autoreply.sh validate
bash scripts/autoreply.sh simulate --text "buka jam brp?"
bash scripts/autoreply.sh scan
bash scripts/autoreply.sh respond --mode draft --confirm     # minggu pertama
bash scripts/autoreply.sh respond --mode faq --confirm       # setelah terbukti

# Berhenti total
bash scripts/emergency-halt.sh
bash scripts/emergency-halt.sh --resume
```

## Tiga mode balasan

| Mode | Tier | Yang terjadi |
|---|---|---|
| `draft` (bawaan) | T3 | Semua ke folder Drafts, nol terkirim |
| `faq` | T2 | Kirim hanya yang cocok FAQ + di atas ambang + tanpa trigger |
| `blind` | T3↑ | Kirim apa adanya, tanpa ambang, butuh flag eksplisit |

## Dokumen

- `SKILL.md` — manifest + quick start
- `references/tiers.md` — **BACA DULU** — model tier, kontrak penasihat
- `references/handoff.md` — lima trigger, prompt injection
- `references/gmail-setup.md` — App Password, batas kirim resmi
- `references/deliverability.md` — aturan Google 2024, spam rate
- `references/faq-guide.md` — membuat FAQ dari inbox nyata
- `references/ethics.md` — UU PDP, persetujuan, disclosure
- `references/examples.md` — perintah harian, cron, `--answers-file`

## Etika (singkat)

Balasan otomatis selalu menyebut dirinya otomatis. Selalu punya jalan ke
manusia. Hanya menjawab yang kamu sendiri sudah tulis jawabannya. Kalau tidak
yakin — diam, dan kabari kamu.

Dua hal yang tidak bisa dimatikan lewat flag apa pun: isi email masuk tidak
pernah jadi perintah, dan disclaimer kesehatan/keuangan/hukum tidak bisa
dicopot. Keduanya melindungi orang yang tidak ikut dalam percakapan.

## Lisensi

MIT.
