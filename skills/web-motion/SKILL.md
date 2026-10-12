---
name: web-motion
description: "Design or implement web interaction animation, text reveals, GSAP timelines, scroll storytelling and looping motion. Use when motion is requested or materially explains state; Chinese triggers include 网页动效、滚动动画、文字动画、交互动画。"
---

# 网页动效

## 使用边界

用户要求和项目已有设计系统优先。沿用现有组件、样式和依赖；修改限定在本次目标内。下方参考文件是按需使用的配方，其固定数值、字体、色彩、版式和输出格式均可依项目调整。
只读取当前任务需要的参考；不默认加载整个库或全部总技能。额外工具、素材生成和新依赖由实际需要决定。
库中的版本、外部链接和代码片段来自旧合集；涉及实际安装或 API 时，先核对项目现有版本和对应官方资料。静态设计或素材示例不代表已实现的数据、交互或持久化。
已有专用技能、工具或组件能完成目标时复用它们，避免重复启动另一套流程。

## 执行方法

先说明动画帮助用户理解什么：反馈、状态、空间连续性、阅读顺序或展示叙事。优先现有动效机制，简单状态变化使用 CSS；需要复杂时间线再选择库。

1. 区分高频产品操作和低频展示动效。按钮反馈常从 100–200ms 起试，浮层约 150–300ms；大场景按阅读节奏调整，这些是起点而非固定标准。
2. 进入可用缓出，离开可更短；拖拽使用可被打断的过渡或弹簧。离场缓入只在快速消失合理时使用，不把任何曲线当作全局禁令。
3. 优先 transform、opacity；模糊、阴影、布局变化和大面积滤镜需测量实际成本。只添加有证据需要的 will-change。
4. 为 prefers-reduced-motion、键盘与触屏提供可理解的静态或低动态表现。不能让内容依赖动画成功才可访问。
5. 在路由卸载、节点销毁或效果停用时清理监听器、observer、时间线和 requestAnimationFrame。平滑滚动只有目标需要时采用。
6. 检查真实播放、中断、重入、首帧和窄屏。时间和顺序用实际播放或帧序列验证，静态截图只检查构图。

## 按需参考

- 名称不明确：`animation-vocabulary`；节奏与编排：`animation-systems`。
- 元素进入：`animation-on-scroll`、`staggered-word-reveal`、`masked-reveal`。
- 连续循环：`marquee-loop`；时间线：`gsap`。
- 滚动叙事：从三个 cinematic / scrolltrigger 配方中选一个，避免把多套初始化机制叠在一起。

## 参考索引

仅当需要具体配方时查看 [index.md](references/index.md)，从中选择当前问题对应的参考文件。
