# Animate the storyboard — Seedance 2.0 image-to-video

**Use this guide after every storyboard still is approved.** Each still becomes one Seedance 2.0 clip; clips get stitched into the final ad.

Read [guide.md](guide.md) for the 4-beat arc and [storyboard-gpt-image-2.md](storyboard-gpt-image-2.md) for how the stills were generated.

## Seedance 2 platform basics (the parts that matter here)

For the full Seedance 2 model guide on KIE, see [../../kie-external-api/prompting/prompt-library/seedance-2.md](../../kie-external-api/prompting/prompt-library/seedance-2.md). Key rules for Pixar-style ads:

- **Endpoint:** `POST /api/v1/jobs/createTask` with `"model": "bytedance/seedance-2"` (verify on [kie.ai/market](https://kie.ai/market))
- **Image input:** pass the approved storyboard URL as `input.image_input[0]` — this anchors the character/scene
- **Duration:** continuous 4–15s. Match the beat target.
- **Aspect ratio:** `"9:16"` (vertical)
- **Resolution:** `"720p"` default
- **Prompt length:** 100–260 words, structured `Subject + Action + Camera + Style + Constraints`
- **Forbidden words for Seedance 2** (do not use even though the Pixar guide allows them generally): `cinematic`, `professional`, `stunning`, `8k`, `studio`, `perfect`. Substitute with: "3D animated film aesthetic", "polished", "high fidelity", "ivory white matte material".

## Universal animation prompt structure

```
[BEAT INTRO]            ← what this clip is
[SUBJECT LOCK]          ← reference the image_input character/scene
[ACTION]                ← one primary motion, with degree adverbs
[CAMERA]                ← framing + camera movement
[STYLE ANCHOR]          ← "3D animated film aesthetic" + Pixar tone words
[DIALOGUE / AUDIO]      ← if any
[CONSTRAINTS]           ← consistency + negatives
```

## Beat 1 — animate the anthropomorphized problem

**Target duration:** 4–6s (1 short spoken line + a slight reaction beat)

**Pattern:**

```
3D animated film aesthetic, image-to-video animation of the character in @(img1).

Subject: {{PAIN_POINT_CHARACTER}} — fully described, matches the still exactly.

Action (0-2s): The character {{SUBTLE_IDLE_MOTION}} — eyes blink once slowly, mouth
trembles slightly, body sags a touch more. (2-{{END}}s): The character looks up at
camera and speaks: "{{LINE}}" — small mouth shapes match the syllables, eyebrows
raise mid-line, a single tear slides down at the end.

Camera: Locked extreme close-up macro, slight handheld micro-drift, no zoom or pan.

Style: Disney-Pixar 3D animated feature film aesthetic, soft volumetric lighting,
subsurface scattering, painterly background, shallow depth of field. Warm cozy
color grade.

Audio: Soft small voice with a hint of {{TONE}} — vulnerable, slightly nasal,
intimate close-mic. Light ambient {{AMBIENT_SOUND}} in the background.

Constraints: The character must remain visually unchanged from @(img1) — same
proportions, same eye color, same surface texture. No live-action footage, no
photorealistic transformation, no extra eyes, no morphing limbs, no on-screen text,
no subtitles, no captions.
```

**Worked example (drain hair, 5s, "I clog your shower drain"):**

```
3D animated film aesthetic, image-to-video animation of the character in @(img1).

Subject: A dark tangled clump of hair sitting in a stainless steel shower drain,
with two oversized Pixar eyes embedded in it, exhausted half-lidded expression, a
small downturned mouth, soap bubbles around the drain.

Action (0-2s): The hair clump's eyes blink once slowly. Its small mouth quivers,
and the whole clump sags a touch lower over the drain edge. (2-5s): The eyes lift
to look up at the camera. Its mouth opens to speak: "I clog your shower drain." A
single tear gently slides down the side of the hair clump as the line finishes,
catching the warm light.

Camera: Locked extreme close-up macro, very subtle handheld micro-drift, no zoom or
pan. Shallow depth of field, drain rim slightly out of focus.

Style: Disney-Pixar 3D animated feature film aesthetic, soft warm ambient lighting
from above the drain, subsurface scattering on the wet hair strands, painterly
soft-focus tile background. Slightly desaturated warm color grade.

Audio: Soft small voice with a hint of vulnerable defeat — slightly nasal, intimate
close-mic. Faint shower drip ambient sound in the background.

Constraints: The hair clump must remain visually unchanged from @(img1) — same shape,
same eye placement, same drain. No live-action footage, no photorealistic hair, no
extra eyes, no morphing limbs, no on-screen text, no subtitles, no captions, no
cinematic color grading.
```

## Beat 2 — animate the protagonist reveal

**Target duration:** 6–8s (1–2 short lines + product hold gesture)

**Pattern:**

```
3D animated film aesthetic, image-to-video animation of the protagonist in @(img1).

Subject: {{PROTAGONIST_DESCRIPTION exactly as in the still}} holding {{PRODUCT
exactly as in the still}}.

Action (0-2s): She looks down at the product in her hands with delighted curiosity,
lips parting slightly. (2-{{MID}}s): She slowly raises her eyes from the product up
to the camera, lips curving into a gentle smile, eyebrows lifting in surprise.
({{MID}}-{{END}}s): She tilts her head slightly, leans the product a touch closer to
camera, and speaks: "{{LINE}}" — natural lip sync, small head nods on emphasized
words.

Camera: Locked medium head-and-shoulders, vertical 9:16, very subtle handheld
breathing motion. No dolly, no pan.

Style: Disney-Pixar 3D animated feature film aesthetic, soft golden-hour window
light wrapping camera-left to camera-right, painterly soft-focus interior
background, shallow depth of field, warm cozy color palette of cream, butter
yellow, and dusty pink.

Audio: Warm relatable young-adult voice, gentle and enthusiastic, intimate close-mic.
Soft room tone, faint birdsong outside.

Constraints: The protagonist must remain visually unchanged from @(img1) — same hair,
same eye color, same outfit, same freckles. Product label must remain visually
unchanged. No live-action, no photorealistic face, no extra fingers, no morphing
features, no on-screen text, no subtitles, no captions.
```

## Beat 3 — animate the mascot mechanism scene

**Target duration:** 8–12s (silent or voiceover; mascots do the work)

**Pattern:**

```
3D animated film aesthetic, image-to-video animation of the scene in @(img1).

Subject: A stylized cross-section of {{INTERIOR_STRUCTURE}} populated by {{N}} small
chibi ivory-white mascot characters with tiny black-dot eyes, soft pink cheeks, and
simple rounded limbs. {{ENERGY_VISUAL}} traces through the structure.

Action (0-3s): The mascots begin {{PRIMARY_MECHANISM}} in coordinated motion — each
mascot pulls, smooths, weaves, or stitches in the same rhythm. (3-{{MID}}s): The
{{ENERGY_VISUAL}} brightens and pulses outward from their work, lighting up the
surrounding {{STRUCTURE_DETAIL}}. ({{MID}}-{{END}}s): The mascots pause, look around
at their finished section, give each other tiny celebratory glances, and the entire
structure now glows softly and evenly.

Camera: Slow gentle dolly-in toward the center of the action, 9:16 vertical
framing. Maintains focus on the mascots throughout.

Style: Disney-Pixar 3D animated feature film aesthetic, soft warm interior glow,
painterly ivory-and-gold color palette, subsurface scattering on the mascot bodies,
shallow depth of field with creamy bokeh.

Audio: Soft magical sparkle sounds matching each mascot motion, warm ambient hum,
no dialogue. Optional gentle voiceover: "{{LINE}}" — calm, instructive, warm.

Constraints: The mascots must remain visually consistent — same ivory color, same
proportions, same eye style — throughout the clip. The structure cross-section must
remain unchanged in geometry. No live-action, no photorealistic anatomy, no
horror-style organs, no extra mascot limbs, no morphing, no on-screen text, no
subtitles, no captions.
```

## Beat 4 — animate the CTA

**Target duration:** 4–6s (final smile + product hold)

**Pattern:**

```
3D animated film aesthetic, image-to-video animation of the protagonist in @(img1).

Subject: {{PROTAGONIST_DESCRIPTION exactly as in beat 2}} now facing the camera
directly, holding {{ONE OR TWO product packages}} at chest height with labels
toward camera.

Action (0-2s): She gives a warm confident smile, eyes brightening, a small happy
head tilt. (2-{{END}}s): She raises the {{packages}} a touch closer to the camera,
the labels rotating slightly so they read cleanly. Her smile widens into a small
satisfied grin at the very end.

Camera: Locked medium shot, vertical 9:16, gentle handheld breathing motion. No
dolly or zoom.

Style: Disney-Pixar 3D animated feature film aesthetic, soft golden-hour window
light from camera-left, painterly soft-focus background, warm cozy color palette.

Audio: Same warm protagonist voice as beat 2, optional short closing line:
"{{LINE}}" — confident and inviting. Soft room tone.

Constraints: The protagonist must remain visually identical to beat 2 — same hair,
same eye color, same outfit, same freckles, same skin tone. Product label must
remain visually identical to the still. Lower third of frame must remain visually
clean for a post-production caption overlay. No live-action, no photorealistic
face, no extra fingers, no morphing, no on-screen text, no subtitles, no captions.
```

## Cross-clip continuity rules

1. **Each clip's `image_input[0]`** must be the approved still for that beat. Don't try to chain by using a frame from a prior animation as the next beat's anchor — animated frames drift.
2. **Lift the protagonist description verbatim** from the cast sheet into beats 2 and 4. Do NOT paraphrase.
3. **Keep the STYLE block consistent** across all beats (substitute "3D animated film aesthetic" everywhere; do not use Seedance's forbidden words).
4. **Run beats in parallel** once all stills are approved — KIE allows up to 100 concurrent jobs. Poll all `taskId`s every ~30s.
5. **Log each call** to `logs/kie-api.jsonl` with `model`, `duration`, `resolution`, and `costTime` for future cost estimates.

## Per-clip QA

For each Seedance result, watch the full clip and check:

- [ ] **Character identity holds** from the input still to the last frame
- [ ] **No finger / limb morphing** — count fingers on every visible hand throughout the clip
- [ ] **No product-label drift** — the label text and colors stay legible and identical
- [ ] **Lip sync is plausible** if dialogue is present (rough match is fine; full Veo/Sora-level sync is not Seedance's strength)
- [ ] **No burned-in text or subtitles** appeared
- [ ] **Motion respects the prompt** — primary action happens, no random unrelated motion

If any check fails, regenerate that beat with a tightened constraint block (e.g. "the protagonist's hands have exactly five fingers each, no morphing"). 2-retry cap per beat.

## Stitching the final ad

After all beats are approved:

```bash
# In the session outputs folder, build the concat list
cat > list.txt <<EOF
file 'beat1.mp4'
file 'beat2.mp4'
file 'beat3.mp4'
file 'beat4.mp4'
EOF

# If all clips share the same codec/resolution:
ffmpeg -f concat -safe 0 -i list.txt -c copy ad_no_caps.mp4

# If codecs differ (re-encode):
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k -movflags +faststart ad_no_caps.mp4
```

Then burn captions (see [guide.md → Captioning](guide.md#captioning-the-tiktok-burned-in-look)).

## Cost notes (per the KIE Seedance 2 guide)

- Seedance 2 wall-clock: ~3–4 min per clip @ 720p
- 5-beat ad = 5× Seedance calls (in parallel) + retries
- Image 2 storyboard: 5× Image 2 calls (sequential, for continuity) + retries
- Total credit estimate must be presented to the user before firing (mandatory per the [KIE SKILL.md credit-cost rule](../../kie-external-api/SKILL.md#credit-cost-estimation-mandatory--show-before-generating))
