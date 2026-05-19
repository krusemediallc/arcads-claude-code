# Captioning a finished video — HyperFrames + Whisper + chroma-key workflow

**Use this skill when:** the user has a finished MP4 (claymation ad, Pixar ad, UGC selfie, B-roll, anything) with a narrator / dialogue / voiceover, and wants timed burned-in captions added without re-rendering the source.

Anchors on **HyperFrames** (HTML-based composition framework) + **Whisper** (word-level transcription) + **ffmpeg chroma-key compositing**. This pattern was tuned across multiple production runs — follow it exactly or expect the bugs listed below.

## Why not just use ffmpeg `subtitles` / `drawtext` directly?

You can, but only if your local ffmpeg was built with `libass` + `libfreetype`. **Homebrew's `ffmpeg` formula ships without them** — the filters are silently missing and `ffmpeg -vf subtitles=...` returns `No such filter`. The HyperFrames workflow below sidesteps that entirely by rendering captions in a real Chrome and compositing the result in.

It's also dramatically nicer for typography: real web fonts, real `text-stroke`, real GSAP animations per phrase, per-emphasis styling. PIL + drawtext can't match.

## The pipeline (5 steps)

### 1. Initialize a captioning project

Sit it alongside the source video, not inside it — keeps reruns clean.

```bash
cd path/to/<run-id>/                                    # the folder that already holds the final mp4
npx --yes hyperframes@0.6.26 init <run-id>-captions
cp final/<source-video>.mp4 <run-id>-captions/source.mp4
```

### 2. Transcribe with Whisper at the right model size

**The model choice matters.** Wrong model → drifty captions. Decision tree:

| Source audio | Model | Why |
|---|---|---|
| Pure speech, no music | `small.en` | Fast, accurate |
| **Speech mixed with background music (typical ad)** | **`medium.en`** | `small.en` biases word boundaries when music interferes — symptoms are per-word drift of 100-300ms |
| Multilingual | `medium` or `large-v3` (no `.en` suffix) | `.en` models *translate* non-English audio into English silently |
| Produced track with vocals + full instrumentation | `large-v3` or OpenAI/Groq API | Even `medium.en` may misalign |

```bash
npx --yes hyperframes@0.6.26 transcribe source.mp4 --model medium.en
```

Output is `transcript.json` — a flat array of `{text, start, end}` per word.

**Run the quality check** (mandatory per the hyperframes-media skill): grep for `♪`/`�` tokens. If >20% of entries are music notes or obvious nonsense words, retry with a larger model.

### 3. Group words into reading phrases

Word-by-word captions are exhausting to read. Group into 3-5 word phrases that break on punctuation. Use this helper (commit it as `build_groups.py` in the project):

```python
#!/usr/bin/env python3
"""transcript.json (word-level) → groups.json (reading phrases)."""
import json, re, pathlib

WORDS = json.load(open("transcript.json"))
MAX_CHARS = 22
MAX_WORDS = 5
MAX_GAP = 0.55   # force a new group if pause exceeds this

def is_sentence_end(t): return bool(re.search(r'[.!?](?:["\'\)\]])?$', t))
def is_clause_break(t): return bool(re.search(r'[,—:;](?:["\'\)\]])?$|\.\.\.$', t))

groups, cur, cur_chars, last_end = [], [], 0, 0.0
for w in WORDS:
    text = w["text"]
    if not text.strip(): continue
    gap = w["start"] - last_end if cur else 0
    candidate = cur_chars + (1 if cur else 0) + len(text)
    if cur and (candidate > MAX_CHARS and len(cur) >= 2 or len(cur) >= MAX_WORDS or gap >= MAX_GAP):
        groups.append(cur); cur, cur_chars = [], 0
    cur.append(w); cur_chars += len(text) + (1 if cur_chars else 0); last_end = w["end"]
    if is_sentence_end(text) or (is_clause_break(text) and len(cur) >= 2):
        groups.append(cur); cur, cur_chars = [], 0
if cur: groups.append(cur)

out = []
for g in groups:
    text = re.sub(r"\s+([,.;:!?])", r"\1", " ".join(w["text"] for w in g).strip())
    out.append({
        "text": text,
        "start": round(g[0]["start"], 2),
        "end": round(g[-1]["end"], 2),
        "emphasis": "normal",   # set per-group manually below if you want comedic/brand/product styling
    })
pathlib.Path("groups.json").write_text(json.dumps(out, indent=2))
print(f"{len(out)} groups → groups.json")
```

