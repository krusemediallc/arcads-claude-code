# Arcads AI Video — Agent Skill Pack

Create AI marketing videos and images using your [Arcads](https://arcads.ai) account, powered by AI agents in **Claude Code** or **Cursor**. Supports Sora 2, Veo 3.1, Kling 3.0, and Nano Banana.

## Get started (5 minutes)

### 1. Clone this repo

```bash
git clone <repo-url>
cd arcads-agent-skills
```

### 2. Run setup

```bash
./scripts/setup.sh
```

This will:
- Ask for your **Arcads API key** (find it at [app.arcads.ai/settings/api](https://app.arcads.ai/settings/api))
- Save it securely in `.env` (never committed to git)
- Verify your connection to Arcads
- Create your personal `MASTER_CONTEXT.md` workspace file

### 3. Open in your AI editor

**Claude Code:** Open the folder. The agent loads the Arcads skill automatically.

**Cursor:** Open the folder. The skill is at `.cursor/skills/arcads-external-api/`.

### 4. Start creating

Ask the agent things like:
- "Generate a 10-second UGC-style video for my product"
- "Create a Veo 3.1 video of someone unboxing a phone"
- "Recreate this influencer's look from a reference photo"
- "Make a Nano Banana product hero image"

The agent handles API calls, polling, prompt engineering, and file organization.

## What's in the box

| Path | What it does |
|------|-------------|
| `skills/arcads-external-api/` | The skill: API reference, prompting guide, per-model prompt library |
| `MASTER_CONTEXT.template.md` | Template for your workspace context (credit costs, brand voice, learnings) |
| `MASTER_CONTEXT.md` | Your personalized copy (created by setup, not committed to git) |
| `.env` | Your API key (created by setup, never committed) |
| `scripts/setup.sh` | One-time setup |
| `scripts/sync-skill.sh` | Copies skill edits to `.claude/` and `.cursor/` directories |
| `scripts/check-arcads-env.sh` | Tests API connectivity |
| `references/` | Drop reference images here (influencers, products, aesthetics) — gitignored |

## Your API key

Your key authenticates with the Arcads API. During setup you paste it once and the agent uses it from `.env` automatically. You never need to paste it into chat.

Find your key: **[Arcads Dashboard > Settings > API](https://app.arcads.ai/settings/api)**

## Project memory

`MASTER_CONTEXT.md` is your workspace's living memory. The agent reads it at the start of every session and writes learnings back. It stores:

- **Default product** — auto-populated on first use so you're never asked "which product?" again
- **Credit costs** — you fill in once (or the agent asks), then every session has them
- **Brand voice** — optional tone, audience, and word preferences
- **API learnings** — universal Arcads quirks that help the agent work better
- **Changelog** — dated notes from each session

## Supported models

| Model | Type | Best for |
|-------|------|----------|
| **Sora 2** | Video | Longer videos (up to 20s), good dialogue, remix existing assets |
| **Veo 3.1** | Video | High-quality ~8s clips, start-frame consistency, 4K |
| **Kling 3.0** | Video | B-roll and scene generation |
| **Nano Banana** | Image | Still frames, product shots, influencer recreation stills |

## Reference images

Drop images into the `references/` folder and the agent will use them automatically:

- **`references/influencers/`** — Photos of people to recreate as AI-generated content
- **`references/products/`** — Product photos for showcase videos and hero images
- **`references/aesthetics/`** — Mood boards, lighting references, style inspiration

Images stay local — the folder contents are gitignored.

## Editing the skill

The canonical skill source lives in `skills/arcads-external-api/`. After editing any file there, run:

```bash
./scripts/sync-skill.sh
```

This copies your changes to `.claude/skills/` and `.cursor/skills/` (which are gitignored — they're generated copies).

## Security

- `.env` is gitignored — never committed
- `MASTER_CONTEXT.md` is gitignored — contains your product IDs and workspace data
- Never paste API keys in GitHub issues or public chats

## Vendor prompting guides

| Model | Guide |
|-------|--------|
| Sora 2 | [OpenAI — Sora 2 prompting guide](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide) |
| Veo 3.1 | [Google Cloud — Veo 3.1](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) |
| Kling 3.0 | [Kling — user guide](https://kling.ai/quickstart/klingai-video-3-model-user-guide) |
| Nano Banana | [Google Cloud — Nano Banana](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana) |

## API docs

[Arcads Swagger UI](https://external-api.arcads.ai/docs)

## Other AI assistants (Manus, Copilot, etc.)

Point your assistant at [AGENTS.md](AGENTS.md) and `MASTER_CONTEXT.md` + the skill path. See [AGENTS.md](AGENTS.md) for details.
