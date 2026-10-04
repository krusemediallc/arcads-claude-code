"""
Shared Meta Marketing API helpers for the meta-ad-builder skill.

Distilled from the Ad Builder Agent deploy scripts: image/video upload,
video-processing polling, and ad creation with transient-error retry/backoff.

Credentials come from environment (load a .env first with python-dotenv):
  META_ACCESS_TOKEN   (required) — long-lived user/system token, ads_management scope
  META_AD_ACCOUNT_ID  (required) — with or without the act_ prefix
  META_API_VERSION    (optional) — Graph API version, default v23.0
"""

import base64
import json
import os
import time
from pathlib import Path

import requests

API_VERSION = os.getenv("META_API_VERSION", "v23.0")
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


def get_access_token():
    token = os.getenv("META_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("META_ACCESS_TOKEN not set — see check-meta-env.sh")
    return token


def get_ad_account_id():
    acct = os.getenv("META_AD_ACCOUNT_ID")
    if not acct:
        raise RuntimeError("META_AD_ACCOUNT_ID not set — see check-meta-env.sh")
    return acct if acct.startswith("act_") else f"act_{acct}"


def auth_headers():
    """Bearer header for Graph API calls.

    The token goes in a header, never in a query string or form body: URLs end up
    in proxy logs, crash reports and shell history. Matches the pattern in
    scripts/meta-ad-library-import/import_ads.py.
    """
    return {"Authorization": "Bearer " + get_access_token()}


# Every Graph call gets an explicit timeout. Without one, requests blocks forever
# on a half-open connection and the deploy appears to hang with no output.
TIMEOUT_JSON = 60
TIMEOUT_UPLOAD_IMAGE = 120
TIMEOUT_UPLOAD_VIDEO = 900


def resolve_output_dir(run_slug):
    """Resolve a per-run output directory.

    Honors OUTPUT_BASE (set by the gen-ai-core workspace); otherwise writes
    under ./outputs/meta-ads/ — both are gitignored, so account-specific ad
    IDs and pulled performance data never land in version control.
    """
    base = os.getenv("OUTPUT_BASE")
    root = Path(base) if base else Path("outputs/meta-ads")
    run_dir = root / run_slug
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def upload_image(path, name=None):
    """Upload an image to /adimages (base64). Returns the image hash."""
    path = Path(path)
    if not path.exists():
        print(f"  ERROR: image not found: {path}")
        return None
    with open(path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    url = f"{BASE_URL}/{get_ad_account_id()}/adimages"
    resp = requests.post(
        url,
        headers=auth_headers(),
        data={
            "bytes": img_b64,
            "name": (name or path.stem)[:90],
        },
        timeout=TIMEOUT_UPLOAD_IMAGE,
    )
    data = resp.json()
    if "images" in data:
        h = list(data["images"].values())[0].get("hash")
        print(f"  Uploaded image. hash={h}")
        return h
    print(f"  Upload error: {json.dumps(data, indent=2)[:500]}")
    return None


def upload_video(path):
    """Upload a video to /advideos (multipart). Returns the video_id."""
    path = Path(path)
    if not path.exists():
        print(f"  ERROR: video not found: {path}")
        return None
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"  Uploading {path.name} ({size_mb:.1f} MB)...")
    url = f"{BASE_URL}/{get_ad_account_id()}/advideos"
    with open(path, "rb") as f:
        files = {"source": (path.name, f, "video/mp4")}
        data = {"name": path.name}
        resp = requests.post(url, headers=auth_headers(), data=data, files=files,
                             timeout=TIMEOUT_UPLOAD_VIDEO)
    if resp.status_code != 200:
        print(f"  ERROR HTTP {resp.status_code}: {resp.text[:500]}")
        return None
    result = resp.json()
    if "error" in result:
        print(f"  ERROR uploading: {json.dumps(result['error'], indent=2)}")
        return None
    vid = result.get("id")
    print(f"  Video uploaded: {vid}")
    return vid


def wait_for_video_processing(video_id, max_wait=360):
    """Poll a video until processing completes. Returns a thumbnail URL.

    Meta rejects video-ad creation until the video is fully processed; the
    returned thumbnail is required by video_data.image_url.
    """
    print("  Waiting for video processing...")
    url = f"{BASE_URL}/{video_id}"
    for attempt in range(max_wait // 10):
        time.sleep(10)
        resp = requests.get(url, headers=auth_headers(), params={
            "fields": "status,picture,thumbnails{uri,is_preferred}",
        }, timeout=TIMEOUT_JSON)
        data = resp.json()
        if "error" in data:
            print(f"    Poll error: {data['error'].get('message', '?')}")
            continue
        status = data.get("status", {})
        phase = status.get("processing_phase", {}).get("status", "unknown")
        video_status = status.get("video_status", "unknown")
        elapsed = (attempt + 1) * 10
        print(f"    {elapsed}s: phase={phase}, video_status={video_status}")
        if phase == "complete" and video_status == "ready":
            thumbs = data.get("thumbnails", {}).get("data", [])
            preferred = next((t for t in thumbs if t.get("is_preferred")), None)
            return (preferred or {}).get("uri") or data.get("picture")
    print("  WARNING: processing timed out. Falling back to picture.")
    resp = requests.get(url, headers=auth_headers(), params={"fields": "picture"},
                        timeout=TIMEOUT_JSON)
    return resp.json().get("picture")


def create_ad(adset_id, ad_name, creative, status="PAUSED", pixel_id=None):
    """Create an ad in an ad set. Never auto-retried.

    status defaults to PAUSED — the skill never launches spending ads
    automatically. The user reviews and un-pauses in Ads Manager.

    Ad creation is not idempotent: Meta offers no idempotency key here, and a
    transient error can be returned *after* the ad was created. Retrying would
    then silently produce duplicate ads in the ad set. So this returns None and
    tells the caller to look before trying again.
    """
    url = f"{BASE_URL}/{get_ad_account_id()}/ads"
    payload = {
        "adset_id": adset_id,
        "name": ad_name,
        "status": status,
        "creative": json.dumps(creative),
    }
    if pixel_id:
        payload["tracking_specs"] = json.dumps([{
            "action.type": ["offsite_conversion"],
            "fb_pixel": [pixel_id],
        }])

    try:
        resp = requests.post(url, headers=auth_headers(), data=payload,
                             timeout=TIMEOUT_JSON)
    except requests.exceptions.RequestException as e:
        print(f"  ERROR creating ad '{ad_name}': request did not complete ({type(e).__name__}).")
        print("  The ad MAY still have been created. Check the ad set in Ads Manager for")
        print(f"  an ad named '{ad_name}' before running this again, or you will get a duplicate.")
        return None

    data = resp.json()
    if "error" not in data:
        ad_id = data["id"]
        print(f"  Created ad: {ad_id} ({ad_name}) [status={status}]")
        return ad_id

    err = data["error"]
    print(f"  ERROR creating ad '{ad_name}': {json.dumps(err, indent=2)}")
    if err.get("is_transient"):
        print("  This error is marked transient, but ad creation is not idempotent, so it is")
        print(f"  not retried. Check the ad set for '{ad_name}' first, then re-run if absent.")
    return None
