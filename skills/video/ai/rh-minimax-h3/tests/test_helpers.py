#!/usr/bin/env python3
"""Offline behavior tests; private configuration isolated in temporary directories."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('credentials', ROOT/'scripts/credentials.py')
credentials = importlib.util.module_from_spec(spec)
spec.loader.exec_module(credentials)


class Helpers(unittest.TestCase):
    def test_secret_storage_and_priority(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)/'private/.env'
            key = 'offline-secret-12345'
            credentials.store_key(key, dest)
            self.assertEqual(dest.stat().st_mode & 0o777, 0o600)
            self.assertEqual(credentials.read_key(dest), key)
            with self.assertRaises(ValueError):
                credentials.store_key('replacement', dest)
            env = {**os.environ, 'RUNNINGHUB_ENV_FILE': str(dest), 'RUNNINGHUB_API_KEY': ''}
            result = subprocess.run([sys.executable, str(ROOT/'scripts/credentials.py'), 'status'],
                                    env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn('已配置', result.stdout)
            self.assertNotIn(key, result.stdout + result.stderr)
            with patch.dict(os.environ, env):
                self.assertEqual(credentials.configured_api_key(), key)
                os.environ['RUNNINGHUB_API_KEY'] = 'override'
                self.assertEqual(credentials.configured_api_key(), 'override')
            source = Path(tmp)/'project.env'
            source.write_text('OTHER=untouched\nexport RUNNINGHUB_API_KEY="import-secret"\n')
            result = subprocess.run([sys.executable, str(ROOT/'scripts/credentials.py'),
                                     'import-env', '--from-env', str(source),
                                     '--env-file', str(dest), '--replace'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(credentials.read_key(dest), 'import-secret')
            self.assertIn('OTHER=untouched', source.read_text())
            self.assertNotIn('import-secret', result.stdout + result.stderr)

    def test_job_defaults_and_1080p(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prompt = tmp/'prompt.txt'; prompt.write_text('A cup rotates slowly.', encoding='utf-8')
            image = tmp/'image.png'; image.write_bytes(b'fixture')
            audio = tmp/'audio.wav'; audio.write_bytes(b'fixture')
            base = [sys.executable, str(ROOT/'scripts/build_jobs.py'), '--prompt-file', str(prompt),
                    '--seconds', '5', '--aspect', '1:1', '--image', str(image)]
            for quality, instance, mp in [(None, 'plus', '1.0'), ('1080P', 'ultra', '2.0')]:
                jobs = tmp/f'{quality or "default"}.json'
                command = base + ['--output', str(jobs), '--audio', str(audio)]
                if quality:
                    command += ['--quality', quality]
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                job = json.loads(jobs.read_text())['jobs'][0]
                nodes = {(n['nodeId'], n['fieldName']): n['fieldValue'] for n in job['nodeInfoList']}
                self.assertEqual(job['appId'], '2104753059472990209')
                self.assertEqual(job['instanceType'], instance)
                self.assertEqual(nodes[('462', 'megapixels')], mp)
                self.assertEqual(nodes[('894', 'value')], 'true')
                self.assertEqual(nodes[('824', 'value')], 'false')
                self.assertEqual(nodes[('827', 'value')], '1')
                self.assertEqual(nodes[('438', 'image')], {'$upload': str(image.resolve())})
                self.assertEqual(nodes[('435', 'image')], {'$upload': str(image.resolve())})
                self.assertEqual(nodes[('429', 'image')], {'$upload': str(image.resolve())})
                self.assertEqual(nodes[('841', 'audio')], {'$upload': str(audio.resolve())})
                self.assertEqual(nodes[('813', 'strength_model')], '0.4000000000000001')
                self.assertEqual(nodes[('817', 'strength_model')], '0.5000000000000001')
                self.assertEqual(nodes[('815', 'strength_model')], '0.6000000000000001')
                self.assertEqual(nodes[('816', 'text')], 'dynv2,')
                dry = subprocess.run([sys.executable, str(ROOT/'scripts/rh_minimax_h3.py'), str(jobs),
                                      '--dry-run', '--output', str(tmp/'out')],
                                     capture_output=True, text=True)
                self.assertEqual(dry.returncode, 0, dry.stderr)
                self.assertIn('待上传素材 2 个', dry.stdout)
                self.assertFalse((tmp/'out').exists())
            result = subprocess.run(base + ['--output', str(tmp/'bad.json'), '--quality', '1080P',
                                             '--instance', 'plus'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((tmp/'bad.json').exists())

    def test_explicit_fields_and_optional_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prompt = tmp/'prompt.txt'; prompt.write_text('test', encoding='utf-8')
            image = tmp/'image.png'; image.write_bytes(b'fixture')
            base = [sys.executable, str(ROOT/'scripts/build_jobs.py'), '--prompt-file', str(prompt),
                    '--output', str(tmp/'job.json')]
            for extra in [[], ['--seconds', '5', '--aspect', '1:1'],
                          ['--seconds', '31', '--aspect', '1:1', '--image', str(image)],
                          ['--seconds', '5', '--aspect', '1:1', '--image', str(image), '--video', 'x']]:
                self.assertNotEqual(subprocess.run(base + extra, capture_output=True).returncode, 0)
            result = subprocess.run(base + ['--seconds', '30', '--aspect', '16:9', '--image', str(image),
                                             '--auto-prompt', 'off', '--output-format', 'zip',
                                             '--lora-1-strength', '0', '--lora-trigger', ''],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            nodes = {(n['nodeId'], n['fieldName']): n['fieldValue']
                     for n in json.loads((tmp/'job.json').read_text())['jobs'][0]['nodeInfoList']}
            self.assertEqual(nodes[('804', 'value')], '30')
            self.assertEqual(nodes[('435', 'image')], 'None')
            self.assertEqual(nodes[('894', 'value')], 'false')
            self.assertEqual(nodes[('824', 'value')], 'true')
            self.assertEqual(float(nodes[('813', 'strength_model')]), 0)
            self.assertEqual(nodes[('816', 'text')], '')

    def test_reject_old_app_and_high_resolution_on_plus(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for index, job in enumerate([
                {'name': 'old', 'appId': '2084320751339032577', 'nodeInfoList': [{'nodeId':'150','fieldName':'value','fieldValue':'x'}]},
                {'name': 'noid', 'nodeInfoList': [{'nodeId':'150','fieldName':'value','fieldValue':'x'}]},
                {'name': 'bad', 'appId': '2104753059472990209', 'instanceType': 'plus', 'nodeInfoList': [{'nodeId':'462','fieldName':'megapixels','fieldValue':'2'}]},
            ]):
                file = tmp/f'{index}.json'; file.write_text(json.dumps({'jobs':[job]}))
                dry = subprocess.run([sys.executable, str(ROOT/'scripts/rh_minimax_h3.py'), str(file), '--dry-run',
                                      '--output', str(tmp/'out')], capture_output=True, text=True)
                self.assertNotEqual(dry.returncode, 0)
                self.assertFalse((tmp/'out').exists())


if __name__ == '__main__':
    unittest.main()
