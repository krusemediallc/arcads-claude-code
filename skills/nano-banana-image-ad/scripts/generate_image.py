#!/usr/bin/env python3
"""
Generate one or more standalone Meta ad creatives with the Nano Banana model family
through Arcads (default) or Atlas Cloud (opt-in). Supported variants are
nano-banana-2 (default), nano-banana-pro, nano-banana, and nano-banana-edit.

Brand contract: this script refuses any model outside the Nano Banana family. The
sibling `chatgpt-image-ad/scripts/generate_image.py` handles ChatGPT Image 2.

Modes:
  --mode image       (default) text-to-image, optionally with --image-ref references
                     for style/subject/character grounding. Up to 14 refs.
  --mode image_edit  edits a --source image (required) using --prompt; --image-ref
                     is optional. Output dimensions track the source.

Output contract:
  stdout: one JSON object per successfully generated variant, one per line
  stderr: human-readable progress + errors
  exit:   0 if at least one variant succeeded; 1 if all failed; 2 on bad args.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

BASE_URL_DEFAULT = "https://external-api.arcads.ai"
ATLAS_BASE_URL_DEFAULT = "https://api.atlascloud.ai/api/v1"
ALLOWED_PROVIDERS = {"arcads", "atlas"}
ALLOWED_RATIOS = {"1:1", "16:9", "9:16"}  # Arcads /v2/images/generate cap (applies to all models on this endpoint)
ALLOWED_MODES = {"image", "image_edit"}
ALLOWED_MODELS = {"nano-banana-2", "nano-banana-pro", "nano-banana", "nano-banana-edit"}
DEFAULT_MODEL = "nano-banana-2"
POLL_INTERVAL_S = 3
POLL_TIMEOUT_S = 240
MIN_DIMENSION = 1024
MAX_REFS = 14  # Arcads cap for Nano Banana family
ATLAS_MODEL_PREFIXES = {
    "nano-banana-2": "google/nano-banana-2",
    "nano-banana-pro": "google/nano-banana-pro",
    "nano-banana": "google/nano-banana",
    "nano-banana-edit": "google/nano-banana",
}

NO_CHROME_SUFFIX = (
    "\n\n[NO PLATFORM CHROME] Render only the standalone ad creative (the static image uploaded to Meta), "
    "not a screenshot of how it displays in-feed. Exclude: iOS device chrome (status bar, home indicator); "
    "platform brand-row above the ad (avatar + handle + Sponsored / Saved label); post body / caption text; "
    "link-card footer (URL + headline + button); engagement rows (likes / comments / shares counts, "
    "Followed-by, View comments); action buttons (Like / Comment / Share / Save); comment input boxes; "
    "platform tab/nav bars (Instagram, Facebook, Twitter); Story chrome (progress bars, story header, "
    "swipe-up arrows). Just the standalone image."
)

SAFE_ZONE_SUFFIX = (
    "\n\n[EDGE-SAFE] All text, headlines, CTAs, table headers, sign/board content, product wordmarks, and "
    "key focal subjects must fit within the central 84% of the canvas (~8% padding from every edge). "
    "Backgrounds and divider lines may bleed; text and focal elements may NOT touch or extend off any edge. "
    "If a tall focal subject doesn't fit at the requested aspect ratio, scale it DOWN — never crop a "
    "headline, never let text run off-frame, never cut off the top/bottom of a sign, board, or product."
)

GLYPH_SAFETY_SUFFIX = (
    "\n\n[TEXT FIDELITY] Inside body-text blocks (chat bubbles, message threads, comment text, ChatGPT "
    "responses, dense paragraphs): plain words only — NO emoji, NO unicode glyphs, NO special characters "
    "mid-sentence. Emoji OK in headlines and short large-text positions where the prompt explicitly calls "
    "for them. Render the EXACT count of conversation elements the prompt specifies — do not invent "
    "additional comments, messages, replies, or responses."
)

MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def load_env(env_path: Path) -> dict:
    if not env_path.exists():
        raise SystemExit(f"error: .env not found at {env_path}")
    out: dict[str, str] = {}
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def auth_header(env: dict) -> str:
    basic = env.get("ARCADS_BASIC_AUTH") or os.environ.get("ARCADS_BASIC_AUTH")
    if basic:
        return basic if basic.startswith("Basic ") else f"Basic {basic}"
    key = env.get("ARCADS_API_KEY") or os.environ.get("ARCADS_API_KEY")
    if not key:
        raise SystemExit(
            "error: neither ARCADS_BASIC_AUTH nor ARCADS_API_KEY set in .env (or shell environment)"
        )
    import base64

    encoded = base64.b64encode(f"{key}:".encode()).decode()
    return f"Basic {encoded}"


def atlas_auth_header(env: dict) -> str:
    key = env.get("ATLASCLOUD_API_KEY") or os.environ.get("ATLASCLOUD_API_KEY")
    if not key:
        raise SystemExit("error: ATLASCLOUD_API_KEY is not set in .env or the shell environment")
    return f"Bearer {key}"


def slugify(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len] or "image"


def http_post_json(url: str, headers: dict, body: dict, timeout: int = 60) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} on {url}: {err_body}") from e


def http_get_json(url: str, headers: dict, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} on {url}: {err_body}") from e


def http_put_file(presigned_url: str, file_path: Path, mime: str, timeout: int = 120) -> None:
    data = file_path.read_bytes()
    req = urllib.request.Request(presigned_url, data=data, method="PUT", headers={"Content-Type": mime})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status >= 300:
            raise RuntimeError(f"presigned PUT failed: HTTP {resp.status}")


def http_download(url: str, dest: Path, timeout: int = 120) -> None:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as out:
        while chunk := resp.read(64 * 1024):
            out.write(chunk)


def atlas_upload(local_path: Path, base_url: str, auth_hdr: str) -> str:
    """Upload one local reference to Atlas Cloud and return its temporary URL."""
    if not local_path.exists():
        raise SystemExit(f"error: image not found: {local_path}")
    mime = MEDIA_TYPES.get(local_path.suffix.lower())
    if not mime:
        raise SystemExit(
            f"error: unsupported image extension '{local_path.suffix}' for {local_path}. "
            f"Supported: {sorted(MEDIA_TYPES)}"
        )

    boundary = f"----arcads-skill-{int(time.time() * 1000)}-{os.getpid()}"
    filename = local_path.name.replace('"', "_").replace("\r", "_").replace("\n", "_")
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode("utf-8") + local_path.read_bytes() + f"\r\n--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/model/uploadMedia",
        data=body,
        method="POST",
        headers={
            "Authorization": auth_hdr,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "arcads-claude-code/atlas-provider",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Atlas upload failed (HTTP {e.code}): {err_body}") from e

    data = payload.get("data", payload)
    url = data.get("download_url") if isinstance(data, dict) else None
    if not url:
        raise RuntimeError(f"Atlas upload response missing download_url: {payload}")
    return url


def atlas_model(model: str, has_images: bool) -> str:
    prefix = ATLAS_MODEL_PREFIXES[model]
    return f"{prefix}/{'edit' if has_images else 'text-to-image'}"


def atlas_submit(
    prompt: str,
    model: str,
    aspect_ratio: str | None,
    image_urls: list[str],
    base_url: str,
    auth_hdr: str,
    allow_chrome: bool = False,
    no_safe_zone: bool = False,
) -> str:
    """Submit one paid Atlas generation request. This function never retries POST."""
    final_prompt = prompt
    if not allow_chrome:
        final_prompt += NO_CHROME_SUFFIX
    if not no_safe_zone:
        final_prompt += SAFE_ZONE_SUFFIX
    final_prompt += GLYPH_SAFETY_SUFFIX

    body: dict = {
        "model": atlas_model(model, bool(image_urls)),
        "prompt": final_prompt,
        "resolution": "1k",
        "output_format": "png",
    }
    if aspect_ratio:
        body["aspect_ratio"] = aspect_ratio
    if image_urls:
        body["images"] = image_urls

    payload = http_post_json(
        f"{base_url}/model/generateImage",
        {
            "Authorization": auth_hdr,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "arcads-claude-code/atlas-provider",
        },
        body,
        timeout=120,
    )
    if payload.get("code") not in (None, 0, 200):
        raise RuntimeError(f"Atlas generation rejected: {payload}")
    data = payload.get("data", payload)
    prediction_id = data.get("id") if isinstance(data, dict) else None
    if not prediction_id:
        raise RuntimeError(f"Atlas generation returned no prediction id: {payload}")
    return prediction_id


def atlas_get_prediction(prediction_id: str, base_url: str, auth_hdr: str) -> dict:
    """Get one Atlas prediction state with bounded transient GET retries."""
    url = f"{base_url}/model/prediction/{urllib.parse.quote(prediction_id, safe='')}"
    headers = {
        "Authorization": auth_hdr,
        "Accept": "application/json",
        "User-Agent": "arcads-claude-code/atlas-provider",
    }
    for attempt in range(3):
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            if payload.get("code") not in (None, 0, 200):
                raise RuntimeError(f"Atlas prediction rejected: {payload}")
            data = payload.get("data", payload)
            if not isinstance(data, dict):
                raise RuntimeError(f"Atlas prediction response is malformed: {payload}")
            return data
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500:
                err_body = e.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"Atlas prediction failed (HTTP {e.code}): {err_body}") from e
            if attempt == 2:
                raise RuntimeError(f"Atlas prediction GET failed after 3 attempts: HTTP {e.code}") from e
        except urllib.error.URLError as e:
            if attempt == 2:
                raise RuntimeError(f"Atlas prediction GET failed after 3 attempts: {e}") from e
        if attempt < 2:
            time.sleep(2 ** attempt)
    raise RuntimeError("Atlas prediction GET failed after bounded retries")


def atlas_poll(prediction_id: str, base_url: str, auth_hdr: str) -> str:
    deadline = time.monotonic() + POLL_TIMEOUT_S
    last_status = None
    while time.monotonic() < deadline:
        prediction = atlas_get_prediction(prediction_id, base_url, auth_hdr)
        status = str(prediction.get("status", "")).lower()
        if status != last_status:
            log(f"  [{prediction_id[:8]}] status={status}")
            last_status = status
        if status == "completed":
            outputs = prediction.get("outputs") or []
            if not outputs:
                raise RuntimeError(f"Atlas prediction completed without outputs: {prediction}")
            return outputs[0]
        if status == "failed":
            raise RuntimeError(f"Atlas generation failed: {prediction}")
        time.sleep(POLL_INTERVAL_S)
    raise TimeoutError(f"Atlas prediction {prediction_id} did not complete in {POLL_TIMEOUT_S}s")


def probe_dimensions(path: Path) -> tuple[int, int]:
    """Return (width, height) for a PNG/JPEG/WebP using stdlib only — cross-platform.

    Reads the file header bytes directly so we don't need ImageMagick, sips
    (macOS), or Pillow. Returns (0, 0) on any error.
    """
    try:
        with path.open("rb") as f:
            header = f.read(32)
        if len(header) < 24:
            return 0, 0
        if header[:8] == b"\x89PNG\r\n\x1a\n" and header[12:16] == b"IHDR":
            w = int.from_bytes(header[16:20], "big")
            h = int.from_bytes(header[20:24], "big")
            return w, h
        if header[:2] == b"\xff\xd8":
            with path.open("rb") as f:
                data = f.read()
            i = 2
            while i < len(data) - 8:
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xD8, 0xD9):
                    i += 2
                    continue
                if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                    h = int.from_bytes(data[i + 5:i + 7], "big")
                    w = int.from_bytes(data[i + 7:i + 9], "big")
                    return w, h
                seg_len = int.from_bytes(data[i + 2:i + 4], "big")
                i += 2 + seg_len
            return 0, 0
        if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
            chunk = header[12:16]
            if chunk == b"VP8X" and len(header) >= 30:
                w = int.from_bytes(header[24:27], "little") + 1
                h = int.from_bytes(header[27:30], "little") + 1
                return w, h
            if chunk == b"VP8 ":
                with path.open("rb") as f:
                    data = f.read(40)
                if len(data) >= 30:
                    w = int.from_bytes(data[26:28], "little") & 0x3FFF
                    h = int.from_bytes(data[28:30], "little") & 0x3FFF
                    return w, h
            if chunk == b"VP8L":
                with path.open("rb") as f:
                    data = f.read(25)
                if len(data) >= 25 and data[20] == 0x2F:
                    b0, b1, b2, b3 = data[21], data[22], data[23], data[24]
                    w = ((b1 & 0x3F) << 8 | b0) + 1
                    h = ((b3 & 0x0F) << 10 | b2 << 2 | (b1 >> 6)) + 1
                    return w, h
        return 0, 0
    except Exception as e:  # noqa: BLE001
        log(f"warn: could not probe dimensions for {path}: {e}")
        return 0, 0


def fetch_default_product(base_url: str, auth_hdr: str) -> str | None:
    """If PRODUCT_ID not set, fetch the first product from Arcads and use that."""
    headers = {"Authorization": auth_hdr, "Accept": "application/json"}
    try:
        resp = http_get_json(f"{base_url}/v1/products", headers)
    except Exception as e:  # noqa: BLE001
        log(f"warn: could not list Arcads products to auto-pick productId: {e}")
        return None
    items = resp.get("items") if isinstance(resp, dict) else resp
    if isinstance(items, list) and items:
        first = items[0]
        pid = first.get("id")
        name = first.get("name") or "(unnamed)"
        log(
            f"info: PRODUCT_ID not set; using first Arcads product '{name}' ({pid}). "
            f"Set PRODUCT_ID=<id> in .env to lock this in."
        )
        return pid
    return None


def upload_reference(local_path: Path, base_url: str, auth_hdr: str) -> str:
    if not local_path.exists():
        raise SystemExit(f"error: image not found: {local_path}")
    mime = MEDIA_TYPES.get(local_path.suffix.lower())
    if not mime:
        raise SystemExit(
            f"error: unsupported image extension '{local_path.suffix}' for {local_path}. "
            f"Supported: {sorted(MEDIA_TYPES)}"
        )
    headers = {
        "Authorization": auth_hdr,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    resp = http_post_json(
        f"{base_url}/v1/file-upload/get-presigned-url", headers, {"fileType": mime}
    )
    presigned = resp.get("presignedUrl")
    file_path = resp.get("filePath")
    if not presigned or not file_path:
        raise RuntimeError(f"presigned-url response missing fields: {resp}")
    http_put_file(presigned, local_path, mime)
    return file_path


def submit(
    prompt: str,
    model: str,
    mode: str,
    aspect_ratio: str | None,
    source_filepath: str | None,
    ref_filepaths: list[str],
    product_id: str | None,
    project_id: str | None,
    base_url: str,
    auth_hdr: str,
    allow_chrome: bool = False,
    no_safe_zone: bool = False,
) -> str:
    final_prompt = prompt
    if not allow_chrome:
        final_prompt += NO_CHROME_SUFFIX
    if not no_safe_zone:
        final_prompt += SAFE_ZONE_SUFFIX
    final_prompt += GLYPH_SAFETY_SUFFIX

    body: dict = {"model": model, "prompt": final_prompt}
    if product_id:
        body["productId"] = product_id
    if project_id:
        body["projectId"] = project_id
    if mode == "image":
        if not aspect_ratio:
            raise ValueError("aspect_ratio required for mode=image")
        body["aspectRatio"] = aspect_ratio
    elif mode == "image_edit":
        if not source_filepath:
            raise ValueError("source filePath required for mode=image_edit")
        body["source"] = source_filepath
    if ref_filepaths:
        body["referenceImages"] = ref_filepaths

    headers = {
        "Authorization": auth_hdr,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    resp = http_post_json(f"{base_url}/v2/images/generate", headers, body)
    asset_id = resp.get("id")
    if not asset_id:
        raise RuntimeError(f"submit returned no id: {resp}")
    return asset_id


def poll(asset_id: str, base_url: str, auth_hdr: str) -> str:
    headers = {"Authorization": auth_hdr, "Accept": "application/json"}
    deadline = time.monotonic() + POLL_TIMEOUT_S
    last_status = None
    while time.monotonic() < deadline:
        resp = http_get_json(f"{base_url}/v1/assets/{asset_id}", headers)
        status = resp.get("status")
        if status != last_status:
            log(f"  [{asset_id[:8]}] status={status}")
            last_status = status
        if status == "generated":
            url = resp.get("url") or resp.get("imageUrl") or resp.get("assetUrl")
            if not url:
                for key in ("output", "result", "data"):
                    nested = resp.get(key)
                    if isinstance(nested, dict):
                        url = nested.get("url") or nested.get("imageUrl")
                        if url:
                            break
                    if isinstance(nested, list) and nested and isinstance(nested[0], dict):
                        url = nested[0].get("url")
                        if url:
                            break
            if not url:
                raise RuntimeError(f"generated but no url in response: {resp}")
            return url
        if status in {"failed", "error", "rejected"}:
            err = resp.get("error") or resp.get("failureReason") or resp.get("message")
            raise RuntimeError(f"generation failed: {err} (full: {resp})")
        time.sleep(POLL_INTERVAL_S)
    raise TimeoutError(f"asset {asset_id} did not complete in {POLL_TIMEOUT_S}s")


def generate_one(
    variant: int,
    prompt: str,
    model: str,
    mode: str,
    aspect_ratio: str | None,
    source_local: Path | None,
    ref_locals: list[Path],
    out_dir: Path,
    slug: str,
    ts: str,
    base_url: str,
    auth_hdr: str,
    product_id: str | None,
    project_id: str | None,
    allow_chrome: bool,
    no_safe_zone: bool,
    provider: str = "arcads",
) -> dict:
    log(f"variant {variant}: uploading refs ({len(ref_locals)}) via {provider}…")
    if provider == "atlas":
        image_urls = [atlas_upload(p, base_url, auth_hdr) for p in ref_locals]
        if source_local:
            image_urls.insert(0, atlas_upload(source_local, base_url, auth_hdr))
        log(f"variant {variant}: submitting once (provider=atlas, model={model}, mode={mode})…")
        asset_id = atlas_submit(
            prompt, model, aspect_ratio, image_urls, base_url, auth_hdr,
            allow_chrome=allow_chrome, no_safe_zone=no_safe_zone,
        )
        url = atlas_poll(asset_id, base_url, auth_hdr)
    else:
        ref_filepaths = [upload_reference(p, base_url, auth_hdr) for p in ref_locals]
        source_filepath = upload_reference(source_local, base_url, auth_hdr) if source_local else None
        log(f"variant {variant}: submitting (provider=arcads, model={model}, mode={mode})…")
        asset_id = submit(
            prompt, model, mode, aspect_ratio, source_filepath, ref_filepaths,
            product_id, project_id, base_url, auth_hdr,
            allow_chrome=allow_chrome, no_safe_zone=no_safe_zone,
        )
        url = poll(asset_id, base_url, auth_hdr)
    log(f"variant {variant}: id={asset_id}")
    dest = out_dir / f"{ts}-{slug}-v{variant}.png"
    log(f"variant {variant}: downloading -> {dest.name}")
    http_download(url, dest)
    w, h = probe_dimensions(dest)
    if w and h and (w < MIN_DIMENSION or h < MIN_DIMENSION):
        log(
            f"variant {variant}: WARNING image is {w}x{h}, below {MIN_DIMENSION}x{MIN_DIMENSION} "
            f"floor. Regenerate or upscale."
        )
    return {
        "variant": variant,
        "path": str(dest),
        "asset_id": asset_id,
        "width": w,
        "height": h,
        "prompt": prompt,
        "mode": mode,
        "aspect_ratio": aspect_ratio,
        "model": model,
        "provider": provider,
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description="Generate Nano Banana image(s) via Arcads or Atlas Cloud. Defaults to Arcads.",
    )
    p.add_argument("--prompt", required=True, help="Image prompt (post-rewrite).")
    p.add_argument(
        "--mode", default="image", choices=sorted(ALLOWED_MODES),
        help="image (default) or image_edit (modify --source).",
    )
    p.add_argument(
        "--aspect-ratio", choices=sorted(ALLOWED_RATIOS),
        help="Required for --mode image. Ignored for --mode image_edit.",
    )
    p.add_argument("--n", type=int, default=1, help="Variant count, 1-5.")
    p.add_argument(
        "--out", type=Path, default=Path("./generated"),
        help="Output directory for PNGs.",
    )
    p.add_argument(
        "--image-ref", type=Path, action="append", default=[], metavar="PATH",
        help=(
            f"Reference image path. Repeatable, max {MAX_REFS}. "
            "Used for style/subject/character grounding."
        ),
    )
    p.add_argument(
        "--source", type=Path, metavar="PATH",
        help="Source image to edit. Required for --mode image_edit.",
    )
    p.add_argument(
        "--model", default=DEFAULT_MODEL, choices=sorted(ALLOWED_MODELS),
        help=(
            f"Nano Banana variant. Default {DEFAULT_MODEL}. "
            "nano-banana-pro is Gemini 3 Pro Image (higher cost, locks identity); "
            "nano-banana-edit is inpaint-focused; nano-banana is the legacy variant."
        ),
    )
    p.add_argument(
        "--env-file", type=Path, default=Path(".env"),
        help="Path to .env (default: ./.env).",
    )
    p.add_argument(
        "--provider", default="arcads", choices=sorted(ALLOWED_PROVIDERS),
        help="Generation provider. Default: arcads; atlas is opt-in.",
    )
    p.add_argument("--product-id", help="Arcads productId (defaults to PRODUCT_ID env / .env).")
    p.add_argument("--project-id", help="Arcads projectId (defaults to PROJECT_ID env / .env).")
    p.add_argument(
        "--base-url", default=None,
        help="Provider API base URL override.",
    )
    p.add_argument("--allow-chrome", action="store_true",
                   help="Allow platform/screenshot UI in the output.")
    p.add_argument("--no-safe-zone", action="store_true",
                   help="Skip the edge-safe suffix.")
    args = p.parse_args()

    if args.model not in ALLOWED_MODELS:
        log(f"error: --model must be one of {sorted(ALLOWED_MODELS)}; got '{args.model}'")
        return 2

    if not (1 <= args.n <= 5):
        log(f"error: --n must be 1..5 (got {args.n})")
        return 2

    if len(args.image_ref) > MAX_REFS:
        log(f"error: too many --image-ref ({len(args.image_ref)}); Nano Banana cap is {MAX_REFS}")
        return 2

    atlas_image_count = len(args.image_ref) + (1 if args.source else 0)
    if args.provider == "atlas" and atlas_image_count > MAX_REFS:
        log(
            f"error: Atlas Cloud accepts at most {MAX_REFS} total source/reference images "
            f"(got {atlas_image_count})"
        )
        return 2

    if args.mode == "image":
        if args.source is not None:
            log("error: --source is not allowed with --mode image. "
                "Use --image-ref for guidance, or switch to --mode image_edit.")
            return 2
        if not args.aspect_ratio:
            log("error: --aspect-ratio is required for --mode image. "
                f"Choose one of {sorted(ALLOWED_RATIOS)}.")
            return 2
    elif args.mode == "image_edit":
        if args.source is None:
            log("error: --source is required for --mode image_edit.")
            return 2
        if args.aspect_ratio:
            log("warn: --aspect-ratio is ignored for --mode image_edit "
                "(output dimensions track the source).")

    env = load_env(args.env_file) if args.env_file.exists() else {}
    if args.provider == "atlas":
        auth_hdr = atlas_auth_header(env)
        base_url = (
            args.base_url
            or env.get("ATLASCLOUD_BASE_URL")
            or os.environ.get("ATLASCLOUD_BASE_URL")
            or ATLAS_BASE_URL_DEFAULT
        )
    else:
        if not args.env_file.exists() and not (
            os.environ.get("ARCADS_BASIC_AUTH") or os.environ.get("ARCADS_API_KEY")
        ):
            log(f"error: .env not found at {args.env_file}")
            return 2
        auth_hdr = auth_header(env)
        base_url = (
            args.base_url
            or env.get("ARCADS_BASE_URL")
            or os.environ.get("ARCADS_BASE_URL")
            or BASE_URL_DEFAULT
        )
    product_id = args.product_id or env.get("PRODUCT_ID") or os.environ.get("PRODUCT_ID")
    project_id = args.project_id or env.get("PROJECT_ID") or os.environ.get("PROJECT_ID")
    if args.provider == "arcads" and not product_id:
        product_id = fetch_default_product(base_url, auth_hdr)
        if not product_id:
            log("error: PRODUCT_ID not set in .env and Arcads has no products yet. "
                "Create one at https://app.arcads.ai/ first.")
            return 2

    args.out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = slugify(args.prompt)

    aspect = args.aspect_ratio if args.mode == "image" else None
    chrome_state = "allowed" if args.allow_chrome else "stripped"
    log(
        f"generating {args.n} variant(s) provider={args.provider} model={args.model} mode={args.mode} "
        f"{'aspect=' + aspect if aspect else 'aspect=from-source'} "
        f"chrome={chrome_state} refs={len(args.image_ref)} -> {args.out}/"
    )

    results: list[dict] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=args.n) as ex:
        futures = {
            ex.submit(
                generate_one, i, args.prompt, args.model, args.mode, aspect,
                args.source, list(args.image_ref), args.out, slug, ts,
                base_url, auth_hdr, product_id, project_id,
                args.allow_chrome, args.no_safe_zone,
                args.provider,
            ): i
            for i in range(1, args.n + 1)
        }
        for fut in as_completed(futures):
            i = futures[fut]
            try:
                results.append(fut.result())
            except Exception as e:  # noqa: BLE001
                errors.append(f"variant {i}: {e}")
                log(f"variant {i}: FAILED — {e}")

    results.sort(key=lambda r: r["variant"])
    for r in results:
        print(json.dumps(r), flush=True)

    if not results:
        log(f"all {args.n} variant(s) failed")
        return 1
    if errors:
        log(f"{len(results)}/{args.n} succeeded, {len(errors)} failed")
    else:
        log(f"all {args.n} variant(s) succeeded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
