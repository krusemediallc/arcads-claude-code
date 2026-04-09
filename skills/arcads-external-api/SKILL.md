---
name: arcads-external-api
description: >-
  Creates and retrieves AI video and image-related assets via the Arcads external API (Seedance 2.0, Sora 2, Veo 3.1, Kling, Grok Video, Nano Banana, b-roll, scene, script/actor flows). Loads prompts from the bundled prompting guide and model library, respects HTTP Basic auth from ARCADS_API_KEY, and polls assets/videos until ready. Use when the user mentions Arcads, external-api.arcads.ai, Seedance, Sora2, Veo, Kling, Nano Banana, b-roll, UGC scripts, or generating marketing creative through Arcads.
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

All video models use `POST /v2/videos/generate` with the appropriate `model` value (see [reference.md](reference.md) for the full `CreateVideoDto` schema).

| User goal | Start here | Prompt library |
|-----------|------------|----------------|
| **Seedance 2.0 UGC video** — selfie-style product review / testimonial | `POST /v2/videos/generate` with `model: "seedance-2.0"` | [seedance-2.md](prompting/prompt-library/seedance-2.md) (platform guide) + [seedance-2-ugc.md](prompting/prompt-library/seedance-2-ugc.md) (9-layer UGC formula) |
| **Seedance 2.0 premium product reveal** — dark-void, no person, text narrative | `POST /v2/videos/generate` with `model: "seedance-2.0"` | [seedance-2.md](prompting/prompt-library/seedance-2.md) + [seedance-2-premium-reveal.md](prompting/prompt-library/seedance-2-premium-reveal.md) |
| **Seedance 2.0 product hero** — elemental effects, no person, splash/mist | `POST /v2/videos/generate` with `model: "seedance-2.0"` | [seedance-2.md](prompting/prompt-library/seedance-2.md) + [seedance-2-product-hero.md](prompting/prompt-library/seedance-2-product-hero.md) |
| **Seedance 2.0 studio lookbook** — polished, voiceover, multi-look | `POST /v2/videos/generate` with `model: "seedance-2.0"` | [seedance-2.md](prompting/prompt-library/seedance-2.md) + [seedance-2-studio-lookbook.md](prompting/prompt-library/seedance-2-studio-lookbook.md) |
| **Seedance 2.0 feature walkthrough** — fast-paced feature demo | `POST /v2/videos/generate` with `model: "seedance-2.0"` | [seedance-2.md](prompting/prompt-library/seedance-2.md) + [seedance-2-feature-walkthrough.md](prompting/prompt-library/seedance-2-feature-walkthrough.md) |
| **Reverse-engineer a video style** into a reusable Seedance 2.0 template | Follow the analyze-video skill | [prompting/analyze-video/SKILL.md](prompting/analyze-video/SKILL.md) |
| Raw **Sora 2** video from text (plus product) | `POST /v2/videos/generate` with `model: "sora2"` | [prompt-library/sora-2.md](prompting/prompt-library/sora-2.md) |
| **Sora** remix of an existing asset | `POST /v1/sora2/remix/video` | [sora-2.md](prompting/prompt-library/sora-2.md) |
| **Veo 3.1** video | `POST /v2/videos/generate` with `model: "veo31"` | [prompt-library/veo-3-1.md](prompting/prompt-library/veo-3-1.md) |
| **Kling 3.0** video | `POST /v2/videos/generate` with `model: "kling-3.0"` | [kling-3.md](prompting/prompt-library/kling-3.md) |
| **Grok Video** | `POST /v2/videos/generate` with `model: "grok-video"` | See [reference.md](reference.md) for fields |
| **Nano Banana still image** (standalone or as starting frame for video) | `POST /v2/images/generate` with `"model":"nano-banana-2"` by default; optional `"model":"nano-banana"` (Nano Banana Pro) | [nano-banana.md](prompting/prompt-library/nano-banana.md) |
| **B-roll** clip (product-level) | `POST /v1/b-roll` | [kling-3.md](prompting/prompt-library/kling-3.md) or [nano-banana.md](prompting/prompt-library/nano-banana.md) for craft; see [reference.md](reference.md) for Kling/Nano routing notes |
| **Scene** generation | `POST /v1/scene` | Same as b-roll row |
| **Recreate an influencer** from a reference photo | **Two-step:** (1) `POST /v2/images/generate` with `refImageAsBase64` to generate a **still image** via Nano Banana, get user approval; (2) upload approved still → `POST /v2/videos/generate` with `model: "veo31"` and `startFrame` for video. **Never skip the approval step.** | [prompt-library/influencer-recreation.md](prompting/prompt-library/influencer-recreation.md) |
| **Product showcase** — AI person holds/uses a product and talks about it | **Two-step:** (1) `POST /v2/images/generate` with product `refImageAsBase64`; (2) user approves still; (3) start-frame → video via `POST /v2/videos/generate`. | [prompt-library/product-showcase.md](prompting/prompt-library/product-showcase.md) |
| **UGC / selfie-style** (authentic reels, cross-model) | Any video model via `POST /v2/videos/generate` | [prompt-library/ugc-selfie-style.md](prompting/prompt-library/ugc-selfie-style.md) — cross-model UGC guide. For Seedance 2.0 specifically, use [seedance-2-ugc.md](prompting/prompt-library/seedance-2-ugc.md) instead. |
| **Create a new AI influencer** from text (character sheet) | **Two-pass:** (1) hero portrait via `POST /v2/images/generate`, get approval; (2) 9 angles with hero as `referenceImages`. Save to `references/influencers/`. | [prompt-library/character-sheet.md](prompting/prompt-library/character-sheet.md) |
| **UGC product selfie** — AI influencer holding a product | Combine character hero + product photo + style references as `referenceImages`. | [prompt-library/ugc-product-selfie.md](prompting/prompt-library/ugc-product-selfie.md) |
| **Talking avatar / script** (actors, voices) | `POST /v1/scripts`, `POST /v1/scripts/{id}/generate` | [prompting/guide.md](prompting/guide.md) |
| **OmniHuman** | `POST /v1/omnihuman` | [prompting/guide.md](prompting/guide.md) |
| **Audio-driven** | `POST /v1/audio-driven` | [prompting/guide.md](prompting/guide.md) |

