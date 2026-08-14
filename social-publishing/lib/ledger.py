#!/usr/bin/env python3
"""
ledger.py — what the hour actually produced, and what's still on the table.

The best sessions end with "besok ngapain" (good). None ended
with what just happened and what it's worth. An attendee who sees
"rara minta harga 50pcs" opens Hermes again tomorrow; one who ends on "here
are 6 templates, copy them yourself" does not.

It is also how session two stops being a cold start. The session that decides
whether this is a tool or a demo is the one where the owner comes back the
next morning — and it must not start from zero.

    python3 ledger.py add --kind sent    --who Wulan --what "maaf + ganti 2 bungkus"
    python3 ledger.py add --kind waiting --who rara  --what "minta harga reseller 50pcs" --money 550000
    python3 ledger.py add --kind fact    --what "3 orang nanya halal minggu ini"
    python3 ledger.py show               # today's recap, for the end of a session
    python3 ledger.py open               # what is still unfinished, for session two
    python3 ledger.py week               # the 15-second weekly recap

Append-only JSONL at ~/.hermes/state/ledger.jsonl. Fails open everywhere: a
ledger that errors must never stop someone answering a customer.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

# The ledger belongs to a business, not to a machine. It first lived in a global
# `~/.hermes/state`, which meant two things went wrong at once: an isolated run
# with its own HERMES_BUSINESS_DIR wrote into the real user's file (so that
# run's recap came up empty), and a test suite's fake sends landed in it
# alongside real ones. Anyone running Hermes for two businesses would have
# had their recaps merged the same way.
def _state_dir() -> Path:
    explicit = os.environ.get("HERMES_STATE_DIR")
    if explicit:
        return Path(explicit)
    biz = os.environ.get("HERMES_BUSINESS_DIR")
    if biz:
        return Path(biz) / "state"
    return Path(os.path.expanduser("~/.hermes/business/state"))


STATE_DIR = _state_dir()
LEDGER = STATE_DIR / "ledger.jsonl"

KINDS = {
    "sent":    ("✅", "kejawab"),
    "waiting": ("💰", "nunggu kamu"),
    "sentblast": ("📤", "promo terkirim"),
    "problem": ("⚠️", "perlu diurus"),
    "fact":    ("📌", "catatan"),
    "done":    ("✅", "beres"),
}


def _rows() -> list[dict]:
    if not LEDGER.is_file():
        return []
    out = []
    try:
        for line in LEDGER.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    except Exception:
        return []
    return out


def add(kind: str, who: str = "", what: str = "", money: int = 0, channel: str = "") -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        rec = {"ts": datetime.now().isoformat(timespec="seconds"), "kind": kind,
               "who": who, "what": what, "money": int(money or 0), "channel": channel}
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass  # fail open, always


def resolve(who: str) -> int:
    """Mark every open item for a person as handled. Returns how many."""
    rows = _rows()
    n = sum(1 for r in rows if r.get("kind") == "waiting"
            and r.get("who", "").lower() == who.lower())
    if n:
        add("done", who=who, what="beres")
    return n


def _since(days: int) -> list[dict]:
    cutoff = datetime.now() - timedelta(days=days)
    out = []
    for r in _rows():
        try:
            if datetime.fromisoformat(r["ts"]) >= cutoff:
                out.append(r)
        except Exception:
            continue
    return out


def _open_items(rows: list[dict]) -> list[dict]:
    done = {r.get("who", "").lower() for r in rows if r.get("kind") == "done"}
    return [r for r in rows if r.get("kind") in ("waiting", "problem")
            and r.get("who", "").lower() not in done]


def _rupiah(n: int) -> str:
    return "Rp " + f"{int(n):,}".replace(",", ".")


def show(days: int = 1) -> str:
    rows = _since(days)
    if not rows:
        return "Belum ada yang tercatat hari ini."
    sent = [r for r in rows if r.get("kind") == "sent"]
    blast = [r for r in rows if r.get("kind") == "sentblast"]
    openi = _open_items(rows)
    money = sum(r.get("money", 0) for r in openi)

    lines = ["Hari ini:"]
    if sent:
        names = ", ".join(dict.fromkeys(r["who"] for r in sent if r.get("who")))
        lines.append(f"  ✅ {len(sent)} orang kejawab" + (f" — {names}" if names else ""))
    if blast:
        total = sum(int(r.get("what") or 0) if str(r.get("what", "")).isdigit() else 1 for r in blast)
        lines.append(f"  📤 promo terkirim ke {total} kontak")
    if openi:
        lines.append("  💰 nunggu keputusan kamu:")
        for r in openi:
            tail = f" ({_rupiah(r['money'])})" if r.get("money") else ""
            lines.append(f"     - {r.get('who') or '?'}: {r.get('what','')}{tail}")
    if money:
        lines.append(f"  Total yang lagi nyangkut: {_rupiah(money)}")
    facts = [r for r in rows if r.get("kind") == "fact"]
    if facts:
        lines.append("  📌 " + " · ".join(r.get("what", "") for r in facts[:3]))
    if openi:
        lines.append(f"  ⏭  besok: mulai dari {openi[0].get('who') or 'yang nunggu'}")
    return "\n".join(lines)


def open_report() -> str:
    """Session two's opening line. Names yesterday's unfinished business."""
    openi = _open_items(_since(14))
    if not openi:
        return ""
    if len(openi) == 1:
        r = openi[0]
        return f"{r.get('who')} masih nunggu — {r.get('what')}. Mulai dari situ?"
    names = ", ".join(r.get("who") or "?" for r in openi[:3])
    more = f" (+{len(openi)-3} lagi)" if len(openi) > 3 else ""
    return f"Kemarin belum kelar: {names}{more}. Mulai dari {openi[0].get('who')}?"


def week() -> str:
    rows = _since(7)
    if not rows:
        return "Minggu ini belum ada yang tercatat."
    sent = sum(1 for r in rows if r.get("kind") == "sent")
    blast = sum(1 for r in rows if r.get("kind") == "sentblast")
    money = sum(r.get("money", 0) for r in rows if r.get("kind") in ("waiting", "done"))
    asked = Counter(r.get("what", "").strip().lower()
                    for r in rows if r.get("kind") == "fact" and r.get("what"))
    lines = [f"Minggu ini: {sent} chat kejawab" + (f", {blast} promo terkirim" if blast else "")]
    if money:
        lines.append(f"  Nilai yang lewat: {_rupiah(money)}")
    if asked:
        top, n = asked.most_common(1)[0]
        if n >= 2:
            lines.append(f"  Paling sering ditanya: {top} ({n}x) — masukin FAQ biar dijawab sendiri")
    openi = _open_items(rows)
    if openi:
        lines.append(f"  Masih nunggu: " + ", ".join(r.get("who") or "?" for r in openi[:4]))
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Catatan hasil sesi.")
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add")
    a.add_argument("--kind", required=True, choices=sorted(KINDS))
    a.add_argument("--who", default="")
    a.add_argument("--what", default="")
    a.add_argument("--money", type=int, default=0)
    a.add_argument("--channel", default="")
    r = sub.add_parser("resolve"); r.add_argument("who")
    s = sub.add_parser("show"); s.add_argument("--days", type=int, default=1)
    sub.add_parser("open")
    sub.add_parser("week")
    args = ap.parse_args()

    if args.cmd == "add":
        add(args.kind, args.who, args.what, args.money, args.channel)
        return 0
    if args.cmd == "resolve":
        print(f"{resolve(args.who)} item beres")
        return 0
    if args.cmd == "open":
        out = open_report()
        print(out) if out else None
        return 0 if out else 1
    if args.cmd == "week":
        print(week())
        return 0
    print(show(getattr(args, "days", 1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
