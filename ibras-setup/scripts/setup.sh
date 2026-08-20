#!/usr/bin/env bash
# setup.sh — one preflight for a Hermes install, in dependency order.
#
#   bash setup.sh          check only, changes nothing
#   bash setup.sh --fix    do the safe ones, print commands for the rest
#
# Exit 0 = every REQUIRED check passed. Exit 1 = something required is missing.
# Optional components (WAHA, SMTP, pillars) never fail the run; they report.
set -uo pipefail

FIX="no"
[[ "${1:-}" == "--fix" ]] && FIX="yes"

HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
CFG="$HOME_DIR/config.yaml"
BIZ="${HERMES_BUSINESS_DIR:-$HOME_DIR/business}"
PORT="${CLOAKSERVE_PORT:-9222}"
SK="$HOME_DIR/skills"

req_ok=0; req_bad=0; opt_missing=0
declare -a TODO

b()  { printf '\n\033[1;36m━━ %s ━━\033[0m\n' "$1"; }
ok() { printf '  \033[1;32m✓\033[0m %s\n' "$1"; req_ok=$((req_ok+1)); }
bad(){ printf '  \033[1;31m✗\033[0m %s\n' "$1"; req_bad=$((req_bad+1)); [[ -n "${2:-}" ]] && TODO+=("$2"); }
opt(){ printf '  \033[1;33m○\033[0m %s\n' "$1"; opt_missing=$((opt_missing+1)); [[ -n "${2:-}" ]] && TODO+=("$2"); }
note(){ printf '      %s\n' "$1"; }

echo "hermes setup — HERMES_HOME=$HOME_DIR"

# ---------------------------------------------------------------- 1. core ---
b "1. Inti — tanpa ini sisanya tidak berarti"

if command -v hermes >/dev/null 2>&1; then ok "hermes: $(hermes --version 2>&1 | head -1)"
else bad "hermes tidak ada di PATH" "curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"; fi

command -v python3 >/dev/null 2>&1 && ok "python3: $(python3 -V 2>&1)" \
  || bad "python3 tidak ada" "pasang python3 lewat paket manager OS kamu"

python3 -c "import yaml" 2>/dev/null && ok "PyYAML ada" || {
  if [[ "$FIX" == "yes" ]] && pip3 install --quiet pyyaml 2>/dev/null; then ok "PyYAML dipasang"
  else bad "PyYAML tidak ada — profil tidak akan kebaca" "pip3 install pyyaml"; fi; }

# model.default: the one that masquerades as a broken skill
if [[ -f "$CFG" ]] && python3 - "$CFG" <<'PY' 2>/dev/null
import sys, yaml
c = yaml.safe_load(open(sys.argv[1])) or {}
d = ((c.get("model") or {}).get("default") or "").strip()
sys.exit(0 if d else 1)
PY
then ok "model.default: $(python3 -c "import yaml,sys;print((yaml.safe_load(open('$CFG')) or {}).get('model',{}).get('default',''))" 2>/dev/null)"
else
  bad "model.default kosong — Hermes akan balas '404 tool-use' dan itu kelihatan seperti skill rusak" \
      "hermes setup --portal    # atau: hermes model"
fi

# ------------------------------------------------------------- 2. browser ---
b "2. Browser / CDP — dipakai riset dan cek harga oleh coach"

cdp_up() { curl -sf --max-time 3 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; }

if cdp_up; then
  ok "CDP hidup di port $PORT — $(curl -sf --max-time 3 http://127.0.0.1:${PORT}/json/version | python3 -c 'import json,sys;print(json.load(sys.stdin).get("Browser",""))' 2>/dev/null)"
