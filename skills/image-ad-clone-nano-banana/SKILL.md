---
name: image-ad-clone-nano-banana
description: >-
  Reverse-engineer an existing image ad into a reusable, parameterizable prompt template validated against Nano Banana (Gemini Flash Image family) via the Arcads external API. Appends the new template to the shared image-ad prompt library so it's reusable by chatgpt-image-ad and nano-banana-image-ad. Triggers on phrases like "clone this ad as a template for nano banana", "reverse engineer this ad with Gemini", "extract a nano-banana template", "add this ad to the nano-banana library", "make this ad reusable on Gemini Image". Anchors on input being an EXISTING ad image AND nano-banana as the validation backend — does NOT trigger for fresh generation requests (use nano-banana-image-ad for that) or gpt-image-2 validation (use image-ad-clone-chatgpt for that).
---

# image-ad-clone-nano-banana (Arcads)

Take an existing image ad and turn it into a reusable, parameterizable prompt template, **validated by round-tripping through `nano-banana-image-ad`'s generator** (default `nano-banana-2`) on the Arcads external API. Output: a new entry appended to the shared prompt library, with `Model notes` explicitly recording Nano Banana behavior on the template.

This is the **template-creation** skill for Nano Banana. The companion skill `nano-banana-image-ad` is the **template-using** skill (it generates ads from filled-in templates).

For the parallel skill that validates against ChatGPT Image 2 instead, see `image-ad-clone-chatgpt`.

## Read order

1. **This file** — the Nano Banana-specific validation loop.
2. **[shared/skills/image-ad-clone/prompting/guide.md](../../shared/skills/image-ad-clone/prompting/guide.md)** — full model-agnostic 10-phase workflow.
3. **[shared/skills/image-ad-prompting/prompting/template-format.md](../../shared/skills/image-ad-prompting/prompting/template-format.md)** — entry skeleton.
4. **[shared/skills/image-ad-prompting/prompting/prompt-library.md](../../shared/skills/image-ad-prompting/prompting/prompt-library.md)** — destination for the new entry.

## Hard rules

Inherits all 6 from the shared guide. Plus one model-specific:

7. **Validation is via Nano Banana** (`nano-banana-2` by default; bump to `nano-banana-pro` if Gemini-2.5-Flash-Image can't lock the structure after 2 iterations and the template is high-stakes). If even `nano-banana-pro` can't reproduce the structure after 4 iterations, the entry's `Model notes` MUST say `nano-banana: weak` and recommend `image-ad-clone-chatgpt` for that template.

## Dependencies

- The `nano-banana-image-ad` skill must be installed in this repo (this skill uses its `scripts/generate_image.py` for iteration).
- `.env` with `ARCADS_BASIC_AUTH` or `ARCADS_API_KEY`.
- Python 3.12+.

## Where this skill's generator lives

When the [shared guide](../../shared/skills/image-ad-clone/prompting/guide.md) Phase 1 tells you to locate the companion generator, look here in this order:

1. `~/.claude/skills/nano-banana-image-ad/scripts/generate_image.py`
2. `<repo>/skills/nano-banana-image-ad/scripts/generate_image.py`
3. If neither: stop and ask the user to install `nano-banana-image-ad` first.

## Aspect ratio mapping

Nano Banana supports the full Meta ratio set: `{1:1, 4:5, 5:4, 2:3, 3:2, 9:16, 16:9, 3:4, 4:3, 21:9}`. When measuring the original ad's aspect (Phase 2), use the exact ratio whenever possible:
- `4:5` ad → `4:5` (Nano Banana renders this natively — preserve it)
- `1.91:1` ad → closest is `16:9`; document the small re-flow
- Most other ratios map 1:1

## Model variant to validate with

Default: `nano-banana-2`. Use `--model nano-banana-pro` for the validation runs when:
- The template needs high character identity continuity (multi-run consistency).
- Material-realism is core (claymation, Pixar, premium product photography).
- You're cloning a hero-format ad that will see heavy reuse.

`nano-banana-pro` costs more credits per run; surface this in the Phase 4 cost confirmation.

## Model notes you'll write at Phase 9

Every template entry created by this skill should include this block (substituting actual findings):

```markdown
**Model notes:**
- **gpt-image-2:** {if cross-tested in Phase 8: actual finding. If not: "untested — validate before using on chatgpt-image-ad backend"}
- **nano-banana:** {observed behavior — e.g. "strong — preferred backend for handheld board photos", "tends to render text in held signs as garbled — keep board text under 6 words", "character identity drifts across variants on -2; use -pro to lock"}
```

Be specific about which Nano Banana variant you validated against (`-2`, `-pro`, `-edit`). If you only tested `-2`, say so explicitly.

## Iteration directory layout

```
<cwd>/iterations/clone-2026-05-25/
  T41-letter-board/
    prompt.txt
    v1.png, v2.png, …                # against the source ref
    test-fill-v1.png, …              # Phase 7 generalization test
    cross-chatgpt-v1.png             # Phase 8 cross-test
    notes.md
```

## Cross-skill validation (Phase 8) — strongly recommended

Run the same template through `chatgpt-image-ad/scripts/generate_image.py` if it's installed:

```bash
~/.claude/skills/chatgpt-image-ad/scripts/generate_image.py \
  --prompt "$(cat iterations/clone-2026-05-25/T41-letter-board/prompt.txt)" \
  --aspect-ratio <gpt-image-2-compatible-ratio> \
  --image-ref <test-brand-product.png> \
  --out iterations/clone-2026-05-25/T41-letter-board/cross-chatgpt \
  --env-file .env
```

If the gpt-image-2-compatible ratio differs from the Nano Banana one (e.g. you used `4:5` for nano-banana, gpt-image-2 needs `2:3`), document the mismatch in `Model notes`. Read the cross-result and write the `gpt-image-2:` note.

## See also

- **[shared/skills/image-ad-clone/prompting/guide.md](../../shared/skills/image-ad-clone/prompting/guide.md)** — full workflow
- **[nano-banana-image-ad skill](../nano-banana-image-ad/SKILL.md)** — the generator this skill uses
- **[image-ad-clone-chatgpt skill](../image-ad-clone-chatgpt/SKILL.md)** — sibling skill that validates against gpt-image-2