Then optionally hand-tag emphasis. Common emphasis classes:
- `normal` — default white text
- `comedic` — slightly larger, warm color, snappier ease
- `brand` — purple/pink, larger, used for brand name mentions
- `product` — pink/magenta, largest, used for pricing/quantity callouts
- `helen` (or other character name) — italic, alternate color, for dialogue spoken by characters in the video (vs. the narrator)

### 4. Write the composition

**CRITICAL: do NOT put `<video>` or `<audio>` elements in the composition.** HyperFrames wraps any `class="clip"` element in a managed timing wrapper that injects its own positioning/sizing styles, which **overrides any CSS you declare**. The wrapper for `<audio>` reserves an ~80 px layout block at the bottom of the stage, producing a hard black bar in the render. This bit us hard once — don't repeat it.

Instead: render captions over a **chroma-key magenta** (`#ff00ff`) background, composite the source video underneath in ffmpeg post.

Skeleton `index.html` (drop into the captioning project root):

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=720, height=1280" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@700;800;900&display=swap" rel="stylesheet">
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body {
        margin: 0; width: 720px; height: 1280px; overflow: hidden;
        /* Chroma-key magenta — keyed out by ffmpeg post-render. */
        background: #ff00ff;
        font-family: "Outfit", system-ui, sans-serif;
      }
      #stage { position: relative; width: 720px; height: 1280px; }
      #captions { position: absolute; inset: 0; z-index: 10; pointer-events: none; }
      .caption-group {
        position: absolute; left: 50%; transform: translateX(-50%);
        max-width: 660px; width: max-content; text-align: center;
        opacity: 0; visibility: hidden; will-change: transform, opacity;
      }
      .caption-group .line {
        display: inline-block; font-family: "Outfit", sans-serif;
        font-weight: 900; font-size: 54px; line-height: 1.1;
        color: #fff; text-transform: uppercase;
        -webkit-text-stroke: 6px #0e0a06; paint-order: stroke fill;
        text-shadow: 0 5px 14px rgba(0,0,0,.7), 0 2px 4px rgba(0,0,0,.9);
        white-space: pre-wrap;
      }
      .caption-group.emp-comedic .line { font-size: 60px; color: #ffe6a8; }
      .caption-group.emp-brand   .line { font-size: 56px; color: #f7d9ff; -webkit-text-stroke: 6px #3d1648; }
      .caption-group.emp-product .line { font-size: 62px; color: #ffd9f6; -webkit-text-stroke: 6px #3d1648; }
      .caption-group.emp-helen   .line { font-style: italic; font-size: 50px; color: #ffd6a8; -webkit-text-stroke: 5px #2a1808; }
    </style>
  </head>
  <body>
    <div id="stage" data-composition-id="main" data-start="0" data-duration="73.36" data-width="720" data-height="1280">
      <div id="captions"></div>
    </div>

    <script>
      /* GROUPS data — built from groups.json. Inline it here or load via fetch. */
      window.__GROUPS__ = __GROUPS_JSON_INLINE__;
    </script>

    <script>
      window.__timelines = window.__timelines || {};

      // Adjust Y positions per project — e.g. lift captions higher during a CTA window
      // to clear a burned-in overlay in the source video.
      const Y_DEFAULT = 940;   // ~73% from top, lower third
      const layer = document.getElementById("captions");
      window.__GROUPS__.forEach((g, gi) => {
        const wrap = document.createElement("div");
        wrap.className = "caption-group emp-" + (g.emphasis || "normal");
        wrap.id = "cg-" + gi;
        wrap.style.top = Y_DEFAULT + "px";
        const line = document.createElement("span");
        line.className = "line";
        line.textContent = g.text;
        wrap.appendChild(line);
        layer.appendChild(wrap);
      });

      const tl = gsap.timeline({ paused: true });
      // SNAPPY SYNC: caption appears AT whisper-reported start (no lead-in), animates
      // in over 60ms. Lead-in offsets cause perceptible drift — don't add them.
      window.__GROUPS__.forEach((g, gi) => {
        const el = document.getElementById("cg-" + gi);
        const inDur = 0.06, outDur = 0.08;
        const prevEnd = gi > 0 ? window.__GROUPS__[gi - 1].end : 0;
        const inStart = Math.max(prevEnd + 0.003, g.start);
        const outStart = Math.max(inStart + inDur + 0.02, g.end - outDur - 0.005);
        const ease = (g.emphasis === "comedic" || g.emphasis === "product" || g.emphasis === "brand") ? "back.out(1.3)" : "power2.out";
        tl.set(el, { visibility: "visible" }, inStart);
        tl.fromTo(el, { opacity: 0, scale: 0.97, y: 4 }, { opacity: 1, scale: 1, y: 0, duration: inDur, ease }, inStart);
        tl.to(el, { opacity: 0, scale: 0.96, y: -6, duration: outDur, ease: "power2.in" }, outStart);
        tl.set(el, { opacity: 0, visibility: "hidden" }, g.end);
      });
      tl.seek(0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
```

Replace `__GROUPS_JSON_INLINE__` with the contents of `groups.json` before rendering (read groups.json + string-substitute, or `fetch("groups.json")` at runtime).

Set `data-duration` on `#stage` to the actual source-video duration (use `ffprobe -v error -show_entries format=duration -of csv=p=0 source.mp4`).

### 5. Render + chroma-key composite

```bash
cd <run-id>-captions
npm run check                       # 0 errors / 0 warnings expected — the 1 contrast warning against magenta is fine and disappears post-key
npm run render                      # outputs renders/<project>_<timestamp>.mp4 — fast (~15s, ~2 MB) since it's flat magenta + text
```

Then composite:

```bash
ffmpeg -y \
  -i ../final/<source-video>.mp4 \
  -i renders/<latest-render>.mp4 \
  -filter_complex "[1:v]chromakey=0xff00ff:0.10:0.05[caps];[0:v][caps]overlay=0:0[vout]" \
  -map "[vout]" -map "0:a" \
  -c:v libx264 -preset medium -crf 18 -c:a copy -pix_fmt yuv420p \
  ../final/<source-video>-with-captions.mp4
```

`chromakey=0xff00ff:0.10:0.05` — first number is similarity (how close to magenta to key out), second is blend (edge softness). These values are tuned: 0.10/0.05 cleanly removes magenta without eating into the white text's stroke.

`-c:a copy` carries the source audio through untouched, so your narration + BGM + ducking mix from the source video is preserved.

## Common pitfalls (and the fixes)

| Symptom | Cause | Fix |
|---|---|---|
| **~80 px black bar at the bottom of the render** | `<audio>` or `<video>` with `class="clip"` in the composition — HyperFrames' wrapper reserves layout space | Remove those elements entirely; use the chroma-key composite-in-post pattern above |
| **Captions drift 100-300 ms per word** | Used `small.en` on audio with background music | Re-transcribe with `medium.en` |
| **Captions fire ~50-150 ms early** | GSAP `inStart` formula has a lead-in like `g.start - 0.05` | Use `g.start` directly. No lead-in. The animation duration (60 ms) is the only "anticipation" you need |
| **Captions feel laggy on the eye** | In-animation duration too long (140+ ms with `back.out`) | Drop to 60 ms with `power2.out` for normal text, `back.out(1.3)` only for emphasis |
| **`ffmpeg -vf subtitles=...` fails with "No such filter"** | Homebrew ffmpeg lacks libass | Don't use that filter — this whole skill is the alternative |
| **Pixel positions off by 1-2 px after chroma-key** | Source video resolution doesn't match composition `data-width`/`data-height` | They must match. Verify with `ffprobe -select_streams v:0 -show_entries stream=width,height` |
| **Captions visible during a burned-in CTA overlay window** | Caption Y position collides with overlay | Lift captions during that time range — e.g. `wrap.style.top = (g.start >= CTA_START ? Y_LIFTED : Y_DEFAULT) + "px"` |

## File layout convention

```
<run-id>/
├── final/
│   ├── <source-video>.mp4                       ← input
│   └── <source-video>-with-captions.mp4         ← output of step 5
└── <run-id>-captions/                           ← the hyperframes project
    ├── index.html
    ├── source.mp4
    ├── transcript.json                          ← whisper output
    ├── groups.json                              ← reading phrases
    ├── build_groups.py
    └── renders/                                 ← timestamped intermediate captions-over-magenta mp4s
```

## When NOT to use this skill

- **Captions need to drive video timing** (e.g. caption-reactive transitions, words synced to scene cuts) — use a more integrated HyperFrames composition that includes the video, accepting the layout caveat by carefully managing element wrappers.
- **Caller wants per-word ("kinetic") captions** — adapt step 3 to emit per-word groups instead of phrase groups; everything else stays the same.
- **Source has burned-in subtitles already** — don't double-caption; tell the user.

## Related skills

- [`claymation-ad`](../claymation-ad/prompting/guide.md) — produces the kind of source video this skill captions
- [`pixar-style-ad`](../pixar-style-ad/prompting/guide.md) — same
- Per-API SKILL.md (Arcads, KIE) — the upstream pipelines that produce the source videos
