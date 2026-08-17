# Tool Selection by Learning Job

<!-- CANONICAL SOURCE: shared/references/tools-mapping.md
     Synced into every skill by shared/sync.sh. Edit the canonical copy only.

     This file used to live inside ibras-brand-strategy-coach/references/, which
     meant five of six skills could not see it. A session that started at
     ibras-waha-marketing picked its tools by keyword match on the user's first sentence.
     It is shared now for that reason. -->

## Principle

Choose a tool because the next experiment needs a specific output. Do not recommend
every installed tool, and do not use a business-type lookup table as strategy.

Research happens before final positioning for every business. Scope it to decision
value: a low-margin product may deserve a one-hour fee/competitor/review check, not a
week-long report.

**Before adding any tool to this table, ask the DRY question in order:** does Hermes
already do this? does a tool we already pay for already do this? Only then build.
See `hermes-runtime.md` §5 for the division of labour.

## Jobs

### Deciding and evidence

| Job | Tool | First useful output | Do not use when |
|---|---|---|---|
| public market/customer research | `ibras-cloakserve-research` | evidence note with direct sources | the answer requires private data or interviews |
| positioning test asset | `ibras-content-creator` | one landing page, listing, post, or invitation variant | message/offer is still undefined |
| qualitative validation | manual interview/outreach | notes from 5–10 qualified conversations | public research can answer it faster |
| pricing/economics check | spreadsheet/manual calculation | contribution and payback range | cost inputs are invented |

### Reaching people

| Job | Tool | First useful output | Do not use when |
|---|---|---|---|
| opted-in WhatsApp follow-up | `ibras-waha-marketing` | reviewed, segmented dry run | contacts did not consent |
| email nurture/sequence | `ibras-email-marketing` (Gmail SMTP/IMAP) | one sequence tied to a real commitment bridge | no relevant subscriber/prospect list |
| **comments & DMs on IG · FB · TikTok · YouTube · Threads** | **Repliz** (`references/repliz.md`) | one automation rule live on one account | the platform is WhatsApp or email — Repliz covers neither |
| **scheduling social posts** | **Repliz** Content Management | one week queued from the content calendar | the post still fails `copycheck.py` |
| logged-in browser clicking on a business account | **nothing. Do not.** | — | always. Use the platform's official route |

### Running without you

| Job | Tool / mechanism | First useful output | Do not use when |
|---|---|---|---|
| watch something that changes on a clock | `scripts/lib/watch.py` → `hermes cronjob` monitor-mode | one draft delivered, **only on real change** | it changes less often than monthly — just check by hand |
| remember across runs | job notepad keys | `contacted_ids`, `last_posted_url`, `last_price` | the job is genuinely stateless |
| stop everything, now | `scripts/halt.sh on` | every outbound path stops at the next message boundary | — (this one always applies) |

### Closing the loop

| Job | Tool | First useful output | Do not use when |
|---|---|---|---|
| drain the escalation queue | `handoff.py answer` → FAQ | one answered question that never rises again | the answer commits money, or makes a health/legal claim |
| close a session | `ledger.py add` / `show` / `open` | one name for tomorrow | nothing was produced — say that instead |
| turn a client voice note into an action | transcription on intake → `ledger.py add --kind waiting` | one line, not three minutes of audio | the customer asked for privacy |
| answer "is this expensive?" | per-profile `totalCostUsd` in Hermes | the actual number | you do not have the number — then say so, do not estimate |

Read the selected tool's `SKILL.md` before invoking it.

## Selection sequence

1. State the riskiest assumption.
2. Decide what observation would reduce uncertainty.
3. Pick the cheapest ethical method.
4. Set budget/time cap and sample.
5. Define stop/scale rule.
6. Choose one main tool; add one support tool only when necessary.

## Examples

### Same-product retail

Risk: buyers may not value a fit-assurance service.

- Main: manual prototype listing or content asset.
- Support: quick research into reviews, platform fees, and competitor guarantees.
- Defer: WA automation until opt-in customers exist.

### B2B service

Risk: economic buyers may not trust the user's proof.

- Main: research buyer context and alternatives.
- Support: create a scoped diagnostic or case-study asset.
- Defer: a large newsletter system until qualified prospects engage.

### Two-market/affiliate

Risk: recruited partners may not activate.

- Main: interview/recruit a small qualified partner sample.
- Support: create one enablement kit.
- Measure partner activation separately from end-user conversion.

### Creator drowning in comments

Risk: the owner quits because the volume is unmanageable, and quitting looks exactly
like "the marketing didn't work".

- Main: Repliz on the one platform with the most inbound, in draft/FAQ posture first.
- Support: `handoff.py` so the questions that do reach her drain out of the queue
  permanently instead of recurring.
- Do **not**: build a comment poller. Do **not**: point a browser at her logged-in
  account.

## Output

```yaml
experiment:
  assumption:
  sample:
  action:
  budget_cap:
  time_box:
  signal:
  stop_rule:
  scale_rule:
tools:
  selected:
    - name:
      job:
      first_output:
  deferred:
    - name:
      reason:
```

Tool setup is complete only when its first output serves the experiment.
