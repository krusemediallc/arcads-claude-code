# Character sheet (ChatGPT Image 2 / gpt-image-2) — generate an AI influencer

**Use when:** The user wants to create a new AI influencer using **gpt-image-2** instead of Nano Banana. Same 10-image character sheet workflow, tuned for gpt-image-2's quirks.

**Parallel to:** [character-sheet.md](character-sheet.md) (Nano Banana version) — same goal, different model. Pick based on the table below.

## When to pick gpt-image-2 vs Nano Banana for character sheets

| Factor | gpt-image-2 | Nano Banana 2 / Pro |
|---|---|---|
| **Photoreal human faces** | Good — stylized photoreal | **Stronger** — more "shot on camera" feel |
| **Character identity continuity across N images** | Moderate — drifts over many gens; needs stronger text anchor | **Stronger**, especially `nano-banana-pro` (Gemini 3 Pro Image) |
| **Multi-reference blending** | Capped at **5 refs** | Up to **14 refs** — more anchors = tighter continuity |
| **Stylized / slightly illustrated look** | **Stronger** — distinct gpt-image aesthetic | Pure photoreal, less stylized |
| **Cost** | Typically higher per image than Nano Banana 2 | Cheaper; Pro is ~closer to gpt-image-2 |
| **Best for** | Brand has a slightly stylized / editorial / poster-art aesthetic; A/B comparison runs; users who hit Nano Banana rate limits | The default for pure photoreal AI-influencer / UGC use |

**Default recommendation:** start with Nano Banana ([character-sheet.md](character-sheet.md)). Use this gpt-image-2 version when (a) the brand aesthetic specifically wants the gpt-image-2 look, (b) you're running a side-by-side test, or (c) the user explicitly asks for ChatGPT Image 2.

## Required flow (do NOT skip steps)

1. User describes the influencer in plain English (e.g., "20-year-old female redhead").
2. Agent expands the description into a detailed visual prompt (Step 1).
3. Agent presents the expanded prompt for user review (Step 2).
4. **Generate 1 hero front portrait** with gpt-image-2 (Step 3).
5. **User approves the hero image** — do NOT skip this step.
6. **Generate 9 remaining angles** using the hero + up to 4 prior angles as `referenceImages` (Step 4 — note the 5-ref cap).
7. **QA all images** (Step 5).
8. **Save to `references/influencers/`** using the naming convention (Step 6).

## Step 1: Expand the user's description

Same as the Nano Banana version — see [character-sheet.md § Step 1](character-sheet.md). The base prompt structure is identical:

```
A {age}-year-old {gender} influencer with {hair color} {hair texture} {hair length} hair, {skin tone} skin with {distinguishing features}, {eye color} eyes, {build} build, {makeup level}, wearing {clothing}. Clean white studio background, photorealistic, visible skin texture, individual hair strands catching light.
```

**gpt-image-2 tuning notes:**

- **Be more specific than you'd be with Nano Banana.** gpt-image-2 leans on the text more than on the reference image for identity, so vague descriptors like "soft features" drift more across angles. Pin specific facial-anatomy notes: "narrow nose bridge", "high cheekbones with subtle hollows", "rounded chin", etc.
- **Always include the texture cues** — "visible skin texture, fine hair flyaways catching light, subtle pores" — gpt-image-2 defaults to a slightly smoother / more illustrated rendering without them.
- **Avoid celebrity / real-person names.** Same rule as Nano Banana.

## Step 2: Present the expanded prompt for approval

Show the user:
1. The expanded visual description (be more anatomically specific than the Nano Banana flow — see Step 1 note).
2. The 5 descriptor tags for the folder name (same convention as Nano Banana — see Step 6).
3. **Flag that this is the gpt-image-2 variant** — tell them you can swap to Nano Banana if they want a more photoreal feel.
4. Ask if anything needs adjusting before generating.

## Step 3: Generate the hero image (full body front)

Anchor image. All 9 other angles will reference it. **Use a full-body shot as the hero** — gives the model complete visual context (face, hair, build, clothing, shoes, proportions).

1. Compose the hero prompt: prepend `"Full body front view, head to toe."` to the base prompt, add the standard hero pose/lighting clauses:
   > "She/He looks directly at camera with a warm, confident expression. Relaxed stance, weight on one hip. Camera at eye level, soft even studio lighting from both sides."

   Include the full outfit (e.g., jeans + white sneakers) in the hero prompt since this is the full-body reference.

