#!/bin/bash
# Poll MiniMax task IDs until they succeed or fail, then download the file.
# Usage: ./poll-minimax-and-download.sh <out-subdir> <slot1>=<task_id1> <slot2>=<task_id2> ...
# Example: ./poll-minimax-and-download.sh clips batch-a=176843862716480 brent=176843862716481
#
# Outputs land in $RUN_DIR/<out-subdir>/<slot>.{mp4|bin}
set -euo pipefail

set -a; source "${ENV_FILE:-$RUN_DIR/.env}" 2>/dev/null || source "$(git rev-parse --show-toplevel 2>/dev/null)/workspace/.env"; set +a

if [[ -z "${MINIMAX_API_KEY:-}" ]]; then
  echo "MINIMAX_API_KEY is required" >&2
  exit 1
fi

MINIMAX_REGION="${MINIMAX_REGION:-global_en}"
case "${MINIMAX_BASE_URL:-}" in
  "") case "$MINIMAX_REGION" in
    global_en) API_ROOT="https://api.minimax.io" ;;
    cn_zh) API_ROOT="https://api.minimaxi.com" ;;
    *) echo "unknown MINIMAX_REGION: $MINIMAX_REGION" >&2; exit 1 ;;
  esac ;;
  *) API_ROOT="${MINIMAX_BASE_URL%/}" ;;
esac
API_ROOT="${API_ROOT%/v1}"
API_ROOT="${API_ROOT%/v2}"
AUTH_HDR="Authorization: Bearer $MINIMAX_API_KEY"

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
MAX_ITERS="${MAX_ITERS:-90}"
POLL_INTERVAL="${POLL_INTERVAL:-15}"

while :; do
  iter=$((iter+1))
  pending=0
  echo "--- poll iter $iter ---"
  for i in "${!SLOT_NAMES[@]}"; do
    [[ "${SLOT_DONE[$i]}" == "1" ]] && continue
    slot="${SLOT_NAMES[$i]}"
    id="${SLOT_IDS[$i]}"
    resp=$(curl -sS -H "$AUTH_HDR" "$API_ROOT/v2/query/video_generation/$id")
    status=$(echo "$resp" | jq -r '.task.status // "?"')
    echo "  [$slot] $id status=$status"
    status_lc=$(printf '%s' "$status" | tr '[:upper:]' '[:lower:]')
    if [[ "$status_lc" == "success" ]]; then
      url=$(echo "$resp" | jq -r '.task.content.url // empty')
      if [[ -n "$url" ]]; then
        ext="${url##*.}"; ext="${ext%%\?*}"
        [[ -z "$ext" || ${#ext} -gt 5 ]] && ext="mp4"
        out="$OUT_DIR/$slot.$ext"
        echo "    -> downloading"
        curl -sS -L "$url" -o "$out"
      fi
      echo "$resp" > "$OUT_DIR/_resp/$slot.json"
      SLOT_DONE[$i]=1
    elif [[ "$status_lc" == "fail" ]]; then
      err=$(echo "$resp" | jq -r '.task.error.message // .task.error // "(no message)"')
      echo "    !! FAILED: $err"
      echo "$resp" > "$OUT_DIR/_resp/$slot.json"
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
