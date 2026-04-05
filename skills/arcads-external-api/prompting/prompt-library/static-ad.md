# Static ad — product and brand image generation (no people)

**Use when:** The user wants to create polished static ad images — product heroes, lifestyle scenes, ingredient spreads, abstract brand visuals, flat lays, banners, etc. — without AI influencers or UGC-style content.

## Workflow

```
User describes the ad concept
        |
        v
Agent gathers inputs:
  - Product photo(s) from references/products/ (optional)
  - Style/mood references from references/aesthetics/ (optional)
  - Brand voice from MASTER_CONTEXT.md (optional)
        |
        v
Agent composes prompt using template below
        |
        v
POST /V2/images/generate (Nano Banana)
        |
        v
QA → iterate → deliver
```

## Ad categories and prompt strategies

| Category | Description | Key prompt cues |
|----------|-------------|-----------------|
| **Product hero** | Single product, clean background, studio feel | Studio lighting, specific surface material, shadows, reflections, no distractions |
| **Lifestyle context** | Product in a natural setting that implies use | Setting details (kitchen counter, gym bag, nightstand), time of day, ambient light |
| **Flat lay** | Top-down arrangement of product + complementary props | `Top-down flat lay`, arranged props, surface texture (marble, wood, linen), even lighting |
| **Ingredient/texture** | Close-up of ingredients, materials, or textures | Macro lens, shallow DOF, texture details, color palette, raw materials |
| **Abstract brand** | Mood/texture/color visuals for brand identity | Color palette, texture, mood words, no specific product, pattern or gradient |
| **Banner/key visual** | Wide-format hero for web or social headers | Specific aspect ratio, rule-of-thirds composition, negative space for text overlay |
| **Before/after** | Side-by-side comparison | Split composition, consistent lighting both sides, clear contrast |
| **Seasonal/thematic** | Holiday, seasonal, or event-themed product shots | Season-specific props and color palette, themed background, product integration |

## Step-by-step flow

### Step 1: Gather inputs

Ask the user for:

1. **Ad concept** — what are they trying to communicate? (e.g., "premium feel for our new serum," "summer vibes with the drink lineup")
2. **Category** — which type from the table above? (or let the agent infer from the description)
3. **Product details** — what product(s) to feature? Check `references/products/` for existing photos. If the user has a product photo, use it as `refImageAsBase64` for fidelity
4. **Aspect ratio** — `1:1` (social feed), `9:16` (stories/reels), `16:9` (banner/web). Default to `1:1` if not specified
5. **Brand guidelines** — check `MASTER_CONTEXT.md` for tone, audience, colors, words to use/avoid. Ask if nothing is filled in
6. **Style references** — check `references/aesthetics/` for relevant mood boards. If the user has specific visual inspiration, offer to save it there for future use
7. **Text on image** — does the user want text/copy baked into the image? **Warn them:** AI-generated text is often garbled or unreadable. Recommend adding text in post-production (Figma, Canva, etc.) unless they want to try. If they insist, keep text to 1-3 short words and include `"legible, sharp text reading: '{EXACT TEXT}'"` in the prompt
8. **Nano Banana engine** — default **Nano Banana 2** (`nano-banana-2`), or **Nano Banana Pro** (`nano-banana`) if they prefer

### Step 2: Compose the prompt

Use the prompt template below. Key principles:

- **Be specific, not vague.** "Warm golden hour light from the left" beats "nice lighting"
- **Name materials and textures.** "Matte black glass bottle on raw concrete slab" beats "product on surface"
- **Specify what's NOT in frame.** Negative cues prevent clutter and unwanted elements
- **Include color palette** when brand consistency matters — name 2-3 dominant colors
- **Composition cues** matter — rule of thirds, centered, off-center, negative space for copy, etc.

If brand voice exists in `MASTER_CONTEXT.md`, translate tone words into visual specifics:
- "Premium" → deep shadows, dark backgrounds, metallic accents, minimal props
- "Playful" → bright saturated colors, dynamic angles, scattered props, bold contrasts
- "Clean/minimal" → white/light backgrounds, generous negative space, single subject
- "Natural/organic" → earth tones, raw textures (wood, stone, linen), soft diffused light
- "Bold/energetic" → high contrast, vivid colors, dramatic angles, motion blur on elements

### Step 3: Upload references (if any)

If the user has product photos or style references:

1. Auto-upscale if longest side < 1024px (see SKILL.md "Image handling")
2. Upload via `POST /v1/file-upload/get-presigned-url` → `PUT` to S3 → get `filePath`
3. For a **product photo** the model should reproduce: use `refImageAsBase64` (strongest signal for product fidelity)
4. For **style/mood references**: use `referenceImages` array (visual inspiration, not literal reproduction)
5. Can combine both: `refImageAsBase64` for the product + `referenceImages` for the style

