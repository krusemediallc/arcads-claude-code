# Sora 2 — prompts for kie.ai

**kie.ai route:** `POST /api/v1/jobs/createTask` with `"model": "sora-2-text-to-video"` (or `"sora-2-image-to-video"` if a first-frame image URL is used). For the Pro tier, use `"sora-2-pro-text-to-video"` / `"sora-2-pro-image-to-video"`.
**Polling:** `GET /api/v1/jobs/recordInfo?taskId=<id>`
**Vendor guide (read for craft):** [OpenAI — Sora 2 prompting guide](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide)

## Checklist (after reading the vendor guide)

- [ ] Clear subject and setting; camera behavior described (not just "cinematic").
- [ ] Motion: what moves, what stays stable across the clip.
- [ ] Lighting and style named explicitly if important.
- [ ] If using a `first_frame_url`, describe how motion should relate to the reference.

## Template

```text
{{HOOK_OPEN}}. {{SUBJECT}} in {{SETTING}}. Camera: {{CAMERA_MOVE}}. Lighting: {{LIGHTING}}. Style: {{STYLE}}. Audio mood: {{AUDIO_MOOD}}. End on {{ENDING_IMAGE}}.
```

## Example (text-to-video)

```text
A skincare founder holds the bottle to camera in a bright bathroom, morning light through blinds. Slow push-in, shallow depth of field. Warm, trustworthy, no medical claims. Soft upbeat ambient. End on product and smile.
```

## Example JSON body (text-to-video)

```json
{
  "model": "sora-2-text-to-video",
  "input": {
    "prompt": "A skincare founder holds the bottle to camera in a bright bathroom...",
    "aspect_ratio": "9:16",
    "duration": 8
  }
}
```

## Example JSON body (image-to-video)

```json
{
  "model": "sora-2-image-to-video",
  "input": {
    "prompt": "A skincare founder holds the bottle to camera...",
    "first_frame_url": "https://i.imgur.com/xxx.jpg",
    "aspect_ratio": "9:16",
    "duration": 8
  }
}
```

Reference images must be hosted at a public HTTPS URL. See `SKILL.md` → "Reference images: hosting and public URLs." Base64 is no longer supported.

## Required `input` fields (kie.ai)

`prompt` is required; `aspect_ratio` and `duration` are commonly set. See [reference.md](../../reference.md) for the full field list per Sora variant.
