#!/usr/bin/env bash
cat <<HELP
content-creator — skill untuk konten kreator sosial (tanpa auto-post)
=====================================================================

Quick start:
  bash voice-profile.sh ~/samples/      # sekali: ekstrak suara kamu
  bash pillars.sh "p1, p2, p3"          # sekali: set 3-5 pilar konten
  bash ideate.sh --week --platform X    # 10 ide konten
  bash repurpose.sh source.md           # 1 konten → N platform variant
  bash calendar.sh --weeks 2            # kalender markdown
  bash caption.sh "topic" --platform X  # draft 1 caption
  bash audit.sh stats.csv --month       # review performa
  bash doctor.sh                        # diagnose

Platform yang didukung (format-aware): instagram, tiktok, youtube, x, linkedin, blog.

⚠  TIDAK ADA auto-posting. Semua output = DRAFT untuk review + post native.
⚠  Baca references/philosophy.md kenapa.

Dokumen di references/:
  philosophy.md       kenapa no auto-post, humanized alignment
  platforms.md        format/length/CTA/cadence per platform (2026)
  voice.md            cara bangun + rawat brand voice
  repurposing.md      hub-and-spoke method
  calendar-template.md template kalender mingguan

Templates di templates/:
  ideation.txt, repurpose.txt, caption.txt, audit.txt, calendar.txt, hooks.txt
HELP
