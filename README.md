# Skill Pemasaran untuk Hermes Agent

Sembilan skill untuk pemilik usaha kecil — riset, posisi merek, konten, email,
sosmed, WhatsApp — berjalan di Hermes Agent milikmu sendiri. File skill tetap
lokal. Data hanya keluar ketika kamu memilih model/provider atau tool eksternal;
cek preview, izin, dan data sensitif sebelum melanjutkan.

| Skill | Buat apa | Butuh apa selain Hermes |
|---|---|---|
| `ibras-marketing-orchestrator` | "Mulai dari mana?" — router yang milih skill mana yang jalan | — |
| `ibras-brand-strategy-coach` | Lab posisi merek 5 tahap (sikap → funnel) | — |
| `ibras-content-creator` | Ide, caption, hook, kalender, repurpose konten | — |
| `ibras-cloakserve-research` | Riset produk/kompetitor/niche sebelum jual | — |
| `ibras-email-marketing` | Baca-tulis email (IMAP/SMTP) + balasan otomatis bertingkat | App Password Gmail + `pip3 install pyyaml` |
| `ibras-social-publishing` | Rencana & keputusan posting sosmed (pilot 2 minggu) | `pip3 install pyyaml` |
| `ibras-waha-marketing` | Broadcast & balasan WhatsApp lewat WAHA (self-host) | Server WAHA sendiri |
| `ibras-setup` | Pasang & cek semua dependensinya sekali: model, browser/CDP, WAHA, SMTP, doctor tiap skill | — |
| `ibras-discipline` | Aturan angka & klaim yang dipanggil skill lain sebelum menyebut harga ke pembeli | — |

Empat skill pertama langsung jalan tanpa setup apa pun — cukup chat.
`ibras-discipline` tidak pernah kamu panggil sendiri: skill lain yang memanggilnya
sebelum menyebut angka atau harga.

---

## Langkah 1–2 — install (2 detik, dua perintah)

**Ini cara yang benar. Pakai ini.** Tidak butuh akun GitHub, tidak butuh token,
tidak kena batas apa pun.

```bash
git clone --depth 1 https://github.com/volfadar/hermes-marketing-skills.git
cd hermes-marketing-skills && bash installer/install.sh
```

Selesai. Installer menyalin kesembilan skill ke Hermes home-mu lalu memverifikasi
semuanya terlihat oleh Hermes. Aman dijalankan ulang kapan saja (jalan ulang =
update). Data bisnismu di `~/.hermes/business/` tidak pernah disentuh.

Cek:

```bash
hermes skills list        # harus muncul 9 baris ibras-*, status enabled
```

Hermes home-mu bukan `~/.hermes`? Tambahkan `--home /path/ke/hermes-home`
(atau export `HERMES_HOME`). Mau sebagian saja?

```bash
bash installer/install.sh --only ibras-email-marketing,ibras-social-publishing
bash installer/install.sh --list        # lihat daftar + status tanpa pasang
```

Tidak ada `git`? Download ZIP dari halaman repo (**Code → Download ZIP**), unzip,
lalu jalankan `bash installer/install.sh` dari dalam folder hasil unzip. Sama
cepatnya.

---

## Jangan pasang lewat Hub/Dashboard tanpa token GitHub

Kalau kamu menyuruh Hermes memasang kesembilan skill lewat identifier
`volfadar/hermes-marketing-skills/...` (baik dari Dashboard Chat maupun
`hermes skills install`), **instalasinya hampir pasti gagal di tengah jalan.**

Sebabnya bukan koneksi dan bukan Hermes-nya rusak:

| | |
|---|---|
| Hub installer mengambil file | **satu request GitHub API per file** |
| Isi repo ini | **296 file** |
| Batas GitHub tanpa login | **60 request per jam** |

Jadi kuota habis setelah kira-kira satu setengah skill, sisanya kena `403`, dan
Hermes mulai mencari jalan lain sendiri. Pada sesi nyata 19 Agustus 2026 hal ini
memakan **21 menit** dan berakhir dengan agent nge-clone repo manual — persis
yang harusnya kamu lakukan dari awal dalam 2 detik.

**Jangan diulang-ulang kalau kena.** Kuotanya per jam, bukan per percobaan;
mengulang justru membakar sisa kuota dan menambah lama.

### Kalau memang mau lewat Hub

Naikkan batasnya dulu dari 60 jadi 5.000 request/jam. Pilih salah satu:

```bash
gh auth login                              # cara A: lewat gh CLI
```

```bash
echo 'GITHUB_TOKEN=ghp_xxxxxxxx' >> ~/.hermes/.env    # cara B: PAT
chmod 600 ~/.hermes/.env
```

