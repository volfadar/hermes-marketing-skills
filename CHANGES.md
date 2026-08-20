# CHANGES.md

Append-only. Three fields per entry: what changed, why, and which session or eval
exposed it. Reasoning that lives only in a chat log is lost at the next compaction.

---

## 2026-08-20 — adopt what the PoC verified

**Added `ibras-discipline` as the 9th skill.** The nine claim rules were a
reference file; reference files load rarely. As a skill invoked with
`skill_view` they loaded in 92% of sessions and cut violations 2.21 → 1.17 per
session (glm) and 4.75 → 1.10 (muse, 6 better / 0 worse).
*Exposed by:* `evals/adopt-poc`, 154 sessions, arms C and E.
*Reverses* the reasoning-only verdict in `mattpocock-adoption-verdict-2026-08-20.md`.

**Rewrote all nine skill descriptions for trigger orthogonality.** Collisions
33 → 21, always-loaded budget 3037 → 2033 bytes. The coach alone went 838 → 213
after Arm D measured no harm (firing 4/12 → 5/12, slop 3 → 2).
*Exposed by:* the trigger experiment, and a collision audit across all nine.
*Verified after:* 12 natural-trigger sessions with all nine skills installed — fired 9/12, bracket-slop 1/12, and each persona reached the right skill (copy → content-creator, niche → coach + research, harga → coach + discipline, otomasi → social-publishing). Not a strict A/B against the 4/12 baseline, which had only the coach installed; the routing correctness is the part that is directly observable.

**Did NOT move stage bodies behind pointers.** Measured harm on two models;
the refuted variant is kept at `evals/adopt-poc/arms/B-disclosed`.
*Exposed by:* 24 paired sessions per model. See `DECISIONS.md` D3.

**Fixed: `ibras-waha-marketing` was invisible to Hermes.** `description: WhatsApp:`
— an unquoted colon makes the YAML invalid and Hermes silently skips the skill
during discovery. `hermes skills list` said "8 local" for nine installed skills;
the WhatsApp skill could never fire. Every test passed throughout, because
nothing parsed the frontmatter.
*Exposed by:* verifying the new skill was visible. Now `shared/tests/test_frontmatter.py`
plus a preflight check in `ibras-setup`, negative-tested against a broken copy.

**Fixed: the router named 7 of 9 skills.** `ibras-discipline` was new;
`ibras-social-publishing` had shipped unrouted because the orchestrator
recommended Repliz directly. A router that omits a shipped skill misroutes
forever and nothing errors.
*Exposed by:* a completeness check while wiring the new skill.
Now `shared/tests/test_router.py`.

**Fixed: 96 `.pyc` files shipped inside skills.** Hermes lists every file under
`scripts/`, so each stale cache file became a line in the progressive-disclosure
menu the model must ignore — the coach's menu was 60 lines, now 49.
`shared/sync.sh` strips them on every run.

**Fixed: a cross-skill call assumed a sibling skill was installed.**
`bash ../ibras-waha-marketing/scripts/waha.sh` in the email examples now guards
the path and says which skill is missing instead of failing obscurely.

**Added `shared/check-sections.sh`.** The Market-fit gate is 386 lines across 7
skills with 7 distinct hashes; `sync.sh` guards whole files and cannot see it.
Reports the drift; deliberately does not rewrite it.

**Added `CONTEXT.md`, `DECISIONS.md`, `OUT-OF-SCOPE.md`, this file.**

---

## 2026-08-20 — earlier that day

**Fixed a mass find/replace that spliced English into three Bahasa paragraphs.**
The PATHLEAK fix inserted "the profile file, whose path is …" mid-sentence in
content-creator, social-publishing, and waha-marketing. Only the coach's
occurrence read correctly, because that is where the phrase was authored. Every
test passed, because no test reads Bahasa grammar.
*Exposed by:* diffing two copies of the Market-fit gate.

**Fixed `voice-profile.sh` rejecting the material a beginner actually has.**
SKILL.md promised voice notes and customer chats as fallbacks; the script
hard-required a folder of `.txt`/`.md`. It now accepts a folder, any readable
file, or stdin. A `cleanup()` trap ending in `[[ -n "" ]]` was also returning 1
and flipping success to failure.
*Exposed by:* explaining pillars/voice, then reading the script.
