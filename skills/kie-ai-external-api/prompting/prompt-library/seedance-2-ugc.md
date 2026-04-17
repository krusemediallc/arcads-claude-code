# UGC video prompt formula — Seedance 2.0

**Use when:** You need to generate a UGC-style product review/testimonial video prompt for any person, any product, in any setting. The output should feel like a real person filmed a casual selfie video on their phone.

**Model guide:** Read [seedance-2.md](seedance-2.md) first for platform rules, API parameters, and the adaptation checklist.

## The anatomy of a UGC video prompt

Every effective UGC video prompt has **9 layers**, stacked in order. Skip a layer and the output falls apart.

```
 1. FORMAT HEADER       — duration, style, device, lighting, angle
 2. PERSON              — appearance, skin texture, clothing
 3. SETTING             — lived-in environment, specific clutter details
 4. PRODUCT INTRO       — how they hold/show the product to camera
 5. SCRIPT BEATS        — jump-cut scenes with dialogue + actions
 6. TONE DIRECTION      — personality, pacing, energy
 7. EDIT STYLE          — jump cuts, angles, take selection
 8. TECHNICAL FLAWS     — camera quality, audio, lighting imperfections
 9. VIBE STATEMENT      — one-sentence emotional anchor
```

---

## Layer-by-layer formula

### Layer 1: Format header

Sets the technical foundation. Always leads the prompt.

**Pattern:**
```
{{DURATION}} UGC style {{CONTENT_TYPE}} video, filmed on smartphone,
{{LIGHTING_SOURCE}}, {{CAMERA_ANGLE}}.
```

**Variables:**

| Variable | Options | Notes |
|----------|---------|-------|
| `DURATION` | 15 seconds, 10 seconds | 15s is the Seedance 2.0 maximum. Use 10s for punchier clips with less dialogue. |

**Duration guide — dialogue must fit the runtime at natural speaking pace:**

| Duration | Jump cuts | Dialogue guidance |
|----------|-----------|-------------------|
| **10s** | 2-3 cuts | Very tight — 1-2 spoken lines max plus one silent beat. Hook + punchline. |
| **15s** | 2-4 cuts | Dialogue is flexible but must be **speakable at a relaxed pace within 15 seconds** including natural pauses. Read your script out loud — if you have to rush to fit it in 15s, cut words. Mix spoken and silent beats. Short punchy lines > long explanations. |

**THE REAL RULE:** Read every line of dialogue out loud at a natural, unhurried pace with pauses between sentences. Time yourself. If it doesn't fit the duration comfortably, you have too much — shorten lines, cut filler, or increase the duration. Include at least one silent action beat (sipping, inspecting, reacting) per video regardless of duration.

| Variable | Options | Notes |
|----------|---------|-------|
| `CONTENT_TYPE` | skincare review, product unboxing, morning routine, haul, get-ready-with-me, first impression, honest review, tutorial, day-in-my-life | Match the creator's natural format |
| `LIGHTING_SOURCE` | natural bedroom window lighting, bathroom vanity mirror lighting, golden hour balcony light, overhead kitchen light, car dashboard light, ring light on desk (subtle) | Natural > artificial. Specify the source, not just "good lighting" |
| `CAMERA_ANGLE` | casual handheld selfie angle, phone propped on counter, mirror selfie angle, laptop webcam angle, phone in one hand walking | Describes HOW they're filming, not just the frame |

**Example:**
> 15 seconds UGC style skincare review video, filmed on smartphone, natural bedroom window lighting, casual handheld selfie angle.

---

### Layer 2: Person

Describe a specific, believable human — not a model. Imperfection is the point.

**Pattern:**
```
A {{AGE_RANGE}} {{GENDER}} with {{HAIR}}, {{SKIN_TEXTURE}},
wearing {{CLOTHING}},
```

**Variables:**

