# 模板选择与使用

角色设计固定为 **真人通用、美女、帅哥、通用3D、AAA CG五个模式，每个模式五个模板，共25份角色模板**。角色模式决定原有审美、肤质、体型、服装和画风；快速整板与分阶段是同一模式内的执行方式。

## 五个模式的完整模板入口

| 角色模式 | 正面肖像 | 头部四视 | 正面半身 | 全身三视 | 综合宫格板 |
|---|---|---|---|---|---|
| 真人通用 | [portrait](../assets/templates/realistic-base/portrait.txt) | [head-four](../assets/templates/realistic-base/head-four.txt) | [half](../assets/templates/realistic-base/half.txt) | [body-three](../assets/templates/realistic-base/body-three.txt) | [board](../assets/templates/realistic-base/board.txt) |
| 美女 | [portrait](../assets/templates/beauty/portrait.txt) | [head-four](../assets/templates/beauty/head-four.txt) | [half](../assets/templates/beauty/half.txt) | [body-three](../assets/templates/beauty/body-three.txt) | [board](../assets/templates/beauty/board.txt) |
| 帅哥 | [portrait](../assets/templates/handsome/portrait.txt) | [head-four](../assets/templates/handsome/head-four.txt) | [half](../assets/templates/handsome/half.txt) | [body-three](../assets/templates/handsome/body-three.txt) | [board](../assets/templates/handsome/board.txt) |
| 通用3D | [portrait](../assets/templates/cg/portrait.txt) | [head-four](../assets/templates/cg/head-four.txt) | [half](../assets/templates/cg/half.txt) | [body-three](../assets/templates/cg/body-three.txt) | [board](../assets/templates/cg/board.txt) |
| AAA CG | [portrait](../assets/templates/aaa/portrait.txt) | [head-four](../assets/templates/aaa/head-four.txt) | [half](../assets/templates/aaa/half.txt) | [body-three](../assets/templates/aaa/body-three.txt) | [board](../assets/templates/aaa/board.txt) |

## 五个阶段的规格

| 模板 | 画幅与内容 |
|---|---|
| `portrait.txt` | 1:1，正面肖像 |
| `head-four.txt` | 16:9，一行0°正面、45°斜侧、90°侧面、180°背面头部四视 |
| `half.txt` | 3:4，正面waist-up半身，完整头顶，下缘位于肚脐下方至胯骨上方 |
| `body-three.txt` | 9:16竖版画布，同一行从左至右正面、90°侧面、180°背面三个完整全身 |
| `board.txt` | 3:4竖版，上方头部四视＋下方左侧半身＋右侧全身三视 |

模板中现有占位符填写本次内容，不把某个角色写入共享模板。未提供的参考不虚构。所有模式保留自己的画风、审美、肤质、体型与服装规则，不能用其他模式的设定覆盖它。

## 同一模式内的两种执行方式

- **快速整板生成**：使用所选模式的 `board.txt`，按实际人物、服装、妆造、特征参考与文字直接生成综合板，无须先制作中间图。模板带 `{{输出模式}}` 时填写“快速整板生成”。已有身份保持，不重新融脸。
- **分阶段精细制作**：依次使用同一模式的肖像、头部、半身和全身模板建立资产；最终读取已验收的头部、半身、全身三张完整源图，调用[拼接脚本](board-composition.md)。综合板模板可提供快速生成和布局规格，但已有源图不为“完成第五模板”再次生图。

真人通用的综合板就是原先已获认可的写实角色宫格板，现在与其四个建档阶段放在同一目录。前四个阶段保留普通基础服装要求；综合板按其原有规则在结尾填写人物与完整服装设计，未指定款式时先设计穿搭。实际成功输入见[城市通勤完整示例](../assets/examples/realistic-board-city-commute.txt)，示例人物与服装不固定为新角色默认设定。

通用3D与AAA的头部、全身分别使用独立head-four、body-three模板；综合板不承担视角补齐。头部条带与全身三视图各为一张整图，不拆分角度。已有全身不重复补齐；缺手、裁边、身份漂移等随机缺陷按相同提示词、参考与规格重抽，不自行改画幅或重设计。已有三张源图拼接时保留完整内容，最终实际尺寸由源图自然形成，不强制精确3:4。

五个角色模式共25份模板；下方四份服装/造型/状态模板是共用辅助模块，不计入角色模式或各模式五份模板。输出是参考图片，不包含真实绑定、网格或三维模型数据。

## 服装与裂变模板

- [原创服装四视图](../assets/four-view-template.txt)：填服装设计与风格字段，写实使用真实服装质感，CG/AAA使用对应角色的材质表现。
- [原穿搭提取](../assets/templates/outfit/extract.txt)：保留原款式、配饰和穿戴关系，不重新设计；新增风格字段用于匹配角色目标表现。
- [角色换装与受控妆造](../assets/character-styling-template.txt)：图1锁身份及排版，图2锁造型，图3～N补细节。仅妆造时不强行要求新服装图；使用模板内“不换装”分支。
- [剧情状态修改](../assets/templates/outfit/state.txt)：以已确认造型板为编辑目标，明确改变与保持项；支持无服装变化的伤口、泪痕、情绪等。

模板只负责本阶段输出，不追加完整镜头、场景或生视频指令。角色参数中不写未经用户确认的“已批准”。

## 更新与来源

当前包为模板维护源，不在执行时依赖oTATo Prompt。软件快照的标题和原始内容摘要见[来源清单](template-sources.json)，原服装技能来源保存在[历史来源](legacy-outfit-source.md)。以后修订保留来源记录，并在用户要求时同步软件；不做隐式双向覆盖。
