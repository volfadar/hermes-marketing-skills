# ibras-content-creator

Hermes skill untuk content kreator sosial — ideate, repurpose, calendar,
caption, audit — **tanpa auto-posting**.

## Install

```bash
cp -R ibras-content-creator ~/.hermes/skills/ibras-content-creator
```

## Setup

```bash
bash scripts/voice-profile.sh ~/samples/   # sekali: ekstrak voice kamu
bash scripts/pillars.sh "p1, p2, p3"       # sekali: set pillars
```

## Pemakaian

```bash
bash scripts/ideate.sh --week --platform instagram
bash scripts/repurpose.sh source.md --platforms all
bash scripts/calendar.sh --weeks 2 --platform instagram
bash scripts/caption.sh "topic" --platform tiktok
bash scripts/audit.sh stats.csv --month
```

## Dokumen

- `SKILL.md` — manifest
- `references/philosophy.md` — kenapa no auto-post
- `references/platforms.md` — format per platform 2026
- `references/voice.md` — bangun + rawat voice
- `references/repurposing.md` — hub-and-spoke method
- `references/calendar-template.md` — template kalender

## Filosofi

AI membantu produksi. Manusia yang engage. Tidak ada auto-posting, tidak ada
bot engagement. Hermes DRAFT, kamu review + post native.

## Lisensi

MIT.
