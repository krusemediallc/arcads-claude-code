# Ad remix — recreate existing ads with new branding

**Use when:** The user has an existing ad image (competitor ad, inspiration piece, previous campaign) and wants to generate a new version with their own product, branding, colors, or copy direction — while preserving the composition, mood, and visual structure of the original.

## Workflow

```
User provides reference ad image
  (drop into references/aesthetics/ad-remix/ or paste URL)
        |
        v
Agent analyzes the reference ad:
  - Composition & layout
  - Lighting & color palette
  - Mood & style
  - Subject placement & framing
  - Background & props
  - What makes it work
        |
        v
Agent presents analysis + proposed swap plan
  (what stays, what changes)
        |
        v
User confirms / adjusts
        |
        v
Agent composes Nano Banana prompt
  using reference ad as style `referenceImages`
  + product photo as `refImageAsBase64` (if applicable)
        |
        v
POST /V2/images/generate
        |
        v
QA → compare to original → iterate → deliver
```

## What can be swapped

| Element | How to swap it | Notes |
|---------|---------------|-------|
| **Product** | Replace with user's product photo via `refImageAsBase64`; describe the new product in the prompt | Product shape/size differences may require composition adjustments |
| **Brand colors** | Specify new color palette in the prompt; override background, accent, and prop colors | Name exact colors (e.g., "deep navy #1B2A4A") for precision |
| **Copy/text direction** | Describe where text should go (negative space) — actual text added in post-production | Do NOT ask Nano Banana to render text; it will garble it |
| **Setting/background** | Describe a new environment while keeping the same lighting style and composition | Lighting cues are more important than the literal location |
| **Model/person** | Swap in an AI influencer from `references/influencers/` as `referenceImages` | Use hero image as first reference for identity consistency |
| **Mood/tone** | Adjust lighting temperature, color grading cues, contrast level | Small changes here shift the entire feel |
| **Aspect ratio** | Change for different platforms (1:1, 9:16, 16:9) | May require recomposing the layout |

## What should stay the same

These are the elements that made the original ad effective — preserve them:

- **Composition structure** — where the subject sits in frame, use of negative space, visual hierarchy
- **Lighting direction and quality** — hard vs soft, direction, color temperature
- **Depth of field** — what's sharp vs blurred
- **Overall mood** — the emotional tone the viewer feels
- **Visual rhythm** — spacing, balance, symmetry or deliberate asymmetry

## Step-by-step flow

### Step 1: Collect the reference ad

The user provides the ad image. Accept it from:
- `references/aesthetics/ad-remix/` folder (preferred — saved for reuse)
- A URL (download and save to `references/aesthetics/ad-remix/`)
- Pasted directly in the conversation

If the user has multiple reference ads, ask which one to start with. Each gets its own remix cycle.

### Step 2: Analyze the reference ad

Examine the image and break it down into these components. Present the analysis to the user so they can confirm you're reading the ad correctly.

**Analysis template:**

```
## Reference ad analysis

**Composition:** [e.g., "Product centered in lower third, generous negative space
upper-right for headline. Rule of thirds — product sits at bottom-left intersection."]

**Subject:** [e.g., "Single amber glass bottle, tall and narrow, gold cap, white label"]

**Lighting:** [e.g., "Soft directional light from upper-left, warm tone (~3500K),
subtle rim light on product edge, soft diffused shadows falling right"]

**Color palette:** [e.g., "Dominant: warm cream (#F5E6D3), soft peach (#FFDAB9).
Accents: gold (#C5A55A), deep amber (#8B4513)"]

**Background:** [e.g., "Smooth gradient from warm cream to soft peach, no props,
no texture — pure color"]

**Mood/style:** [e.g., "Premium, minimal, warm, luxurious — reads as high-end
skincare or fragrance"]

**Depth of field:** [e.g., "Deep — everything in focus, product is tack-sharp"]

**Props/context:** [e.g., "None — product only. Surface appears to be polished
stone or marble slab, beige/cream"]

**What makes it work:** [e.g., "The simplicity — one product, warm tones, generous
breathing room. The gold accents tie the cap to the background warmth. Feels
expensive without being busy."]
```

### Step 3: Define the swap plan

Based on the analysis, propose what changes and what stays:

```
## Swap plan

**Keeping (from original):**
- Composition: product centered in lower third, negative space upper-right
- Lighting: soft directional from upper-left, warm tone, rim light on edges
- Style: premium minimal, deep focus, clean background
- Color temperature: warm

**Changing:**
- Product: [original] → [user's product description]
- Color palette: [original colors] → [user's brand colors]
- Background: [original] → [adjusted for brand colors]
- Surface: [original] → [adjusted if needed]
```

Get user confirmation before generating.

### Step 4: Compose the prompt

Build the prompt by translating the analysis into Nano Banana language:

1. **Start with composition cues** — where the product sits, framing, negative space
2. **Describe the new product** — shape, material, color, label details (if the user provided a product photo, this supplements `refImageAsBase64`)
3. **Replicate the lighting** — direction, quality, temperature, shadow behavior
4. **Specify the new color palette** — background, accent colors, surface material
5. **Set the mood** — style descriptors that match the original's emotional tone
6. **Add negative cues** — "Avoid" anything that would break the composition

**Prompt structure:**

