# Claymation storyboard — ChatGPT Image 2

**Generate the still-image storyboard before animating with Seedance 2.0.** Read [guide.md](guide.md) first for the 8-beat arc, cast sheet, and aesthetic anchors.

## Universal prompt structure

Each beat uses the same six-block structure. Paste them in this order:

```
[STYLE LOCK]            ← identical across all beats
[ASPECT + FRAMING]
[CHARACTER(S)]          ← protagonist alone, two-shot, or product/infographic
[SCENE / ACTION]
[MATERIAL DETAIL]       ← clay/fabric/wood specifics — critical for the look
[NEGATIVE]
```

### STYLE LOCK (paste verbatim into every beat)

```
Aardman-style stop-motion claymation aesthetic. Hand-sculpted plasticine
characters with visible fingerprint impressions and sculpting-tool marks on
clay surfaces, matte clay material with subtle micro-bumps, slightly
asymmetric facial features, painted-on or carefully sculpted eyebrows. Real
knit-fabric clothing with visible weave and stitch lines. Wooden and ceramic
miniature-set props with hand-painted finishes. Warm tungsten interior
lighting, shallow macro depth of field with soft photographic bokeh that
reinforces the miniature-set illusion. Subtle imperfection in every surface —
slightly uneven paint, irregular fabric weave, asymmetric forms.
```

### NEGATIVE (paste into every beat)

```
Not photorealistic, not live-action, not Pixar style, not 3D rendered, not
CGI, not anime, not 2D illustration, not smooth digital render, not glossy,
no ray-traced reflections, no subsurface scattering, no oversized Pixar-style
eyes with multiple highlights. No extra fingers, no merged features, no
warped product labels, no on-screen text unless explicitly requested.
```

### MATERIAL DETAIL (paste a relevant subset into every beat)

Adjust which lines apply to what's in frame:

```
- Skin: matte plasticine, visible thumbprint impressions on cheeks and forehead,
  small sculpting-knife creases at the corners of the eyes, slight asymmetry
  between left and right side of the face
- Hair: sculpted in distinct ribbon-strands of plasticine, individual strand
  grooves carved with a tool, slightly stiff and not flowing
- Eyes: small matte clay or painted-resin orbs set into sculpted sockets,
  single soft highlight, no wet shine
- Knitwear: real chunky wool yarn, individual stitches visible, slight wear
  at cuffs and hems
- Wood props: hand-painted matte finish, visible grain, small dents and
  scratches that suggest age
- Ceramic / pottery: hand-thrown irregular form, glaze pooling at the bottom
  edges, slight off-roundness
- Product packaging: rendered as a clay-shaded prop with hand-painted label,
  paint slightly uneven and matte
```

---

## Beat 1 — Setup (protagonist in their world)

**Goal:** Wide or medium shot establishing the protagonist in their primary domestic miniature set. Narrator introduces them by name.

**Formula:**

```
{STYLE LOCK}

Aspect ratio 9:16, {{WIDE_OR_MEDIUM}} shot of {{PROTAGONIST_FROM_CAST_SHEET}}
standing or sitting in {{PRIMARY_SETTING}}. {{POSTURE_AND_ACTION}}. Warm
morning tungsten light falls across the scene from {{LIGHT_SOURCE}},
casting soft shadows on the wooden floor. Background includes
{{BACKGROUND_PROPS}} in soft macro bokeh — the miniature-set illusion is
strong.

{MATERIAL DETAIL — skin, hair, knitwear, wood, ceramic}

{NEGATIVE}
```

**Worked example (Diane in kitchen):**

```
[STYLE LOCK]

Aspect ratio 9:16, medium-wide shot of Diane, a woman in her late 50s with
shoulder-length terracotta-brown wavy plasticine hair sculpted in distinct
ribbon-strands, deep laugh lines and hooded eyelids in matte sculpted clay,
warm brown eyes set into deep sockets. She wears a cream chunky knit
cardigan over a rust-red blouse, dark wool trousers, brown leather slippers.
She stands at her sunlit kitchen counter, pouring tea from a hand-thrown
ceramic kettle into a wide cup. Warm morning tungsten light falls from a
large window on camera-left, casting soft shadows on the wooden floor.
Background includes green-painted cabinets, a red gingham tablecloth, potted
herbs on the windowsill, all in soft macro bokeh.

[MATERIAL DETAIL — skin shows thumbprint impressions on cheeks; hair has
individual carved strand grooves; knit cardigan shows real wool weave with
slight wear at cuffs; wooden counter has visible grain and small dents;
ceramic kettle has slight off-round form with glaze pooling at the base.]

[NEGATIVE]
```

