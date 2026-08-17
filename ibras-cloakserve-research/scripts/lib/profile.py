#!/usr/bin/env python3
"""
profile.py — the one thing every marketing skill reads before it drafts.

Three layers, and each exists because a recorded failure needed it:

  FAKTA    prices, ongkir, jam buka, what can be promised.
           Without it a model invents — a "Rp 150.000/kg → Rp 135.000/kg,
           total kontrak Rp 12.150.000" quote out of nothing, or thirteen
           promo messages containing no price at all because it had none
           to put in.

  SIKAP    why this seller and not the stall next door, who it's for, what
           she promises every time, how she sounds. Facts stop fabrication;
           only stance stops slop. Every recorded promo survived the
           swap test (replace the product noun, message still works) because
           nobody had ever recorded an answer to "kenapa beli dari kamu".

  BATASAN  REFUSE / CAP / ACCESS / PERMISSION, in her own words. Lifted from
           skill-ibras-brand-strategy-coach, which had the right mechanism and no
           reader. A proposal violating a REFUSE is a failure however good it
           otherwise looks.

Everything here FAILS OPEN. A missing, unreadable, or half-written profile
must never stop someone answering a customer. `load()` returns None and the
caller carries on; that is the designed behaviour, not a degraded mode.

CLI:
    python3 profile.py show                 # one-screen summary
    python3 profile.py missing              # what the intake still needs
    python3 profile.py get fakta.jam_buka   # dotted lookup
    python3 profile.py check                # validate, exit 1 if malformed
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # fail open: no yaml means no profile, not a crash
    yaml = None

DEFAULT_DIR = os.environ.get("HERMES_BUSINESS_DIR") or os.path.expanduser(
    "~/.hermes/business"
)
PROFILE_NAME = "profile.yaml"

# Layer names are Indonesian on purpose — the file is read aloud to the owner
# during intake, and an English key is a word she has to skip over.
LAYERS = ("fakta", "sikap", "batasan")

SIKAP_FIELDS = ("kenapa_aku", "buat_siapa", "janji_tiap_kali", "ga_pernah")
BATASAN_KINDS = ("REFUSE", "CAP", "ACCESS", "PERMISSION")


def profile_path(base: str | os.PathLike | None = None) -> Path:
    return Path(base or DEFAULT_DIR) / PROFILE_NAME


class Profile:
    def __init__(self, data: dict, path: Path | None = None):
        self.data = data or {}
        self.path = path

    # ---- generic access ---------------------------------------------------
    def get(self, dotted: str, default=None):
        node = self.data
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    @property
    def meta(self) -> dict:
        return self.data.get("meta") or {}

    @property
    def fakta(self) -> dict:
        return self.data.get("fakta") or {}

    @property
    def sikap(self) -> dict:
        return self.data.get("sikap") or {}

    @property
    def batasan(self) -> dict:
        return self.data.get("batasan") or {}

    @property
    def jenis(self) -> str:
        """barang | jasa | reseller — the single branch the intake takes."""
        return str(self.meta.get("jenis") or "").strip().lower()

    # ---- FAKTA ------------------------------------------------------------
    def products(self) -> list[dict]:
        p = self.fakta.get("produk")
        return [x for x in p if isinstance(x, dict)] if isinstance(p, list) else []

    def prices(self) -> list[int]:
        """Every number a customer could act on. Used by the copy checker."""
        out = []
        for prod in self.products():
            h = prod.get("harga")
            if isinstance(h, (int, float)):
                out.append(int(h))
        for special in self.fakta.get("harga_khusus") or []:
            if isinstance(special, dict) and isinstance(special.get("harga"), (int, float)):
                out.append(int(special["harga"]))
        ongkir = self.fakta.get("ongkir")
        if isinstance(ongkir, dict):
            out += [int(v) for v in ongkir.values() if isinstance(v, (int, float))]
        return out

    def product_nouns(self) -> list[str]:
        """Nouns the swap test replaces. Brand + product names + their words."""
        nouns: set[str] = set()
        for key in ("usaha", "pemilik"):
            val = self.meta.get(key)
            if val:
                nouns.add(str(val))
                nouns.update(w for w in str(val).split() if len(w) > 2)
        for prod in self.products():
            nama = prod.get("nama")
            if nama:
                nouns.add(str(nama))
                nouns.update(w for w in str(nama).split() if len(w) > 2)
        return sorted(nouns, key=len, reverse=True)

    def may_promise(self) -> list[str]:
        v = self.fakta.get("yang_boleh_dijanjikan")
        return [str(x) for x in v] if isinstance(v, list) else []

    def must_ask_first(self) -> list[str]:
        v = self.fakta.get("yang_harus_tanya_dulu")
        return [str(x) for x in v] if isinstance(v, list) else []

    def is_pre_approved(self, text: str) -> bool:
        """A promise she already decided shouldn't cost her a turn to re-approve."""
        low = (text or "").lower()
        return any(p.lower() in low for p in self.may_promise() if p.strip())

    # ---- SIKAP ------------------------------------------------------------
    def voice_pronoun(self) -> str:
        return str((self.sikap.get("suara_saya") or {}).get("sapaan") or "").strip().lower()

    def voice_samples(self) -> list[str]:
        v = (self.sikap.get("suara_saya") or {}).get("contoh_chat")
        return [str(x) for x in v] if isinstance(v, list) else []

    def stories(self) -> list[str]:
        v = self.sikap.get("cerita")
        return [str(x) for x in v] if isinstance(v, list) else []

    def specific_phrases(self) -> list[str]:
        """
        The material that lets a message survive the swap test: her reasons,
        her promise, her stories. A promo containing none of this is
        interchangeable with any competitor's.
        """
        borrowed = _example_values()
        out: list[str] = []
        for f in SIKAP_FIELDS:
            val = self.sikap.get(f)
            if isinstance(val, str) and val.strip():
                out.append(val.strip())
        out += [s for s in self.stories() if s.strip()]
        # A sentence lifted from the example is not hers, so it cannot be what
        # makes a message hers. Letting it count would hand a free pass to
        # exactly the copy the swap test exists to catch.
        return [s for s in out if s not in borrowed]

    # ---- BATASAN ----------------------------------------------------------
    def constraints(self, kind: str) -> list[str]:
        v = self.batasan.get(kind.upper())
        return [str(x) for x in v] if isinstance(v, list) else []

    def refuses(self, proposal: str) -> list[str]:
        """
        Return every REFUSE the proposal collides with. Word-level overlap,
        deliberately generous: a false positive costs one clarifying sentence,
        a false negative recommends the thing she told us she will not do.
        """
        text = _norm(proposal)
        hits = []
        for rule in self.constraints("REFUSE"):
            words = {w for w in _norm(rule).split() if len(w) > 3}
            if words and len(words & set(text.split())) >= max(1, len(words) // 2):
                hits.append(rule)
        return hits

    # ---- intake -----------------------------------------------------------
    def missing(self) -> list[tuple[str, str]]:
        """(field, the question to ask her) — drives the intake, in order."""
        gaps: list[tuple[str, str]] = []
        if not self.meta.get("usaha"):
            gaps.append(("meta.usaha", "Usahanya namanya apa?"))
        if self.jenis not in ("barang", "jasa", "reseller"):
            gaps.append(("meta.jenis", "Kamu jualan barang, jasa, atau jadi reseller?"))
        if not self.products():
            gaps.append(("fakta.produk", "Jualan apa aja, dan harganya berapa?"))
        elif not self.prices():
            gaps.append(("fakta.produk[].harga", "Harganya berapa? (belum ada angkanya)"))
        if not self.fakta.get("ongkir"):
            gaps.append(("fakta.ongkir", "Ongkir biasanya berapa, atau gimana ngitungnya?"))
        if not self.fakta.get("jam_buka"):
            gaps.append(("fakta.jam_buka", "Buka jam berapa sampai jam berapa?"))
        if not self.may_promise():
            gaps.append(("fakta.yang_boleh_dijanjikan",
                         "Apa yang boleh aku janjiin sendiri tanpa nanya kamu dulu?"))
        for f, q in (
            ("kenapa_aku", "Kalau pelanggan pilih yang sebelah, biasanya kenapa?"),
            ("buat_siapa", "Yang paling sering beli itu orang kayak gimana?"),
            ("janji_tiap_kali", "Apa yang kamu pastiin selalu dapet, tiap pesanan?"),
            ("ga_pernah", "Ada yang kamu nggak mau lakuin walaupun laku?"),
        ):
            if not str(self.sikap.get(f) or "").strip():
                gaps.append((f"sikap.{f}", q))
        if not self.voice_samples():
            gaps.append(("sikap.suara_saya.contoh_chat",
                         "Copy-paste 3 chat asli kamu ke pelanggan, apa adanya."))
        return gaps

    def completeness(self) -> tuple[int, int]:
        total = 11
        return max(0, total - len(self.missing())), total

    # ---- rendering --------------------------------------------------------
    def summary(self) -> str:
        done, total = self.completeness()
        lines = [f"# {self.meta.get('usaha') or '(usaha belum diisi)'}"
                 f"  ·  {self.meta.get('kota') or '?'}  ·  {self.jenis or '?'}",
                 f"  profil terisi {done}/{total}"]
        if self.products():
            lines.append("\n## Harga")
            for p in self.products():
                harga = p.get("harga")
                harga_s = f"{int(harga):,}".replace(",", ".") if isinstance(harga, (int, float)) else "?"
                lines.append(f"  - {p.get('nama','?')}: Rp {harga_s}/{p.get('satuan','pcs')}"
                             + (f" — {p['catatan']}" if p.get("catatan") else ""))
        for label, key in (("Ongkir", "ongkir"), ("Jam buka", "jam_buka")):
            val = self.fakta.get(key)
            if val:
                lines.append(f"  {label}: {val}")
        if self.may_promise():
            lines.append("\n## Boleh dijanjikan tanpa nanya\n  - " + "\n  - ".join(self.may_promise()))
        if self.must_ask_first():
            lines.append("\n## Harus nanya dulu\n  - " + "\n  - ".join(self.must_ask_first()))
        sik = [f"  {f}: {self.sikap[f]}" for f in SIKAP_FIELDS if self.sikap.get(f)]
        if sik:
            lines.append("\n## Sikap\n" + "\n".join(sik))
        if self.stories():
            lines.append("\n## Cerita yang bisa dipakai\n  - " + "\n  - ".join(self.stories()))
        if self.voice_pronoun() or self.voice_samples():
            lines.append(f"\n## Suara ({self.voice_pronoun() or '?'})")
            lines += [f'  "{s}"' for s in self.voice_samples()]
        for kind in BATASAN_KINDS:
            vals = self.constraints(kind)
            if vals:
                lines.append(f"\n## {kind}\n  - " + "\n  - ".join(vals))
        gaps = self.missing()
        if gaps:
            lines.append("\n## Belum diisi — tanyakan satu per satu, jangan sekaligus")
            lines += [f"  {field}  →  {q}" for field, q in gaps]
        return "\n".join(lines)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", (s or "").lower())


def load(base: str | os.PathLike | None = None) -> Profile | None:
    """Never raises. Returns None when there is nothing usable to read."""
    if yaml is None:
        return None
    try:
        p = profile_path(base)
        if not p.is_file():
            return None
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        return Profile(data, p) if isinstance(data, dict) else None
    except Exception:
        return None


def _example_values() -> set[str]:
    """Every scalar in the shipped example, for the borrowed-stance check."""
    ex = Path(__file__).resolve().parents[2] / "templates" / "profile.example.yaml"
    if not ex.is_file():
        ex = Path(__file__).resolve().parent / "profile.example.yaml"
    out: set[str] = set()
    if yaml is None or not ex.is_file():
        return out

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str) and len(node.strip()) > 12:
            out.add(node.strip())

    try:
        walk(yaml.safe_load(ex.read_text(encoding="utf-8")))
    except Exception:
        return set()
    return out


