# Character sheet — generate an AI influencer from a text description

**Use when:** The user wants to create a new AI influencer from scratch by describing them in plain English. Generates a 10-image character sheet (multiple angles, white background) that becomes the reference set for all future generations with that character.

## Required flow (do NOT skip steps)

1. User describes the influencer in plain English (e.g., "20-year-old female redhead")
2. Agent expands the description into a detailed visual prompt (Step 1)
3. Agent presents the expanded prompt for user review (Step 2)
4. **Generate 1 hero front portrait** (Step 3)
5. **User approves the hero image** — do NOT skip this step
6. **Generate 9 remaining angles** using the hero as `referenceImages` (Step 4)
7. **QA all images** (Step 5)
8. **Save to `references/influencers/`** using the naming convention (Step 6)

## Step 1: Expand the user's description

Take the user's plain-English description and expand it into a detailed visual prompt. Fill in any unspecified details with natural, photorealistic defaults. The prompt should be specific enough to produce a consistent character.

**Base prompt structure:**

```
A {age}-year-old {gender} influencer with {hair color} {hair texture} {hair length} hair, {skin tone} skin with {distinguishing features}, {eye color} eyes, {build} build, {makeup level}, wearing {clothing}. Clean white studio background, photorealistic, visible skin texture, individual hair strands catching light.
```

