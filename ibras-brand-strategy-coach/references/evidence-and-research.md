# Evidence and Market Research

## Research must precede a final position

Research is useful only when it can change, narrow, or kill an idea. Do not browse merely to decorate a recommendation.

## Build the brief from the dossier

Define:

- geography and language;
- buyer and end user;
- offer/category and substitutes;
- price/margin or business model;
- user's unusual access or proof;
- the decision and risky assumptions.

Turn assumptions into questions. Example: “Do small Shopee sellers pay for response-time operations?” is researchable; “admin services are promising” is not.

## Use available research tools

Prefer the installed `ibras-cloakserve-research` skill for public market research. Read its `SKILL.md` before use and follow its ethics. If unavailable, use another web/browser tool.

Research at least these evidence classes:

1. **Customer language and unresolved jobs** — reviews, forum threads, public questions, complaint patterns, interviews, or support discussions.
2. **Alternatives and conventions** — direct competitors, substitutes, DIY behavior, doing nothing, category claims, prices, guarantees, packaging, and distribution.
3. **Buying context and channel** — where discovery and purchase happen, the occasion, decision-makers, trust transfer, and local behavior.
4. **Economics or constraints** — fees, gross margin, return risk, capacity, regulation, platform policy, or buying cycle.

For a quick positioning pass, use at least four relevant sources across at least three classes. More sources do not compensate for weak relevance.

## Source hierarchy

Use the strongest source appropriate to the claim:

1. official statistics, regulations, platform documentation, company filings, and original research;
2. credible industry associations, datasets, and established research organizations;
3. reputable reporting and specialist publications with named methods/sources;
4. marketplace listings, reviews, forums, and social comments for qualitative language and examples;
5. vendor blogs and generic marketing articles only as leads, not load-bearing proof.

Books and established frameworks can explain a method; they do not prove current Indonesian demand. Name the author, title, edition/year where relevant, and distinguish the framework from market evidence.

## Evidence note format

```markdown
### What the evidence says — as of YYYY-MM-DD

| Observation | Type | Source | Confidence | Decision impact |
|---|---|---|---|---|
| ... | fact / qualitative signal | [direct title](URL) | high/medium/low | keep/change/kill |

Contradictions:
- ...

Still unknown:
- ...
```

Link to the actual page, dataset, listing, report, or document—not a search-results page. Cite near the claim.

**A source is a page you opened.** See `hermes-discipline.md` Rule 1 for the full tier table and
the traps. The short version: a link, title, or snippet appearing *inside* a results page is a
lead, not a source; a Google AI Overview is not a source; a breadcrumb URL (`site.com › path`)
reassembled into a link is a search result wearing a source's clothes. Never describe the
contents of a page you did not fetch.

Record retrieval status for every source — `opened`, `opened_empty` (login wall, JS shell, 404),
`search_result`, `ai_summary` — and report the failures rather than hiding them. Then verify
with `scripts/check-citations.py` instead of trusting recall.

**Minimum for a positioning pass: four successfully opened non-search pages across at least
three evidence classes.** Twelve search queries and zero opened pages is not research. If you
cannot reach four, deliver a research *plan* and say what remains unverified.

## Fact, inference, experiment

Use:

- **Fact:** “The platform charges X according to its current fee page.” Cite it.
- **Inference:** “That fee likely makes this SKU fragile at the user's stated margin.” Show the calculation and assumptions.
- **Experiment:** “List ten SKUs for seven days and measure qualified chats per 100 visits before buying inventory.”

Never convert a handful of comments into a prevalence claim. Say “a recurring complaint in the reviewed sample,” list the sample, and keep the limitation visible.

## Research sequence

1. Search broad category language and official constraints.
2. Inspect direct alternatives and substitutes.
3. Read negative reviews and abandoned-workaround discussions.
4. Check local discovery/purchase context.
5. Test the initial idea against economics and user access.
6. Search specifically for disconfirming evidence.
7. Summarize what changed.

Stop when additional searching no longer changes the decision or when the next uncertainty requires an interview/experiment rather than more pages.

## High-stakes claims

For medical, legal, financial, tax, privacy, safety, or regulatory advice:

- use primary/official sources;
- state scope and jurisdiction;
- avoid diagnosis or definitive compliance claims;
- ask a qualified professional to verify material decisions;
- do not turn symptoms into a marketing quiz without clinical validation.

## Failure modes

- positioning first and citations afterward;
- sources that mention a category but do not support the claim;
- uncited conversion rates or “market rates”;
- fake precision from a small qualitative sample;
- using global data as Indonesian behavior without qualification;
- citing a framework as proof of demand;
- ignoring evidence because the first idea sounds creative;
- recommending a second brand without testing the cost of operating it.
