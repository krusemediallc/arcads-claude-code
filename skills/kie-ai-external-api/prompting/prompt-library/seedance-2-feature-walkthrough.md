# Feature walkthrough — Seedance 2.0

**Use when:** You need a product showcase video where the person is actively wearing or using the product and walks the viewer through its features one by one, physically demonstrating each one. The vibe is enthusiastic, informative, and fast-paced — like an influencer who genuinely loves a product and is speedrunning every reason why.

**Model guide:** Read [seedance-2.md](seedance-2.md) first for platform rules, API parameters, and the adaptation checklist.

## What defines this style

This is NOT a review. There's no skepticism arc, no "I was surprised," no before-and-after. The person loves the product from the first frame and the entire video is a high-energy feature dump — each beat isolates one specific feature and physically demonstrates it on camera.

1. **Show, don't tell.** Every feature claim is backed by a physical action. "Hidden pockets" means she's reaching into the pocket on camera. "Stretchy waistband" means she's pulling the elastic. The person never just *talks about* a feature — they *prove it* with their hands.

2. **Density without overwhelm.** The person talks fast and covers a lot of ground, but each beat is cleanly separated by a jump cut. Within a 15-second clip, this style covers 1-2 distinct features. For products with many features, generate multiple 15-second clips that each tackle a different slice.

3. **First-person embodiment.** The person IS the product demo. They're wearing it, using it, living in it while they talk. The camera is close, the framing is personal.

## The structure

```
 1. FORMAT HEADER         — duration, content type, device, lighting, angle
 2. PERSON + PRODUCT      — appearance AND the product they're wearing/using (inseparable)
 3. SETTING               — simple background that doesn't compete with the product
 4. FEATURE BEATS         — one feature per beat, each with dialogue + physical demo
 5. GRAPHIC OVERLAYS      — text captions, info cards, color/size callouts
 6. TONE & PACING         — energy level, speech rhythm, relationship to viewer
 7. TECHNICAL QUALITY     — camera, lighting, audio characteristics
```

---

## Layer-by-layer formula

### Layer 1: Format header

**Pattern:**
```
15 seconds UGC style {{CONTENT_TYPE}} video, filmed on smartphone,
{{LIGHTING_SOURCE}}, {{CAMERA_ANGLE}}.
```

| Variable | Options | Notes |
|----------|---------|-------|
| `CONTENT_TYPE` | product showcase, feature walkthrough, try-on review, gear breakdown | Match the product category |
| `LIGHTING_SOURCE` | natural living room light, bright overhead apartment light, daylight from large windows, bedroom lamp light | Indoor residential — never studio |
| `CAMERA_ANGLE` | casual handheld selfie angle, phone propped at chest height, phone in one hand slightly below eye level | Always front-facing, always personal |

**15-second constraint:** A natural speaker covers 2-3 short sentences in 15 seconds. This style is fast-paced, so you can push to 3-4 short punchy lines, but that's the ceiling. Structure each clip around **one hook + 1-2 feature demos + a kicker line.**

**Multi-clip strategy:** If the product has 4+ features, split across 2-3 separate 15-second prompts:

| Clip | Beat 1 (Hook) | Beat 2 (Demo) | Beat 3 (Kicker) |
|------|---------------|---------------|-----------------|
| **Clip A: Hero** | "If I could only wear one thing..." | Demos the #1 standout feature | Quick reaction — "I'm obsessed" |
| **Clip B: Features** | "Let me show you why this is different" | Demos 1-2 secondary features | Use case — "perfect for travel" |
| **Clip C: Fit + CTA** | "The fit on this is unreal" | Turn-around, pulls at fabric, shows sizing | Urgency — "go run, sizes selling out" |

---

### Layer 2: Person + product (combined)

The person and product are inseparable — they're wearing/using it from the first frame.

**Pattern:**
```
A {{AGE_RANGE}} {{GENDER}} with {{HAIR}}, {{SKIN_DETAILS}},
wearing the @(img1) ({{PRODUCT_DESCRIPTION}}) — {{FIT_DETAILS}}.
```

| Variable | How to fill | Key principle |
|----------|-------------|---------------|
| `AGE_RANGE` | young woman, woman in her late 20s, guy in his mid-20s | Natural language, not exact ages |
| `HAIR` | long dark hair with soft waves, short curly hair, straight blonde hair in a ponytail | Casual styling |
| `SKIN_DETAILS` | natural skin with visible texture, warm complexion, light makeup with natural finish | 1-2 reality cues, slightly more polished than raw UGC |
| `PRODUCT_DESCRIPTION` | full product name + key visual details: color, pattern, material | Visually recognizable |
| `FIT_DETAILS` | how it sits on their body — relaxed, oversized, fitted, cropped | Sizing reference if relevant |

**Skin detail bank** (pick 1-2 — lighter touch than raw UGC):
- `natural skin with visible texture and warm undertones`
- `light makeup, natural-looking foundation`
- `natural complexion, slight shine on forehead`
- `clean skin with a few expression lines when smiling`

