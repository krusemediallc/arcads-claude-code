## This repo specifically

- **APIs:** Arcads external API (`https://external-api.arcads.ai`) by default. The `nano-banana-image-ad` skill also supports Atlas Cloud (`https://api.atlascloud.ai/api/v1`) as an explicit opt-in provider.
- **Auth:** Arcads uses HTTP Basic via `ARCADS_BASIC_AUTH` (pre-encoded `Basic ...` header) or `ARCADS_API_KEY` as the Basic password. Atlas Cloud uses `ATLASCLOUD_API_KEY` as a Bearer token. Values in `.env` must be **single-quoted** due to special characters.
- **Skills:**
  - `arcads-external-api` — main API reference (endpoints, auth, polling, asset routing).
  - `generate-youtube-thumbnail` — YouTube thumbnail batch workflow on top of the Nano Banana 2 image endpoint.
  - **Image-ad ecosystem** (3 skills + shared 37-template library) — see [shared/skills/image-ad-prompting/OVERVIEW.md](shared/skills/image-ad-prompting/OVERVIEW.md):
    - `chatgpt-image-ad` — generate via Arcads `gpt-image-2` (typography / UI-mimicry creatives)
    - `nano-banana-image-ad` — generate `nano-banana-2`/`-pro`/`-edit` via Arcads by default or Atlas Cloud with `--provider atlas` (photoreal / lifestyle creatives)
    - `image-ad-clone` — single backend-agnostic skill that reverse-engineers existing ads into reusable templates (asks which backend to validate against at Phase 1; optionally cross-validates at Phase 8)
- **Setup check:** `./scripts/check-arcads-env.sh`.