Prefer the **shortest** path: if the user only needs a single model, do not create scripts unless they ask for actors/lip-sync workflows.

## Creative layer

- **MANDATORY:** Before composing any prompt for the API, **read the relevant `prompting/prompt-library/*.md` file** for the chosen model/workflow. Do NOT skip this step — every prompt must align with the vendor guide's formula and best practices.
- Build **one** clear prompt paragraph; avoid keyword soup.
- For Seedance 2.0 / Sora2 / Veo3.1 / Kling / Grok Video / Nano Banana, align with the **official vendor guides** linked in each `prompting/prompt-library/*.md` file (do not paste full vendor docs into chat—summarize checks).
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

Before firing **any** generation calls, calculate and present the total credit cost to the user as an **estimate**. **Do not generate until the user confirms.**

> **ALWAYS label credit totals as estimates and tell the user to confirm the exact cost in the Arcads platform before generating if precision matters.** The Arcads API does not expose billing endpoints; pricing varies by duration, resolution, and reference inputs.

### Cost data sources (in priority order)

1. **`logs/arcads-api.jsonl`** — historical record of actual `creditsCharged` values for every previous call. **Read this first.** Grep for entries with the same `model` and similar config (same `duration`, `resolution`, `referenceImagesCount`, `audioEnabled`) and use the recorded `creditsCharged` as the estimate. This is the most accurate source.
2. **`MASTER_CONTEXT.md` → Credit costs** — user-provided pricing rules (e.g. "Seedance 2.0 image-to-video ≈ 0.06/sec"). Use when no matching log entry exists.
3. **Ask the user** — if neither source has data for the config, ask the user and write the answer into `MASTER_CONTEXT.md`.

Never invent numbers. Always cite the source of the estimate ("based on log entry from YYYY-MM-DD" or "from MASTER_CONTEXT.md rate table").

### How to calculate

```
total_credits ≈ sum(credits_per_model × variations_requested) for each model
```

### Example output to user

```
Estimated credit cost:
  Seedance 2.0 (15s i2v) × 1 = ~0.9 credits   (from logs/arcads-api.jsonl 2026-04-09)
  Veo 3.1                × 2 = ~8 credits     (from MASTER_CONTEXT.md)
  ─────────────────────────────
  Estimated total: ~8.9 credits

⚠️ Estimate only — confirm exact cost in the Arcads platform before proceeding.
Proceed? (yes/no)
```

Always wait for confirmation before firing. If the user has a credit balance visible in `MASTER_CONTEXT.md`, warn them if the total would exceed it. If neither the logs nor `MASTER_CONTEXT.md` have data for the config, ask the user before the first generation and save the answer.

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

### MANDATORY — dialogue confirmation gate

Before generating **any** video that contains spoken dialogue, the agent MUST:

