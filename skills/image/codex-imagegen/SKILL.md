---
name: codex-imagegen
description: Generate or edit raster images by calling the locally logged-in Codex CLI (ChatGPT auth, built-in image_gen tool, no OPENAI_API_KEY needed). Use whenever the user asks to create, draw, generate, edit, restyle or iterate on an image, photo, illustration, poster, banner, hero image, icon, product mockup, UI mockup, texture, sprite, concept art or transparent cutout — including Chinese phrasings such as 生图, 出图, 画图, 画一张, 生成图片, 做张图, 配图, 改图, 用 Codex 画. Also use for generating variants from one or more reference images. **Use it proactively, without being asked**, whenever a task needs a raster asset that would otherwise be stubbed out, left as a grey box, linked to a dead placeholder URL, or skipped — hero/banner images for a page or app being built, product and UI mockups, preview visuals, avatars, empty-state art, textures, sprites, slide imagery, OG/social cards, or any other bitmap the deliverable actually needs. Do not use when the deliverable should be SVG/vector, an existing icon/logo system, or a diagram better written as HTML/CSS/canvas code.
---

# Codex 生图 (codex-imagegen)

通过本机已登录的 Codex CLI 调用其**内置 `image_gen` 工具**出图。
走 ChatGPT 账号鉴权，**不需要 `OPENAI_API_KEY`**。

## 触发场景

**主要场景不是用户开口要图，而是你做任务时自己需要素材。**
用户的原话：「通常不是我说，是你在任务过程当中需要素材、预览等各种需要生图来完成的操作使用。」

所以只要正在做的交付物需要一张位图，就**自己调这个 skill 生成，不用问**：

- 在做网页/应用 → hero 图、banner、背景图、空状态插画、头像、OG/社交卡片
- 在做演示/文档 → 配图、封面、示意图（写实或插画风那种，不是流程图）
- 在做原型 → 产品图、UI mockup、素材占位
- 在做游戏/3D → 贴图、sprite、概念图
- 需要给用户看效果预览 → 直接生成，而不是描述"这里应该放一张图"

**反模式**（看到自己要做这些，就说明该生图了）：
- 写 `<img src="placeholder.jpg">` 或指向不存在的图片路径
- 用灰色方块 / `background: #ccc` 糊弄
- 用 emoji 或纯 CSS figure 代替本该是照片的东西
- 在交付里写"此处需补一张图"然后就不管了

用户显式说"生图 / 出图 / 画一张 / 做张图 / 配图 / 改图"时当然也用。

**不要用**：需要 SVG/矢量输出、要扩展仓库里已有的图标/Logo 体系、
或者用 HTML/CSS/canvas 写更合适的图表和线框图。

**注意额度**：自动生图也要克制。一次任务里按需生成，不要为了"更全"批量铺图；
批量时严格串行（见下）。

## 主路径：用自带脚本（默认走这条）

```bash
~/.claude/skills/codex-imagegen/scripts/gen-image.sh \
  --workdir "$PWD" --slug "hero-image" <<'EOF'
Use case: photorealistic-natural
Primary request: <用户的核心需求>
Style/medium: <写实摄影 / 插画 / 3D 渲染>
Composition/framing: <构图、景别、留白>
Lighting/mood: <光线与情绪>
Color palette: <色板>
Text (verbatim): "<画面内文字，逐字照抄>"
Constraints: <必须保留的东西>
Avoid: <不要出现的东西：文字、水印、logo…>
EOF
```

脚本会：解析 codex 二进制 → 建 `outputs/` → 算出不覆盖的文件名 →
把"保存到绝对路径"的指令追加进提示词 → 调 Codex →
目标文件没出现就从默认落盘位置回收 → **stdout 只打印最终绝对路径**。

参数：

| 参数 | 说明 |
|---|---|
| `--workdir <dir>` | 工作目录，默认 `$PWD` |
| `--out <绝对路径.png>` | 精确指定输出路径 |
| `--slug <名字>` | 不传 `--out` 时用于拼 `outputs/<日期>_<slug>_<序号>.png` |
| `--ref <图片>` | 参考图，**可重复传多张** |