Token cukup yang **public repo, read-only** — tidak perlu izin tulis apa pun.
Hermes membacanya dengan urutan: `GITHUB_TOKEN` / `GH_TOKEN` → `gh auth token`
→ GitHub App → tanpa login. Cek kuotamu kapan saja:

```bash
curl -s https://api.github.com/rate_limit | grep -o '"remaining":[0-9]*' | head -1
```

Setelah token terpasang, prompt satu-tempel ini boleh dipakai di Dashboard Chat:

> Pasang 9 skill IBRAS ke profile Hermes aktif memakai identifier exact
> `volfadar/hermes-marketing-skills/` + nama berikut:
> `ibras-marketing-orchestrator`, `ibras-brand-strategy-coach`,
> `ibras-content-creator`, `ibras-social-publishing`, `ibras-waha-marketing`,
> `ibras-email-marketing`, `ibras-cloakserve-research`, `ibras-setup`,
> `ibras-discipline`. Jangan pilih hasil
> search yang namanya mirip. Pasang 5 SAFE normal. Untuk 2 CAUTION, force hanya
> bila alasannya cocok: email = IMAP/SMTP; cloakserve = Docker/sudo/Tailscale.
> Jangan bypass DANGEROUS. Instal saja—jangan setup, baca data, menjalankan
> Docker, atau kirim apa pun. Akhiri dengan status exact 9/9.

Lalu buka **Skills → Installed**, cari `ibras-`, pastikan 9/9 aktif, dan buka
**Chat → New chat** supaya skill baru aktif di sesi berikutnya.

Dua verdict CAUTION dijelaskan di dalam prompt supaya persetujuannya terbatas:
instalasi tidak memberi izin mengonfigurasi email, membaca data, memakai
kredensial, menjalankan Docker, atau mengirim pesan. Verdict DANGEROUS tidak
boleh dilewati — `--force` memang tidak bisa menimpanya.

Jangan pakai `hermes skills tap add` untuk repo ini — tap mengharapkan skill di
subfolder `skills/`, jadi namanya bisa me-resolve ke skill orang lain yang
kebetulan sama.

### Salin manual (tanpa installer)

Nama folder di repo ini sudah = nama skill, jadi salin apa adanya:

```bash
cp -R ibras-email-marketing ~/.hermes/skills/
```

JANGAN tambah prefiks apa pun pada nama folder — Hermes menemukan skill
berdasarkan nama folder yang sama dengan `name:` di SKILL.md.

---

## Langkah 3 — pasang konteksnya (jangan dilewat)

Skill terpasang **bukan** berarti skill terpakai. Ini masalah yang paling sering
kejadian dan paling sulit kelihatan, karena tidak ada error sama sekali:

| Yang terjadi | Yang kamu lihat |
|---|---|
| SKILL.md kebuka, `references/*.md` tidak pernah dibuka | jawaban lancar, terdengar masuk akal, isinya jawaban model biasa |
| Model jawab dari pengetahuannya dulu, skill dipakai buat ngerapiin kalimat | gaya bahasanya berubah, isinya tidak |
| Aturan "cek dulu sebelum jawab" dipenuhi dengan *cerita* sudah ngecek | terdengar disiplin, nol halaman dibuka |

Ketiganya terukur di pengujian 20 Agustus 2026. Yang ketiga verbatim: *"saya coba
buka beberapa halaman harga agensi Jakarta tapi keblokir"* — di sesi yang tidak
melakukan satu pun tool call.

Perbaikannya satu file. Hermes membaca `~/.hermes/SOUL.md` sebagai **bagian paling
awal system prompt** (`agent/prompt_builder.py`, fungsi `load_soul_md()`, disuntik
di `agent/system_prompt.py`) — jadi isinya dibaca sebelum apa pun yang lain,
termasuk sebelum skill.

```bash
# dari folder repo hasil clone
cp evals/soul-md-id/SOUL.id.md ~/.hermes/SOUL.md
```

Belum punya file itu? Buat manual: `nano ~/.hermes/SOUL.md`, tempel isi
`evals/soul-md-id/SOUL.id.md`. Mulai chat **baru** setelahnya — sesi lama tetap
pakai prompt lama.

**Isinya empat hal, dan tidak satu pun berupa angka** (angka di system prompt akan
basi lalu keluar sebagai fakta — persis masalah yang mau diperbaiki):

1. **Baca skill dulu, baru jawab.** Bukan jawab dulu lalu skill dipakai mengedit.
2. **File yang ditunjuk skill itu bagian dari skill.** `references/*.md` dibuka
   *sebelum* menjawab giliran yang membutuhkannya, bukan sesudah.
3. **Kalau aturan bilang cek, ya panggil tool.** Menceritakan pengecekan yang tidak
   dilakukan itu bukan jalan pintas.
