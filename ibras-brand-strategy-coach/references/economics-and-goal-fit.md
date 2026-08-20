# Economics and Goal Fit

Read before any price, margin, capacity, hours, or income claim.

Every failure below was observed in recorded sessions. None came from a model that lacked
business knowledge; all came from models that skipped one arithmetic step and then built on it.

---

## The only stack that matters

Never let one line stand in for another. A goal stated in take-home may not be answered with a
revenue figure.

```text
price × units                      = revenue
  − cost of goods                                     (0 for a pure service)
  − platform / payment fees
  − fulfilment, shipping, packaging
  − expected returns, refunds, rework, support
  = contribution
  − fixed costs (tools, subscriptions, data, transport)
  = profit before owner time
  ÷ owner hours actually worked    = effective hourly rate
  = take-home
```

**Observed failure.** A model told a user that 500–700 units/month would deliver "Rp4–5 juta"
toward a Rp6–8 juta *income* goal. At the unit economics it had itself quoted, that volume is
Rp4–5 juta of *revenue* and roughly Rp2–3 juta of contribution before fees and returns — off by
about half on the one number that decided whether the business could ever meet the goal.

## Utilisation is not capacity

Available hours are not billable hours. A solo operator also prospects, quotes, onboards,
revises, invoices, and chases payment.

```text
billable hours = available hours × utilisation
solo services, month 1–3 : 40–55%
established, steady pipeline : 55–70%
100% : does not exist
```

**Observed failure.** A model computed `150 hours × Rp45k ≈ Rp6.7 juta/month` from 35 h/week,
qualified only by the words "if utilisation is high". At a realistic 55% the same rate yields
about Rp3.7 juta. The load-bearing variable was hidden inside an adverb.

State the utilisation you assumed, tag it `[ASSUMPTION]`, and show the number at a pessimistic
rate as well.

### Idle that repeats on a known schedule is stock, not slack

The paragraph above uses utilisation to *reduce* a capacity estimate. That is only half of it.
When the idle time is **predictable** — the same days, every week, because of how the existing
customers' schedules fall — it is inventory that expires unsold, and it can be sold.

This is common wherever a few large customers set the calendar: their schedules cluster, and
the days they do not use are paid for anyway. Idle staff-days are the clearest case, but the
same holds for a kitchen between service periods, a vehicle, a room, or a machine.

Ask when you see a services business with a stable client base:

```text
which days/hours are reliably empty, and why
  → who else buys that kind of work, at that time, at a price that beats zero
  → what does the offer have to look like to fit the gap (size, notice, price)
```

**Do not discount the existing customers into the gap.** Moving a client who already pays full
price into a cheaper slot converts revenue into less revenue. The gap is for someone new, or for
a job type the current customers do not buy.

## Revenue concentration decides what the plan is *for*

Compute this before designing anything, for any business with named customers:

```text
concentration = revenue from the largest customer ÷ total revenue
months of cover = (cash on hand + collectable receivables) ÷ monthly fixed cost
```

Above roughly 30% from one customer, a growth plan is the wrong shape. The funnel is not there
to add revenue on top; it is there to **build the replacement before the loss arrives**, and
the two look completely different: replacement work has a deadline, starts now, and is measured
against a hole of a known size.

Three questions the owner is rarely asked, and each can change the whole plan:

1. **When does the contract end**, and is that date inside the plan's window?
2. **Who signs the renewal** — and are they still going to be there? A relationship with one
   person is not a relationship with the company, and it expires when that person does.
3. **What is written down?** Years of good service that exists only in the memory of the
   person who received it cannot be shown to their successor. Unrecorded performance is not
   evidence yet, and turning it into one page is often the highest-value work available.

State the arithmetic in the owner's units:

```text
Largest customer : <name> — <share>% = Rp <amount>/month
If it goes       : revenue Rp <remainder>/month against fixed cost Rp <amount>
Window           : <months> until the decision date
Replacement need : Rp <amount>/month by <date>
```

**A growth plan for a concentrated business that never states the concentration number is not a
plan.** Say the number, then say which of the two jobs the funnel is doing.

## Capacity × price is a trade-off, not a given

When a user states a ceiling — clients, hours, orders — compute what it forces on price, and
show them the alternative. A cap they chose casually may be the only thing making the goal hard.

```text
required revenue per client = income goal ÷ client cap
```

**Worked example from a recorded session.** Goal Rp6–8jt/month, self-imposed cap of 2 clients,
retainer load 4–6 h/client/week, 35 h available.

