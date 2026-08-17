#!/usr/bin/env bash
# help.sh — quick command reference.
cat <<HELP
ibras-cloakserve-research — skill command reference
=============================================

Quick start:
  bash initialize.sh                    full setup (deps + start + wire + smoke test)
  bash research.sh "<query>"            prep infra + print ready prompt
  bash research.sh --list               list all prompt templates

Lifecycle:
  bash start.sh                         start the stealth CDP browser
  bash stop.sh                          stop & remove container
  bash status.sh                        show status (container + CDP + wiring + tailscale)
  bash status.sh --logs                 also tail container logs

Diagnostics:
  bash doctor.sh                        full diagnostic with pass/warn/fail summary
  bash doctor.sh --brief                one-line summary

Wiring (usually called by initialize):
  bash wire-hermes.sh                   point Hermes's browser.cdp_url at cloakserve

Optional (research reliability for Indonesia):
  bash tailscale-setup.sh               interactive — route via your own phone's IP

Prompt templates (use from research.sh, or paste manually):
  competitor-marketplace                5 produk di Tokopedia/Shopee + pola harga
  forum-questions                       pertanyaan nyata dari Reddit/FB group
  landing-page-audit                    analisis landing page kompetitor
  serp-check                            cek top 10 hasil Google untuk keyword
  product-research                      riset mendalam 1 produk (review, harga, seller)
  niche-trend                           tren mingguan di niche kamu

Docs in references/:
  faq.md                                termink (CloakBrowser vs cloakserve?), limits
  troubleshooting.md                    error → fix table
  ethics.md                             what's OK and NOT OK to research
  architecture.md                       bagaimana semuanya terhubung
  cost.md                               biaya OpenRouter / Nous Portal / Tailscale

Ethics reminders:
  - Riset PUBLIK saja. Tidak login, tidak bypass paywall/ToS/anti-fraud.
  - Tidak scraping volume tinggi yang ganggu target.
  - Hermes DRAFT. Manusia REVIEW sebelum apa pun terlihat customer.
HELP
