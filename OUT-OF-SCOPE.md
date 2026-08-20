# OUT-OF-SCOPE.md — asked for, deliberately not built

Rejections with their reasons, so the next person relitigates with context instead
of from zero. A entry here is not "never" — it is "not without this changing".

## A browser that logs into her business accounts and clicks
**Refused outright.** Not a risk trade-off: it is credential handling plus a
platform-terms breach in someone else's name. The nearest thing we do build is
`ibras-cloakserve-research`, which reads *public* pages only.

## Diagnostic health quizzes ("cek risiko diabetes kamu")
Regulated-claim territory. The disclaimer that would make it lawful also makes it
useless as a funnel, and the version that converts is the version that harms.

## A comment poller, a post scheduler, a unified social inbox
Repliz does all three, from Rp 18.000 one-time, and its webhook is push not poll.
Building ours would be worse and permanent. Recorded so nobody rebuilds it.

## Hard caps on how many questions the coach may ask
Requested after a long session. Rejected: a cap conflates "this person needs more
excavation" with "the prompt was vague". The fix for a long session is a better
gate, not a counter.

## Normalising the seven drifted Market-fit gate blocks into one
Wanted, and correct in principle. Held because it is a mass edit across every
skill with no proof-of-concept, and mass edits on skills that *act* are runtime
changes — see `DECISIONS.md` D4 and the PATHLEAK splice of 2026-08-20.
`shared/check-sections.sh` reports the drift meanwhile.

## Moving the coach's stage bodies behind pointers
Tried, measured, rejected. Violations roughly doubled on glm-4.7 and rose ~6× on
muse-spark-1.2; the moved files were opened in 0 of 24 sessions on glm. The
refuted variant is kept at `evals/adopt-poc/arms/B-disclosed` so it is not
rebuilt from scratch. `DECISIONS.md` D3.
