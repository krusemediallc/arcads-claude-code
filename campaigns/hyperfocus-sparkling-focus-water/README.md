# HYPERFOCUS Sparkling Focus Water — fast-paced cinematic ad (Seedance 2.5 via Arcads)

**Status (2026-09-14):** creative locked, prompt written, generation script tested offline against a stub of the Arcads API. **Not yet rendered** — the session that built this package had no Arcads credentials (the Arcads MCP connector needs an OAuth sign-in that a non-interactive cloud session cannot complete, and the cloud environment has no `.env` / `ARCADS_BASIC_AUTH`). Everything below renders the finished clip in one command once credentials are present.

## Render it (3 steps)

1. **Save the product image** (the white-to-blue HYPERFOCUS can on the grey backdrop) to `references/products/hyperfocus-can.png` (gitignored). Any PNG/JPG ≥ 1024 px on the long side works; smaller files are auto-upscaled.
2. **Credentials:** `./scripts/check-arcads-env.sh` must print `OK`. Locally that means `ARCADS_BASIC_AUTH` in `.env`. For Claude Code cloud sessions, add `ARCADS_BASIC_AUTH` as an environment variable in the environment's settings (Settings → Environments), or authorize the Arcads connector under claude.ai Settings → Connectors — either unblocks this for future sessions.
3. **Generate:**

```bash
# inspect the payload + credit estimate, spend nothing
python3 scripts/generate-seedance-video.py \
  --prompt-file campaigns/hyperfocus-sparkling-focus-water/prompt-seedance-2.5-15s.txt \
  --image references/products/hyperfocus-can.png \
  --name hyperfocus-cinematic --model seedance-2.5 --duration 15 --aspect 9:16 --resolution 720p --dry-run

# render (same command, --yes instead of --dry-run). Output: outputs/seedance/<timestamp>-hyperfocus-cinematic-v1.mp4
python3 scripts/generate-seedance-video.py \
  --prompt-file campaigns/hyperfocus-sparkling-focus-water/prompt-seedance-2.5-15s.txt \
  --image references/products/hyperfocus-can.png \
  --name hyperfocus-cinematic --model seedance-2.5 --duration 15 --aspect 9:16 --resolution 720p --yes
```

Add `--resolution 1080p` for the delivery master, `--aspect 16:9` for a landscape cut, `--n 2` for two takes of the same prompt, `--product-name "<your Arcads product>"` if the workspace has several products (the default is the first one). The script appends the run to `logs/arcads-api.jsonl` and puts the asset in the dated **Arcads API - YYYY-MM-DD** folder/project in the dashboard.

## Cost estimate (estimate only — confirm in the Arcads platform)

| Config | Estimate | Source |
|--------|---------:|--------|
| seedance-2.0 image-to-video, 15 s, 720p | ~720 credits | `skills/arcads-external-api/reference.md`, validated 2026-05-19 (~48 credits/sec) |
| **seedance-2.5, 15 s, 720p** (this ad) | **≥ ~720 credits** | no logged 2.5 runs yet; 2.0 rate used as the floor |
| seedance-2.5, 15 s, 1080p | unknown, plan for up to ~2× | — |

The script prints `GET /v1/credits` before and after the run and writes the actual `creditsCharged` into the log, so the second render of any config is priced from real data.

## Creative

**Product facts (from the can):** HYPERFOCUS — Sparkling Focus Water by Mr. Paid Social. L-Theanine + Natural Caffeine. Label claim: *"Holds Attention Longer."* Tall slim can, matte white fading to cobalt blue, silver rim, vertical bold blue HYPERFOCUS wordmark, white concentric-ring (target/ripple) icon at the colour transition.

**Concept — "Hold rate."** The audience is media buyers, so the ad talks like one. Line one names the job (*3 seconds to stop the scroll*), the product answers with its own label claim (*Holds attention longer*), and the ring icon on the can becomes the visual language for attention: water ripples, light pulses, a heartbeat that settles. No person, no dialogue (so no dialogue-approval gate), the can is the only subject — the Seedance *product hero* template pushed to a fast cut rhythm: seven shots in fifteen seconds, hard cuts, slow-motion impacts inside a fast edit, black void + wet mirror floor + cobalt light.

