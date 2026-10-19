#!/usr/bin/env python3
"""Generate and save text-to-image results with the MiniMax image API."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


REGIONAL_ENDPOINTS = {
    "global_en": "https://api.minimax.io/v1/image_generation",
    "cn_zh": "https://api.minimaxi.com/v1/image_generation",
}
ALLOWED_MODELS = {"image-01", "image-01-live"}
DEFAULT_MODEL = "image-01"
MEDIA_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class MiniMaxAPIError(RuntimeError):
    """Raised when the API returns an unsuccessful response."""


def load_env(path: Path | None) -> dict[str, str]:
    """Load a small .env file without adding a runtime dependency."""
    if path is None:
        return {}
    if not path.exists():
        raise SystemExit(f"error: environment file not found: {path}")

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        values[name.strip()] = value.strip().strip('"').strip("'")
    return values


def api_key(env: dict[str, str]) -> str:
    key = os.environ.get("MINIMAX_API_KEY") or env.get("MINIMAX_API_KEY")
    if not key:
        raise SystemExit("error: MINIMAX_API_KEY is not set")
    return key


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    payload: dict[str, object] = {
        "model": args.model,
        "prompt": args.prompt,
        "response_format": args.response_format,
        "n": args.n,
    }
    optional_fields = (
        "aspect_ratio",
        "width",
        "height",
        "seed",
        "prompt_optimizer",
    )
    for field in optional_fields:
        value = getattr(args, field)
        if value is not None:
            payload[field] = value
    return payload


def post_generation(endpoint: str, key: str, payload: dict[str, object]) -> dict:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise MiniMaxAPIError(f"HTTP {error.code}: {detail}") from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise MiniMaxAPIError(f"request failed: {error}") from error
    except json.JSONDecodeError as error:
        raise MiniMaxAPIError("the API returned invalid JSON") from error


def response_images(response: dict) -> tuple[list[str], dict[str, int]]:
    base_response = response.get("base_resp") or {}
    status_code = base_response.get("status_code", 0)
    if status_code not in (0, None):
        message = base_response.get("status_msg") or "image generation failed"
        raise MiniMaxAPIError(f"API error {status_code}: {message}")

    data = response.get("data") or {}
    images = data.get("image_urls") or []
    if not isinstance(images, list) or not images or not all(isinstance(item, str) for item in images):
        raise MiniMaxAPIError("the response did not include data.image_urls")

    metadata = response.get("metadata") or {}
    counts = {
        "success_count": int(metadata.get("success_count", len(images))),
        "failed_count": int(metadata.get("failed_count", 0)),
    }
    if counts["success_count"] < 1:
        raise MiniMaxAPIError("the API reported no successful images")
    return images, counts


def slugify(value: str, max_length: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:max_length] or "image"


def _decode_base64(value: str) -> bytes:
    encoded = value.split(",", 1)[1] if value.startswith("data:") and "," in value else value
    try:
        return base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as error:
        raise MiniMaxAPIError("the API returned invalid base64 image data") from error


def save_image(value: str, response_format: str, destination: Path) -> Path:
    if response_format == "base64":
        destination = destination.with_suffix(".png")
        destination.write_bytes(_decode_base64(value))
        return destination

    try:
        with urllib.request.urlopen(value, timeout=120) as response:
            content_type = response.headers.get_content_type()
            extension = MEDIA_EXTENSIONS.get(content_type)
            if extension is None:
                extension = Path(urllib.parse.urlparse(value).path).suffix.lower()
            if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
                extension = ".png"
            destination = destination.with_suffix(extension)
            destination.write_bytes(response.read())
            return destination
    except (urllib.error.URLError, TimeoutError) as error:
        raise MiniMaxAPIError(f"image download failed: {error}") from error


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate text-to-image assets with MiniMax.")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--region", choices=sorted(REGIONAL_ENDPOINTS), default="global_en")
    parser.add_argument("--model", choices=sorted(ALLOWED_MODELS), default=DEFAULT_MODEL)
    parser.add_argument("--response-format", choices=("url", "base64"), default="url")
    parser.add_argument("--aspect-ratio")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--n", type=int, default=1)
    optimizer = parser.add_mutually_exclusive_group()
    optimizer.add_argument("--prompt-optimizer", dest="prompt_optimizer", action="store_true")
    optimizer.add_argument("--no-prompt-optimizer", dest="prompt_optimizer", action="store_false")
    parser.set_defaults(prompt_optimizer=None)
    parser.add_argument("--out", type=Path, default=Path("generated/minimax"))
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args(argv)

    if args.n < 1:
        parser.error("--n must be at least 1")
    if (args.width is None) != (args.height is None):
        parser.error("--width and --height must be provided together")
    if args.aspect_ratio and args.width is not None:
        parser.error("use --aspect-ratio or --width/--height, not both")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    env_path = args.env_file
    if env_path is None and Path(".env").exists():
        env_path = Path(".env")

    try:
        key = api_key(load_env(env_path))
        payload = build_payload(args)
        response = post_generation(REGIONAL_ENDPOINTS[args.region], key, payload)
        images, counts = response_images(response)
        args.out.mkdir(parents=True, exist_ok=True)
        stem = slugify(args.prompt)
        for index, image in enumerate(images, start=1):
            path = save_image(image, args.response_format, args.out / f"{stem}-{index:02d}")
            print(json.dumps({
                "variant": index,
                "path": str(path),
                "model": args.model,
                "region": args.region,
                "response_format": args.response_format,
            }))
        print(
            f"saved {len(images)} image(s); "
            f"API successes={counts['success_count']} failures={counts['failed_count']}",
            file=sys.stderr,
        )
        return 0
    except (MiniMaxAPIError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
