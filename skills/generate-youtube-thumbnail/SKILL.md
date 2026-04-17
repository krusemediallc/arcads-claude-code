---
name: generate-youtube-thumbnail
description: >-
  Generate high-CTR YouTube thumbnails using Nano Banana 2 (or Nano Banana Pro) via the kie.ai API. Handles character likeness alignment via public reference image URLs, proven CTR-tested prompt formulas, and parallel batch generation. Use when the user asks to create a YouTube thumbnail, video thumbnail, A/B test thumbnail variations, or refers to thumbnail design with their face, brand assets, or product photos.
---

# Generate YouTube Thumbnail

A reusable workflow for creating YouTube thumbnails via kie.ai's Nano Banana image endpoint with proper character likeness and proven CTR formulas.

## When to use this skill

Trigger on phrases like:
- "make me a YouTube thumbnail"
- "create a thumbnail for this video"
- "I need thumbnail variations / A/B tests"
- "remake this thumbnail with my face"
- "generate 10 thumbnail concepts"
- "thumbnail with [me / my product / my brand]"

## Read order

1. **This file** — workflow, decision tree, batch generation
2. **[prompting/guide.md](prompting/guide.md)** — likeness alignment, expressions cheat sheet, prompt structure
3. **[prompting/formulas.md](prompting/formulas.md)** — 5 proven thumbnail formulas with templates
4. **[scripts/generate-batch.sh](scripts/generate-batch.sh)** — copy/adapt this script for new batches
5. **[../kie-ai-external-api/SKILL.md](../kie-ai-external-api/SKILL.md)** — parent skill: auth, endpoint families, hosting flow, polling

## Prerequisites

- `.env` with `KIE_API_KEY` (Bearer token — see `../kie-ai-external-api/SKILL.md`)
- **Reference images hosted at public HTTPS URLs** — kie.ai does not accept file uploads or base64. You must host each reference yourself (Imgur `i.imgur.com/*.jpg`, Cloudflare R2, Supabase Storage, GitHub raw, etc.) and pass the public URLs in. See `../kie-ai-external-api/SKILL.md` → "Reference images: hosting and public URLs".
- Local reference images organized (optional but recommended) in a project folder so you can track which file maps to which hosted URL:
  - `face/` — 5+ photos of the subject (headshot + 3/4 angles + close-ups + expressions)
  - `logos/` — brand logos as files
  - `products/` — clean product shots
  - `examples/` — real ad screenshots, comparison material
  - `style/` — example thumbnails the user wants to match aesthetically

If references are missing or the user pastes images in chat instead of saving/hosting them, **stop and ask the user to save the files AND host them at public URLs** (e.g. drop into `references/youtube thumbnail/` for tracking, then upload to Imgur/R2). Chat paste ≠ file on disk ≠ public URL.

## Workflow

### 1. Gather requirements (in order)

Ask the user for any missing context, but only what you actually need:

1. **Concept** — what's the video about? Single concept, A/B variations, or specific recreation of an existing thumbnail style?
2. **Subject** — who is in the thumbnail (the user themselves, an AI character, no person)?
3. **Brand assets** — which logos / products / brand colors should appear?
4. **Text** — what should the title text say? Will text be baked in, or added in post (Canva/Photoshop)?
5. **Comparison material** — for "real vs AI" thumbnails, what real ad and what AI-generated ad?
6. **Reference URLs** — for every brand-specific visual (face, logo, product), ask the user for the **public HTTPS URL**. If they only have local files, walk them through the hosting flow in `../kie-ai-external-api/SKILL.md`.

### 2. Verify reference URLs exist

Collect the list of hosted URLs the user will pass to the API. Quick sanity check: open each URL in a browser preview (or `curl -I`) — it should return `200` and `Content-Type: image/*`. Watch-outs:
- Imgur page URLs (`imgur.com/abc123`) do **not** work — use the direct `i.imgur.com/abc123.jpg` link.
- Google Drive / Dropbox share pages redirect to HTML — won't work.
- Signed S3 URLs expire; use long-lived public-bucket URLs for repeat batches.

If the user has local files but no URLs yet, stop and resolve hosting first. **Do not proceed with text-only descriptions for brand-specific items** (logos, branded products, branded apparel) — you'll get generic AI approximations that don't match the brand. Generic descriptions are OK for backgrounds, expressions, and clothing.

### 3. Estimate cost and confirm

Always present cost as an **estimate** before firing. Read per-model rates from `MASTER_CONTEXT.md`:

> "Estimated cost: N variations × $X (nano-banana-2) = $Y. Confirm before I fire?"

Model choice:
- **`nano-banana-2`** — default. 1K/2K output. Fastest and cheapest.
- **`nano-banana-pro`** — supports 4K output and stronger fine-detail rendering. Use when the thumbnail needs crisp small text or detailed product surfaces.

### 4. Pick a formula

See **[prompting/formulas.md](prompting/formulas.md)** for the 5 proven formulas. Match the user's intent:

| User says... | Use formula |
|---|---|
| "Just me with my brand" / "branding thumbnail" | **Peace-sign / branding** |
| "Real vs AI" / "compare" / "before/after" | **Real vs AI comparison** |
| "Show the process" / "with the terminal" | **Terminal flow** |
| "Surprised face" / "shocked reaction" | **Reaction shock** |
| "Replace" / "alternative" / "swap out" | **Before/after split** |

