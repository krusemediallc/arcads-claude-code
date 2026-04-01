# Product showcase — AI person with product

**Use when:** The user wants to generate a video of an AI person holding, using, or demonstrating a physical product.

## Workflow

```
User provides product image(s)
        |
        v
Agent writes Nano Banana prompt
(AI person + product interaction)
        |
        v
POST /V2/images/generate
with refImageAsBase64 (product photo)
        |
        v
Nano Banana generates still image
(person holding/using product)
        |
        v
User approves still image
        |
        v
Still -> startFrame for video gen
(Veo 3.1 / Sora 2 / Kling 3.0)
        |
        v
Final product showcase video
```

## Step-by-step

### 1. Collect product info

Ask the user for:
- **Product image(s)** — photos of the item from different angles
- **Product context** — what it is, key features, target audience (check `MASTER_CONTEXT.md` or the Arcads product fields for existing context)
- **Video intent** — UGC selfie-style? Polished ad? Unboxing?
- **Person description** — what should the AI person look like? (Or reuse an existing influencer prompt from `MASTER_CONTEXT.md`)
- **Nano Banana engine** — default **Nano Banana 2** (`nano-banana-2`), or **Nano Banana Pro** (`nano-banana`) if they prefer (see [nano-banana.md](nano-banana.md))

### 2. Compose the Nano Banana image prompt

Follow the template below. The prompt should describe:

1. **The person** — age, gender, appearance, wardrobe, expression, pose
2. **The product interaction** — how they hold it, where it sits in frame, what angle, how prominent
3. **Match the video intent** — if the final video is UGC selfie-style, the still should already look like a selfie. If it's a polished product ad, frame accordingly
4. **Include the product image** as `refImageAsBase64` so Nano Banana can composite it

### 3. Generate the still image

1. Auto-upscale the product image if needed (see SKILL.md "Image handling").
2. Call `POST /V2/images/generate` (note uppercase V2) with:
   - `productId` and `projectId` (from session folder)
   - `model` — **`nano-banana-2`** unless the user chose Nano Banana Pro (`nano-banana`)
   - `prompt` — the Nano Banana product showcase prompt
   - `aspectRatio` — match the video intent (`9:16` for reels, `16:9` for landscape, `1:1` for square)
   - `refImageAsBase64` — the product photo
3. Poll `GET /v1/assets/{id}` until `generated`.
4. **Post-generation QA:** Inspect the still per [nano-banana.md](nano-banana.md) (hands, product edges, merged geometry). **Regenerate** with a refined prompt if needed — up to **2** retries after the first attempt. **Only then** treat the still as ready to show.
5. Assign **all** relevant assets to the session project via `POST /v1/assets/add-to-project`.
6. Show the **QA-passed** (or best-effort after max retries) image to the user.

### 4. Get user approval

- Show the generated still to the user — **after** internal QA and auto-retries in step 3–4.
- **Wait for explicit approval** before proceeding to video.
- If the user wants a different creative direction (not just defect fixes), iterate on the prompt and regenerate per SKILL.md credit rules.

### 5. Generate video from approved still

1. Upload the approved image via `POST /v1/file-upload/get-presigned-url` → `PUT` to S3.
2. Pass the `filePath` as `startFrame` in the video model of choice:
   - **Veo 3.1:** `POST /v1/veo31/generate/video` with `startFrame`
   - **Sora 2:** `POST /v1/sora2/generate/video` with `refImageAsBase64`
3. Include dialogue/script in the video prompt (see SKILL.md "Script and dialogue").
4. Poll until `generated`, assign to session project, return watch/download URLs.

## Prompt template

```text
{{PERSON_DESCRIPTION}}. They are {{INTERACTION}} a {{PRODUCT_DESCRIPTION}}.
Setting: {{SETTING}}. Camera: {{CAMERA}}. Lighting: {{LIGHTING}}.
The product is {{PRODUCT_PLACEMENT}} — clearly visible, in-focus, natural grip.
Style: {{STYLE}}. Avoid: studio lighting, floating product, unnatural hand pose.
```

## Example

```text
A 25-year-old woman with shoulder-length brown hair in a casual white t-shirt,
smiling warmly at camera. She is holding a small amber glass skincare bottle in
her right hand at chin height, label facing camera. Setting: bright modern
bathroom, morning light through frosted window. Camera: front-facing selfie
angle, slightly above eye level. The product is centered in the lower third of
frame — clearly visible, natural grip with fingertips around the bottle.
Style: authentic, unfiltered, soft natural tones. Avoid: studio lighting,
floating product, perfect skin retouching.
```

## Script prompting for video stage

Once the starting frame is approved and video generation begins, the video model prompt should:

- Reference the starting frame ("continues from the still image")
- Add **motion and dialogue** — what the person says about the product
- Follow the relevant model's prompt library ([veo-3-1.md](veo-3-1.md), [sora-2.md](sora-2.md), [kling-3.md](kling-3.md))
- Pull product context from `MASTER_CONTEXT.md` or the Arcads product fields (`description`, `mainFeatures`, `painPoint`)

### Video prompt template

```text
{{PERSON}} holds {{PRODUCT}} and speaks directly to camera. {{ACTION_BEATS}}.
Product details: {{KEY_FEATURES}}. Tone: {{TONE}}. Setting: {{SETTING}}.
Camera: {{CAMERA}}. Dialogue: "{{SCRIPT}}". {{STYLE_AND_IMPERFECTIONS}}.
```

## Product context via API

Products in Arcads carry marketing context (not images via the API):

```
POST /v1/products
{
  "name": "Product Name",
  "description": "What the product is",
  "targetAudience": "Who it's for",
  "mainFeatures": ["feature 1", "feature 2", "feature 3"],
  "painPoint": "Problem it solves",
  "perceived": "How customers see it"
}
```

Product images are managed through the Arcads dashboard (`pictureId` on the product object), not the API. For product showcase workflows, the product image is passed directly as `refImageAsBase64` in the Nano Banana image generation call.

## Tips

- **Product fidelity:** If the generated still distorts the product (wrong label, color shift), try a cleaner product photo with white/neutral background.
- **Hand pose:** "natural grip with fingertips" in the prompt helps avoid the common AI issue of unnatural hand poses around objects.
- **Consistency:** Save the approved person prompt in `MASTER_CONTEXT.md` for reuse across multiple product shoots with the same AI influencer.
