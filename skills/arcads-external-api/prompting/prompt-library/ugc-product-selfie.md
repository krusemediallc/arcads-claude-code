# UGC product selfie — character + product + style reference workflow

**Use when:** The user wants to generate a UGC-style selfie image of one of their AI influencers holding/using a product. Combines a character sheet, a product photo, and style reference images into a single Nano Banana generation.

## Required inputs

| Input | Source | Role in `referenceImages` |
|-------|--------|---------------------------|
| **Character hero** | `references/influencers/{name}/01-hero-front.png` | Identity — face, hair, build, skin |
| **Product photo** | `references/products/{product}.png` | What they're holding/using |
| **Style references** (2-4) | `references/aesthetics/{style}/` | Visual vibe — lighting, framing, quality |

All inputs are uploaded via `POST /v1/file-upload/get-presigned-url` → `PUT` to S3 → passed as `referenceImages` array.

## Reference image order

```
referenceImages = [
  character_hero_filePath,    # position 1: identity anchor
  product_filePath,           # position 2: product context
  style_ref_1_filePath,       # position 3+: style/vibe
  style_ref_2_filePath,
  style_ref_3_filePath,       # 3 style refs is the sweet spot
]
```

Nano Banana supports up to 14 `referenceImages`. The character hero should always be first (strongest identity signal). 3 style references is the sweet spot — enough to establish the vibe without diluting the character identity.

## Prompt formula

The prompt must fight the model's tendency toward polished, studio-quality output. UGC works because it feels raw and real.

### Structure

```
[Camera hardware] + [Framing] + [Character description] + [Action with product] + [Expression] + [Outfit] + [Setting/background] + [Imperfection block] + [Negative cues]
```

### The imperfection block (CRITICAL)

This is what separates convincing UGC from "AI influencer photo." Always include at least 4-5 of these:

- `slight motion blur on hair strands`
- `slightly overexposed highlights on forehead and nose`
- `visible image grain and noise`
- `iPhone front camera wide-angle lens distortion on the extended arm`
- `slightly off-center framing, tilted a few degrees`
- `washed out flat color grading`
- `soft focus — nothing is tack sharp`
- `uneven ambient indoor lighting with one side of face slightly in shadow`
- `caught mid-blink or mid-word, not a perfect expression`

### Skin realism block (CRITICAL — always include)

AI models default to airbrushed, flawless skin which instantly reads as fake. Always describe **subtle, natural skin** in the character description. Pick 3-4 of these cues based on the character:

- `natural skin with visible pores`
- `slight unevenness in skin tone`
- `minor undereye shadows`
- `a hint of shine on the nose and forehead from natural oils`
- `slight pinkness on cheeks and nose` (works well for fair skin)
- `minor skin texture variation`
- `faint undereye shadows`
- `the kind of skin you see on a real person's unfiltered front camera`

**Do NOT use:** acne, pimples, breakouts, blemishes, redness, or anything that sounds like a skin condition. The goal is "real person, not retouched" — not "person with skin problems."

Place these cues **inline with the character description**, not in the imperfection block. Example: `"...warm tan skin with visible pores, slight unevenness in skin tone, minor undereye shadows, a hint of shine on the nose and forehead from natural oils..."`

### Negative cues (always include)

```
No retouching, no beauty filter, no studio lighting, not a professional photo, not overly polished, not perfectly composed, not tack sharp. No airbrushed skin, no flawless complexion.
```

### Example prompt (tested and approved)

```
Raw iPhone front-camera selfie video frame grab. A 25-year-old mixed race
woman with voluminous curly honey-brown hair, warm tan skin with visible
pores, slight unevenness in skin tone, minor undereye shadows, a hint of
shine on the nose and forehead from natural oils — beauty mark on right
cheek, green eyes. She is on her couch holding up a tall purple and gold
Arcads Artificial Cola can, talking mid-sentence to camera with a candid
unposed expression — mouth slightly open, caught between words, not
smiling perfectly.

Casual oversized beige hoodie. Cozy messy apartment background —
houseplants, throw pillows, warm lamp glow — slightly out of focus.

CRITICAL STYLE: This must look like an unedited frame pulled from a real
iPhone selfie video, NOT a professional photo. Include these imperfections:
slight motion blur on hair strands, slightly overexposed highlights on
forehead and nose, visible image grain and noise, iPhone front camera
wide-angle lens distortion on the arm holding the phone, slightly
off-center framing tilted a few degrees, washed out flat color grading,
soft focus — nothing is tack sharp, uneven ambient indoor lighting with
one side of face slightly in shadow. No retouching, no beauty filter,
no studio lighting, no airbrushed skin, no flawless complexion. The image
should feel raw, unpolished, and authentically amateur.
```

## Step-by-step flow

### Step 1: Gather inputs

1. **Character:** Ask which influencer (by name). Load their `01-hero-front.png`.
2. **Product:** Ask which product or check `references/products/`. If multiple, ask user to pick.
3. **Style:** Default to `references/aesthetics/ugc-selfie/` for UGC. If other style folders exist, ask user which vibe. Load 3 images from the chosen style folder (pick the most varied ones if more than 3 exist).
4. **Scene:** Ask for the scene/setting (bedroom, car, kitchen, outdoors, etc.) and outfit. If the user doesn't specify, pick a natural casual setting.

### Step 2: Upload all reference images

Upload all files via presigned URL:
- 1 character hero
- 1 product photo
- 2-4 style references (3 is ideal)

Total: 4-6 `referenceImages` per call.

### Step 3: Compose the prompt

