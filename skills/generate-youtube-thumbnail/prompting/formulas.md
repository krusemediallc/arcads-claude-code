# 5 proven YouTube thumbnail formulas

Each formula is a layout pattern that has been tested and validated. Pick based on the user's intent (see the decision matrix in [SKILL.md](../SKILL.md)).

For each formula:
- **When to use** — the trigger conditions
- **Layout** — what goes where
- **Reference images needed** — what files you need on disk
- **Prompt template** — copy and fill in the brackets
- **Expression options** — which expressions work best with this formula
- **Pitfalls** — common things that go wrong

---

## Formula 1: Peace-sign / branding

**When to use:** User wants a clean branding thumbnail showing themselves with two brand logos. Best for "introducing X" or "this changed everything" video framings. The cleanest, most flexible formula.

**Layout:**
- Subject centered, head-and-shoulders crop
- Brand logo 1 (square app icon) on the LEFT at chest level
- Brand logo 2 (square app icon) on the RIGHT at chest level
- Massive bold yellow title at the top with thick black outline
- Dark navy gradient background

**Reference images needed:**
- 5+ face references (headshot + 3/4 + close-ups)
- Brand logo 1 (clean PNG/JPEG)
- Brand logo 2 (clean PNG/JPEG)

**Prompt template:**

```
YouTube thumbnail, 16:9 landscape.

CRITICAL CHARACTER LIKENESS: The subject is the exact same person shown in
ALL the face reference photos. Match his face EXACTLY: [DESCRIBE FEATURES].
Maintain the exact same facial proportions, eye shape, beard style, and skin
tone as the reference photos. Do not generalize — this is a specific real
person and his exact likeness must be preserved.

He is wearing [CLOTHING DESCRIPTION]. The shot is a tight head-and-shoulders
crop with his face large and prominent, filling the central 50 percent of
the frame. NO HANDS VISIBLE. Just head and upper shoulders, facing camera.

Expression: [EXPRESSION FROM CHEAT SHEET]

To his LEFT side at chest level is a large rounded-square app icon
containing the [LOGO 1 DESCRIPTION] — use the [LOGO 1 NAME] reference
exactly. To his RIGHT side at chest level is a large rounded-square app
icon containing the [LOGO 2 DESCRIPTION] — use the [LOGO 2 NAME] reference
exactly.

Across the very top of the frame in massive bold yellow block letters with
a thick black outline reads [TITLE].

Background: dark navy gradient with subtle blue glow.

Style: clean high-impact YouTube thumbnail in the style of Mr Beast and
tech YouTubers, vibrant saturated colors, oversized text, app icons
floating beside the subject.

Avoid: distorted face, hands visible, peace signs, generic face, blurry
logos, illegible text.
```

**Expression options (best to worst for this formula):**
1. Wide excited open-mouth smile
2. Confident closed-mouth smile
3. Smug smirk

**Pitfalls:**
- Don't include peace signs unless explicitly requested — they cause finger-count errors
- Logos at "chest level" sit right beside the head; "below the subject" puts them too low
- Background should be solid dark — avoid busy patterns

---

## Formula 2: Real vs AI comparison

**When to use:** User wants to demonstrate AI replicating human content. Strong for "you can't tell which is AI" framings. High curiosity gap when the AI version looks photorealistic.

**Layout:**
- Subject centered, head-and-shoulders, often shocked expression
- Phone mockup on the LEFT showing the REAL ad (red label)
- Phone mockup on the RIGHT showing the AI version (green label)
- Brand logos in upper corners
- Title text at top or bottom

**Reference images needed:**
- 5+ face references
- Real ad screenshot (the source material)
- AI-generated ad image (the recreation)
- Brand logos for the corners

**Prompt template:**

```
YouTube thumbnail, 16:9 landscape.

[CRITICAL CHARACTER LIKENESS BLOCK]

He is wearing [CLOTHING]. Centered with shocked open-mouth surprised
expression matching the surprised reference photo. NO HANDS VISIBLE.

Expression: shocked open-mouth surprise, eyes wide, eyebrows raised in
disbelief.

On the LEFT side of the frame is a tall vertical smartphone mockup labeled
REAL in bold red text, displaying the real [PRODUCT TYPE] ad reference
image exactly as provided ([BRIEF DESCRIPTION OF REAL AD CONTENT]).

On the RIGHT side of the frame is a matching tall vertical smartphone
mockup labeled AI in bold green text, displaying the AI [PRODUCT TYPE] ad
reference image exactly as provided ([BRIEF DESCRIPTION OF AI AD CONTENT]).

In the top-left corner is the [LOGO 1 DESCRIPTION] — use the [LOGO 1 NAME]
reference exactly.

In the top-right corner is the [LOGO 2 DESCRIPTION] — use the [LOGO 2 NAME]
reference exactly.

Bold yellow text at the bottom with thick black outline reads
[TITLE — e.g. "CAN YOU TELL THE DIFFERENCE"].

Background: dark moody studio with purple and teal neon.

Style: high-impact YouTube thumbnail, dramatic three-point lighting on
subject, phones glow brightly.

Avoid: distorted face, hands visible, generic face, blurry logos,
illegible phone screen content.
```

