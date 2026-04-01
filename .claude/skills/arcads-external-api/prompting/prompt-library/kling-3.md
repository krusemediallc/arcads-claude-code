# Kling 3.0 — prompts for Arcads

**Vendor guide:** [Kling — video model user guide](https://kling.ai/quickstart/klingai-video-3-model-user-guide)

## Arcads API note

The published OpenAPI does **not** expose a dedicated `POST .../kling/...` route. Generated assets may show `type: "kling_30"` in `GET /v1/assets/{id}`. In practice, teams often reach Kling-style output via Arcads **b-roll** or **scene** flows (`POST /v1/b-roll`, `POST /v1/scene`) depending on workspace configuration. Confirm with Arcads if your generations are not using Kling as expected.

## Checklist (from Kling guide habits)

- [ ] Subject, environment, and **motion path** described clearly.
- [ ] Separate **style** vs **content** when the guide recommends it.
- [ ] If using reference or start frames (base64 fields on b-roll/scene DTOs), say how motion should treat them.

## Template

```text
{{SUBJECT}}. {{ACTION_MOTION}}. Environment: {{ENV}}. Camera: {{CAM}}. Mood: {{MOOD}}. Avoid: {{NEGATIVE}}.
```

## Example

```text
Coffee pours in slow motion into a ceramic mug on a wooden counter, steam rising. Soft window light, shallow depth of field, calm ASMR pacing. No text overlays.
```

## Typical Arcads body

`CreateBRollDto` or `CreateSceneDto` — see [reference.md](../../reference.md) for required fields.
