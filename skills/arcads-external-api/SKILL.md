---
name: arcads-external-api
description: >-
  Creates and retrieves AI video and image-related assets via the Arcads external API (Sora 2, Veo 3.1, Nano Banana, b-roll, scene, script/actor flows). Loads prompts from the bundled prompting guide and model library, respects HTTP Basic auth from ARCADS_API_KEY, and polls assets/videos until ready. Use when the user mentions Arcads, external-api.arcads.ai, Sora2, Veo, Kling, Nano Banana, b-roll, UGC scripts, or generating marketing creative through Arcads.
---

# Arcads external API

## Configuration

- **Base URL:** `https://external-api.arcads.ai` (or `ARCADS_BASE_URL`).
- **Auth:** HTTP Basic — use `ARCADS_API_KEY` as the **username** and an **empty password** unless Arcads documentation for your key specifies otherwise. Example curl: `curl -u "$ARCADS_API_KEY:" "$ARCADS_BASE_URL/v1/products"`.
- **Never** print API keys, commit `.env`, or paste keys into `MASTER_CONTEXT.md`.

### If the key is missing or the API returns 401/403

1. **Editor-first (default):** Ensure `.env` exists (copy from `.env.example` in the repo root). Ask the user to paste `ARCADS_API_KEY` **only inside** `.env` and save. Do not ask them to paste the key in chat unless they insist.
2. **Chat-assisted:** If they paste the key in chat, write `.env` for them, confirm "saved to `.env`" **without repeating the key**, and remind them that chat history may retain secrets—rotate the key in Arcads if the chat could be shared.

Before the first call, confirm `.gitignore` excludes `.env`.

## Read order

1. Repo root **`MASTER_CONTEXT.md`** when present (brand voice, decisions, quirks).
2. This skill's **[reference.md](reference.md)** for routes, bodies, polling.
3. **[prompting/guide.md](prompting/guide.md)** then the right **`prompting/prompt-library/`** file for the model (see table below).

## Decision tree: which flow?

