"""Regression tests for user-visible shot-plan contracts; no image generation."""
import re
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('plan_set.py')


def run_plan(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


class PlanTests(unittest.TestCase):
    def test_post_keeps_one_scene_even_for_location_specific_types(self):
        result = run_plan('--seed', '3', '--type', '隔桌对拍', '--count', '3')
        self.assertEqual(result.returncode, 0, result.stderr)
        scenes = re.findall(r'^- 场景：([^（\n]+)', result.stdout, re.M)
        self.assertEqual(len(scenes), 4)
        self.assertEqual(len(set(scenes)), 1, scenes)

    def test_explicit_scene_survives_mixed_mode(self):
        result = run_plan('--seed', '2', '--mode', 'mixed', '--scene', '用户指定的同一间房', '--count', '4')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(re.findall(r'^- 场景：([^\n]+)', result.stdout, re.M), ['用户指定的同一间房'] * 4)

    def test_post_keeps_one_finish(self):
        result = run_plan('--seed', '8', '--type', '直闪夜拍', '--count', '3')
        self.assertEqual(result.returncode, 0, result.stderr)
        finishes = re.findall(r'^- 后期：([^（\n]+)', result.stdout, re.M)
        self.assertEqual(len(set(finishes)), 1, finishes)

    def test_close_up_does_not_request_legs_or_waist(self):
        for seed in range(8):
            result = run_plan('--seed', str(seed), '--focus', 'outfit', '--type', '怼脸自拍', '--count', '1')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotRegex(result.stdout, r'展示重点：(长腿|腰线|整体比例|背部|上围曲线)')

    def test_summer_six_images_does_not_exhaust_props(self):
        result = run_plan('--seed', '9', '--month', '7', '--count', '6')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(re.findall(r'^## 第 ', result.stdout, re.M)), 6)

    def test_invalid_inputs_fail_clearly(self):
        for args in [('--count', '0'), ('--month', '13'), ('--type', '不存在'),
                     ('--type', '怼脸自拍', '--type', '怼脸自拍')]:
            result = run_plan(*args)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertNotIn('Traceback', result.stderr)

    def test_look_only_does_not_depend_on_shot_count(self):
        result = run_plan('--look-only', '--count', '100', '--seed', '2')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('## 第 ', result.stdout)

    def test_known_scene_rejects_incompatible_forced_type(self):
        result = run_plan('--scene', '海边沙滩', '--type', '镜前自拍')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