**What to specify (fill in defaults if the user doesn't mention):**
- **Age:** Exact number, not a range
- **Hair:** Color, texture (straight/wavy/curly), length (shoulder-length/long/short)
- **Skin:** Tone + one distinguishing feature (freckles, clear, beauty mark, etc.)
- **Eyes:** Color
- **Build:** Slim, athletic, curvy, etc.
- **Makeup:** Soft natural / minimal / none
- **Clothing:** Default to a fitted white t-shirt (neutral, doesn't distract from the character)

**Rules:**
- Use specific visual language, not vague adjectives
- Do NOT use celebrity names or real people's names
- Keep clothing simple and neutral — the character sheet is about the person, not the outfit
- Always include texture cues: "visible skin texture," "individual hair strands catching light"

## Step 2: Present the expanded prompt for approval

Show the user:
1. The expanded visual description you wrote
2. The 5 descriptor tags you'll use for the folder name (see naming convention below)
3. Ask if anything needs adjusting before generating

## Step 3: Generate the hero image (full body front)

This is the anchor image that defines the character. All other angles will reference it. **Use a full-body shot as the hero** — this gives the model complete visual context (face, hair, build, clothing, shoes, proportions) so every subsequent angle stays consistent. A medium portrait forces the model to invent the lower half for full-body angles.

1. Compose the hero prompt: prepend `"Full body front view, head to toe."` to the base prompt, add `"She/He looks directly at camera with a warm, confident expression. Relaxed stance, weight on one hip. Camera at eye level, soft even studio lighting from both sides."` Include the full outfit (e.g., jeans + white sneakers) in the hero prompt since this is the full-body reference.
2. Call `POST /V2/images/generate` with:
   - `productId` and `projectId` (from session folder)
   - `model`: `nano-banana-2` (default) or `nano-banana` (Pro)
   - `prompt`: the hero prompt
   - `aspectRatio`: `9:16`
3. Poll `GET /v1/assets/{id}` until `generated`.
4. **Post-generation QA:** Inspect for anatomy defects per [nano-banana.md](nano-banana.md). Regenerate with refined prompt if needed (up to 2 retries).
5. Download the image to the character's `references/influencers/` folder and **open it for the user** using `open <path>` (macOS) so they can review it at full resolution in Preview.
6. **Wait for explicit user approval.** This is the character — if they don't like it, iterate before generating 9 more images. Do NOT proceed without approval.

## Step 4: Generate 9 remaining angles

Once the hero is approved:

1. Upload the hero image via `POST /v1/file-upload/get-presigned-url` → `PUT` to S3 → get `filePath`.
2. For each of the 9 remaining angles, compose a prompt that:
   - Starts with the angle description
   - References the hero: `"The exact same person from the reference image — same face, same {hair description}, same {distinguishing features}, same {eye color} eyes, same {build} build, same {clothing}."`
   - Specifies white studio background, photorealistic
   - Includes angle-specific lighting and pose
3. Call `POST /V2/images/generate` for each with:
   - Same `productId`, `projectId`, `model`, `aspectRatio` as hero
   - `referenceImages`: `[hero_filePath]`
   - The angle-specific prompt
4. Fire all 9 in sequence (not parallel — to avoid rate limits), poll all concurrently.
5. QA each image per [nano-banana.md](nano-banana.md).

### The 10 angles

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

## Step 5: QA all images

Follow [nano-banana.md](nano-banana.md) QA checklist for each image. Additionally check for **cross-image consistency:**
- Same hair color, texture, and length across all 10
- Same face shape and features
- Same skin tone and distinguishing features
- Same clothing

If any image drifts significantly from the hero, note it when presenting results.

## Step 6: Save to references folder

### Folder naming convention

```
references/influencers/{name}-{hair_color}-{hair_style}-{feature}-{eye_color}-{skin_tone}/
```

**Format:** All lowercase, hyphens between words within a descriptor, hyphens between descriptors.

| Position | Category | Examples |
|----------|----------|----------|
| 1 | **Name** (human first name) | `emma`, `sofia`, `kai`, `marcus`, `luna` |
| 2 | **Hair color** | `redhead`, `blonde`, `brunette`, `black-hair`, `silver`, `auburn` |
| 3 | **Hair style** | `wavy`, `straight`, `curly`, `pixie`, `braided`, `bob`, `long-straight` |
| 4 | **Distinguishing feature** | `freckles`, `dimples`, `sharp-jaw`, `high-cheeks`, `beauty-mark`, `clear-skin` |
| 5 | **Eye color** | `green-eyes`, `blue-eyes`, `brown-eyes`, `hazel-eyes`, `gray-eyes` |
| 6 | **Skin tone** | `fair`, `olive`, `tan`, `deep`, `medium`, `porcelain` |

**Examples:**
- `emma-redhead-wavy-freckles-green-eyes-fair/`
- `sofia-brunette-straight-dimples-brown-eyes-olive/`
- `kai-blonde-curly-sharp-jaw-blue-eyes-tan/`
- `marcus-black-hair-fade-strong-brow-brown-eyes-deep/`

### File naming convention

Files are zero-padded and named by angle:

```
01-hero-front.jpg
02-3q-left.jpg
03-3q-right.jpg
04-profile-left.jpg
05-profile-right.jpg
06-face-closeup.jpg
07-back-shoulder.jpg
08-medium-portrait.jpg
09-full-body-3q.jpg
10-above-angle.jpg
```

`01-hero-front.jpg` is always the approved anchor image. The agent should use this as the primary `referenceImages` entry when generating new content with this influencer.

### After saving

- Assign all generated assets to the session project via `POST /v1/assets/add-to-project`
- **Open the full character folder** for the user using `open <folder_path>` (macOS) so they can review all 10 images at full resolution
- Present results as a numbered list showing all 10 angles
- Note total credits used

## Credit cost

```
Hero image:     1 × Nano Banana 2 = 0.03 credits
9 angle images: 9 × Nano Banana 2 = 0.27 credits
────────────────────────────────────────────────
Total:          10 generations     = 0.30 credits
```

Plus any QA retry generations (0.03 each). Show the cost breakdown and get user confirmation before generating.

## Using a character sheet for subsequent workflows

Once a character sheet exists in `references/influencers/`, it can be used as input for:

- **Product showcase** ([product-showcase.md](product-showcase.md)) — use the hero image + product photo to generate the influencer holding the product
- **Influencer recreation** ([influencer-recreation.md](influencer-recreation.md)) — skip the "analyze reference" step since the character already exists
- **Video generation** — upload the hero (or any angle) as `startFrame` for Veo 3.1 or `refImageAsBase64` for Sora 2
- **UGC selfie-style** ([ugc-selfie-style.md](ugc-selfie-style.md)) — use character sheet images as references, combine with UGC prompting formulas

When referencing an existing character, load `01-hero-front.jpg` as the primary reference. For maximum consistency, load multiple angles from the folder as additional `referenceImages` (up to 14 supported by Nano Banana).

## Example

**User says:** "Create a 20-year-old female influencer redhead"

**Agent expands to:**
> A 20-year-old female influencer with natural red hair, fair skin with light freckles across her nose and cheeks, green eyes, slim build, soft natural makeup, wearing a fitted white t-shirt. Clean white studio background, photorealistic, visible skin texture, individual hair strands catching light.

**Folder name:** `emma-redhead-wavy-freckles-green-eyes-fair`

**Descriptor tags:** redhead, wavy, freckles, green-eyes, fair

**Flow:** Generate hero → user approves → generate 9 angles with hero as reference → QA → save to folder → done.
