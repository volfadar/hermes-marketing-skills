#!/usr/bin/env bash
# doctor.sh — periksa apakah skill ini siap dipakai.
#
# Skill ini pintu masuk utama workshop dan justru satu-satunya yang dulu tidak punya
# doctor. Orang yang bingung menjalankan `doctor` duluan; kalau tidak ada, dia
# menyimpulkan skill-nya rusak.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/doctor-common.sh"

doctor_common "brand-strategy-coach"

echo "Khusus skill ini:"
check "profil bisnis bisa dibaca"       python3 "$HERE/../lib/profile.py" show
check "template stage lengkap"          test -d "$HERE/../templates"
check "referensi positioning ada"       test -f "$HERE/../references/positioning-lab.md"
check "referensi ekonomi ada"           test -f "$HERE/../references/economics-and-goal-fit.md"
check "peta pemilihan tool ada"         test -f "$HERE/../references/tools-mapping.md"
warn_check "preflight bisa dijalankan"  test -x "$HERE/preflight.sh"

echo ""
echo "Pertanyaan berikutnya yang belum terjawab di profil:"
python3 "$HERE/../lib/profile.py" missing 2>/dev/null | head -3 || echo "  (profil belum ada — mulai sesi dulu)"

doctor_summary
