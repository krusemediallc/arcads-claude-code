# Arcads AI Video — Agent Skill Pack

Create AI marketing videos and images using your [Arcads](https://arcads.ai/?via=claude-code) account, powered by AI agents in **Claude Code** or **Cursor**. Supports the full Arcads creative stack — **Seedance 2.0** (flagship video), **Sora 2**, **Veo 3.1**, **Kling 3.0**, **Grok Video**, **Nano Banana 2 / Pro / Edit**, **ChatGPT Image 2**, **OmniHuman**, and **Audio-driven** — plus a 37-template static Meta image-ad library and a pipeline for **Pixar-style** and **claymation** animated ads.

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

## Prerequisites

The agent and the basic Arcads workflows (image generation, video generation, polling) work with just **Python 3.10+** and the API key from setup. Some multi-step pipelines need a few extra CLI tools:

| Tool | Required for | Install (macOS) |
|---|---|---|
| **Python 3.10+** | Everything (the image-ad generators are stdlib-only — no pip install) | preinstalled or `brew install python@3.12` |
| **`ffmpeg`** | Pixar-style ad, claymation ad, caption-video (stitching + chroma-key overlay) | `brew install ffmpeg` |
| **`jq`** | Several bash scripts (pixar-style-ad, etc.) | `brew install jq` |
| **Node.js + `npx hyperframes`** | Caption burn-in workflow | `brew install node` (the skill runs `npx` on demand) |
| **`whisper`** Python package | Caption transcription | `pip install openai-whisper` (or `pip3`) |
| **`meta-ad-builder` deps** | Publishing to Meta Marketing API | `pip install -r shared/skills/meta-ad-builder/scripts/requirements.txt` |

The image-ad generator scripts (`chatgpt-image-ad`, `nano-banana-image-ad`, `image-ad-clone`) are intentionally stdlib-only — no extra installs needed. The deps above are only required when you invoke the matching multi-step workflow.

Linux users: `apt install ffmpeg jq nodejs python3`. Windows users: WSL2 recommended; the shell scripts assume bash.

## Get started (5 minutes)

### 1. Clone this repo

```bash
git clone https://github.com/krusemediallc/arcads-claude-code.git
cd arcads-claude-code
```

### 2. Run setup

```bash
./scripts/setup.sh
```

This will:
- Sign up if you need an Arcads account: [arcads.ai/?via=claude-code](https://arcads.ai/?via=claude-code)
- Ask for your **Arcads API key** (find it at [app.arcads.ai/settings/api](https://app.arcads.ai/settings/api))
- Save it securely in `.env` (never committed to git)
- Verify your connection to Arcads
- Create your personal `MASTER_CONTEXT.md` workspace file

### 3. Open in your AI editor

**Claude Code:** Open the folder. A `SessionStart` hook runs and prints an orientation banner showing which skills are installed, whether your `.env` and `MASTER_CONTEXT.md` are set up, and where the docs live.

**Cursor:** Open the folder. Same skills are exposed at `.cursor/skills/`.

### 4. Start creating

The agent handles API calls, polling, prompt engineering, file organization, and cost confirmation. Workflows are grouped by what you want to make.

---

### 🎬 Seedance 2.0 videos (the flagship — start here)

Seedance 2.0 is the most flexible model in the stack — 4–15s clips, native audio, image-to-video or video-to-video, reference images, multiple shot styles. Five prompt formulas ship with the skill:

#### UGC selfie-style product review

> "Make a 12-second Seedance UGC video — woman in a kitchen, holding the product, says she stopped buying [competitor]"

Uses the 9-layer UGC formula tuned for Seedance 2.0 (iPhone-shot aesthetic, natural eye-contact breaks, casual delivery). See `skills/arcads-external-api/prompting/prompt-library/seedance-2-ugc.md`.

#### Premium product reveal (no person)

> "Premium reveal of [product] — dark void, text narrative, hero rotation"

Dark-void aesthetic, text overlays narrating the product's positioning, no person on screen. See `skills/arcads-external-api/prompting/prompt-library/seedance-2-premium-reveal.md`.

#### Product hero with elemental effects

> "Seedance product hero — water splash, mist, slow rotation"

Splash, mist, light rays, slow rotation. See `skills/arcads-external-api/prompting/prompt-library/seedance-2-product-hero.md`.

#### Studio lookbook with voiceover

> "Studio lookbook of [product] — multi-look, polished, with voiceover script"

Polished editorial / lookbook style, multi-shot, with embedded dialogue. See `skills/arcads-external-api/prompting/prompt-library/seedance-2-studio-lookbook.md`.

#### Feature walkthrough demo

> "Seedance feature walkthrough — fast-paced, show off [features]"

Fast-paced product-demo cuts. See `skills/arcads-external-api/prompting/prompt-library/seedance-2-feature-walkthrough.md`.

---

### 🎬 Other video models

#### Sora 2 (text-to-video, up to 20s)

> "Generate a 16-second Sora video of [scene]" — optionally drop a product photo as a style reference.

Sora 2 handles longer durations than Veo. The agent auto-selects `duration` from your script's word count (~2.5 words/sec). Sora 2 remix is also supported via `POST /v1/sora2/remix/video` for remixing an existing asset.

#### Veo 3.1 (starting-frame animation)

> "Animate this Nano Banana still into an 8-second Veo with dialogue"

Veo 3.1 with `startFrame` is the standard path for **UGC stills → video**. The video starts from your exact image with natural human motion and embedded dialogue. The agent confirms the dialogue separately before generating (the MANDATORY dialogue gate).

#### Kling 3.0 (b-roll / scene)

> "Make a 5-second b-roll clip of [scene]" or "Generate a scene of [environment]"

Kling 3.0 is the b-roll / scene workhorse. Hits the dedicated `POST /v1/b-roll` and `POST /v1/scene` endpoints.

#### Grok Video

> "Generate a Grok video of [scene]"

Hits `POST /v2/videos/generate` with `model: "grok-video"`.

#### OmniHuman / Audio-driven

> "OmniHuman avatar of [person] delivering [script]" or "Audio-driven video lip-synced to [audio file]"

`POST /v1/omnihuman` for talking-avatar workflows; `POST /v1/audio-driven` for lip-sync against an audio file.

---

### 🖼️ Image generation (Nano Banana + ChatGPT Image 2)

#### Create a new AI influencer (10-image character sheet)

> "Create a new AI influencer — 22-year-old college student with freckles, golden-hour kitchen lighting"

Two-pass workflow: (1) generate a hero front portrait via Nano Banana, get your approval, (2) generate 9 additional angles (3/4 views, profile, close-up, expressions) with the hero as the reference. All 10 saved to `references/influencers/` for future reuse.

#### UGC product selfie still

> "Generate a UGC selfie of Sofia holding [product] in her bedroom"

Combines your character hero + product photo + style references from `references/aesthetics/ugc-selfie/` into an authentic-looking iPhone selfie frame grab. Includes skin realism and camera imperfections to fight AI's polished default.

#### Product showcase still (Nano Banana → Veo / Seedance video)

> "AI person holding [product] talking about [feature]"

Two-step: Nano Banana still of person + product → user approves → start-frame → video via Veo 3.1 or Seedance 2.0.

#### Recreate an influencer from a reference photo

> "Recreate this influencer's look from this reference photo"

Two-step: Nano Banana still from `refImageAsBase64` → user approves → Veo 3.1 with `startFrame`.

#### Nano Banana model choice

Default is `nano-banana-2`. Use `model: "nano-banana"` for **Nano Banana Pro** (Gemini 3 Pro Image — higher fidelity, locks character identity tighter across reference batches). `nano-banana-edit` for inpainting.

---

### 📸 Static Meta image ad creative (37-template library)

> "Make me an Apple Notes-style ad for my product" / "Generate a Forbes editorial ad" / "Clone this comparison-table ad as a template"

A four-skill family for static Meta image ads with a shared library of **37 validated prompt templates** (Apple Notes lists, editorial hero, fake Google search, comparison tables, sticky-note flatlays, fake Slack threads, ChatGPT-conversation ads, iMessage screenshots, magazine cover, billboard, museum exhibit, weather forecast UI, scratch-off ticket, founder letter, dating-app card, more).

- **`chatgpt-image-ad`** — typography-heavy / UI-mimicry creatives (gpt-image-2)
- **`nano-banana-image-ad`** — photoreal / lifestyle / multi-reference creatives (Nano Banana 2 / Pro / Edit)
- **`image-ad-clone`** — single backend-agnostic skill that reverse-engineers any existing ad image into a new library entry (asks which generator to validate against at Phase 1; optionally cross-validates against the other at Phase 8)

Output is image files. Pair with the `meta-ad-builder` skill to publish as paused Meta ads. **Read `shared/skills/image-ad-prompting/OVERVIEW.md` first** — it has the decision tree (which backend for which template), the aspect-ratio compatibility matrix per backend, and the standard generate / clone workflows. Live-validated end-to-end against the Arcads API.

---

### 🎞️ Multi-step animated ad pipelines

#### Pixar-style 3D animated ad

> "Make a Pixar-style ad for [product] — anthropomorphized mascot, 8-beat story arc"

Lock cast sheet → ChatGPT Image 2 storyboard stills (sequential, prior frame as ref for identity lock, max 5 `referenceImages`) → Seedance 2.0 image-to-video per beat → ffmpeg stitch + burn captions. See `shared/skills/pixar-style-ad/prompting/guide.md`.

#### Claymation / Aardman-style ad

> "Make a claymation ad — sculpted plasticine characters, narrator-driven, 60–115s"

Same backbone as Pixar with an 8-beat narrator-driven story arc and clay textures. ChatGPT Image 2 storyboard → Seedance 2.0 i2v → ffmpeg stitch with optional `fps=12,fps=24` stop-motion judder. VO generated externally (ElevenLabs) and mixed in post. See `shared/skills/claymation-ad/prompting/guide.md`.

#### YouTube thumbnails (5 CTR formulas)

> "Make 6 YouTube thumbnail variations with my face and product"

Specialized `generate-youtube-thumbnail` skill: peace-sign/branding, real-vs-AI comparison, terminal flow, reaction shock, before/after split. Likeness lockdown via 5+ face references. Parallel batch firing against Nano Banana 2. See `skills/generate-youtube-thumbnail/`.

#### Burn captions onto a finished video

> "Add captions to this MP4"

Out-of-band post-step (no Arcads call) that works on any source — Pixar, claymation, UGC, B-roll. HyperFrames + Whisper `medium.en` for transcription → group word-level transcript into reading phrases → render captions-only HTML over `#ff00ff` magenta → ffmpeg chroma-key overlay. See `shared/skills/caption-video/prompting/guide.md`.

---

### 🔄 Reverse-engineer existing creative

#### Analyze a reference video into a Seedance template

> "Reverse-engineer this video into a reusable Seedance template"

The `analyze-video` workflow under `skills/arcads-external-api/prompting/analyze-video/` extracts the structure of a reference video into a parameterizable Seedance 2.0 prompt template.

#### Clone an existing video ad for a different product

> "Clone this video ad for our new product"

`skills/arcads-external-api/prompting/clone-ad/` — end-to-end: analyze the reference → adapt to the new product → generate. The companion to `analyze-video` when you want to ship the cloned version directly.

#### Clone a static image ad into the prompt library

> "Reverse-engineer this image ad as a reusable template"

The `image-ad-clone` skill produces parameterizable entries for the 37-template library (see above).

---

### 📤 Publish creatives as paused Meta ads

> "Publish this approved creative as a paused Meta ad in my account"

The cross-API `meta-ad-builder` skill (in `shared/skills/`) takes a finished creative path and uploads it via the Meta Marketing API. Every ad is created PAUSED — you review and launch manually in Ads Manager. Also has a research path to pull top-spending ads and competitor ads. Auth via `META_*` keys in `.env`.

## What's in the box

| Path | What it does |
|------|-------------|
| `skills/arcads-external-api/` | **The core skill.** API reference, prompting guide, per-model prompt libraries (Seedance / Sora / Veo / Kling / Nano Banana), analyze-video + clone-ad sub-workflows. |
| `skills/generate-youtube-thumbnail/` | 5 CTR-tested YouTube thumbnail formulas with parallel batch firing against Nano Banana 2. |
| `skills/chatgpt-image-ad/` | Static Meta image-ad creatives via gpt-image-2 (typography / UI mimicry). Live-validated. |
| `skills/nano-banana-image-ad/` | Static Meta image-ad creatives via Nano Banana 2 / Pro / Edit (photoreal / lifestyle). Live-validated. |
| `skills/image-ad-clone/` | Reverse-engineer an existing ad image into a reusable library entry. Backend-agnostic — asks at Phase 1 whether to validate via gpt-image-2 or Nano Banana, optionally cross-validates against the other at Phase 8. |
| `shared/skills/image-ad-prompting/` | Shared brain for the image-ad ecosystem: 37 validated templates, safety suffixes, entry format, `OVERVIEW.md`. |
| `shared/skills/pixar-style-ad/` | Cross-API recipe: 8-beat anthropomorphized mascot ad via GPT Image 2 storyboard + Seedance 2.0 i2v. |
| `shared/skills/claymation-ad/` | Cross-API recipe: Aardman-style 8-beat clay narrative ad; same backbone as Pixar with stop-motion judder option. |
| `shared/skills/caption-video/` | Out-of-band post step: HyperFrames + Whisper + ffmpeg chroma-key to burn captions onto any finished MP4. |
| `shared/skills/meta-ad-builder/` | Publish finished creatives as paused Meta ads via the Meta Marketing API. |
| `shared/scripts/check-context.sh` | SessionStart banner — lists installed skills, checks `.env` / `MASTER_CONTEXT.md` status, surfaces ecosystem pointers. Hooked into `.claude/settings.json`. |
| `MASTER_CONTEXT.template.md` | Template for your workspace context (credit costs, brand voice, learnings). |
| `MASTER_CONTEXT.md` | Your personalized copy (created by setup, not committed to git). |
| `.env` | Your API key (created by setup, never committed). |
| `scripts/setup.sh` | One-time setup. |
| `scripts/sync-skill.sh` | Copies skill edits to `.claude/` and `.cursor/` directories. |
| `scripts/check-arcads-env.sh` | Tests API connectivity. |
| `references/` | Drop reference images here (influencers, products, aesthetics) — gitignored. |
| `logs/arcads-api.jsonl` | Per-call audit log: model, duration, resolution, reference counts, `creditsCharged`. Powers cost-estimation accuracy across sessions. |

## Your API key

Your key authenticates with the Arcads API. During setup you paste it once and the agent uses it from `.env` automatically. You never need to paste it into chat.

Need an Arcads account first? Create one here: **[https://arcads.ai/?via=claude-code](https://arcads.ai/?via=claude-code)**

Find your key: **[Arcads Dashboard > Settings > API](https://app.arcads.ai/settings/api)**

For Meta-ad publishing (the `meta-ad-builder` skill), you'll also need `META_ACCESS_TOKEN` and `META_AD_ACCOUNT_ID` in `.env` — the `.env.example` has placeholder rows.

## Project memory

`MASTER_CONTEXT.md` is your workspace's living memory. The agent reads it at the start of every session and writes learnings back. It stores:

- **Default product** — auto-populated on first use so you're never asked "which product?" again
- **Default project / folder** — session output organized in the Arcads dashboard automatically
- **Credit costs** — you fill in once (or the agent asks), then every session has them
- **Image hosting** — where you stage reference images if a workflow needs hosted URLs
- **Brand voice** — optional tone, audience, and word preferences
- **API learnings** — universal Arcads quirks that help the agent work better
- **Changelog** — dated notes from each session

## Supported models

| Model | Type | Best for | Notes |
|-------|------|----------|-------|
| **Seedance 2.0** | Video (4–15s) | Flagship video model. UGC, premium reveal, product hero, lookbook, feature walkthrough. Native audio. | `model: "seedance-2.0"`. 5 prompt formulas ship. Mutually exclusive: `referenceVideos` vs `referenceImages`. |
| **Sora 2** | Video (up to 20s) | Long-duration text-to-video, image-to-video with product photo as style ref. | `model: "sora2"`. Duration enum: `[4, 8, 12, 16, 20]`. Remix: `POST /v1/sora2/remix/video`. |
| **Veo 3.1** | Video (~8s) | Animating a starting frame (UGC stills → video). Best for character / influencer flows. | `model: "veo31"`. `startFrame` and `referenceImages` are mutually exclusive — default `startFrame` for single person photos. |
| **Kling 3.0** | Video (5s or 10s) | B-roll and scene generation. | Hits `POST /v1/b-roll` / `POST /v1/scene` directly. |
| **Grok Video** | Video | Text-to-video via xAI's video model. | `model: "grok-video"`. |
| **Nano Banana 2** | Image | Default still-image model. UGC stills, character sheets, product shots, influencer recreation, image-ad creatives. | `model: "nano-banana-2"`. |
| **Nano Banana Pro** | Image | Premium image quality (Gemini 3 Pro Image). Locks character identity tighter across batches. | `model: "nano-banana"` (the bare string maps to Pro on Arcads). |
| **Nano Banana Edit** | Image | Inpaint / edit an existing image. | `model: "nano-banana-edit"`. |
| **ChatGPT Image 2** | Image | Typography-heavy / UI-mimicry static ad creatives. Used by `chatgpt-image-ad` skill + the Pixar / Claymation storyboard pipelines. | `model: "gpt-image-2"`. Max 5 `referenceImages`. Aspect ratios: `1:1`, `16:9`, `9:16`. |
| **OmniHuman** | Video | Talking-avatar / lip-sync workflows. | `POST /v1/omnihuman`. |
| **Audio-driven** | Video | Lip-sync a video to a supplied audio file. | `POST /v1/audio-driven`. |

Cost is presented as an **estimate** before every generation; the agent reads `logs/arcads-api.jsonl` for historical `creditsCharged` values matching your config. Always confirm exact pricing in the Arcads dashboard if it matters for budgeting.

## Reference images

Drop images into the `references/` folder and the agent will use them automatically:

- **`references/influencers/`** — Photos of people to recreate as AI-generated content (and saved character sheets)
- **`references/products/`** — Product photos for showcase videos and hero images
- **`references/aesthetics/`** — Style references organized by vibe (`ugc-selfie/`, `cinematic/`, etc.)

Images stay local — the folder contents are gitignored. The agent auto-upscales any reference below 1024px (the API's min-size floor) using Lanczos before submitting.

## Editing skills

Each skill's canonical source lives in `skills/<name>/`. After editing any file there, run:

```bash
./scripts/sync-skill.sh
```

This copies your changes to `.claude/skills/` and `.cursor/skills/` (which are gitignored — they're generated copies). The `SessionStart` hook in `.claude/settings.json` also runs this automatically when Claude Code opens.

## Staying current

This repo updates regularly — new templates land in the prompt library, new workflows get added, bugs get fixed. To stay in sync with upstream:

- **At every Claude Code session start**, the `check-context.sh` hook automatically runs `git fetch origin` (with a 10s timeout, never blocks). If your local clone is behind, the SessionStart banner will list the pending commits and tell you to run `git pull`. No surprise pulls — it just notifies.
- **To pull updates manually:** `git pull origin main` from the repo root. If you've made local changes to tracked files, stash them first: `git stash && git pull && git stash pop`.
- **If you've forked the repo on GitHub:** click the "Sync fork" button on your fork's page to bring it in line with this upstream, then `git pull` locally.
- **Customizations:** your `.env`, `MASTER_CONTEXT.md`, `references/`, `outputs/`, and `logs/` are all gitignored — they survive every update. If you customize a core skill file (e.g. tune a SKILL.md for your brand), expect potential merge conflicts on `git pull` — keep custom versions under a non-tracked path (e.g. `local-skills/`) if you don't want them affected by upstream updates.

## Security

- `.env` is gitignored — never committed
- `MASTER_CONTEXT.md` is gitignored — contains your product IDs and workspace data
- Never paste API keys in GitHub issues or public chats
- Every Meta ad created via `meta-ad-builder` is created **PAUSED** — nothing goes live without you launching it manually in Ads Manager

## Vendor prompting guides

| Model | Guide |
|-------|--------|
| Seedance 2.0 | Aligned to ByteDance's published Seedance prompting platform (the skill summarizes this in `skills/arcads-external-api/prompting/prompt-library/seedance-2.md`) |
| Sora 2 | [OpenAI — Sora 2 prompting guide](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide) |
| Veo 3.1 | [Google Cloud — Veo 3.1](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) |
| Kling 3.0 | [Kling — user guide](https://kling.ai/quickstart/klingai-video-3-model-user-guide) |
| Nano Banana | [Google Cloud — Nano Banana](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana) |
| ChatGPT Image 2 | OpenAI image-generation guidance (summarized in `shared/skills/chatgpt-image-ad/prompting/guide.md` with model-specific strengths and limits) |

## API docs

[Arcads Swagger UI](https://external-api.arcads.ai/docs)

## Other AI assistants (Manus, Copilot, etc.)

Point your assistant at [AGENTS.md](AGENTS.md) and `MASTER_CONTEXT.md` + the skill paths in `skills/` and `shared/skills/`. See [AGENTS.md](AGENTS.md) for details.
