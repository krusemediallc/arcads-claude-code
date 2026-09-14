#!/usr/bin/env python3
"""
burn-overlays.py — burn the HYPERFOCUS text overlays (overlays.json) onto a rendered clip with ffmpeg.

Use this with the *no-text* prompt variant when you want deterministic, brand-clean typography
instead of model-rendered text (Seedance sometimes garbles on-screen words).

  python3 campaigns/hyperfocus-sparkling-focus-water/burn-overlays.py \
      --in outputs/seedance/<clip>.mp4 --out outputs/seedance/<clip>-titled.mp4

Options: --font /path/to/Bold.ttf   --overlays overlays.json   --ffmpeg /path/to/ffmpeg   --fade 0.15
Stdlib only. Needs an ffmpeg build with the drawtext filter (libfreetype): `brew install ffmpeg` on macOS,
`apt install ffmpeg` on Linux. The pip `imageio-ffmpeg` wheel does NOT include drawtext.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",       # macOS
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:/Windows/Fonts/arialbd.ttf",                              # Windows
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",     # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def has_drawtext(ffmpeg: str) -> bool:
    try:
        out = subprocess.run([ffmpeg, "-hide_banner", "-filters"], capture_output=True, text=True, timeout=30).stdout
    except Exception:  # noqa: BLE001
        return False
    return " drawtext " in out


def find_ffmpeg(explicit: str | None) -> str:
    candidates = [explicit] if explicit else []
    on_path = shutil.which("ffmpeg")
    if on_path:
        candidates.append(on_path)
    try:
        import imageio_ffmpeg  # type: ignore

        candidates.append(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:  # noqa: BLE001
        pass
    for cand in candidates:
        if cand and Path(cand).exists() and has_drawtext(cand):
            return cand
    if candidates:
        sys.exit("error: found ffmpeg but no build with the drawtext filter (the pip imageio-ffmpeg wheel lacks it). "
                 "Install a full build: brew install ffmpeg (macOS) / apt install ffmpeg (Linux), or pass --ffmpeg /path/to/ffmpeg.")
    sys.exit("error: ffmpeg not found. Install it: brew install ffmpeg (macOS) / apt install ffmpeg (Linux).")


def find_font(explicit: str | None) -> str:
    if explicit:
        if not Path(explicit).exists():
            sys.exit(f"error: font not found: {explicit}")
        return explicit
    for cand in FONT_CANDIDATES:
        if Path(cand).exists():
            return cand
    sys.exit("error: no bold font found; pass --font /path/to/Bold.ttf")


def probe_size(ffmpeg: str, src: Path) -> tuple[int, int]:
    """Read WxH from ffmpeg's stderr banner (avoids needing ffprobe)."""
    proc = subprocess.run([ffmpeg, "-hide_banner", "-i", str(src)], capture_output=True, text=True)
    import re

    m = re.search(r"Video:.*?\s(\d{2,5})x(\d{2,5})", proc.stderr)
    if not m:
        sys.exit(f"error: could not read video dimensions from {src}")
    return int(m.group(1)), int(m.group(2))


def ff_escape_path(p: str) -> str:
    # drawtext option values: escape backslashes, colons and single quotes.
    return p.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def main() -> int:
    ap = argparse.ArgumentParser(description="Burn overlays.json text onto a video with ffmpeg drawtext.")
    ap.add_argument("--in", dest="src", required=True, type=Path)
    ap.add_argument("--out", dest="dst", required=True, type=Path)
    ap.add_argument("--overlays", type=Path, default=HERE / "overlays.json")
    ap.add_argument("--font", default=None)
    ap.add_argument("--ffmpeg", default=None)
    ap.add_argument("--fade", type=float, default=0.15, help="fade in/out seconds per overlay")
    args = ap.parse_args()

    if not args.src.exists():
        sys.exit(f"error: input not found: {args.src}")
    ffmpeg = find_ffmpeg(args.ffmpeg)
    font = find_font(args.font)
    spec = json.loads(args.overlays.read_text())
    width, height = probe_size(ffmpeg, args.src)

    tmpdir = Path(tempfile.mkdtemp(prefix="hyperfocus-overlays-"))
    filters: list[str] = []
    fade = args.fade
    for ov in spec["overlays"]:
        textfile = tmpdir / f"{ov['id']}.txt"
        textfile.write_text(ov["text"])
        start, end = float(ov["start"]), float(ov["end"])
        size = max(12, int(width * float(ov["size_pct"])))
        y = int(height * float(ov["y_pct"]))
        alpha = (
            f"if(lt(t\\,{start + fade})\\,(t-{start})/{fade}\\,"
            f"if(gt(t\\,{end - fade})\\,({end}-t)/{fade}\\,1))"
        )
        filters.append(
            "drawtext="
            f"fontfile='{ff_escape_path(font)}':"
            f"textfile='{ff_escape_path(str(textfile))}':"
            f"fontsize={size}:fontcolor=white:"
            "line_spacing=8:text_align=center:"
            "x=(w-text_w)/2:"
            f"y={y}:"
            "shadowcolor=black@0.55:shadowx=3:shadowy=3:"
            f"alpha='{alpha}':"
            f"enable='between(t\\,{start}\\,{end})'"
        )
    vf = ",".join(filters)
    args.dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(args.src),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart",
        str(args.dst),
    ]
    print(f"burning {len(filters)} overlays ({width}x{height}) -> {args.dst}", file=sys.stderr)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        return 1
    print(str(args.dst))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
