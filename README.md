# kie.ai AI Video — Agent Skill Pack

Create AI marketing videos and images using your [kie.ai](https://kie.ai) account, powered by AI agents in **Claude Code** or **Cursor**. Supports Seedance 2.0, Sora 2, Sora 2 Pro, Veo 3 / 3.1, Kling 2.6 / 3.0, and Nano Banana 2 / Pro.

## Get started (5 minutes)

### 1. Clone this repo

```bash
git clone <repo-url>
cd arcads-claude-code
```

### 2. Run setup

```bash
./scripts/setup.sh
```

This will:
- If you don't have a kie.ai account yet, create one at [kie.ai](https://kie.ai)
- Ask for your **kie.ai API key** (create one at [kie.ai/api-key](https://kie.ai/api-key))
- Save it securely in `.env` (never committed to git)
- Verify your connection to kie.ai
- Create your personal `MASTER_CONTEXT.md` workspace file

### 3. Open in your AI editor

**Claude Code:** Open the folder. The agent loads the kie-ai-external-api skill automatically.

**Cursor:** Open the folder. The skill is at `.cursor/skills/kie-ai-external-api/`.

### 4. Start creating

The agent handles API calls, polling, prompt engineering, and file organization. Main workflows:

#### Create an AI influencer (character sheet)

> "Create a new AI influencer — a 22-year-old college student with freckles"

The agent generates a full-body hero image for your approval, then creates 9 additional angles (3/4 views, profile, closeup, etc.) using the hero as a reference via Nano Banana 2. All 10 images are saved to `references/influencers/` for future use.

#### Generate UGC product selfie stills

> "Generate a UGC selfie of Sofia holding the Nova Cola can in her bedroom"

Combines your character + product photo + style references from `references/aesthetics/ugc-selfie/` into an authentic-looking iPhone selfie frame grab. Includes skin realism and camera imperfections to fight AI's polished default.

#### Animate a still into video

> "Turn that image into a video — have her talk about the product"

Uses Seedance 2.0 (`first_frame_url`) or Veo 3.1 (`FIRST_AND_LAST_FRAMES_2_VIDEO`) to animate your approved UGC still. The video starts from that exact image with natural human motion (eye contact breaks, head tilts, body shifts) and dialogue.

#### Quick UGC video (no starting frame)

> "Generate a UGC video ad for this product" + drop a product photo

Uses Sora 2 with your product photo as a style reference to generate a video directly — faster but less control over the person's appearance.

#### Other things to try

- "Recreate this influencer's look from a reference photo"
- "Make a Nano Banana product hero image"
- "Generate 5 different ad variations for this product"

## Reference images: hosting

**Important: kie.ai requires public HTTPS URLs for reference images** — unlike some competing APIs, it does not host your files for you. When you drop an image into `references/` and ask the agent to use it, the agent will prompt you to host it first.

**Fastest options:**
- **Imgur** — upload at [imgur.com](https://imgur.com/upload), copy the direct `i.imgur.com/*.jpg` link.
- **Supabase Storage / Cloudflare R2 / S3** — if you already have them, use a public bucket.
- **GitHub raw** — good for small, non-sensitive references you've committed to a public repo.

See the skill's reference for the full guide and gotchas (e.g. the Imgur direct-link rule, why Google Drive share pages don't work).

## What's in the box

| Path | What it does |
|------|-------------|
| `skills/kie-ai-external-api/` | The skill: API reference, prompting guide, per-model prompt library |
| `skills/generate-youtube-thumbnail/` | Extra skill for YouTube thumbnails |
| `MASTER_CONTEXT.template.md` | Template for your workspace context (cost rates, brand voice, learnings) |
| `MASTER_CONTEXT.md` | Your personalized copy (created by setup, not committed to git) |
| `.env` | Your API key (created by setup, never committed) |
| `scripts/setup.sh` | One-time setup |
| `scripts/sync-skill.sh` | Copies skill edits to `.claude/` and `.cursor/` directories |
| `scripts/check-kie-env.sh` | Tests API connectivity |
| `references/` | Drop reference images here (influencers, products, aesthetics) — gitignored |
| `logs/kie-api.jsonl` | Append-only log of every API call (config + status, not prompts or keys) |

## Your API key

Your key authenticates with the kie.ai API. During setup you paste it once and the agent uses it from `.env` automatically. You never need to paste it into chat.

Need a kie.ai account first? Create one at **[https://kie.ai](https://kie.ai)**.

Manage keys: **[kie.ai/api-key](https://kie.ai/api-key)**

## Project memory

`MASTER_CONTEXT.md` is your workspace's living memory. The agent reads it at the start of every session and writes learnings back. It stores:

- **Cost rates** — you fill in once (or the agent asks), then every session has them
- **Brand voice** — optional tone, audience, and word preferences
- **API learnings** — universal kie.ai quirks that help the agent work better
- **Changelog** — dated notes from each session

## Supported models

| Model | Type | Best for | kie.ai model slug |
|-------|------|----------|-------------------|
| **Seedance 2.0** | Video | UGC selfie-style video with speech, image-to-video up to 15s | `bytedance/seedance-2` |
| **Sora 2 / Sora 2 Pro** | Video | Longer videos (up to 20s), text-to-video, speech | `sora-2-text-to-video`, `sora-2-image-to-video`, `sora-2-pro-*` |
| **Veo 3 / 3.1** | Video | Animating a starting frame into ~8s video with dialogue | `veo3`, `veo3_fast` (on `/api/v1/veo/generate`) |
| **Kling 3.0** | Video | B-roll / scene clips, motion control (silent) | `kling-3.0/video`, `kling-3.0/motion-control` |
| **Nano Banana 2 / Pro** | Image | UGC stills, character sheets, product shots, influencer recreation | `nano-banana-2`, `nano-banana-pro` |

## Reference images folder

Drop images into the `references/` folder and the agent will offer to use them:

- **`references/influencers/`** — Photos of people to recreate as AI-generated content
- **`references/products/`** — Product photos for showcase videos and hero images
- **`references/aesthetics/`** — Style references organized by vibe (`ugc-selfie/`, `cinematic/`, etc.)

Images stay local (gitignored). **Before kie.ai can see them, you must host them at a public HTTPS URL** — the agent will walk you through this on first use.

## Editing the skill

The canonical skill source lives in `skills/kie-ai-external-api/`. After editing any file there, run:

```bash
./scripts/sync-skill.sh
```

This copies your changes to `.claude/skills/` and `.cursor/skills/` (which are gitignored — they're generated copies).

## Security

- `.env` is gitignored — never committed
- `MASTER_CONTEXT.md` is gitignored — contains your workspace data
- Never paste API keys in GitHub issues or public chats

## Vendor prompting guides

| Model | Guide |
|-------|--------|
| Sora 2 | [OpenAI — Sora 2 prompting guide](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide) |
| Veo 3.1 | [Google Cloud — Veo 3.1](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) |
| Kling 3.0 | [Kling — user guide](https://kling.ai/quickstart/klingai-video-3-model-user-guide) |
| Nano Banana | [Google Cloud — Nano Banana](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana) |

## API docs

[kie.ai official docs](https://docs.kie.ai/) • [Model marketplace](https://kie.ai/market) • [Pricing](https://kie.ai/pricing)

## Other AI assistants (Manus, Copilot, etc.)

Point your assistant at [AGENTS.md](AGENTS.md) and `MASTER_CONTEXT.md` + the skill path. See [AGENTS.md](AGENTS.md) for details.
