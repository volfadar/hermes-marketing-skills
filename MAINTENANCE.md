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

# 3. Commit + push, lalu bangun bundel untuk peserta:
git add -A && git commit -m "..." && git push
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
  distribusi offline.
- `hermes skills list` di profile lain: `HERMES_HOME=/path hermes skills list`.

## Jalur install GitHub — hasil scan per skill (14 Agu 2026)

Repo live: https://github.com/volfadar/hermes-marketing-skills
(branch `master`; remote `origin` sudah dikonfigurasi — `git push` saja.)

| Skill | `hermes skills install volfadar/hermes-marketing-skills/<skill>` |
|---|---|
| marketing-orchestrator | ✅ lolos scan |
| content-creator | ✅ lolos scan |
| brand-strategy-coach | ❌ DANGEROUS (dokumen anti-injeksi memuat pola serangan) |
| social-publishing | ❌ DANGEROUS (pembahasan API tidak resmi + browser automation) |
| email-marketing | ❌ DANGEROUS (kredensial IMAP dari env, kirim email, regex deteksi injeksi) |
| waha-marketing | ❌ DANGEROUS (kirim HTTP ke WAHA) |
| cloakserve-research | ❌ DANGEROUS (browser stealth — intrinsik ke fungsi skill) |

Dua CRITICAL false-positive pertama sudah diredam di sumber (contoh
pipe-ke-python di docstring copycheck; kalimat injeksi literal di
hermes-discipline.md) — itu yang membuat 2 skill lolos. Sisanya intrinsik ke
isi skill; jangan menulis ulang konten keamanan demi skor pemindai. Kalau
suatu saat skills.sh punya jalur verifikasi penerbit, angka di atas layak
diukur ulang. Jalur andalan peserta tetap bundel zip + installer (Cara A di
README) — folder-copy tidak melalui pemindai.

`hermes skills tap add` TIDAK cocok untuk repo ini: tap mengharapkan subfolder
`skills/` (repo ini menyimpan skill di root), dan nama pendek bisa me-resolve
ke skill orang lain yang bernama sama — terverifikasi secara langsung
(sempat ter-install "Marketing Orchestrator" milik orang lain lewat jalur
ini). Gunakan identifier lengkap `volfadar/hermes-marketing-skills/<skill>`.