---

### Layer 3: Setting

Simple and residential. Says "this is her real home" but doesn't steal attention.

**Pattern:**
```
standing in {{SPACE}} — {{DETAIL_1}}, {{DETAIL_2}}, {{ATMOSPHERE}}.
The background is slightly out of focus, keeping attention on {{PRONOUN}} and the product.
```

| Setting | Background details | Atmosphere |
|---------|-------------------|------------|
| **Living room** | couch visible behind her, neutral walls | bright, open, modern |
| **Bedroom** | bed in background, pillows, nightstand lamp | cozy, personal |
| **Hallway / entry** | door frame, coat hooks, shoes by the door | casual, on-the-go |
| **Kitchen** | counter behind her, cabinets, morning light | warm, everyday |

---

### Layer 4: Feature beats (the engine)

Each beat follows a strict formula: **one feature = one physical demonstration + one dialogue line.**

**Beat pattern:**
```
{{TRANSITION}} — {{FRAMING_CHANGE}}, {{PRONOUN}} {{PHYSICAL_DEMO}}: "{{DIALOGUE}}"
```

**15-second beat structure (3 beats):**

| Beat # | Purpose | What happens | Dialogue | Time budget |
|--------|---------|-------------|----------|-------------|
| 1 | **Hook** | Bold claim or excited statement, gestures to product | 1 punchy sentence | ~4 seconds |
| 2 | **Feature demo** | Physically demonstrates 1-2 features with hands | 1-2 short sentences | ~7 seconds |
| 3 | **Kicker** | Quick reaction, verdict, or CTA | 1 short line | ~4 seconds |

**The silent beat option:** One of the three beats can be a SILENT physical demo (no dialogue, just action). This creates a breath in the dense dialogue. If used, put it at beat 2.

**Physical demonstration bank:**

| Feature type | Physical demo |
|-------------|---------------|
| Hidden pockets | reaches into pocket, pulls hand out showing depth |
| Stretch/comfort | pulls at waistband or fabric, shows elastic snap-back |
| Hood/built-in feature | pulls hood up, shows how feature works |
| Softness/material | runs hand across fabric, bunches it to show texture |
| Fit | turns around, shows the back, pulls at sides |
| Zipper/closure | zips up/down, shows how it fastens |
| Weight/structure | lifts the product slightly, lets it drop to show weight |

