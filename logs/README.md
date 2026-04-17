# kie.ai API logs

This directory contains **append-only logs** of every kie.ai API generation call made by the agent. The logs power smarter cost estimation over time and give you a local audit trail of what was generated when.

## Files

- **`kie-api.jsonl`** — one JSON object per line. Every `POST` to a generation endpoint (`/api/v1/jobs/createTask`, `/api/v1/veo/generate`) appends one line when the request is fired and updates the same line with final status after polling completes.
- **`arcads-api.archive.jsonl`** — frozen historical log from when this repo targeted the Arcads API. Different schema (uses `assetId`, `productId`, `projectId`, `creditsCharged`). Keep for reference; do not append to it.

## Entry schema

```json
{
  "timestamp": "2026-04-17T19:18:24.611Z",
  "endpoint": "POST /api/v1/jobs/createTask",
  "model": "bytedance/seedance-2",
  "taskId": "b7f3e9c2-8a4d-4e1f-9c6b-2f8d7a3e5b1c",
  "request": {
    "duration": 15,
    "resolution": "720p",
    "aspect_ratio": "9:16",
    "audio": true,
    "firstFrameUrlPresent": true,
    "lastFrameUrlPresent": false,
    "referenceImageUrlsCount": 0,
    "referenceVideoUrlsCount": 0,
    "referenceAudioUrlsCount": 0,
    "imageInputCount": 0,
    "generationType": null,
    "promptWordCount": 340
  },
  "response": {
    "successFlag": 1,
    "state": "success",
    "generationTimeSec": 207,
    "resultUrlsCount": 1,
    "error": null
  }
}
```

## What to log and NOT to log

**DO log:**
- `taskId` (public identifier)
- Model slug and endpoint family
- Request config (durations, resolutions, aspect ratios, boolean flags)
- **Counts** of reference URLs (not the URLs themselves — they may be private)
- Word count of the prompt (not the prompt text)
- Final `successFlag`, state, elapsed time
- Error messages from `data.error` (these are diagnostic, no user data)

**Do NOT log:**
- `KIE_API_KEY`, `Authorization` headers, or any secret
- Full prompt text (prompts can contain user brief details; log the word count instead)
- Reference URLs (the user's private Imgur / Supabase / R2 URLs shouldn't be appended to a plaintext log)
- `resultUrls[]` content (they may be temporary; log the count)

## How the agent uses this file

- **Before any new generation:** the agent reads this log to cross-check that the rate in `MASTER_CONTEXT.md` roughly matches historical runs. If a model's typical generation time has shifted (e.g. Seedance started taking twice as long), that's an early signal to flag.
- **After each generation:** append the request metadata at POST time (with `successFlag: 0`, `state: "pending"`), then update the same line after polling completes with final status and elapsed time.
- **Cost reconciliation:** kie.ai does not return a per-call cost figure on the task response. To reconcile costs, the agent will periodically ask the user to check their [kie.ai billing page](https://kie.ai/billing) and update `MASTER_CONTEXT.md` if the effective rates have changed.

Logs are **not gitignored** — historical usage data across sessions is valuable. But because they contain no secrets and no prompt text, they're safe to commit.