### Step 4: Generate

Call `POST /V2/images/generate` with:
- `productId` and `projectId` (from session folder)
- `model`: `nano-banana-2` (default) or `nano-banana` (Pro)
- `prompt`: the composed prompt
- `aspectRatio`: as determined in Step 1
- `refImageAsBase64` and/or `referenceImages`: if applicable

Default to **3 variations** so the user can compare. Fire sequentially, poll concurrently.

### Step 5: QA and present

1. **Post-generation QA** per [nano-banana.md](nano-banana.md): check for merged objects, melted edges, garbled text, impossible geometry, artifact seams
2. For product shots specifically, also check:
   - Product proportions match the real product
   - Labels/logos are not garbled (if visible)
   - Colors are consistent with the brand palette
   - No phantom objects or extra items that weren't prompted
3. Regenerate with refined prompt if defective (up to 2 retries per image)
4. Present QA-passed images as a numbered list
5. Assign all assets to session project via `POST /v1/assets/add-to-project`

## Prompt template

```text
{{CATEGORY}}: {{SUBJECT_DESCRIPTION}}.
Surface/setting: {{SURFACE_AND_ENVIRONMENT}}.
Composition: {{FRAMING_AND_LAYOUT}}.
Lighting: {{LIGHTING_DESCRIPTION}}.
Color palette: {{DOMINANT_COLORS}}.
Style: {{STYLE_AND_MOOD}}.
Avoid: {{NEGATIVE_CUES}}.
```

## Category-specific templates

### Product hero

```text
Product hero shot: {{PRODUCT_DESCRIPTION}} centered on {{SURFACE}}.
Composition: {{FRAMING}} with {{NEGATIVE_SPACE_DIRECTION}} negative space.
Lighting: {{LIGHTING}} with {{SHADOW_STYLE}} shadows.
Background: {{BACKGROUND}}.
Style: commercial product photography, crisp focus on product, {{MOOD}}.
Avoid: people, hands, text, clutter, busy backgrounds, extra props.
```

### Lifestyle context

```text
{{PRODUCT_DESCRIPTION}} placed naturally in {{SETTING}}.
Time of day: {{TIME}}. The product sits {{PLACEMENT}} — not centered, discovered naturally.
Props: {{2-3_CONTEXTUAL_PROPS}} arranged casually, not styled.
Lighting: {{NATURAL_LIGHT_SOURCE}}.
Style: editorial lifestyle photography, shallow depth of field on the product, {{MOOD}}.
Avoid: people, hands, staged look, studio lighting, floating objects.
```

### Flat lay

```text
Top-down flat lay on {{SURFACE_TEXTURE}}.
Center: {{PRODUCT_DESCRIPTION}}.
Arranged around it: {{PROPS_LIST}} — spaced evenly, nothing overlapping the product.
Lighting: soft even overhead lighting, minimal shadows.
Color palette: {{COLORS}}.
Style: clean editorial flat lay, every item intentional, {{MOOD}}.
Avoid: people, clutter, overlapping items, harsh shadows, text.
```

### Ingredient/texture

```text
Macro close-up: {{INGREDIENT_OR_TEXTURE_DESCRIPTION}}.
Shallow depth of field, tack-sharp foreground detail, soft bokeh background.
Lighting: {{LIGHT}} highlighting texture and surface detail.
Color palette: {{COLORS}}.
Style: food/beauty photography, sensory and tactile, {{MOOD}}.
Avoid: people, product packaging (unless requested), text, full product in frame.
```

### Abstract brand

```text
Abstract brand visual: {{MOOD_AND_CONCEPT}}.
Dominant colors: {{COLOR_1}}, {{COLOR_2}}, {{COLOR_3}}.
Texture: {{TEXTURE_DESCRIPTION}}.
Composition: {{PATTERN_OR_FLOW}}.
Style: abstract, modern, {{MOOD}} — suitable for brand background or social tile.
Avoid: people, products, text, recognizable objects, photorealism.
```

### Banner/key visual

```text
Wide-format key visual: {{SUBJECT_DESCRIPTION}}.
Composition: rule of thirds, {{SUBJECT_POSITION}} with generous negative space on {{SIDE}} for text overlay.
Aspect ratio: 16:9.
Lighting: {{LIGHTING}}.
Background: {{BACKGROUND}} — uncluttered, supports readability of overlaid text.
Style: {{STYLE}}, high production value, {{MOOD}}.
Avoid: text baked into image, busy backgrounds, centered composition, clutter.
```

## Examples

### Product hero — skincare serum