4. **Terrain default Indonesia.** Jangan impor default pasar Amerika.

### Apa bedanya — diukur, bukan dikira

Uji A/B, satu pertanyaan sama, dua identitas, model sama (`muse-spark-1.2`),
skill sengaja dilepas supaya yang terukur identitasnya:

| Probe jasa konsultasi karir | SOUL bawaan | SOUL Indonesia |
|---|---|---|
| Kosakata funnel impor | tripwire, core offer, high ticket, Calendly, Linktree, webinar | 0 |
| Harga Rupiah diklaim tanpa sumber | 79rb · 349rb · 1,2jt | **0** |
| Tetap memberi rencana lengkap | ya | ya |

Kontrol: pertanyaan Python berbahasa Inggris keluar normal, tanpa bocor framing
Indonesia. Transkrip lengkap: `evals/soul-md-id/HASIL.md`.

**Jujurnya:** untuk produk fisik (keripik) pengetahuan taktis model soal Indonesia
sudah bagus tanpa SOUL — titip warung, CFD, PIRT, reseller ibu-ibu, nol kosakata
US. Yang rusak di situ bukan pasarnya, tapi **angka karangan**: 7 angka tanpa
sumber jadi 0. Bias pasar US baru muncul di bisnis jasa/pengetahuan.

### Cek SOUL-nya kepakai

```bash
hermes chat -q "Sebutkan tiga aturan pertama dari identitas kamu, singkat saja." -Q
```

Kalau jawabannya tidak menyebut baca-skill-dulu / buka-file-referensi / cek-jangan-
diceritakan, berarti file-nya belum kebaca — cek lokasinya (`echo $HERMES_HOME`,
default `~/.hermes`) dan mulai chat baru.

### Kalau kamu pakai lebih dari satu Hermes home

`profile.yaml` dan SOUL mengikuti `HERMES_BUSINESS_DIR` → `HERMES_HOME` → default.
Satu mesin dengan beberapa home yang salah setel pernah membuat **tiga sesi pemilik
usaha berbeda menulis ke file yang sama** — sesi terbuka dengan menyapa seorang
lulusan SMK memakai komunitas milik orang lain. Tidak ada pesan error untuk ini.
Cek dengan:

```bash
python3 ~/.hermes/skills/ibras-brand-strategy-coach/scripts/lib/profile.py path
```

## Langkah 4 — jalankan setup, sekali

Skill terpasang bukan berarti skill jalan. Yang gagal itu **dependensinya**, dan
gagalnya diam-diam: tidak ada error, jawabannya saja jadi lebih buruk.

```bash
bash ~/.hermes/skills/ibras-setup/scripts/setup.sh          # cek saja, tidak mengubah apa pun
bash ~/.hermes/skills/ibras-setup/scripts/setup.sh --fix    # kerjakan yang aman, sisanya dicetak
```

Keluarnya satu daftar berurutan: apa yang kurang, akibatnya apa, perintahnya apa.
Exit code 0 kalau semua yang **wajib** sudah lewat.

### Yang dicek, dan kenapa

| Kurang | Yang kamu lihat kalau tidak dicek |
|---|---|
| `model.default` kosong | **`404 tool-use`** — pesan errornya tidak menyebut model sama sekali, jadi orang membongkar skill-nya |
| browser/CDP mati | agent bilang *"halamannya keblokir"* untuk halaman yang balas `200 OK` |
| Playwright setengah jadi | folder ada, biner `chrome` tidak ada, semuanya terlihat normal |
| CDP terpasang tapi belum di-wire | biner ada, tidak ada yang mendengarkan di 9222, browser tetap mati |
| WAHA belum ada | skill WhatsApp menolak semua aksi, selamanya |
| SMTP belum diset | skill email tidak bisa baca/draft |

Diukur di instalasi bersih 20 Agustus 2026. Tidak satu pun memunculkan error yang
bisa ditindaklanjuti; tiga di antaranya membuat agent memberi **jawaban salah yang
terdengar yakin**, bukannya berhenti.

`--fix` memasang dan menyalakan browser, membuat folder config, menyalin contoh
config. Dia **tidak** menyentuh kredensial, tidak menjalankan container, tidak
mengirim apa pun — itu dicetak sebagai perintah untuk kamu baca dulu.

### Dua yang perlu tanganmu sendiri

```bash
bash ~/.hermes/skills/ibras-setup/scripts/waha.sh     # WhatsApp
bash ~/.hermes/skills/ibras-setup/scripts/smtp.sh     # email
```

**WAHA sekarang gratis seluruhnya.** WAHA Plus dilebur ke WAHA Core sejak versi
**2026.6.1** — sesi tanpa batas, multimedia, semua storage, security bawaan, semua
ada di image publik `devlikeapro/waha`. Tidak ada lagi `devlikeapro/waha-plus`,
tidak perlu `docker login`, tidak perlu Patron key.
Sumber: <https://waha.devlike.pro/docs/how-to/waha-plus/> (dibaca 20 Agu 2026).

