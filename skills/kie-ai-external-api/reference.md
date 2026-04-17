# kie.ai external API — reference

Official docs: **[docs.kie.ai](https://docs.kie.ai/)**  
Model marketplace: **[kie.ai/market](https://kie.ai/market)**  
Pricing: **[kie.ai/pricing](https://kie.ai/pricing)**  
API key management: **[kie.ai/api-key](https://kie.ai/api-key)**

## Base URL

`https://api.kie.ai`

Override with env `KIE_BASE_URL` if kie.ai provides a different host for your workspace.

## Authentication

HTTP **Bearer** token. Create a key at [kie.ai/api-key](https://kie.ai/api-key) and load it from `.env` as `KIE_API_KEY`.

On every request:

```
Authorization: Bearer $KIE_API_KEY
Content-Type: application/json
```

- **Env:** `KIE_API_KEY` — never commit it; load from `.env` locally.
- **401 / 403:** key missing, wrong, or revoked — run the setup flow in `SKILL.md` (editor-first `.env`).
- **402:** authenticated but out of credits — top up at [kie.ai/billing](https://kie.ai/billing).

### curl example

```bash
curl -sS -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nano-banana-2",
    "input": { "prompt": "a UGC selfie of a 22yo with freckles in her bedroom", "aspect_ratio": "1:1" }
  }'
```

## Endpoint families

kie.ai has two endpoint families. Most models route through the **unified task endpoint**. Veo is the exception.

### Family 1: unified task endpoint (most models)

- `POST /api/v1/jobs/createTask` — create a task. Body: `{"model": "<slug>", "input": {...}, "callBackUrl"?: "https://..."}`.
- `GET /api/v1/jobs/recordInfo?taskId=<id>` — poll task status + result. Same response shape as Veo's `record-info`.

### Family 2: Veo legacy endpoint

- `POST /api/v1/veo/generate` — Veo-specific body shape.
- `GET /api/v1/veo/record-info?taskId=<id>` — Veo-specific polling.

## Model → route mapping

| Model | Endpoint | `model` value | Input schema |
|-------|----------|---------------|--------------|
| **Seedance 2.0** (video) | `POST /api/v1/jobs/createTask` | `bytedance/seedance-2` | `SeedanceInput` (below) |
| **Sora 2 text-to-video** | `POST /api/v1/jobs/createTask` | `sora-2-text-to-video` | `Sora2TextInput` |
| **Sora 2 image-to-video** | `POST /api/v1/jobs/createTask` | `sora-2-image-to-video` | `Sora2ImageInput` |
| **Sora 2 Pro text-to-video** | `POST /api/v1/jobs/createTask` | `sora-2-pro-text-to-video` | `Sora2TextInput` |
| **Sora 2 Pro image-to-video** | `POST /api/v1/jobs/createTask` | `sora-2-pro-image-to-video` | `Sora2ImageInput` |
| **Kling 3.0** | `POST /api/v1/jobs/createTask` | `kling-3.0/video` | `KlingInput` |
| **Kling 3.0 motion-control** | `POST /api/v1/jobs/createTask` | `kling-3.0/motion-control` | `KlingMotionInput` |
| **Kling 2.6** | `POST /api/v1/jobs/createTask` | `kling-2.6/video` | `KlingInput` |
| **Nano Banana 2** (image) | `POST /api/v1/jobs/createTask` | `nano-banana-2` | `NanoBananaInput` |
| **Nano Banana Pro** (image) | `POST /api/v1/jobs/createTask` | `nano-banana-pro` | `NanoBananaInput` |
| **Veo 3 / 3.1** (video) | `POST /api/v1/veo/generate` | body includes `model: "veo3" \| "veo3_fast"` | `Veo3Body` |

Always check the current [kie.ai marketplace](https://kie.ai/market) for newer model slugs — kie.ai adds models regularly. When in doubt, click a model card on the marketplace → the page shows the exact `model` slug and `input` schema.

## Response shape

### Create response (both families)

```json
{
  "code": 200,
  "msg": "success",
  "data": { "taskId": "abc123..." }
}
```

- `code` — HTTP-style status. `200` = accepted (task created and queued). Non-200 values carry the failure reason in `msg`.
- `msg` — human-readable message (empty on success).
- `data.taskId` — opaque ID to poll.

### Poll response (both families)

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "abc123...",
    "model": "bytedance/seedance-2",
    "state": "success",
    "successFlag": 1,
    "response": {
      "resultUrls": [
        "https://cdn.kie.ai/.../output.mp4"
      ]
    },
    "paramJson": "{...original request JSON...}",
    "completeTime": 1712847623,
    "createTime": 1712847510,
    "error": null
  }
}
```

Key fields:

- **`successFlag`** — canonical state indicator:
  - `0` — generating (keep polling).
  - `1` — success — `data.response.resultUrls[]` holds the final assets.
  - `2` — failed (upstream error — retry may help).
  - `3` — failed (validation / content / config — retry will repeat the same failure; fix the prompt or inputs).
- **`data.response.resultUrls[]`** — array of public HTTPS URLs to the generated assets. For video models, a single MP4. For Nano Banana images, one or more PNGs.
- **`data.error`** — populated when `successFlag` is `2` or `3`; read for the reason.
- **`data.paramJson`** — echoes the original request body as a string; useful for log reconstruction.

### Typical polling cadence

- First poll: 3–5 s after create.
- Steady-state: every 3–5 s.
- Back off to 10 s after ~60 s of polling.
- Max generation time by model (observed on kie.ai):
  - Nano Banana image: ~30–60 s.
  - Sora 2 (4s): ~60–120 s.
  - Seedance 2.0 (4–15s): ~2–6 min.
  - Veo 3.1: ~60–90 s.
  - Kling 3.0 (up to 15s): up to ~4 min.

## Input schemas (per model)

### `SeedanceInput` — Seedance 2.0 via `createTask`

**Full `input` shape:**

```jsonc
{
  "prompt": "string (required) — the video prompt, includes dialogue if audio is enabled",
  "duration": 5,                   // integer 4-15 (seconds)
  "aspect_ratio": "9:16",          // "9:16" | "16:9"
  "resolution": "720p",            // "480p" | "720p"
  "audio": true,                    // boolean — enables speech output from the prompt

  // --- mutually exclusive reference-input modes (pick ONE) ---

  // Mode A: image-to-video
  "first_frame_url": "https://...",           // public HTTPS URL
  "last_frame_url": "https://...",            // optional, pairs with first_frame_url

  // Mode B: reference-to-video
  "reference_image_urls": ["https://..."],    // up to 3 public HTTPS URLs
  "reference_video_urls": ["https://..."],    // up to 3 public HTTPS URLs (video-to-video)
  "reference_audio_urls": ["https://..."]     // up to 3 public HTTPS URLs — can combine with any mode
}
```

**Mode rules:**

- **Image-to-video (A):** use `first_frame_url` (+ optional `last_frame_url`). No `reference_image_urls` / `reference_video_urls` in the same call.
- **Reference-to-video (B):** use `reference_image_urls` OR `reference_video_urls` (not both together — Arcads quirk carries over). Up to 3 entries.
- **Audio refs:** `reference_audio_urls` can coexist with either mode.

**Sample payload:**

```json
{
  "model": "bytedance/seedance-2",
  "input": {
    "prompt": "15 seconds UGC style skincare review...",
    "duration": 15,
    "aspect_ratio": "9:16",
    "resolution": "720p",
    "audio": true,
    "first_frame_url": "https://i.imgur.com/abc123.jpg"
  }
}
```

### `Sora2TextInput` — Sora 2 text-to-video

```jsonc
{
  "prompt": "string (required)",
  "duration": 8,                   // 4 | 8 | 12 | 16 | 20 (seconds)
  "aspect_ratio": "9:16",          // "1:1" | "16:9" | "9:16"
  "resolution": "720p"             // "720p" | "1080p"
}
```

### `Sora2ImageInput` — Sora 2 image-to-video

Same as `Sora2TextInput` plus:

```jsonc
{
  "image_url": "https://..."       // public HTTPS URL — style/mood reference, not strict first-frame
}
```

### `KlingInput` — Kling 3.0 / 2.6

```jsonc
{
  "prompt": "string (required)",
  "duration": 5,                   // 5 | 10 (Kling 2.6) or 3-15 (Kling 3.0, continuous)
  "aspect_ratio": "9:16",          // "1:1" | "16:9" | "9:16"
  "negative_prompt": "string",     // optional
  "first_frame_url": "https://...", // optional — starting frame
  "last_frame_url": "https://..."   // optional — ending frame (Kling 2.6; Kling 3.0 limited)
}
```

**Kling 3.0 note:** `last_frame_url` support is limited; frame-to-frame morph is more reliable on Veo 3.1. Kling has no native audio output — silent only.

### `NanoBananaInput` — Nano Banana 2 / Pro (image)

```jsonc
{
  "prompt": "string (required)",
  "aspect_ratio": "1:1",           // "1:1" | "16:9" | "9:16" | "3:4" | "4:3"
  "resolution": "1K",               // "1K" | "2K" | "4K"  (Pro-only for 4K)
  "output_format": "png",           // "png" | "jpg"
  "image_input": ["https://..."]    // optional — up to 14 public HTTPS reference URLs
}
```

**Field names are distinct from the video models:** Nano Banana uses `image_input[]`, not `reference_image_urls`. This is kie.ai's nomenclature for this model family.

**Pro vs 2:**
- `nano-banana-2` — default; supports 1K/2K output.
- `nano-banana-pro` — supports up to 4K; better fine-detail fidelity (text, hands, product geometry).

### `Veo3Body` — Veo 3 / 3.1 legacy endpoint

**Endpoint:** `POST /api/v1/veo/generate` (NOT `createTask`).

**Full body:**

```jsonc
{
  "prompt": "string (required)",
  "model": "veo3",                                // "veo3" | "veo3_fast" | "veo3_lite"
  "generationType": "TEXT_2_VIDEO",                // "TEXT_2_VIDEO" | "FIRST_AND_LAST_FRAMES_2_VIDEO" | "REFERENCE_2_VIDEO"
  "imageUrls": ["https://..."],                    // used when generationType != TEXT_2_VIDEO
  "aspect_ratio": "9:16",                          // "1:1" | "16:9" | "9:16"
  "resolution": "720p",                            // "720p" | "1080p" | "4k"
  "callBackUrl": "https://example.com/webhook"     // optional
}
```

**`generationType` meaning:**

| Value | `imageUrls` meaning | Use case |
|-------|---------------------|----------|
| `TEXT_2_VIDEO` | Ignored | Pure text prompt, no reference image. |
| `FIRST_AND_LAST_FRAMES_2_VIDEO` | `[firstFrameUrl]` (first-frame only) or `[firstFrameUrl, lastFrameUrl]` | Animate from a specific starting image; optionally morph to an ending image. |
| `REFERENCE_2_VIDEO` | Up to 3 URLs | Style / mood references, not literal first-frame. |

**Poll:** `GET /api/v1/veo/record-info?taskId=<id>` — same `successFlag` semantics as the unified endpoint.

## Per-model quick reference

| Field | Sora 2 | Sora 2 Pro | Veo 3 / 3.1 | Kling 2.6 | Kling 3.0 | Seedance 2.0 | Nano Banana 2 / Pro |
|-------|:------:|:----------:|:-----------:|:---------:|:---------:|:------------:|:-------------------:|
| `prompt` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `duration` | 4/8/12/16/20 | 4/8/12/16/20 | auto ~8s | 5/10 | 3–15 | 4–15 | n/a (still) |
| `resolution` | 720p/1080p | 720p/1080p | 720p/1080p/4k | — | — | 480p/720p | 1K/2K/4K† |
| `aspect_ratio` | 1:1/16:9/9:16 | 1:1/16:9/9:16 | 1:1/16:9/9:16 | 1:1/16:9/9:16 | 1:1/16:9/9:16 | 9:16/16:9 | 1:1/16:9/9:16/3:4/4:3 |
| `first_frame_url` | ❌ (via `image_url`) | ❌ (via `image_url`) | via `imageUrls[0]` + `FIRST_AND_LAST_FRAMES_2_VIDEO` | ✅ | ✅ | ✅ |
| `last_frame_url` | — | — | via `imageUrls[1]` + `FIRST_AND_LAST_FRAMES_2_VIDEO` | ✅ | limited (prefer Veo) | ✅ |
| `reference_image_urls` | ❌ (`image_url` only, 1 ref) | ❌ (`image_url` only, 1 ref) | via `imageUrls[]` + `REFERENCE_2_VIDEO` (max 3) | — | — | max 3 |
| `reference_video_urls` | — | — | — | — | — | max 3 |
| `reference_audio_urls` | — | — | — | — | — | max 3 |
| `image_input` (image model) | — | — | — | — | — | — | max 14 |
| `audio` / speech | ✅ from prompt | ✅ from prompt | ✅ from prompt | ❌ silent | ❌ silent | ✅ via `audio: true` | n/a |

† `nano-banana-2` tops out at 2K; `nano-banana-pro` supports 4K.

## File hosting (public HTTPS URLs)

**Unlike presigned-upload APIs, kie.ai does not host your reference files.** Every URL you pass in `first_frame_url`, `last_frame_url`, `reference_image_urls[]`, `reference_video_urls[]`, `reference_audio_urls[]`, `image_url`, `image_input[]`, or Veo `imageUrls[]` must be:

1. **HTTPS** (HTTP is rejected).
2. **Publicly reachable** — no auth headers, no IP allowlist. kie.ai's workers fetch the URL server-side.
3. **A direct file URL** with a correct `Content-Type` — not an HTML preview page. (Imgur gotcha: use `https://i.imgur.com/xxx.jpg`, not `https://imgur.com/xxx`.)
4. **Stable for the lifetime of the task** — the worker fetches at enqueue time; if the URL expires before that, the task fails with a validation error.

### Recommended hosting options

| Option | When to use | Notes |
|--------|-------------|-------|
| **Imgur** | Single-use references; no account for single images | Free, instant. Use the `i.imgur.com` direct link. |
| **Supabase Storage** | Owned hosting; fits inside an existing Supabase project | Public bucket with a policy allowing `SELECT` for anon. |
| **Cloudflare R2** | High volume; wants zero egress cost | Bucket + public.r2.dev URL or custom domain. |
| **AWS S3 + CloudFront** | Enterprise; wants signed short-lived URLs | Presigned URLs work as long as they're valid long enough for the worker to fetch. |
| **Backblaze B2** | Cheap egress | Bucket with public download settings. |
| **GitHub raw** | Small, already-committed assets | `https://raw.githubusercontent.com/<user>/<repo>/<branch>/<path>` — fine for tests, not for prod or sensitive refs. |

**Never pass:** `localhost`, `127.0.0.1`, private IPs, `file://`, `data:`, Google Drive / Dropbox share pages (these redirect to HTML), or presigned URLs that expire before kie.ai fetches them.

### Sanity check a URL before firing

```bash
curl -I -L "$URL"
# Expect: HTTP/2 200, Content-Type: image/* or video/*
```

## File minimum sizes

Kie.ai accepts images down to ~512 px on the longest side for most video models. Nano Banana handles smaller inputs but output quality suffers below 1K input.

**Recommended:** upscale reference images to **1080 px on the longest side** before hosting. On macOS:

```bash
sips -Z 1080 input.jpg --out upscaled.jpg
```

Or with ImageMagick:

```bash
convert input.jpg -resize 1080x1080\> upscaled.jpg
```

## Callbacks (optional)

Any `createTask` or `veo/generate` call accepts an optional `callBackUrl`. Kie.ai will `POST` the final task payload to that URL when `successFlag` becomes `1`, `2`, or `3`. Payload shape matches the poll response.

**When to use callbacks:**
- You have a public webhook endpoint (e.g. a deployed Cloudflare Worker or Vercel function).
- You want to avoid polling overhead for long-running tasks (Seedance, Kling 3.0).

**When NOT to use callbacks:**
- Running locally from Claude Code or Cursor — you don't have a public endpoint. Just poll.

For this skill, **polling is the default**.

## Errors

| HTTP | Typical meaning |
|------|-----------------|
| 401 | Missing / bad `Authorization: Bearer` header |
| 402 | Valid key, out of credits — top up at [kie.ai/billing](https://kie.ai/billing) |
| 400 / 422 | Malformed body or invalid field value (bad `model` slug, missing required `input` field, wrong enum) |
| 429 | Rate-limited — back off and retry |
| 500 / 503 | Upstream model error — retry once or twice before surfacing |

**Task-level failures** (HTTP 200 on create, but `successFlag: 2 \| 3` on poll):

- `2` — transient / upstream. Retrying the same payload often works.
- `3` — validation / content-policy / config. Do **not** retry the same payload. Read `data.error.message` and fix the prompt or inputs.

Common `data.error.message` strings:
- `"content policy violation"` / `"flagged by content checker"` — prompt triggered moderation. Tighten wording.
- `"failed to download reference url"` — your hosted image isn't reachable (expired, private, or HTML instead of image).
- `"invalid duration"` / `"invalid aspect_ratio"` — re-check the per-model field compatibility table.

## Health check

Kie.ai does not publish an unauthenticated health endpoint. The skill's `scripts/check-kie-env.sh` script probes auth by sending an intentionally-empty `POST /api/v1/jobs/createTask` — the server validates the Bearer token before the body, so a good key returns `400`/`422` (body rejected) and a bad key returns `401`.

## Migration notes (Arcads → kie.ai)

For anyone carrying knowledge over from the Arcads version of this skill:

| Arcads concept | kie.ai equivalent |
|---------------|-------------------|
| `Authorization: Basic <base64>` + `ARCADS_API_KEY` | `Authorization: Bearer <key>` + `KIE_API_KEY` |
| `POST /v2/videos/generate` (unified) | `POST /api/v1/jobs/createTask` (unified, different body shape: `{model, input}`) |
| `POST /v2/images/generate` | same `POST /api/v1/jobs/createTask` with `model: "nano-banana-2"` etc. |
| `POST /v1/veo31/generate/video` | `POST /api/v1/veo/generate` |
| `GET /v1/assets/{id}` polling | `GET /api/v1/jobs/recordInfo?taskId=<id>` (or `/api/v1/veo/record-info` for Veo) |
| Asset status `created \| pending \| generated \| failed \| uploaded` | `successFlag`: `0` (generating) → `1` (success) / `2` / `3` (failed) |
| `startFrame` (presigned filePath) | `first_frame_url` (public HTTPS URL) |
| `endFrame` | `last_frame_url` |
| `referenceImages[]` | `reference_image_urls[]` (Seedance) / `image_input[]` (Nano Banana) / `imageUrls[]` + `REFERENCE_2_VIDEO` (Veo) |
| `referenceVideos[]` | `reference_video_urls[]` (Seedance only) |
| `referenceAudios[]` | `reference_audio_urls[]` (Seedance only) |
| `audioEnabled: true` | `audio: true` (Seedance) — for Veo/Sora/Sora Pro, speech is enabled by embedding dialogue in the `prompt` |
| `productId`, folders, projects, `POST /v1/assets/add-to-project` | **Removed.** kie.ai has no workspace/org model; organize outputs locally in `outputs/`. |
| `POST /v1/file-upload/get-presigned-url` | **Removed.** You host files yourself at a public HTTPS URL. |
| `POST /v1/b-roll`, `POST /v1/scene`, `POST /v1/scripts`, `POST /v1/omnihuman`, `POST /v1/audio-driven`, `POST /v1/sora2/remix/video` | **No direct kie.ai equivalent.** For b-roll / scene, use Kling 3.0 or Nano Banana. For lip-sync actor avatars, kie.ai doesn't host talent — use an external service. |
| `creditsCharged` on response | Not returned. Price from `MASTER_CONTEXT.md` table. |
| `nbGenerations` (batch Sora 2) | Not supported. Fire N separate `createTask` calls in parallel. |