### 5. Compose prompts

Follow the template in **[prompting/guide.md](prompting/guide.md)**:

```
YouTube thumbnail, 16:9 landscape.
[SUBJECT — likeness block + clothing + framing + "no hands" if applicable]
Expression: [specific expression from expressions cheat sheet]
[LEFT visual element + reference]
[RIGHT visual element + reference]
Across the top in massive bold yellow block letters with thick black outline reads [TITLE].
Background: [color + glow]
Style: [aesthetic notes]
Avoid: distorted face, extra fingers, hands visible, blurry logos, generic face
```

**Always include the CRITICAL CHARACTER LIKENESS block** when the subject is a real person. See `prompting/guide.md`.

### 6. Generate (use the batch script)

Copy `scripts/generate-batch.sh` to a new versioned script (`scripts/generate-thumbnails-vN.sh`) and modify:

1. Update `REFERENCE_URLS` array with the public HTTPS URLs for your references (max 14 per generation — Nano Banana's `image_input[]` limit)
2. Replace the `PROMPTS` array entries with your composed prompts
3. (Optional) switch `MODEL` to `nano-banana-pro` if you need 4K
4. Run with `bash scripts/generate-thumbnails-vN.sh > output/run.log 2>&1 &`
5. Monitor with `tail -F output/run.log | grep -E "DONE|FAILED|Task"`

The script handles:
- `POST /api/v1/jobs/createTask` with `{model, input: {prompt, image_input, aspect_ratio}}`
- Parallel firing (all variations fired in parallel)
- Retry on failure
- Polling `GET /api/v1/jobs/recordInfo?taskId=...` until `successFlag` is `1` (success) or `2|3` (failure)
- Downloading the result from `data.response.resultUrls[0]`
- Appending a log entry to `logs/kie-api.jsonl` per the parent skill's schema

### 7. Review and present

After all generations complete, read each thumbnail with the Read tool and present:

- Brief verdict per thumbnail (likeness, readability, emotional impact)
- Top 3 picks ranked by CTR potential
- Specific reasons for the picks (which expression, which color contrast, which formula)
- Offer next-step refinements (different expression, background color, copy variation)

### 8. Mandatory disclosures

- **Always label dollar totals as estimates** and tell the user to confirm exact pricing at [kie.ai/billing](https://kie.ai/billing)
- **Cost data:** read from `MASTER_CONTEXT.md` cost table — Nano Banana 2 and Nano Banana Pro rows
- **Generation time:** Nano Banana ~30–60 seconds typical
- **Parallel budget:** 10 in parallel typically finishes in ~1.5–2 min total (kie.ai queue depending)

## Quirks and pitfalls

### Public URLs only — no base64, no file uploads

kie.ai does not host reference images. The API takes `image_input: ["https://...", ...]` — each entry must be a publicly reachable HTTPS URL returning an image. No presigned upload flow, no multipart POST, no base64.

### Imgur direct link only

Use `https://i.imgur.com/AbC123.jpg`, not `https://imgur.com/AbC123`. The page URL returns HTML and fails silently (the model sees no reference, output drifts to "generic bearded man with glasses").

### Stale / signed URLs expire

If you use signed S3/GCS URLs, make sure the signature window covers your entire batch + retries. For repeat batches over days/weeks, prefer a long-lived public bucket (Cloudflare R2 public bucket, Supabase public storage, GitHub raw).

### Chat-pasted images are NOT URLs

If the user pastes an image directly in chat, you cannot pass it to the API. Ask them to save the file AND host it. Both steps.

### Likeness drift without enough references

With 1-2 face references the AI generalizes to "generic bearded man with glasses." With 5+ face references from different angles it locks in the specific person. **Always use 5+ face references for character work.** Nano Banana accepts up to 14 URLs in `image_input[]`.

### Brand-specific items need actual reference images

Text descriptions of brand-specific items (logos, branded apparel, custom merchandise) will produce generic approximations. For pixel-accurate brand reproduction, host the actual brand asset and pass it as a reference.

### macOS bash 3.2

Default macOS bash doesn't support `declare -A` (associative arrays). The batch script uses indexed arrays throughout.

### Aspect ratio

Nano Banana supports `1:1, 16:9, 9:16, 3:4, 4:3`. Use `16:9` for YouTube thumbnails.

## Cost reference

Read the current rates from `MASTER_CONTEXT.md`. Typical pattern:

| Operation | Notes |
|---|---|
| Nano Banana 2 image (1 generation) | default; 1K/2K output |
| Nano Banana Pro image (1 generation) | higher; supports 4K, better fine detail |
| 6-variation batch | typical for first explorations |
| 10-variation batch | typical for refinements |
| 20-variation batch | typical for broad concept exploration |

Always present as estimates, confirm exact at [kie.ai/billing](https://kie.ai/billing).

## See also

- **[prompting/guide.md](prompting/guide.md)** — likeness alignment, expressions, prompt structure
- **[prompting/formulas.md](prompting/formulas.md)** — 5 proven CTR formulas with prompt templates
- **[scripts/generate-batch.sh](scripts/generate-batch.sh)** — reusable bash batch generator
- **[kie-ai-external-api skill](../kie-ai-external-api/SKILL.md)** — parent skill: auth, Nano Banana reference, public URL hosting flow, polling, log schema