1. Start with `"Raw iPhone front-camera selfie video frame grab."`
2. Describe the character using their key visual traits from the character sheet folder name (hair, eyes, skin, build, distinguishing features).
3. **Add skin realism cues inline** with the character description — pick 3-4 from the skin realism block above (e.g., "visible pores, slight unevenness in skin tone, minor undereye shadows, hint of shine from natural oils"). This is non-negotiable.
4. Describe the action with the product — holding it up, drinking it, showing it to camera, etc.
5. Describe a candid mid-speech expression — NOT a perfect smile.
6. Specify the outfit (casual, contextual to the scene).
7. Describe the background/setting — make it lived-in and slightly messy.
8. **Add the full imperfection block** — this is non-negotiable. Without it, the output will look too polished.
9. End with negative cues.

### Step 4: Generate

Call `POST /V2/images/generate` with:
- `productId` and `projectId`
- `model`: `nano-banana-2`
- `prompt`: the composed prompt
- `aspectRatio`: `9:16`
- `referenceImages`: array of all uploaded `filePath` values

Default to **3 variations** so the user can compare. Fire all 3 in sequence with a small delay.

### Step 5: Present and iterate

1. Download all variations.
2. **Open them for the user** using `open <path>` (macOS).
3. QA each for anatomy issues (hands holding the product are the most common problem area).
4. Present as a numbered list.
5. Ask user which they prefer, or if they want adjustments.

## Scene suggestions

When the user doesn't specify a scene, rotate through these for variety:

| Scene | Background cues | Outfit suggestion |
|-------|----------------|-------------------|
| **Living room couch** | Throw pillows, houseplants, warm lamp, slightly messy | Oversized hoodie or loungewear |
| **Bedroom** | Bed with rumpled sheets, nightstand, fairy lights | Tank top, casual tee |
| **Car** | Leather seats, sunroof visible, buildings through window | Sweater, jacket |
| **Kitchen** | Counter, coffee mug, morning light through window | Robe, casual tee |
| **Bathroom mirror** | Mirror selfie, bathroom counter, towels | Getting-ready outfit |
| **Outdoor cafe** | Table, coffee cup, street in background | Casual date outfit |
| **Desk/office** | Laptop, notebook, desk lamp | Work-from-home casual |

## Style folder system

Style references live in `references/aesthetics/{style}/`. Each folder should contain 3-5 images that define the visual language.

### Available styles (add more by creating new folders with reference images)

| Folder | Vibe | When to use |
|--------|------|-------------|
| `ugc-selfie/` | iPhone selfie, casual, authentic, imperfect | Product reviews, "OMG you guys" moments, talking to camera |
| `cinematic/` | Moody lighting, shallow DOF, film grain | Brand storytelling, premium product launches |
| `lifestyle/` | Outdoor, natural light, aspirational but real | Wellness, fitness, food & drink brands |
| `editorial/` | High contrast, fashion magazine, posed | Fashion, beauty, luxury brands |

To add a new style: create the folder, drop in 3-5 reference images, and the agent will automatically use them when you ask for that style.

## Credit cost

```
3 variations × Nano Banana 2 = 0.09 credits ($0.90)
```

Plus any retries for QA issues. Show cost and get confirmation before generating.

## Common issues and fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Image looks too polished/professional | Missing imperfection block | Add ALL imperfection cues — don't skip any |
| Character face doesn't match | Too many style references diluting identity | Reduce style refs to 2, keep character hero first |
| Product is unrecognizable | Text on product garbled (common AI limitation) | Describe the product visually in the prompt (color, shape, size) rather than relying on text |
| Hands look wrong | AI hand generation is imperfect | Add "naturally gripping the can/bottle, anatomically correct hand with five fingers" to prompt; regenerate if needed |
| Background too clean | Default AI behavior | Explicitly describe mess: "cluttered coffee table, stacked books, charging cable visible" |

## Combining with video

Once the user approves a UGC still, it can be used as a `startFrame` for video generation.

### Veo 3.1 (RECOMMENDED for UGC stills → video)

**Use `startFrame`** — the video literally starts from the approved image. Face, pose, scene, product placement are all preserved from frame one. This is the correct path for animating UGC stills.

1. Upload approved still via `POST /v1/file-upload/get-presigned-url` → `PUT` to S3 → get `filePath`
2. `POST /v1/veo31/generate/video` with `startFrame: filePath` + dialogue in `prompt`
3. **Resolution:** Default to `720p` — 4K and 1080p show no visible quality difference for UGC-style content and produce 3-8x larger files. Use `1080p` only if the user specifically requests higher resolution.
4. **Human motion cues (CRITICAL):** Always include at least 3-4 natural movement cues in the prompt. Without these, the video will look like a frozen mannequin staring at camera. Pick from:
   - Eye behavior: "briefly breaks eye contact, glances down at the product, then looks back at camera"
   - Head/face: "slight head tilts while talking, nods along with own words, raises eyebrows for emphasis"
   - Body: "shifts weight, leans toward camera for emphasis, adjusts grip on the product"
   - Scene motion: "takes a small step, turns the product to show another angle"
5. **ALWAYS end prompt with:** `"No subtitles, no captions, no text overlays."`
6. See [ugc-selfie-style.md](ugc-selfie-style.md) for full UGC video prompting formula and cue library

### Sora 2 (NOT recommended for UGC stills → video)

Sora 2's `refImageAsBase64` is a **style/mood reference**, not a literal starting frame. It will generate the video primarily from the text prompt and use the image as loose inspiration only. The character's face, pose, and scene will NOT match the approved still.

**Only use Sora 2 when:**
- You need longer duration (up to 20s) and don't need exact frame-one fidelity
- You're generating from a text prompt only (no starting frame)
- The image is meant as a style reference, not a literal reproduction
