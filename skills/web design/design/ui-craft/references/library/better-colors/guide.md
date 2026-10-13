> 用途：按需参考原模块的技术或风格配方。项目与用户选择优先；示例数值、主题和文案格式不构成全局要求。

# 配色与 OKLCH

先保留项目的颜色语义与 token。OKLCH 可用于转换、调整明度和生成色阶，但不要求全量改写现有 CSS。
使用 oklch(L C H / alpha)，其中 L 为 0–1、C 为色度、H 为角度。可用范围随色域和明度变化，不直接把固定 C 当作所有色相相同鲜艳度。
色阶关注角色、层级、色域边界和相邻级差。先调整明度改善可读性，再用实际合成颜色计算对比度；不能仅以 L 的差值替代测量。
前景在透明、渐变、图片或玻璃背景上，需要确定最终背景或保证文本底层的稳定对比。
P3 色彩按项目目标提供 sRGB 回退。深浅主题按语义角色设计，不机械反转全部明度。
具体转换、色阶、对比度与 Tailwind 配方见下表；其中示例和启发式不能替代实际色域及对比度计算。

| 问题 | 参考 |
| --- | --- |
| 格式转换 | [color-conversion.md](color-conversion.md) |
| 色阶生成 | [palette-generation.md](palette-generation.md) |
| 对比度验证 | [accessibility-contrast.md](accessibility-contrast.md) |
| 色域和 Tailwind | [gamut-and-tailwind.md](gamut-and-tailwind.md) |
