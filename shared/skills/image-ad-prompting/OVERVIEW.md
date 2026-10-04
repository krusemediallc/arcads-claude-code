# Image-ad ecosystem — overview for AI coding agents

**One-line summary:** four skills + one shared prompt library let you generate standalone Meta image-ad creatives with either ChatGPT Image 2 or Nano Banana (Gemini Flash Image), and reverse-engineer existing ads into reusable templates. Output is image files. Meta-side uploading is handled by a *separate* `meta-ad-builder` skill, not by these.

**Read this whole file** at the start of any session where the user mentions: making an ad, image creative, ad library, gpt-image-2, ChatGPT Image 2, Nano Banana, Gemini Image, cloning an ad, reverse-engineering an ad, or anything in the `T1–T39` template namespace.

---

## What's in the family

```
┌─────────────────────────────────────────────────────────────────┐
│ SHARED BRAIN (no SKILL.md — referenced by all 3 skills below)   │
│ shared/skills/image-ad-prompting/                               │
│   ├ prompting/prompt-library.md   37 validated templates        │
│   ├ prompting/template-format.md  entry-format skeleton         │
│   ├ prompting/safety-suffixes.md  3 always-on prompt guards     │
│   └ OVERVIEW.md                   this file                     │
├─────────────────────────────────────────────────────────────────┤
│ GENERATOR SKILLS (produce image files)                          │
│ skills/chatgpt-image-ad/         → gpt-image-2                  │
│ skills/nano-banana-image-ad/     → nano-banana-2 / -pro / -edit │
├─────────────────────────────────────────────────────────────────┤
│ TEMPLATE-CREATION SKILL (reverse-engineer an ad → library)      │
│ skills/image-ad-clone/   asks which backend, routes to matching │
│                          generator above. Single skill replaces │
│                          the older per-model clone variants.    │
└─────────────────────────────────────────────────────────────────┘
```

Each per-API repo (Arcads, KIE.ai) has all four skills. The skills look identical in name and CLI surface area, but the underlying scripts call different backends. **Live-validated 2026-05-25:**

| | Arcads (both chatgpt + nano-banana) | KIE chatgpt-image-ad | KIE nano-banana-image-ad |
|---|---|---|---|
| **Endpoint** | `POST /v2/images/generate` | `POST /api/v1/gpt4o-image/generate` (dedicated endpoint) | `POST /api/v1/jobs/createTask` |
| **Auth** | HTTP Basic (`ARCADS_BASIC_AUTH` or `ARCADS_API_KEY`) | Bearer (`KIE_API_KEY`) | Bearer (`KIE_API_KEY`) |
| **Reference images** | Local file paths → script uploads via presigned URL flow | Public URLs in `filesUrl[]` (max 5) | Public URLs in `input.image_input[]` (max 14) |
| **Polling** | `GET /v1/assets/{id}` until `status: generated` | `GET /api/v1/gpt4o-image/record-info?taskId=…` until `data.successFlag == 1` | `GET /api/v1/jobs/recordInfo?taskId=…` until `data.state == "success"` |
| **Required IDs** | `productId` (UUID; script auto-fetches first product if `PRODUCT_ID` not in env) + optional `projectId` | none | none |
| **CLI flag for refs** | `--image-ref <path.png>` | `--image-url <https://...>` | `--image-url <https://...>` |
| **Variants** | `--n 1..5` → N separate parallel requests | `--n {1, 2, 4}` → built-in batch in one request (nVariants) | `--n 1..5` → N separate parallel requests |
| **Aspect ratios** | `1:1`, `16:9`, `9:16` only | `1:1`, `3:2`, `2:3` only | full Meta set (`1:1`, `4:5`, `5:4`, `2:3`, `3:2`, `9:16`, `16:9`, `3:4`, `4:3`, `21:9`) |

See [prompting/prompt-library.md § Aspect-ratio compatibility](prompting/prompt-library.md) for the full ratio matrix and fallback strategy.

The shared brain (`shared/skills/image-ad-prompting/`) is identical across both repos.

---

## Decision tree — which skill to use

The user's first sentence usually tells you which way to branch.

**Step 1: Are they generating from scratch, or cloning an existing ad image?**

