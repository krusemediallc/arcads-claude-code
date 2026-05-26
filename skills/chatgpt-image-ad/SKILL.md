---
name: chatgpt-image-ad
description: >-
  Generate one or more standalone Meta image-ad creatives via ChatGPT Image 2 (gpt-image-2) through the Arcads external API. Locks the model, auto-strips platform chrome, enforces edge-safe layouts and glyph-safety inside body text. Use when the user asks for a "gpt-image-2 ad", "ChatGPT Image ad", "Image 2 ad creative", "make a static image ad with GPT", or anchors on a need for typography-heavy / dense-text / UI-mimicry ad creatives (chat threads, comparison tables, fake search results, iOS dialogs, Slack snapshots, ChatGPT-conversation ads, Apple Notes lists). Does NOT trigger on Nano Banana cues — use nano-banana-image-ad for those.
---

# chatgpt-image-ad (Arcads)

Generate one or more **standalone Meta ad image creatives** via Arcads' `POST /v2/images/generate` with `model: "gpt-image-2"`. Hands the image paths off to your Meta-ad-builder skill — this skill does not upload to Meta itself.

## Read order

1. **This file** — Arcads-specific endpoint, auth, presigned upload flow, workflow phases.
2. **[shared/skills/chatgpt-image-ad/prompting/guide.md](../../shared/skills/chatgpt-image-ad/prompting/guide.md)** — model-specific prompting (what gpt-image-2 is good/bad at, when to switch to nano-banana).
3. **[shared/skills/image-ad-prompting/prompting/prompt-library.md](../../shared/skills/image-ad-prompting/prompting/prompt-library.md)** — 30+ validated templates with per-model notes.
4. **[shared/skills/image-ad-prompting/prompting/safety-suffixes.md](../../shared/skills/image-ad-prompting/prompting/safety-suffixes.md)** — the 3 always-on guards.
5. **[scripts/generate_image.py](scripts/generate_image.py)** — the helper script (Python stdlib only).

## Hard rules — never relax

