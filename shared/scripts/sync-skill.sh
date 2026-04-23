#!/usr/bin/env bash
# Copies all canonical skills from skills/ to Claude Code and Cursor paths.
# Called automatically by scripts/setup.sh and by the SessionStart hook in .claude/settings.json.
# Run manually after editing any file under skills/.
#
# Resolves project root robustly so it works whether invoked as `scripts/sync-skill.sh`
# (the legacy location) or `shared/scripts/sync-skill.sh` (the propagated copy).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# If we landed inside shared/, the actual project root is one level up.
if [[ "$(basename "$ROOT")" == "shared" ]]; then
  ROOT="$(dirname "$ROOT")"
fi

SRC_DIR="$ROOT/skills"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Expected $SRC_DIR — aborting." >&2
  exit 1
fi

# Sync every top-level directory under skills/ that contains a SKILL.md
for skill_path in "$SRC_DIR"/*/; do
  skill_name=$(basename "$skill_path")
  if [[ ! -f "$skill_path/SKILL.md" ]]; then
    echo "Skipping $skill_name — no SKILL.md found"
    continue
  fi
  for dest in "$ROOT/.claude/skills/$skill_name" "$ROOT/.cursor/skills/$skill_name"; do
    rm -rf "$dest"
    mkdir -p "$(dirname "$dest")"
    cp -R "$skill_path" "$dest"
  done
  echo "Synced $skill_name skill to .claude/skills and .cursor/skills"
done
