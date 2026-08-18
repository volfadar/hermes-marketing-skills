#!/usr/bin/env python3
"""artifact-guard.py — a pre_tool_call hook that enforces the discipline at write time.

Why this exists
---------------
Recorded forward sessions showed five capable models reading ~2,700 words of evidence
discipline and all five violating it. Post-hardening sessions showed the same
shape at smaller amplitude: an honest goal reconciliation and zero fabricated
citations, but dozens of untagged decision figures written into the artifacts —
and saved into the working directory rather than a declared output directory,
three times running.

The pattern is positional, not moral. The rules are read once at session start; the
violation happens at message ~120, when the model is composing a deliverable. Prose
that far upstream does not survive the trip.

So the checks run at the moment of the write. Hermes shell hooks may block a tool call
(``{"decision": "block", "reason": ...}``), and a blocked write comes back to the model
as a correctable error — which is exactly the feedback loop the prose could not create.

Checks
------
  1. LOCATION      — with HERMES_OUTPUT_DIR set, writes must land under it.
  2. PROVENANCE    — decision figures carry [SOURCE:]/[USER]/[CALC:]/[ASSUMPTION]
                     (or the Indonesian [SUMBER:]/[PENGGUNA]/[HITUNG:]/[ASUMSI]).
  3. GOAL FIT      — a plan/funnel/journey artifact states needs vs yields vs gap.
  4. MONEY GATES   — stop/scale rules key on money, not on replies and DMs.
  5. TRANSFER      — a rate or rank asserted about *the reader's* business must not
                     rest on a statistic drawn from someone else's record.

Deadlock safety
---------------
A wrong block must never strand a session. Each (session, path) is blocked at most
MAX_BLOCKS times; the next attempt is allowed with the findings recorded to the log.
The agent gets two chances to fix its own work, then ships with the problem visible.

Install
-------
  hooks:
    pre_tool_call:
      - matcher: "write_file|patch|create_file|edit_file|apply_patch"
        command: "/path/to/artifact-guard.py"
        timeout: 10

Exit code is always 0; the decision travels in stdout JSON.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

MAX_BLOCKS = 2
STATE = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / "cache" / "artifact-guard.json"
LOG = STATE.with_name("artifact-guard.log")

TAG_RE = re.compile(
    r"\[(SOURCE\s*:[^\]]+|SUMBER\s*:[^\]]+|USER|PENGGUNA|CALC\s*:[^\]]+"
    r"|HITUNG\s*:[^\]]+|ASSUMPTION|ASUMSI)\]",
    re.I,
)
MONEY_RE = re.compile(r"(?:Rp|IDR|USD|\$)\s?[\d][\d.,]*\s?(?:rb|ribu|jt|juta|k)?", re.I)
PERCENT_RE = re.compile(r"\d[\d.,]*\s?%")
UNIT_RE = re.compile(
    r"\b\d[\d.,]*\s?(?:jam|hari|minggu|bulan|pcs|sku|klien|client|orang|pesan|order|listing)\b",
    re.I,
)
SKIP_LINE_RE = re.compile(r"^\s*(?:#{1,6}\s|\|[\s:-]+\||>?\s*\[?\d+\]?[.)]\s*$|<!--)")

# A deliverable that draws a route to a purchase must first say what it earns.
PLAN_RE = re.compile(r"\b(journey|funnel|jalur|rute|graph|roadmap|rencana|plan)\b", re.I)
MARKET_FIT_RE = re.compile(
    r"\b(market[\s-]*fit|kecocokan pasar|buyer[\s-]*side|sinyal pembeli)\b",
    re.I,
)
GOAL_FIT_RE = re.compile(
    r"(goal[\s-]*(fit|reconciliation)|rekonsiliasi|butuh.*rencana.*hasil"
    r"|gap\s*[:=]|needs\s*[:=]|target bulan|bulan 1 .*(realistis|tidak akan))",
    re.I,
)

STOPRULE_RE = re.compile(r"\b(stop[\s/-]*(rule|scale)|stop/scale|gate|kill switch|kriteria lanjut)\b", re.I)
# The demand ladder's upper rungs: money received, a deposit, a scheduled paid pilot,
# a written commitment. "Someone replied" is the bottom rung and is not a stop rule.
MONEY_SIGNAL_RE = re.compile(
    r"\b(bayar|dibayar|membayar|transfer|DP|deposit|uang masuk|invoice|paid|"
    r"komitmen tertulis|tanda jadi|pilot berbayar|harga disepakati)\b",
    re.I,
)

RANK_RE = re.compile(
    r"\b(nomor \d|no\.? ?\d|peringkat|paling sering|penyebab utama|terbesar|"
    r"top ?\d|sumber .* utama)\b",
    re.I,
)
SECOND_PERSON_RE = re.compile(r"\b(kamu|anda|toko kamu|toko anda|bisnis kamu|your)\b", re.I)

URL_RE = re.compile(r'https?://[^\s"\'<>)\]},;]+')
SEARCH_HOST_RE = re.compile(r"(google\.[a-z.]+/search|/search\?|bing\.com/search|duckduckgo)", re.I)

WRITE_TOOLS = {"write_file", "patch", "create_file", "edit_file", "apply_patch"}
PATH_KEYS = ("path", "file_path", "filename", "target", "file")
CONTENT_KEYS = ("content", "text", "body", "new_content", "patch", "data")


def scrub(line: str) -> str:
    line = re.sub(r"`[^`]*`", " ", line)
    line = re.sub(r"https?://\S+", " ", line)
    line = re.sub(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b", " ", line)
    line = re.sub(r"\bv?\d+\.\d+(?:\.\d+)?\b", " ", line)
    return line


ZERO_MONEY_RE = re.compile(r"^(?:Rp|IDR|USD|\$)\s?0+(?:[.,]0+)?$", re.I)


def figures(line: str) -> list[str]:
    """Figures that could move a decision. A zero cost cannot mislead anyone about
    what something costs, so it is not worth a provenance tag — the free-rung problem
    is caught by the money-gate check instead."""
    out: list[str] = []
    for rx in (MONEY_RE, PERCENT_RE, UNIT_RE):
        for m in rx.finditer(line):
            tok = m.group(0).strip()
            if ZERO_MONEY_RE.match(tok):
                continue
            out.append(tok)
    return out


def normalise(url: str) -> str:
    """Trailing punctuation is markup, not address. The backslash matters: tool
    arguments are often a JSON *string*, so re-serialising them leaves `\\"` and a
    naive capture ends every URL with a backslash — which silently makes every
    citation look unopened."""
    return url.rstrip("/).,;\"'\\").lower()


def navigated_urls(session_id: str) -> set[str]:
    """Every URL this session actually asked a tool to open.

    Read from the live state.db rather than trusted from the artifact, because the
    thing being checked is precisely a self-reported status. A v4 run navigated to
    komerce.id/blog/biaya-admin-marketplace-2024/, then wrote the full Google-result
    URL into its source ledger marked `opened` with a publication date. The ledger
    format the skill mandates made the unopened citation look *more* credible.
    """
    db = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / "state.db"
    if not db.exists() or not session_id:
        return set()
    try:
        import sqlite3
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=3)
        rows = con.execute(
            "SELECT tool_calls FROM messages WHERE session_id=? AND tool_calls IS NOT NULL",
            (session_id,),
        ).fetchall()
        con.close()
    except Exception:
        return set()
    urls: set[str] = set()
    for (blob,) in rows:
        if not blob:
            continue
        if isinstance(blob, (bytes, bytearray)):
            blob = blob.decode("utf-8", "replace")
        try:
            calls = json.loads(blob)
        except Exception:
            continue
        for call in calls if isinstance(calls, list) else [calls]:
            if not isinstance(call, dict):
                continue
            fn = call.get("function") if isinstance(call.get("function"), dict) else {}
            name = str(fn.get("name") or call.get("name") or "")
            # Only a navigation counts. Including every tool call would let the write
            # itself vouch for its own citations — the artifact contains the URLs, the
            # write is a tool call, so every citation would validate itself.
            if not name.startswith(("browser_", "fetch", "http", "web")):
                continue
            payload = json.dumps(fn.get("arguments") or call.get("arguments") or call,
                                 ensure_ascii=False)
            urls.update(normalise(u) for u in URL_RE.findall(payload))
    return urls


def check(path: str, content: str, session_id: str = "") -> list[str]:
    problems: list[str] = []

    out_dir = os.environ.get("HERMES_OUTPUT_DIR", "").strip()
    if out_dir and path:
        try:
            resolved = Path(path).expanduser().resolve()
            target = Path(out_dir).expanduser().resolve()
            if not str(resolved).startswith(str(target)):
                problems.append(
                    f"LOCATION: session artifacts belong under {target}, not {resolved}. "
                    f"Rewrite the same content to {target / resolved.name}."
                )
        except Exception:
            pass

    untagged: list[str] = []
    in_fence = False
    lines = content.splitlines()
    for n, raw in enumerate(lines, 1):
        if raw.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or SKIP_LINE_RE.match(raw):
            continue
        figs = figures(scrub(raw))
        if figs and not TAG_RE.search(raw):
            untagged.append(f"L{n}: {', '.join(figs[:3])} — {raw.strip()[:70]}")

    if len(untagged) > 3:
        problems.append(
            "PROVENANCE: %d lines carry a decision figure with no origin tag. "
            "Tag each with [SUMBER: …] / [PENGGUNA] / [HITUNG: …] / [ASUMSI]. First few:\n    %s"
            % (len(untagged), "\n    ".join(untagged[:6]))
        )

    if PLAN_RE.search(content) and len(content) > 600 and not GOAL_FIT_RE.search(content):
        problems.append(
            "GOAL FIT: this plan never reconciles against the goal. State three lines "
            "before the route — what the user needs and by when, what this plan yields "
            "in that window, and the gap."
        )

    if PLAN_RE.search(content) and len(content) > 600 and not MARKET_FIT_RE.search(content):
        problems.append(
            "MARKET FIT: this commercial route has no market-fit record. Before "
            "installing an offer or channel, state the geography, buyer/scale, "
            "purchase context, current alternative, strongest buyer-side signal, "
            "segment-transfer gap, and verdict (validated / plausible-test-only / "
            "unverified / contradicted). Seller pages prove supply, not demand."
        )

    if STOPRULE_RE.search(content) and not MONEY_SIGNAL_RE.search(content):
        problems.append(
            "MONEY GATES: the stop/scale rules key on replies, DMs or downloads. "
            "Those are the bottom of the demand ladder. At least one gate must turn on "
            "money received, a deposit, a scheduled paid pilot, or a written commitment."
        )

    # A rank is itself the figure ("complaint number 4"), so this must not require a
    # separate money/unit token — that is why the v3 overreach slipped through the
    # first version of this check.
    for n, raw in enumerate(lines, 1):
        if RANK_RE.search(raw) and SECOND_PERSON_RE.search(raw):
            problems.append(
                f"TRANSFER (L{n}): a rank or rate is asserted about the reader's own "
                f"business from a record of someone else's. State the denominator and "
                f"whose it is, or reframe as a question to test.\n    {raw.strip()[:120]}"
            )
            break

    cited = {normalise(u) for u in URL_RE.findall(content) if not SEARCH_HOST_RE.search(u)}
    if cited:
        opened = navigated_urls(session_id)
        if opened:
            # Only accuse when the session did navigate somewhere; an empty set means
            # the tool-call shape was unreadable, not that nothing was opened.
            unopened = sorted(u for u in cited if u not in opened)
            if unopened:
                problems.append(
                    "CITATION: %d URL(s) appear in this artifact that this session never "
                    "opened. A URL copied from a search result is a lead, not a source, and "
                    "writing `opened` next to it does not make it so. Open them or move them "
                    "to a leads list marked [search result]:\n    %s"
                    % (len(unopened), "\n    ".join(unopened[:5]))
                )

    return problems


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}


def save_state(st: dict) -> None:
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(st))
    except Exception:
        pass


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") not in WRITE_TOOLS:
        return 0

    args = payload.get("tool_input") or payload.get("args") or {}
    if not isinstance(args, dict):
        return 0

    path = next((str(args[k]) for k in PATH_KEYS if args.get(k)), "")
    content = next((str(args[k]) for k in CONTENT_KEYS if args.get(k)), "")
    if not content or len(content) < 200:
        return 0
    if not (path.endswith((".md", ".txt", ".markdown")) or not path):
        return 0

    problems = check(path, content, str(payload.get("session_id") or ""))
    if not problems:
        return 0

    key = f"{payload.get('session_id', '-')}::{path}"
    st = load_state()
    count = int(st.get(key, 0))

    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a") as fh:
            fh.write(json.dumps({
                "t": int(time.time()), "path": path, "attempt": count + 1,
                "blocked": count < MAX_BLOCKS, "problems": problems,
            }, ensure_ascii=False) + "\n")
    except Exception:
        pass

    if count >= MAX_BLOCKS:
        # Two corrections were offered and not taken. Ship it rather than strand
        # the session, but the log keeps the receipt.
        return 0

    st[key] = count + 1
    save_state(st)

    json.dump({
        "decision": "block",
        "reason": (
            "Artifact rejected by the discipline guard — fix and write again "
            f"(attempt {count + 1} of {MAX_BLOCKS}):\n\n- " + "\n- ".join(problems)
        ),
    }, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