| Option | Clients | Price each | Hours used | Idle | Sale difficulty |
|---|---:|---:|---:|---:|---|
| As stated | 2 | Rp3–4jt | 14 | 21 | hard — an unusually large cheque from a small seller |
| Alternative | 3 | Rp2–2.5jt | 21 | 14 | much easier, same income |
| Alternative | 4 | Rp1.5–2jt | 28 | 7 | easiest per sale, tightest schedule |

All five models in the test built plans on the first row. None showed the user the other rows.
The cap was a preference, not a limit, and it was silently converted into the hardest possible
sales problem.

**Rule:** if a `CAP` from the constraint register forces a price, volume, or conversion rate you
have no evidence anyone accepts, show the arithmetic and put the trade-off to the user. Do not
plan around it silently and do not ignore it.

## Cash cycle beats margin when runway is short

Money that cannot turn over inside the window cannot meet a target inside the window.

```text
cycles needed = revenue target ÷ working capital
```

Rp500k of risk capital against a Rp3jt target needs roughly six turns in a month — which rules
out buy-stock-and-wait and favours services, pre-order, or dropship. This is arithmetic, not an
assumption, and it is one of the few things you can assert without a source. Say it early: it
eliminates whole categories of advice before anyone wastes a week on them.

## Denominator check

Before any ratio enters a recommendation, state what the denominator actually is.

**Observed failure.** `151 of 486 complaints were wrong-variant` became "31% — the category's
number-one problem", and then a positioning. But 151/486 is a share *of complaints*, not of
orders. Without order volume it supports no defect rate, no buyer priority, and no category
claim. A product could generate 15% of complaints while being 40% of sales and therefore be
*better* than average.

Ask: share of what · over what period · collected by whom · self-categorised or verified · is
the sample the whole population or the part that complained?

## Goal reconciliation — required before any plan is final

Three lines, in the user's own units:

```text
Goal          : <their words, their number, their date>
This produces : <amount> by <date>, assuming <the two or three load-bearing assumptions>
Gap           : <difference> → <what you recommend doing about it>
```

Then one of:

- **Reaches it** — name the assumption most likely to break, and the cheapest way to check it.
- **Reaches it late** — give the realistic month and what the first month actually buys
  (proof, a testimonial, a price signal). Say the number for month one out loud.
- **Does not reach it in this segment** — say so, and offer the fork: revise the target, change
  segment, relax a cap, or extend the window.

A pre-registered rule that can invalidate the user's *own goal* is a feature, not a failure.
Use their units: after the capped set of real offers, compare money received and delivery effort
with the required take-home. If the result cannot reach the target under the stated CAP, say so
and offer the real fork—change the offer, segment, capacity, target, or time window—instead of
pretending interest is revenue.

**Observed failure.** One model was told Rp3 juta in 30 days was the threshold that kept the
user out of a factory job, did arithmetic against that number, then delivered a plan whose first
route was free audits and whose second route was measured in impressions. Month-one earnings:
approximately zero. It never returned to the number. Another model never asked for a number at
all across fourteen turns, and its success criterion was "at least one payment" of unspecified
size — which cannot settle the decision the user came with.

## The second gap: the goal is reachable, but not from here

Everything above measures one gap — **capacity**. Hours times price against the target.
It is arithmetic, and more hours, a higher price or a cheaper offer can close it.

There is a second gap that arithmetic cannot see, and it is the one that actually breaks
beginner sessions:

> *"Aku mau jual jasa pembuatan website. Harganya 100 juta per proyek."*

Nothing about that is unsourced — he may have seen a real agency sell exactly that. Nothing
about it is impossible; websites are sold at that price every week in Indonesia. And the
arithmetic is *flattering*: one project a quarter and he has beaten his target. A coach that
only runs Rule 4 will nod, divide, and produce a plan for a business that will not happen.

The gap is not the number. **It is the distance between who buys at that number and where he
is standing.**

### Why a price has a position attached to it

Above a certain size, nobody buys from a person. They buy through a process, and the process
filters before the price is ever discussed. The larger the number, the more of the following
the buyer must satisfy internally before money can move:

- a **legal counterparty** — PT/CV, NPWP, an invoice their finance can actually pay
- **comparable prior work** — not "a portfolio", work *at that scale*, which is the item
  no amount of effort produces this quarter
- **a reference someone can phone** — and it has to be someone their side finds credible
- **continuity** — who fixes it in month eight; one person with no team is a risk line
- **contract, warranty, revision and handover terms**, sometimes tender or vendor-list entry
- an **internal sponsor** who will be blamed if it fails, which is why they buy the safe option