| Variable | How to fill | Key principle |
|----------|-------------|---------------|
| `AGE_RANGE` | young woman, man in his 30s, college-aged guy, woman in her late 20s | Use natural language, not exact ages |
| `HAIR` | brown hair pulled back, messy bun, short curly hair, blonde highlights in a claw clip | Casual styling, not salon-perfect |
| `SKIN_TEXTURE` | natural skin with visible texture, light freckles across nose, slight undereye circles, a few smile lines, subtle acne scarring near jawline | **CRITICAL** — always include 2-3 skin reality cues. Without them, AI defaults to airbrushed |
| `CLOTHING` | casual grey t-shirt, oversized college hoodie, tank top and shorts, worn-in flannel | Comfort clothes. Nothing styled or "outfit of the day" |

**Skin reality cue bank** (pick 2-3):
- `natural skin with visible texture`
- `visible pores across nose and cheeks`
- `slight unevenness in skin tone`
- `minor undereye shadows`
- `a hint of shine on forehead from natural oils`
- `slight pinkness on cheeks and nose`
- `a few expression lines when smiling`
- `light freckles` (if appropriate for the character)

**Do NOT use:** acne, pimples, breakouts, blemishes, rosacea — real ≠ dermatological.

---

### Layer 3: Setting

The background sells authenticity. Describe 3-4 specific objects that make it feel lived-in.

**Pattern:**
```
in {{THEIR_SPACE}} — {{DETAIL_1}}, {{DETAIL_2}}, {{DETAIL_3}},
{{ATMOSPHERE_WORD}} and real.
```

**Setting bank:**

| Setting | Specific clutter details | Atmosphere |
|---------|------------------------|------------|
| **Bedroom** | books on shelves, plants on windowsill, clothes on a chair, fairy lights on headboard | cozy, lived-in |
| **Bathroom** | towels hanging, skincare bottles on counter, toothbrush in holder, foggy mirror edge | steamy, morning |
| **Kitchen** | coffee mug on counter, cutting board, fruit bowl, morning light through blinds | warm, morning routine |
| **Living room** | throw blanket on couch, remote on cushion, candle on coffee table, shoes by the door | relaxed, casual |
| **Car** | coffee in cupholder, sunglasses on dash, aux cord hanging, parking lot through windshield | on-the-go |
| **Desk/office** | laptop half-open, sticky notes, water bottle, headphones draped over monitor | work-from-home |
| **Outdoor/balcony** | railing in background, plants in pots, city/trees visible, wind moving hair | golden hour, fresh |

---

### Layer 4: Product introduction

How the product physically enters the frame. This is the bridge from person to pitch.

**Pattern:**
```
{{PRONOUN}} holds the @(img1) ({{PRODUCT_DESCRIPTION}}) {{HOW}}.
```

**Product intro styles:**

| Style | When to use | Example |
|-------|-------------|---------|
| **Show to camera** | Review, first impression | "holds the bottle up to the camera" |
| **Already using** | Tutorial, routine | "is mid-application, product already on her skin" |
| **Unboxing reveal** | Haul, unboxing | "pulls it out of the box, eyes lighting up" |
| **In-hand casual** | Day-in-my-life | "has it sitting on her lap, picks it up" |
| **Before/after** | Results-focused | "holds it next to her face, turning to show her skin" |

---

### Layer 5: Script beats (the heart of the prompt)

Each beat is one jump cut. Structure: **setup → demonstration → proof → verdict.**

**IMPORTANT:** Not every beat needs dialogue. Silent beats (inspecting product, sipping, reacting with facial expressions, reading the label) feel more authentic and prevent cramming too many words into the runtime. Every video should have at least one silent action beat. The number of spoken vs silent beats is flexible — optimize for what sounds natural when read aloud at a relaxed pace within the target duration.

**Pattern (per beat):**
```
{{TRANSITION}} — {{FRAMING_CHANGE}}, {{ACTION}}: "{{DIALOGUE}}"
// OR for silent beats:
{{TRANSITION}} — {{FRAMING_CHANGE}}, {{ACTION}}.
```

**Beat framework:**

