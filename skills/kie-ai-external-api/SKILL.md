---
name: kie-ai-external-api
description: >-
  Creates and retrieves AI video and image assets via the kie.ai API (Seedance 2.0, Sora 2, Sora 2 Pro, Veo 3 / 3.1, Kling 2.6/3.0, Nano Banana 2 / Pro). Loads prompts from the bundled prompting guide and per-model prompt library, uses Bearer-token auth from KIE_API_KEY, and polls task status until ready. Use when the user mentions kie.ai, api.kie.ai, Seedance, Sora2, Veo, Kling, Nano Banana, or generating AI marketing creative through kie.ai.
---

# kie.ai external API

## Configuration

- **Base URL:** `https://api.kie.ai` (or `KIE_BASE_URL`).
- **Auth:** HTTP Bearer — send `Authorization: Bearer $KIE_API_KEY` on every call. Create keys at [kie.ai/api-key](https://kie.ai/api-key).
- **Never** print API keys, commit `.env`, or paste keys into `MASTER_CONTEXT.md`.

### If the key is missing or the API returns 401

1. **Editor-first (default):** Ensure `.env` exists (copy from `.env.example` in the repo root). Ask the user to paste `KIE_API_KEY` **only inside** `.env` and save. Do not ask them to paste the key in chat unless they insist.
2. **Chat-assisted:** If they paste the key in chat, write `.env` for them, confirm "saved to `.env`" **without repeating the key**, and remind them that chat history may retain secrets — rotate the key at [kie.ai/api-key](https://kie.ai/api-key) if the chat could be shared.

Before the first call, confirm `.gitignore` excludes `.env`.

## Read order

1. Repo root **`MASTER_CONTEXT.md`** when present (brand voice, decisions, quirks).
2. This skill's **[reference.md](reference.md)** for endpoints, request bodies, polling, and per-model input fields.
3. **[prompting/guide.md](prompting/guide.md)** then the right **`prompting/prompt-library/`** file for the model.

## The shape of the kie.ai API

kie.ai exposes two endpoint families:

1. **Unified task endpoint** — `POST /api/v1/jobs/createTask` with `{"model": "<slug>", "input": {...}}`. Used for Seedance, Sora 2, Kling 3.0, Nano Banana, and most marketplace models. Poll via the unified task-details endpoint. See [reference.md](reference.md) for the exact slug per model.
2. **Veo legacy endpoint** — `POST /api/v1/veo/generate` (different body shape). Poll via `GET /api/v1/veo/record-info?taskId=...`.

In both families, a successful create returns `{ taskId, code, msg }`. Poll until `successFlag` transitions from `0` (generating) to `1` (success) or `2|3` (failure). The final asset URLs are on `data.response.resultUrls[]`.

## Decision tree: which flow?

| User goal | Endpoint + model slug | Prompt library |
|-----------|-----------------------|----------------|
| **Seedance 2.0 UGC video** — selfie-style product review / testimonial | `POST /api/v1/jobs/createTask` with `"model": "bytedance/seedance-2"` | [seedance-2.md](prompting/prompt-library/seedance-2.md) + [seedance-2-ugc.md](prompting/prompt-library/seedance-2-ugc.md) |
| **Seedance 2.0 premium product reveal** — dark-void, no person | `POST /api/v1/jobs/createTask` with `"model": "bytedance/seedance-2"` | [seedance-2.md](prompting/prompt-library/seedance-2.md) + [seedance-2-premium-reveal.md](prompting/prompt-library/seedance-2-premium-reveal.md) |
| **Seedance 2.0 product hero** — elemental effects, no person | `POST /api/v1/jobs/createTask` with `"model": "bytedance/seedance-2"` | [seedance-2.md](prompting/prompt-library/seedance-2.md) + [seedance-2-product-hero.md](prompting/prompt-library/seedance-2-product-hero.md) |
| **Seedance 2.0 studio lookbook** — polished, voiceover, multi-look | `POST /api/v1/jobs/createTask` with `"model": "bytedance/seedance-2"` | [seedance-2.md](prompting/prompt-library/seedance-2.md) + [seedance-2-studio-lookbook.md](prompting/prompt-library/seedance-2-studio-lookbook.md) |
| **Seedance 2.0 feature walkthrough** — fast-paced feature demo | `POST /api/v1/jobs/createTask` with `"model": "bytedance/seedance-2"` | [seedance-2.md](prompting/prompt-library/seedance-2.md) + [seedance-2-feature-walkthrough.md](prompting/prompt-library/seedance-2-feature-walkthrough.md) |
| **Reverse-engineer a video style** into a reusable Seedance 2.0 template | Follow the analyze-video skill | [prompting/analyze-video/SKILL.md](prompting/analyze-video/SKILL.md) |
| **Clone/replicate an existing video ad** for a different product | Follow the clone-ad skill | [prompting/clone-ad/SKILL.md](prompting/clone-ad/SKILL.md) |
| Raw **Sora 2** video from text | `POST /api/v1/jobs/createTask` with `"model": "sora-2-text-to-video"` | [sora-2.md](prompting/prompt-library/sora-2.md) |
| **Sora 2** image-to-video (product photo as starting context) | `POST /api/v1/jobs/createTask` with `"model": "sora-2-image-to-video"` | [sora-2.md](prompting/prompt-library/sora-2.md) |
| **Veo 3.1** video | `POST /api/v1/veo/generate` with `"model": "veo3"` (or `veo3_fast`) | [veo-3-1.md](prompting/prompt-library/veo-3-1.md) |
| **Kling 3.0** video | `POST /api/v1/jobs/createTask` with `"model": "kling-3.0/video"` | [kling-3.md](prompting/prompt-library/kling-3.md) |
| **Nano Banana 2 still image** (standalone or as starting frame for video) | `POST /api/v1/jobs/createTask` with `"model": "nano-banana-2"` (default) or `"nano-banana-pro"` for Pro | [nano-banana.md](prompting/prompt-library/nano-banana.md) |
| **Recreate an influencer** from a reference photo | **Two-step:** (1) `POST /api/v1/jobs/createTask` with `nano-banana-2` and the reference as `image_input[]` to generate a **still image** via Nano Banana, get user approval; (2) use approved still's public URL as `first_frame_url` (Seedance) / `imageUrls[]` (Veo) in the video call. **Never skip the approval step.** | [influencer-recreation.md](prompting/prompt-library/influencer-recreation.md) |
| **Product showcase** — AI person holds/uses a product and talks about it | **Two-step:** (1) Nano Banana still of person with product; (2) user approves; (3) still URL → video via Seedance 2.0 (`first_frame_url`) or Veo 3.1 (`imageUrls[0]`). | [product-showcase.md](prompting/prompt-library/product-showcase.md) |
| **UGC / selfie-style** (authentic reels, cross-model) | Seedance 2.0 or Sora 2 via `createTask` | [ugc-selfie-style.md](prompting/prompt-library/ugc-selfie-style.md) — cross-model UGC guide. For Seedance 2.0 specifically, use [seedance-2-ugc.md](prompting/prompt-library/seedance-2-ugc.md). |
| **Create a new AI influencer** from text (character sheet) | **Two-pass:** (1) hero portrait via `nano-banana-2`, get approval; (2) 9 angles with hero as `image_input[]`. Save to `references/influencers/`. | [character-sheet.md](prompting/prompt-library/character-sheet.md) |
| **UGC product selfie** — AI influencer holding a product | Combine character hero + product photo + style references as `image_input[]`. | [ugc-product-selfie.md](prompting/prompt-library/ugc-product-selfie.md) |

Prefer the **shortest** path: if the user only needs a single model, generate directly instead of adding extra steps.

## Creative layer

- **MANDATORY:** Before composing any prompt for the API, **read the relevant `prompting/prompt-library/*.md` file** for the chosen model/workflow. Every prompt must align with the vendor guide's formula and best practices.
- Build **one** clear prompt paragraph; avoid keyword soup.
- For Seedance 2.0 / Sora 2 / Veo 3.1 / Kling / Nano Banana, align with the **official vendor guides** linked in each `prompting/prompt-library/*.md` file (do not paste full vendor docs into chat — summarize checks).
- Merge slot values from the user and from **`MASTER_CONTEXT.md`** when it conflicts with defaults.

## Reference images: hosting and public URLs

kie.ai requires reference images (`first_frame_url`, `last_frame_url`, `reference_image_urls[]`, `image_input[]`, `imageUrls[]` for Veo) to be **publicly accessible HTTPS URLs** — unlike Arcads' presigned-S3 flow. The user hosts the image, you pass the URL.

**When the user provides a local file path:**

1. Tell them the image needs to be hosted at a public HTTPS URL before kie.ai can see it, and offer these options:
   - **Imgur** (fastest, no account for single images): upload at [imgur.com](https://imgur.com/upload), copy the direct image link (`https://i.imgur.com/xxx.jpg`).
   - **Supabase / Cloudflare R2 / AWS S3 / Backblaze B2** (own your hosting): upload once, paste the object's public URL.
   - **GitHub raw** (small images only, ≤100 MB): commit to a public repo, use `https://raw.githubusercontent.com/...`.
2. **Do NOT ever** suggest pasting the image as base64 in chat — kie.ai doesn't accept base64 anywhere in this repo's supported flows.
3. Once the user gives you a URL, sanity-check it resolves (HEAD request; 200 OK and `Content-Type: image/*`). If it 403s or redirects to HTML, the URL is wrong (common Imgur gotcha: use `i.imgur.com/*.jpg`, not `imgur.com/*`).
4. Validate the URL is **HTTPS** (not HTTP) and on the **public internet** (not `localhost`, `127.0.0.1`, or a private IP).

**Generated assets** (returned by kie.ai in `resultUrls[]`) are already public URLs — you can pipe them straight into the next call as `first_frame_url` or `imageUrls[]` without re-hosting.

**Image minimum size:** kie.ai accepts images down to ~512 px on the longest side. If the user's reference is smaller, warn them; if they want, offer to upscale locally (`sips -Z 1080 img.jpg` on macOS) before they re-host.

## Credit cost estimation (MANDATORY — show before generating)

Before firing **any** generation calls, calculate and present the total credit cost to the user as an **estimate**. **Do not generate until the user confirms.**

> **ALWAYS label credit totals as estimates and tell the user to confirm the exact cost in their kie.ai account before generating if precision matters.** kie.ai does not return `creditsCharged` on every task — you price from a static table.

### Cost data sources (in priority order)

1. **`MASTER_CONTEXT.md` → Credit costs** — user-provided pricing rules (e.g. "Seedance 2.0 ≈ $0.06/sec"). This is the primary source.
2. **`logs/kie-api.jsonl`** — historical record of what we've fired. Kie.ai doesn't return a per-call credit figure, but historical config (model, duration, resolution) helps cross-check the rate table. Use this as a secondary sanity check.
3. **Ask the user** — if neither source has a rate for the model, ask the user (or point them at [kie.ai pricing](https://kie.ai/pricing)) and write the answer into `MASTER_CONTEXT.md`.

Never invent numbers. Always cite the source of the estimate ("from MASTER_CONTEXT.md rate table" or "per kie.ai pricing page, confirmed by user on YYYY-MM-DD").

### How to calculate

```
total_credits ≈ sum(credits_per_model × duration_multiplier × variations_requested) for each model
```

### Example output to user

```
Estimated cost:
  Seedance 2.0 (15s i2v) × 1 = ~$0.90  (from MASTER_CONTEXT.md: $0.06/sec)
  Veo 3.1 (auto ~8s)     × 2 = ~$2.00  (from MASTER_CONTEXT.md: $1.00/gen)
  ───────────────────────────────
  Estimated total: ~$2.90

⚠️ Estimate only — confirm exact cost at kie.ai/pricing before proceeding.
Proceed? (yes/no)
```

Always wait for confirmation before firing. If the user has a credit/dollar balance visible in `MASTER_CONTEXT.md`, warn them if the total would exceed it.

**Exception — QA-fix retries (still images only):** After the user has confirmed the initial batch, **automatic regeneration to fix visible defects** (see [Generated image QA](#generated-image-qa-mandatory) below) does **not** require asking again for cost confirmation. Each retry is still billed — note the extra cost when summarizing the session.

## Generation count: multiple variations per prompt

Before firing any generation call, **ask the user how many variations** they want for this prompt. Default is 1 if they don't specify.

When the count is greater than 1, send **N separate `createTask` calls** with the identical payload. kie.ai has no batch parameter on the unified endpoint. Fire them in parallel where possible, then poll all `taskId`s concurrently.

Present results as a numbered list so the user can compare and pick favorites.

## Nano Banana image: model choice (`nano-banana-2` vs `nano-banana-pro`)

For image generation via `POST /api/v1/jobs/createTask`:

- **Default:** `"model": "nano-banana-2"` (Nano Banana 2).
- **Optional:** `"model": "nano-banana-pro"` when the user asks for **Nano Banana Pro**.

Before the first Nano Banana image call in a workflow, ask: *"Use default Nano Banana 2, or Nano Banana Pro?"* If they have no preference, use `nano-banana-2`. Include the chosen `model` in the credit estimate (separate rows in `MASTER_CONTEXT.md` if pricing differs).

## Script and dialogue

For any video that features a person speaking, **ask the user for the script** (the exact words the AI person should say). This is separate from the visual prompt — it's the dialogue.

### MANDATORY — dialogue confirmation gate

Before generating **any** video that contains spoken dialogue, the agent MUST:

1. **Extract the dialogue lines from the full prompt** and show them to the user in a dedicated block, separate from the visual/cinematography description.
2. **Present them as a clean, numbered list** with beat labels (hook / show / demo / verdict, or similar) and any silent beats clearly marked as `(silent beat — no dialogue)`.
3. **Read the dialogue out loud in your head at a natural pace, time it against the target duration, and flag the total spoken word count** plus whether it comfortably fits.
4. **Explicitly ask for dialogue approval** before moving on — e.g. "Approve this dialogue? (yes / edit / rewrite)". **Never assume approval from earlier confirmations** (tone, template, cost). Dialogue approval is its own gate.
5. Only after the user types `yes` (or equivalent) may you proceed to the cost confirmation and then generation. If the user says "edit" or proposes changes, revise and re-present the numbered dialogue block until they approve.

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

This gate applies to **Seedance 2.0**, **Veo 3.1**, and **Sora 2** — any flow where the model speaks. Skip for silent flows (Kling 3.0 has no native speech; Nano Banana images).

### Model-specific notes

- For **Seedance 2.0**, **Veo 3.1**, and **Sora 2**: embed the dialogue in the `prompt` field using a `Dialogue: "..."` or `She speaks: "..."` pattern (these models generate speech from the text prompt).
- For **Seedance 2.0** specifically: before generating, **always ask the user** whether to enable audio output (kie.ai Seedance exposes an `audio` / `audioEnabled` flag — see reference.md). Also ask whether they want to supply `reference_audio_urls[]` (e.g. a voice clip). The user hosts the audio file at a public HTTPS URL (same rules as images).
- For **Kling 3.0**: no native speech output — silent only. If the user wants speech, redirect to Seedance 2.0, Veo 3.1, or Sora 2.
- For **Nano Banana images**: no speech — these are still images. Speech is handled in the subsequent video generation step.

## Script length → video duration (auto-select)

Use the script's word count to automatically pick the best duration. Average speaking pace: **~2.5 words per second** (~150 WPM). Round **up** to the next available duration to give breathing room.

### Sora 2 — duration: `[4, 8, 12, 16, 20]` seconds

| Script length | Duration |
|---------------|----------|
| 1–8 words | 4s |
| 9–18 words | 8s |
| 19–28 words | 12s |
| 29–38 words | 16s |
| 39–48 words | 20s |
| **49+ words** | **Too long** — offer to split (see below) |

### Veo 3.1 — duration enum via kie.ai: `[8]` (most common)

Kie.ai's Veo wrapper exposes limited duration control — Veo 3.1 auto-determines length (~8s). If the script exceeds ~20 words, warn the user Veo may truncate dialogue and offer to split or switch to Sora 2.

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

**Aspect ratio:** `9:16` (vertical, default for UGC/social) or `16:9` (landscape).

### Kling 3.0 — duration: `[5, 10]` seconds (typical)

Kling is silent. For timed clips:

| Script length | Duration |
|---------------|----------|
| 1–12 words | 5s |
| 13–24 words | 10s |
| **25+ words** | **Too long** — redirect to Sora 2 / Veo 3.1 for speech |

## Splitting long scripts into multiple videos

If the script exceeds the maximum duration for the chosen model:

1. **Tell the user** the script is too long for a single video and show the word/duration math.
2. **Offer two options:**
   - **Split into segments** — the agent breaks the script at natural sentence boundaries into chunks that each fit within the model's max duration. Each chunk becomes a separate `createTask` call.
   - **Switch models** — if they're on Kling (10s max), suggest Sora 2 (up to 20s).
3. If the user chooses to split, generate each segment as a separate video (respecting the generation count — if they asked for 3 variations, generate 3 of *each* segment).
4. **Offer to stitch** the final segments together using `ffmpeg`:
   - Download all segment videos locally from the `resultUrls[]`.
   - Concatenate using `ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4` (re-encode if codecs differ).
   - Present the stitched file alongside the individual segments so the user has both.

## Veo 3.1: generationType — pick one

Kie.ai's Veo wrapper exposes a `generationType` field that controls how `imageUrls[]` is interpreted.

| Mode | `generationType` | `imageUrls[]` meaning | When to use |
|------|------------------|------------------------|-------------|
| **Text-to-video** | `TEXT_2_VIDEO` | Ignored | No reference image — pure text prompt. |
| **First-and-last frames** | `FIRST_AND_LAST_FRAMES_2_VIDEO` | `[firstFrameUrl, lastFrameUrl]` | Frame-to-frame morph; video animates between two images. |
| **Reference-to-video** | `REFERENCE_2_VIDEO` | Up to 3 style/mood references | Style/mood inspiration, not literal first-frame animation. |

**Default rule:** When the user provides a single reference photo of a person or scene they want the video to **start from**, use `FIRST_AND_LAST_FRAMES_2_VIDEO` with `imageUrls: [startFrameUrl]` (omit the second entry — kie.ai accepts a one-element array for first-frame-only). For pure style/mood, use `REFERENCE_2_VIDEO`.

## Generated image QA (mandatory)

Applies to **still images** from kie.ai, especially `nano-banana-2` / `nano-banana-pro` via `createTask`. After each task reaches `successFlag: 1`, **visually inspect the output** (download or open the image URL from `resultUrls[0]` / use the agent's image-reading capability).

**Look for:** extra or missing hands or fingers; wrong limb count; distorted, duplicated, or merged facial features; melted or fused objects; impossible anatomy; stray limbs; obvious texture or boundary artifacts; unreadable or garbled text if text was requested.

**If something looks wrong:** Do **not** hand off the bad frame as the final deliverable without trying again. **Regenerate** with a **revised prompt** that explicitly corrects the issue (e.g. "exactly two hands, five fingers each, anatomically correct arms," "single face, no duplicate features"). Do **not** resend the identical payload and expect a different outcome.

**Retry cap:** Up to **2 regeneration attempts per originally requested image** (3 attempts total including the first). If defects remain after the cap, stop auto-retries, tell the user what still looks wrong, show the best attempt or URLs for all attempts, and ask how they want to proceed.

**Credits:** Each attempt is a separate generation and is billed. Summarize total cost used for that image after the QA loop ends. See **Exception — QA-fix retries** under [Credit cost estimation](#credit-cost-estimation-mandatory--show-before-generating).

**Video (optional quick check):** Before spending heavily on downstream video, you may spot-check generated-video thumbnails or extracted frames for the same kinds of defects; scope is lighter than for hero stills.

Details and checklist items: [prompting/prompt-library/nano-banana.md](prompting/prompt-library/nano-banana.md).

## Execution checklist (agent)

1. **Ask for script/dialogue:** If the output is a video with a person speaking, ask the user for the exact words. Count words to auto-select duration (see "Script length → video duration" above). If too long, offer to split. (Skip for Nano Banana image-only requests.)
   - **MANDATORY dialogue confirmation gate (before cost / before generation):** Extract the dialogue lines from the drafted prompt and present them to the user as a dedicated, numbered block separate from the visual description. Follow the format in [Script and dialogue → MANDATORY dialogue confirmation gate](#mandatory--dialogue-confirmation-gate). Wait for explicit `yes` before moving on. This gate is separate from the cost confirmation — both must be satisfied.
2. **Nano Banana image model:** For image calls, confirm Nano Banana 2 (default) vs Nano Banana Pro per the section above. Skip if not an image call.
3. **Ask for generation count:** Ask how many variations the user wants for this prompt. Default to 1.
4. **Show cost and get confirmation:** Calculate total cost from `MASTER_CONTEXT.md`. Present the breakdown to the user. **Do NOT proceed until they confirm.**
5. **Resolve reference image URLs:** Before composing the prompt, check the repo-root `references/` folder for relevant images: `references/influencers/` for person recreation, `references/products/` for product showcase, `references/aesthetics/` for style/mood. If the user hasn't provided an image but a relevant one exists in `references/`, offer to use it — but remind them it must be hosted at a public HTTPS URL before kie.ai can consume it. Follow the flow in [Reference images: hosting and public URLs](#reference-images-hosting-and-public-urls). For Veo, choose `generationType` per the section above.
6. Compose JSON per [reference.md](reference.md):
   - **Seedance 2.0, Sora 2, Kling 3.0, Nano Banana:** `POST /api/v1/jobs/createTask` with `{"model": "<slug>", "input": {...}}`.
   - **Veo 3.1:** `POST /api/v1/veo/generate` with the Veo-specific body.
   - Include `callBackUrl` only if the user has a public webhook endpoint — otherwise omit and poll.
7. `POST` **N times** (once per requested variation) with the same payload. Fire in parallel where possible. **Immediately after each POST succeeds, append a log entry to `logs/kie-api.jsonl`** with the request config (endpoint, model, duration, resolution, aspect_ratio, audio, reference-URL counts, promptWordCount, taskId). Do NOT log the full prompt text, API keys, Authorization headers, or reference URLs (log the count, not the URLs — they may be private).
8. **Poll:** for Veo, `GET /api/v1/veo/record-info?taskId=...`; for everything else, use the unified task-details endpoint (see [reference.md](reference.md)). Poll all task IDs concurrently, every 3–5 seconds, until `successFlag` is `1` (success) or `2|3` (failure). **When polling completes, update the log entry** with `response.status`, `response.generationTimeSec`, `response.resultUrls` (count only, not the URLs), and `response.error` (if failed). See `logs/README.md` for the schema.
9. **Generated image QA:** For each **still image** produced in this turn (Nano Banana outputs), follow [Generated image QA](#generated-image-qa-mandatory): inspect the image; if defective, regenerate with a refined prompt until pass or **2 retries** are exhausted. Skip this step for video-only outputs with no still to review.
10. **Present results:** Return the `resultUrls[]` from each task for **QA-passed** stills (or the best attempt after max retries, with a clear note). If multiple variations, present as a numbered list for comparison. Explain `failed` with moderation/validation hints when appropriate. For Nano Banana images used as starting frames, show the image and **wait for user approval** before proceeding to video generation.
    - **ALWAYS open the output folder** on the user's machine after saving generated files so they can immediately review: `open "<output_directory>"` (macOS). Save videos to `outputs/` with a descriptive subfolder (e.g. `outputs/seedance-tests/`, `outputs/clone-ad-tests/`). Result URLs from kie.ai eventually expire — download locally for anything you want to keep.
11. **Stitch if split:** If the script was split into segments, offer to stitch the final videos together with `ffmpeg` and provide both the stitched file and individual segments.

## Errors (user-facing)

- **401:** Bad or missing `KIE_API_KEY` — fix in `.env` (setup flow above).
- **402:** Out of credits on kie.ai — top up at [kie.ai/billing](https://kie.ai/billing).
- **400 / 422:** Validation or moderation — tighten prompt, remove disallowed content, check required enums (aspect ratio, duration). Kie.ai returns a human-readable message in `msg`.
- **429:** Rate limit — back off and retry. Default kie.ai rate limits are generous for paid accounts.
- **500 / 503:** Upstream model error — retry later; if repeated on a specific prompt, try tightening the prompt (content checker may be flagging it silently).
- **`successFlag: 2` or `3`:** Task-level failure. Read `data.error` for the reason. Common causes: content-checker rejection, stale or unreachable reference URL, invalid field combination.

## Supporting files

- [reference.md](reference.md) — endpoints, auth detail, polling, per-model `input` schemas, URL-hosting notes.
- [prompting/guide.md](prompting/guide.md) — marketing brief → API.
- **Seedance 2.0:**
  - [prompting/prompt-library/seedance-2.md](prompting/prompt-library/seedance-2.md) — main Seedance 2.0 model guide (platform rules, API parameters, style template directory).
  - [prompting/prompt-library/seedance-2-ugc.md](prompting/prompt-library/seedance-2-ugc.md) — 9-layer UGC selfie-style formula.
  - [prompting/prompt-library/seedance-2-premium-reveal.md](prompting/prompt-library/seedance-2-premium-reveal.md) — dark-void premium product reveal (no person).
  - [prompting/prompt-library/seedance-2-product-hero.md](prompting/prompt-library/seedance-2-product-hero.md) — elemental product hero with splash/effects (no person).
  - [prompting/prompt-library/seedance-2-studio-lookbook.md](prompting/prompt-library/seedance-2-studio-lookbook.md) — studio lookbook with voiceover.
  - [prompting/prompt-library/seedance-2-feature-walkthrough.md](prompting/prompt-library/seedance-2-feature-walkthrough.md) — fast-paced feature walkthrough demo.
  - [prompting/analyze-video/SKILL.md](prompting/analyze-video/SKILL.md) — reverse-engineer a reference video into a reusable Seedance 2.0 prompting template.
  - [prompting/clone-ad/SKILL.md](prompting/clone-ad/SKILL.md) — clone a reference video ad for a different product (end-to-end: analyze → adapt → generate).
- **Other models:**
  - [prompting/prompt-library/influencer-recreation.md](prompting/prompt-library/influencer-recreation.md) — analyze a reference photo and recreate the influencer.
  - [prompting/prompt-library/ugc-selfie-style.md](prompting/prompt-library/ugc-selfie-style.md) — cross-model UGC guide (iPhone aesthetic, negative prompts, per-model formulas).
  - [prompting/prompt-library/product-showcase.md](prompting/prompt-library/product-showcase.md) — product-in-hand video workflow (Nano Banana image → approve → video).
  - [prompting/prompt-library/nano-banana.md](prompting/prompt-library/nano-banana.md) — Nano Banana image prompting guide.
  - [prompting/prompt-library/character-sheet.md](prompting/prompt-library/character-sheet.md) — generate a 10-image character sheet for a new AI influencer from a text description.
  - [prompting/prompt-library/ugc-product-selfie.md](prompting/prompt-library/ugc-product-selfie.md) — UGC selfie-style still image: character + product + style references.
- [prompting/brand-voice-starter.md](prompting/brand-voice-starter.md) — template to copy into `MASTER_CONTEXT.md`.
