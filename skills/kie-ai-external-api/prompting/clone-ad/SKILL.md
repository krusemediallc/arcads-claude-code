---
name: clone-ad
description: >
  Clone an existing video ad for a different product or offer. Analyzes the source
  video's style, pacing, camera work, dialogue, and tone, then adapts and generates
  a new Seedance 2.0 video customized for the user's product. End-to-end workflow:
  input video → analysis → adapted prompt → generation → delivery. Use when someone
  says "clone this ad", "make this ad but for my product", "recreate this video for
  my brand", or provides a video ad and a product image asking for a similar video.
---

# Clone ad — Seedance 2.0

Clone an existing video ad for a different product or offer. The agent analyzes the
source video frame-by-frame, transcribes dialogue, extracts the visual style and
beat structure, then generates a new Seedance 2.0 video adapted for the user's product.

**How this differs from analyze-video:**
- **analyze-video** → output is a **reusable markdown template** saved to `prompt-library/`
- **clone-ad** → output is a **generated Seedance 2.0 video** delivered to the user

## Prerequisites

Before starting, verify:

```bash
which ffmpeg || echo "MISSING — run: brew install ffmpeg"
python3 -c "import whisper; print('whisper OK')" 2>/dev/null || echo "MISSING — run: pip3 install openai-whisper"
```

Both `extract-frames.sh` and whisper depend on ffmpeg. If missing, install via `brew install ffmpeg` before proceeding.

## Workflow

### Step 0: Gather inputs

Collect from the user:

| Input | Required | Notes |
|-------|----------|-------|
| **Source video** | yes | The video ad to clone. File path to `.mp4`, `.mov`, `.webm` |
| **Product image** | recommended | Reference photo of the user's product. Becomes `reference_image_urls` / `@(img1)` in the prompt. Must be hosted at a public HTTPS URL — see `SKILL.md` → "Reference images: hosting and public URLs". Without this, Seedance invents its own product design. |
| **Product/offer description** | if no image | Text description of the product, its features, target audience, and key selling points. Used to rewrite dialogue and product references. |
| **Brand voice** | optional | Check `MASTER_CONTEXT.md` for brand blocks. If empty, ask the user for tone/audience preferences. |

If the user only provides a video and says "clone this for my product," ask them for
at least a product image or a text description before proceeding.

### Step 1: Extract frames and audio

Reuse the analyze-video extraction script — do NOT duplicate it.

```bash
bash "skills/kie-ai-external-api/prompting/analyze-video/scripts/extract-frames.sh" \
  "<source_video_path>" "/tmp/clone-ad-analysis" <num_frames>
```

**Frame count by duration:**

| Source duration | Frames |
|-----------------|--------|
| Under 10s | 8 |
| 10–20s | 12 |
| 20–30s | 16 |
| Over 30s | 20 |

**Outputs:**
- `frame_001.jpg` through `frame_NNN.jpg`
- `audio.wav` (16 kHz mono, whisper-ready)
- `metadata.txt` (duration, resolution, fps, frame count)

Read `metadata.txt` to get the source video duration — you'll need it for step 6.

### Step 2: Transcribe audio

Use whisper to get the exact dialogue. This is critical — the dialogue pattern is what
gets adapted for the user's product.

```python
import whisper
model = whisper.load_model("base")
result = model.transcribe("/tmp/clone-ad-analysis/audio.wav")
```

Record:
- Full transcript text
- Per-segment timestamps and text (`result["segments"]`)
- Total word count
- Language detected

If the video is **silent** (no speech detected), note that and skip the dialogue
adaptation in step 7. The clone will be a visual-style clone only.

### Step 3: Compressed analysis

Read **ALL** extracted frames visually. For each frame, note:

**Structure and pacing:**
- How many distinct beats/shots are there?
- What's the narrative arc? (hook → demo → verdict? reveal → detail → CTA?)
- How long does each beat last? (map to segment timestamps)

**Camera and framing:**
- POV style: selfie/handheld, tripod, propped phone, over-the-shoulder?
- Framing per beat: wide, medium, close-up, macro?
- Camera movement: static, pan, dolly, handheld shake?
- Signature framing moves (e.g., "leans into camera," "tilts product toward lens")

