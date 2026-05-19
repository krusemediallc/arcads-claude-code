# Pixar-style AI cartoon ad — cross-API prompting guide

**Aesthetic:** Disney-Pixar 3D animated feature film look applied to short-form product ads (TikTok/Reels/Shorts).
**Default pipeline:** **ChatGPT Image 2** for storyboard frames → **Seedance 2.0** image-to-video for animation → stitch with ffmpeg.
**Format:** 9:16 vertical, 60–90s total, 4–6 beats stitched from 4–15s Seedance clips, burned-in captions.

Use this guide when the user asks for a "Pixar-style ad," "Pixar cartoon ad," "3D animated ad," or shows a reference video that matches the look in [the example folder](../../../../Ai%20Annimation%20Ad%20Examples/Pixar%20Ads/).

> Sibling guides (planned): claymation, stop-motion, anime, 2D-Saturday-morning. Each is its own folder under `content/skills/<style>-ad/`.

## What "Pixar style" means here (and what it doesn't)

The look is the **Disney-Pixar feature film aesthetic** specifically — not generic CGI, not Studio Ghibli (that's 2D), not anime, not Dreamworks-stretchy. Anchor every prompt on these traits:

- **3D rendered**, full volumetric lighting, ray-traced reflections
- **Oversized expressive eyes** with multiple specular highlights (the Pixar "wet eye")
- **Stylized but believable proportions** — slightly larger heads, soft features, simplified hands, smooth flowing forms
- **Rich material rendering** — subsurface scattering on skin, detailed fabric weave (waffle robes, knitwear), realistic hair strands, glass/liquid refraction
- **Soft warm golden-hour interior lighting** — sunlight through curtains, window light, lamp glow; almost never harsh top-down or fluorescent
- **Shallow depth of field** with creamy bokeh; subject always sharply rendered
- **"Appeal"** — characters look like they're about to smile, mid-emotion, never blank-staring
- **Anthropomorphism welcome** — objects with faces/limbs/eyes are core to the genre

**Do NOT use these words** (they pull away from the Pixar look):
`anime`, `Ghibli`, `2D`, `cel-shaded`, `cartoon` (yes — say "Pixar-style 3D animated" instead), `Dreamworks`, `realistic photo`, `live action`, `photorealistic`. Also avoid Seedance's forbidden words list when prompting Seedance: `cinematic`, `professional`, `stunning`, `8k`, `studio`, `perfect`.

## The 4-beat Pixar ad arc (what makes these ads work)

Every successful Pixar-style product ad in this genre follows roughly the same structure. The hook is **anthropomorphism + a tiny story**, not the product. Plan all 4 beats upfront so character/setting are consistent across stills.

| Beat | Length | Purpose | What's on screen |
|------|--------|---------|------------------|
| **1. Hook — anthropomorphized problem** | 3–6s | Give the user's pain point a sentient face and voice. The pain point itself is the character. | Close-up macro shot of the problem object given Pixar eyes/mouth (e.g. a clump of hair in a drain, a cracked fingernail, a tired pillow, a moody pile of laundry). It speaks the user's complaint in first person. |
| **2. Reveal — protagonist meets product** | 4–8s | Cut to a Pixar-style human in a sunlit cozy interior, introducing the product. | Big-eyed protagonist (robe, knitwear, soft hair) holding the product, soft window light, plants in background. Surprised/delighted expression. |
| **3. Mechanism-of-action — mascot scene** | 6–10s | Visualize *how* the product works using cute mascot characters inside the body / inside a structure. | Stylized interior (skin layers, hair follicle, joint, gut) with chibi mascot characters actively doing the mechanism — repairing collagen fibers, stitching keratin, plumping cells. Glowing energy lines connect them. |
| **4. CTA — protagonist + packaging** | 4–6s | Resolve the hook by showing the protagonist with the product packaging, captioned CTA. | Protagonist now smiling/confident, holding one or two product packs facing camera. Burned-in caption: "Try {Brand} {Product} now." |

Variations:
- **Cold-open intercut**: alternate Beat 1 (problem character) with quick cuts of the human protagonist looking distressed before settling into Beat 2. Adds urgency.
- **Multi-pain montage**: 3–4 anthropomorphized problem characters in sequence ("I clog your drain", "I weigh down your hair", "I make you self-conscious") before Beat 2.
- **Testimonial overlay**: Beat 2 protagonist speaks the value prop in first person ("I tried this for 30 days and...") instead of a third-person narrator.

## Cast & continuity sheet (do this BEFORE generating anything)

Pixar ads live or die on **character continuity across beats**. Build a one-page sheet you reuse in every Image 2 prompt:

```
PROTAGONIST (human hero)
- Age range: 20s / 30s / 40s
- Build: petite / average / curvy
- Hair: color, length, style (e.g. "ash-brown low bun with face-framing strands")
- Eyes: color, large Pixar irises, multiple catchlights
- Skin: warm undertone with light freckles across nose bridge
- Outfit: cream waffle-knit robe over fitted tank, gold thin necklace
- Personality cue: gentle smile, slightly tilted head

ANTHROPOMORPHIC PROBLEM CHARACTER (beat 1)
- What object: <e.g. clump of dark hair in shower drain>
- Face placement: <e.g. two big sad eyes and small downturned mouth embedded in the hair>
- Voice/personality: <e.g. defeated, weary, mumbling>

MASCOT CHARACTERS (beat 3)
- Form: chibi blob, 2–3 inches "tall", smooth matte rubbery material
- Color: ivory white with soft pink cheeks
- Eyes: tiny black dot pupils, single highlight, oversized
- Behavior: cooperative team, gently working on the mechanism

SETTING
- Beat 2 & 4: sunlit bedroom or kitchen, sheer curtains, plant in clay pot, soft warm color grade
- Beat 3: stylized cross-section interior of <skin / hair follicle / joint / etc.>

PRODUCT
- Packaging colors / shape / label text (paste from the brand or take from product photo)
- Held at chest height with one or both hands, facing camera

STYLE LOCK (paste verbatim into every image prompt)
"Disney-Pixar 3D animated feature film aesthetic, soft volumetric golden-hour lighting,
subsurface scattering on skin, large expressive eyes with multiple catchlights, stylized
but believable proportions, rich material rendering, shallow depth of field, warm cozy
color palette, painterly background."
```

Save this sheet in `references/<brand>-pixar-cast.md` so the next ad in the same campaign reuses it.

## Pipeline: Image 2 → Seedance 2.0 → stitch

### Why this order

1. **Image 2 for storyboard stills** — gpt-image-2 produces the most consistent stylized 3D-animated stills currently available, especially when you re-feed prior outputs as reference images for the next frame in the storyboard. It holds character identity across beats far better than text-to-video text-only.
2. **Seedance 2.0 image-to-video** — animates each still while preserving the rendered character. Seedance 2 takes a reference image in `input.image_input` and produces 4–15s of motion driven by a text prompt.
3. **ffmpeg concat** — stitch the per-beat clips into one continuous 60–90s vertical video and (optionally) burn in TikTok-style captions.

### One-shot text-to-video is the wrong choice

Don't try to one-prompt the whole ad in Seedance 2.0. You'll get character drift between beats, and Seedance's 15s ceiling caps you below the typical 60–90s ad length anyway. The image-first pipeline is mandatory for this style.

### Step-by-step

1. **Lock the cast sheet** with the user (above). Confirm protagonist appearance, packaging, brand voice.
2. **Write the 4–6 beat script** as plain English narration with timestamps. One sentence per beat. Get user approval before any generation.
3. **Generate Beat 1 hero still** with Image 2 using the storyboard formula in [storyboard-gpt-image-2.md](storyboard-gpt-image-2.md). Show user. Iterate until approved.
4. **Generate Beats 2–N hero stills** one at a time, passing the prior approved still(s) as reference inputs to lock continuity. Approve each before moving on.
5. **Animate each still with Seedance 2.0** using the formula in [animate-seedance-2.md](animate-seedance-2.md). Run beats in parallel (KIE allows up to 100 concurrent tasks). Default `duration` to match the beat target (4–15s).
6. **QA each clip** — watch for character morphing, hand artifacts, product-label drift, eye misalignment. Regenerate up to 2 retries per beat (see KIE SKILL.md "Generated image QA" — same rule applies to video frames).
7. **Stitch with ffmpeg** — `ffmpeg -f concat -safe 0 -i list.txt -c copy ad.mp4` (re-encode with `-c:v libx264 -c:a aac` if codecs differ).
8. **Burn captions** (optional) — TikTok-style: white sans-serif (Montserrat/Proxima Bold), thick black stroke, mid-low third placement. Use `ffmpeg drawtext` or pre-export an `.ass` subtitle file and burn with `-vf subtitles=`.

### Aspect ratio & resolution defaults

- **Aspect ratio:** `9:16` (vertical) for TikTok / Reels / Shorts. Use `1:1` only if the user explicitly wants a feed post. Avoid `16:9` for this genre — the framing assumptions in the prompts (close-up macros, head-and-shoulders human shots) don't translate.
- **Image 2 output size:** 1024×1792 (vertical). Pass this into Seedance as `input.image_input[0]`.
- **Seedance resolution:** `720p` default, `480p` for cost-sensitive drafts.

## Cost & confirmation (mandatory)

Before firing any generation, calculate and present total credit cost to the user. Standard KIE rule (see [KIE SKILL.md "Credit cost estimation"](../../kie-external-api/SKILL.md#credit-cost-estimation-mandatory--show-before-generating)).

For a typical 5-beat ad:
- 5× Image 2 frames (storyboard) — record per-image cost from prior runs in `logs/kie-api.jsonl` or ask the user
- 5× Seedance 2 clips @ 720p, 8–15s each — Seedance 2 wall-clock is ~3–4 min per clip
- Plus retries (cap 2 per beat per QA rule)

Always wait for explicit confirmation before firing.

## Negative prompt block (paste into every video prompt)

```
no live-action footage, no photorealistic faces, no anime style, no 2D cel-shaded
look, no Studio Ghibli style, no flat illustration, no harsh fluorescent lighting,
no extra fingers, no melted features, no morphing between frames, no warped product
labels, no on-screen text unless specified, no subtitles, no captions
```

For Seedance 2 specifically, also strip the model's forbidden words from your prompt: no `cinematic`, `professional`, `stunning`, `8k`, `studio`, `perfect`. Substitute: "3D animated film aesthetic" for cinematic; "polished" for stunning; "high fidelity" for 8k; "ivory white matte material" for perfect.

## Captioning (the TikTok burned-in look)

If the user wants the white-text-with-black-outline TikTok caption style:

- **Font:** Proxima Nova Bold, Montserrat Bold, or system Inter Bold (use a license you own). Avoid Arial — looks dated.
- **Size:** ~7% of video height
- **Position:** lower third, centered horizontally, ~25% from the bottom (above the TikTok UI overlay)
- **Style:** white fill, 4–6 px solid black stroke, no drop shadow
- **Timing:** caption changes per spoken phrase, not per word. Display for the duration of the phrase + 0.3s buffer.
- **Burn pipeline:** write the captions to an `.ass` (Advanced SubStation) file with timing, then `ffmpeg -i clip.mp4 -vf "subtitles=caps.ass" out.mp4`. This is more reliable than `drawtext` for multi-line timing.

**Important — let Seedance render the scene WITHOUT captions.** Tell Seedance "no on-screen text, no captions, no subtitles" in every prompt. Burn captions on after stitching, with control. Seedance occasionally invents captions when you don't ask for them — the negative prompt fights this.

### Recommended pipeline: HyperFrames-rendered animated captions

For per-phrase emphasis (scale-pop on punchlines, brand-color callouts on the product reveal), use the [`hyperframes`](../../../shared/skills/hyperframes/) skill rather than static `.ass` burning. Quick recipe:

1. `npx hyperframes init pixar-captions --video <your-stitched-ad.mp4> --non-interactive --example blank` — scaffolds project + auto-transcribes audio (whisper.cpp, word-level timestamps).
2. **Flatten whisper.cpp tokens to a clean word array** — whisper splits multi-syllable brand/product words (ASHWAGANDHA, sourceless, gummy) into subword fragments. Merge tokens using the leading-space convention (tokens with leading space are word-starts; without are continuations). Fix any homophone misreads.
3. **Group words into 3–4 word caption phrases**, breaking on sentence end / >0.6s pauses / 4-word cap. Treat `Mr.`, `Mrs.`, `Dr.`, `Ms.` as non-sentence-end so brand names don't get split.
4. **Build the composition with the captions track only** — see the [HF gotcha block below](#-hyperframes-gotcha-portrait-video-clipping). Tag groups by emphasis (`normal` / `comedic` / `brand` / `product`) and style per [shared/skills/hyperframes/references/captions.md](../../hyperframes/references/captions.md) (social / hype tone for Pixar: bold scale-pop, bright cream/pink palette).
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
     data-duration="<ad-duration>"
     data-width="720"
     data-height="1280"
     style="position: relative; width: 720px; height: 1280px;">
  <div id="captions"></div>
</div>
```

Use `--format mov` (ProRes 4444) for the alpha render — `--format webm` came out as `yuv420p` (no alpha) in our test even though the docs say WebM supports transparency, while `--format mov` reliably produced `yuva444p12le`. The MOV is ~3× larger as an intermediate, but it gets discarded after the ffmpeg composite.

## Per-API endpoint notes (KIE vs Arcads)

The **prompt content is identical** across APIs — the storyboard and animation files in this folder are the source of truth. The differences are auth, endpoint paths, and how reference images are delivered. Pick the API from `MASTER_CONTEXT.md` or ask the user.

### KIE.ai

| Step | Endpoint | Model string | Reference images |
|------|----------|--------------|------------------|
| Storyboard (Image 2) | `POST /api/v1/jobs/createTask` | `gpt-image-2` (verify on [kie.ai/market](https://kie.ai/market)) | Public URLs in `input.image_input[]` |
| Animation (Seedance 2.0) | `POST /api/v1/jobs/createTask` | `bytedance/seedance-2` | Public URL in `input.image_input[]` |
| Polling | `GET /api/v1/jobs/recordInfo?taskId=...` | — | — |
| Auth | `Authorization: Bearer $KIE_API_KEY` | — | — |

Reference image delivery requires a public URL (CDN/bucket/Cloudinary/etc.). KIE has no presigned-upload flow. Auto-upscale any image below 1024 px longest side per [KIE SKILL.md "Image handling"](../../kie-external-api/SKILL.md#image-handling-auto-upscale-small-inputs).

### Arcads

| Step | Endpoint | Model string | Reference images |
|------|----------|--------------|------------------|
| Storyboard (Image 2) | `POST /v2/images/generate` | `gpt-image-2` | `referenceImages: [filePath, ...]` — **max 5** for `gpt-image-2` (per [Arcads reference.md:287](../../arcads-external-api/reference.md)). Upload via `POST /v1/file-upload/get-presigned-url` first to get the `filePath` |
| Animation (Seedance 2.0) | `POST /v2/videos/generate` | `seedance-2.0` | `startFrame` URL from approved storyboard still |
| Polling | `gpt-image-2` → `GET /v1/assets/{id}`. **Seedance 2.0 → `GET /v1/assets/{id}` (NOT `/v1/videos/{id}`)** — see gotcha below. | — | — |
| Auth | `Authorization: $ARCADS_BASIC_AUTH` header (the env var already contains the `Basic ...` prefix — do NOT add another `Basic ` in front of it). | — | — |

Arcads' Image 2 cap of 5 reference images is **not a problem** for this skill — each beat only chains 1–2 prior stills as continuity references.

### When MASTER_CONTEXT.md picks the API

Check `MASTER_CONTEXT.md` for a preferred API for ad generation; default to whatever's noted there. Otherwise ask the user once per session, and write the choice into `MASTER_CONTEXT.md` so the next session inherits it.

### Arcads gotchas confirmed in testing (2026-05-19)

Two things to know up front when running the storyboard → animate flow on Arcads. Both are also recorded in [`shared/skills/arcads-external-api/reference.md`](../../arcads-external-api/reference.md) for the broader API surface.

**1. Presigned `filePath` is one-time-use.**
A `filePath` returned by `POST /v1/file-upload/get-presigned-url` works for exactly **one** downstream generation call. The first call that references it (e.g. Beat 2 using Beat 1 as a reference image) consumes it; every subsequent call referencing the same `filePath` returns `HTTP 400 REFERENCE_FILE_NOT_FOUND`.

In this skill the hero still gets passed as the protagonist anchor to Beats 2, 3, 4 (or more in claymation). **Re-upload it once per call** — the file is small, the upload is fast, and it's the only path that works. Don't try to "cache" `filePath` across parallel calls.

**2. Seedance 2.0 video jobs poll the assets endpoint, not the videos endpoint.**
Even though Seedance 2.0 is fired via the unified `POST /v2/videos/generate`, its job record lives at `GET /v1/assets/{id}` — the create response returns `type: "seedance_20"` and `GET /v1/videos/{id}` for the same id returns `HTTP 404`. The final mp4 URL lands on the top-level `url` field of the asset response (presigned S3, ~12h lifetime).

This is the opposite of the other video models on the same endpoint (`sora2`, `veo31`, `kling-*`, `grok-video`) which all poll under `/v1/videos/{id}`. Pick the polling path by inspecting the `type` field on the create response, not by assuming "videos endpoint → videos polling."

## Supporting files

- [storyboard-gpt-image-2.md](storyboard-gpt-image-2.md) — ChatGPT Image 2 prompt formulas for each of the 4 beats
- [animate-seedance-2.md](animate-seedance-2.md) — Seedance 2.0 image-to-video formulas, per-beat
- [reference-stack.md](reference-stack.md) — list of public reference videos and visual style anchors

## Trigger phrases (for skill activation)

- "make a Pixar-style ad"
- "Pixar cartoon ad for {product}"
- "3D animated ad like {reference}"
- "animated ad with the [object] character"
- "Pixar-style storyboard for an ad"
- references to the [Pixar Ads example folder](../../../../Ai%20Annimation%20Ad%20Examples/Pixar%20Ads/)
