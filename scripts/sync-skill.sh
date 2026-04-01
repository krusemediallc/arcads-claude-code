#!/usr/bin/env bash
# Copies the canonical skill from skills/arcads-external-api to Claude Code and Cursor paths.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/skills/arcads-external-api"
if [[ ! -f "$SRC/SKILL.md" ]]; then
  echo "Expected $SRC/SKILL.md — aborting." >&2
  exit 1
fi
for dest in "$ROOT/.claude/skills/arcads-external-api" "$ROOT/.cursor/skills/arcads-external-api"; do
  rm -rf "$dest"
  mkdir -p "$(dirname "$dest")"
  cp -R "$SRC" "$dest"
done
echo "Synced arcads-external-api skill to .claude/skills and .cursor/skills"