**Edit style:**
- Transition type: jump cuts, dissolves, match cuts?
- Visual rhythm: fast cuts vs held shots?
- Any recurring motif (e.g., "every other beat is an extreme close-up")?

**Dialogue and script structure:**
- Hook format: question, statement, exclamation, reaction?
- Speech pattern: casual/formal, filler words, trailing thoughts, mid-sentence cuts?
- How many spoken lines? How many silent beats?
- CTA style: direct ("link in bio"), soft ("you need to try this"), none?

**Tone and energy:**
- Emotion words that describe the speaker/mood
- Energy arc: starts calm → builds excitement? Flat? Burst then settle?
- Speaker's relationship to viewer: friend, expert, skeptic, fan?

**Lighting and technical quality:**
- Light source: natural/artificial, direction, quality
- Camera quality: phone/DSLR/cinema, intentional flaws?
- Audio quality: phone mic, studio, car, outdoor?

**Product references:**
- How is the product physically shown? (held up, worn, applied, on a surface)
- What specific claims or features are called out?
- Brand mentions, labels visible, text overlays?

**What makes this ad distinctive (2–3 defining traits):**
- The unique combination of elements that makes this ad recognizable
- These are the traits that MUST transfer to the clone

Store this analysis internally — it does NOT get saved as a template file.

### Step 4: Present analysis summary

Show the user a structured breakdown before proceeding:

```
📋 Source video analysis

Duration: Xs | Beats: N | Dialogue: Y words | Style: [style name]

Beat map:
  [00:00–00:03]  HOOK — close-up, excited expression, "opening line"
  [00:03–00:07]  SHOW — tilts product to camera, "feature call-out"
  [00:07–00:10]  DEMO — (silent) applies/uses product, close-up on texture
  [00:10–00:15]  VERDICT — back to camera, "closing line + CTA"

Defining traits:
  1. [trait 1]
  2. [trait 2]
  3. [trait 3]

What transfers to your product:
  ✅ Beat structure, pacing, camera angles, edit style, tone, energy
  ✅ Dialogue pattern (adapted for your product)
  ✅ Lighting and technical quality cues

What gets swapped:
  🔄 Product references → your product
  🔄 Specific claims → your product's features
  🔄 Brand mentions → your brand (if provided)

Proceed with adaptation? (yes / adjust)
```

Wait for user confirmation before continuing.

### Step 5: Decide generation mode

Walk through this decision tree:

```
┌─ Source video ≤ 15s?
│   YES → Single-clip generation
│   NO  → Multi-clip split at natural beat boundaries
│         Each clip ≤ 15s (Seedance max)
│         Identify best split points from beat map
│         Use the CHAINED MULTI-CLIP PIPELINE below
│
├─ User provided a product IMAGE?
│   YES → Image-to-video mode (reference_image_urls with @(img1) in prompt)
│         For multi-clip: use i2v for clip 1 ONLY, then chain v2v for clips 2+
│   NO  → Text-only mode (describe product in prompt text only)
│         OR v2v if:
│           - Source video has NO human faces
│           - AND user wants to preserve exact visual style
│           - (v2v with faces → content checker rejection + billed)
│
├─ Source video has person SPEAKING?
│   YES → audio: true (confirm with user)
│         Dialogue confirmation gate REQUIRED (step 7)
│   NO  → audio: false (or ask user preference)
│         Skip dialogue gate
│
└─ User wants voice clone from source audio?
    YES → Host source audio at a public HTTPS URL and pass it via
          reference_audio_urls
          (check audio+image regression: run sanity probe first)
    NO  → Seedance generates its own voice from text
```

### Chained multi-clip pipeline (confirmed 2026-04-10)

When the source ad is longer than 15s, use this hybrid i2v→v2v chaining pattern for visual continuity:

```
Clip 1: i2v mode
  - reference_image_urls: [product image URL]  ← establishes brand fidelity
  - audio: true (if speech)
  - Generate → poll → download output

Clip 2: v2v mode
  - reference_video_urls: [clip 1 output URL]  ← inherits hands, surface, lighting, product
  - NO reference_image_urls (mutually exclusive)
  - audio: true (if speech)
  - Host clip 1 output at a public HTTPS URL
  - Generate → poll → download output

Clip 3: v2v mode
  - reference_video_urls: [clip 2 output URL]  ← chain from MOST RECENT clip, not clip 1
  - Host clip 2 output at a public HTTPS URL
  - Generate → poll → download output

...continue for clips 4+
```

