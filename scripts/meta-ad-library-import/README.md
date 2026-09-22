# Meta Ad Library → Airtable

Collect active static-ad metadata through Meta's Ad Library API, download the original creative from each API-provided snapshot, review the image, and import it with tags and a recreation prompt. This workflow keeps the Facebook advertiser Page separate from the advertised brand or community.

The commands are deliberately separate so you can inspect their outputs. `fetch` calls Meta's API. `extract` uses an automated headless Chrome session because the API exposes snapshot URLs, not downloadable competitor image files. `prepare` requires image-specific visual review; it does not invent prompts from ad copy. `import` is a dry run unless you pass `--write`.

## Using this workflow with an AI agent

Give your agent the destination Airtable URL, the credential file location, and up to ten advertiser definitions: a brand name, numeric Facebook Page ID, and optional community URL and `include_any` filters. Finding competitors and confirming which Pages advertise them is a research step before running this CLI. For communities advertised by a shared Page, use a separate brand entry and a distinctive filter for each community; verify the actual destination after extraction.

You can use this handoff:

> Follow this guide to collect active static image ads for [brands and Facebook Page IDs] and import them into [Airtable URL]. Use [credential file] for Meta and the connected Airtable MCP or configured Airtable PAT. Collect up to 100 ads per brand entry. I authorize automated headless rendering of the API-provided snapshots. Open and inspect every selected image, choose relevant existing tags and formats, and write a detailed, individual ChatGPT Image 2.5 recreation prompt. Populate all source-supported fields, skip duplicate ad IDs, and verify the uploaded attachments and written metadata before reporting completion.

Carry out these stages in order:

1. **Inspect the destination and sources.** Read the Airtable schema and existing Ad Library URLs. Confirm each brand-to-Page relationship, then create the advertiser definitions from the supplied inputs.
2. **Collect through Meta's API.** Run `fetch`, inspect pagination and stop reasons, and confirm that returned ads match the intended brand. Keep the actual result count; the configured cap is a maximum, not a quota.
3. **Extract and review the images.** Run `extract` with authorization, open the downloaded files, and select the real static ad rather than a profile image or video poster. Confirm CTA wording and destination from the snapshot. Fill the per-ad enrichment JSON only after this review.
4. **Write useful recreation prompts.** Describe each specific image's canvas, composition, typography, colors, exact text hierarchy and reference-asset roles. Use the supplied product photo, founder portrait or service screenshot where the reference design calls for it. Keep observed competitor claims separate from replacement copy, and label prompts as untested unless you actually generate and inspect a recreation.
5. **Prepare, import and verify.** Validate the schema mapping, check the dry-run counts, then perform the authorized import. Read back the created records, confirm both attachments have finished processing, and compare the written metadata, tags and prompts with the prepared values. The CLI verifies ad-ID uniqueness and attachment ingestion; the metadata comparison is an additional agent review step.

The result is one Airtable row per selected ad ID, with its image, thumbnail, source metadata, relevant tags and recreation prompt. The downloaded image files, source JSON and write receipt stay in ignored `outputs/` for recovery. Unknown end dates remain blank; Created is automatic, and Runtime/Transcript do not apply to static images. Existing authorization covers the requested import; a dry run is a validation step, not a requirement to ask for permission again.

