#!/usr/bin/env bash
# First-run setup for the Arcads skill pack.
# Creates .env, MASTER_CONTEXT.md, syncs skills, and verifies API connectivity.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Arcads Skill Pack Setup ==="
echo ""

# ── Step 1: .env ──────────────────────────────────────────────────────────────
if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Created .env from template."
  echo ""
  echo "Go to https://app.arcads.ai/settings/api and copy your Basic auth header."
  echo "It looks like: Basic ODQxMTg4NDExZDY1NDQ0MmJk..."
  echo ""
  echo "Paste it below (or press Enter to skip and edit .env manually):"
  read -r basic_auth
  if [[ -n "$basic_auth" ]]; then
    # Ensure it starts with 'Basic '
    if [[ "$basic_auth" != Basic\ * ]]; then
      basic_auth="Basic $basic_auth"
    fi
    # Write to .env with single quotes to handle special characters
    sed "s|ARCADS_BASIC_AUTH=.*|ARCADS_BASIC_AUTH='$basic_auth'|" "$ROOT/.env" > "$ROOT/.env.tmp" && mv "$ROOT/.env.tmp" "$ROOT/.env"
    echo "Auth header saved to .env"
  else
    echo "Skipped — edit .env manually before using the skill."
  fi
else
  echo ".env already exists — skipping."
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
