#!/bin/bash
# Fire N Seedance 2.0 image-to-video jobs in parallel (one per still × variation).
# Reads jobs from STDIN:
#   <slot>::<prompt-text>::<duration-seconds>::<still-slot>::<variation-idx>
#
# Looks up the startFrame from $RUN_DIR/references/seedance-startframes.txt
# (produced by upload-startframes.sh). Format there: <still-slot>:<var>:<filePath>
#
# Example:
#   cat <<EOF | ./generate-seedance.sh clips
#   pain-cpm-v1::3D animated film aesthetic, image-to-video of @(img1)...::4::pain-cpm::1
#   pain-cpm-v2::3D animated film aesthetic, image-to-video of @(img1)...::4::pain-cpm::2
#   brent-reveal-v1::3D animated film aesthetic, image-to-video of @(img1)...::8::brent-reveal::1
#   EOF
#
# Required env: ARCADS_BASIC_AUTH, PRODUCT_ID, PROJECT_ID, RUN_DIR
set -euo pipefail

set -a; source "${ENV_FILE:-$RUN_DIR/.env}" 2>/dev/null || source "$(git rev-parse --show-toplevel 2>/dev/null)/workspace/.env"; set +a

BASE="${ARCADS_BASE_URL:-https://external-api.arcads.ai}"
AUTH_HDR="Authorization: ${ARCADS_BASIC_AUTH:-Basic $(printf '%s:' "$ARCADS_API_KEY" | base64)}"
ASPECT="${ASPECT_RATIO:-9:16}"
RESOLUTION="${RESOLUTION:-720p}"
AUDIO_ENABLED="${AUDIO_ENABLED:-true}"

SUBDIR="$1"
OUT_DIR="$RUN_DIR/$SUBDIR/_resp"
SF_MAP="$RUN_DIR/references/seedance-startframes.txt"
mkdir -p "$OUT_DIR"

lookup_startframe() {
  local key="$1:$2"
  grep -m 1 "^$key:" "$SF_MAP" | cut -d: -f3-
}

post_one() {
  local slot="$1" prompt="$2" duration="$3" still_key="$4" var_idx="$5"
  local sf; sf=$(lookup_startframe "$still_key" "$var_idx")
  if [[ -z "$sf" ]]; then
    echo "[$slot] !! no startframe in $SF_MAP for $still_key:$var_idx" >&2
    return 1
  fi
  local body
  body=$(jq -n --arg p "$prompt" --arg sf "$sf" --argjson dur "$duration" \
    '{model:"seedance-2.0", productId:"'$PRODUCT_ID'", projectId:"'$PROJECT_ID'",
      prompt:$p, aspectRatio:"'$ASPECT'", resolution:"'$RESOLUTION'",
      duration:$dur, audioEnabled:'$AUDIO_ENABLED', referenceImages:[$sf]}')
  # curl -sS alone exits 0 on HTTP 4xx/5xx, so capture the status code too and
  # treat "no job id" as failure. Otherwise a rejected batch looks successful.
  local raw rc=0
  raw=$(curl -sS -w $'\n%{http_code}' -H "$AUTH_HDR" -H "Content-Type: application/json" \
    -X POST "$BASE/v2/videos/generate" -d "$body") || rc=$?
  local http_code="" resp=""
  if [[ -n "$raw" ]]; then
    http_code=$(printf %s "$raw" | tail -n 1)
    resp=$(printf %s "$raw" | sed '$d')
  fi
  printf %s "$resp" > "$OUT_DIR/$slot.json"

  if (( rc != 0 )); then
    echo "[$slot] FAILED: curl exit $rc (network/DNS/TLS). Nothing billed for this slot." >&2
    return 1
  fi
  if [[ ! "$http_code" =~ ^2 ]]; then
    local msg; msg=$(printf %s "$resp" | jq -r '.message // .error // empty' 2>/dev/null | head -c 200)
    echo "[$slot] FAILED: HTTP $http_code${msg:+ - $msg}" >&2
    return 1
  fi
  local id; id=$(printf %s "$resp" | jq -r '.id // empty')
  if [[ -z "$id" ]]; then
    echo "[$slot] FAILED: HTTP $http_code but no job id (see $OUT_DIR/$slot.json)." >&2
    return 1
  fi
  local status; status=$(printf %s "$resp" | jq -r '.status // empty')
  local credits; credits=$(printf %s "$resp" | jq -r '.data.creditsCharged // empty')
  echo "[$slot] id=$id status=$status credits=$credits dur=${duration}s"
}

export -f post_one lookup_startframe
export BASE AUTH_HDR PRODUCT_ID PROJECT_ID ASPECT RESOLUTION AUDIO_ENABLED OUT_DIR SF_MAP

# Cap concurrent billable calls. Override with MAX_PARALLEL=N.
MAX_PARALLEL="${MAX_PARALLEL:-5}"
OK=0; FAILED=0; TOTAL=0
PIDS=()

drain() {
  local pid
  if (( ${#PIDS[@]} )); then
    for pid in "${PIDS[@]}"; do
      if wait "$pid"; then OK=$((OK + 1)); else FAILED=$((FAILED + 1)); fi
    done
  fi
  PIDS=()
}

while IFS=$'\n' read -r line; do
  [[ -z "$line" || "$line" =~ ^# ]] && continue
  slot="${line%%::*}"; rest="${line#*::}"
  prompt="${rest%%::*}"; rest="${rest#*::}"
  duration="${rest%%::*}"; rest="${rest#*::}"
  still_key="${rest%%::*}"; var_idx="${rest##*::}"
  TOTAL=$((TOTAL + 1))
  post_one "$slot" "$prompt" "$duration" "$still_key" "$var_idx" &
  PIDS+=($!)
  if (( ${#PIDS[@]} >= MAX_PARALLEL )); then drain; fi
done
drain

echo "=== Seedance: $OK succeeded, $FAILED failed, of $TOTAL requested (max $MAX_PARALLEL in flight). ==="
if (( FAILED > 0 )); then
  echo "    $FAILED job(s) never started. Responses in $OUT_DIR/. Re-run only the failed slots." >&2
  exit 1
fi
echo "Poll with poll-and-download.sh."
