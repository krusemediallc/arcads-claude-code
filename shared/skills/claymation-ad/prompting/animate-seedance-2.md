# Claymation animation — Seedance 2.0 image-to-video

Use this guide after every storyboard still is approved. Each still becomes one Seedance 2.0 clip; the 8 clips get stitched into the final ad.

Read [guide.md](guide.md) for the 8-beat arc and [storyboard-gpt-image-2.md](storyboard-gpt-image-2.md) for how the stills were generated.

## Seedance 2 platform basics (what changes for claymation)

For the full Seedance 2 model guide on KIE see [../../kie-external-api/prompting/prompt-library/seedance-2.md](../../kie-external-api/prompting/prompt-library/seedance-2.md). Claymation-specific rules:

- **Endpoint:** `POST /api/v1/jobs/createTask` with `"model": "bytedance/seedance-2"` (KIE) or `POST /v2/videos/generate` with `"model": "seedance-2.0"` (Arcads). Verify model string on the marketplace page.
- **Image input:** pass the approved still as `input.image_input[0]` (KIE) or `startFrame` (Arcads).
- **Duration:** continuous 4–15s. Match each beat target from [guide.md](guide.md).
- **Aspect ratio:** `"9:16"`.
- **Resolution:** `"720p"`.
- **Prompt length:** 100–260 words, `Subject + Action + Camera + Style + Constraints`.
- **Forbidden Seedance words** (do not use): `cinematic`, `professional`, `stunning`, `8k`, `studio`, `perfect`. Use instead: "stop-motion claymation film aesthetic", "polished hand-sculpted", "high fidelity", "evenly hand-painted".
- **Critical for this style:** the motion must read as **smooth AI-rendered animation that preserves the claymation aesthetic of the still**. Do NOT ask Seedance to "stop-motion judder" — that breaks the look. If the user wants judder, post-process with ffmpeg after stitching (see [guide.md → Smooth motion vs stop-motion judder](guide.md#smooth-motion-vs-stop-motion-judder--pick-one)).

## Universal animation prompt structure

```
[BEAT INTRO]            ← what this clip is
[SUBJECT LOCK]          ← reference the image_input character/scene exactly
[ACTION]                ← one primary motion + small secondary motions, with degree adverbs
[CAMERA]                ← framing + small camera motion (often locked or breathing)
[STYLE ANCHOR]          ← "stop-motion claymation film aesthetic" + Aardman tone words
[NARRATOR / AUDIO]      ← narrator VO line, character dialogue if any, ambient sound
[CONSTRAINTS]           ← consistency + negatives, claymation-specific
```

## Reusable subject lock fragments

Lift these verbatim into the SUBJECT LOCK block of every relevant beat. Same phrasing every time.

```
DIANE (protagonist):
"Diane, a woman in her late 50s with shoulder-length terracotta-brown wavy
plasticine hair sculpted in distinct ribbon-strands, matte clay skin with
visible thumbprint impressions and deep sculpted laugh lines, warm brown
matte clay eyes set into deep sockets, sculpted brow furrow. She wears a
cream chunky knit cardigan with visible wool weave over a rust-red blouse,
dark wool trousers, brown leather slippers."

MARGARET (supporting):
"Margaret, a woman in her 60s with silver curly plasticine hair (carved
strand grooves), round wire glasses, sage-green cable-knit sweater with
visible wool weave, matte clay skin."

PRIMARY SETTING (Diane's kitchen):
"A sunlit miniature claymation kitchen — green-painted wooden cabinets,
red gingham tablecloth, hand-thrown ceramic cups, copper kettle on a small
stove, potted herbs on the windowsill, warm tungsten light from a window
on camera-left."
```

## Beat 1 — animate the setup

**Target duration:** 8–10s (narrator intro + light idle motion)

```
Stop-motion claymation film aesthetic, image-to-video animation of the
scene in @(img1).

Subject: {{PROTAGONIST_FRAGMENT}} in {{PRIMARY_SETTING_FRAGMENT}}.

Action (0-3s): She slowly pours tea from the ceramic kettle into the wide
cup, the stream of tea moving naturally. (3-{{MID}}s): She gently sets the
kettle down on the counter, her sculpted hand turning slightly. ({{MID}}-{{END}}s):
She tilts her head a touch toward the window, expression calm and unhurried,
sculpted eyelids blinking once slowly. Subtle micro-motion in the steam
rising from the cup.

Camera: Locked medium-wide shot, very subtle handheld macro breathing
motion (the miniature-set feel). No zoom or pan.

Style: Stop-motion claymation film aesthetic, Aardman-style hand-sculpted
plasticine characters, matte clay surfaces, real knit-fabric clothing, warm
tungsten interior lighting, shallow macro depth of field with soft
photographic bokeh.

Narrator (warm, mid-pace, slight smile in voice): "{{NARRATOR_LINE}}"
Ambient: faint kettle pour, soft kitchen room tone, distant birdsong outside.

Constraints: The protagonist must remain visually unchanged from @(img1) —
same plasticine hair ribbon-strands, same matte clay skin with thumbprint
impressions, same cream knit cardigan with wool weave, same eye sockets.
The kitchen set must remain visually unchanged. No live-action, no
photorealistic transformation, no Pixar smoothing, no 3D ray-traced
materials, no extra fingers, no morphing, no on-screen text, no subtitles,
no captions.
```

---

## Beat 2 — animate the inciting moment

**Target duration:** 6–8s (close-up reaction)

```
Stop-motion claymation film aesthetic, image-to-video animation of the
character in @(img1).

Subject: {{PROTAGONIST_FRAGMENT}} in tight close-up at the bathroom mirror.

Action (0-2s): Her sculpted clay fingertip lifts toward her upper lip and
gently touches the area where the small carved lines are visible. Her eyes
follow her own fingertip in the mirror. (2-{{END}}s): Her sculpted brow
furrows a touch more, mouth slightly opens in quiet alarm. A single slow
sculpted blink. She holds the moment, very still.

Camera: Locked tight close-up, very subtle handheld micro-drift, no zoom
or pan. Shallow macro depth of field.

Style: Stop-motion claymation film aesthetic, hand-sculpted plasticine,
matte clay surfaces, soft directional tungsten light from camera-right.

Narrator (concerned, gentle): "{{NARRATOR_LINE}}"
Ambient: very soft bathroom room tone, faint plumbing hum.

Constraints: The protagonist must remain visually unchanged from @(img1) —
same plasticine hair strands, same matte clay skin with thumbprint
impressions, same sculpted eye sockets with single matte highlight. The
sculpted lip lines must remain in the same position. No live-action, no
photorealistic skin smoothing, no Pixar wet-eye sheen, no morphing, no
on-screen text, no subtitles, no captions.
```

---

## Beat 3 — animate the two-character scene

**Target duration:** 8–10s (one character speaks, the other reacts)

```
Stop-motion claymation film aesthetic, image-to-video animation of the
two-shot in @(img1).

Subject: {{PROTAGONIST_FRAGMENT}} on the right and {{SUPPORTING_CHARACTER_FRAGMENT}}
on the left, both seated at a wooden cafe table holding hand-thrown ceramic
teacups.

Action (0-3s): Margaret tilts her head a touch, sculpted clay mouth opening
to speak — her painted lips form clear shapes (rough lip sync, not exact):
"{{MARGARET_LINE}}" — her sculpted eyebrows raise on emphasized words.
(3-{{MID}}s): Diane's sculpted eyes glance down at her teacup, expression
softly self-conscious, mouth closing. ({{MID}}-{{END}}s): Diane lifts her
teacup partway to her mouth, hesitates, then sets it back down. Slight
steam rises from both cups throughout.

Camera: Locked medium two-shot, very subtle handheld breathing motion. No
zoom or pan.

Style: Stop-motion claymation film aesthetic, Aardman-style hand-sculpted
plasticine, matte clay surfaces, real knit-fabric clothing, warm tungsten
overhead light, shallow macro depth of field, soft cafe-bokeh background.

Narrator (warm, ongoing storytelling — under or between Margaret's line):
"{{NARRATOR_LINE}}"
Ambient: soft cafe room tone, faint clinking of cup against saucer, distant
muffled conversation.

Constraints: Both characters must remain visually unchanged from @(img1) —
same plasticine hair colors and carved strand grooves, same matte clay
skin, same knit garments with visible wool weave, same eye sockets. The
cafe set must remain unchanged. No live-action, no photorealistic skin
smoothing, no Pixar wet-eye sheen, no extra fingers on the teacups, no
morphing, no on-screen text, no subtitles, no captions.
```

---

## Beat 4 — animate the quiet despair

**Target duration:** 5–7s (slow, sparse motion; narrator carries it)

```
Stop-motion claymation film aesthetic, image-to-video animation of the
scene in @(img1).

Subject: {{PROTAGONIST_FRAGMENT}} standing alone in her dimly lit living
room in front of a full-length wood-framed standing mirror.

Action (0-2s): She slowly lifts her sculpted clay hand to her cheek, fingers
resting lightly against the skin. (2-{{MID}}s): Her sculpted eyes lower a
fraction, expression subdued. Very slow sculpted blink. ({{MID}}-{{END}}s):
She lets her hand fall slowly back to her side, gaze still on her own
reflection. The mirror reflection mirrors her motion exactly.

Camera: Locked medium-wide shot, very subtle handheld macro breathing
motion. No zoom or pan.

Style: Stop-motion claymation film aesthetic, hand-sculpted plasticine,
matte clay, soft dim tungsten light from a single side lamp casting long
sculpted shadows.

Narrator (gentle, slightly reflective): "{{NARRATOR_LINE}}"
Ambient: very soft room tone, the faintest distant clock tick.

Constraints: The protagonist must remain visually unchanged from @(img1) —
same plasticine hair strands, same matte clay skin with thumbprint
impressions, same cream knit cardigan with wool weave. The dim living room
set must remain unchanged. The mirror reflection must match the
protagonist's pose accurately throughout. No live-action, no photorealistic
smoothing, no Pixar sheen, no morphing, no on-screen text, no subtitles,
no captions.
```

---

## Beat 5 — animate the clay infographic

**Target duration:** 8–10s (chart "reveal" with a small animated indicator)

```
Stop-motion claymation film aesthetic, image-to-video animation of the
hand-sculpted chart in @(img1).

Subject: A line graph sculpted entirely from clay and plasticine on a
hand-carved wooden frame, mounted on a cream-painted clay wall. The chart
shows "CALCIUM IN SKIN" with HIGH→LOW axis and a sculpted line dropping
sharply at the menopause label.

Action (0-2s): The chart sits still, soft tungsten light gently shifting
across its surface as if a curtain moved nearby. (2-{{MID}}s): A small
sculpted clay arrow indicator slowly traces along the line graph from left
to right, moving in measured even motion, drawing the viewer's eye to the
drop. ({{MID}}-{{END}}s): The arrow comes to rest at the bottom-right end
of the line. The MENOPAUSE label tag visibly settles into place with a
small final motion.

Camera: Locked head-on shot, very subtle handheld macro breathing motion.
Slight slow zoom-in (5% over the full duration) toward the drop in the
line.

Style: Stop-motion claymation film aesthetic, hand-sculpted plasticine
letters and graph elements, hand-carved wooden frame, matte cream-painted
clay wall background, soft tungsten light from camera-left.

Narrator (informative, calm): "{{NARRATOR_LINE}}"
Ambient: a quiet, low ambient hum — the silence of a "research" beat.

Constraints: The chart and frame must remain visually unchanged from
@(img1) — same chunky sculpted letters with slight asymmetry, same
plasticine line ribbon, same hand-carved frame. No live-action, no
digital-text overlay, no smooth animated graphics, no Pixar render, no
morphing, no extra labels, no on-screen text beyond what is already
sculpted into the still.
```

---

## Beat 6 — animate the discovery

**Target duration:** 6–8s (hand reaches, picks up product)

```
Stop-motion claymation film aesthetic, image-to-video animation of the
scene in @(img1).

Subject: A small dusty-purple cylindrical bottle labeled "{{PRODUCT_LABEL}}"
in hand-painted cream lettering, rendered as a clay prop, sitting on a
wooden kitchen table. {{PROTAGONIST_FRAGMENT}}'s sculpted clay hand enters
frame from camera-right.

Action (0-2s): Her sculpted fingers move slowly toward the bottle, hovering
briefly above it. (2-{{MID}}s): Her hand gently picks up the bottle,
sculpted fingers curling around it. The bottle lifts from the table.
({{MID}}-{{END}}s): She slowly rotates the bottle in her hand, the
hand-painted label turning to face the camera more cleanly. The light
catches the matte paint.

Camera: Locked medium shot, very subtle handheld macro breathing motion.
Slight slow dolly-in (3% over duration) toward the bottle.

Style: Stop-motion claymation film aesthetic, hand-sculpted plasticine
hand, matte clay-painted bottle prop, wooden table with visible grain, warm
tungsten light from a window on camera-left catching the label.

Narrator (curious, hopeful): "{{NARRATOR_LINE}}"
Ambient: soft kitchen room tone, faint kettle whistle in the distance.

Constraints: The product bottle must remain visually unchanged from
@(img1) — same dusty-purple paint with subtle brush texture, same
hand-painted label text legible and readable, same matte finish. The
protagonist's hand must remain visually unchanged — same matte clay
texture, sculpted knuckle creases, slight asymmetry. No live-action, no
photorealistic product render, no smooth digital plastic look, no warped
or shifting label text, no extra fingers, no morphing, no on-screen text,
no subtitles, no captions.
```

---

## Beat 7 — animate the transformation

**Target duration:** 10–12s (apply product + subtle reveal)

```
Stop-motion claymation film aesthetic, image-to-video animation of the
scene in @(img1).

Subject: {{PROTAGONIST_FRAGMENT}} in her bathroom, mirror visible behind
her, holding the "{{PRODUCT_LABEL}}" bottle.

Action (0-3s): She uncaps the bottle, takes a small amount of cream onto
her sculpted clay fingertip, slow deliberate motion. (3-{{MID}}s): She
gently applies the cream to her upper lip with measured strokes, her
sculpted eyes watching her own reflection in the mirror. ({{MID}}-{{END}}s):
She lowers her hand, looks at her reflection — her expression slowly warms
into a small pleased smile. The carved lines above her lip are visibly
slightly smoother than the start of the clip, while everything else about
her identity remains exactly the same.

Camera: Locked medium close-up, very subtle handheld macro breathing
motion. Slight slow dolly-in (3% over duration) on her face for the final
beat.

Style: Stop-motion claymation film aesthetic, hand-sculpted plasticine,
matte clay surfaces, warm tungsten light slightly brighter and warmer
than earlier beats to signal positive change.

Narrator (encouraging, warm): "{{NARRATOR_LINE}}"
Ambient: soft bathroom room tone, the gentle sound of a small cap
unscrewing.

Constraints: The protagonist must remain visually unchanged from @(img1) —
same terracotta plasticine hair with carved strand grooves, same matte
clay skin with thumbprint impressions across cheeks and forehead, same
cream knit cardigan with visible wool weave, same sculpted eye sockets.
The bottle prop must remain visually identical to Beat 6. Only the specific
upper-lip area may appear subtly smoother by the end — no other part of
the face changes. No live-action, no photorealistic skin smoothing across
the whole face, no Pixar render, no morphing, no on-screen text, no
subtitles, no captions.
```

---

## Beat 8 — animate the resolution + CTA

**Target duration:** 6–8s (smile, product hold, hold for caption)

```
Stop-motion claymation film aesthetic, image-to-video animation of the
character in @(img1).

Subject: {{PROTAGONIST_FRAGMENT}} in {{PRIMARY_SETTING_FRAGMENT}}, holding
the "{{PRODUCT_LABEL}}" bottle at chest height, facing camera.

Action (0-2s): She gives a small warm gentle smile, sculpted laugh lines
working with the smile. Her sculpted eyes meet the camera, brightening
softly. (2-{{MID}}s): She raises the bottle a touch closer to camera, her
hand turning slightly so the hand-painted label reads cleanly. ({{MID}}-{{END}}s):
Her smile widens into a small satisfied grin. She holds the pose, still
and warm, ready for a caption to land on the lower third of frame.

Camera: Locked medium shot, very subtle handheld macro breathing motion.
No zoom or pan.

Style: Stop-motion claymation film aesthetic, Aardman-style hand-sculpted
plasticine, matte clay surfaces, real knit-fabric cardigan, warm tungsten
light from camera-left with a soft rim from camera-right catching her hair.

Narrator (warm, inviting): "{{NARRATOR_LINE}}"
Ambient: warm kitchen room tone, faint birdsong outside.

Constraints: The protagonist must remain visually identical to Beat 7 —
same plasticine hair, same matte clay skin, same cream knit cardigan with
wool weave, same eye sockets. The bottle prop must remain visually
identical to Beat 6 and Beat 7. The lower third of frame must remain
visually clean and uncluttered for a post-production caption overlay. No
live-action, no photorealistic smoothing, no Pixar sheen, no morphing,
no extra fingers, no on-screen text, no subtitles, no captions.
```

---

## Cross-clip continuity rules

1. **Each clip's `image_input[0]`** is the approved still for that beat. Don't chain by using an animated end-frame as the next beat's anchor — drift compounds.
2. **Lift the SUBJECT LOCK fragments verbatim** into every beat. Don't paraphrase the protagonist description.
3. **Keep the STYLE block consistent** across all beats: use "stop-motion claymation film aesthetic" everywhere; never `cinematic`, never `Pixar`, never `3D rendered`.
4. **Beat ordering for parallelism:** Beats 1, 5 can fire in parallel. Beats 2, 3, 4, 6, 7, 8 fire in parallel once their stills are all approved. KIE allows ~100 concurrent jobs.
5. **Log each call** to `logs/<api>-api.jsonl` with `model`, `duration`, `resolution`, and `costTime`.

## Per-clip QA (claymation-specific)

For each Seedance result, watch the full clip and verify:

- [ ] **Clay texture preserved end-to-end** — the smoothing tendency of video models is the #1 risk. Fingerprint impressions and tool marks should remain visible in close-ups.
- [ ] **Knit fabric stays as woven wool**, not painted-on stripes
- [ ] **Matte eyes** — no Pixar wet-eye sheen developing mid-clip
- [ ] **Character identity holds** from input still to last frame — same face proportions, same hair color and strand grooves, same outfit
- [ ] **Product label paint stays hand-applied looking** — no digital crispness leaking in
- [ ] **Subtle improvement on Beat 7 is localized** (only the upper-lip area, not the whole face)
- [ ] **No burned-in text or subtitles** appeared
- [ ] **Mirror reflections move correctly** on Beats 2, 4, 7
- [ ] **Two-shot lip sync on Beat 3** is plausible (rough match is fine for Seedance)

If clay texture flattens or identity drifts, regenerate with a tightened MATERIAL DETAIL block and an explicit "preserve all clay texture from @(img1)" constraint. 2-retry cap per beat.

## Stitching the final ad

After all 8 beats are approved:

```bash
# In the session outputs folder:
cat > list.txt <<EOF
file 'beat1.mp4'
file 'beat2.mp4'
file 'beat3.mp4'
file 'beat4.mp4'
file 'beat5.mp4'
file 'beat6.mp4'
file 'beat7.mp4'
file 'beat8.mp4'
EOF

# If all clips share codec/resolution:
ffmpeg -f concat -safe 0 -i list.txt -c copy ad_smooth.mp4

# If codecs differ (re-encode):
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k -movflags +faststart ad_smooth.mp4

# OPTIONAL stop-motion judder pass:
ffmpeg -i ad_smooth.mp4 -filter:v "fps=12,fps=24" -c:a copy ad_judder.mp4
```

Then burn captions (see [guide.md → Captioning](guide.md#captioning)).

## Cost notes

- Seedance 2 wall-clock: ~3–4 min per clip @ 720p
- 8-beat ad = 8× Seedance calls (most can run in parallel) + retries
- Image 2 storyboard: 8× Image 2 calls (sequential for identity continuity) + retries
- Worst case with full 2-retry cap: 24 image + 24 video calls

Always present total credit cost and wait for explicit user confirmation before firing.
