# MAINTENANCE — untuk penyelenggara, bukan peserta

Repo ini adalah **repo distribusi**. Sumber kebenaran tetap repo workshop
(`hermes-for-marketing`): skill dikembangkan di sana, lalu ditarik ke sini.
Materi kursus, persona, dan eval TIDAK PERNAH ikut ke sini — `audit.sh`
menjaga itu.

## Alur kerja

```bash
# 1. Setelah mengubah skill di repo workshop:
cd ~/hermes-for-marketing && bash shared/sync.sh

# 2. Tarik ke repo distribusi ini (bersihkan + audit otomatis):
cd ~/hermes-marketing-skills && bash installer/sync-from-source.sh

# 3. Commit, lalu bangun bundel untuk peserta:
bash installer/make-bundle.sh     # → dist/hermes-marketing-skills-<tanggal>.zip
```

## Yang dijaga audit.sh

- ID sesi eval internal (`s3-...`) dan kode model uji (`dspro`, `hy3`)
- Istilah metodologi eval (scoreboard, corpus, forward test, evaluation repository)
- Pointer ke file materi kursus (`5-tangga.md`, `materi workshop`, dst.)
- Biaya "per peserta" workshop
- Nama persona workshop
- Path internal (`hermes-for-marketing`, `/root/`)
- `__pycache__` / `*.pyc`

Audit gagal = bundel tidak boleh dibagikan. Kalau ada hit yang menurutmu sah
(mis. nama model di tabel biaya sebagai rekomendasi), tambahkan pengecualian
yang sempit di `audit.sh` — jangan matikan audit.

## Fakta platform yang sudah diverifikasi (14 Agu 2026)

- Hermes menemukan skill lokal dari `~/.hermes/skills/<nama>/` dengan
  **nama folder == `name:` frontmatter**. Folder berprefiks `skill-` TIDAK
  ditemukan — karena itu repo sumber memakai prefiks (kerapian repo) dan
  repo ini tidak.
- `hermes skills snapshot export` hanya mengekspor skill yang di-install dari
  registry — skill lokal (copy folder) tidak ikut. Folder-copy adalah jalur
  distribusi offline; `hermes skills install <owner>/<repo>/<skill>` jalur
  online begitu repo ini di-publish.
- `hermes skills list` di profile lain: `HERMES_HOME=/path hermes skills list`.

## Push ke GitHub (sewaktu-waktu dibutuhkan)

Repo ini sudah `git init` + commit awal. Untuk mengaktifkan jalur install
online:

```bash
git remote add origin git@github.com:<user>/hermes-marketing-skills.git
git push -u origin main
```

Lalu README peserta (Cara B) tinggal mengganti `<user>` dengan nama akun.
Tidak ada perubahan struktur yang dibutuhkan — setiap folder skill sudah
berdiri sendiri dengan SKILL.md di akar folder.
