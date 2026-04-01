# Veo 3.1 — prompts for Arcads

**Arcads route:** `POST /v1/veo31/generate/video` (`StartVeo31Dto`).  
**Vendor guide:** [Google Cloud — Ultimate prompting guide for Veo 3.1](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)

## Checklist

- [ ] Describe scene, action, and **how the shot evolves** over time (first frame → later beats).
- [ ] Specify **style** (film stock, animation, documentary, etc.) if it matters.
- [ ] If using **reference images** or **start/end frames**, follow the API rules in [reference.md](../../reference.md) (mutual exclusions, presigned upload path).

## Template

```text
{{OPENING_BEAT}}. {{ACTION_OVER_TIME}}. Setting: {{SETTING}}. Camera: {{CAMERA}}. Style: {{STYLE}}. Lighting: {{LIGHT}}. Optional dialogue: {{DIALOGUE}}.
```

## Example

```text
Wide shot of a city rooftop at golden hour; runner ties shoes, then jogs toward camera as the camera tracks sideways. Documentary handheld feel, warm natural light, subtle film grain. No logos on clothing.
```

## Required JSON fields (Arcads)

`productId`, `prompt`, `resolution`, `aspectRatio` — see [reference.md](../../reference.md).
