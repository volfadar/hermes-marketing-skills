---
name: ibras-cloakserve-research
description: Use for market research, buyer demand, competitors, prices, reviews, alternatives, trends, or evidence from public web pages. Separates seller-side supply from buyer-side signals and browses through a stealth CDP route when ordinary sites block access.
version: 1.0.0
author: Hermes Marketing Workshop
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Browser, CDP, Market-Research, Stealth, Affiliate, Marketing]
    related_skills: [research, firecrawl-scrape, firecrawl-search]
---

# CloakServe Research

## Market-fit gate — before any commercial recommendation

Read `references/market-adaptation.md`. If a money figure is ambiguous, first
separate **personal salary**, **business revenue**, profit/take-home, buyer
budget, and experiment cap; ask only the distinction that changes the next
action. **Supply is not demand:** a seller page proves an offer exists, not
that this buyer segment pays. Match geography, buyer/scale, purchase context,
current alternative, category language, and buyer-side evidence; then label
the route validated, plausible-test-only, unverified, or contradicted. Never
hardcode one country, channel, income band, or expert-method offer.

**First-turn stop rule.** “Short” means one short question, not permission to
skip the gate. When `income`, `penghasilan`, `earnings`, or another money word
could mean personal salary, business revenue, profit/take-home, or buyer
budget, **do not produce the plan yet**—ask which one it is. Do not invent
prices, margin, volume, conversion, cadence, speed, or impact. A past buyer or
chat history is not marketing consent; never turn it into proactive WA/email.
Ask naturally. Never mention the skill, rule, gate, market-fit card, or internal
labels to the owner.

**Unverified-offer stop.** If the only evidence is seller-side supply or a
different buyer segment, the paid category is unverified. Do not propose a
price, funnel, channel, or renamed version and do not invent how that segment
usually behaves. State the gap, define a buyer-side commercial test, and compare
the direct outcome, bundled diagnosis, and separately paid diagnosis. A catchy
local label that preserves the same work and buying reason still fails.
The response is limited to the evidence gap, one buyer-side test, and those
three shapes. Do not continue into a “helpful” generic plan while waiting.
Do not assert the target segment's budget, margin, awareness, channel, or
behaviour. Turn those into test questions, and leave sample, time, and price
caps for the user to set. When explaining a mismatch, state only that the
segment match is unproven; do not fill the gap with stereotyped reasons. Ask
for the missing reach, time, cash, or price constraint before sizing the test.

**Validated positive control.** Matching buyer-side payment is evidence to keep
the offer provisionally; never ban it by country or category. Check outcomes and
renewal or referral, delivery economics and capacity, plus contradictions before
scaling. Ask only the missing item that changes the next decision.
Name all four check areas in the response, then ask only the highest-priority
missing question.

A self-contained skill that lets you (or the agent) **reliably research public web
pages** — competitor landing pages, marketplace listings, SERPs, public forum
threads — using a stealth Chromium browser (CloakBrowser) exposed over CDP, with
an optional Tailscale exit-node so traffic egresses from your own phone's
Indonesian residential IP.

**Ethics (read `references/ethics.md`):** This is a *reliability layer for
legitimate public research*, NOT a bypass tool. No logins, no paywalls, no ToS
evasion, no anti-fraud circumvention, no mass scraping. The agent must refuse
anything that crosses these lines and explain why.

## When to Use
- "Riset 5 kompetitor di Tokopedia/Shopee — produk, harga, rating."
- "Cek bagaimana toko saya muncul di Google dari IP Indonesia."
- "Bandingkan landing page 3 kompetitor."
- "Cari pertanyaan nyata audience di forum/komunitas publik."
- "Riset tren mingguan di niche saya."

Don't use for: anything behind a login, paywalls, ToS-restricted scraping,
evading anti-fraud, or mass-volume scraping. If unsure, read
`references/ethics.md` and when still unsure, **ask the human**.

## Evidence discipline (READ `references/hermes-discipline.md` FIRST)

