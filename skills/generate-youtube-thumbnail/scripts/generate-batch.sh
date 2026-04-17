#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Reusable YouTube thumbnail batch generator (Nano Banana via kie.ai API)
#
# This is a TEMPLATE. Copy to scripts/generate-thumbnails-vN.sh and customize:
#   1. Update REFERENCE_URLS array with your PUBLIC HTTPS URLs (see hosting note)
#   2. Replace PROMPTS array with your composed prompts
#   3. (Optional) switch MODEL to "nano-banana-pro" for 4K output
#   4. Run: bash scripts/generate-thumbnails-vN.sh > output/run.log 2>&1 &
#   5. Monitor: tail -F output/run.log | grep -E "DONE|FAILED|Task"
#
# Hosting note:
#   kie.ai does NOT accept file uploads or base64. Every entry in
#   REFERENCE_URLS must be a publicly reachable HTTPS URL returning an
#   image (Imgur direct link, Cloudflare R2 public bucket, Supabase Storage,
#   GitHub raw, etc.). See ../../kie-ai-external-api/SKILL.md →
#   "Reference images: hosting and public URLs".
#
# Features:
#   - POST /api/v1/jobs/createTask with {model, input}
#   - Parallel firing (default: all variations in parallel)
#   - Retry on failure
#   - Poll GET /api/v1/jobs/recordInfo?taskId=... until done
#   - Append log entry to logs/kie-api.jsonl (see logs/README.md)
#   - Downloads result image from data.response.resultUrls[0]
#
# Requires:
#   - .env with KIE_API_KEY
#   - Python 3 (for JSON handling)
#   - macOS bash 3.2+ or any bash 4+
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail
cd "$(dirname "$0")/.."
source .env

: "${KIE_API_KEY:?KIE_API_KEY not set in .env}"
API="${KIE_BASE_URL:-https://api.kie.ai}"

# ─── CONFIG ─────────────────────────────────────────────────────────────────
MODEL="nano-banana-2"            # or "nano-banana-pro" for 4K
ASPECT="16:9"                    # 1:1, 16:9, 9:16, 3:4, 4:3
OUTPUT_DIR="output/thumbnails-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$(pwd)/../../logs/kie-api.jsonl"
mkdir -p "$OUTPUT_DIR"

# ─── REFERENCE URLS ─────────────────────────────────────────────────────────
# Public HTTPS URLs only — kie.ai does not host your images.
# Aim for 5+ face references for good likeness alignment.
# Max 14 entries (Nano Banana image_input[] limit).

declare -a REFERENCE_URLS=(
  "https://REPLACE_WITH_YOUR_HOST/face/headshot.jpg"
  "https://REPLACE_WITH_YOUR_HOST/face/three-quarter.jpg"
  "https://REPLACE_WITH_YOUR_HOST/face/close-up.jpg"
  "https://REPLACE_WITH_YOUR_HOST/face/smile.jpg"
  "https://REPLACE_WITH_YOUR_HOST/face/neutral.jpg"
  "https://REPLACE_WITH_YOUR_HOST/logos/brand-1.png"
  "https://REPLACE_WITH_YOUR_HOST/logos/brand-2.png"
  # Add product photos, comparison material, etc. as needed (max 14 total)
)

# Quick sanity-check the URLs before burning generations.
for u in "${REFERENCE_URLS[@]}"; do
  if [[ "$u" == *"REPLACE_WITH_YOUR_HOST"* ]]; then
    echo "FAIL: Update REFERENCE_URLS with real public HTTPS URLs first." >&2
    exit 1
  fi
  code=$(curl -sS -o /dev/null -w "%{http_code}" -I "$u" || echo "000")
  if [ "$code" != "200" ]; then
    echo "WARN: $u returned HTTP $code (expected 200). Continuing anyway." >&2
  fi
done

