# chatgpt-image-ad — model-specific prompting guide

This guide is the brain for the **`chatgpt-image-ad`** skill — generating standalone Meta ad creatives with **ChatGPT Image 2** (`gpt-image-2`).

For the shared template library and entry format, see:
- [shared/skills/image-ad-prompting/prompting/prompt-library.md](../../image-ad-prompting/prompting/prompt-library.md) — 30+ validated templates
- [shared/skills/image-ad-prompting/prompting/template-format.md](../../image-ad-prompting/prompting/template-format.md) — how to write a new entry
- [shared/skills/image-ad-prompting/prompting/safety-suffixes.md](../../image-ad-prompting/prompting/safety-suffixes.md) — the 3 always-on prompt guards

## What `gpt-image-2` is good at

Pick this skill (over `nano-banana-image-ad`) when the ad's success depends on any of these:

- **Dense text fidelity** — table rows, chat bubbles, ChatGPT-response panels, comment threads, Slack messages, comparison tables, Apple Notes lists, weather/forecast UI, fake search results pages.
- **UI mimicry** — iOS dialogs, iMessage threads, AirDrop modals, Google search pages, Slack conversations, Apple Notes / Calendar / Weather, dating-app cards. ChatGPT Image 2 was trained extensively on these patterns and reproduces them faithfully.
- **Logo and wordmark legibility** — publication wordmarks (FORBES, WIRED, Vogue), brand wordmarks, small-caps subheads, monospace numbers.
- **Typography-led layouts** — brutalist big-statement hero quotes, magazine mastheads, editorial article heros, condensed-sans hero stats.
- **Diagrammatic layouts** — flowcharts, stacked-bar comparisons, calendar timelines, annotated callouts with arrows.

## What `gpt-image-2` struggles with

If any of these are core to the ad, **prefer `nano-banana-image-ad` instead**:

- **Photoreal handheld objects** — held-up whiteboard signs, handwritten napkin testimonials, flatlay product photography with rich material rendering (leather + metal + fabric textures next to each other).
- **Aspirational lifestyle photography** — full-bleed scenic backgrounds (sunset coastline, mountain trail, kitchen at golden hour) with naturalistic lighting.
- **Stop-motion / claymation / Pixar / clay textures** — anything that needs material-based realism.
- **Subject continuity across many references** — `nano-banana` supports up to 14 reference images on Arcads; `gpt-image-2` caps at **5 references** and tends to blend them less smoothly.

## Hard limits

These come from the upstream API contracts:

1. **Model is `gpt-image-2`.** The script refuses other model strings (`dall-e-3`, `gpt-image-1`, etc.). Lock matches the uni-1 brand-contract pattern: predictable model means predictable cost + behavior per run.
2. **Max 5 reference images** (Arcads, observed 2026-04-23 via `400 Max 5 reference image(s) allowed`). The script enforces this. If you need more refs, switch skills.
3. **No platform/screenshot chrome in output.** The `NO_CHROME_SUFFIX` is always on (unless you explicitly `--allow-chrome` for the rare UGC screen-recording aesthetic). Output is the standalone ad creative — the static image that gets uploaded.
4. **Edge-safe rule always on.** Text and focal subjects must sit inside the central 84% of the canvas. Backgrounds may bleed.
5. **Glyph-safety rule always on.** Plain words inside body-text blocks. Emoji OK in headlines.

## Aspect ratios supported (per backend)

Brokers expose different aspect-ratio enums on top of the underlying OpenAI image model. The shared library's templates use the full Meta-ad ratio set, but only a subset is renderable on each backend at native ratio. **Live-validated 2026-05-25:**

| Ratio | Arcads `/v2/images/generate` | KIE `/api/v1/gpt4o-image/generate` |
|---|---|---|
| `1:1` | ✅ | ✅ |
| `16:9` | ✅ | ❌ |
| `9:16` | ✅ | ❌ |
| `2:3` | ❌ | ✅ |
| `3:2` | ❌ | ✅ |
| `4:5`, `5:4`, etc. | ❌ | ❌ |

**Fallback strategy:** if your template wants a ratio your backend doesn't support, generate at the nearest supported ratio and post-crop in your downstream ad-builder skill. For Meta-feed-portrait (`4:5`) specifically, the cleanest path is to switch skills to `nano-banana-image-ad` (which supports `4:5` natively on KIE).

The script does not auto-crop — it returns what the API produced and warns via stderr if dimensions are below 1024 on either side.

## Workflow phases (`chatgpt-image-ad`)

This skill produces *images* — not Meta ads. Meta-side uploading is handled by a separate skill in your stack. The phases here cover input → prompt → generate → confirm. The Meta hand-off happens after Phase 5.

### Phase 1: Preflight

Verify in this exact order; bail on the first failure with a fix-it message.

1. The current working directory has a `.env` file with the credentials the per-API repo's `SKILL.md` requires (e.g. `ARCADS_BASIC_AUTH` or `ARCADS_API_KEY` for the Arcads version; `KIE_API_KEY` for the KIE version).
2. If running from a per-API repo: confirm the API health check the SKILL.md specifies passes (e.g. `curl -u "$ARCADS_API_KEY:" "$ARCADS_BASE_URL/v1/products"` returns 200).
3. Read `~/.claude/skills/chatgpt-image-ad/state.json` if it exists, for any cached defaults.