This skill exists to *retrieve* evidence. Retrieval is worthless if what you report is not what
you fetched. In recorded sessions, models using browser research cited vendor pages they
had never opened, harvested from Google result breadcrumbs and AI Overviews.

Non-negotiable for every research batch:

1. **Only a page you opened is a source.** Links, titles and snippets inside a results page are
   leads. A Google AI Overview is not evidence. Never describe a page you did not fetch.
2. **A results page is not a source even when you opened it.** Opening
   `tokopedia.com/search?q=…` licenses "I saw N listings priced X–Y on this results page" —
   nothing about any listing you did not open.
3. **Deliver a source ledger, not a link list.** Every row carries a retrieval status:

   | URL | Status | Fetched | What it actually supports |
   |---|---|---|---|
   | … | `opened` / `opened_empty` / `search_result` / `ai_summary` | date | one clause |

   Report failures — 404s, login walls, JS shells — rather than dropping them silently. A
   documented dead end is a finding; a quiet omission is a distortion.
4. **Minimum for a positioning-grade pass:** four successfully opened non-search pages across at
   least three evidence classes (customer language · alternatives & substitutes · buying context
   · economics/fees/policy). Twelve queries and zero opened pages is not research — deliver a
   research *plan* instead and say what is unverified.
5. **Tag every number** you extract: `[SOURCE: <url>]`. Prices, volumes and ratings copied from
   a snippet are `search_result`, not fact.
6. **Disclose the egress.** Indonesian marketplace and SERP results differ by IP. If Tailscale
   is not routing through an Indonesian residential IP, say so beside the results: *"riset ini
   tidak memakai IP Indonesia, hasil bisa berbeda dari yang Anda lihat."* The one model that
   volunteered this in testing gave the most trustworthy research note of the five.

Verify before delivering: `python3 scripts/check-citations.py <session> --strict`

## Prerequisites
- **Docker** installed and runnable by current user.
- **Hermes Agent** with the `browser` tool enabled.
- **(Optional)** Tailscale, for residential-IP egress via your own phone.

## Quick Start (one command)

```bash
bash "${HERMES_SKILL_DIR}/scripts/initialize.sh"
```

This will: check deps → pull CloakBrowser image → start cloakserve container →
wire Hermes → smoke test → optionally suggest Tailscale. Idempotent — safe to
re-run.

## The 6 commands you'll actually use

| Command | What it does |
|---|---|
| `bash scripts/initialize.sh` | One-shot full setup. **Start here.** |
| `bash scripts/research.sh "<query>"` | Prep infra + print a ready-to-paste prompt |
| `bash scripts/research.sh --list` | See all available prompt templates |
| `bash scripts/status.sh` | Quick status check |
| `bash scripts/doctor.sh` | Full diagnostic (run when anything breaks) |
| `bash scripts/stop.sh` | Stop & remove container |

## How to Run a Research Task

### Option A: Use the helper (recommended for beginners)
```bash
bash scripts/research.sh "kopi arabika"
# → starts cloakserve if needed, wires Hermes, prints a ready prompt
# → paste that prompt into Hermes
```
Pick a specific template:
```bash
bash scripts/research.sh "kopi arabika" --template competitor-marketplace
bash scripts/research.sh "manual brew" --template forum-questions
bash scripts/research.sh "https://toko-contoh.com" --template landing-page-audit
```

### Option B: Direct prompt (for the agent)
```
Riset <thing>. Langkah:
1. Cek status: bash ${HERMES_SKILL_DIR}/scripts/status.sh
2. Pakai browser (CDP ws://127.0.0.1:9222) buka <url>
3. Ambil <data yang diminta>.
Output tabel markdown. Hanya riset publik.
```

## Procedure (the steps the agent follows)

1. **Ask the human what they want to research and why.** Confirm it's public,
   legitimate market research. If it needs a login, paywall, or evades
   anti-fraud — **refuse and explain** (point them to `references/ethics.md`).
