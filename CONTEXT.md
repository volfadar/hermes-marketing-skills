# CONTEXT.md — the shared language

The words the skills use on purpose, what each one means, and what to avoid saying
instead. A term drifts the moment two skills use it differently, so this file is
the tiebreaker. Change a meaning here and in the skills in the same commit.

Bahasa terms are load-bearing, not decoration: `sikap` beats "brand stance"
because it is one word the owner already owns.

---

## `sikap`
Her stance — what she will and will not say, the greeting she actually uses, the
example chats in her own words. Lives at `profile.yaml › sikap`.
**Avoid:** "brand voice", "branding", "tone of voice" — all three invite a
marketer's abstraction instead of her sentences.
**Test:** the swap test. If a competitor could paste the line into their own
feed unchanged, it is not `sikap` yet.
Produced by [[Harvest]]; consumed by every skill that writes copy.

## `fakta`
Numbers and facts she has stated or that came from a page someone opened, with a
date. Never inferred, never rounded into a claim.
**Avoid:** "data", "insight" — both make a guess sound sourced.
**Why it exists:** one eval quoted `Rp 12.150.000` from nothing.

## `batasan`
What she has ruled out, in four kinds: `REFUSE` (will not do), `CAP` (limit),
`ACCESS` (tools/accounts she actually has), `PERMISSION` (what recipients allowed).
**Avoid:** "constraints", "preferences" — a preference can be argued with, a
`REFUSE` cannot.
A route that violates a `REFUSE` is a failure however good its numbers are.

## Harvest
The end-of-session ritual: take one sentence she actually said, put it in `sikap`,
append to the ledger, and leave exactly one name for tomorrow.
**Avoid:** "wrap up", "summary" — a summary is for the agent, a Harvest is for her.

## state bus
`profile.yaml` · `ledger.jsonl` · `escalations.jsonl` · handoff notes. The slots
skills read and write so session two does not start from zero.
**Avoid:** "memory", "context" — both suggest something the model holds, and this
is a set of files with owners.

## seam
One of ten places a beginner's raw material is buried: work, schooling, community,
what people always ask her for, who she admires, what annoys her, what she likes,
family trade, what she has already built, where a number came from.
**Avoid:** "background question" — a seam is opened by pointing at an artefact, not
by asking an abstract question.

## the two gaps
**Capacity gap** — arithmetic; closable by effort. **Position gap** — the buyer's
procurement filter (legal counterparty, comparable prior work, a phoneable
reference, continuity); not closable this quarter.
Naming which gap a target sits behind is the difference between coaching and
discouragement.

## `unverified`
A market claim nobody has checked yet. It is an instruction to go and look, not a
verdict, and not a hedge to leave in the answer.

## primitive
A rule or discipline several skills need. Since 2026-08-20 a primitive that must
fire *every session* ships as its own skill, because a skill loads reliably and a
reference file does not. See `DECISIONS.md` D1.
**Avoid:** "shared reference" for this case — that is the thing that measurably
did not load.

## progressive disclosure
Hermes lists every file under `references/`, `templates/`, `scripts/`, `assets/`
and loads none of them. The list carries names, never conditions.
**Avoid:** treating it as free. Moving a load-bearing rule behind a pointer
measurably degraded behaviour on two models — `DECISIONS.md` D3.

## discoverable
Hermes parses a skill's YAML frontmatter and silently skips the skill if it fails.
Installed ≠ discoverable. Asserted by `shared/tests/test_frontmatter.py`.
