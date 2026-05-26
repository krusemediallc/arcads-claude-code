---
name: nano-banana-image-ad
description: >-
  Generate one or more standalone Meta image-ad creatives via Nano Banana 2 / Nano Banana Pro (Gemini Flash Image family) through the Arcads external API. Locks the model family, auto-strips platform chrome, enforces edge-safe layouts. Use when the user asks for a "Nano Banana ad", "Gemini image ad", "nano-banana-2 ad creative", "make a static image ad with Gemini", or anchors on a need for photoreal / lifestyle / multi-reference / handheld-object / clay-texture ad creatives (sticky-note flatlays, held-whiteboard signs, lifestyle portraits, ingredient collages, OOH photography). Does NOT trigger on ChatGPT Image cues — use chatgpt-image-ad for those.
---

# nano-banana-image-ad (Arcads)

Generate one or more **standalone Meta ad image creatives** via Arcads' `POST /v2/images/generate` with the Nano Banana model family (default `nano-banana-2`). Hands the image paths off to your Meta-ad-builder skill — this skill does not upload to Meta itself.

## Read order

1. **This file** — Arcads-specific endpoint, auth, presigned upload flow, workflow phases.
2. **[shared/skills/nano-banana-image-ad/prompting/guide.md](../../shared/skills/nano-banana-image-ad/prompting/guide.md)** — model-specific prompting (what Nano Banana is good/bad at, when to switch to gpt-image-2).
3. **[shared/skills/image-ad-prompting/prompting/prompt-library.md](../../shared/skills/image-ad-prompting/prompting/prompt-library.md)** — 30+ validated templates with per-model notes.
4. **[shared/skills/image-ad-prompting/prompting/safety-suffixes.md](../../shared/skills/image-ad-prompting/prompting/safety-suffixes.md)** — the 3 always-on guards.
5. **[scripts/generate_image.py](scripts/generate_image.py)** — the helper script (Python stdlib only).

## Hard rules — never relax

1. **Model is in the Nano Banana family.** The script accepts `nano-banana-2` (default), `nano-banana-pro` (Gemini 3 Pro Image, higher cost / locked identity), `nano-banana-edit` (inpaint-focused), or `nano-banana` (legacy). Anything else is refused. If the user asks for gpt-image-2, point them at `chatgpt-image-ad`.
2. **No platform/screenshot chrome in output.** `NO_CHROME_SUFFIX` is always on (override only with `--allow-chrome`).
3. **Edge-safe + glyph-safety suffixes always on** unless `--no-safe-zone` is explicit.
4. **Max 14 reference images.** Hard Arcads cap for Nano Banana. Script enforces.
5. **No Meta upload from this skill.** Image generation only. The user has a separate ad-builder skill in their stack — hand off via filesystem paths.
6. **Always present a credit-cost estimate before generating.** Each Nano Banana call is one image; multiply by `--n`. `nano-banana-pro` costs more than `nano-banana-2` — surface the per-model rate from `logs/arcads-api.jsonl`.

## Prerequisites

- `.env` containing `ARCADS_BASIC_AUTH` (preferred) OR `ARCADS_API_KEY`
- Optional: `PRODUCT_ID`, `PROJECT_ID` in `.env` for session-folder organization
- Reference images on local disk. The script handles the Arcads presigned-upload flow internally.

## Configuration

- **Base URL:** `https://external-api.arcads.ai` (or `ARCADS_BASE_URL`).
- **Auth:** HTTP Basic. The script prefers a pre-encoded `ARCADS_BASIC_AUTH`; falls back to encoding `ARCADS_API_KEY`.
- **Endpoint:** `POST /v2/images/generate`; poll `GET /v1/assets/{id}` until `status: generated`.
- **Reference uploads:** `POST /v1/file-upload/get-presigned-url` returns `{presignedUrl, filePath}`; `PUT` bytes to `presignedUrl`; pass the `filePath` in `referenceImages`. Single-use — re-uploaded fresh per variant by the script.

## Generation modes

| Mode | When to use | Required | Optional |
|---|---|---|---|
| `image` (default) | Brand-new ad image. | `--prompt`, `--aspect-ratio` | `--image-ref` (up to 14) |
| `image_edit` | Modify a `--source` image. | `--prompt`, `--source` | `--image-ref` (up to 14) |

## Supported aspect ratios

`1:1`, `16:9`, `9:16`. **Only these three are accepted by Arcads' `/v2/images/generate` endpoint** (the same endpoint serves gpt-image-2 and Nano Banana — same ratio constraints). Templates in the shared library that use `2:3`, `4:5`, `3:2`, etc. won't render at their native ratio on this backend — fall back to `1:1` and post-crop, or use the KIE nano-banana-image-ad sibling which supports the full Meta ratio set natively via the `/jobs/createTask` endpoint.

## Model variants (`--model`)

- **`nano-banana-2`** (default) — Gemini 2.5 Flash Image. The standard. Use for most templates.
- **`nano-banana-pro`** — Gemini 3 Pro Image. Use for hero stills, character continuity across runs, material-realism critical shots (claymation, Pixar, premium product photography). Costs more credits.
- **`nano-banana-edit`** — inpaint-focused. Use only with `--mode image_edit` for tight masked edits (swap background, change object color).
- **`nano-banana`** — legacy. Use only if the user explicitly asks; new work should use `nano-banana-2`.

