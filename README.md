# Skill Pemasaran untuk Hermes Agent

Tujuh skill untuk pemilik usaha kecil — riset, posisi merek, konten, email,
sosmed, WhatsApp — berjalan di Hermes Agent milikmu sendiri. Tidak ada SaaS
baru, tidak ada data keluar dari laptop/HP-mu.

| Skill | Buat apa | Butuh apa selain Hermes |
|---|---|---|
| `ibras-marketing-orchestrator` | "Mulai dari mana?" — router yang milih skill mana yang jalan | — |
| `ibras-brand-strategy-coach` | Lab posisi merek 5 tahap (sikap → funnel) | — |
| `ibras-content-creator` | Ide, caption, hook, kalender, repurpose konten | — |
| `ibras-cloakserve-research` | Riset produk/kompetitor/niche sebelum jual | — |
| `ibras-email-marketing` | Baca-tulis email (IMAP/SMTP) + balasan otomatis bertingkat | App Password Gmail + `pip3 install pyyaml` |
| `ibras-social-publishing` | Rencana & keputusan posting sosmed (pilot 2 minggu) | `pip3 install pyyaml` |
| `ibras-waha-marketing` | Broadcast & balasan WhatsApp lewat WAHA (self-host) | Server WAHA sendiri |

Empat skill pertama langsung jalan tanpa setup apa pun — cukup chat.

## Install

**Cara A — dari folder ini / hasil unzip bundel:**

```bash
bash installer/install.sh
```

Installer memeriksa Hermes home, menyalin ketujuh skill, dan memverifikasi
semuanya terlihat oleh `hermes skills list`. Aman dijalankan ulang kapan saja
(jalan ulang = update).

**Cara B — dari GitHub, satu perintah per skill:**

Repo sumber: <https://github.com/volfadar/hermes-marketing-skills>

Lima skill terpasang langsung:

```bash
hermes skills install volfadar/hermes-marketing-skills/ibras-marketing-orchestrator
hermes skills install volfadar/hermes-marketing-skills/ibras-brand-strategy-coach
hermes skills install volfadar/hermes-marketing-skills/ibras-content-creator
hermes skills install volfadar/hermes-marketing-skills/ibras-social-publishing
hermes skills install volfadar/hermes-marketing-skills/ibras-waha-marketing
```

Dua skill ini menangkap verdict **CAUTION** — Hermes meminta kamu memeriksa
dulu karena skill-nya menyentuh kredensial email / menjalankan Docker +
browser riset. Periksa isinya di repo (setiap folder berdiri sendiri), lalu
tambahkan `--force`:

```bash
hermes skills install volfadar/hermes-marketing-skills/ibras-email-marketing --force
hermes skills install volfadar/hermes-marketing-skills/ibras-cloakserve-research --force
```

Matriks scanner dan kelengkapan bundle ini diverifikasi pada Hermes Agent
v0.20.2 (2026.8.16) di container Incus Ubuntu yang bersih pada 17 Agustus
2026, memakai URL `SKILL.md` yang dipatok ke commit rebrand. Lima skill
mendapat verdict `SAFE`; email dan cloakserve mendapat `CAUTION` tanpa temuan
`CRITICAL`. Ketujuh bundle terpasang lengkap dan muncul `enabled` di
`hermes skills list`. Verifikasi ulang tujuh identifier pendek di atas adalah
release gate setelah nama baru mencapai branch `master`.

`--force` **tidak** bisa menimpa verdict DANGEROUS — hanya CAUTION, dan hanya
setelah kamu sendiri memutuskan isinya aman. Kalau tidak mau repot memeriksa,
pakai Cara A: installer menyalin folder yang persis sama tanpa lewat pemindai.

Jangan pakai `hermes skills tap add` untuk repo ini — tap mengharapkan skill di
subfolder `skills/`, jadi namanya bisa me-resolve ke skill orang lain yang
kebetulan sama. Cukup pakai identifier lengkap di atas.

**Cara C — salin manual (tanpa installer):**

```bash
cp -R ibras-email-marketing ~/.hermes/skills/
```

