---
name: image-ad-clone-chatgpt
description: >-
  Reverse-engineer an existing image ad into a reusable, parameterizable prompt template validated against ChatGPT Image 2 (gpt-image-2) via the Arcads external API. Appends the new template to the shared image-ad prompt library so it's reusable by chatgpt-image-ad and nano-banana-image-ad. Triggers on phrases like "clone this ad as a template for gpt-image-2", "reverse engineer this ad with ChatGPT Image", "extract a gpt-image-2 template", "add this ad to the chatgpt library", "make this ad reusable on gpt-image-2". Anchors on input being an EXISTING ad image AND gpt-image-2 as the validation backend — does NOT trigger for fresh generation requests (use chatgpt-image-ad for that) or nano-banana validation (use image-ad-clone-nano-banana for that).
---

# image-ad-clone-chatgpt (Arcads)

Take an existing image ad and turn it into a reusable, parameterizable prompt template, **validated by round-tripping through `chatgpt-image-ad`'s gpt-image-2 generator** on the Arcads external API. Output: a new entry appended to the shared prompt library, with `Model notes` explicitly recording gpt-image-2 behavior on the template.

This is the **template-creation** skill for ChatGPT Image 2. The companion skill `chatgpt-image-ad` is the **template-using** skill (it generates ads from filled-in templates). They're meant to be installed together.

For the parallel skill that validates against Nano Banana instead, see `image-ad-clone-nano-banana`.

## Read order

1. **This file** — the gpt-image-2-specific validation loop (Phases 1, 4, 7 are model-specific).
2. **[shared/skills/image-ad-clone/prompting/guide.md](../../shared/skills/image-ad-clone/prompting/guide.md)** — the full model-agnostic 10-phase workflow.
3. **[shared/skills/image-ad-prompting/prompting/template-format.md](../../shared/skills/image-ad-prompting/prompting/template-format.md)** — entry skeleton.
4. **[shared/skills/image-ad-prompting/prompting/prompt-library.md](../../shared/skills/image-ad-prompting/prompting/prompt-library.md)** — destination for the new entry.

## Hard rules

See [shared/skills/image-ad-clone/prompting/guide.md § Hard rules](../../shared/skills/image-ad-clone/prompting/guide.md). Inherits all 6. Plus one model-specific:

7. **Validation is via gpt-image-2.** This skill's job is to confirm the template renders cleanly on ChatGPT Image 2. If gpt-image-2 can't reproduce the structure after 4 iterations, the entry's `Model notes` MUST say `gpt-image-2: weak` or `gpt-image-2: unreliable — use nano-banana instead` and recommend the sibling skill.

## Dependencies

- The `chatgpt-image-ad` skill must be installed in this repo (this skill uses its `scripts/generate_image.py` for iteration).
- `.env` with `ARCADS_BASIC_AUTH` or `ARCADS_API_KEY`.
- Python 3.12+.

## Where this skill's generator lives

When the [shared guide](../../shared/skills/image-ad-clone/prompting/guide.md) Phase 1 tells you to locate the companion generator, look here in this order:

1. `~/.claude/skills/chatgpt-image-ad/scripts/generate_image.py`
2. `<repo>/skills/chatgpt-image-ad/scripts/generate_image.py`
3. If neither: stop and ask the user to install `chatgpt-image-ad` first.

## Aspect ratio mapping

gpt-image-2 supports `{1:1, 2:3, 3:2, 9:16, 16:9}`. When measuring the original ad's aspect (Phase 2), map to the nearest gpt-image-2 ratio:
- `4:5` ad → use `2:3` (slightly taller; document as a deliberate map)
- `1.91:1` ad → use `16:9`
- `5:4` ad → use `1:1` (small re-flow needed)

If the original requires a ratio that gpt-image-2 can't approximate well, recommend using `image-ad-clone-nano-banana` instead (Nano Banana supports the full Meta ratio set).

## Model notes you'll write at Phase 9

Every template entry created by this skill should include this block in its library entry (substituting actual findings):

```markdown
**Model notes:**
- **gpt-image-2:** {observed behavior — e.g. "clean — strong on UI mimicry and table text", "tends to add a 4th Slack message — keep prompt explicit about exactly N", "small chart axis labels blur — bump font size feel"}
- **nano-banana:** {if cross-tested in Phase 8: actual finding. If not: "untested — validate before using on nano-banana-image-ad backend"}
```

The diff between the uni-1 library and the new library is this `Model notes` block. Don't skip it.

## Iteration directory layout

```
<cwd>/iterations/clone-2026-05-25/
  T40-lifestyle-hero/
    prompt.txt                # final validated prompt
    v1.png, v2.png, …         # each iteration's output against the source ref
    test-fill-v1.png, …       # Phase 7 generalization test against a different brand
    notes.md                  # deltas observed + iteration log
```

Move outputs here after Phase 10 confirms.

## Cross-skill validation (Phase 8) — strongly recommended

Even though this skill ships templates as "validated for gpt-image-2," run Phase 8 cross-test against `nano-banana-image-ad` if it's installed. Most templates work on both with caveats; documenting the caveats is the whole point of `Model notes`.

To run the cross-test:

```bash
~/.claude/skills/nano-banana-image-ad/scripts/generate_image.py \
  --prompt "$(cat iterations/clone-2026-05-25/T40-lifestyle-hero/prompt.txt)" \
  --aspect-ratio <matched_ratio_for_nano_banana> \
  --image-ref <test-brand-product.png> \
  --out iterations/clone-2026-05-25/T40-lifestyle-hero/cross-nano-banana \
  --env-file .env
```

Read the cross-result image and write the `nano-banana:` note for the entry's Model notes block.

## See also

- **[shared/skills/image-ad-clone/prompting/guide.md](../../shared/skills/image-ad-clone/prompting/guide.md)** — full workflow
- **[chatgpt-image-ad skill](../chatgpt-image-ad/SKILL.md)** — the generator this skill uses
- **[image-ad-clone-nano-banana skill](../image-ad-clone-nano-banana/SKILL.md)** — sibling skill that validates against Nano Banana
