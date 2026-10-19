# Pixar-style ad — pipeline scripts

End-to-end shell + Python pipeline that backs the [guide](../prompting/guide.md). Use these as a starting point; copy them into a per-run directory and edit prompts/timings/durations to fit your campaign.

## Prerequisites

- `ARCADS_BASIC_AUTH` (preferred) or `ARCADS_API_KEY` in `.env` for still generation
- `MINIMAX_API_KEY` in `.env` for video generation
- `ELEVENLABS_API_KEY` in `.env`
- `ffmpeg` (Homebrew build is fine for video, but the Pillow caption renderer is used because Homebrew ffmpeg ships without `libass` / `drawtext`)
- `python3` with `Pillow` (`pip install Pillow`)
- `jq` (`brew install jq`)

## Per-run setup

```bash
export RUN_DIR="$HOME/runs/$(date +%Y-%m-%d)-<campaign-slug>"
export PRODUCT_ID="<arcads-product-uuid>"
export PROJECT_ID="<arcads-project-uuid>"   # create via POST /v1/projects
mkdir -p "$RUN_DIR"/{stills,clips,vo-beats,captions-png,references}
```

## Pipeline order

1. **Lock the cast sheet + write the 4-beat script** — see [guide](../prompting/guide.md). Storyboarding is human work; everything below assumes you have approved 5-7 stills' worth of prompts and per-beat VO copy.
2. **`generate-stills.sh`** — fire N gpt-image-2 calls in parallel. One per beat, optionally with reference images for character continuity.
3. **`poll-and-download.sh`** — poll asset IDs every 15s until generated, download to `$RUN_DIR/stills/`.
4. (manual) QA the stills. Regenerate any with defects.
5. **`upload-startframes.sh`** — for each approved still, prepare N fresh copies in the per-run start-frame map.
6. **`generate-seedance.sh`** — fire one MiniMax H3 image-to-video call per (still × variation). Local first-frame files are converted to data URLs when needed.
7. **`poll-minimax-and-download.sh`** — poll the MiniMax task IDs and download the finished mp4.
8. (manual) QA the clips. Pick favorite take per beat.
9. **`restitch-tight.sh`** — trim each chosen clip to roughly its VO line length (no dead space) and concat with audio preserved.
10. **`generate-vo-elevenlabs.sh`** — generate ONE VO clip per visual beat so timing snaps to cuts. Use `A.I.` (with periods) for fluid acronym pronunciation; `A I` reads as separated letters.
11. **`generate-music-elevenlabs.sh`** — compose a 30-60s instrumental bed. Prompt for the genre that fits your audience, not generic "uplifting." Will be mixed at ~10%.
12. **`render-captions.py`** — emit one transparent PNG per caption with timing in `schedule.tsv`. Edit the `CAPTIONS` array to match VO word-for-word.
13. **`final-assembly.sh`** — final ffmpeg mix: video + per-beat VOs (at their offsets) + music (low) + original Seedance audio as SFX bed + caption PNG overlays.

## Key conventions baked in

- **No dead space:** trim each clip to ~0.5s longer than its VO line. Original 4s Seedance clip becomes ~2.5-3.5s. See [`restitch-tight.sh`](restitch-tight.sh).
- **VO per visual beat, not per script paragraph:** generate one short ElevenLabs file per visual cut and `adelay` each to its cut time. A single long VO file always drifts. See [`generate-vo-elevenlabs.sh`](generate-vo-elevenlabs.sh).
- **Captions per beat, position decided by where the character lives:** if the character fills the lower half of the frame (laptop reveal, full-frame mascot), captions go **top**; if the character lives upper-center (dashboard close-ups), captions go **bottom**. Caption text matches VO verbatim. See [`render-captions.py`](render-captions.py).
- **Audio mix:** VO 100%, Seedance SFX 28%, music 10%. See [`final-assembly.sh`](final-assembly.sh).
- **Caption renderer is Pillow + ffmpeg overlay, not libass.** Homebrew ffmpeg ships without `subtitles` / `drawtext` filters. Pillow + transparent PNGs is the workaround.

## Example prompts

Reference prompts from a real run (Mr Paid Social Pixar ad, May 2026) are in [`example-prompts/`](example-prompts/) — useful as a template for prompt structure, voice/SFX choices, and beat structure.

## Cost reference

A single 7-beat ad ran ~$75 in Arcads credits (image stills + 21 Seedance clips at 3 variations per beat) + negligible ElevenLabs cost on the starter tier. Re-runs are cheaper since the storyboard is the expensive iteration loop.