---

## Beat 2 — Inciting moment (close-up, protagonist notices the problem)

**Goal:** Tight close-up on the protagonist's face as they see the issue. Surprised or concerned expression.

**Formula:**

```
{STYLE LOCK}

Aspect ratio 9:16, tight close-up of {{PROTAGONIST_FROM_CAST_SHEET}}'s face
as she {{NOTICING_ACTION}}. Her expression is {{CONCERNED_EXPRESSION}} —
{{SPECIFIC_FACIAL_CUE}}. {{REFLECTION_OR_FOCAL_OBJECT}} is partially visible
in frame. Soft directional tungsten light wraps her face from
{{LIGHT_DIRECTION}}. Shallow depth of field, miniature-set bokeh behind her.

{MATERIAL DETAIL — emphasize skin texture, eye sockets, sculpted brow}

{NEGATIVE}
```

**Variable examples:**

| Slot | Examples |
|------|----------|
| `NOTICING_ACTION` | "leans toward a small wood-framed bathroom mirror, fingertip lifted to her upper lip" / "looks down at the bathroom scale at her feet" / "studies a clay-rendered chart on the wall" |
| `CONCERNED_EXPRESSION` | "softly furrowed brow, mouth slightly open" / "eyes widening with quiet alarm" / "lips pursed, sculpted eyebrows raised" |
| `SPECIFIC_FACIAL_CUE` | "small carved lines visible above her lip" / "a single sculpted crease deepens between her brows" |
| `REFLECTION_OR_FOCAL_OBJECT` | "her own reflection in the mirror, hair slightly different" / "the scale's clay-painted dial" |

**Worked example (Diane sees lines above lip):**

```
[STYLE LOCK]

Aspect ratio 9:16, tight close-up of Diane (terracotta plasticine hair, matte
clay skin with deep laugh lines, warm brown clay eyes) as she leans toward a
small wood-framed bathroom mirror, her fingertip lifted to her upper lip.
Her expression is softly furrowed, mouth slightly open in quiet alarm —
small carved lines are visible above her lip. Her own reflection in the
mirror shows the same face from a different angle, hair slightly different.
Soft directional tungsten light wraps her face from camera-right. Shallow
depth of field, bathroom-tile bokeh behind her.

[MATERIAL DETAIL — clay skin shows visible thumbprint impressions across
cheeks; eye sockets sculpted deep with single matte highlight; sculpted
brow furrow visible as a tool-carved crease; hair strands carved as ribbons.]

[NEGATIVE]
```

---

## Beat 3 — Social validation (two-shot)

**Goal:** Protagonist with a friend/spouse/coworker in the secondary setting. A small exchange or remark.

**Formula:**

```
{STYLE LOCK}

Aspect ratio 9:16, medium two-shot of {{PROTAGONIST_FROM_CAST_SHEET}} on
the {{LEFT_OR_RIGHT}} and {{SUPPORTING_CHARACTER_FROM_CAST_SHEET}} on the
opposite side, both seated at {{SECONDARY_SETTING_PROP}}. {{SHARED_ACTIVITY}}.
The supporting character is mid-remark — mouth slightly open, sculpted
eyebrows raised in curiosity, looking at the protagonist. The protagonist
{{REACTION}}. Background includes {{SECONDARY_SETTING_DETAIL}} in soft macro
bokeh. Warm tungsten light from above.

{MATERIAL DETAIL — both characters' skin/hair/knit; secondary setting props}

{NEGATIVE}
```

**Worked example (Diane and Margaret at cafe):**

