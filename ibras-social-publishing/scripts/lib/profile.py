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

  ASAL     where she comes from: job, family trade, campus, communities, what
           she already built, what people always ask her for, who she follows,
           what irritates her — and the thread through them. Added after a
           recorded session (19-08-2026) collected five limits, zero assets, and
           produced a plan made entirely of limits. `batasan` is the walls;
           `asal` is the room. A recommendation built only from walls is generic
           by construction, which is what the user called "AI slop".

           It is also the fix for a straightforward bug: before this layer,
           `missing()` asked a website freelancer with no customers what his
           ONGKIR was, because the intake assumed a seller with products.

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

def _default_dir() -> str:
    """
    Where profile.yaml lives, in precedence order.

    `HERMES_HOME` has to be honoured here. It was not, and the bug is worse than
    it looks: every Hermes home on a machine read the *same* `~/.hermes/business/
    profile.yaml`, so two profiles were never two businesses. Caught on the first
    smoke test of the ten-persona run — a brand-new home, its own skills, its own
    state.db, opened by greeting a fresh school-leaver with the previous
    persona's AK3U grup and his refusal to be a joki. One person's answers
    reaching another person's session is the failure mode this whole eval exists
    to rule out, and the harness would have inherited it silently.
    """
    explicit = os.environ.get("HERMES_BUSINESS_DIR")
    if explicit:
        return explicit
    home = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
    return os.path.join(home, "business")


DEFAULT_DIR = _default_dir()
PROFILE_NAME = "profile.yaml"

# Layer names are Indonesian on purpose — the file is read aloud to the owner
# during intake, and an English key is a word she has to skip over.
LAYERS = ("fakta", "sikap", "batasan", "asal")

SIKAP_FIELDS = ("kenapa_aku", "buat_siapa", "janji_tiap_kali", "ga_pernah")
BATASAN_KINDS = ("REFUSE", "CAP", "ACCESS", "PERMISSION")

