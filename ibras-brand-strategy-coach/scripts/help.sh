#!/usr/bin/env bash
# help.sh
cat <<HELP
ibras-brand-strategy-coach — skill coaching 5-tahap branding & marketing
=================================================================

Flow:
  bash start-session.sh [--user X]    # Stage 1: Temu Bakat
  bash stage2.sh [--user X]           # Stage 2: Background Interview
  bash stage3.sh [--user X]           # Stage 3: Brand Positioning
  bash stage4.sh [--user X]           # Stage 4: Tool Integration
  bash stage5.sh [--user X]           # Stage 5: Funnel Design

Save & resume:
  bash save-profile.sh stage3 --data '<json>'    # save stage output
  bash resume.sh [--user X]                       # lanjut stage terakhir

Profile disimpan di:
  ~/.brand-coach/profiles/<user>.json

Output Stage 3 (positioning) → USER.md Hermes memory + ibras-content-creator pillars.

Dokumen di references/:
  philosophy.md     kenapa strategy sebelum tools
  temu-bakat.md     tes bakat sumber + channel mapping
  niche-down.md     teknik A → A.1 → A.2 → A.3
  funnel-ethics.md  soft selling, bridging, anti-spam
  tools-mapping.md  profile × tool recommendation

⚠  JANGAN skip tahap. Positioning tanpa bakat/background = generic.
HELP