else
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    bad "CDP mati, tapi Docker ada — pakai cloakserve (fingerprint Asia/Jakarta + id-ID)" \
        "bash $SK/ibras-cloakserve-research/scripts/start.sh"
  else
    CHROME="$(find "$HOME/.cache/ms-playwright" -name chrome -type f 2>/dev/null | head -1)"
    if [[ -z "$CHROME" ]]; then
      if [[ -d "$HOME/.cache/ms-playwright" ]]; then
        note "folder ms-playwright ADA tapi biner 'chrome' tidak — instalasi setengah jadi, ini kelihatan seperti terpasang"
      fi
      if [[ "$FIX" == "yes" ]]; then
        echo "      memasang chromium…"
        npx -y playwright@latest install chromium >/dev/null 2>&1
        CHROME="$(find "$HOME/.cache/ms-playwright" -name chrome -type f 2>/dev/null | head -1)"
      fi
    fi
    if [[ -z "$CHROME" ]]; then
      bad "tidak ada browser sama sekali" "npx playwright install chromium"
    else
      ok "biner chromium ada: $("$CHROME" --version 2>&1 | head -1)"
      if [[ "$FIX" == "yes" ]]; then
        nohup "$CHROME" --headless=new --no-sandbox --disable-gpu \
          --remote-debugging-port="$PORT" --remote-debugging-address=127.0.0.1 \
          --lang=id-ID --user-data-dir=/tmp/cdp-profile >/tmp/chrome-cdp.log 2>&1 &
        for _ in 1 2 3 4 5 6 7 8; do cdp_up && break; sleep 1; done
      fi
      cdp_up && ok "CDP hidup di port $PORT" \
             || bad "biner ada tapi tidak ada yang mendengarkan di $PORT — memasang saja tidak cukup" \
                    "\"$CHROME\" --headless=new --no-sandbox --remote-debugging-port=$PORT --lang=id-ID --user-data-dir=/tmp/cdp-profile &"
    fi
  fi
fi

# wiring is separate from running, and skipping it leaves the browser dead
WIRED="$(python3 - "$CFG" <<'PY' 2>/dev/null
import sys, yaml
try: c = yaml.safe_load(open(sys.argv[1])) or {}
except Exception: c = {}
b = c.get("browser") or {}
print("yes" if (b.get("cdp_url") and b.get("enabled")) else "no")
PY
)"
if [[ "$WIRED" == "yes" ]]; then ok "Hermes diarahkan ke CDP (browser.cdp_url + enabled)"
else
  W="$SK/ibras-cloakserve-research/scripts/wire-hermes.sh"
  if [[ "$FIX" == "yes" && -f "$W" ]] && bash "$W" --port "$PORT" --quiet >/dev/null 2>&1; then
    ok "Hermes diarahkan ke CDP"
  else
    bad "browser.cdp_url belum di-set — browser tetap mati walau binernya ada" \
        "bash $W --port $PORT"
  fi
fi

# ------------------------------------------------------ 3. optional config ---
b "3. Config per-skill — boleh dilewat, tapi tahu yang kamu lewatkan"

[[ -d "$BIZ" ]] || { [[ "$FIX" == "yes" ]] && mkdir -p "$BIZ"; }
[[ -d "$BIZ" ]] && ok "folder business: $BIZ" || opt "folder business belum ada" "mkdir -p $BIZ"

WCFG="${WAHA_CONFIG_DIR:-${HERMES_HOME:-$HOME}/.waha-marketing}/config.env"
if [[ -f "$WCFG" ]]; then ok "WAHA terkonfigurasi"
else opt "WAHA belum diset — skill WhatsApp akan menolak semua aksi" \
         "bash $SK/ibras-setup/scripts/waha.sh          # jalankan WAHA lokal (gratis sejak 2026.6.1)"; fi

ECFG="${HERMES_EMAIL_CONFIG_DIR:-$HOME/.hermes-email}/config.env"
if [[ -f "$ECFG" ]]; then ok "email/SMTP terkonfigurasi"
else opt "SMTP belum diset — skill email tidak bisa baca/draft" \
         "bash $SK/ibras-setup/scripts/smtp.sh"; fi

if [[ -f "$BIZ/faq.yaml" ]]; then ok "faq.yaml ada"
else
  SRC="$SK/ibras-email-marketing/templates/faq.example.yaml"
  if [[ "$FIX" == "yes" && -f "$SRC" ]]; then cp "$SRC" "$BIZ/faq.yaml" && ok "faq.yaml disalin dari contoh"
  else opt "faq.yaml belum ada — mode balas email belum bisa jalan" "cp $SRC $BIZ/faq.yaml"; fi
