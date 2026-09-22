#!/usr/bin/env python3
"""API discovery -> opt-in snapshot extraction -> visual review -> Airtable.

All outputs should live in the repository's ignored outputs/ directory.
Credentials are loaded from the environment; no credentials are CLI arguments.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

COUNTRIES = 'GB,DE,FR,ES,NL,IT,SE,IE,PL,BE,AT,PT,DK,FI,CZ,RO,HU,GR,BG,HR,SK,SI,LT,LV,EE,LU,MT,CY'
FIELDS = ','.join(('id', 'page_id', 'page_name', 'ad_creative_bodies',
    'ad_creative_link_titles', 'ad_creative_link_captions',
    'ad_creative_link_descriptions', 'ad_delivery_start_time',
    'ad_delivery_stop_time', 'publisher_platforms', 'ad_snapshot_url'))
SECRET_KEYS = {'access_token', 'token', 'authorization', 'client_secret', 'appsecret_proof'}
REQUIRED_FIELDS = ('Name', 'Asset', 'Format', 'Display Format', 'Brand',
    'Brand Category', 'Ad Status', 'Start Date', 'End Date', 'Aspect Ratio',
    'Platforms', 'Ad Copy', 'CTA Text', 'CTA Link', 'Landing Title',
    'Ad Library URL', 'Thumbnail', 'Tags', 'AI Prompt')


class WorkflowError(Exception):
    """A safe, user-facing error with no credential-bearing request URL."""


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(clean(value), ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)


def load_env(path):
    if not path:
        return
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:]
        key, sep, value = line.partition('=')
        key = key.strip()
        if sep and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', key):
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            os.environ.setdefault(key, value)


def credential(name):
    value = os.environ.get(name, '')
    if not value or value.startswith('YOUR_'):
        raise WorkflowError(f'Set {name} in the environment or --env-file.')
    return value


def clean(value):
    """Remove secrets and token-bearing paging URLs from persisted evidence."""
    if isinstance(value, dict):
        result = {k: clean(v) for k, v in value.items() if k.lower() not in SECRET_KEYS}
        if isinstance(result.get('paging'), dict):
            paging = result['paging']
            paging['has_next'] = bool(paging.pop('next', None)) or bool(paging.get('has_next'))
            paging.pop('previous', None)
        return result
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, str):
        for name in ('META_ACCESS_TOKEN', 'AIRTABLE_PAT'):
            secret = os.environ.get(name)
            if secret:
                value = value.replace(secret, '[REDACTED]').replace(urllib.parse.quote(secret, safe=''), '[REDACTED]')
        if value.startswith(('https://', 'http://')):
            parts = urllib.parse.urlsplit(value)
            query = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
                     if k.lower() not in SECRET_KEYS]
            value = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path,
                                            urllib.parse.urlencode(query), ''))
        return value
    return value


def http_json(url, token, *, method='GET', body=None):
    # GET retries are safe. Never automatically retry an ambiguous write.
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(3 if method == 'GET' else 1):
        try:
            request = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if method == 'GET' and error.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue
            # Server error bodies may echo URLs/tokens; report only structured codes.
            try:
                detail = json.loads(error.read()).get('error', {})
                code = detail.get('code', detail.get('type', 'unknown')) if isinstance(detail, dict) else 'unknown'
            except (ValueError, AttributeError):
                code = 'unknown'
            safe_code = re.sub(r'[^a-zA-Z0-9_:-]', '', str(code))[:60]
            raise WorkflowError(f'API request failed: HTTP {error.code}, code {safe_code}.') from None
        except (TimeoutError, urllib.error.URLError):
            if method == 'GET' and attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue
            suffix = ' Re-run import to check for existing records before another write.' if method != 'GET' else ''
            raise WorkflowError('API network request failed.' + suffix) from None
    raise WorkflowError('API request failed.')


def canonical_ad_url(ad_id):
    if not re.fullmatch(r'\d+', str(ad_id)):
        raise WorkflowError('Ad IDs must be numeric.')
    return f'https://www.facebook.com/ads/library/?id={ad_id}'


def canonical_existing_url(url):
    if not isinstance(url, str):
        return ''
    parts = urllib.parse.urlsplit(url)
    if parts.hostname not in ('facebook.com', 'www.facebook.com', 'm.facebook.com'):
        return ''
    aid = urllib.parse.parse_qs(parts.query).get('id', [''])[0]
    return canonical_ad_url(aid) if aid.isdigit() else ''


def collect_archive(advertiser, *, request, countries, version='v26.0', cap=100, max_pages=50):
    """Apply community filtering before the cap; preserve source Page identity."""
    if not re.fullmatch(r'\d+', str(advertiser['page_id'])):
        raise WorkflowError('Advertiser page_id must be numeric.')
    if not advertiser.get('brand'):
        raise WorkflowError('Each advertiser needs a brand.')
    params = {'ad_type': 'ALL', 'ad_active_status': 'ACTIVE', 'media_type': 'IMAGE',
              'ad_reached_countries': json.dumps(countries), 'search_page_ids': json.dumps([str(advertiser['page_id'])]),
              'fields': FIELDS, 'limit': 100}
    selected, seen, cursors = [], set(), set()
    more, reason = False, 'exhausted'
    pages = 0
    for _ in range(max_pages):
        response = request(dict(params))
        pages += 1
        data = response.get('data')
        if not isinstance(data, list):
            raise WorkflowError('Meta returned an unexpected archive response.')
        matched = []
        for ad in data:
            aid = str(ad.get('id', ''))
            if aid in seen:
                continue
            canonical_ad_url(aid)
            seen.add(aid)
            haystack = json.dumps(ad, ensure_ascii=False).casefold()
            terms = advertiser.get('include_any', [])
            if terms and not any(term.casefold() in haystack for term in terms):
                continue
            matched.append({'brand': advertiser['brand'], 'community_url': advertiser.get('community_url'),
                            'api_record': clean(ad)})
        remaining = cap - len(selected)
        selected.extend(matched[:remaining])
        paging = response.get('paging', {})
        more = bool(paging.get('next') or paging.get('has_next'))
        if len(matched) > remaining or (len(selected) >= cap and more):
            reason = 'cap'
            break
        if not more:
            break
        cursor = paging.get('cursors', {}).get('after')
        if not cursor or cursor in cursors:
            raise WorkflowError('Meta pagination repeated or omitted its next cursor; no silent partial import.')
        cursors.add(cursor)
        params['after'] = cursor
    else:
        reason = 'max_pages' if more else 'exhausted'
    return {'brand': advertiser['brand'], 'page_id': str(advertiser['page_id']), 'ads': selected,
            'pages_fetched': pages, 'unique_ads_scanned': len(seen), 'stop_reason': reason,
            'complete': reason == 'exhausted', 'api_version': version, 'countries': countries}


def command_fetch(args):
    token = credential('META_ACCESS_TOKEN')
    if not re.fullmatch(r'v\d+\.\d+', args.api_version):
        raise WorkflowError('Use an API version such as v26.0.')
    countries = [c.strip().upper() for c in args.countries.split(',') if c.strip()]
    if not countries or any(not re.fullmatch(r'[A-Z]{2}', c) for c in countries):
        raise WorkflowError('Supply explicit two-letter country codes; ALL is intentionally unsupported.')
    advertisers = load(args.advertisers)
    if not isinstance(advertisers, list) or not 1 <= len(advertisers) <= 10:
        raise WorkflowError('Provide 1–10 advertiser definitions.')
    endpoint = f'https://graph.facebook.com/{args.api_version}/ads_archive'
    results = []
    for advertiser in advertisers:
        result = collect_archive(advertiser, request=lambda p: http_json(endpoint + '?' + urllib.parse.urlencode(p), token),
                                 countries=countries, version=args.api_version, cap=args.cap, max_pages=args.max_pages)
        results.append(result)
        save(args.out, {'collected_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'advertisers': results})
        print(json.dumps({k: result[k] for k in ('brand', 'pages_fetched', 'stop_reason')}))


def archive_ads(path):
    result, seen = [], set()
    for advertiser in load(path)['advertisers']:
        for row in advertiser['ads']:
            aid = row['api_record']['id']
            if aid in seen:
                raise WorkflowError(f'Ad {aid} matched more than one brand; resolve overlapping filters.')
            seen.add(aid)
            result.append(row)
    return result


SNAPSHOT_JS = '''return {title: document.title, text: document.body.innerText,
images: Array.from(document.querySelectorAll('img')).map(x => ({url:x.currentSrc || x.src,
width:x.naturalWidth,height:x.naturalHeight,alt:x.alt})).filter(x=>x.width>=200 && x.height>=200),
links: Array.from(document.querySelectorAll('a')).map(x=>({text:x.innerText,href:x.href})),
videos: Array.from(document.querySelectorAll('video')).map(x=>x.currentSrc || x.src)};'''


def media_url_allowed(url):
    parts = urllib.parse.urlsplit(url)
    host = parts.hostname or ''
    return parts.scheme == 'https' and any(host == suffix or host.endswith('.' + suffix)
                                         for suffix in ('fbcdn.net', 'cdninstagram.com'))


def snapshot_url(ad, token):
    parts = urllib.parse.urlsplit(ad['ad_snapshot_url'])
    if parts.scheme != 'https' or parts.hostname not in ('www.facebook.com', 'facebook.com') or parts.path != '/ads/archive/render_ad/':
        raise WorkflowError('Unexpected Meta snapshot URL; refusing to send the token.')
    query = dict(urllib.parse.parse_qsl(parts.query))
    if query.get('id') != str(ad['id']):
        raise WorkflowError('Snapshot ad ID does not match the API record.')
    query['access_token'] = token
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(query), ''))


def command_extract(args):
    if not args.allow_headless:
        raise WorkflowError('Snapshot rendering uses a browser. Pass --allow-headless only when authorized.')
    try:
        from selenium import webdriver
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.common.exceptions import TimeoutException
        from PIL import Image
    except ImportError:
        raise WorkflowError('Install requirements.txt for snapshot extraction.') from None
    token = credential('META_ACCESS_TOKEN')
    output = Path(args.out_dir)
    (output / 'images').mkdir(parents=True, exist_ok=True)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1440,1200')
    if args.chrome_binary:
        options.binary_location = args.chrome_binary
    # Selenium Manager finds a compatible driver. Use a fresh temporary profile.
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(45)
    failures = 0
    try:
        for row in archive_ads(args.archive):
            ad = row['api_record']
            aid = str(ad['id'])
            destination = output / f'{aid}.json'
            if destination.exists() and load(destination).get('assets') and not args.refresh:
                continue
            result = {'ad_id': aid, 'brand': row['brand'], 'assets': []}
            try:
                driver.get(snapshot_url(ad, token))
                try:
                    WebDriverWait(driver, 25, poll_frequency=0.5).until(lambda d: d.execute_script(
                        "return Array.from(document.images).some(x=>x.naturalWidth>=200 && x.naturalHeight>=200);"))
                except TimeoutException:
                    pass
                snapshot = clean(driver.execute_script(SNAPSHOT_JS))
                result['snapshot'] = snapshot
                seen = set()
                for candidate in snapshot['images']:
                    url = candidate['url']
                    if url in seen or not media_url_allowed(url):
                        continue
                    seen.add(url)
                    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(request, timeout=45) as response:
                        if not media_url_allowed(response.geturl()):
                            raise WorkflowError('Unexpected media redirect.')
                        data = response.read(30 * 1024 * 1024 + 1)
                    if len(data) > 30 * 1024 * 1024:
                        raise WorkflowError('Image exceeds the 30 MiB download limit.')
                    with Image.open(io.BytesIO(data)) as im:
                        width, height = im.size
                        file_format = im.format
                        if getattr(im, 'n_frames', 1) != 1 or file_format not in ('JPEG', 'PNG', 'WEBP'):
                            continue
                        im.verify()
                    extension = {'JPEG': 'jpg', 'PNG': 'png', 'WEBP': 'webp'}[file_format]
                    relative_path = f'images/{aid}-{len(result["assets"])}.{extension}'
                    (output / relative_path).write_bytes(data)
                    result['assets'].append({'url': url, 'path': relative_path, 'width': width, 'height': height,
                                             'sha256': hashlib.sha256(data).hexdigest()})
                if not result['assets']:
                    result['error'] = 'No static image candidates. Snapshot may be unavailable or require login.'
            except Exception as error:
                # Selenium errors often contain the token-bearing URL: never persist repr/error text.
                result['error'] = type(error).__name__
            if result.get('error'):
                failures += 1
            save(destination, result)
            print(json.dumps({'ad_id': aid, 'image_candidates': len(result['assets']), 'error': result.get('error')}))
    finally:
        driver.quit()
    if failures:
        raise WorkflowError(f'{failures} snapshots need attention; successful downloads were retained.')


def normalize_schema(schema):
    table = schema.get('table', schema)
    fields = {f['name']: dict(f) for f in table['fields']}
    configs = {f['id']: f for f in schema.get('config', {}).get('fields', [])}
    for field in fields.values():
        options = field.get('options', configs.get(field['id'], {}).get('config', {}))
        field['choices'] = [c['name'] for c in options.get('choices', [])]
    missing = set(REQUIRED_FIELDS) - fields.keys()
    if missing:
        raise WorkflowError('Airtable schema is missing fields: ' + ', '.join(sorted(missing)))
    return fields


def encode_field(field, value):
    kind = field['type']
    if kind == 'multipleSelects':
        if not isinstance(value, list):
            raise WorkflowError(f'{field["name"]} must be a list.')
        if any(v not in field['choices'] for v in value):
            raise WorkflowError(f'{field["name"]} contains an unknown select choice; configure the schema first.')
        return value
    if isinstance(value, list) and kind in ('multilineText', 'singleLineText'):
        return '\n'.join(value)
    if kind == 'singleSelect' and value not in field['choices']:
        raise WorkflowError(f'{field["name"]} contains an unknown select choice; configure the schema first.')
    return value


def prepare_record(row, extracted, enrichment, schema):
    ad = row['api_record']
    aid = str(ad['id'])
    if enrichment.get('visually_reviewed') is not True:
        raise WorkflowError(f'Ad {aid} needs visual review before preparing its prompt and tags.')
    if extracted.get('snapshot', {}).get('videos') and enrichment.get('static_image_confirmed') is not True:
        raise WorkflowError(f'Ad {aid} snapshot contains video; confirm the selected asset is a standalone static ad, not a video poster.')
    for name in ('name', 'format', 'brand_category', 'tags', 'ai_prompt', 'cta_text', 'cta_link', 'landing_title'):
        if not enrichment.get(name):
            raise WorkflowError(f'Ad {aid} is missing reviewed {name}.')
    if not isinstance(enrichment['tags'], list):
        raise WorkflowError(f'Ad {aid} tags must be a list.')
    index = enrichment.get('asset_index')
    if isinstance(index, bool) or not isinstance(index, int) or index < 0 or index >= len(extracted.get('assets', [])):
        raise WorkflowError(f'Ad {aid} needs a valid, visually selected asset_index.')
    asset = extracted['assets'][index]
    if extracted.get('ad_id') != aid:
        raise WorkflowError('Extracted image manifest does not match the ad.')
    width, height = asset['width'], asset['height']
    divisor = math.gcd(width, height)
    if divisor <= 0 or width <= 0 or height <= 0:
        raise WorkflowError('Invalid image dimensions.')
    url = enrichment.get('asset_url', asset['url'])
    if urllib.parse.urlsplit(url).scheme != 'https' or clean(url) != url:
        raise WorkflowError('Asset URL must be credential-free HTTPS.')
    if urllib.parse.urlsplit(enrichment['cta_link']).scheme not in ('http', 'https'):
        raise WorkflowError('CTA Link must be the verified HTTP(S) destination.')
    attachment = [{'url': url, 'filename': Path(asset['path']).name}]
    tags = list(dict.fromkeys(enrichment['tags']))
    if schema['Tags']['type'] != 'multipleSelects':
        tags += [f'Facebook Page: {ad["page_name"]} ({ad["page_id"]})', f'Meta ad ID: {aid}']
    values = {'Name': enrichment['name'], 'Asset': attachment, 'Format': enrichment['format'],
              'Display Format': 'image', 'Brand': row['brand'], 'Brand Category': enrichment['brand_category'],
              'Ad Status': 'active', 'Aspect Ratio': f'{width // divisor}:{height // divisor}',
              'Platforms': ad.get('publisher_platforms', []), 'Ad Copy': ad.get('ad_creative_bodies', []),
              'CTA Text': enrichment['cta_text'], 'CTA Link': enrichment['cta_link'],
              'Landing Title': enrichment['landing_title'], 'Ad Library URL': canonical_ad_url(aid),
              'Thumbnail': attachment, 'Tags': tags, 'AI Prompt': enrichment['ai_prompt']}
    for api_name, name in (('ad_delivery_start_time', 'Start Date'), ('ad_delivery_stop_time', 'End Date')):
        if ad.get(api_name):
            value = ad[api_name][:10]
            dt.date.fromisoformat(value)
            values[name] = value
    # Active status is known from the archive query. Missing end dates stay unknown.
    # Created is computed by Airtable; Runtime/Transcript do not apply to static ads.
    fields = {schema[name]['id']: encode_field(schema[name], value) for name, value in values.items()}
    return {'fields': fields}


def command_prepare(args):
    schema = normalize_schema(load(args.schema))
    enrichment = load(args.enrichment)
    rows = archive_ads(args.archive)
    unknown = set(enrichment) - {row['api_record']['id'] for row in rows}
    if unknown:
        raise WorkflowError('Enrichment contains ad IDs absent from the archive.')
    records = []
    for row in rows:
        aid = row['api_record']['id']
        if aid not in enrichment:
            continue
        extracted = load(Path(args.extracted) / f'{aid}.json')
        records.append(prepare_record(row, extracted, enrichment[aid], schema))
    if not records:
        raise WorkflowError('No visually reviewed ads selected for preparation.')
    save(args.out, {'records': records, 'typecast': False,
                    'dedupe_field': schema['Ad Library URL']['id'],
                    'attachment_fields': [schema['Asset']['id'], schema['Thumbnail']['id']],
                    'skipped_unreviewed_ads': len(rows) - len(records)})
    print(json.dumps({'prepared': len(records), 'skipped_unreviewed_ads': len(rows) - len(records)}))


def airtable_endpoint(base, table):
    if not re.fullmatch(r'app[A-Za-z0-9]+', base) or not re.fullmatch(r'tbl[A-Za-z0-9]+', table):
        raise WorkflowError('Use Airtable base and table IDs, not names.')
    return f'https://api.airtable.com/v0/{base}/{table}'


def read_records(endpoint, token):
    rows, seen_offsets = [], set()
    params = {'pageSize': 100, 'returnFieldsByFieldId': 'true'}
    while True:
        response = http_json(endpoint + '?' + urllib.parse.urlencode(params), token)
        rows.extend(response['records'])
        offset = response.get('offset')
        if not offset:
            return rows
        if offset in seen_offsets:
            raise WorkflowError('Airtable pagination repeated its offset.')
        seen_offsets.add(offset)
        params['offset'] = offset


def new_records(prepared, existing, dedupe_field):
    seen = {canonical_existing_url(row.get('fields', {}).get(dedupe_field)) for row in existing}
    pending = []
    for record in prepared:
        url = canonical_existing_url(record['fields'].get(dedupe_field))
        if not url:
            raise WorkflowError('A prepared record has no valid Ad Library URL.')
        if url not in seen:
            pending.append(record)
            seen.add(url)
    return pending


def attachments_ready(record, fields):
    return all(record.get('fields', {}).get(field) and
               all(a.get('id') and a.get('url') and a.get('size', 0) > 0 for a in record['fields'][field])
               for field in fields)


def command_import(args):
    packet = load(args.prepared)
    endpoint = airtable_endpoint(args.base, args.table)
    token = credential('AIRTABLE_PAT')
    existing = read_records(endpoint, token)
    pending = new_records(packet['records'], existing, packet['dedupe_field'])
    receipt = {'base_id': args.base, 'table_id': args.table, 'write': args.write,
               'prepared_count': len(packet['records']), 'new_count': len(pending),
               'skipped_existing_count': len(packet['records']) - len(pending), 'created_ids': [],
               'attachments_verified': False}
    save(args.receipt, receipt)
    if not args.write:
        print(json.dumps(receipt))
        return
    for offset in range(0, len(pending), 10):
        response = http_json(endpoint, token, method='POST', body={
            'records': pending[offset:offset + 10], 'typecast': False, 'returnFieldsByFieldId': True})
        receipt['created_ids'].extend(r['id'] for r in response['records'])
        save(args.receipt, receipt)
        time.sleep(0.25)
    target_urls = {canonical_existing_url(r['fields'][packet['dedupe_field']]) for r in packet['records']}
    deadline = time.monotonic() + args.attachment_timeout
    while True:
        actual = [r for r in read_records(endpoint, token)
                  if canonical_existing_url(r.get('fields', {}).get(packet['dedupe_field'])) in target_urls]
        counts = {}
        for row in actual:
            url = canonical_existing_url(row['fields'][packet['dedupe_field']])
            counts[url] = counts.get(url, 0) + 1
        receipt['duplicate_urls'] = [u for u, n in counts.items() if n > 1]
        receipt['unverified_record_ids'] = [r['id'] for r in actual if not attachments_ready(r, packet['attachment_fields'])]
        receipt['attachments_verified'] = len(counts) == len(target_urls) and not receipt['unverified_record_ids'] and not receipt['duplicate_urls']
        save(args.receipt, receipt)
        if receipt['attachments_verified']:
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(5, remaining))
    print(json.dumps(receipt))
    if not receipt['attachments_verified']:
        raise WorkflowError('Import needs review: missing records, duplicates, or pending/failed attachments. See receipt; do not blindly re-create rows.')


def command_schema(args):
    airtable_endpoint(args.base, args.table)
    response = http_json(f'https://api.airtable.com/v0/meta/bases/{args.base}/tables', credential('AIRTABLE_PAT'))
    match = next((t for t in response['tables'] if t['id'] == args.table), None)
    if not match:
        raise WorkflowError('Table not found in base schema.')
    save(args.out, {'table': match})
    print('Saved table schema.')


def positive(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError('Must be positive.')
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', help='Optional dotenv file; existing environment values take precedence.')
    sub = parser.add_subparsers(dest='command', required=True)
    fetch = sub.add_parser('fetch', help='Read active IMAGE metadata from the Meta archive API.')
    fetch.add_argument('--advertisers', required=True)
    fetch.add_argument('--out', required=True)
    fetch.add_argument('--api-version', default='v26.0')
    fetch.add_argument('--countries', default=COUNTRIES)
    fetch.add_argument('--cap', type=positive, default=100, help='Maximum selected ads per advertiser/brand.')
    fetch.add_argument('--max-pages', type=positive, default=50)
    fetch.set_defaults(run=command_fetch)
    extract = sub.add_parser('extract', help='Opt-in headless rendering of API-discovered snapshots.')
    extract.add_argument('--archive', required=True)
    extract.add_argument('--out-dir', required=True)
    extract.add_argument('--allow-headless', action='store_true')
    extract.add_argument('--refresh', action='store_true', help='Refresh expired asset URLs and downloads.')
    extract.add_argument('--chrome-binary')
    extract.set_defaults(run=command_extract)
    schema = sub.add_parser('schema', help='Read Airtable field IDs, types and select choices.')
    schema.add_argument('--base', required=True)
    schema.add_argument('--table', required=True)
    schema.add_argument('--out', required=True)
    schema.set_defaults(run=command_schema)
    prepare = sub.add_parser('prepare', help='Map visually reviewed creatives to an Airtable/MCP payload.')
    prepare.add_argument('--archive', required=True)
    prepare.add_argument('--extracted', required=True)
    prepare.add_argument('--schema', required=True)
    prepare.add_argument('--enrichment', required=True)
    prepare.add_argument('--out', required=True)
    prepare.set_defaults(run=command_prepare)
    imp = sub.add_parser('import', help='Deduplicate, dry-run, then optionally write and verify Airtable records.')
    imp.add_argument('--prepared', required=True)
    imp.add_argument('--base', required=True)
    imp.add_argument('--table', required=True)
    imp.add_argument('--receipt', required=True)
    imp.add_argument('--write', action='store_true', help='Required to create rows; default is read-only dry run.')
    imp.add_argument('--attachment-timeout', type=positive, default=120,
                     help='Seconds to wait for attachment readback after writes (default: 120; polls every 5 seconds).')
    imp.set_defaults(run=command_import)
    args = parser.parse_args(argv)
    try:
        load_env(args.env_file)
        args.run(args)
    except WorkflowError as error:
        print(f'Error: {clean(str(error))}', file=sys.stderr)
        return 1
    except (KeyError, ValueError, TypeError, OSError):
        print('Error: invalid input, unreadable file, or missing required data. Check the documented JSON shapes.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
