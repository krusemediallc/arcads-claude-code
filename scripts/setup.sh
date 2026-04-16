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
  echo "Need an Arcads account first? Sign up here: https://arcads.ai/?via=caleb"
  echo "Then go to https://app.arcads.ai/settings/api and copy your Basic auth header."
  echo "It looks like: Basic ODQxMTg4NDExZDY1NDQ0MmJk..."
  echo ""

  attempts=0
  while (( attempts < 3 )); do
    attempts=$((attempts + 1))
    # -s hides input so the key never echoes or lands in scrollback.
    printf "Paste your Basic auth header (input hidden, Enter to skip): "
    read -rs basic_auth
    printf "\n"

    if [[ -z "$basic_auth" ]]; then
      echo "Skipped — edit .env manually before using the skill."
      break
    fi

    # Normalize: prepend "Basic " if missing.
    if [[ "$basic_auth" != Basic\ * ]]; then
      basic_auth="Basic $basic_auth"
    fi

    echo "Validating against $BASE_URL/v1/products ..."
    if validate_auth "$basic_auth"; then
      # Write to .env with single quotes to handle special characters.
      sed "s|ARCADS_BASIC_AUTH=.*|ARCADS_BASIC_AUTH='$basic_auth'|" "$ROOT/.env" > "$ROOT/.env.tmp" \
        && mv "$ROOT/.env.tmp" "$ROOT/.env"
      chmod 600 "$ROOT/.env" 2>/dev/null || true
      echo "✓ Valid. Saved to .env as $(mask_secret "$basic_auth")"
      unset basic_auth
      break
    else
      echo "✗ Invalid credentials (Arcads rejected them). Attempts left: $((3 - attempts))"
      unset basic_auth
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
