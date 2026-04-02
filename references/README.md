# Reference images

Drop reference images here for the agent to use when generating Nano Banana stills, Veo 3.1 start frames, and other Arcads outputs. The agent checks this folder automatically.

## Folder structure

### `influencers/`
Photos of people whose look you want to recreate in AI-generated content.
- Face shots, full body, different angles
- The agent uses these as `refImageAsBase64` in the influencer recreation workflow
- Tip: name files descriptively (e.g., `sarah-headshot-natural-light.jpg`)

### `products/`
Product photos for showcase videos and product hero images.
- Different angles, packaging, in-use shots, flat lays
- The agent uses these as `refImageAsBase64` in the product showcase workflow
- Tip: clean backgrounds (white/neutral) produce the best results

### `aesthetics/`
Mood boards, lighting references, color palettes, style inspiration.
- The agent uses these as `referenceImages` (style/mood, not literal reproduction)
- Screenshots from ads you like, color swatches, composition examples

## Supported formats

JPEG, PNG, WebP. The agent auto-converts and upscales images below 1024px before sending to the API.

## Privacy

This folder is gitignored — your images stay local and are never committed to the repo.