```
[STYLE LOCK]

Aspect ratio 9:16, medium two-shot of Diane on the right and her friend
Margaret on the left, both seated at a small wooden cafe table holding
hand-thrown ceramic teacups. Margaret has silver curly plasticine hair,
round wire glasses, a sage-green cable-knit sweater. They are sharing
afternoon tea over a small clay teapot. Margaret is mid-remark — mouth
slightly open, sculpted eyebrows raised in curiosity, looking at Diane.
Diane holds her teacup partway to her mouth, expression softly self-conscious,
eyes glancing down. Background includes a wall of potted plants on wooden
shelves, hanging brass pendant lights, all in soft macro bokeh. Warm tungsten
light from above.

[MATERIAL DETAIL — Diane's terracotta plasticine hair and Margaret's silver
sculpted curls both show carved strand grooves; both knit garments show
real wool weave; ceramic teacups are hand-thrown with slight off-roundness;
wooden table has visible grain.]

[NEGATIVE]
```

---

## Beat 4 — Quiet despair (solo reflection)

**Goal:** Protagonist alone, looking at her reflection or out a window. Narrator carries the emotional beat.

**Formula:**

```
{STYLE LOCK}

Aspect ratio 9:16, {{MEDIUM_OR_WIDE}} shot of {{PROTAGONIST_FROM_CAST_SHEET}}
standing alone in {{INTROSPECTIVE_LOCATION}}, {{REFLECTIVE_POSE}}. Her
expression is {{SUBDUED_EMOTION}}. Soft dim tungsten light enters from
{{LIGHT_SOURCE}}, casting long sculpted shadows. The background is sparse,
quiet, and slightly shadowed compared to other beats — emphasizing solitude.

{MATERIAL DETAIL — skin/hair/knit emphasized in the dimmer light}

{NEGATIVE}
```

**Worked example (Diane at full-length mirror):**

```
[STYLE LOCK]

Aspect ratio 9:16, medium-wide shot of Diane standing alone in her dimly lit
living room, in front of a full-length wood-framed standing mirror. She
faces the mirror in three-quarter profile, one hand lifted to her cheek.
Her reflection shows the same pose from the front, slightly different —
she studies it quietly. Her expression is subdued, lips closed, eyes lowered.
Soft dim tungsten light enters from a single lamp on a wooden side table,
casting long sculpted shadows across the rug. The background is sparse —
a worn armchair, a bookshelf with clay-rendered book spines — quiet and
slightly shadowed.

[MATERIAL DETAIL — cream knit cardigan shows wool weave even in dim light;
sculpted hair strands catch the lamp glow; wooden floor and mirror frame
show visible grain and hand-painted finish.]

[NEGATIVE]
```

---

## Beat 5 — Clay infographic / "research" (no characters needed)

**Goal:** A hand-sculpted clay chart, diagram, or infographic explaining the mechanism. Static or with one subtle indicator.

**Formula:**

```
{STYLE LOCK}

Aspect ratio 9:16, head-on shot of a {{CHART_TYPE}} sculpted entirely from
clay and plasticine on a {{FRAME_DESCRIPTION}}. Title at top reads
"{{TITLE_TEXT}}" in chunky hand-sculpted clay letters with slight
asymmetry — each letter looks individually shaped by hand. The chart shows
{{CHART_CONTENT}}. {{INDICATOR_OR_ANNOTATION}}. Soft tungsten light falls
across the chart from camera-left, casting subtle sculpted shadows that
reveal the depth of each clay element. The wall behind the frame is plain
cream-painted clay with a slight texture.

{MATERIAL DETAIL — emphasize clay letters/lines, hand-shaped imperfection}

{NEGATIVE}
```

**Worked example (Calcium-in-skin chart from reference):**

```
[STYLE LOCK]

Aspect ratio 9:16, head-on shot of a line graph sculpted entirely from clay
and plasticine on a hand-carved wooden frame. Title at top reads "CALCIUM
IN SKIN" in chunky hand-sculpted clay letters with slight asymmetry — each
letter looks individually shaped by hand. The chart shows a high horizontal
line on the left labeled "HIGH" that drops sharply down to "LOW" near the
right side, with x-axis tick marks labeled "30 40 50 60" in clay buttons.
A small clay arrow points to the drop, labeled "MENOPAUSE" in a sculpted
rounded tag. Soft tungsten light falls across the chart from camera-left,
casting subtle sculpted shadows that reveal the depth of each clay element.
The wall behind the frame is plain cream-painted clay with a slight texture.

[MATERIAL DETAIL — clay letters show fingerprint impressions and slightly
uneven edges; line graph is a single carved plasticine ribbon; arrow and
tags are individually pressed clay; wooden frame has hand-carved grain and
hand-painted finish.]

[NEGATIVE]
```

