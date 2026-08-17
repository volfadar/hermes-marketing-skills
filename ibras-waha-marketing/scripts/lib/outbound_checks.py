#!/usr/bin/env python3
"""
outbound_checks.py — the promise / regulated-claim checks, for WhatsApp.

Why this file exists, and why it is a near-copy rather than an import: these
checks were written in `ibras-email-marketing/scripts/lib/mailbox.py`, and for a while that
was the only place they lived. Evaluation showed what that costs.

Two sessions, two different models, same seeded WhatsApp inbox. Both sent:

    "Halo Ratna, aman kok buat asam lambung."          → no disclaimer
    "pesanan berikutnya gue kasih gratis ongkir"       → no hold, owner never saw it

Neither was a model failure in the usual sense. `waha.sh send-text` is a curl
wrapper; there was nothing to fail. The brakes were one directory away, on the
channel where messages are *rarer and more deliberate*, while the channel where
a small business actually talks to customers all day had none.

WhatsApp deserves them more, not less. The volume is higher, the register is
looser, and the penalty for a bad automated send is a blocked number that takes
every order with it.

Kept standalone (stdlib only, no cross-skill import) because the two skills are
installed independently — `ibras-waha-marketing` must work when `ibras-email-marketing` is
absent. `scripts/doctor.sh` checks the two lexicons have not drifted apart.

    python3 outbound_checks.py --text "kami kembalikan uangnya"
    python3 outbound_checks.py --file pesan.txt --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# --- promises made on the owner's behalf -----------------------------------
# Written to survive rewording. A model that meets the gate and paraphrases past
# it has done something worse than sending the promise: it sent the promise and
# believes it complied. One did exactly that — rewrote "0,5%" as "setengah
# persen", pushed the send through nine seconds later, and reported that it had
# "changed a word and sent it safely".
BINDING_PATTERNS = [
    (r"\brefund\b"
     r"|(kembalikan|dikembalikan|mengembalikan|pengembalian|balikin|dibalikin)"
     r"[^.\n]{0,30}(uang|dana|biaya|pembayaran|duit|nominal)"
     r"|(uang|dana|biaya|pembayaran|duit)[^.\n]{0,30}"
     r"(kembalikan|dikembalikan|mengembalikan|pengembalian|kembali|balik)"
     r"|dikembalikan (penuh|sepenuhnya|100)", "refund / uang kembali"),
    (r"\bgratis\b|cuma-cuma|tanpa biaya|free ongkir|gratis ongkir|bebas ongkir",
     "sesuatu digratiskan"),
    (r"\bdiskon\b|potongan harga|\bpromo\b\s*\d"
     r"|(diskon|potongan|korting|cashback|off)[^.\n]{0,25}\d+\s*%"
     r"|\d+\s*%[^.\n]{0,25}(diskon|potongan|korting|cashback|off)", "diskon / potongan harga"),
    (r"garansi|jaminan|dijamin|menjamin"
     # Penjual solo menulis "saya/aku jamin", bukan "kami jamin". Pola lama
     # ditulis dengan suara perusahaan, jadi janji paling mungkin dari
     # pengguna yang skill ini memang tuju justru lolos. Ditemukan oleh
     # shared/tests/test_outbound.py.
     r"|\b(kami|saya|aku|gue|gua)\s+jamin(in)?\b"
     r"|\bjaminin\b", "garansi / jaminan"),
    (r"ganti rugi|kompensasi|kami ganti", "ganti rugi"),
    (r"tempo \d|termin \d|bayar (belakangan|nanti)|jatuh tempo", "termin pembayaran"),
    (r"pasti (sampai|tiba|dikirim)|dijamin sampai|besok (pasti )?sampai"
     r"|hari ini (pasti )?sampai|paling telat \d", "janji waktu kirim"),
    (r"kirim ulang|kami kirimkan ulang|dikirim ulang", "kirim ulang gratis"),
]

# --- claims that must carry a note -----------------------------------------
# Kept byte-identical to skill-ibras-email-marketing/scripts/lib/mailbox.py — the two
# skills install separately so this cannot be imported, and silent drift
# between them is how a phrase gets gated on email and waved through on
# WhatsApp. test-parity.py compares these strings and fails on any diff.
REGULATED_CLAIM = {
    "health": r"(aman|sehat|bagus|cocok|ramah|lembut|rendah asam|tidak (ber)?bahaya|"
              r"nggak (ber)?bahaya|gak (ber)?bahaya|menyembuhkan|mengobati|meredakan|"
              r"membantu)\b[^.\n]{0,60}"
              r"(lambung|maag|gerd|asam|diabetes|kolesterol|darah|jantung|diet|"
              r"kesehatan|kondisi|penyakit|hamil|anak)"
              r"|(lambung|maag|gerd|asam lambung|diabetes)[^.\n]{0,60}\b(aman|tidak masalah|"
              r"nggak masalah|gak masalah|boleh|ramah|cocok)"
              r"|(banyak|beberapa|banyak sekali)\s+(pelanggan|customer|pembeli|orang)"
              r"[^.\n]{0,80}(lambung|maag|gerd|tanpa keluhan|nggak masalah|"
              r"gak masalah|tidak masalah|aman)"
              r"|(aman|tidak berbahaya|nggak (ber)?bahaya|gak (ber)?bahaya)"
              r"[^.\n]{0,30}(diminum|dikonsumsi|dimakan|konsumsi)",
    "finance": r"(pasti|dijamin|guaranteed)[^.\n]{0,40}(untung|profit|balik modal|cuan)"
               r"|(untung|profit|roi|return)[^.\n]{0,30}\d+\s*%"
               r"|(pph|ppn|pbb|pajak|spt|npwp|tarif|omzet|peredaran bruto)"
               r"[^.\n]{0,60}(\d+[.,]?\d*\s*%|\d+\s*(jt|juta|m\b|miliar|milyar))"
               r"|(\d+[.,]?\d*\s*%|\d+\s*(jt|juta|m\b|miliar|milyar))"
               r"[^.\n]{0,60}(pph|ppn|pajak|spt|final|tarif|omzet)"
               r"|(masih (bisa|boleh)|tidak (kena|wajib)|nggak (kena|wajib)|gak (kena|wajib)|"
               r"bebas|tidak perlu bayar)[^.\n]{0,50}(pajak|pph|ppn|spt|lapor)"
               r"|\d+[.,]?\d*\s*%\s*[x×*]\s*(rp\.?\s*)?\d",
    "legal": r"(tidak akan|nggak akan|gak akan|pasti tidak)[^.\n]{0,40}"
             r"(kena|dituntut|denda|sanksi|pidana|masalah hukum)"
             r"|(legal|sah|aman)[^.\n]{0,30}(secara hukum|di mata hukum)"
             r"|(denda|sanksi|bunga)[^.\n]{0,40}"
             r"(\d+[.,]?\d*\s*%|\d+\s*(bulan|tahun|jt|juta)|rp\.?\s*\d[\d.,]*)"
             r"|(pidana|penjara|kurungan)[^.\n]{0,40}\d+\s*(bulan|tahun)"
             r"|pasal\s*\d+[a-z]?\b[^.\n]{0,30}(uu|undang|kup|ite|pdp|perpajakan)",
}
DISCLAIMERS = {
    "health": "Catatan: ini info umum, bukan saran medis. Untuk kondisi kesehatan "
              "pribadi, sebaiknya tanya ke dokter dulu ya.",
    "finance": "Catatan: ini bukan saran keuangan. Angka bisa berbeda tiap orang.",
    "legal": "Catatan: ini bukan nasihat hukum. Untuk kasus spesifik, konsultasi "
             "ke ahlinya ya.",
}

ALREADY_DISCLAIMED = ("bukan saran medis", "tenaga medis", "tanya ke dokter",
                      "konsultasi", "konsultasikan", "ke dokter",
                      "bukan saran keuangan", "bukan nasihat hukum")


def find_binding(text: str) -> list[tuple[str, str]]:
    out = []
    for pat, label in BINDING_PATTERNS:
        m = re.search(pat, text, re.I)
        if m:
            start = max(0, m.start() - 40)
            out.append((label, "…" + text[start:m.end() + 40].replace("\n", " ").strip() + "…"))
    return out


def find_regulated(text: str) -> str | None:
    for kind, pat in REGULATED_CLAIM.items():
        if re.search(pat, text, re.I):
            return kind
    return None


def apply_disclaimer(text: str) -> tuple[str, str | None]:
    """Append the required note. No flag removes this."""
    kind = find_regulated(text)
    if not kind:
        return text, None
    if any(m in text.lower() for m in ALREADY_DISCLAIMED):
        return text, None
    return text.rstrip() + "\n\n" + DISCLAIMERS[kind], kind


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--text")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    text = a.text if a.text else (open(a.file, encoding="utf-8").read() if a.file else "")
    if not text:
        ap.error("need --text or --file")

    binding = find_binding(text)
    body, kind = apply_disclaimer(text)

    if a.json:
        print(json.dumps({"binding": [{"label": l, "quote": q} for l, q in binding],
                          "regulated": kind, "body": body}, ensure_ascii=False))
        return 3 if binding else 0

    if kind:
        print(f"DISCLAIMER::{kind}")
        print(body)
    else:
        print(body)
    if binding:
        for label, quote in binding:
            print(f"BINDING::{label}::{quote}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