2. Call `POST /v2/images/generate` with:
   - `productId` and `projectId` (from session folder — see arcads-external-api/SKILL.md "Session setup" if not yet established)
   - `model`: **`gpt-image-2`** ← key difference from Nano Banana version
   - `prompt`: the hero prompt
   - `aspectRatio`: **`9:16`** (Arcads' /v2/images/generate accepts only `1:1`, `16:9`, `9:16`)

3. Poll `GET /v1/assets/{id}` until `generated`.

4. **Post-generation QA:** Inspect for anatomy defects per [nano-banana.md](nano-banana.md) (the QA checklist applies to any image model). gpt-image-2-specific watch-outs:
   - **Hands and fingers** — gpt-image-2 still occasionally renders extra fingers or warped hands; check both visible hands carefully on the full-body shot.
   - **Skin texture flatness** — if the output looks too smooth / illustrated, regen with explicit texture clauses ("visible pores, fine flyaways, light grain").
   - **Identity vs the prompt** — does the rendered character match every facial-anatomy clue you specified? If not, the angles will drift even more.
   - Regenerate with refined prompt if needed (up to 2 retries).

5. Download the image to the character's `references/influencers/{folder}/` and **open it for the user** so they can review at full resolution:
   - macOS: `open <path>`
   - Linux: `xdg-open <path>`
   - Windows: `explorer <path>`

6. **Wait for explicit user approval.** This is the character — if they don't like it, iterate before generating 9 more images. Do NOT proceed without approval.

## Step 4: Generate 9 remaining angles (5-ref cap)

Once the hero is approved:

1. Upload the hero image via `POST /v1/file-upload/get-presigned-url` → `PUT` to S3 → get `filePath`. (Same Arcads presigned flow as the Nano Banana version.)
2. **Reference-image strategy (key gpt-image-2 difference):**
   - gpt-image-2 accepts **max 5 `referenceImages` per request** (Arcads-enforced; observed `400 Max 5 reference image(s) allowed`).
   - Always include the **hero** as the first ref (the anchor).
   - For angles 2-5: pass `[hero]` only (4 free slots, but you have no prior angles yet anyway).
   - For angles 6+: pass `[hero, angle_N-1, angle_N-2, angle_N-3, angle_N-4]` — the most recent 4 angles plus the hero. This keeps continuity from the most recent successful gen while still anchoring on the hero.
   - **Don't include angles that drifted.** If angle N looked off, exclude it from the reference set for angle N+1.
3. Strengthen the textual prompt for each angle (gpt-image-2 leans on text more than Nano Banana does):
   - Start with the angle description (see the table below).
   - **Re-state the full character description verbatim** — don't shortcut with "the same person from the reference." Include hair / skin / eye / build / outfit. Yes it's verbose; this is what holds identity on gpt-image-2.
   - Add: `"The exact same person — same face, hair, body, and clothing as the reference images. Photorealistic, visible skin texture."`
   - Specify white studio background.
   - Include angle-specific lighting and pose.
4. Call `POST /v2/images/generate` for each with:
   - Same `productId`, `projectId`, `aspectRatio: 9:16` as hero
   - `model`: `gpt-image-2`
   - `referenceImages`: the array per step 2 above (max 5)
   - The angle-specific prompt
5. Fire all 9 in sequence (not parallel — avoid rate limits), poll all concurrently.
6. QA each per the Step 3 checklist.

### The 10 angles (same as Nano Banana version)

| # | File name | Angle | Prompt prefix | Pose/lighting notes |
|---|-----------|-------|---------------|---------------------|
| 1 | `01-hero-front.jpg` | Full body front (hero) | `Full body front view, head to toe.` | Direct eye contact, relaxed stance, weight on one hip, full outfit visible, soft even lighting from both sides |
| 2 | `02-3q-left.jpg` | 3/4 left | `Three-quarter view from the left.` | Angled 45° to camera-left, looking toward lens, soft directional light from camera-right |
| 3 | `03-3q-right.jpg` | 3/4 right | `Three-quarter view from the right.` | Angled 45° to camera-right, looking toward lens, soft directional light from camera-left |
| 4 | `04-profile-left.jpg` | Profile left | `Left profile view.` | Full side profile facing camera-left, hair falls naturally, soft rim light from behind |
| 5 | `05-profile-right.jpg` | Profile right | `Right profile view.` | Full side profile facing camera-right, hair falls naturally, soft rim light from behind |
| 6 | `06-face-closeup.jpg` | Face close-up | `Face close-up, tight crop.` | Forehead to chin, hair down and loose, every detail visible, soft beauty lighting, catchlights in both eyes |
| 7 | `07-back-shoulder.jpg` | Back/over shoulder | `Back view, looking over her/his shoulder.` | Faces away, looking back over right shoulder, playful glance, hair visible from behind |
| 8 | `08-medium-portrait.jpg` | Medium portrait | `Front-facing medium portrait, waist up.` | Waist-up framing, direct eye contact, warm expression, soft even lighting |
| 9 | `09-full-body-3q.jpg` | Full body 3/4 | `Full body three-quarter view.` | Full length, angled 45° to camera-left, walking toward camera, same full outfit |
| 10 | `10-above-angle.jpg` | Above angle | `Slightly above angle, looking up at camera.` | Camera positioned slightly above, chin tilted up, bright smile, soft overhead lighting |

### gpt-image-2 angle-specific tips

- **Profile shots (4, 5)** drift the most on gpt-image-2 — facial features can shift between profile and 3/4. Pass `[hero, 02-3q-left]` as refs for `04-profile-left` (the 3/4 anchors the facial features in a related angle).
- **Face close-up (6)** is where identity really shows. If drift appears here, regenerate with the hero PLUS angle 8 (medium portrait, same front-facing pose) as refs.
- **Back shoulder (7)** — the face is partial. Less drift risk. Just hero as ref is fine.

## Step 5: QA all images

Follow [nano-banana.md](nano-banana.md) QA checklist for each image. Additionally check for **cross-image consistency:**
- Same hair color, texture, and length across all 10
- Same face shape and features (gpt-image-2 is more prone to subtle drift here — be strict)
- Same skin tone and distinguishing features (freckles in same positions, etc.)
- Same clothing

If any image drifts significantly, note it when presenting results. **Offer the user a "regenerate with stronger anchor" option:** rerun that angle with `[hero, 01-hero-front, 06-face-closeup]` (or whatever angles render most cleanly) as refs, plus an even more verbose textual character description.

## Step 6: Save to references folder

Same folder naming + file naming convention as the Nano Banana version — see [character-sheet.md § Step 6](character-sheet.md). The folder structure does NOT change; this version's outputs live alongside any Nano Banana outputs.

**Tip — distinguishing gpt-image-2 vs Nano Banana outputs:**

If you generate a character with BOTH models for A/B testing, save them in sibling folders with a `-gpt` suffix:

```
references/influencers/emma-redhead-wavy-freckles-green-eyes-fair/         # Nano Banana version
references/influencers/emma-redhead-wavy-freckles-green-eyes-fair-gpt/     # gpt-image-2 version
```

The agent should treat each folder as a fully independent character sheet — don't cross-reference angles from the Nano Banana folder when generating gpt-image-2 angles (or vice versa); the rendering styles differ enough that mixing breaks consistency.

## Credit cost

gpt-image-2 has **no published credit rate** — Arcads exposes no billing endpoint. Check `logs/arcads-api.jsonl` for a recent `creditsCharged` value on this model, or the `MASTER_CONTEXT.md` rate table.

**If neither has a figure, do not show a placeholder as an estimate.** Say the per-image cost is unknown on this account, then calibrate: get approval for the hero image alone (`--n 1`), read its `creditsCharged`, write it into `MASTER_CONTEXT.md`, and only then price the remaining 9. Once the rate `R` is known:

```
Hero image:     1 × gpt-image-2 = R
9 angle images: 9 × gpt-image-2 = 9 × R
─────────────────────────────────────────
Total:          10 generations  = ~10 × R
```

Plus any QA retry generations (~2 per character sheet is typical for gpt-image-2 vs ~1 for Nano Banana). **Show the cost breakdown and get user confirmation before generating** — gpt-image-2 is typically more expensive per image than Nano Banana 2, so this isn't a "swap and forget" decision.

## Using a gpt-image-2 character sheet for subsequent workflows

Once the character sheet exists, it can be used as input for:

- **Product showcase** ([product-showcase.md](product-showcase.md)) — use the hero image + product photo to generate the influencer holding the product. Use `gpt-image-2` again for the showcase still if you want the rendering style to match the sheet.
- **Influencer recreation** ([influencer-recreation.md](influencer-recreation.md)) — skip the "analyze reference" step since the character already exists.
- **Video generation** — upload the hero (or any angle) as `startFrame` for Veo 3.1 or `refImageAsBase64` for Sora 2. Note: video models like Veo / Seedance may render the character with a slight rendering-style shift since they're not gpt-image-2-native; mention this to the user before they spend on video.
- **UGC selfie-style** ([ugc-selfie-style.md](ugc-selfie-style.md)) — gpt-image-2 has a slightly stylized aesthetic that can fight against "iPhone selfie" realism cues. Consider using the Nano Banana sheet for UGC use cases even if the gpt-image-2 sheet exists for the same character.

**Cross-model rendering style:** if you mix references from the gpt-image-2 sheet with a Nano Banana generation request, the model will average between styles. Pick one model per derived workflow for cleanest output.

## Example

**User says:** "Create a 20-year-old female influencer redhead — use ChatGPT Image not Nano Banana"

**Agent expands to:**
> A 20-year-old female influencer with natural deep-auburn red hair, mid-length and softly wavy, fair skin with light freckles scattered across the bridge of her nose and high cheekbones, almond-shaped emerald-green eyes, slim athletic build with narrow shoulders, soft natural makeup, wearing a fitted white t-shirt and dark fitted jeans with white sneakers. Clean white studio background, photorealistic, visible skin texture with subtle pores, fine flyaway hairs catching light, individual eyelashes visible.

(Note the extra anatomy specificity vs the Nano Banana example — gpt-image-2 needs the verbose anchor.)

**Folder name:** `emma-redhead-wavy-freckles-green-eyes-fair-gpt`

**Descriptor tags:** redhead, wavy, freckles, green-eyes, fair

**Flow:** Generate hero (gpt-image-2) → user approves → generate 9 angles with `[hero]` + recent angles as refs (max 5 total) → QA strictly for identity drift → save to `-gpt` folder → done.