- **Generating** → one of the two generator skills.
- **Cloning** (they shared an ad image and want it as a reusable prompt) → the single `image-ad-clone` skill (it asks which backend to validate against at Phase 1).

**Step 2: Pick the model.**

Skim what the user wants and match it to model strengths:

| The user wants... | Pick |
|---|---|
| Apple Notes lists, fake search results, chat threads, ChatGPT-style conversations, iOS dialogs, Slack snapshots, comparison tables, Hinge cards, iMessage, calendar UI, weather forecast UI, magazine cover, anything **typography-heavy or UI-mimicry** | **`chatgpt-image-ad`** |
| Handheld whiteboard signs, napkin handwritten testimonials, sticky-note + product flatlays, letter-board signs, lifestyle scenes, OOH/transit photography, scratch-off tickets, **photoreal / material-rich / multi-reference** ads | **`nano-banana-image-ad`** |
| Ambiguous? | Look up the matching template in `prompting/prompt-library.md` and read its `Model notes:` block — every entry recommends one or the other. |

**Step 3: For cloning, the `image-ad-clone` skill handles both backends.** At Phase 1 it asks the user (or auto-detects from the reference's typography-vs-photo balance) whether to validate via `chatgpt-image-ad` or `nano-banana-image-ad`. It then routes through the matching generator's `scripts/generate_image.py`. Phase 8 of the workflow optionally cross-validates against the other backend so the resulting library entry has `Model notes:` for both.

The clone skill depends on at least one of the two generators being installed in the same repo. If neither is installed, install one first.

---

## The shared prompt library

`prompting/prompt-library.md` ships with **37 validated full prompts** (tags T1 through T39, with intentional gaps at T16/T22 from the source Uni1 lineage). Every entry has:

- **When to use** — positioning fit
- **Aspect ratio** — recommended canvas
- **Reference image** — what to pass via `--image-ref` / `--image-url`
- **Variables** — the placeholder schema
- **Template prompt** — the full validated AG1 prompt in a fenced code block (drop-in usable; swap brand-specifics per the Variables block)
- **Model notes** — `gpt-image-2:` and `nano-banana:` behavior on this template (which backend is preferred, where each struggles)

The library is **the first place to look** when the user describes an ad concept. Match their brief to a template, fill the variables, and ship — that's the fast path. The bespoke-prompt path (writing from scratch) is the fallback when nothing matches.

---

## Always-on safety suffixes

Every generator script auto-appends three guards to the prompt:

1. **`NO_CHROME_SUFFIX`** — strips iOS chrome, Sponsored badges, engagement rows, link-card footers, story chrome, tab bars. The output is the *standalone* image creative, not a screenshot of how it displays in-feed. Override with `--allow-chrome` only when the ad concept genuinely needs simulated platform chrome (rare).
2. **`SAFE_ZONE_SUFFIX`** — keeps text + focal subjects inside the central 84% of the canvas. Eliminates clipped headlines.
3. **`GLYPH_SAFETY_SUFFIX`** — forbids emoji and unicode glyphs inside body-text blocks (chat bubbles, comment threads, ChatGPT responses); enforces the exact count of conversation elements.

Full text in `prompting/safety-suffixes.md`. **Do not silently disable these** — they fix recurring rendering failures across every modern image model. If you need to disable one for a specific run, use `--allow-chrome` or `--no-safe-zone` flags and document why.

---

## Standard workflow — generate an ad from a brief

This is the workflow inside any chat session where the user wants to make an ad:

1. **Match to a library template.** Read `prompting/prompt-library.md`. If their brief maps onto an existing template, use it. If not, plan a fresh prompt.

2. **Pick the backend.** Read the template's `Model notes:`. If both work, default to `chatgpt-image-ad` for typography-heavy templates and `nano-banana-image-ad` for photoreal/lifestyle templates.

3. **Fill placeholders.** Swap `{brand.name}`, `{brand.color_primary}`, `{ad.headline}`, etc. with the user's brand. Show the rewritten prompt and ask for approval.

4. **Show the credit-cost estimate** per the per-API repo's existing conventions (read `logs/<api>-api.jsonl` or `MASTER_CONTEXT.md` for the rate). Wait for explicit confirmation.

5. **Generate.** Run the matching `scripts/generate_image.py` with `--prompt`, `--aspect-ratio`, `--n`, and reference images.
   The generator refuses to spend without `--confirm`; pass it only after the user approves the credit cost. `--dry-run` prints the billable plan and the exact request body without spending.

6. **Visual QA.** Read each output image. Check for: garbled small text (most common gpt-image-2 failure), extra fingers / wrong limb count (Nano Banana failure), wordmark drift, wrong text count, UI proportion drift. Regenerate with a revised prompt if defective (cap 2 retries).

7. **Hand off the image paths** to the user's separate `meta-ad-builder` skill — that's the skill that uploads to Meta, writes ad copy, clones page/ad-set/CTA, etc. The image-ad skills produce *images*, not *ads*.

---

## Standard workflow — clone an existing ad into a reusable template

Use the `image-ad-clone` skill (single backend-agnostic skill — Phase 1 asks which generator to validate against, Phase 8 optionally cross-validates against the other).

The 10-phase workflow lives in `shared/skills/image-ad-clone/prompting/guide.md`. Key checkpoints:

- **Phase 2 (visual analysis)** — describe the reference structurally, separating brand-specific content from format/structure.
- **Phase 4-5 (generate + iterate)** — round-trip the prompt through the matching generator until structure is faithful. Cap at 4 iterations.
- **Phase 6 (generalize)** — replace `[BRAND]`-marked elements with `{placeholder}` variables.
- **Phase 7 (test with different brand)** — fill placeholders for a different brand and regenerate. If structure breaks, refine the placeholder set.
- **Phase 8 (cross-model validation, optional)** — round-trip the same template through the *other* generator and document deltas in the `Model notes:` block.
- **Phase 9-10 (document + save)** — append a new T<n> entry to `prompting/prompt-library.md` with the required structure.

The library is append-only. New templates start at T40 (next available number after the seeded T1-T39).

---

## What this ecosystem does NOT do

Surface these limits clearly when the user asks for anything outside scope:

- **Meta upload.** Different skill — `meta-ad-builder` (in `shared/skills/meta-ad-builder/`). The image-ad skills produce image files; the ad-builder skill handles cloning page/ad-set/CTA, writing copy, and uploading as paused ads.
- **Ad copy writing.** Different skill (the user's `meta-ad-builder` or equivalent handles body/headline).
- **Video, carousel, DCO ads.** Image only.
- **Cross-backend in one run.** If the user wants gpt-image-2 AND nano-banana variants of the same prompt, run both skills sequentially. Each skill is locked to one model family.
- **Backends other than the per-API repo's configured one.** Arcads repo's skills call Arcads; KIE repo's skills call KIE. To use the other backend, open the other per-API repo.

---

## Files this ecosystem owns

In each per-API repo:

```
skills/
  chatgpt-image-ad/
    SKILL.md
    scripts/generate_image.py
  nano-banana-image-ad/
    SKILL.md
    scripts/generate_image.py
  image-ad-clone/
    SKILL.md

shared/skills/             ← propagated from gen-ai-core/content/skills/
  image-ad-prompting/      ← shared brain (this folder)
    OVERVIEW.md            ← this file
    prompting/
      prompt-library.md
      template-format.md
      safety-suffixes.md
  chatgpt-image-ad/
    prompting/guide.md
  nano-banana-image-ad/
    prompting/guide.md
  image-ad-clone/
    prompting/guide.md
```

The per-API SKILL.md files are repo-specific (different scripts for Arcads vs KIE). The `shared/skills/` content is identical across both repos.

---

## For human onboarding

If you're a human reading this for the first time:
- See [shared/skills/image-ad-prompting/prompting/prompt-library.md](prompting/prompt-library.md) for the 37 validated ad templates.
- See your repo-specific [chatgpt-image-ad/SKILL.md](../chatgpt-image-ad/SKILL.md) and [nano-banana-image-ad/SKILL.md](../nano-banana-image-ad/SKILL.md) for hands-on usage.
- The `image-ad-clone-*` skills are for *making new templates*, not generating ads — only invoke them when you want to add to the library.
