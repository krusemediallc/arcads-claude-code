# nano-banana-image-ad — model-specific prompting guide

This guide is the brain for the **`nano-banana-image-ad`** skill — generating standalone Meta ad creatives with **Nano Banana** (Google's Gemini Flash Image family: `nano-banana-2`, `nano-banana-pro`, `nano-banana-edit`).

For the shared template library and entry format, see:
- [shared/skills/image-ad-prompting/prompting/prompt-library.md](../../image-ad-prompting/prompting/prompt-library.md) — 30+ validated templates
- [shared/skills/image-ad-prompting/prompting/template-format.md](../../image-ad-prompting/prompting/template-format.md) — how to write a new entry
- [shared/skills/image-ad-prompting/prompting/safety-suffixes.md](../../image-ad-prompting/prompting/safety-suffixes.md) — the 3 always-on prompt guards

## What `nano-banana` is good at

Pick this skill (over `chatgpt-image-ad`) when the ad's success depends on any of these:

- **Photoreal handheld objects** — held-up whiteboard signs, hand-lettered cardboard, handwritten napkin notes, sticky-note + product flatlays, letter-board signs. Nano Banana renders held-paper texture, marker bleed, and hand-shadow naturalism better than gpt-image-2.
- **Aspirational lifestyle photography** — full-bleed scenic backgrounds (sunset coastline, mountain trail, kitchen at golden hour) with naturalistic lighting and shallow DOF.
- **Multi-image reference blending** — Nano Banana accepts up to 14 reference images and blends them more smoothly (logo + product + style board + character + setting in one composition).
- **Subject continuity across multiple runs** — pass a hero portrait as `--image-ref` across N generations and the character stays consistent.
- **Rich material rendering** — leather, metal, fabric, foil, glass, liquid, plasticine. Anywhere the brief says "photoreal" or "tactile".
- **Stop-motion / claymation / Pixar-adjacent aesthetics** — the Gemini-3-Pro variant (`nano-banana-pro` on KIE, `nano-banana` on Arcads) handles material-based realism that gpt-image-2 flattens.

## What `nano-banana` struggles with

If any of these are core to the ad, **prefer `chatgpt-image-ad` instead**:

- **Dense small body text** — chat bubbles, ChatGPT-response panels, table rows, calendar blocks, Slack messages, comment threads, search results pages. Letters blur or rearrange at small size.
- **UI mimicry of specific platforms** — iOS Messages chrome, Slack window proportions, Google search result layout. The aesthetic is "close enough" but not pixel-faithful.
- **Brand wordmark fidelity** — text wordmarks (FORBES, the exact "AG1" font weight) can drift if not passed as `--image-ref`.
- **Condensed-sans / brutalist typography hero quotes** — letter-spacing and condensed letterforms shift run-to-run.
- **Crossword grids, AirDrop dialogs, fake comment threads** — anything where small-text fidelity inside a rectangular UI element is the whole gag.

## Hard limits

These come from the upstream API contracts:

1. **Model is `nano-banana-2` (default), `nano-banana-pro`, or `nano-banana-edit`.** The script defaults to `nano-banana-2` and refuses unrelated model strings (no `gpt-image-2`, no `dall-e-3`). You can opt into `nano-banana-pro` (Gemini 3 Pro Image) per-run for higher-stakes hero shots — it costs more credits.
2. **Max 14 reference images** on Arcads (`referenceImages` array). KIE's `input.image_input` also caps at 14 URLs per task. The script enforces this.
3. **No platform/screenshot chrome in output.** `NO_CHROME_SUFFIX` is always on (unless `--allow-chrome`).
4. **Edge-safe rule always on.** Text and focal subjects must sit inside the central 84% of the canvas.
5. **Glyph-safety rule always on.** Plain words inside body-text blocks; emoji OK in headlines.

## Aspect ratios supported (per backend)

Brokers expose different aspect-ratio enums. **Live-validated 2026-05-25:**

| Ratio | Arcads `/v2/images/generate` | KIE `/api/v1/jobs/createTask` (nano-banana-2) |
|---|---|---|
| `1:1` | ✅ | ✅ |
| `16:9` | ✅ | ✅ |
| `9:16` | ✅ | ✅ |
| `4:5` | ❌ | ✅ (preferred for Meta feed-portrait) |
| `5:4` | ❌ | ✅ |
| `2:3` | ❌ | ✅ |
| `3:2` | ❌ | ✅ |
| `3:4`, `4:3`, `21:9` | ❌ | ✅ |

**On Arcads** — only `1:1`, `16:9`, `9:16` are accepted by the image-generation endpoint. Templates that need `2:3`, `4:5`, etc. need to fall back to `1:1` and post-crop.

**On KIE** — the full Meta ratio set is supported. **Default to `4:5` for Meta feed-portrait** — Nano Banana renders it natively.

## Model choice within Nano Banana family

The skill defaults to `nano-banana-2`. Override per-run with `--model nano-banana-pro` for:
- Hero stills you'll spend significant downstream production on (Seedance video, OOH placement).
- Character / influencer continuity work — the Pro variant locks identity tighter across reference batches.
- Material-realism critical shots (claymation, Pixar, premium product photography).

For `image_edit` mode, use `--model nano-banana-edit` (inpaint-focused variant on KIE; Arcads serves edits through the same endpoint with a `source` field).

The script refuses any model string outside `{nano-banana-2, nano-banana-pro, nano-banana-edit}` — `nano-banana` (legacy) is allowed only via explicit `--model nano-banana`.

## Workflow phases (`nano-banana-image-ad`)

This skill produces *images* — not Meta ads. Meta-side uploading is handled by a separate skill in your stack.

### Phase 1: Preflight

Verify in this exact order; bail on the first failure with a fix-it message.

1. The current working directory has a `.env` file with the credentials the per-API repo's `SKILL.md` requires.
2. If running from a per-API repo: confirm the API health check the SKILL.md specifies passes.
3. Read `~/.claude/skills/nano-banana-image-ad/state.json` if it exists.

### Phase 2: Gather inputs

| Input | Source | Notes |
|---|---|---|
| Seed prompt | User | Creative direction in their words. You will rewrite it (see Phase 3). |
| Mode | User or inferred | `image` (default) or `image_edit` (modify a `--source`). |
| Source image (`--source`) | User | Required only for `image_edit`. |
| Reference image(s) (`--image-ref`) | User | Optional but strongly recommended. Up to **14** for Nano Banana. |
| Variant count `N` | User, default 1 | Cap at 5. |
| Aspect ratio | User | One of `1:1`, `4:5`, `5:4`, `2:3`, `3:2`, `9:16`, `16:9`, `3:4`, `4:3`, `21:9`. Reject anything else. Ignored in `image_edit` mode. |
| Model variant | Optional | `nano-banana-2` (default), `nano-banana-pro`, `nano-banana-edit`. |

### Phase 3: Prompt rewrite

**First check the prompt library** (`shared/skills/image-ad-prompting/prompting/prompt-library.md`).

#### 3a — Check the prompt library

If the user's seed prompt or brief maps onto an existing template:
1. Read the matching template's `Model notes` block — **only proceed if it says `nano-banana: clean` or "preferred backend" or "strong"**. If it says gpt-image-2 is strongly preferred, suggest switching skills.
2. Fill in the `{placeholder}` variables.
3. Use that as the rewritten prompt.

#### 3b — Fleshing out a fresh prompt (or filling a template)

When writing or completing a prompt, anchor on:

- Subject and pose
- **Lighting and time of day** — Nano Banana renders natural light beautifully; specify "golden hour through east-facing window," "diffuse overhead studio softbox," "harsh midday sun with crisp shadows."
- **Lens / framing** — "35mm shallow DOF," "macro extreme close-up," "wide environmental"
- Color palette / mood
- Composition
- **Negative space for text overlay** if the ad has body/headline copy
- **Reference roles** — name each `--image-ref` explicitly: "the product in image_ref[0]," "the lighting/mood from image_ref[1]," "the character/influencer from image_ref[2]." Nano Banana's multi-ref blending improves dramatically with named roles.
- **Material specifics** — "subsurface scattering on skin," "satin foil reflectivity," "knit fabric weave," "marker bleed at stroke edges." Nano Banana renders material distinctions; lean into them.
- **Standalone-creative scope** — never describe iOS chrome, Sponsored badges, engagement counts, or platform UI.
- **Avoid keyword-soup prompts** — Nano Banana responds better to one well-written paragraph than to a comma-separated keyword list.

Show the rewritten prompt to the user as one block. Tell them which template (if any) it's based on. Ask: "Use this, edit it, or start over?" Loop until approved.

### Phase 4: Generate

Run the helper script:

```bash
~/.claude/skills/nano-banana-image-ad/scripts/generate_image.py \
  --prompt "<rewritten>" \
  --aspect-ratio <ratio> \
  --n <N> \
  --image-ref <product.png> \
  [--image-ref <style-board.png>] \
  [--image-ref <character.png>] \
  --out ./generated \
  --env-file .env \n  --confirm

# For higher-stakes hero shots:
~/.claude/skills/nano-banana-image-ad/scripts/generate_image.py \
  --model nano-banana-pro \
  --prompt "<rewritten>" \
  --aspect-ratio <ratio> \
  --n <N> \
  --image-ref <product.png> \
  --out ./generated \
  --env-file .env \n  --confirm

# For an edit run:
~/.claude/skills/nano-banana-image-ad/scripts/generate_image.py \
  --mode image_edit \
  --model nano-banana-edit \
  --prompt "<edit-instruction>" \
  --source <existing.png> \
  [--image-ref <guidance.png>] \
  --n <N> \
  --out ./generated \
  --env-file .env \n  --confirm
```

Each line on stdout is JSON for one variant. Display the paths to the user.

### Phase 5: Confirm variants

Show all paths and ask: "Use all / use these specific ones / regenerate / cancel."

### Phase 6: Hand off

Selected variants are now ready for your Meta-ad-builder skill (the one you already have in your stack).

## Retry mode (when a variant fails the QA visual check)

Common nano-banana defects + their fix prompts:
- **Garbled small text** → If text is essential, switch to `chatgpt-image-ad`. Or scale the text block up to occupy ≥30% of the canvas and re-render.
- **Wordmark drift** → Pass the wordmark as `--image-ref` AND name it ("the brand wordmark from image_ref[0]"). For Gemini-3-Pro fidelity, use `--model nano-banana-pro`.
- **Wrong character identity** (multi-run continuity) → Pass the hero portrait as `--image-ref` in every run. For locked identity, use `--model nano-banana-pro`.
- **Extra fingers / wrong limb count** → Add explicit anatomy clause: "exactly two hands, five fingers each, anatomically correct arms, no extra limbs."

**Retry cap:** 2 regen attempts per variant (3 total). If defects remain, stop, show best attempt, ask user how to proceed.

## Out of scope — fail clearly

- **Meta upload** — different skill. This skill produces images only.
- **Ad copy writing** — different skill.
- **Video, carousel, DCO ads** — image only.
- **ChatGPT Image 2 / gpt-image-2 generation** — use `chatgpt-image-ad` instead.
- **Editing the prompt library** — use `image-ad-clone` to add new validated templates (it asks which backend to validate against, and routes accordingly).
