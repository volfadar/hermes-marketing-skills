#!/usr/bin/env python3
"""
Autoresponder — tiered, bounded, and always able to hand the conversation back.

This is the part that can talk to your customers without you. It is deliberately
boring: pattern matching over a FAQ file you wrote, a confidence number you can
read, and five triggers that stop it. No hidden judgement.

THE POSITION (see references/tiers.md for the long version)

  Automation is not the problem. Automation *that keeps going when it doesn't
  know* is the problem. A bot that answers "jam buka jam berapa?" for the 400th
  time is fine. A bot that guesses at a refund request, invents a delivery date,
  or lets a stranger rewrite its instructions is how a business loses a customer
  it will never hear from again.

  So: this tool will do what you tell it, including things it advises against.
  It warns once, offers a better shape, then complies. Two things it will not do,
  because they harm someone who is not in the conversation and did not choose:

    1. It never treats the content of an inbound email as an instruction.
       Prompt-injection attempts are flagged and escalated, never answered —
       in every mode, including --mode blind.
    2. It never strips a regulated-topic disclaimer (health, money, legal)
       from an answer that carries one.

MODES

  --mode draft   (default)  Writes replies into your Drafts folder. Nothing is
                            sent. You open Gmail, skim, hit send. Tier T3.
  --mode faq                Sends answers for FAQ hits above the confidence
                            threshold with no trigger fired. Everything else
                            gets a holding message and is escalated to you.
                            Tier T2 — the shape this skill recommends.
  --mode blind              Sends whatever is in --answers-file, no threshold.
                            "Full trusted." Requires --i-understand-blind-mode.
                            Loop protection, cooldown, caps, audit log, and the
                            two rules above still apply.

Usage:
  python3 autoresponder.py scan --limit 30
  python3 autoresponder.py simulate --text "kak, pesanan saya belum sampai"
  python3 autoresponder.py respond --mode draft --limit 10
  python3 autoresponder.py respond --mode faq --confirm
  python3 autoresponder.py log --today
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
import unicodedata
from datetime import datetime, time as dtime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mailbox as mb_lib   # noqa: E402  (same directory, intentional)

try:
    import yaml
except ImportError:
    print("Butuh PyYAML: pip3 install pyyaml", file=sys.stderr)
    sys.exit(1)


try:
    import ledger as ledger_lib   # shared layer, synced by shared/sync.sh
except Exception:
    ledger_lib = None


def _ledger(kind: str, **kw) -> None:
    """Best-effort bookkeeping. Never let a recap failure look like a send failure."""
    if ledger_lib is None:
        return
    try:
        ledger_lib.add(kind, **kw)
    except Exception:
        pass


BUSINESS_DIR = mb_lib.BUSINESS_DIR
FAQ_FILE = Path(os.environ.get("HERMES_FAQ_FILE", BUSINESS_DIR / "faq.yaml"))
STATE_FILE = mb_lib.STATE_DIR / "autoreply-state.json"
ESCALATION_LOG = BUSINESS_DIR / "escalations.jsonl"
HALT_FILE = mb_lib.HALT_FILE

# ---------------------------------------------------------------------------
# Defaults — every one of these is overridable in faq.yaml -> meta:
# ---------------------------------------------------------------------------

DEFAULTS = {
    "confidence_threshold": 0.75,
    "auto_reply_cooldown_hours": 12,
    "daily_auto_cap": 40,
    "business_hours": "",            # e.g. "08:00-21:00"; empty = always on
    "disclosure": "Dijawab otomatis oleh asisten. Kalau butuh orangnya langsung, "
                  "balas pesan ini — nanti saya yang jawab.",
    "holding_message": "Terima kasih sudah menghubungi. Pertanyaan ini saya teruskan ke "
                       "tim dan akan dijawab langsung oleh orangnya. Mohon tunggu ya.",
    "signature": "",
    "owner_name": "",
    "business": "",
}

# Disclaimers that cannot be removed. Non-negotiable #2 in the governance model:
# they protect the reader, who is not part of the owner's risk decision.
DISCLAIMERS = {
    "health": "Catatan: informasi ini bersifat edukasi umum, bukan diagnosis atau saran "
              "medis. Untuk kondisi kesehatan pribadi, konsultasikan ke tenaga medis.",
    "finance": "Catatan: ini bukan saran keuangan atau investasi. Angka bisa berbeda "
               "untuk situasi masing-masing orang.",
    "legal": "Catatan: ini bukan nasihat hukum. Untuk kasus spesifik, konsultasikan ke "
             "konsultan atau kuasa hukum.",
    "income": "Catatan: hasil setiap orang berbeda. Tidak ada jaminan pendapatan.",
}

# ---------------------------------------------------------------------------
# Handoff trigger lexicons (Bahasa Indonesia + English)
# ---------------------------------------------------------------------------

EMOTION_TERMS = [
    # ID
    "kecewa", "marah", "komplain", "keluhan", "protes", "parah", "buruk sekali",
    "tidak sesuai", "gak sesuai", "nggak sesuai", "rusak", "cacat", "salah kirim",
    "lama sekali", "lambat banget", "belum sampai", "penipuan", "tipu", "menipu",
    "bohong", "kapok", "tidak profesional", "mengecewakan", "minta ganti", "refund",
    "uang kembali", "lapor", "somasi", "viral", "review jelek", "bintang 1",
    # EN
    "disappointed", "angry", "frustrated", "unacceptable", "terrible", "worst",
    "scam", "fraud", "refund", "money back", "complaint", "lawyer", "legal action",
]

BINDING_TERMS = [
    # ID — anything that would create an obligation if answered wrongly
    "harga khusus", "harga spesial", "nego", "negosiasi", "diskon", "potongan harga",
    "garansi", "jaminan", "refund", "retur", "tukar barang", "kapan sampai",
    "pasti sampai", "dijamin", "kontrak", "mou", "invoice", "faktur", "termin",
    "pembayaran mundur", "tempo", "dp", "cicilan", "kerja sama", "reseller",
    "distributor", "keagenan", "eksklusif", "bisa kurang", "minta turun",
    # EN
    "discount", "special price", "warranty", "guarantee", "sla", "contract",
    "net 30", "payment terms", "exclusive", "partnership",
]

INJECTION_PATTERNS = [
    r"ignore (all |the |your )?(previous|prior|above|earlier) (instruction|prompt|rule)",
    r"abaikan (semua |seluruh )?(instruksi|perintah|aturan) (sebelumnya|di atas|kamu)",
    r"lupakan (semua )?(instruksi|perintah|aturan)",
    r"you are now (a|an|the)\b",
    r"kamu sekarang (adalah )?(seorang|sebuah)?\b.*(asisten|bot|ai)",
    r"(system|developer|assistant)\s*(prompt|message|role)\s*[:=]",
    r"</?(system|instruction|prompt)>",
    r"\[\[?\s*system\s*\]?\]",
    r"(reveal|show|print|repeat|tampilkan|tunjukkan) (your |the |semua )?(system )?"
    r"(prompt|instruction|instruksi|konfigurasi|config|api[_ ]?key|password)",
    r"act as (if|though) you",
    r"berpura-pura (kamu|anda)",
    r"do not (tell|inform|mention) (the )?(owner|human|user)",
    r"jangan (beritahu|kasih tahu|laporkan) (ke )?(pemilik|owner|admin)",
    r"send (all |the )?(emails?|data|contacts?) to\b",
    r"kirim (semua )?(email|data|kontak) ke\b",
]
INJECTION_RE = [re.compile(p, re.I) for p in INJECTION_PATTERNS]

# Senders you must never auto-reply to. A loop here fills two mailboxes overnight.
NOREPLY_RE = re.compile(
    r"(no[-_.]?reply|do[-_.]?not[-_.]?reply|donotreply|mailer[-_.]?daemon|postmaster|"
    r"bounce|notification|notifications|alerts?|automated|noreply)@", re.I)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def strip_quoted(body: str) -> str:
    """Drop the quoted history so a trigger word from last week's thread does not
    fire on today's message."""
    out = []
    for line in (body or "").splitlines():
        s = line.strip()
        if s.startswith(">"):
            continue
        if re.match(r"^-{2,}\s*(pesan|forwarded|original)", s, re.I):
            break
        if re.match(r"^(pada|on)\b.{0,80}\b(menulis|wrote):\s*$", s, re.I):
            break
        out.append(line)
    return "\n".join(out).strip()


