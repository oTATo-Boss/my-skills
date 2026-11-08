import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from io import BytesIO
import threading
import sys
import time

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'rh_krea2.py'
spec = importlib.util.spec_from_file_location('rh_krea2', SCRIPT)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


class KreaTests(unittest.TestCase):
    def test_recovery_cli_updates_original_receipt_and_reserved_slot(self):
        import subprocess, os, json
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = root/'unknown.json'
            q.write_json(receipt, {'appId': '2080156609159286785', 'status': 'SUBMIT_UNKNOWN'})
            with patch.object(sys, 'path', [str(SCRIPT.parent), *sys.path]):
                from rh_queue import Queue
                queue = Queue('offline-recovery', root=root/'queue')
                queue.acquire(str(receipt.resolve()), wait=0)
                env = {**os.environ, 'RUNNINGHUB_API_KEY': 'offline-recovery', 'RH_QUEUE_DIR': str(root/'queue')}
                command = [sys.executable, str(SCRIPT.parent/'rh_queue.py'), '--receipt', str(receipt), '--task-id', 'verified-123']
                result = subprocess.run(command, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(q.read_json(receipt)['taskId'], 'verified-123')
                self.assertEqual(queue.snapshot()[str(receipt.resolve())]['taskId'], 'verified-123')
                command[-1] = 'different-456'
                result = subprocess.run(command, env=env, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(q.read_json(receipt)['taskId'], 'verified-123')

    def test_app_request_uses_screenshot_models_and_latest_defaults(self):
        payload = q.payload_for({'prompt': 'Change the cup to blue', 'images': ['cup.png']}, ['uploaded.png'])
        fields = {(n['nodeId'], n['fieldName']): n['fieldValue'] for n in payload['nodeInfoList']}
        self.assertEqual(len(fields), 14)
        expected = {
            ('72', 'image'): 'uploaded.png', ('99', 'text'): 'Change the cup to blue',
            ('130', 'unet_name'): 'FinePorn_V6.1_INT8_20261105.safetensors',
            ('133', 'lora_name'): 'realism_engine_krea2_v3.1_new.safetensors',
            ('133', 'strength_model'): '0.4',
            ('145', 'lora_name'): 'Krea-2-Turbo-HTT_c1-st10000.safetensors',
            ('145', 'strength_model'): '0.4', ('142', 'value'): 'true',
            ('83', 'aspect_ratio'): '9:16 (Portrait Widescreen)',
            ('141', 'value'): '1.0', ('131', 'value'): '2.25',
            ('132', 'strength_model'): '0', ('105', 'value'): '1', ('119', 'value'): 'false'}
        self.assertEqual(fields, expected)
        self.assertEqual(payload['instanceType'], 'default')
        response = Mock(status_code=200)
        response.json.return_value = {'taskId': 'new-app-task', 'status': 'RUNNING'}
        with patch.object(q.requests, 'post', return_value=response) as post:
            q.Client('offline-secret').submit(payload)
            self.assertEqual(post.call_args.args[0], 'https://www.runninghub.ai/openapi/v2/run/ai-app/2080156609159286785')

    def test_explicit_ratio_enables_switch_and_reference_strength(self):
        job = dict(prompt='A blue cup', images=['cup.png'], aspect='4:3',
                   megapixels=2, reference_strength=6, count=3, instance='plus')
        payload = q.payload_for(job, ['up.png'])
        fields = {(n['nodeId'], n['fieldName']): n['fieldValue'] for n in payload['nodeInfoList']}
        self.assertEqual(fields[('142', 'value')], 'true')
        self.assertEqual(fields[('83', 'aspect_ratio')], '4:3 (Standard)')
        self.assertEqual(float(fields[('131', 'value')]), 6)
        self.assertEqual(float(fields[('141', 'value')]), 2)
        self.assertEqual(fields[('105', 'value')], '3')
        self.assertEqual(payload['instanceType'], 'plus')
        original = q.payload_for(dict(job, aspect='original'), ['up.png'])
        fields = {(n['nodeId'], n['fieldName']): n['fieldValue'] for n in original['nodeInfoList']}
        self.assertEqual(fields[('142', 'value')], 'false')

    def test_input_errors_are_rejected_before_upload(self):
        job = dict(prompt='Blue cup', images=['cup.png'])
        q.validate(job, check_files=False)
        for updates in ({'images': []}, {'images': ['a', 'b']}, {'prompt': ' '},
                        {'reference_strength': 0.9}, {'reference_strength': 6.1},
                        {'reference_strength': True}, {'reference_strength': float('nan')},
                        {'megapixels': 0}, {'megapixels': float('inf')},
                        {'count': True}, {'count': 5}, {'aspect': 'custom'},
                        {'quality': '2K'}, {'instance': 'invalid'}, {'seed': 123}):
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                q.validate(dict(job, **updates), check_files=False)

    def test_cli_offline_relative_image_and_batch(self):
        import subprocess, os, json
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            q.Image.new('RGB', (12, 8)).save(root / 'cup.png')
            job = root / 'job.json'
            for content in ({'prompt': 'Blue cup', 'images': ['cup.png']},
                            {'jobs': [{'prompt': 'Blue cup', 'images': ['cup.png']}]}):
                job.write_text(json.dumps(content))
                result = subprocess.run([sys.executable, str(SCRIPT), str(job), '--dry-run'],
                    cwd='/', env={**os.environ, 'RUNNINGHUB_API_KEY': '', 'RUNNINGHUB_ENV_FILE': str(root/'missing.env')},
                    capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                data = json.loads(result.stdout)
                self.assertEqual(data['appId'], '2080156609159286785')
                self.assertFalse((root/'missing.env').exists())

    def test_batch_starts_three_and_refills_while_downloading(self):
        lock = threading.Lock()
        first_three = threading.Event()
        state = {'active': 0, 'peak': 0, 'submitted': 0, 'downloads_done': 0,
                 'fourth_during_download': False}
        class FakeClient:
            def __init__(self, key): self.key = key
            def upload(self, filename): return 'uploaded.png'
            def submit(self, payload):
                with lock:
                    state['active'] += 1
                    state['peak'] = max(state['peak'], state['active'])
                    state['submitted'] += 1
                    number = state['submitted']
                    if number == 3: first_three.set()
                    if number == 4: state['fourth_during_download'] = state['downloads_done'] < 3
                return {'taskId': str(number), 'status': 'RUNNING'}
            def query(self, task_id):
                if not first_three.wait(3): raise RuntimeError('tasks ran serially')
                with lock: state['active'] -= 1
                return {'status': 'SUCCESS', 'results': [{'url':'https://example.com/result.png','outputType':'png'}]}
            def download(self, url, destination):
                time.sleep(0.2)
                with lock: state['downloads_done'] += 1
                return {'path':str(destination),'width':1,'height':1}
        with tempfile.TemporaryDirectory() as tmp, patch.dict(q.os.environ, {'RH_QUEUE_DIR': tmp+'/queue'}), \
                patch.object(q, 'Client', FakeClient), patch.object(q, 'configured_key', return_value='offline'), \
                patch.object(sys, 'path', [str(SCRIPT.parent), *sys.path]):
            jobs = [dict(name=f'job-{i}', prompt='edit', images=['unused.png']) for i in range(5)]
            result = q.run_batch(jobs, Path(tmp)/'output', 5)
            self.assertEqual(len(result), 5)
            self.assertEqual(state['peak'], 3)
            self.assertTrue(state['fourth_during_download'])

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