1. **Extract the dialogue lines from the full prompt** and show them to the user in a dedicated block, separate from the visual/cinematography description.
2. **Present them as a clean, numbered list** with beat labels (hook / show / demo / verdict, or similar) and any silent beats clearly marked as `(silent beat — no dialogue)`.
3. **Read the dialogue out loud in your head at a natural pace, time it against the target duration, and flag the total spoken word count** plus whether it comfortably fits.
4. **Explicitly ask for dialogue approval** before moving on — e.g. "Approve this dialogue? (yes / edit / rewrite)". **Never assume approval from earlier confirmations** (tone, template, credit cost). Dialogue approval is its own gate.
5. Only after the user types `yes` (or equivalent) may you proceed to the credit cost confirmation and then generation. If the user says "edit" or proposes changes, revise and re-present the numbered dialogue block until they approve.

**Presentation format (use this exact structure):**

```
📝 Dialogue script (please confirm before I generate)

  1. [HOOK]   "Bro. BRO. Look what just showed up."
  2. [SHOW]   "The PAID SOCIAL stripe? Insane. Like, who greenlit this?"
  3. [DEMO]   (silent beat — thumb brushing the suede, small nod)
  4. [VERDICT] "I'm literally wearing these to the gym tomorrow. You guys have to see these in person."

Total spoken words: ~28  |  Target duration: 15s  |  Fits at natural pace: ✅

Approve this dialogue? (yes / edit / rewrite)
```

This gate applies to **Seedance 2.0**, **Veo 3.1**, **Sora 2**, and **Scene** — any flow where the model speaks. Skip for silent flows (B-roll, pure product-hero, premium-reveal with no voiceover, Nano Banana images).

### Model-specific notes

- For **Seedance 2.0**, **Veo 3.1**, and **Sora 2**: embed the dialogue in the `prompt` field using a `Dialogue: "..."` or `She speaks: "..."` pattern (these models generate speech from the text prompt).
- For **Seedance 2.0** specifically: before generating, **always ask the user** whether to enable audio output (`audioEnabled: true`). Also ask whether they want to supply `referenceAudios` (e.g. background music or a specific voice clip). Upload audio files via presigned URL if provided.
- For **Scene** (`CreateSceneDto`): use the dedicated `script` field for dialogue and `prompt` for visuals.
- For **B-roll**: no speech — b-roll is silent/ambient by nature. If the user wants speech, redirect to Seedance 2.0, Veo 3.1, Sora 2, or Scene.
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

### Seedance 2.0 — duration: 4–15 seconds (continuous)

Seedance 2.0 supports any integer from 4 to 15. Use ~2.5 words/second, round up to the nearest second.

| Script length | Duration |
|---------------|----------|
| 1–8 words | 4–5s |
| 9–15 words | 6–8s |
| 16–25 words | 9–12s |
| 26–35 words | 13–15s |
| **36+ words** | **Too long** — offer to split into multiple clips |

For no-dialogue styles (product hero, premium reveal), default to **15s**.

**Resolution:** Default to `720p`. Only use `480p` if the user asks for a faster/cheaper test generation.

**Aspect ratio:** `9:16` (vertical, default for UGC/social) or `16:9` (landscape). No `1:1` support.

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

## Execution checklist (agent)

