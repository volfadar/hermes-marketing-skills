# cloakserve-research

Hermes Agent skill untuk riset web publik yang reliable, menggunakan stealth
Chromium (CloakBrowser) via CDP, dengan opsi Tailscale exit node ke HP sendiri
untuk akurasi geo Indonesia.

## Install

```bash
# Copy folder skill ke Hermes skills directory
cp -R cloakserve-research ~/.hermes/skills/cloakserve-research

# Atau, kalau di-host via git:
hermes skills install <user>/hermes-marketing-skills/cloakserve-research
```

## Pakai

```bash
# Setup sekali (cek deps, start cloakserve, wire Hermes, smoke test)
bash ~/.hermes/skills/cloakserve-research/scripts/initialize.sh

# Riset
bash ~/.hermes/skills/cloakserve-research/scripts/research.sh "kopi arabika"

# Diagnosa kalau ada masalah
bash ~/.hermes/skills/cloakserve-research/scripts/doctor.sh

# Stop
bash ~/.hermes/skills/cloakserve-research/scripts/stop.sh
```

## Dokumentasi

- **`SKILL.md`** — manifest + quick start (baca dulu).
- **`references/faq.md`** — CloakBrowser vs cloakserve, batasan, FAQ.
- **`references/troubleshooting.md`** — error → fix table.
- **`references/ethics.md`** — apa yang boleh dan dilarang.
- **`references/architecture.md`** — bagaimana semua terhubung.
- **`references/cost.md`** — biaya OpenRouter / Tailscale.
- **`templates/`** — 6 prompt template siap pakai.
- **`examples/`** — contoh output riset.

## Etika (singkat)

Skill ini untuk **riset publik yang sah** (kompetitor, pasar, SERP). Bukan
untuk bypass login/paywall/ToS/anti-fraud, bukan untuk multi-accounting,
bukan untuk scraping massal yang ganggu target. Baca `references/ethics.md`.

## Komponen

- **CloakBrowser** — stealth Chromium (fingerprint di-patch di source C++).
- **cloakserve** — CDP multiplexer (disajikan di port 9222). Hanya ada di Docker image resmi.
- **Hermes Agent** — orchestrator dengan `browser` tool.
- **Tailscale** (opsional) — exit node ke HP kamu sendiri untuk IP residensial Indonesia.

## Lisensi

MIT. Lihat `SKILL.md` frontmatter.
