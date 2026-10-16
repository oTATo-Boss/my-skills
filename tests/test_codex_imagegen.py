"""Offline behavioral checks; never call a real image service."""
from concurrent.futures import ThreadPoolExecutor
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / 'skills/image/codex-imagegen/scripts/gen_image.py'
spec = importlib.util.spec_from_file_location('gen_image', PATH)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
PNG = b'\x89PNG\r\n\x1a\n' + b'\x00\x00\x00\rIHDR' + (1).to_bytes(4,'big') * 2


class ImageBridgeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='image bridge 测试 ')
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def source(self, name='generated.png'):
        p = self.root / name
        p.write_bytes(PNG)
        return p

    def test_exclusive_publish_preserves_existing_and_races(self):
        source = self.source()
        out = self.root / 'image_01.png'
        out.write_bytes(b'original')
        with ThreadPoolExecutor(max_workers=4) as workers:
            outputs = list(workers.map(lambda _: bridge.publish_without_overwrite(source, out), range(8)))
        self.assertEqual(out.read_bytes(), b'original')
        self.assertEqual(len(set(outputs)), 8)
        self.assertTrue(all(p.read_bytes() == PNG for p in outputs))

    def test_recovery_requires_explicit_fresh_owned_result(self):
        image = self.source()
        last = self.root / 'last.txt'
        last.write_text(str(image), encoding='utf-8')
        self.assertEqual(bridge.recover_explicit_result(last, self.root, time.time()), image.resolve())
        os.utime(image, (1, 1))
        self.assertIsNone(bridge.recover_explicit_result(last, self.root, time.time()))
        last.write_text('result\n' + str(image), encoding='utf-8')
        self.assertIsNone(bridge.recover_explicit_result(last, self.root, 0))
        last.write_text('generated.png', encoding='utf-8')
        self.assertIsNone(bridge.recover_explicit_result(last, self.root, 0))

    def test_does_not_scan_newer_unrelated_images(self):
        self.source('unrelated.png')
        self.assertIsNone(bridge.recover_explicit_result(self.root / 'missing.txt', self.root, 0))

    def test_rejects_output_escape_and_non_png(self):
        for name in ('../outside.png', 'file.jpg'):
            args = bridge.parser().parse_args(['--out', name])
            with self.assertRaises(bridge.ImagegenError):
                bridge.requested_output(args, self.root)
        args = bridge.parser().parse_args(['--slug', '../../escape'])
        self.assertTrue(bridge.within(bridge.requested_output(args, self.root), self.root))

    def test_rejects_symlink_output_escape(self):
        with tempfile.TemporaryDirectory() as other:
            try:
                (self.root / 'link').symlink_to(other, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('host does not permit directory symlinks')
            args = bridge.parser().parse_args(['--out', 'link/image.png'])
            with self.assertRaises(bridge.ImagegenError):
                bridge.requested_output(args, self.root)

    def fake_codex(self, command, **kwargs):
        if command[1:] == ['--version']:
            return subprocess.CompletedProcess(command, 0, 'codex test\n', '')
        if command[1:] == ['login', 'status']:
            return subprocess.CompletedProcess(command, 0, '', 'Logged in using ChatGPT\n')
        if command[1:] == ['features', 'list']:
            return subprocess.CompletedProcess(command, 0, 'image_generation stable true\n', '')
        if command[1:] == ['exec', '--help']:
            return subprocess.CompletedProcess(command, 0, '--sandbox workspace-write --output-last-message --skip-git-repo-check', '')
        self.assertEqual(command[command.index('-s') + 1], 'workspace-write')
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', command)
        last = Path(command[command.index('-o') + 1])
        result = last.parent / 'generated.png'
        result.write_bytes(PNG)
        last.write_text(str(result), encoding='utf-8')
        self.assertIn('中文 prompt with `literal` $value', kwargs['input'])
        return subprocess.CompletedProcess(command, 0)

    def test_mock_cli_unicode_prompt_output_and_receipt(self):
        prompt = self.root / '提示词.txt'
        prompt.write_text('中文 prompt with `literal` $value', encoding='utf-8')
        capture = io.StringIO()
        with patch.object(bridge, 'find_codex', return_value='codex'), \
             patch.object(bridge.subprocess, 'run', side_effect=self.fake_codex), \
             contextlib.redirect_stdout(capture):
            result = bridge.main(['--workdir', str(self.root), '--prompt-file', str(prompt)])
        self.assertEqual(result, 0)
        lines = capture.getvalue().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertTrue(bridge.is_png(Path(lines[0])))
        receipt = json.loads(next((self.root / '.codex-imagegen').rglob('receipt.json')).read_text())
        self.assertEqual(receipt['actual_generation'], 'output-returned-needs-visual-review')

    def test_failed_capability_never_executes_generation(self):
        capture, error = io.StringIO(), io.StringIO()
        def disabled(command, **kwargs):
            if command[1:] == ['features', 'list']:
                return subprocess.CompletedProcess(command, 0, 'image_generation stable false\n', '')
            return self.fake_codex(command, **kwargs)
        with patch.object(bridge, 'find_codex', return_value='codex'), \
             patch.object(bridge.subprocess, 'run', side_effect=disabled) as runner, \
             contextlib.redirect_stdout(capture), contextlib.redirect_stderr(error):
            result = bridge.main(['--workdir', str(self.root)])
        self.assertEqual(result, 1)
        self.assertEqual(runner.call_count, 4)
        self.assertEqual(capture.getvalue(), '')
        self.assertIn('Preflight failed', error.getvalue())
        self.assertFalse((self.root / '.codex-imagegen').exists())

    def test_bad_image_and_unavailable_tool_do_not_publish(self):
        prompt = self.root / 'prompt.txt'
        prompt.write_text('test', encoding='utf-8')
        def unavailable(command, **kwargs):
            if command[1] == 'exec' and '--help' not in command:
                last = Path(command[command.index('-o') + 1])
                last.write_text('IMAGEGEN_UNAVAILABLE', encoding='utf-8')
                return subprocess.CompletedProcess(command, 0)
            return self.fake_codex(command, **kwargs)
        with patch.object(bridge, 'find_codex', return_value='codex'), \
             patch.object(bridge.subprocess, 'run', side_effect=unavailable), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(bridge.main(['--workdir', str(self.root), '--prompt-file', str(prompt)]), 1)
        self.assertEqual(list((self.root / 'outputs').glob('*.png')), [])
        self.assertFalse(bridge.is_png(prompt))


if __name__ == '__main__':
    unittest.main()
