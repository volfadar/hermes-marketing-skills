#!/usr/bin/env bash
# waha.sh — Swiss-army wrapper for common WAHA operations (read-heavy).
# Loads config from ~/.waha-marketing/config.env.
#
# Usage:
#   bash waha.sh status                       session info + health
#   bash waha.sh sessions [--all]             list all sessions
#   bash waha.sh groups [--limit N]           list groups (light)
#   bash waha.sh group <groupId>              group detail
#   bash waha.sh group-participants <groupId> list participants
#   bash waha.sh contacts [--limit N]         list contacts
#   bash waha.sh check-exists <phone>         is number on WhatsApp?
#   bash waha.sh labels                        list labels (Business)
#   bash waha.sh chats [--limit N]            recent chats
#   bash waha.sh messages <chatId> [--limit N] message history
#   bash waha.sh me                            current account
#
# Write operations (HUMAN confirm first):
#   bash waha.sh send-text <chatId> "<text>"      sends a single text
#   bash waha.sh send-seen <chatId>               mark as read
#   bash waha.sh label-chat <chatId> <labelId>    assign label
#
# Session bookkeeping (no network, safe to run any time):
#   bash waha.sh open                          siapa yang masih nunggu dari kemarin
#   bash waha.sh recap                         apa yang kelar hari ini
#   bash waha.sh week                          ringkasan seminggu
#   bash waha.sh profile [show|missing|check]  profil usaha yang dibaca semua tool
#
# All write ops print "DRY RUN" preview unless --confirm is passed.
set -euo pipefail

CFG_DIR="${WAHA_CONFIG_DIR:-$HOME/.waha-marketing}"
CFG="$CFG_DIR/config.env"
[[ -f "$CFG" ]] || { echo "Run initialize.sh first (no config at $CFG)" >&2; exit 1; }
# shellcheck disable=SC1090
source "$CFG"

CMD="${1:-status}"; shift || true

# --confirm is accepted ANYWHERE in the argument list, not just first.
# Everyone types it last ("send-text 628… 'halo' --confirm") because that is
# where every other CLI puts it. When it only worked in first position, the
# command silently stayed a dry run and the caller believed the message had
# gone out. A safety flag that fails closed is fine; one that fails *quietly*
# is not.
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

CONFIRM="no"
BLAST_ACK="no"
BINDING_ACK="no"
_args=()
for _a in "$@"; do
  case "$_a" in
    --confirm)      CONFIRM="yes" ;;
    --blast-ack)    BLAST_ACK="yes" ;;
    --binding-ack)  BINDING_ACK="yes" ;;
    *)              _args+=("$_a") ;;
  esac
done
set -- ${_args+"${_args[@]}"}

# ---------------------------------------------------------------------------
# Pacing for single sends.
#
# lib/broadcast.py already paces properly — 12-45 s between messages, long
# pauses between batches. But nothing stopped an agent from writing
#     for n in $(cat numbers.txt); do bash waha.sh send-text "$n" "$MSG" --confirm; done
# which bypasses every one of those constants. Against a WAHA mock that models
# WhatsApp's actual triggers, that loop got the number banned after SIX sends.
#
# So the pacing lives here too. It is automatic and silent when you are working
# normally — nobody chatting with customers notices a 12 s floor. It only bites
# when the pattern is the one that gets numbers blocked.
# ---------------------------------------------------------------------------
SEND_STATE="$CFG_DIR/state/send-log.tsv"
MIN_GAP_S="${WAHA_MIN_GAP_S:-12}"
BLAST_THRESHOLD="${WAHA_BLAST_THRESHOLD:-5}"
COLD_THRESHOLD="${WAHA_COLD_THRESHOLD:-4}"
KNOWN_CACHE="$CFG_DIR/state/known-chats.txt"
KNOWN_TTL_S="${WAHA_KNOWN_TTL_S:-600}"