**提示词走 stdin heredoc**，所以中文引号、JSON、换行都不会有 shell 转义问题。
用 `<<'EOF'`（带引号）避免变量被意外展开。

脚本把沙箱参数（`--skip-git-repo-check -s workspace-write`）**写死在内部**，
不接受外部覆盖。这是它能被 `permissions.allow` 整体放行的前提 ——
**不要给它加任何能绕过沙箱的开关**。

## 底层命令（脚本内部等价物，调试或手工跑时用）

```bash
CODEX="$(command -v codex || echo /Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex)"

"$CODEX" exec \
  --skip-git-repo-check \
  -s workspace-write \
  -C "$W" \
  -i "$W/refs/style.png" \
  -o "$W/.codex-last-message.txt" \
  - < "$PROMPT_FILE"
```

参数说明（全部来自 `codex exec --help` 实际输出）：

- `--skip-git-repo-check` —— **非 git 目录必须加**，否则拒绝运行
- `-s workspace-write` —— 允许写工作目录，这是 `cp` 到 `outputs/` 的前提
- `-C <DIR>` —— 指定工作根目录，比 `cd` 可靠
- `-` + `< file` —— 从 stdin 读提示词（省略 `[PROMPT]` 时也默认读 stdin）
- `-o <FILE>` —— 把 agent 最后一条消息写进文件，用来取回最终路径
- `-i <FILE>...` —— 附带参考图，可重复
- `--json` —— JSONL 事件流，调试用；**输出必须重定向到文件**，别直接灌进上下文
  （不加 `--json` 的普通输出也很长，一次约 35KB）

## 环境事实（已实测，codex-cli 0.160.1）

| 项 | 值 |
|---|---|
| 二进制位置 | `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex`（**不在 PATH 里**） |
| 登录态 | `codex login status` → `Logged in using ChatGPT` |
| 生图能力 | feature flag `image_generation` = stable / true，内置工具 |
| 默认落盘 | `~/.codex/generated_images/<thread-id>/exec-<uuid>.png` |
| 目标路径 | 内置工具**没有**输出路径参数 —— 必须先生成再 `cp` 到目标位置 |

## 参考图 / 改图

`--ref` 可重复传多张，**已实测生效**：附一张橘猫窗台图 + "改成黄昏逆光"，
输出保持了同一只猫、同样姿势、同样场景，只换了光线。

提示词里要**显式标注每张图的角色**（Codex 官方 skill 的要求）：

```text
Input images: Image 1: 风格参考（只取配色和笔触）; Image 2: 主体参考（保持人物外观不变）
```

- 拿图当**风格/构图参考** → 算 generate，直接 `--ref` 传
- 要**保留原图大部分内容**只改局部 → 算 edit，提示词里把不变量写死
  （`change only X; keep Y unchanged`），每轮迭代都重复一遍，防止漂移
- 透明底：直接在提示词里要求 transparent background，内置工具会保留 alpha

## 输出约定

- 默认存到**当前工作目录的 `outputs/`**
- 文件名 `日期_简短描述_序号.png`，例如 `2026-10-07_cat-windowsill_01.png`
  - 日期 `date +%F`；slug 用短横线连接，ASCII 优先；序号两位
- **不覆盖**已有文件 —— 脚本会自动递增序号

### 兜底：图片没出现在目标路径

脚本已内置回收逻辑。手工排查时用：

```bash
find "$HOME/.codex/generated_images" -type f -name '*.png' \
  -exec stat -f '%m %N' {} + 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-
```

注意 macOS 的 `find` **不支持** `-newermt "-10 minutes"` 这种相对时间写法，
要按时间筛就用上面的 `stat -f '%m %N' | sort -rn`，或 `-newer <参照文件>`。

## 生成后必须验收

