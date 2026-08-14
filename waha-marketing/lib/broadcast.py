#!/usr/bin/env python3
"""
WAHA Broadcast Engine — humanized, opt-in-aware, anti-ban.

The single most important script in this skill. Sends a sequence of WhatsApp
messages through WAHA, but with ALL the safeguards the official WAHA
"how to avoid blocking" guide demands:

  - randomized delays (never fixed intervals)
  - per-contact cooldown tracking (never hammer one person)
  - batch + long pause pattern (4 msgs/contact/hour, then halt)
  - message variation (rotate templates, insert first name)
  - typing indicator before each message (humanization)
  - soft warnings (opt-in check, spam-likelihood estimator)
  - kill-switch env var (HALT file) for emergency stop
  - per-message error handling (skip 463 = shadow restriction, don't restart)
  - dry-run mode (validate plan without sending)

This is NOT a spam tool. It is a SAFE BROADCAST HELPER for opted-in lists.
The skill refuses to run without explicit --i-confirm-optin flag.

Usage:
  python3 broadcast.py \\
    --session all-in-one-device \\
    --contacts contacts.csv \\
    --message-templates templates.txt \\
    --waha-url https://your-waha.example \\
    --api-key XXX \\
    --dry-run            # plan only, no send
  python3 broadcast.py ... --i-confirm-optin   # actually send

See references/anti-ban.md for the full reasoning behind every safeguard.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import signal
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ---------------------------------------------------------------------------
# Anti-ban constants (sourced from WAHA official docs + community consensus)
# ---------------------------------------------------------------------------

# Per WAHA docs: "maximum 4 messages per contact that have replied per hour,
# then halt for another hour."
MAX_MSGS_PER_CONTACT_PER_HOUR = 4

# Randomized per-message delay bounds (seconds).
# Range chosen to feel human but not glacial. Multiply by message length factor.
DELAY_MIN = 12.0
DELAY_MAX = 45.0
DELAY_LONG_BATCH_MIN = 300.0   # 5-min pause between batches
DELAY_LONG_BATCH_MAX = 900.0   # up to 15-min

# Hard daily cap (community consensus for safety; adjust per account age).
DAILY_CAP_NEW_ACCOUNT = 50
DAILY_CAP_WARMED_30D = 200
DAILY_CAP_ESTABLISHED = 500

# Kill-switch. The canonical switch is shared (`lib/halt.py`) so that ONE command
# stops WhatsApp, email and scheduled jobs together, and so that it survives a
# reboot — the old `/tmp` file did not, which meant a halted install could quietly
# resume after a restart with nobody pressing resume.
#
# The legacy path stays honoured for reading, so upgrading never un-halts anything.
HALT_FILE = Path(os.environ.get("WAHA_HALT_FILE", "/tmp/waha-broadcast-halt"))

_HALT_LIB = None
try:  # pragma: no cover - import shape depends on how the file is invoked
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import halt as _HALT_LIB  # type: ignore
except Exception:  # noqa: BLE001 - a missing shared lib must not brick sending
    _HALT_LIB = None

# State directory for cooldown tracking
STATE_DIR = Path(os.environ.get("WAHA_STATE_DIR", os.path.expanduser("~/.waha-marketing/state")))

# Anti-ban brakes — shared with waha.sh `pace_and_check` via the SAME state file,
# so an agent cannot bypass by alternating `send-text` and broadcast. A recorded
# finding: these brakes existed only in waha.sh; a blast through
# broadcast.py walked straight past them and the number was banned.
WAHA_CFG_DIR = os.environ.get("WAHA_CONFIG_DIR", os.path.expanduser("~/.waha-marketing"))
SEND_LOG = Path(os.environ.get("WAHA_SEND_LOG",
                               os.path.join(WAHA_CFG_DIR, "state", "send-log.tsv")))
KNOWN_CACHE = Path(os.path.join(WAHA_CFG_DIR, "state", "known-chats.txt"))
KNOWN_TTL_S = 300
COLD_THRESHOLD = int(os.environ.get("WAHA_COLD_THRESHOLD", "4"))
BLAST_THRESHOLD = int(os.environ.get("WAHA_BLAST_THRESHOLD", "5"))
MIN_GAP_S = float(os.environ.get("WAHA_MIN_GAP_S", "12"))
STATE_DIR.mkdir(parents=True, exist_ok=True)

# Shared layer: the business profile and the copy checker. Both fail open —
# a missing profile must never stop a broadcast, it only means the copy is
# judged on mechanics alone and the swap test sits out.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import profile as profile_lib
except Exception:
    profile_lib = None
try:
    import copycheck
except Exception:
    copycheck = None
try:
    import ledger as ledger_lib
except Exception:
    ledger_lib = None


def _ledger(kind: str, **kw) -> None:
    """
    Best-effort bookkeeping.

    `waha.sh send-text` recorded sends and this path did not, so a broadcast of
    four messages left the day's recap empty and tomorrow opened as a cold
    start. That is the same shape as the gates-on-email-not-WhatsApp and
    brakes-on-send-text-not-broadcast findings: **behaviour landing on one send
    path and not its twin.** Fourth instance; assume any new send path is
    missing everything until a test says otherwise.
    """
    if ledger_lib is None:
        return
    try:
        ledger_lib.add(kind, **kw)
    except Exception:
        pass


@dataclass
class Contact:
    phone: str               # e.g. "6281234567890"
    name: str = ""           # first name (for personalization)
    opt_in: bool = False     # explicit opt-in flag from CSV
    opt_in_source: str = ""  # where they opted in (form, WA reply, etc.)
    labels: list = field(default_factory=list)


@dataclass
class BroadcastPlan:
    contacts: list
    skipped_no_optin: list
    skipped_blacklist: list
    estimated_minutes: int
    daily_cap_risk: str      # "low" | "moderate" | "high" | "block"


def log(msg: str, level: str = "INFO") -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {level}: {msg}", file=sys.stderr)


def soft_warn(msg: str) -> None:
    """Soft warning — does not block, but emphasizes risk. Per user's request."""
    print(f"\n  ⚠️  SOFT WARNING: {msg}\n", file=sys.stderr)