# Who has actually talked to us before.
#
# Pacing and text-variation were not enough. The only number banned during the
# whole evaluation was banned for neither: the agent rotated seven templates and
# left 9-30 s gaps, and WhatsApp still killed it at
#     "cold outreach: 6 nomor berturut-turut yang belum pernah chat duluan"
# after it walked off the end of the contact list onto strangers. Slow, varied
# messages to people who never wrote to you are still the fastest way to lose a
# number — so the third pattern needs its own check.
#
# Cached, because this runs on every single send and a warung's contact list
# does not change between two messages. Fails open on any error: a lookup that
# cannot complete must never stop somebody answering a customer.
known_chats() {
  local age=0
  if [[ -f "$KNOWN_CACHE" ]]; then
    age=$(( $(date +%s) - $(stat -c %Y "$KNOWN_CACHE" 2>/dev/null || echo 0) ))
    if (( age < KNOWN_TTL_S )); then cat "$KNOWN_CACHE"; return 0; fi
  fi
  mkdir -p "$(dirname "$KNOWN_CACHE")"
  { get "/api/chats?session=${WAHA_SESSION}&limit=500" || true; } > /tmp/waha-chats.$$ 2>/dev/null
  { get "/api/contacts/all?session=${WAHA_SESSION}&limit=500" || true; } > /tmp/waha-cts.$$ 2>/dev/null
  python3 - /tmp/waha-chats.$$ /tmp/waha-cts.$$ 2>/dev/null <<'PY' > "$KNOWN_CACHE.tmp" || true
import json, sys

ids = set()
for path, contacts in ((sys.argv[1], False), (sys.argv[2], True)):
    try:
        data = json.load(open(path))
    except Exception:
        continue
    if not isinstance(data, list):
        continue
    for row in data:
        if not isinstance(row, dict):
            continue
        # A contact only counts as warm if WhatsApp says it is really ours.
        # Numbers that merely exist are exactly the cold-outreach case.
        if contacts and not row.get("isMyContact"):
            continue
        cid = row.get("id")
        if isinstance(cid, dict):
            cid = cid.get("_serialized")
        if cid:
            ids.add(str(cid))
print("\n".join(sorted(ids)))
PY
  rm -f /tmp/waha-chats.$$ /tmp/waha-cts.$$
  # An empty answer means the lookup failed, not that we know nobody. Keep the
  # previous cache rather than declaring every customer a stranger.
  if [[ -s "$KNOWN_CACHE.tmp" ]]; then mv "$KNOWN_CACHE.tmp" "$KNOWN_CACHE"
  else rm -f "$KNOWN_CACHE.tmp"; touch "$KNOWN_CACHE"; fi
  cat "$KNOWN_CACHE"
}

pace_and_check() {   # pace_and_check <chatId> <text>
  local cid="$1" txt="$2" now last gap hash same cold streak
  mkdir -p "$(dirname "$SEND_STATE")"; touch "$SEND_STATE"
  now=$(date +%s)
  hash=$(printf '%s' "$txt" | cksum | cut -d' ' -f1)

  # 0. Strangers in a row. Column 4 of the log records whether each send went to
  #    someone we had heard from; the streak is what WhatsApp actually watches.
  cold=0
  local warm; warm="$(known_chats)"
  if [[ -n "$warm" ]] && ! grep -qxF "$cid" <<<"$warm"; then cold=1; fi
  if [[ "$cold" == "1" ]]; then
    streak=$(awk -F'\t' '{ if ($4 == "1") n++; else n=0 } END { print n+0 }' "$SEND_STATE")
    streak=$(( streak + 1 ))
    if (( streak >= COLD_THRESHOLD )) && [[ "$BLAST_ACK" != "yes" ]]; then
      cat >&2 <<MSG

  ⚠  Ini nomor ke-$streak berturut-turut yang belum pernah chat duluan.

     Bukan soal cepat atau lambat. WhatsApp paling cepat memblokir nomor yang
     menyapa orang asing berturut-turut — pesan pelan dan kalimat variasi pun
     tetap kena. Yang berhenti nomor WhatsApp Anda, berikut semua orderan yang
     masuk lewat situ.

     Yang jauh lebih aman: kirim dulu ke orang yang pernah beli atau pernah
     chat duluan. Lihat daftarnya:
       bash scripts/waha.sh chats

     Kalau memang harus ke nomor baru, selingi dengan balasan ke pelanggan
     lama, atau tambahkan --blast-ack kalau Anda sudah paham risikonya.
     Belum ada yang dikirim.

MSG
      return 1
    fi
  fi

  # 1. Identical text to many different chats = the pattern WhatsApp reads as a
  #    blast, regardless of how slowly you send it.
  same=$(awk -F'\t' -v h="$hash" -v c="$cid" '$3==h && $2!=c {print $2}' "$SEND_STATE" | sort -u | wc -l)
  if [[ "$same" -ge "$BLAST_THRESHOLD" && "$BLAST_ACK" != "yes" ]]; then
    cat >&2 <<MSG

  ⚠  Teks yang sama sudah dikirim ke $same nomor berbeda.

     Ini pola yang paling cepat memicu blokir — bukan jumlahnya, tapi
     kesamaannya. Yang diblokir nomor WhatsApp-nya, bukan servernya. Semua
     orderan yang masuk lewat nomor itu ikut berhenti.

     Untuk kirim ke banyak orang, pakai alat yang memang untuk itu:
       bash scripts/broadcast-helper.sh --contacts list.csv --templates pesan.txt

     Dia memakai beberapa variasi kalimat, jeda 12-45 detik, dan berhenti
     sendiri kalau ada yang tidak beres. Belum ada yang dikirim.

     Kalau tetap mau lewat perintah ini, tambahkan --blast-ack.

MSG
    return 1
  fi

  # 2. Floor on the gap between sends. Sleeps rather than refusing — the goal is
  #    to make the safe thing the default, not to make the tool annoying.
  last=$(tail -1 "$SEND_STATE" 2>/dev/null | cut -f1)
  if [[ -n "$last" ]]; then
    gap=$(( now - last ))
    if (( gap < MIN_GAP_S )); then
      local wait=$(( MIN_GAP_S - gap ))
      echo "  ⏳ jeda ${wait}s dulu (biar tidak terbaca bot)…" >&2
      sleep "$wait"
      now=$(date +%s)
    fi
  fi
  printf '%s\t%s\t%s\t%s\n' "$now" "$cid" "$hash" "$cold" >> "$SEND_STATE"
  return 0
}