# ---------------------------------------------------------------------------
# FAQ loading + matching
# ---------------------------------------------------------------------------

class FAQ:
    def __init__(self, path: Path):
        if not path.exists():
            mb_lib.fatal(
                f"FAQ belum ada di {path}.\n"
                "  Salin contohnya dulu:\n"
                "    mkdir -p ~/.hermes/business\n"
                "    cp templates/faq.example.yaml ~/.hermes/business/faq.yaml\n"
                "  Lalu isi dengan pertanyaan yang MEMANG sering masuk ke inbox kamu.\n"
                "  Jangan mengarang pertanyaan — buka inbox, hitung yang berulang.")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        self.meta = {**DEFAULTS, **(data.get("meta") or {})}
        self.entries = data.get("entries") or []
        for i, e in enumerate(self.entries):
            if not e.get("id"):
                mb_lib.fatal(f"entries[{i}] tidak punya 'id'.")
            if not e.get("patterns"):
                mb_lib.fatal(f"entry '{e['id']}' tidak punya 'patterns'.")
            if not e.get("answer"):
                mb_lib.fatal(f"entry '{e['id']}' tidak punya 'answer'.")

    def match(self, text: str) -> dict:
        """Explainable scoring. Returns best entry, score, runner-up and reasons."""
        norm = normalize(text)
        words = set(norm.split())
        scored = []
        for e in self.entries:
            hits, best = [], 0.0
            for pat in e["patterns"]:
                p = normalize(pat)
                if not p:
                    continue
                if p in norm:                      # exact phrase present
                    s = 1.0
                else:
                    toks = p.split()
                    overlap = sum(1 for t in toks if t in words)
                    s = 0.75 * (overlap / len(toks)) if toks else 0.0
                if s > 0.3:
                    hits.append((pat, round(s, 2)))
                best = max(best, s)
            if any(normalize(n) in norm for n in (e.get("must_not") or [])):
                best = 0.0
                hits = []
            if len(hits) > 1:
                best = min(1.0, best + 0.10)       # corroboration bonus
            scored.append({"entry": e, "score": round(best, 3), "hits": hits})
        scored.sort(key=lambda d: d["score"], reverse=True)
        top = scored[0] if scored else {"entry": None, "score": 0.0, "hits": []}
        second = scored[1] if len(scored) > 1 else {"entry": None, "score": 0.0}
        ambiguous = bool(top["entry"] and second["entry"]
                         and top["score"] > 0 and (top["score"] - second["score"]) < 0.15)
        hit = top["entry"] if top["score"] > 0 else None
        return {
            "id": hit["id"] if hit else None,
            "score": top["score"],
            "hits": top["hits"],
            "entry": hit,
            "runner_up": second["entry"]["id"] if (second["entry"] and second["score"] > 0) else None,
            "runner_up_score": second["score"],
            "ambiguous": ambiguous and top["score"] > 0,
        }


