# Arcads API logs

This directory contains **append-only logs** of every Arcads API generation call made by the agent. The logs power smarter credit-cost estimation over time.

## Files

- **`arcads-api.jsonl`** — one JSON object per line. Every `POST` to a generation endpoint (`/v2/videos/generate`, `/v2/images/generate`, `/v1/b-roll`, `/v1/scene`, etc.) gets one line.

  **Who writes it.** The two image-ad generators (`skills/chatgpt-image-ad/scripts/generate_image.py` and the Nano Banana sibling) append their own records automatically — one line per variant, written once the call reaches a terminal state (`generated` or failed), including failures. Disable with `--no-log`, redirect with `--log-file`. Every other endpoint is still the agent's job to log.

  **One append, not two.** Variants run concurrently, so rewriting a line in place after polling is not thread-safe. The scripts therefore write a single complete record at the end rather than appending on fire and updating later. A record with `"status": "failed"` and a non-null `response.error` is a call that was attempted; treat `creditsCharged: null` as unknown, not zero.

## Entry schema

```json
{
  "timestamp": "2026-04-09T19:18:24.611Z",
  "endpoint": "POST /v2/videos/generate",
  "model": "seedance-2.0",
  "assetId": "290dc89f-d763-4bcf-8da2-290caa00deef",
  "productId": "10b24deb-2ce7-47f7-8cf3-624b844658b8",
  "projectId": "0f1e0482-35f8-4ea6-96d9-dbf114f159bf",
  "request": {
    "duration": 15,
    "resolution": "720p",
    "aspectRatio": "9:16",
    "audioEnabled": true,
    "referenceImagesCount": 1,
    "referenceVideosCount": 0,
    "referenceAudiosCount": 0,
    "promptWordCount": 340
  },
  "response": {
    "status": "generated",
    "creditsCharged": 0.9,
    "generationTimeSec": 90,
    "videoUrl": "s3://... (presigned, expires)",
    "thumbnailUrl": "s3://... (presigned, expires)",
    "error": null
  },
  "session": {
    "folderName": "Arcads API - 2026-04-09"
  }
}
```

## How the agent uses this file

- **Before any new generation:** grep the log for entries with the same `model` + similar config and use the **actual recorded `creditsCharged`** to compute the estimate — not a hardcoded table.
- **After each generation:** append the request metadata and the final polled response (including `creditsCharged` and elapsed time).
- **When pricing rules emerge:** derive per-second or per-unit rates from recorded data and document them in `MASTER_CONTEXT.md`.

Logs are **not gitignored** — historical cost data across sessions is valuable. Do NOT log API keys, Authorization headers, or full prompt text (prompts can be large; store a word count instead).
