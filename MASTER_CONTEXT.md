# Master context (Arcads + agents)

**Purpose:** One place for humans and AI agents to capture **decisions**, **brand voice**, **API quirks**, and **what we learned** while using this repo with Arcads.

## How agents should use this file

- **At the start of substantive work:** Read this file for project-specific context that is not in the skill.
- **After meaningful changes:** Append a new **dated entry** under [Changelog](#changelog) (Decision / What changed / Why).

## Project snapshot

- **Arcads API base:** `https://external-api.arcads.ai` (see `.env.example`).
- **Skill:** `.claude/skills/arcads-external-api/` and `.cursor/skills/arcads-external-api/` (sync from `skills/arcads-external-api/` via `scripts/sync-skill.sh`).

## Brand (optional)

_Edit or replace with your real brand blocks (see `skills/arcads-external-api/prompting/brand-voice-starter.md`)._

- **Tone:**
- **Audience:**
- **Words to use / avoid:**

## Changelog

### 2026-03-25 — First end-to-end generation test (scene → Veo 3.1)

- **Auth confirmed:** HTTP Basic with `ARCADS_BASIC_AUTH` (pre-encoded header from dashboard) or `ARCADS_API_KEY` as Basic username. Values in `.env` must be **single-quoted** due to special characters (`{`, `[`, `*`).
- **Scene for image-like output:** `POST /v1/scene` with only `productId`, `prompt`, `aspectRatio` produces a short video + `.jpg` thumbnail. This is the best path when you need a still frame to feed into another model. No `duration` required (unlike b-roll which needs 5 or 10).
- **B-roll also works** but requires `duration` and was slower to generate.
- **Veo 3.1 start frame pipeline:** `POST /v1/file-upload/get-presigned-url` (field: `fileType`, not `contentType`) → `PUT` image to returned `presignedUrl` → pass `filePath` string as `startFrame` in `StartVeo31Dto`. Character consistency held — same face, outfit, lighting carried over from the scene thumbnail.
- **Kling / Nano Banana:** No dedicated POST endpoints. Asset type enums (`kling_30`, `nano-banana`) exist on responses. Model selection may be server-side for b-roll/scene. Need further testing to confirm how to force a specific model.
- **Polling:** `GET /v1/assets/{id}` — scene took ~75s, b-roll ~5min, Veo 3.1 ~4min. Status goes `pending` → `generated` | `failed`.
- **Products:** Workspace has "Arcads" (`10b24deb-...`) and "LOTR Vlog Series" (`9774cb42-...`).

### 2026-03-25 — Auto-create dated folders for session organization

- **Decision:** Every agent session that generates assets should create (or reuse) a folder named **"Arcads API - YYYY-MM-DD"** with a matching project inside it, then assign all generated assets to that project.
- **API calls:** `POST /v1/folders` (with `productId` + `name`), `POST /v1/projects` (with `productId` + `folderId` + `name`), `POST /v1/assets/add-to-project` (with `assetId` + `projectId`). Check `GET /v1/products/{productId}/folders` first to avoid duplicates.
- **Why:** Assets created via the API without a `projectId` end up as loose items under the product — hard to find in the dashboard. Dated folders make every session's output easy to locate.

### 2026-03-25 — Influencer recreation must follow two-step flow

- **Decision:** When recreating an influencer from a reference image, agents must ALWAYS: (1) generate a still image first, (2) show it to the user and get explicit approval, (3) only then generate video using the approved still as a start frame. Never skip the approval step.
- **Nano Banana routing:** The Arcads API does not have a dedicated Nano Banana POST endpoint. Asset types `nano-banana` and `nano-banana-2` exist in responses but model selection appears to be server-side. `POST /v1/scene` with `refImageAsBase64` is the current best path — it produces a short clip; use the `thumbnailUrl` as the still frame for approval.
- **Why:** Jumping straight to video wastes credits if the face/look doesn't match. The still image is cheap to iterate on; video is expensive.

### 2026-03-25 — Product showcase layer (placeholder, pending Nano Banana endpoint)

- **Decision:** Added a placeholder product-showcase workflow to the skill. The intended flow: user provides product images → Nano Banana generates a starting frame of an AI person holding/using the product → user approves the still → video generation via Veo 3.1 / Sora 2 / Kling 3.0.
- **Blocked on:** Arcads confirming the correct Nano Banana endpoint for still-image generation. The `POST /v1/scene` workaround (video + thumbnail) exists but a dedicated image route may be available.
- **Product API note:** `ProductCreationDto` has text-only fields (`name`, `description`, `targetAudience`, `mainFeatures`, `painPoint`, `perceived`) — no image upload. Product images are dashboard-only (`pictureId` field). The Arcads script/actor pipeline (situations, voices) is a separate system from the Veo/Sora/Kling direct-model routes this skill primarily uses.
- **Files added/updated:** `prompting/prompt-library/product-showcase.md` (new placeholder), `SKILL.md` (decision tree + supporting files), `reference.md` (product showcase workflow section + `ProductCreationDto` schema).

### 2026-03-25 — Generation count, script prompting, auto-duration, and split/stitch

- **Generation count:** Agent now asks user how many variations they want per prompt, then fires N parallel API calls with the same payload. Results presented as a numbered list for comparison.
- **Script prompting:** Agent asks for the dialogue/script the AI person should speak. For Veo 3.1 and Sora 2, dialogue is embedded in the `prompt` field. For Scene, the dedicated `script` field is used. B-roll has no speech.
- **Auto-duration from script length:** Word count mapped to duration at ~2.5 words/second. Sora 2: 4/8/12/16/20s (max ~48 words). Veo 3.1: no duration field, ~8s typical, warn if >20 words. B-roll: 5/10s, no speech. Scene: no duration field, has `script` field.
- **Split/stitch for long scripts:** If script exceeds max duration, agent offers to split at sentence boundaries into multiple videos. Each segment respects the generation count. Agent offers to stitch final segments with `ffmpeg -f concat`.

### 2026-03-25 — Credit cost confirmation and Veo 3.1 image mode clarity

- **Credit cost:** Agent must now calculate and display total credit cost before firing any generation calls. User must confirm before proceeding. Default cost table added to SKILL.md (Veo 3.1 = 4, Sora 2 = 2, Sora 2 Pro = 4, Kling/scene/b-roll = 2). Users can override costs in `MASTER_CONTEXT.md` if their plan differs. The Arcads API has no credit/billing endpoints — costs are estimated from published pricing.
- **Veo 3.1 `startFrame` vs `referenceImages`:** These are mutually exclusive. `startFrame` = video animates from this exact image (use for person reference photos). `referenceImages` = style/mood inspiration only. Default: always use `startFrame` when user provides a single person photo.
- **Why:** User noticed 4 Veo 3.1 generations (2 startFrame + 2 referenceImages) when only 2 were intended. Clear rules prevent accidental duplicates. Credit cost confirmation prevents surprise spend.

### 2026-04-01 — Nano Banana image endpoint confirmed and tested: POST /V2/images/generate

- **Decision:** The Nano Banana still-image generation endpoint is `POST /V2/images/generate` (note uppercase V2). This unblocks the product showcase workflow and replaces the `POST /v1/scene` thumbnail workaround for influencer recreation stills.
- **Endpoint confirmed by test:** `model` is **required** — valid values: `nano-banana`, `nano-banana-2`, `gpt-image`, `soul`, `grok_image`, `seedream`, `seedream_5_lite`. Credits: 0.03 per nano-banana generation. Generation time: ~35 seconds. Output: `.png` at the `url` field on the asset response (no `thumbnailUrl`). Auth: must use `Authorization: Basic ...` header.
- **Change:** Updated all skill files — `reference.md` (route mapping, `CreateImageDto` schema), `SKILL.md` (decision tree, execution checklist), `nano-banana.md` (endpoint, model field, curl example), `influencer-recreation.md` (Step 4 now uses `/V2/images/generate`), `product-showcase.md` (removed PLACEHOLDER status, full workflow documented).
- **Why:** Previously blocked — Arcads had no confirmed dedicated image route for Nano Banana. The scene endpoint workaround (video + thumbnail extraction) was slow, expensive, and indirect. The dedicated image endpoint enables the clean two-step flow: generate still → approve → generate video.
- **Model defaults (same day):** Default `model` to **`nano-banana-2`**; optional **Nano Banana Pro** = **`nano-banana`** (no `nano-banana-pro` in the API enum). Documented in `SKILL.md`, `reference.md`, `nano-banana.md`, influencer/product workflows.

### YYYY-MM-DD — Template entry

- **Decision:**
- **Change:**
- **Why:**
