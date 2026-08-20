#!/usr/bin/env python3
"""
handoff.py — the queue that makes "always escalates" mean something.

Both skills already detect what must go to a human: emotion, money promises,
health/finance/legal claims, strangers, and instructions arriving inside
someone else's message. Both write those to `escalations.jsonl`. Neither had
any way to *clear* the list, which meant "escalate" was operationally the same
as "don't answer" — and that is what turned a permitted automation into a
useless one.

The loop this closes:

    naik ke kamu  →  dia jawab sekali  →  jawaban masuk FAQ  →  nggak naik lagi

That last arrow is the point. Without it every week's handoffs are the same
handoffs, and the automation never gets smarter. With it, the questions that
actually repeat drain out of the queue by themselves.

    python3 handoff.py list                       # antrean, satu baris per orang
    python3 handoff.py answer 1 --text "..."      # jawab, simpan ke FAQ
    python3 handoff.py answer 1 --text "..." --no-faq
    python3 handoff.py skip 1                     # nggak perlu dijawab
    python3 handoff.py stats                      # apa yang paling sering naik

Fails open: an unreadable or missing queue prints "kosong" and exits 0.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

def _business_dir() -> str:
    """
    HERMES_BUSINESS_DIR > HERMES_HOME/business > ~/.hermes/business.

    `HERMES_HOME` used to be skipped here, which meant every Hermes home on one
    machine shared a single business directory — one owner's profile, HALT
    switch, ledger and escalation queue reaching every other owner's session.
    See profile.py `_default_dir` for the run that surfaced it.
    """
    explicit = os.environ.get("HERMES_BUSINESS_DIR")
    if explicit:
        return explicit
    home = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
    return os.path.join(home, "business")


BUSINESS_DIR = Path(_business_dir())
QUEUE = Path(os.environ.get("HERMES_ESCALATION_LOG", BUSINESS_DIR / "escalations.jsonl"))
RESOLVED = BUSINESS_DIR / "escalations-resolved.jsonl"
FAQ_FILE = Path(os.environ.get("HERMES_FAQ_FILE", BUSINESS_DIR / "faq.yaml"))

# Words that carry no topic. Stripped before building FAQ match patterns.
STOP = {
    "yang", "untuk", "dengan", "dari", "kalau", "sama", "juga", "bisa", "saya",
    "kamu", "aku", "kak", "mas", "mbak", "bu", "pak", "ini", "itu", "ada",
    "apa", "gimana", "bagaimana", "berapa", "kapan", "mau", "nya", "sih", "dong",
    "ya", "aja", "udah", "sudah", "belum", "nggak", "gak", "tidak", "the", "and",
}


def _read(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return rows


def _resolved_keys() -> set[str]:
    return {r.get("key", "") for r in _read(RESOLVED) if r.get("key")}


def _key(row: dict) -> str:
    return f"{row.get('channel','?')}:{row.get('uid') or row.get('from','?')}"


def pending() -> list[dict]:
    done = _resolved_keys()
    out, seen = [], set()
    for r in _read(QUEUE):
        k = _key(r)
        if k in done or k in seen:
            continue
        seen.add(k)
        r["_key"] = k
        out.append(r)
    return out


def _who(row: dict) -> str:
    frm = str(row.get("from") or "?")
    return frm.split("@")[0].split("<")[-1].strip(" >")


def _topic(row: dict) -> str:
    subj = str(row.get("subject") or "").strip()
    if subj and subj.lower() not in ("(no subject)", "no subject"):
        return subj[:60]
    trig = row.get("triggers") or row.get("trigger_types") or []
    if isinstance(trig, list) and trig:
        return ", ".join(str(t) for t in trig[:2])
    return str(row.get("note") or "perlu dilihat")[:60]


def cmd_list(_args) -> int:
    rows = pending()
    if not rows:
        print("Antrean kosong — nggak ada yang nunggu jawaban kamu.")
        return 0
    print(f"{len(rows)} chat nunggu jawaban kamu:\n")
    for i, r in enumerate(rows, 1):
        print(f"  [{i}] {_who(r)} — {_topic(r)}")
    print('\nJawab: python3 handoff.py answer <no> --text "jawabannya"')
    print("Jawabannya langsung masuk FAQ, jadi lain kali nggak naik lagi.")
    return 0


def _patterns_from(text: str) -> list[str]:
    words = [w for w in re.findall(r"[a-zA-Z]{3,}", (text or "").lower())
             if w not in STOP]
    seen, uniq = set(), []
    for w in words:
        if w not in seen:
            seen.add(w)
            uniq.append(w)
    pats = uniq[:4]
    if len(uniq) >= 2:
        pats.insert(0, " ".join(uniq[:2]))
    return pats[:5]


def add_faq_entry(question: str, answer: str, tier: str = "T2") -> str | None:
    """
    Append one entry so the same question answers itself next time.

    Written conservatively: T2 (factual, non-binding) unless told otherwise,
    patterns drawn from the question's own words, and never overwriting an
    existing id.
    """
    if yaml is None:
        return None
    pats = _patterns_from(question)
    if not pats:
        return None
    try:
        FAQ_FILE.parent.mkdir(parents=True, exist_ok=True)
        doc = {}
        if FAQ_FILE.is_file():
            doc = yaml.safe_load(FAQ_FILE.read_text(encoding="utf-8")) or {}
        if not isinstance(doc, dict):
            return None
        entries = doc.setdefault("entries", [])
        if not isinstance(entries, list):
            return None
        base = re.sub(r"[^a-z0-9]+", "-", pats[0].lower()).strip("-") or "tanya"
        eid, n = base, 2
        existing = {e.get("id") for e in entries if isinstance(e, dict)}
        while eid in existing:
            eid, n = f"{base}-{n}", n + 1
        entries.append({"id": eid, "tier": tier, "patterns": pats,
                        "answer": answer.strip() + "\n",
                        "added": datetime.now().strftime("%Y-%m-%d"),
                        "source": "handoff"})
        FAQ_FILE.write_text(
            yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=88),
            encoding="utf-8")
        return eid
    except Exception:
        return None


def _resolve(row: dict, answer: str, faq_id: str | None, skipped: bool) -> None:
    try:
        BUSINESS_DIR.mkdir(parents=True, exist_ok=True)
        with RESOLVED.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "ts": datetime.now().isoformat(timespec="seconds"),
                "key": row["_key"], "who": _who(row), "topic": _topic(row),
                "answer": answer, "faq_id": faq_id, "skipped": skipped,
            }, ensure_ascii=False) + "\n")
    except Exception:
        pass


def cmd_answer(args) -> int:
    rows = pending()
    if not 1 <= args.n <= len(rows):
        print(f"Nomor {args.n} nggak ada. Jalankan `list` dulu.", file=sys.stderr)
        return 2
    row = rows[args.n - 1]
    faq_id = None
    if not args.no_faq:
        faq_id = add_faq_entry(_topic(row), args.text, tier=args.tier)
    _resolve(row, args.text, faq_id, skipped=False)
    print(f"✅ {_who(row)} — jawaban dicatat.")
    if faq_id:
        print(f"   Masuk FAQ sebagai '{faq_id}'. Pertanyaan begini nggak naik lagi.")
    elif not args.no_faq:
        print("   (belum masuk FAQ — cek faq.yaml-nya)")
    left = len(pending())
    print(f"   Sisa {left} lagi." if left else "   Antrean kosong.")
    return 0


def cmd_skip(args) -> int:
    rows = pending()
    if not 1 <= args.n <= len(rows):
        print(f"Nomor {args.n} nggak ada.", file=sys.stderr)
        return 2
    row = rows[args.n - 1]
    _resolve(row, "", None, skipped=True)
    print(f"Dilewati: {_who(row)} — {_topic(row)}")
    return 0


def cmd_stats(_args) -> int:
    from collections import Counter
    rows = _read(QUEUE)
    if not rows:
        print("Belum ada yang pernah naik ke kamu.")
        return 0
    trig = Counter()
    for r in rows:
        for t in (r.get("triggers") or r.get("trigger_types") or ["?"]):
            trig[str(t)] += 1
    print(f"{len(rows)} kali naik ke kamu, {len(pending())} masih nunggu.\n")
    for t, n in trig.most_common(6):
        note = "  ← ini kandidat FAQ" if n >= 3 and t not in ("injection", "binding") else ""
        print(f"  {n:3d}x  {t}{note}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Antrean chat yang butuh jawaban pemiliknya.")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("list")
    a = sub.add_parser("answer")
    a.add_argument("n", type=int)
    a.add_argument("--text", required=True)
    a.add_argument("--tier", default="T2", choices=["T2", "T3"])
    a.add_argument("--no-faq", action="store_true",
                   help="jawab sekali aja, jangan disimpan ke FAQ")
    s = sub.add_parser("skip"); s.add_argument("n", type=int)
    sub.add_parser("stats")
    args = ap.parse_args()
    return {"answer": cmd_answer, "skip": cmd_skip,
            "stats": cmd_stats}.get(args.cmd, cmd_list)(args)


if __name__ == "__main__":
    sys.exit(main())
