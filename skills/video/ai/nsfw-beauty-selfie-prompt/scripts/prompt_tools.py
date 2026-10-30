#!/usr/bin/env python3
"""prompt_tools.py — nsfw-beauty-selfie-prompt 轻量结构门禁。

子命令：
  hash  <文件或->     输出内容 SHA-256（stdin 亦可）
  count <文件或->     输出 12 栏非空白字符数（stdin 亦可）
  check <文件或->     对单段公式提示词跑结构 QC，全过打印 PASS

check 依据 templates/prompt_template.md 的 12 个栏目键定位（行首 `栏目名：`）。
只查结构，不判内容好坏：露骨 / 真实感由模板措辞约束，不再用锚词卡死。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys

SECTIONS = [
    "默认设定", "人物", "服装", "场景", "完整连续动作", "表情与视线",
    "机位与构图", "运镜", "动作节奏", "光线与画质", "声音", "抖音真人感",
]
LIMITS = {
    "默认设定": 150, "人物": 150, "服装": 150, "场景": 250,
    "完整连续动作": 700, "表情与视线": 300, "机位与构图": 250, "运镜": 150,
    "动作节奏": 150, "光线与画质": 250, "声音": 250, "抖音真人感": 200,
}
CAMERA_RE = re.compile(
    r"摄影机身份：\s*(front_camera_selfie|mirror_selfie|third_party_capture)"
)
FILMIC_REJECT = [
    "电影感", "史诗", "推轨", "环绕", "升格", "慢动作", "宽银幕",
    "暗角", "梦幻感", "柔光罩", "情绪布光", "定格",
]
PARAM_REJECT = ["焦距", "光圈", "快门", "ISO", "滤镜参数"]
SPEECH_QUOTE_CHARS = [
    "\u201c", "\u201d", "\u2018", "\u2019", '"', "'",
    "\u300c", "\u300d", "\u300e", "\u300f",
]


def section_bodies(text: str) -> dict[str, str]:
    """按行首 `栏目名：` 抓取每个栏目整行内容（冒号后）。"""
    out: dict[str, str] = {}
    for name in SECTIONS:
        m = re.search(r"(?m)^" + re.escape(name) + r"：(.*)$", text)
        out[name] = m.group(1) if m else ""
    return out


def non_blank(text: str) -> int:
    return len(re.sub(r"\s", "", text))


def check(text: str) -> list[str]:
    errs: list[str] = []

    # 1) 每栏恰好出现一次（行首栏目名）
    for name in SECTIONS:
        n = len(re.findall(r"(?m)^" + re.escape(name) + r"：", text))
        if n != 1:
            errs.append(f"E_STRUCTURE: 栏目「{name}」应恰好出现一次，实际 {n} 次")

    # 2) 顺序
    positions = []
    for name in SECTIONS:
        m = re.search(r"(?m)^" + re.escape(name) + r"：", text)
        positions.append(m.start() if m else -1)
    if all(p >= 0 for p in positions) and positions != sorted(positions):
        errs.append("E_STRUCTURE: 栏目顺序错误")

    # 3) 逐栏字数上限
    bodies = section_bodies(text)
    for name, limit in LIMITS.items():
        length = non_blank(bodies.get(name, ""))
        if length > limit:
            errs.append(f"E_LENGTH: 「{name}」{length} 非空白字符，上限 {limit}")

    # 4) 摄影机身份：默认设定里唯一合法值
    default = bodies.get("默认设定", "")
    modes = CAMERA_RE.findall(default)
    if not modes:
        errs.append(
            "E_CAPTURE_MODE_REQUIRED: 默认设定 缺少 摄影机身份："
            "front_camera_selfie / mirror_selfie / third_party_capture"
        )
    elif len(set(modes)) != 1:
        errs.append(f"E_CAPTURE_MODE_MIXED: 出现多个摄影机身份 {sorted(set(modes))}")

    # 5) 电影腔黑名单（私密感来自内容而非影调）
    filmic = {t: text.count(t) for t in FILMIC_REJECT if t in text}
    if filmic:
        errs.append(f"E_FILMIC_CICHE: 电影腔词：{filmic}")

    # 6) 设备参数黑名单
    params = {t: text.count(t) for t in PARAM_REJECT if t in text}
    if params:
        errs.append(f"E_FORBIDDEN_PARAMS: 设备参数：{params}")

    # 7) 引号拟声禁用（声音只写呻吟/喘息性质，不写可逐字念出来的字）
    quotes = [c for c in SPEECH_QUOTE_CHARS if c in text]
    if quotes:
        errs.append("E_SPEECH_HINT: 出现引号字符；声音只写性质，不写带引号的拟声 / 骚话字")

    return errs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("hash", "count", "check"):
        sp = sub.add_parser(name)
        sp.add_argument("path", nargs="?", help="file path, or - for stdin")
    args = parser.parse_args()

    if args.path is None or args.path == "-":
        raw = sys.stdin.buffer.read()
    else:
        with open(args.path, "rb") as f:
            raw = f.read()
    text = raw.decode("utf-8")

    if args.cmd == "hash":
        print(hashlib.sha256(raw).hexdigest())
        return 0
    if args.cmd == "count":
        bodies = section_bodies(text)
        for name in SECTIONS:
            print(f"{name}={non_blank(bodies.get(name, ''))}")
        return 0
    if args.cmd == "check":
        errors = check(text)
        if errors:
            print(f"FAIL ({len(errors)}):")
            for e in errors:
                print("- " + e)
            return 1
        print("PASS: nsfw-seedance structure QC")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