Keduanya membaca rahasia lewat input tersembunyi atau env — **tidak pernah lewat
command line**, karena argv terbaca proses lain di mesin yang sama.

### Kenapa browser menentukan kualitas jawaban

Halaman harga agensi hanya membuktikan berapa yang **diminta**. Listing marketplace
yang ter-render membawa sisi pembeli — harga *plus* jumlah terjual dan rating:

```
BMC            Mulai Rp500.000     Terjual 35   5,0 (33)
Agil Prasetyo  Mulai Rp1.400.000   Terjual 14   5,0 (11)
```

Bedanya nyata. Dengan browser hidup, *"jasa website 100 juta per proyek, aku baru
lulus SMK"* dijawab dengan empat vendor yang benar-benar dibuka — nama PT, alamat,
tanggal, link — lalu *"paket Advanced Rp 11 juta … kamu minta 100 juta untuk scope
mirip, itu 9 kali lipat"*, plus anak tangga terdekat Rp 4–8 juta. Tanpa browser,
jawaban untuk pertanyaan yang sama berhenti di *"belum terverifikasi"*.

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

   Belum punya usaha sama sekali juga boleh — skill ini justru dirancang untuk
   itu. Coba: *"pengen nambah penghasilan tapi bingung dari mana, saya cuma
   karyawan biasa."*

4. **Konten** (`ibras-content-creator`):
   > Buat 5 hook Instagram untuk konten "behind the scene produksi keripik",
   > bahasa santai, bukan marketer-an.

5. **Baca inbox (aman, read-only)** (`ibras-email-marketing`, setelah setup Gmail):
   > Baca inbox saya, mana email yang perlu dibalas hari ini? Jangan balas,
   > tunjukin dulu daftarnya.

6. **Rencana sosmed tanpa auto-posting nekat** (`ibras-social-publishing`):
   > Saya posting IG 4x sebulan, hasil sepi. Bikin pilot 2 minggu yang bisa
   > saya hentikan kapan saja.

Budaya kerja semua skill ini: **bukti dulu dan preview dulu**. Untuk promosi,
persetujuan owner atau flag `confirm` tidak pernah menggantikan izin penerima.
Kalau kamu minta hal yang berisiko—kirim massal, auto-kirim buta, atau memakai
data sensitif—skill akan mengerem dan menjelaskan blocker. Itu fitur, bukan
error.

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

Untuk OpenRouter, buka **API Keys → LLM Providers → OpenRouter** di Dashboard.
Jangan taruh API key di chat, screenshot, atau dokumen. Dokumentasi resmi UI:
[Web Dashboard](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)
dan [Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills).

## Update & uninstall

```bash
cd hermes-marketing-skills && git pull && bash installer/install.sh
bash installer/uninstall.sh      # hapus semua 7
```

Data bisnismu (`~/.hermes/business/profile.yaml`, FAQ, log) tidak pernah
disentuh oleh update maupun uninstall — itu milikmu.

## Kalau macet

| Gejala | Sebab & obat |
|---|---|
| Install lewat Hub jalan belasan menit lalu gagal / `403` / `rate limit` | Batas GitHub 60 request/jam habis. **Jangan diulang.** Pakai `git clone` + `installer/install.sh` di atas, atau pasang `GITHUB_TOKEN`. |
| Agent mulai `git clone` atau `curl` sendiri waktu disuruh install | Gejala yang sama — kuota API-nya sudah habis. Hentikan, pakai cara clone. |
| Skill tidak muncul di `hermes skills list` | Nama folder berubah/berprefiks — jangan ubah nama folder, atau `--home` salah |
| `hermes: command not found` | Hermes Agent belum terpasang. Pasang dulu, lalu ulangi installer. |
| Profile tidak kebaca / skill jalan aneh | `python3 -c "import yaml"` — kalau gagal: `pip3 install pyyaml` |
| Skill terpasang tapi Hermes nggak pernah kepake waktu ngobrol | Buka **Chat → New chat**. Skill baru aktif di sesi berikutnya, bukan sesi yang sedang jalan. |
| Mau lihat daftar tanpa pasang | `bash installer/install.sh --list` |

Identifier diuji pada Hermes Agent v0.20.2 (18 Agustus 2026) dan jalur
`git clone` + `installer/install.sh` diukur ulang pada v0.20.4 (20 Agustus 2026)
di container Incus Ubuntu baru: **2 detik, 7/7 enabled, 0 request GitHub API** (diukur 19 Agustus, waktu itu masih 7 skill).
