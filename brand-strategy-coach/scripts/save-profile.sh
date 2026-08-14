#!/usr/bin/env bash
# save-profile.sh — save stage output to profile JSON + export to USER.md.
# Usage: bash save-profile.sh <stage1-5> [--user <name>] [--data '<json>']
set -euo pipefail
STAGE="${1:?usage: save-profile.sh <stage1-5>}"
shift
USER="${USER_NAME:-peserta}"
DATA=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) USER="$2"; shift 2 ;;
    --data) DATA="$2"; shift 2 ;;
    *) shift ;;
  esac
done

CFG_DIR="${BRAND_COACH_DIR:-$HOME/.brand-coach}"
PROFILE="$CFG_DIR/profiles/$USER.json"
[[ -f "$PROFILE" ]] || { echo "Profile tidak ada. Run start-session.sh dulu." >&2; exit 1; }

# Update profile JSON
python3 - "$PROFILE" "$STAGE" "${DATA:-}" <<'PY'
import sys, json
from datetime import datetime
path, stage, data_raw = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path) as f:
    profile = json.load(f)

def merge_dict(base, incoming):
    """Recursively merge a partial stage payload without erasing pending fields."""
    result = dict(base) if isinstance(base, dict) else {}
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_dict(result[key], value)
        else:
            result[key] = value
    return result

try:
    data = json.loads(data_raw) if data_raw else None
except json.JSONDecodeError:
    data = {"_raw": data_raw}  # kalau bukan JSON valid, simpan mentah

field_map = {
    "stage1": ("talent", 2),
    "stage2": ("background", 3),
    "stage3": ("positioning", 4),
    "stage4": ("tools", 5),
    "stage5": ("funnel", None),
}
if stage not in field_map:
    print(f"Unknown stage: {stage}", file=sys.stderr); sys.exit(2)
field, next_stage = field_map[stage]

# Be defensive: if user wrapped the data in the field name (e.g. {"talent": {...}}),
# unwrap it so we don't end up with profile["talent"]["talent"].
if data and isinstance(data, dict) and field in data and isinstance(data[field], dict):
    data = data[field]

profile[field] = data

# Mirror stage payloads into the v2 working fields while keeping the original
# five stage keys readable by older scripts.
if isinstance(data, dict):
    if field == "talent":
        if "goal" in data:
            profile["goal"] = data["goal"]
    elif field == "background":
        dossier = data.get("dossier", data)
        if isinstance(dossier, dict):
            profile["dossier"] = merge_dict(profile.get("dossier", {}), dossier)
        proof = data.get("proof_ledger")
        if isinstance(proof, list):
            profile["evidence_ledger"] = proof
    elif field == "positioning":
        research = data.get("research")
        if isinstance(research, dict):
            profile["research"] = merge_dict(profile.get("research", {}), research)
        evidence = data.get("evidence")
        if isinstance(evidence, list):
            profile["evidence_ledger"] = evidence
    elif field == "tools":
        experiment = data.get("experiment")
        if isinstance(experiment, dict):
            experiments = profile.setdefault("experiments", [])
            experiment_id = experiment.get("id")
            if not experiment_id or all(
                existing.get("id") != experiment_id
                for existing in experiments
                if isinstance(existing, dict)
            ):
                experiments.append(experiment)
    elif field == "funnel":
        economics = data.get("economics")
        if isinstance(economics, dict):
            profile.setdefault("economics", {}).update(economics)

# Cross-stage fields: the register, goal fit, retractions, and the improvement backlog
# can be updated from any stage because evidence arrives out of order.
if isinstance(data, dict):
    constraints = data.get("constraints")
    if isinstance(constraints, dict):
        target = profile.setdefault("dossier", {}).setdefault("constraints", {})
        for bucket in ("refuse", "cap", "access", "permission"):
            incoming = constraints.get(bucket)
            if isinstance(incoming, list):
                existing = target.setdefault(bucket, [])
                existing.extend(i for i in incoming if i not in existing)
        for key, value in constraints.items():
            if key not in ("refuse", "cap", "access", "permission"):
                target[key] = value

    goal_fit = data.get("goal_fit")
    if isinstance(goal_fit, dict):
        profile.setdefault("goal_fit", {}).update(goal_fit)

    for key in ("retracted", "backlog"):
        incoming = data.get(key)
        if isinstance(incoming, list):
            existing = profile.setdefault(key, [])
            existing.extend(i for i in incoming if i not in existing)

    sources = (data.get("research") or {}).get("sources") if isinstance(data.get("research"), dict) else None
    if isinstance(sources, list):
        known = {s.get("url") for s in profile.setdefault("research", {}).setdefault("sources", []) if isinstance(s, dict)}
        for s in sources:
            if isinstance(s, dict) and s.get("url") not in known:
                profile["research"]["sources"].append(s)

# Stage 5 may not close while the goal is unreconciled: the single most consequential
# omission in recorded sessions was a finished plan that never met the stated goal.
if stage == "stage5" and not (profile.get("goal_fit") or {}).get("gap"):
    print("WARNING: goal_fit.gap is empty. State what the plan produces against what the "
          "user said they need before calling Stage 5 complete.", file=sys.stderr)

if next_stage:
    profile["current_stage"] = next_stage
profile["updated_at"] = datetime.now().isoformat()
with open(path, "w") as f:
    json.dump(profile, f, indent=2, ensure_ascii=False)
print(f"✓ Saved {field} → {path}")
print(f"  Next: stage{next_stage}" if next_stage else "  All 5 stages complete!")
PY

# Export positioning (Stage 3) to USER.md Hermes memory
if [[ "$STAGE" == "stage3" && -n "$DATA" ]]; then
  MEM_DIR="${HERMES_HOME:-$HOME/.hermes}/memories"
  mkdir -p "$MEM_DIR"
  echo ""
  echo "=== Export ke Hermes memory (USER.md) ==="
  echo "Untuk export, jalankan Hermes dan ketik:"
  echo "  'Simpan positioning ini ke USER.md:'"
  echo "  $(echo "$DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); d=d.get('positioning',d); c=d.get('chosen',{}); print(d.get('statement') or (c.get('public_line','') if isinstance(c,dict) else ''))" 2>/dev/null)"
  echo ""
  echo "Lalu set pillars di content-creator:"
  echo "  bash ~/.hermes/skills/content-creator/scripts/pillars.sh \"<pilar1>, <pilar2>, <pilar3>\""
fi
