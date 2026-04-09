# Arcads external API — reference

Official Swagger UI: [https://external-api.arcads.ai/docs](https://external-api.arcads.ai/docs)  
OpenAPI JSON (machine-readable): `GET https://external-api.arcads.ai/docs-json`

## Base URL

`https://external-api.arcads.ai`

Override with env `ARCADS_BASE_URL` if Arcads provides a different host for your workspace.

## Authentication

The API uses **HTTP Basic** (`securitySchemes.basic` in OpenAPI).

- **Typical pattern:** use your **Arcads API key as the Basic auth username** and an **empty password** (this matches the common "Authorize" UX in Swagger: paste the key in the username field, leave password blank).
- **Env:** `ARCADS_API_KEY` — never commit it; load from `.env` locally.
- **401 / 403:** key missing, wrong, or lacks permission — run the setup flow in `SKILL.md` (editor-first `.env`).

### curl example

```bash
curl -sS -u "$ARCADS_API_KEY:" "https://external-api.arcads.ai/v1/products"
```

(`-u 'key:'` means password empty.)

## Model → route mapping

### Primary: unified v2 video endpoint

All video models are available through a single endpoint. Use this as the **primary route** for all video generation.

| Model | `model` value | Endpoint | Request body |
|-------|---------------|----------|-------------|
| **Sora 2** | `sora2` | `POST /v2/videos/generate` | `CreateVideoDto` |
| **Sora 2 Pro** | `sora2-pro` | `POST /v2/videos/generate` | `CreateVideoDto` |
| **Veo 3.1** | `veo31` | `POST /v2/videos/generate` | `CreateVideoDto` |
| **Kling 2.6** | `kling-2.6` | `POST /v2/videos/generate` | `CreateVideoDto` |
| **Kling 3.0** | `kling-3.0` | `POST /v2/videos/generate` | `CreateVideoDto` |
| **Grok Video** | `grok-video` | `POST /v2/videos/generate` | `CreateVideoDto` |
| **Seedance 2.0** | `seedance-2.0` | `POST /v2/videos/generate` | `CreateVideoDto` |

### Other endpoints (not on the v2 unified route)

| Model / flow | Endpoint | Request body |
|-------------|----------|-------------|
| **Nano Banana (image)** | `POST /v2/images/generate` | `CreateImageDto` — default `model`: `nano-banana-2`; optional `nano-banana` (Nano Banana Pro) |
| **B-roll** | `POST /v1/b-roll` | `CreateBRollDto` |
| **Scene** | `POST /v1/scene` | `CreateSceneDto` |
| **Sora 2 remix** | `POST /v1/sora2/remix/video` | `RemixSora2Dto` |
| **Nano Banana (video via b-roll/scene)** | `POST /v1/b-roll` or `POST /v1/scene` | `CreateBRollDto` / `CreateSceneDto` — asset `type` may read `nano-banana` / `nano-banana-2` |

### Legacy v1 model-specific endpoints

These still work and are kept for backward compatibility. Prefer the v2 unified endpoint for new work.

| Model | Legacy route | Legacy DTO |
|-------|-------------|------------|
| Sora 2 | `POST /v1/sora2/generate/video` | `StartSora2Dto` |
| Veo 3.1 | `POST /v1/veo31/generate/video` | `StartVeo31Dto` |

**Note:** Kling models did not have dedicated v1 endpoints. B-roll and scene endpoints remain unchanged (no v2 equivalent).

**Important — image endpoint casing:** The Nano Banana image route uses **`/v2/`** (the OpenAPI spec shows lowercase). Previous testing confirmed uppercase `/V2/` also works. Use lowercase `/v2/` going forward.

## Images vs video

- **Video:** primary surface — Sora2, Veo31, b-roll, scene, script generation, watch links.
- **Image generation (Nano Banana):** `POST /V2/images/generate` — dedicated endpoint for still-image generation. Use for influencer recreation stills, product showcase starting frames, and any workflow needing a Nano Banana image before video. See `CreateImageDto` below.
- **Other image-like outputs:** OpenAPI `AssetResponseDto.type` includes image-oriented values (e.g. `gpt-image`, `grok_image`, `skin_enhanced_image`, `nano-banana`, etc.).
- **Thumbnails:** `thumbnailUrl` on asset responses when available.

## Polling and delivery

### Videos (`VideoDto`)

- `GET /v1/videos/{videoId}` — includes `videoUrl`, `videoStatus`.
- `GET /v1/videos/{videoId}/watch` — watch link when applicable.

### Assets (b-roll, scene, many generated types — including Nano Banana images)

- `GET /v1/assets/{id}` — `status` enum: `created` | `pending` | `generated` | `failed` | `uploaded`.
- Poll every few seconds until `generated` or `failed` (back off if the API rate-limits).
- `GET /v1/assets/{id}/watch` — watch link when applicable.
- For Nano Banana images, poll the same way — the response will include image URLs instead of video URLs.

### Script / actor pipeline

- `POST /v1/scripts` — create script (folder or project).
- `POST /v1/scripts/{scriptId}/generate` — trigger generation.
- `GET /v1/scripts/{scriptId}/videos` — list videos for script.

## Key request bodies (summary)

### `CreateVideoDto` (OpenAPI) — `POST /v2/videos/generate`

**Endpoint:** `POST /v2/videos/generate` — unified video generation for all models.

**Fields:**

- `model` (required) — enum: `sora2`, `sora2-pro`, `veo31`, `kling-2.6`, `kling-3.0`, `grok-video`, `seedance-2.0`
- `productId` (required) — UUID of the Arcads product
- `prompt` (required) — the video prompt
- `aspectRatio` (optional) — varies by model (see compatibility table below)
- `duration` (optional) — varies by model (see compatibility table below)
- `resolution` (optional) — varies by model (see compatibility table below)
- `referenceImages` (optional) — array of `filePath` strings from presigned upload (max varies by model)
- `referenceVideos` (optional) — array of `filePath` strings; **Seedance 2.0 only** (max 3)
- `referenceAudios` (optional) — array of `filePath` strings; **Seedance 2.0 only** (max 3)
- `audioEnabled` (optional) — boolean; **Seedance 2.0 only**
- `startFrame` (optional) — presigned `filePath`; supported by veo31, kling-2.6, kling-3.0, grok-video (NOT Seedance 2.0)
- `endFrame` (optional) — presigned `filePath`; supported by veo31, kling-2.6, kling-3.0
- `projectId` (optional) — assign to session project
- `nbGenerations` (optional) — sora2 / sora2-pro only (1–10)

**Seedance 2.0 — mutually exclusive reference input modes (confirmed 2026-04-09):**

On Seedance 2.0, `referenceVideos` and `referenceImages` **cannot be combined** in the same request. Sending both fields returns `HTTP 500 UNKNOWN_ERROR` from the server. Choose one mode per call:

- **Image-to-video:** `referenceImages` (1–3), no `referenceVideos`.
- **Video-to-video:** `referenceVideos` (1–3), no `referenceImages`.
- `referenceAudios` can be combined with either mode (confirmed 2026-04-09 with i2v + audio-ref).

This is not documented in the OpenAPI spec — add a sanity check before firing any Seedance 2.0 call and refuse to mix the two.

**Seedance 2.0 — confirmed pricing (2026-04-09):**

- **Image-to-video:** ~0.06 credits/sec. 4s ≈ 0.24, 15s ≈ 0.9. Audio reference does NOT change price.
- **Video-to-video:** ~0.1 credits/sec. 15s ≈ 1.5 (exact). Base rate cited by user was 1.0 (likely for a shorter duration).

Use these as the default estimate; `logs/arcads-api.jsonl` has the raw per-call data.

**⚠️ Seedance 2.0 content-check billing behavior (confirmed 2026-04-09):**

Credits are charged at **create time**, BEFORE the content checker runs. If the prompt is flagged after creation, the asset status transitions to `failed` with `data.error.message` = `"body.prompt: The content could not be processed because it contained material flagged by a content checker"` and the full `creditsCharged` is NOT refunded by the API.

**Implication:** Before firing a Seedance 2.0 call with a new or modified prompt, sanity-check for anything that could trip a filter — especially on `v2v` calls where content checking appears stricter. If a 500 or failed status comes back on the first attempt, do **not** automatically retry the same payload — tighten the prompt language first.

**Per-model field compatibility:**

| Field | sora2 / sora2-pro | veo31 | kling-2.6 | kling-3.0 | grok-video | seedance-2.0 |
|-------|:-:|:-:|:-:|:-:|:-:|:-:|
| `aspectRatio` | 1:1, 16:9, 9:16 | 1:1, 16:9, 9:16 | — | — | auto, 1:1, 16:9, 9:16 | **9:16, 16:9 only** |
| `duration` | 4,8,12,16,20 | — (auto ~8s) | 5,10 | 3–15 | 1–15 | **4–15** |
| `resolution` | 720p, 1080p | 720p, 1080p, 4K | — | — | 480p, 720p | **480p, 720p** |
| `referenceImages` | max 1 | max 3 | — | — | — | **max 3** |
| `referenceVideos` | — | — | — | — | — | **max 3** |
| `referenceAudios` | — | — | — | — | — | **max 3** |
| `audioEnabled` | — | — | — | — | — | **yes** |
| `startFrame` | — | yes | yes | yes | yes | — |
| `endFrame` | — | yes | yes | yes | — | — |
| `nbGenerations` | 1–10 | — | — | — | — | — |

**Response (201):** Returns an asset object. Poll via `GET /v1/assets/{id}`.

**curl example (Seedance 2.0):**

```bash
source .env && curl -sS -X POST \
  -u "$ARCADS_API_KEY:" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "seedance-2.0",
    "productId": "...",
    "prompt": "15 seconds UGC style skincare review...",
    "aspectRatio": "9:16",
    "duration": 15,
    "resolution": "720p",
    "audioEnabled": true,
    "referenceImages": ["/path/from/presigned-upload.jpg"]
  }' \
  "https://external-api.arcads.ai/v2/videos/generate"
```

**curl example (Sora 2 via v2):**

```bash
source .env && curl -sS -X POST \
  -u "$ARCADS_API_KEY:" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sora2",
    "productId": "...",
    "prompt": "...",
    "aspectRatio": "9:16",
    "duration": 8,
    "resolution": "720p"
  }' \
  "https://external-api.arcads.ai/v2/videos/generate"
```

### `CreateImageDto` (OpenAPI) — `POST /v2/images/generate`

**Endpoint:** `POST /V2/images/generate` (note uppercase V2). Same body as documented in Swagger under **`CreateImageDto`**.

**Nano Banana `model` values (this repo):**

- **Default:** `nano-banana-2` (Nano Banana 2)
- **Optional:** `nano-banana` (user-facing: **Nano Banana Pro** — the other Nano Banana engine in the API enum)

There is no separate `nano-banana-pro` string; "Nano Banana Pro" maps to `nano-banana` here.

**Fields (OpenAPI + tested 2026-04-01):**

- `productId` (required) — UUID of the Arcads product
- `prompt` (required) — the image prompt (follow `prompting/prompt-library/nano-banana.md`)
- `model` (required) — enum includes `nano-banana`, `nano-banana-2`, `gpt-image`, `soul`, `grok_image`, `seedream`, `seedream_5_lite`
- `aspectRatio` (required) — `1:1`, `16:9`, `9:16`
- `referenceImages` (optional) — array of `filePath` strings from `POST /v1/file-upload/get-presigned-url` (max 14 for `nano-banana` and `nano-banana-2` per OpenAPI)
- `projectId` (optional) — assign to a project on creation
- `nbGenerations` (optional) — SOUL model only (1–10)

**Response (201):** Returns an asset object with `id`, `status: "pending"`, `type` (matches the model, e.g. `nano-banana-2`), and `data` (includes `creditsCharged`). The `url` field contains a presigned S3 `.png` URL once generated.

**Polling:** `GET /v1/assets/{id}` — status goes `pending` → `generated`. Typical time: ~35 seconds. The image URL is in the `url` field (not `thumbnailUrl`).

**Credits:** Use `data.creditsCharged` on the response; configure per-model estimates in `MASTER_CONTEXT.md` (example: `nano-banana` once charged 0.03 in a test).

**Auth note:** Use the `Authorization: Basic ...` header (the `ARCADS_BASIC_AUTH` env var), not `-u` style, to avoid 403 on subsequent asset polling.

**curl example (default Nano Banana 2):**

```bash
source .env && curl -sS -X POST \
  -H "Authorization: $ARCADS_BASIC_AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "...",
    "prompt": "...",
    "model": "nano-banana-2",
    "aspectRatio": "1:1"
  }' \
  "https://external-api.arcads.ai/V2/images/generate"
```

### `StartSora2Dto` (legacy — `POST /v1/sora2/generate/video`)

Prefer `CreateVideoDto` with `model: "sora2"` via `POST /v2/videos/generate`.

- `productId`, `prompt`, `aspectRatio`, `duration`
- Optional: `projectId`, `refImageAsBase64`, `resolution`, `model` (`sora2` | `sora2_pro`)
- **`duration`** enum: **4, 8, 12, 16, 20** seconds.
- **`resolution`** enum: `720p`, `1080p`
- **`aspectRatio`** enum: `1:1`, `16:9`, `9:16`

### `StartVeo31Dto` (legacy — `POST /v1/veo31/generate/video`)

Prefer `CreateVideoDto` with `model: "veo31"` via `POST /v2/videos/generate`.

- `productId`, `prompt`, `resolution`, `aspectRatio`
- Optional: `projectId`, `referenceImages`, `startFrame`, `endFrame` (see API docs for mutual exclusions)
- **No `duration` field** — Veo 3.1 auto-determines length (~8s typical).
- **`resolution`** enum: `720p`, `1080p`, `4K`
- **`aspectRatio`** enum: `1:1`, `16:9`, `9:16`

### `CreateBRollDto` (required fields)

- `productId`, `prompt`, `aspectRatio`, `duration` (5 or 10 seconds)
- Optional: `projectId`, `refImageAsBase64`, `startFrameAsBase64`, `endFrameAsBase64`
- **`duration`** enum: **5, 10** seconds. B-roll is typically wordless.
- **`aspectRatio`** enum: `1:1`, `16:9`, `9:16`

### `CreateSceneDto` (required fields)

- `productId`, `prompt`, `aspectRatio`
- Optional: `projectId`, `script`, `contextScript`, `contextPrompt`, `refImageAsBase64`, `startFrameAsBase64`
- **No `duration` field** — auto-determined.
- **`script`** field: Use for dialogue (separate from visual `prompt`).
- **`aspectRatio`** enum: `1:1`, `16:9`, `9:16`

### Duration summary (quick reference)

| Model | Duration field | Options (seconds) | Has speech? |
|-------|---------------|-------------------|-------------|
| Sora 2 | `duration` (required) | 4, 8, 12, 16, 20 | Yes (in prompt) |
| Veo 3.1 | None (auto) | ~8s typical | Yes (in prompt) |
| Kling 2.6 | `duration` | 5, 10 | No |
| Kling 3.0 | `duration` | 3–15 | No |
| Grok Video | `duration` | 1–15 | No |
| **Seedance 2.0** | `duration` | **4–15** (continuous) | **Yes (in prompt)** |
| B-roll | `duration` (required) | 5, 10 | No |
| Scene | None (auto) | Varies | Yes (`script` field) |
| Nano Banana (image) | N/A (still image) | N/A | No |

### File upload (for reference images, videos, audio)

`POST /v1/file-upload/get-presigned-url` — supports images, videos, and audio files.

- **Request body:** `{"fileType": "image/jpeg"}` (field is `fileType`, **not** `contentType`).
- **Supported `fileType` values:** `image/jpeg`, `image/jpg`, `image/png`, `image/gif`, `image/webp`, `image/heic`, `image/heif`, `video/mp4`, `video/quicktime`, `video/avi`, `video/mov`, `video/wmv`, `video/webm`, `audio/mp3`, `audio/mp4`, `audio/wav`, `audio/m4a`, `audio/x-m4a`, `audio/aac`, `audio/ogg`, `audio/flac`, `audio/webm`, `audio/mpeg`, `audio/opus`
- **Response:** `presignedUrl` (for `PUT` upload to S3), `filePath` (pass into `startFrame` / `referenceImages` / `referenceVideos` / `referenceAudios`), `fileId`, `expiresIn` (seconds), `maxFileSize` (bytes), `maxDuration` (seconds, for video uploads).
- **Upload:** `curl -X PUT -H "Content-Type: image/jpeg" --data-binary @file.jpg "$presignedUrl"`.
- Then use `filePath` value in `CreateVideoDto` fields.

**Seedance 2.0 file uploads:** Use the same presigned URL flow for `referenceVideos` (pass `fileType: "video/mp4"`) and `referenceAudios` (pass `fileType: "audio/mp3"` or similar).

### Image minimum size — auto-upscale

Several endpoints (e.g. `POST /v1/b-roll`, `POST /V2/images/generate`) reject images below a minimum resolution with **422 — "The provided image is too small."** To avoid this:

1. Before sending any image, check its dimensions.
2. If the **longest side < 1024 px**, upscale with Lanczos resampling so the longest side = **1080 px** (preserve aspect ratio).
3. Convert to **RGB JPEG** (quality 90–95) — this also strips RGBA alpha channels that some endpoints don't handle.
4. Re-encode as base64 or upload the resized file.

This should happen transparently — never ask the user about it.

## Product showcase workflow

The flow for generating videos of an AI person holding/using a physical product:

1. User provides **product image(s)** (photos of the item from different angles).
2. Agent composes a **Nano Banana prompt** describing the AI person interacting with the product — holding it, unboxing it, applying it, etc.
3. `POST /V2/images/generate` with `prompt` and `refImageAsBase64` (product image) to generate a **still image** (starting frame) of the person with the product.
4. User **approves** the still.
5. Approved still is uploaded as a **`startFrame`** (Veo 3.1) or **`refImageAsBase64`** (Sora 2 / Kling 3.0) for video generation.

See [prompting/prompt-library/product-showcase.md](prompting/prompt-library/product-showcase.md) for prompt templates and workflow details.

### Product context via `ProductCreationDto`

Products in Arcads carry marketing context (not images via the API):

```
POST /v1/products
{
  "name": "Product Name",
  "description": "What the product is",
  "targetAudience": "Who it's for",
  "mainFeatures": ["feature 1", "feature 2", "feature 3"],
  "painPoint": "Problem it solves",
  "perceived": "How customers see it"
}
```

These text fields feed into script/prompt context. Product images are currently managed through the Arcads dashboard (`pictureId` on the product object).

## Folders and projects

### Create folder

`POST /v1/folders` — `{"productId": "...", "name": "Arcads API - YYYY-MM-DD"}`. Returns `id`, `productId`, `name`.

### List folders

`GET /v1/products/{productId}/folders` — paginated list with `items[]`. Check for existing dated folder before creating a new one.

### Create project (inside a folder)

`POST /v1/projects` — `{"productId": "...", "folderId": "...", "name": "Arcads API - YYYY-MM-DD"}`. Returns `id`, `folderId`, `name`.

### Assign asset to project

`POST /v1/assets/add-to-project` — `{"assetId": "...", "projectId": "..."}`. Use after generation if the asset's `projects` array is empty.

### Remove asset from project

`POST /v1/assets/remove-from-project` — `{"assetId": "...", "projectId": "..."}`.

## Health

- `GET /health` — no auth required for basic uptime checks.

## Errors

| Code | Typical meaning |
|------|-----------------|
| 401 / 403 | Auth / permission |
| 404 | Wrong ID or resource missing |
| 422 | Validation or moderation block |
| 500 | Server error — retry later |
