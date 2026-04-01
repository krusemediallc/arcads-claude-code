# Sora 2 — prompts for Arcads

**Arcads route:** `POST /v1/sora2/generate/video` (`StartSora2Dto`).  
**Vendor guide (read for craft):** [OpenAI — Sora 2 prompting guide](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide)

## Checklist (after reading the vendor guide)

- [ ] Clear subject and setting; camera behavior described (not just “cinematic”).
- [ ] Motion: what moves, what stays stable across the clip.
- [ ] Lighting and style named explicitly if important.
- [ ] If using `refImageAsBase64`, describe how motion should relate to the reference.

## Template

```text
{{HOOK_OPEN}}. {{SUBJECT}} in {{SETTING}}. Camera: {{CAMERA_MOVE}}. Lighting: {{LIGHTING}}. Style: {{STYLE}}. Audio mood: {{AUDIO_MOOD}}. End on {{ENDING_IMAGE}}.
```

## Example (replace IDs in JSON separately)

```text
A skincare founder holds the bottle to camera in a bright bathroom, morning light through blinds. Slow push-in, shallow depth of field. Warm, trustworthy, no medical claims. Soft upbeat ambient. End on product and smile.
```

## Required JSON fields (Arcads)

`productId`, `prompt`, `aspectRatio`, `duration` — see [reference.md](../../reference.md).