**Expression options:**
1. Shocked open-mouth surprise (best — matches the "wait what" curiosity)
2. Wide excited smile
3. Smug smirk (cocky variant — "I made this")

**Title variations that work:**
- "CAN YOU TELL THE DIFFERENCE"
- "I CLONED THIS AD"
- "REAL vs AI"
- "WHICH ONE IS REAL?"
- "100% AI GENERATED"

**Pitfalls:**
- The AI ad reference must visually match the real ad's POV/aesthetic — flat product photos paired with hands-holding real ads look mismatched
- Phone screens render best at 2:3 vertical aspect inside the thumbnail
- Don't use too many reference images here (cap at 7) — the comparison gets muddied

---

## Formula 3: Terminal flow

**When to use:** User wants to show "the process" — feeding input through Claude Code / a terminal / an AI tool to produce output. Strong for technical / developer / "I built this" framings.

**Layout:**
- Large dark Claude Code terminal window taking up most of the frame
- Real ad / input on the LEFT inside the terminal
- AI-generated output on the RIGHT inside the terminal
- Glowing yellow arrow connecting input to output
- Subject reacting from the right side or bottom corner
- Title at the top

**Reference images needed:**
- 5+ face references
- Input image (real ad / source material)
- Output image (AI-generated result)
- Brand logos for corner placement (e.g. channel logo top-left, sponsor logo top-right)

**Prompt template:**

```
YouTube thumbnail, 16:9 landscape.

LEFT TWO-THIRDS / CENTER: a large dark macOS-style terminal window with
black background and crisp white monospace text. The terminal title bar
shows "Claude Code" and the prompt shows commands like
"$ claude generate ad", "Loading reference...", "Generating video... 99%",
"Success! Output ready".

Inside the terminal on the left is the [INPUT DESCRIPTION] reference image
exactly as provided, labeled INPUT in red. A bright glowing yellow arrow
flows from the input to the [OUTPUT DESCRIPTION] reference image on the
right inside the terminal, labeled OUTPUT in green.

[CRITICAL CHARACTER LIKENESS BLOCK]

In the [bottom-right / right-third / lower-right corner] is the bearded
man, looking at the terminal with [EXPRESSION], use his exact facial
likeness from the headshot reference. NO HANDS VISIBLE.

[PRIMARY BRAND LOGO] glows in the top-left of the terminal
(use the [primary] logo reference exactly). [SECONDARY BRAND LOGO] glows in
the top-right (use the [secondary] logo reference exactly).

Bold yellow text at the top with thick black outline reads
[TITLE — e.g. "I CLONED THIS AD"].

Background: dark dramatic studio with purple-blue neon ambient glow on
the subject.

Style: cinematic dark studio thumbnail with crisp terminal text and
glowing neon arrows. The terminal is the visual centerpiece.

Avoid: distorted face, hands visible, illegible terminal text, blurry
input/output images, generic face.
```

**Expression options:**
1. Wide-eyed shocked surprise (subject is amazed by the terminal output)
2. Wide excited open-mouth smile (subject is celebrating the result)
3. Smug knowing smirk (subject is showing off)

**Title variations:**
- "I CLONED THIS AD"
- "CLONE ANY AD"
- "AI AD FACTORY"
- "PROMPT TO AD"
- "BEFORE vs AFTER"
- "CODE YOUR ADS"

**Pitfalls:**
- The terminal text gets garbled if you specify too many specific lines — keep terminal text descriptions general ("commands like X")
- The arrow + INPUT/OUTPUT labels are critical for the flow to read — don't omit them
- If the subject is too small in the corner, increase their size with "subject occupies bottom 40% of frame"
- Real terminal screenshots sometimes work better than text descriptions — if the user has one, use it as a reference

---

## Formula 4: Reaction shock

**When to use:** Pure curiosity-driven thumbnail. Subject's face takes center stage with an exaggerated reaction. Best when the video has a "wait, this is real?" hook.

**Layout:**
- Subject takes 50-60% of frame, head-and-shoulders close-up
- Massive expression (shocked, amazed, jaw-dropping)
- Optional: 1-2 small visual elements (phone, screen, product) at the edges
- Big curiosity-gap title at the top

**Reference images needed:**
- 5+ face references (especially shocked/surprised expressions if you have them)
- 1-2 supporting visual elements

**Prompt template:**

