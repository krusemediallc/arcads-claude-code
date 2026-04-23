---
name: generate-youtube-thumbnail
description: >-
  Generate high-CTR YouTube thumbnails using Nano Banana 2 via the Arcads external API. Handles reference image upload, character likeness alignment, proven CTR-tested prompt formulas, and parallel batch generation. Use when the user asks to create a YouTube thumbnail, video thumbnail, A/B test thumbnail variations, or refers to thumbnail design with their face, brand assets, or product photos.
---

# Generate YouTube Thumbnail

A reusable workflow for creating YouTube thumbnails via Arcads' Nano Banana 2 image endpoint with proper character likeness and proven CTR formulas.

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
2. **[shared/skills/generate-youtube-thumbnail/prompting/guide.md](../../shared/skills/generate-youtube-thumbnail/prompting/guide.md)** — likeness alignment, expressions cheat sheet, prompt structure (shared across all generative-AI APIs in this portfolio)
3. **[shared/skills/generate-youtube-thumbnail/prompting/formulas.md](../../shared/skills/generate-youtube-thumbnail/prompting/formulas.md)** — 5 proven thumbnail formulas with templates (shared)
4. **[scripts/generate-batch.sh](scripts/generate-batch.sh)** — Arcads-specific batch script (presigned upload + S3 PUT pipeline)

## Prerequisites

