# Agent instructions

This repository is set up for AI coding agents (Cursor, Claude Code, Copilot-style tools, etc.).

## First-time setup

If `.env` or `MASTER_CONTEXT.md` do not exist, tell the user to run `./scripts/setup.sh`.

## Every session

1. Read **[MASTER_CONTEXT.md](MASTER_CONTEXT.md)** for brand voice, cost rates, and learnings.
2. Follow the skill at `.cursor/skills/kie-ai-external-api/` or `.claude/skills/kie-ai-external-api/` (synced from `skills/kie-ai-external-api/` via `scripts/sync-skill.sh`).
3. If `MASTER_CONTEXT.md` has empty fields (cost rates, brand voice), offer to populate them — ask the user and write the values back so future sessions have them.
4. After material changes, add a dated entry to **MASTER_CONTEXT.md** Changelog.