**每次生成完都要用 Read 工具把图片读出来看**，不能只看 exit code 和文件大小。
`file` 只能证明它是合法 PNG，证明不了画面对不对。

看完对照需求简要评估，再决定要不要迭代：

1. 主体对不对（物种、人数、姿势、产品形态）
2. 风格和光线是否符合要求
3. 构图/景别/留白是否可用
4. 画面文字是否逐字正确（最容易出错）
5. Avoid 清单里的东西有没有混进来（水印、多余文字、logo）

迭代规则：**一次只改一个点**，改完重新看图。多点同时改会互相干扰，难定位。

## 批量生成

**串行执行，一次一张**，不要并发 —— 会打满账号额度，而且 Codex 内置工具本来就是
"每个素材一次独立调用"的设计。

```bash
for spec in "$PWD/specs"/*.md; do
  ~/.claude/skills/codex-imagegen/scripts/gen-image.sh \
    --workdir "$PWD" --slug "$(basename "$spec" .md)" < "$spec"
done
```

批量跑完，**每张都要 Read 看过**再汇报。

## 提示词结构（Codex 官方 schema）

```text
Use case: <taxonomy slug>
Asset type: <这张图用在哪>
Primary request: <核心需求>
Input images: <Image 1: 角色; Image 2: 角色>
Scene/backdrop: <环境>
Subject: <主体>
Style/medium: <摄影/插画/3D>
Composition/framing: <构图景别>
Lighting/mood: <光线情绪>
Color palette: <色板>
Materials/textures: <材质>
Text (verbatim): "<画面文字，逐字>"
Constraints: <必须保留>
Avoid: <负向约束>
```

`Use case` 可选值（照抄官方 slug）：

- 生成：`photorealistic-natural`、`product-mockup`、`ui-mockup`、`infographic-diagram`、
  `scientific-educational`、`ads-marketing`、`productivity-visual`、`logo-brand`、
  `illustration-story`、`stylized-concept`、`historical-scene`
- 编辑：`text-localization`、`identity-preserve`、`precise-object-edit`、`lighting-weather`、
  `background-extraction`、`style-transfer`、`compositing`、`sketch-to-render`

提示词原则：
- 结构按 场景 → 主体 → 细节 → 约束 排
- 用户给的提示词已经很具体 → 只做结构化，**不要自己加创意**
- 用户给的很笼统 → 才补充能实质提升质量的细节
- 画面文字要加引号逐字写，难拼的词逐字母拆开并要求照抄
- 追求写实就用相机语言（焦段、光圈、景深）

## 尺寸

内置 `image_gen` **没有公开的 size 参数**，尺寸在提示词里用自然语言要
（"横版 16:9"、"竖版手机壁纸"、"正方形"）。实测会按构图描述自动选，
出过 1370×1148 和 1536×1024。要精确像素就生成后用 `sips` 再处理：

```bash
sips -z 1080 1920 "$OUT" --out "$OUT"   # 高 宽
```

（官方文档里那套 `1024x1024` / `3840x2160` 精确尺寸表属于 **CLI fallback 路径**，
那条路要 `OPENAI_API_KEY`，默认不走。用户明确要求才换。）

## 约束

- **不要修改 Codex 自己的配置和登录态**（`~/.codex/config.toml`、`auth.json`）
- 不需要也不要去设 `OPENAI_API_KEY`，内置工具用的是 ChatGPT 登录态
- 如果 Codex 报 "ignoring N unrecognized configuration settings"，那是用户 `config.toml`
  里的过期键（`features.child_agents_md`、`mcp_servers.node_repl.type`），
  **与生图无关，忽略即可**，不要去"修"它
- 同理 `.agents/skills/canvas/SKILL.md missing YAML frontmatter` 也是既有的无关报错
- **本 skill 不要装进 `~/.codex/skills/`** —— 它的作用是从别的 agent 调 Codex，
  装进 Codex 自己那里是循环调用隐患；Codex 本来就有 `.system/imagegen`
- 内置工具失败时才提 CLI fallback（需要 API key），而且要先问用户