# ---------------------------------------------------------------------------
# Triggers
# ---------------------------------------------------------------------------

def find_terms(text: str, terms: list[str]) -> list[str]:
    norm = normalize(text)
    return [t for t in terms if normalize(t) in norm]


def find_injection(text: str) -> list[str]:
    return [rx.pattern for rx in INJECTION_RE if rx.search(text or "")]


def evaluate(msg: dict, faq: FAQ, self_address: str) -> dict:
    """Full triage of one message. Pure function — touches nothing."""
    body = strip_quoted(msg.get("body", ""))
    subject = msg.get("subject", "")
    text = f"{subject}\n{body}"

    # --- hard skips: never auto-reply to these at all ---
    skip = None
    sender = (msg.get("from") or "").lower()
    if not sender:
        skip = "pengirim kosong"
    elif sender == self_address.lower():
        skip = "email dari diri sendiri"
    elif NOREPLY_RE.search(sender):
        skip = "alamat no-reply"
    elif msg.get("auto_submitted") and msg["auto_submitted"].lower() != "no":
        skip = f"Auto-Submitted: {msg['auto_submitted']} (pesan otomatis)"
    elif msg.get("list_id") or msg.get("list_unsubscribe"):
        skip = "mailing list / newsletter"
    elif (msg.get("precedence") or "").lower() in ("bulk", "list", "junk"):
        skip = f"Precedence: {msg['precedence']}"

    match = faq.match(text)
    threshold = float(faq.meta["confidence_threshold"])

    triggers = []
    inj = find_injection(text)
    if inj:
        triggers.append({"type": "injection", "detail": inj[:3]})
    emo = find_terms(text, EMOTION_TERMS)
    if emo:
        triggers.append({"type": "emotion", "detail": emo[:5]})
    bind = find_terms(text, BINDING_TERMS)
    if bind:
        triggers.append({"type": "binding", "detail": bind[:5]})
    if not match["id"] or match["score"] <= 0.3:
        triggers.append({"type": "scope", "detail": "tidak ada FAQ yang cocok"})
    elif match["score"] < threshold:
        triggers.append({"type": "confidence",
                         "detail": f"{match['score']:.2f} < ambang {threshold:.2f}"})
    elif match["ambiguous"]:
        triggers.append({"type": "confidence",
                         "detail": f"ambigu: '{match['id']}' {match['score']:.2f} vs "
                                   f"'{match['runner_up']}' {match['runner_up_score']:.2f}"})

    entry_tier = (match["entry"] or {}).get("tier", "T2")
    if entry_tier == "T3":
        triggers.append({"type": "scope", "detail": "entry ini ditandai T3 di faq.yaml"})

    types = {t["type"] for t in triggers}
    if skip:
        action, tier = "skip", "—"
    elif "injection" in types:
        action, tier = "escalate_only", "T1"      # never answered, in any mode
    elif triggers:
        action, tier = "holding_and_escalate", "T3"
    else:
        action, tier = "auto_answer", "T2"

    return {
        "uid": msg.get("uid"),
        "from": msg.get("from"),
        "from_name": msg.get("from_name"),
        "subject": subject,
        # Kept so a reply can be built without going back to the server.
        "message_id": msg.get("message_id", ""),
        "references": msg.get("references", ""),
        "skip_reason": skip,
        "faq_id": match["id"],
        "confidence": match["score"],
        "matched_patterns": match["hits"],
        "runner_up": match["runner_up"],
        "runner_up_score": match["runner_up_score"],
        "ambiguous": match["ambiguous"],
        "triggers": triggers,
        "trigger_types": sorted(types),
        "action": action,
        "tier": tier,
        "answer": (match["entry"] or {}).get("answer", ""),
        "disclaimer": (match["entry"] or {}).get("disclaimer"),
    }


