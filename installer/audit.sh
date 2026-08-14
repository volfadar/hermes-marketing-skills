#!/usr/bin/env bash
# audit.sh — gerbang kebocoran sebelum skill ini dibagikan.
#
# Repo pengembangan (workshop) memuat materi kursus, persona, dan eval yang
# TIDAK boleh ikut ke repo distribusi ini. Audit ini memindai isi repo
# terhadap daftar-hitam: ID sesi eval internal, kode model uji, istilah
# metodologi eval, pointer ke file materi kursus, nama persona workshop,
# dan path internal. Gagal (exit 1) kalau ada yang cocok.
#
#   bash installer/audit.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

status=0

deny() {  # deny <label> <egrep-pattern>
  local label="$1" pattern="$2" hits
  hits=$(grep -rInE "$pattern" --include='*' . \
    --exclude-dir=.git --exclude-dir=dist --exclude-dir=__pycache__ \
    --exclude='*.pyc' --exclude='audit.sh' \
    --exclude='MAINTENANCE.md' --exclude='sync-from-source.sh' 2>/dev/null || true)
  if [[ -n "$hits" ]]; then
    echo "✗ LEAK [$label]"; echo "$hits" | head -8
    status=1
  fi
}

# ID sesi eval internal + kode model uji
deny "session-id"      '\bs[0-9]+-[a-z0-9]+-(yuni|joko|ayu|galih|teguh|maya|aisyah)'
deny "model-code"      '\b(dspro|hy3)\b'
# Metodologi / artefak eval
deny "eval-terms"      'eval scoreboard|eval corpus|eval session|in the eval|during the .*eval|forward test|evaluation repository|agent-to-agent'
# Pointer ke materi kursus
deny "course-pointer"  'materi workshop|5-tangga|bank-contoh|lembar-kerja|RANCANGAN|workshop-playbook|workshop-research|workshop-personas|workshop-id-section'
deny "course-cost"     'Pemakaian workshop|\$[0-9][^|]*per peserta'
# Path internal repo pengembangan
deny "internal-path"   'hermes-for-marketing|/root/'
# Nama persona workshop (persona sintetis milik skill, mis. Dini, boleh)
deny "persona"         'Sekar Ayu|Galih Pamungkas|Yuni Karlina|Teguh Wijaya|Maya Saraswati|Aisyah Dhiya|Kopi Ngarai'
# Model tertentu di kutipan temuan (pilihan model di tabel biaya adalah konten sah)
deny "eval-finding"    'DeepSeek V4 Pro'

# File sampah Python tidak boleh ikut
junk=$(find . -name '__pycache__' -o -name '*.pyc' | grep -v '.git' || true)
if [[ -n "$junk" ]]; then echo "✗ LEAK [pycache]"; echo "$junk" | head -5; status=1; fi

# Laporan lunak: kata "workshop" boleh ada sebagai suara produk, tapi
# tampil di sini supaya perubahan terlihat.
soft=$(grep -rIn 'workshop' --include='*.md' --include='*.py' --include='*.sh' . \
  --exclude-dir=.git --exclude-dir=dist 2>/dev/null \
  | grep -v 'audit.sh' | grep -v 'MAINTENANCE.md' | grep -v 'sync-from-source.sh' || true)
if [[ -n "$soft" ]]; then
  echo "— info: penyebutan 'workshop' (${#soft} baris) — suara produk, periksa kalau mau hilangkan:"
  echo "$soft" | head -5
fi

if [[ $status -eq 0 ]]; then echo "audit: BERSIH"; else echo "audit: GAGAL — bersihkan sebelum membagikan."; fi
exit $status
