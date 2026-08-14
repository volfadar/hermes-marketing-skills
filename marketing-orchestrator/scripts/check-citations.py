#!/usr/bin/env python3
"""check-citations.py — prove every cited URL was actually fetched.

Audits a Hermes session export (or a written artifact) and classifies every URL
that appears in agent output against what the tool trace actually retrieved.

Why this exists
---------------
In recorded coaching sessions, two of five models cited pages they
never opened: vendor URLs harvested from a Google results page and a Google AI
Overview, presented as consulted sources with claims attached. One model cited a
URL that appears nowhere in its trace at all. Prose rules did not prevent this —
all five models had read "never fabricate a URL" and "link to the actual page,
not a search-results page".

Classification
--------------
  FETCHED   URL was a tool-call target and the following result reported success.
            Safe to cite.
  SERP_ONLY URL appeared inside a tool result (search page, AI overview, another
            page's links) but was never opened. NOT a source. Cite only as
            "seen in search results, not opened".
  UNSOURCED URL appears nowhere in the trace before the agent used it.
            Treat as fabricated until proven otherwise.

Agent output means assistant messages AND the content of write_file / patch /
create_file calls — the artifact the user keeps is graded too, not just the chat.

Usage
-----
  check-citations.py <session.jsonl> [more.jsonl ...]
  check-citations.py --artifact <file.md> --session <session.jsonl>
  check-citations.py <session.jsonl> --json
  check-citations.py <session.jsonl> --strict     # exit 1 if any violation

Exit codes: 0 clean (or non-strict), 1 violations found under --strict, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

URL_RE = re.compile(r'https?://[^\s"\'\\<>)\]},;]+')
# Google renders result URLs as breadcrumbs: "https://jubelio.com › omnichannel-marketplace"
# and truncates long paths with "...". A model that copies that string is citing a search
# result, not a page it opened — the single most common citation failure observed.
BREADCRUMB_RE = re.compile(
    r'https?://([^\s"\'\\<>,;]+?)((?:\s*(?:\u203a|›)\s*[^\s"\'\\<>,;›\u203a]+)+)'
)
SEARCH_HOST_MARKERS = (
    "google.com/search",
    "google.co.id/search",
    "bing.com/search",
    "duckduckgo.com/",
    "search.yahoo.com",
    "/search?q=",
    "search.json?q=",
)
OUTPUT_TOOLS = {"write_file", "patch", "create_file", "edit_file", "apply_patch"}


def normalize(url: str) -> str:
    """Trim trailing punctuation and fragments so citations match fetches."""
    url = url.split("#", 1)[0]
    url = url.rstrip(".,;:!?)\"'*>]}")
    url = re.sub(r"^http://", "https://", url)
    return url.rstrip("/")


def key_of(url: str) -> str:
    """Host+path, for matching a citation to a fetch that carried query params."""
    m = re.match(r"https?://([^/]+)(/[^?]*)?", url)
    if not m:
        return url
    host = m.group(1).lower().removeprefix("www.")
    return host + (m.group(2) or "").rstrip("/")


def is_search_page(url: str) -> bool:
    return any(marker in url for marker in SEARCH_HOST_MARKERS)


def breadcrumb_urls(text: str) -> list[tuple[str, bool]]:
    """Reconstruct '(url, is_truncated)' from Google breadcrumb display strings."""
    out = []
    for host, tail in BREADCRUMB_RE.findall(text):
        segments = [s.strip() for s in re.split(r"›|›", tail) if s.strip()]
        if not segments:
            continue
        truncated = segments[-1].endswith("...")
        segments[-1] = segments[-1].rstrip(".")
        url = f"https://{host.rstrip('/')}/" + "/".join(segments)
        out.append((normalize(url), truncated))
    return out


def as_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def result_succeeded(text: str) -> bool:
    """A tool result counts as a successful fetch unless it says otherwise."""
    if '"success": false' in text or '"success":false' in text:
        return False
    if re.search(r'"exit_code":\s*[1-9]', text):
        return False
    if re.search(r"\b(404|403|502|503)\b.{0,40}(not found|forbidden|error|gateway)", text, re.I):
        return False
    return True


def load_messages(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8", errors="replace").strip()
    if not raw:
        return []
    if raw[0] == "{":
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict) and isinstance(obj.get("messages"), list):
                return obj["messages"]
            if isinstance(obj, dict):
                return [obj]
        except json.JSONDecodeError:
            pass
    messages = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return messages


def tool_calls_of(message: dict) -> list[tuple[str, str]]:
    """Return (tool_name, argument_text) for every tool call on a message."""
    out = []
    for call in message.get("tool_calls") or []:
        fn = call.get("function") or {}
        name = fn.get("name") or call.get("name") or ""
        args = fn.get("arguments", call.get("arguments", ""))
        out.append((name, as_text(args)))
    return out


def audit(messages: list[dict], extra_outputs: list[tuple[str, str]] | None = None) -> dict:
    fetched: set[str] = set()
    fetched_keys: set[str] = set()
    seen_in_results: set[str] = set()
    seen_prefixes: list[str] = []  # from truncated Google breadcrumbs
    findings: list[dict] = []

    def classify(url: str) -> str:
        n = normalize(url)
        if n in fetched or key_of(n) in fetched_keys:
            return "FETCHED"
        if n in seen_in_results or any(key_of(n) == key_of(s) for s in seen_in_results):
            return "SERP_ONLY"
        stripped = n.rstrip(".")
        if any(stripped.startswith(p) or p.startswith(stripped) for p in seen_prefixes):
            return "SERP_ONLY"
        return "UNSOURCED"

    def record(url: str, where: str, index: int) -> None:
        n = normalize(url)
        findings.append(
            {
                "url": n,
                "status": classify(n),
                "is_search_page": is_search_page(n),
                "where": where,
                "message_index": index,
            }
        )

    pending: list[str] = []  # URLs targeted by the immediately preceding tool call

    for i, message in enumerate(messages):
        role = message.get("role")
        content = as_text(message.get("content"))

        if role == "tool":
            # Resolve whatever the preceding call targeted.
            if pending and result_succeeded(content):
                for url in pending:
                    fetched.add(url)
                    fetched_keys.add(key_of(url))
            pending = []
            # Everything else visible in the body was seen, not opened.
            for url in URL_RE.findall(content):
                n = normalize(url)
                if n not in fetched:
                    seen_in_results.add(n)
            for url, truncated in breadcrumb_urls(content):
                if truncated:
                    seen_prefixes.append(url.rstrip("."))
                elif url not in fetched:
                    seen_in_results.add(url)
            continue

        if role == "assistant":
            calls = tool_calls_of(message)
            # Agent-authored files are output, and are graded like chat.
            for name, args in calls:
                if name in OUTPUT_TOOLS:
                    for url in URL_RE.findall(args):
                        record(url, f"{name} (artifact)", i)
            # Non-output calls declare fetch intent for the next tool result.
            pending = [
                normalize(u)
                for name, args in calls
                if name not in OUTPUT_TOOLS
                for u in URL_RE.findall(args)
            ]
            for url in URL_RE.findall(content):
                record(url, "assistant message", i)
            continue

        pending = []

    for where, text in extra_outputs or []:
        for url in URL_RE.findall(text):
            record(url, where, -1)

    return {
        "fetched_count": len(fetched),
        "seen_only_count": len(seen_in_results),
        "citations": findings,
    }


def summarize(label: str, report: dict) -> int:
    citations = report["citations"]
    bad = [c for c in citations if c["status"] != "FETCHED"]
    search_cites = [c for c in citations if c["status"] == "FETCHED" and c["is_search_page"]]

    print(f"\n=== {label} ===")
    print(f"  pages actually fetched : {report['fetched_count']}")
    print(f"  URLs cited by the agent: {len(citations)}")

    if not citations:
        print("  OK — no citations to verify.")
        return 0

    for status in ("UNSOURCED", "SERP_ONLY"):
        hits = [c for c in bad if c["status"] == status]
        if not hits:
            continue
        note = (
            "appears nowhere in the trace — treat as fabricated"
            if status == "UNSOURCED"
            else "seen in a result but never opened — not a source"
        )
        print(f"\n  {status} ({len(hits)}) — {note}:")
        for c in hits:
            print(f"    ✗ {c['url']}")
            print(f"        in: {c['where']} (msg {c['message_index']})")

    if search_cites:
        print(f"\n  WEAK ({len(search_cites)}) — cited a search-results page as a source:")
        for c in search_cites:
            print(f"    ! {c['url']}")

    violations = len(bad)
    if violations == 0 and not search_cites:
        print("  OK — every cited URL was fetched successfully.")
    return violations


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sessions", nargs="*", type=Path, help="session export(s) to audit")
    ap.add_argument("--session", type=Path, help="session export providing the tool trace")
    ap.add_argument("--artifact", type=Path, action="append", default=[],
                    help="agent-written file to grade against that trace")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--strict", action="store_true", help="exit 1 when any citation is not FETCHED")
    args = ap.parse_args()

    jobs: list[tuple[str, list[dict], list[tuple[str, str]]]] = []

    if args.session or args.artifact:
        if not args.session:
            print("--artifact requires --session (the trace to verify against)", file=sys.stderr)
            return 2
        messages = load_messages(args.session)
        extras = [(f"artifact:{p.name}", p.read_text(encoding="utf-8", errors="replace"))
                  for p in args.artifact]
        jobs.append((args.session.parent.name or args.session.name, messages, extras))

    for path in args.sessions:
        jobs.append((path.parent.name or path.name, load_messages(path), []))

    if not jobs:
        ap.print_usage(sys.stderr)
        return 2

    total = 0
    reports = {}
    for label, messages, extras in jobs:
        report = audit(messages, extras)
        reports[label] = report
        if args.json:
            continue
        total += summarize(label, report)

    if args.json:
        print(json.dumps(reports, indent=2, ensure_ascii=False))
        total = sum(
            1 for r in reports.values() for c in r["citations"] if c["status"] != "FETCHED"
        )

    if not args.json:
        print(f"\nTotal citations needing correction: {total}")
    return 1 if (args.strict and total) else 0


if __name__ == "__main__":
    sys.exit(main())
