# Master context (Arcads + agents)

**Purpose:** One place for humans and AI agents to capture **decisions**, **brand voice**, **API quirks**, and **what we learned** while using this repo with Arcads.

## How agents should use this file

- **At the start of substantive work:** Read this file for project-specific context that is not in the skill.
- **After meaningful changes:** Append a new **dated entry** under [Changelog](#changelog) (Decision / What changed / Why).
- **If fields are empty:** Offer to populate them (credit costs from the user, default product from `GET /v1/products`).

## Project snapshot

- **Arcads API base:** `https://external-api.arcads.ai` (see `.env.example`).
- **Skill:** `.claude/skills/arcads-external-api/` and `.cursor/skills/arcads-external-api/` (sync from `skills/arcads-external-api/` via `scripts/sync-skill.sh`).

## My workspace

- **Default product ID:** _(auto-populated after first `GET /v1/products` call)_
- **Default product name:** _(auto-populated)_

## Credit costs

_Fill in your plan's credit costs below. The agent references this table before every generation. If left blank, the agent will ask you once and can fill them in._

| Model | Credits per generation |
|-------|----------------------|
| Veo 3.1 | |
| Sora 2 | |
| Sora 2 Pro | |
| Kling 3.0 (scene) | |
| Kling 3.0 (b-roll) | |
| Nano Banana 2 (image, `nano-banana-2`) | |
| Nano Banana Pro (image, `nano-banana`) | |
| Nano Banana (scene) | |

## Brand (optional)

_Edit or replace with your real brand blocks (see `skills/arcads-external-api/prompting/brand-voice-starter.md`)._

- **Tone:**
- **Audience:**
- **Words to use / avoid:**

## Reference images

Drop reference images into the `references/` folder at the repo root:
- `references/influencers/` — face/body photos to recreate as AI people
- `references/products/` — product photos for showcase workflows
- `references/aesthetics/` — mood boards, lighting references, style inspiration

The agent checks this folder when composing prompts and automatically uses images as `refImageAsBase64` or `referenceImages` depending on the workflow.

## API learnings (universal)

These are confirmed behaviors of the Arcads external API. They apply to all workspaces.

### Auth

- HTTP Basic with `ARCADS_BASIC_AUTH` (pre-encoded header from dashboard) or `ARCADS_API_KEY` as Basic username.
- Values in `.env` must be **single-quoted** due to special characters (`{`, `[`, `*`).

### Nano Banana image endpoint

- `POST /V2/images/generate` (note **uppercase V2**). `model` is **required**.
- Valid models: `nano-banana`, `nano-banana-2`, `gpt-image`, `soul`, `grok_image`, `seedream`, `seedream_5_lite`.
- Default to `nano-banana-2` (Nano Banana 2). `nano-banana` = Nano Banana Pro (no `nano-banana-pro` in the API enum).
- Output: `.png` at the `url` field on the asset response (no `thumbnailUrl`).
- Generation time: ~35 seconds typical.
- Auth: must use `Authorization: Basic ...` header.

### Scene for image-like output

- `POST /v1/scene` with only `productId`, `prompt`, `aspectRatio` produces a short video + `.jpg` thumbnail.
- Best path when you need a still frame to feed into another model (before the Nano Banana image endpoint was confirmed).
- No `duration` required (unlike b-roll which needs 5 or 10).

### B-roll

- Requires `duration` (5 or 10 seconds).
- Slower to generate than scene (~5 min vs ~75s).

### Veo 3.1

- `startFrame` vs `referenceImages` are **mutually exclusive**. `startFrame` = video animates from this exact image. `referenceImages` = style/mood inspiration only.
- Default: always use `startFrame` when user provides a single person photo.
- No `duration` field — auto-determines length (~8s typical).

### File upload (for Veo start frames / reference images)

- `POST /v1/file-upload/get-presigned-url` — field is `fileType`, **not** `contentType`.
- Response: `presignedUrl` (for `PUT` upload) + `filePath` (pass into `startFrame` / `referenceImages`).

### Kling / Nano Banana video routing

- No dedicated POST endpoints for Kling. Asset type enums (`kling_30`, `nano-banana`) exist on responses.
- Model selection may be server-side for b-roll/scene.

### Polling

- `GET /v1/assets/{id}` — status goes `pending` -> `generated` | `failed`.
- Typical times: scene ~75s, b-roll ~5 min, Veo 3.1 ~4 min, Nano Banana image ~35s.

### Product API

- `ProductCreationDto` has text-only fields (`name`, `description`, `targetAudience`, `mainFeatures`, `painPoint`, `perceived`) — no image upload.
- Product images are dashboard-only (`pictureId` field).
- The Arcads script/actor pipeline (situations, voices) is a separate system from the Veo/Sora/Kling direct-model routes.

### Folder / project organization

- Every agent session that generates assets should create (or reuse) a folder named **"Arcads API - YYYY-MM-DD"** with a matching project inside it, then assign all generated assets to that project.
- API calls: `POST /v1/folders`, `POST /v1/projects`, `POST /v1/assets/add-to-project`. Check `GET /v1/products/{productId}/folders` first to avoid duplicates.

### Influencer recreation

- Must follow two-step flow: (1) generate still image via `POST /V2/images/generate` with `refImageAsBase64`, (2) show user for approval, (3) only then generate video using approved still as start frame.
- Never skip the approval step — video is expensive, stills are cheap to iterate.

### Image QA

- Agents must visually review still images after generation (hands, fingers, limbs, face, merged objects, artifacts).
- If defective, regenerate with refined prompt — up to 2 retries (3 attempts total).
- QA retries skip a second credit confirmation but still bill credits.

## Changelog

### YYYY-MM-DD -- Template entry

- **Decision:**
- **Change:**
- **Why:**