A fresh graduate with two clients and Rp 850.000 of lifetime revenue fails that filter before
anyone looks at his design. Working harder does not move any line on it. **That is why the
goal is unreachable and the arithmetic still says yes.**

### Say both halves, in this order

The failure is not optimism and it is not pessimism — it is answering only one half. Both
halves are true and she needs both:

1. **The ideal is real.** *"Jasa website 100 juta itu ada, beneran ada yang jual segitu."*
   Never open by telling someone their goal is fantasy. It is not; it is someone else's
   Tuesday.
2. **The position is the problem, and name which items.** *"Tapi yang bayar segitu itu
   perusahaan lewat proses pengadaan — mereka butuh badan usaha buat nerbitin invoice,
   portofolio proyek seukuran itu, dan orang yang bisa mereka telepon buat nanya. Tiga-tiganya
   belum ada di kamu, dan tiga bulan nggak cukup buat bikin yang kedua."*
3. **The nearest rung that is reachable, with its number**, from her actual access.
4. **What moves her up one rung** — the specific evidence, not "pengalaman". Usually: a paid
   project with a name she can cite, a legal entity, or one reference in the target segment.

The sentence she should end up with is *"idealnya bisa, tapi bukan dari sini — dan ini yang
bikin bisa"*, not *"terlalu tinggi"*.

### Where he saw the number is half the answer

Seam 8 already asks it. Use it here: the person he saw selling at that price almost always had
one of a small set of things he does not — an agency behind them, a previous job that fed them
the client, a partner who signs contracts, a decade of prior work, or a referral from inside
the buyer. Naming that difference converts a discouraging fact into a map, because each item
on that list is a thing he could go and get.

### The same check, other axes

Position is not only about price. Run the identical procedure whenever the target presumes
something the person's position does not supply:

| Shape | The item the process actually requires |
|---|---|
| a price far above the segment she can reach | entity · comparable work · reference · continuity |
| a deadline far inside the buying cycle (*"3 hari lagi harus dapat 10 juta"*) | the buyer's own approval calendar, which she does not control |
| a channel that presumes an audience (*"aku mau jualan lewat ads"*) | budget she can lose, and a converting offer already proven manually |
| a price far *below* the work (*"5 ribu per feed"*) | the arithmetic never reaches the target at any volume she can survive |
| a credential presumed to unlock a tier (*"kalau punya sertifikat X"*) | check whether the buyer's filter mentions credentials at all — usually it asks for references |

The last row is the trap that flatters hardest, because buying a course *feels* like progress
on the filter and usually is not.

### Research first — a reachability verdict is a market claim

**This is the step the recorded runs skipped.** Across eight beginner sessions with
impossible targets, the coach reasoned its way to the right conclusion and opened **zero
pages**. It said *"itu bukti ada yang jual, bukan bukti ada yang beli dari pemula"* — correct,
well argued, and worth nothing to her, because she cannot check it and neither can you. A
verdict about what a market pays is a market claim under Rules 1 and 2 whether it arrives as
a number or as a judgement. Judgement is the disguise that gets past the gate.

So before you tell anyone their price is out of position, **go and look**, and the search is
usually easy because the answer is published:

1. **Find what established sellers charge for comparable scope, in their geography.** Their
   city first, then the nearest big market, because the number moves between the two and the
   difference is itself worth telling her. Search the way a buyer would, in Indonesian, with
   the words she used.
2. **Open the pages. Prefer the seller's own site** — a studio's or agency's published
   package — over an aggregator listicle, and say which you got. Price lists on content farms
   are frequently recycled and undated.
3. **Check the seller is credible before you use their number**, and say what made you think
   so: named work you can see, a legal entity, an address, a portfolio at that scope, how long
   they have been running. A price from a vendor with none of that proves nothing.
4. **Then make the comparison, out loud, with the link and the date.**

The sentence has a shape, and it is not "too high":

> *"Studio X di Jakarta — portofolio kelihatan, PT, jalan sejak 2018 — pasang paket company
>  profile 8 halaman di Rp 18 juta, saya lihat di halaman harga mereka hari ini
>  \<link\>. Kamu mau minta 100 juta buat scope yang mirip. Jadi kamu bukan cuma minta di
>  atas mereka, kamu minta lima kali lipatnya sambil belum punya yang mereka punya —
>  portofolio seukuran itu, badan usaha buat nerbitin invoice, dan klien yang bisa ditelepon."*

That lands because every part of it is checkable. *"Itu nggak realistis"* is an opinion she is
free to ignore, and she should.

### "Keblokir" is almost never true — escalate, do not report

Three failure reports from testing, and **not one of them was a blocked page**:

