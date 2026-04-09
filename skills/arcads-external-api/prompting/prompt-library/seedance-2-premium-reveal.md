# Premium Product Reveal — Seedance 2.0

**Use when:** You need a dramatic, dark-background product launch video — the kind brands use for hero product announcements, new model reveals, or "introducing the next generation" content. No person on screen. The product IS the star, floating in a void of black with dramatic lighting, animated text reveals, and premium material close-ups.

**Model guide:** Read [seedance-2.md](seedance-2.md) first for platform rules, API parameters, and the adaptation checklist.

## What defines this style

This style strips away everything except the product and dramatic text. The entire frame is black void — no environment, no lifestyle, no person. The product emerges from darkness through dramatic lighting that catches metallic surfaces, glass edges, or textured materials. Text builds phrase by phrase in clean, bold typography, creating a narrative rhythm without any spoken dialogue.

The power comes from **restraint and revelation**. Each beat reveals slightly more — a new angle, a new detail, a new text line that reframes what you're looking at. The pacing is deliberate and slow. Where UGC videos feel spontaneous and fast, this style feels inevitable and weighty. Every frame is composed, every movement is controlled, every text reveal is timed to land.

## The structure

```
 1. VOID STAGE        — the black backdrop and lighting setup
 2. PRODUCT HERO      — what the product looks like and how it's lit
 3. TEXT NARRATIVE     — the story told through animated typography
 4. REVEAL SEQUENCE   — the choreography of product angles and details
 5. VARIANT SHOWCASE  — size/color/model comparisons (optional)
 6. BRAND CLOSE       — final product name + series branding card
```

---

## Layer-by-layer formula

### Layer 1: Void stage

The background is pure black — not dark grey, not moody shadows, but true black void. The product appears to float in nothingness. Lighting is the only thing that gives the scene dimension.

**Pattern:**
```
{{DURATION}} premium product reveal video. Pure black background, {{LIGHTING_STYLE}}, {{LIGHTING_DIRECTION}}.
```

**Variables:**

| Variable | Options | Notes |
|----------|---------|-------|
| `DURATION` | 15 seconds | Seedance 2.0 maximum. Use full duration for this style. |
| `LIGHTING_STYLE` | dramatic studio rim lighting, soft gradient spotlight, hard directional key light, warm amber accent lighting, cool silver edge lighting | Rim lighting is the default — it outlines the product against the void |
| `LIGHTING_DIRECTION` | light coming from above and behind the product, side-lit from the left with a subtle fill on the right, backlit with a soft halo around the edges, overhead spot with sharp falloff | Specifies WHERE light hits the product |

**Key rule:** Never describe a visible light source (no lamps, no windows, no studio softboxes). The light simply exists — the source is invisible. This maintains the "floating in void" illusion.

---

### Layer 2: Product hero

Describe the product's physical form, material, and the specific way light interacts with its surfaces.

**Pattern:**
```
A {{PRODUCT_DESCRIPTION}} — {{MATERIAL_SURFACE}}, {{LIGHT_INTERACTION}}.
The product @(img1) is centered in frame, {{SCALE_CUE}}.
```

**Variables:**

| Variable | Options | Notes |
|----------|---------|-------|
| `PRODUCT_DESCRIPTION` | brushed stainless steel fire pit, matte black water bottle, polished aluminum speaker, frosted glass perfume bottle | Name the product + its primary material |
| `MATERIAL_SURFACE` | brushed metal with fine grain texture, polished surface with mirror reflections, matte finish absorbing light softly, textured rubber grip with subtle sheen | How the surface LOOKS under dramatic lighting |
| `LIGHT_INTERACTION` | rim light catching the edges in a thin white line, reflections sliding across the curved surface, light pooling in the engraved logo, soft highlights moving across the brushed grain | How light BEHAVES on this specific material |
| `SCALE_CUE` | filling the lower third of the frame, small enough to see its full form with black space around it, large and imposing in frame | Helps the model size the product correctly |

**Material-light pairing bank:**

| Material | Best lighting interaction | Example |
|----------|-------------------------|---------|
| Brushed metal | Rim light catching edges, grain visible | stainless steel fire pit, aluminum laptop |
| Polished/chrome | Sharp reflections sliding across surface | sunglasses, chrome hardware |
| Matte plastic/rubber | Soft diffused highlights, no hard reflections | phone case, matte water bottle |
| Glass/clear | Light refracting through, caustic patterns | perfume bottle, glass jar |
| Fabric/textile | Subtle texture under raking light, soft shadows | shoe upper, bag material |

---

### Layer 3: Text narrative

The text tells the story. It builds phrase by phrase — each line appearing in sequence, creating a narrative rhythm.

**Pattern:**
```
Bold white text appears: "{{LINE_1}}" — {{LINE_1_TIMING}}.
{{LINE_2_TRANSITION}}: "{{LINE_2}}" — {{LINE_2_TIMING}}.
{{LINE_3_TRANSITION}}: "{{LINE_3}}" — {{LINE_3_TIMING}}.
```

**Text reveal timing options:**