# ---------------------------------------------------------------------------
# Rate limiting / state
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def cooldown_ok(state: dict, sender: str, hours: float) -> bool:
    last = state.get("senders", {}).get(sender.lower(), 0)
    return (datetime.now(timezone.utc).timestamp() - last) > hours * 3600


def today_count(state: dict) -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return state.get("daily", {}).get(today, 0)


def record_send(state: dict, sender: str) -> dict:
    now = datetime.now(timezone.utc)
    state.setdefault("senders", {})[sender.lower()] = now.timestamp()
    today = now.strftime("%Y-%m-%d")
    state.setdefault("daily", {})
    state["daily"][today] = state["daily"].get(today, 0) + 1
    cutoff = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    state["daily"] = {k: v for k, v in state["daily"].items() if k >= cutoff}
    return state


def within_business_hours(spec: str) -> bool:
    if not spec:
        return True
    try:
        a, b = spec.split("-")
        start = dtime(*map(int, a.strip().split(":")))
        end = dtime(*map(int, b.strip().split(":")))
    except Exception:
        return True
    now = datetime.now().time()
    return start <= now <= end if start <= end else (now >= start or now <= end)


def escalate(item: dict, note: str, notify_cmd: str | None) -> None:
    BUSINESS_DIR.mkdir(parents=True, exist_ok=True)
    row = {"ts": datetime.now(timezone.utc).isoformat(), "channel": "email",
           "uid": item["uid"], "from": item["from"], "subject": item["subject"],
           "triggers": item["trigger_types"], "detail": item["triggers"], "note": note}
    with ESCALATION_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    # Also on the day's ledger, so the end-of-session recap can say who is
    # still waiting instead of leaving it in a log nobody opens. Clear it with
    # `python3 lib/handoff.py answer <n> --text "..."`, which files the answer
    # into faq.yaml so the same question stops escalating.
    _ledger("waiting", who=str(item.get("from", "")).split("@")[0],
            what=str(item.get("subject", ""))[:60], channel="email")
    if notify_cmd:
        text = (f"[EMAIL {'/'.join(item['trigger_types']) or 'perlu perhatian'}] "
                f"{item['from']}: {item['subject'][:80]}")
        os.system(notify_cmd.replace("{msg}", shlex.quote(text)))