**Beat sheet (15 s, 9:16):**

| Time | Shot | Motion | Sound | Overlay |
|------|------|--------|-------|---------|
| 0:00 | Extreme macro, single drop onto still blue water | Ripple rings spread outward (echo of the ring icon) | Sub-bass hit | **3 SECONDS TO STOP THE SCROLL.** |
| 0:02 | Low angle, can slams onto the wet floor | Crown splash in slow motion, blue light in every droplet | Impact thud | — |
| 0:04 | Whip pan → extreme close-up of the HYPERFOCUS lettering | Condensation beads racing down, quick dolly-in | Whoosh | — |
| 0:05 | Top-down, tab cracks open | Fizz + cold mist bursting at the lens | Crack-hiss, fizz | — |
| 0:07 | Can spins, stops dead with the ring icon centred | Blue light pulses ripple across the floor on the beat | Heartbeat kick | **HOLDS ATTENTION LONGER.** |
| 0:10 | Rapid orbit, ice shards + droplets frozen mid-air | Speed-ramp to a dead stop on the front hero angle | Riser | — |
| 0:12 | End card, can centred in a settling pool | Hold | Steady heartbeat, resolve | **HYPERFOCUS / Sparkling Focus Water** |

**Prompt discipline:** Subject → Action → Camera → Style → Constraints, timestamped blocks, degree adverbs on every motion, product-consistency anchor (`@(img1)` identical in every shot, one can only), style anchors *dramatic / photoreal / premium*, none of the Seedance-unfriendly words (cinematic, professional, stunning, 8k, studio, perfect). Inside the 100–260 word guideline (the script warns if a prompt drifts outside it).

## Files

| File | Purpose |
|------|---------|
| `prompt-seedance-2.5-15s.txt` | Primary prompt — text overlays rendered by the model. |
| `prompt-seedance-2.5-15s-no-text.txt` | Same edit with no on-screen text and the upper third kept clear — use when the model garbles the words, then burn clean typography with the script below. |
| `overlays.json` | The three overlays with timings/positions (upper third, Reels-safe). |
| `burn-overlays.py` | `python3 campaigns/hyperfocus-sparkling-focus-water/burn-overlays.py --in <clip>.mp4 --out <clip>-titled.mp4` — ffmpeg drawtext, white bold type with a soft shadow, 0.15 s fades. Needs a full ffmpeg build (`brew install ffmpeg` / `apt install ffmpeg`); the pip `imageio-ffmpeg` wheel has no drawtext filter. |

## QA after the render

1. Watch for: label legible and unchanged across shots, exactly one can, no extra hands/objects, water/fizz physics plausible, text spelled correctly, cuts landing near the timestamps.
2. **Text garbled?** Re-render with `prompt-seedance-2.5-15s-no-text.txt` and run `burn-overlays.py`. Don't resend the identical payload hoping for a different result.
3. **Product drifts between shots?** Strengthen the consistency line ("the can from @(img1) must remain visually unchanged in every shot") and drop the orbit beat's ice shards.
4. **Pacing too slow?** Shorten the [00:07] and [00:10] blocks to one action each; too rushed → drop one beat rather than adding words.
5. Retry cap per the skill: two revised attempts, each billed at create time (a content-checker `failed` is not refunded).

## Changelog note for MASTER_CONTEXT.md

> **2026-09-14** — Decision: first Seedance 2.5 campaign package (`campaigns/hyperfocus-sparkling-focus-water/`). What changed: `scripts/generate-seedance-video.py` (one-command i2v runner), `seedance-2.5` documented in the arcads-external-api skill from the live OpenAPI spec (4–30 s, 1080p max, 30 refs, asset type `seedance_25`). Why: Seedance 2.5 was missing from the skill and no runner existed; the cloud session had no Arcads credentials, so the render itself is a one-command follow-up.