| Timing | Description | Use when |
|--------|-------------|----------|
| `fades in over 1 second` | Smooth, premium feel | Opening line, brand name |
| `snaps on screen` | Impact, emphasis | Key claim, product name reveal |
| `types on letter by letter` | Building tension | Feature descriptions |
| `slides in from left/right/below` | Motion energy | Secondary info lines |
| `builds word by word` | Dramatic pacing | Multi-word claims, taglines |

**Text narrative structures:**

| Structure | Line 1 | Line 2 | Line 3 | Best for |
|-----------|--------|--------|--------|----------|
| **Introduction** | "INTRODUCING" | Product category claim | Product name | New product launches |
| **Superlative** | Bold claim ("Our most X ever") | Proof point | Product name | Upgrades, next-gen |
| **Question** | "What if X?" | Answer/feature | Product name reveal | Innovation stories |
| **Feature stack** | Feature 1 | Feature 2 | Feature 3 + product name | Feature-heavy products |

**Key rules:**
- Max 3 text lines in 15 seconds — more feels rushed
- Each line should be under 8 words — this is a billboard, not a paragraph
- Text appears CENTER FRAME or upper third — never at the very bottom

---

### Layer 4: Reveal sequence

The choreography — how the product moves and how the camera moves around it. In 15 seconds, you get 2-3 distinct product views.

**Pattern:**
```
{{OPENING_REVEAL}}. {{CAMERA_MOVE_1}}.
{{TRANSITION}} — {{CAMERA_MOVE_2}}, {{DETAIL_FOCUS}}.
{{FINAL_POSITION}}.
```

**Opening reveal styles:**

| Style | Description | Best for |
|-------|-------------|----------|
| **Rise from below** | Product slowly rises into frame from bottom | Height-oriented products (bottles, fire pits) |
| **Fade from dark** | Lighting gradually illuminates a product already in frame | Any product, most dramatic |
| **Rotate in** | Product spins into position from off-angle | Products with interesting 3D form |
| **Zoom out** | Starts on extreme close-up detail, pulls back to reveal full product | Products with distinctive textures/details |

**Camera movement bank:**

| Move | Description | Effect |
|------|-------------|--------|
| `slow 360 rotation around the product` | Product stays center, camera orbits | Shows all sides, premium feel |
| `gentle push-in from medium to close-up` | Camera slowly approaches | Builds intimacy with product |
| `overhead top-down view descending` | Bird's eye, moving down | Great for products with interesting top profile |
| `slow pan across surface detail` | Camera slides laterally across texture | Highlights material quality |

**Key rule:** Every camera movement is SLOW. Movements should take 3-5 seconds minimum. Use adverbs like "slowly," "deliberately," "gracefully."

---

### Layer 5: Variant showcase (optional)

If the product comes in multiple sizes, colors, or models, show them in comparison.

**Pattern:**
```
{{COMPARISON_LAYOUT}} — {{ITEM_1_APPEARS}}, {{ITEM_2_APPEARS}}, {{ITEM_3_APPEARS}}.
{{SIZE_LABELS}} appear below each variant.
```

**Comparison layouts:**

| Layout | Description | Best for |
|--------|-------------|----------|
| **Top-down lineup** | Products viewed from above, appearing left to right | Size variants (small/medium/large) |
| **Side-by-side** | Products standing next to each other, camera at eye level | Height/form comparison |
| **Single swap** | One product morphs/transitions into another | Color variants, generations |

---

### Layer 6: Brand close

The final 2-3 seconds. Product name, series name, and brand lockup on screen.

**Pattern:**
```
Final frame: {{BRAND_LOCKUP_POSITION}}. Text reads "{{PRODUCT_FULL_NAME}}" in {{TYPOGRAPHY_STYLE}}.
The product is {{FINAL_HERO_ANGLE}}.
```

---

## Beat structure (15-second format)

| Beat | Timing | What happens | Text |
|------|--------|-------------|------|
| **1: Tease** | 0-4s | Product partially visible or emerging from darkness. First text line appears. Slow, dramatic. | "INTRODUCING" or bold claim |
| **2: Reveal** | 4-10s | Full product visible, camera moves around it. Key feature/claim text. This is the hero moment. | Product category + key differentiator |
| **3: Lineup + Close** | 10-15s | Variant comparison (if applicable) OR final hero angle. Product name and brand lockup. | Full product name + series branding |

**Pacing rules:**
- No spoken dialogue. Music/SFX carry the energy.
- Camera movements are slow and deliberate — never jerky or fast.
- Text transitions drive the rhythm. Each new text line = a new beat of energy.
- At least 1 second of pure black between the last text and the video end.

---

## Multi-clip strategy

This style naturally maps to a **3-clip product launch series:**

| Clip | Focus | Text narrative | Product view |
|------|-------|---------------|-------------|
| **Clip A: The Announcement** | "Something new is here" | INTRODUCING → bold claim → product name | Emerging from void, hero angle, brand close |
| **Clip B: The Features** | "Here's what makes it special" | Feature 1 → Feature 2 → Feature 3 | Close-ups on each feature detail, texture shots |
| **Clip C: The Lineup** | "Available in X sizes/colors" | "In All-New Sizes" or "X Colors" | Side-by-side comparison, variant reveal sequence |

