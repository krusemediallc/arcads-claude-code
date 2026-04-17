# Influencer recreation from reference image

**Use when:** The user provides a photo of an influencer (or themselves) and wants to recreate that person in AI-generated content via kie.ai.

## Required flow (do NOT skip steps)

1. User provides a reference image
2. Agent analyzes the image (Step 1 below)
3. Agent writes a Nano Banana-style recreation prompt (Step 2)
4. **Generate a still image** using `POST /api/v1/jobs/createTask` with `model: "nano-banana-2"`
5. **User approves** the still image
6. **Only after approval** → generate video using the approved image as a Veo 3.1 / Sora 2 first-frame reference

**kie.ai route for image:** `POST /api/v1/jobs/createTask` with `model: "nano-banana-2"` (or `nano-banana-pro`). Host the original reference photo at a public HTTPS URL and pass it via `input.image_input` so Nano Banana can match the person's appearance. Poll `GET /api/v1/jobs/recordInfo?taskId=<id>` until complete, then retrieve the image URL.

**kie.ai route for video (after approval):** Host the approved still at a public HTTPS URL, then:
- **Veo 3.1:** `POST /api/v1/veo/generate` with `generationType: "FIRST_AND_LAST_FRAMES_2_VIDEO"` and `imageUrls: [stillUrl]`
- **Sora 2:** `POST /api/v1/jobs/createTask` with `model: "sora-2-image-to-video"` and `input.first_frame_url: stillUrl`

## Workflow

### Step 1: Analyze the reference image

When the user shares an image, **dissect it systematically** using this checklist. Describe what you see — do not invent or assume details not visible.

**Face and features:**
- Estimated age range
- Skin tone (light / medium / olive / tan / deep / dark)
- Face shape (oval, round, square, heart, etc.)
- Distinctive features (dimples, freckles, beauty marks, jawline)

**Hair:**
- Color (natural shade — e.g. "warm chestnut brown," not just "brown")
- Length (above shoulder / shoulder-length / mid-back / long)
- Texture and style (straight, wavy, curly, coily; loose, pulled back, braided, etc.)
- Parting (center, side, none visible)

**Eyes and brows:**
- Eye color if visible
- Brow shape (arched, straight, thick, thin)
- Makeup if present (winged liner, smoky, natural, none)

**Makeup and skin:**
- Level (bare-faced, natural/minimal, glam, editorial)
- Lip color
- Skin finish (dewy, matte, natural)

**Body and pose:**
- Build (petite, slim, athletic, curvy, plus-size)
- Posture and pose (relaxed, confident, leaning, arms crossed, etc.)
- Hand position and gestures

**Clothing and accessories:**
- Garment type, color, fabric texture (e.g. "cream satin button-up blouse")
- Jewelry (earrings, necklace, rings — material and style)
- Other accessories (sunglasses, hat, bag)

**Lighting and environment:**
- Light direction and quality (golden hour side light, overhead fluorescent, ring light, window light)
- Background (blurred rooftop, bedroom, studio, street, nature)
- Color temperature (warm, neutral, cool)

**Vibe / energy:**
- Expression (warm smile, serious, candid laugh, pensive)
- Overall aesthetic (editorial, casual, glam, sporty, bohemian)

### Step 2: Write the recreation prompt

Combine the analysis into **one dense paragraph** (80-150 words) following this structure:

```
[Subject description with physical features] in [setting/environment].
[Clothing and accessories described specifically].
[Pose and expression]. [Lighting described as physical properties].
[Camera and style]. [Skin and texture realism cues].
```

**Rules:**
- Use **specific visual language**, not vague adjectives ("warm chestnut wavy hair past her shoulders" not "nice hair")
- Describe **lighting as physics** ("soft directional golden-hour light from camera-left creating gentle shadows on the right side of her face") not mood words alone
- Include **at least one texture cue** for realism ("visible skin texture," "fabric sheen," "individual hair strands catching light")
- Do NOT use celebrity names or real people's names in the prompt
- State aspect ratio and any framing (close-up, medium shot, etc.)

### Step 3: Present to user for approval of the PROMPT

Show the user:
1. Your **breakdown** of what you observed in the image (the analysis)
2. The **recreation prompt** you wrote
3. Ask if anything needs adjusting before generating the image

