#!/usr/bin/env bash
# First-run setup for the kie.ai skill pack.
# Creates .env, MASTER_CONTEXT.md, syncs skills, and verifies API connectivity.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== kie.ai Skill Pack Setup ==="
echo ""

BASE_URL="${KIE_BASE_URL:-https://api.kie.ai}"

# Returns 0 if the given Bearer token works against /api/v1/jobs/createTask,
# else non-zero. We send an empty body: kie.ai validates auth before body, so
# a good key returns 400/422 (body rejected) and a bad key returns 401.
validate_auth() {
  local key="$1"
  local code
  code="$(curl -sS -o /dev/null -w "%{http_code}" \
    -X POST "$BASE_URL/api/v1/jobs/createTask" \
    -H "Authorization: Bearer $key" \
    -H "Content-Type: application/json" \
    -d '{}' || echo "000")"
  case "$code" in
    200|400|402|422) return 0 ;;  # key accepted
    *) return 1 ;;                 # 401 or other → rejected
  esac
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
elif grep -q "your_kie_api_key_here" "$ROOT/.env"; then
  echo ".env exists but still has placeholder credentials."
  needs_key=1
else
  echo ".env already exists with credentials — skipping prompt."
  needs_key=0
fi

if [[ "$needs_key" == "1" ]]; then
  echo ""
  echo "Create a kie.ai API key at: https://kie.ai/api-key"
  echo "The key looks like: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  echo ""

  attempts=0
  while (( attempts < 3 )); do
    attempts=$((attempts + 1))
    # -s hides input so the key never echoes or lands in scrollback.
    printf "Paste your kie.ai API key (input hidden, Enter to skip): "
    read -rs kie_key
    printf "\n"

    if [[ -z "$kie_key" ]]; then
      echo "Skipped — edit .env manually before using the skill."
      break
    fi

    # Strip a leading "Bearer " if the user pasted the full header.
    kie_key="${kie_key#Bearer }"

    echo "Validating against $BASE_URL/api/v1/jobs/createTask ..."
    if validate_auth "$kie_key"; then
      # Write to .env with single quotes to handle special characters.
      sed "s|KIE_API_KEY=.*|KIE_API_KEY='$kie_key'|" "$ROOT/.env" > "$ROOT/.env.tmp" \
        && mv "$ROOT/.env.tmp" "$ROOT/.env"
      chmod 600 "$ROOT/.env" 2>/dev/null || true
      echo "✓ Valid. Saved to .env as $(mask_secret "$kie_key")"
      unset kie_key
      break
    else
      echo "✗ Invalid credentials (kie.ai rejected them). Attempts left: $((3 - attempts))"
      unset kie_key
    fi
  done
fi

echo ""

# ── Step 2: MASTER_CONTEXT.md ────────────────────────────────────────────────
if [[ ! -f "$ROOT/MASTER_CONTEXT.md" ]]; then
  cp "$ROOT/MASTER_CONTEXT.template.md" "$ROOT/MASTER_CONTEXT.md"
  echo "Created MASTER_CONTEXT.md from template."
  echo "The agent will help you fill in credit costs and brand voice on first use."
else
  echo "MASTER_CONTEXT.md already exists — skipping."
fi

echo ""

# ── Step 3: Sync skills to .claude/ and .cursor/ ─────────────────────────────
"$ROOT/scripts/sync-skill.sh"

echo ""

# ── Step 4: Verify API connectivity ──────────────────────────────────────────
if grep -q "your_kie_api_key_here" "$ROOT/.env" 2>/dev/null; then
  echo "Credentials not yet set in .env — skipping connectivity check."
  echo "Run ./scripts/check-kie-env.sh after adding your KIE_API_KEY."
else
  "$ROOT/scripts/check-kie-env.sh"
fi

echo ""
echo "Setup complete. Open this folder in Claude Code or Cursor to start."
