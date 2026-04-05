# Image quality playbook — getting the best static ads from Arcads

**Use when:** You want to maximize the quality of AI-generated static ad images. Covers workarounds for common AI image shortfalls, model comparison, and a post-production checklist.

## Available image models (all via `POST /V2/images/generate`)

All models use the same endpoint and the same request body. Only the `model` field changes.

| Model value | Name | Best for | Notes |
|------------|------|----------|-------|
| `nano-banana-2` | Nano Banana 2 | General purpose, starting frames | Default. Fast (~35s). 0.03 credits (tested) |
| `nano-banana` | Nano Banana Pro | Higher fidelity when NB2 falls short | Slightly different engine. Same API |
| `gpt-image` | GPT Image | Product shots, text rendering, complex scenes | May handle text better than Nano Banana |
| `seedream` | SeedReam | Photorealistic scenes, product photography | Google's image model |
| `seedream_5_lite` | SeedReam 5 Lite | Faster/cheaper SeedReam variant | Lighter version |
| `soul` | Soul | Artistic/stylized images | Supports `nbGenerations` (1-10) for batch |
| `grok_image` | Grok Image | General purpose alternative | xAI's image model |

**Start with `nano-banana-2`** — it's the default, cheapest, and fastest. If results aren't good enough, try others.

## Model comparison workflow (simple)

When you want to find the best model for your ad type:

1. **Write one prompt** using the static-ad or ad-remix template
2. **Tell the agent:** "Generate this prompt across nano-banana-2, nano-banana, gpt-image, and seedream"
3. The agent fires 4 calls (one per model) with the identical prompt, polls all concurrently
4. **Compare results side by side** — pick the model that works best for your use case
5. **Save the winner** in `MASTER_CONTEXT.md` under Brand so future sessions default to it

**Agent instructions for model comparison:**

```
For each model in the comparison set:
1. POST /V2/images/generate with identical prompt, aspectRatio, productId, projectId
   — only change the `model` field
2. Poll all concurrently
3. Present results as a numbered list with model name labeled
4. Note credits charged per model (from response `data.creditsCharged`)
```

Fire all calls in parallel. Do NOT change the prompt between models — the point is to isolate the model variable.

## Addressing common shortfalls

### Problem: Text on images is garbled

**Why:** All current image AI models struggle with text rendering. This is an industry-wide limitation.

**Workarounds:**
- **Best:** Don't put text in the AI image at all. Generate the image with negative space where text should go, then add text in Figma, Canva, or Photoshop. This is what professional ad teams do anyway
- **If you must try:** Keep text to 1-2 very short words. Use `"legible, sharp text reading: 'WORD'"` in the prompt. Try `gpt-image` model which may handle text better
- **In the prompt:** Add `"generous negative space on [top/bottom/left/right] for text overlay"` so the composition leaves room

### Problem: Product labels/logos are distorted

**Why:** AI models don't understand that logos are specific designs — they approximate them.

**Workarounds:**
- **Provide a product photo** as `refImageAsBase64` — this gives the model a real reference to work from, dramatically improving product fidelity
- **Angle the product** away from camera so the label is partially obscured — `"product angled 30 degrees, label partially visible"` — this hides imperfections naturally
- **Use silhouette/shape language** instead of relying on label details — describe the product by shape, color, and material: `"tall amber glass bottle with gold cap"` not `"bottle with 'GlowSerum' label"`
- **Post-production:** Composite the real label onto the AI-generated product in Photoshop. Generate the scene without worrying about label accuracy, then overlay

### Problem: Colors don't match brand exactly

**Why:** AI models interpret color descriptions loosely. "Navy blue" to a model could be anywhere in a range.

**Workarounds:**
- **Name colors multiple ways:** `"deep navy blue (#1B2A4A), dark midnight tone"` — redundancy helps
- **Use relative color language:** `"the same blue as a midnight sky"` alongside hex codes
- **Post-production color grading** is the fastest fix — adjust hue/saturation in any photo editor to match brand guidelines exactly
- **Style references help:** Drop images with your exact brand colors into `references/aesthetics/` and use them as `referenceImages` — the model will pull color cues from them

### Problem: Complex compositions fall apart (multiple products, many props)

**Why:** More objects = more chances for merging, floating, impossible geometry.

**Workarounds:**
- **Simplify:** The best ads are often the simplest. One product, clean background, strong lighting. Start here
- **Generate in layers:** Create the background/scene first, then composite the product in post-production
- **Be extremely specific about spatial relationships:** `"bottle standing upright on the left, glass to the right with 6 inches of space between them, nothing touching"` — vague spatial cues lead to merged objects
- **Reduce props:** If you prompt 5 props and things merge, try 2-3. Add the rest in post

### Problem: Output looks too "AI" / too perfect / uncanny

**Why:** AI defaults to hyper-polished, symmetrical, overly clean output.

**Workarounds:**
- **Add imperfection cues for lifestyle shots:** `"slight dust on the surface, one leaf slightly wilted, water droplet on the bottle, not perfectly centered"`
- **Specify real-world lighting:** `"natural window light from the left, slightly uneven"` instead of `"studio lighting"`
- **Use photography language:** `"shot on Canon EOS R5, 85mm f/1.4, shallow depth of field"` — this biases the model toward photorealistic rendering
- **Add texture:** `"visible grain on the wooden surface, slight scratches on the marble"` — micro-details break the AI uncanny valley
- **Reference images are powerful:** Drop 2-3 real product photos with the aesthetic you want into `references/aesthetics/` and use as `referenceImages`

### Problem: Product proportions are wrong

**Why:** Without a reference photo, the model guesses size and proportions from text alone.

**Workarounds:**
- **Always provide a product photo** via `refImageAsBase64` when possible
- **Describe relative scale:** `"small 30ml bottle, fits in one hand"` or `"large 500ml bottle, taller than the coffee mug next to it"`
- **Describe the shape precisely:** `"cylindrical, 6 inches tall, 2 inches diameter, rounded shoulders"` — not just `"a bottle"`

## Post-production checklist

AI-generated images are **raw creative** — treat them as 80% done. Final polish happens outside Arcads:

| Step | Tool | What to do |
|------|------|------------|
| **Color correction** | Any photo editor | Match exact brand colors, adjust white balance |
| **Text/copy overlay** | Figma, Canva, Photoshop | Add headlines, CTAs, legal text |
| **Logo placement** | Figma, Canva, Photoshop | Add your actual logo (don't rely on AI to render it) |
| **Product label fix** | Photoshop | Composite real label onto AI product if distorted |
| **Crop/resize** | Any editor | Fine-tune for exact platform dimensions |
| **Export** | Any editor | Export at correct DPI/resolution for the platform |

## Quick start: your first static ad

If this is your first time, do exactly this:

1. **Set up `.env`** with your Arcads API key
2. **Tell the agent:** "Generate a product hero shot of [describe your product]. Use Nano Banana 2, 1:1 aspect ratio, 1 variation"
3. **Look at the result.** Is it close? Tell the agent what to change
4. **Once you like the composition/lighting:** Run a model comparison with the same prompt across 2-3 models to find the best engine for your product type
5. **Save the winning model** in `MASTER_CONTEXT.md` as your default

That's it. Start simple, iterate. The system handles the API calls, polling, QA, and file management — you just describe what you want and react to what you see.