2. **Check status** with `bash scripts/status.sh`. If not running, ask the
   human whether to start it (`bash scripts/initialize.sh` or `start.sh`).
3. **About Tailscale**: if not set up, mention it's optional for Indonesia
   geo-accuracy. **Always ask before running `tailscale-setup.sh`** — it's
   interactive and modifies network routing. Explain pros/cons
   (see `SKILL.md` section "Tailscale" below and `references/faq.md`).
4. **Run the research** via the browser tool. For each page, capture only what
   the human asked for. **Do not log in, do not submit forms, do not click
   "buy".** If a site requires a login to view content, stop and tell the human.
5. **Deliver as clean markdown table/summary** the human can act on. Flag
   anything that looked gated or that you couldn't reach.
6. **Stop the browser** with `bash scripts/stop.sh` when the session is over.

## Tailscale (ask before enabling)

**Pros of routing cloakserve through your own phone (Tailscale exit node):**
- Traffic egresses from a real Indonesian residential IP — marketplace SERPs,
  geo-restricted promo banners, local prices appear as a local user sees them.
- Free (Tailscale personal tier). End-to-end encrypted.
- It's your *own* connection on your *own* phone — not a purchased proxy.

**Cons / trade-offs:**
- Uses phone's mobile data when active (turn off when not researching).
- Needs a one-time Tailscale account + app install on the phone (~5 min).
- Adds latency.

**Always explain and get a clear "yes" before running `tailscale-setup.sh`.**

## Why this skill exists (and what it's NOT)

- CloakBrowser (stealth Chromium) **solves the problem of public sites that
  block plain headless browsers** — Tokopedia, Shopee, news sites with Captcha.
  You're not "tricking" anyone; you're just not being falsely flagged as a
  malicious bot for doing legitimate research.
- Tailscale exit node **solves the geo-accuracy problem** — research from a
  datacenter IP outside Indonesia shows different SERPs/promos than what your
  audience sees. Your own phone's IP is the ground truth.
- This skill is **explicitly NOT** for: account automation, multi-accounting,
  bypassing platform anti-fraud, scraping at volumes that harm targets, or
  accessing gated content. Those will get accounts banned and may violate laws.

## Pitfalls
- **Don't leave cloakserve running 24/7** — stop it when the session ends
  (`bash scripts/stop.sh`).
- **First start downloads ~150MB** stealth Chromium binary (a few minutes).
- **If `/json/version` returns 502**, inner Chromium is still starting. Wait
  30-60s; `status.sh` reports progress.
- **Deepseek-v4-flash is "stupid" at multi-step abstractions** — don't ask it
  to "follow SKILL.md". Use `research.sh` (which uses explicit templates) or
  paste a template from `templates/` directly.
- **Tailscale exit node uses your phone's data** — turn off when not researching
  (`sudo tailscale up --exit-node=`).
- **Don't share `--fingerprint` seeds publicly** — they're stable identities.

## Verification (after setup)
- [ ] `bash scripts/doctor.sh` shows mostly ✓ (no ✗ fail).
- [ ] `bash scripts/status.sh` shows "container: running" + "cdp: reachable" + "wired: yes".
- [ ] A `browser_navigate` to a public page returns real content.
- [ ] Every research batch is shown to the human for review before being used.
- [ ] No login pages, no form submissions, no purchases were attempted.

## Documentation

Read these (in `references/`):
- **`hermes-discipline.md`** — source tiers, number tags, red flags (READ FIRST)
- **`hermes-runtime.md`** — what the HOST already does: scheduler, job notepad, monitor-mode, cost screen, consent gates. **READ BEFORE BUILDING ANYTHING** — most "we need a script for that" turns out to be a flag
- **`tools-mapping.md`** — which tool for which learning job, and which jobs are bought rather than built
- **`repliz.md`** — official route for comments/DMs/scheduling on IG · FB · TikTok · YouTube · Threads (from Rp 18.000, one-time). Does **not** cover WhatsApp or email
- **`automation-posture.md`** — how to answer an automation request: warn, offer, do. READ BEFORE REFUSING ANYTHING
- **`faq.md`** — termink (CloakBrowser vs cloakserve?), limits, common questions.
- **`troubleshooting.md`** — symptom → cause → fix table.
- **`ethics.md`** — what's OK and NOT OK to research (READ FIRST).
- **`architecture.md`** — how everything connects.
- **`cost.md`** — OpenRouter / Tailscale / Pro tier costs + minimize strategies.

