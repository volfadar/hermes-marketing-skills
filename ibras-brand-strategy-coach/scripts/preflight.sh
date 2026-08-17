#!/usr/bin/env bash
# preflight.sh — run every mechanical check before shipping a deliverable.
#
# Recorded sessions showed that prose rules do not survive contact with a long session:
# five models read the same evidence rules and five violated them. These checks are the
# part of the discipline that does not depend on remembering.
#
# Usage:
#   bash preflight.sh --user rizki
#   bash preflight.sh --user rizki --artifact plan.md --session export.jsonl
#   bash preflight.sh --artifact plan.md --strict
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFG_DIR="${BRAND_COACH_DIR:-$HOME/.brand-coach}"
USER_NAME="${USER_NAME:-peserta}"
ARTIFACTS=()
SESSION=""
STRICT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)     USER_NAME="$2"; shift 2 ;;
    --artifact) ARTIFACTS+=("$2"); shift 2 ;;
    --session)  SESSION="$2"; shift 2 ;;
    --strict)   STRICT=1; shift ;;
    -h|--help)  sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

PROFILE="$CFG_DIR/profiles/$USER_NAME.json"
FAILURES=0
WARNINGS=0

section() { printf '\n\033[1m%s\033[0m\n' "$1"; }
pass()    { printf '  \033[32m✓\033[0m %s\n' "$1"; }
warn()    { printf '  \033[33m!\033[0m %s\n' "$1"; WARNINGS=$((WARNINGS+1)); }
fail()    { printf '  \033[31m✗\033[0m %s\n' "$1"; FAILURES=$((FAILURES+1)); }

# ── 1. Stage gates ────────────────────────────────────────────────────────────
section "Stage gates — $USER_NAME"
if [[ ! -f "$PROFILE" ]]; then
  warn "no profile at $PROFILE (run start-session.sh) — skipping gate checks"
elif ! command -v jq >/dev/null 2>&1; then
  warn "jq not installed — skipping gate checks"
else
  stage=$(jq -r '.current_stage // 1' "$PROFILE")
  pass "current stage: $stage"

  check_gate() { # name, jq filter, message
    if jq -e "$2" "$PROFILE" >/dev/null 2>&1; then pass "$1"; else fail "$3"; fi
  }

  [[ "$stage" -ge 3 ]] && {
    check_gate "dossier: CV or explicit proof gap" \
      '.dossier.cv.status != "pending" or (.dossier.proof_gap // false)' \
      "Stage 3+ but CV never parsed and no proof gap recorded"
    check_gate "dossier: portfolio inspected or gap recorded" \
      '.dossier.portfolio.status != "pending" or (.dossier.proof_gap // false)' \
      "Stage 3+ but portfolio never requested — the richest proof asset is usually here"
    check_gate "constraint register populated" \
      '(.dossier.constraints | type == "object") and (.dossier.constraints | length > 0)' \
      "constraint register empty — REFUSE/CAP/ACCESS/PERMISSION must be captured in Stage 2"
  }

  [[ "$stage" -ge 4 ]] && {
    check_gate "research recorded with an as-of date" \
      '.research.as_of != null' "Stage 4+ but no dated research"
    check_gate "at least one opened source" \
      '[.research.sources[]? | select(.status == "opened")] | length >= 1' \
      "no source with status \"opened\" — search results are not sources"
    opened=$(jq '[.research.sources[]? | select(.status == "opened" and (.is_search_page // false) == false)] | length' "$PROFILE")
    if [[ "${opened:-0}" -ge 4 ]]; then pass "opened non-search pages: $opened (min 4)"
    else warn "only ${opened:-0} opened non-search pages — minimum for a positioning pass is 4"; fi
  }

  [[ "$stage" -ge 5 ]] && {
    check_gate "economics: budget captured"  '.economics.budget != null'   "budget missing"
    check_gate "economics: capacity captured" '.economics.capacity != null' "capacity missing"
    check_gate "goal fit stated"             '.goal_fit.gap != null' \
      "no goal-reconciliation statement — say what the plan produces against what they need"
  }
fi

# ── 2. Citation integrity ─────────────────────────────────────────────────────
section "Citation integrity"
if [[ -n "$SESSION" && -f "$SESSION" ]]; then
  args=("$SESSION")
  for a in "${ARTIFACTS[@]:-}"; do [[ -n "$a" && -f "$a" ]] && args=(--session "$SESSION" --artifact "$a"); done
  if out=$(python3 "$SCRIPT_DIR/check-citations.py" "${args[@]}" 2>&1); then
    bad=$(sed -n 's/^Total citations needing correction: //p' <<<"$out")
    if [[ "${bad:-0}" -eq 0 ]]; then pass "every cited URL was fetched"
    else fail "$bad citation(s) not fetched — see below"; sed -n '/SERP_ONLY\|UNSOURCED\|WEAK/,$p' <<<"$out" | head -30; fi
  else
    warn "check-citations.py could not run"
  fi
else
  warn "no --session supplied — citations unverified (this is how unopened URLs ship)"
fi

# ── 3. Number provenance + retracted-claim leakage ────────────────────────────
section "Number provenance"
if [[ ${#ARTIFACTS[@]} -eq 0 ]]; then
  warn "no --artifact supplied — number tags unverified"
else
  for a in "${ARTIFACTS[@]}"; do
    [[ -f "$a" ]] || { fail "artifact not found: $a"; continue; }
    prof_arg=(); [[ -f "$PROFILE" ]] && prof_arg=(--profile "$PROFILE")
    out=$(python3 "$SCRIPT_DIR/check-numbers.py" "$a" "${prof_arg[@]}" 2>&1)
    n=$(sed -n 's/^Total violations: //p' <<<"$out")
    if [[ "${n:-0}" -eq 0 ]]; then pass "$(basename "$a"): all figures tagged"
    else fail "$(basename "$a"): $n untagged/unsafe figure(s)"; sed -n '/UNTAGGED\|LOAD-BEARING\|RETRACTED/,$p' <<<"$out" | head -25; fi
    grep -qi "corrections log" "$a" && pass "$(basename "$a"): corrections log present" \
      || warn "$(basename "$a"): no '## Corrections log' section"
  done
fi

# ── 4. Session hygiene ────────────────────────────────────────────────────────
section "Session hygiene"
CFG="${HERMES_HOME:-$HOME/.hermes}/config.yaml"
if [[ -f "$CFG" ]]; then
  grep -q 'creation_nudge_interval:[[:space:]]*0' "$CFG" \
    && pass "background skill review disabled" \
    || fail "set skills.creation_nudge_interval: 0 — a background reviewer mutated the live skill in 3 of 5 recorded runs"
else
  warn "no hermes config at $CFG"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
printf '\n\033[1mPREFLIGHT: %d failed, %d warning(s)\033[0m\n' "$FAILURES" "$WARNINGS"
if [[ "$FAILURES" -gt 0 ]]; then
  echo "Fix these, or state the gap explicitly in the message you send."
  [[ "$STRICT" -eq 1 ]] && exit 1
fi
exit 0
