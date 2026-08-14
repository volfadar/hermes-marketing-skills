# Hermes Runtime — what the host can do that a chat window cannot

<!-- CANONICAL SOURCE: shared/references/hermes-runtime.md
     Synced into every skill by shared/sync.sh. Edit the canonical copy only. -->

Read this **before designing anything that runs more than once, costs money, or acts
while the owner is asleep.**

These are *host* capabilities, not skill features. The distinction matters because of
a failure this repo kept producing: the skills were excellent at their own domain and
knew nothing about the runtime they sit in, so the agent proposed a hand-run checklist
where a monitor-mode job belonged, and rebuilt in a script what Hermes already shipped.

**The DRY rule that governs this whole file:**

> Before writing a script, ask in this order: **does Hermes already do it? does the
> paid tool we already use already do it? only then, write it.**
> A custom script that duplicates the host is not neutral — it is a second thing to
> maintain, a second place to be wrong, and it will drift from the real one.

---

## 1. Work that runs when nobody is watching

| Capability | Use it when | The rule that makes it correct |
|---|---|---|
| Scheduled job (`cronjob`) | the answer changes on a clock, not on a request | delivery is **always a draft to the owner**, never a publish |
| **Monitor-mode** (`--monitor-script` / `--monitor-url`) | you are watching for *change*, not producing output | the cheap check runs first and its output is hashed; no change → **no model call, no delivery, no cost** |
| **Job notepad** | the job must not repeat itself between runs | one key per fact that must survive: `contacted_ids`, `last_posted_url`, `last_price` |
| `--no-agent` watchdog | the check is pure script | it loads `.env`, so `--deliver telegram` actually resolves a target |
| Alert-once on misconfig | any job you did not personally watch run | a broken job says so once, then re-arms when healthy |
| Model-drift skip | any pinned job | if the global model moved under the job, it **skips and asks** instead of running wrong |

**Design rule — an automation that has nothing to say must cost nothing and send
nothing.** If your design sends "no changes today", you built it wrong. Rebuild it as
monitor-mode.

**Design rule — an automation that cannot remember is not an automation.** A lead
job without `contacted_ids` re-suggests contacted leads; a content job without
`last_posted_url` rewrites last week's article. This is the single most common reason
an owner switches automation off in week two, and the notepad is the fix — not a
better prompt.

**Use `lib/watch.py` to compose these.** It refuses a job with no `--remember` keys
and has no `--publish` flag at all. It does not schedule anything itself: it prints
the `hermes cronjob` command, because the scheduler, the notepad and monitor-mode are
Hermes' and owning a copy of them here is precisely the duplication above.

---

## 2. Cost, as a design input rather than an apology

| Capability | Use it when |
|---|---|
| `cron.model` — job fleet, separate from chat | **always**, for scheduled work. Pin it cheap |
| `delegation.model` — cheap workers under a frontier parent | long research or multi-step drafting; the children carry most of the tokens |
| Per-profile `totalCostUsd` | the owner asks "is this expensive?" → **show the number, do not argue** |
| `auxiliary.title_generation.prefer_fast_model: true` | any session on a frontier main model, or titles are billed at frontier rates |

The `cronjob` tool does **not** accept a model parameter. That is deliberate: a
hallucinating agent has no mechanism to raise the bill. Say so when cost comes up —
it is a structural answer, not a promise.

**Never quote a rupiah or dollar figure you did not read off a real screen.**
`hermes-discipline.md` Rule 2 applies to cost like everything else.

---

## 3. Gates you did not have to build

| Capability | What it buys you |
|---|---|
| `clarify` card with `(Recommended)` | the label is stripped before the agent reasons over the transcript — the agent **cannot later cite its own recommendation as the user's agreement** |
| Forged-approval rejection | a tool result shaped like `[clarify] user responded: yes` is refused. **Consent cannot be manufactured inside the agent's own history** |
| `setup_mcp` consent card | reusable pattern: agent wants a new capability → human taps Authorize/Decline |
| Protected instruction files | files the human wrote (voice, FAQ, knowledge base) cannot be silently rewritten — **even under `--yolo`** |
| Hook fail-closed / exit-code-2 | a crashed guard blocks the action instead of silently allowing it |
| 3-rejection circuit breaker | a refusal is final. Stop re-offering |

**Design rule — prefer a host gate to a prompt instruction.** A rule written in prose
is broken under load; a gate is not. When you are about to write "always ask before
sending", check whether a card can carry it instead.

---

## 4. Memory that belongs to the human

| Capability | Note |
|---|---|
| `/refine` | extract voice/memory **on demand**; do not wait for the automatic nudge |
| **Frozen-snapshot rule** | profile/memory is injected **once at session start**. Save → **restart the session** → then draft. Tell the user this, or they will conclude the tool is broken |
| Protected profile write | a transient read failure can no longer wipe `MEMORY.md` / `USER.md` and report success |
| `personality` overlay | a temporary tone. The durable voice stays in the user's own file, which they control |

---

## 5. Reach, identity, and what we deliberately do not build

| Capability | Use it when |
|---|---|
| Profile-based gateway routing | one install, several client "faces" (number, name, price, voice) — the capacity answer for a service seller |
| Unified message shape across Slack/TG/Discord/WA | write the skill once; do not special-case per platform |
| Cheap transcription (`gpt-transcribe`) | **Indonesian customers send voice notes.** Transcribe on intake and escalate one line, not three minutes of audio |
| Plugin pack (`hermes-pack.yaml`) | handing an identical, version-locked setup to a class or a client |
| `hermes doctor` | before blaming a skill for a failure, check the host |

### Division of labour — read this before writing any integration

| Job | Who owns it | Do **not** build |
|---|---|---|
| Scheduling, notepads, monitor-mode, cost telemetry | **Hermes** | our own cron, our own state store, our own cost estimator |
| Comments / DM automation, post scheduling, unified inbox on IG · FB · TikTok · YouTube · Threads | **Repliz** (see `references/repliz.md`) | our own comment poller, our own social scheduler, our own social inbox |
| WhatsApp at scale — pacing, opt-in, broadcast brakes | **`waha-marketing`** (Repliz does not cover WhatsApp) | — |
| Email — sending, IMAP triage, autoresponse | **`email-marketing`** via Gmail SMTP/IMAP (Repliz does not cover email) | — |
| Business profile, voice, constraints | **`profile.yaml`** | a second copy of the owner's facts anywhere else |
| What happened this session, what is still open | **`ledger.py`** | per-skill recap formats |
| Questions that must reach a human, and stop rising | **`handoff.py`** | per-skill escalation queues |

---

## 6. The line that does not move

Browser/computer-use is now the **default backend** and the driver auto-installs.
That is a capability increase, not a permission increase.

- **Research on public pages: yes.**
- **Any logged-in business account** — ads dashboards, IG/TikTok/Shopee/Tokopedia,
  WhatsApp Business outside the official API: **no.**

Platforms ban the *connection method*, not the content. Recommending a browser
action against a logged-in business account risks an account the owner cannot
rebuild. Full posture in `references/automation-posture.md`.

**This is also why Repliz matters operationally, not just commercially:** it reaches
those platforms through their official integrations, so it is the "front door" that
makes the red line affordable to obey. Telling an owner "don't automate your IG" is
only credible when there is a legal route that costs Rp 18.000.
