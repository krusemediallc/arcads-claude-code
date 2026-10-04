import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('import_ads', Path(__file__).parents[1] / 'import_ads.py')
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def ad(aid, body='Example community'):
    return {'id': aid, 'page_id': '123', 'page_name': 'Shared advertiser',
            'ad_creative_bodies': [body], 'ad_delivery_start_time': '2026-09-01',
            'publisher_platforms': ['facebook', 'instagram'],
            'ad_snapshot_url': f'https://www.facebook.com/ads/archive/render_ad/?id={aid}&access_token=secret'}


def schema():
    fields = []
    choices = {'Format': ['Headline'], 'Display Format': ['image'], 'Ad Status': ['active', 'inactive']}
    for index, name in enumerate(mod.REQUIRED_FIELDS):
        kind = 'singleSelect' if name in choices else 'singleLineText'
        if name in ('Asset', 'Thumbnail'):
            kind = 'multipleAttachments'
        if name in ('Tags', 'Ad Copy', 'Platforms', 'AI Prompt'):
            kind = 'multilineText'
        fields.append({'id': f'fld{index}', 'name': name, 'type': kind,
                       'options': {'choices': [{'name': c} for c in choices.get(name, [])]}})
    return mod.normalize_schema({'table': {'fields': fields}})


def reviewed():
    return {'visually_reviewed': True, 'asset_index': 0, 'name': 'Example headline', 'format': 'Headline',
            'brand_category': 'Education', 'tags': ['Education'], 'ai_prompt': 'A specifically reviewed prompt.',
            'cta_text': 'Learn more', 'cta_link': 'https://example.com/community', 'landing_title': 'Example'}


class ArchiveTests(unittest.TestCase):
    def test_filter_precedes_cap_and_pages_do_not_use_returned_urls(self):
        responses = [
            {'data': [ad('1', 'Unrelated'), ad('2')], 'paging': {'next': 'https://untrusted.test/?access_token=secret', 'cursors': {'after': 'A'}}},
            {'data': [ad('2'), ad('3'), ad('4')], 'paging': {'next': 'ignored', 'cursors': {'after': 'B'}}}]
        calls = []
        def request(params):
            calls.append(params)
            return responses.pop(0)
        result = mod.collect_archive({'brand': 'Example', 'page_id': '123', 'include_any': ['Example community']},
                                     request=request, countries=['GB'], cap=2)
        self.assertEqual([r['api_record']['id'] for r in result['ads']], ['2', '3'])
        self.assertEqual(calls[1]['after'], 'A')
        self.assertEqual(result['stop_reason'], 'cap')
        self.assertFalse(result['complete'])
        self.assertNotIn('access_token', json.dumps(result))

    def test_missing_or_repeated_cursor_is_error(self):
        for paging in ({'next': 'yes'}, {'next': 'yes', 'cursors': {'after': 'same'}}):
            with self.subTest(paging=paging), self.assertRaises(mod.WorkflowError):
                mod.collect_archive({'brand': 'Example', 'page_id': '123'},
                    request=lambda p: {'data': [], 'paging': paging}, countries=['GB'], max_pages=3)

    def test_empty_is_exhausted_not_auth_failure(self):
        result = mod.collect_archive({'brand': 'Example', 'page_id': '123'},
                                     request=lambda p: {'data': []}, countries=['GB'])
        self.assertEqual(result['ads'], [])
        self.assertTrue(result['complete'])


