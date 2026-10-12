#!/usr/bin/env python3
from validate_skill_contract import validate

FULL_OK='''```markdown
---
# 视频编辑指令
@视频 为唯一实拍基础素材。
除后续逐镜明确摄影例外外，完全保留 @视频 的摄影、表演和动作。
完全去除 @视频 中非最终成片内容。
最终影调与电影质感以 @分镜图 以及后续「影片质感」为标准。
具体内容以后续「逐镜分解」执行。

# 素材锁定
## 场景锁定
@场景
## 角色视觉锁定
女1 使用 @角色 与 @服装。
## 道具视觉锁定
无。

# 影片质感
## 风格类型
...
## 摄影偏好
...
## 整体质感与氛围
...
## 光影与色彩
...

# 逐镜分解
## 分镜1｜测试
### 构图与景别
...
### 背景与空间
...
### 空间透视与镜头匹配
...
### 光源与融合
...
### 最终画面
...
### VFX
...
---
```'''

SINGLE_OK='''```markdown
---
# 逐镜分解
## 分镜1｜测试
### 构图与景别
...
### 背景与空间
...
### 空间透视与镜头匹配
...
### 光源与融合
...
### 最终画面
...
### VFX
...
---
```'''

PURE_OK='''```markdown
---
# 纯 AI 镜头提示词
## 镜头1｜测试
### 镜头定位
...
### 素材使用
@分镜图 @场景 @角色 @服装
### 构图与景别
...
### 背景与空间
...
### 空间透视与镜头匹配
...
### 光源与融合
...
### 最终画面
...
### VFX
...
---
```'''

BAD_OLD=SINGLE_OK.replace('### 最终画面','### 画面内容')
BAD_MISSING=SINGLE_OK.replace('### 空间透视与镜头匹配\n...\n','')
BAD_ORDER=SINGLE_OK.replace('### 背景与空间\n...\n### 空间透视与镜头匹配','### 空间透视与镜头匹配\n...\n### 背景与空间').replace('### 空间透视与镜头匹配\n...\n...','### 空间透视与镜头匹配\n...')
BAD_OUTSIDE='解释\n'+FULL_OK
BAD_MIXED=FULL_OK.replace('@角色','{{Mixed 3}}')
BAD_PLACEHOLDER=FULL_OK.replace('@角色','@[角色参考]')

cases=[
('full_ok',FULL_OK,True),('single_ok',SINGLE_OK,True),('pure_ok',PURE_OK,True),
('old',BAD_OLD,False),('missing',BAD_MISSING,False),('outside',BAD_OUTSIDE,False),
('mixed',BAD_MIXED,False),('placeholder',BAD_PLACEHOLDER,False)]
for n,s,expected in cases:
    r=validate(s)
    if r.ok!=expected: raise SystemExit(f'{n}: expected {expected}, got {r.ok}; {r.errors}')
print('ALL TESTS PASSED')
