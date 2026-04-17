# Nano Banana — prompts for kie.ai

**Vendor guide:** [Google Cloud — Ultimate prompting guide for Nano Banana](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana)

## kie.ai API endpoint

**Image generation:** `POST /api/v1/jobs/createTask` with a Nano Banana model slug.

Use it for:
- Influencer recreation stills (see [influencer-recreation.md](influencer-recreation.md))
- Product showcase starting frames (see [product-showcase.md](product-showcase.md))
- Standalone Nano Banana images (product heroes, lifestyle shots, etc.)

Poll `GET /api/v1/jobs/recordInfo?taskId=<id>` until `status` is `generated` (or the kie.ai equivalent success state).

## Model selection (`model` field on `createTask`)

| User-facing name | API `model` value | When to use |
|------------------|-------------------|-------------|
| **Nano Banana 2** (default) | `nano-banana-2` | Use unless the user asks for Pro. |
| **Nano Banana Pro** (optional) | `nano-banana-pro` | When the user explicitly wants Pro. |

**Agent behavior:** Default to `nano-banana-2`. Before the first image call in a session, ask once: *"Use default Nano Banana 2, or Nano Banana Pro?"* If they do not care, use `nano-banana-2`.

**Credits:** kie.ai bills per generation in USD. Check the user's cost table in `MASTER_CONTEXT.md` for the exact rate — ask if it isn't listed.

## Request body (kie.ai `{model, input}` wrapper)

See [reference.md](../../reference.md) for the full schema. Key fields:

- `model` (required) — `nano-banana-2` (default) or `nano-banana-pro`
- `input.prompt` (required) — follow the template and checklist below
- `input.aspect_ratio` — `1:1`, `16:9`, `9:16`
- `input.image_input` (optional) — array of public HTTPS URLs for reference images. Base64 is not supported.

**Generation time:** ~35 seconds typical for Nano Banana images (varies).

## Checklist

- [ ] Follow the vendor guide for framing **subject**, **style**, and **constraints**.
- [ ] State whether the output should be **photoreal**, **illustration**, **product hero**, etc.
- [ ] Call out **text on image** only if the pipeline supports legible text for your use case.
- [ ] All reference image URLs are public HTTPS (not base64, not local paths).
- [ ] After `status: generated`, run **post-generation QA** (see below) before treating the image as final.

### Post-generation QA (mandatory)

After downloading or viewing the result, check for:

- Extra or missing **hands** or **fingers**; wrong finger count; fused or blurred digits
- Wrong number of **limbs**; duplicated or missing arms/legs; impossible **joints** or poses
- **Face:** duplicate or merged features, asymmetry beyond natural range, distorted eyes or teeth
- **Objects:** merged geometry, floating items, melted product edges (product shots)
- **Artifacts:** obvious seams, texture soup, stray body parts at frame edges

If anything looks off, follow **Regeneration loop** — do not pass a defective still to the user as the only option without at least one retry (unless the user explicitly waives QA).

### Regeneration loop

1. **Inspect** the image from the asset URL (or local download).
2. If **defective:** compose a **new prompt** that names the fix (e.g. "exactly two hands visible, five fingers each," "single coherent face," "product label sharp and readable"). Keep the rest of the creative intent; add corrective constraints rather than resending the exact same JSON.
3. Call `POST /api/v1/jobs/createTask` again with the same `model`, `aspect_ratio`, and `image_input` reference inputs as before unless you are intentionally changing them.
4. **Cap:** at most **2** regeneration attempts after the first image (**3** total generations per deliverable). After that, describe remaining issues, list asset URLs, and ask the user how to proceed.
5. **Cost:** each generation bills separately — note cumulative cost when reporting. QA retries use the [QA-fix exception](../../SKILL.md) (no second pre-confirmation, but still billed).

Full agent steps: [SKILL.md — Generated image QA](../../SKILL.md#generated-image-qa-mandatory).

## Template

```text
{{SUBJECT}}. Style: {{STYLE}}. Composition: {{COMPOSITION}}. Lighting: {{LIGHT}}. Background: {{BG}}. Avoid: {{AVOID}}.
```

## Example

```text
Minimal product hero: matte black earbuds on concrete, soft three-point lighting, subtle reflection, no people, no extra props.
```

## curl example

```bash
source .env && curl -sS -X POST \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nano-banana-2",
    "input": {
      "prompt": "Minimal product hero: matte black earbuds on concrete, soft three-point lighting, subtle reflection, no people, no extra props.",
      "aspect_ratio": "1:1"
    }
  }' \
  "https://api.kie.ai/api/v1/jobs/createTask"
```
