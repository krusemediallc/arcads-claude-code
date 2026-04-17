# Creative brief playbook (kie.ai)

Use this **before** opening a model-specific file in `prompting/prompt-library/`.

## 1. Capture the marketing intent (ask the user)

- **Audience:** Who is this for? (one sentence)
- **Job to be done:** What should the viewer feel or do after watching?
- **Offer / proof:** Product name, one concrete benefit, optional social proof.
- **Hook:** First 1–2 seconds—pattern interrupt, curiosity, or relatable moment.
- **CTA:** Exact words if spoken or on-screen (e.g. "Shop the drop," "Book a demo").
- **Constraints:** Length, aspect ratio, banned topics, brand words to avoid.

## 2. Turn intent into a single coherent prompt

- Prefer **one paragraph** of clear direction over a bag of keywords.
- Name the **subject**, **setting**, **camera / motion**, **lighting**, **style**, and **audio mood** when the model supports audio (per vendor guide).
- If the user gave a vague adjective ("premium," "fun"), **translate** into visual specifics (materials, wardrobe, locations, pace).

## 3. Map the brief to kie.ai

1. Pick the **model slug and endpoint** using `SKILL.md` decision tree and [reference.md](../reference.md).
2. Open the matching **`prompting/prompt-library/*.md`** for **Sora 2**, **Veo 3.1**, **Kling 3.0**, **Seedance 2.0**, or **Nano Banana** and align wording with that vendor's guide (linked in each file).
3. Collect any **reference image URLs** (public HTTPS) the prompt will use — host local files first if the user only has file paths. See `SKILL.md` → "Reference images: hosting and public URLs".

## 4. Merge with project memory

If `MASTER_CONTEXT.md` (repo root) lists brand voice, banned phrases, or winning prompts, **prefer those** over generic templates.

## 5. Quality check before sending

- [ ] Required `input` fields present per [reference.md](../reference.md) for the chosen `model` slug.
- [ ] All reference URLs are HTTPS, publicly reachable, and point to direct media (not HTML pages).
- [ ] Prompt matches the **vendor guide style** for the chosen model.
- [ ] No secrets in the request body (only creative text and public URLs).
- [ ] User confirmed aspect ratio and duration where enums apply.
- [ ] User confirmed estimated cost (from `MASTER_CONTEXT.md` rate table).
