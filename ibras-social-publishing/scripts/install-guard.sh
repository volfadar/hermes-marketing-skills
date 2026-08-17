#!/usr/bin/env bash
# install-guard.sh — wire artifact-guard.py into a Hermes home as a pre_tool_call hook.
#
# The guard blocks a deliverable that breaks a rule the model already read. It exists
# because recorded sessions showed the rules being read and then broken ~120 messages
# later, at the moment of the write. Checks that run at the write moment survive that
# distance; prose at session start does not.
#
#   install-guard.sh [--home DIR] [--output-dir DIR] [--check]
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
GUARD="$SKILL_DIR/scripts/hooks/artifact-guard.py"
HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
OUT_DIR=""
MODE=install

while [[ $# -gt 0 ]]; do
  case "$1" in
    --home)       HOME_DIR="$2"; shift 2 ;;
    --output-dir) OUT_DIR="$2";  shift 2 ;;
    --check)      MODE=check;    shift ;;
    -h|--help)    sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

test -f "$GUARD" || { echo "FAIL: missing $GUARD" >&2; exit 1; }
chmod +x "$GUARD"

CFG="$HOME_DIR/config.yaml"

if [[ "$MODE" == check ]]; then
  grep -q 'artifact-guard.py' "$CFG" 2>/dev/null \
    || { echo "FAIL: artifact-guard not wired into $CFG" >&2; exit 1; }
  echo "artifact guard: wired"
  exit 0
fi

mkdir -p "$HOME_DIR"
if grep -q 'artifact-guard.py' "$CFG" 2>/dev/null; then
  echo "artifact guard: already wired in $CFG"
else
  cat >> "$CFG" <<YAML
hooks:
  pre_tool_call:
    - matcher: "write_file|patch|create_file|edit_file|apply_patch"
      command: "$GUARD"
      timeout: 15
YAML
  echo "artifact guard: wired into $CFG"
fi

# A write has nowhere legitimate to land unless the run declares one. Without this
# the LOCATION check is inert — which is how consecutive runs saved session
# artifacts into whatever directory the model was sitting in.
if [[ -n "$OUT_DIR" ]]; then
  mkdir -p "$OUT_DIR"
  echo "output dir: $OUT_DIR (export HERMES_OUTPUT_DIR=$OUT_DIR before running)"
fi

# The allowlist gates first use of every (event, command) pair. A non-TTY run has no
# prompt to answer, so an unapproved hook is skipped *silently* — the failure mode that
# makes a guarded run indistinguishable from an unguarded one. Approve it explicitly and
# verify with `hermes hooks doctor` before trusting any run.
ALLOW="$HOME_DIR/shell-hooks-allowlist.json"
python3 - "$ALLOW" "$GUARD" <<'PY'
import json, pathlib, sys
path, guard = pathlib.Path(sys.argv[1]), sys.argv[2]
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
if not isinstance(data, dict):
    data = {}
approvals = data.setdefault("approvals", [])
entry = {"event": "pre_tool_call", "command": guard}
if entry not in approvals:
    approvals.append(entry)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(data, indent=2))
print(f"allowlisted: {guard}")
PY

hermes hooks doctor 2>&1 | grep -q '✗' \
  && { echo "FAIL: hook not live — see 'hermes hooks doctor'" >&2; exit 1; }
echo "artifact guard: live"
