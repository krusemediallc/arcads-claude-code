#!/usr/bin/env python3
"""
Generate one or more standalone Meta ad creatives via Arcads' POST /v2/images/generate
with ChatGPT Image 2 (gpt-image-2).

Brand contract: this script REFUSES to use any model other than `gpt-image-2`. The
sibling `nano-banana-image-ad/scripts/generate_image.py` handles Nano Banana.

Modes:
  --mode image       (default) text-to-image, optionally with --image-ref references
                     for style/subject grounding.
  --mode image_edit  edits a --source image (required) using --prompt; --image-ref
                     is optional. Output dimensions track the source — --aspect-ratio
                     is ignored for this mode.

Output contract:
  stdout: one JSON object per successfully generated variant, one per line
          {"variant": int, "path": str, "asset_id": str,
           "width": int, "height": int, "prompt": str, "mode": str,
           "aspect_ratio": str|null, "model": str}
  stderr: human-readable progress + errors
  exit:   0 if at least one variant succeeded; 1 if all failed; 2 on bad args.

Stdlib only. No requests, no python-dotenv.
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
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

BASE_URL_DEFAULT = "https://external-api.arcads.ai"
ALLOWED_RATIOS = {"1:1", "16:9", "9:16"}  # Arcads /v2/images/generate cap
ALLOWED_MODES = {"image", "image_edit"}
LOCKED_MODEL = "gpt-image-2"
POLL_INTERVAL_S = 3
POLL_TIMEOUT_S = 240
MIN_DIMENSION = 1024
MAX_REFS = 5  # Arcads cap for gpt-image-2 (observed via 400 Max 5 reference image(s) allowed)

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
    """Parse a .env file into a dict. No external deps."""
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
    """Build the Authorization header value. Prefer ARCADS_BASIC_AUTH if set."""
    basic = env.get("ARCADS_BASIC_AUTH") or os.environ.get("ARCADS_BASIC_AUTH")
    if basic:
        # Already includes "Basic " prefix
        return basic if basic.startswith("Basic ") else f"Basic {basic}"
    key = env.get("ARCADS_API_KEY") or os.environ.get("ARCADS_API_KEY")
    if not key:
        raise SystemExit(
            "error: neither ARCADS_BASIC_AUTH nor ARCADS_API_KEY set in .env (or shell environment)"
        )
    import base64

    encoded = base64.b64encode(f"{key}:".encode()).decode()
    return f"Basic {encoded}"


def slugify(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len] or "image"


def http_post_json(url: str, headers: dict, body: dict, timeout: int = 60) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
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
    req = urllib.request.Request(
        presigned_url,
        data=data,
        method="PUT",
        headers={"Content-Type": mime},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status >= 300:
            raise RuntimeError(f"presigned PUT failed: HTTP {resp.status}")


def http_download(url: str, dest: Path, timeout: int = 120) -> None:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as out:
        while chunk := resp.read(64 * 1024):
            out.write(chunk)


def probe_dimensions(path: Path) -> tuple[int, int]:
    """Return (width, height) using macOS `sips`. Falls back to (0, 0) on error."""
    try:
        out = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        ).stdout
        w = h = 0
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("pixelWidth:"):
                w = int(line.split(":", 1)[1].strip())
            elif line.startswith("pixelHeight:"):
                h = int(line.split(":", 1)[1].strip())
        return w, h
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
    """Upload a local image via Arcads presigned-URL flow. Returns the filePath."""
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
    """Submit a generation request. Returns asset id."""
    final_prompt = prompt
    if not allow_chrome:
        final_prompt += NO_CHROME_SUFFIX
    if not no_safe_zone:
        final_prompt += SAFE_ZONE_SUFFIX
    final_prompt += GLYPH_SAFETY_SUFFIX

    body: dict = {
        "model": LOCKED_MODEL,
        "prompt": final_prompt,
    }
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
    """Poll GET /v1/assets/<id> until status=generated. Returns the image URL."""
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
                # Some endpoints nest the URL — scan common locations
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
) -> dict:
    log(f"variant {variant}: uploading refs ({len(ref_locals)})…")
    # Arcads filePaths are single-use across generation calls, so we upload fresh per variant.
    ref_filepaths = [upload_reference(p, base_url, auth_hdr) for p in ref_locals]
    source_filepath = upload_reference(source_local, base_url, auth_hdr) if source_local else None

    log(f"variant {variant}: submitting (mode={mode})…")
    asset_id = submit(
        prompt, mode, aspect_ratio, source_filepath, ref_filepaths,
        product_id, project_id, base_url, auth_hdr,
        allow_chrome=allow_chrome, no_safe_zone=no_safe_zone,
    )
    log(f"variant {variant}: id={asset_id}")
    url = poll(asset_id, base_url, auth_hdr)
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
        "model": LOCKED_MODEL,
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description="Generate gpt-image-2 image(s) via Arcads. Brand contract: gpt-image-2 only.",
    )
    p.add_argument("--prompt", required=True, help="Image prompt (post-rewrite).")
    p.add_argument(
        "--mode",
        default="image",
        choices=sorted(ALLOWED_MODES),
        help="image (default, text-to-image with optional refs) or image_edit (modify --source).",
    )
    p.add_argument(
        "--aspect-ratio",
        choices=sorted(ALLOWED_RATIOS),
        help="Required for --mode image. Ignored for --mode image_edit.",
    )
    p.add_argument("--n", type=int, default=1, help="Variant count, 1-5.")
    p.add_argument(
        "--out",
        type=Path,
        default=Path("./generated"),
        help="Output directory for PNGs.",
    )
    p.add_argument(
        "--image-ref",
        type=Path,
        action="append",
        default=[],
        metavar="PATH",
        help=(
            f"Reference image path (PNG/JPG/WEBP). Repeatable, max {MAX_REFS}. "
            "Used for style/subject grounding in --mode image, and as additional "
            "references in --mode image_edit."
        ),
    )
    p.add_argument(
        "--source",
        type=Path,
        metavar="PATH",
        help="Source image to edit. Required for --mode image_edit, rejected for --mode image.",
    )
    p.add_argument(
        "--model",
        default=LOCKED_MODEL,
        help=f"Locked to {LOCKED_MODEL} by brand contract.",
    )
    p.add_argument(
        "--env-file",
        type=Path,
        default=Path(".env"),
        help="Path to .env (default: ./.env).",
    )
    p.add_argument(
        "--product-id",
        help="Arcads productId (defaults to PRODUCT_ID env / .env).",
    )
    p.add_argument(
        "--project-id",
        help="Arcads projectId (defaults to PROJECT_ID env / .env).",
    )
    p.add_argument(
        "--base-url",
        default=None,
        help=f"Arcads API base URL (default: {BASE_URL_DEFAULT} or ARCADS_BASE_URL).",
    )
    p.add_argument(
        "--allow-chrome",
        action="store_true",
        help="Allow platform/screenshot UI in the output. Default is to strip all such UI.",
    )
    p.add_argument(
        "--no-safe-zone",
        action="store_true",
        help="Skip the edge-safe suffix. Use only if you genuinely need text to bleed.",
    )
    args = p.parse_args()

    if args.model != LOCKED_MODEL:
        log(
            f"error: brand contract violation — model must be '{LOCKED_MODEL}', got '{args.model}'. "
            f"This skill is locked to ChatGPT Image 2. For Nano Banana, use the "
            f"nano-banana-image-ad skill instead."
        )
        return 2

    if not (1 <= args.n <= 5):
        log(f"error: --n must be 1..5 (got {args.n})")
        return 2

    if len(args.image_ref) > MAX_REFS:
        log(f"error: too many --image-ref ({len(args.image_ref)}); gpt-image-2 cap is {MAX_REFS}")
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

    env = load_env(args.env_file)
    auth_hdr = auth_header(env)
    base_url = args.base_url or env.get("ARCADS_BASE_URL") or os.environ.get("ARCADS_BASE_URL") or BASE_URL_DEFAULT
    product_id = args.product_id or env.get("PRODUCT_ID") or os.environ.get("PRODUCT_ID")
    project_id = args.project_id or env.get("PROJECT_ID") or os.environ.get("PROJECT_ID")
    if not product_id:
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
        f"generating {args.n} variant(s) model={LOCKED_MODEL} mode={args.mode} "
        f"{'aspect=' + aspect if aspect else 'aspect=from-source'} "
        f"chrome={chrome_state} refs={len(args.image_ref)} -> {args.out}/"
    )

    results: list[dict] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=args.n) as ex:
        futures = {
            ex.submit(
                generate_one, i, args.prompt, args.mode, aspect,
                args.source, list(args.image_ref), args.out, slug, ts,
                base_url, auth_hdr, product_id, project_id,
                args.allow_chrome, args.no_safe_zone,
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
