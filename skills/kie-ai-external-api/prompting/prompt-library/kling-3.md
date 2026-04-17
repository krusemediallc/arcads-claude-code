# Kling 3.0 — prompts for kie.ai

**kie.ai route:** `POST /api/v1/jobs/createTask` with `"model": "kling-3.0/video"` (or `"kling-2.6/video"` for the older tier).
**Polling:** `GET /api/v1/jobs/recordInfo?taskId=<id>`
**Vendor guide:** [Kling — video model user guide](https://kling.ai/quickstart/klingai-video-3-model-user-guide)

## kie.ai API note

kie.ai exposes Kling directly via the unified `createTask` endpoint. For short product-only or motion-only clips (pours, textures, short b-roll moments), call Kling 3.0 with a short `duration` — there is no separate b-roll or scene endpoint.

## Checklist (from Kling guide habits)

- [ ] Subject, environment, and **motion path** described clearly.
- [ ] Separate **style** vs **content** when the guide recommends it.
- [ ] If using a first-frame reference, describe how motion should treat it.

## Template

```text
{{SUBJECT}}. {{ACTION_MOTION}}. Environment: {{ENV}}. Camera: {{CAM}}. Mood: {{MOOD}}. Avoid: {{NEGATIVE}}.
```

## Example

```text
Coffee pours in slow motion into a ceramic mug on a wooden counter, steam rising. Soft window light, shallow depth of field, calm ASMR pacing. No text overlays.
```

## Example JSON body

```json
{
  "model": "kling-3.0/video",
  "input": {
    "prompt": "Coffee pours in slow motion into a ceramic mug...",
    "duration": 5,
    "aspect_ratio": "9:16"
  }
}
```

For a start-frame animation, add `"first_frame_url": "https://i.imgur.com/xxx.jpg"` inside `input`. Reference images must be hosted at a public HTTPS URL — see `SKILL.md` → "Reference images: hosting and public URLs."

## Required `input` fields (kie.ai)

`prompt` is required; `duration` and `aspect_ratio` are commonly set. See [reference.md](../../reference.md) for the full field list per Kling tier.
