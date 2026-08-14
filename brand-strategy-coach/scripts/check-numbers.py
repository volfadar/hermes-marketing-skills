#!/usr/bin/env python3
"""check-numbers.py — every decision-relevant number must declare where it came from.

Why this exists
---------------
In recorded coaching sessions, four of five models published invented
figures inside arguments: a Rp1–2jt monthly loss, a Rp2.5–3.5jt fee, a "300+ orders/month"
qualification threshold, a 40% required margin, wholesale/retail price bands from four
search pages, and 150 billable hours a month at implied full utilisation. Each was
plausible. None had a source. Each shaped a recommendation given to a user with one
month of runway.

The rule (references/hermes-discipline.md, Rule 2): a figure that can influence a
decision carries a tag the first time it appears.

    [SOURCE: <url or document>]   from a page you opened, or the user's own file
    [USER]                        the user said it
    [CALC: 2 x 300000]            arithmetic over tagged inputs
    [ASSUMPTION]                  you chose it — may define a test, never justify a claim

Usage
-----
  check-numbers.py PLAN.md                       # audit a deliverable
  check-numbers.py PLAN.md --profile p.json      # also check retracted claims
  check-numbers.py --stdin < draft.md
  check-numbers.py PLAN.md --strict              # exit 1 on any violation

Exit codes: 0 clean, 1 violations under --strict, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# The coaching session runs in Indonesian, so the agent writes the tags in Indonesian.
# one recorded run: a model tagged 5 figures [ASUMSI] and this checker reported all five
# as untagged. A validator that only speaks English manufactures violations in the
# language the skill actually operates in.
TAG_RE = re.compile(
    r"\[(SOURCE\s*:[^\]]+|SUMBER\s*:[^\]]+"
    r"|USER|PENGGUNA|DARI\s+USER"
    r"|CALC\s*:[^\]]+|HITUNG\s*:[^\]]+"
    r"|ASSUMPTION|ASUMSI)\]",
    re.I,
)
ASSUMPTION_TAGS = ("ASSUMPTION", "ASUMSI")

# Figures that can move a decision: money, percentages, and counted units.
MONEY_RE = re.compile(r"(?:Rp|IDR|USD|\$)\s?[\d][\d.,]*\s?(?:rb|ribu|jt|juta|k|m|M)?", re.I)
PERCENT_RE = re.compile(r"\d[\d.,]*\s?%")
UNIT_RE = re.compile(
    r"\b\d[\d.,]*\s?(?:jam|hari|minggu|bulan|tahun|pcs|sku|klien|client|orang|pesan|"
    r"listing|order|kali|x|×|/jam|/hari|/bulan)\b",
    re.I,
)

# Things that look numeric but carry no claim.
SKIP_LINE_RE = re.compile(
    r"^\s*(?:#{1,6}\s|\|[\s:-]+\||```|>?\s*\[?\d+\]?[.)]\s*$|<!--)"
)
DATE_RE = re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|Mei|May|Jun|Jul|Agu|Aug|Sep|Okt|Oct|Nov|Des|Dec)\w*\s+\d{4}\b")
VERSION_RE = re.compile(r"\bv?\d+\.\d+(?:\.\d+)?\b")


def scrub(line: str) -> str:
    """Remove spans where a bare number is not a claim."""
    line = re.sub(r"`[^`]*`", " ", line)          # inline code
    line = re.sub(r"https?://\S+", " ", line)      # urls
    line = re.sub(r"\[[^\]]*\]\([^)]*\)", " ", line)  # markdown links
    line = DATE_RE.sub(" ", line)
    line = VERSION_RE.sub(" ", line)
    return line


def figures(line: str) -> list[str]:
    found: list[str] = []
    for rx in (MONEY_RE, PERCENT_RE, UNIT_RE):
        found += [m.group(0).strip() for m in rx.finditer(line)]
    # de-duplicate, keep order
    seen, out = set(), []
    for f in found:
        k = f.lower().replace(" ", "")
        if k not in seen:
            seen.add(k)
            out.append(f)
    return out


def audit(text: str, retracted: list[str] | None = None) -> dict:
    untagged: list[dict] = []
    assumption_in_reason: list[dict] = []
    leaked: list[dict] = []
    tagged_count = 0
    in_fence = False

    # A reason-giving line asserts *why*, so an [ASSUMPTION] there is load-bearing.
    reason_markers = re.compile(
        r"\b(karena|sebab|jadi|maka|artinya|berarti|sehingga|therefore|because|so that|"
        r"which means|alasan)\b",
        re.I,
    )

    for n, raw in enumerate(text.splitlines(), 1):
        if raw.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or SKIP_LINE_RE.match(raw):
            continue

        line = scrub(raw)
        figs = figures(line)
        tags = TAG_RE.findall(raw)

        if figs and not tags:
            untagged.append({"line": n, "text": raw.strip()[:150], "figures": figs})
        elif tags:
            tagged_count += len(tags)
            if any(t.upper().startswith(ASSUMPTION_TAGS) for t in tags) and reason_markers.search(raw):
                assumption_in_reason.append({"line": n, "text": raw.strip()[:150]})

        for term in retracted or []:
            if term and term.lower() in raw.lower():
                leaked.append({"line": n, "term": term, "text": raw.strip()[:150]})

    return {
        "untagged": untagged,
        "assumption_in_reason": assumption_in_reason,
        "retracted_leaked": leaked,
        "tagged_count": tagged_count,
    }


def report(label: str, r: dict) -> int:
    print(f"\n=== {label} ===")
    print(f"  tagged figures: {r['tagged_count']}")
    violations = 0

    if r["untagged"]:
        violations += len(r["untagged"])
        print(f"\n  UNTAGGED ({len(r['untagged'])}) — add [SOURCE:…] / [USER] / [CALC:…] / [ASSUMPTION]:")
        for item in r["untagged"][:40]:
            print(f"    L{item['line']:>4}  {', '.join(item['figures'])}")
            print(f"           {item['text']}")
        if len(r["untagged"]) > 40:
            print(f"    … and {len(r['untagged']) - 40} more")

    if r["assumption_in_reason"]:
        violations += len(r["assumption_in_reason"])
        print(f"\n  LOAD-BEARING ASSUMPTION ({len(r['assumption_in_reason'])}) — "
              f"an invented number is justifying a claim. Make it a test instead:")
        for item in r["assumption_in_reason"]:
            print(f"    L{item['line']:>4}  {item['text']}")

    if r["retracted_leaked"]:
        violations += len(r["retracted_leaked"])
        print(f"\n  RETRACTED CLAIM STILL IN FILE ({len(r['retracted_leaked'])}) — "
              f"you corrected this in chat but not here:")
        for item in r["retracted_leaked"]:
            print(f"    L{item['line']:>4}  [{item['term']}]  {item['text']}")

    if not violations:
        print("  OK — every decision-relevant figure declares its origin.")
    return violations


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--stdin", action="store_true")
    ap.add_argument("--profile", type=Path, help="profile JSON supplying a 'retracted' list")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    retracted: list[str] = []
    if args.profile and args.profile.exists():
        try:
            retracted = json.loads(args.profile.read_text()).get("retracted", []) or []
        except json.JSONDecodeError:
            print(f"warning: could not parse {args.profile}", file=sys.stderr)

    jobs: list[tuple[str, str]] = []
    if args.stdin:
        jobs.append(("stdin", sys.stdin.read()))
    for p in args.files:
        jobs.append((p.name, p.read_text(encoding="utf-8", errors="replace")))
    if not jobs:
        ap.print_usage(sys.stderr)
        return 2

    total = sum(report(label, audit(text, retracted)) for label, text in jobs)
    print(f"\nTotal violations: {total}")
    return 1 if (args.strict and total) else 0


if __name__ == "__main__":
    sys.exit(main())