fi

# ------------------------------------------- 3b. skills are DISCOVERABLE ---
# A skill on disk is not a skill Hermes can see. Invalid YAML frontmatter (an
# unquoted colon is enough) makes Hermes skip it silently during discovery —
# no error, no warning, the skill simply never fires. This caught
# ibras-waha-marketing on 2026-08-20. See DECISIONS.md D6.
b "3b. Skill terbaca oleh Hermes"
if python3 -c "import yaml" >/dev/null 2>&1; then
  bad=0
  for d in "$SK"/ibras-*/; do
    n="$(basename "$d")"; [[ -f "$d/SKILL.md" ]] || continue
    if ! HERMES_SKILL_DIR="$d" python3 - "$d/SKILL.md" "$n" <<'PYX' >/dev/null 2>&1
import sys, re, yaml
t = open(sys.argv[1], encoding="utf-8").read()
m = re.match(r"^---\n(.*?)\n---", t, re.S)
d = yaml.safe_load(m.group(1))
assert isinstance(d, dict) and d.get("name") == sys.argv[2] and str(d.get("description","")).strip()
PYX
    then
      bad "$n: frontmatter tidak terbaca — Hermes akan melewatinya diam-diam" \
          "cek tanda titik dua tanpa kutip di description:, dan name: harus sama dengan nama folder"
      bad=$((bad+1))
    fi
  done
  [[ $bad -eq 0 ]] && ok "semua skill punya frontmatter yang valid"
else
  opt "pyyaml belum ada — lewati cek discoverability" "pip3 install pyyaml"
fi

# The router must name every installed skill, or people get sent to the wrong
# place forever and nothing errors. See DECISIONS.md and shared/tests/test_router.py.
ORCH="$SK/ibras-marketing-orchestrator/SKILL.md"
if [[ -f "$ORCH" ]]; then
  miss=0
  for d in "$SK"/ibras-*/; do
    n="$(basename "$d")"; [[ "$n" == "ibras-marketing-orchestrator" ]] && continue
    grep -q -- "$n" "$ORCH" || { opt "router belum menyebut $n" "tambahkan $n ke tabel rute di ibras-marketing-orchestrator"; miss=$((miss+1)); }
  done
  [[ $miss -eq 0 ]] && ok "router menyebut semua skill terpasang"
fi

# ------------------------------------------------------------ 4. doctors ---
b "4. Doctor tiap skill"
for d in "$SK"/ibras-*/; do
  n="$(basename "$d")"; [[ "$n" == "ibras-setup" ]] && continue
  if [[ -f "$d/scripts/doctor.sh" ]]; then
    out="$(HERMES_HOME="$HOME_DIR" timeout 25 bash "$d/scripts/doctor.sh" 2>&1 || true)"
    f="$(printf '%s' "$out" | grep -c '✗' || true)"
    w="$(printf '%s' "$out" | grep -c '⚠' || true)"
    if [[ "$f" -eq 0 ]]; then printf '  \033[1;32m✓\033[0m %-38s bersih (%s peringatan)\n' "$n" "$w"
    else printf '  \033[1;31m✗\033[0m %-38s %s gagal, %s peringatan  → bash %sscripts/doctor.sh\n' "$n" "$f" "$w" "$d"; fi
  else printf '  \033[1;33m○\033[0m %-38s tidak punya doctor.sh\n' "$n"; fi
done

# ------------------------------------------------------------- summary -----
b "Yang harus kamu jalankan, berurutan"
if [[ ${#TODO[@]} -eq 0 ]]; then
  echo "  (tidak ada — semuanya siap)"
else
  i=1; for t in "${TODO[@]}"; do printf '  %d. %s\n' "$i" "$t"; i=$((i+1)); done
fi
printf '\n  wajib: %d ok, %d gagal   ·   opsional belum diset: %d\n' "$req_ok" "$req_bad" "$opt_missing"
[[ "$FIX" == "no" && "$req_bad" -gt 0 ]] && echo "  (coba: bash setup.sh --fix — yang aman dikerjakan otomatis)"
exit $(( req_bad > 0 ? 1 : 0 ))