### Phase 2: Gather inputs

| Input | Source | Notes |
|---|---|---|
| Seed prompt | User | The creative direction in their words. You will rewrite it (see Phase 3). |
| Mode | User or inferred | `image` (default, text-to-image with optional refs) or `image_edit` (modify a `--source` image). |
| Source image (`--source`) | User | Required only for `image_edit`. |
| Reference image(s) (`--image-ref`) | User | Optional but **strongly recommended** when the ad features a specific product. Up to **5** for `gpt-image-2`. |
| Variant count `N` | User, default 1 | Cap at 5. |
| Aspect ratio | User | One of `1:1`, `2:3`, `3:2`, `9:16`, `16:9`. Reject anything else. Ignored in `image_edit` mode. |

### Phase 3: Prompt rewrite

**First check the prompt library** (`shared/skills/image-ad-prompting/prompting/prompt-library.md`). It has 30+ validated parameterizable templates with per-model notes.

#### 3a — Check the prompt library

If the user's seed prompt or brief maps onto an existing template, use it:
1. Read the matching template's `Model notes` block — **only proceed if it says `gpt-image-2: clean` or "preferred backend"**. If it says nano-banana is preferred, suggest switching skills.
2. Fill in the `{placeholder}` variables for the user's brand.
3. Use that as the rewritten prompt.

Tell the user which template you matched and why.

#### 3b — Fleshing out a fresh prompt (or filling a template)

When writing or completing a prompt, anchor on:

- Subject and pose
- Lighting and time of day
- Lens / framing
- Color palette / mood (pull from the brand's identity)
- Composition (rule of thirds, leading lines)
- **Negative space for text overlay** if the ad has body/headline copy
- **Reference roles** — if `--image-ref` is being used, name each reference's role explicitly in the prompt (e.g. "the product in image_ref[0]", "the lighting from image_ref[1]"). Multi-reference quality improves when each reference is labeled in the prompt.
- **Standalone-creative scope** — never describe iOS chrome, Sponsored badges, engagement counts, or platform UI. The script's no-chrome guard catches violations, but write the prompt as if the rule is on you.
- **gpt-image-2 strengths to lean on** — explicit typography (font weight + size feel), UI proportions ("iOS dialog with rounded corners ~24px"), small-text body content (treat lines as exact strings).

Show the rewritten prompt to the user as one block. Tell them which template (if any) it's based on. Ask: "Use this, edit it, or start over?" Loop until approved.

### Phase 4: Generate

Run the helper script (location depends on the per-API repo):

```bash
~/.claude/skills/chatgpt-image-ad/scripts/generate_image.py \
  --prompt "<rewritten>" \
  --aspect-ratio <ratio> \
  --n <N> \
  --image-ref <product.png> \
  [--image-ref <style-board.png>] \
  --out ./generated \
  --env-file .env \n  --confirm
```

For an edit run, switch to `--mode image_edit --source <path>`.

Each line on stdout is JSON for one variant (`variant`, `path`, `generation_id`, `width`, `height`). Display the paths to the user.

If any variant comes back below 1080×1080, regenerate it (the script logs a warning to stderr but still emits the JSON line). If all variants failed, stop and report the error from stderr.

### Phase 5: Confirm variants

Show all paths and ask: "Use all / use these specific ones / regenerate / cancel." One confirmation covers all selected variants.

### Phase 6: Hand off

The selected variants are now ready to be used by **your Meta-ad-builder skill** (the one you already have in your stack). The handoff is just a list of file paths; the ad-builder skill picks them up and does the cloning + copy-writing + upload.

If your ad-builder skill expects a specific output shape, write the variant paths to a known location (e.g. `./generated/run-<ts>.jsonl`) and tell the user the path so they can pipe it.

## Retry mode (when a variant fails the QA visual check)

If a variant has obvious defects (extra fingers, garbled text, wrong UI proportions, blurred wordmark), regenerate with a **revised prompt** that explicitly corrects the issue. Do NOT resend the same payload and expect a different outcome.

Common gpt-image-2 defects + their fix prompts:
- **Garbled small text** → "Render <specific text block> at LARGE size, occupying at least 25% of the canvas height. Plain English words only, no glyph artifacts."
- **Wrong text count** (e.g. asked for 3 Slack messages, got 4) → Explicit count, e.g. "EXACTLY THREE message rows, no fourth row, no scroll cutoff at the bottom."
- **Wordmark drift** → Pass the actual wordmark file as `--image-ref` AND name it in the prompt ("the brand wordmark from image_ref[0]").
- **UI proportion drift** (e.g. iOS dialog too small) → "The iOS dialog occupies the central 70% of the canvas width."

**Retry cap:** 2 regeneration attempts per variant (3 total including the first). If defects remain after the cap, stop, show the best attempt, and ask the user how to proceed.

## Out of scope — fail clearly

- **Meta upload** — different skill. This skill produces images only.
- **Ad copy writing** — different skill.
- **Video, carousel, DCO ads** — image only.
- **Nano Banana / Gemini image generation** — use `nano-banana-image-ad` instead.
- **Editing the prompt library** — use `image-ad-clone` to add new validated templates (it asks which backend to validate against, and routes accordingly).