def fatal(msg: str) -> None:
    log(msg, "FATAL")
    sys.exit(1)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def waha_request(url: str, api_key: str, method: str = "GET", body: dict = None, timeout: int = 30):
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, method=method)
    req.add_header("X-Api-Key", api_key)
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                return resp.status, json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                return resp.status, {"_raw": raw.decode(errors="replace")}
    except HTTPError as e:
        body_text = e.read().decode(errors="replace")[:300]
        return e.code, {"error": body_text}


# ---------------------------------------------------------------------------
# Humanization
# ---------------------------------------------------------------------------

def randomized_delay(base_min: float = DELAY_MIN, base_max: float = DELAY_MAX,
                     msg_len: int = 0) -> float:
    """Longer messages => longer 'typing' delay, with jitter."""
    # ~1 second per 30 chars, capped, plus random jitter
    length_factor = min(msg_len / 30.0, 12.0)
    base = random.uniform(base_min, base_max) + length_factor
    # ±25% jitter on top
    jitter = base * random.uniform(-0.25, 0.25)
    return max(5.0, base + jitter)


HONORIFICS = ("bu", "pak", "ibu", "bapak", "mas", "mbak", "kak", "kang", "teh")


def humanize_message(template: str, contact: Contact) -> str:
    """Insert the recipient's first name, plus a small randomization to defeat
    identical-message detection.

    The variation must never land on the customer's own name. An earlier version
    randomized between `contact.name` and `contact.name.lower().capitalize()`,
    which rewrote "Bu Dewi" as "Bu dewi" — and against a template reading
    "Kak {name}" the message that reached a regular customer was
    "Kak Bu dewi, Makaroni Level 5 baru nyampe nih!". Doubled honorific, name
    misspelled. Vary the sentence, never the person.
    """
    msg = template
    if contact.name:
        name = contact.name.strip()
        # If the template already says Kak/Bu/Pak right before the placeholder,
        # a stored name of "Bu Dewi" would stack a second one.
        before = msg.split("{name}")[0].rstrip()
        lead = before.split()[-1].lower().strip(",.:") if before.split() else ""
        parts = name.split()
        if lead in HONORIFICS and len(parts) > 1 and parts[0].lower() in HONORIFICS:
            name = " ".join(parts[1:])
        msg = msg.replace("{name}", name)
    else:
        # No name is not a reason to send "Selamat siang !" — four numbers got
        # exactly that during evaluation. Close the gap the placeholder left.
        msg = msg.replace("{name}", "")
        msg = re.sub(r"[ \t]{2,}", " ", msg)
        msg = re.sub(r"\s+([,.!?])", r"\1", msg)        # "siang !"  -> "siang!"
        msg = re.sub(r"^[\s,.!?]+", "", msg)            # ", basreng" -> "basreng"
        msg = re.sub(r"^([A-Za-z]+),", r"\1!", msg)     # "Hai, yang" -> "Hai! yang"
        msg = re.sub(r"([.!?])\s+([a-z])",
                     lambda m: f"{m.group(1)} {m.group(2).upper()}", msg, count=1)
        msg = (msg[:1].upper() + msg[1:]).strip()
    # Random double-space insertion at one mid-sentence spot (subtle variation)
    if random.random() < 0.3 and ". " in msg:
        variants = msg.split(". ", 1)
        sep = random.choice([". ", ".  ", ".\n"])
        msg = variants[0] + sep + variants[1]
    return msg.strip()


