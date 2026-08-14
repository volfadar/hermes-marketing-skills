#!/usr/bin/env bash
# sync-discipline.sh — SHIM. Kept so existing callers and the contract test keep working.
#
# The discipline file is no longer canonical here. It moved to
# `shared/references/hermes-discipline.md` and is mirrored by `shared/sync.sh`
# together with the enforcers it tells the agent to run — check-numbers.py,
# check-citations.py and artifact-guard.py — which used to exist in this skill only.
#
# Two sync mechanisms for one job is the duplication this repo keeps warning about,
# so there is one now. This file just forwards.
#
#   bash scripts/sync-discipline.sh          # -> shared/sync.sh
#   bash scripts/sync-discipline.sh --check  # -> shared/sync.sh --check
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SYNC="$ROOT_DIR/shared/sync.sh"

if [[ ! -f "$SYNC" ]]; then
  echo "FAIL: $SYNC tidak ada — shared layer hilang." >&2
  exit 1
fi

echo "note: sync-discipline.sh sekarang meneruskan ke shared/sync.sh" >&2
exec bash "$SYNC" "${1:---write}"
