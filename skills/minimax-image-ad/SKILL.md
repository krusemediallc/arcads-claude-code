---
name: minimax-image-ad
description: >-
  Generate standalone text-to-image assets with MiniMax image-01 through the
  global or China API. Use when a user requests MiniMax image generation,
  regional routing, or downloadable URL/base64 image output.
---

# MiniMax image generation

Generate text-to-image assets with MiniMax and save every returned image to disk.
The bundled client uses only the Python standard library.

## Prerequisites

- Set `MINIMAX_API_KEY` in the shell or in `.env`.
- Use Python 3.10 or newer.

## Configuration

- Global region: `https://api.minimax.io/v1/image_generation`
- China region: `https://api.minimaxi.com/v1/image_generation`
- Default model: `image-01`
- Optional model: `image-01-live`
- Response formats: `url` and `base64`

The client sends `model`, `prompt`, `response_format`, and `n`. It also supports
`aspect_ratio`, paired `width`/`height`, `seed`, and `prompt_optimizer`. An aspect
ratio cannot be combined with explicit dimensions.

## Generate

```bash
python3 skills/minimax-image-ad/scripts/generate_image.py \
  --prompt "A clean studio photograph of the product" \
  --aspect-ratio 1:1 \
  --n 2 \
  --out generated/minimax
```

Use `--region cn_zh` for the China endpoint. Use `--response-format base64` when
the API should return encoded image content instead of temporary URLs. URL
responses are downloaded immediately because they expire after 24 hours.

Each successful image produces one JSON line on stdout with `variant`, `path`,
`model`, `region`, and `response_format`. Progress and errors go to stderr. The
client validates `base_resp.status_code`, reads `data.image_urls`, and reports
`metadata.success_count` and `metadata.failed_count`.

## Checks

```bash
python3 -m unittest discover -s skills/minimax-image-ad/tests -v
```

## Official API documentation

- Global: <https://platform.minimax.io/docs/api-reference/image-generation-t2i>
- China: <https://platform.minimaxi.com/docs/api-reference/image-generation-t2i>