```text
Product hero shot: amber glass dropper bottle with gold cap, label reading "Glow Serum",
centered on a slab of raw beige travertine stone.
Composition: centered, vertical product, generous negative space above for cropping.
Lighting: soft studio three-point lighting, warm tone, subtle reflection on stone surface,
gentle shadow falling to the right.
Background: smooth gradient from warm cream to soft peach.
Style: commercial product photography, crisp focus on the bottle, premium and clean.
Avoid: people, hands, text, clutter, busy backgrounds, extra props.
```

### Lifestyle context — energy drink

```text
A tall matte-black energy drink can placed on a weathered wooden desk next to
an open laptop and scattered sticky notes. Late afternoon — golden hour light
streaming through a window to the left, casting long warm shadows across the desk.
The can catches a highlight on its edge. Shallow depth of field — laptop and
background soft, can in sharp focus.
Style: editorial lifestyle photography, authentic workspace, productive energy mood.
Avoid: people, hands, staged look, studio lighting, floating objects, visible brand logos on laptop.
```

### Flat lay — supplement stack

```text
Top-down flat lay on light grey linen fabric.
Center: three supplement bottles (white, amber, black) arranged in a diagonal line.
Around them: a halved lemon, fresh rosemary sprigs, a small wooden scoop with
powder, and a glass of water — spaced with breathing room, nothing overlapping.
Lighting: soft even overhead, minimal shadows, clean and bright.
Color palette: whites, ambers, soft greens, lemon yellow.
Style: clean wellness editorial flat lay, every item intentional, fresh and healthy.
Avoid: people, clutter, overlapping items, harsh shadows, text.
```

### Banner — SaaS product launch

```text
Wide-format key visual: a sleek laptop displaying a colorful dashboard interface,
floating slightly above a dark navy surface with subtle geometric light patterns beneath.
Composition: rule of thirds, laptop positioned left with generous negative space
on the right for headline text overlay.
Aspect ratio: 16:9.
Lighting: cool blue ambient glow from the screen, soft rim light from above,
dark dramatic background.
Background: deep navy gradient with subtle abstract geometric shapes — uncluttered.
Style: modern tech, high production value, innovative and confident.
Avoid: text baked into image, busy backgrounds, centered composition, people, hands.
```

## Working with brand guidelines

When `MASTER_CONTEXT.md` has brand information, apply it to every static ad:

| Brand field | How it affects prompts |
|-------------|----------------------|
| **Tone** | Translates to lighting, color temperature, prop choices, composition style |
| **Audience** | Informs setting choices, prop selection, overall vibe |
| **Colors** | Becomes the `Color palette` line in the prompt; influence background and prop colors |
| **Words to use** | Can inspire mood cues and style descriptors |
| **Words to avoid** | Check that prompt language and visual concepts don't contradict these |

## Iterating on results

After the user sees the initial variations:

- **"More premium"** → darken background, add reflections, reduce props, deepen shadows
- **"More vibrant"** → increase color saturation cues, brighter lighting, add complementary color props
- **"More minimal"** → remove props, increase negative space, simplify background
- **"More natural"** → switch to natural light, organic textures, earth tones, raw surfaces
- **"Needs more contrast"** → specify high contrast lighting, darker shadows, brighter highlights
- **"Product isn't prominent enough"** → tighter crop, larger product in frame, blur background more, add rim light on product edges

When iterating, keep the same `referenceImages` and `refImageAsBase64` — only change the prompt text. This maintains visual consistency across rounds.

## Preparing images for ad platforms

The generated images are raw creative — they'll likely need post-production for final ads:

- **Add text/copy** in Figma, Canva, or your design tool (AI text generation is unreliable)
- **Crop to platform specs** — generate at the closest aspect ratio, then fine-tune
- **Color grade** to match your brand exactly if the AI output is close but not perfect
- **Add logo/watermark** in post

For images intended as backgrounds for text overlay, always specify `"generous negative space on [side] for text overlay"` in the prompt and use the Banner template.

## Credit cost

```
3 variations × Nano Banana 2 = 0.09 credits
3 variations × Nano Banana Pro = (check MASTER_CONTEXT.md pricing)
```

Plus any QA retry generations. Show cost breakdown and get confirmation before generating.

## Combining with other workflows

Static ad images can feed into other Arcads workflows:

- **Start frame for video ads** — use an approved product hero as `startFrame` for Veo 3.1 to create an animated product reveal
- **B-roll background** — generate a scene/setting image, then use it as inspiration for Kling 3.0 b-roll video
- **Campaign consistency** — generate a series of static ads with the same `referenceImages` (style refs) to maintain visual cohesion across a campaign
- **Influencer + static** — pair character sheet images (from [character-sheet.md](character-sheet.md)) with static product shots for a complete campaign kit
