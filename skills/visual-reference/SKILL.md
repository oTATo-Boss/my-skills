---
name: visual-reference
description: "Analyze visual references, translate images or videos into UI specifications, create requested design concepts or brand boards, capture reference pages, or select assets. Chinese triggers include 参考图、视觉反推、图转代码、设计概念图、品牌板、灵感采集。"
---

# 视觉参考与转译

## 使用边界

用户要求和项目已有设计系统优先。沿用现有组件、样式和依赖；修改限定在本次目标内。下方参考文件是按需使用的配方，其固定数值、字体、色彩、版式和输出格式均可依项目调整。
只读取当前任务需要的参考；不默认加载整个库或全部总技能。额外工具、素材生成和新依赖由实际需要决定。
库中的版本、外部链接和代码片段来自旧合集；涉及实际安装或 API 时，先核对项目现有版本和对应官方资料。静态设计或素材示例不代表已实现的数据、交互或持久化。
已有专用技能、工具或组件能完成目标时复用它们，避免重复启动另一套流程。

## 执行方法

先识别交付类型：参考分析、图转代码、概念图、品牌板、素材选择或网页采集。用户提供的参考是当前视觉来源；不能为了套用流程先替换成自己生成的图。

1. 检查原图、视频、HTML 或真实页面，提取布局、字体角色、色彩、素材、关键交互与响应式推断。分别标记观察事实和推断。
2. 生成设计提示词时明确目标、布局层级、字体角色、色彩材质、真实文案和约束。只变更需要探索的变量。
3. 需要生成图像时使用当前可用生图工具。数量与画幅按实际交付决定；只在整体图细节不足时增加区块图，不强制每区块生图。
4. 多屏或多区块共享字体、颜色、图标、组件和素材语言。移动界面检查平台安全区、键盘、返回路径和空/错误状态；不默认把设备外框作为界面的一部分。
5. 转代码时用现有组件和样式实现，保证媒体比例和文字可读性。参考图没有显示的交互不能宣称已实现。
6. 素材使用真实可访问的来源或已有文件，记录出处和本次用途。现有品牌标识不要静默替换成示例品牌。最终检查实现与参考的关键区域。

## 按需参考

- 图转代码：`image-to-code`；网页或移动概念图：两个 `imagegen-frontend-*` 配方；品牌板：`brandkit`。
- 设计提示词：`design-first-ui-prompting`；HTML 或视频分析：`html-to-interaction-prompts`、`video-to-superprompt`。
- 网页采集：`stitched-full-page-capture`；灵感集：`daily-ui-inspiration-capture`。当次采集不隐含创建定时任务。
- 素材：aura / unsplash / company-logos 配方。真实站点、来源和嵌入许可在实际使用时核对。

## 参考索引

仅当需要具体配方时查看 [index.md](references/index.md)，从中选择当前问题对应的参考文件。
