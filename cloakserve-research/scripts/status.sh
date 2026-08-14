#!/usr/bin/env bash
# status.sh — compact status. Use --logs for container logs.
# Usage: bash status.sh [--logs]
set -euo pipefail
PORT="${CLOAKSERVE_PORT:-9222}"
CONTAINER_NAME="${CLOAKSERVE_CONTAINER:-cloakserve}"
HERMES_HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
CFG="${HERMES_HOME_DIR}/config.yaml"

echo "=== cloakserve container ==="
if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "${CONTAINER_NAME}"; then
  echo "container: running (${CONTAINER_NAME})"
else
  echo "container: NOT running"
fi

echo ""
echo "=== CDP endpoint (port ${PORT}) ==="
if VER=$(curl -sf --max-time 3 "http://127.0.0.1:${PORT}/json/version" 2>/dev/null); then
  echo "cdp: reachable"
  echo "$VER" | python3 -c "import sys,json; d=json.load(sys.stdin); print('browser:', d.get('Browser')); print('user-agent:', d.get('User-Agent'))" 2>/dev/null
  echo "cdp_url: ws://127.0.0.1:${PORT}"
else
  echo "cdp: NOT reachable on port ${PORT}"
fi

echo ""
echo "=== Hermes wiring ==="
if [[ -f "$CFG" ]]; then
  if grep -q "cdp_url" "$CFG" 2>/dev/null; then
    echo "wired: yes ($(grep cdp_url "$CFG" | head -1 | xargs))"
  else
    echo "wired: no — run: bash $(dirname "$0")/wire-hermes.sh"
  fi
else
  echo "wired: unknown (no config.yaml at $HERMES_HOME_DIR)"
fi

echo ""
echo "=== Tailscale exit node (optional) ==="
if command -v tailscale >/dev/null 2>&1 && tailscale status >/dev/null 2>&1; then
  CUR=$(tailscale status --json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('ExitNodeStatus',{}).get('Online',False))" 2>/dev/null || echo "False")
  echo "exit node in use: ${CUR}"
else
  echo "tailscale: not installed/up (optional)"
fi

if [[ "${1:-}" == "--logs" ]]; then
  echo ""
  echo "=== container logs (last 20) ==="
  docker logs "${CONTAINER_NAME}" 2>&1 | tail -20 || echo "(no container)"
fi