```text
{{COMPOSITION_CUE}}: {{NEW_PRODUCT_DESCRIPTION}} {{PLACEMENT}}.
Surface: {{SURFACE_MATERIAL_AND_COLOR}}.
Lighting: {{REPLICATED_LIGHTING_FROM_ANALYSIS}}.
Background: {{NEW_BACKGROUND_WITH_BRAND_COLORS}}.
Color palette: {{BRAND_COLORS}}.
Style: {{MOOD_DESCRIPTORS_FROM_ANALYSIS}}.
Depth of field: {{DOF_FROM_ANALYSIS}}.
Avoid: {{NEGATIVE_CUES}}, text, people, clutter.
```

### Step 5: Set up references

| Input | API field | Purpose |
|-------|-----------|---------|
| **Reference ad image** | `referenceImages` | Style/composition reference — the model uses this for visual inspiration |
| **Product photo** (if available) | `refImageAsBase64` | Product fidelity — the model tries to reproduce this product |

Upload both via presigned URL. The reference ad goes in `referenceImages`, the product photo in `refImageAsBase64`. This tells the model: "Make something that *looks like* the reference ad but *features* this product."

If no product photo is available, describe the product in detail in the prompt and use only the reference ad as `referenceImages`.

### Step 6: Generate

Call `POST /V2/images/generate` with:
- `productId` and `projectId` (from session folder)
- `model`: as chosen by user (default `nano-banana-2`)
- `prompt`: the composed prompt
- `aspectRatio`: match the original ad's ratio unless the user wants a different platform format
- `referenceImages`: [reference ad `filePath`]
- `refImageAsBase64`: product photo (if available)

Default to **3 variations** for comparison. Fire sequentially, poll concurrently.

### Step 7: Compare, QA, and iterate

1. **Side-by-side comparison:** Present each variation alongside the original reference ad
2. **Check structural fidelity:** Does the composition match? Lighting direction? Color temperature? Negative space placement?
3. **Check brand accuracy:** Are the new colors correct? Does the product look right?
4. **Standard QA** per [nano-banana.md](nano-banana.md): merged objects, artifacts, garbled text, impossible geometry
5. If the composition drifted significantly from the original, refine the prompt with stronger composition cues and regenerate

**Common iteration directions:**
- **"Closer to the original"** → strengthen composition cues, add more specific layout language
- **"More differentiated"** → loosen composition cues, let the brand voice take over
- **"Product doesn't look right"** → use a cleaner product photo, add more product detail in prompt
- **"Colors are off"** → specify exact hex codes, name the color in multiple ways ("deep navy blue, #1B2A4A, dark midnight blue")

## Batch remix workflow

When the user wants to remix **multiple reference ads** in one session:

1. Collect all reference ads into `references/aesthetics/ad-remix/`
2. Name them descriptively: `competitor-hero-shot.jpg`, `inspo-flat-lay.jpg`, etc.
3. Process each one through the full analyze → swap → generate → iterate cycle
4. Use the **same product photo and brand colors** across all to maintain campaign consistency
5. Keep the same `referenceImages` for product/brand references; only swap the style reference ad for each

## Storing reference ads

```
references/
  aesthetics/
    ad-remix/
      competitor-hero-shot.jpg     # Ad to remix
      inspo-flat-lay.jpg           # Another ad to remix
      brand-campaign-q1.jpg        # Previous campaign to refresh
```

Save reference ads here so they can be reused across sessions. Name them descriptively.

## Example

**User provides:** A competitor's skincare ad — amber bottle on marble, warm cream background, premium feel.

**Analysis:**
- Composition: centered product, lower third, negative space upper-right
- Lighting: soft from upper-left, warm, rim light on bottle edges
- Colors: cream, peach, gold, amber
- Mood: premium minimal luxury

**User's brand:** Cool-toned, modern, deep navy + silver + white

**Swap plan:** Keep composition and lighting direction. Change colors to navy gradient background, silver accents, white marble surface. Swap product to user's frosted glass bottle.

**Resulting prompt:**
```text
Product hero shot: frosted glass serum bottle with silver cap, centered in the
lower third of frame, generous negative space in the upper-right quadrant.
Surface: white Carrara marble slab with subtle grey veining.
Lighting: soft directional light from upper-left, cool tone, subtle rim light
on bottle edges catching silver highlights, soft diffused shadow falling right.
Background: smooth gradient from deep navy (#1B2A4A) to slate blue (#4A6274).
Color palette: deep navy, silver, white, cool grey.
Style: premium minimal, modern luxury, tack-sharp focus on product, editorial
product photography.
Depth of field: deep — everything in focus.
Avoid: people, hands, text, warm tones, gold, clutter, busy backgrounds, extra props.
```

## Credit cost

```
3 variations × Nano Banana 2 = 0.09 credits
3 variations × Nano Banana Pro = (check MASTER_CONTEXT.md pricing)
```

Plus any QA/iteration retries. Show cost and get confirmation before generating.

## Tips

- **The reference ad is style inspiration, not a template.** Nano Banana won't replicate it pixel-for-pixel. You're capturing the *essence* — the composition logic, lighting feel, and mood — not making a copy.
- **Strongest results come from clear composition language.** "Product in lower-left third with negative space upper-right" is more actionable than "like the reference."
- **Color specificity matters.** Always name colors multiple ways: descriptive name + hex code + mood word (e.g., "deep navy blue #1B2A4A, dark and confident").
- **One remix at a time.** Don't try to remix multiple reference ads in a single prompt. Each reference ad gets its own generation cycle.
- **Product photos dramatically improve fidelity.** Without `refImageAsBase64`, the model invents the product from text. With it, the product shape, material, and proportions are grounded.