def do_typing_indicator(waha_url: str, api_key: str, session: str, chat_id: str,
                        duration_sec: float) -> None:
    """Send startTyping -> sleep -> stopTyping to mimic human composition."""
    code, _ = waha_request(f"{waha_url}/api/startTyping", api_key, "POST",
                           {"session": session, "chatId": chat_id}, timeout=10)
    if code not in (200, 201, 204):
        log(f"startTyping returned {code} (non-fatal)", "WARN")
    time.sleep(max(1.0, min(duration_sec, 30.0)))  # cap single typing burst at 30s
    waha_request(f"{waha_url}/api/stopTyping", api_key, "POST",
                 {"session": session, "chatId": chat_id}, timeout=10)


def mark_seen(waha_url: str, api_key: str, session: str, chat_id: str) -> None:
    """Mark chat as read first (recommended by WAHA docs)."""
    waha_request(f"{waha_url}/api/sendSeen", api_key, "POST",
                 {"session": session, "chatId": chat_id}, timeout=10)


# ---------------------------------------------------------------------------
# Cooldown / state
# ---------------------------------------------------------------------------

def load_sent_state() -> dict:
    f = STATE_DIR / "sent.json"
    if f.exists():
        try:
            return json.loads(f.read_text())
        except Exception:
            return {}
    return {}


def save_sent_state(state: dict) -> None:
    f = STATE_DIR / "sent.json"
    f.write_text(json.dumps(state, indent=2))


def under_hour_cap(state: dict, phone: str) -> bool:
    """Has this contact received < MAX_MSGS_PER_CONTACT_PER_HOUR in the last hour?"""
    now = time.time()
    recent = [t for t in state.get(phone, {}).get("sent_at", []) if now - t < 3600]
    return len(recent) < MAX_MSGS_PER_CONTACT_PER_HOUR


def record_sent(state: dict, phone: str) -> dict:
    state.setdefault(phone, {"sent_at": []})
    state(phone)["sent_at"].append(time.time()) if False else None  # type: ignore
    state[phone].setdefault("sent_at", []).append(time.time())
    # Trim history older than 24h
    now = time.time()
    state[phone]["sent_at"] = [t for t in state[phone]["sent_at"] if now - t < 86400]
    return state


def state_(state: dict, phone: str):
    """Helper because of the awkward one-liner above."""
    return state.setdefault(phone, {"sent_at": []})


def _hash_text(text: str) -> str:
    import hashlib
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:16]


def known_chats(waha_url: str, api_key: str, session: str) -> set:
    """Set of chatIds that have messaged us first (warm). Mirrors waha.sh
    `known_chats`: /api/chats plus /api/contacts/all filtered to isMyContact.
    Cached KNOWN_TTL_S. An empty lookup means the call failed — keep the prior
    cache rather than declaring every customer a stranger (fail-safe, not
    fail-cold)."""
    if KNOWN_CACHE.exists() and (time.time() - KNOWN_CACHE.stat().st_mtime) < KNOWN_TTL_S:
        return {l for l in KNOWN_CACHE.read_text().splitlines() if l.strip()}
    ids = set()
    for path, contacts in ((f"{waha_url}/api/chats?session={session}&limit=500", False),
                           (f"{waha_url}/api/contacts/all?session={session}&limit=500", True)):
        try:
            code, data = waha_request(path, api_key, "GET", timeout=30)
        except Exception:
            continue
        if code != 200 or not isinstance(data, list):
            continue
        for row in data:
            if not isinstance(row, dict):
                continue
            if contacts and not row.get("isMyContact"):
                continue
            cid = row.get("id")
            if isinstance(cid, dict):
                cid = cid.get("_serialized")
            if cid:
                ids.add(str(cid))
    KNOWN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    if ids:
        KNOWN_CACHE.write_text("\n".join(sorted(ids)))
        return ids
    # lookup returned nothing usable — keep previous cache, never assume cold
    if KNOWN_CACHE.exists():
        return {l for l in KNOWN_CACHE.read_text().splitlines() if l.strip()}
    return set()


