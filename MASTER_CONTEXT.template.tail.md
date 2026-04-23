## Project snapshot — Arcads

- **API base:** `https://external-api.arcads.ai` (see `.env.example`).
- **Auth:** HTTP Basic via `ARCADS_BASIC_AUTH` (pre-encoded `Basic ...` header) or `ARCADS_API_KEY` as Basic password. Values in `.env` must be **single-quoted** (special chars: `{`, `[`, `*`).
- **Skill:** `.claude/skills/arcads-external-api/` and `.cursor/skills/arcads-external-api/` (sync from `skills/arcads-external-api/` via `scripts/sync-skill.sh`).

## My workspace

- **Default product ID:** _(auto-populated after first `GET /v1/products` call)_
- **Default product name:** _(auto-populated)_

## Credit costs

_Fill in your plan's credit costs below. The agent references this table before every generation. If left blank, the agent will ask you once and can fill them in._

| Model | Credits per generation | Notes |
|-------|----------------------|-------|
| Veo 3.1 | 1 | Same cost at 720p, 1080p, and 4K |
| Sora 2 | _(fill in)_ | |
| Sora 2 Pro | _(fill in)_ | Auto-selected when using `refImageAsBase64` |
| Kling 3.0 (scene) | _(fill in)_ | |
| Kling 3.0 (b-roll) | _(fill in)_ | |
| Nano Banana 2 (image, `nano-banana-2`) | 0.03 | ~35s generation time |
| Nano Banana Pro (image, `nano-banana`) | _(fill in)_ | |
| Nano Banana (scene) | _(fill in)_ | |

## API learnings — Arcads

These are confirmed behaviors of the Arcads external API.

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
- **Default resolution: `720p`** — 4K and 1080p show no visible quality difference for UGC content but produce 3-8x larger files.

### Sora 2

- `refImageAsBase64` is a **style/mood reference only** — it does NOT preserve face, pose, or scene from the input image. Do NOT use Sora 2 to animate a specific starting frame.
- Best for: text-only video generation, or when you just have a product photo and want to generate a UGC video directly (no starting frame step).
- Supports duration up to 20s (enum: 4, 8, 12, 16, 20).

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
