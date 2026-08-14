#!/usr/bin/env bash
# stop.sh — stop and remove the cloakserve container.
# Usage: bash stop.sh
set -euo pipefail
CONTAINER_NAME="${CLOAKSERVE_CONTAINER:-cloakserve}"

if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -qx "${CONTAINER_NAME}"; then
  docker rm -f "${CONTAINER_NAME}" >/dev/null
  echo "cloakserve: stopped (container ${CONTAINER_NAME} removed)"
else
  echo "cloakserve: not running (no container named ${CONTAINER_NAME})"
fi

# Helpful reminder if a Tailscale exit node is still active
if command -v tailscale >/dev/null 2>&1 && tailscale status >/dev/null 2>&1; then
  CUR=$(tailscale status --json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('ExitNodeStatus',{}).get('Online',False))" 2>/dev/null || echo "False")
  if [[ "$CUR" == "True" ]]; then
    echo "tailscale: exit node still active. To return to direct egress:"
    echo "  sudo tailscale up --exit-node="
  fi
fi