| Beat # | Purpose | Framing | Example action |
|--------|---------|---------|----------------|
| 1 (Hook) | Grab attention | Looking into camera | Expressive opener, holds product up |
| 2 (Show) | Product detail | Closer to lens | Tilts/turns product, shows label/texture |
| 3 (Demo) | Proof of use | Extreme close-up | Applies product, shows consistency/texture |
| 4 (Result) | Evidence | Mirror/different angle | Points at skin/result, shows before/after |
| 5 (Verdict) | Final opinion | Back to original angle | Holds product up, delivers final line |

For 10s, pick 2-3 of these. For 15s, use 3-4. Any beat can be spoken or silent — just make sure the total dialogue fits the runtime when read aloud naturally.

**Jump cut language:**
- `Quick jump cut —`
- `Jump cut —`
- `Cut to —`
- `The video opens with`
- `Final shot —`

**Framing changes** (vary every beat):
- `she's now showing the bottle closer to the lens`
- `extreme close-up of her pressing the dropper`
- `phone propped up, you can see her reflection`
- `she leans into the camera`
- `she holds the bottle up one final time`

**Dialogue rules:**
- Written in quotes, casual spoken language
- Use filler words: "okay so," "literally," "I'm not even," "like," "you guys"
- End mid-thought or with a laugh, not a polished sign-off
- Each line should feel like a different take stitched together

---

### Layer 6: Tone direction

One paragraph that tells the model the emotional texture of the entire video.

**Pattern:**
```
Throughout the video, the tone is {{EMOTION_1}}, {{EMOTION_2}},
{{EMOTION_3}} — {{BEHAVIOR_DESCRIPTION}}.
```

**Pacing rule (ALWAYS include):** Every tone direction paragraph MUST include an explicit pacing/speed cue. AI video generators default to unnaturally fast speech. Counter this by specifying pauses, breath beats, and natural human rhythm. Use phrases like:
- `pauses between thoughts as if collecting the next word`
- `leaves a beat of silence after each sentence before continuing`
- `speaks at a relaxed, unhurried pace — no rushing`
- `takes natural breaths between sentences, never rushing to the next line`
- `lets moments breathe — a sip, a glance down, a pause before speaking again`

**Tone bank:**

| Vibe | Emotion words | Behavior description |
|------|---------------|---------------------|
| **Excited fan** | genuine, excited, breathless | she talks with energy but pauses between thoughts, uses natural breaths, laughs at herself |
| **Chill recommender** | relaxed, honest, conversational | she speaks slowly, leaves beats of silence between lines, makes eye contact, shrugs casually |
| **Skeptic converted** | surprised, impressed, almost reluctant | she raises her eyebrows, pauses mid-sentence as if reconsidering, sounds like she can't believe it |
| **Best friend sharing** | warm, conspiratorial, intimate | she lowers her voice, leans in, takes her time — talks like it's a secret worth savoring |
| **Morning routine casual** | sleepy, soft, unhurried | she yawns, moves slowly, long pauses between sentences, talks between sips of coffee |

---

### Layer 7: Edit style

Describes how the jump cuts and takes work together.

**Pattern:**
```
Each jump cut is {{ANGLE_VARIATION}}. {{EDIT_FEEL}}.
```

**Standard UGC edit style** (use this as default):
> Each jump cut is slightly closer or at a different angle, as if she filmed multiple takes and edited the best bits together.

**Variations:**
- `Quick cuts between tight close-ups and medium shots, TikTok editing rhythm`
- `Long unbroken take with one or two hard cuts where she paused to think`
- `Get-ready-with-me style — time skips with each step of the routine`

---

### Layer 8: Technical flaws

This is what makes it feel real. Include ALL of these — every single one matters.

**Standard technical flaw block** (copy this every time, adjust to setting):
```
The lighting is {{LIGHT_TYPE}} — {{LIGHT_FLAW}}.
The image is slightly imperfect — {{CAMERA_FLAW_1}}, {{CAMERA_FLAW_2}}, {{CAMERA_FLAW_3}}.
The sound is {{AUDIO_SOURCE}} — {{AUDIO_DETAILS}}.
```