# Helper for GET
get() {
  local path="$1"
  curl -s "${WAHA_URL}${path}" -H "X-Api-Key: ${WAHA_API_KEY}" --max-time 30
}

# Helper for POST/PUT with body
post() {
  local method="$1" path="$2" body="$3"
  curl -s -X "$method" "${WAHA_URL}${path}" \
    -H "X-Api-Key: ${WAHA_API_KEY}" \
    -H "Content-Type: application/json" \
    --max-time 30 \
    ${body:+-d "$body"}
}

pp() { python3 -m json.tool 2>/dev/null || cat; }

case "$CMD" in
  status)
    echo "=== WAHA health ==="
    get "/health" | pp | head -8
    echo ""
    echo "=== Session $WAHA_SESSION ==="
    get "/api/sessions/$WAHA_SESSION" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'status:  {d.get(\"status\",\"?\")}')
print(f'account: {d.get(\"me\",{}).get(\"pushName\",\"?\")} ({d.get(\"me\",{}).get(\"id\",\"?\")})')
print(f'engine:  {d.get(\"engine\",{}).get(\"gows\",{})}')
" 2>/dev/null || get "/api/sessions/$WAHA_SESSION" | pp
    ;;

  me)
    get "/api/sessions/$WAHA_SESSION/me" | pp
    ;;

  sessions)
    ALL=""
    [[ "${1:-}" == "--all" ]] && ALL="?all=true"
    get "/api/sessions$ALL" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for s in d:
    me = s.get('me') or {}
    print(f'  {s[\"name\"]:25} {s[\"status\"]:12} {me.get(\"pushName\",\"\")}')
" 2>/dev/null || get "/api/sessions$ALL" | pp
    ;;

  groups)
    LIM="${1:---limit}"; [[ "$LIM" == "--limit" ]] && LIM="${2:-10}"
    get "/api/$WAHA_SESSION/groups?limit=$LIM" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for g in d:
    # field names vary by engine; handle both
    name = g.get('Name') or g.get('name') or g.get('subject') or '?'
    jid  = g.get('JID') or g.get('id') or '?'
    sz   = g.get('ParticipantCount') or g.get('size') or g.get('participants_count') or '?'
    print(f'  {jid:35} {str(sz):>5}  {name[:50]}')
" 2>/dev/null || get "/api/$WAHA_SESSION/groups?limit=$LIM" | pp | head -50
    ;;

  group)
    GID="$1"
    get "/api/$WAHA_SESSION/groups/$GID" | pp
    ;;

  group-participants)
    GID="$1"
    get "/api/$WAHA_SESSION/groups/$GID/participants" | python3 -c "
import sys, json
d = json.load(sys.stdin)
arr = d if isinstance(d, list) else d.get('participants', [])
for p in arr:
    jid = p.get('JID') or p.get('id') or '?'
    ph  = p.get('PhoneNumber') or ''
    isAdmin = p.get('IsAdmin') or p.get('isAdmin') or False
    tag = ' [admin]' if isAdmin else ''
    print(f'  {jid:40} {ph:20} {tag}')
