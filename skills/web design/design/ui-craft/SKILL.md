---
name: ui-craft
description: "Polish web and product UI typography, colors, spacing, alignment, surfaces and component states. Use for targeted visual fixes or UI implementation within an existing design system; Chinese triggers include 界面精修、排版、配色、间距、圆角、对齐。"
---

# UI 基础与精修

## 使用边界

用户要求和项目已有设计系统优先。沿用现有组件、样式和依赖；修改限定在本次目标内。下方参考文件是按需使用的配方，其固定数值、字体、色彩、版式和输出格式均可依项目调整。
只读取当前任务需要的参考；不默认加载整个库或全部总技能。额外工具、素材生成和新依赖由实际需要决定。
库中的版本、外部链接和代码片段来自旧合集；涉及实际安装或 API 时，先核对项目现有版本和对应官方资料。静态设计或素材示例不代表已实现的数据、交互或持久化。
已有专用技能、工具或组件能完成目标时复用它们，避免重复启动另一套流程。

## 执行方法

先看指定界面的真实内容、样式入口和已有设计 token，确定是排版、层级、表面还是控件状态问题，再做最小调整。

1. 用语义层级组织字号、字重、行高与间距。中文字体、混排、换行和窄屏要用真实文案验证；不要把英文行长或大写字距直接套到中文。
2. 保留项目颜色的语义角色。调整可读性时测量实际前景与背景；透明、叠图和玻璃表面需考虑合成后的颜色。OKLCH 是可选工具，不要求全项目改写颜色。
3. 校准嵌套圆角、视觉对齐和点击区域。边框、阴影、平面材质按项目风格选；按钮缩放幅度由尺寸和使用频率决定。
4. 补齐本次控件相关的 hover、focus、active、disabled、loading、empty 或 error 状态，保持文字和布局稳定。高频操作避免每次播放装饰动画。
5. 在真实页面检查改动区域和一个相关窄屏状态。纯视觉修改以截图与实际交互为主要证据；代码检查按影响选择。

## 按需参考

- 排版问题：`better-typography`；配色问题：`better-colors`；控件细节：`better-ui`。
- 手势、拖拽、弹簧和组件行为：`apple-design`、`emil-design-eng`。
- 项目采用 Tailwind 时：`tailwindcss`。这些参考不要求引入该框架。

## 参考索引

仅当需要具体配方时查看 [index.md](references/index.md)，从中选择当前问题对应的参考文件。
