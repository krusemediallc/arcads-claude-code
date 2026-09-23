#!/bin/bash
# Poll Arcads asset IDs until all are 'generated' or 'failed', then download.
# Usage: ./poll-and-download.sh <out-subdir> <slot1>=<id1> <slot2>=<id2> ...
# Example: ./poll-and-download.sh stills/batch-a pain-cpm=abc123 brent=def456
#
# Outputs land in $RUN_DIR/<out-subdir>/<slot>.{png|mp4}
set -euo pipefail

set -a; source "${ENV_FILE:-$RUN_DIR/.env}" 2>/dev/null || source "$(git rev-parse --show-toplevel 2>/dev/null)/workspace/.env"; set +a

BASE="${ARCADS_BASE_URL:-https://external-api.arcads.ai}"
AUTH_HDR="Authorization: ${ARCADS_BASIC_AUTH:-Basic $(printf '%s:' "$ARCADS_API_KEY" | base64)}"

SUBDIR="$1"; shift
OUT_DIR="$RUN_DIR/$SUBDIR"
mkdir -p "$OUT_DIR/_resp"

SLOT_NAMES=()
SLOT_IDS=()
SLOT_DONE=()
for kv in "$@"; do
  SLOT_NAMES+=("${kv%%=*}")
  SLOT_IDS+=("${kv#*=}")
  SLOT_DONE+=(0)
done

iter=0
MAX_ITERS="${MAX_ITERS:-90}"     # 90 x 15s = 22.5 min
POLL_INTERVAL="${POLL_INTERVAL:-15}"

while :; do
  iter=$((iter+1))
  pending=0
  echo "--- poll iter $iter ---"
  for i in "${!SLOT_NAMES[@]}"; do
    [[ "${SLOT_DONE[$i]}" == "1" ]] && continue
    slot="${SLOT_NAMES[$i]}"
    id="${SLOT_IDS[$i]}"
    resp=$(curl -sS -H "$AUTH_HDR" "$BASE/v1/assets/$id")
    status=$(echo "$resp" | jq -r '.status // "?"')
    echo "  [$slot] $id status=$status"
    if [[ "$status" == "generated" ]]; then
      url=$(echo "$resp" | jq -r '.url // .data.url // empty')
      if [[ -n "$url" ]]; then
        ext="${url##*.}"; ext="${ext%%\?*}"
        [[ -z "$ext" || ${#ext} -gt 5 ]] && ext="bin"
        out="$OUT_DIR/$slot.$ext"
        echo "    -> downloading"
        curl -sS -L "$url" -o "$out"
        echo "$resp" > "$OUT_DIR/_resp/$slot.json"
      fi
      SLOT_DONE[$i]=1
    elif [[ "$status" == "failed" ]]; then
      err=$(echo "$resp" | jq -r '.data.error.message // .errorMessage // "(no message)"')
      echo "    !! FAILED: $err"
      SLOT_DONE[$i]=1
    else
      pending=$((pending+1))
    fi
  done
  if [[ $pending -eq 0 ]]; then
    echo "=== all done ==="
    break
  fi
  if [[ $iter -gt $MAX_ITERS ]]; then
    echo "!! timeout after $iter iterations"
    break
  fi
  sleep "$POLL_INTERVAL"
done
ls -la "$OUT_DIR" 2>/dev/null | grep -v _resp || true
