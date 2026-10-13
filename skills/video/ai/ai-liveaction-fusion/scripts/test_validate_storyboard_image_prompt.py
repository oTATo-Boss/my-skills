#!/usr/bin/env python3
from validate_storyboard_image_prompt import validate

GOOD = """# 图像编辑指令
执行背景替换。
# 当前素材锁定
@原图 负责构图。
# 画面质感
真人影视质感。
# 单帧画面
## 构图与景别
保持近景。
## 背景与空间
门外夜景。
## 空间透视与镜头匹配
远景退焦。
## 光源与融合
冷背光与暖面光。
## 最终画面
人物站在门口。
## VFX
清除技术字。
"""

cases = [
    ("good", GOOD, True),
    ("missing", GOOD.replace("## VFX\n清除技术字。\n", ""), False),
    ("wrong_order", GOOD.replace("## 背景与空间", "## 临时").replace("## 构图与景别", "## 背景与空间").replace("## 临时", "## 构图与景别"), False),
    ("placeholder", GOOD.replace("执行背景替换。", "[声明唯一底图]"), False),
]

for name, text, expected in cases:
    result = validate(text)
    if result.ok != expected:
        raise SystemExit(f"{name}: expected {expected}, got {result.ok}; {result.errors}")

print("ALL STORYBOARD TESTS PASSED")
