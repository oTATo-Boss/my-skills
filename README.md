# my-skills

我的原创及二创 Skill 仓库，集中维护源码、脚本和资源。

以下命令全局安装到 **Codex**，使用文件复制方式。安装到 **Claude Code** 时，将 `-a codex` 改为 `-a claude-code`。需要本机已安装 Node.js；安装选项见 [skills CLI](https://github.com/vercel-labs/skills)。

| Skill | 简单说明 | 安装命令 |
| --- | --- | --- |
| [ai-liveaction-fusion](skills/ai-liveaction-fusion/SKILL.md) | AI 与实拍融合：镜头分析、静态分镜、视频提示词、审片与返修。 | `npx skills add oTATo-Boss/my-skills --skill ai-liveaction-fusion -g -a codex --copy -y` |
| [ai-video-prompt](skills/ai-video-prompt/SKILL.md) | 创作、修改和审查通用 AI 视频提示词。 | `npx skills add oTATo-Boss/my-skills --skill ai-video-prompt -g -a codex --copy -y` |
| [json-prompt-system](skills/json-prompt-system/SKILL.md) | 生成或还原自拍、生活照、电商服装与试穿的 JSON 图像提示词。 | `npx skills add oTATo-Boss/my-skills --skill json-prompt-system -g -a codex --copy -y` |
| [fashion-picture](skills/fashion-picture/SKILL.md) | 设计服装、四视图样衣、人物换装与妆造图片。 | `npx skills add oTATo-Boss/my-skills --skill fashion-picture -g -a codex --copy -y` |
| [nsfw-seedance-prompt-skill](skills/nsfw-seedance-prompt-skill/SKILL.md) | 成人题材视频提示词的结构化编写与检查。 | `npx skills add oTATo-Boss/my-skills --skill nsfw-seedance-prompt-skill -g -a codex --copy -y` |
| [social-media](skills/social-media/SKILL.md) | 制作社交媒体视频与图文，配齐封面、标题、正文和标签。 | `npx skills add oTATo-Boss/my-skills --skill social-media -g -a codex --copy -y` |
| [codex-imagegen](skills/codex-imagegen/SKILL.md) | 让其他 Agent 通过本机 Codex CLI 生成和编辑图片。 | `npx skills add oTATo-Boss/my-skills --skill codex-imagegen -g -a codex --copy -y` |
| [direct-video](skills/direct-video/SKILL.md) | 统筹视频创意、分镜、节奏、声音和成片验收。 | `npx skills add oTATo-Boss/my-skills --skill direct-video -g -a codex --copy -y` |
| [design-review](skills/design-review/SKILL.md) | 审查已有界面的视觉层级、交互状态、动效与性能。 | `npx skills add oTATo-Boss/my-skills --skill design-review -g -a codex --copy -y` |
| [ui-craft](skills/ui-craft/SKILL.md) | 精修界面的字体、颜色、间距、对齐和控件状态。 | `npx skills add oTATo-Boss/my-skills --skill ui-craft -g -a codex --copy -y` |
| [visual-reference](skills/visual-reference/SKILL.md) | 分析图片、视频和网页参考，转成设计规格或界面实现。 | `npx skills add oTATo-Boss/my-skills --skill visual-reference -g -a codex --copy -y` |
| [web-art-direction](skills/web-art-direction/SKILL.md) | 确定并实现网站整体视觉方向。 | `npx skills add oTATo-Boss/my-skills --skill web-art-direction -g -a codex --copy -y` |
| [web-motion](skills/web-motion/SKILL.md) | 设计和实现网页交互、文字、滚动与时间线动画。 | `npx skills add oTATo-Boss/my-skills --skill web-motion -g -a codex --copy -y` |
| [web-visual-effects](skills/web-visual-effects/SKILL.md) | 实现玻璃、纹理、粒子、WebGL 和三维网页效果。 | `npx skills add oTATo-Boss/my-skills --skill web-visual-effects -g -a codex --copy -y` |

一次安装全部 14 个：

```bash
npx skills add oTATo-Boss/my-skills --skill '*' -g -a codex --copy -y
```

源码与参考资料的来源见 [SOURCE_NOTES.md](SOURCE_NOTES.md)；开发与本机同步约定见 [AGENTS.md](AGENTS.md)。
