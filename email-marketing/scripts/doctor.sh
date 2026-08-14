#!/usr/bin/env bash
# doctor.sh — diagnosa koneksi email + kesiapan balasan otomatis.
set -uo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CFG_DIR="${HERMES_EMAIL_CONFIG_DIR:-$HOME/.hermes-email}"
CFG="$CFG_DIR/config.env"
BIZ_DIR="${HERMES_BUSINESS_DIR:-$HOME/.hermes/business}"
HALT="${HERMES_EMAIL_HALT_FILE:-/tmp/hermes-email-halt}"

PASS=0; WARN=0; FAIL=0
ok()    { PASS=$((PASS+1)); printf '  \033[1;32m✓\033[0m %s\n' "$1"; }
p_warn(){ WARN=$((WARN+1)); printf '  \033[1;33m⚠\033[0m %s\n' "$1"; }
p_fail(){ FAIL=$((FAIL+1)); printf '  \033[1;31m✗\033[0m %s\n' "$1"; }
hdr()   { printf '\n\033[1;36m━━ %s ━━\033[0m\n' "$1"; }

hdr "1. Config"
if [[ -f "$CFG" ]]; then
  ok "Config: $CFG"
  PERM=$(stat -c "%a" "$CFG" 2>/dev/null || stat -f "%Lp" "$CFG" 2>/dev/null || echo "?")
  [[ "$PERM" == "600" ]] && ok "Permission 600 (app password tidak terbaca user lain)" \
                         || p_warn "Permission $PERM — sebaiknya 600: chmod 600 $CFG"
  # shellcheck disable=SC1090
  source "$CFG"
  [[ -n "${EMAIL_ADDRESS:-}" ]] && ok "EMAIL_ADDRESS: $EMAIL_ADDRESS" || p_fail "EMAIL_ADDRESS kosong"
  [[ -n "${EMAIL_APP_PASSWORD:-}" ]] && ok "App password terisi (disembunyikan)" || p_fail "App password kosong"
  ok "IMAP ${IMAP_HOST:-?}:${IMAP_PORT:-?}  ·  SMTP ${SMTP_HOST:-?}:${SMTP_PORT:-?}"
  if [[ "${EMAIL_PROVIDER:-}" == "gmail" || "${EMAIL_PROVIDER:-}" == "workspace" ]]; then
    LEN=${#EMAIL_APP_PASSWORD}
    [[ "$LEN" -eq 16 ]] && ok "Panjang app password 16 (khas Gmail)" \
                        || p_warn "Panjang app password $LEN, bukan 16 — cek references/gmail-setup.md"
  fi
else
  p_fail "Belum ada config. Jalankan: bash scripts/initialize.sh --email ... --app-password ..."
fi

hdr "2. Dependensi"
command -v python3 >/dev/null && ok "python3 ada" || p_fail "python3 tidak ada"
python3 -c "import imaplib, smtplib, email" 2>/dev/null && ok "modul email stdlib ada" || p_fail "stdlib email bermasalah"
python3 -c "import yaml" 2>/dev/null && ok "PyYAML ada" || p_fail "PyYAML belum ada: pip3 install pyyaml"

hdr "3. Koneksi"
if [[ -f "$CFG" ]]; then
  if python3 "$SKILL_DIR/lib/mailbox.py" test >/tmp/hermes-email-doctor.log 2>&1; then
    ok "IMAP login OK"
    ok "SMTP login OK"
    grep -E "INBOX berisi|folder terdeteksi" /tmp/hermes-email-doctor.log | sed 's/^ *✓ */    /'
  else
    p_fail "Koneksi gagal — detail:"
    sed 's/^/      /' /tmp/hermes-email-doctor.log | tail -12
    echo "      Penyebab tersering: pakai password akun, bukan App Password 16 digit."
    echo "      Baca: references/gmail-setup.md"
  fi
fi

hdr "4. Kesiapan balasan otomatis"
if [[ -f "$BIZ_DIR/faq.yaml" ]]; then
  ok "faq.yaml ada: $BIZ_DIR/faq.yaml"
  N=$(python3 -c "
import yaml,sys
d=yaml.safe_load(open('$BIZ_DIR/faq.yaml',encoding='utf-8')) or {}
print(len(d.get('entries') or []))" 2>/dev/null || echo 0)
  [[ "$N" -ge 5 ]] && ok "$N entri FAQ" \
                   || p_warn "$N entri FAQ — di bawah 5 biasanya belum menutup inbox nyata"
  TH=$(python3 -c "
import yaml
d=yaml.safe_load(open('$BIZ_DIR/faq.yaml',encoding='utf-8')) or {}
print((d.get('meta') or {}).get('confidence_threshold','0.75'))" 2>/dev/null || echo "?")
  ok "Ambang keyakinan: $TH"
else
  p_warn "faq.yaml belum ada — mode faq/blind belum bisa jalan (mode draft juga butuh ini)"
  echo "      cp $SKILL_DIR/templates/faq.example.yaml $BIZ_DIR/faq.yaml"
fi

if [[ -f "$HALT" ]]; then
  p_fail "HALT file ada ($HALT) — semua pengiriman otomatis berhenti"
  echo "      Hapus untuk melanjutkan: rm $HALT"
else
  ok "Tidak ada HALT file"
fi

[[ -f "$BIZ_DIR/auto-log.jsonl" ]] && ok "Audit log ada ($(wc -l < "$BIZ_DIR/auto-log.jsonl") baris)" \
                                   || p_warn "Belum ada audit log (normal kalau belum pernah kirim)"
[[ -f "$BIZ_DIR/escalations.jsonl" ]] && ok "Escalation log ada ($(wc -l < "$BIZ_DIR/escalations.jsonl") baris)" \
                                      || p_warn "Belum ada escalation log"

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for f in profile.py ledger.py handoff.py; do
  [[ -f "$SKILL_ROOT/lib/$f" ]] && ok "lib/$f ada" \
    || p_fail "lib/$f hilang — jalankan: bash shared/sync.sh"
done
# An unanswered queue is the failure mode that makes "always escalates" mean
# "never answered". Say the number out loud so it does not quietly grow.
if [[ -f "$SKILL_ROOT/lib/handoff.py" ]]; then
  QN="$(python3 "$SKILL_ROOT/lib/handoff.py" list 2>/dev/null | grep -cE '^  \[[0-9]+\]' || true)"
  if [[ "${QN:-0}" -gt 0 ]]; then
    p_warn "$QN chat nunggu jawaban pemiliknya — bersihkan: python3 lib/handoff.py list"
  else
    ok "Antrean handoff kosong"
  fi
fi
python3 "$SKILL_ROOT/lib/profile.py" check >/dev/null 2>&1 \
  && ok "Profil usaha terbaca" \
  || p_warn "Profil usaha belum ada/rusak — semua tetap jalan, tapi Hermes nggak tahu harga kamu"

printf '\n\033[1;36m━━ Ringkasan ━━\033[0m  \033[1;32m%d OK\033[0m  \033[1;33m%d warn\033[0m  \033[1;31m%d fail\033[0m\n' "$PASS" "$WARN" "$FAIL"
[[ "$FAIL" -gt 0 ]] && exit 1
exit 0
