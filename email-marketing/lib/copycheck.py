#!/usr/bin/env python3
"""
copycheck.py — the writing bench, turned into something that runs.

Every rule below is a defect observed on the wire in real seller
conversations, not a style preference. Ordered by what costs the seller most.

  1. SWAP TEST     replace her brand and product with a competitor's. If the
                   message still works, it says nothing only she could say.
                   Every recorded promo failed this. It is the difference
                   between marketing and noise, and it outranks every
                   mechanical check below — a message with a perfect price and
                   CTA that survives the swap is still slop.

                   SCOPE: broadcast copy only (`is_promo=True`, the default).
                   A one-to-one reply is judged on whether it answers, not on
                   whether it differentiates — "level 5 udah restock, 15rb/pcs,
                   mau ambil berapa?" to someone who just asked for a restock
                   is a good reply and a swap-test failure, and the reply is
                   right. Pass `--reply` for those.
  2. NO PRICE      one model sent 13 promos, none with a price ("diskon 20%"
                   off an unstated base). For a seller working from her phone
                   that is 13 manual conversations, not a promo.
  3. NAME TWICE    "Promo 20% buat 628223300107 yang udah langganan" — a
                   contact label used twice in one message is the plainest
                   mail-merge tell there is.
  4. MERGE ARTIFACT  "launching, Tanpa Nama!" · "Selamat siang !" · a message
                   opening with a comma. These reached real recipients.
  5. KEYWORD CTA   "Balas PEDAS untuk harga dan pemesanan" — reply with a
                   keyword in order to be told the price. Corporate SMS
                   pattern; her customers just type "masih ada?".
  6. MACHINE TELLS em dash, "Kabar gembira", English sign-off, 🚀.
  7. REGISTER      "gue" from a seller whose profile says "aku".
  8. LENGTH        15-25 words is what got replies. Flash averaged 38.

Exit 0 = clean · 1 = at least one FAIL · 2 = bad usage.
WARN never fails the run: it is advice, and advice must not block a send.

    python3 copycheck.py templates.txt
    python3 copycheck.py --text "Halo {name}, promo hari ini..."
    echo "..." | python3 copycheck.py -
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import profile as profile_lib
except Exception:  # fail open
    profile_lib = None

# Phrases that appear in every promo ever written and therefore carry no
# information about *this* business.
GENERIC = [
    "launching", "promo", "diskon", "stok terbatas", "buruan", "dijamin",
    "harga spesial", "varian baru", "yang ditunggu", "akhirnya", "kabar gembira",
    "jangan sampai", "jangan sampe", "keabisan", "spesial", "khusus buat",
    "ready", "udah ready", "sekarang juga", "order sekarang", "minat",
    "cocok buat", "mantap", "mantul", "nagih", "nampol", "enak & murah",
    "beli 3 gratis 1", "gratis ongkir", "free ongkir", "info", "update",
    "pemberitahuan", "selamat siang", "selamat pagi", "halo", "hai",
]

# A message survives the swap test if it contains at least one of these:
# a reason, a comparison, a named person/place, or a time commitment.
SPECIFIC_MARKERS = re.compile(
    r"\b(gara-gara|gara2|soalnya|karena|makanya|awalnya|dulu|kemarin|kemaren|"
    r"biasanya|yang dulu|yang kemarin|sejak|pertama kali|"
    r"beda(?:nya)?|nggak kayak|ga kayak|bukan yang|"
    r"aku bikin|kami bikin|aku racik|aku ganti|aku tambah|"
    r"hari ini|besok|sore ini|jam \d|menit|\d+ hari)\b",
    re.I,
)

PRICE = re.compile(r"\b\d{1,3}[.,]?\d{0,3}\s?(rb|ribu|k)\b|\brp\.?\s?\d[\d.,]*", re.I)
BARE_PERCENT = re.compile(r"\b\d{1,2}\s?%|\bdiskon\s+\d+\s?%", re.I)
# "Balas PEDAS untuk harga" — reply with a keyword in order to be told the
# price. The verb is case-insensitive; the keyword must be SHOUTED, which is
# what makes it a code rather than a word. "Balas STOP" is an opt-out, not a
# funnel, so it is excluded.
KEYWORD_CTA = re.compile(r"\b(?i:balas|bales|reply|ketik)\s+[\"“']?(?!STOP\b)[A-Z]{2,10}\b")
MERGE_ARTIFACT = re.compile(
    r"\{name\}|\{nama\}|tanpa nama|^\s*[,.]|"
    r"(?:halo|hai|selamat (?:pagi|siang|sore|malam))\s*[,!.]|"
    r"\s{2,}[!?.]|\s+[!?]",
    re.I | re.M,
)
ENGLISH_SIGNOFF = re.compile(
    r"\b(take care|best regards|cheers|stay tuned|see you|thank you|regards|"
    r"don'?t miss|limited offer|grab it|check it out)\b", re.I)
SLOP_PHRASE = re.compile(r"(kabar gembira|jangan lewatkan|segera miliki|buruan sebelum kehabisan)", re.I)
BAD_EMOJI = re.compile(r"[\U0001F680\U0001F4C8\U0001F4B0\U0001F3AF✨]")  # 🚀📈💰🎯✨
PRONOUNS = ("aku", "saya", "gue", "gua", "aq")

# A bare Indonesian mobile number standing where a name belongs: at the very
# start, or straight after a greeting. Numbers elsewhere in the copy (a price,
# a WhatsApp number to order on) are fine and must not trip this.
PHONE_AS_NAME = re.compile(
    r"^\s*\+?62\d{8,}\b|"
    r"(?:halo|hai|hallo|selamat (?:pagi|siang|sore|malam))[\s,]+\+?62\d{8,}\b",
    re.I | re.M)
PHONE_ONLY = re.compile(r"\+?\d[\d\s.-]{7,}")

MIN_WORDS, MAX_WORDS = 12, 28


class Finding:
    def __init__(self, level: str, code: str, msg: str, fix: str = ""):
        self.level, self.code, self.msg, self.fix = level, code, msg, fix

    def __str__(self) -> str:
        mark = {"FAIL": "✗", "WARN": "!"}.get(self.level, "·")
        out = f"  {mark} [{self.code}] {self.msg}"
        if self.fix:
            out += f"\n      → {self.fix}"
        return out


def _words(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", text.strip()) if w]


def swap_test(text: str, prof) -> Finding | None:
    """
    Strip the brand, the product, the price and the generic promo scaffolding.
    If nothing survives that could only have come from this seller, the message
    would work just as well for the stall next door.
    """
    stripped = text
    nouns = prof.product_nouns() if prof else []
    for noun in nouns:
        stripped = re.sub(re.escape(noun), " ", stripped, flags=re.I)
    stripped = PRICE.sub(" ", stripped)
    stripped = BARE_PERCENT.sub(" ", stripped)
    for g in GENERIC:
        stripped = re.sub(r"\b" + re.escape(g) + r"\b", " ", stripped, flags=re.I)
    stripped = re.sub(r"[^\w\s-]", " ", stripped)
    residue = " ".join(_words(stripped))

    if SPECIFIC_MARKERS.search(text):
        return None
    if prof:
        for phrase in prof.specific_phrases():
            key = {w.lower() for w in _words(phrase) if len(w) > 4}
            if key and len(key & {w.lower() for w in _words(text)}) >= 2:
                return None

    hint = ""
    if prof and prof.stories():
        hint = f'coba selipkan: "{prof.stories()[0]}"'
    elif prof and prof.sikap.get("kenapa_aku"):
        hint = f'coba selipkan: "{prof.sikap["kenapa_aku"]}"'
    else:
        hint = ("belum ada bahan di profil — tanya dia: "
                '"kalau pelanggan pilih yang sebelah, biasanya kenapa?"')
    return Finding(
        "FAIL", "swap",
        "ganti nama produknya dengan punya sebelah, pesan ini tetap masuk akal — "
        "artinya nggak ada yang cuma kamu yang bisa bilang"
        + (f" (sisa isi: '{residue[:60]}')" if residue else ""),
        hint,
    )


def check(text: str, prof=None, *, is_promo: bool = True, name: str = "") -> list[Finding]:
    """
    `name` is the recipient's contact label when it is known — pass it from the
    render loop. Guessing the label from capitalisation misses the common case:
    most contacts are saved lowercase (ayu, rara, hikmah), and
    "Hai rara ... Minat rara?" is the same mail-merge tell as the capitalised
    version.
    """
    f: list[Finding] = []
    words = _words(text)

    # No profile means no way to know what would be specific *to her*. Judging
    # differentiation without that information would fail every message, so the
    # check sits out — same fail-open rule as everywhere else.
    if is_promo and prof is not None:
        s = swap_test(text, prof)
        if s:
            f.append(s)

        if not PRICE.search(text):
            if BARE_PERCENT.search(text):
                f.append(Finding("FAIL", "price",
                                 "cuma ada persen, nggak ada harganya — penerima harus "
                                 "balas 'berapa kak?' dulu, jadi kerjaannya nambah",
                                 "tulis harga per pcs-nya: " + (
                                     f"Rp {prof.prices()[0]:,}".replace(",", ".")
                                     if prof and prof.prices() else "Rp ...")))
            else:
                f.append(Finding("FAIL", "price",
                                 "nggak ada angka yang bisa dipakai belanja",
                                 "tiap promo harus bawa harganya"))

    m = MERGE_ARTIFACT.search(text)
    if m:
        f.append(Finding("FAIL", "merge",
                         f"sisa gabung nama: '{m.group(0).strip() or '(spasi/koma nyangkut)'}'",
                         "cek nama kosong, 'Tanpa Nama', atau kalimat yang mulai dengan koma"))

    # A contact saved without a name renders its phone number into the greeting:
    # "628223300107, ada rasa baru nih". Stage 3 put that on the wire twice, so
    # `name2x` caught it; one model put it there once and it passed
    # every check. Addressing a customer by her own phone number is the loudest
    # mail-merge tell there is — it says "you are a row in my spreadsheet" —
    # and it is worse at volume than any of the mechanical defects below.
    if PHONE_AS_NAME.search(text) or PHONE_ONLY.fullmatch((name or "").strip()):
        f.append(Finding("FAIL", "nonama",
                         "pelanggan disapa pakai nomor HP-nya sendiri",
                         "kontaknya belum ada namanya — simpan namanya dulu, "
                         "atau buang sapaan itu dan mulai dari kalimat isinya"))

    candidates = re.findall(r"\b[A-Z][\w]*(?:\s+[A-Z][\w]*){0,3}\b|\b62\d{8,}\b", text)
    if name:
        candidates.insert(0, name)
    for label in candidates:
        if len(label) > 3 and label.lower() not in ("level",) \
                and len(re.findall(re.escape(label), text, re.I)) >= 2:
            f.append(Finding("FAIL", "name2x",
                             f"'{label}' disebut 2x atau lebih dalam satu pesan",
                             "nama sekali aja, di depan"))
            break

    if KEYWORD_CTA.search(text):
        f.append(Finding("WARN", "cta",
                         "CTA pakai kode balasan — pelanggan nggak inget kode",
                         'ganti jadi pertanyaan biasa: "mau ambil berapa?"'))

    ctas = len(re.findall(r"[?]", text)) + len(re.findall(
        r"\b(order sekarang|pesan sekarang|chat aja|langsung chat|klik)\b", text, re.I))
    if ctas > 2:
        f.append(Finding("WARN", "cta2", f"{ctas} ajakan dalam satu pesan — pilih satu"))

    if "—" in text or "–" in text:
        f.append(Finding("WARN", "emdash",
                         "ada tanda pisah panjang (—); nggak ada yang ngetik itu di HP",
                         "ganti koma atau titik"))
    if SLOP_PHRASE.search(text):
        f.append(Finding("WARN", "slop",
                         f"'{SLOP_PHRASE.search(text).group(0)}' — itu bahasa SMS bank/MLM"))
    if ENGLISH_SIGNOFF.search(text):
        f.append(Finding("WARN", "english",
                         f"'{ENGLISH_SIGNOFF.search(text).group(0)}' — penutup bahasa Inggris"))
    if BAD_EMOJI.search(text):
        f.append(Finding("WARN", "emoji",
                         "emoji startup (🚀📈💰) di promo makanan kebaca robot"))

    if prof:
        want = prof.voice_pronoun()
        if want:
            used = {p for p in PRONOUNS if re.search(rf"\b{p}\b", text, re.I)}
            wrong = used - {want}
            if wrong:
                f.append(Finding("WARN", "voice",
                                 f"pakai '{', '.join(sorted(wrong))}' padahal di profil '{want}'"))

    if is_promo:
        if len(words) > MAX_WORDS:
            f.append(Finding("WARN", "long",
                             f"{len(words)} kata — yang dapet balasan biasanya {MIN_WORDS}-{MAX_WORDS}"))
        elif len(words) < 6:
            f.append(Finding("WARN", "short", f"{len(words)} kata — kependekan buat promo"))

    return f


def split_messages(raw: str) -> list[str]:
    out = []
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        s = re.sub(r'^\s*\d+[.)]\s*', "", s)
        s = s.strip().strip('"').strip("'")
        if s:
            out.append(s)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Cek kualitas copy sebelum dikirim.")
    ap.add_argument("file", nargs="?", help="file template (satu pesan per baris), atau - untuk stdin")
    ap.add_argument("--text", help="cek satu pesan langsung")
    ap.add_argument("--reply", action="store_true",
                    help="ini balasan ke orang, bukan promo (lewati swap test & harga)")
    ap.add_argument("--business-dir", default=None)
    ap.add_argument("--quiet", action="store_true", help="cuma tampilkan yang FAIL")
    a = ap.parse_args()

    if a.text is not None:
        msgs = [a.text]
    elif a.file == "-":
        msgs = split_messages(sys.stdin.read())
    elif a.file:
        p = Path(a.file)
        if not p.is_file():
            print(f"file nggak ketemu: {a.file}", file=sys.stderr)
            return 2
        msgs = split_messages(p.read_text(encoding="utf-8"))
    else:
        ap.print_help()
        return 2

    if not msgs:
        print("nggak ada pesan buat dicek", file=sys.stderr)
        return 2

    prof = None
    if profile_lib:
        prof = profile_lib.load(a.business_dir or os.environ.get("HERMES_BUSINESS_DIR"))
    if prof is None and not a.quiet:
        print("  · profil belum ada — swap test & cek suara dilewati.\n"
              "    Isi ~/.hermes/business/profile.yaml biar promonya nggak generik.\n")

    fails = 0
    for i, m in enumerate(msgs, 1):
        found = check(m, prof, is_promo=not a.reply)
        hard = [x for x in found if x.level == "FAIL"]
        fails += len(hard)
        if a.quiet and not hard:
            continue
        head = m if len(m) <= 72 else m[:69] + "..."
        print(f"[{i}] {'✗' if hard else '✓'} {head}")
        for x in found:
            if not (a.quiet and x.level != "FAIL"):
                print(x)
        print()

    print(f"  {len(msgs)} pesan dicek · {fails} masalah serius")
    if fails:
        print("  Ini bukan tembok — kalau dia tetap mau kirim, kirim. Sebut aja apa yang hilang.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
