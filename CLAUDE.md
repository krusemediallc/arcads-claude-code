@shared/CLAUDE.md

# Arcads-specific session rules

- **API:** Arcads external API (`https://external-api.arcads.ai`).
- **Auth:** HTTP Basic via `ARCADS_BASIC_AUTH` or `ARCADS_API_KEY`. Setup check: `./scripts/check-arcads-env.sh`.
- **Skill:** `.claude/skills/arcads-external-api/SKILL.md` for API calls, prompts, and polling.
- **YouTube thumbnails:** `.claude/skills/generate-youtube-thumbnail/SKILL.md` (uses the Nano Banana 2 image endpoint via Arcads).
- **Cost disclosure:** Always present credit totals as **estimates** — Arcads has no billing endpoint. Tell the user to confirm exact pricing in the Arcads platform.
- **Logging:** Log every generation call to `logs/arcads-api.jsonl`.
- **First-time setup:** If `.env` is missing, run `./scripts/setup.sh`. If `MASTER_CONTEXT.md` is missing, copy `MASTER_CONTEXT.template.md` to `MASTER_CONTEXT.md`.
