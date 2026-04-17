# Seedance 2.0 — model guide

**kie.ai route:** `POST /api/v1/jobs/createTask` with `"model": "bytedance/seedance-2"`
**Polling:** `GET /api/v1/jobs/recordInfo?taskId=<id>`

## API parameters (inside the `input` object)

kie.ai wraps everything in `{model, input: {...}}`. Put the fields below inside `input`.

| Field | Required | Value / Range | Notes |
|-------|----------|---------------|-------|
| `model` (top-level) | yes | `"bytedance/seedance-2"` | |
| `input.prompt` | yes | string | 100–260 words sweet spot (see below) |
| `input.aspect_ratio` | no | `"9:16"`, `"16:9"` | No `1:1`. Default `9:16` for UGC/social. |
| `input.duration` | no | 4–15 (integer seconds) | Continuous range, not an enum. Default to 15 for full-length clips. |
| `input.resolution` | no | `"480p"`, `"720p"` | Default `720p`. |
| `input.first_frame_url` | no | public HTTPS URL | Start-frame image. Host the file first — see SKILL.md → "Reference images: hosting and public URLs". |
| `input.last_frame_url` | no | public HTTPS URL | End-frame image (when supported). |
| `input.reference_image_urls` | no | array of public HTTPS URLs (max 3) | Style / product references. |
| `input.reference_video_urls` | no | array of public HTTPS URLs | Seedance 2.0 exclusive. |
| `input.reference_audio_urls` | no | array of public HTTPS URLs | Seedance 2.0 exclusive. |
| `input.audio` | no | boolean | Seedance 2.0 exclusive. Ask the user before each generation. |

**Not supported:** base64 image inputs (must be URLs). kie.ai has no `productId`, `projectId`, or `nbGenerations` — to generate multiple variations, fire N parallel `createTask` calls.

### `@(img1)` reference image mapping

The Seedance 2.0 prompting templates use `@(img1)` / `@(img2)` / `@(img3)` tokens inline in the prompt text to reference product images. In the API:

- Pass the corresponding images via the `input.reference_image_urls` array (index 0 = `@(img1)`, index 1 = `@(img2)`, etc.).
- **Keep the `@(img1)` tokens in the prompt text.** The model may interpret them as pointers to the reference images. If a generation ignores the reference image, try removing the token and relying solely on the `reference_image_urls` array as a fallback.

This mapping needs confirmation during the first real generation — document findings in `MASTER_CONTEXT.md`.

### Example request body

```json
{
  "model": "bytedance/seedance-2",
  "input": {
    "prompt": "15 seconds UGC style skincare review video...",
    "duration": 15,
    "aspect_ratio": "9:16",
    "resolution": "720p",
    "audio": true,
    "reference_image_urls": ["https://i.imgur.com/xxx.jpg"]
  }
}
```

## Seedance 2.0 platform guide

These rules are specific to how Seedance 2.0 interprets prompts. Apply them on top of whichever style template you use.

### Prompt length

Keep prompts between **100 and 260 words**. Shorter prompts produce vague results. Longer ones overwhelm the model and cause it to lose focus on key details.

### Prompt structure

Seedance 2.0 responds best to this order:

```
Subject + Action + Camera + Style + Constraints
```

- **Subject** — who/what is in the scene. Age, clothing, expression, posture all help.
- **Action** — what happens. Present tense, one primary movement per shot.
- **Camera** — framing (wide, medium, close-up) and movement (dolly-in, pan, handheld).
- **Style** — visual tone: lighting, color grading, atmosphere.
- **Constraints** — reduce artifacts: "maintain face consistency," "steady motion," "no distortion."

### Be explicit about motion

The model can't guess intensity from a still reference. Instead of "she picks up the bottle," write "she slowly picks up the bottle with her right hand, turning it toward the camera." Degree adverbs — **slowly, gently, quickly, casually, deliberately** — make a noticeable difference.

### Timestamps for precise timing

For multi-beat sequences, timestamps give control over pacing:

```
[00:00] A guy sits in his car, holding an electrolyte packet. Medium shot, dashboard light.
[00:05] He pours the packet into his water bottle and shakes it. Close-up on hands.
[00:09] He takes a sip, pauses, nods with raised eyebrows. Back to medium shot.
[00:13] He holds the packet up to the camera, half-smile. "Yeah these are legit."
```

Timestamps work well for:
- Multi-shot sequences with clear choreography
- Controlling pacing (preventing the model from rushing)
- Style or camera transitions within a single clip

Keep each segment focused on **one main action**. Clear timing = cleaner motion.

### Reference image consistency

