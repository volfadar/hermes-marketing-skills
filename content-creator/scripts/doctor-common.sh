#!/usr/bin/env bash
# doctor-common.sh — pemeriksaan yang sama untuk semua skill.
#
# Sebelum ini tiap skill menulis ulang pemeriksaan yang sama (python ada? profil
# terbaca? guard terpasang?), dan `brand-strategy-coach` — pintu masuk utama —
# malah tidak punya `doctor.sh` sama sekali. Ini bagian bersamanya; tiap skill
# memanggilnya lalu menambahkan pemeriksaan khususnya sendiri.
#
#   source "$(dirname "$0")/doctor-common.sh"
#   doctor_common "nama-skill"
#   check "punya API key"  test -n "${FOO_API_KEY:-}"
#   doctor_summary
set -uo pipefail

DOCTOR_FAILS=0
DOCTOR_WARNS=0

check() {   # check "label" <perintah...>
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "  ✓ $label"
  else
    echo "  ✗ $label"
    DOCTOR_FAILS=$((DOCTOR_FAILS + 1))
  fi
}

warn_check() {  # sama, tapi tidak menggagalkan
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "  ✓ $label"
  else
    echo "  ⚠ $label (opsional)"
    DOCTOR_WARNS=$((DOCTOR_WARNS + 1))
  fi
}

doctor_common() {
  local skill_name="${1:-skill}"
  local here; here="$(cd "$(dirname "${BASH_SOURCE[1]}")/.." && pwd)"

  echo "hermes doctor — $skill_name"
  echo ""
  echo "Dasar:"
  check "python3 tersedia"              command -v python3
  check "profil terbaca"                python3 "$here/lib/profile.py" check
  check "aturan disiplin ada"           test -f "$here/references/hermes-discipline.md"
  check "peta runtime Hermes ada"       test -f "$here/references/hermes-runtime.md"

  echo ""
  echo "Penegak (harus ada di TIAP skill, bukan cuma di coach):"
  check "check-numbers.py bisa dijalankan"   test -x "$here/scripts/check-numbers.py"
  check "check-citations.py bisa dijalankan" test -x "$here/scripts/check-citations.py"
  check "artifact-guard.py bisa dijalankan"  test -x "$here/hooks/artifact-guard.py"
  warn_check "guard terpasang di ~/.hermes"  bash "$here/scripts/install-guard.sh" --check

  echo ""
  echo "Rem:"
  if python3 "$here/lib/halt.py" status >/dev/null 2>&1; then
    echo "  ✓ tombol berhenti terbaca — status: JALAN"
  else
    echo "  ⛔ tombol berhenti terbaca — status: SEDANG BERHENTI"
    echo "     (ini bukan error. jalankan: bash scripts/halt.sh status)"
  fi
  echo ""
}

doctor_summary() {
  echo ""
  if [[ "$DOCTOR_FAILS" -eq 0 ]]; then
    echo "doctor: PASS${DOCTOR_WARNS:+ ($DOCTOR_WARNS peringatan)}"
    return 0
  fi
  echo "doctor: $DOCTOR_FAILS masalah" >&2
  echo "Perbaikan paling sering: bash shared/sync.sh" >&2
  return 1
}
