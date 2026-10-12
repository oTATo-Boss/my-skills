#!/usr/bin/env python3
"""Validate ai-liveaction-fusion v4.2.2 video-prompt output contract."""
from __future__ import annotations
import re, sys
from dataclasses import dataclass

SECTION_ORDER = ["视频编辑指令", "素材锁定", "影片质感", "逐镜分解"]
ALLOWED_SINGLE = set(SECTION_ORDER + ["纯 AI 镜头提示词", "成片审查", "单变量返修提示词"])
SHOT_SUBS = ["构图与景别","背景与空间","空间透视与镜头匹配","光源与融合","最终画面","VFX"]
PURE_SUBS = ["镜头定位","素材使用"] + SHOT_SUBS

@dataclass
class Result:
    ok: bool
    errors: list[str]

def extract_single_markdown_block(text: str):
    m=re.match(r"\A\s*```markdown\n([\s\S]*?)\n```\s*\Z", text)
    if not m:
        return None,["输出必须且只能包含一个 markdown 代码框，且代码框外不得有其他文本。"]
    return m.group(1),[]

def heading_titles(body: str):
    return re.findall(r"^#\s+(.+?)\s*$", body, flags=re.M)

def get_module_slice(body: str, title: str):
    ms=list(re.finditer(r"^#\s+(.+?)\s*$", body, flags=re.M))
    for i,m in enumerate(ms):
        if m.group(1)==title:
            return body[m.start(): ms[i+1].start() if i+1<len(ms) else len(body)]
    return body

def subheadings(block: str):
    return re.findall(r"^###\s+(.+?)\s*$", block, flags=re.M)

def validate_shot_block(shot: str, idx: int):
    e=[]
    subs=subheadings(shot)
    if subs != SHOT_SUBS:
        e.append(f"分镜{idx}三级栏目必须严格为：" + " → ".join(SHOT_SUBS))
    if re.search(r"^###\s+(视频内容|画面内容)\s*$",shot,re.M):
        e.append(f"分镜{idx}检测到旧栏目，v4.2.2 必须使用“最终画面”。")
    return e

def validate_module_body(title: str, module: str):
    e=[]
    if title=="素材锁定":
        for sub in ["场景锁定","角色视觉锁定","道具视觉锁定"]:
            if not re.search(rf"^##\s+{re.escape(sub)}\s*$",module,re.M): e.append(f"素材锁定缺少二级标题：{sub}")
    elif title=="影片质感":
        for sub in ["风格类型","摄影偏好","整体质感与氛围","光影与色彩"]:
            if not re.search(rf"^##\s+{re.escape(sub)}\s*$",module,re.M): e.append(f"影片质感缺少二级标题：{sub}")
    elif title=="逐镜分解":
        if not re.search(r"^##\s+分镜1(?:｜.*)?$",module,re.M): e.append("逐镜分解至少需要从“分镜1”开始。")
        shots=[s for s in re.split(r"(?=^##\s+分镜\d+)",module,flags=re.M) if re.search(r"^##\s+分镜\d+",s,re.M)]
        for i,shot in enumerate(shots,1): e.extend(validate_shot_block(shot,i))
    elif title=="视频编辑指令":
        for p in ["@视频","@分镜图","完全保留","完全去除","影片质感","逐镜"]:
            if p not in module: e.append(f"视频编辑指令缺少关键内容：{p}")
    elif title=="纯 AI 镜头提示词":
        subs=subheadings(module)
        if subs != PURE_SUBS: e.append("纯 AI 镜头三级栏目必须严格为：" + " → ".join(PURE_SUBS))
    return e

def validate(text: str):
    body,errs=extract_single_markdown_block(text)
    if errs: return Result(False,errs)
    st=body.strip()
    if not st.startswith('---'): errs.append('代码框正文必须以 --- 开始。')
    if not st.endswith('---'): errs.append('代码框正文必须以 --- 结束。')
    if '{{Mixed' in body: errs.append('不得使用 {{Mixed X}} 作为 canonical 素材句柄。')
    if '@[' in body: errs.append('存在未解析的 @[占位符]，正式交付前必须替换为实际 @句柄。')
    unresolved=['[删除本段','[若有','[按本段','[按实际','[列出','[只写','[同上','[...]','[...']
    if any(x in body for x in unresolved): errs.append('存在未清理的模板说明占位文本，正式交付前必须删除或填充。')
    titles=heading_titles(body)
    if not titles: return Result(False,errs+["代码框内至少需要一个一级标题。"])
    for t in titles:
        if t not in ALLOWED_SINGLE: errs.append(f"不允许的一级标题：{t}")
    if len(set(titles))!=len(titles): errs.append('一级标题不得重复。')
    std=[t for t in titles if t in SECTION_ORDER]; exp=[t for t in SECTION_ORDER if t in titles]
    if std!=exp: errs.append('标准四模块必须按照：视频编辑指令 → 素材锁定 → 影片质感 → 逐镜分解 的顺序出现。')
    for t in titles: errs.extend(validate_module_body(t,get_module_slice(body,t)))
    return Result(not errs,errs)

def main():
    text=open(sys.argv[1],encoding='utf-8').read() if len(sys.argv)>1 and sys.argv[1]!='-' else sys.stdin.read()
    r=validate(text)
    print('PASS' if r.ok else 'FAIL')
    if not r.ok:
        for e in r.errors: print('-',e)
    return 0 if r.ok else 1
if __name__=='__main__': raise SystemExit(main())
