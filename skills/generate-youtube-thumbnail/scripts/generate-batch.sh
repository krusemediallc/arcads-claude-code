#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Reusable YouTube thumbnail batch generator (Nano Banana 2 via Arcads API)
#
# This is a TEMPLATE. Copy to scripts/generate-thumbnails-vN.sh and customize:
#   1. Update REF_BASE and COMMON_REFS array with your reference file paths
#   2. Replace PROMPTS array with your composed prompts
#   3. Run: bash scripts/generate-thumbnails-vN.sh > output/run.log 2>&1 &
#   4. Monitor: tail -F output/run.log | grep -E "DONE|FAILED|Asset"
#
# Features:
#   - Image upscaling (Lanczos to 1080px longest side, RGB JPEG)
#   - Presigned URL upload + S3 PUT
#   - Fresh upload per generation (avoids 500 errors from reused references)
#   - Parallel firing (default: all variations in parallel)
#   - Retry on failure
#   - Asset polling and download
#
# Requires:
#   - .env with ARCADS_BASIC_AUTH and ARCADS_API_KEY
#   - Python 3 with PIL/Pillow installed
#   - macOS bash 3.2+ or any bash 4+
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail
cd "$(dirname "$0")/.."
source .env

# ─── CONFIG ─────────────────────────────────────────────────────────────────
API="https://external-api.arcads.ai"
PRODUCT_ID="REPLACE_WITH_YOUR_PRODUCT_ID"  # from MASTER_CONTEXT.md
MODEL="nano-banana-2"
ASPECT="16:9"  # 1:1, 16:9, or 9:16
OUTPUT_DIR="${OUTPUT_BASE:-output}/thumbnails-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTPUT_DIR"
TMP_DIR="$OUTPUT_DIR/.tmp"
mkdir -p "$TMP_DIR"

# ─── REFERENCE IMAGES ───────────────────────────────────────────────────────
# Use absolute paths (filenames with spaces are fine).
# Aim for 5+ face references for good likeness alignment.
REF_BASE="$(pwd)/references/youtube thumbnail"

declare -a COMMON_REFS=(
  "${REF_BASE}/face/headshot.png"
  "${REF_BASE}/face/three-quarter.png"
  "${REF_BASE}/face/close-up.png"
  "${REF_BASE}/face/smile.png"
  "${REF_BASE}/face/neutral.png"
  "${REF_BASE}/logos/brand-1.png"
  "${REF_BASE}/logos/brand-2.png"
  # Add product photos, comparison material, etc. as needed (max 14 total)
)

# Verify all references exist before starting
for f in "${COMMON_REFS[@]}"; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f" >&2
    exit 1
  fi
done

# ─── HELPERS ────────────────────────────────────────────────────────────────

# Upscale image to ≥1080px longest side and convert to RGB JPEG.
# Required because Nano Banana 2 rejects images <1080px with 422.
prepare_image() {
  python3 - "$1" "$2" <<'PY'
import sys
from PIL import Image
inp, out = sys.argv[1], sys.argv[2]
img = Image.open(inp).convert("RGB")
w, h = img.size
longest = max(w, h)
if longest < 1080:
    scale = 1080.0 / longest
    img = img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
img.save(out, "JPEG", quality=92)
PY
}

# Get presigned upload URL, PUT the file, return the filePath string.
upload_file() {
  local file="$1"
  local prepared="$TMP_DIR/$(basename "$file" | tr ' ' '_')_$$_$RANDOM.jpg"
  prepare_image "$file" "$prepared"

  local presign_resp presigned_url file_path
  presign_resp=$(curl -sS -X POST \
    -H "Authorization: $ARCADS_BASIC_AUTH" \
    -H "Content-Type: application/json" \
    -d '{"fileType":"image/jpeg"}' \
    "$API/v1/file-upload/get-presigned-url")
  presigned_url=$(echo "$presign_resp" | python3 -c "import json,sys; print(json.load(sys.stdin).get('presignedUrl',''))")
  file_path=$(echo "$presign_resp" | python3 -c "import json,sys; print(json.load(sys.stdin).get('filePath',''))")

  if [ -z "$presigned_url" ] || [ -z "$file_path" ]; then
    echo "PRESIGN FAIL: $presign_resp" >&2
    return 1
  fi

  curl -sS -X PUT \
    -H "Content-Type: image/jpeg" \
    --data-binary "@$prepared" \
    "$presigned_url" >/dev/null
  echo "$file_path"
}