def apply_disclaimer(answer: str, kind: str | None) -> str:
    """Non-negotiable #2. There is no flag that removes this.

    `kind` arrives from the FAQ entry's optional `disclaimer:` key — which is to
    say, from whatever the agent remembered to type when it wrote the FAQ. In
    one recorded run the agent wrote three tax entries and gave none of them the
    key, so this answer auto-fired to a client with nothing attached:

        Untuk UMKM: omzet di bawah Rp 500 juta setahun bebas PPh final.
        Omzet Rp 500 juta sampai Rp 4,8 miliar kena PPh final UMKM setengah
        persen dari omzet…

    while the identical content sent through `mail.sh reply` carried a caveat,
    because that path reads the text instead of trusting a key. Same skill, same
    claim, two paths, one protected — the exact shape of every other failure this
    evaluation found. So read the text here too, and treat the FAQ key as a hint
    that can only add, never as the sole trigger.
    """
    kind = kind or mb_lib.find_regulated(answer)
    if not kind:
        return answer
    if any(m in answer.lower() for m in mb_lib.ALREADY_DISCLAIMED):
        return answer
    text = DISCLAIMERS.get(kind, DISCLAIMERS["health"])
    return answer if text in answer else answer.rstrip() + "\n\n" + text


def compose(item: dict, faq: FAQ, body_override: str | None = None) -> str:
    meta = faq.meta
    body = body_override if body_override is not None else item["answer"]
    body = apply_disclaimer(body, item.get("disclaimer"))
    parts = [body.rstrip()]
    if meta.get("disclosure"):
        parts.append("—\n" + meta["disclosure"].strip())
    if meta.get("signature"):
        parts.append(meta["signature"].strip())
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def gather(cfg, faq, args) -> list[dict]:
    """Fetch candidate messages and triage them."""
    items = []
    with mb_lib.Mailbox(cfg) as mb:
        mb.select("inbox")
        uids = mb.search(["UNSEEN"] if args.unread_only else ["ALL"])
        uids = uids[-args.limit:] if args.limit else uids
        for head in mb.headers(uids):
            full = mb.full(head["uid"])
            if not full:
                continue
            full.pop("_raw", None)
            items.append(evaluate(full, faq, cfg["EMAIL_ADDRESS"]))
    items.reverse()
    return items


def cmd_scan(args, cfg):
    faq = FAQ(FAQ_FILE)
    items = gather(cfg, faq, args)
    if args.json:
        print(json.dumps({"faq_file": str(FAQ_FILE), "threshold": faq.meta["confidence_threshold"],
                          "items": items}, ensure_ascii=False, indent=2))
        return 0

    counts = {}
    print(f"\n  FAQ: {FAQ_FILE}  ({len(faq.entries)} entri, ambang "
          f"{faq.meta['confidence_threshold']})\n")
    print(f"  {'UID':>7}  {'AKSI':<20} {'TIER':<5} {'CONF':>5}  {'FAQ':<16} PENGIRIM / SUBJECT")
    print(f"  {'-'*7}  {'-'*20} {'-'*5} {'-'*5}  {'-'*16} {'-'*40}")
    for it in items:
        counts[it["action"]] = counts.get(it["action"], 0) + 1
        who = (it["from_name"] or it["from"] or "?")[:22]
        print(f"  {it['uid']:>7}  {it['action']:<20} {it['tier']:<5} {it['confidence']:>5.2f}  "
              f"{(it['faq_id'] or '—'):<16} {who} — {it['subject'][:40]}")
        if it["skip_reason"]:
            print(f"           ↳ dilewati: {it['skip_reason']}")
        for t in it["triggers"]:
            print(f"           ↳ trigger {t['type']}: {t['detail']}")
    summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items())) or "kosong"
    print(f"\n  Ringkasan: {summary}")
    auto = counts.get("auto_answer", 0)
    total = len(items) or 1
    print(f"  {auto}/{len(items)} ({auto*100//total}%) bisa dijawab otomatis dengan FAQ sekarang.")
    if auto == 0 and items:
        print("  FAQ belum menutup apa pun di batch ini. Tambah entri dari pertanyaan nyata "
              "di atas, jangan dari tebakan.")
    print()
    return 0


def cmd_simulate(args, cfg):
    """Test one message against the FAQ without touching the mailbox."""
    faq = FAQ(FAQ_FILE)
    text = args.text or sys.stdin.read()
    fake = {"uid": "sim", "from": args.from_ or "orang@contoh.com", "from_name": "Simulasi",
            "subject": args.subject or "", "body": text, "auto_submitted": "", "list_id": "",
            "list_unsubscribe": "", "precedence": ""}
    item = evaluate(fake, faq, cfg["EMAIL_ADDRESS"])
    print(f"\n  Aksi:       {item['action']}  (tier {item['tier']})")
    print(f"  FAQ cocok:  {item['faq_id'] or '—'}   confidence {item['confidence']:.2f} "
          f"(ambang {faq.meta['confidence_threshold']})")
    if item["matched_patterns"]:
        print(f"  Pola kena:  {item['matched_patterns']}")
    if item["runner_up"]:
        print(f"  Kandidat 2: {item['runner_up']} ({item['runner_up_score']:.2f})"
              + ("   ← terlalu dekat, dianggap ambigu" if item["ambiguous"] else ""))
    for t in item["triggers"]:
        print(f"  Trigger:    {t['type']} → {t['detail']}")
    print("\n  Balasan yang akan dipakai:\n" + "-"*60)
    if item["action"] == "auto_answer":
        print(compose(item, faq))
    elif item["action"] == "escalate_only":
        print("(tidak ada — indikasi prompt injection. Diteruskan ke pemilik, tidak dijawab.)")
    else:
        print(faq.meta["holding_message"])
    print("-"*60 + "\n")
    return 0