def blast_guard(waha_url: str, api_key: str, session: str, chat_id: str, text: str,
                blast_ack: bool):
    """The three brakes from waha.sh `pace_and_check`, now on the broadcast path,
    sharing SEND_LOG so neither tool can be used to bypass the other. Returns
    (ok, reason). ok=False means HOLD this send (caller skips, does not POST)."""
    SEND_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not SEND_LOG.exists():
        SEND_LOG.touch()
    rows = []
    for ln in SEND_LOG.read_text().splitlines():
        p = ln.split("\t")
        rows.append(p if len(p) >= 4 else p + [""] * (4 - len(p)))
    now = int(time.time())
    h = _hash_text(text)
    warm = known_chats(waha_url, api_key, session)
    cold = "1" if (warm and chat_id not in warm) else "0"

    # 0. consecutive strangers — the pattern that bans fastest
    if cold == "1":
        streak = 0
        for r in rows:
            streak = streak + 1 if r[3] == "1" else 0
        streak += 1
        if streak >= COLD_THRESHOLD and not blast_ack:
            return False, ("cold-streak", streak)

    # 1. identical text to many distinct chats — WhatsApp reads sameness, not volume
    distinct = {r[1] for r in rows if len(r) > 2 and r[2] == h and r[1] != chat_id}
    if len(distinct) >= BLAST_THRESHOLD and not blast_ack:
        return False, ("identical-fanout", len(distinct))

    # 2. min-gap floor — sleep rather than refuse (make the safe thing default)
    if rows:
        try:
            last = int(rows[-1][0])
            gap = now - last
            if gap < MIN_GAP_S:
                time.sleep(MIN_GAP_S - gap)
        except (ValueError, IndexError):
            pass

    # all checks passed — record intent (parity with waha.sh:204) then proceed
    with open(SEND_LOG, "a") as f:
        f.write(f"{int(time.time())}\t{chat_id}\t{h}\t{cold}\n")
    return True, ("ok", int(cold))


# ---------------------------------------------------------------------------
# Planning + risk assessment
# ---------------------------------------------------------------------------

def estimate_spam_risk(n_contacts: int, account_age_days: int, opted_in_pct: float,
                       templates_count: int) -> str:
    """Soft spam-risk estimator. Returns low/moderate/high/block."""
    score = 0
    if account_age_days < 7:
        score += 3
    elif account_age_days < 30:
        score += 1
    if n_contacts > DAILY_CAP_NEW_ACCOUNT and account_age_days < 30:
        score += 3
    elif n_contacts > DAILY_CAP_WARMED_30D and account_age_days < 90:
        score += 2
    elif n_contacts > DAILY_CAP_ESTABLISHED:
        score += 1
    if opted_in_pct < 0.5:
        score += 3
    elif opted_in_pct < 0.8:
        score += 1
    if templates_count < 2:
        score += 2
    if score >= 7: return "block"
    if score >= 4: return "high"
    if score >= 2: return "moderate"
    return "low"


def plan_broadcast(contacts: list, account_age_days: int, templates_count: int) -> BroadcastPlan:
    opted = [c for c in contacts if c.opt_in]
    skipped_no_optin = [c for c in contacts if not c.opt_in]
    skipped_blacklist = []  # placeholder for future blacklist matching

    n = len(opted)
    opted_in_pct = (n / len(contacts)) if contacts else 0
    risk = estimate_spam_risk(n, account_age_days, opted_in_pct, templates_count)

    avg_delay = (DELAY_MIN + DELAY_MAX) / 2 + 6
    est_minutes = int((n * avg_delay) / 60)

    return BroadcastPlan(
        contacts=opted,
        skipped_no_optin=skipped_no_optin,
        skipped_blacklist=skipped_blacklist,
        estimated_minutes=est_minutes,
        daily_cap_risk=risk,
    )