# Build the JSON array of URLs once — same refs used for every generation.
REF_JSON=$(python3 -c "
import json, sys
print(json.dumps([$(printf '\"%s\",' "${REFERENCE_URLS[@]}" | sed 's/,$//')]))
")

# ─── HELPERS ────────────────────────────────────────────────────────────────

# Append a log line to logs/kie-api.jsonl. Never logs prompt text, URLs, or key.
# Args: task_id prompt state generation_time_sec result_count error
log_entry() {
  local task_id="$1" prompt="$2" state="$3" gen_sec="$4" result_count="$5" error="$6"
  local word_count
  word_count=$(echo "$prompt" | wc -w | tr -d ' ')
  python3 - "$task_id" "$MODEL" "$ASPECT" "${#REFERENCE_URLS[@]}" "$word_count" "$state" "$gen_sec" "$result_count" "$error" "$LOG_FILE" <<'PY'
import json, sys, datetime, os
task_id, model, aspect, ref_count, word_count, state, gen_sec, result_count, error, log_file = sys.argv[1:11]
success_flag = {"success": 1, "pending": 0, "failed": 2}.get(state, 0)
entry = {
  "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
  "endpoint": "POST /api/v1/jobs/createTask",
  "model": model,
  "taskId": task_id,
  "request": {
    "aspect_ratio": aspect,
    "imageInputCount": int(ref_count),
    "promptWordCount": int(word_count),
  },
  "response": {
    "successFlag": success_flag,
    "state": state,
    "generationTimeSec": int(gen_sec) if gen_sec else None,
    "resultUrlsCount": int(result_count) if result_count else 0,
    "error": error or None,
  },
}
os.makedirs(os.path.dirname(log_file), exist_ok=True)
with open(log_file, "a") as f:
  f.write(json.dumps(entry) + "\n")
PY
}

# Generate a single thumbnail: submit → poll → download.
generate_one() {
  local idx=$1
  local prompt=$2
  local started
  started=$(date +%s)
  echo "[#$idx] Submitting generation..."

  # Build request body via Python to handle JSON encoding safely.
  local body
  body=$(python3 -c "
import json
print(json.dumps({
  'model': '$MODEL',
  'input': {
    'prompt': '''$prompt'''.strip(),
    'image_input': json.loads('''$REF_JSON'''),
    'aspect_ratio': '$ASPECT',
  },
}))
")

  local response task_id
  response=$(curl -sS \
    -H "Authorization: Bearer $KIE_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "$API/api/v1/jobs/createTask" 2>&1)

  task_id=$(echo "$response" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('data', {}).get('taskId', '') or d.get('taskId', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")

  if [ -z "$task_id" ]; then
    echo "[#$idx] ERROR: $response"
    echo "$response" > "$OUTPUT_DIR/${idx}_error.json"
    log_entry "" "$prompt" "failed" "" "" "createTask returned no taskId"
    return 1
  fi

  log_entry "$task_id" "$prompt" "pending" "" "" ""
  echo "[#$idx] Task $task_id — polling..."

  local poll success_flag state url_count url
  for attempt in $(seq 1 60); do
    sleep 5
    poll=$(curl -sS \
      -H "Authorization: Bearer $KIE_API_KEY" \
      "$API/api/v1/jobs/recordInfo?taskId=$task_id" 2>&1)
    success_flag=$(echo "$poll" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('data', {}).get('successFlag', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")

    if [ "$success_flag" = "1" ]; then
      url=$(echo "$poll" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    urls = d.get('data', {}).get('response', {}).get('resultUrls', []) or []
    print(urls[0] if urls else '')
except Exception:
    print('')
" 2>/dev/null || echo "")
      url_count=$(echo "$poll" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(len(d.get('data', {}).get('response', {}).get('resultUrls', []) or []))
except Exception:
    print(0)
" 2>/dev/null || echo "0")
      local ended=$(date +%s)
      local gen_sec=$((ended - started))
      echo "[#$idx] DONE in ${gen_sec}s"
      echo "$poll" > "$OUTPUT_DIR/${idx}_task.json"
      if [ -n "$url" ]; then
        curl -sS -o "$OUTPUT_DIR/${idx}_thumbnail.png" "$url"
        echo "[#$idx] Downloaded"
      fi
      log_entry "$task_id" "$prompt" "success" "$gen_sec" "$url_count" ""
      return 0
    elif [ "$success_flag" = "2" ] || [ "$success_flag" = "3" ]; then
      local err
      err=$(echo "$poll" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('data', {}).get('error', '') or d.get('msg', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")
      echo "[#$idx] FAILED: $err"
      echo "$poll" > "$OUTPUT_DIR/${idx}_failed.json"
      local ended=$(date +%s)
      log_entry "$task_id" "$prompt" "failed" "$((ended - started))" "0" "$err"
      return 1
    fi
  done
  echo "[#$idx] TIMEOUT after 300s"
  local ended=$(date +%s)
  log_entry "$task_id" "$prompt" "failed" "$((ended - started))" "0" "polling timeout"
  return 1
}

# Wrapper: try once, then retry once after 15s.
run_with_retry() {
  local idx=$1
  local prompt=$2
  generate_one "$idx" "$prompt" || {
    echo "[#$idx] Retrying after 15s..."
    sleep 15
    generate_one "$idx" "$prompt" || echo "[#$idx] Failed twice — giving up"
  }
}

# ─── PROMPTS ────────────────────────────────────────────────────────────────
# Define your prompts here. Each entry generates one thumbnail.
# See ../prompting/guide.md and ../prompting/formulas.md for templates.

declare -a PROMPTS=(

# Example 1 — Peace-sign / branding formula
"YouTube thumbnail, 16:9 landscape. CRITICAL CHARACTER LIKENESS: The subject is the exact same person shown in ALL the face reference photos. Match his face EXACTLY: [DESCRIBE FEATURES]. Maintain the exact same facial proportions, eye shape, beard style, and skin tone as the reference photos. Do not generalize — this is a specific real person and his exact likeness must be preserved. He is wearing [CLOTHING]. The shot is a tight head-and-shoulders crop with his face large and prominent, filling the central 50 percent of the frame. NO HANDS VISIBLE. Just head and upper shoulders, facing camera. Expression: wide excited open-mouth smile showing teeth, eyebrows raised in genuine excitement, eyes wide. To his LEFT side at chest level is a large rounded-square app icon containing [LOGO 1 DESCRIPTION] — use the [LOGO 1] reference exactly. To his RIGHT side at chest level is a large rounded-square app icon containing [LOGO 2 DESCRIPTION] — use the [LOGO 2] reference exactly. Across the very top of the frame in massive bold yellow block letters with a thick black outline reads [TITLE]. Background: dark navy gradient with subtle blue glow. Style: clean high-impact YouTube thumbnail. Avoid: distorted face, hands visible, peace signs, generic face, blurry logos, illegible text."

# Add more prompts here, one per array entry
)

# ─── EXECUTION ──────────────────────────────────────────────────────────────

echo "═══════════════════════════════════════"
echo "Generating ${#PROMPTS[@]} thumbnails in parallel..."
echo "Model: $MODEL   Aspect: $ASPECT"
echo "References: ${#REFERENCE_URLS[@]} public URLs"
echo "Output: $OUTPUT_DIR"
echo "═══════════════════════════════════════"

for i in "${!PROMPTS[@]}"; do
  idx=$((i + 1))
  run_with_retry "$idx" "${PROMPTS[$i]}" &
  sleep 0.3  # small stagger to avoid per-second rate-limit races
done

wait

echo "═══════════════════════════════════════"
echo "DONE. Results in: $OUTPUT_DIR"
DOWNLOADED=$(ls "$OUTPUT_DIR"/*_thumbnail.png 2>/dev/null | wc -l | tr -d ' ')
ERRORS=$(ls "$OUTPUT_DIR"/*_error.json "$OUTPUT_DIR"/*_failed.json 2>/dev/null | wc -l | tr -d ' ')
echo "$DOWNLOADED downloaded, $ERRORS errors"
echo "═══════════════════════════════════════"
open "$OUTPUT_DIR" 2>/dev/null || true
