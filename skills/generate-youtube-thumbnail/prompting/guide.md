# Prompting guide — YouTube thumbnails via Nano Banana 2

This guide covers **likeness alignment**, **expressions**, and **prompt structure**. Pair with [formulas.md](formulas.md) for the actual layout templates.

## The Big Three

1. **Likeness alignment** — use 5+ face references and an explicit CRITICAL block
2. **Expression** — pick from the cheat sheet below, be specific
3. **Structure** — follow the template, include all sections

## 1. Character likeness alignment

The single biggest difference between a thumbnail that "looks like a generic bearded guy" and one that "looks like *me*" is the number and variety of face references.

### The 5-reference rule

Use **at least 5 face reference images** showing the subject from different angles and expressions:

| Reference | Purpose |
|---|---|
| Front-facing headshot | Locks core face shape and proportions |
| Studio close-up (high detail) | Beard texture, skin tone, eye color |
| 3/4 angle | Cheekbone structure, profile |
| Front with smile | How the face changes with expression |
| Front with neutral / different expression | Baseline alignment |

With 1-2 references the AI generalizes. With 5+ it locks in the specific person.

### The CRITICAL CHARACTER LIKENESS block

Always include this in the prompt when the subject is a real person. It explicitly names features the AI tends to drift on, and tells the model not to generalize.

**Template:**
```
CRITICAL CHARACTER LIKENESS: The subject is the exact same person shown in
ALL the face reference photos. Match his/her face EXACTLY: [describe beard,
hair color, skin tone, eye color, glasses style, distinctive features, age].
Maintain the exact same facial proportions, eye shape, [beard style], and
skin tone as the reference photos. Do not generalize or use a generic
[bearded man / blonde woman / etc.] — this is a specific real person and
his/her exact likeness must be preserved.
```

**Example (Caleb):**
```
CRITICAL CHARACTER LIKENESS: The subject is the exact same person shown in
ALL the face reference photos. Match his face EXACTLY: full ginger
reddish-brown beard with mustache, fair pale skin with subtle freckles,
light blue-green eyes, round thin-rimmed wire-frame glasses with black
metal frames, slightly receding hairline, prominent cheekbones, gentle
nose, mid-30s. Maintain the exact same facial proportions, eye shape,
beard style, and skin tone as the reference photos. Do not generalize or
use a generic bearded man — this is a specific real person and his exact
likeness must be preserved.
```

### Why this works

The AI defaults to "average face that matches the description." Naming features explicitly + emphasizing "specific real person" + providing 5+ refs forces it to interpolate from the actual reference data instead of falling back to its training prior.

## 2. Expressions cheat sheet

Pick **one** specific expression per thumbnail. Vague ("happy", "excited") underperforms specific ("wide excited open-mouth smile showing teeth, eyebrows raised").

### Expressions ranked by typical YouTube CTR

| Rank | Expression | Prompt phrase | Best for |
|---|---|---|---|
| 1 | **Wide excited open-mouth smile** | "wide excited open-mouth smile showing teeth, eyebrows raised in genuine excitement, eyes wide" | Discovery / reveals / "this is amazing" |
| 2 | **Surprised shock** | "mouth slightly open in surprise, eyes wide and shocked, eyebrows raised high — genuinely surprised reaction" | Curiosity gap / "wait, what?!" |
| 3 | **Smug confident smirk** | "smug confident smirk with one eyebrow slightly raised, slight head tilt" | Secrets / "I know something you don't" |
| 4 | **Confident closed-mouth smile** | "confident closed-mouth smile, looking directly at camera, eyes warm" | Authority / professional / tutorial |
| 5 | **Big genuine laugh** | "huge genuine laughing smile showing all teeth, eyes squinting from laughter, head tilted slightly back, joyful and infectious" | Positive emotion / fun / community |
| 6 | **Shh / finger to lips** | "finger pressed to lips in a shh gesture, eyes wide with a mischievous knowing smirk looking directly at camera" | Secrets / hacks (note: includes hands) |
| 7 | **Pointing at element** | "pointing dramatically with one hand toward [element], mouth open in awe, eyebrows raised" | Tutorials / explainers (note: includes hands) |
| 8 | **Hands gripping cap (mind blown)** | "both hands gripping the brim of his cap as if his mind is blown, mouth wide open" | Reaction / shock (note: includes hands) |

### Hands or no hands?

If the user wants a **clean head-and-shoulders crop**, explicitly say "NO HANDS VISIBLE. Just head and upper shoulders" in the SUBJECT block. Otherwise the AI will often add hands forming weird shapes.

If the formula calls for hands (peace signs, pointing, shh gesture), use it but expect higher reject rate due to finger-count errors.

## 3. Prompt structure

The template that consistently produces the best results:

```
YouTube thumbnail, 16:9 landscape.

[SUBJECT BLOCK — likeness CRITICAL block + clothing + framing + hands rule]

Expression: [specific expression from cheat sheet]

[LEFT VISUAL ELEMENT — describe + reference]

[RIGHT VISUAL ELEMENT — describe + reference]

Across the [top / bottom] of the frame in massive bold yellow block letters
with a thick black outline reads [TITLE TEXT].

Background: [color + glow style]

Style: [aesthetic notes — vibrant, high-contrast, Mr Beast style, etc.]

Avoid: distorted face, extra fingers, [hands visible if no-hands rule],
blurry logos, illegible text, generic face
```