1. **Model is `gpt-image-2`.** The script refuses any other value. If the user asks for nano-banana, point them at `nano-banana-image-ad`.
2. **No platform/screenshot chrome in output.** `NO_CHROME_SUFFIX` is always on (override with `--allow-chrome` only when the ad's concept *requires* chrome — rare).
3. **Edge-safe + glyph-safety suffixes always on** unless `--no-safe-zone` is explicit. They fix real failures; don't remove silently.
4. **Max 5 reference images.** Hard Arcads cap for gpt-image-2 (observed `400 Max 5 reference image(s) allowed`). The script enforces.
5. **No Meta upload from this skill.** Image generation only. The user has a separate ad-builder skill in their stack — hand off via filesystem paths.
6. **Always present a credit-cost estimate before generating** (see Arcads `arcads-external-api` skill conventions). Each gpt-image-2 call is one image; multiply by `--n` variants.

## Prerequisites

- `.env` containing `ARCADS_BASIC_AUTH` (preferred, pre-encoded) OR `ARCADS_API_KEY`
- Optional: `PRODUCT_ID`, `PROJECT_ID` in `.env` so generated assets land in the right Arcads dashboard folder (see `arcads-external-api` SKILL.md for the session-folder pattern)
- Reference images on local disk (PNG/JPG/JPEG/WEBP/GIF). The script handles the Arcads presigned-upload flow internally — you pass local paths.

## Configuration

- **Base URL:** `https://external-api.arcads.ai` (or `ARCADS_BASE_URL`).
- **Auth:** HTTP Basic. The script prefers a pre-encoded `ARCADS_BASIC_AUTH` env var (e.g. `Basic ZXhhbXBsZTo=`); falls back to encoding `ARCADS_API_KEY` with an empty password.
- **Endpoint:** `POST /v2/images/generate` (request); `GET /v1/assets/{id}` (poll until `status: generated`); image URL fetched once status flips.
- **Reference uploads:** `POST /v1/file-upload/get-presigned-url` returns `{presignedUrl, filePath}`; `PUT` the bytes to `presignedUrl`; pass the `filePath` string in `referenceImages`. **Each filePath is single-use** — the script re-uploads per variant so parallel runs don't collide.

## Generation modes

| Mode | When to use | Required | Optional |
|---|---|---|---|
| `image` (default) | Generate a brand-new ad image. | `--prompt`, `--aspect-ratio` | `--image-ref` (up to 5) |
| `image_edit` | Modify an existing image (swap colors, change background, add element). | `--prompt`, `--source` | `--image-ref` (up to 5) |

## Supported aspect ratios

`1:1`, `16:9`, `9:16`. **Only these three are accepted by Arcads' `/v2/images/generate` endpoint** (confirmed live: `aspectRatio must be one of the following values: 1:1, 16:9, 9:16`). Templates in the shared library that use `2:3`, `3:2`, `4:5`, etc. won't render at their native ratio on this backend — fall back to `1:1` and crop, or use the KIE chatgpt-image-ad sibling which supports `2:3` and `3:2` natively via its dedicated `/gpt4o-image/generate` endpoint.

## Inputs the user must provide

| Input | Notes |
|---|---|
| Seed prompt | The creative direction in their words. You will rewrite it (see Phase 3). |
| Aspect ratio | One of the 5 above. Reject anything else. |
| Reference image(s) | Optional but strongly recommended when the ad features a specific product. Up to 5. |
| Variant count `N` | Default 1. Cap at 5. |
| Mode | `image` (default) or `image_edit`. |
| Source image | Required only for `image_edit`. |

## Workflow

### Phase 1: Preflight

1. `.env` exists with `ARCADS_BASIC_AUTH` or `ARCADS_API_KEY`.
2. (Optional) `arcads-external-api` session folder is set up (see that skill's "Session setup" section). If `PRODUCT_ID` / `PROJECT_ID` aren't set, generated assets land in the default project — you can fix later via `POST /v1/assets/add-to-project`.
3. Health-check: `curl -sf -H "$AUTH" "$BASE_URL/v1/products"` returns 200.

### Phase 2: Gather inputs

Collect: seed prompt, mode, source (if edit), reference paths, variant count, aspect ratio.

### Phase 3: Prompt rewrite

Read [shared/skills/image-ad-prompting/prompting/prompt-library.md](../../shared/skills/image-ad-prompting/prompting/prompt-library.md). If the user's brief maps onto a template, **check the Model notes block** — only proceed if `gpt-image-2` is marked clean or preferred. If nano-banana is preferred, suggest switching skills before generating.

Fill the `{placeholders}` and show the user the rewritten prompt. Ask "Use this, edit it, or start over?" Loop until approved.

For fresh prompts (no template match), follow the structure in [shared/skills/chatgpt-image-ad/prompting/guide.md § Phase 3b](../../shared/skills/chatgpt-image-ad/prompting/guide.md).

### Phase 4: Credit cost confirmation (MANDATORY)

Per `arcads-external-api` conventions: present an estimated credit cost (read from `logs/arcads-api.jsonl` for matching past calls, or `MASTER_CONTEXT.md` rate table). Wait for explicit confirmation before firing.

### Phase 5: Generate

```bash
~/.claude/skills/chatgpt-image-ad/scripts/generate_image.py \
  --prompt "<rewritten>" \
  --aspect-ratio <ratio> \
  --n <N> \
  --image-ref <product.png> \
  [--image-ref <style-board.png>] \
  --out ./generated \
  --env-file .env

# For an edit run:
~/.claude/skills/chatgpt-image-ad/scripts/generate_image.py \
  --mode image_edit \
  --prompt "<edit-instruction>" \
  --source <existing.png> \
  [--image-ref <guidance.png>] \
  --n <N> \
  --out ./generated \
  --env-file .env
```

Each line on stdout is one JSON variant (`variant`, `path`, `asset_id`, `width`, `height`, `prompt`, `mode`, `aspect_ratio`, `model`).

Log each call to `logs/arcads-api.jsonl` with `model=gpt-image-2`, the variant count, `referenceImages` count, and the returned `asset_id`s, per `arcads-external-api` skill conventions.

### Phase 6: Visual QA (MANDATORY)

For each completed variant, **read the image** and inspect for:
- Garbled small text (most common gpt-image-2 failure on dense body text)
- Wordmark drift (if a brand wordmark wasn't passed as `--image-ref`)
- Wrong text count (e.g. 4 Slack messages instead of 3)
- iOS dialog / UI proportion drift

If defects: regenerate with a revised prompt explicitly correcting the issue (see [shared/skills/chatgpt-image-ad/prompting/guide.md § Retry mode](../../shared/skills/chatgpt-image-ad/prompting/guide.md)). Cap at 2 retries per variant.

### Phase 7: Confirm and hand off

Show all paths to the user. Ask "Use all / use these specific ones / regenerate / cancel."

Selected variants are now ready for your **Meta-ad-builder skill** (the separate skill that handles cloning, copy, and upload). Print the paths so the user can pipe them.

Optionally, write the selected paths to `./generated/run-<ts>.jsonl` (one path per line, JSON-wrapped) for downstream consumption.

## Out of scope — fail clearly

- **Meta upload** — different skill in your stack.
- **Nano Banana / Gemini image generation** — use `nano-banana-image-ad`.
- **Video, carousel, DCO ads** — image only.
- **Ad copy writing** — different skill.
- **Editing the shared prompt library** — use `image-ad-clone-chatgpt`.

## Common errors

- **401/403** → fix `.env` per `arcads-external-api` setup flow.
- **400 Max 5 reference image(s) allowed** → reduce `--image-ref` count to ≤5.
- **422 validation/moderation** → tighten the prompt; check that `aspectRatio` is in the supported set.
- **500 UNKNOWN_ERROR** → usually a stale presigned filePath being reused. The script re-uploads per variant; if you still see this, file an issue with the `asset_id` from the response.

## Files this skill owns

- `~/.claude/skills/chatgpt-image-ad/SKILL.md` — this file
- `~/.claude/skills/chatgpt-image-ad/scripts/generate_image.py` — Arcads gpt-image-2 caller (presigned upload + generate + poll + download)

## See also

- **[shared/skills/chatgpt-image-ad/prompting/guide.md](../../shared/skills/chatgpt-image-ad/prompting/guide.md)** — model-specific prompting (gpt-image-2 strengths/limits, when to switch to nano-banana)
- **[shared/skills/image-ad-prompting/prompting/prompt-library.md](../../shared/skills/image-ad-prompting/prompting/prompt-library.md)** — shared template library (30+ entries with per-model notes)
- **[shared/skills/image-ad-prompting/prompting/template-format.md](../../shared/skills/image-ad-prompting/prompting/template-format.md)** — entry skeleton for new templates
- **[shared/skills/image-ad-prompting/prompting/safety-suffixes.md](../../shared/skills/image-ad-prompting/prompting/safety-suffixes.md)** — the 3 always-on guards
- **[image-ad-clone-chatgpt skill](../image-ad-clone-chatgpt/SKILL.md)** — reverse-engineer an existing ad into a reusable template, validated via this skill's generator
- **[arcads-external-api skill](../arcads-external-api/SKILL.md)** — underlying Arcads conventions (session folder, credit cost, QA loop, logs)
- **[nano-banana-image-ad skill](../nano-banana-image-ad/SKILL.md)** — sibling skill for photoreal / lifestyle / multi-ref templates