Ask the user which variant they want **before the first generation in a session** if the value isn't already set in `MASTER_CONTEXT.md`. Default to `nano-banana-2`.

## Workflow

### Phase 1: Preflight

1. `.env` exists with credentials.
2. (Optional) `arcads-external-api` session folder set up.
3. Health-check: `curl -sf -H "$AUTH" "$BASE_URL/v1/products"` returns 200.

### Phase 2: Gather inputs

Collect: seed prompt, mode, source (if edit), reference paths (up to 14), variant count, aspect ratio, model variant.

### Phase 3: Prompt rewrite

Read [shared/skills/image-ad-prompting/prompting/prompt-library.md](../../shared/skills/image-ad-prompting/prompting/prompt-library.md). If the user's brief matches a template, **check the Model notes block** — only proceed if `nano-banana` is marked clean, preferred, or strong. If gpt-image-2 is preferred, suggest switching skills.

Fill `{placeholders}` and show the user the rewritten prompt. Ask for approval before generating.

For fresh prompts (no template match), follow the structure in [shared/skills/nano-banana-image-ad/prompting/guide.md § Phase 3b](../../shared/skills/nano-banana-image-ad/prompting/guide.md) — lean on Nano Banana strengths (named reference roles, lighting specifics, material specifics).

### Phase 4: Credit cost confirmation (MANDATORY)

Present the estimated credit cost (read from `logs/arcads-api.jsonl` for matching past calls). Surface the model variant prominently: `nano-banana-pro` costs more than `nano-banana-2`. Wait for explicit confirmation.

### Phase 5: Generate

```bash
~/.claude/skills/nano-banana-image-ad/scripts/generate_image.py \
  --prompt "<rewritten>" \
  --aspect-ratio <ratio> \
  --n <N> \
  --image-ref <product.png> \
  [--image-ref <character.png>] \
  [--image-ref <style.png>] \
  --out ./generated \
  --env-file .env

# For higher-stakes hero shots:
~/.claude/skills/nano-banana-image-ad/scripts/generate_image.py \
  --model nano-banana-pro \
  --prompt "<rewritten>" \
  --aspect-ratio <ratio> \
  --n <N> \
  --image-ref <product.png> \
  --out ./generated \
  --env-file .env

# For an edit run (inpaint):
~/.claude/skills/nano-banana-image-ad/scripts/generate_image.py \
  --mode image_edit \
  --model nano-banana-edit \
  --prompt "<edit-instruction>" \
  --source <existing.png> \
  [--image-ref <guidance.png>] \
  --n <N> \
  --out ./generated \
  --env-file .env
```

Each line on stdout is one JSON variant (`variant`, `path`, `asset_id`, `width`, `height`, `prompt`, `mode`, `aspect_ratio`, `model`).

Log each call to `logs/arcads-api.jsonl` with the model variant, ref count, and returned `asset_id`s.

### Phase 6: Visual QA (MANDATORY)

For each completed variant, **read the image** and inspect for:
- Garbled small text (the main Nano Banana weakness)
- Extra fingers / wrong limb count (common Gemini-family failure)
- Wordmark drift (always pass brand wordmarks as `--image-ref` to mitigate)
- Character identity drift across variants (use `nano-banana-pro` to lock identity if it matters)

If defects: regenerate with a revised prompt that explicitly corrects the issue (see [shared/skills/nano-banana-image-ad/prompting/guide.md § Retry mode](../../shared/skills/nano-banana-image-ad/prompting/guide.md)). Cap at 2 retries per variant.

### Phase 7: Confirm and hand off

Show all paths to the user. Ask "Use all / use these specific ones / regenerate / cancel."

Selected variants are ready for your **Meta-ad-builder skill**. Print the paths.

Optionally, write the selected paths to `./generated/run-<ts>.jsonl` for downstream consumption.

## Out of scope — fail clearly

- **Meta upload** — different skill in your stack.
- **ChatGPT Image 2 / gpt-image-2 generation** — use `chatgpt-image-ad`.
- **Video, carousel, DCO ads** — image only.
- **Ad copy writing** — different skill.
- **Editing the shared prompt library** — use `image-ad-clone-nano-banana`.

## Common errors

- **401/403** → fix `.env`.
- **422 validation/moderation** → tighten prompt; check `aspectRatio` is in supported set; check `--n` ≤ 5.
- **500 UNKNOWN_ERROR** → usually a stale presigned filePath. The script re-uploads per variant; if persistent, file an issue with the `asset_id`.

## Files this skill owns

- `~/.claude/skills/nano-banana-image-ad/SKILL.md` — this file
- `~/.claude/skills/nano-banana-image-ad/scripts/generate_image.py` — Arcads Nano Banana caller

## See also

- **[shared/skills/nano-banana-image-ad/prompting/guide.md](../../shared/skills/nano-banana-image-ad/prompting/guide.md)** — model-specific prompting
- **[shared/skills/image-ad-prompting/prompting/prompt-library.md](../../shared/skills/image-ad-prompting/prompting/prompt-library.md)** — shared template library
- **[image-ad-clone-nano-banana skill](../image-ad-clone-nano-banana/SKILL.md)** — reverse-engineer ads into reusable templates
- **[arcads-external-api skill](../arcads-external-api/SKILL.md)** — underlying Arcads conventions
- **[chatgpt-image-ad skill](../chatgpt-image-ad/SKILL.md)** — sibling skill for typography-heavy / UI-mimicry templates
