#!/usr/bin/env bash
# First-run setup for the Arcads skill pack.
# Creates .env, MASTER_CONTEXT.md, syncs skills, and verifies API connectivity.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Arcads Skill Pack Setup ==="
echo ""

BASE_URL="${ARCADS_BASE_URL:-https://external-api.arcads.ai}"

# ── Step 0: tool preflight ───────────────────────────────────────────────────
# Fail early and name the missing tool. A missing curl used to surface further
# down as "Invalid credentials", which sent people hunting for a key problem
# they did not have.
missing_required=()
for tool in curl base64 sed; do
  command -v "$tool" >/dev/null 2>&1 || missing_required+=("$tool")
done
if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
  missing_required+=("python3")
fi
if (( ${#missing_required[@]} )); then
  echo "Missing required tool(s): ${missing_required[*]}" >&2
  echo "" >&2
  echo "Install them, then re-run ./scripts/setup.sh:" >&2
  echo "  macOS:   brew install ${missing_required[*]}" >&2
  echo "  Linux:   sudo apt install ${missing_required[*]}" >&2
  echo "  Windows: use WSL2, or Git Bash (which ships curl and sed)." >&2
  exit 1
fi

# Optional tools. Only specific multi-step workflows need these, so warn and
# continue — the image and video API workflows work without them.
optional_missing=()
command -v jq      >/dev/null 2>&1 || optional_missing+=("jq      - pixar-style-ad / claymation-ad shell pipelines")
command -v ffmpeg  >/dev/null 2>&1 || optional_missing+=("ffmpeg  - video stitching and caption burn-in")
command -v node    >/dev/null 2>&1 || optional_missing+=("node    - caption-video (npx hyperframes)")
command -v whisper >/dev/null 2>&1 || optional_missing+=("whisper - caption transcription (pip install openai-whisper)")
if (( ${#optional_missing[@]} )); then
  echo "Optional tools not found. Image and video generation still work; these"
  echo "are only needed for the workflows named:"
  printf '  %s\n' "${optional_missing[@]}"
  echo ""
fi

# Set by validate_auth so the caller can report what actually went wrong.
LAST_AUTH_ERROR=""

# Returns 0 if the header works, 1 if Arcads rejected it, 2 if the request never
# completed. The caller must not report a transport failure as a bad credential.
validate_auth() {
  local header="$1"
  local code rc=0
  code="$(curl -sS -o /dev/null -w "%{http_code}" \
    -H "Authorization: $header" "$BASE_URL/v1/products" 2>/dev/null)" || rc=$?
  if (( rc != 0 )); then
    LAST_AUTH_ERROR="curl exited $rc - the request to $BASE_URL never completed (network, proxy, DNS or TLS)."
    return 2
  fi
  if [[ "$code" == "200" ]]; then
    return 0
  fi
  LAST_AUTH_ERROR="Arcads returned HTTP $code for GET /v1/products."
  return 1
}

# Mask all but the last 4 chars of a secret for display.
mask_secret() {
  local s="$1"
  local n=${#s}
  if (( n <= 4 )); then
    printf '****'
  else
    printf '%s%s' "$(printf '%*s' $((n-4)) '' | tr ' ' '*')" "${s: -4}"
  fi
}

# ── Step 1: .env ──────────────────────────────────────────────────────────────
if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Created .env from template."
  needs_key=1
elif grep -q "your_base64_encoded_credentials_here" "$ROOT/.env"; then
  echo ".env exists but still has placeholder credentials."
  needs_key=1
else
  echo ".env already exists with credentials — skipping prompt."
  needs_key=0
fi

if [[ "$needs_key" == "1" ]]; then
  echo ""
  echo "Need an Arcads account first? Sign up here: https://arcads.ai/?via=claude-code"
  echo "Then go to https://app.arcads.ai/settings/api and copy EITHER:"
  echo "  • the Basic auth header (e.g. 'Basic ODQxMTg4NDExZDY1NDQ0MmJk...'), OR"
  echo "  • the raw API key (we'll build the header for you)"
  echo ""

  attempts=0
  while (( attempts < 3 )); do
    attempts=$((attempts + 1))
    # -s hides input so the key never echoes or lands in scrollback.
    printf "Paste your Basic header or raw API key (input hidden, Enter to skip): "
    read -rs input
    printf "\n"

    if [[ -z "$input" ]]; then
      echo "Skipped — edit .env manually before using the skill."
      break
    fi

    # Try several interpretations of the input, validate each, use whichever works.
    candidates=()
    if [[ "$input" == Basic\ * ]]; then
      # Pasted with "Basic " prefix — try as-is, then strip and re-base64 in case
      # it's a raw key the user accidentally prepended "Basic " to.
      candidates+=("$input")
      stripped="${input#Basic }"
      candidates+=("Basic $(printf '%s:' "$stripped" | base64 | tr -d '\n')")
    else
      # No prefix. Could be (a) base64-encoded credentials already, or
      # (b) the raw API key. Try both.
      candidates+=("Basic $input")
      candidates+=("Basic $(printf '%s:' "$input" | base64 | tr -d '\n')")
    fi

    basic_auth=""
    raw_key=""
    transport_failed=0
    echo "Validating against $BASE_URL/v1/products ..."
    for candidate in "${candidates[@]}"; do
      verdict=0
      validate_auth "$candidate" || verdict=$?
      if (( verdict == 2 )); then
        # Never completed: the credential was not tested. Stop trying variants.
        transport_failed=1
        break
      fi
      if (( verdict == 0 )); then
        basic_auth="$candidate"
        # If the candidate came from base64-encoding the input, the input was the raw key.
        if [[ "$candidate" == "Basic $(printf '%s:' "$input" | base64 | tr -d '\n')" ]] \
           || [[ "$candidate" == "Basic $(printf '%s:' "${input#Basic }" | base64 | tr -d '\n')" ]]; then
          raw_key="${input#Basic }"
        fi
        break
      fi
    done

    if [[ -n "$basic_auth" ]]; then
      # Write Basic header (always). Also write API key if we recovered it.
      sed "s|ARCADS_BASIC_AUTH=.*|ARCADS_BASIC_AUTH='$basic_auth'|" "$ROOT/.env" > "$ROOT/.env.tmp" \
        && mv "$ROOT/.env.tmp" "$ROOT/.env"
      if [[ -n "$raw_key" ]] && grep -q "^# ARCADS_API_KEY=" "$ROOT/.env"; then
        sed "s|^# ARCADS_API_KEY=.*|ARCADS_API_KEY='$raw_key'|" "$ROOT/.env" > "$ROOT/.env.tmp" \
          && mv "$ROOT/.env.tmp" "$ROOT/.env"
      fi
      chmod 600 "$ROOT/.env" 2>/dev/null || true
      echo "✓ Valid. Saved to .env as $(mask_secret "$basic_auth")"
      unset input basic_auth raw_key candidates candidate
      break
    elif (( transport_failed )); then
      echo "✗ Could not reach Arcads — your credential was NOT tested, so this is"
      echo "  not a sign that it is wrong."
      echo "  $LAST_AUTH_ERROR"
      echo "  Fix the connection (network, VPN, corporate proxy) and re-run"
      echo "  ./scripts/setup.sh. Nothing was written to .env."
      unset input basic_auth raw_key candidates candidate
      break
    else
      echo "✗ Arcads rejected this credential (tried it as a Basic header and as a raw key)."
      echo "  $LAST_AUTH_ERROR"
      echo "  Copy it again from https://app.arcads.ai/settings/api — attempts left: $((3 - attempts))"
      unset input basic_auth raw_key candidates candidate
    fi
  done
fi

echo ""

# ── Step 2: MASTER_CONTEXT.md ────────────────────────────────────────────────
if [[ ! -f "$ROOT/MASTER_CONTEXT.md" ]]; then
  cp "$ROOT/MASTER_CONTEXT.template.md" "$ROOT/MASTER_CONTEXT.md"
  echo "Created MASTER_CONTEXT.md from template."
  echo "The agent will help you fill in credit costs and product info on first use."
else
  echo "MASTER_CONTEXT.md already exists — skipping."
fi

echo ""

# ── Step 3: Sync skills to .claude/ and .cursor/ ─────────────────────────────
"$ROOT/scripts/sync-skill.sh"

echo ""

# ── Step 4: Verify API connectivity ──────────────────────────────────────────
if grep -q "your_base64_encoded_credentials_here" "$ROOT/.env" 2>/dev/null || grep -q "your_key_here" "$ROOT/.env" 2>/dev/null; then
  echo "Credentials not yet set in .env — skipping connectivity check."
  echo "Run ./scripts/check-arcads-env.sh after adding your credentials."
else
  "$ROOT/scripts/check-arcads-env.sh"
fi

echo ""
echo "Setup complete. Open this folder in Claude Code or Cursor to start."
