# Arcads external API — agent skill pack

Portable **Agent Skills** ([agentskills.io](https://agentskills.io/)) for the [Arcads external API](https://external-api.arcads.ai/docs): create and track AI creative assets (video-first; image-related asset types exist in the API), with a **prompting guide** and **per-model prompt library** (Sora 2, Veo 3.1, Kling 3.0, Nano Banana).

Works in **Claude Code** (`.claude/skills/`), **Cursor** (`.cursor/skills/`), and any tool that loads the same skill folder. Other assistants (e.g. Manus) can follow [AGENTS.md](AGENTS.md) and point the model at `MASTER_CONTEXT.md` + the skill path.

## Quick start

1. Clone this repo.
2. Copy `.env.example` to `.env` and add your Arcads API key (see **API key** below).
3. Optional: `chmod +x scripts/*.sh && ./scripts/check-arcads-env.sh` to verify auth (requires a valid key).
4. Open the project in **Cursor** or **Claude Code** — the skill **`arcads-external-api`** is preinstalled under both skill directories.

Canonical skill source lives in **`skills/arcads-external-api/`**. After editing it, run:

```bash
./scripts/sync-skill.sh
```

to copy changes to `.claude/skills/arcads-external-api/` and `.cursor/skills/arcads-external-api/`.

## API key (marketer-friendly)

**Recommended:** Put the key only in **`.env`** (create from `.env.example`). Open `.env` in the editor, paste the key, save. The AI agent does not need the secret in chat.

**Alternative:** Paste the key in chat and ask the agent to write `.env` for you. That is easy but **chat history may retain the secret**—rotate the key in Arcads if the conversation could be shared.

Authentication uses **HTTP Basic** with the API key as the **username** and an **empty password** (see the skill’s [reference.md](skills/arcads-external-api/reference.md)).

## Project memory

- **`MASTER_CONTEXT.md`** — living log: brand, decisions, learnings. Agents are instructed to read it at session start and append dated notes after substantive work ([CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md), [`.cursor/rules/project-context.mdc`](.cursor/rules/project-context.mdc)).

## Vendor prompting guides (primary models)

| Model | Guide |
|-------|--------|
| Sora 2 | [OpenAI — Sora 2 prompting guide](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide) |
| Veo 3.1 | [Google Cloud — Veo 3.1](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) |
| Kling 3.0 | [Kling — user guide](https://kling.ai/quickstart/klingai-video-3-model-user-guide) |
| Nano Banana | [Google Cloud — Nano Banana](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana) |

The repo links these from `skills/arcads-external-api/prompting/prompt-library/` and adds short checklists—not full copies of vendor docs.

## Security

- Never commit **`.env`** (gitignored).
- Do not paste API keys into GitHub issues or public chats unnecessarily.

## Docs

- Arcads Swagger: [https://external-api.arcads.ai/docs](https://external-api.arcads.ai/docs)

## Manus (or other assistants)

There is no universal standard for all tools. Point your assistant at:

- [AGENTS.md](AGENTS.md)
- [MASTER_CONTEXT.md](MASTER_CONTEXT.md)
- `skills/arcads-external-api/SKILL.md` (or the synced copy under `.cursor/skills/` / `.claude/skills/`)
