#!/usr/bin/env python3
"""Validate the camera-to-scene projection gate in a shot fact card."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass


FIELDS = [
    "证据帧",
    "摄影机",
    "人物姿态拓扑",
    "人物接触与遮挡",
    "主导可见表面",
    "表面分布",
    "地墙交界 / 地平线",
    "消失方向与地面纹理收缩",
    "场景资产映射",
    "资产原视角级别",
    "空间边界",
    "当前机位允许出现",
    "当前机位禁止出现",
    "高影响不确定项",
]

UNRESOLVED = {"", "待填写", "未知", "未分析", "tbd", "todo", "...", "…"}


@dataclass
class Result:
    ok: bool
    blocked: bool
    errors: list[str]


def field_value(text: str, label: str) -> str | None:
    match = re.search(rf"^-\s*{re.escape(label)}\s*[：:]\s*(.*?)\s*$", text, flags=re.M)
    return None if match is None else match.group(1).strip()


def validate(text: str) -> Result:
    errors: list[str] = []
    if not re.search(r"^##\s+镜头—场景投影\s*$", text, flags=re.M):
        errors.append("缺少二级标题：镜头—场景投影")

    values: dict[str, str] = {}
    for label in FIELDS:
        value = field_value(text, label)
        if value is None:
            errors.append(f"缺少投影字段：{label}")
            continue
        values[label] = value
        if value.lower() in UNRESOLVED:
            errors.append(f"投影字段未填写：{label}")

    blocked = False
    uncertainty = values.get("高影响不确定项", "")
    if uncertainty and not re.match(r"^(无|没有|none)\b", uncertainty, flags=re.I):
        blocked = True

    return Result(not errors and not blocked, blocked, errors)


def main() -> int:
    text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 and sys.argv[1] != "-" else sys.stdin.read()
    result = validate(text)
    if result.errors:
        print("FAIL")
        for error in result.errors:
            print("-", error)
        return 1
    if result.blocked:
        print("BLOCKED")
        print("- 高影响不确定项尚未清零：必须先获得用户确认，禁止进入生成阶段。")
        return 2
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
