"""Regression tests for explicit photography decisions surviving composition."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/compose.py'


def sample(mode='third-person'):
    return {'摄影设计': {
        '版本': '1.0', '分享重点': '抬眼与蓝袖框脸',
        '相机': {'拍摄关系': mode, '摄影者位置': '高于坐姿头顶向下拍',
                 '距离与透视': '近距离，脸近膝远', '画幅边界': '发顶至弯膝，手肘贴左边'},
        '人物': {'身份依据': '成年模特参考', '妆发穿搭': '蓝袖黑发',
                 '姿态与支撑': '坐稳，左手绕头', '视线与表情': '抬眼轻笑'},
        '空间层次': '前景袖，人物，深色地板',
        '光线': '左侧日光，右颊留暗', '明暗与颜色': '蓝袖衬灰地面',
        '成像质感': '眼睛清晰，皮肤柔和，少量发丝亮点',
        '成功条件': ['高位俯拍', '双眼可见', '袖臂弧线'],
        '参考分工': []}}


class ComposeTest(unittest.TestCase):
    def run_cli(self, card, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args],
            input=json.dumps(card, ensure_ascii=False), text=True, capture_output=True)

    def test_photography_keeps_angle_and_actual_resolution(self):
        r = self.run_cli(sample(), 'third-person', '--photography', '--resolution', '1K')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('高于坐姿头顶', r.stdout)
        self.assertIn('1K', r.stdout)
        for default in ['原生 4K', '平视或轻微低机位为主', '不磨皮', '自动测光', '不刻意摆拍']:
            self.assertNotIn(default, r.stdout)

    def test_all_relationships_and_json_only(self):
        for mode in ['third-person', 'front-camera-selfie', 'mirror-selfie', 'ecommerce-editorial']:
            with self.subTest(mode=mode):
                r = self.run_cli(sample(mode), mode, '--photography', '--json-only')
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(json.loads(r.stdout), sample(mode))

    def test_missing_field_and_relationship_mismatch_fail(self):
        card = sample(); del card['摄影设计']['光线']
        r = self.run_cli(card, 'third-person', '--photography')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('光线', r.stderr)
        r = self.run_cli(sample('mirror-selfie'), 'third-person', '--photography')
        self.assertNotEqual(r.returncode, 0)

    def test_empty_and_wrong_types_fail(self):
        for field, value in [('光线', ''), ('成功条件', ['']), ('参考分工', '图1')]:
            card = sample(); card['摄影设计'][field] = value
            r = self.run_cli(card, 'third-person', '--photography')
            self.assertNotEqual(r.returncode, 0)

    def test_reference_order_and_rendered_roles(self):
        card = sample()
        card['摄影设计']['参考分工'] = [{'图号': 1, '负责': '身份', '保留': '脸型', '调整': '妆造'}]
        r = self.run_cli(card, 'third-person', '--photography')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('图1负责身份', r.stdout)
        for bad in [0, 2, True]:
            card['摄影设计']['参考分工'][0]['图号'] = bad
            self.assertNotEqual(self.run_cli(card, 'third-person', '--photography').returncode, 0)

    def test_conflicting_reference_option_also_rejected_for_json_only(self):
        r = self.run_cli(sample(), 'third-person', '--photography', '--json-only',
                         '--reference-rules-file', 'unused.md')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('参考分工', r.stderr)

    def test_duplicate_json_fields_are_rejected_in_photography(self):
        text = json.dumps(sample(), ensure_ascii=False).replace('"光线":', '"光线":"冲突光", "光线":')
        r = subprocess.run([sys.executable, str(SCRIPT), 'third-person', '--photography'],
                           input=text, text=True, capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('Duplicate', r.stderr)

    def test_legacy_output_is_identical(self):
        for mode in ['third-person', 'front-camera-selfie', 'mirror-selfie', 'ecommerce-editorial']:
            with self.subTest(mode=mode):
                folder = ROOT / 'references/json-prompt-system/modes' / mode
                card = json.loads((folder/'mode_template.txt').read_text())
                r = self.run_cli(card, mode)
                expected = (folder/'fixed.md').read_text()
                expected = expected.replace('{{RATIO}}', '3:4').replace('{{PROFILE_PROMPT}}', '')
                expected = expected.replace('{{REFERENCE_RULES}}', '本次无参考图，依据人物档案、任务设定与下方 JSON 生成。')
                expected = expected.replace('{{ACTION_JSON}}', json.dumps(card, ensure_ascii=False, indent=2))
                self.assertEqual(r.stdout, expected + '\n')
                self.assertEqual(r.returncode, 0, r.stderr)
                raw = self.run_cli(card, mode, '--json-only')
                self.assertEqual(raw.returncode, 0, raw.stderr)
                self.assertEqual(json.loads(raw.stdout), card)

    def test_literal_placeholder_is_not_replaced_in_card(self):
        card = sample(); card['摄影设计']['分享重点'] = '保留字面 {{RATIO}}'
        r = self.run_cli(card, 'third-person', '--photography')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('{{RATIO}}', r.stdout)


if __name__ == '__main__':
    unittest.main()
