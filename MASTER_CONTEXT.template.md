# Master context (kie.ai + agents)

**Purpose:** One place for humans and AI agents to capture **decisions**, **brand voice**, **API quirks**, and **what we learned** while using this repo with kie.ai.

## How agents should use this file

- **At the start of substantive work:** Read this file for project-specific context that is not in the skill.
- **After meaningful changes:** Append a new **dated entry** under [Changelog](#changelog) (Decision / What changed / Why).
- **If fields are empty:** Offer to populate them (cost rates from the user, brand voice from the user).

## Project snapshot

- **kie.ai API base:** `https://api.kie.ai` (see `.env.example`).
- **Skill:** `.claude/skills/kie-ai-external-api/` and `.cursor/skills/kie-ai-external-api/` (sync from `skills/kie-ai-external-api/` via `scripts/sync-skill.sh`).

## Cost rates

_Fill in your per-model cost rates below. The agent references this table before every generation. If left blank, the agent will ask you once and can fill them in. Pricing source: [kie.ai/pricing](https://kie.ai/pricing)._

| Model | Unit cost | Notes |
|-------|-----------|-------|
| Seedance 2.0 (image-to-video) | _(fill in, e.g. $0.06/sec)_ | kie.ai slug: `bytedance/seedance-2` |
| Seedance 2.0 (video-to-video) | _(fill in)_ | |
| Sora 2 (text-to-video) | _(fill in, e.g. $0.50 per 8s)_ | kie.ai slug: `sora-2-text-to-video` |
| Sora 2 (image-to-video) | _(fill in)_ | kie.ai slug: `sora-2-image-to-video` |
| Sora 2 Pro | _(fill in)_ | kie.ai slugs: `sora-2-pro-text-to-video`, `sora-2-pro-image-to-video` |
| Veo 3.1 (veo3) | _(fill in, e.g. $1.00/gen ~8s)_ | kie.ai endpoint: `POST /api/v1/veo/generate`, `model: veo3` |
| Veo 3.1 Fast (veo3_fast) | _(fill in)_ | kie.ai `model: veo3_fast` |
| Kling 3.0 (video) | _(fill in)_ | kie.ai slug: `kling-3.0/video` |
| Kling 2.6 (video) | _(fill in)_ | kie.ai slug: `kling-2.6/video` |
| Nano Banana 2 (image) | _(fill in, e.g. $0.03/image)_ | kie.ai slug: `nano-banana-2` |
| Nano Banana Pro (image) | _(fill in)_ | kie.ai slug: `nano-banana-pro`; supports 4K |

## Brand (optional)

_Edit or replace with your real brand blocks (see `skills/kie-ai-external-api/prompting/brand-voice-starter.md`)._

- **Tone:**
- **Audience:**
- **Words to use / avoid:**

## Reference image hosting

_Fill in your preferred host so the agent doesn't ask every time._

- **Preferred host:** _(e.g. Imgur for quick tests, Cloudflare R2 for repeat use, Supabase for project-scoped uploads)_
- **Base URL (if self-hosted):**
- **Public bucket name (if R2/S3/Supabase):**

Drop reference images into `references/`:
- `references/influencers/` — face/body photos to recreate as AI people
- `references/products/` — product photos for showcase workflows
- `references/aesthetics/` — mood boards, lighting references, style inspiration

The agent checks this folder when composing prompts and will offer to use images from it — but **kie.ai needs a public HTTPS URL**, so you'll host them before firing. See `skills/kie-ai-external-api/SKILL.md` → "Reference images: hosting and public URLs" for the flow.

## API learnings (universal)

These are confirmed behaviors of the kie.ai API. They apply to all workspaces.

### Auth

- HTTP Bearer with `KIE_API_KEY` in `.env`: `Authorization: Bearer $KIE_API_KEY`.
- Values in `.env` must be **single-quoted** if they contain shell special chars (rarely needed for kie.ai keys, but keep the convention).

### Endpoint families

- **Unified tasks:** `POST /api/v1/jobs/createTask` with `{model, input}` body → poll via `GET /api/v1/jobs/recordInfo?taskId=<id>`. Used for Seedance, Sora 2, Kling, Nano Banana.
- **Veo legacy:** `POST /api/v1/veo/generate` (flat body with `generationType`) → poll via `GET /api/v1/veo/record-info?taskId=<id>`.

### Polling

- Both endpoint families return `successFlag`: `0` = generating, `1` = success, `2`/`3` = failed.
- `data.response.resultUrls[]` holds the generated asset URLs.
- Typical generation times: Nano Banana ~30–60s, Sora 2 4s ~60–120s, Seedance 4–15s ~2–6 min, Veo ~60–90s, Kling 3.0 up to ~4 min.

### Reference image hosting

- kie.ai does NOT host your reference images. Pass **public HTTPS URLs**.
- Base64 is not accepted anywhere in this skill's supported flows.
- Imgur quirk: use the direct `i.imgur.com/*.jpg` link, not the page URL.
- Google Drive / Dropbox share pages redirect to HTML — won't work.

### Seedance 2.0

- Slug: `bytedance/seedance-2`. `input.audio: true` to enable speech.
- **Mutually exclusive input modes:** image-to-video (`first_frame_url` [+ optional `last_frame_url`]) vs reference-to-video (`reference_image_urls[]` OR `reference_video_urls[]`). Do not combine.
- `reference_audio_urls[]` can coexist with any mode.
- Aspect ratio: `9:16` or `16:9` only (no 1:1).
- Duration: 4–15s continuous.
- Resolution: 480p or 720p.

### Sora 2

- Text-to-video slug: `sora-2-text-to-video`. Image-to-video: `sora-2-image-to-video` — uses `input.image_url` as a style/mood ref (not a strict first-frame animate).
- Duration enum: 4, 8, 12, 16, 20. Aspect ratios: 1:1, 16:9, 9:16. Resolution: 720p, 1080p.
- Speech supported via dialogue in the `prompt` field.

### Veo 3.1

- Endpoint: `POST /api/v1/veo/generate` (different body than the unified task endpoint).
- `generationType`:
  - `TEXT_2_VIDEO` — pure text.
  - `FIRST_AND_LAST_FRAMES_2_VIDEO` — `imageUrls: [firstFrameUrl]` or `[firstFrameUrl, lastFrameUrl]` for first-frame / frame-to-frame morph.
  - `REFERENCE_2_VIDEO` — up to 3 style/mood reference URLs.
- Duration auto-determined (~8s). Resolution: 720p, 1080p, 4k. Aspect ratios: 1:1, 16:9, 9:16.
- **ALWAYS include** `"No subtitles, no captions, no text overlays."` at the end of every Veo prompt — Veo 3.1 sometimes burns subtitles into the video.
- **Human motion cues are mandatory** — without them subjects look like frozen mannequins. Include 3–4 cues per prompt: breaking eye contact, head tilts, shifting weight, adjusting product grip.

### Kling 3.0

- Slug: `kling-3.0/video`. Silent only (no native speech output).
- Duration: 3–15s continuous. Aspect ratios: 1:1, 16:9, 9:16.
- `first_frame_url` supported; `last_frame_url` support is limited — prefer Veo 3.1 for frame-to-frame morph.

### Nano Banana (image)

- Slugs: `nano-banana-2` (default, 1K/2K) or `nano-banana-pro` (supports 4K, better fine detail).
- `input.image_input[]` — up to 14 reference URLs. Note: this is **different** from the video models' `reference_image_urls`.
- Output at `data.response.resultUrls[0]`. No `thumbnailUrl`.
- Aspect ratios: 1:1, 16:9, 9:16, 3:4, 4:3.

### Influencer recreation

- Must follow two-step flow: (1) generate still image via `nano-banana-2` with `image_input[]`, (2) show user for approval, (3) only then generate video using the approved still's public URL as `first_frame_url` (Seedance) or `imageUrls[0]` + `FIRST_AND_LAST_FRAMES_2_VIDEO` (Veo).
- Never skip the approval step — video is expensive, stills are cheap to iterate.

### UGC prompting

- **Imperfection block (camera):** Every UGC image/video prompt must include camera imperfections: motion blur, overexposure, grain, lens distortion, off-center framing, soft focus. Without this, output looks too polished.
- **Skin realism block (mandatory):** Include 3–4 subtle skin cues inline with character description: "visible pores, slight unevenness in skin tone, minor undereye shadows, hint of shine from natural oils." Do NOT use: acne, pimples, breakouts, blemishes, redness. Goal: "real person, not retouched" — not "person with skin problems."
- **Reference image order:** character hero first (strongest identity signal), then product, then style refs from `references/aesthetics/`.
- **Style references:** Store in `references/aesthetics/{style-name}/` (e.g., `ugc-selfie/`, `cinematic/`). Host a few and load their URLs as reference URLs in the call.

### Image QA

- Agents must visually review still images after generation (hands, fingers, limbs, face, merged objects, artifacts).
- If defective, regenerate with refined prompt — up to 2 retries (3 attempts total).
- QA retries skip a second cost confirmation but still bill.

## Changelog

### YYYY-MM-DD -- Template entry

- **Decision:**
- **Change:**
- **Why:**