1. **Session folder:** Ensure today's dated folder + project exist (see above).
2. Resolve `productId` (and `projectId` from session folder): `GET /v1/products` or ask the user.
3. **Ask for script/dialogue:** If the output is a video with a person speaking, ask the user for the exact words. Count words to auto-select duration (see "Script length → video duration" above). If too long, offer to split. (Skip for Nano Banana image-only requests.)
   - **MANDATORY dialogue confirmation gate (before credit cost / before generation):** Extract the dialogue lines from the drafted prompt and present them to the user as a dedicated, numbered block separate from the visual description. Follow the format in [Script and dialogue → MANDATORY dialogue confirmation gate](#mandatory--dialogue-confirmation-gate). Wait for explicit `yes` before moving on. This gate is separate from the credit cost confirmation — both must be satisfied.
4. **Nano Banana image model:** For `POST /V2/images/generate`, confirm Nano Banana 2 (default) vs Nano Banana Pro (`nano-banana`) per the section above. Skip if not an image call.
5. **Ask for generation count:** Ask how many variations the user wants for this prompt. Default to 1.
6. **Show credit cost and get confirmation:** Calculate total credits using the cost table above. Present the breakdown to the user. **Do NOT proceed until they confirm.**
7. **Check `references/` folder:** Before composing the prompt, check the repo-root `references/` folder for relevant images: `references/influencers/` for person recreation, `references/products/` for product showcase, `references/aesthetics/` for style/mood. If the user hasn't provided an image but a relevant one exists in `references/`, offer to use it. Auto-upscale any reference image if needed. For Veo 3.1, determine whether to use `startFrame` or `referenceImages` (see section above — default to `startFrame` for person photos).
8. Compose JSON per OpenAPI / [reference.md](reference.md). **Primary video endpoint:** `POST /v2/videos/generate` with the appropriate `model` value (see `CreateVideoDto` in reference.md). Include `projectId` when the DTO supports it. Set `duration` based on script length for models that require it. For Nano Banana images, use `POST /v2/images/generate` with `model` set per the Nano Banana section (`nano-banana-2` unless the user chose Pro).
   - **Seedance 2.0 extras:** Set `resolution` to `720p` (default). Set `aspectRatio` to `9:16` (UGC/social) or `16:9` (landscape). Include `audioEnabled` per user confirmation. If the user provided reference images, upload via presigned URL and pass `filePath` strings in `referenceImages` (max 3). Same for `referenceVideos` and `referenceAudios` if provided. Keep `@(img1)` tokens in the prompt text alongside the `referenceImages` array.
   - **⚠️ Seedance 2.0 mutually exclusive input modes (confirmed 2026-04-09):** `referenceVideos` and `referenceImages` **cannot be combined in the same request** — the API returns `HTTP 500 UNKNOWN_ERROR`. Pick one: image-to-video OR video-to-video. `referenceAudios` may be combined with either. See `reference.md` for details.
9. `POST` the correct endpoint **N times** (once per requested variation) with the same payload. Fire in parallel where possible. **Immediately after the POST succeeds, append a log entry to `logs/arcads-api.jsonl`** with the request config (model, duration, resolution, aspectRatio, audioEnabled, reference counts, promptWordCount, assetId). Do NOT log the full prompt text, API keys, or Authorization headers.
10. **Poll:** `GET /v1/videos/{videoId}` for video IDs; `GET /v1/assets/{id}` for asset IDs (including Nano Banana images) until `status` is `generated` or `failed` (see [reference.md](reference.md)). Poll all asset IDs concurrently. **When polling completes, update the log entry** with `response.status`, `response.creditsCharged`, `response.generationTimeSec`, `response.videoUrl`, `response.thumbnailUrl`, and `response.error` (if failed). See `logs/README.md` for the schema.
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

- [reference.md](reference.md) — endpoints, auth detail, polling, model mapping notes, `CreateVideoDto` schema.
- [prompting/guide.md](prompting/guide.md) — marketing brief → API.
- **Seedance 2.0:**
  - [prompting/prompt-library/seedance-2.md](prompting/prompt-library/seedance-2.md) — main Seedance 2.0 model guide (platform rules, API parameters, style template directory).
  - [prompting/prompt-library/seedance-2-ugc.md](prompting/prompt-library/seedance-2-ugc.md) — 9-layer UGC selfie-style formula for Seedance 2.0.
  - [prompting/prompt-library/seedance-2-premium-reveal.md](prompting/prompt-library/seedance-2-premium-reveal.md) — dark-void premium product reveal (no person).
  - [prompting/prompt-library/seedance-2-product-hero.md](prompting/prompt-library/seedance-2-product-hero.md) — elemental product hero with splash/effects (no person).
  - [prompting/prompt-library/seedance-2-studio-lookbook.md](prompting/prompt-library/seedance-2-studio-lookbook.md) — studio lookbook with voiceover.
  - [prompting/prompt-library/seedance-2-feature-walkthrough.md](prompting/prompt-library/seedance-2-feature-walkthrough.md) — fast-paced feature walkthrough demo.
  - [prompting/analyze-video/SKILL.md](prompting/analyze-video/SKILL.md) — reverse-engineer a reference video into a reusable Seedance 2.0 prompting template.
- **Other models:**
  - [prompting/prompt-library/influencer-recreation.md](prompting/prompt-library/influencer-recreation.md) — analyze a reference photo and recreate the influencer.
  - [prompting/prompt-library/ugc-selfie-style.md](prompting/prompt-library/ugc-selfie-style.md) — cross-model UGC guide (iPhone aesthetic, negative prompts, per-model formulas).
  - [prompting/prompt-library/product-showcase.md](prompting/prompt-library/product-showcase.md) — product-in-hand video workflow (Nano Banana image → approve → video).
  - [prompting/prompt-library/nano-banana.md](prompting/prompt-library/nano-banana.md) — Nano Banana image prompting guide.
  - [prompting/prompt-library/character-sheet.md](prompting/prompt-library/character-sheet.md) — generate a 10-image character sheet for a new AI influencer from a text description.
  - [prompting/prompt-library/ugc-product-selfie.md](prompting/prompt-library/ugc-product-selfie.md) — UGC selfie-style still image: character + product + style references.
- [prompting/brand-voice-starter.md](prompting/brand-voice-starter.md) — template to copy into `MASTER_CONTEXT.md`.
