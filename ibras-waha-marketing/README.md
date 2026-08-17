# ibras-waha-marketing

Hermes skill untuk WhatsApp marketing via WAHA — contacts, labels, groups,
broadcast, dengan **anti-ban humanization baked into code**.

## Install

```bash
cp -R ibras-waha-marketing ~/.hermes/skills/ibras-waha-marketing
```

## Setup (one command)

```bash
bash ~/.hermes/skills/ibras-waha-marketing/scripts/initialize.sh \
  --url https://your-waha.example \
  --key YOUR_API_KEY \
  --session all-in-one-device
```

## Pemakaian

```bash
# Read (safe)
bash scripts/waha.sh status
bash scripts/waha.sh groups
bash scripts/waha.sh contacts --limit 20

# Broadcast (humanized, opt-in required, dry-run first)
bash scripts/broadcast-helper.sh --contacts c.csv --templates t.txt --dry-run
bash scripts/broadcast-helper.sh --contacts c.csv --templates t.txt --i-confirm-optin

# Emergency stop
bash scripts/emergency-halt.sh
```

## Dokumen

- `SKILL.md` — manifest + quick start
- `references/anti-ban.md` — **BACA DULU** sebelum broadcast apapun
- `references/api-reference.md` — semua endpoint WAHA
- `references/broadcast-guide.md` — broadcast sehat end-to-end
- `references/ethics.md` — opt-in, UU ITE/PDP
- `references/examples.md` — contoh CSV, template, webhook

## Etika (singkat)

Opt-in only. Tidak ada cold outreach. Tidak ada auto-broadcast. Hermes draft,
manusia review + trigger. Baca `references/anti-ban.md` dan `references/ethics.md`.

## Lisensi

MIT.
