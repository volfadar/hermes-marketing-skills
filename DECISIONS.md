# DECISIONS.md — what we adopted from mattpocock/skills, and what the evidence said

Every entry: the constraint, the choice, the evidence, and the invariant it creates.
Adopted only what a proof-of-concept verified. Rejected only what a PoC refuted.
Anything still unmeasured is listed as pending, not silently skipped.

**The PoC.** `evals/adopt-poc/` — four skill variants of the same coach, byte-identical
persona scripts, isolated `HERMES_HOME` per cell, scored with the repo's own unmodified
detectors (`check_discipline.py`, `check_excavation.py`). 96 sessions on glm-4.7 plus a
36-session replication on muse-spark-1.2. Rate-limited cells are excluded as invalid,
not scored as clean.

| arm | what it changes | n | seams/session | violations/session | primitive loaded |
|---|---|---|---|---|---|
| A control | the 841-line monolith | 24 | 1.50 | 1.12 | — |
| B disclosed | stage bodies moved to `stages/*.md` | 24 | **0.83** | **2.21** | — |
| C disclosed + primitive | B, plus discipline as its own skill | 24 | 1.46 | **1.17** | **92%** |
| E primitive only | A, plus discipline as its own skill | 24 | 1.42 | 1.67 | 79% |

---

## D1 — ADOPT: a shared primitive is a SKILL, not a reference file

**Constraint.** Reference files are progressive-disclosure data. Hermes never auto-loads
them; it appends a flat listing of every file in `references/templates/scripts/assets`
and leaves the decision to the model.

**Evidence.** The same nine rules, as a reference file, were opened rarely. As a separate
skill invoked with `skill_view(name="ibras-discipline")` they loaded in **92% of sessions
(C) and 79% (E)** — measured from the tool ledger, 48 sessions. Inside the disclosed arm
the primitive cut violations from 2.21 to 1.17 per session (paired n=24: 12 better, 7
worse) and raised seams 0.83 → 1.46.

**Choice.** `skill-ibras-discipline/` is now a real skill; the coach calls it. The
reference file stays in place as a fallback for skills not yet migrated.

**This reverses an earlier reasoning-only verdict.** `mattpocock-adoption-verdict-2026-08-20.md`
argued a primitive-as-skill costs the same as a reference file and should therefore be
inverted. That was wrong, and the PoC is what showed it: the two do *not* cost the same,
because they do not load at the same rate.

**Invariant.** A rule that must fire every session belongs in a skill, not behind a pointer.

---

## D2 — ADOPT: slim, orthogonal skill descriptions

**Evidence.** The coach's description was 838 bytes — 28% of the whole always-loaded
budget. Arm D cut it to 213. Across 24 natural-trigger sessions, firing went **4/12 → 5/12**
and bracket-slop **3 → 2**. No harm detected, 75% of that skill's context load returned.

**Choice.** The coach ships the slimmed description. The other seven are untested and
were left alone.

**Invariant.** Description length is not a proxy for reach. Changing one is a measurable
act; measure it.

---

## D3 — REJECT (for now): moving stage bodies behind pointers

This is the study's Move 3. It is the one change with evidence *against* it.

| | glm-4.7 | muse-spark-1.2 |
|---|---|---|
| violations/session, control | 1.12 | 0.75 |
| violations/session, disclosed | **2.21** | **4.75** |
| paired Δ (n=24 / n=12) | **+1.08** (3 better, 12 worse) | **+4.00** (2 better, 7 worse) |
| seams/session | 1.50 → 0.83 | 1.42 → 1.00 |
| stage files ever opened | **0 of 24 sessions** | 6 opens |

Harm replicated on two different models and got *worse* on the second. On glm the moved
files were never opened once. On muse they were opened and the arm still degraded.

**Choice.** The coach stays a monolith. `evals/adopt-poc/arms/B-disclosed` is kept as the
refuted variant so the next person does not rebuild it from scratch.

**What this does NOT say.** It indicts *this implementation* — stage bodies behind a gate
table. A different mechanism (fewer files, self-routing filenames, an imperative gate)
may work. D1 is the clue: the same content loaded reliably once it became a skill.

**Invariant.** Do not move a load-bearing rule behind a pointer without a PoC.

---

## D4 — ADOPT: detect shared-section drift, do not rewrite it

**Evidence.** The Market-fit gate sits in 7 of 8 skills: 386 lines, **7 distinct hashes**.
`sync.sh` guards whole files and cannot see it. Every test passed throughout.

**Choice.** `shared/check-sections.sh` reports the drift. It deliberately does **not**
normalise the text: merging seven drifted blocks is a mass edit across every skill, and a
mass edit on skills that act is a runtime change. There is no PoC for the merged text yet,
so we bought the safe half — visibility.

**Invariant.** Cosmetic-looking mass edits ship with a verification pass or they do not ship.
Precedent: the PATHLEAK find/replace that spliced English mid-sentence into three Bahasa
paragraphs on 2026-08-20 while every test stayed green.

---

## D5 — KEEP: model-invoked routing, stateful skills

Not adopted from Matt, and deliberately: his users type slash commands and hold an index in
their heads. Ours are owners chatting in Bahasa who must be *caught*, not asked to remember.
His skills are stateless; the state bus is our whole value.

---

## D6 — ADOPT: treat discoverability as a build failure

**Found while verifying D1.** `hermes skills list` reported **8 local** for nine installed
skills. `skill-ibras-waha-marketing` carried:

```yaml
description: WhatsApp: balas chat, kontak, label, grup, broadcast.
```

The unquoted colon makes the YAML invalid. Hermes does not error — it **silently skips the
skill during discovery**. The WhatsApp skill could not fire at all, and every test in the
repo passed the entire time, because no test parsed the frontmatter.

This is the same failure class mattpocock/skills hit on 2026-08-19, when a repo-wide
cosmetic sweep left unquoted colons in six skills' frontmatter and unshipped all six.

**Choice.** Value quoted (not reworded — the trigger words are load-bearing), and
`shared/tests/test_frontmatter.py` now asserts, for every skill: frontmatter parses,
`name` exists, `name` equals the folder, description is non-empty.

**Invariant.** A skill that cannot be discovered is not installed. Discoverability is
tested, never assumed.

---

## Pending — measured but not yet acted on

- **The skill fires on only ~⅓ of bare openers** (4/12 control, 5/12 slimmed). This dwarfs
  every structural question in this file and has no fix yet.
- **Move 2 on its own is a wash** (E vs A, paired n=24: seams −0.09, violations +0.45).
  The primitive's proven benefit is *loading reliability*, not answer quality by itself.
- **Detector-gated pruning** — the rule is written (a line is a no-op only if deleting it
  moves no detector count across the corpus); the pass has not been run.
- The remaining seven descriptions, and failure-mode anchoring order. Untested.