# Upload all common references and return a JSON array of filePath strings.
# CRITICAL: Always upload fresh per generation. Re-using filePaths across
# generations causes HTTP 500 UNKNOWN_ERROR.
upload_all_fresh() {
  local out=""
  for f in "${COMMON_REFS[@]}"; do
    local fp
    fp=$(upload_file "$f") || return 1
    if [ -z "$out" ]; then out="\"$fp\""; else out="$out,\"$fp\""; fi
  done
  echo "[$out]"
}

# Generate a single thumbnail: upload refs → submit → poll → download.
generate_one() {
  local idx=$1
  local prompt=$2
  echo "[#$idx] Uploading fresh references..."
  local ref_json
  ref_json=$(upload_all_fresh) || { echo "[#$idx] Upload failed"; return 1; }
  echo "[#$idx] Submitting generation..."

  # Build request body via Python to handle JSON encoding safely.
  local body
  body=$(python3 -c "
import json
print(json.dumps({
  'productId': '$PRODUCT_ID',
  'prompt': '''$prompt'''.strip(),
  'model': '$MODEL',
  'aspectRatio': '$ASPECT',
  'referenceImages': $ref_json
}))
")

  local response asset_id
  response=$(curl -sS \
    -H "Authorization: $ARCADS_BASIC_AUTH" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "$API/V2/images/generate" 2>&1)

  asset_id=$(echo "$response" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(d.get('id','') or d.get('data',{}).get('id',''))
" 2>/dev/null || echo "")

  if [ -z "$asset_id" ]; then
    echo "[#$idx] ERROR: $response"
    echo "$response" > "$OUTPUT_DIR/${idx}_error.json"
    return 1
  fi

  echo "[#$idx] Asset $asset_id — polling..."
  local poll status url
  for attempt in $(seq 1 60); do
    sleep 5
    poll=$(curl -sS -H "Authorization: $ARCADS_BASIC_AUTH" "$API/v1/assets/$asset_id" 2>&1)
    status=$(echo "$poll" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null || echo "unknown")

    if [ "$status" = "generated" ]; then
      url=$(echo "$poll" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('url',''))" 2>/dev/null || echo "")
      echo "[#$idx] DONE!"
      echo "$poll" > "$OUTPUT_DIR/${idx}_asset.json"
      if [ -n "$url" ]; then
        curl -sS -o "$OUTPUT_DIR/${idx}_thumbnail.png" "$url"
        echo "[#$idx] Downloaded"
      fi
      return 0
    elif [ "$status" = "failed" ]; then
      echo "[#$idx] FAILED: $poll"
      echo "$poll" > "$OUTPUT_DIR/${idx}_failed.json"
      return 1
    fi
  done
  echo "[#$idx] TIMEOUT after 300s"
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
echo "Output: $OUTPUT_DIR"
echo "═══════════════════════════════════════"

for i in "${!PROMPTS[@]}"; do
  idx=$((i + 1))
  run_with_retry "$idx" "${PROMPTS[$i]}" &
  sleep 0.3  # small stagger to avoid presign endpoint race
done

wait

echo "═══════════════════════════════════════"
echo "DONE. Results in: $OUTPUT_DIR"
DOWNLOADED=$(ls "$OUTPUT_DIR"/*_thumbnail.png 2>/dev/null | wc -l | tr -d ' ')
ERRORS=$(ls "$OUTPUT_DIR"/*_error.json "$OUTPUT_DIR"/*_failed.json 2>/dev/null | wc -l | tr -d ' ')
echo "$DOWNLOADED downloaded, $ERRORS errors"
echo "═══════════════════════════════════════"
open "$OUTPUT_DIR" 2>/dev/null || true
