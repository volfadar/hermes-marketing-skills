# brand-strategy-coach

Hermes skill untuk coaching strategis 5 tahap: hipotesis bakat → dossier CV/
portfolio → riset dan positioning → eksperimen/tools → journey graph. Skill ini
dipakai sebelum memasang rangkaian tools pemasaran.

## Install

```bash
cp -R brand-strategy-coach ~/.hermes/skills/brand-strategy-coach
```

## Pemakaian (1-on-1 per peserta)

Untuk sesi produksi yang harus reproducible, matikan background
skill review — Hermes secara default dapat mencoba mengedit skill di tengah
sesi. Lewat `hermes config`, set `skills.creation_nudge_interval: 0` dan
`skills.write_approval: true`, lalu `provider_routing.data_collection: deny`.

Jalankan review/improvement skill sebagai sesi terpisah setelah coaching. Opsi
`write_approval` juga menahan perubahan skill lain sampai pengguna menyetujuinya.
Untuk CV asli, pertahankan data-policy filter ini dan redaksi data sensitif;
jangan longgarkan routing hanya untuk mengejar provider termurah.

```bash
# Stage 1: Temu Bakat
export USER_NAME="dini"
bash ~/.hermes/skills/brand-strategy-coach/scripts/start-session.sh --user "$USER_NAME"

# (jalankan sebagai percakapan bertahap, lalu simpan evidence yang sudah dikonfirmasi)
bash ~/.hermes/skills/brand-strategy-coach/scripts/save-profile.sh stage1 \
  --data '{"talent":{"tests":{},"hypotheses":[],"behavioral_evidence":[],"accommodations":[]}}'

# Stage 2: Background
bash ~/.hermes/skills/brand-strategy-coach/scripts/stage2.sh --user "$USER_NAME"
# ... dst sampai stage 5
```

## Output = Input untuk 3 skill lain

- Stage 2 dossier → bukti kerja, akses pasar, batasan, dan gap yang masih harus diwawancarai
- Stage 3 positioning → research note, tiga territory, pilihan, dan falsification test
- Stage 4 experiment → satu tes murah beserta tool yang benar-benar dibutuhkan
- Stage 5 journey graph → beberapa route/bridge yang mengikuti budget dan unit economics

## Dokumen

- `SKILL.md` — manifest lengkap
- `references/hermes-discipline.md` — **BACA DULU.** 7 aturan keras: sumber = halaman yang
  dibuka, tag provenance untuk tiap angka, constraint register, goal reconciliation, tangga
  bukti demand, koreksi harus sampai ke file, dan larangan mengubah skill saat sesi berjalan
- `references/economics-and-goal-fit.md` — revenue vs contribution vs take-home, utilisasi,
  trade-off kapasitas × harga, dan pernyataan goal reconciliation
- `references/philosophy.md` — strategy before tools
- `references/personality-interests.md` — Big Five × O*NET RIASEC combined framework
- `references/big-five.md` — Big Five (OCEAN) detail: 5 domains, 30 facets, channel patterns
- `references/conversation-and-dossier.md` — aturan percakapan manusiawi dan extraction CV/portfolio
- `references/evidence-and-research.md` — standar evidence, browsing, citation, dan research note
- `references/positioning-lab.md` — territory levers, scoring, remembered cue, dan proof
- `references/niche-down.md` — teknik A → A.3
- `references/funnel-ethics.md` — value ladder, parallel routes, economics, consent, dan anti-spam
- `references/tools-mapping.md` — profile × tool matrix
- `examples/sample-profile-dini.md` — contoh lengkap output 5 tahap

## Validator (jalankan sebelum mengirim deliverable)

Aturan berbentuk prosa terbukti tidak cukup: lima model membaca aturan yang sama dan lima-
limanya melanggarnya. Yang bisa dicek mesin, dicek mesin.

```bash
bash scripts/preflight.sh --user rizki \
     --session out/session.jsonl --artifact out/plan.md
```

| Script | Yang dicek |
|---|---|
| `scripts/check-citations.py` | Tiap URL yang dikutip: FETCHED / SERP_ONLY / UNSOURCED |
| `scripts/check-numbers.py` | Angka tanpa tag, asumsi yang dipakai sebagai alasan, klaim yang sudah ditarik tapi masih ada di file |
| `scripts/preflight.sh` | Gate tiap stage, integritas sitasi, provenance angka, dan higiene sesi |
| `scripts/sync-discipline.sh` | SHIM — meneruskan ke `shared/sync.sh`. Aturan kanonik kini di `shared/references/`, disalin ke **tujuh** skill bersama penegaknya |
| `scripts/doctor.sh` | Periksa skill ini siap dipakai (dulu satu-satunya skill tanpa doctor) |

## Filosofi

Coaching dibangun dari percakapan, bukan satu formulir panjang. Hasil tes adalah
hipotesis; CV, portfolio, dan contoh kerja adalah bukti; browsing adalah gate
sebelum klaim positioning. Saran akhir harus menunjukkan sumber, asumsi,
eksperimen termurah, serta hal yang bisa membatalkan rekomendasi.

## Lisensi

MIT.