- `.env` with `ARCADS_BASIC_AUTH` and `ARCADS_API_KEY`
- A `productId` (defaults to MASTER_CONTEXT.md's "My workspace" product)
- Reference images on disk (NOT pasted in chat — chat-pasted images are NOT accessible to the API):
  - `face/` — 5+ photos of the subject (headshot + 3/4 angles + close-ups + expressions)
  - `logos/` — brand logos as files (orange Claude Code starburst, black Arcads A, etc.)
  - `products/` — clean product shots
  - `examples/` — real ad screenshots, comparison material
  - `style/` — example thumbnails the user wants to match aesthetically

If references are missing or the user pastes images in chat instead of saving them, **stop and ask the user to drop the actual files into a project folder** (e.g. `references/youtube thumbnail/`). Chat paste ≠ file on disk.

## Workflow

### 1. Gather requirements (in order)

Ask the user for any missing context, but only what you actually need:

1. **Concept** — what's the video about? Single concept, A/B variations, or specific recreation of an existing thumbnail style?
2. **Subject** — who is in the thumbnail (the user themselves, an AI character, no person)?
3. **Brand assets** — which logos / products / brand colors should appear?
4. **Text** — what should the title text say? Will text be baked in, or added in post (Canva/Photoshop)?
5. **Comparison material** — for "real vs AI" thumbnails, what real ad and what AI-generated ad?

### 2. Verify references exist on disk

```bash
ls "references/youtube thumbnail/"
```

If references are missing, ask the user to drop them. **Do not proceed with text-only descriptions for brand-specific items** (logos, branded products, branded apparel) — you'll get generic AI approximations that don't match the brand. Generic descriptions are OK for backgrounds, expressions, and clothing.

### 3. Estimate cost and confirm

Always present cost as an **estimate** before firing:

> "Estimated cost: N variations × 24 credits = X credits. Tell me if you want to confirm exact pricing in the Arcads platform first."

### 4. Pick a formula

See **[shared/skills/generate-youtube-thumbnail/prompting/formulas.md](../../shared/skills/generate-youtube-thumbnail/prompting/formulas.md)** for the 5 proven formulas. Match the user's intent:

| User says... | Use formula |
|---|---|
| "Just me with my brand" / "branding thumbnail" | **Peace-sign / branding** |
| "Real vs AI" / "compare" / "before/after" | **Real vs AI comparison** |
| "Show the process" / "with the terminal" | **Terminal flow** |
| "Surprised face" / "shocked reaction" | **Reaction shock** |
| "Replace" / "alternative" / "swap out" | **Before/after split** |

### 5. Compose prompts

Follow the template in **[shared/skills/generate-youtube-thumbnail/prompting/guide.md](../../shared/skills/generate-youtube-thumbnail/prompting/guide.md)**:

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

**Always include the CRITICAL CHARACTER LIKENESS block** when the subject is a real person. See `shared/skills/generate-youtube-thumbnail/prompting/guide.md`.

### 6. Generate (use the batch script)

Copy `scripts/generate-batch.sh` to a new versioned script (`scripts/generate-thumbnails-vN.sh`) and modify:

1. Update `REF_BASE` and `COMMON_REFS` array with your reference file paths
2. Replace the `PROMPTS` array entries with your composed prompts
3. Run with `bash scripts/generate-thumbnails-vN.sh > output/run.log 2>&1 &`
4. Monitor with `tail -F output/run.log | grep -E "DONE|FAILED|Asset"`

The script handles:
- Image upscaling (Lanczos to 1080px longest side, RGB JPEG conversion)
- Presigned upload + S3 PUT
- **Fresh upload per generation** (critical — re-using filePaths causes 500 errors)
- Parallel firing (10 in flight ≈ 1.5 min total)
- Retry on failure
- Asset polling and download

### 7. Review and present

After all generations complete, read each thumbnail with the Read tool and present:

- Brief verdict per thumbnail (likeness, readability, emotional impact)
- Top 3 picks ranked by CTR potential
- Specific reasons for the picks (which expression, which color contrast, which formula)
- Offer next-step refinements (different expression, background color, copy variation)

### 8. Mandatory disclosures

- **Always label credit totals as estimates** and tell the user to confirm exact pricing in Arcads
- **Cost data:** Nano Banana 2 image = **24 credits** per generation (post-April-2026 800x credit multiplier)
- **Generation time:** ~30–60 seconds typical
- **Parallel budget:** 10 in parallel finishes in ~1.5–2 min total

## Quirks and pitfalls

### Reference images are effectively one-shot per upload

Reusing the same uploaded `filePath` across multiple generation calls causes `HTTP 500 UNKNOWN_ERROR`. **Always upload fresh references for each generation.** The batch script handles this automatically with `upload_all_fresh()` per `generate_one()` call.

### Image preprocessing is mandatory

Images smaller than 1080px longest side return `422 — The provided image is too small.` The skill's `prepare_image()` function:
1. Opens the image
2. Converts to RGB (strips alpha which trips some endpoints)
3. Upscales to 1080px longest side with Lanczos resampling if needed
4. Saves as JPEG quality 92

### `referenceImages` is array of plain strings

Not objects. Sending `[{filePath: "..."}]` returns `400 — each value in referenceImages must be a string`. Send `["external-api-temp-uploads/abc.jpg", ...]` instead.

### Chat-pasted images are NOT files

If the user pastes an image directly in chat, you cannot pass it to the API. Ask them to save the actual file into a project folder.

### Likeness drift without enough references

With 1-2 face references the AI generalizes to "generic bearded man with glasses." With 5+ face references from different angles it locks in the specific person. **Always use 5+ face references for character work.**

### macOS bash 3.2

Default macOS bash doesn't support `declare -A` (associative arrays). The batch script uses indexed arrays + temp files instead.

### Stale presigned URLs

Presigned URLs expire after the `expiresIn` window (~10 min). Don't reuse URLs across long-running jobs — upload fresh.

### Brand-specific items need actual reference files

Text descriptions of brand-specific items (logos, branded apparel, custom merchandise) will produce generic approximations. The Mr. Paid Social hat from text alone reads as "MR PAID SOCIAL" but won't match the real patch typography. **For pixel-accurate brand reproduction, save the actual brand asset to disk and pass it as a reference.**

## Cost reference

| Operation | Credits | Notes |
|---|---|---|
| Nano Banana 2 image (1 generation) | 24 | post-800x multiplier |
| 6-variation batch | 144 | typical for first explorations |
| 10-variation batch | 240 | typical for refinements |
| 20-variation batch | 480 | typical for broad concept exploration |

Always present as estimates, confirm exact in the Arcads platform.

## See also

- **[shared/skills/generate-youtube-thumbnail/prompting/guide.md](../../shared/skills/generate-youtube-thumbnail/prompting/guide.md)** — likeness alignment, expressions, prompt structure (shared across APIs)
- **[shared/skills/generate-youtube-thumbnail/prompting/formulas.md](../../shared/skills/generate-youtube-thumbnail/prompting/formulas.md)** — 5 proven CTR formulas with prompt templates (shared)
- **[scripts/generate-batch.sh](scripts/generate-batch.sh)** — Arcads-specific bash batch generator (presigned upload pipeline)
- **[arcads-external-api skill](../arcads-external-api/SKILL.md)** — underlying API reference for Nano Banana 2 endpoint and reference upload pipeline
