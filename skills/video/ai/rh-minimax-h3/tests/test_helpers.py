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


if __name__ == '__main__':
    unittest.main()
