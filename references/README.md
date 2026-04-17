# Reference images

Drop reference images here for the agent to use when generating Nano Banana stills, Veo 3.1 start frames, and other kie.ai outputs. The agent checks this folder automatically.

> **Important:** kie.ai requires **public HTTPS URLs** for reference images — it does not host your files. The agent will ask you to upload the image to your preferred host (Imgur / Supabase / R2 / etc.) before firing the API call. See `skills/kie-ai-external-api/SKILL.md` → "Reference images: hosting and public URLs".

## Folder structure

### `influencers/`
AI-generated character sheets — each influencer gets their own subfolder with 10 reference angles.

#### Folder naming convention

```
{name}-{descriptor1}-{descriptor2}-{descriptor3}-{descriptor4}-{descriptor5}
```

- **name:** A human first name (lowercase) — for easy reference in conversation
- **5 descriptors:** Visual architecture tags (lowercase, hyphenated) that identify the influencer at a glance

Descriptors should cover these categories in order:
1. **Hair color** — `redhead`, `blonde`, `brunette`, `black-hair`, `silver`
2. **Hair style** — `wavy`, `straight`, `curly`, `pixie`, `braided`
3. **Distinguishing feature** — `freckles`, `dimples`, `sharp-jaw`, `high-cheeks`, `beauty-mark`
4. **Eye color** — `green-eyes`, `blue-eyes`, `brown-eyes`, `hazel-eyes`
5. **Skin tone** — `fair`, `olive`, `tan`, `deep`, `medium`

**Examples:**
- `emma-redhead-wavy-freckles-green-eyes-fair/`
- `sofia-brunette-straight-dimples-brown-eyes-olive/`
- `kai-blonde-curly-sharp-jaw-blue-eyes-tan/`

#### File naming convention (inside each influencer folder)

```
01-hero-front.jpg      ← the approved anchor image (full body front)
02-3q-left.jpg
03-3q-right.jpg
04-profile-left.jpg
05-profile-right.jpg
06-face-closeup.jpg
07-back-shoulder.jpg
08-medium-portrait.jpg
09-full-body-3q.jpg
10-above-angle.jpg
```

The agent uses `01-hero-front.jpg` as the primary reference and can load all 10 as `image_input[]` (Nano Banana) or `reference_image_urls[]` (Seedance) for maximum consistency — after you host them at public HTTPS URLs.

### `products/`
Product photos for showcase videos and product hero images.
- Different angles, packaging, in-use shots, flat lays
- The agent uses these as `first_frame_url` (for image-to-video flows) or as entries in `image_input[]` (Nano Banana composition) — after you host them at public HTTPS URLs
- Tip: clean backgrounds (white/neutral) produce the best results

### `aesthetics/`
Style references organized into subfolders by vibe. The agent loads 3 images from the chosen style folder as `reference_image_urls[]` (Seedance) or `imageUrls[]` + `REFERENCE_2_VIDEO` (Veo) to influence generation style — after you host them at public HTTPS URLs.

#### `aesthetics/ugc-selfie/`
iPhone selfie-style UGC — raw, unpolished, authentic-looking frame grabs. Drop 3-5 reference images showing the target aesthetic: front-camera selfies, slightly grainy, imperfect lighting, casual environments.

#### Adding new styles
Create a new subfolder (e.g., `aesthetics/cinematic/`, `aesthetics/studio/`) and populate with 3-5 reference images. The agent will ask which style to use when generating.

### `examples/ugc-stills/`
5 example UGC product selfie outputs showing the target quality — character + product + scene with skin realism and camera imperfections baked in. Use these as a visual reference for what the UGC pipeline produces.

## Supported formats

JPEG, PNG, WebP. Shipped images are JPEG 85% for smaller repo size. For best results, upscale images below 1024px before hosting — on macOS: `sips -Z 1080 img.jpg`.

## Privacy

This folder is gitignored — your images stay local and are never committed to the repo.