Nama folder di repo ini sudah = nama skill, jadi salin apa adanya.
JANGAN tambah prefiks apa pun pada nama folder — Hermes menemukan skill
berdasarkan nama folder yang sama dengan `name:` di SKILL.md.

**Pilih sebagian saja:**

```bash
bash installer/install.sh --only ibras-email-marketing,ibras-social-publishing
```

## Cek berhasil

```bash
hermes skills list
```

Harus muncul 7 baris, status `enabled`. Hermes home-mu bukan `~/.hermes`?
Tambahkan `--home /path/ke/hermes-home` (atau export `HERMES_HOME`).

## Coba 5 menit pertama (copy-paste aja)

Ganti dengan nama bisnismu sendiri.

1. **Router** — mulai selalu dari sini:
   > Halo, saya Joko, pemilik kedai kopi di Ende. Pelanggan saya 600-an kontak
   > WhatsApp tapi saya tidak pernah Follow up. Mulai dari mana?

2. **Riset dulu sebelum jual** (`ibras-cloakserve-research`):
   > Saya mau jual binder plug ke fotografer wedding. Riset dulu: ada nggak
   > yang jual ini di marketplace, dan apa keluhan mereka di forum?

3. **Lab posisi merek** (`ibras-brand-strategy-coach`):
   > Bisnis saya keripik pedas frozen, pembeli ibu-ibu muda di Bandung. Bawa
   > saya lewat tahap sikap dulu — jangan loncat ke funnel.

4. **Konten** (`ibras-content-creator`):
   > Buat 5 hook Instagram untuk konten "behind the scene produksi keripik",
   > bahasa santai, bukan marketer-an.

5. **Baca inbox (aman, read-only)** (`ibras-email-marketing`, setelah setup Gmail):
   > Baca inbox saya, mana email yang perlu dibalas hari ini? Jangan balas,
   > tunjukin dulu daftarnya.

6. **Rencana sosmed tanpa auto-posting nekat** (`ibras-social-publishing`):
   > Saya posting IG 4x sebulan, hasil sepi. Bikin pilot 2 minggu yang bisa
   > saya hentikan kapan saja.

Budaya kerja semua skill ini: **dulu dulu dan selalu draft dulu**. Tidak ada
yang kirim/publish apa pun tanpa `--confirm` darimu. Kalau kamu minta hal
yang berisiko (kirim massal, auto-kirim buta, API resmi), skill akan mengerem
dan jelaskan kenapa — itu fitur, bukan error.

## Setup tambahan (hanya kalau pakai skill itu)

**ibras-email-marketing** — satu perintah, butuh App Password 16 digit
(bukan password akun; aktifkan 2FA dulu di
<https://myaccount.google.com/apppasswords>):

```bash
pip3 install pyyaml   # sekali
bash ~/.hermes/skills/ibras-email-marketing/scripts/initialize.sh \
  --email kamu@gmail.com \
  --app-password "abcd efgh ijkl mnop" \
  --name "Nama Bisnismu"
```

**ibras-waha-marketing** — hanya kalau kamu sudah punya server WAHA:

```bash
bash ~/.hermes/skills/ibras-waha-marketing/scripts/initialize.sh \
  --url https://waha-kamu.example --key KUNCI --session all-in-one-device
```

**Sisanya** — tidak ada. Chat saja.

## Update & uninstall

```bash
bash installer/install.sh        # jalan ulang = update semua skill
bash installer/uninstall.sh      # hapus semua 7
```

Data bisnismu (`~/.hermes/business/profile.yaml`, FAQ, log) tidak pernah
disentuh oleh update maupun uninstall — itu milikmu.

## Kalau macet

| Gejala | Sebab & obat |
|---|---|
| Skill tidak muncul di `hermes skills list` | Nama folder berubah/berprefiks — jangan ubah nama folder, atau `--home` salah |
| `hermes: command not found` | Hermes Agent belum terpasang. Pasang dulu, lalu ulangi installer. |
| Profile tidak kebaca / skill jalan aneh | `python3 -c "import yaml"` — kalau gagal: `pip3 install pyyaml` |
| Mau lihat daftar tanpa pasang | `bash installer/install.sh --list` |
