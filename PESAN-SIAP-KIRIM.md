# PESAN-SIAP-KIRIM — cara mengajak peserta mencoba skill

Untuk penyelenggara. Tiga varian pesan siap tempel + checklist + FAQ.
Prinsipnya: **satu jalur utama, dua langkah, satu prompt pertama.**
Semakin banyak pilihan di pesan, semakin sedikit yang mencoba.

## Prasyarat peserta — apa yang harus mereka punya DULU

Zip skill tidak berguna tanpa dua hal ini. Diverifikasi ke dokumen resmi
Hermes (<https://hermes-agent.nousresearch.com/docs/getting-started/quickstart>,
14 Agu 2026):

**1. Hermes Agent terpasang** (pilih satu):

| Cara | Perintah |
|---|---|
| Installer Desktop macOS/Windows (**resmi justru merekomendasikan ini**) | unduh dari dokumen quickstart |
| Linux / macOS / WSL2 / Termux | `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| bash` |
| Windows native (PowerShell) | `iex (irm https://hermes-agent.nousresearch.com/install.ps1)` |

**2. Model aktif** — jalur termudah, tanpa API key:

```bash
hermes setup --portal
```

Satu OAuth login → model + Tool Gateway aktif sekaligus (jalur "Quick Setup"
yang direkomendasikan docs). Alternatif: `hermes model` untuk pakai key
sendiri (OpenRouter, dsb.). Verifikasi: kirim satu chat sungguhan dan pastikan
dijawab, BARU pasang skill.

⚠️ **Jangan pilih mode "Blank Slate" saat setup** — mode itu mematikan
toolset skills bawaan; kalau sudah terlanjur, nyalakan lagi dengan
`hermes skills opt-in --sync`.

Setelah itu baru: unzip → `bash installer/install.sh` → `hermes skills list`
→ 7 skill. Ekstra per skill (opsional): App Password Gmail untuk
ibras-email-marketing; server WAHA untuk ibras-waha-marketing; `pip3 install pyyaml`.

## Checklist sebelum kirim

- [ ] Upload `dist/hermes-marketing-skills-<tanggal>.zip` ke Drive / file
      grup WhatsApp, atur bisa diunduh siapa saja. (Alternatif tanpa upload:
      link zip otomatis GitHub —
      `https://github.com/volfadar/hermes-marketing-skills/archive/refs/heads/master.zip`)
- [ ] Ganti `<LINK-ZIP>` di varian pesan dengan link-mu.
- [ ] Tes alurnya sekali di Hermes home lain:
      `HERMES_HOME=/tmp/tes bash installer/install.sh --home /tmp/tes`
- [ ] Siapkan momen kirim: paling efektif **saat sesi penutup**, langsung
      setelah slide terakhir — peserta masih ada di ruangan/chat.

---

## Varian A — chat grup / WhatsApp (utama, pendek)

> 🎉 Skill marketing dari workshop tadi sudah bisa dicoba di Hermes kamu!
>
> **Cara pasang (2 menit):**
> 1. Download & unzip: <LINK-ZIP>
> 2. Buka terminal di folder hasil unzip, jalankan:
>    `bash installer/install.sh`
> 3. Cek: `hermes skills list` — harus muncul 7 skill ✅
>
> Langsung coba — chat Hermes begini aja:
> *"Aku jual [produk kamu] lewat [WA/IG/email]. Mulai dari mana?"*
>
> Kalau macet, screenshot error-nya kirim ke sini.
> Kalau berhasil, balas screenshot `hermes skills list`-mu — kami hitung 🙌

Alasan tiap baris: link tunggal di atas; satu perintah install; satu prompt
pertama yang personal (router akan membawa mereka ke skill yang tepat); dan
minta screenshot sebagai check-in — itu juga cara termurah mengukur berapa
peserta benar-benar memasang.

## Varian B — email / follow-up (lengkap)