| User goal | Start here | Prompt library |
|-----------|------------|----------------|
| Raw **Sora 2** video from text (plus product) | `POST /v1/sora2/generate/video` | [prompt-library/sora-2.md](prompting/prompt-library/sora-2.md) |
| **Sora** remix of an existing asset | `POST /v1/sora2/remix/video` | [sora-2.md](prompting/prompt-library/sora-2.md) |
| **Veo 3.1** video | `POST /v1/veo31/generate/video` | [prompt-library/veo-3-1.md](prompting/prompt-library/veo-3-1.md) |
| **Nano Banana still image** (standalone or as starting frame for video) | `POST /V2/images/generate` with `"model":"nano-banana-2"` by default; optional `"model":"nano-banana"` (Nano Banana Pro) (note uppercase V2) | [nano-banana.md](prompting/prompt-library/nano-banana.md) |
| **B-roll** clip (product-level) | `POST /v1/b-roll` | [kling-3.md](prompting/prompt-library/kling-3.md) or [nano-banana.md](prompting/prompt-library/nano-banana.md) for craft; see [reference.md](reference.md) for Kling/Nano routing notes |
| **Scene** generation | `POST /v1/scene` | Same as b-roll row |
| **Kling 3.0** style video | Often **b-roll** / **scene** in Arcads; asset `type` may read `kling_30` | Vendor guide in [kling-3.md](prompting/prompt-library/kling-3.md) |
| **Recreate an influencer** from a reference photo | **Two-step:** (1) `POST /V2/images/generate` with `refImageAsBase64` to generate a **still image** via Nano Banana, get user approval; (2) upload approved still → `POST /v1/veo31/generate/video` with `startFrame` for video. **Never skip the approval step.** | [prompt-library/influencer-recreation.md](prompting/prompt-library/influencer-recreation.md) — full workflow: analyze → prompt → still → approve → video |
| **Product showcase** — AI person holds/uses a product and talks about it | **Two-step:** (1) `POST /V2/images/generate` with product `refImageAsBase64` to generate a starting frame of the AI person with the product; (2) user approves still; (3) start-frame → Veo 3.1 / Sora 2 / Kling 3.0 for video. | [prompt-library/product-showcase.md](prompting/prompt-library/product-showcase.md) |
| **UGC / selfie-style** (authentic reels) | Any model route (Sora2, Veo31) or scene/b-roll | [prompt-library/ugc-selfie-style.md](prompting/prompt-library/ugc-selfie-style.md) — cross-model UGC guide with iPhone-shot aesthetic, negative prompts, per-model formulas |
| **Create a new AI influencer** from a text description (character sheet) | **Two-pass:** (1) generate hero front portrait via `POST /V2/images/generate`, get user approval; (2) generate 9 remaining angles with hero as `referenceImages`. Save all 10 to `references/influencers/`. | [prompt-library/character-sheet.md](prompting/prompt-library/character-sheet.md) — full workflow: describe → expand → hero → approve → 9 angles → QA → save |
| **UGC product selfie** — AI influencer holding a product in a selfie-style image | Combine character hero + product photo + style references from `references/aesthetics/` as `referenceImages`. Prompt must include imperfection block for authenticity. | [prompt-library/ugc-product-selfie.md](prompting/prompt-library/ugc-product-selfie.md) — full workflow: gather inputs → upload refs → compose prompt → generate → iterate |
| **Static ad** — product heroes, lifestyle shots, flat lays, banners, abstract brand visuals (no people) | `POST /V2/images/generate` with product photo as `refImageAsBase64` and/or style refs as `referenceImages`. Choose category (product hero, lifestyle, flat lay, ingredient, abstract, banner, seasonal). | [prompt-library/static-ad.md](prompting/prompt-library/static-ad.md) — full workflow: concept → category → compose prompt → generate → QA → iterate |
| **Ad remix** — recreate an existing ad with new branding, product, or colors | Analyze reference ad → define swap plan → `POST /V2/images/generate` with reference ad as `referenceImages` (style) + product photo as `refImageAsBase64` (fidelity). | [prompt-library/ad-remix.md](prompting/prompt-library/ad-remix.md) — full workflow: analyze → swap plan → compose prompt → generate → compare → iterate |
| **Model comparison** — find the best image model for a specific ad type | Fire the same prompt across multiple models (`nano-banana-2`, `nano-banana`, `gpt-image`, `seedream`, etc.) via `POST /V2/images/generate`, compare results side by side. | [prompt-library/image-quality-playbook.md](prompting/prompt-library/image-quality-playbook.md) — model list, comparison workflow, quality workarounds |
| **Talking avatar / script** (actors, voices) | `POST /v1/products` → folders/projects/scripts as needed; `POST /v1/scripts`, `POST /v1/scripts/{id}/generate` | [prompting/guide.md](prompting/guide.md) for brief structure; pull `situationId` / `voiceId` from `GET /v1/actors`, `GET /v1/situations`, `GET /v1/voices` |
| **OmniHuman** | `POST /v1/omnihuman` or script `generate-omnihuman` per API | [prompting/guide.md](prompting/guide.md) |
| **Audio-driven** | `POST /v1/audio-driven` | [prompting/guide.md](prompting/guide.md) |

Prefer the **shortest** path: if the user only needs Sora2 or Veo31, do not create scripts unless they ask for actors/lip-sync workflows.

## Creative layer

- **MANDATORY:** Before composing any prompt for the API, **read the relevant `prompting/prompt-library/*.md` file** for the chosen model/workflow. Do NOT skip this step — every prompt must align with the vendor guide's formula and best practices.
- Build **one** clear prompt paragraph; avoid keyword soup.
- For Sora2 / Veo3.1 / Kling / Nano Banana, align with the **official vendor guides** linked in each `prompting/prompt-library/*.md` file (do not paste full vendor docs into chat—summarize checks).
- Merge slot values from the user and from **`MASTER_CONTEXT.md`** when it conflicts with defaults.

