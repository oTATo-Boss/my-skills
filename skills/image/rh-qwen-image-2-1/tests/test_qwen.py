import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from io import BytesIO

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'rh_qwen.py'
spec = importlib.util.spec_from_file_location('rh_qwen', SCRIPT)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


class QwenTests(unittest.TestCase):
    def test_shared_runninghub_default_and_overrides(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(q.os.environ, {'HOME': tmp}, clear=True):
            shared = Path(tmp)/'.config/runninghub/.env'
            shared.parent.mkdir(parents=True)
            shared.write_text('RUNNINGHUB_API_KEY=shared-offline-key\n')
            self.assertEqual(q.configured_key(), 'shared-offline-key')
            alternate = Path(tmp)/'alternate.env'
            alternate.write_text('RUNNINGHUB_API_KEY=alternate-key\n')
            q.os.environ['RUNNINGHUB_ENV_FILE'] = str(alternate)
            self.assertEqual(q.configured_key(), 'alternate-key')
            q.os.environ['RUNNINGHUB_API_KEY'] = 'env-override'
            self.assertEqual(q.configured_key(), 'env-override')

    def test_nodes_preserve_slot_order_and_empty_values(self):
        nodes = q.nodes('换衣服', ['a.png', 'b.png'], '9:16', '2K', 2)
        self.assertEqual([n['nodeId'] for n in nodes[:6]],
                         ['420', '432', '433', '436', '435', '434'])
        self.assertEqual([n['fieldValue'] for n in nodes[:6]],
                         ['a.png', 'b.png', 'None', 'None', 'None', 'None'])
        values = {n['nodeId']: n['fieldValue'] for n in nodes}
        self.assertEqual(values['481'], '2000')
        self.assertEqual(values['482'], '2')
        self.assertEqual(values['478'], '换衣服')

    def test_invalid_inputs_rejected_before_upload(self):
        for updates in ({'images': []}, {'images': ['x'] * 7},
                        {'prompt': ' '}, {'count': 5}, {'count': True},
                        {'quality': '8K'}, {'aspect': 'custom'}):
            job = dict(prompt='edit', images=['x'], count=1, quality='2K', aspect='9:16')
            job.update(updates)
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                q.validate(job, check_files=False)

    def test_ambiguous_submission_blocks_second_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'state.json'
            client = Mock()
            client.submit.side_effect = TimeoutError('network')
            with self.assertRaises(RuntimeError):
                q.submit_once(client, state, {'nodeInfoList': []})
            self.assertEqual(q.read_json(state)['status'], 'SUBMIT_UNKNOWN')
            with self.assertRaises(FileExistsError):
                q.submit_once(client, state, {'nodeInfoList': []})
            self.assertEqual(client.submit.call_count, 1)

    def test_receipt_exists_before_submit_and_missing_id_is_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'state.json'
            client = Mock()
            def response(payload):
                self.assertEqual(q.read_json(state)['status'], 'SUBMITTING')
                return {'status': 'RUNNING'}
            client.submit.side_effect = response
            with self.assertRaises(RuntimeError):
                q.submit_once(client, state, {})
            self.assertEqual(q.read_json(state)['status'], 'SUBMIT_UNKNOWN')

    def test_resume_never_submits_and_downloads_all_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'state.json'
            q.write_json(state, {'taskId': 'task-1', 'status': 'SUBMITTED'})
            client = Mock()
            client.download.side_effect = lambda url, path: {'path': str(path), 'width': 1, 'height': 1}
            client.query.return_value = {'status': 'SUCCESS', 'usage': {'coins': 1},
                'results': [{'url': 'https://example.com/a.png', 'outputType': 'png'},
                            {'url': 'https://example.com/b.png', 'outputType': 'png'}]}
            q.resume(client, state, 0)
            client.submit.assert_not_called()
            self.assertEqual(client.download.call_count, 2)
            self.assertEqual(q.read_json(state)['usage'], {'coins': 1})

    def test_real_download_decodes_image_without_credentials(self):
        image = BytesIO()
        q.Image.new('RGB', (12, 8)).save(image, format='PNG')
        response = Mock()
        response.iter_content.return_value = [image.getvalue()]
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        with tempfile.TemporaryDirectory() as tmp, patch.object(q.requests, 'get', return_value=response) as get:
            result = q.Client('test-secret').download('https://example.com/image.png', Path(tmp) / 'result.png')
            self.assertEqual((result['width'], result['height']), (12, 8))
            self.assertNotIn('headers', get.call_args.kwargs)
            response.iter_content.return_value = [b'<html>error</html>']
            with self.assertRaises(Exception):
                q.Client('test-secret').download('https://example.com/error.png', Path(tmp) / 'error.png')
            self.assertFalse((Path(tmp) / 'error.png').exists())

    def test_api_no_redirect_retry_or_credential_echo(self):
        response = Mock(status_code=200)
        response.json.return_value = {'status': 'SUCCESS', 'message': 'test-secret'}
        with patch.object(q.requests, 'post', return_value=response) as post:
            data = q.Client('test-secret').query('123')
            self.assertEqual(data['message'], '[REDACTED]')
            self.assertFalse(post.call_args.kwargs['allow_redirects'])
            self.assertEqual(post.call_count, 1)

    def test_pending_timeout_keeps_task_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'state.json'
            q.write_json(state, {'taskId': 'task-2', 'status': 'SUBMITTED'})
            client = Mock()
            client.query.return_value = {'status': 'RUNNING'}
            with self.assertRaises(TimeoutError):
                q.resume(client, state, 0)
            self.assertEqual(q.read_json(state)['taskId'], 'task-2')
            client.submit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