### Section breakdown

**SUBJECT BLOCK** — The most important section. Always includes:
- CRITICAL CHARACTER LIKENESS paragraph
- Clothing description (with brand details if applicable)
- Framing instructions ("tight head-and-shoulders crop", "face fills central 50% of frame")
- Hands rule ("NO HANDS VISIBLE" or specific hand gesture)

**Expression** — Pull from the cheat sheet above. Use the full prompt phrase, not just "smile."

**LEFT / RIGHT VISUAL ELEMENTS** — Describe each element AND reference the file ("use the Seedance logo reference exactly", "the cloned ad reference image showing [content description]"). The reference description tells the AI what's in the image; the "use the X reference exactly" phrase tells it to honor the file.

**Title text** — Phrase as: `Across the top in massive bold yellow block letters with a thick black outline reads [TITLE]`. This consistently produces readable bold-yellow-with-black-outline text. Other styles work too:
- `Bold red block text reads [TITLE]`
- `Massive white text with red outline at the top reads [TITLE]`
- `Hand-written marker style yellow text reads [TITLE]`

**Background** — Specify a color + glow:
- "dark navy gradient with subtle blue glow"
- "dark moody studio with purple and teal neon"
- "dark gradient with intense purple-pink ambient"
- For comparisons: "split background, warm left side, cool right side"

**Style** — Reinforce the aesthetic:
- "high-impact YouTube thumbnail in the style of Mr Beast and tech YouTubers"
- "vibrant saturated colors, oversized text, app icons floating beside subject"
- "cinematic dramatic mood, high contrast, neon rim lighting"

**Avoid** — The negative prompts that consistently matter:
- `distorted face` — always include
- `extra fingers` — always include if hands are visible
- `hands visible` — include when enforcing no-hands rule
- `peace signs` — include when explicitly avoiding peace signs
- `blurry logos` — include when logos are critical
- `illegible text` — include when title text is critical
- `generic face` — include when working with a specific person likeness
- `flat product photos` — include when you want lifestyle / hands-holding shots

## 4. Composition tips

### Framing for max likeness

The bigger the face, the more likeness data the AI shows. **Tight head-and-shoulders crops let the AI use more of the face data from your references.** Wide shots (full body) give the AI more freedom to drift.

For maximum likeness:
- "Tight head-and-shoulders crop with the face filling the central 50 percent of the frame"
- Add: "Use his exact facial likeness from the headshot reference"

### Logo placement

For symmetrical layouts, describe both:
- "To his LEFT side at chest level is a large rounded-square app icon containing [logo description] — use the [logo] reference exactly"
- "To his RIGHT side at chest level is a large rounded-square app icon containing [other logo description] — use the [other logo] reference exactly"

For corner placement:
- "[Primary brand logo] glows in the upper-left corner"
- "[Secondary brand logo] glows in the upper-right corner"

### Phone mockups

For "real vs AI" comparison thumbnails:
- "Tall vertical smartphone mockup labeled REAL in bold red text, displaying the [reference name] reference image"
- "Matching smartphone mockup labeled AI in bold green text, displaying the [reference name] reference image"

The phone labels (REAL / AI in red/green) consistently render correctly.

## 5. What to avoid in prompts

- **Vague expressions** — "happy" → "wide genuine smile showing teeth"
- **Vague colors** — "colorful" → "vibrant saturated purple and teal"
- **Vague composition** — "with the logo" → "logo at chest level on the left side"
- **Conflicting instructions** — "no hands" + "pointing at" don't combine
- **Long Avoid lists with redundant items** — keep to 4-6 specific items
- **Too many reference descriptions** — pick the 1-2 most important to call out, the rest will be inferred

## 6. Iteration patterns

When refining a generated thumbnail:

1. **Likeness off?** → Add more face references (5+ minimum), strengthen the CRITICAL block, name specific features that drifted
2. **Wrong expression?** → Use the more specific phrase from the cheat sheet
3. **Hands wrong?** → Add "NO HANDS VISIBLE" to subject block AND "hands visible" to Avoid
4. **Logo wrong?** → Add the actual file as a reference (don't rely on text description), use "use the X reference exactly"
5. **Text illegible?** → Make the text shorter, use the bold yellow + black outline phrasing
6. **Background too busy?** → Specify "clean dark gradient, no clutter"
7. **Face too small?** → "tight head-and-shoulders crop, face fills central 50 percent"

## 7. Reference image quality tips

- **Use sharp, well-lit photos** — blurry refs produce blurry features
- **Vary the angles** — front + 3/4 + close-up beats 5 front shots
- **Vary the expressions** — neutral + smile + serious gives the AI more to interpolate from
- **Use the actual brand assets** — pixel-accurate logos and products require real files, not descriptions
- **Upscale small images** — the batch script handles this, but starting with high-res is better
- **Strip backgrounds for icons/logos** — clean alpha or white backgrounds render more reliably