**Dialogue rules:**
- Confident, not questioning. She KNOWS this product is good.
- Descriptive and specific — names materials, features, design choices
- Fast-paced — sentences are short and punchy
- Uses "this" and "these" a lot (pointing at what she's wearing)
- Last beat always has urgency language ("go run to," "selling out," "link in bio")

---

### Layer 5: Graphic overlays

| Overlay type | When it appears | Example |
|-------------|-----------------|---------|
| **Keyword caption** | Bottom of frame, during each beat | "HIDDEN POCKETS", "STRETCHY AND COMFORTABLE" |
| **Size reference** | During fit/turn-around beat | "5'4" / Size: M" |
| **Color swatches** | During CTA/closer beat | Product color options shown as swatches |

Not every beat needs an overlay, but the hook and CTA beats almost always have one.

---

### Layer 6: Tone & pacing

**Pattern:**
```
Throughout the video, the tone is {{EMOTION_1}}, {{EMOTION_2}},
{{EMOTION_3}} — {{BEHAVIOR_DESCRIPTION}}. {{PACING_CUE}}.
```

**Tone bank:**

| Vibe | Emotion words | Behavior |
|------|---------------|----------|
| **Enthusiastic expert** | confident, excited, knowledgeable | talks fast but clearly, moves with purpose |
| **Hype girl** | bubbly, high-energy, contagious | smiles constantly, gestures big |
| **Cool recommender** | assured, casual-expert, effortless | knows the product inside out |

**Pacing:** This style moves FAST. The rhythm is:
`Speak (1-2 sentences) → demonstrate (1-2 seconds of action) → cut → repeat`

---

### Layer 7: Technical quality

**Pattern:**
```
The lighting is {{LIGHT_TYPE}} — {{LIGHT_QUALITY}}.
The image is {{CAMERA_QUALITY}} — {{CAMERA_DETAILS}}.
The sound is {{AUDIO_SOURCE}} — {{AUDIO_DETAILS}}.
```

**Lighting:** Bright, even, residential. Natural daylight from windows is ideal.

**Camera:** Phone quality but steady and well-framed. Slightly more polished than raw UGC.

**Audio:** Direct phone mic, clear voice, room is quiet.

---

## Complete template

```
15 seconds UGC style {{CONTENT_TYPE}} video, filmed on smartphone,
{{LIGHTING_SOURCE}}, {{CAMERA_ANGLE}}. A {{AGE_RANGE}} {{GENDER}} with
{{HAIR}}, {{SKIN_DETAILS}}, wearing the @(img1) ({{PRODUCT_DESCRIPTION}})
— {{FIT_DETAILS}}. Standing in {{SPACE}} — {{BG_DETAIL_1}},
{{BG_DETAIL_2}}, {{ATMOSPHERE}}.

The video opens with {{PRONOUN}} {{HOOK_ACTION}}: "{{HOOK_LINE}}"

Jump cut — {{BEAT_2_FRAMING}}, {{BEAT_2_DEMO}}: "{{BEAT_2_DIALOGUE}}"

Jump cut — {{BEAT_3_FRAMING}}, {{BEAT_3_ACTION}}: "{{KICKER_LINE}}"
{{CLOSING_ACTION}}.

Throughout the video, the tone is {{TONE_EMOTIONS}} —
{{TONE_BEHAVIOR}}. {{PACING_CUE}}.

The lighting is {{LIGHT_TYPE}} — {{LIGHT_QUALITY}}. The image is
{{CAMERA_QUALITY}} — {{CAMERA_DETAILS}}. The sound is
{{AUDIO_SOURCE}} — {{AUDIO_DETAILS}}.
```

---

## Example: Backpack (2-clip series)

### Clip A — Hook + hero feature

```
15 seconds UGC style product showcase video, filmed on smartphone,
bright natural daylight from large windows, casual handheld selfie
angle. A guy in his late 20s with short dark hair and a trimmed
beard, natural skin with visible texture and slight tan, wearing the
@(img1) (Nomad Tech Backpack — matte black, 30L, roll-top closure
with magnetic buckles) — the bag is on his back, straps adjusted.
Standing in his apartment entryway — shoes by the door, keys on a
hook, bright and minimal.

The video opens with him gesturing to the backpack over his shoulder,
smiling at camera: "If I could only use one bag for everything —
work, gym, travel — this is the one."

Jump cut — he swings the bag around to his front, unrolls the top,
shows the magnetic buckle snapping shut: "Roll-top expands when you
need space, locks down with these magnets."

Jump cut — he holds the bag at chest height, taps the side, nods:
"Absolute game changer." He laughs, video cuts.

Throughout the video, the tone is confident, knowledgeable, genuinely
impressed — he presents each feature like an obvious advantage,
speaks quickly but clearly, demonstrates without fumbling. Each beat
is quick but not rushed.

The lighting is bright natural daylight from the windows, filling the
entryway evenly. The image is natural phone quality, not color graded
but well-exposed, steady handheld with slight movement when he turns.
The sound is direct from phone mic — his voice is clear and close,
minimal room echo, no music underneath.
```

### Clip B — Secondary features + CTA

```
15 seconds UGC style feature walkthrough video, filmed on smartphone,
bright natural daylight from large windows, casual handheld selfie
angle. A guy in his late 20s with short dark hair and a trimmed
beard, natural skin with visible texture and slight tan, wearing the
@(img1) (Nomad Tech Backpack — matte black, 30L) — the bag is on
his back. Standing in his apartment entryway — shoes by the door,
keys on a hook, bright and minimal.

The video opens with him turning the bag to show the back panel,
unzipping it to reveal a padded laptop sleeve: "Separate laptop
compartment — fits a 16-inch, padded on all sides."

Jump cut — he runs his hand across the outside fabric, then flicks
water droplets off with his fingers: "Waterproof nylon. Got rained
on last week, everything inside was bone dry."

Jump cut — he puts the bag back on, adjusts the chest strap, looks
at camera: "Link's in bio — they sold out twice already, don't
sleep on it." He taps the strap and walks off frame.

Throughout the video, the tone is assured, casual-expert, effortless
— he knows the product inside out, presents features like obvious
facts, no hype, just confidence. Speaks at an upbeat pace with no
hesitation.

The lighting is bright natural daylight from the windows, filling the
entryway evenly. The image is natural phone quality, not color graded
but well-exposed, steady handheld with slight movement when he turns.
The sound is direct from phone mic — his voice is clear and close,
minimal room echo, no music underneath.
```

---

## Adaptation checklist

- [ ] **15 seconds** — every clip is a single Seedance 2.0 prompt
- [ ] **Max 3 beats per clip** — hook, feature demo, kicker
- [ ] **Max 2-3 spoken lines** — if more dialogue, split into another clip
- [ ] **Every feature beat has a physical demonstration** — no talking-only beats
- [ ] **Hook is a bold claim** — superlative, confident, no hedging
- [ ] **Person is wearing/using the product from frame 1** — no unboxing, no reveal
- [ ] **Framing changes every beat** — tighter, wider, close-up, turn-around
- [ ] **Setting is simple** — 2 background details max
- [ ] **Pacing cue included** — this style moves fast, specify that
- [ ] **Multi-clip series planned** — if product has 4+ features, split across 2-3 clips
- [ ] **Word count** — prompt between 100–260 words
- [ ] **@(img1)** — product image reference included
- [ ] **No forbidden words** — no "cinematic," "professional," "stunning," "8k," "studio," "perfect"