def _blind_advisory(faq: FAQ) -> None:
    print("""
  ┌─ MODE BLIND (full trusted) ────────────────────────────────────────────┐
  │ Ini bisa dilakukan. Sebelum jalan, ini yang berubah:                    │
  │                                                                        │
  │  • Tidak ada ambang keyakinan. Jawaban dikirim apa adanya.              │
  │  • Kalau jawabannya salah, yang menanggung nama baik kamu, bukan tool.  │
  │  • Pelanggan yang merasa dijawab robot yang salah biasanya tidak        │
  │    komplain — mereka pergi diam-diam, dan kamu tidak pernah tahu.       │
  │                                                                        │
  │ Bentuk yang lebih aman (sama cepatnya untuk kamu):                      │
  │  1. --mode faq dengan ambang 0.75 → FAQ dijawab, sisanya naik ke kamu.  │
  │  2. --mode draft seminggu dulu → lihat apa yang akan dikirim, baru      │
  │     naikkan yang sudah terbukti benar ke --mode faq.                    │
  │                                                                        │
  │ Kalau tetap mau blind: silakan, ini keputusan kamu. Yang tetap jalan:   │
  │  injection tetap di-escalate, disclaimer tetap terpasang, semua kirim   │
  │  tetap tercatat di auto-log.jsonl, `emergency-halt.sh` tetap menghentikan.│
  └────────────────────────────────────────────────────────────────────────┘
""")