```
YouTube thumbnail, 16:9 landscape.

[CRITICAL CHARACTER LIKENESS BLOCK]

He is wearing [CLOTHING]. The shot is a tight close-up with his face
filling 60 percent of the frame. NO HANDS VISIBLE.

Expression: mouth wide open in genuine shock, eyes wide and disbelieving,
eyebrows raised as high as possible, head pulled back slightly — the
"wait what?!" reaction. Show genuine surprise, not exaggerated cartoon.

[OPTIONAL: at the edge of the frame, the [REFERENCE ELEMENT] is partially
visible, glowing, with the orange Claude Code starburst logo nearby.]

Bold yellow text at the top with thick black outline reads
[TITLE — e.g. "WAIT, IT WORKED?!"].

Background: dark moody gradient with intense purple-blue rim light on
the subject.

Style: high-impact reaction thumbnail, dramatic key light on the face,
strong rim light, vibrant colors. Face is the centerpiece.

Avoid: distorted face, exaggerated cartoon expression, hands visible,
generic face, blurry text.
```

**Expression options:**
1. Shocked open-mouth (the canonical reaction)
2. Wide-eyed disbelief (mouth closed, eyes huge)
3. Hands gripping cap "mind blown" (if you allow hands)

**Title variations (curiosity hooks):**
- "HOW IS THIS REAL"
- "WAIT, IT WORKED?!"
- "I CAN'T BELIEVE THIS"
- "THIS BROKE MY BRAIN"
- "100% REAL"
- "NO WAY"

**Pitfalls:**
- "Exaggerated" or "cartoon" expressions look fake — use "genuine" in the prompt
- Without supporting visual elements the thumbnail can feel empty — at minimum add a glowing logo
- Background should NOT compete with the face — keep it dark and clean

---

## Formula 5: Before/after split

**When to use:** Direct comparison thumbnail. Strong for "replace your X" or "stop doing Y" framings. Most informative formula.

**Layout:**
- Vertical split down the middle (lightning bolt or clean line)
- LEFT: "BEFORE" with red X — the old way
- RIGHT: "AFTER" with green checkmark — the new way
- Optional: subject at the bottom-center reacting
- Big bold title at the top

**Reference images needed:**
- "Before" reference (could be a stock image of film crew, expensive setup, etc.)
- "After" reference (could be the AI tool output, a laptop with software, etc.)
- Optional face references for the reactor

**Prompt template:**

```
YouTube thumbnail, 16:9 landscape.

Clean split comparison with a jagged lightning bolt divider down the
middle.

LEFT HALF: [BEFORE DESCRIPTION — e.g. "expensive film production with
camera crew, lighting rigs, boom mic, and director"]. A big red X stamp
overlays the scene. Label "BEFORE" in bold red text at the top.

RIGHT HALF: [AFTER DESCRIPTION — e.g. "minimalist desk with just a laptop
generating video content, AI output visible on screen"]. A green checkmark
overlays the scene. Label "AFTER" in bold green text at the top.

[OPTIONAL: at the bottom-center is the bearded man with [EXPRESSION], use
his exact facial likeness. NO HANDS VISIBLE except possibly pointing at
the AFTER side.]

Bold yellow text at the top with thick black outline reads
[TITLE — e.g. "REPLACE YOUR FILM CREW"].

Background: warm tones on the BEFORE side, cool tech blue on the AFTER side.

Style: clean editorial comparison, bold contrast, YouTube thumbnail
aesthetic.

Avoid: cluttered busy composition, distorted face, illegible labels.
```

**Expression options (if subject is included):**
1. Pointing at the AFTER side
2. Smug smirk (knowing better)
3. Confident closed-mouth smile

**Title variations:**
- "REPLACE YOUR [X]"
- "STOP DOING [Y]"
- "BEFORE vs AFTER"
- "OLD WAY vs NEW WAY"
- "DON'T DO THIS"

**Pitfalls:**
- Each side needs its own clear visual centerpiece — don't let them blend
- Color-code the sides (warm/cool, red/green) for instant clarity
- Don't make the subject too prominent — the BEFORE/AFTER comparison is the centerpiece
- Avoid more than 2 visual elements per side — clutter kills readability

---

## Picking between formulas

| User intent | Formula | Why |
|---|---|---|
| "Just me + my brand for this video" | 1. Peace-sign / branding | Cleanest, most flexible |
| "Compare the original to the AI version" | 2. Real vs AI | Direct visual proof |
| "Show how I built this with Claude Code" | 3. Terminal flow | Process visualization |
| "I want a curiosity-driven thumbnail" | 4. Reaction shock | Pure CTR play |
| "Old way vs new way" / "replace X with Y" | 5. Before/after split | Direct framing |

When in doubt, **Formula 1 (peace-sign / branding)** is the safest bet — it works for almost any video topic and consistently produces clean results.

## Combining formulas

Some formulas can blend:
- **1 + 4** — Branding peace-sign with shocked expression (excited variant)
- **2 + 4** — Comparison with shocked subject in the middle
- **3 + 4** — Terminal flow with shocked subject reacting

When blending, lean on the dominant formula's structure and add the secondary formula's expression or visual element.
