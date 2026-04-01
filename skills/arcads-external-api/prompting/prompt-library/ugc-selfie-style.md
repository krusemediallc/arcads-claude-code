# UGC selfie-style video — cross-model prompting guide

**Applies to:** Veo 3.1, Sora 2, Kling 3.0 (via Arcads scene / b-roll / direct model routes)  
**Aesthetic:** iPhone-shot, Instagram Reels, unpolished realism

Use this guide when the user wants **authentic-looking UGC** — selfie angles, handheld shake, imperfect lighting, casual speech. The biggest mistake is letting the AI produce polished cinematic output; UGC works because it feels real.

## Core principles (all models)

### 1. Camera physics — simulate a smartphone

Stop using "cinematic," "8k," or "award-winning." Instead:

- **Lens:** "iPhone 15 Pro front camera in selfie mode," "native wide lens (~26 mm)," "f/2.2 aperture"
- **Focus:** "Autofocus micro-pulses," "deep focus (everything sharp)," "no artificial blur"
- **Lighting:** "Unbalanced exposure," "slight overexposure in bright areas," "auto white balance with a slight blue cast"
- **Imperfections:** "Subtle edge distortion," "natural micro lens flare," "rolling-shutter micro-artifacts," "mild luminance grain"

### 2. "Accidental" composition

- "Awkward angle," "messy crop," "deliberately mediocre framing"
- "Unpolished casual home environment," "cluttered background"
- Avoid "centered framing" or "perfect composition"

### 3. Natural human motion

- **Selfie arm:** "Holding the camera at arm's length," "arm extended naturally, clearly visible in the frame"
- **Micro-expressions:** "Subtle head turns," "hair catching the light," "glancing off-camera before looking back at the lens"
- **Handheld feel:** "Handheld one-hand shot, slightly shaky," "quick handheld adjustments"

### 4. Negative prompting

Always exclude: "studio lighting, professional photography, stock photo, perfect skin, heavy makeup, centered framing, staged, cinematic, LUT, color graded, stabilization"

## Model-specific strategies

### Veo 3.1 — scene and shot designer

**Formula:** `[Camera] + [Subject] + [Action] + [Context/Lighting] + [Style/Imperfections] + [Dialogue/Audio]`

- Start with **"A selfie video of..."** to trigger correct framing
- Lock perspective with `(thats where the camera is)` syntax
- Add **"The image is slightly grainy, looks very film-like"** to fight Veo's clean default
- For multi-shot Reels, use timestamps: `[00:00-00:02] ... [00:02-00:04] ...`
- Sweet spot: **75–125 words**

**Example:**
```text
A selfie video of a 25-year-old woman in her messy apartment holding
the camera at arm's length (thats where the camera is). Her right arm
is clearly visible in the frame. Natural lighting from a large window
creates unbalanced, soft shadows. She is casually talking, occasionally
looking off-camera before looking directly into the lens with a
conspiratorial expression. The image is slightly grainy, documentary-
style handheld camera work, completely unedited vlog aesthetic.
Background sounds of city traffic. She speaks in a casual tone:
'Nobody talks about how productivity advice is just procrastination.'
No subtitles.
```

### Sora 2 — narrative director

**Formula:** Structure with headers: `Format & Style`, `Camera`, `Main Subject`, `Location`, `Lighting`, `Actions & Camera Beats`

- Break into **second-by-second beats** (`0-4s: [Action]`, `4-8s: [Action]`)
- Specify raw audio: "Raw phone audio: slight room echo, fridge hum, auto gain fluctuates with voice volume"
- Use "autofocus micro-pulses," "completely ungraded iPhone video," "flat colors"

**Example:**
```text
Format & Style: UGC reaction video – authentic, handheld, shot on
front iPhone camera. Style: unfiltered realism, slight overexposure.
Camera: iPhone 15 Pro front camera in selfie mode. Handheld one-hand
shot, slightly shaky with autofocus micro-pulses. No stabilization.
Main Subject: Late 20s male, oversized hoodie, messy hair.
Location: Plain kitchen, daylight spilling through blinds.
Lighting: Pure natural light from side window — unbalanced exposure.
Actions & Camera Beats (0-8s):
  0-4s — Subject lifts coffee cup close to camera, eyes wide.
         Focus flickers between face and cup.
  4-8s — Laughs, shakes head gently. Quick handheld adjustments.
Dialogue: "Guys, I swear this is the best thing I've ever tasted."
Sound: Raw phone audio, slight room echo, background hiss intact.
```

### Kling 3.0 — motion operator

**Formula:** Think physics engine: `[Environment] -> [Lighting] -> [Camera Movement] -> [Subject/Product Behavior]`

- **Describe physics:** Not "she turns her head" but "She turns her head slowly left to right. Her hair follows just behind, catches the light. Slight tension in her neck."
- **Anchor hands** to objects to avoid AI hand morphing: "holding a phone," "gripping a coffee cup"
- **Emphasize texture:** "Visible breath," "sweat," "fabric sheen," "condensation," "visible skin pores"
- Keep prompts **compact and operational** — trim poetic language

**Example:**
```text
Medium close-up mirror selfie. A Korean-American woman in a white
dressing room holding a phone. Handheld smartphone drift, subtle sway.
Natural overhead fluorescent lighting casting slight shadows. She looks
into the mirror, waves her hand casually. Motion details: natural
wrist rotation, fabric of her sleeve moves with the gesture. Texture:
visible skin pores, slight grain of phone camera. She speaks softly:
'Just testing this out. The details are crazy.' Tone is breathy and
impressed. Realistic facial motion, subtle eye blinks.
```

## Instagram Reels checklist (final pass)

- [ ] **Aspect ratio:** 9:16 specified
- [ ] **Hook:** First 2 seconds have dynamic motion or strong facial expression
- [ ] **Lighting:** "Natural," "window light," or "room lighting" — NOT "studio" or "cinematic"
- [ ] **Camera:** "iPhone front camera," "selfie-style," "handheld shake" stated
- [ ] **Flaws:** At least two imperfections included (grain, overexposure, focus hunting, messy background)

## References

- [iPhone selfie simulation prompts](https://createvision.ai/templates/community-hyper-realistic-iphone-17-pro-selfie-simulation-prompt-6647)
- [Sora 2 prompt guide](https://higgsfield.ai/sora-2-prompt-guide)
- [UGC AI prompting guide](https://adlibrary.com/guides/ai-prompting-guide-ugc-content-creators)
- [Kling 3.0 realistic motion](https://www.atlascloud.ai/blog/guides/mastering-kling-3.0-10-advanced-ai-video-prompts-for-realistic-human-motion)
- [Veo 3 prompting guide (GitHub)](https://github.com/snubroot/Veo-3-Prompting-Guide)
- [OpenAI Sora 2 cookbook](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide/)
- [Kling 3.0 prompting guide (fal.ai)](https://blog.fal.ai/kling-3-0-prompting-guide/)