# The ten seams of references/excavation.md, in ask-order, with the opening
# question in her words. `missing()` serves these to a pre-revenue user instead
# of asking a person with no customers what their delivery fee is.
#
# Seam 10 (refusals) is deliberately absent: it lands in `batasan`, and it is
# asked LAST. A limit collected before an asset becomes the shape of the whole
# plan — that is the recorded failure this ordering exists to prevent.
ASAL_SEAMS = (
    ("kerja", "Sehari-hari kerja di bidang apa? Kantornya jualan apa, ke siapa?"),
    ("jejak", "Ada yang pernah kamu bikin sampai jadi? Nggak harus yang dibayar."),
    ("sering_diminta", "Kalau temen atau keluarga butuh bantuan, kamu paling sering dimintain tolong soal apa?"),
    ("pendidikan", "Kuliah/sekolah jurusan apa? Kalau tugas kelompok, kamu biasanya kebagian apa?"),
    ("komunitas", "Ada komunitas atau grup yang kamu ikutin? Grup WA, Discord, alumni, hobi — apa aja."),
    ("keluarga", "Orang tua kerjanya apa? Ada saudara yang punya usaha?"),
    ("minat", "Di luar kerjaan, waktu luang kamu paling sering habis buat apa?"),
    ("keresahan", "Ada hal di bidang kamu yang bikin kamu mikir 'kok gini banget, harusnya bisa lebih bener'?"),
    ("panutan", "Ada orang yang kamu ikutin terus, yang kalau dia ngepost kamu pasti baca?"),
)
ASAL_LIST_FIELDS = ("komunitas", "minat", "panutan", "jejak", "cerita")


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
    def asal(self) -> dict:
        return self.data.get("asal") or {}

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
        """
        Case-insensitive on purpose.

        A live session (19-08-2026, muse-spark-1.2) wrote a perfectly good
        register under `batasan.refuse` — lowercase — including "nggak mau joki
        dokumen biar orang lolos padahal nggak ngerti - prinsip". The lookup was
        `batasan.get("REFUSE")`, so every one of those rules read back as an
        empty list and `refuses()` would have cleared any proposal at all.

        Silent, total, and invisible: the register looked full in the file and
        empty to the check that exists to enforce it. Keys are matched
        case-insensitively now, because the agent writing the file and the code
        reading it must not have to agree on shift state.
        """
        want = kind.upper()
        for key, val in self.batasan.items():
            if str(key).upper() == want and isinstance(val, list):
                return [str(x) for x in val]
        return []

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

    # ---- ASAL -------------------------------------------------------------
    def seams_filled(self) -> list[str]:
        """Which excavation seams have produced anything. Empty list ≠ no history."""
        out = []
        for field, _ in ASAL_SEAMS:
            val = self.asal.get(field)
            if isinstance(val, str) and val.strip():
                out.append(field)
            elif isinstance(val, list) and any(str(x).strip() for x in val):
                out.append(field)
        return out

    def benang_merah(self) -> str:
        return str(self.asal.get("benang_merah") or "").strip()

    # ---- the number they arrived with -------------------------------------
    def target(self) -> str:
        """Their income/revenue goal, verbatim. `meta.target`."""
        return str(self.meta.get("target") or "").strip()

    def target_origin(self) -> str:
        """Where they saw that number — seam 8. `meta.target_dari`."""
        return str(self.meta.get("target_dari") or "").strip()

    def untraced_target(self) -> bool:
        """
        A goal is recorded and nobody ever asked where it came from.

        This is the exact state the 19-08-2026 session ended in: `5 juta` sat in
        the profile for sixteen turns as if it were self-explanatory, seam 8 was
        the one seam of ten never opened, and in an earlier attempt the model
        filled the vacuum by inventing salary bands to justify it. An untraced
        number is not a small gap — it is the space an invented benchmark grows
        into, so it outranks every other question.
        """
        return bool(self.target()) and not self.target_origin()

    def assets(self) -> list[str]:
        """
        Everything she has, flattened — the list to re-read before recommending,
        the way `batasan` is re-read. A plan that touches none of it is generic
        by construction.
        """
        out: list[str] = []
        for field, _ in ASAL_SEAMS:
            val = self.asal.get(field)
            if isinstance(val, str) and val.strip():
                out.append(f"{field}: {val.strip()}")
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        nama = str(item.get("nama") or "").strip()
                        untuk = str(item.get("untuk_siapa") or "").strip()
                        if nama:
                            out.append(f"{field}: {nama}" + (f" (untuk {untuk})" if untuk else ""))
                    elif str(item).strip():
                        out.append(f"{field}: {str(item).strip()}")
        return out

    def unexamined_trail(self) -> list[str]:
        """
        Things she built whose `untuk_siapa` is still blank.

        This is the highest-value gap in the whole profile and it looks like
        nothing. In the recorded session two live sites with bought domains sat
        in the transcript labelled "iseng", unexamined, while the coach told the
        user he had no proof and no access. Whoever received the thing is a warm
        contact; why it exists is a positioning lever. Both were one question away.
        """
        out = []
        for item in self.asal.get("jejak") or []:
            if isinstance(item, dict) and not str(item.get("untuk_siapa") or "").strip():
                nama = str(item.get("nama") or "?").strip()
                out.append(nama)
        return out

    def pre_revenue(self) -> bool:
        """
        Nobody has paid yet, or there is nothing priced to pay for.

        Decides which intake runs. Asking a person with no customers what their
        ongkir is — which is what this file did before — reads as a form written
        for somebody else, and it is: the old intake assumed a seller with stock.
        """
        return not self.products() or not self.prices()

    def _excavation_gaps(self, limit: int = 3) -> list[tuple[str, str]]:
        """
        The next few seams to open, never all of them.

        Capped on purpose. Nine questions in one payload is a form however
        carefully the caller was told to ask one at a time, and a form is where
        she leaves. Three is a conversation with somewhere to go.
        """
        gaps: list[tuple[str, str]] = []
        # Outranks everything: a number with no origin. See untraced_target().
        if self.untraced_target():
            gaps.append(("meta.target_dari",
                         f"{self.target()} itu kamu lihat dari mana? Ada yang pernah "
                         f"kamu lihat dapet segitu?"))
        # Next: something she already built that nobody asked about.
        for nama in self.unexamined_trail():
            gaps.append((f"asal.jejak[{nama}].untuk_siapa",
                         f"{nama} itu buat siapa, dan kenapa kamu bikin? Ada yang minta?"))
        filled = set(self.seams_filled())
        for field, question in ASAL_SEAMS:
            if len(gaps) >= limit:
                break
            if field not in filled:
                gaps.append((f"asal.{field}", question))
        if len(filled) >= 5 and not self.benang_merah() and len(gaps) < limit:
            gaps.append(("asal.benang_merah",
                         "Tarik benang merahnya sekarang — susun dari kata-kata dia, "
                         "lalu bacakan balik sebagai pertanyaan, bukan sebagai kesimpulan."))
        return gaps[:limit]

    # ---- intake -----------------------------------------------------------
    def missing(self) -> list[tuple[str, str]]:
        """
        (field, the question to ask her) — drives the intake, in order.

        Two orders, because two situations. A running seller needs `fakta` first:
        it takes ninety seconds and it unblocks today's work. Someone pre-revenue
        has no `fakta` to give, and asking anyway produces the interrogation the
        19-08-2026 session became — so excavation leads instead, and the seams
        run before the walls.
        """
        gaps: list[tuple[str, str]] = []
        if not self.meta.get("usaha"):
            gaps.append(("meta.usaha", "Usahanya namanya apa?"))
        if self.jenis not in ("barang", "jasa", "reseller"):
            gaps.append(("meta.jenis", "Kamu jualan barang, jasa, atau jadi reseller?"))

        if self.pre_revenue():
            gaps += self._excavation_gaps()

        if not self.products():
            gaps.append(("fakta.produk", "Jualan apa aja, dan harganya berapa?"))
        elif not self.prices():
            gaps.append(("fakta.produk[].harga", "Harganya berapa? (belum ada angkanya)"))
        # Logistics only make sense once there is something to deliver. Asked of
        # a service with no customers they are noise, and noise reads as a form.
        if self.products():
            if not self.fakta.get("ongkir"):
                gaps.append(("fakta.ongkir", "Ongkir biasanya berapa, atau gimana ngitungnya?"))
            if not self.fakta.get("jam_buka"):
                gaps.append(("fakta.jam_buka", "Buka jam berapa sampai jam berapa?"))
        if not self.may_promise():
            gaps.append(("fakta.yang_boleh_dijanjikan",
                         "Apa yang boleh aku janjiin sendiri tanpa nanya kamu dulu?"))
        if not self.target():
            gaps.append(("meta.target",
                         "Sebulan pengennya dapet berapa, dan kapan mulai kepakainya?"))
        if not self.pre_revenue():
            gaps += self._excavation_gaps()
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
        # 11 fakta/sikap slots + the 3 excavation slots `missing()` serves at a time.
        total = 14
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
        # Assets before walls, on screen as well as in the interview. An agent
        # that reads the limits first plans to the limits — that is the whole
        # finding of the 19-08-2026 session.
        if self.benang_merah():
            lines.append("\n## Benang merah\n  " + self.benang_merah())
        assets = self.assets()
        if assets:
            lines.append("\n## Yang dia punya — baca ulang sebelum tiap saran\n  - "
                         + "\n  - ".join(assets))
        unexamined = self.unexamined_trail()
        if unexamined:
            lines.append("\n## Belum ditanya buat siapa — ini gali dulu\n  - "
                         + "\n  - ".join(unexamined))
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
    # A copied `benang_merah` is the same defect one layer up, and worse in one
    # respect: it is a sentence she starts saying about herself. The thread has
    # to be assembled from things she actually said, then read back and
    # confirmed — so a verbatim match with the example means it was not.
    for field in ("benang_merah", "kerja", "keluarga", "pendidikan",
                  "sering_diminta", "keresahan"):
        val = prof.asal.get(field)
        if isinstance(val, str) and val.strip() in ex:
            hits.append(f"asal.{field}")
    for i, story in enumerate(prof.asal.get("cerita") or []):
        if isinstance(story, str) and story.strip() in ex:
            hits.append(f"asal.cerita[{i}]")
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
    if cmd == "path":
        # The one command that stops a coaching session writing one owner's
        # business into another owner's file. The skills used to name
        # `~/.hermes/business/profile.yaml` in prose, so the model wrote that
        # literal path — and on a machine running more than one Hermes home,
        # three sessions landed in the same file. Resolve, never hardcode.
        print(profile_path())
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
