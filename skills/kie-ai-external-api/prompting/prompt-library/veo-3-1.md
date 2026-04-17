# Veo 3.1 — prompts for kie.ai

**kie.ai route:** `POST /api/v1/veo/generate` with `"model": "veo3"` — note Veo uses the legacy flat body shape, NOT the `{model, input}` wrapper.
**Polling:** `GET /api/v1/veo/record-info?taskId=<id>`
**Vendor guide:** [Google Cloud — Ultimate prompting guide for Veo 3.1](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)

## Checklist

- [ ] Describe scene, action, and **how the shot evolves** over time (first frame → later beats).
- [ ] Specify **style** (film stock, animation, documentary, etc.) if it matters.
- [ ] If using **reference images** or **start/end frames**, use the correct `generationType` (see below) and put public HTTPS URLs in `imageUrls`.
- [ ] **ALWAYS** end the prompt with `"No subtitles, no captions, no text overlays."` — Veo 3.1 sometimes burns subtitles into the video if not explicitly excluded.

## Template

```text
{{OPENING_BEAT}}. {{ACTION_OVER_TIME}}. Setting: {{SETTING}}. Camera: {{CAMERA}}. Style: {{STYLE}}. Lighting: {{LIGHT}}. Optional dialogue: {{DIALOGUE}}.
```

## Example

```text
Wide shot of a city rooftop at golden hour; runner ties shoes, then jogs toward camera as the camera tracks sideways. Documentary handheld feel, warm natural light, subtle film grain. No logos on clothing. No subtitles, no captions, no text overlays.
```

## `generationType` options

Veo's body shape requires you to declare how you're using reference images:

| `generationType` | `imageUrls` | Use when |
|------------------|-------------|----------|
| `TEXT_2_VIDEO` | `[]` | No image refs — pure text-to-video |
| `FIRST_AND_LAST_FRAMES_2_VIDEO` | `[firstFrameUrl]` or `[firstFrameUrl, lastFrameUrl]` | Animate from a start frame (optionally to an end frame) |
| `REFERENCE_2_VIDEO` | `[url1, url2, url3]` (up to 3) | Style / subject reference images |

## Example JSON body (text-to-video)

```json
{
  "prompt": "Wide shot of a city rooftop at golden hour... No subtitles, no captions, no text overlays.",
  "model": "veo3",
  "generationType": "TEXT_2_VIDEO",
  "imageUrls": [],
  "aspect_ratio": "9:16",
  "resolution": "720p"
}
```

## Example JSON body (start-frame animation)

```json
{
  "prompt": "The subject from the first frame walks forward slowly...",
  "model": "veo3",
  "generationType": "FIRST_AND_LAST_FRAMES_2_VIDEO",
  "imageUrls": ["https://i.imgur.com/xxx.jpg"],
  "aspect_ratio": "9:16",
  "resolution": "720p"
}
```

Reference images must be hosted at a public HTTPS URL. See `SKILL.md` → "Reference images: hosting and public URLs." Base64 is no longer supported.

## Required body fields (kie.ai)

`prompt`, `model`, `generationType`, `imageUrls`, `aspect_ratio`, `resolution` — see [reference.md](../../reference.md).
