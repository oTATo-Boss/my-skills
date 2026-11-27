"""Mechanical pre-submit check for one image prompt. Exit 1 on any FAIL.

Run from the skill root:
    python3 scripts/lint_prompt.py prompt.txt
    python3 scripts/lint_prompt.py - < prompt.txt

This catches mechanical problems only. Passing does not mean the picture is beautiful;
the design and the four quoted checks in references/art-direction-polish.md still apply.
"""
import argparse
import re
import sys

NEGATION_ZH = ("无", "不", "没有", "避免", "禁止", "不要", "拒绝", "零")
NEGATION_EN = ("no ", "zero ", "without ", "avoid ", "not ", "never ")

BANNED_ZH = ("奶油虚化", "慢门", "光轨", "拖影", "百叶窗", "超广角", "0.5x", "电影感", "大片感",
             "杰作", "8K", "8k", "冷白荧光", "影棚背景")
BANNED_EN = ("8k", "masterpiece", "cinematic", "editorial photography", "atmospheric lighting",
             "f/1.4", "f1.4", "creamy bokeh", "bokeh", "light trails", "venetian blind",
             "ultra-wide", "0.5x", "best quality", "award-winning")
FAIL_PHRASES = ("同上", "其余同上", "保持前一张", "保持原身材比例", "原身材比例", "same as above",
                "original body proportions", "same body proportions")
PLACEHOLDERS = (r"\{\{", r"\}\}", r"TODO", r"XXX", r"_{3,}", r"【[^】]*】", r"<[^>]*填[^>]*>")
VAGUE_ZH = ("精致妆容", "穿着漂亮", "氛围感", "高级感", "微笑看镜头", "美丽的", "完美身材")

CAMERA = ("手机", "前置", "后置", "主摄", "卡片机", "CCD", "相机", "镜头", "自拍", "对镜",
          "smartphone", "phone", "camera", "selfie", "compact")
DEPTH = ("景深", "背景可辨", "清晰可辨", "自然减弱", "depth of field", "deep focus", "in focus",
         "readable", "sharp background")
LIGHT = ("光", "灯", "闪", "sun", "light", "flash", "lamp", "window")
DIRECTION = ("左", "右", "侧", "前方", "后方", "身后", "顶", "上方", "斜", "背光", "逆光",
             "left", "right", "side", "behind", "overhead", "above", "from the front", "backlit")
EYES = ("眼", "视线", "直视", "看向", "望向", "gaze", "eyes", "looking", "stare")


def negated(text, start, english):
    window = text[max(0, start - 12):start].lower()
    marks = NEGATION_EN if english else NEGATION_ZH
    return any(mark in window for mark in marks)


def find_banned(text):
    hits = []
    lower = text.lower()
    for term in BANNED_EN:
        for match in re.finditer(re.escape(term), lower):
            if not negated(lower, match.start(), True):
                hits.append(term)
                break
    for term in BANNED_ZH:
        for match in re.finditer(re.escape(term), text):
            if not negated(text, match.start(), False):
                hits.append(term)
                break
    return sorted(set(hits))


def has_any(text, words):
    lower = text.lower()
    return any(word.lower() in lower for word in words)


def measure(text):
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    words = len(re.findall(r"[A-Za-z][A-Za-z'\-/]*", text))
    if words > cjk / 2:
        return "en", words, (150, 300)
    return "zh", cjk + words, (300, 600)


def lint(text):
    fails, warns = [], []
    banned = find_banned(text)
    if banned:
        fails.append("禁用词或 AI 味写法未删除：" + "、".join(banned))
    phrases = [p for p in FAIL_PHRASES if p.lower() in text.lower()]
    if phrases:
        fails.append("不自包含或越界的身材写法：" + "、".join(phrases))
    marks = [p for p in PLACEHOLDERS if re.search(p, text)]
    if marks:
        fails.append("残留占位符或模板标记，请填成真实内容")
    lang, size, (low, high) = measure(text)
    unit = "词" if lang == "en" else "字"
    if size < low * 0.8 or size > high * 1.3:
        fails.append(f"长度 {size}{unit}，远离建议范围 {low}–{high}{unit}")
    elif size < low or size > high:
        warns.append(f"长度 {size}{unit}，建议范围 {low}–{high}{unit}")
    if not has_any(text, CAMERA):
        fails.append("没有写谁在用什么拍（手机／卡片机／自拍／对镜等）")
    if not has_any(text, DEPTH):
        fails.append("没有写景深或背景清晰程度")
    if not (has_any(text, LIGHT) and has_any(text, DIRECTION)):
        fails.append("没有写光源以及它从哪个方向照来")
    if not has_any(text, EYES):
        fails.append("没有写眼睛看向哪里")
    vague = [p for p in VAGUE_ZH if p in text]
    if vague:
        warns.append("空泛词需要换成具体可见描写：" + "、".join(vague))
    return fails, warns


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="Prompt file, or - for stdin")
    args = parser.parse_args()
    text = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    fails, warns = lint(text)
    for item in fails:
        print("FAIL", item)
    for item in warns:
        print("WARN", item)
    if fails:
        print("结果：未通过。修改提示词后重新运行，通过前不要提交生图。")
        sys.exit(1)
    print("结果：机械检查通过。仍需完成 art-direction-polish.md 第五节的四项摘句核对。")


if __name__ == "__main__":
    main()
