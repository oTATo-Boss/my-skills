#!/usr/bin/env python3
"""Validate the fixed static storyboard image-prompt contract."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass

TOP = ["图像编辑指令", "当前素材锁定", "画面质感", "单帧画面"]
SUB = ["构图与景别", "背景与空间", "空间透视与镜头匹配", "光源与融合", "最终画面", "VFX"]


@dataclass
class Result:
    ok: bool
    errors: list[str]


def validate(text: str) -> Result:
    errors: list[str] = []
    top = re.findall(r"^#\s+(.+?)\s*$", text, flags=re.M)
    sub = re.findall(r"^##\s+(.+?)\s*$", text, flags=re.M)
    if top != TOP:
        errors.append("一级标题必须严格为：" + " → ".join(TOP))
    if sub != SUB:
        errors.append("单帧画面二级标题必须严格为：" + " → ".join(SUB))
    if len(set(top)) != len(top) or len(set(sub)) != len(sub):
        errors.append("标题不得重复。")
    if "# 单帧画面" in text:
        before, after = text.split("# 单帧画面", 1)
        if re.search(r"^##\s+", before, flags=re.M):
            errors.append("二级标题只能位于“单帧画面”之后。")
        if not after.strip():
            errors.append("“单帧画面”不得为空。")
    for token in ["[声明", "[逐项", "[写当前", "[只写", "[用结果", "[列出"]:
        if token in text:
            errors.append("存在未清理的模板说明占位文本。")
            break
    return Result(not errors, errors)


def main() -> int:
    text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 and sys.argv[1] != "-" else sys.stdin.read()
    result = validate(text)
    print("PASS" if result.ok else "FAIL")
    for error in result.errors:
        print("-", error)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
