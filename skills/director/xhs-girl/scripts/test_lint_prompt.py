"""Behavioral checks for the mechanical prompt linter."""
import importlib.util
from pathlib import Path
import unittest

ENGINE = Path(__file__).with_name("lint_prompt.py")

GOOD_ZH = (
    "3:4竖幅，图1保持她的五官、脸型、原肤色和发型，其余造型按本次设计。朋友拿手机在她右前方齐胸高度近距拍，"
    "取景从头顶到大腿中部。她坐在洗衣房折叠台边缘，重心落在左侧臀部，左手撑着台面，右手刚把一件叠好的白T恤"
    "放进藤编筐，肩线向镜头一侧打开，腰侧显出一段柔和弧线。她转回头，眼睛直视镜头，眼尾微微弯起，嘴角一侧先笑，"
    "唇中间有一点水光。面中透着蜜桃色腮红，鼻尖和颧骨有细小高光，耳侧几缕碎发落在银色小耳圈前。她穿浅灰罗纹"
    "短款开衫，前两颗扣子没扣，露出白色细肩带内搭的蕾丝边，下身是深蓝高腰直筒牛仔裤，裤腰贴合，膝盖处有自然折痕。"
    "台面上有半瓶洗衣液、一卷没撕完的烘干纸和她的手机，筐边搭着一只袜子。身后两台滚筒洗衣机一台正在转，圆窗里"
    "能看到翻滚的毛巾，墙上贴着手写的使用时间表，远处一个人背对镜头在取衣服，不露正脸。顶上的日光灯管从她左上方"
    "照下来，混合门口进来的下午日光从右侧打亮脸和肩，台面上留下她手臂的短影。手机主摄近距透视，小底深景深，"
    "背景洗衣机和时间表清晰可辨并随距离自然减弱，保留真实肤质纹理和轻微的手机直出颗粒，整体色彩清爽干净，"
    "灰、白、深蓝之间有明确层次，人物比背景更亮更醒目，不做奶油虚化。"
)


class LintPromptTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("lint_prompt", ENGINE)
        self.engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.engine)

    def test_specific_prompt_passes(self):
        fails, _ = self.engine.lint(GOOD_ZH)
        self.assertEqual(fails, [])

    def test_banned_words_fail_but_negated_forms_pass(self):
        fails, _ = self.engine.lint(GOOD_ZH + " cinematic, 8k masterpiece")
        self.assertTrue(any("禁用词" in f for f in fails))
        self.assertEqual(self.engine.find_banned("zero creamy bokeh, 无奶油虚化"), [])
        self.assertIn("bokeh", self.engine.find_banned("soft creamy bokeh background"))

    def test_self_containment_and_body_rules_fail(self):
        fails, _ = self.engine.lint(GOOD_ZH.replace("3:4竖幅", "3:4竖幅，其余同上，保持原身材比例"))
        self.assertTrue(any("身材" in f for f in fails))

    def test_leftover_template_labels_fail(self):
        fails, _ = self.engine.lint("【1 输入与身份】" + GOOD_ZH)
        self.assertTrue(any("占位符" in f for f in fails))

    def test_missing_light_direction_and_eyes_fail(self):
        fails, _ = self.engine.lint("她站在店里穿白裙。" * 40)
        joined = " ".join(fails)
        self.assertIn("光源", joined)
        self.assertIn("眼睛", joined)
        self.assertIn("拍", joined)

    def test_length_bounds(self):
        fails, _ = self.engine.lint("手机拍，眼睛直视，左侧窗光，景深。")
        self.assertTrue(any("长度" in f for f in fails))
        fails, _ = self.engine.lint(GOOD_ZH * 3)
        self.assertTrue(any("长度" in f for f in fails))

    def test_vague_labels_warn(self):
        _, warns = self.engine.lint(GOOD_ZH + "精致妆容，氛围感。")
        self.assertTrue(any("空泛" in w for w in warns))


if __name__ == "__main__":
    unittest.main()