### Step 4: Generate the still image (Nano Banana)

Once the user approves the prompt:

1. Read **[nano-banana.md](nano-banana.md)** and follow the vendor guide's formula.
2. Host the reference image at a public HTTPS URL (see main SKILL.md → "Reference images: hosting and public URLs"). Auto-upscale if longest side < 1024px (see SKILL.md "Image handling: auto-upscale small inputs"). Base64 is not supported.
3. Call `POST /api/v1/jobs/createTask` with:
   - `model` — default **`nano-banana-2`**; use **`nano-banana-pro`** if the user asked for **Nano Banana Pro** (see [nano-banana.md](nano-banana.md))
   - `input.prompt` — the Nano Banana-aligned recreation prompt
   - `input.aspect_ratio` — match the reference image or user preference
   - `input.image_input` — `[referenceImageUrl]` (improves consistency)
4. Poll `GET /api/v1/jobs/recordInfo?taskId=<id>` until complete.
5. **Post-generation QA:** Visually inspect the still (see [nano-banana.md](nano-banana.md) — Post-generation QA and Regeneration loop). If you see defects (extra fingers, bad hands, etc.), regenerate with a refined prompt — up to **2** retries after the first attempt. **Do not show the user a still as "the result" until QA passes or retries are exhausted** (if still bad after retries, explain and show attempts).
6. Retrieve the image URL for the **QA-passed** (or best-effort) still and **show it to the user** next to the original reference.

### Step 5: User approves the still image

- Show the recreation result alongside the original reference — **after** internal QA and any auto-retries above.
- **Wait for explicit user approval** before proceeding to video.
- If the user is not satisfied, iterate on the prompt and regenerate (this is separate from automatic QA retries; follow cost confirmation rules in SKILL.md for new user-directed generations).

### Step 6: Generate video from approved image

Only after the user says the still looks good:

1. Host the approved image at a public HTTPS URL (see main SKILL.md → "Reference images: hosting and public URLs").
2. For Veo 3.1: `POST /api/v1/veo/generate` with `generationType: "FIRST_AND_LAST_FRAMES_2_VIDEO"` and `imageUrls: [stillUrl]`. For Sora 2: `POST /api/v1/jobs/createTask` with `model: "sora-2-image-to-video"` and `input.first_frame_url: stillUrl`.
3. Poll until complete (`/api/v1/veo/record-info` or `/api/v1/jobs/recordInfo`), then return watch/download URLs.

## Example

**Reference analysis:**
> Woman in her mid-20s, medium olive skin tone, oval face with subtle dimples. Warm chestnut brown wavy hair, shoulder-length, center-parted, individual strands catching light. Hazel-green eyes, natural arched brows. Minimal makeup — light coverage, nude lip, dewy skin finish. Slim build, relaxed upright posture. Wearing a cream satin button-up blouse, small gold hoop earrings. Soft golden-hour light from camera-left, shallow depth of field, blurred urban rooftop background. Warm confident smile with direct eye contact. Casual editorial vibe.

**Recreation prompt:**
```text
A woman in her mid-20s with medium olive skin, oval face, and subtle
dimples. Warm chestnut brown wavy hair, shoulder-length, center-parted,
individual strands catching golden light. Hazel-green eyes, natural
arched brows, minimal makeup with nude lip and dewy skin. She wears a
cream satin button-up blouse and small gold hoop earrings. Relaxed
upright posture, warm confident smile with direct eye contact. Soft
directional golden-hour light from camera-left creates gentle shadows.
Shallow depth of field, blurred urban rooftop background. Medium
close-up, editorial portrait style. Visible skin texture, fabric
sheen on blouse. Photorealistic.
```

## Tips for consistency across multiple generations

- Save the approved prompt text in `MASTER_CONTEXT.md` under a heading like **"Influencer: [name/alias]"** so future sessions can reuse it without re-analyzing.
- When generating video from the recreation, host the Nano Banana image output at a public HTTPS URL and pass the URL as the first-frame reference to Veo 3.1 (`imageUrls[0]`) or Sora 2 (`input.first_frame_url`). See [reference.md](../../reference.md) for the full field list.
- Small wording changes between generations will drift the face. Keep the core description **frozen** and only vary pose, clothing, or setting in subsequent prompts.
