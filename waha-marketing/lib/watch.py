#!/usr/bin/env python3
"""
watch.py — scheduled work that is cheap and forgetful-proof by construction.

Not a scheduler. Hermes already has one (`cronjob`), and rewriting it would be the
exact DRY violation this repo keeps warning about. This is a *shape* on top of it:
it composes the flags that make a recurring job correct, and refuses the two shapes
that make it wrong.

Why a library and not a paragraph in a reference file. `hermes-discipline.md` opens
with the only sentence that matters here — "Prose did not hold. Checks do." Told in
prose to build a monitor-mode job with a notepad, a model writes a plain daily job,
because that is the shortest thing to write. So make the correct shape the short one.

Two refusals, both structural:

  1. --remember is REQUIRED. A job with no notepad keys is rejected, not warned
     about. This is the failure that kills automation in week two: the lead job
     re-suggests a contacted lead, the content job rewrites last week's article,
     and the owner concludes the whole thing is stupid. They are right.

  2. --publish does not exist. Delivery is always a draft to the owner. There is no
     flag to change that, the same way Hermes' own `cronjob` tool takes no model
     parameter — the brake is the absence of a control, not the discipline to
     avoid one.

And one default: --check runs a cheap script first and hashes the output. No change
means no model call, no delivery, no cost. A watcher that pays a model to say
"nothing changed" is a defect, not a feature.

    python3 watch.py create --name harga-supplier \
        --check "bash scripts/cek-harga.sh" \
        --every "senin 06:00" \
        --remember last_price,last_notified \
        --deliver telegram
    python3 watch.py list
    python3 watch.py why  harga-supplier      # kenapa bunyi / kenapa diam
    python3 watch.py cost harga-supplier
    python3 watch.py rm   harga-supplier

Fails open on read paths (list/why/cost print "kosong" rather than exploding) and
fail-closed on create: a job it cannot prove is well-formed is not created.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BUSINESS_DIR = Path(os.environ.get("HERMES_BUSINESS_DIR") or
                    os.path.expanduser("~/.hermes/business"))
WATCH_FILE = Path(os.environ.get("HERMES_WATCH_FILE", BUSINESS_DIR / "watches.json"))
RUNLOG = Path(os.environ.get("HERMES_WATCH_LOG", BUSINESS_DIR / "watch-runs.jsonl"))

# Scheduled work runs on the cheap fleet. Not settable from the command line: a job
# whose model can be raised from the call is a job whose bill can be raised by
# whatever wrote the call.
DEFAULT_JOB_MODEL = os.environ.get("HERMES_CRON_MODEL", "cron.model")

DELIVERIES = ("telegram", "discord", "slack", "whatsapp", "desktop", "none")


class WatchError(Exception):
    pass


# ---------------------------------------------------------------- storage


def _load() -> dict:
    try:
        if WATCH_FILE.is_file():
            data = json.loads(WATCH_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except (OSError, ValueError):
        pass
    return {}


def _save(data: dict) -> None:
    WATCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = WATCH_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(WATCH_FILE)


def _append_run(rec: dict) -> None:
    try:
        RUNLOG.parent.mkdir(parents=True, exist_ok=True)
        with RUNLOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass  # a run log that fails must never stop the job


# ---------------------------------------------------------------- validation


def validate(name: str, check: str, every: str, remember: list[str],
             deliver: str) -> None:
    """Raise WatchError with a reason a human can act on. Never a bare False."""
    if not name or not name.replace("-", "").replace("_", "").isalnum():
        raise WatchError(
            f"nama '{name}' tidak valid — pakai huruf, angka, - atau _")

    if not check.strip():
        raise WatchError(
            "--check kosong. Job tanpa pemeriksa murah berarti tiap jalan memanggil\n"
            "model, termasuk di hari yang tidak ada perubahan. Itu yang bikin\n"
            "otomasi mahal padahal tidak menghasilkan apa-apa.")

    if not every.strip():
        raise WatchError("--every kosong — kapan job ini jalan?")

    if not remember:
        raise WatchError(
            "--remember wajib diisi, dan ini bukan formalitas.\n"
            "\n"
            "Job yang tidak mengingat apa pun akan mengulang dirinya sendiri:\n"
            "  · job lead menyarankan lead yang minggu lalu sudah dihubungi\n"
            "  · job konten menulis ulang artikel yang sudah ditulis\n"
            "  · job harga mengabari harga yang sudah dikabari kemarin\n"
            "\n"
            "Itu alasan nomor satu orang mematikan otomasi di minggu kedua.\n"
            "Sebutkan apa yang harus diingat antar-jalan, contoh:\n"
            "  --remember last_price,last_notified\n"
            "  --remember contacted_ids\n"
            "  --remember last_posted_url")

    bad = [k for k in remember if not k.replace("_", "").replace("-", "").isalnum()]
    if bad:
        raise WatchError(f"kunci notepad tidak valid: {', '.join(bad)}")

    if deliver not in DELIVERIES:
        raise WatchError(
            f"--deliver '{deliver}' tidak dikenal. Pilihan: {', '.join(DELIVERIES)}")


# ---------------------------------------------------------------- commands


def cmd_create(args) -> int:
    remember = [k.strip() for k in (args.remember or "").split(",") if k.strip()]
    try:
        validate(args.name, args.check or "", args.every or "", remember, args.deliver)
    except WatchError as exc:
        print(f"✗ job tidak dibuat.\n\n{exc}", file=sys.stderr)
        return 2

    data = _load()
    if args.name in data and not args.force:
        print(f"✗ '{args.name}' sudah ada. Pakai --force untuk menimpa.", file=sys.stderr)
        return 2

    job = {
        "name": args.name,
        "check": args.check,
        "every": args.every,
        "remember": remember,
        "deliver": args.deliver,
        "model": DEFAULT_JOB_MODEL,
        "draft_only": True,          # tidak ada jalan lain. lihat docstring.
        "prompt": args.prompt or "",
        "created": datetime.now().astimezone().isoformat(timespec="seconds"),
        "last_hash": None,
        "runs": 0,
        "fired": 0,
    }
    data[args.name] = job
    _save(data)

    print(f"✓ watcher '{args.name}' dibuat.")
    print(f"  Jalan     : {args.every}")
    print(f"  Cek murah : {args.check}")
    print(f"  Ingat     : {', '.join(remember)}")
    print(f"  Kirim     : {args.deliver} — sebagai DRAFT ke kamu, tidak pernah publish")
    print(f"  Model     : {DEFAULT_JOB_MODEL} (armada job, terpisah dari model chat)")
    print()
    print("  Kalau tidak ada perubahan: tidak ada panggilan model, tidak ada biaya.")
    print()
    print("  Daftarkan ke penjadwal Hermes dengan:")
    print(f"    {hermes_cron_command(job)}")
    return 0


def hermes_cron_command(job: dict) -> str:
    """The Hermes-native command this job maps to.

    We deliberately print it instead of shelling out: the scheduler is Hermes', the
    notepad is Hermes', monitor-mode is Hermes'. Owning a copy of any of those here
    would be the duplication this file exists to avoid.
    """
    keys = ",".join(job["remember"])
    parts = [
        "hermes cronjob create",
        f"--name {job['name']}",
        f"--schedule {json.dumps(job['every'])}",
        f"--monitor-script {json.dumps(job['check'])}",
        f"--notepad {keys}",
        f"--model {job['model']}",
        f"--deliver {job['deliver']}",
        "--draft",
    ]
    if job.get("prompt"):
        parts.append(f"--prompt {json.dumps(job['prompt'])}")
    return " \\\n      ".join(parts)


def run_check(job: dict) -> tuple[str, str]:
    """Run the cheap check, return (hash, output). No model involved."""
    try:
        proc = subprocess.run(job["check"], shell=True, capture_output=True,
                              text=True, timeout=120)
        out = (proc.stdout or "") + (proc.stderr or "")
    except (subprocess.SubprocessError, OSError) as exc:
        out = f"__CHECK_FAILED__ {exc}"
    return hashlib.sha256(out.encode("utf-8", "replace")).hexdigest(), out


def cmd_test(args) -> int:
    """Run the cheap check once, show what would happen. No model, no delivery."""
    data = _load()
    job = data.get(args.name)
    if not job:
        print(f"'{args.name}' tidak ada.", file=sys.stderr)
        return 1

    digest, out = run_check(job)
    changed = digest != job.get("last_hash")
    print(f"watcher : {args.name}")
    print(f"hash    : {digest[:12]}  (sebelumnya: {str(job.get('last_hash'))[:12]})")
    print(f"berubah : {'YA — job akan bangun & bikin draft' if changed else 'TIDAK — diam, Rp 0'}")
    print()
    print("keluaran cek:")
    for line in out.strip().splitlines()[:20]:
        print(f"  {line}")
    if args.save:
        job["last_hash"] = digest
        job["runs"] = job.get("runs", 0) + 1
        if changed:
            job["fired"] = job.get("fired", 0) + 1
        data[args.name] = job
        _save(data)
        _append_run({"when": datetime.now().astimezone().isoformat(timespec="seconds"),
                     "name": args.name, "changed": changed, "hash": digest})
        print("\n(hash disimpan)")
    return 0


def cmd_list(args) -> int:
    data = _load()
    if not data:
        print("kosong — belum ada watcher.")
        return 0
    for name, job in sorted(data.items()):
        runs, fired = job.get("runs", 0), job.get("fired", 0)
        quiet = runs - fired
        print(f"{name}")
        print(f"  jalan {job['every']} · ingat: {', '.join(job['remember'])}")
        print(f"  {runs} kali dicek · {fired} kali bunyi · {quiet} kali diam (Rp 0)")
    return 0


def cmd_why(args) -> int:
    """The most common support question: is it broken, or is nothing happening?"""
    data = _load()
    job = data.get(args.name)
    if not job:
        print(f"'{args.name}' tidak ada.", file=sys.stderr)
        return 1
    runs, fired = job.get("runs", 0), job.get("fired", 0)
    print(f"watcher : {args.name}")
    print(f"dibuat  : {job.get('created')}")
    print(f"dicek   : {runs} kali · bunyi {fired} kali · diam {runs - fired} kali")
    print()
    if runs == 0:
        print("Belum pernah jalan. Kalau harusnya sudah, cek pendaftarannya:")
        print(f"  {hermes_cron_command(job)}")
    elif fired == 0:
        print("Jalan, tapi belum pernah ada perubahan. Ini BUKAN rusak —")
        print("ini justru bentuk yang benar: diam berarti tidak ada kabar,")
        print("dan diam itu tidak memanggil model sama sekali.")
        print()
        print("Mau memastikan? Jalankan cek-nya sekarang:")
        print(f"  python3 watch.py test {args.name}")
    else:
        print("Berjalan normal.")
    print()
    try:
        lines = RUNLOG.read_text(encoding="utf-8").strip().splitlines()
        recent = [json.loads(l) for l in lines if f'"{args.name}"' in l][-5:]
        if recent:
            print("5 jalan terakhir:")
            for r in recent:
                mark = "bunyi" if r.get("changed") else "diam "
                print(f"  {r.get('when','?')}  {mark}  {str(r.get('hash',''))[:12]}")
    except (OSError, ValueError):
        pass
    return 0


def cmd_cost(args) -> int:
    data = _load()
    job = data.get(args.name)
    if not job:
        print(f"'{args.name}' tidak ada.", file=sys.stderr)
        return 1
    runs, fired = job.get("runs", 0), job.get("fired", 0)
    print(f"watcher : {args.name}")
    print(f"  dicek {runs} kali, tapi cuma {fired} kali memanggil model.")
    print(f"  {runs - fired} kali lainnya: skrip murah jalan, hasilnya sama, selesai.")
    print()
    print("  Angka rupiah/dolarnya ada di layar biaya Hermes per profil,")
    print("  bukan di sini — file ini tidak boleh menebak biaya.")
    print("  (aturan angka: setiap angka harus jelas asalnya)")
    return 0


def cmd_rm(args) -> int:
    data = _load()
    if args.name not in data:
        print(f"'{args.name}' tidak ada.", file=sys.stderr)
        return 1
    del data[args.name]
    _save(data)
    print(f"✓ '{args.name}' dihapus dari daftar.")
    print("  Catatan: ini tidak mencabut pendaftaran di penjadwal Hermes.")
    print(f"  Jalankan juga: hermes cronjob delete --name {args.name}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="watch.py",
        description="Kerja terjadwal yang murah waktu diam dan tidak mengulang dirinya.")
    sub = ap.add_subparsers(dest="cmd")

    c = sub.add_parser("create", help="bikin watcher baru")
    c.add_argument("--name", required=True)
    c.add_argument("--check", required=True, help="perintah murah, tanpa model")
    c.add_argument("--every", required=True, help='contoh: "senin 06:00"')
    c.add_argument("--remember", required=True,
                   help="kunci yang harus diingat antar-jalan, dipisah koma (WAJIB)")
    c.add_argument("--deliver", default="telegram", choices=DELIVERIES)
    c.add_argument("--prompt", help="apa yang dikerjakan agen saat ada perubahan")
    c.add_argument("--force", action="store_true")
    c.set_defaults(func=cmd_create)

    t = sub.add_parser("test", help="jalankan cek murahnya sekali, tanpa model")
    t.add_argument("name")
    t.add_argument("--save", action="store_true", help="simpan hash hasilnya")
    t.set_defaults(func=cmd_test)

    for nm, fn, hlp in (("list", cmd_list, "daftar watcher"),
                        ("why", cmd_why, "kenapa bunyi / kenapa diam"),
                        ("cost", cmd_cost, "berapa kali benar-benar manggil model"),
                        ("rm", cmd_rm, "hapus watcher")):
        p = sub.add_parser(nm, help=hlp)
        if nm != "list":
            p.add_argument("name")
        p.set_defaults(func=fn)

    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        ap.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