**Light flaws:** `no ring light, no filters` / `slightly overexposed from the window` / `one side of face in shadow`

**Camera flaws (pick 2-3):**
- `natural phone quality, not color graded`
- `slight motion blur on fast movements`
- `soft focus, nothing is tack sharp`
- `visible grain in darker areas`
- `auto white balance shift between cuts`

**Audio source options:**
- `direct from the phone mic` — her natural voice, room ambience, no music underneath
- `front camera mic` — slightly tinny, room echo, background hum
- `car interior acoustics` — muffled, road noise underneath

---

### Layer 9: Vibe statement

One sentence that anchors the entire emotional feel. This is the "north star" for the model.

**Pattern:**
```
The overall feel is {{ADJECTIVE_1}}, {{ADJECTIVE_2}}, {{ADJECTIVE_3}} —
{{RELATABLE_METAPHOR}}.
```

**Examples:**
- `trustworthy, relatable, real — a friend telling you about something she genuinely likes.`
- `chaotic, genuine, fun — like a voice memo she sent to her group chat.`
- `calm, honest, intimate — like overhearing someone's morning routine.`
- `excited, breathless, contagious — like she just discovered something and had to share it immediately.`

---

## Complete template

Copy this and fill in the `{{VARIABLES}}`:

```
{{DURATION}} UGC style {{CONTENT_TYPE}} video, filmed on smartphone,
{{LIGHTING_SOURCE}}, {{CAMERA_ANGLE}}. A {{AGE_RANGE}} {{GENDER}} with
{{HAIR}}, {{SKIN_TEXTURE}}, wearing {{CLOTHING}}, in {{THEIR_SPACE}} —
{{CLUTTER_DETAIL_1}}, {{CLUTTER_DETAIL_2}}, {{CLUTTER_DETAIL_3}},
{{ATMOSPHERE}} and real. {{PRONOUN}} holds the @(img1)
({{PRODUCT_DESCRIPTION}}) {{PRODUCT_INTRO_STYLE}}.

The video opens with {{PRONOUN}} {{HOOK_ACTION}}: "{{HOOK_LINE}}"

Quick jump cut — {{BEAT_2_FRAMING}}, {{BEAT_2_ACTION}}:
"{{BEAT_2_DIALOGUE}}"

Jump cut — {{BEAT_3_FRAMING}}, {{BEAT_3_ACTION}}.

Jump cut — {{BEAT_4_FRAMING}}, {{BEAT_4_ACTION}}:
"{{BEAT_4_DIALOGUE}}" {{CLOSING_ACTION}}.

Throughout the video, the tone is {{TONE_EMOTIONS}} —
{{TONE_BEHAVIOR}}. The pacing is natural and unhurried — {{PACING_CUE}}.
Each jump cut is {{ANGLE_VARIATION}}. {{EDIT_FEEL}}.

The lighting is {{LIGHT_TYPE}} — {{LIGHT_FLAW}}. The image is
slightly imperfect — {{CAMERA_FLAWS}}. The sound is
{{AUDIO_SOURCE}} — {{AUDIO_DETAILS}}.

The overall feel is {{VIBE_ADJECTIVES}} — {{RELATABLE_METAPHOR}}.
```

---

## Quick-start examples

### Example A: Skincare serum (bedroom, excited fan)