" 2>/dev/null || get "/api/$WAHA_SESSION/groups/$GID/participants" | pp | head -40
    ;;

  contacts)
    LIM="${1:---limit}"; [[ "$LIM" == "--limit" ]] && LIM="${2:-20}"
    get "/api/contacts/all?session=$WAHA_SESSION&limit=$LIM&sortBy=name&sortOrder=asc" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for c in d:
    cid = c.get('id','?')
    name = c.get('name','') or c.get('pushname','') or '(no name)'
    print(f'  {cid:30} {name[:40]}')
" 2>/dev/null || get "/api/contacts/all?session=$WAHA_SESSION&limit=$LIM" | pp | head -30
    ;;

  check-exists)
    PH="$1"
    get "/api/contacts/check-exists?phone=$PH&session=$WAHA_SESSION" | pp
    ;;

  labels)
    get "/api/$WAHA_SESSION/labels" | pp
    ;;

  label-chat)
    CID="$1"; LBL="$2"
    BODY="{\"labels\":[{\"id\":\"$LBL\"}]}"
    if [[ "$CONFIRM" != "yes" ]]; then
      echo "DRY RUN — would PUT /api/$WAHA_SESSION/labels/chats/$CID/ body=$BODY"
      echo "Pass --confirm to actually apply."
    else
      post PUT "/api/$WAHA_SESSION/labels/chats/$CID/" "$BODY" | pp
    fi
    ;;

  chats)
    LIM="${1:---limit}"; [[ "$LIM" == "--limit" ]] && LIM="${2:-20}"
    get "/api/chats?session=$WAHA_SESSION&limit=$LIM" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if isinstance(d, dict): d = d.get('chats', [])
for c in d:
    cid = c.get('id','?')
    name = c.get('name','') or '(no name)'
    unread = c.get('unreadCount', 0)
    print(f'  {cid:35} unread={unread:>3}  {name[:40]}')
" 2>/dev/null || get "/api/chats?session=$WAHA_SESSION&limit=$LIM" | pp | head -30
    ;;

  messages)
    CID="$1"
    # `chats`, `groups` and `contacts` all accept `--limit N`, the help text
    # promises it here too, and this one took `$2` raw — so the documented
    # `messages <chatId> --limit 20` sent `limit=--limit`, the server 500'd, and
    # the agent burned five minutes retrying a call it had written correctly.
    LIM="${2:---limit}"; [[ "$LIM" == "--limit" ]] && LIM="${3:-20}"
    [[ "$LIM" =~ ^[0-9]+$ ]] || LIM=20
    # chatId perlu di-escape @ -> %40
    CID_ENC="${CID/@/%40}"
    get "/api/messages?chatId=$CID_ENC&session=$WAHA_SESSION&limit=$LIM&downloadMedia=false" | python3 -c "
import sys, json
d = json.load(sys.stdin)
arr = d if isinstance(d, list) else d.get('messages', [])
for m in arr[-20:]:
    frm = m.get('from','?')[:20]
    me = 'me' if m.get('fromMe') else 'in'
    body = (m.get('body','') or '')[:60]
    ts = m.get('timestamp','?')
    print(f'  [{me}] {frm:22} {ts:>12}  {body}')
