---
name: analyze-video
description: >
  Analyze a reference video and reverse-engineer its style into a reusable Seedance 2.0
  prompting template. The output is a new skill/formula (like seedance-2-ugc.md) that
  captures the video's structure, pacing, camera work, edit style, and tone so it can be
  recreated with any product, any person, in any setting. Use this whenever someone provides
  a video they want to use as a style reference, says "I want to make videos like this",
  "deconstruct this video", "turn this into a template", "analyze this style", or drops
  a video file and wants to recreate that format repeatedly.
---

# Analyze Video → Reusable Prompting Template

Someone found a video style they love. Your job is to deconstruct it into a reusable
prompting template — a formula they can plug any product, person, or setting into and
get that same style back from Seedance 2.0.

**Critical constraint: Seedance 2.0 has a 15-second maximum per clip.** The reference
video may be longer than 15 seconds (often 30-60s). Your template must be designed
for 15-second output — which means distilling the style's essence into what can be
captured in a single 15-second clip, and providing a multi-clip strategy for recreating
the full effect of longer-form styles across a series of clips.

The output is NOT a single prompt. It's a **template skill** saved to
`skills/kie-ai-external-api/prompting/prompt-library/` that works the same way
[seedance-2-ugc.md](../prompt-library/seedance-2-ugc.md) works — a documented formula
with layers, variables, options, and examples that the agent can use to generate unlimited
prompts in that style.

## Dependencies

- **ffmpeg** / **ffprobe** — required for frame extraction (Step 1). Install via `brew install ffmpeg` on macOS.
- **whisper** — optional, for audio transcription (Step 2). Install via `pip3 install openai-whisper`. If unavailable, the agent can ask the user to provide dialogue manually.

## Inputs

- **Video file** (required): path to `.mp4`, `.mov`, `.webm`, or similar
- **Style name** (optional): what to call this template (e.g., "car-review", "unboxing-hype", "skeptic-converted"). If not provided, you'll name it based on what you observe.

## Step 1: Extract frames and audio

Run the extraction script:

```bash
bash "skills/kie-ai-external-api/prompting/analyze-video/scripts/extract-frames.sh" "<video_path>" "/tmp/video-analysis" <num_frames>
```

Frame count by duration:
- Under 10s → 8 frames
- 10-20s → 12 frames
- 20-30s → 16 frames
- Over 30s → 20 frames

Read `metadata.txt` for duration, resolution, and fps.

## Step 2: Transcribe audio

Try transcription tools in this order:

1. `whisper` CLI: `whisper /tmp/video-analysis/audio.wav --model base --output_format txt --output_dir /tmp/video-analysis`
2. Python whisper: quick inline script
3. If nothing is available, ask the user to provide dialogue or install whisper (`pip3 install openai-whisper`)

The transcript helps you understand pacing, speech rhythm, filler word usage, and how
dialogue interleaves with action — all of which define the style.

## Step 3: Study the reference templates

Read the existing Seedance 2.0 prompting templates to understand the gold standard
for how a template should be structured:

- [seedance-2-ugc.md](../prompt-library/seedance-2-ugc.md) — 9-layer UGC formula (richest example)
- [seedance-2-premium-reveal.md](../prompt-library/seedance-2-premium-reveal.md) — 6-layer dark-void reveal
- [seedance-2-product-hero.md](../prompt-library/seedance-2-product-hero.md) — 6-layer elemental product hero
- [seedance-2-studio-lookbook.md](../prompt-library/seedance-2-studio-lookbook.md) — 7-layer studio lookbook
- [seedance-2-feature-walkthrough.md](../prompt-library/seedance-2-feature-walkthrough.md) — 7-layer feature demo

Also read the main model guide for platform rules:
- [seedance-2.md](../prompt-library/seedance-2.md) — API parameters, prompt length, forbidden words, adaptation checklist

