#!/usr/bin/env python3
"""
generate-seedance-video.py — one-command Seedance 2.5 / 2.0 image-to-video via the Arcads external API.

Follows skills/arcads-external-api/SKILL.md end to end:

  1. Load .env (ARCADS_BASIC_AUTH or ARCADS_API_KEY) and verify auth with GET /v1/products.
  2. Read the credit balance (GET /v1/credits) before and after, so the real cost lands in the log.
  3. Resolve the product (--product-id | --product-name | PRODUCT_ID in .env | first product).
  4. Ensure today's "Arcads API - YYYY-MM-DD" folder + project (skip with --no-project).
  5. Upload every --image via presigned URL. Uploads are one-time-use, so each variation re-uploads.
  6. Show the credit estimate; stop unless --yes (or an interactive "y"). --dry-run prints the payload only.
  7. POST /v2/videos/generate, append a line to logs/arcads-api.jsonl, poll GET /v1/assets/{id}
     (fallback GET /v1/videos/{id}), then update the same log line with status / creditsCharged / URLs.
  8. Download the mp4 into --out, add the asset to the project if needed, open the output folder.

Example (HYPERFOCUS campaign):
  python3 scripts/generate-seedance-video.py \
      --prompt-file campaigns/hyperfocus-sparkling-focus-water/prompt-seedance-2.5-15s.txt \
      --image references/products/hyperfocus-can.png \
      --name hyperfocus-cinematic --duration 15 --aspect 9:16 --resolution 720p --yes

Stdlib only. Exit 0 if at least one variation succeeded, 1 if all failed, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL_DEFAULT = "https://external-api.arcads.ai"
ROOT = Path(__file__).resolve().parent.parent
LOG_PATH_DEFAULT = ROOT / "logs" / "arcads-api.jsonl"

# Live OpenAPI (GET /docs-json, checked 2026-09-14). Only image-to-video is wired here.
MODEL_RULES: dict[str, dict] = {
    "seedance-2.5": {"duration": (4, 30), "resolution": {"480p", "720p", "1080p"}, "max_images": 30},
    "seedance-2.0": {"duration": (4, 15), "resolution": {"480p", "720p", "1080p", "4K"}, "max_images": 9},
}
ASPECTS = {"9:16", "16:9"}  # seedance-2.0 / seedance-2.5 accept these two only
MEDIA_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
FORBIDDEN_WORDS = ("cinematic", "professional", "stunning", "8k", "studio", "perfect")  # seedance-2.md
MIN_LONGEST_SIDE = 1024
POLL_INTERVAL_S = 10
# Documented rate for seedance-2.0 i2v @720p (skills/arcads-external-api/reference.md, 2026-05-19).
FALLBACK_RATE = {"model": "seedance-2.0", "resolution": "720p", "credits_per_sec": 48.0}


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- env / auth

def load_env(env_path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not env_path.exists():
        return out
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def auth_header(env: dict[str, str]) -> str:
    basic = env.get("ARCADS_BASIC_AUTH") or os.environ.get("ARCADS_BASIC_AUTH")
    if basic and "your_base64_encoded" not in basic:
        return basic if basic.startswith("Basic ") else f"Basic {basic}"
    key = env.get("ARCADS_API_KEY") or os.environ.get("ARCADS_API_KEY")
    if key and key != "your_key_here":
        return "Basic " + base64.b64encode(f"{key}:".encode()).decode()
    raise SystemExit(
        "error: no Arcads credentials. Put ARCADS_BASIC_AUTH (or ARCADS_API_KEY) in .env — "
        "run ./scripts/setup.sh, then ./scripts/check-arcads-env.sh. "
        "Get the header at https://app.arcads.ai/settings/api (no account yet? https://arcads.ai/?via=claude-code)"
    )


# ---------------------------------------------------------------- http

class Api:
    def __init__(self, base_url: str, auth: str):
        self.base = base_url.rstrip("/")
        self.headers = {"Authorization": auth, "Accept": "application/json"}

    def _do(self, method: str, path: str, body: dict | None = None, timeout: int = 60) -> tuple[int, dict | list | None]:
        url = path if path.startswith("http") else f"{self.base}{path}"
        data = json.dumps(body).encode() if body is not None else None
        headers = dict(self.headers)
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                return resp.status, (json.loads(raw) if raw.strip() else None)
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw)
            except Exception:  # noqa: BLE001
                parsed = {"message": raw}
            return e.code, parsed

    def get(self, path: str) -> tuple[int, dict | list | None]:
        return self._do("GET", path)

    def post(self, path: str, body: dict) -> tuple[int, dict | list | None]:
        return self._do("POST", path, body)

    def must(self, method: str, path: str, body: dict | None = None) -> dict | list:
        code, data = self._do(method, path, body)
        if code >= 300:
            raise RuntimeError(f"HTTP {code} on {method} {path}: {json.dumps(data)[:600]}")
        return data if data is not None else {}


def http_put_file(presigned_url: str, file_path: Path, mime: str) -> None:
    req = urllib.request.Request(presigned_url, data=file_path.read_bytes(), method="PUT", headers={"Content-Type": mime})
    with urllib.request.urlopen(req, timeout=300) as resp:
        if resp.status >= 300:
            raise RuntimeError(f"presigned PUT failed: HTTP {resp.status}")


def http_download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=600) as resp, dest.open("wb") as out:
        while chunk := resp.read(256 * 1024):
            out.write(chunk)


# ---------------------------------------------------------------- images

def probe_dimensions(path: Path) -> tuple[int, int]:
    """(width, height) for PNG/JPEG/WebP from the header bytes; (0, 0) if unknown."""
    try:
        data = path.read_bytes()
        if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
            return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
        if data[:2] == b"\xff\xd8":
            i = 2
            while i < len(data) - 9:
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xD8, 0xD9):
                    i += 2
                    continue
                if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                    return int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
                i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP" and data[12:16] == b"VP8X":
            return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
    except Exception as e:  # noqa: BLE001
        log(f"warn: could not probe {path.name}: {e}")
    return 0, 0


def prepare_image(path: Path, workdir: Path) -> Path:
    """Auto-upscale small refs (longest side < 1024 → 1080, Lanczos) and flatten to RGB JPEG when Pillow is available."""
    if not path.exists():
        raise SystemExit(f"error: image not found: {path}")
    if path.suffix.lower() not in MEDIA_TYPES:
        raise SystemExit(f"error: unsupported image type {path.suffix}; use png/jpg/webp")
    w, h = probe_dimensions(path)
    if w and h and max(w, h) >= MIN_LONGEST_SIDE:
        return path
    try:
        from PIL import Image  # type: ignore
    except Exception:  # noqa: BLE001
        log(f"warn: {path.name} is {w}x{h} (< {MIN_LONGEST_SIDE}px) and Pillow is not installed; sending as-is. "
            "pip install pillow to auto-upscale.")
        return path
    im = Image.open(path).convert("RGB")
    scale = 1080 / max(im.size)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    out = workdir / f"{path.stem}-upscaled.jpg"
    im.save(out, "JPEG", quality=93)
    log(f"info: upscaled {path.name} {w}x{h} -> {im.width}x{im.height} ({out.name})")
    return out


def upload_reference(api: Api, local: Path) -> str:
    mime = MEDIA_TYPES[local.suffix.lower()]
    resp = api.must("POST", "/v1/file-upload/get-presigned-url", {"fileType": mime})
    presigned, file_path = resp.get("presignedUrl"), resp.get("filePath")
    if not presigned or not file_path:
        raise RuntimeError(f"presigned-url response missing fields: {resp}")
    http_put_file(presigned, local, mime)
    return file_path


# ---------------------------------------------------------------- arcads bookkeeping

def get_credits(api: Api) -> dict | None:
    code, data = api.get("/v1/credits")
    return data if code == 200 and isinstance(data, dict) else None


def resolve_product(api: Api, product_id: str | None, product_name: str | None) -> tuple[str, str]:
    data = api.must("GET", "/v1/products?pageSize=100&page=1")
    items = data.get("items", []) if isinstance(data, dict) else data
    if product_id:
        for p in items:
            if p.get("id") == product_id:
                return p["id"], p.get("name", "")
        return product_id, "(id not in first 100 products)"
    if product_name:
        needle = product_name.lower()
        exact = [p for p in items if (p.get("name") or "").lower() == needle]
        partial = [p for p in items if needle in (p.get("name") or "").lower()]
        pick = (exact or partial or [None])[0]
        if not pick:
            names = ", ".join(sorted((p.get("name") or "?") for p in items))
            raise SystemExit(f"error: no product matching '{product_name}'. Products: {names}")
        return pick["id"], pick.get("name", "")
    if not items:
        raise SystemExit("error: the workspace has no products — create one at https://app.arcads.ai first")
    if len(items) > 1:
        log("info: several products exist; using the first. Pass --product-name/--product-id to choose:")
        for p in items:
            log(f"      - {p.get('name')}  ({p.get('id')})")
    return items[0]["id"], items[0].get("name", "")


def ensure_project(api: Api, product_id: str, name: str) -> tuple[str | None, str | None]:
    """Return (folderId, projectId) for the dated session folder, creating both when missing."""
    data = api.must("GET", f"/v1/products/{product_id}/folders?pageSize=100&page=1")
    folders = data.get("items", []) if isinstance(data, dict) else data
    folder = next((f for f in folders if f.get("name") == name), None)
    if not folder:
        folder = api.must("POST", "/v1/folders", {"productId": product_id, "name": name})
        log(f"info: created folder '{name}' ({folder.get('id')})")
    folder_id = folder.get("id")
    project = api.must("POST", "/v1/projects", {"folderId": folder_id, "name": name})
    return folder_id, project.get("id")


# ---------------------------------------------------------------- logging (logs/arcads-api.jsonl)

def log_append(log_path: Path, entry: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def log_update(log_path: Path, asset_id: str, response: dict) -> None:
    if not log_path.exists():
        return
    lines = log_path.read_text().splitlines()
    for i, line in enumerate(lines):
        try:
            obj = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if obj.get("assetId") == asset_id:
            obj["response"] = response
            lines[i] = json.dumps(obj)
            break
    log_path.write_text("\n".join(lines) + "\n")


def estimate_credits(log_path: Path, model: str, resolution: str, duration: int) -> tuple[float | None, str]:
    """Median credits/sec from past log entries with the same model+resolution; documented fallback otherwise."""
    rates: list[float] = []
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            try:
                obj = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            req, resp = obj.get("request") or {}, obj.get("response") or {}
            if obj.get("model") == model and req.get("resolution") == resolution and req.get("duration") \
                    and isinstance(resp.get("creditsCharged"), (int, float)) and resp.get("creditsCharged") > 0:
                rates.append(resp["creditsCharged"] / float(req["duration"]))
    if rates:
        rate = statistics.median(rates)
        return rate * duration, f"median of {len(rates)} logged {model} {resolution} run(s): {rate:.1f} credits/sec"
    fb = FALLBACK_RATE
    note = (f"no logged {model} {resolution} runs; using the documented {fb['model']} {fb['resolution']} "
            f"rate of {fb['credits_per_sec']:.0f} credits/sec as a floor (reference.md, 2026-05-19)")
    if model != fb["model"] or resolution != fb["resolution"]:
        note += " — the real rate for this config is unknown until the first run lands in the log"
    return fb["credits_per_sec"] * duration, note


# ---------------------------------------------------------------- generation

def poll_asset(api: Api, asset_id: str, timeout_s: int) -> dict:
    deadline = time.monotonic() + timeout_s
    last = None
    use_videos = False
    while time.monotonic() < deadline:
        path = f"/v1/videos/{asset_id}" if use_videos else f"/v1/assets/{asset_id}"
        code, data = api.get(path)
        if code == 404 and not use_videos:
            use_videos = True  # non-seedance types live under /v1/videos
            continue
        if code >= 300 or not isinstance(data, dict):
            log(f"  [{asset_id[:8]}] poll HTTP {code}; retrying")
            time.sleep(POLL_INTERVAL_S)
            continue
        status = data.get("status") or data.get("videoStatus")
        if isinstance(status, dict):
            status = status.get("status") or json.dumps(status)
        if status != last:
            log(f"  [{asset_id[:8]}] status={status}")
            last = status
        if status in ("generated", "completed", "done"):
            return data
        if status in ("failed", "error", "rejected"):
            err = ((data.get("data") or {}).get("error") or {}).get("message") if isinstance(data.get("data"), dict) else None
            raise RuntimeError(f"generation failed: {err or data.get('error') or data.get('message') or json.dumps(data)[:400]}")
        time.sleep(POLL_INTERVAL_S)
    raise TimeoutError(f"asset {asset_id} did not finish within {timeout_s}s (it keeps rendering — check the Arcads dashboard)")


def open_folder(path: Path) -> None:
    for cmd in (["open", str(path)], ["xdg-open", str(path)], ["explorer", str(path)]):
        try:
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            return
        except Exception:  # noqa: BLE001
            continue


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "seedance"


def main() -> int:
    ap = argparse.ArgumentParser(description="Seedance 2.5 / 2.0 image-to-video via the Arcads external API.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt-file", type=Path, help="text file with the full prompt (keeps @(img1) tokens)")
    src.add_argument("--prompt", help="inline prompt")
    ap.add_argument("--image", type=Path, action="append", default=[], help="reference image (repeatable; index 0 = @(img1))")
    ap.add_argument("--image-url", action="append", default=[], help="reference image URL to download first (repeatable)")
    ap.add_argument("--model", default="seedance-2.5", choices=sorted(MODEL_RULES))
    ap.add_argument("--duration", type=int, default=15)
    ap.add_argument("--aspect", default="9:16", choices=sorted(ASPECTS))
    ap.add_argument("--resolution", default="720p", help="480p | 720p (default, documented rate) | 1080p | 4K (seedance-2.0 only)")
    ap.add_argument("--no-audio", action="store_true", help="audioEnabled=false (default: generate audio)")
    ap.add_argument("--enhance", action="store_true", help="let Arcads enhance the prompt (+8 credits)")
    ap.add_argument("--n", type=int, default=1, help="number of variations (separate calls, same payload)")
    ap.add_argument("--name", default=None, help="slug for output files (default: from the prompt)")
    ap.add_argument("--out", type=Path, default=ROOT / "outputs" / "seedance")
    ap.add_argument("--product-id", default=None)
    ap.add_argument("--product-name", default=None, help="case-insensitive match against product names")
    ap.add_argument("--project-name", default=None, help='default "Arcads API - YYYY-MM-DD"')
    ap.add_argument("--no-project", action="store_true", help="skip folder/project bookkeeping")
    ap.add_argument("--env-file", type=Path, default=ROOT / ".env")
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--log-file", type=Path, default=LOG_PATH_DEFAULT)
    ap.add_argument("--timeout", type=int, default=1800, help="poll timeout seconds per variation")
    ap.add_argument("--yes", action="store_true", help="skip the credit-estimate confirmation")
    ap.add_argument("--dry-run", action="store_true", help="validate, upload nothing, print the payload, exit")
    ap.add_argument("--no-open", action="store_true", help="do not open the output folder when done")
    args = ap.parse_args()

    rules = MODEL_RULES[args.model]
    lo, hi = rules["duration"]
    if not (lo <= args.duration <= hi):
        log(f"error: {args.model} duration must be {lo}-{hi}s (got {args.duration})")
        return 2
    if args.resolution not in rules["resolution"]:
        log(f"error: {args.model} resolution must be one of {sorted(rules['resolution'])} (got {args.resolution})")
        return 2
    if not (1 <= args.n <= 8):
        log("error: --n must be 1..8")
        return 2
    prompt = (args.prompt_file.read_text() if args.prompt_file else args.prompt).strip()
    if not prompt:
        log("error: empty prompt")
        return 2
    words = len(prompt.split())
    if not (100 <= words <= 260):
        log(f"warn: prompt is {words} words; the Seedance guide recommends 100-260")
    hits = [w for w in FORBIDDEN_WORDS if re.search(rf"\b{re.escape(w)}\b", prompt, flags=re.I)]
    if hits:
        log(f"warn: prompt contains Seedance-unfriendly words {hits} (see prompting/prompt-library/seedance-2.md)")
    n_refs = len(args.image) + len(args.image_url)
    if n_refs > rules["max_images"]:
        log(f"error: {args.model} accepts at most {rules['max_images']} reference images (got {n_refs})")
        return 2
    if n_refs == 0:
        log("warn: no --image given; the @(img1) token in the prompt will have nothing to point at (text-to-video)")

    env = load_env(args.env_file)
    auth = auth_header(env)
    base_url = args.base_url or env.get("ARCADS_BASE_URL") or os.environ.get("ARCADS_BASE_URL") or BASE_URL_DEFAULT
    api = Api(base_url, auth)

    product_id, product_name = resolve_product(
        api, args.product_id or env.get("PRODUCT_ID") or os.environ.get("PRODUCT_ID"), args.product_name)
    log(f"product: {product_name} ({product_id})")

    balance_before = get_credits(api)
    if balance_before:
        log(f"credits remaining before: {balance_before.get('creditsRemaining')}")

    estimate, source = estimate_credits(args.log_file, args.model, args.resolution, args.duration)
    total = (estimate or 0) * args.n + (8 * args.n if args.enhance else 0)
    log("")
    log("Estimated credit cost (ESTIMATE ONLY — confirm exact pricing in the Arcads platform):")
    log(f"  {args.model} {args.duration}s {args.resolution} {args.aspect} x {args.n} = ~{total:.0f} credits")
    log(f"  source: {source}")
    if balance_before and isinstance(balance_before.get("creditsRemaining"), (int, float)) and total > balance_before["creditsRemaining"]:
        log(f"  WARNING: estimate exceeds the remaining balance ({balance_before['creditsRemaining']})")
    log("")

    payload_preview = {
        "model": args.model, "productId": product_id, "prompt": prompt, "aspectRatio": args.aspect,
        "duration": args.duration, "resolution": args.resolution, "audioEnabled": not args.no_audio,
        "referenceImages": [f"<upload of {p}>" for p in args.image] + [f"<download+upload of {u}>" for u in args.image_url],
    }
    if args.enhance:
        payload_preview["enhance"] = True
    if args.dry_run:
        print(json.dumps({"dryRun": True, "baseUrl": base_url, "estimatedCredits": total, "estimateSource": source,
                          "payload": payload_preview}, indent=2))
        return 0
    if not args.yes:
        if not sys.stdin.isatty():
            log("Refusing to spend credits without confirmation. Re-run with --yes (or --dry-run to inspect).")
            return 2
        if input("Proceed? [y/N] ").strip().lower() not in ("y", "yes"):
            log("aborted")
            return 2

    project_name = args.project_name or f"Arcads API - {datetime.now().strftime('%Y-%m-%d')}"
    project_id = None
    if not args.no_project:
        try:
            _, project_id = ensure_project(api, product_id, project_name)
            log(f"project: {project_name} ({project_id})")
        except Exception as e:  # noqa: BLE001
            log(f"warn: could not create session folder/project ({e}); continuing without projectId")

    args.out.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix="arcads-seedance-"))
    local_images: list[Path] = []
    for i, url in enumerate(args.image_url):
        dest = workdir / f"ref-url-{i}{Path(url.split('?')[0]).suffix or '.jpg'}"
        http_download(url, dest)
        local_images.append(dest)
    local_images = [prepare_image(p, workdir) for p in list(args.image) + local_images]

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = args.name or slugify(prompt)
    results: list[dict] = []
    failures = 0
    for variant in range(1, args.n + 1):
        try:
            ref_paths = [upload_reference(api, p) for p in local_images]  # fresh upload per call (one-time-use paths)
            body: dict = {
                "model": args.model, "productId": product_id, "prompt": prompt, "aspectRatio": args.aspect,
                "duration": args.duration, "resolution": args.resolution, "audioEnabled": not args.no_audio,
            }
            if ref_paths:
                body["referenceImages"] = ref_paths
            if project_id:
                body["projectId"] = project_id
            if args.enhance:
                body["enhance"] = True
            started = time.monotonic()
            created = api.must("POST", "/v2/videos/generate", body)
            asset_id = created.get("id")
            if not asset_id:
                raise RuntimeError(f"create returned no id: {json.dumps(created)[:400]}")
            log(f"variant {variant}: created {asset_id} (type={created.get('type')}, status={created.get('status')})")
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                "endpoint": "POST /v2/videos/generate", "model": args.model, "assetId": asset_id,
                "productId": product_id, "projectId": project_id,
                "request": {"duration": args.duration, "resolution": args.resolution, "aspectRatio": args.aspect,
                            "audioEnabled": not args.no_audio, "referenceImagesCount": len(ref_paths),
                            "referenceVideosCount": 0, "referenceAudiosCount": 0, "promptWordCount": words,
                            "enhance": bool(args.enhance)},
                "response": {"status": created.get("status") or "pending", "creditsCharged": (created.get("data") or {}).get("creditsCharged"),
                             "generationTimeSec": None, "videoUrl": None, "thumbnailUrl": None, "error": None},
                "session": {"folderName": project_name if not args.no_project else None, "script": "scripts/generate-seedance-video.py"},
            }
            log_append(args.log_file, entry)

            final = poll_asset(api, asset_id, args.timeout)
            elapsed = round(time.monotonic() - started)
            url = final.get("url") or final.get("videoUrl") or final.get("sdUrl")
            if not url:
                raise RuntimeError(f"generated but no url: {json.dumps(final)[:400]}")
            dest = args.out / f"{ts}-{slug}-v{variant}.mp4"
            log(f"variant {variant}: downloading -> {dest}")
            http_download(url, dest)
            credits = (final.get("data") or {}).get("creditsCharged") if isinstance(final.get("data"), dict) else None
            log_update(args.log_file, asset_id, {
                "status": final.get("status") or "generated", "creditsCharged": credits, "generationTimeSec": elapsed,
                "videoUrl": url, "thumbnailUrl": final.get("thumbnailUrl"), "error": None,
            })
            if project_id and project_id not in (final.get("projects") or []):
                code, _ = api.post("/v1/assets/add-to-project", {"assetId": asset_id, "projectId": project_id})
                if code >= 300:
                    log(f"warn: add-to-project returned HTTP {code}")
            results.append({"variant": variant, "assetId": asset_id, "path": str(dest), "videoUrl": url,
                            "thumbnailUrl": final.get("thumbnailUrl"), "creditsCharged": credits,
                            "generationTimeSec": elapsed, "watchUrl": f"{base_url}/v1/assets/{asset_id}/watch"})
        except Exception as e:  # noqa: BLE001
            failures += 1
            log(f"variant {variant}: FAILED — {e}")
            if "content checker" in str(e).lower() or "flagged" in str(e).lower():
                log("  hint: credits are charged at create time; tighten the prompt before retrying (do not resend the same payload)")

    balance_after = get_credits(api)
    spent = None
    if balance_before and balance_after and all(isinstance(b.get("creditsRemaining"), (int, float)) for b in (balance_before, balance_after)):
        spent = balance_before["creditsRemaining"] - balance_after["creditsRemaining"]
        log(f"credits remaining after: {balance_after['creditsRemaining']} (spent this run: {spent})")

    summary = {"ok": bool(results), "product": {"id": product_id, "name": product_name}, "projectId": project_id,
               "model": args.model, "duration": args.duration, "resolution": args.resolution, "aspect": args.aspect,
               "estimatedCredits": total, "creditsSpent": spent, "results": results, "failures": failures}
    print(json.dumps(summary, indent=2))
    if results and not args.no_open:
        open_folder(args.out)
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())
