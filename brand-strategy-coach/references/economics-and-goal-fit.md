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

A pre-registered rule that can invalidate the user's *own goal* is a feature, not a failure:

> "After three paid audits, ask openly what weekly upkeep is worth. If the median answer is
> under Rp1jt, the Rp3–4jt retainer is not valid and Rp6–8jt is not reachable in this segment —
> I will say the target needs revising rather than pretend it is selling."

**Observed failure.** One model was told Rp3 juta in 30 days was the threshold that kept the
user out of a factory job, did arithmetic against that number, then delivered a plan whose first
route was free audits and whose second route was measured in impressions. Month-one earnings:
approximately zero. It never returned to the number. Another model never asked for a number at
all across fourteen turns, and its success criterion was "at least one payment" of unspecified
size — which cannot settle the decision the user came with.

## Never do

- Import a conversion rate, close rate, or "market rate" without a source and a local caveat.
- Call revenue "income", or contribution "profit".
- Quote a monthly figure derived from full utilisation.
- Present a price you invented as what the market pays. Price is a hypothesis until money moves.
- Let a `[ASSUMPTION]` number justify a claim. It may only define a test.
- Treat a stated price ("I'd pay maybe Rp2jt") as demand. See the ladder in
  `hermes-discipline.md` Rule 5.
- Frame the user's fallback job as failure. It is usually the risk buffer that makes the
  experiment survivable, and it often runs in parallel.
