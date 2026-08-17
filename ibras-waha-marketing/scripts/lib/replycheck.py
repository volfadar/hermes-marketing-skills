#!/usr/bin/env python3
"""
replycheck.py — inspect what Hermes is about to say to the owner.

Rationale: a rule shipped as *code* holds even on the cheapest model
(disclaimer append, binding gate, pacing floor, cold-outreach brake). A rule
shipped as *prose* fails under load — "max 80 kata", "halve the next turn if
they say kepanjangan", "never claim a check you didn't run" each failed
verbatim in recorded sessions. This moves four of those prose rules into code.

Checks:
  LENGTH     over the ceiling → compress. Median turn was 136 words for the
             cheapest model against a 9-word question.
  HALVE      previous owner turn said "kepanjangan"/"ga sempet baca" → this
             turn is capped at half. One model went 161 → 564 words immediately
             after being told "waduh panjang bgt".
  JARGON     opt-in, IMAP, chatId, endpoint, cron, UID, "session WORKING".
             The word *opt-in* alone stalled one attendee for 11 of 15 turns.
  CLAIMED    says it checked / sent / saved something. Verified against the
             command log. Three sessions said "saya cek belum ada setup WAHA"
             with the config sitting on disk; one said "inbox bersih" with 14
             unread; one reported a safety hold with zero POSTs on the wire.

The last one is the reason this file exists. A model does not reliably
distinguish what it *intended* from what it *did*; prose cannot fix that and
code can.

Usage (in a skill script, before emitting):
    python3 replycheck.py --text "$REPLY" --log ~/.hermes/state/commands.log
    python3 replycheck.py --text "$REPLY" --last-user-turn "kepanjangan"

Exit 0 clean · 1 findings present · 2 usage. Never rewrites silently: it
prints what to fix, because a reply the owner never sees cannot be repaired.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_MAX_WORDS = int(os.environ.get("HERMES_MAX_WORDS", "80"))
HARD_MAX_WORDS = int(os.environ.get("HERMES_HARD_MAX_WORDS", "120"))

CONFUSION = re.compile(
    r"\b(kepanjangan|panjang bgt|panjang banget|ga sempet baca|gak sempet baca|"
    r"nggak sempet baca|ga ngerti|gak ngerti|nggak ngerti|bingung|pusing|"
    r"maksudnya gimana|apa itu|gimana maksudnya|ribet|kelamaan|lama amat)\b", re.I)

JARGON = {
    "opt-in": "yang pernah beli atau chat duluan",
    "opt in": "yang pernah beli atau chat duluan",
    "optin": "yang pernah beli atau chat duluan",
    "imap": "kotak masuk email",
    "smtp": "pengiriman email",
    "app password": "kode khusus dari Google",
    "api key": "kunci sambungan",
    "endpoint": "alamat sambungan",
    "chatid": "nomor chat",
    "cron": "jadwal otomatis",
    "uid": "nomor email",
    "session working": "sambungannya nyala",
    "rate limit": "batas kirim",
    "threshold": "batas",
    "disclaimer": "catatan tambahan",
    "binding": "janji yang mengikat",
    "--binding-ack": "",
    "--blast-ack": "",
    "--confirm": "",
    "dry-run": "coba dulu tanpa kirim",
    "payload": "isi pesan",
    "webhook": "sambungan otomatis",
    "fromme": "",
    "json": "",
    "yaml": "",
    "regex": "",
}

# "I checked / I sent / I saved" — each needs an act on the record.
CLAIM_PATTERNS = [
    ("check", re.compile(
        r"\b(sudah|udah|saya|aku)?\s?(cek|ngecek|mengecek|periksa|baca|membaca|liat|lihat)\b"
        r"[^.!?\n]{0,40}\b(inbox|chat|kontak|email|pesan|semua|setup|config|koneksi)\b", re.I)),
    ("send", re.compile(
        r"\b(udah|sudah)\s+(ke)?kirim|terkirim|udah dikirim|sudah dikirim|"
        r"saya kirim(kan)?|aku kirim(in)?\b", re.I)),
    ("save", re.compile(r"\b(udah|sudah)\s+(saya|aku)?\s?(simpan|disimpan|kesimpen|tersimpan|catat)\b", re.I)),
    ("clean", re.compile(r"\b(inbox|chat)\w*\s+(udah|sudah)\s+(bersih|kosong|beres)\b", re.I)),
]

# What counts as proof, per claim kind, when scanning the command log.
PROOF = {
    "check": re.compile(r"\b(chats|messages|contacts|scan|list|fetch|status|GET)\b", re.I),
    "send":  re.compile(r"\b(send-text|sendText|POST|broadcast|smtp|reply|respond)\b", re.I),
    "save":  re.compile(r"\b(write|save|>|tee|faq\.yaml|profile\.yaml)\b", re.I),
    "clean": re.compile(r"\b(archive|seen|read|delete|move)\b", re.I),
}


class Finding:
    def __init__(self, level, code, msg, fix=""):
        self.level, self.code, self.msg, self.fix = level, code, msg, fix

    def __str__(self):
        mark = {"FAIL": "✗", "WARN": "!"}.get(self.level, "·")
        return f"  {mark} [{self.code}] {self.msg}" + (f"\n      → {self.fix}" if self.fix else "")


def read_log(path: str | None) -> str:
    """Whatever the skill recorded doing this turn. Missing log = fail open."""
    if not path:
        return ""
    try:
        p = Path(path)
        if not p.is_file():
            return ""
        text = p.read_text(encoding="utf-8", errors="replace")
        return text[-20000:]
    except Exception:
        return ""


def check(text: str, *, last_user_turn: str = "", log: str = "",
          max_words: int = DEFAULT_MAX_WORDS) -> list[Finding]:
    out: list[Finding] = []
    words = [w for w in re.split(r"\s+", text.strip()) if w]
    n = len(words)

    cap = max_words
    if last_user_turn and CONFUSION.search(last_user_turn):
        cap = max(25, max_words // 2)
        if n > cap:
            out.append(Finding(
                "FAIL", "halve",
                f"dia baru bilang nggak kebaca, giliran ini {n} kata (batas {cap})",
                "potong separuh. Jawabannya di kalimat pertama, sisanya buang."))
    if n > HARD_MAX_WORDS:
        out.append(Finding("FAIL", "length",
                           f"{n} kata — di atas batas keras {HARD_MAX_WORDS}",
                           "satu jawaban, satu pertanyaan. Sisanya simpan buat giliran depan."))
    elif n > cap:
        out.append(Finding("WARN", "length", f"{n} kata (target {cap})"))

    low = text.lower()
    hits = [(j, alt) for j, alt in JARGON.items() if j in low]
    if hits:
        worst = hits[0]
        out.append(Finding(
            "FAIL" if len(hits) > 1 else "WARN", "jargon",
            "istilah yang dia nggak tahu: " + ", ".join(j for j, _ in hits[:4]),
            (f"'{worst[0]}' → '{worst[1]}'" if worst[1] else f"buang '{worst[0]}' dari jawaban")))

    for kind, pat in CLAIM_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        if not log:
            out.append(Finding("WARN", f"claim:{kind}",
                               f"ngaku '{m.group(0).strip()}' tapi nggak ada catatan perintahnya",
                               "jalankan dulu, baru lapor"))
        elif not PROOF[kind].search(log):
            out.append(Finding("FAIL", f"claim:{kind}",
                               f"ngaku '{m.group(0).strip()}' — nggak ada di catatan perintah "
                               "giliran ini",
                               "jangan pernah lapor hasil pemeriksaan yang belum dijalankan"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Periksa jawaban Hermes sebelum dikirim ke pemilik usaha.")
    ap.add_argument("--text", help="isi jawaban; kalau kosong, dibaca dari stdin")
    ap.add_argument("--last-user-turn", default="", help="pesan terakhir dari pemiliknya")
    ap.add_argument("--log", default=os.environ.get("HERMES_COMMAND_LOG", ""),
                    help="catatan perintah yang benar-benar dijalankan giliran ini")
    ap.add_argument("--max-words", type=int, default=DEFAULT_MAX_WORDS)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    text = a.text if a.text is not None else sys.stdin.read()
    if not text.strip():
        return 2

    found = check(text, last_user_turn=a.last_user_turn,
                  log=read_log(a.log), max_words=a.max_words)

    if a.json:
        print(json.dumps([{"level": f.level, "code": f.code, "msg": f.msg, "fix": f.fix}
                          for f in found], ensure_ascii=False))
    else:
        if not found:
            print("  ✓ jawaban lolos")
        for f in found:
            print(f)
    return 1 if any(f.level == "FAIL" for f in found) else 0


if __name__ == "__main__":
    sys.exit(main())
