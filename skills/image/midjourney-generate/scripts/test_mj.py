"""Offline behavior tests: python3 -m unittest discover -s scripts -p test_mj.py."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import mj


class FakeClient:
    base = 'https://example.test/mj-fast'

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, path, body=None):
        self.calls.append((method, path, body))
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = mj.Store(self.tmp.name)

    def test_private_config_and_environment_precedence(self):
        import os
        path = Path(self.tmp.name) / 'config.json'
        path.write_text(json.dumps({'base_url': 'https://example.test', 'api_key': 'test-only'}))
        path.chmod(0o600)
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(mj.load_settings(config_path=path), ('https://example.test', 'test-only'))
            with patch.dict(os.environ, {'MJ_API_KEY': 'override', 'APILIO_BASE_URL': 'https://shared.test'}):
                self.assertEqual(mj.load_settings('https://explicit.test', path), ('https://explicit.test', 'override'))
        path.chmod(0o644)
        with self.assertRaisesRegex(mj.MJError, '0600'):
            mj.load_settings(config_path=path)

    def test_queued_submit_reuses_result_without_post(self):
        c = FakeClient({'code': 22, 'result': '123'})
        a = self.store.mutate(c, 'imagine', {'prompt': 'cat'}, 'initial', 2)
        b = self.store.mutate(c, 'imagine', {'prompt': 'cat'}, 'initial', 2)
        self.assertEqual(a, b)
        self.assertEqual(len(c.calls), 1)
        self.assertEqual(mj.read_json(self.store.ledger)['initial']['task_id'], '123')

    def test_ambiguous_post_blocks_replay_and_keeps_evidence(self):
        c = FakeClient(mj.MJError('response lost'))
        with self.assertRaises(mj.MJError):
            self.store.mutate(c, 'imagine', {'prompt': 'cat'}, 'initial', 2)
        with self.assertRaisesRegex(mj.MJError, 'unknown'):
            self.store.mutate(c, 'imagine', {'prompt': 'cat'}, 'initial', 2)
        self.assertEqual(len(c.calls), 1)
        self.assertEqual(mj.read_json(self.store.ledger)['initial']['phase'], 'unknown')

    def test_budget_and_operation_collision(self):
        c = FakeClient({'code': 1, 'result': '123'})
        self.store.mutate(c, 'imagine', {'prompt': 'cat'}, 'one', 1)
        with self.assertRaisesRegex(mj.MJError, 'different input'):
            self.store.mutate(c, 'imagine', {'prompt': 'dog'}, 'one', 2)
        with self.assertRaisesRegex(mj.MJError, 'budget'):
            self.store.mutate(c, 'imagine', {'prompt': 'dog'}, 'two', 1)
        self.assertEqual(len(c.calls), 1)

    def test_modal_tracks_new_id_and_parent_chain(self):
        c = FakeClient({'code': 21, 'result': '456'}, {'code': 1, 'result': '789'})
        self.store.mutate(c, 'action', {'taskId': '123', 'customId': 'real-region'}, 'region', 2)
        self.store.mutate(c, 'modal', {'taskId': '456', 'prompt': 'red'}, 'confirm', 2)
        ledger = mj.read_json(self.store.ledger)
        self.assertEqual(ledger['region']['phase'], 'modal')
        self.assertEqual(ledger['confirm']['parent'], '456')
        self.assertEqual(ledger['confirm']['task_id'], '789')

    def test_rejected_response_not_marked_accepted_or_reposted(self):
        c = FakeClient({'code': 23, 'result': '123', 'description': 'queue full'})
        self.store.mutate(c, 'imagine', {'prompt': 'cat'}, 'initial', 2)
        self.store.mutate(c, 'imagine', {'prompt': 'cat'}, 'initial', 2)
        entry = mj.read_json(self.store.ledger)['initial']
        self.assertEqual(entry['phase'], 'rejected')
        self.assertEqual(entry['response']['description'], 'queue full')
        self.assertNotIn('task_id', entry)
        self.assertEqual(len(c.calls), 1)

    def test_buttons_are_dynamic_and_ambiguous_labels_refused(self):
        task = {'status': 'SUCCESS', 'buttons': [{'label': 'U2', 'customId': 'server-value'}]}
        self.assertEqual(mj.select_button(task, label='U2'), 'server-value')
        with self.assertRaises(mj.MJError):
            mj.select_button(task, custom_id='invented-value')
        task['buttons'].append({'label': 'U2', 'customId': 'another'})
        with self.assertRaises(mj.MJError):
            mj.select_button(task, label='U2')

    def test_poll_uses_status_not_progress_and_saves_failure(self):
        c = FakeClient({'id': '123', 'status': 'IN_PROGRESS', 'progress': '100%'},
                       {'id': '123', 'status': 'FAILURE', 'failReason': 'actual error'})
        with patch.object(mj.time, 'sleep'):
            result = mj.wait_task(c, self.store, '123', 10, 1)
        self.assertEqual(result['status'], 'FAILURE')
        self.assertEqual(len(c.calls), 2)
        self.assertEqual(mj.read_json(Path(self.tmp.name) / 'task-123.json')['failReason'], 'actual error')

    def test_modal_stops_polling_and_text_success_needs_no_image(self):
        for status in ('MODAL', 'SUCCESS', 'CANCEL'):
            c = FakeClient({'id': '123', 'status': status, 'properties': {'finalPrompt': 'text'}})
            result = mj.wait_task(c, self.store, '123', 10, 1)
            self.assertEqual(result['status'], status)
            self.assertEqual(len(c.calls), 1)

    def test_existing_id_recovers_with_get_only_and_auth_failure_not_retried(self):
        c = FakeClient({'id': '123', 'status': 'SUCCESS'})
        mj.fetch(c, self.store, '123')
        self.assertEqual(c.calls[0], ('GET', 'task/123/fetch', None))
        c = FakeClient(mj.HTTPFailure(401))
        with self.assertRaises(mj.HTTPFailure):
            mj.wait_task(c, self.store, '123', 10, 1)
        self.assertEqual(len(c.calls), 1)

    def test_upload_returns_url_array_without_task_id(self):
        c = FakeClient({'code': 1, 'result': ['https://example.test/image.png']})
        self.store.mutate(c, 'upload-discord-images', {'base64Array': ['data']}, 'upload', 2)
        entry = mj.read_json(self.store.ledger)['upload']
        self.assertNotIn('task_id', entry)
        self.assertEqual(entry['phase'], 'accepted')

    def test_cli_action_modal_flow_uses_response_id(self):
        client = FakeClient(
            {'id': '123', 'status': 'SUCCESS', 'buttons': [{'label': 'Vary (Region)', 'customId': 'real-region'}]},
            {'code': 21, 'result': '456'},
            {'id': '456', 'status': 'MODAL'},
            {'code': 1, 'result': '789'})
        common = ['--base-url', client.base, '--state-dir', self.tmp.name, '--max-posts', '2']
        args = mj.parser().parse_args(common + ['action', '--op', 'region', '--task-id', '123', '--label', 'Vary (Region)'])
        with patch.object(mj, 'Client', return_value=client), patch.object(mj, 'load_settings', return_value=(client.base, 'fake-key')):
            response = mj.run(args)
            self.assertTrue(response['needs_modal'])
            self.assertEqual(response['task_id'], '456')
            args = mj.parser().parse_args(common + ['modal', '--op', 'confirm', '--task-id', response['task_id']])
            final = mj.run(args)
        self.assertEqual(final['task_id'], '789')
        self.assertEqual(client.calls[1][2]['customId'], 'real-region')
        self.assertEqual(client.calls[3][2]['taskId'], '456')

    def test_timeout_preserves_id_and_rate_limit_only_retries_get(self):
        c = FakeClient({'id': '123', 'status': 'IN_PROGRESS'})
        with patch.object(mj.time, 'monotonic', side_effect=[0, 2]):
            with self.assertRaisesRegex(mj.MJError, 'resume GET for task 123'):
                mj.wait_task(c, self.store, '123', 1, 1)
        self.assertTrue((Path(self.tmp.name) / 'task-123.json').exists())
        c = FakeClient(mj.HTTPFailure(429), {'id': '123', 'status': 'SUCCESS'})
        with patch.object(mj.time, 'sleep'):
            self.assertEqual(mj.wait_task(c, self.store, '123', 10, 1)['status'], 'SUCCESS')
        self.assertEqual([x[0] for x in c.calls], ['GET', 'GET'])

    def test_cdn_403_falls_back_to_unauthenticated_curl(self):
        from PIL import Image
        import urllib.error
        class HTTP:
            def open(self, request, timeout):
                raise urllib.error.HTTPError(request.full_url, 403, 'Forbidden', {}, None)
        def curl(args, **kwargs):
            target = args[args.index('--output') + 1]
            Image.new('RGB', (12, 10)).save(target, format='PNG')
            self.assertNotIn('--header', args)
            self.assertIn('--proto-redir', args)
            self.assertNotIn('--insecure', args)
            return type('Result', (), {'returncode': 0})()
        target = Path(self.tmp.name) / 'curl.png'
        with patch.object(mj.subprocess, 'run', side_effect=curl):
            result = mj.download_image('https://example.test/result', target, HTTP())
        self.assertEqual((result['width'], result['height']), (12, 10))

    def test_download_decodes_and_rejects_html_without_delivering(self):
        from PIL import Image
        raw = io.BytesIO()
        Image.new('RGB', (32, 24), 'red').save(raw, format='PNG')
        class HTTP:
            def __init__(self, data): self.data = data; self.request = None
            def open(self, request, timeout): self.request = request; return io.BytesIO(self.data)
        http = HTTP(raw.getvalue())
        path = Path(self.tmp.name) / 'image.png'
        meta = mj.download_image('https://example.test/result', path, http)
        self.assertEqual((meta['width'], meta['height']), (32, 24))
        self.assertNotIn('Authorization', http.request.headers)
        with self.assertRaises(mj.MJError):
            mj.download_image('https://example.test/result', path, http)
        bad = Path(self.tmp.name) / 'bad.png'
        with self.assertRaises(OSError):
            mj.download_image('https://example.test/result', bad, HTTP(b'<html>error</html>'))
        self.assertFalse(bad.exists())


if __name__ == '__main__':
    unittest.main()
