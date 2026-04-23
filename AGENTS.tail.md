## This repo specifically

- **API:** Arcads external API (`https://external-api.arcads.ai`).
- **Auth:** HTTP Basic via `ARCADS_BASIC_AUTH` (pre-encoded `Basic ...` header) or `ARCADS_API_KEY` as the Basic password. Values in `.env` must be **single-quoted** due to special characters.
- **Skills:**
  - `arcads-external-api` — main API reference (endpoints, auth, polling, asset routing).
  - `generate-youtube-thumbnail` — YouTube thumbnail batch workflow on top of the Nano Banana 2 image endpoint.
- **Setup check:** `./scripts/check-arcads-env.sh`.