## Session setup: auto-create a dated folder

At the **start of each session** that will generate assets, create a folder and project for the day so everything is organized in the Arcads dashboard:

1. Get today's date as `YYYY-MM-DD`.
2. `GET /v1/products` → pick the target product (default to whichever `MASTER_CONTEXT.md` specifies under "My workspace"). If no default is set: if only one product exists, auto-populate `MASTER_CONTEXT.md` with its ID and name; if multiple, ask the user to pick and save their choice to `MASTER_CONTEXT.md`.
3. Check existing folders (`GET /v1/products/{productId}/folders`) — if **"Arcads API - {today}"** already exists, reuse it. Otherwise:
   - `POST /v1/folders` with `{"productId": "...", "name": "Arcads API - YYYY-MM-DD"}`.
   - `POST /v1/projects` with `{"productId": "...", "folderId": "...", "name": "Arcads API - YYYY-MM-DD"}`.
4. Store the `projectId` for the session and pass it in every generation call (`projectId` field on Sora2/Veo31/b-roll/scene/image DTOs) **and** use `POST /v1/assets/add-to-project` after generation for asset types that do not accept `projectId` directly.

This ensures every generated asset is findable in the Arcads dashboard under **Product → "Arcads API - {date}"**.

## Credit cost estimation (MANDATORY — show before generating)

Before firing **any** generation calls, calculate and present the total credit cost to the user. **Do not generate until the user confirms.**

### Credit cost table

Check `MASTER_CONTEXT.md` → **Credit costs** table. If the table is empty, ask the user for their per-model credit pricing and **write the values into `MASTER_CONTEXT.md`** so future sessions have them. Do NOT guess or use placeholder values.

The Arcads API does not expose credit/billing endpoints. Costs must be provided by the user.

### How to calculate

```
total_credits = sum(credits_per_model × variations_requested) for each model
```

### Example output to user

```
Credit cost breakdown:
  Veo 3.1     × 2 variations = 8 credits
  Sora 2 Pro  × 2 variations = 8 credits
  Kling 3.0   × 2 variations = 4 credits
  ─────────────────────────────
  Total: 20 credits

Proceed? (yes/no)
```

Always wait for confirmation before firing. If the user has a credit balance visible in `MASTER_CONTEXT.md`, warn them if the total would exceed it. If credit costs have not been configured yet, ask the user to provide them before the first generation.

