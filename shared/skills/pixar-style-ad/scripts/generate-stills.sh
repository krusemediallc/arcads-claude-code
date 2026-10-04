#!/bin/bash
# Fire N gpt-image-2 image generation calls in parallel.
# Each call uses a different prompt; optionally each can pull a different
# reference image (for character continuity between beats).
#
# Reads jobs from STDIN, one per line:
#   <slot>::<prompt-text>::<optional-comma-separated-reference-image-filePaths>
#
# Example:
#   cat <<EOF | ./generate-stills.sh stills/batch-a
#   pain-cpm::Pixar-style $47.83 dollar amount character...::
#   brent-reveal::Pixar-style mid-30s man holding laptop...::external-api-temp-uploads/abc.png
#   EOF
#
# Required env: ARCADS_BASIC_AUTH, PRODUCT_ID, PROJECT_ID, RUN_DIR
set -euo pipefail

set -a; source "${ENV_FILE:-$RUN_DIR/.env}" 2>/dev/null || source "$(git rev-parse --show-toplevel 2>/dev/null)/workspace/.env"; set +a

BASE="${ARCADS_BASE_URL:-https://external-api.arcads.ai}"
AUTH_HDR="Authorization: ${ARCADS_BASIC_AUTH:-Basic $(printf '%s:' "$ARCADS_API_KEY" | base64)}"
MODEL="${IMAGE_MODEL:-gpt-image-2}"   # or nano-banana, nano-banana-2
ASPECT="${ASPECT_RATIO:-9:16}"

SUBDIR="$1"
OUT_DIR="$RUN_DIR/$SUBDIR/_resp"
mkdir -p "$OUT_DIR"

post_one() {
  local slot="$1" prompt="$2" refs_csv="$3"
  local refs_json='[]'
  if [[ -n "$refs_csv" ]]; then
    refs_json=$(echo "$refs_csv" | tr ',' '\n' | jq -R . | jq -s .)
  fi
  local body
  body=$(jq -n \
    --arg model "$MODEL" --arg productId "$PRODUCT_ID" --arg projectId "$PROJECT_ID" \
    --arg prompt "$prompt" --arg aspectRatio "$ASPECT" --argjson refs "$refs_json" \
    '{model:$model, productId:$productId, projectId:$projectId, prompt:$prompt, aspectRatio:$aspectRatio} + (if ($refs|length)>0 then {referenceImages:$refs} else {} end)')

  # curl -sS alone exits 0 on HTTP 4xx/5xx, so capture the status code too and
  # treat "no asset id" as failure. Otherwise a rejected batch looks successful.
  local raw rc=0
  raw=$(curl -sS -w $'\n%{http_code}' -H "$AUTH_HDR" -H "Content-Type: application/json" \
    -X POST "$BASE/v2/images/generate" -d "$body") || rc=$?
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
    echo "[$slot] FAILED: HTTP $http_code but no asset id (see $OUT_DIR/$slot.json)." >&2
    return 1
  fi
  local status; status=$(printf %s "$resp" | jq -r '.status // empty')
  echo "[$slot] id=$id status=$status"
}

export -f post_one
export BASE AUTH_HDR PRODUCT_ID PROJECT_ID MODEL ASPECT OUT_DIR

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
  prompt="${rest%%::*}"; refs="${rest#*::}"
  TOTAL=$((TOTAL + 1))
  post_one "$slot" "$prompt" "$refs" &
  PIDS+=($!)
  if (( ${#PIDS[@]} >= MAX_PARALLEL )); then drain; fi
done
drain

echo "=== Stills: $OK succeeded, $FAILED failed, of $TOTAL requested (max $MAX_PARALLEL in flight). ==="
if (( FAILED > 0 )); then
  echo "    $FAILED slot(s) never started. Responses in $OUT_DIR/. Re-run only the failed slots." >&2
  exit 1
fi
echo "Now run poll-and-download.sh with the returned IDs."