Notice the structure these templates share:
- They identify **layers** (the structural building blocks of the style)
- Each layer has a **pattern** (the repeatable sentence structure with `{{VARIABLES}}`)
- Variables come with **option banks** (tables of choices that fit the style)
- There are **rules and principles** that explain why certain choices matter
- There are **complete examples** showing the template fully filled in

Your output template needs to hit the same level of depth and usability.

## Step 4: Analyze the frames — identify what defines this style

Read ALL extracted frames. You're not describing one specific video — you're identifying
the **transferable patterns** that make this style what it is.

Ask yourself for each dimension: "What about this is specific to THIS VIDEO (the person,
the product, the setting) vs. what is THE STYLE (the approach, the structure, the feel)?"

Only the style goes into the template. The specifics become variables.

### Structure & pacing
- How long is the video? (The source video will often be 30-60s, which is fine — you'll compress the style for 15s output.)
- How many distinct scenes/beats are there? Which 2-3 are the ESSENTIAL beats that define the style?
- What's the narrative arc? (hook → demo → proof → verdict? or something different?)
- What's the rhythm — fast cuts or lingering shots? How long does each beat last?
- Are there silent beats or is it all dialogue?
- **15-second compression question:** If you had to capture this video's entire feel in just 3 beats and 2-3 spoken lines, which moments would you keep?

### Camera & framing
- What's the primary filming perspective? (selfie, propped phone, someone else filming, screen recording, etc.)
- How does framing change between beats? (tighter, wider, different angle, same angle throughout)
- Is there a signature camera move or framing choice that defines this style?

### Edit style
- Jump cuts between takes? Continuous shot? Time-lapse? Split screen?
- How do transitions work? Hard cuts, dissolves, text overlays?
- Any recurring visual motifs? (close-up product shots, reaction face, before/after)

### Dialogue & script structure
- What's the hook format? (question, bold claim, mid-action, reaction)
- How is dialogue structured? (scripted, improvised, voiceover, text-on-screen)
- What speech patterns define the tone? (filler words, sentence length, vocabulary level)
- How do spoken lines relate to on-screen actions?

### Tone & energy
- What 3-4 emotion words capture the vibe?
- How does energy change across the video? (builds, stays flat, peaks then drops)
- What's the relationship to the viewer? (talking to a friend, addressing followers, thinking out loud)

### Lighting & technical quality
- What's the lighting approach? (natural, ring light, moody, overexposed)
- Phone quality or polished? What technical "flaws" are part of the aesthetic?
- Audio quality — phone mic, lapel, voiceover, ambient?

### What makes this style DIFFERENT
This is the most important analysis. After cataloging everything above, identify the
2-3 things that make this style distinct from a generic UGC video or a generic product
review. Maybe it's the pacing, maybe it's the hook format, maybe it's the way the product
is revealed, maybe it's the edit rhythm. These defining traits become the core of your
template.

### 15-second optimization plan
The source video is almost certainly longer than 15 seconds. Before building the template,
plan how the style maps to the Seedance 15-second limit:

- **What's the minimum viable version of this style?** Identify which beats/elements
  are essential vs. nice-to-have. A 15-second clip needs to capture the ESSENCE of the
  style — the thing that makes someone say "oh that's THAT kind of video."
- **Does this style need a multi-clip strategy?** If the style's power comes from a
  narrative arc (setup → payoff) or a feature rundown, it needs 2-3 clips. If the style
  is more about a vibe or a single moment, one clip might be enough.
- **How many spoken lines fit?** At natural pace, 15 seconds fits 2-3 short sentences.
  Count the lines in the source transcript and figure out which ones carry the style's
  voice. Those go in the template's dialogue rules.
- **What's the beat structure?** 15 seconds = 2-3 beats max. Map the source video's
  beat structure down to a 3-beat skeleton: hook → core moment → kicker.

## Step 5: Build the template

Create a new markdown file structured as a reusable prompting skill. The file should
be self-contained — someone should be able to read it and generate prompts in this
style without ever seeing the original video.

### Template structure

```markdown
# [Style Name] — Seedance 2.0

**Use when:** [describe the type of video this template produces]

**Model guide:** Read [seedance-2.md](seedance-2.md) first for platform rules, API parameters, and the adaptation checklist.

## What defines this style

[2-3 paragraphs explaining what makes this style distinctive and why it works.
This is the "theory" section — it helps the prompt writer understand the style
intuitively so they can make good variable choices, not just fill in blanks.]

## The structure

[Identify the layers/building blocks of THIS style. Don't force-fit the 9-layer
UGC model if this style works differently. If it's a 5-layer style, make it 5.
If it's 12, make it 12. Let the video's actual structure drive the template.]

## Layer-by-layer formula

### Layer N: [Name]

[Explain what this layer does and why it matters for this style.]

**Pattern:**
\```
[The repeatable sentence structure with {{VARIABLES}}]
\```

**Variables:**

| Variable | Options | Notes |
|----------|---------|-------|
| `VARIABLE_NAME` | option 1, option 2, option 3 | [guidance] |

[Include option banks, tips, and gotchas specific to this style]

### [... more layers ...]

## Beat structure (15-second format)

[Detail the 3-beat framework for a single 15-second clip in this style.
What's beat 1 (hook), beat 2 (core), beat 3 (kicker)? Which beats have
dialogue vs. silent action? Max 2-3 spoken lines total.]

## Multi-clip strategy (if applicable)

[If the full style needs more than 15 seconds, show how to split it across
2-3 clips. Each clip must stand alone with its own hook energy, but together
they recreate the full style. Include a table showing which features/moments
go in which clip.]

## Tone & pacing guide

[How to calibrate the energy, speech patterns, and rhythm for this style.
Include a pacing cue bank specific to this style.]

## Technical specs

[Lighting, camera quality, audio characteristics that define this style's
look and feel. Include the specific "flaws" that make it authentic.]

## Complete template

[A single copy-paste block for ONE 15-second clip with ALL variables
marked as {{PLACEHOLDERS}}. Max 3 beats, max 2-3 dialogue lines.
This is the core unit — every prompt generated from this template
produces one 15-second Seedance clip.]

## Example prompts

[Show a multi-clip example (2-3 clips) using a DIFFERENT product/person/setting
than the source video. Each clip is a complete 15-second prompt. Together
they demonstrate how the style works across a series.]

## Adaptation checklist

[A quick checklist to verify all layers are covered before submitting
the prompt. Always include the standard Seedance 2.0 checks from seedance-2.md.]
```

### Key principles for the template

- **Every prompt is 15 seconds.** This is a hard constraint from Seedance 2.0. The template
  must produce prompts that fit within 15 seconds — max 3 beats, max 2-3 spoken lines.
  If the style needs more, the template should include a multi-clip strategy showing how
  to split across 2-3 separate 15-second prompts.

- **Variables should be meaningful choices, not open-ended fill-in-the-blanks.** For each
  variable, provide a curated bank of options that fit this style. "Any lighting" is useless.
  "Natural window light, overhead kitchen light, golden hour balcony light" gives real guidance.

- **Capture the rules, not just the structure.** If the hook has to be a question, say so.
  If there should be exactly one silent beat, say so. The template should make it hard to
  write a bad prompt.

- **The example prompts must use DIFFERENT content than the source video.** If the source
  video was a woman reviewing a serum in her bedroom, the example should be a guy reviewing
  a protein bar in his kitchen (or whatever). This proves the template generalizes.

- **Include a `@(img1)` product image reference** in the template pattern, since Seedance
  prompts accept image references for the product.

- **Preserve the voice of the style.** If the original uses specific types of filler words,
  specific sentence structures, specific energy patterns — encode those into the template's
  dialogue rules and tone guide so every prompt generated from it sounds right.

- **Dialogue must fit 15 seconds.** A natural human speaks ~2-3 short sentences in 15
  seconds with pauses. If the source video has dense, fast dialogue, the template should
  note that the speaker's pace is fast and each line should be punchy and short. Count
  words — 30-40 spoken words is the realistic ceiling for 15 seconds.

- **Follow the Seedance 2.0 platform guide.** All templates must comply with
  [seedance-2.md](../prompt-library/seedance-2.md) — prompt length (100-260 words),
  no forbidden words ("cinematic," "professional," "stunning," "8k," "studio," "perfect"),
  explicit motion specificity, and consistency anchors for product references.

## Step 6: Save and present

1. Save the template to `skills/kie-ai-external-api/prompting/prompt-library/seedance-2-<style-name>.md`
2. Print a summary to the conversation:
   - What style was identified
   - The key layers/structure
   - What makes it distinctive
   - The file path where it was saved
3. Ask: "Want me to generate a test prompt using this template to make sure it works?"

If they say yes, generate a prompt for a different product/person/setting than the
source video — this validates the template is genuinely reusable.

## Step 7: Submit to kie.ai

After generating and saving a prompt, offer to submit it to kie.ai for video generation.

**API endpoint:** `POST /api/v1/jobs/createTask`

**Request body:**

```json
{
  "model": "bytedance/seedance-2",
  "input": {
    "prompt": "<the-generated-prompt>",
    "aspect_ratio": "9:16",
    "duration": 15,
    "resolution": "720p",
    "audio": true,
    "reference_image_urls": ["https://i.imgur.com/xxx.jpg"]
  }
}
```

**Before submitting:**

1. Ask whether to enable audio (`input.audio`).
2. If the user has product images, host them at a public HTTPS URL (see `SKILL.md` → "Reference images: hosting and public URLs") and pass the URLs in `input.reference_image_urls`. Base64 is no longer supported.
3. Show the cost estimate in USD and wait for confirmation.
4. Submit via the API. Poll `GET /api/v1/jobs/recordInfo?taskId=<id>` until the task is complete.

**For multi-clip series**, submit each clip as a separate `createTask` call and present all results together.

Include this API submission section in every template you generate:

```markdown
## Submitting to kie.ai

After filling in the template and generating your prompt:

1. Host product images at a public HTTPS URL (see SKILL.md → "Reference images: hosting and public URLs").
2. Submit via `POST /api/v1/jobs/createTask`:

\```json
{
  "model": "bytedance/seedance-2",
  "input": {
    "prompt": "<your-filled-prompt>",
    "aspect_ratio": "9:16",
    "duration": 15,
    "resolution": "720p",
    "audio": true,
    "reference_image_urls": ["https://i.imgur.com/xxx.jpg"]
  }
}
\```

3. Poll `GET /api/v1/jobs/recordInfo?taskId=<id>` until the task completes.

For multi-clip series, submit each clip as a separate API call.
```

## File map

```
skills/kie-ai-external-api/
├── SKILL.md                              ← main skill (decision tree, execution checklist)
├── reference.md                          ← API routes, body shapes, polling
├── prompting/
│   ├── guide.md                          ← marketing brief → API
│   ├── analyze-video/
│   │   ├── SKILL.md                      ← THIS FILE — reverse-engineer video styles
│   │   └── scripts/
│   │       └── extract-frames.sh         ← ffmpeg frame + audio extraction
│   └── prompt-library/
│       ├── seedance-2.md                 ← Seedance 2.0 model guide (platform rules)
│       ├── seedance-2-ugc.md             ← 9-layer UGC formula
│       ├── seedance-2-premium-reveal.md  ← dark-void premium reveal
│       ├── seedance-2-product-hero.md    ← elemental product hero
│       ├── seedance-2-studio-lookbook.md ← studio lookbook with voiceover
│       ├── seedance-2-feature-walkthrough.md ← feature walkthrough demo
│       ├── sora-2.md                     ← Sora 2 guide
│       ├── veo-3-1.md                    ← Veo 3.1 guide
│       ├── kling-3.md                    ← Kling 3.0 guide
│       └── ...                           ← other model guides
```
