#!/usr/bin/env bash
# First-run setup for the Arcads skill pack.
# Creates .env, MASTER_CONTEXT.md, syncs skills, and verifies API connectivity.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Arcads Skill Pack Setup ==="
echo ""

BASE_URL="${ARCADS_BASE_URL:-https://external-api.arcads.ai}"

# Returns 0 if the given Basic auth header works against /v1/products, else non-zero.
validate_auth() {
  local header="$1"
  local code
  code="$(curl -sS -o /dev/null -w "%{http_code}" \
    -H "Authorization: $header" "$BASE_URL/v1/products" || echo "000")"
  [[ "$code" == "200" ]]
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
    echo "Validating against $BASE_URL/v1/products ..."
    for candidate in "${candidates[@]}"; do
      if validate_auth "$candidate"; then
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
    else
      echo "✗ Invalid credentials (Arcads rejected both header and raw-key interpretations). Attempts left: $((3 - attempts))"
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
