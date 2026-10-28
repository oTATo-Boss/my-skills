# 模板选择与使用

只读取当前阶段与当前画风需要的文件。模板中现有占位符填写本次内容，不把某个角色写入共享模板。未提供的参考不虚构。

## 基础模板

| 阶段 | 写实 | 通用3D-CG | AAA-CG |
|---|---|---|---|
| 正面肖像 | [portrait](../assets/templates/realistic/portrait.txt) | [portrait](../assets/templates/cg/portrait.txt) | [portrait](../assets/templates/aaa/portrait.txt) |
| 头部四视图 | [head-four](../assets/templates/realistic/head-four.txt) | 综合模板的头部补齐模式 | 综合模板的头部补齐模式 |
| 正面半身 | [half](../assets/templates/realistic/half.txt) | [half](../assets/templates/cg/half.txt) | [half](../assets/templates/aaa/half.txt) |
| 全身 | [body-three](../assets/templates/realistic/body-three.txt) | 综合模板的全身补齐模式 | [body-four](../assets/templates/aaa/body-four.txt) |
| 综合板 | [board](../assets/templates/realistic/board.txt) | [board](../assets/templates/cg/board.txt) | [board](../assets/templates/aaa/board.txt) |

软件模板已纠错的快照是版本起点；随包适配补齐模式和模块化风格字段。输出是参考图片，不包含真实绑定、网格或三维模型数据。

## 综合模板的运行模式

CG和AAA综合模板新增 `{{输出模式}}`、`{{本次输入与参考职责}}`。运行前明确填一种模式；不让图片模型自行选择：

- `头部补齐`：只输出16:9头部四视图，0°/45°/90°/180°。输入已确认肖像，不依赖半身或全身。
- `全身补齐`：只输出9:16正面/侧面/背面全身三视图；仅通用CG使用。输入肖像、已定头部和半身。
- `综合板`：作为排版规格与裂变参考，不默认再次调用生图。已有面板交[排版脚本](board-composition.md)拼接。若某一源图有缺陷，只修该图。

写实综合模板也主要用于规定排版和状态一致性；已有源图直接拼接。三个综合模板都不要求“为了排版统一”重绘已确认面部。

## 服装与裂变模板

- [原创服装四视图](../assets/four-view-template.txt)：填服装设计与风格字段，写实使用真实服装质感，CG/AAA使用对应角色的材质表现。
- [原穿搭提取](../assets/templates/outfit/extract.txt)：保留原款式、配饰和穿戴关系，不重新设计；新增风格字段用于匹配角色目标表现。
- [角色换装与受控妆造](../assets/character-styling-template.txt)：图1锁身份及排版，图2锁造型，图3～N补细节。仅妆造时不强行要求新服装图；使用模板内“不换装”分支。
- [剧情状态修改](../assets/templates/outfit/state.txt)：以已确认造型板为编辑目标，明确改变与保持项；支持无服装变化的伤口、泪痕、情绪等。

模板只负责本阶段输出，不追加完整镜头、场景或生视频指令。角色参数中不写未经用户确认的“已批准”。

## 更新与来源

当前包为模板维护源，不在执行时依赖oTATo Prompt。软件快照的标题和原始内容摘要见[来源清单](template-sources.json)，原服装技能来源保存在[历史来源](legacy-outfit-source.md)。以后修订保留来源记录，并在用户要求时同步软件；不做隐式双向覆盖。