**Exception — QA-fix retries (still images only):** After the user has confirmed the initial batch, **automatic regeneration to fix visible defects** (see [Generated image QA](#generated-image-qa-mandatory) below) does **not** require asking again for credit confirmation. Each retry is still billed — note the extra `creditsCharged` when summarizing the session.

## Generation count: multiple variations per prompt

Before firing any generation call, **ask the user how many variations** they want for this prompt. Default is 1 if they don't specify.

When the count is greater than 1, send **N separate API calls** with the identical payload. Do NOT batch them into a single request — the API has no batch parameter. Fire them in parallel where possible, then poll all asset IDs concurrently.

Present results as a numbered list so the user can compare and pick favorites.

## Nano Banana image: model choice (`nano-banana-2` vs Nano Banana Pro)

For `POST /V2/images/generate` when using a Nano Banana engine:

- **Default:** `"model": "nano-banana-2"` (Nano Banana 2).
- **Optional:** `"model": "nano-banana"` when the user asks for **Nano Banana Pro** (the API has no `nano-banana-pro` enum — Pro maps to `nano-banana`; see [nano-banana.md](prompting/prompt-library/nano-banana.md)).

Before the first Nano Banana image call in a workflow, ask: *"Use default Nano Banana 2, or Nano Banana Pro?"* If they have no preference, use `nano-banana-2`. Include the chosen `model` in the credit estimate (separate rows in `MASTER_CONTEXT.md` if pricing differs).

## Script and dialogue

For any video that features a person speaking, **ask the user for the script** (the exact words the AI person should say). This is separate from the visual prompt — it's the dialogue.

- For **Veo 3.1** and **Sora 2**: embed the dialogue in the `prompt` field using a `Dialogue: "..."` or `She speaks: "..."` pattern (these models generate speech from the text prompt).
- For **Scene** (`CreateSceneDto`): use the dedicated `script` field for dialogue and `prompt` for visuals.
- For **B-roll**: no speech — b-roll is silent/ambient by nature. If the user wants speech, redirect to Veo 3.1, Sora 2, or Scene.
- For **Nano Banana images**: no speech — these are still images. Speech is handled in the subsequent video generation step.

## Script length → video duration (auto-select)

Use the script's word count to automatically pick the best `duration` value. Average speaking pace: **~2.5 words per second** (~150 WPM). Round **up** to the next available duration to give breathing room.

### Sora 2 — duration enum: `[4, 8, 12, 16, 20]` seconds

| Script length | Duration |
|---------------|----------|
| 1–8 words | 4s |
| 9–18 words | 8s |
| 19–28 words | 12s |
| 29–38 words | 16s |
| 39–48 words | 20s |
| **49+ words** | **Too long** — offer to split (see below) |

### Veo 3.1 — no `duration` field

Veo 3.1 auto-determines video length (~8s typical). If the script exceeds ~20 words, warn the user that Veo may truncate dialogue and offer to split or switch to Sora 2 which has longer duration options.

### B-roll (Kling 3.0) — duration enum: `[5, 10]` seconds

B-roll is typically wordless. If the user insists on a timed clip with context:

| Script length | Duration |
|---------------|----------|
| 1–12 words | 5s |
| 13–24 words | 10s |
| **25+ words** | **Too long** — redirect to Sora 2 / Veo 3.1 for speech |

### Scene — no `duration` field

Scene auto-determines length. Use the `script` field for dialogue.

## Splitting long scripts into multiple videos

If the script exceeds the maximum duration for the chosen model:

1. **Tell the user** the script is too long for a single video and show the word/duration math.
2. **Offer two options:**
   - **Split into segments** — the agent breaks the script at natural sentence boundaries into chunks that each fit within the model's max duration. Each chunk becomes a separate generation call.
   - **Switch models** — if they're on Kling (10s max), suggest Sora 2 (up to 20s).
3. If the user chooses to split, generate each segment as a separate video (respecting the generation count — if they asked for 3 variations, generate 3 of *each* segment).
4. **Offer to stitch** the final segments together using `ffmpeg`:
   - Download all segment videos locally.
   - Concatenate using `ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4` (re-encode if codecs differ).
   - Present the stitched file alongside the individual segments so the user has both.

## Veo 3.1: `startFrame` vs `referenceImages` — pick one

Veo 3.1 has two mutually exclusive image input modes. **Never use both on the same call.**

| Mode | Field | When to use |
|------|-------|-------------|
| **Start frame** | `startFrame` (presigned upload `filePath`) | User provides a reference image of a **person or scene they want the video to start from**. The video will animate from this exact image. Use this for influencer recreation, character consistency, or any "make this image come alive" request. |
| **Reference images** | `referenceImages` (array of `filePath` strings) | User provides images for **style, mood, or visual tone** — not to appear literally in frame. The model uses them as inspiration, not as a first frame. |

**Default rule:** When the user provides a single reference photo of a person, **always use `startFrame`** unless they explicitly say they want it as a style reference.

## Image handling: auto-upscale small inputs

Before sending any reference image, start frame, or base64 image to the API:

1. **Check dimensions.** If the image's longest side is below **1024 px**, upscale it using Lanczos resampling so the longest side reaches **1080 px** (preserve aspect ratio).
2. **Convert to RGB JPEG** (quality 90–95) to strip alpha channels and keep payload size reasonable.
3. Re-encode as base64 (for `refImageAsBase64`) or upload the resized file (for `startFrame` via presigned URL).

Several Arcads endpoints (notably `POST /v1/b-roll`) reject images below a minimum resolution with `422 — The provided image is too small`. Auto-upscaling prevents this silently so the user never hits the error.

## Generated image QA (mandatory)

Applies to **still images** from Arcads, especially `POST /V2/images/generate` (Nano Banana and other image models). After each image asset reaches `status: generated`, **visually inspect the output** (download or open the image URL / use the agent's image-reading capability).

**Look for:** extra or missing hands or fingers; wrong limb count; distorted, duplicated, or merged facial features; melted or fused objects; impossible anatomy; stray limbs; obvious texture or boundary artifacts; unreadable or garbled text if text was requested.

**If something looks wrong:** Do **not** hand off the bad frame as the final deliverable without trying again. **Regenerate** with a **revised prompt** that explicitly corrects the issue (e.g. "exactly two hands, five fingers each, anatomically correct arms," "single face, no duplicate features"). Do **not** resend the identical payload and expect a different outcome.

**Retry cap:** Up to **2 regeneration attempts per originally requested image** (3 attempts total including the first). If defects remain after the cap, stop auto-retries, tell the user what still looks wrong, show the best attempt or URLs for all attempts, and ask how they want to proceed.

**Credits:** Each attempt is a separate generation and is billed. Summarize total credits used for that image after the QA loop ends. See **Exception — QA-fix retries** under [Credit cost estimation](#credit-cost-estimation-mandatory--show-before-generating).

**Video (optional quick check):** Before spending heavily on downstream video, you may spot-check **scene/b-roll thumbnails** or extracted frames for the same kinds of defects; scope is lighter than for hero stills.

Details and checklist items: [prompting/prompt-library/nano-banana.md](prompting/prompt-library/nano-banana.md).

## Creative brief intake

If the user mentions a brief, check `references/briefs/` for filled-in copies of `BRIEF_TEMPLATE.md`. Read the brief and extract all inputs needed for the chosen workflow (static ad, ad remix, product showcase, etc.). The brief replaces the need to ask the user each question individually — but still confirm any ambiguous or missing fields before generating.

If no brief exists but the user wants to use one, point them to `references/briefs/BRIEF_TEMPLATE.md` and ask them to copy, fill in, and save it.

## Execution checklist (agent)

1. **Session folder:** Ensure today's dated folder + project exist (see above).
2. Resolve `productId` (and `projectId` from session folder): `GET /v1/products` or ask the user.
3. **Ask for script/dialogue:** If the output is a video with a person speaking, ask the user for the exact words. Count words to auto-select duration (see "Script length → video duration" above). If too long, offer to split. (Skip for Nano Banana image-only requests.)
4. **Nano Banana image model:** For `POST /V2/images/generate`, confirm Nano Banana 2 (default) vs Nano Banana Pro (`nano-banana`) per the section above. Skip if not an image call.
5. **Ask for generation count:** Ask how many variations the user wants for this prompt. Default to 1.
6. **Show credit cost and get confirmation:** Calculate total credits using the cost table above. Present the breakdown to the user. **Do NOT proceed until they confirm.**
7. **Check `references/` folder:** Before composing the prompt, check the repo-root `references/` folder for relevant images: `references/influencers/` for person recreation, `references/products/` for product showcase, `references/aesthetics/` for style/mood. If the user hasn't provided an image but a relevant one exists in `references/`, offer to use it. Auto-upscale any reference image if needed. For Veo 3.1, determine whether to use `startFrame` or `referenceImages` (see section above — default to `startFrame` for person photos).
8. Compose JSON per OpenAPI / [reference.md](reference.md). Include `projectId` when the DTO supports it. Set `duration` based on script length for models that require it. For Nano Banana images, use `POST /V2/images/generate` (uppercase V2) with `model` set per the Nano Banana section (`nano-banana-2` unless the user chose Pro).
9. `POST` the correct endpoint **N times** (once per requested variation) with the same payload. Fire in parallel where possible.
10. **Poll:** `GET /v1/videos/{videoId}` for video IDs; `GET /v1/assets/{id}` for asset IDs (including Nano Banana images) until `status` is `generated` or `failed` (see [reference.md](reference.md)). Poll all asset IDs concurrently.
11. **Generated image QA:** For each **still image** produced in this turn (e.g. `POST /V2/images/generate`), follow [Generated image QA](#generated-image-qa-mandatory): inspect the image; if defective, regenerate with a refined prompt until pass or **2 retries** are exhausted. Skip this step for video-only outputs with no still to review.
12. **Assign ALL assets to session project:** After generation (and QA retries), check each asset's `projects` array. If it does not include the session `projectId`, call `POST /v1/assets/add-to-project`. This applies to **every** generated asset — including **failed QA attempts** and **intermediate assets** like Nano Banana stills used as starting frames for subsequent video generations. All assets from the session must end up in the same dated project folder.
13. **Present results:** Return **watch URLs**, image URLs, or download URLs for **QA-passed** stills (or the best attempt after max retries, with a clear note). If multiple variations, present as a numbered list for comparison. Explain `failed` with moderation/validation hints if `422` occurred. For Nano Banana images used as starting frames, show the image and **wait for user approval** before proceeding to video generation.
14. **Stitch if split:** If the script was split into segments, offer to stitch the final videos together with `ffmpeg` and provide both the stitched file and individual segments.

## Errors (user-facing)

- **401/403:** Fix API key / workspace access (setup flow above).
- **404:** Wrong UUID; re-fetch lists.
- **422:** Validation or moderation — tighten prompt, remove disallowed content, check required enums (aspect ratio, duration).
- **500:** Retry later; if repeated, stop and report.

## Supporting files

- [reference.md](reference.md) — endpoints, auth detail, polling, model mapping notes.
- [prompting/guide.md](prompting/guide.md) — marketing brief → API.
- [prompting/prompt-library/influencer-recreation.md](prompting/prompt-library/influencer-recreation.md) — analyze a reference photo and recreate the influencer.
- [prompting/prompt-library/ugc-selfie-style.md](prompting/prompt-library/ugc-selfie-style.md) — cross-model UGC guide (iPhone aesthetic, negative prompts, per-model formulas).
- [prompting/prompt-library/product-showcase.md](prompting/prompt-library/product-showcase.md) — product-in-hand video workflow (Nano Banana image → approve → video).
- [prompting/prompt-library/nano-banana.md](prompting/prompt-library/nano-banana.md) — Nano Banana image prompting guide.
- [prompting/prompt-library/character-sheet.md](prompting/prompt-library/character-sheet.md) — generate a 10-image character sheet for a new AI influencer from a text description.
- [prompting/prompt-library/ugc-product-selfie.md](prompting/prompt-library/ugc-product-selfie.md) — UGC selfie-style still image: character + product + style references.
- [prompting/prompt-library/static-ad.md](prompting/prompt-library/static-ad.md) — static ad images (product heroes, lifestyle, flat lays, banners, abstract brand visuals) without people.
- [prompting/prompt-library/ad-remix.md](prompting/prompt-library/ad-remix.md) — recreate existing ads with new branding, product, or colors.
- [prompting/prompt-library/image-quality-playbook.md](prompting/prompt-library/image-quality-playbook.md) — maximizing image quality, model comparison workflow, workarounds for common AI shortfalls, post-production checklist.
- [prompting/brand-voice-starter.md](prompting/brand-voice-starter.md) — template to copy into `MASTER_CONTEXT.md`.
- `references/briefs/BRIEF_TEMPLATE.md` — creative brief template; copy, fill in, drop in `references/briefs/` for the agent to read.