---

## Beat 6 — Discovery (product close-up + protagonist reach)

**Goal:** Close to medium shot of the product (rendered as a clay-shaded prop) sitting on a wooden surface, with the protagonist reaching toward it.

**Formula:**

```
{STYLE LOCK}

Aspect ratio 9:16, {{CLOSE_OR_MEDIUM}} shot of {{PRODUCT_DESCRIPTION_AS_CLAY_PROP}}
sitting on {{SURFACE}}. {{PROTAGONIST_FROM_CAST_SHEET}}'s hand enters frame
from {{HAND_DIRECTION}}, sculpted fingers reaching toward the product.
Surrounding props include {{SUPPORTING_PROPS}} in soft macro bokeh. Warm
tungsten light from {{LIGHT_SOURCE}} catches the product label, making the
hand-painted text readable.

{MATERIAL DETAIL — product prop, surrounding wood/ceramic/cloth}

{NEGATIVE}
```

**Worked example (refirm bottle on kitchen table):**

```
[STYLE LOCK]

Aspect ratio 9:16, medium shot of a small dusty-purple cylindrical bottle
labeled "refirm" in hand-painted cream lettering, with smaller hand-painted
text underneath that reads "PREMIUM HERBAL SUPPLEMENT" in matte purple,
sitting on a wooden kitchen table. The bottle is rendered as a clay prop —
slightly imperfect cylinder, hand-applied matte paint with subtle brush
texture. Diane's hand enters frame from camera-right, terracotta-clay
fingers reaching toward the bottle. Surrounding props include a cream
hand-thrown ceramic cup, a red gingham tablecloth corner, a tin kettle in
the background — all in soft macro bokeh. Warm tungsten light from a window
on camera-left catches the bottle label.

[MATERIAL DETAIL — bottle paint is slightly uneven matte; ceramic cup has
glaze pooling at the base; wooden table has visible grain and small dents;
hand shows sculpted knuckle creases and slight asymmetry.]

[NEGATIVE]
```

---

## Beat 7 — Transformation (montage / "weeks later")

**Goal:** Time passes. Protagonist uses the product. A weeks-later reveal shot showing subtle visual improvement.

**Formula:**

```
{STYLE LOCK}

Aspect ratio 9:16, {{FRAMING}} of {{PROTAGONIST_FROM_CAST_SHEET}} {{USING_OR_AFTER_USING_PRODUCT}}.
{{SUBTLE_TRANSFORMATION_CUE}}. Her expression is {{POSITIVE_EMOTION}} —
{{SPECIFIC_FACIAL_CUE}}. Soft natural tungsten light, slightly brighter and
warmer than earlier beats to signal positive change. Background is the
{{PRIMARY_SETTING}} from Beat 1, lit a touch more openly.

{MATERIAL DETAIL — note the subtle improvement: slightly smoother clay skin
in specific areas, slightly more open eyes, posture upright}

{NEGATIVE}
```

**Worked example (Diane weeks later in mirror):**

```
[STYLE LOCK]

Aspect ratio 9:16, medium close-up of Diane standing in front of her
bathroom mirror again, but the framing is slightly more open and the light
warmer than Beat 2. She is gently applying a small amount of cream from the
refirm bottle to her upper lip with one fingertip. Her expression is calmly
pleased — mouth softly closed, eyes brighter than before. The carved lines
above her lip are subtly less pronounced — same character, same identity,
but the clay surface there looks a touch smoother than in earlier beats.
Soft natural tungsten light, slightly brighter and warmer than earlier
beats. Background is her bathroom from Beat 2, lit a touch more openly.

[MATERIAL DETAIL — terracotta clay hair unchanged; clay skin still shows
thumbprint impressions everywhere except the specific lip area, which is
slightly smoother; cream cardigan shows the same wool weave; refirm bottle
is the same clay-shaded prop as Beat 6.]

[NEGATIVE]
```

---

## Beat 8 — Resolution + CTA

