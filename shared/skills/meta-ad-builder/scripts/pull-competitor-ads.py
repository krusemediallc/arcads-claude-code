#!/usr/bin/env python3
"""
Pull a competitor's running ads from the Meta Ad Library (ads_archive) to study
their hooks, copy angles, and creative volume. Writes ad metadata + snapshot
URLs to JSON; open a snapshot URL in a browser to view the actual creative.

Usage:
  python pull-competitor-ads.py --pages "Nike,Coca-Cola"
  python pull-competitor-ads.py --pages 123456789 --countries US,CA --limit 50
  python pull-competitor-ads.py --pages "SomeBrand" --active-only --media-type video

Required env (load via .env): META_ACCESS_TOKEN.
Output JSON is written under OUTPUT_BASE (or ./outputs/meta-ads/) — gitignored.
"""

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent / "lib"))

load_dotenv()

import requests  # noqa: E402
import meta_api  # noqa: E402

ARCHIVE_FIELDS = (
    "id,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,"
    "page_id,page_name,publisher_platforms"
)


def resolve_page_id(identifier, token):
    """Numeric → returned as-is. Name/username → Graph API lookup."""
    identifier = str(identifier).strip()
    if identifier.isdigit():
        return identifier
    resp = requests.get(f"{meta_api.BASE_URL}/{identifier}",
                        headers=meta_api.auth_headers(),
                        params={"fields": "id"}, timeout=15)
    data = resp.json()
    return str(data["id"]) if "error" not in data and data.get("id") else None


def resolve_via_search(identifier, token, countries, date_min, date_max):
    """Fallback: find the page_id by searching the Ad Library for the name."""
    resp = requests.get(f"{meta_api.BASE_URL}/ads_archive",
                        headers=meta_api.auth_headers(), params={
        "search_terms": identifier,
        "ad_reached_countries": countries,
        "ad_delivery_date_min": date_min,
        "ad_delivery_date_max": date_max,
        "ad_active_status": "ALL",
        "fields": "page_id,page_name",
        "limit": 50,
    }, timeout=30)
    data = resp.json()
    if "error" in data:
        return None, None
    ads = data.get("data", [])
    counts = Counter(a.get("page_id") for a in ads if a.get("page_id"))
    names = {a.get("page_id"): a.get("page_name") for a in ads}
    ident = identifier.lower().replace(".", " ").replace("_", " ")
    for pid, _ in counts.most_common(10):
        pname = (names.get(pid) or "").lower()
        if ident in pname or all(p in pname for p in ident.split() if len(p) > 2):
            return pid, names.get(pid) or pid
    if counts:
        pid = counts.most_common(1)[0][0]
        return pid, names.get(pid) or pid
    return None, None


def fetch_ads_archive(page_id, token, countries, date_min, date_max,
                      limit, sort_by, active_status, media_type):
    params = {
        "search_page_ids": page_id,
        "ad_reached_countries": countries,
        "ad_delivery_date_min": date_min,
        "ad_delivery_date_max": date_max,
        "ad_active_status": active_status,
        "sort_by": sort_by,
        "fields": ARCHIVE_FIELDS,
        "limit": min(limit, 100),
    }
    if media_type != "all":
        params["media_type"] = media_type
    url = f"{meta_api.BASE_URL}/ads_archive"
    all_ads, seen = [], set()
    while True:
        resp = requests.get(url, headers=meta_api.auth_headers(), params=params, timeout=30)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 60))
            print(f"  Rate limited. Waiting {wait}s...")
            time.sleep(wait)
            continue
        if resp.status_code >= 500:
            print(f"  Server error {resp.status_code}. Retrying in 5s...")
            time.sleep(5)
            continue
        data = resp.json()
        if "error" in data:
            return all_ads, data["error"].get("message", "Unknown API error")
        for ad in data.get("data", []):
            if ad.get("id") and ad["id"] not in seen:
                seen.add(ad["id"])
                all_ads.append(ad)
        next_url = data.get("paging", {}).get("next")
        if not next_url or len(all_ads) >= limit:
            break
        url, params = next_url, None
    return all_ads[:limit], None


def main():
    parser = argparse.ArgumentParser(description="Pull competitor ads from the Meta Ad Library")
    parser.add_argument("--pages", required=True,
                        help='Comma-separated page names or numeric IDs')
    parser.add_argument("--countries", default="US", help="Comma-separated country codes (default US)")
    parser.add_argument("--days", type=int, default=365, help="Days back to search (default 365)")
    parser.add_argument("--limit", type=int, default=50, help="Max ads per page (default 50)")
    parser.add_argument("--sort-by", default="impressions_high_to_low",
                        choices=["impressions_high_to_low", "longest_running", "most_recent",
                                 "ad_delivery_start_time_ascending",
                                 "ad_delivery_start_time_descending"])
    parser.add_argument("--active-only", action="store_true", help="Only currently-active ads")
    parser.add_argument("--media-type", choices=["all", "video", "image"], default="all")
    args = parser.parse_args()

    token = meta_api.get_access_token()
    now = datetime.now(timezone.utc)
    date_max = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    date_min = (now - timedelta(days=args.days)).strftime("%Y-%m-%d")

    pages = [p.strip() for p in args.pages.split(",") if p.strip()]
    report = {"pulled_at": now.isoformat(), "pages": []}

    for page_input in pages:
        print(f"\n{'='*60}\nProcessing: {page_input}\n{'='*60}")
        page_id = resolve_page_id(page_input, token)
        page_name = None
        if not page_id:
            page_id, page_name = resolve_via_search(page_input, token, args.countries,
                                                    date_min, date_max)
        if not page_id:
            print(f"  Could not resolve a page ID for '{page_input}'. Skipping.")
            print("  Tip: pass the numeric ID from the Ad Library URL (view_all_page_id=...).")
            continue
        print(f"  Page ID: {page_id}")

        ads, err = fetch_ads_archive(
            page_id, token, args.countries, date_min, date_max,
            limit=args.limit, sort_by=args.sort_by,
            active_status="ACTIVE" if args.active_only else "ALL",
            media_type=args.media_type,
        )
        if err:
            print(f"  API Error: {err}")
            continue
        print(f"  Found {len(ads)} ads.")
        report["pages"].append({
            "page_input": page_input,
            "page_id": page_id,
            "page_name": page_name or (ads[0].get("page_name") if ads else page_input),
            "ad_count": len(ads),
            "ads": ads,
        })

    run_slug = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    out_dir = meta_api.resolve_output_dir(run_slug)
    out_file = out_dir / "competitor-ads.json"
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2)
    total = sum(p["ad_count"] for p in report["pages"])
    print(f"\nSaved {total} ads across {len(report['pages'])} page(s) → {out_file}")
    print("Open each ad's ad_snapshot_url in a browser to view the creative.")
    print("NOTE: Meta's snapshot URLs carry an access token, so treat this file as a")
    print(f"      secret. It lives under {out_dir} (gitignored) - do not share it.")


if __name__ == "__main__":
    main()
