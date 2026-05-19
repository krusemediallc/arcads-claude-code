# Claymation AI cartoon ad — cross-API prompting guide

**Aesthetic:** Aardman / Laika stop-motion claymation feature film look applied to short-form product ads (TikTok/Reels/Shorts).
**Default pipeline:** **ChatGPT Image 2** for storyboard frames (or **Nano Banana Pro** when clay texture detail matters more than identity continuity) → **Seedance 2.0** image-to-video for animation → stitch with ffmpeg.
**Format:** 9:16 vertical, **60–115s total**, 8–12 beats stitched from 6–12s Seedance clips, narrator voiceover, burned-in captions.

Use this guide when the user asks for a "claymation ad," "Aardman-style ad," "stop-motion ad," or shows a reference video that matches the look in [the example folder](../../../../Ai%20Annimation%20Ad%20Examples/claymation/).

Sibling: [Pixar-style ad](../../pixar-style-ad/prompting/guide.md).

## What "claymation" means here (and what it doesn't)

This look anchors on **Aardman Animations** (Wallace & Gromit, Chicken Run) and **Laika** (Coraline, Kubo) lineage — hand-sculpted clay/plasticine, visible tool marks, slightly imperfect armatures, miniature physical sets. Not generic CGI cartoon.

Anchor every prompt on these traits:

- **Hand-sculpted clay/plasticine surfaces** — visible fingerprint impressions, sculpting-tool marks, slight asymmetry, subtle pinch lines around facial features
- **Matte clay material** — no Pixar wet-eye sheen, no glossy refraction; clay reads as opaque, slightly waxy, with soft micro-bumps
- **Exaggerated, character-driven faces** — oversized noses, deep wrinkles when called for, asymmetric eye placement, painted-on or sculpted eyebrows; characters can be quirky/grotesque rather than appealing
- **Real-looking knit/felt fabric** — chunky wool sweaters, knit cardigans, felt curtains — separately constructed and stitched, not painted-on
- **Wooden and ceramic props** — Aardman miniature-set vibe: real-wood tables, hand-thrown ceramic mugs, tin kettles, fabric tablecloths
- **Warm tungsten interior lighting** for domestic scenes; cool fluorescent for office/dystopian scenes (see [reference video C](../../../../Ai%20Annimation%20Ad%20Examples/claymation/ssstwitter.com_1779210191690.mp4))
- **Shallow depth of field** with creamy bokeh; soft macro-photography feel that reinforces the miniature-set illusion
- **Subtle imperfection everywhere** — slightly uneven paint on labels, fabric weave irregular, clay surfaces never perfectly smooth

**Do NOT use these words** (they pull away from the claymation look):
`Pixar`, `3D rendered`, `digital`, `CGI`, `anime`, `cel-shaded`, `2D`, `painted illustration`, `realistic photo`, `live action`, `photorealistic`, `smooth render`, `subsurface scattering`, `ray-traced`. Also avoid Seedance 2's forbidden words list when prompting Seedance: `cinematic`, `professional`, `stunning`, `8k`, `studio`, `perfect`.

## Smooth motion vs stop-motion judder — pick one

Real stop-motion has ~12–15 fps judder. AI video generators output smooth 24/30 fps. The reference videos in `claymation/` are **all smooth** — the AI keeps the visual aesthetic but plays motion smoothly. That's the default.

If the user explicitly wants the **stop-motion judder feel**, add a post step: re-encode with `ffmpeg -filter:v "fps=12,fps=24"` (drops to 12 fps, then duplicates frames back to 24) — produces visible judder. Don't bake this into the Seedance prompt; Seedance can't reliably control framerate, and asking for "stop-motion judder" tends to break the aesthetic.

## The claymation story arc (8 beats — longer-form than Pixar)

Claymation ads in this genre are **narrative**: a quirky third-person narrator tells a story about a character. The protagonist drives the entire arc; there is no "anthropomorphized problem character" beat like in Pixar. Plan all 8 beats up front so character and miniature set stay consistent.

