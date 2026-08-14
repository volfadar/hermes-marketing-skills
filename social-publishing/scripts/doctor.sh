#!/usr/bin/env bash
# doctor.sh — periksa isi skill ini: data lengkap, sumber tidak kedaluwarsa,
# referensi silang antar-berkas tidak putus.
#
# Skill ini tidak menyambung ke layanan apa pun, jadi tidak ada koneksi yang
# perlu dites. Yang perlu dites adalah apakah isinya masih benar.
set -uo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

PASS=0; WARN=0; FAIL=0
ok()    { PASS=$((PASS+1)); printf '  \033[1;32m✓\033[0m %s\n' "$1"; }
p_warn(){ WARN=$((WARN+1)); printf '  \033[1;33m⚠\033[0m %s\n' "$1"; }
p_fail(){ FAIL=$((FAIL+1)); printf '  \033[1;31m✗\033[0m %s\n' "$1"; }
hdr()   { printf '\n\033[1;36m━━ %s ━━\033[0m\n' "$1"; }

hdr "1. Dependensi"
command -v python3 >/dev/null && ok "python3 ada" || p_fail "python3 tidak ada"
python3 -c "import yaml" 2>/dev/null && ok "PyYAML ada" || p_fail "PyYAML belum ada: pip3 install pyyaml"

hdr "2. Berkas data"
for f in options.yaml platforms.yaml sources.yaml; do
  if [[ -f "$SKILL_DIR/data/$f" ]]; then
    if python3 -c "import yaml,sys; yaml.safe_load(open('$SKILL_DIR/data/$f',encoding='utf-8'))" 2>/dev/null; then
      ok "data/$f valid"
    else
      p_fail "data/$f ada tapi YAML-nya rusak"
    fi
  else
    p_fail "data/$f hilang"
  fi
done

hdr "3. Keutuhan isi"
INTEGRITY_OUT="$(python3 - "$SKILL_DIR" <<'PY'
import sys, yaml, datetime
from pathlib import Path

root = Path(sys.argv[1])
ok = lambda m: print(f"  \033[1;32m✓\033[0m {m}")
warn = lambda m: print(f"  \033[1;33m⚠\033[0m {m}")
fail = lambda m: print(f"  \033[1;31m✗\033[0m {m}")

opts = yaml.safe_load((root/"data/options.yaml").read_text(encoding="utf-8"))
srcs = yaml.safe_load((root/"data/sources.yaml").read_text(encoding="utf-8"))
plats = yaml.safe_load((root/"data/platforms.yaml").read_text(encoding="utf-8"))

src_ids = {s["id"] for s in srcs["sources"]}
opt_ids = {o["id"] for o in opts["options"]}

# setiap evidence: harus menunjuk sumber yang ada
broken = [(o["id"], e) for o in opts["options"] for e in (o.get("evidence") or []) if e not in src_ids]
if broken:
    for oid, e in broken:
        fail(f"opsi '{oid}' menunjuk sumber '{e}' yang tidak ada di sources.yaml")
else:
    ok("semua rujukan bukti menunjuk sumber yang ada")

# setiap alternative: harus menunjuk opsi yang ada
broken = [(o["id"], a) for o in opts["options"] for a in (o.get("alternatives") or []) if a not in opt_ids]
if broken:
    for oid, a in broken:
        fail(f"opsi '{oid}' menunjuk alternatif '{a}' yang tidak ada")
else:
    ok("semua rujukan alternatif menunjuk opsi yang ada")

# setiap opsi punya kerugian yang ditulis — ini inti skill-nya
thin = [o["id"] for o in opts["options"] if len(o.get("drawbacks") or []) < 3]
if thin:
    for oid in thin:
        fail(f"opsi '{oid}' punya kurang dari 3 kerugian tertulis — itu iklan, bukan nasihat")
else:
    ok("setiap opsi punya minimal 3 kerugian tertulis")

# umur verifikasi sumber
today = datetime.date.today()
stale = []
for s in srcs["sources"]:
    try:
        d = datetime.date.fromisoformat(str(s["verified"]))
    except Exception:
        continue
    age = (today - d).days
    if age > 90:
        stale.append((s["id"], age))
if stale:
    for sid, age in stale:
        warn(f"sumber '{sid}' terakhir dicek {age} hari lalu — buka lagi sebelum dipakai mengajar")
else:
    ok("semua sumber dicek dalam 90 hari terakhir")

# platform yang sengaja kosong
unver = [p["id"] for p in plats["platforms"] if not p.get("verified")]
if unver:
    warn(f"platform belum diverifikasi (sengaja, jangan dikutip): {', '.join(unver)}")
else:
    ok("semua platform punya tanggal verifikasi")
PY
)"
printf '%s\n' "$INTEGRITY_OUT"
# hitung hasil blok di atas ke dalam ringkasan
PASS=$((PASS + $(grep -c '✓' <<<"$INTEGRITY_OUT")))
WARN=$((WARN + $(grep -c '⚠' <<<"$INTEGRITY_OUT")))
FAIL=$((FAIL + $(grep -c '✗' <<<"$INTEGRITY_OUT")))

hdr "4. Dokumen referensi"
for f in jalur.md research-digest.md platform-limits.md publishing-architecture.md \
         browser-tailscale.md tiers.md ethics.md hermes-discipline.md; do
  [[ -f "$SKILL_DIR/references/$f" ]] && ok "references/$f" || p_fail "references/$f hilang"
done

hdr "5. Uji cepat advisor"
if python3 "$SKILL_DIR/lib/advisor.py" options >/dev/null 2>&1; then
  ok "advisor.py options jalan"
else
  p_fail "advisor.py options gagal"
fi
if python3 "$SKILL_DIR/lib/advisor.py" recommend --budget 5 >/dev/null 2>&1; then
  ok "advisor.py recommend jalan"
else
  p_fail "advisor.py recommend gagal"
fi

printf '\n\033[1;36m━━ Ringkasan ━━\033[0m  \033[1;32m%d OK\033[0m  \033[1;33m%d warn\033[0m  \033[1;31m%d fail\033[0m\n' "$PASS" "$WARN" "$FAIL"
[[ "$FAIL" -gt 0 ]] && exit 1
exit 0
