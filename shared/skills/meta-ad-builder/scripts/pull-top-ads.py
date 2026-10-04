#!/usr/bin/env python3
"""
Pull ad-level insights from a Meta ad account, rank by ROAS (or spend), and
fetch the winning creative copy for the top N ads. Use the output to inform
new ad copy — feed it to the copy-guide.md workflow.

Usage:
  python pull-top-ads.py
  python pull-top-ads.py --date-preset last_30d --min-spend 100 --limit 15
  python pull-top-ads.py --sort spend --ad-account act_1234567890

Required env (load via .env): META_ACCESS_TOKEN, META_AD_ACCOUNT_ID.
Output JSON is written under OUTPUT_BASE (or ./outputs/meta-ads/) — gitignored,
because it contains account-specific spend and revenue figures.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent / "lib"))

load_dotenv()

import requests  # noqa: E402
import meta_api  # noqa: E402

INSIGHT_FIELDS = [
    "ad_id", "ad_name", "campaign_name", "adset_name", "spend", "impressions",
    "clicks", "ctr", "cpc", "cpm", "actions", "action_values", "cost_per_action_type",
]


def get_ad_insights(ad_account, token, date_preset):
    url = f"{meta_api.BASE_URL}/{ad_account}/insights"
    params = {
        "level": "ad",
        "fields": ",".join(INSIGHT_FIELDS),
        "date_preset": date_preset,
        "sort": "spend_descending",
        "limit": 100,
        "filtering": json.dumps([
            {"field": "spend", "operator": "GREATER_THAN", "value": "0"}
        ]),
    }
    all_insights = []
    while url:
        resp = requests.get(url, headers=meta_api.auth_headers(), params=params, timeout=60)
        data = resp.json()
        if "error" in data:
            print(f"API Error: {json.dumps(data['error'], indent=2)}")
            return []
        all_insights.extend(data.get("data", []))
        url = data.get("paging", {}).get("next")
        params = None  # the next URL already carries params
    return all_insights


def get_ad_creative(ad_id, token):
    url = f"{meta_api.BASE_URL}/{ad_id}"
    params = {
        # asset_feed_spec holds the rotating copy for multi-variant (TEXT_LIQUIDITY)
        # ads; body/title cover legacy single-copy ads. Do NOT request
        # link_description — it is not a valid creative field and errors the call.
        "fields": "creative{id,name,title,body,object_story_spec,asset_feed_spec}",
    }
    resp = requests.get(url, headers=meta_api.auth_headers(), params=params, timeout=60)
    data = resp.json()
    if "error" in data:
        print(f"  creative fetch error for {ad_id}: {data['error'].get('message')}")
        return None
    return data.get("creative", {})


def extract_purchases(actions, action_values):
    purchases, revenue = 0, 0.0
    for a in (actions or []):
        if a.get("action_type") == "purchase":
            purchases = int(float(a.get("value", 0)))
    for a in (action_values or []):
        if a.get("action_type") == "purchase":
            revenue = float(a.get("value", 0))
    return purchases, revenue


def extract_copy(creative):
    """Pull copy from a creative, handling both multi-variant ads
    (asset_feed_spec / TEXT_LIQUIDITY) and legacy single-copy ads."""
    afs = creative.get("asset_feed_spec") or {}
    bodies = [b.get("text", "") for b in afs.get("bodies", []) if b.get("text")]
    titles = [t.get("text", "") for t in afs.get("titles", []) if t.get("text")]
    descriptions = [d.get("text", "") for d in afs.get("descriptions", []) if d.get("text")]

    # Legacy single-copy fallback when there is no asset_feed_spec.
    story = creative.get("object_story_spec", {}) or {}
    link_data = story.get("link_data", {}) or {}
    video_data = story.get("video_data", {}) or {}
    if not bodies:
        b = creative.get("body") or link_data.get("message") or video_data.get("message")
        if b:
            bodies = [b]
    if not titles:
        t = creative.get("title") or link_data.get("name")
        if t:
            titles = [t]

    return {"bodies": bodies, "titles": titles, "descriptions": descriptions}


def main():
    parser = argparse.ArgumentParser(description="Rank a Meta ad account's ads and pull winning copy")
    parser.add_argument("--ad-account", help="Ad account ID (default: META_AD_ACCOUNT_ID env)")
    parser.add_argument("--date-preset", default="maximum",
                        help="maximum, last_30d, last_7d, last_90d, etc. (default maximum)")
    parser.add_argument("--min-spend", type=float, default=50.0,
                        help="Minimum spend to qualify (default 50)")
    parser.add_argument("--limit", type=int, default=20, help="Top N ads to keep (default 20)")
    parser.add_argument("--sort", choices=["roas", "spend"], default="roas",
                        help="Ranking metric (default roas)")
    args = parser.parse_args()

    token = meta_api.get_access_token()
    ad_account = args.ad_account or meta_api.get_ad_account_id()
    if not ad_account.startswith("act_"):
        ad_account = f"act_{ad_account}"

    print(f"Pulling ad insights from {ad_account} (date_preset={args.date_preset})...\n")
    insights = get_ad_insights(ad_account, token, args.date_preset)
    if not insights:
        print("No insights returned. Check token, ad account ID, and date preset.")
        return

    enriched = []
    for row in insights:
        spend = float(row.get("spend", 0))
        purchases, revenue = extract_purchases(row.get("actions"), row.get("action_values"))
        enriched.append({
            "ad_id": row.get("ad_id"),
            "ad_name": row.get("ad_name"),
            "campaign_name": row.get("campaign_name"),
            "adset_name": row.get("adset_name"),
            "spend": spend,
            "impressions": int(row.get("impressions", 0)),
            "clicks": int(row.get("clicks", 0)),
            "ctr": float(row.get("ctr", 0)),
            "cpc": float(row.get("cpc", 0)),
            "purchases": purchases,
            "revenue": revenue,
            "roas": revenue / spend if spend > 0 else 0,
        })

    qualified = [a for a in enriched if a["spend"] >= args.min_spend]
    qualified.sort(key=lambda x: x[args.sort], reverse=True)
    top_ads = qualified[: args.limit]

    print(f"Top {len(top_ads)} ads by {args.sort} (min ${args.min_spend} spend):\n")
    print(f"{'#':<4} {'ROAS':<8} {'Spend':<11} {'Rev':<11} {'Purch':<7} {'CTR':<7} Ad Name")
    print("-" * 90)
    for i, ad in enumerate(top_ads, 1):
        print(f"{i:<4} {ad['roas']:<8.2f} ${ad['spend']:<10.2f} ${ad['revenue']:<10.2f} "
              f"{ad['purchases']:<7} {ad['ctr']:<7.2f} {(ad['ad_name'] or '')[:48]}")

    print("\nFetching creative copy for the top ads...")
    for ad in top_ads:
        creative = get_ad_creative(ad["ad_id"], token) or {}
        ad["creative"] = creative
        if creative:
            ad["copy"] = extract_copy(creative)

    run_slug = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    out_dir = meta_api.resolve_output_dir(run_slug)
    out_file = out_dir / "top-ads.json"
    with open(out_file, "w") as f:
        json.dump(top_ads, f, indent=2)
    print(f"\nSaved {len(top_ads)} ranked ads → {out_file}")


if __name__ == "__main__":
    main()
