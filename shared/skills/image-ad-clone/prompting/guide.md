# image-ad-clone — reverse-engineer an existing ad into a reusable template

This guide is the shared brain for the **`image-ad-clone`** skill — taking an existing image ad and turning it into a parameterizable prompt template stored in the shared library.

The workflow is **model-agnostic through Phase 6**. The model choice happens in Phase 1: the skill asks the user (or auto-detects from the reference's typography-vs-photo balance) whether to validate against:
- **`chatgpt-image-ad`'s generator** (gpt-image-2) — for typography / UI-mimicry templates
- **`nano-banana-image-ad`'s generator** (Nano Banana family) — for photoreal / lifestyle / multi-ref templates

Phase 8 optionally cross-validates against the OTHER backend so the resulting library entry has accurate `Model notes:` for both.

For the shared library, see:
- [shared/skills/image-ad-prompting/prompting/prompt-library.md](../../image-ad-prompting/prompting/prompt-library.md) — destination for new entries
- [shared/skills/image-ad-prompting/prompting/template-format.md](../../image-ad-prompting/prompting/template-format.md) — entry format / skeleton
- [shared/skills/image-ad-prompting/prompting/safety-suffixes.md](../../image-ad-prompting/prompting/safety-suffixes.md) — the 3 always-on suffixes

## Hard rules — never relax

1. **Strip platform/screenshot chrome from analysis.** When describing what's in the reference, describe the actual ad creative, not the screenshot wrapper. Do not include iOS status bars, "Sponsored"/"Saved" badges, post text/captions surrounding the image, link-card footers, engagement rows, platform tab bars. If the reference is a screenshot of an ad-in-feed, mentally crop the wrapper. The output template must produce a standalone image that would be uploaded as a Meta creative.

2. **Always validate by generating.** A template that hasn't been round-tripped through the chosen model against the original isn't validated. Run at least one generation with `--image-ref <original>` and compare. Refine the prompt until the structure matches.

3. **Always test the generalized version.** Before saving, fill the placeholders with a *different brand* (use AG1 if the user has no preference — there are seeded examples in the existing library) and generate. If the structure breaks, the placeholder set is wrong — fix it.

4. **Never write brand-specific text into the final template.** Wordmarks, product names, slogans, specific photographs, hex colors specific to the source brand — all become `{placeholders}`. Only structural content (layout descriptions, photography style, typography family, composition rules) remains literal.

5. **Save to the user's library, do not silently overwrite.** Default save target is the shared library at `shared/skills/image-ad-prompting/prompting/prompt-library.md`. If the target template name (e.g., `T40 — Lifestyle hero`) collides with an existing entry, ask the user before overwriting.

6. **Validate against BOTH target models when possible.** Even if the user only cares about one backend right now, document model notes for both. The library entry's value is portability — a `gpt-image-2: clean / nano-banana: weak on small text` note saves future you from picking the wrong backend.

## Inputs the user must provide

| Input | Notes |
|---|---|
| **Reference ad image** | Path to a local file (PNG/JPG/WEBP). The thing being reverse-engineered. |
| Brand to test against (optional) | If they want the test fill to use a specific brand. Default: AG1 if any AG1 assets exist, otherwise ask. |
| Save target (optional) | Defaults to the shared library at `shared/skills/image-ad-prompting/prompting/prompt-library.md`. |
| Template tag (optional) | Short identifier like `T40`, `Lifestyle Hero` — Claude proposes one based on the analysis if not given. |

## Workflow

### Phase 1: Preflight

1. The reference image path resolves to an existing file. If not, stop and ask.
2. The credentials the matching `generate_image.py` needs are present in `.env`.
3. **Pick the backend.** Ask the user "validate against gpt-image-2 or Nano Banana?" or auto-detect from the reference (typography-heavy → gpt-image-2; photoreal / handheld / multi-ref → Nano Banana). Then locate the matching companion generator:
   - For gpt-image-2: `chatgpt-image-ad/scripts/generate_image.py`
   - For Nano Banana: `nano-banana-image-ad/scripts/generate_image.py`

   Look in this order:
   - `~/.claude/skills/<companion>/scripts/generate_image.py`
   - `<repo>/skills/<companion>/scripts/generate_image.py`
   - If neither: stop and ask the user to install the companion skill (this skill's hard dependency).
4. Read the save target (the shared library). If the file exists, read its current entries to know what tags are taken. If not, plan to create it.

### Phase 2: Visual analysis

This is the most important phase. Read the reference image and describe what you see, structurally separating brand-specific content from format/structure. Document each of these:

- **Aspect ratio.** Measure or estimate (W:H). Map to the nearest supported ratio for the chosen model. For `chatgpt-image-ad`: `{1:1, 2:3, 3:2, 9:16, 16:9}`. For `nano-banana-image-ad`: also `{4:5, 5:4, 3:4, 4:3, 21:9}`.
- **Format type.** What this ad pretends to be: editorial article, product flatlay, comparison table, fake search results, story composite, native UI mimic, etc.
- **Layout structure.** Header / hero / footer / grid — how regions are arranged.
- **Typography.** Family (geometric sans, condensed sans, serif, handwritten marker, monospace), weight, hierarchy. Do NOT name specific fonts unless they're iconic and necessary; instead describe the *feel*.
- **Color palette.** 3-6 hex codes. Identify which are brand-specific (will become `{brand.color_*}` variables) vs neutral/structural (white/black/grey backgrounds — stay literal).
- **Photography style.** Studio product flatlay, lifestyle UGC, editorial portrait, stock-photo-grid, etc. Describe lighting and lens.
- **Text content (verbatim).** Every visible string in the image. Mark which strings are *brand-specific* (e.g. "AG1", "Drink AG1") vs *structural* (e.g. "AS SEEN ON", "VS").
- **Decorative / non-text elements.** Icons, divider lines, badges, emojis, hand-lettering, sticky-note props.
- **Branded vs structural elements.** This is the key column. For everything you've described, mark each piece as `[BRAND]` (will become a variable) or `[STRUCTURE]` (stays literal in the template).
- **Chrome to strip.** Anything you saw that's a screenshot/platform artifact. Note it for explicit exclusion in the prompt.

State this analysis to the user as a compact summary. Don't move on until it's complete.

### Phase 3: Draft v1 prompt (faithful, brand-specifics intact)

Write a prompt that, paired with the reference image as `--image-ref`, would reproduce the ad faithfully. At this stage, leave brand-specific content **literal** — do not placeholder-ize yet.

Structure the prompt with these sections (omit any that don't apply):
- Aspect ratio + canvas (e.g. "1:1 static ad creative, 1080x1080, edge-to-edge")
- Background description
- Header section (top X% of the image)
- Main content / hero section
- Decorative elements (badges, dividers)
- Bottom section / footer band
- Typography note (weight, family-feel, hierarchy)
- Composition / spacing rules
- **Explicit chrome exclusion** — name what NOT to render (the script's no-chrome suffix is a safety net; the prompt should also explicitly exclude)

Show the v1 prompt to the user.

### Phase 4: Generate with reference (model-specific)

Use the matching `generate_image.py` to fire one generation. Pass the original reference as `--image-ref` and the matched aspect ratio.

```bash
<path-to>/generate_image.py \
  --prompt "$(cat /tmp/v1.prompt)" \
  --aspect-ratio <matched_ratio> \
  --image-ref <reference_path> \
  --out iterations/clone-tmp \
  --env-file .env \n  --confirm
```

(Write the prompt to a temp file to avoid shell-quoting hell.) Wait for completion. Read the generated image.

### Phase 5: Compare and iterate

Show user the original side-by-side description with the generated. Identify deltas:
- Layout regions misplaced or missing
- Typography weight wrong
- Wrong aspect ratio interpretation
- Brand color drifted
- Decorative elements (icons, badges) wrong or missing

Refine the prompt based on the deltas. Regenerate. Repeat until the structure is faithful enough to call it "good." **Cap at 4 iterations** — beyond that, the prompt has a structural problem and needs more dramatic editing rather than tweaking.

### Phase 6: Generalize into placeholders

This is where the template becomes reusable. Walk back through the v1 prompt and replace every `[BRAND]`-marked element from Phase 2 with a `{placeholder}` variable. Use the standard placeholder vocabulary:

**Standard variables** (use these names where they fit):
- `{brand.name}` — wordmark text
- `{brand.color_primary}` — primary brand color hex (e.g. `#1A4731`)
- `{brand.color_accent}` — secondary accent color hex (if used)
- `{brand.product_image_description}` — one-line description of the product visible in the ad
- `{brand.tagline}` — short brand promise
- `{brand.competitor_category}` — for comparison templates: what's being compared against
- `{ad.headline}` — top-line headline copy
- `{ad.subcopy}` — sub-headline / supporting copy
- `{ad.body}` — primary text block
- `{ad.cta_phrase}` — CTA button text

**Template-specific variables** — name them clearly when needed:
- `{checklist_items[]}` (Notes-style)
- `{tweet_body}` (story templates)
- `{rows[]}` (comparison templates)
- `{publication}` (editorial templates)
- `{ugc_subject}` (UGC photo composite templates)

For each variable: write a 1-line description of what it represents and what kind of value goes in it.

### Phase 7: Test the generalized template (model-specific)

Pick a different brand (default AG1 if assets exist; otherwise ask). Substitute test values into every placeholder. Generate again with `--image-ref` set to the test brand's product photo (NOT the original ad). The output should:
1. Have the same layout/composition as the original
2. Show the test brand instead of the source brand
3. Read as a coherent ad, not a frankenstein

If the test fails, the structure breaks under different brand assumptions — return to Phase 6 and refine the placeholder set. Often the fix is making a placeholder that was missed (e.g. you hardcoded a font feel that's specific to one brand).

### Phase 8: Cross-model validation (optional but recommended)

If time permits, run the same template through the **other** model (if you cloned with chatgpt, also test on nano-banana — and vice versa). Note the deltas in your `Model notes` block:

```markdown
**Model notes:**
- **gpt-image-2:** {what works, what struggles, e.g. "clean — strong on the table text"}
- **nano-banana:** {what works, what struggles, e.g. "table text blurs at small row height — bump row count down or use gpt-image-2"}
```

If you only validated against one model, say so explicitly:

```markdown
**Model notes:**
- **gpt-image-2:** validated clean (see iteration path)
- **nano-banana:** untested — validate before using on this backend
```

### Phase 9: Document the template

Compose the library entry. Use the format in [template-format.md](../../image-ad-prompting/prompting/template-format.md).

The entry must include:
- **Tag and one-line title** (e.g. `T40 — Lifestyle hero with overlay text`)
- **When to use** — 1-2 sentences on positioning fit
- **Aspect ratio** recommendation
- **Reference image guidance** — what kind of `--image-ref` to pass when reusing this template
- **Variable schema** — every `{placeholder}` with a 1-line description
- **Template prompt** in a fenced code block, ready to copy-paste-fill
- **Example fill** — the test fill from Phase 7, showing the variables substituted
- **Model notes** — gpt-image-2 + nano-banana behavior (from Phase 8)
- **Validated example path** — pointer to the iteration dir

### Phase 10: Save and confirm

1. Append the entry to the configured library file. If overwriting an existing tag, ask first.
2. Print the entry's path so the user can review.
3. Move the validated PNGs from `iterations/clone-tmp/` to a permanent dir keyed by the template tag (e.g. `iterations/clone-2026-05-25/T40/`).
4. Tell the user the template is now available for use by `chatgpt-image-ad` AND `nano-banana-image-ad` (subject to the model notes' recommendation).

## Naming convention for new templates

If the save target already has T1–T39 (the seeded templates), continue with T40, T41, … Use semantic suffixes if helpful: `T40 — Lifestyle hero`, `T41 — Carousel cover`. Keep the `T<n>` part for cross-skill referencing.

## Out of scope

- **Generating real ads / uploading to Meta.** Different skill in your stack. This skill produces templates only.
- **Reverse-engineering video ads.** Image only. Refuse with: *"This skill is for static image ads. Video reverse-engineering isn't supported in this version."*
- **Multi-template extraction in one run.** One reference → one template per skill invocation. If the user has 5 references, do 5 sequential runs (or batch via the same flow once you've done one).
- **Modifying existing templates in the library.** If the user wants to revise T3, treat it as a new run pointed at the same library entry — show the diff and ask before overwriting.

## Files this skill writes to (in user space)

- The configured prompt library (default: `shared/skills/image-ad-prompting/prompting/prompt-library.md`) — appended, never silently overwritten
- `<cwd>/iterations/clone-<date>/<tag>/prompt.txt` — the final validated prompt
- `<cwd>/iterations/clone-<date>/<tag>/v1.png`, `v2.png`, … — each iteration's output

## Dependencies

- The matching companion skill (`chatgpt-image-ad` or `nano-banana-image-ad`) must be installed in the same per-API repo (this skill uses its `generate_image.py` for iteration). If not installed, fail Phase 1 with a clear instruction.
- The per-API credentials the companion needs (`ARCADS_*` or `KIE_API_KEY`).
- Python 3.12+.