| Beat | Length | Purpose | What's on screen |
|------|--------|---------|------------------|
| **1. Setup** | 6–10s | Introduce the protagonist in their everyday world. | Wide or medium shot of the protagonist in their domestic miniature set (kitchen, bedroom, bathroom). Narrator says their name and a single defining trait. |
| **2. Inciting moment** | 6–8s | The protagonist notices the problem. | Close-up of the protagonist's face as they spot the issue (lines in a mirror, weight on a scale, a sound). Surprised or concerned expression. |
| **3. Social validation** | 6–10s | Someone else acknowledges the problem (often unintentionally). | Two-character scene: protagonist with a friend/spouse/coworker in a cafe / living room / office. A small exchange or remark. |
| **4. Quiet despair** | 5–8s | Solo reflection beat. | Protagonist alone at a window, mirror, or sink, looking at their reflection. No dialogue — narrator carries it. |
| **5. Clay infographic / "research"** | 6–10s | Explain the mechanism using a clay-rendered chart or diagram. | A hand-sculpted clay infographic on a wall or tablet (e.g. "Calcium in skin" chart with clay letters and a plasticine line graph). Static or with a small animated indicator. **Optional** — drop this beat if the product doesn't need explanation. |
| **6. Discovery** | 6–8s | The protagonist finds the product. | Close-up to medium shot of the product (rendered as a slightly imperfect clay-shaded prop) sitting on a wooden table, bathroom shelf, or windowsill. Protagonist reaches for it. |
| **7. Transformation** | 8–12s | Time passes, protagonist uses the product, change is visible. | Montage: applying / taking the product, then a "weeks later" reveal — clay protagonist with subtle visual improvement (smoother skin / brighter eyes / better posture). |
| **8. Resolution + CTA** | 6–8s | Confident protagonist with the product, captioned CTA. | Protagonist holds the product, smiling at camera or at another character. Lower third clean for burned-in CTA caption. |

**Total:** ~50–75s of clip duration; add 5–10s of breath/cuts in editing. If the user wants the shorter format, drop beats 3, 4, and 5 — the **5-beat short** (Setup → Inciting → Discovery → Transformation → CTA) lands around 35–45s.

**Variations by category:**