def borrowed_from_example(prof: "Profile | None") -> list[str]:
    """
    Values copied verbatim out of the example file.

    A live session did exactly this: asked for her stance, read the template,
    and wrote the template's `kenapa_aku` into her profile as though she had
    said it. She never did. That sentence would then have been injected into
    every future promo as *her own words* — which is the precise opposite of
    what `sikap` is for, and invisible to her because it reads plausibly.

    This is the "claims vs reality" class landing in a new place, so it gets a
    code check rather than a warning comment in the template. **A fabricated
    `sikap` is worse than an empty one.**
    """
    if prof is None:
        return []
    ex = _example_values()
    if not ex:
        return []
    hits = []
    for field in SIKAP_FIELDS:
        val = prof.sikap.get(field)
        if isinstance(val, str) and val.strip() in ex:
            hits.append(f"sikap.{field}")
    for i, story in enumerate(prof.stories()):
        if story.strip() in ex:
            hits.append(f"sikap.cerita[{i}]")
    for i, chat in enumerate(prof.voice_samples()):
        if chat.strip() in ex:
            hits.append(f"sikap.suara_saya.contoh_chat[{i}]")
    return hits


def validate(prof: "Profile | None") -> list[str]:
    """Structural problems only — an incomplete profile is normal, not an error."""
    if prof is None:
        return ["profil tidak terbaca atau belum ada"]
    errs = []
    for field in borrowed_from_example(prof):
        errs.append(f"{field} masih sama persis dengan contoh — itu bukan kalimat dia. "
                    "Kosongkan, lalu tanya ulang. Sikap yang dikarang lebih buruk "
                    "daripada sikap yang kosong.")
    for layer in LAYERS:
        val = prof.data.get(layer)
        if val is not None and not isinstance(val, dict):
            errs.append(f"`{layer}` harus berupa blok, bukan {type(val).__name__}")
    for i, prod in enumerate(prof.fakta.get("produk") or []):
        if not isinstance(prod, dict):
            errs.append(f"fakta.produk[{i}] harus punya `nama` dan `harga`")
        elif prod.get("harga") is not None and not isinstance(prod["harga"], (int, float)):
            errs.append(f"fakta.produk[{i}].harga harus angka polos (15000, bukan '15rb')")
    for kind in BATASAN_KINDS:
        val = prof.batasan.get(kind)
        if val is not None and not isinstance(val, list):
            errs.append(f"batasan.{kind} harus berupa daftar")
    return errs


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "show"
    prof = load()
    if cmd == "show":
        if prof is None:
            print("Belum ada profil di " + str(profile_path()) + "\n"
                  "Ini bukan error — kerjaan tetap jalan. Tapi tanpa ini Hermes\n"
                  "nggak tahu harga kamu, dan promonya bakal generik.")
            return 0
        print(prof.summary())
        return 0
    if cmd == "missing":
        for field, q in (prof.missing() if prof else [("*", "profil belum ada")]):
            print(f"{field}\t{q}")
        return 0
    if cmd == "get":
        if len(argv) < 3:
            print("usage: profile.py get <dotted.key>", file=sys.stderr)
            return 2
        val = prof.get(argv[2]) if prof else None
        if val is None:
            return 1
        print(val)
        return 0
    if cmd == "check":
        errs = validate(prof)
        if prof is None:
            print("profil belum ada — itu wajar, semua tool tetap jalan")
            return 0
        for e in errs:
            print("  ✗ " + e, file=sys.stderr)
        done, total = prof.completeness()
        print(f"  profil terisi {done}/{total}" + ("" if errs else "  · struktur OK"))
        return 1 if errs else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
