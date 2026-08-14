#!/usr/bin/env bash
# wire-hermes.sh — point Hermes's browser tool at the cloakserve CDP endpoint.
# Safe: only edits the `browser:` mapping. Preserves model, gateway, etc.
# Usage: bash wire-hermes.sh [--port 9222] [--quiet]
set -euo pipefail
PORT="${CLOAKSERVE_PORT:-9222}"
QUIET="no"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    --quiet) QUIET="yes"; shift ;;
    -h|--help) sed -n '2,4p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

HERMES_HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
CFG="${HERMES_HOME_DIR}/config.yaml"
mkdir -p "${HERMES_HOME_DIR}"
[[ -f "${CFG}" ]] || printf '' > "${CFG}"
CDP_URL="ws://127.0.0.1:${PORT}"

[[ "$QUIET" == "yes" ]] || echo "[wire] setting browser.cdp_url=${CDP_URL}, browser.enabled=true"

# Try Hermes's own config CLI (handles nested keys + may notify running gateway).
if command -v hermes >/dev/null 2>&1; then
  HERMES_HOME="${HERMES_HOME_DIR}" hermes config set browser.cdp_url "${CDP_URL}" >/dev/null 2>&1 || true
  HERMES_HOME="${HERMES_HOME_DIR}" hermes config set browser.enabled true >/dev/null 2>&1 || true
fi

# YAML-aware editor: only touches the `browser:` mapping. Preserves everything else.
python3 - "$CFG" "$CDP_URL" <<'PY'
import sys, re
cfg_path, cdp_url = sys.argv[1], sys.argv[2]
with open(cfg_path) as f:
    lines = f.readlines()

def find_block(name):
    start = None
    for i, ln in enumerate(lines):
        s = ln.rstrip('\n')
        if (s == name + ':' or s.startswith(name + ':')) and not ln[0].isspace():
            start = i; break
    if start is None: return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        ln2 = lines[j]
        if ln2.strip() == '' or ln2.startswith('#'): continue
        if not ln2[0].isspace():
            end = j; break
    return (start, end)

def set_in_block(br, key, value):
    s, e = br
    pat = f'  {key}:'
    for i in range(s + 1, e):
        if lines[i].rstrip('\n').startswith(pat):
            lines[i] = f'  {key}: {value}\n'; return
    lines.insert(s + 1, f'  {key}: {value}\n')

br = find_block('browser')
if br is None:
    if lines and not lines[-1].endswith('\n'): lines[-1] += '\n'
    if lines and lines[-1].strip() != '': lines.append('\n')
    lines.append('browser:\n')
    lines.append(f'  cdp_url: {cdp_url}\n')
    lines.append('  enabled: true\n')
else:
    set_in_block(br, 'cdp_url', cdp_url)
    set_in_block(br, 'enabled', 'true')

with open(cfg_path, 'w') as f:
    f.writelines(lines)
PY

if [[ "$QUIET" != "yes" ]]; then
  echo "wired: yes"
  echo "cdp_url: ${CDP_URL}  (in ${CFG})"
  echo "other config preserved (model, gateway, etc.)"
fi