**Goal:** Confident protagonist with the product, ready for the burned-in CTA caption.

**Formula:**

```
{STYLE LOCK}

Aspect ratio 9:16, medium shot of {{PROTAGONIST_FROM_CAST_SHEET}} in
{{PRIMARY_SETTING}}, facing camera directly with a {{CONFIDENT_SMILE}}.
She holds {{PRODUCT_DESCRIPTION}} at chest height with sculpted clay hands,
the hand-painted label rotated cleanly toward camera. Warm tungsten light
from camera-left wraps her face, a soft rim light from camera-right.
{{BACKGROUND_PROPS}} are in soft macro bokeh. The lower third of frame
remains visually clean and uncluttered, leaving room for a post-production
caption overlay.

{MATERIAL DETAIL — clay skin, hair, knitwear, product, surrounding props}

{NEGATIVE}
```

**Worked example (Diane holds refirm):**

```
[STYLE LOCK]

Aspect ratio 9:16, medium shot of Diane standing in her sunlit kitchen,
facing camera directly with a warm gentle smile, sculpted laugh lines now
working with the smile instead of against her. She holds the small
dusty-purple refirm bottle at chest height with her sculpted clay hands,
the hand-painted "refirm" label rotated cleanly toward camera. Warm
tungsten light from camera-left wraps her face, a soft rim light from
camera-right catches her terracotta hair. Green-painted cabinets and the
red gingham tablecloth corner are in soft macro bokeh. The lower third of
frame remains visually clean and uncluttered, leaving room for a
post-production caption overlay.

[MATERIAL DETAIL — clay skin shows thumbprint impressions, clay hair shows
ribbon-strand grooves, cream cardigan shows real wool weave with slight
cuff wear, bottle paint is matte and slightly uneven, wooden cabinets
visible in bokeh show hand-painted finish.]

[NEGATIVE]
```

---

## Cross-beat continuity rules

1. **Always pass the prior approved protagonist still as a reference image** when generating the next beat that includes the protagonist. Beats 1 → 2 → 4 → 6 → 7 → 8 should chain. Beat 3 attaches Beat 1 (or Beat 2) as the protagonist reference; the supporting character is generated fresh from the cast sheet.
2. **Keep the STYLE LOCK and MATERIAL DETAIL blocks consistent.** Don't paraphrase.
3. **Reuse exact phrasing** for hair color, eye color, clothing, skin texture across every protagonist beat. "Terracotta-brown wavy plasticine hair sculpted in distinct ribbon-strands" should appear identically in every prompt — don't shorten to "brown clay hair" in later beats.
4. **Generate sequentially**, not in parallel. Identity drift compounds otherwise.
5. **Beat 5 is independent** — no character continuity needed. Can fire in parallel with beat 1.
6. **Beat 7 references Beat 6's product prop** — pass the approved Beat 6 still as a reference to keep the bottle identical.

## Image QA checklist (claymation-specific)

Before sending a still to Seedance, verify:

- [ ] **Clay texture is preserved** — thumbprint/tool marks visible on faces and hands; no smooth Pixar-style render leaking in
- [ ] **Knit fabric reads as real wool weave**, not painted-on stripes
- [ ] **Eyes are matte, not glossy** — single soft highlight max, no Pixar wet-eye multi-catchlight
- [ ] **Hair shows individual carved strand grooves**
- [ ] **Wooden/ceramic props show hand-painted finish** and slight irregularity
- [ ] **Character identity holds** across all protagonist beats — same face proportions, same hair color/style, same outfit
- [ ] **Product label paint looks hand-applied** — slight unevenness, matte
- [ ] **No burned-in text** unless beat 5 (the clay infographic) explicitly needs sculpted-letter copy
- [ ] **9:16 aspect ratio**
- [ ] **Lower third has clean negative space** on beat 8 for caption overlay

Standard 2-retry cap per beat. If the third attempt still loses clay texture or character identity, **try Nano Banana Pro for that specific beat** (it tends to hold texture better on close-ups and product props). Don't switch the entire ad — beat-by-beat fallback.

## When the user has a brand character sheet already

If they provide an existing claymation-style hero image, skip the cast-sheet protagonist build. Pass that hero as the reference image for every protagonist beat. Beat 5 (infographic) doesn't need it.
