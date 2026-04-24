# Arcads AI Video — Agent Skill Pack

Create AI marketing videos and images using your [Arcads](https://arcads.ai/?via=caleb) account, powered by AI agents in **Claude Code** or **Cursor**. Supports Sora 2, Veo 3.1, Kling 3.0, and Nano Banana.

## Level up your media buying with AI

This repo handles the **creative** side. If you want the full system — scaling, ROAS, automation, and the AI workflows behind 8-figure ad accounts — come build with me inside **[The AI Ad Alchemists](https://skool.com/mrpaidsocial)**.

It's a private Skool community of **460+ media buyers** managing 8-figure ad accounts, run by me (Caleb — aka "Mr. Paid Social") drawing on 12 years and **$150M+ in ad spend**. Inside you get:

- **Meta Masterclass** — the exact systems I use to scale Meta ads (valued at $1.2k)
- **Custom GPTs** for ad copywriting and compliance
- **Ad swipe files** + breakdowns of what's working *right now*
- **Airtable & Google Sheets scaling systems** — the operational backbone behind 8-fig accounts
- **AI tool walkthroughs** — including the Ad Agent (built in Claude Code) and the GenAI system in Airtable I'm shipping next
- **Monthly group calls** + guest speakers
- **Direct access** to me and the network

If you're using this repo to crank out creative, the community is where you learn to **turn that creative into ROAS at scale**.

**→ [Join The AI Ad Alchemists — $97/month](https://skool.com/mrpaidsocial)**

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
- If you need an Arcads account first, sign up here: [arcads.ai/?via=caleb](https://arcads.ai/?via=caleb)
- Ask for your **Arcads API key** (find it at [app.arcads.ai/settings/api](https://app.arcads.ai/settings/api))
- Save it securely in `.env` (never committed to git)
- Verify your connection to Arcads
- Create your personal `MASTER_CONTEXT.md` workspace file

### 3. Open in your AI editor

**Claude Code:** Open the folder. The agent loads the Arcads skill automatically.

**Cursor:** Open the folder. The skill is at `.cursor/skills/arcads-external-api/`.

### 4. Start creating

The agent handles API calls, polling, prompt engineering, and file organization. Here are the main workflows:

#### Create an AI influencer (character sheet)

> "Create a new AI influencer — a 22-year-old college student with freckles"

The agent generates a full-body hero image for your approval, then creates 9 additional angles (3/4 views, profile, closeup, etc.) using the hero as a reference. All 10 images are saved to `references/influencers/` for future use.

#### Generate UGC product selfie stills

> "Generate a UGC selfie of Sofia holding the Arcads Cola can in her bedroom"

Combines your character + product photo + style references from `references/aesthetics/ugc-selfie/` into an authentic-looking iPhone selfie frame grab. Includes skin realism and camera imperfections to fight AI's polished default.

#### Animate a still into video

> "Turn that image into a video — have her talk about the product"

Uses Veo 3.1 with `startFrame` to animate your approved UGC still. The video starts from that exact image with natural human motion (eye contact breaks, head tilts, body shifts) and dialogue.

#### Quick UGC video (no starting frame)

> "Generate a UGC video ad for this product" + drop a product photo

Uses Sora 2 with your product photo as a style reference to generate a video directly — no starting frame needed. Faster but less control over the person's appearance.

#### Other things to try

- "Recreate this influencer's look from a reference photo"
- "Make a Nano Banana product hero image"
- "Generate 5 different ad variations for this product"

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

Need an Arcads account first? Create one here: **[https://arcads.ai/?via=caleb](https://arcads.ai/?via=caleb)**

Find your key: **[Arcads Dashboard > Settings > API](https://app.arcads.ai/settings/api)**

## Project memory

`MASTER_CONTEXT.md` is your workspace's living memory. The agent reads it at the start of every session and writes learnings back. It stores:

- **Default product** — auto-populated on first use so you're never asked "which product?" again
- **Credit costs** — you fill in once (or the agent asks), then every session has them
- **Brand voice** — optional tone, audience, and word preferences
- **API learnings** — universal Arcads quirks that help the agent work better
- **Changelog** — dated notes from each session

## Supported models

| Model | Type | Best for | Credits |
|-------|------|----------|---------|
| **Veo 3.1** | Video | Animating a starting frame into ~8s video with dialogue. Best for UGC stills → video. | 1 |
| **Sora 2** | Video | Longer videos (up to 20s) from text prompts. Product photo as style ref (no starting frame). | varies |
| **Kling 3.0** | Video | B-roll and scene generation (via scene/b-roll endpoints) | varies |
| **Nano Banana 2** | Image | UGC stills, character sheets, product shots, influencer recreation | 0.03 |

## Reference images

Drop images into the `references/` folder and the agent will use them automatically:

- **`references/influencers/`** — Photos of people to recreate as AI-generated content
- **`references/products/`** — Product photos for showcase videos and hero images
- **`references/aesthetics/`** — Style references organized by vibe (`ugc-selfie/`, `cinematic/`, etc.)

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