class SecurityTests(unittest.TestCase):
    def test_recursive_redaction_and_removal_of_paging_urls(self):
        with patch.dict(os.environ, {'META_ACCESS_TOKEN': 'secret-token', 'AIRTABLE_PAT': 'secret-pat'}):
            result = mod.clean({'nested': ['message secret-token secret-pat',
                'https://www.facebook.com/test?id=1&ACCESS_TOKEN=other-secret'],
                'Authorization': 'Bearer secret-token',
                'paging': {'next': 'https://graph.facebook.com?access_token=secret-token',
                           'previous': 'https://x?token=hidden', 'cursors': {'after': 'safe'}}})
        text = json.dumps(result)
        for secret in ('secret-token', 'secret-pat', 'other-secret', 'hidden', 'Authorization'):
            self.assertNotIn(secret, text)
        self.assertEqual(result['paging'], {'has_next': True, 'cursors': {'after': 'safe'}})

    def test_snapshot_token_only_to_valid_snapshot_and_id(self):
        url = mod.snapshot_url(ad('1'), 'abc')
        self.assertIn('access_token=abc', url)
        for url in ('https://facebook.com.evil.test/ads/archive/render_ad/?id=1',
                    'https://www.facebook.com/login/?id=1',
                    'https://www.facebook.com/ads/archive/render_ad/?id=2'):
            with self.subTest(url=url), self.assertRaises(mod.WorkflowError):
                mod.snapshot_url({**ad('1'), 'ad_snapshot_url': url}, 'abc')

    def test_media_allowlist_uses_hostname_boundaries(self):
        self.assertTrue(mod.media_url_allowed('https://scontent.xx.fbcdn.net/image.jpg'))
        self.assertFalse(mod.media_url_allowed('https://fbcdn.net.evil.test/image.jpg'))
        self.assertFalse(mod.media_url_allowed('http://scontent.xx.fbcdn.net/image.jpg'))

    def test_env_file_does_not_override_existing_env(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {'META_ACCESS_TOKEN': 'existing'}):
            env = Path(root) / '.env'
            env.write_text("META_ACCESS_TOKEN='from-file'\nSYNTHETIC_SETTING='value with spaces'\n")
            mod.load_env(env)
            self.assertEqual(os.environ['META_ACCESS_TOKEN'], 'existing')
            self.assertEqual(os.environ['SYNTHETIC_SETTING'], 'value with spaces')
            os.environ.pop('SYNTHETIC_SETTING')


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.schema = schema()
        self.row = {'brand': 'Community brand', 'api_record': ad('1')}
        self.extracted = {'ad_id': '1', 'assets': [{'url': 'https://scontent.xx.fbcdn.net/image.jpg',
            'width': 1080, 'height': 1350, 'path': 'images/1-0.jpg'}]}

    def test_mapping_preserves_brand_page_difference_and_static_blanks(self):
        fields = mod.prepare_record(self.row, self.extracted, reviewed(), self.schema)['fields']
        get = lambda name: fields.get(self.schema[name]['id'])
        self.assertEqual(get('Brand'), 'Community brand')
        self.assertIn('Shared advertiser (123)', get('Tags'))
        self.assertEqual(get('Aspect Ratio'), '4:5')
        self.assertEqual(get('Start Date'), '2026-09-01')
        self.assertIsNone(get('End Date'))
        self.assertEqual(get('Ad Library URL'), 'https://www.facebook.com/ads/library/?id=1')
        self.assertEqual(len(fields), len(mod.REQUIRED_FIELDS) - 1)

    def test_unreviewed_unknown_format_bad_asset_are_rejected(self):
        for change in ({'visually_reviewed': False}, {'format': 'Invented'}, {'asset_index': -1}, {'tags': 'all'}):
            with self.subTest(change=change), self.assertRaises(mod.WorkflowError):
                mod.prepare_record(self.row, self.extracted, {**reviewed(), **change}, self.schema)

    def test_connector_schema_choices_are_supported(self):
        fields = [{'id': v['id'], 'name': v['name'], 'type': v['type']} for v in self.schema.values()]
        config = [{'id': v['id'], 'config': {'choices': [{'name': c} for c in v['choices']]}} for v in self.schema.values()]
        result = mod.normalize_schema({'table': {'fields': fields}, 'config': {'fields': config}})
        self.assertEqual(result['Format']['choices'], ['Headline'])

    def test_video_poster_requires_explicit_static_confirmation(self):
        extracted = {**self.extracted, 'snapshot': {'videos': ['https://example.com/video.mp4']}}
        with self.assertRaises(mod.WorkflowError):
            mod.prepare_record(self.row, extracted, reviewed(), self.schema)
        record = mod.prepare_record(self.row, extracted, {**reviewed(), 'static_image_confirmed': True}, self.schema)
        self.assertTrue(record['fields'])


class ImportTests(unittest.TestCase):
    def test_idempotence_for_existing_and_in_batch_duplicates(self):
        records = [{'fields': {'fldURL': f'https://www.facebook.com/ads/library/?id={aid}'}} for aid in ('1', '2', '2')]
        existing = [{'fields': {'fldURL': 'https://facebook.com/ads/library/?id=1&extra=ignored'}}]
        pending = mod.new_records(records, existing, 'fldURL')
        self.assertEqual(len(pending), 1)
        self.assertEqual(mod.new_records(records, existing + pending, 'fldURL'), [])

    def test_attachments_need_fetched_bytes_and_ids(self):
        self.assertFalse(mod.attachments_ready({'fields': {'a': [{'url': 'https://example.com'}]}}, ['a']))
        self.assertTrue(mod.attachments_ready({'fields': {'a': [{'id': 'att1', 'url': 'https://example.com', 'size': 42}]}}, ['a']))

    def test_import_defaults_to_no_writes(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {'AIRTABLE_PAT': 'fake'}):
            path = Path(root)
            mod.save(path / 'prepared.json', {'records': [{'fields': {'fldURL': mod.canonical_ad_url('1')}}],
                                            'dedupe_field': 'fldURL', 'attachment_fields': ['fldAsset']})
            with patch.object(mod, 'http_json', return_value={'records': []}) as request:
                result = mod.main(['import', '--prepared', str(path / 'prepared.json'), '--base', 'appExample',
                                   '--table', 'tblExample', '--receipt', str(path / 'receipt.json')])
            self.assertEqual(result, 0)
            self.assertTrue(all(call.kwargs.get('method', 'GET') == 'GET' for call in request.call_args_list))
            self.assertFalse(mod.load(path / 'receipt.json')['write'])

    def test_write_batches_ten_and_verifies_readback(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {'AIRTABLE_PAT': 'fake'}):
            path = Path(root)
            records = [{'fields': {'fldURL': mod.canonical_ad_url(str(i)), 'fldAsset': [{'url': 'https://example.com/image.jpg'}]}}
                       for i in range(21)]
            mod.save(path / 'prepared.json', {'records': records, 'dedupe_field': 'fldURL', 'attachment_fields': ['fldAsset']})
            stored, sizes = [], []
            def request(url, token, *, method='GET', body=None):
                if method == 'POST':
                    sizes.append(len(body['records']))
                    for row in body['records']:
                        saved = json.loads(json.dumps(row))
                        saved['id'] = 'rec' + str(len(stored))
                        saved['fields']['fldAsset'][0].update({'id': 'att1', 'size': 123})
                        stored.append(saved)
                    return {'records': stored[-len(body['records']):]}
                return {'records': stored}
            with patch.object(mod, 'http_json', side_effect=request), patch.object(mod.time, 'sleep'):
                result = mod.main(['import', '--prepared', str(path / 'prepared.json'), '--base', 'appExample',
                                   '--table', 'tblExample', '--receipt', str(path / 'receipt.json'), '--write'])
            self.assertEqual(result, 0)
            self.assertEqual(sizes, [10, 10, 1])
            self.assertTrue(mod.load(path / 'receipt.json')['attachments_verified'])


if __name__ == '__main__':
    unittest.main()