**Critical rules for chaining:**
1. **Always chain from the most recent clip** — do not reuse earlier uploads.
2. **Host each clip output fresh** at a public HTTPS URL before passing it as a `reference_video_urls` entry. See `SKILL.md` → "Reference images: hosting and public URLs" (same pattern applies to video).
3. **Wait for each clip to reach `generated` status** before hosting it as a reference for the next clip. Do not fire clips in parallel — they must be sequential.
4. **Clip 1 uses i2v** for brand fidelity (product image as reference). All subsequent clips use **v2v** (previous clip as reference) for visual continuity.
5. After all clips are generated, **stitch with ffmpeg**: `ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4` (use absolute paths in the list file).

**Why chaining works:** Seedance v2v inherits the visual style, hands, surface, lighting, and product appearance from the reference video. By chaining clip N → clip N+1, each subsequent clip maintains continuity with the one before it. The first clip's i2v reference image establishes the product identity; v2v propagates it through the series.

**Cost note:** kie.ai bills in USD. Check `MASTER_CONTEXT.md` for the Seedance 2.0 rate — ask the user if the rate isn't listed. For multi-clip series, estimate per-clip cost and total.

**Important constraints to check:**
- `reference_image_urls` and `reference_video_urls` are **mutually exclusive** — pick one per call
- v2v with human-containing reference videos → content checker rejection (cost still billed)
- `audio: true` + `reference_image_urls` may error (intermittent regression) — sanity probe first
- `reference_video_urls` count > 1 may fail — only 1 ref video is known to work
- If using v2v: only use product-only/abstract/hands-only videos (no faces)
- Hands-only clips (no face visible) pass the v2v content checker — confirmed 2026-04-10

Tell the user which mode you're using and why.

### Step 6: Adapt for user's product

This is the creative core. Using the analysis from step 3:

**Dialogue adaptation (if source has speech):**
- Keep the **same conversational pattern**: if the source uses a question hook, use a question hook. If it uses filler words ("like," "okay so"), keep filler words.
- Keep the **same number of spoken lines** and **same silent beat placement**
- Keep the **same energy arc** (excited → calm, or flat, or building)
- Replace **product-specific references** with the user's product name, features, and claims
- Match the **word count** of each line closely (±3 words per beat) to preserve pacing
- Read the adapted dialogue out loud at natural pace — it must fit the target duration

**Visual adaptation:**
- Keep the analyzed camera work, framing per beat, and edit style
- Replace the product description with the user's product (physical appearance, colors, materials, label details)
- Keep the setting, lighting, and atmosphere
- Keep the person description (or adapt if user specifies a different persona)
- Keep the technical flaw cues (phone quality, mic type, lighting imperfections)

**Prompt composition:**
- Read [seedance-2.md](../prompt-library/seedance-2.md) for platform rules before composing
- Read the closest matching style template (e.g., [seedance-2-ugc.md](../prompt-library/seedance-2-ugc.md) for UGC-style sources) for structural guidance
- Follow the **Subject + Action + Camera + Style + Constraints** order
- Stay within **100–260 words** (Seedance sweet spot)
- Include `@(img1)` token if user provided a product image
- Add consistency anchors: "The product from @(img1) must remain visually unchanged in every shot"
- Add pacing cues in the tone direction paragraph
- Use timestamps `[00:00]`, `[00:04]`, etc. for multi-beat sequences
- **No forbidden words:** cinematic, professional, stunning, 8k, studio, perfect

**Duration selection:**
- If source ≤ 15s: match source duration (or round to nearest second in 4–15 range)
- If source > 15s: split into clips, each ≤ 15s
- Use dialogue word count to validate (see main SKILL.md duration table: ~2.5 words/sec)

### Step 7: Dialogue confirmation gate

**MANDATORY** for any clone with spoken dialogue. Follow the exact format from the
main SKILL.md:

```
📝 Dialogue script (please confirm before I generate)

  1. [HOOK]    "adapted line matching original pattern"
  2. [SHOW]    "adapted feature call-out for user's product"
  3. [DEMO]    (silent beat — physical demonstration, no dialogue)
  4. [VERDICT] "adapted closing line / CTA"

Total spoken words: ~N  |  Target duration: Xs  |  Fits at natural pace: ✅/❌

Approve this dialogue? (yes / edit / rewrite)
```

**Rules:**
- This gate is **separate** from the cost confirmation — both must be satisfied
- Never assume approval from earlier confirmations (tone, analysis, cost)
- If user says "edit" or proposes changes, revise and re-present until approved
- Skip ONLY if the source video is entirely silent (no speech detected in step 2)

### Step 8: Audio decision

Ask the user:

1. **Enable audio output?** (`audio: true` / `false`)
   - Default to `true` if source video has speech
   - Default to `false` if source video is silent
2. **Supply reference audio for voice cloning?**
   - Offer to extract the source video's audio and host it at a public HTTPS URL for `reference_audio_urls`
   - Or user can provide their own voice clip
3. **Sanity probe** (if using `audio: true` + `reference_image_urls`):
   - This combo has a known regression that can error
   - Before the full call, fire a minimal test to check if the regression is still active
   - If still broken, offer fallbacks:
     - Drop audio (`audio: false`)
     - Drop reference image (text-only, lose brand fidelity)
     - Use v2v workaround (generate silent i2v first, then v2v with audio on top)

### Step 9: Cost estimation

Follow the main SKILL.md's mandatory estimation flow:

