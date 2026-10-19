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

    def test_build_reference_job_and_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prompt = tmp/'prompt.txt'
            prompt.write_text('<Subject 1> 和 <Picture 2>。慢慢转身，镜头推近。')
            image = tmp/'image.png'; image.write_bytes(b'fixture')
            audio = tmp/'audio.wav'; audio.write_bytes(b'fixture')
            video = ROOT/'tests/real.mp4'
            jobs = tmp/'jobs.json'
            args = [sys.executable, str(ROOT/'scripts/build_jobs.py'), '--prompt-file', str(prompt),
                    '--output', str(jobs), '--image', str(image), '--audio', str(audio),
                    '--video', str(video), '--quality', '1080P', '--seconds', '5']
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            nodes = {(n['nodeId'],n['fieldName']):n['fieldValue']
                     for n in json.loads(jobs.read_text())['jobs'][0]['nodeInfoList']}
            self.assertEqual(json.loads(jobs.read_text())['jobs'][0]['appId'], '2084320751339032577')
            self.assertEqual(nodes[('147','value')], '2.0')
            self.assertEqual(nodes[('186','value')], '5')
            self.assertEqual(nodes[('163','value')], 'true')
            self.assertEqual(nodes[('159','strength_model')], '0')
            self.assertEqual(nodes[('141','image')], {'$upload': str(image.resolve())})
            self.assertEqual(nodes[('142','image')], 'None')
            self.assertEqual(nodes[('144','audio')], {'$upload': str(audio.resolve())})
            self.assertEqual(nodes[('164','video')], {'$upload': str(video)})
            env = {**os.environ, 'RUNNINGHUB_API_KEY': '',
                   'RUNNINGHUB_ENV_FILE': str(tmp/'nonexistent'),
                   'RUNNINGHUB_BASE_URL': 'http://127.0.0.1:1'}
            dry = subprocess.run([sys.executable, str(ROOT/'scripts/rh_minimax_h3.py'), str(jobs),
                                  '--dry-run', '--output', str(tmp/'out')],
                                 env=env, capture_output=True, text=True)
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertFalse((tmp/'out').exists())
            before = jobs.read_bytes()
            self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)
            self.assertEqual(jobs.read_bytes(), before)

    def test_mode_defaults_and_long_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prompt = tmp/'prompt.txt'
            prompt.write_text('陶杯在木桌上，窗光缓慢移动，镜头保持稳定。', encoding='utf-8')
            images = []
            for i in range(6):
                image = tmp/f'ref{i}.png'
                image.write_bytes(b'offline-fixture')
                images.extend(['--image', str(image)])
            for mode, seconds, aspect, instance in [('short', '15', '9:16', 'plus'),
                                                   ('long', '35', '16:9', 'default')]:
                jobs = tmp/f'{mode}.json'
                command = [sys.executable, str(ROOT/'scripts/build_jobs.py'), '--mode', mode,
                           '--prompt-file', str(prompt), '--output', str(jobs)]
                result = subprocess.run(command + (images if mode == 'long' else []),
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                job = json.loads(jobs.read_text())['jobs'][0]
                nodes = {(n['nodeId'], n['fieldName']): n['fieldValue'] for n in job['nodeInfoList']}
                self.assertEqual(job['instanceType'], instance)
                self.assertIs(job['usePersonalQueue'], False)
                if mode == 'long':
                    self.assertEqual(job['appId'], '2103012816681041921')
                    self.assertEqual(nodes[('59', 'prompt')], prompt.read_text())
                    self.assertEqual(nodes[('291', 'value')], seconds)
                    self.assertEqual(nodes[('426', 'megapixels')], '0.5')
                    self.assertTrue(nodes[('426', 'aspect_ratio')].startswith(aspect))
                    self.assertEqual(nodes[('481', 'value')], '1')
                    self.assertEqual(nodes[('393', 'value')], 'false')
                    self.assertEqual(nodes[('272', 'value')], 'false')
                    for node_id in ('446', '444', '443'):
                        self.assertEqual(nodes[(node_id, 'strength_model')], '0')
                    self.assertEqual(nodes[('442', 'text')], '')
                    for i, node_id in enumerate(('28', '273', '285', '436', '462', '463')):
                        self.assertEqual(nodes[(node_id, 'image')], {'$upload': str((tmp/f'ref{i}.png').resolve())})
                    self.assertNotIn(('150', 'value'), nodes)
                else:
                    self.assertEqual(nodes[('186', 'value')], seconds)
                    self.assertEqual(nodes[('147', 'value')], '0.9')
                    self.assertEqual(nodes[('192', 'value')], '8')
                    self.assertTrue(nodes[('115', 'aspect_ratio')].startswith(aspect))
                env = {**os.environ, 'RUNNINGHUB_API_KEY': '',
                       'RUNNINGHUB_ENV_FILE': str(tmp/'nonexistent'),
                       'RUNNINGHUB_BASE_URL': 'http://127.0.0.1:1'}
                dry = subprocess.run([sys.executable, str(ROOT/'scripts/rh_minimax_h3.py'),
                                      str(jobs), '--dry-run', '--output', str(tmp/'out')],
                                     env=env, capture_output=True, text=True)
                self.assertEqual(dry.returncode, 0, dry.stderr)
                self.assertIn(job['appId'], dry.stdout)
                self.assertFalse((tmp/'out').exists())

    def test_long_parameters_and_mode_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prompt = tmp/'prompt.txt'
            prompt.write_text('桌上的陶杯逐渐升起蒸汽。', encoding='utf-8')
            jobs = tmp/'long.json'
            base = [sys.executable, str(ROOT/'scripts/build_jobs.py'), '--mode', 'long',
                    '--prompt-file', str(prompt), '--output', str(jobs)]
            for invalid in [('--audio', 'absent.wav'), ('--video', 'absent.mp4'),
                            ('--steps', '8'), ('--quality', '720P'), ('--seconds', '0'),
                            ('--megapixels', 'nan'), ('--megapixels', 'inf'), ('--megapixels', '-1'),
                            ('--node-map', str(ROOT/'references/node_map.json'))]:
                with self.subTest(arguments=invalid):
                    result = subprocess.run(base + list(invalid), capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(jobs.exists())
            result = subprocess.run(base + ['--seconds', '40', '--megapixels', '0.7', '--aspect', '9:16'],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            nodes = {(n['nodeId'], n['fieldName']): n['fieldValue']
                     for n in json.loads(jobs.read_text())['jobs'][0]['nodeInfoList']}
            self.assertEqual(nodes[('291', 'value')], '40')
            self.assertEqual(nodes[('426', 'megapixels')], '0.7')
            self.assertEqual(nodes[('28', 'image')], 'None')
            # The default mode must still reject >15 seconds and the new mode's map.
            for extra in [('--seconds', '35'), ('--node-map', str(ROOT/'references/node_map_long.json'))]:
                result = subprocess.run([sys.executable, str(ROOT/'scripts/build_jobs.py'),
                                         '--prompt-file', str(prompt), '--output', str(tmp/'short.json'),
                                         *extra], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((tmp/'short.json').exists())


if __name__ == '__main__':
    unittest.main()