# ---------------------------------------------------------------------------
# Contacts + templates loading
# ---------------------------------------------------------------------------

def load_contacts_csv(path: str) -> list:
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            phone = (row.get("phone") or row.get("Phone") or "").strip()
            if not phone:
                continue
            # normalize: digits only, keep leading country code
            phone = "".join(c for c in phone if c.isdigit() or c == "+").lstrip("+")
            opt = (row.get("opt_in") or row.get("OptIn") or "").strip().lower()
            out.append(Contact(
                phone=phone,
                name=(row.get("name") or row.get("Name") or "").strip(),
                opt_in=opt in ("yes", "true", "1", "y"),
                opt_in_source=(row.get("opt_in_source") or "").strip(),
                labels=[l.strip() for l in (row.get("labels") or "").split(",") if l.strip()],
            ))
    return out


def load_templates(path: str) -> list:
    """One template per line, blank lines ignored, {name} placeholder supported."""
    with open(path, encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]


# ---------------------------------------------------------------------------
# Main broadcast loop
# ---------------------------------------------------------------------------

def check_halt() -> bool:
    """True when anything has pressed the stop button — this skill's or another's.

    Reads the shared switch when available (which also covers the legacy paths and
    fails closed on an unreadable switch). Falls back to the legacy file so a broken
    shared layer is never *worse* than the behaviour this replaced.
    """
    if _HALT_LIB is not None:
        try:
            return _HALT_LIB.is_halted()
        except Exception:  # noqa: BLE001
            return True  # cannot tell -> treat as halted; see shared/lib/halt.py
    return HALT_FILE.exists()


def review_copy(rendered: list[tuple[str, str]]) -> int:
    """
    Read the messages the way the recipient will, before any of them go out.

    Stage-2/3 evidence for each thing this catches: thirteen promo messages
    shipped with no price at all (customers must reply "berapa kak?", so the
    promo *creates* work); "launching, Tanpa Nama!" and "Selamat siang !"
    reached real recipients; a customer was addressed as "628223300107" twice
    in one sentence.

    Advisory only. It prints what is wrong and returns the count — it never
    blocks a send, because a checker that stops someone contacting customers
    is a checker that gets switched off.
    """
    if copycheck is None or not rendered:
        return 0
    prof = profile_lib.load() if profile_lib else None

    problems: dict[str, list[str]] = {}
    for who, msg in rendered:
        for f in copycheck.check(msg, prof, is_promo=True, name=who):
            if f.level == "FAIL":
                problems.setdefault(f.code, []).append(f"{who}: {f.msg}")

    if not problems:
        return 0

    print("\n  ── Cek isi pesan " + "─" * 43)
    if prof is None:
        print("  (profil usaha belum ada, jadi cek 'cuma kamu yang bisa bilang' dilewati)")
    for code, hits in problems.items():
        print(f"  ✗ {len(hits)} pesan — {hits[0].split(': ', 1)[1]}")
        for h in hits[:2]:
            print(f"      · {h.split(': ', 1)[0]}")
        if len(hits) > 2:
            print(f"      · +{len(hits) - 2} lagi")
    print("  Ini catatan, bukan larangan. Kalau tetap mau kirim, kirim aja.")
    print("  " + "─" * 58)
    return sum(len(v) for v in problems.values())