def cmd_respond(args, cfg):
    faq = FAQ(FAQ_FILE)
    meta = faq.meta

    if args.mode == "blind":
        _blind_advisory(faq)
        if not args.i_understand_blind_mode:
            print("  Tambahkan --i-understand-blind-mode untuk lanjut.\n")
            return 0
        if not args.answers_file:
            mb_lib.fatal("--mode blind butuh --answers-file "
                         "(JSON: [{\"uid\": \"123\", \"body\": \"...\"}, ...]) "
                         "yang berisi jawaban yang sudah kamu/Hermes tulis.")

    if mb_lib.is_halted():
        mb_lib.fatal("BERHENTI aktif — semua balasan otomatis dihentikan.\n"
                     + mb_lib.halt_hint())

    overrides = {}
    if args.answers_file:
        for row in json.loads(Path(args.answers_file).read_text(encoding="utf-8")):
            overrides[str(row["uid"])] = row["body"]

    state = load_state()
    cap = int(meta["daily_auto_cap"])
    sent_today = today_count(state)
    if args.mode != "draft" and sent_today >= cap:
        mb_lib.soft_warn(f"Sudah {sent_today} balasan otomatis hari ini (batas {cap}). "
                         "Naikkan daily_auto_cap di faq.yaml kalau memang mau lebih.")
        return 0

    open_now = within_business_hours(meta.get("business_hours", ""))
    items = gather(cfg, faq, args)
    acted = skipped = escalated = 0

    # Drafts need one IMAP connection for the whole batch, not one per message.
    draft_mb = None
    if args.mode == "draft" and args.confirm:
        draft_mb = mb_lib.Mailbox(cfg).__enter__()

    for it in items:
        uid, sender = it["uid"], it["from"] or ""
        if it["skip_reason"]:
            skipped += 1
            print(f"  – {uid} dilewati: {it['skip_reason']}")
            continue

        # Injection is never answered, in any mode. Non-negotiable #1.
        if "injection" in it["trigger_types"]:
            escalate(it, "indikasi prompt injection — tidak dijawab", args.notify_cmd)
            escalated += 1
            print(f"  ⚑ {uid} INJECTION dari {sender} — di-escalate, tidak dijawab")
            continue

        if args.mode != "draft" and not cooldown_ok(state, sender, float(meta["auto_reply_cooldown_hours"])):
            skipped += 1
            print(f"  – {uid} dilewati: {sender} sudah dapat balasan otomatis "
                  f"< {meta['auto_reply_cooldown_hours']} jam lalu")
            continue

        body_override = overrides.get(str(uid))
        if args.mode == "blind":
            if body_override is None:
                skipped += 1
                print(f"  – {uid} tidak ada jawaban di --answers-file")
                continue
            action = "auto_answer"
        elif args.mode == "faq":
            action = it["action"]
        else:  # draft
            action = "draft"

        if action == "auto_answer":
            text = compose(it, faq, body_override)
            ok = _send_reply(cfg, it, text, dry=not args.confirm)
            if ok and args.confirm:
                state = record_send(state, sender)
                save_state(state)
                mb_lib.audit({"action": "auto_reply", "mode": args.mode, "uid": uid,
                              "to": sender, "subject": it["subject"], "faq_id": it["faq_id"],
                              "confidence": it["confidence"], "tier": it["tier"], "ok": True})
            acted += 1
            print(f"  {'✓' if args.confirm else '·'} {uid} → {sender}  "
                  f"[{it['faq_id'] or 'override'} {it['confidence']:.2f}]")

        elif action == "holding_and_escalate":
            note = "di luar cakupan FAQ" if not open_now else "butuh keputusan manusia"
            if args.holding and args.confirm:
                _send_reply(cfg, it, compose({**it, "answer": meta["holding_message"],
                                              "disclaimer": None}, faq), dry=False)
                state = record_send(state, sender)
                save_state(state)
                mb_lib.audit({"action": "holding_message", "uid": uid, "to": sender,
                              "triggers": it["trigger_types"], "ok": True})
            escalate(it, note, args.notify_cmd)
            escalated += 1
            print(f"  ↑ {uid} escalate ({'/'.join(it['trigger_types'])}) — {sender}")

        else:  # draft
            text = compose(it, faq, body_override) if (it["answer"] or body_override) else ""
            if not text:
                escalate(it, "tidak ada draft otomatis — perlu ditulis manual", args.notify_cmd)
                escalated += 1
                print(f"  ↑ {uid} tidak ada FAQ — perlu kamu tulis sendiri ({sender})")
                continue
            _save_draft(draft_mb, cfg, it, text, dry=not args.confirm)
            acted += 1
            print(f"  {'✓' if args.confirm else '·'} draft {uid} → {sender} "
                  f"[{it['faq_id']} {it['confidence']:.2f}]")

    if draft_mb is not None:
        draft_mb.__exit__(None, None, None)

    print(f"\n  Selesai: {acted} ditindak, {escalated} di-escalate, {skipped} dilewati.")
    if not args.confirm:
        print("  (DRY RUN — belum ada yang benar-benar dikirim/disimpan. "
              "Tambahkan --confirm.)")
    if escalated:
        print(f"  Escalation tercatat di {ESCALATION_LOG}")
    print()
    return 0


def _reply_message(cfg, item: dict, text: str, auto: bool):
    """Build the reply from the triage record — no extra round trip to the server."""
    subject = item["subject"] or "(tanpa subject)"
    if not subject.lower().startswith("re:"):
        subject = "Re: " + subject
    return subject, mb_lib.build_message(
        cfg, [item["from"]], subject, text,
        reply_to_msg={"message_id": item.get("message_id", ""),
                      "references": item.get("references", "")},
        auto_replied=auto)


def _preview(label: str, item: dict, subject: str, text: str) -> None:
    print(f"      DRY RUN — {label} ke {item['from']}, subject '{subject}':")
    for line in text.splitlines()[:8]:
        print(f"        | {line}")


def _send_reply(cfg, item: dict, text: str, dry: bool) -> bool:
    subject, msg = _reply_message(cfg, item, text, auto=True)
    if dry:
        _preview("balasan", item, subject, text)
        return True
    ok, detail = mb_lib.smtp_send(cfg, msg)
    if not ok:
        print(f"      ✗ {detail}")
    else:
        _ledger("sent", who=str(item.get("from", "")).split("@")[0],
                what=str(item.get("subject", ""))[:60], channel="email")
    return ok


def _save_draft(mb, cfg, item: dict, text: str, dry: bool) -> bool:
    subject, msg = _reply_message(cfg, item, text, auto=False)
    if dry:
        _preview("draft", item, subject, text)
        return True
    return mb.append("drafts", msg, flags="\\Draft")


