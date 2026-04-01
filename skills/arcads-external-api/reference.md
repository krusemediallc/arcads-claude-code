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

## Model → route mapping (primary models)

| Model (product) | REST route | Request body schema (OpenAPI) |
|-------------------|------------|-------------------------------|
| **Sora 2** | `POST /v1/sora2/generate/video` | `StartSora2Dto` |
| **Sora 2 remix** | `POST /v1/sora2/remix/video` | `RemixSora2Dto` |
| **Veo 3.1** | `POST /v1/veo31/generate/video` | `StartVeo31Dto` |
| **Kling 3.0** | No separate `kling` path in the published OpenAPI. Asset results can have `type: "kling_30"` (see `AssetResponseDto`). Use **`POST /v1/b-roll`** or **`POST /v1/scene`** when your Arcads workflow uses those flows for Kling-style clips; craft prompts using the Kling vendor guide in `prompting/prompt-library/kling-3.md`. |
| **Nano Banana (image)** | `POST /V2/images/generate` | `CreateImageDto` — default `model`: `nano-banana-2`; optional `nano-banana` (Nano Banana Pro) (see below) |
| **Nano Banana (video via b-roll/scene)** | `POST /v1/b-roll` or `POST /v1/scene` | `CreateBRollDto` / `CreateSceneDto` — asset `type` may read `nano-banana` / `nano-banana-2`; prompts follow `prompting/prompt-library/nano-banana.md` |

**Note:** `CreateBRollDto` / `CreateSceneDto` do not expose a `model` enum in the published schema — model routing may be workspace- or server-side. If generation does not match the intended engine, confirm in the Arcads product or support which endpoint backs Kling / Nano Banana for your account.

**Important — V2 casing:** The Nano Banana image route uses an uppercase **`/V2/`** prefix (not `/v2/`). Keep this exact casing in all requests.

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

### `CreateImageDto` (OpenAPI) — `POST /V2/images/generate`

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

### `StartSora2Dto` (required fields)

- `productId`, `prompt`, `aspectRatio`, `duration`
- Optional: `projectId`, `refImageAsBase64`, `resolution`, `model` (`sora2` | `sora2_pro`)
- **`duration`** enum: **4, 8, 12, 16, 20** seconds. Auto-select based on script word count (see SKILL.md "Script length → video duration").
- **`resolution`** enum: `720p`, `1080p`
- **`aspectRatio`** enum: `1:1`, `16:9`, `9:16`
- **Dialogue:** Embed in `prompt` (e.g. `Dialogue: "text here"`)

### `StartVeo31Dto` (required fields)

- `productId`, `prompt`, `resolution`, `aspectRatio`
- Optional: `projectId`, `referenceImages`, `startFrame`, `endFrame` (see API docs for mutual exclusions)
- **No `duration` field** — Veo 3.1 auto-determines length (~8s typical). Warn user if script is long (>20 words).
- **`resolution`** enum: `720p`, `1080p`, `4K`
- **`aspectRatio`** enum: `1:1`, `16:9`, `9:16`
- **Dialogue:** Embed in `prompt` (e.g. `She speaks: "text here"`)

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
| B-roll | `duration` (required) | 5, 10 | No |
| Scene | None (auto) | Varies | Yes (`script` field) |
| Nano Banana (image) | N/A (still image) | N/A | No |

### File upload (for Veo reference images / frames)

- `POST /v1/file-upload/get-presigned-url` with body `{"fileType": "image/jpeg"}` (field is `fileType`, **not** `contentType`).
- Response: `presignedUrl` (for `PUT` upload to S3), `filePath` (pass this string into `startFrame` / `referenceImages` / `endFrame`), `fileId`, `expiresIn` (seconds).
- Upload: `curl -X PUT -H "Content-Type: image/jpeg" --data-binary @file.jpg "$presignedUrl"`.
- Then use `filePath` value in `StartVeo31Dto` fields.

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

`POST /v1/folders` — `{"productId": "...", "name": "Arcads API - 2026-03-24"}`. Returns `id`, `productId`, `name`.

### List folders

`GET /v1/products/{productId}/folders` — paginated list with `items[]`. Check for existing dated folder before creating a new one.

### Create project (inside a folder)

`POST /v1/projects` — `{"productId": "...", "folderId": "...", "name": "Arcads API - 2026-03-24"}`. Returns `id`, `folderId`, `name`.

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