> Subjek: Skill marketing dari workshop — cara mencobanya (2 menit)
>
> Halo!
>
> Skill yang dipakai di workshop kemarin sekarang bisa dipasang di Hermes
> Agent milikmu sendiri. Tujuh skill: perute sesi, lab posisi merek, riset
> produk, pembuat konten, email, sosmed, dan WhatsApp.
>
> **Pasang:**
> 1. Download & unzip: <LINK-ZIP>
> 2. Terminal, di folder hasil unzip: `bash installer/install.sh`
> 3. Verifikasi: `hermes skills list` → 7 skill, status enabled.
>
> **Coba pertama (copy-paste, ganti bagian [ ]):**
>
> 1. *"Aku jual [produk] ke [pembeli] di [kota]. Mau mulai jualan lagi
>    setelah [berapa lama rehat]. Mulai dari mana?"*
> 2. *"Bisnis saya [deskripsi]. Bawa saya lewat tahap sikap dulu — jangan
>    loncat ke funnel."*
> 3. *"Buat 5 hook Instagram untuk [konten], bahasa santai, bukan
>    marketer-an."*
>
> Budaya kerja skill-nya: selalu draft dulu, tidak ada yang terkirim tanpa
> konfirmasi kamu. Kalau kamu minta hal berisiko, skill akan mengerem dan
> menjelaskan kenapa.
>
> Butuh bantuan? Balas email ini dengan screenshot error-nya.
>
> — [Nama kamu]

## Varian C — tanpa download (satu baris, dari GitHub)

Untuk peserta yang sudah nyaman dengan terminal:

> Dua perintah, dua detik, dan tidak butuh akun GitHub:
>
> ```
> git clone --depth 1 https://github.com/volfadar/hermes-marketing-skills.git
> cd hermes-marketing-skills && bash installer/install.sh
> ```
>
> Cek dengan `hermes skills list` — harus muncul 7 baris `ibras-*` berstatus
> `enabled`. Jalan ulang perintah yang sama kapan saja = update.

**Jangan** menyuruh Hermes memasang ketujuhnya lewat identifier
`hermes skills install volfadar/...` atau lewat Dashboard Chat tanpa token
GitHub. Hub installer mengambil **satu request API per file**, isi repo ini
**296 file**, dan batas GitHub tanpa login **60 request per jam** — jadi kuota
habis di tengah skill kedua dan sisanya gagal. Pada sesi nyata 19 Agustus 2026
itu memakan 21 menit dan tetap gagal.

Kalau memang mau lewat Hub, naikkan batasnya dulu jadi 5.000/jam dengan
`gh auth login`, atau taruh `GITHUB_TOKEN=ghp_...` (public repo, read-only) di
`~/.hermes/.env`. Sesudah itu identifier di README boleh dipakai.

---

## Jawaban FAQ cepat (untuk dibalas ke grup)

| Pertanyaan | Jawaban singkat |
|---|---|
| `hermes: command not found` | Hermes Agent-nya belum terpasang — `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| bash` (Windows PowerShell: `iex (irm https://hermes-agent.nousresearch.com/install.ps1)`). |
| Hermes jalan tapi tidak menjawab / jawaban aneh | Model belum aktif — `hermes setup --portal` (login sekali, tanpa API key). |
| Skill tidak muncul di list padahal terpasang | Cek apakah setup-nya dulu memilih "Blank Slate" (mematikan toolset skills) — `hermes skills opt-in --sync`. Kalau bukan: jangan ubah nama folder hasil unzip; jalan ulang installer. |
| `hermes skills install` menolak `ibras-email-marketing` / `ibras-cloakserve-research` | Itu verdict CAUTION, bukan DANGEROUS: skill-nya memegang kredensial email atau menjalankan Docker/Tailscale. Periksa isinya di repo lalu tambahkan `--force`. Atau pakai zip + installer (Varian A) — tanpa scan. |
| Install lewat Hub/Dashboard lama banget lalu gagal (`403` / `rate limit`) | Kuota GitHub 60 request/jam habis — hub ngambil 1 request per file, repo ini 296 file. **Jangan diulang**, kuotanya per jam. Pakai `git clone` + `bash installer/install.sh` (2 detik). |
| Profile tidak kebaca | `pip3 install pyyaml` |
| Pakai Windows? | Hermes berjalan di WSL/macOS/Linux — jalankan installer dari terminal Hermes-mu berjalan. |
| Data saya aman? | Semua berjalan lokal di Hermes kamu sendiri; tidak ada SaaS baru. Skill email/WhatsApp hanya bertindak dengan konfirmasi. |