When using `@(img1)` / `@(img2)` / `@(img3)` reference images, tell the model to keep them consistent:

- "The product from @(img1) must remain visually unchanged in every shot."
- "Maintain product design and label details throughout."
- "Keep outfit unchanged across all cuts."

This prevents visual drift where the product subtly changes between shots.

### Style keywords

Always include at least one style anchor:
- `documentary` — natural, observational feel
- `photorealistic` — grounded in reality, no stylization
- `commercial` — polished but still natural (use sparingly for UGC)
- `handheld` — reinforces the phone-filmed look

**Avoid:** `cinematic`, `anime`, `studio` — these pull away from UGC authenticity. For premium/product-hero styles, use `dramatic` or `premium` instead of `cinematic`.

### Forbidden words

Never use in Seedance 2.0 prompts: `cinematic`, `professional`, `stunning`, `8k`, `studio`, `perfect`.

### Iteration tips

If a generation is close but not right, adjust **one element at a time**:
1. Action looks good but framing is off → adjust camera description
2. Pacing is rushed → add timestamps or reduce dialogue
3. Product drifts between shots → add consistency constraint
4. Motion is too stiff → add degree adverbs (slowly, casually, deliberately)

## Duration and dialogue

Seedance 2.0 supports **4–15 seconds** (continuous, not an enum). Use the script word count to auto-select:

| Script word count | Duration |
|-------------------|----------|
| 1–8 words | 4–5s |
| 9–15 words | 6–8s |
| 16–25 words | 9–12s |
| 26–35 words | 13–15s |
| **36+ words** | **Too long** — offer to split into multiple clips |

For no-dialogue styles (product hero, premium reveal), default to **15s** for maximum visual impact.

Embed dialogue in the `prompt` field using natural phrasing (e.g., `She speaks: "text here"` or `He says: "text here"`).

## Style template directory

Pick the template that matches the user's goal, then read its file before composing the prompt:

| User goal | Style template | Key trait |
|-----------|---------------|-----------|
| UGC selfie-style product review / testimonial | [seedance-2-ugc.md](seedance-2-ugc.md) | 9-layer formula: person + setting + jump cuts + technical flaws |
| Dark-background premium product reveal (no person) | [seedance-2-premium-reveal.md](seedance-2-premium-reveal.md) | Void stage + text narrative + dramatic lighting |
| Elemental product hero — splash, mist, effects (no person) | [seedance-2-product-hero.md](seedance-2-product-hero.md) | Product-only with environmental interaction |
| Studio lookbook with voiceover (polished, multi-look) | [seedance-2-studio-lookbook.md](seedance-2-studio-lookbook.md) | Voiceover narration over styled product shots |
| Fast-paced feature walkthrough / demo | [seedance-2-feature-walkthrough.md](seedance-2-feature-walkthrough.md) | Feature-per-beat physical demos with dialogue |
| **Reverse-engineer a reference video** into a reusable template | [../analyze-video/SKILL.md](../analyze-video/SKILL.md) | Extract frames → analyze style → generate new template |
| **Clone a specific video ad** for a different product | [../clone-ad/SKILL.md](../clone-ad/SKILL.md) | Analyze source → adapt for user's product → generate |

If none of the above fit, use the platform guide rules in this file directly and compose a custom prompt following the Subject + Action + Camera + Style + Constraints structure.

### Cross-reference: existing UGC guide

The repo also has [ugc-selfie-style.md](ugc-selfie-style.md) — a cross-model UGC guide for Sora 2 / Veo 3.1. The Seedance-specific [seedance-2-ugc.md](seedance-2-ugc.md) has a richer 9-layer formula optimized for Seedance 2.0's strengths. Use the Seedance version when generating with `model: "bytedance/seedance-2"`.

## Adaptation checklist (all styles)

Before submitting any Seedance 2.0 prompt, verify:

- [ ] **Word count** — prompt is between 100–260 words
- [ ] **Duration** — set based on dialogue word count (4–15s) or default 15s for no-dialogue
- [ ] **Aspect ratio** — `9:16` (vertical/social) or `16:9` (landscape) — no `1:1`
- [ ] **Motion specificity** — actions describe degree/direction, not just "moves"
- [ ] **Consistency anchors** — product/outfit described as unchanged across shots
- [ ] **No forbidden words** — no "cinematic," "professional," "stunning," "8k," "studio," "perfect"
- [ ] **@(img1) included** — if product image is provided, referenced in prompt text
- [ ] **Style anchor** — at least one style keyword (documentary, photorealistic, etc.)
- [ ] **Timestamps** — used for multi-beat sequences to control pacing
