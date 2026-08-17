#!/usr/bin/env bash
# doctor.sh — periksa apakah router ini bisa melihat seluruh state bus.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/doctor-common.sh"

doctor_common "ibras-marketing-orchestrator"

echo "State bus — router ini tidak berguna kalau salah satu tidak terbaca:"
check "profile.py"  test -f "$HERE/lib/profile.py"
check "ledger.py"   test -f "$HERE/lib/ledger.py"
check "handoff.py"  test -f "$HERE/lib/handoff.py"
check "watch.py"    test -f "$HERE/lib/watch.py"
check "halt.py"     test -f "$HERE/lib/halt.py"
check "copycheck.py" test -f "$HERE/lib/copycheck.py"

echo ""
echo "Peta rute:"
check "tools-mapping.md" test -f "$HERE/../references/tools-mapping.md"
check "repliz.md"        test -f "$HERE/../references/repliz.md"
check "hermes-runtime.md" test -f "$HERE/../references/hermes-runtime.md"

doctor_summary
