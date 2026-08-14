#!/usr/bin/env python3
"""
Advisor — jawab "sebaiknya saya pakai apa untuk posting?" dari riset yang sudah ada.

Skill ini tidak memilihkan untukmu dan tidak melarang apa pun. Dia membaca
`data/options.yaml`, mencocokkan dengan batasanmu, lalu menunjukkan urutannya
**lengkap dengan kerugian tiap jalur** — termasuk jalur yang dia rekomendasikan.

Kenapa dibangun begini: tiga laporan riset mendalam di repo ini sepakat pada
satu hal, dan itu bukan "pakai tool X". Yang mereka sepakati adalah bahwa
pilihan yang benar berubah total tergantung satu pertanyaan — seberapa mahal
kalau akunnya hilang. Alat yang menjawab "pakai Postiz" tanpa menanyakan itu
sedang menebak.

Perintah:
  python3 advisor.py options                      semua jalur, ringkas
  python3 advisor.py show selfhost-scheduler      satu jalur, lengkap
  python3 advisor.py recommend --budget 5 --platforms instagram,x --skill 2
  python3 advisor.py compare official-api selfhost-scheduler
  python3 advisor.py platforms                    angka resmi per platform
  python3 advisor.py sources                      dari mana setiap klaim berasal
  python3 advisor.py search "ban"                 cari di seluruh riset
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Butuh PyYAML: pip3 install pyyaml", file=sys.stderr)
    sys.exit(1)

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SKILL_DIR / "data"
REF_DIR = SKILL_DIR / "references"

RISK_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3, "very_high": 4}
RISK_LABEL = {"none": "tidak ada", "low": "rendah", "medium": "sedang",
              "high": "tinggi", "very_high": "sangat tinggi"}
TOS_LABEL = {"compliant": "sesuai ToS", "gray": "abu-abu", "violation": "melanggar ToS"}


def load(name: str) -> dict:
    path = DATA_DIR / name
    if not path.exists():
        print(f"Data hilang: {path}", file=sys.stderr)
        sys.exit(1)
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def bullets(items, indent="      ", limit=None, bullet="·"):
    for it in (items or [])[:limit]:
        wrapped = wrap(str(it), width=78 - len(indent))
        print(f"{indent}{bullet} {wrapped[0]}")
        for line in wrapped[1:]:
            print(f"{indent}  {line}")


def wrap(text: str, width: int = 74) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines or [""]


def cost_str(c: dict) -> str:
    lo, hi = c.get("min", 0), c.get("max", 0)
    if lo == hi == 0:
        return "gratis"
    return f"${lo}–{hi}/bln" if lo != hi else f"${lo}/bln"


# ---------------------------------------------------------------------------

def cmd_options(args):
    data = load("options.yaml")
    print(f"\n  {len(data['options'])} jalur — data per {data['updated']}\n")
    print(f"  {'ID':<20} {'BIAYA':<12} {'RISIKO':<14} {'TOS':<14} {'SKILL':<6} NAMA")
    print(f"  {'-'*20} {'-'*12} {'-'*14} {'-'*14} {'-'*6} {'-'*30}")
    for o in data["options"]:
        print(f"  {o['id']:<20} {cost_str(o['cost_usd_month']):<12} "
              f"{RISK_LABEL[o['risk']]:<14} {TOS_LABEL[o['tos']]:<14} "
              f"{o['skill_required']}/5    {o['name'][:34]}")
    print("\n  Detail satu jalur:  python3 advisor.py show <id>")
    print("  Rekomendasi:        python3 advisor.py recommend --help\n")
    return 0


def cmd_show(args):
    data = load("options.yaml")
    o = next((x for x in data["options"] if x["id"] == args.id), None)
    if not o:
        print(f"Jalur '{args.id}' tidak ada. Lihat: python3 advisor.py options", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(o, ensure_ascii=False, indent=2))
        return 0

    print(f"\n{'='*80}")
    print(f"  {o['name']}")
    print(f"  {o['tagline']}")
    print(f"{'='*80}\n")
    print(f"  Biaya          {cost_str(o['cost_usd_month'])}   ({o['cost_usd_month'].get('note','')})")
    print(f"  Risiko akun    {RISK_LABEL[o['risk']]}")
    print(f"  Status ToS     {TOS_LABEL[o['tos']]}")
    print(f"  Kemampuan      {o['skill_required']}/5 teknis")
    print(f"  Setup          {o['setup_hours'][0]}–{o['setup_hours'][1]} jam")
    print(f"  Tier           {o['tier']}")
    print(f"  Platform       {', '.join(o['platforms'])}")
    print(f"  Batas wajar    ~{o['volume_ceiling_per_week']} post/minggu")
    print(f"  Kalau salah    {o['reversible']}")

    print("\n  APA YANG DIKERJAKAN HERMES DI JALUR INI")
    bullets(o["what_hermes_does"])

    print("\n  KERUGIAN (baca ini, ini bagian yang penting)")
    bullets(o["drawbacks"], bullet="✗")

    print("\n  IMPLIKASI")
    bullets(o["implications"], bullet="→")

    print("\n  PILIH INI KALAU")
    bullets(o["when_to_pick"], bullet="✓")

    print("\n  JANGAN PILIH INI KALAU")
    bullets(o["when_not_to"], bullet="✗")

    if o.get("safer_shape"):
        print("\n  BENTUK YANG LEBIH AMAN (kalau kamu tetap mau jalur ini)")
        bullets(o["safer_shape"], bullet="◆")

    if o.get("alternatives"):
        print(f"\n  ALTERNATIF     {', '.join(o['alternatives'])}")
    if o.get("evidence"):
        print(f"  BUKTI          {', '.join(o['evidence'])}")
        print(f"                 python3 advisor.py sources --id {o['evidence'][0]}")
    print()
    return 0


def score_option(o: dict, want_platforms: list[str], budget: float, risk_tol: str,
                 skill: int, volume: int, account_value: str) -> tuple[float, list[str]]:
    """Explainable scoring. Every deduction comes with a sentence."""
    reasons = []
    score = 0.0

    # Coverage — 30
    if want_platforms:
        covered = [p for p in want_platforms if p in o["platforms"]]
        frac = len(covered) / len(want_platforms)
        score += 30 * frac
        missing = [p for p in want_platforms if p not in o["platforms"]]
        if missing:
            reasons.append(f"tidak mencakup {', '.join(missing)}")
    else:
        score += 30

    # Cost — 20
    lo = o["cost_usd_month"].get("min", 0)
    if lo <= budget:
        score += 20
    else:
        over = lo - budget
        score += max(0, 20 - over * 2)
        reasons.append(f"biaya mulai ${lo}/bln, di atas anggaran ${budget:g}")

    # Risk — 25, and account value multiplies the penalty
    r, tol = RISK_ORDER[o["risk"]], RISK_ORDER[risk_tol]
    if r <= tol:
        score += 25
    else:
        gap = r - tol
        penalty = gap * 8 * (2.0 if account_value == "high" else 1.0)
        score += max(0, 25 - penalty)
        reasons.append(f"risiko {RISK_LABEL[o['risk']]}, di atas toleransi {RISK_LABEL[risk_tol]}"
                       + (" — dan akun ini kamu sebut tidak tergantikan" if account_value == "high" else ""))
    if o["tos"] == "violation" and account_value == "high":
        score -= 15
        reasons.append("melanggar ToS pada akun yang tidak tergantikan")

    # Skill — 15
    if o["skill_required"] <= skill:
        score += 15
    else:
        gap = o["skill_required"] - skill
        score += max(0, 15 - gap * 6)
        reasons.append(f"butuh kemampuan teknis {o['skill_required']}/5, kamu isi {skill}/5")

    # Volume — 10
    ceil = o["volume_ceiling_per_week"]
    if volume <= ceil:
        score += 10
    else:
        score += max(0, 10 - (volume - ceil) / max(1, ceil) * 10)
        reasons.append(f"volume {volume}/minggu di atas batas wajar jalur ini (~{ceil})")

    return round(max(0.0, score), 1), reasons


def cmd_recommend(args):
    data = load("options.yaml")
    frame = data.get("decision_frame", {})
    want = [p.strip().lower() for p in (args.platforms or "").split(",") if p.strip()]

    if args.json:
        ranked = sorted(
            ((score_option(o, want, args.budget, args.risk, args.skill,
                           args.volume, args.account_value), o) for o in data["options"]),
            key=lambda t: t[0][0], reverse=True)
        print(json.dumps({
            "decision_frame": frame,
            "constraints": {"budget": args.budget, "risk": args.risk,
                            "platforms": want, "skill": args.skill,
                            "volume": args.volume, "account_value": args.account_value},
            "ranked": [{"score": s, "id": o["id"], "name": o["name"],
                        "cost": cost_str(o["cost_usd_month"]), "risk": o["risk"],
                        "tos": o["tos"], "deductions": r, "drawbacks": o["drawbacks"],
                        "alternatives": o.get("alternatives", [])}
                       for (s, r), o in ranked],
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"\n{'='*80}")
    print("  DUA PERTANYAAN SEBELUM TABEL APA PUN")
    print(f"{'='*80}\n")
    print(f"  1. {frame.get('first_question','')}")
    for line in wrap(frame.get("why", ""), 74):
        print(f"     {line}")
    print(f"\n  2. {frame.get('second_question','')}")
    for line in wrap(frame.get("why_second", ""), 74):
        print(f"     {line}")

    print(f"\n{'='*80}")
    print("  BATASAN YANG KAMU MASUKKAN")
    print(f"{'='*80}\n")
    print(f"  Anggaran        ${args.budget:g}/bulan")
    print(f"  Toleransi risiko {RISK_LABEL[args.risk]}")
    print(f"  Platform        {', '.join(want) if want else 'semua'}")
    print(f"  Kemampuan       {args.skill}/5")
    print(f"  Volume          {args.volume} post/minggu")
    print(f"  Nilai akun      {args.account_value}")

    ranked = []
    for o in data["options"]:
        s, reasons = score_option(o, want, args.budget, args.risk, args.skill,
                                  args.volume, args.account_value)
        ranked.append((s, o, reasons))
    ranked.sort(key=lambda t: t[0], reverse=True)

    print(f"\n{'='*80}")
    print("  URUTAN")
    print(f"{'='*80}\n")
    for i, (s, o, reasons) in enumerate(ranked, 1):
        tag = "  ← paling cocok dengan batasanmu" if i == 1 else ""
        print(f"  {i}. [{s:>5.1f}] {o['name']}{tag}")
        print(f"           {o['tagline']}")
        print(f"           {cost_str(o['cost_usd_month'])} · risiko {RISK_LABEL[o['risk']]} · "
              f"{TOS_LABEL[o['tos']]} · skill {o['skill_required']}/5")
        if reasons:
            print("           dikurangi karena:")
            bullets(reasons, indent="             ", bullet="−")
        print("           kerugian utama:")
        bullets(o["drawbacks"], indent="             ", limit=3, bullet="✗")
        print()

    top = ranked[0][1]
    print(f"{'='*80}")
    print("  CATATAN")
    print(f"{'='*80}\n")
    for line in wrap(f"Urutan ini keluar dari angka yang kamu masukkan, bukan dari "
                     f"pendapat siapa pun. Ubah satu batasan dan urutannya berubah — "
                     f"coba jalankan lagi dengan --account-value low kalau akun ini "
                     f"sebenarnya bisa diganti.", 76):
        print(f"  {line}")
    print()
    for line in wrap(f"Sebelum memakai '{top['name']}', baca kerugiannya lengkap: "
                     f"python3 advisor.py show {top['id']}", 76):
        print(f"  {line}")
    print()
    if top["id"] in ("selfhost-scheduler", "official-api"):
        for line in wrap("Untuk dua jalur yang benar-benar mempublikasikan: jalankan uji "
                         "dua minggu dengan post asli sebelum mempercayakan jadwal ke "
                         "mesin. Kegagalan yang paling mahal di riset ini semuanya "
                         "kegagalan SCHEDULER — dan scheduler tidak pernah rusak saat "
                         "kamu sedang menontonnya.", 76):
            print(f"  {line}")
        print()
    return 0


def cmd_compare(args):
    data = load("options.yaml")
    picked = []
    for oid in args.ids:
        o = next((x for x in data["options"] if x["id"] == oid), None)
        if not o:
            print(f"Jalur '{oid}' tidak ada.", file=sys.stderr)
            return 1
        picked.append(o)

    rows = [
        ("Biaya", lambda o: cost_str(o["cost_usd_month"])),
        ("Risiko akun", lambda o: RISK_LABEL[o["risk"]]),
        ("Status ToS", lambda o: TOS_LABEL[o["tos"]]),
        ("Kemampuan", lambda o: f"{o['skill_required']}/5"),
        ("Setup (jam)", lambda o: f"{o['setup_hours'][0]}–{o['setup_hours'][1]}"),
        ("Tier", lambda o: o["tier"]),
        ("Batas/minggu", lambda o: f"~{o['volume_ceiling_per_week']}"),
        ("Platform", lambda o: str(len(o["platforms"]))),
    ]
    w = 18
    print()
    print("  " + " " * w + "".join(f"{o['id'][:22]:<24}" for o in picked))
    print("  " + "-" * (w + 24 * len(picked)))
    for label, fn in rows:
        print(f"  {label:<{w}}" + "".join(f"{fn(o)[:22]:<24}" for o in picked))
    for o in picked:
        print(f"\n  {o['name']} — kerugian:")
        bullets(o["drawbacks"], indent="      ", bullet="✗")
    print()
    return 0


def cmd_platforms(args):
    data = load("platforms.yaml")
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(f"\n  Angka resmi per platform — diverifikasi {data['updated']}\n")
    for p in data["platforms"]:
        ver = p.get("verified") or "BELUM DIVERIFIKASI"
        print(f"  {'─'*76}")
        print(f"  {p['name']}   ({ver})")
        print(f"    API      {p['publish_api']}")
        print(f"    Akun     {p['account_requirement']}")
        print(f"    Biaya    {p['cost']}")
        for k, v in (p.get("limits") or {}).items():
            print(f"    {k:<22} {v}")
        for k, v in (p.get("pricing") or {}).items():
            print(f"    {k:<22} ${v}")
        if p.get("not_supported"):
            print(f"    Tidak didukung:")
            bullets(p["not_supported"], indent="      ", bullet="·")
        if p.get("gotchas"):
            print(f"    Yang perlu diketahui:")
            bullets(p["gotchas"], indent="      ", bullet="!")
    print()
    return 0


def cmd_sources(args):
    data = load("sources.yaml")
    marks = {"green": "🟢", "yellow": "🟡", "orange": "🟠", "red": "🔴"}
    srcs = data["sources"]
    if args.id:
        srcs = [s for s in srcs if s["id"] == args.id]
        if not srcs:
            print(f"Sumber '{args.id}' tidak ada.", file=sys.stderr)
            return 1
    if args.json:
        print(json.dumps(srcs, ensure_ascii=False, indent=2))
        return 0
    print(f"\n  Legenda: 🟢 primer, dibuka langsung · 🟡 komunitas berulang · "
          f"🟠 satu sumber · 🔴 klaim vendor\n")
    for s in srcs:
        print(f"  {marks.get(s['confidence'],'?')} {s['id']}   (dicek {s['verified']})")
        print(f"     {s['title']}")
        print(f"     {s['url']}")
        for c in s.get("claims", []):
            for line in wrap(c, 70):
                print(f"       · {line}")
        if s.get("note"):
            print()
            for line in wrap(s["note"], 70):
                print(f"       {line}")
        print()
    if not args.id:
        note = (load("sources.yaml").get("meta") or {}).get("note_report_b")
        if note:
            print(f"  {'─'*76}")
            print("  Catatan tentang salah satu laporan sumber:")
            for line in wrap(note, 74):
                print(f"    {line}")
            print()
    return 0


def cmd_search(args):
    """Cari di seluruh riset yang sudah dikompilasi: data + dokumen referensi."""
    q = args.query.lower()
    targets = sorted(DATA_DIR.glob("*.yaml")) + sorted(REF_DIR.glob("*.md"))
    hits = 0
    print(f"\n  Mencari \"{args.query}\" di {len(targets)} berkas riset\n")
    for path in targets:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        matched = [(i + 1, ln) for i, ln in enumerate(lines) if q in ln.lower()]
        if not matched:
            continue
        rel = path.relative_to(SKILL_DIR)
        print(f"  {'─'*76}")
        print(f"  {rel}  ({len(matched)} baris)")
        for lineno, ln in matched[:args.limit]:
            text = ln.strip()
            if len(text) > 150:
                text = text[:150] + "…"
            print(f"    {lineno:>5}  {text}")
            hits += 1
        if len(matched) > args.limit:
            print(f"          … +{len(matched)-args.limit} baris lagi di berkas ini")
    if not hits:
        print("  Tidak ada. Coba kata kunci lain, atau lihat daftar jalur:")
        print("    python3 advisor.py options\n")
        return 1
    print(f"\n  {hits} baris ditampilkan.\n")
    return 0


def main():
    p = argparse.ArgumentParser(prog="advisor.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("options", help="daftar semua jalur").set_defaults(fn=cmd_options)

    sp = sub.add_parser("show", help="detail satu jalur, termasuk kerugiannya")
    sp.add_argument("id")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_show)

    sp = sub.add_parser("recommend", help="urutkan jalur sesuai batasanmu")
    sp.add_argument("--budget", type=float, default=5, help="USD/bulan (default 5)")
    sp.add_argument("--risk", choices=list(RISK_ORDER), default="low",
                    help="toleransi risiko akun (default low)")
    sp.add_argument("--platforms", help="instagram,threads,x,facebook,tiktok,linkedin")
    sp.add_argument("--skill", type=int, default=2, help="kemampuan teknis 1-5 (default 2)")
    sp.add_argument("--volume", type=int, default=5, help="post per minggu (default 5)")
    sp.add_argument("--account-value", choices=["low", "medium", "high"], default="high",
                    help="seberapa mahal kalau akun ini hilang (default high)")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_recommend)

    sp = sub.add_parser("compare", help="bandingkan 2-3 jalur berdampingan")
    sp.add_argument("ids", nargs="+")
    sp.set_defaults(fn=cmd_compare)

    sp = sub.add_parser("platforms", help="angka resmi per platform")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_platforms)

    sp = sub.add_parser("sources", help="dari mana setiap klaim berasal")
    sp.add_argument("--id")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_sources)

    sp = sub.add_parser("search", help="cari di seluruh riset yang dikompilasi")
    sp.add_argument("query")
    sp.add_argument("--limit", type=int, default=6, help="baris per berkas")
    sp.set_defaults(fn=cmd_search)

    args = p.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
