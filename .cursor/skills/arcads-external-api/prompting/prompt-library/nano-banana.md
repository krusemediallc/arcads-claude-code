# Nano Banana — prompts for Arcads

**Vendor guide:** [Google Cloud — Ultimate prompting guide for Nano Banana](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana)

## Arcads API endpoint

**Image generation:** `POST /V2/images/generate` (note uppercase V2).

This is the dedicated Nano Banana route for still-image generation. Use it for:
- Influencer recreation stills (see [influencer-recreation.md](influencer-recreation.md))
- Product showcase starting frames (see [product-showcase.md](product-showcase.md))
- Standalone Nano Banana images (product heroes, lifestyle shots, etc.)

Asset types `nano-banana` and `nano-banana-2` appear on `AssetResponseDto`. Poll with `GET /v1/assets/{id}` until `status` is `generated`.

For **video** generation via Nano Banana, use `POST /v1/b-roll` or `POST /v1/scene` — model routing may be workspace- or server-side.

## Model selection (`model` field on `POST /V2/images/generate`)

The Arcads OpenAPI enum (`CreateImageDto.model`) only has two Nano Banana strings: `nano-banana` and `nano-banana-2`. In this repo we use:

| User-facing name | API `model` value | When to use |
|------------------|-------------------|-------------|
| **Nano Banana 2** (default) | `nano-banana-2` | Use unless the user asks for Pro. |
| **Nano Banana Pro** (optional) | `nano-banana` | When the user explicitly wants Pro / the first-gen Nano Banana engine. |

**Agent behavior:** Default to `nano-banana-2`. Before the first image call in a session, ask once: *"Use default Nano Banana 2, or Nano Banana Pro?"* If they do not care, use `nano-banana-2`.

**Credits:** Pricing may differ per model — use `data.creditsCharged` on the asset response and the user's cost table in `MASTER_CONTEXT.md`. (Example observed: 0.03 for `nano-banana` in one test.)

## Request body (`CreateImageDto` / image generate) — confirmed 2026-04-01

See [reference.md](../../reference.md) for the full schema. Key fields:

- `productId` (required) — UUID of the Arcads product
- `prompt` (required) — follow the template and checklist below
- `model` (required) — for Nano Banana stills, default **`nano-banana-2`**; optional **`nano-banana`** (Nano Banana Pro). Other image engines: `gpt-image`, `soul`, `grok_image`, `seedream`, `seedream_5_lite`
- `aspectRatio` (required) — `1:1`, `16:9`, `9:16`
- `referenceImages` (optional) — array of `filePath` strings from presigned upload (OpenAPI); see [reference.md](../../reference.md) for reference limits per model
- `projectId` (optional) — assign to a session project

**Generation time:** ~35 seconds typical for Nano Banana images (varies).

## Checklist

- [ ] Follow the vendor guide for framing **subject**, **style**, and **constraints**.
- [ ] State whether the output should be **photoreal**, **illustration**, **product hero**, etc.
- [ ] Call out **text on image** only if the pipeline supports legible text for your use case.
- [ ] Use `POST /V2/images/generate` (uppercase V2) — not `/v2/`.

## Template

```text
{{SUBJECT}}. Style: {{STYLE}}. Composition: {{COMPOSITION}}. Lighting: {{LIGHT}}. Background: {{BG}}. Avoid: {{AVOID}}.
```

## Example

```text
Minimal product hero: matte black earbuds on concrete, soft studio three-point lighting, subtle reflection, no people, no extra props.
```

## curl example

```bash
source .env && curl -sS -X POST \
  -H "Authorization: $ARCADS_BASIC_AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "...",
    "prompt": "Minimal product hero: matte black earbuds on concrete, soft studio three-point lighting, subtle reflection, no people, no extra props.",
    "model": "nano-banana-2",
    "aspectRatio": "1:1"
  }' \
  "https://external-api.arcads.ai/V2/images/generate"
```