def cmd_log(args, cfg):
    path = mb_lib.AUDIT_LOG
    if not path.exists():
        print(f"  Belum ada log di {path}")
        return 0
    rows = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("channel") != "email":
            continue
        if args.today and not r.get("ts", "").startswith(today):
            continue
        rows.append(r)
    rows = rows[-args.limit:]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    print(f"\n  {len(rows)} entri terakhir dari {path}\n")
    for r in rows:
        who = r.get("to") or r.get("from") or "—"
        if isinstance(who, list):
            who = ", ".join(who)
        print(f"  {r['ts'][:19]}  {r.get('action','?'):<16} {str(who)[:32]:<32} "
              f"{str(r.get('subject',''))[:38]}")
    print()
    return 0


def cmd_validate(args, cfg):
    """Check faq.yaml before it goes anywhere near a customer."""
    faq = FAQ(FAQ_FILE)
    print(f"\n  {FAQ_FILE}: {len(faq.entries)} entri\n")
    problems = 0
    seen_patterns = {}
    for e in faq.entries:
        tier = e.get("tier", "T2")
        n_pat = len(e["patterns"])
        flag = ""
        if n_pat < 3:
            flag += "  ⚠ hanya %d pola — gampang meleset" % n_pat
            problems += 1
        if len(e["answer"]) < 30:
            flag += "  ⚠ jawaban sangat pendek"
            problems += 1
        for p in e["patterns"]:
            key = normalize(p)
            if key in seen_patterns and seen_patterns[key] != e["id"]:
                flag += f"  ⚠ pola '{p}' bentrok dengan entri '{seen_patterns[key]}'"
                problems += 1
            seen_patterns[key] = e["id"]
        print(f"  {e['id']:<20} {tier:<4} {n_pat:>2} pola  "
              f"{'disclaimer:' + e['disclaimer'] if e.get('disclaimer') else ''}{flag}")
    # cross-check: does any entry answer a binding question? that should be T3.
    for e in faq.entries:
        joined = " ".join(e["patterns"]) + " " + e["answer"]
        bind = find_terms(joined, BINDING_TERMS)
        if bind and e.get("tier") != "T3":
            print(f"\n  ⚠ '{e['id']}' menyentuh hal mengikat ({bind[:3]}) tapi tier-nya "
                  f"{e.get('tier','T2')}. Pertimbangkan tier: T3 supaya selalu jadi draft.")
            problems += 1
    print(f"\n  {'✓ tidak ada masalah' if not problems else f'{problems} hal untuk dicek'}\n")
    return 0


def main():
    p = argparse.ArgumentParser(prog="autoresponder.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("scan", help="triage inbox: apa yang bisa dijawab otomatis")
    sp.add_argument("--limit", type=int, default=25)
    sp.add_argument("--unread-only", action="store_true", default=True)
    sp.add_argument("--all", dest="unread_only", action="store_false")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_scan)

    sp = sub.add_parser("simulate", help="uji satu pesan tanpa menyentuh mailbox")
    sp.add_argument("--text")
    sp.add_argument("--subject")
    sp.add_argument("--from", dest="from_")
    sp.set_defaults(fn=cmd_simulate)

    sp = sub.add_parser("respond", help="bertindak atas inbox")
    sp.add_argument("--mode", choices=["draft", "faq", "blind"], default="draft")
    sp.add_argument("--limit", type=int, default=25)
    sp.add_argument("--unread-only", action="store_true", default=True)
    sp.add_argument("--all", dest="unread_only", action="store_false")
    sp.add_argument("--holding", action="store_true",
                    help="kirim pesan tunggu untuk yang di-escalate")
    sp.add_argument("--answers-file", help="JSON jawaban yang ditulis Hermes/kamu")
    sp.add_argument("--notify-cmd",
                    help="perintah shell untuk notifikasi escalation; {msg} diganti teks")
    sp.add_argument("--i-understand-blind-mode", action="store_true")
    sp.add_argument("--confirm", action="store_true")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_respond)

    sp = sub.add_parser("log", help="lihat catatan balasan otomatis")
    sp.add_argument("--today", action="store_true")
    sp.add_argument("--limit", type=int, default=40)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_log)

    sub.add_parser("validate", help="periksa faq.yaml").set_defaults(fn=cmd_validate)

    args = p.parse_args()
    cfg = mb_lib.load_config()
    mb_lib.STATE_DIR.mkdir(parents=True, exist_ok=True)
    sys.exit(args.fn(args, cfg))


if __name__ == "__main__":
    main()