- **Health/supplement (refirm, ashwagandha, GLP-1)** — full 8-beat works well; the chart beat sells the mechanism.
- **Beauty/skincare** — emphasize beats 2 (mirror) and 4 (self-reflection); chart beat optional.
- **Office / B2B (Lion's Mane–style)** — protagonist is in a fluorescent-lit office (frame from reference C: bald exhausted office worker); cool-light palette for beats 1–4, warm only after the discovery/transformation.
- **Food / kitchen products** — beats 1, 6, 7 dominate; social beat (3) becomes a family dinner.

## Cast & continuity sheet (do this BEFORE generating anything)

Claymation ads usually feature **two or three named characters**. Lock all of them up front. Save the sheet to `references/<brand>-claymation-cast.md`.

```
PROTAGONIST
- Name (used by narrator): <e.g. Diane>
- Age range: <30s/40s/50s/60s — claymation favors middle-aged and older characters>
- Distinctive feature: <e.g. shoulder-length terracotta-brown wavy hair, deep laugh lines, hooded eyelids>
- Build: <average / petite / sturdy>
- Eye color: <e.g. warm brown, sculpted lower lids visible>
- Outfit: <e.g. cream chunky knit cardigan over rust-red blouse, dark wool trousers, brown leather slippers>
- Posture cue: <e.g. slight forward lean, soft rounded shoulders>

SUPPORTING CHARACTER (beat 3)
- Relationship: <best friend / spouse / coworker>
- Distinctive feature: <e.g. silver curly hair, round wire glasses, sage-green cable-knit sweater>
- Age range: <similar or older than protagonist>

NARRATOR (voiceover, not visible)
- Voice persona: <warm storytelling, slight British inflection, mid-pace> OR <wry midwestern, dry humor>
- Tone: <gentle observational / wry / matter-of-fact>

SETTING — primary location
- Domestic: <e.g. small sunlit kitchen with green-painted cabinets, red gingham tablecloth, wooden table, copper kettle on stove, potted herbs on windowsill>
- Reuse this setting for beats 1, 6, 8 to anchor continuity

SETTING — secondary location (beat 3)
- <e.g. neighborhood cafe with potted plants, wooden tables, hanging brass pendant lights>

PRODUCT
- Render as a clay-stylized prop: matte-painted label, slightly imperfect cylinder/jar shape, paint that looks hand-applied
- Copy exact label text from the brand reference
- Position: on the wooden table / bathroom shelf / kitchen counter

STYLE LOCK (paste verbatim into every image prompt)
"Aardman-style stop-motion claymation aesthetic. Hand-sculpted plasticine
characters with visible fingerprint impressions and sculpting-tool marks,
matte clay surfaces, slightly asymmetric features. Real knit-fabric clothing
with visible weave, wooden and ceramic miniature-set props. Warm tungsten
interior lighting, shallow macro depth of field, soft photographic bokeh.
Subtle imperfection in every surface. 9:16 vertical."
```

## Pipeline: Image 2 → Seedance 2.0 → stitch

### Why Image 2 (with a Nano Banana Pro fallback)

1. **Identity continuity across 8 beats** — Image 2 holds the same sculpted character face when you re-feed prior frames as references. Critical for "Diane" appearing in beats 1, 2, 3, 4, 6, 7, 8.
2. **Strong stylized stop-motion output** — Image 2 renders clay textures cleanly when the STYLE LOCK is verbatim.
3. **Fallback to Nano Banana Pro** — if the user reports that Image 2 is smoothing out the clay texture or losing fingerprint detail on close-ups, switch to Nano Banana Pro for those specific beats. Trade-off: Nano Banana Pro is slightly weaker on cross-beat identity, so use it only for product close-ups (beat 6) and infographic beats (beat 5) where character identity doesn't matter.

### Why Seedance 2.0 image-to-video

Same reasoning as Pixar — animates each approved still while preserving the rendered clay aesthetic. Seedance 2's 4–15s ceiling is per-clip; 8 beats × ~8s avg = ~64s of final ad after stitching.

### Step-by-step

1. **Lock the cast sheet** with the user. Confirm protagonist, supporting character, narrator voice, primary + secondary settings, product packaging.
2. **Write the 8-beat narrator script** as plain English. One narrator sentence per beat plus any spoken dialogue. Get user approval before any generation.
3. **Generate Beat 1 hero still** with Image 2 using [storyboard-gpt-image-2.md](storyboard-gpt-image-2.md). Show user, iterate.
4. **Generate Beats 2, 4, 6, 7, 8 (protagonist beats) sequentially**, passing the prior approved protagonist still as a reference. Approve each one.
5. **Generate Beat 3 (two-character scene)** with both the approved protagonist still and the supporting character description.
6. **Generate Beat 5 (clay infographic)** independently — no character continuity needed.
7. **Animate each still with Seedance 2.0** using [animate-seedance-2.md](animate-seedance-2.md). Run beats in parallel.
8. **QA each clip** — claymation-specific: watch for clay texture flattening into 3D-rendered smoothness, fabric losing knit weave, label paint becoming digitally crisp. Up to 2 retries per beat.
9. **Stitch with ffmpeg.** Optional: re-encode with `fps=12,fps=24` filter chain for stop-motion judder if requested.
10. **Burn captions** — same TikTok caption style as Pixar guide OR use the "orange highlight block" style seen in [reference C](../../../../Ai%20Annimation%20Ad%20Examples/claymation/ssstwitter.com_1779210191690.mp4) (white text on solid orange rounded rectangle, slight tilt).

### Aspect ratio & resolution defaults

- **Aspect ratio:** `9:16` for TikTok/Reels/Shorts.
- **Image 2 output size:** 1024×1792.
- **Seedance resolution:** `720p` default.

## Narration & dialogue

Claymation ads are **narrator-driven**, unlike Pixar's first-person protagonist voice. The narrator carries 70–90% of the audio; characters speak only in beat 3 (the social validation scene) and sometimes briefly in beat 7.

**Narrator voice direction:**
- Warm storytelling cadence, slight pause between sentences
- Mid-pace — never rushed
- Slight smile in the voice
- References to character by name ("Diane noticed...", "When her friend Margaret asked...")

**Character dialogue:**
- Sparse — one short line per character
- Casual, natural — no marketing copy
- Often the supporting character makes the observation: *"You look different — what is that?"*

**Auto-select per-beat duration based on narrator line length** (~2.5 words/sec):

| Narrator words | Beat duration |
|----------------|---------------|
| 1–15 | 6s |
| 16–22 | 8s |
| 23–30 | 10s |
| 31–37 | 12s |
| 38+ | Split across beats |

## Cost & confirmation (mandatory)

Before firing any generation, calculate and present total credit cost to the user (per the [KIE](../../kie-external-api/SKILL.md#credit-cost-estimation-mandatory--show-before-generating) / [Arcads](../../arcads-external-api/SKILL.md) credit rules).

For a typical 8-beat claymation ad:
- 8× Image 2 frames (storyboard) — sequential for identity continuity
- 8× Seedance 2 clips @ 720p, mostly 6–10s each → ~64s of final video
- Retries cap at 2 per beat per QA rule
- Worst-case: 24 image calls + 24 video calls

Always wait for explicit user confirmation before firing.

## Negative prompt block (paste into every video prompt)

```
no live-action footage, no photorealistic faces, no Pixar style, no 3D rendered
look, no CGI, no anime, no 2D illustration, no smooth digital render, no ray-traced
materials, no subsurface scattering, no extra fingers, no melted features, no
morphing between frames, no warped product labels, no on-screen text unless
specified, no subtitles, no captions
```

For Seedance 2 specifically, also strip the model's forbidden words: no `cinematic`, `professional`, `stunning`, `8k`, `studio`, `perfect`. Substitute: "stop-motion claymation film aesthetic", "polished hand-sculpted", "high fidelity", "evenly hand-painted".

## Captioning

Two style options that work for this genre:

**A. TikTok white-with-stroke** (matches reference videos A and B in `claymation/`)
- White Proxima/Montserrat Bold, ~7% of video height
- 4–6 px solid black stroke
- Lower third, centered
- Per-phrase timing, not per-word

**B. Orange highlight block** (matches reference video C)
- White Proxima/Montserrat Bold
- Solid orange-red rounded rectangle background (`#E94B23` ish), 8–12 px padding
- Slight 2–3° rotation for handmade feel
- Lower third, slightly off-center
- One word or short phrase per highlight block

Burn captions after stitching (`ffmpeg -vf "subtitles=caps.ass"`), not in the Seedance prompt. The negative block tells Seedance "no captions" — burn them on in post.

### Recommended pipeline: HyperFrames-rendered animated captions

For per-phrase emphasis (scale-pop on punchlines, brand-color callouts on the product reveal), use the [`hyperframes`](../../../shared/skills/hyperframes/) skill rather than static `.ass` burning. Quick recipe:

1. `npx hyperframes init claymation-captions --video <your-stitched-ad.mp4> --non-interactive --example blank` — scaffolds project + auto-transcribes audio (whisper.cpp, word-level timestamps).
2. **Flatten whisper.cpp tokens to a clean word array** — whisper splits ASHWAGANDHA/gummy/sourceless into subword fragments. Merge tokens using the leading-space convention (tokens with leading space are word-starts; without are continuations). Fix any homophone misreads (e.g. "warrior" → "worrier" for stress-related copy).
3. **Group words into 3–4 word caption phrases**, breaking on sentence end / >0.6s pauses / 4-word cap. Treat `Mr.`, `Mrs.`, `Dr.`, `Ms.` as non-sentence-end so brand names don't get split.
4. **Build the composition with the captions track only** — see the [HF gotcha block below](#-hyperframes-gotcha-portrait-video-clipping). Tag groups by emphasis (`normal` / `comedic` / `brand` / `product`) and style per [shared/skills/hyperframes/references/captions.md](../../hyperframes/references/captions.md) (storytelling tone for claymation: white-with-stroke base, warm-cream punchlines, brand-purple product reveal).
5. **Clamp timing so one caption is visible at a time** — `inStart = max(prev.end + 0.01, g.start - 0.06)`, `outStart = g.end - outDur - 0.01`. Without this clamp, the entry of group N+1 cross-fades over the exit of group N when they're back-to-back, producing two captions stacked on screen for a few frames.
6. `npx hyperframes lint && npx hyperframes inspect` → 0 errors before render.
7. `npx hyperframes render --format mov --quality high --fps 30` → ProRes 4444 with `yuva444p12le` alpha.
8. `ffmpeg -i source.mp4 -i captions.mov -filter_complex "[0:v][1:v]overlay=0:0:format=auto[v]" -map "[v]" -map "0:a" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart final.mp4` — composites the alpha caption track over the source.

#### ⚠️ HyperFrames gotcha: portrait video clipping

**Do NOT put the source mp4 inside the HyperFrames composition as a `<video>` element with `position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover` (the canonical pattern in HF's blank template) when the canvas is portrait (e.g. 720×1280).** The HF runtime intercepts that pattern and applies its own inline-style positioning to the media track. At portrait resolutions this clips ~87 px off the bottom — leaving a black bar across the lower frame and visibly shifting the video up on the canvas. Confirmed 2026-05-19 on `hyperframes@0.6.26`, repro'd at 720×1280 with every variant of position/sizing CSS we tried (relative root, pixel dims, `position: fixed`) — the runtime's inline-style mutations win against composition CSS.

**Correct pattern: render captions onto a transparent canvas (no `<video>` element in the composition), then composite over the source mp4 with ffmpeg `overlay` (see step 8 above).** This keeps the source mp4 pristine at its native resolution and bypasses the runtime's media-track sizing entirely.

```html
<!-- Captions-only HF composition root — no <video> tag here -->
<div id="root"
     data-composition-id="main"
     data-start="0"
     data-duration="45.88"
     data-width="720"
     data-height="1280"
     style="position: relative; width: 720px; height: 1280px;">
  <div id="captions"></div>
</div>
```

Use `--format mov` (ProRes 4444) for the alpha render — `--format webm` came out as `yuv420p` (no alpha) in our test even though the docs say WebM supports transparency, while `--format mov` reliably produced `yuva444p12le`. The MOV is ~3× larger as an intermediate, but it gets discarded after the ffmpeg composite.

## Per-API endpoint notes (KIE vs Arcads)

The prompt content is identical across APIs. Differences are auth, endpoint paths, and reference image delivery.

### KIE.ai

| Step | Endpoint | Model string | Reference images |
|------|----------|--------------|------------------|
| Storyboard (Image 2) | `POST /api/v1/jobs/createTask` | `gpt-image-2` (verify on [kie.ai/market](https://kie.ai/market)) | Public URLs in `input.image_input[]` |
| Storyboard (Nano Banana Pro fallback) | `POST /api/v1/jobs/createTask` | `nano-banana-pro` | Public URLs in `input.image_input[]` (up to 14) |
| Animation (Seedance 2.0) | `POST /api/v1/jobs/createTask` | `bytedance/seedance-2` | Public URL in `input.image_input[]` |
| Polling | `GET /api/v1/jobs/recordInfo?taskId=...` | — | — |
| Auth | `Authorization: Bearer $KIE_API_KEY` | — | — |

### Arcads

| Step | Endpoint | Model string | Reference images |
|------|----------|--------------|------------------|
| Storyboard (Image 2) | `POST /v2/images/generate` | `gpt-image-2` | `referenceImages: [filePath, ...]` — **max 5** for `gpt-image-2`. Upload via `POST /v1/file-upload/get-presigned-url` first |
| Storyboard (Nano Banana Pro fallback) | `POST /v2/images/generate` | `nano-banana` | `referenceImages: [filePath, ...]` (max 14) |
| Animation (Seedance 2.0) | `POST /v2/videos/generate` | `seedance-2.0` | `startFrame` URL from approved still |
| Polling | `gpt-image-2` → `GET /v1/assets/{id}`. **Seedance 2.0 → `GET /v1/assets/{id}` (NOT `/v1/videos/{id}`)** — see gotcha below. | — | — |
| Auth | `Authorization: $ARCADS_BASIC_AUTH` header — the env var already contains the `Basic ...` prefix, do NOT add another `Basic ` in front of it | — | — |

### Arcads gotchas confirmed in testing (2026-05-19)

Two things to know up front when running this skill on Arcads. Both are also recorded in [`shared/skills/arcads-external-api/reference.md`](../../arcads-external-api/reference.md) for the broader API surface.

**1. Presigned `filePath` is one-time-use.**
A `filePath` returned by `POST /v1/file-upload/get-presigned-url` works for exactly **one** downstream generation call. The first call that references it (e.g. Beat 2 using Beat 1 as a reference image) consumes it; every subsequent call referencing the same `filePath` returns `HTTP 400 REFERENCE_FILE_NOT_FOUND`.

This skill chains the protagonist anchor (Beat 1) across Beats 2, 3, 4, 6, 7, 8 — and uses each beat-still again as a Seedance reference. **Re-upload the source PNG once per downstream call.** Don't try to "cache" `filePath` across parallel calls — it'll silently work for the first and 400 for the rest.

```bash
# Re-upload-per-call pattern
for n in 1 2 3 4 5 6 7 8; do
  PRESIGN=$(curl -sS -X POST -H "Authorization: $ARCADS_BASIC_AUTH" -H "Content-Type: application/json" \
    -d '{"fileType":"image/png"}' "$BASE/v1/file-upload/get-presigned-url")
  URL=$(echo "$PRESIGN" | jq -r .presignedUrl)
  FP=$(echo "$PRESIGN" | jq -r .filePath)
  curl -sS -o /dev/null -X PUT -H "Content-Type: image/png" --data-binary @hero.png "$URL"
  # Now $FP is good for exactly one call.
done
```

**2. Seedance 2.0 video jobs poll the assets endpoint, not the videos endpoint.**
Even though Seedance 2.0 is fired via the unified `POST /v2/videos/generate`, its job record lives at `GET /v1/assets/{id}` — the create response returns `type: "seedance_20"` and `GET /v1/videos/{id}` for the same id returns `HTTP 404`. The final mp4 URL lands on the top-level `url` field of the asset response (presigned S3, ~12h lifetime).

This is the opposite of the other video models on the same endpoint (`sora2`, `veo31`, `kling-*`, `grok-video`) which all poll under `/v1/videos/{id}`. Pick the polling path by inspecting the `type` field on the create response, not by assuming "videos endpoint → videos polling."

## Supporting files

- [storyboard-gpt-image-2.md](storyboard-gpt-image-2.md) — Image 2 prompt formulas for each of the 8 beats
- [animate-seedance-2.md](animate-seedance-2.md) — Seedance 2.0 image-to-video formulas, per-beat

## Trigger phrases (for skill activation)

- "make a claymation ad"
- "Aardman-style ad for {product}"
- "stop-motion ad like {reference}"
- "clay-style 3D ad"
- "Wallace and Gromit style ad"
- "claymation story ad with {character name}"
- references to the [claymation example folder](../../../../Ai%20Annimation%20Ad%20Examples/claymation/)
