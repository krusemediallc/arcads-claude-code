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
  echo "Paste your Arcads API key below (find it at https://app.arcads.ai/settings/api)."
  echo "Press Enter to skip (you can edit .env manually later):"
  read -r api_key
  if [[ -n "$api_key" ]]; then
    # Portable sed: write to temp file then move (works on macOS and Linux)
    sed "s/your_key_here/$api_key/" "$ROOT/.env" > "$ROOT/.env.tmp" && mv "$ROOT/.env.tmp" "$ROOT/.env"
    echo "API key saved to .env"
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
if grep -q "your_key_here" "$ROOT/.env" 2>/dev/null; then
  echo "API key not yet set in .env — skipping connectivity check."
  echo "Run ./scripts/check-arcads-env.sh after adding your key."
else
  "$ROOT/scripts/check-arcads-env.sh"
fi

echo ""
echo "Setup complete. Open this folder in Claude Code or Cursor to start."