Each clip stands alone as a 15-second ad, but together they tell a complete product launch story.

---

## Technical specs

### Lighting
- **Primary:** Rim/edge lighting from behind — creates a thin white outline around the product
- **Secondary:** Soft fill from one side to show surface detail without flattening
- **No visible light source** — light appears to come from nowhere
- **Highlight behavior:** Highlights should slide slowly across surfaces as the camera or product moves

### Color palette
- **Background:** Pure black (#000000)
- **Product:** True-to-life product colors with slightly boosted contrast
- **Text:** White or single brand accent color
- **No color grading** beyond high contrast

### Camera quality
- **Ultra-clean, sharp focus** — this is the opposite of UGC
- **No grain, no noise, no imperfections** — everything is deliberate
- **Shallow depth of field** on close-up shots
- **Smooth motion** — dolly/track feel, no handheld shake

### Resolution note
- Vertical (9:16) for social — product centered in frame with generous black space above and below
- Text must be readable on mobile — large, bold, high-contrast

---

## Complete template

```
15 seconds premium product reveal video. Pure black background,
{{LIGHTING_STYLE}}, {{LIGHTING_DIRECTION}}.

A {{PRODUCT_DESCRIPTION}} — {{MATERIAL_SURFACE}},
{{LIGHT_INTERACTION}}. The product @(img1) is centered in frame,
{{SCALE_CUE}}.

[00:00] {{OPENING_REVEAL}}. Bold white text fades in: "{{TEXT_LINE_1}}"
— centered above the product.

[00:04] {{CAMERA_MOVE_1}}, revealing {{DETAIL_1}}.
Text transitions to: "{{TEXT_LINE_2}}" — {{LINE_2_TIMING}}.

[00:09] {{CAMERA_MOVE_2}}. {{VARIANT_OR_HERO_ACTION}}.
Text: "{{TEXT_LINE_3}}" — {{LINE_3_TIMING}}.

[00:13] Final frame: {{BRAND_LOCKUP_POSITION}}.
Text reads "{{PRODUCT_FULL_NAME}}" in {{TYPOGRAPHY_STYLE}}.
The product is {{FINAL_HERO_ANGLE}}.

The camera moves slowly and deliberately throughout — every movement
is smooth, no quick cuts or handheld shake. The lighting is dramatic,
with rim light catching the product edges against the pure black void.
The feel is premium, authoritative, restrained — a product announcement
that commands attention through simplicity.
```

---

## Example: Premium Water Bottle Launch

```
15 seconds premium product reveal video. Pure black background,
dramatic studio rim lighting, light coming from above and behind
the product.

A double-walled insulated water bottle in matte midnight blue —
smooth matte finish absorbing light softly, rim light catching the
brushed metal lid in a thin white line. The product @(img1) is
centered in frame, filling the lower third of the frame.

[00:00] The bottle slowly rises into frame from below, rim light
illuminating its edges against the void. Bold white text fades in:
"ENGINEERED TO KEEP UP" — centered above the bottle.

[00:04] Slow 360 rotation around the bottle, revealing the textured
grip band and laser-etched logo. Text snaps on screen: "48-Hour
Ice Retention." — bold, centered.

[00:09] Camera pushes in to a close-up of the lid mechanism, showing
the one-hand flip action in slow motion. Text slides in from below:
"The All-New Summit Series" — mixed weight typography.

[00:13] Final frame: brand logo top-center with product name below it.
Text reads "SUMMIT HYDRATION SERIES" in bold sans-serif white text.
The bottle is shown at a slight 3/4 angle with rim lighting,
slowly rotating to a stop.

The camera moves slowly and deliberately throughout — every movement
is smooth, no quick cuts or handheld shake. The lighting is dramatic,
with rim light catching the metal lid and bottle edges against the
pure black void. The feel is premium, authoritative, restrained — a
product announcement that commands attention through simplicity.
```

---

## Adaptation checklist

- [ ] **15 seconds** — single Seedance 2.0 clip (max duration)
- [ ] **Pure black background** — void stage, no environment
- [ ] **Product is the only subject** — described in full detail (label, colors, material, shape)
- [ ] **No dialogue** — text-and-visuals-only format, zero spoken words
- [ ] **Max 3 text lines** — each under 8 words, reveal timing specified
- [ ] **Reveal sequence** — opening reveal style chosen, 2-3 camera movements, all SLOW
- [ ] **Brand close** — product full name, typography style, final hero angle
- [ ] **Lighting** — rim/edge lighting dominant, no visible light source
- [ ] **Timestamps** — 4 timestamp blocks covering the full 15 seconds
- [ ] **Word count** — prompt between 100–260 words
- [ ] **@(img1)** — product image reference included
- [ ] **No forbidden words** — no "cinematic" (use "dramatic" or "premium"), no "8k," "studio," "perfect"