def broadcast(args) -> int:
    contacts = load_contacts_csv(args.contacts)
    templates = load_templates(args.templates)

    if not contacts:
        fatal("No contacts loaded from CSV.")
    if not templates:
        fatal("No templates loaded.")

    plan = plan_broadcast(contacts, args.account_age_days, len(templates))

    print(f"\n{'='*60}")
    print(f"WAHA BROADCAST PLAN")
    print(f"{'='*60}")
    print(f"Contacts total:     {len(contacts)}")
    print(f"  Opted-in:         {len(plan.contacts)}")
    print(f"  No opt-in (skip): {len(plan.skipped_no_optin)}")
    print(f"Message templates: {len(templates)} (rotation)")
    print(f"Est. duration:     ~{plan.estimated_minutes} min")
    print(f"Spam risk:         {plan.daily_cap_risk.upper()}")
    print(f"{'='*60}\n")

    # ---- Soft warnings (non-blocking) ----
    if plan.daily_cap_risk == "block":
        soft_warn("Spam risk = BLOCK. Refusing to proceed even with --i-confirm-optin. "
                  "Reduce list size, get more opt-ins, or age the account.")
        return 2
    if plan.daily_cap_risk in ("high", "moderate"):
        soft_warn(f"Spam risk = {plan.daily_cap_risk.upper()}. Consider: fewer contacts, "
                  "more message variants, longer delays, or split into multiple days.")
    if len(plan.skipped_no_optin) > 0:
        soft_warn(f"{len(plan.skipped_no_optin)} contacts have NO opt-in flag and will be SKIPPED. "
                  "Cold outreach to non-opted-in contacts is the #1 ban trigger. "
                  "Only message people who asked to hear from you.")
    if len(templates) < 3:
        soft_warn(f"Only {len(templates)} templates. WhatsApp flags identical messages across "
                  "recipients. Use 5+ variants with different wording + {name} personalization.")
    if args.account_age_days < 7:
        soft_warn(f"Account is only {args.account_age_days} days old. New numbers are extremely "
                  "fragile. Consider a 7-day warm-up (manual conversations) before any broadcast.")

    # Render every message exactly as it will be sent, so merge failures and
    # priceless promos are visible before the first one goes out rather than
    # after the ninth.
    rendered = [(c.name or c.phone, humanize_message(templates[i % len(templates)], c))
                for i, c in enumerate(plan.contacts, 1)]

    if not args.i_confirm_optin:
        print("\nDRY RUN — no messages will be sent.")
        print("To actually send, re-run with --i-confirm-optin.\n")
        for i, (who, msg) in enumerate(rendered[:10], 1):
            print(f'  [{i}] {who}: "{msg[:80]}{"..." if len(msg) > 80 else ""}"')
        if len(rendered) > 10:
            print(f"  ... +{len(rendered)-10} more")
        review_copy(rendered)
        return 0

    review_copy(rendered)

    # ---- Confirmation gate ----
    if not args.yes:
        print(f"\nAbout to send {len(plan.contacts)} messages via WAHA.")
        confirm = input(f"Type the session name '{args.session}' to confirm: ").strip()
        if confirm != args.session:
            print("Confirmation did not match session name. Aborting.")
            return 1

    # ---- Execute ----
    state = load_sent_state()
    sent_count = 0
    skipped_cooldown = 0
    errors = []
    skipped_hold = 0

    log(f"Starting broadcast to {len(plan.contacts)} contacts on session '{args.session}'")
    log(f"Halt file: {HALT_FILE} (touch it to emergency-stop)")

    for i, contact in enumerate(plan.contacts, 1):
        if check_halt():
            log(f"HALT file detected — stopping at contact {i-1}.", "WARN")
            break

        if not under_hour_cap(state, contact.phone):
            log(f"  [{i}] {contact.phone}: over per-hour cap, skipping", "SKIP")
            skipped_cooldown += 1
            continue

        chat_id = f"{contact.phone}@c.us"
        template = templates[i % len(templates)]
        msg = humanize_message(template, contact)

        # Brakes shared with waha.sh (cold-outreach + identical-text + min-gap).
        # These used to live only on send-text; the broadcast path bypassed
        # them and got numbers banned (a recorded finding).
        ok, reason = blast_guard(args.waha_url, args.api_key, args.session,
                                 chat_id, msg, args.blast_ack)
        if not ok:
            why, n = reason
            if why == "cold-streak":
                log(f"  [{i}] {contact.phone}: HOLD — nomor ke-{n} berturut-turut "
                    f"yang belum pernah chat duluan. Selingi balasan ke pelanggan "
                    f"lama, atau --blast-ack kalau sudah paham risikonya. Belum dikirim.", "HOLD")
            else:
                log(f"  [{i}] {contact.phone}: HOLD — teks yang sama sudah ke {n} "
                    f"nomor berbeda. Tambah variasi kalimat, atau --blast-ack. "
                    f"Belum dikirim.", "HOLD")
            skipped_hold += 1
            continue

        # Anti-ban sequence: seen -> typing -> delay -> stop -> send
        try:
            mark_seen(args.waha_url, args.api_key, args.session, chat_id)
            delay = randomized_delay(msg_len=len(msg))
            if args.typing:
                do_typing_indicator(args.waha_url, args.api_key, args.session, chat_id,
                                    duration_sec=delay * 0.6)
            else:
                time.sleep(delay)

            code, resp = waha_request(
                f"{args.waha_url}/api/sendText",
                args.api_key, "POST",
                {"session": args.session, "chatId": chat_id, "text": msg},
                timeout=30,
            )

            # WAHA answers 201 Created on POST /api/sendText, not 200. Testing
            # against a mock built to WAHA's documented responses caught this:
            # every successful send fell into the `else` and was logged as an
            # error, so a completely successful broadcast reported
            # "Sent: 0 / Errors: 6" — and, far worse, record_sent() and
            # save_sent_state() never ran. Send history and the per-contact
            # hourly cap were never written to disk, so re-running the same
            # broadcast messaged everyone a second time with no cap in force.
            # That is the exact double-send this file exists to prevent.
            if code in (200, 201):
                sent_count += 1
                state = record_sent(state, contact.phone)
                save_sent_state(state)
                _ledger("sent", who=contact.name or contact.phone,
                        what=msg[:60], channel="wa")
                log(f"  [{i}/{len(plan.contacts)}] sent -> {contact.phone} ({contact.name or '?'})")
            elif code == 463:
                log(f"  [{i}] HTTP 463 — SHADOW RESTRICTION detected. "
                    "Halting broadcast. DO NOT restart/logout. Wait 24h.", "BAN")
                soft_warn("WhatsApp has shadow-restricted this number (error 463). "
                          "STOP all outreach to new contacts. The restriction lifts automatically. "
                          "DO NOT restart, logout, or re-pair the session.")
                break
            else:
                log(f"  [{i}] {contact.phone}: HTTP {code} — {resp}", "ERR")
                errors.append((contact.phone, code, resp))

        except URLError as e:
            log(f"  [{i}] {contact.phone}: network error {e}", "ERR")
            errors.append((contact.phone, "network", str(e)))

        # Batch pause every 20 messages
        if i % 20 == 0 and i < len(plan.contacts):
            batch_pause = random.uniform(DELAY_LONG_BATCH_MIN, DELAY_LONG_BATCH_MAX)
            log(f"  Batch pause: {int(batch_pause)}s (anti-burst)")
            time.sleep(batch_pause)

    print(f"\n{'='*60}")
    print(f"BROADCAST COMPLETE")
    print(f"{'='*60}")
    print(f"Sent:              {sent_count}")
    print(f"Held by brakes:    {skipped_hold}  (cold-outreach/identical-text; --blast-ack to release)")
    print(f"Skipped (cooldown):{skipped_cooldown}")
    print(f"Errors:            {len(errors)}")
    if errors:
        for ph, code, body in errors[:5]:
            print(f"  - {ph}: {code} {str(body)[:80]}")
    print(f"{'='*60}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--waha-url", required=True, help="WAHA base URL")
    p.add_argument("--api-key", required=True, help="WAHA X-Api-Key")
    p.add_argument("--session", required=True, help="WAHA session name")
    p.add_argument("--contacts", required=True, help="CSV: phone,name,opt_in,opt_in_source,labels")
    p.add_argument("--templates", required=True, help="TXT: one message template per line")
    p.add_argument("--account-age-days", type=int, default=30,
                   help="How old is the WhatsApp account? (affects daily cap)")
    p.add_argument("--blast-ack", action="store_true",
                   help="acknowledge cold-outreach/identical-text risk; releases the holds")
    p.add_argument("--typing", action="store_true", default=True,
                   help="Send typing indicator before each message (humanize)")
    p.add_argument("--no-typing", action="store_false", dest="typing")
    p.add_argument("--i-confirm-optin", action="store_true",
                   help="All contacts in CSV have explicitly opted in. Without this flag, dry-run.")
    p.add_argument("--yes", action="store_true", help="Skip interactive confirmation")
    args = p.parse_args()

    # Graceful SIGINT
    def sigint_handler(sig, frame):
        log("Interrupted by user — halting cleanly.", "WARN")
        sys.exit(130)
    signal.signal(signal.SIGINT, sigint_handler)

    sys.exit(broadcast(args))


if __name__ == "__main__":
    main()