1. Check `logs/kie-api.jsonl` for matching `model` + similar config
2. Fall back to `MASTER_CONTEXT.md` rate table (ask the user if the rate isn't listed)
3. For multi-clip: show per-clip and total
4. Present with source citation and estimate-only disclosure:

```
Estimated cost:
  Seedance 2.0 (15s i2v) × 1 clip × 1 variation = ~$<rate>
    (from logs/kie-api.jsonl 2026-04-09)
  ─────────────────────────────────────
  Estimated total: ~$<rate>

  ⚠️ Estimate only — confirm exact cost in the kie.ai dashboard.
  Proceed? (yes/no)
```

**Do NOT generate until the user confirms.**

### Step 10: Host references

Save outputs to `outputs/clone-ad-tests/` (or a descriptive subfolder) locally.

Host references at public HTTPS URLs (see main SKILL.md → "Reference images: hosting and public URLs"):
   - Product image → public HTTPS URL (auto-upscale if longest side < 1024px)
   - Source video (if v2v mode) → public HTTPS URL
   - Reference audio (if voice clone) → public HTTPS URL

Store all URLs for the generation payload.

### Step 11: Generate

1. Compose the kie.ai request body:
   ```json
   {
     "model": "bytedance/seedance-2",
     "input": {
       "prompt": "<from step 6>",
       "aspect_ratio": "9:16",
       "duration": 15,
       "resolution": "720p",
       "audio": true,
       "reference_image_urls": ["https://..."]
     }
   }
   ```
   Swap `reference_image_urls` for `reference_video_urls` in v2v mode (they're mutually exclusive). Add `reference_audio_urls` for voice cloning.

2. Ask generation count (how many variations? default 1). kie.ai has no `nbGenerations` field — fire N parallel `createTask` calls to get multiple variations.

3. **Single-clip:** Fire N parallel `POST /api/v1/jobs/createTask` calls.
   **Multi-clip (chained):** Fire clips **sequentially** per the chaining pipeline in step 5.
   Each clip depends on the previous clip's output — do not fire in parallel.

4. **Log immediately** to `logs/kie-api.jsonl`:
   ```json
   {
     "timestamp": "...",
     "endpoint": "POST /api/v1/jobs/createTask",
     "model": "bytedance/seedance-2",
     "taskId": "...",
     "request": { "duration": ..., "resolution": ..., ... },
     "response": { "status": "pending" },
     "session": { "notes": "clone-ad: ..." }
   }
   ```

5. Poll `GET /api/v1/jobs/recordInfo?taskId=<id>` until complete or failed
   - Single-clip: poll all variation task IDs concurrently
   - Multi-clip: poll each clip individually, wait for completion before proceeding to the next
   - Update log entry with final status, `generationTimeSec`, output URLs

6. For multi-clip: host each completed clip at a public HTTPS URL, then use it as the `reference_video_urls` entry for the next clip (see chaining pipeline in step 5)

### Step 12: Present results

1. **Save all videos** to `outputs/clone-ad-tests/` (or a descriptive subfolder)
2. **Open the output folder** on the user's machine so they can immediately review:
   ```bash
   open "outputs/clone-ad-tests/"   # macOS
   ```
3. Present watch/download URLs
4. For multiple variations: numbered list for comparison
5. For multi-clip:
   - Present each clip separately
   - Stitch with ffmpeg using **absolute paths**:
     ```bash
     printf "file '%s'\n" "$(pwd)/clip1.mp4" "$(pwd)/clip2.mp4" "$(pwd)/clip3.mp4" > /tmp/stitch-list.txt
     ffmpeg -y -f concat -safe 0 -i /tmp/stitch-list.txt -c copy stitched-output.mp4
     ```
   - Provide both stitched file and individual clips
6. Show cost summary in USD (total across all clips/variations)

## Seedance 2.0 constraints (quick reference)

Check [reference.md](../../reference.md) for full details. These are the ones most
likely to bite during clone-ad:

| Constraint | Impact |
|-----------|--------|
| `reference_video_urls` + `reference_image_urls` mutually exclusive | Cannot combine in same request |
| v2v with human faces in reference video | Content checker rejects, cost still billed |
| `audio: true` + `reference_image_urls` regression | May error — sanity probe first |
| `reference_video_urls` count > 1 may fail | Only 1 reference video is known to work reliably |
| Content check bills before checking | Cost billed at create time, not refunded on rejection |
| `last_frame_url` non-functional on Seedance 2.0 | Do not use |
| Prompt length | 100–260 words (Seedance sweet spot) |
| Duration | 4–15 seconds (continuous integer) |
| Aspect ratio | `9:16` or `16:9` only (no `1:1`) |
| Forbidden words | cinematic, professional, stunning, 8k, studio, perfect |

## Error recovery

| Error | Recovery |
|-------|----------|
| Content checker rejects prompt | Do NOT retry same payload. Remove potentially flagged language. Tighten motion descriptions. Check for forbidden words. |
| Error on `audio: true` + `reference_image_urls` | Audio+image regression is active. **Fallback options:** (a) drop audio, (b) drop image and go text-only, (c) v2v workaround: generate silent i2v first, then run v2v with audio on top using the i2v output as reference video |
| v2v face rejection | Source video has humans — switch to i2v mode with user's product image |
| Prompt too long (> 260 words) | Trim: cut filler from tone direction, compress setting details, shorten consistency anchors. Prioritize beat structure and dialogue. |
| Source video > 15s | Split into clips at natural beat boundaries. Generate each separately. Offer to stitch. |
| Generation fails | Check the error message on the poll response. If content-related, rewrite prompt. If server error, wait and retry once. |

## Related files

- [analyze-video/SKILL.md](../analyze-video/SKILL.md) — the template-creation cousin (creates reusable `.md` templates instead of generating)
- [analyze-video/scripts/extract-frames.sh](../analyze-video/scripts/extract-frames.sh) — frame + audio extraction (reused by this skill)
- [seedance-2.md](../prompt-library/seedance-2.md) — Seedance 2.0 platform rules (read before composing any prompt)
- [seedance-2-ugc.md](../prompt-library/seedance-2-ugc.md) — 9-layer UGC formula (use as structural reference for UGC-style source videos)
- [seedance-2-premium-reveal.md](../prompt-library/seedance-2-premium-reveal.md) — premium reveal formula (for dark-void product-only source videos)
- [seedance-2-product-hero.md](../prompt-library/seedance-2-product-hero.md) — product hero formula (for elemental/effects product-only source videos)
- [seedance-2-studio-lookbook.md](../prompt-library/seedance-2-studio-lookbook.md) — studio lookbook formula (for polished voiceover-style source videos)
- [seedance-2-feature-walkthrough.md](../prompt-library/seedance-2-feature-walkthrough.md) — feature walkthrough formula (for fast-paced demo source videos)
- [../../reference.md](../../reference.md) — API routes, request body shapes, polling, constraints
- [../../SKILL.md](../../SKILL.md) — main execution checklist (session setup, dialogue gate, cost estimation, logging)
