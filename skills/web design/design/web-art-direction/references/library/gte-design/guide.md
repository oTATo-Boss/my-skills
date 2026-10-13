> 用途：按需参考原模块的技术或风格配方。项目与用户选择优先；示例数值、主题和文案格式不构成全局要求。

# GTE 品牌系统与可用素材

仅在明确制作 GTE 品牌内容或用户选择该示例系统时使用。普通项目保持自己的品牌、字体与数据语义。
先读 [foundations.md](foundations.md) 了解品牌规则，再选择实际任务需要的层。

| 任务 | 本包内容 |
| --- | --- |
| 色彩、字体与间距 | [colors_and_type.css](colors_and_type.css)、`fonts/` |
| 产品组件结构 | [components.md](references/components.md)、`ui_kits/web/*.jsx` |
| 营销页面 | [marketing.md](references/marketing.md)、`preview/landing-*.html` |
| 技术图解 | [diagrams.md](references/diagrams.md) |
| 标识与图片 | `assets/logos/`、`assets/brand-images/`、`assets/chains/`、`assets/tokens/` |

`preview/` 是本地 HTML 示例，按实际存在的文件选择组件；引用相邻 CSS 与素材时保留目录结构，或把必要样式和素材移入目标项目。
`ui_kits/web/index.html` 是使用外部 React/Babel 的演示入口，不能视为离线生产应用。移植时采用目标项目的组件与构建方式。
示例交易数据不是真实行情。只有在当前项目实际存在相关组件时才复用项目组件路径；本包不依赖作者的私有仓库。
正文密度、主题、数字字体与 23.43° 装饰是这个品牌的特定语法，不传播为其它项目的全局要求。
