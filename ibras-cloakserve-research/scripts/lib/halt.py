#!/usr/bin/env python3
"""
halt.py — one stop button for every outbound path.

Before this file there were two kill switches, with two different env vars and two
different paths, and neither knew about the other:

    WAHA_HALT_FILE          -> /tmp/waha-broadcast-halt
    HERMES_EMAIL_HALT_FILE  -> /tmp/hermes-email-halt

Two problems, both real:

1. The owner who needs to stop everything at 10pm had to remember two commands, and
   stopping one did not stop the other. The moment someone reaches for a stop button
   is the moment they can remember the least.

2. `/tmp` does not survive a reboot. The autoresponder is designed to run on a
   schedule, so a halted system could quietly come back to life after a restart with
   nobody pressing resume. For a kill switch that is the wrong direction to fail in.

So: one file, in the business directory next to the other state that must survive
(`escalations.jsonl`, `faq.yaml`), carrying who stopped it and why.

    python3 halt.py on  --why "salah kirim ke grup" --who yuni
    python3 halt.py status
    python3 halt.py off

FAIL-CLOSED, on purpose. `ledger.py` and `handoff.py` fail open because a broken
recap must never stop someone answering a customer. This one is the opposite: if the
halt state cannot be determined, we report halted. A false stop costs a delay; a
false send costs messages to real people that cannot be recalled.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

BUSINESS_DIR = Path(os.environ.get("HERMES_BUSINESS_DIR") or
                    os.path.expanduser("~/.hermes/business"))

# The canonical switch. One file, every outbound path reads it.
HALT_FILE = Path(os.environ.get("HERMES_HALT_FILE", BUSINESS_DIR / "HALT"))

# Legacy switches stay honoured for reading, so an already-halted install does not
# silently resume the moment it upgrades. Nothing writes these any more.
LEGACY_FILES = [
    Path(os.environ.get("WAHA_HALT_FILE", "/tmp/waha-broadcast-halt")),
    Path(os.environ.get("HERMES_EMAIL_HALT_FILE", "/tmp/hermes-email-halt")),
]


def _read_state() -> dict | None:
    """Return the halt record, or None if not halted. Raises nothing."""
    for path in [HALT_FILE, *LEGACY_FILES]:
        try:
            if not path.exists():
                continue
        except OSError:
            # Cannot even stat the switch. Treat as halted — see module docstring.
            return {"when": "unknown", "who": "unknown",
                    "why": f"tidak bisa membaca {path} — dianggap BERHENTI",
                    "legacy": False, "unreadable": True}
        try:
            raw = path.read_text(encoding="utf-8").strip()
        except OSError:
            return {"when": "unknown", "who": "unknown",
                    "why": f"{path} ada tapi tidak terbaca — dianggap BERHENTI",
                    "legacy": path != HALT_FILE, "unreadable": True}
        if not raw:
            # An empty `touch`ed file is still a halt. The old scripts did exactly that.
            return {"when": "unknown", "who": "unknown", "why": "(tanpa alasan)",
                    "legacy": path != HALT_FILE}
        try:
            rec = json.loads(raw)
            if isinstance(rec, dict):
                rec.setdefault("when", "unknown")
                rec.setdefault("who", "unknown")
                rec.setdefault("why", "(tanpa alasan)")
                rec["legacy"] = path != HALT_FILE
                return rec
        except (ValueError, TypeError):
            pass
        # A plain timestamp, which is what the old email switch wrote.
        return {"when": raw, "who": "unknown", "why": "(tanpa alasan)",
                "legacy": path != HALT_FILE}
    return None


def is_halted() -> bool:
    """The single question every outbound path asks before it sends."""
    return _read_state() is not None


def state() -> dict | None:
    return _read_state()


def engage(why: str = "", who: str = "") -> Path:
    HALT_FILE.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "when": datetime.now().astimezone().isoformat(timespec="seconds"),
        "who": who or os.environ.get("USER", "unknown"),
        "why": why or "(tanpa alasan)",
    }
    HALT_FILE.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return HALT_FILE


def release() -> list[Path]:
    """Clear the canonical switch and any legacy ones, so `off` means off."""
    cleared = []
    for path in [HALT_FILE, *LEGACY_FILES]:
        try:
            if path.exists():
                path.unlink()
                cleared.append(path)
        except OSError:
            pass
    return cleared


def _cmd_on(args) -> int:
    path = engage(why=args.why or "", who=args.who or "")
    print(f"⛔ BERHENTI. Semua jalur keluar disetop: WhatsApp, email, dan job terjadwal.")
    print(f"   File : {path}")
    print(f"   Alasan: {args.why or '(tanpa alasan)'}")
    print()
    print("   Yang sedang berjalan berhenti di batas pesan berikutnya.")
    print("   Untuk jalan lagi:  python3 halt.py off")
    return 0


def _cmd_off(args) -> int:
    cleared = release()
    if not cleared:
        print("✓ Tidak sedang berhenti. Tidak ada yang perlu dicabut.")
        return 0
    print("✓ Berhenti dicabut. Jalur keluar boleh jalan lagi.")
    for p in cleared:
        print(f"   dihapus: {p}")
    return 0


def _cmd_status(args) -> int:
    rec = _read_state()
    if rec is None:
        print("✓ JALAN — tidak sedang berhenti.")
        print(f"  Switch: {HALT_FILE} (belum ada)")
        return 0
    print("⛔ SEDANG BERHENTI — tidak ada yang dikirim.")
    print(f"  Sejak  : {rec.get('when')}")
    print(f"  Oleh   : {rec.get('who')}")
    print(f"  Alasan : {rec.get('why')}")
    if rec.get("legacy"):
        print("  Catatan: ini switch lama (/tmp). Jalankan `halt.py off` lalu `on` lagi")
        print("           supaya pindah ke switch baru yang tahan reboot.")
    if rec.get("unreadable"):
        print("  Catatan: statusnya tidak terbaca, jadi dianggap BERHENTI (fail-closed).")
    print()
    print("  Jalan lagi: python3 halt.py off")
    return 1  # non-zero so a script can gate on it


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="halt.py",
        description="Satu tombol berhenti untuk semua jalur keluar (WA, email, job).")
    sub = ap.add_subparsers(dest="cmd")

    p_on = sub.add_parser("on", help="hentikan semua pengiriman sekarang")
    p_on.add_argument("--why", help="alasan singkat, supaya besok kamu ingat")
    p_on.add_argument("--who", help="siapa yang menghentikan")
    p_on.set_defaults(func=_cmd_on)

    p_off = sub.add_parser("off", help="cabut penghentian")
    p_off.set_defaults(func=_cmd_off)

    p_st = sub.add_parser("status", help="sedang berhenti atau tidak")
    p_st.set_defaults(func=_cmd_status)

    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        return _cmd_status(args)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
