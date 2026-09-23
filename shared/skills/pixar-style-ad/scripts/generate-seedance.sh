#!/bin/bash
# Fire N MiniMax H3 image-to-video jobs in parallel (one per still × variation).
# Reads jobs from STDIN:
#   <slot>::<prompt-text>::<duration-seconds>::<still-slot>::<variation-idx>
#
# Looks up the first-frame source from $RUN_DIR/references/seedance-startframes.txt
# (produced by upload-startframes.sh). Format there: <still-slot>:<var>:<local-path-or-url>
#
# Example:
#   cat <<EOF | ./generate-seedance.sh clips
#   pain-cpm-v1::3D animated film aesthetic, image-to-video of @(img1)...::4::pain-cpm::1
#   pain-cpm-v2::3D animated film aesthetic, image-to-video of @(img1)...::4::pain-cpm::2
#   brent-reveal-v1::3D animated film aesthetic, image-to-video of @(img1)...::8::brent-reveal::1
#   EOF
#
# Required env: MINIMAX_API_KEY, RUN_DIR
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
MODEL="${MINIMAX_MODEL:-MiniMax-H3}"
RESOLUTION="${MINIMAX_RESOLUTION:-2K}"
RATIO="${MINIMAX_RATIO:-adaptive}"
CALLBACK_URL="${MINIMAX_CALLBACK_URL:-}"

SUBDIR="$1"
OUT_DIR="$RUN_DIR/$SUBDIR/_resp"
SF_MAP="$RUN_DIR/references/seedance-startframes.txt"
mkdir -p "$OUT_DIR"

lookup_startframe() {
  local key="$1:$2"
  grep -m 1 "^$key:" "$SF_MAP" | cut -d: -f3-
}

to_image_url() {
  local source="$1"
  if [[ "$source" =~ ^https?:// || "$source" =~ ^data: ]]; then
    printf '%s' "$source"
    return 0
  fi
  if [[ ! -f "$source" ]]; then
    echo "[$source] !! missing local first-frame source" >&2
    return 1
  fi
  local mime="image/png"
  case "$source" in
    *.jpg|*.jpeg|*.JPG|*.JPEG) mime="image/jpeg" ;;
    *.png|*.PNG) mime="image/png" ;;
    *.webp|*.WEBP) mime="image/webp" ;;
    *.heic|*.HEIC) mime="image/heic" ;;
    *.heif|*.HEIF) mime="image/heif" ;;
  esac
  local encoded
  encoded="$(base64 < "$source" | tr -d '\n')"
  printf 'data:%s;base64,%s' "$mime" "$encoded"
}

post_one() {
  local slot="$1" prompt="$2" duration="$3" still_key="$4" var_idx="$5"
  local sf; sf=$(lookup_startframe "$still_key" "$var_idx")
  if [[ -z "$sf" ]]; then
    echo "[$slot] !! no first-frame source in $SF_MAP for $still_key:$var_idx" >&2
    return 1
  fi
  local image_url; image_url=$(to_image_url "$sf")
  local body
  body=$(jq -n --arg model "$MODEL" --arg p "$prompt" --arg image_url "$image_url" --arg resolution "$RESOLUTION" --arg ratio "$RATIO" --arg callback_url "$CALLBACK_URL" --argjson dur "$duration" '{model:$model,content:[{type:"text",text:$p},{type:"image_url",image_url:{url:$image_url},role:"first_frame"}],resolution:$resolution,duration:$dur,ratio:$ratio} + (if $callback_url != "" then {callback_url:$callback_url} else {} end)')
  local resp
  resp=$(curl -sS -H "$AUTH_HDR" -H "Content-Type: application/json" -X POST "$API_ROOT/v2/video_generation" -d "$body")
  echo "$resp" > "$OUT_DIR/$slot.json"
  local id; id=$(echo "$resp" | jq -r '.task_id // .id // empty')
  local status; status=$(echo "$resp" | jq -r '.status // .task.status // empty')
  local err; err=$(echo "$resp" | jq -r '.error.message // .message // .base_resp.status_msg // empty')
  if [[ -n "$err" || -z "$id" ]]; then
    [[ -n "$err" ]] || err="response did not include task_id"
    echo "[$slot] task_id=$id status=$status error=$err" >&2
    return 1
  fi
  echo "[$slot] task_id=$id status=$status dur=${duration}s"
}

export -f post_one lookup_startframe to_image_url
export API_ROOT AUTH_HDR MODEL RESOLUTION RATIO CALLBACK_URL OUT_DIR SF_MAP

PIDS=()
while IFS=$'\n' read -r line; do
  [[ -z "$line" || "$line" =~ ^# ]] && continue
  slot="${line%%::*}"; rest="${line#*::}"
  prompt="${rest%%::*}"; rest="${rest#*::}"
  duration="${rest%%::*}"; rest="${rest#*::}"
  still_key="${rest%%::*}"; var_idx="${rest##*::}"
  post_one "$slot" "$prompt" "$duration" "$still_key" "$var_idx" &
  PIDS+=($!)
done
for pid in "${PIDS[@]}"; do wait "$pid"; done

echo "=== Issued ${#PIDS[@]} MiniMax jobs. Poll with poll-minimax-and-download.sh. ==="