Templates (in `templates/`):
- `competitor-marketplace.txt` — 5 produk di Tokopedia/Shopee
- `forum-questions.txt` — pertanyaan nyata dari komunitas
- `landing-page-audit.txt` — analisis landing page kompetitor
- `serp-check.txt` — top 10 hasil Google
- `product-research.txt` — riset mendalam 1 produk
- `niche-trend.txt` — tren mingguan di niche

Examples (in `examples/`):
- `sample-output-marketplace.md` — contoh output riset kompetitor

<!-- HERMES_BUNDLE_MANIFEST_START -->
## Hermes bundle manifest

Hermes Skills Hub installs only support files linked directly from this file.
These links are the complete runtime manifest; load individual files only when needed.

### examples

- [examples/sample-output-marketplace.md](examples/sample-output-marketplace.md)

### references

- [references/architecture.md](references/architecture.md)
- [references/automation-posture.md](references/automation-posture.md)
- [references/cost.md](references/cost.md)
- [references/ethics.md](references/ethics.md)
- [references/faq.md](references/faq.md)
- [references/hermes-discipline.md](references/hermes-discipline.md)
- [references/hermes-runtime.md](references/hermes-runtime.md)
- [references/market-adaptation.md](references/market-adaptation.md)
- [references/repliz.md](references/repliz.md)
- [references/tools-mapping.md](references/tools-mapping.md)
- [references/troubleshooting.md](references/troubleshooting.md)

### scripts

- [scripts/check-citations.py](scripts/check-citations.py)
- [scripts/check-numbers.py](scripts/check-numbers.py)
- [scripts/doctor-common.sh](scripts/doctor-common.sh)
- [scripts/doctor.sh](scripts/doctor.sh)
- [scripts/halt.sh](scripts/halt.sh)
- [scripts/help.sh](scripts/help.sh)
- [scripts/hooks/artifact-guard.py](scripts/hooks/artifact-guard.py)
- [scripts/initialize.sh](scripts/initialize.sh)
- [scripts/install-guard.sh](scripts/install-guard.sh)
- [scripts/lib/copycheck.py](scripts/lib/copycheck.py)
- [scripts/lib/halt.py](scripts/lib/halt.py)
- [scripts/lib/handoff.py](scripts/lib/handoff.py)
- [scripts/lib/ledger.py](scripts/lib/ledger.py)
- [scripts/lib/profile.py](scripts/lib/profile.py)
- [scripts/lib/replycheck.py](scripts/lib/replycheck.py)
- [scripts/lib/watch.py](scripts/lib/watch.py)
- [scripts/preflight.sh](scripts/preflight.sh)
- [scripts/research.sh](scripts/research.sh)
- [scripts/start.sh](scripts/start.sh)
- [scripts/status.sh](scripts/status.sh)
- [scripts/stop.sh](scripts/stop.sh)
- [scripts/tailscale-setup.sh](scripts/tailscale-setup.sh)
- [scripts/wire-hermes.sh](scripts/wire-hermes.sh)

### templates

- [templates/competitor-marketplace.txt](templates/competitor-marketplace.txt)
- [templates/forum-questions.txt](templates/forum-questions.txt)
- [templates/landing-page-audit.txt](templates/landing-page-audit.txt)
- [templates/niche-trend.txt](templates/niche-trend.txt)
- [templates/product-research.txt](templates/product-research.txt)
- [templates/profile.example.yaml](templates/profile.example.yaml)
- [templates/serp-check.txt](templates/serp-check.txt)

<!-- HERMES_BUNDLE_MANIFEST_END -->
