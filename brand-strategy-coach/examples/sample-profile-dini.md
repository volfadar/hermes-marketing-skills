# Sample Profile — Dini (synthetic, in progress)

This example shows the shape of a version-2 profile. It is deliberately marked
in progress: a polished slogan and a large funnel would be false precision until
the research and willingness-to-pay experiments are complete.

## Profile JSON

```json
{
  "schema_version": 2,
  "user": "dini",
  "current_stage": 4,
  "talent": {
    "tests": {
      "big_five": {"status": "not_provided"},
      "onet": {"status": "not_provided"}
    },
    "hypotheses": [
      "May sustain educational work when it includes hands-on demonstrations"
    ],
    "behavioral_evidence": [
      "Has published 18 informal coffee reviews and continued without a posting schedule"
    ],
    "accommodations": ["Prefer one weekly filming block over daily production"]
  },
  "background": {
    "dossier": {
      "career_sequence": ["Specialty-coffee barista, three years"],
      "work_examples": ["Customer brew consultations", "18 Instagram reviews"],
      "customer_familiarity": ["Beginner home brewers in Yogyakarta"]
    },
    "proof_ledger": [
      {
        "claim": "Can diagnose beginner brewing mistakes",
        "proof": "Repeated customer consultations; no outcome log yet"
      }
    ],
    "access": ["Former customers who consented to follow-up", "Two local roasters"],
    "constraints": {"cash_idr": 750000, "hours_per_week": 6},
    "unknowns": ["Paid demand", "Gross margin after fulfilment", "Repeat frequency"]
  },
  "positioning": {
    "research": {
      "as_of": "example only — replace with live date and direct citations",
      "status": "incomplete",
      "gaps": ["Competitor price map", "Customer-language interviews", "Shipping economics"]
    },
    "territories": [
      {"lever": "risk", "idea": "Beginner brew rescue with a measurable retry"},
      {"lever": "occasion", "idea": "Coffee setup for small boarding-house kitchens"},
      {"lever": "format", "idea": "Taste-before-gear remote diagnostic"}
    ],
    "chosen": null,
    "evidence": [],
    "implications": [],
    "falsification": "Do not choose a territory until five problem interviews and one paid test"
  },
  "tools": {
    "experiment": {
      "assumption": "Beginners will pay for diagnosis before buying more equipment",
      "time_box_days": 7,
      "budget_cap_idr": 150000,
      "sample": "Five consented former customers",
      "offer": "Three paid diagnostic slots at Rp50000",
      "scale_rule": "At least two paid slots and one completed retry",
      "stop_rule": "No paid slot after five direct invitations"
    },
    "jobs": ["One invitation message", "Payment record", "Before/after brew log"],
    "selected": ["Manual outreach", "Spreadsheet"],
    "deferred": ["Content automation", "Broadcast tooling", "Paid ads"],
    "measures": ["Invited", "Replied", "Paid", "Completed retry"]
  },
  "funnel": {
    "status": "not_designed",
    "reason": "Price, contribution margin, capacity, repeat behavior, and winning entry route are not yet known"
  }
}
```

## Why this is a valid incomplete result

- Test scores are optional; observed behavior is recorded as evidence.
- A title is not treated as proof. The outcome log is explicitly missing.
- Three positioning territories use different levers, but none is declared the
  winner before research.
- The first test fits the stated cash and time constraints.
- Tools are selected for the immediate experiment; automation is deferred.
- A funnel is not invented while price, margin, retention, and acquisition
  evidence are unknown.

## Next conversation turn

Ask one question: “Dari lima mantan pelanggan yang masih boleh kamu hubungi,
berapa orang yang pernah membeli alat baru karena seduhannya terasa gagal?”
The answer will refine the interview sample and test whether “brew rescue” is a
real buying problem or only an attractive story.