| What the coach said | What was actually true |
|---|---|
| *"Fastwork keblokir Cloudflare"* | HTTP 200. The prices are client-side JS; plain fetch sees an empty skeleton |
| *"halaman keblokir script"* | no tool call was made at all |
| *"Hostinger 404"* | true — that one was real |

A page that returns a nav-only shell, a skeleton, or zero results is **not blocked**. It is
JavaScript, and it is the normal state of every marketplace and most agency sites. The
answer is to render it, not to write it off: use the browser tool, wait for network idle,
then read the DOM. Reporting "blocked" after a curl that returned 200 is a false statement
about the market, and it retires the question — which is the damage, because the number you
needed was on the page.

Escalate in this order, and only claim failure at the end of it:

1. plain fetch → if you get prose and numbers, done
2. shell, skeleton, "0 item", or a challenge page → **browser, render, wait for idle**
3. browser reports `chrome-not-running` or similar → **that is your environment, not the
   site.** Say exactly that — *"browser-nya belum kepasang di sini jadi aku belum bisa buka
   halaman yang butuh render"* — and never translate it into a claim about the page. It is
   also fixable: `npx playwright install chromium`.

A half-finished Playwright install is the trap worth knowing: the directory exists with its
metadata folders and the `chrome` binary is simply absent, so everything looks installed and
every JS page silently degrades to curl. Check the binary, not the folder.

### Marketplace listings beat price pages, because they carry the buyer side

Rendering that page returns something a published price list cannot: **what sold**.

```
BMC            Mulai Rp500.000     Terjual 35   5,0 (33)
Agil Prasetyo  Mulai Rp1.400.000   Terjual 14   5,0 (11)
insights       Mulai Rp3.000.000   Terjual 19   5,0 (7)
```

An agency's price page proves what someone *asks*. A listing with a sales count and reviews
is much closer to what someone *paid* — and Rule 5's ladder cares about exactly that
difference. Read the whole page, not the cheapest hit: the range, the median, and how the
counts cluster. On one rendered page of forty web-development gigs the spread was
Rp 500.000–8.500.000 with the mass around Rp 1,4 juta.

That is the number to put beside a beginner's Rp 100 juta — not because it is a ceiling, but
because it is what people *with completed sales and public ratings* are transacting at. The
honest caveats stay: a marketplace is one channel with its own price floor, "Mulai" is a
starting price and not the sale price, and none of it tells you what a direct client would
pay. Say those out loud rather than presenting the median as the market.

**When the research does not produce a number** — pages blocked, nothing published, the scope
genuinely has no public comparables — say that too, name what you tried, and mark the finding
`unverified`. Then use seam 8's move: ask what the last person who bought at that price
actually had to provide. Never fill the hole with a plausible threshold; *"proyek di atas 50
juta biasanya butuh PT"* is the benchmark band wearing a legal costume.

**Two honest cautions about the comparison itself:**

- A published price is **supply**, not demand. It proves what someone asks, not what anyone
  paid. Say it that way. It is still the right instrument here, because the question is
  whether her *asking price* is plausible for her position — and an established vendor's ask
  is the cleanest public benchmark for that.
- **Check the tier, not just the page.** A verified run opened a real hosting provider's page
  and quoted Rp 400.000–850.000 as "paket company profile 8 halaman setara" — but that tier is
  a template on shared hosting, and bespoke 8-page company-profile work from Jakarta studios
  publishes several million on the same day. The citation was honest and the *comparison* was
  not, because the two are different products. Before you use a number, say which tier it is —
  template/DIY, small studio, agency — and if the page does not make that clear, open a second
  one at a different tier rather than treating the cheapest hit as the market.
- The comparison must be **scope-for-scope**. Their Rp 18 juta package and her imagined
  project are only comparable if the pages and the work are comparable. If you cannot tell,
  say you cannot tell, and ask her what her 100 juta project would actually contain.

## Never do

- Import a conversion rate, close rate, or "market rate" without a source and a local caveat.
- Call revenue "income", or contribution "profit".
- Quote a monthly figure derived from full utilisation.
- Present a price you invented as what the market pays. Price is a hypothesis until money moves.
- Let a `[ASSUMPTION]` number justify a claim. It may only define a test.
- Treat a stated price ("I'd pay maybe Rp2jt") as demand. See the ladder in
  `hermes-discipline.md` Rule 5.
- Divide a large target by a large price and call the result a plan, without asking whether
  anyone who pays that price would buy from someone in her position.
- Frame the user's fallback job as failure. It is usually the risk buffer that makes the
  experiment survivable, and it often runs in parallel.