For terminal commands, continue below. If Airtable is already connected to your agent, use the [MCP handoff](#using-an-airtable-mcp-instead-of-a-pat) for schema access and record writes.

## Requirements

- Python 3.10+ for metadata collection, preparation and Airtable import.
- A Meta access token authorized for the [Ad Library API](https://www.facebook.com/ads/library/api/). A token that can read your own Marketing API account does not necessarily have archive access.
- Chrome and the packages in `requirements.txt` for image extraction. Selenium Manager resolves the compatible Chrome driver; its first run may download a driver.
- An Airtable personal access token with access to the destination base and `data.records:read`, `data.records:write`, and `schema.bases:read` scopes for the full CLI flow. A connected Airtable MCP can replace the schema/read/write steps.

Do not treat this API as a complete global competitor-ad feed. Commercial-ad archive coverage is constrained by Meta's supported delivery countries, dates and token access. This workflow's tested discovery configuration is `v26.0`, `ACTIVE`, `IMAGE`, and explicit UK/EU countries. An `ALL`-country query returned empty results in the original run while explicit countries returned records. Empty data is not proof that a competitor has no ads. Versions and availability can change; see [Meta's archive reference](https://developers.facebook.com/docs/graph-api/reference/ads_archive/).

## 1. Configure and fetch

Run these commands from the repository root. Keep downloads and generated JSON in ignored `outputs/`.

```bash
mkdir -p outputs/ad-library
cp scripts/meta-ad-library-import/.env.example outputs/ad-library/.env
cp scripts/meta-ad-library-import/examples/advertisers.json outputs/ad-library/advertisers.json
```

Edit the copied `.env` with your tokens and replace the synthetic advertiser. Environment variables already set in the shell take precedence over the file. Tokens are never command-line arguments.

Each advertiser needs `brand` and the numeric Facebook `page_id`. Optional `include_any` strings match the API record case-insensitively **before** applying the cap. Use them when one Page, such as Skool's shared advertiser, advertises multiple communities. Check the resulting ad copy and destination to verify the brand relationship. A public community URL alone is not evidence of its Facebook Page.

```bash
python3 scripts/meta-ad-library-import/import_ads.py --env-file outputs/ad-library/.env fetch \
  --advertisers outputs/ad-library/advertisers.json \
  --out outputs/ad-library/archive.json \
  --cap 100
```

The advertiser list accepts 1–10 entries. Defaults cover explicit UK/EU countries; override with `--countries GB,DE,FR` and `--api-version v26.0` as needed. `--max-pages` defaults to 50 per advertiser. Pagination rebuilds requests from the `after` cursor, never follows token-bearing `paging.next` URLs, deduplicates ad IDs and applies the cap to selected ads. The output reports `stop_reason` (`exhausted`, `cap`, or `max_pages`) and `complete` per advertiser. Inspect partial results before making coverage claims. Overlapping brand filters are rejected in later stages to avoid assigning one ad to two competitors.

## 2. Extract the images

This step uses headless browser rendering. Only run it when browser-based snapshot extraction is authorized; it is not an API-only download operation. It uses a fresh temporary Chrome profile, does not log in or reuse personal browser cookies, and does not bypass access restrictions.

```bash
python3 -m venv outputs/ad-library/venv
outputs/ad-library/venv/bin/python -m pip install -r scripts/meta-ad-library-import/requirements.txt
outputs/ad-library/venv/bin/python scripts/meta-ad-library-import/import_ads.py --env-file outputs/ad-library/.env extract \
  --archive outputs/ad-library/archive.json \
  --out-dir outputs/ad-library/extracted \
  --allow-headless
```

Each ad gets a JSON manifest and original image candidates under `extracted/images/`. Manifests include pixel dimensions, SHA-256, source URL, snapshot text and candidate links. Errors are recorded per ad without credential-bearing exception text. Existing successful downloads are reused; `--refresh` replaces them and renews source URLs. Revisit visual review after refreshing: candidate ordering can change. If Chrome is installed in a nonstandard location, use `--chrome-binary /path/to/chrome`.

The snapshot may contain profile pictures, multiple variations, carousel cards, or video posters. The size and CDN checks only find **candidates**. Open the actual files and select the intended static creative. Skip videos, carousels, unrelated branding and unrenderable snapshots. A failed image extraction must not become an invented attachment or prompt.

Preparation rejects snapshots containing video unless the reviewed enrichment explicitly sets `static_image_confirmed: true`. Only set this when the selected image is a verified standalone static ad, not a video poster in the snapshot.

## 3. Read your Airtable schema and review each ad

```bash
python3 scripts/meta-ad-library-import/import_ads.py --env-file outputs/ad-library/.env schema \
  --base appYOURBASE --table tblYOURTABLE \
  --out outputs/ad-library/schema.json
cp scripts/meta-ad-library-import/examples/enrichment.json outputs/ad-library/enrichment.json
```

Use the JSON example as a shape, not as ad data. Key each entry by its real Meta ad ID. After opening the image, set `visually_reviewed` to `true`, select its zero-based `asset_index`, and write its name, exact existing format choice, relevant tags, category and recreation prompt. Set CTA text, destination and landing title from the snapshot evidence; unwrap Facebook redirect links to their actual destination when needed. If these details cannot be verified, leave the ad out of enrichment until resolved. Entries absent from enrichment are skipped with a count.

Write a distinct recreation prompt for each image. Include the requested generator (for example the user's requested “ChatGPT Image 2.5”), canvas ratio, composition, margins, typography, color palette, subject placement, exact headline/body/CTA hierarchy, and instructions for substituting the supplied product or brand reference. The generator name is prompt text; this tool does not claim a particular model endpoint exists or generate images.

Supported table fields:

| Field | Expected type / behavior |
| --- | --- |
| Name, Brand, Brand Category, Aspect Ratio, CTA Text, Landing Title | Text |
| Asset, Thumbnail | Attachment; both use the reviewed image |
| Format | Single select; reviewed value must already exist |
| Display Format | Single select with `image` |
| Ad Status | Single select with `active` |
| Start Date, End Date | Date; only actual API dates are included |
| Platforms, Ad Copy | Text; API arrays are joined with newlines |
| CTA Link, Ad Library URL | URL |
| Tags | Text, or multiple select with all provided choices already configured |
| AI Prompt | Long text |
| Created | Airtable-generated; never written |
| Runtime, Transcript | Left blank because these are static images |

The Tags text field also stores the source Facebook Page name/ID and Meta ad ID. For a multiple-select Tags field, source Page identity remains in `archive.json`; only the reviewed taxonomy tags are selected. Select choices are validated against the schema and never created implicitly. The community is stored in Brand even when the advertiser is a shared Page. Missing end dates remain blank; an ongoing ad has no known end date. Read-only or inapplicable columns are not filled with made-up values.

The schema reader accepts either the Airtable REST table shape (`{"table":{"fields":[...]}}`) or the connected Airtable MCP's combined `table` + `config` schema shape. Required fields must have these names; field IDs are resolved at preparation time, not hardcoded.

```bash
python3 scripts/meta-ad-library-import/import_ads.py prepare \
  --archive outputs/ad-library/archive.json \
  --extracted outputs/ad-library/extracted \
  --schema outputs/ad-library/schema.json \
  --enrichment outputs/ad-library/enrichment.json \
  --out outputs/ad-library/prepared.json
```

Airtable fetches attachments from public HTTPS URLs. Meta CDN URLs expire. Import promptly after extraction, or upload the downloaded originals to your own approved public asset storage and set each enrichment entry's optional `asset_url`. Do not put credential-protected storage URLs or a Meta snapshot URL into an attachment field.

## 4. Dry-run, write, and verify

```bash
python3 scripts/meta-ad-library-import/import_ads.py --env-file outputs/ad-library/.env import \
  --prepared outputs/ad-library/prepared.json \
  --base appYOURBASE --table tblYOURTABLE \
  --receipt outputs/ad-library/import-receipt.json
```

Review `new_count` and `skipped_existing_count`, then run the same command with `--write`:

```bash
python3 scripts/meta-ad-library-import/import_ads.py --env-file outputs/ad-library/.env import \
  --prepared outputs/ad-library/prepared.json \
  --base appYOURBASE --table tblYOURTABLE \
  --receipt outputs/ad-library/import-receipt.json --write
```

The importer reads every existing row, canonicalizes each Ad Library URL, skips existing ad IDs and duplicates within the incoming batch, and creates at most 10 records per request. It never deletes or replaces existing records. One ad ID gets one row; identical images used under different ad IDs are retained as distinct ads. Use extracted SHA-256 hashes to curate unique creative images separately if desired.

A receipt is saved before the first write and after every batch. The final readback checks that each expected ad is present once and that both attachment fields have Airtable attachment IDs, URLs and nonzero sizes. It polls every five seconds for up to `--attachment-timeout 120` seconds because attachment ingestion is asynchronous. An attachment failure exits with an error and lists affected records; fix those rows rather than recreating them. Existing matching rows are skipped, not repaired or overwritten. Partial failed writes can be retried safely after reading the receipt: a fresh scan skips rows that already arrived. Writes are never automatically retried after a timeout.

Run only one importer per destination table at a time. The read-before-create check is resumable and duplicate-aware, but Airtable does not enforce a uniqueness constraint on this URL field, so concurrent writers can race. Existing duplicate rows are reported during verification and not deleted automatically.

### Using an Airtable MCP instead of a PAT

`fetch`, `extract`, and `prepare` do not need an Airtable PAT when you supply a schema exported from your connected Airtable tool. The prepared file contains `records` in the connector-compatible `[{"fields":{"fld...":value}}]` shape.

1. Read all existing rows and build an Ad Library URL → record ID map, including all pagination.
2. Apply the same ad-ID deduplication before writes. The reusable `new_records()` helper accepts REST-style existing records; convert MCP `cellValuesByFieldId` into `fields` first.
3. Send only `records` to the connector's create-records tool with the selected base/table and `typecast: false`, in batches of at most 10. `dedupe_field`, `attachment_fields`, and `skipped_unreviewed_ads` are local packet metadata, not API arguments.
4. Read the created rows back and verify actual attachment IDs, sizes, metadata, tags and prompts. Save returned record IDs in a local receipt. Do not call the CLI import as well for the same batch.

## Offline checks

```bash
python3 -m unittest discover -s scripts/meta-ad-library-import/tests -v
python3 scripts/meta-ad-library-import/import_ads.py --help
```

Tests cover filtered pagination, repeated cursors, redaction, snapshot/CDN URL validation, schema mapping, required visual review, static-field semantics, deduplication, dry-run behavior, 10-record write batches and attachment readback. They use synthetic data and make no live API requests.