```
15 seconds UGC style skincare review video, filmed on smartphone,
natural bedroom window lighting, casual handheld selfie angle. A young
woman with brown hair pulled back, natural skin with visible texture,
wearing a casual grey t-shirt, in her cozy bedroom — books on shelves,
plants on the windowsill, clothes on a chair, lived-in and real. She
holds the @(img1) (LUNA Aurora Serum bottle) up to the camera.

The video opens with her looking into the camera, excited expression:
"Okay, so I've been using this for two weeks, and I need to talk about
it."

Quick jump cut — she's now showing the bottle closer to the lens,
tilting it so the holographic text catches the light from the window:
"The texture is insane, it's like water but silky?"

Jump cut — extreme close-up of her pressing the dropper, the serum
dropping onto her fingertips, she rubs it between her fingers, showing
the consistency.

Jump cut — she leans into the camera, pointing at her cheek with a
genuine smile: "Look, I actually have a glow right now, and I'm
literally wearing nothing." She laughs, the video cuts.

Throughout the video, the tone is genuine, unscripted-feeling, warm —
she talks fast, uses natural pauses, laughs at herself. Each jump cut
is slightly closer or at a different angle, as if she filmed multiple
takes and edited the best bits together.

The lighting is soft natural daylight, no ring light, no filters. The
image is slightly imperfect — natural phone quality, not color graded,
authentic. The sound is direct from the phone mic — room ambience, her
natural voice, no music underneath.

The overall feel is trustworthy, relatable, real — a friend telling you
about something she genuinely likes.
```

### Example B: Protein powder (kitchen, chill recommender)

```
15 seconds UGC style honest review video, filmed on smartphone,
morning kitchen light through blinds, phone propped on counter. A guy
in his late 20s with short dark hair and stubble, natural skin with
visible pores and slight undereye shadows, wearing a worn-in black
t-shirt, in his small apartment kitchen — coffee mug on counter,
cutting board with banana peel, blender in background, morning mess
and real. He has the @(img1) (GAINZ Chocolate Whey tub) sitting next
to the blender.

The video opens with him looking at camera, half-smile: "Alright so
everyone keeps asking me about my protein powder, so here it is."

Quick jump cut — he picks up the tub, turns it to show the label:
"Chocolate whey, nothing fancy, but the macros are actually insane."

Jump cut — he scoops powder into the blender, close-up of the scoop
coming out clean.

Jump cut — he holds the tub up, taps the label: "Link's in my bio,
you're welcome." He laughs and walks off frame.

Throughout the video, the tone is relaxed, honest, conversational —
he speaks slowly, makes steady eye contact, shrugs casually. Each
jump cut is slightly closer or at a different angle, morning light
shifting between takes.

The lighting is uneven kitchen light — bright from the window side,
shadow on the other, no overhead light on. The image is slightly
imperfect — natural phone quality, slight warm cast, not color graded.
The sound is front camera mic — slightly tinny, fridge hum in
background, his natural voice.

The overall feel is calm, honest, no-BS — a buddy telling you what
he actually uses, not selling you anything.
```

---

## Adaptation checklist

When building a new prompt, verify each layer:

- [ ] **Format header** — duration (max 15s), style, device, lighting source, camera angle all specified
- [ ] **Person** — described with natural imperfections, not a model casting call
- [ ] **Skin texture** — at least 2 reality cues included (pores, unevenness, shine, shadows)
- [ ] **Setting** — 3+ specific clutter objects, atmosphere word
- [ ] **Product intro** — clear physical description of product, how it enters the frame
- [ ] **Script beats** — beat count matches duration (10s = 2-3, 15s = 3-4), silent beats included
- [ ] **Dialogue** — fits the runtime at natural pace, uses filler words, ends naturally (laugh, trail off)
- [ ] **Tone direction** — 3 emotion words + behavior description
- [ ] **Pacing** — explicit pacing cues in tone direction, pauses/breaths between lines
- [ ] **Edit style** — how cuts relate to each other
- [ ] **Technical flaws** — lighting flaws, camera flaws, audio source all specified
- [ ] **Vibe statement** — one-sentence emotional metaphor to anchor the whole piece
- [ ] **Word count** — prompt is between 100–260 words (Seedance 2.0 sweet spot)
- [ ] **Motion specificity** — actions describe degree/direction, not just "moves"
- [ ] **Consistency anchors** — product/outfit described as unchanged across shots
- [ ] **No forbidden words** — no "cinematic," "professional," "stunning," "8k," "studio," "perfect"