" 2>/dev/null || get "/api/messages?chatId=$CID_ENC&session=$WAHA_SESSION&limit=$LIM" | pp | head -30
    ;;

  send-seen)
    CID="$1"
    BODY="{\"session\":\"$WAHA_SESSION\",\"chatId\":\"$CID\"}"
    if [[ "$CONFIRM" != "yes" ]]; then
      echo "DRY RUN — would POST /api/sendSeen body=$BODY"
    else
      post POST "/api/sendSeen" "$BODY" | pp
    fi
    ;;

  send-text)
    CID="$1"; TXT="$2"
    # Escape quotes in text
    TXT_ESC="${TXT//\"/\\\"}"
    BODY="{\"session\":\"$WAHA_SESSION\",\"chatId\":\"$CID\",\"text\":\"$TXT_ESC\"}"
    if [[ "$CONFIRM" != "yes" ]]; then
      echo "DRY RUN — would POST /api/sendText"
      echo "  to:   $CID"
      echo "  text: $TXT"
      echo "Pass --confirm to actually send."
      echo ""
      echo "⚠  Soft warning: pastikan penerima sudah opt-in. Jangan spam."
    else
      # Same two brakes the email skill has. WhatsApp needs them more, not less:
      # higher volume, looser register, and the penalty is a blocked number that
      # takes every order with it. Evaluation sent "aman kok buat asam lambung"
      # and "pesanan berikutnya gue kasih gratis ongkir" down this path with
      # nothing in the way, because there was nothing in the way.
      # `|| CHECK_RC=$?` is load-bearing: under `set -e` an assignment whose
      # command substitution exits non-zero kills the script on the spot. The
      # send was correctly held, and the paragraph explaining why never printed
      # — a silent refusal, which is the failure mode this whole gate exists to
      # avoid.
      CHECK_RC=0
      CHECK_OUT="$(python3 "$SKILL_DIR/lib/outbound_checks.py" --text "$TXT" \
                    2>/tmp/waha-binding.$$)" || CHECK_RC=$?
      if [[ "$CHECK_OUT" == DISCLAIMER::* ]]; then
        KIND="${CHECK_OUT%%$'\n'*}"; KIND="${KIND#DISCLAIMER::}"
        TXT="${CHECK_OUT#*$'\n'}"
        printf '\n  \033[1;33m⚠\033[0m Pesan ini membuat klaim %s. Catatan ditambahkan otomatis\n' "$KIND"
        printf '     — ini satu dari dua hal yang tidak bisa dicopot.\n\n'
        TXT_ESC="${TXT//\"/\\\"}"; TXT_ESC="${TXT_ESC//$'\n'/\\n}"
        BODY="{\"session\":\"$WAHA_SESSION\",\"chatId\":\"$CID\",\"text\":\"$TXT_ESC\"}"
      fi
      # A promise she already decided is not a promise that needs deciding.
      # One recorded run cost a whole turn holding "beli 3 gratis 1" — an offer
      # the owner had announced two turns earlier. If it is listed under
      # `fakta.yang_boleh_dijanjikan` in her profile, it is pre-approved and
      # the gate stands down. Everything not listed still stops here.
      if [[ $CHECK_RC -eq 3 ]] && python3 - "$TXT" "$SKILL_DIR/lib" <<'PY' 2>/dev/null
import sys
sys.path.insert(0, sys.argv[2])
try:
    import profile as P
    prof = P.load()
    sys.exit(0 if (prof and prof.is_pre_approved(sys.argv[1])) else 1)
except Exception:
    sys.exit(1)
PY
      then
        printf '\n  \033[0;36mi\033[0m Janji ini sudah kamu setujui di profil usaha — lanjut.\n\n'
        CHECK_RC=0
      fi
      if [[ $CHECK_RC -eq 3 && "$BINDING_ACK" != "yes" ]]; then
        printf '\n  \033[1;33m⚠  Pesan ini berisi JANJI atas nama usahamu:\033[0m\n'
        sed 's/^BINDING::/     • /; s/::/\n       /' /tmp/waha-binding.$$ 2>/dev/null
        cat <<'MSG'

     Yang menanggung janji ini pemiliknya, bukan yang mengetik.
     Tanyakan dulu: "boleh saya janjikan ini?"

     Jangan menulis ulang kalimatnya supaya lolos — yang butuh izin itu
     janjinya, bukan kata-katanya.

     Kalau sudah boleh, ulangi perintah yang SAMA ditambah --binding-ack.
     Belum ada yang dikirim.
MSG
        rm -f /tmp/waha-binding.$$
        exit 3
      fi
      rm -f /tmp/waha-binding.$$
      pace_and_check "$CID" "$TXT" || exit 3
      echo "Sending to $CID..."
      post POST "/api/sendText" "$BODY" | pp
      # Record it, so the end-of-session recap can say who was answered and
      # tomorrow can open by naming who still is not. Silent and best-effort:
      # a bookkeeping failure must never look like a send failure.
      python3 "$SKILL_DIR/lib/ledger.py" add --kind sent --who "${CID%%@*}" \
        --what "$(printf '%s' "$TXT" | cut -c1-60)" --channel wa >/dev/null 2>&1 || true
    fi
    ;;

  # Session two stops being a cold start. Every recorded session began from
  # nothing; this is the one line that makes the second morning different.
  recap)
    python3 "$SKILL_DIR/lib/ledger.py" show
    ;;
  open)
    python3 "$SKILL_DIR/lib/ledger.py" open
    ;;
  week)
    python3 "$SKILL_DIR/lib/ledger.py" week
    ;;
  profile)
    python3 "$SKILL_DIR/lib/profile.py" "${1:-show}"
    ;;

  -h|--help|help)
    sed -n '2,30p' "$0"
    ;;

  *)
    echo "Unknown command: $CMD" >&2
    echo "Run: bash $0 --help" >&2
    exit 2
    ;;
esac
