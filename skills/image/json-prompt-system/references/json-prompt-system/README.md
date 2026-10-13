# json-prompt-system

面向图像生成管线的**动作变量层**提示词规范仓库：由规则文本与 JSON 模板驱动 Agent，产出可直接拼进完整生图提示词的结构化 JSON（姿势、镜头关系、表情、物理逻辑、构图与手机直出质感等），**不包含可执行代码**。

## 你在整个系统里的位置

本仓库的 JSON 通常只是完整提示词的一部分。外层常见固定块包括（名称以你的实际模板为准）：

- Technical Specifications
- Five-Reference Protocol（多模态合成）
- Core Directive、Physics & Camera Constraints、Character Profile
- 人物、身材、手机、背景、服装等参考图

职责边界详见 `core/pipeline_context.txt`（仅供 Agent 内部阅读，不得写入成品 JSON）。

## 目录结构

| 路径 | 作用 |
|------|------|
| `core/` | 跨模式规则、工作流、角色定义、坏案例、细节控制、模式路由等 |
| `modes/<mode>/` | 各拍摄模式的规则、工作流、模板、示例、质量门 |

### 根目录说明文档

| 文件 | 作用 |
|------|------|
| `README.md` | 本说明 |
| `flowchart.md` | 启动与总流程：图+文 / 仅图 / 仅文 如何分支，再汇入统一执行链 |
| `soul.md` | 系统气质、原则与非谈判边界 |

## 支持的模式（mode）

| mode | 典型场景 |
|------|-----------|
| `mirror-selfie` | 对镜自拍、越肩镜拍、镜前动作；镜面关系必须成立 |
| `front-camera-selfie` | 前置自拍、举机向己；设备多在画外，强调手臂延伸与近拍关系 |
| `third-person` | 他拍、第三视角；可写场景、支撑、氛围、镜头语言等更完整照片结构 |
| `ecommerce-clothing` | 电商服装渲染；Ghost Mannequin、商品立体主视角、工艺特写、功能展示图 |
| `ecommerce-tryon` | 电商模特上身；商品展示优先的模特商拍效果图 |

路由逻辑见 `core/mode_selector.txt`。

## Agent 推荐阅读顺序

每次任务到达时优先读 `flowchart.md`，对齐入口：仅图须先分析再选 mode；仅文须先解析命令；图+文直接并入统一流程。

1. `core/rule.txt` -> `core/Role.txt` -> `core/pipeline_context.txt` -> `core/workflow.txt`
2. `core/detail_control_logic.txt` -> 生活图 mode 继续读 `core/women_selfie_presentation_logic.txt`、`core/visual_anchor_abstraction.txt`、`core/expression_intensity_logic.txt`、`core/original_pose_invention_logic.txt`、`core/anatomy_pose_sanity.txt`、`core/expressive_pose_translation.txt`、`core/seated_pose_anatomy_library.txt`、`core/output_density_control.txt` -> `core/mode_selector.txt`
3. 选定 mode 后：`modes/<mode>/mode_rule.txt`、`mode_workflow.txt`、`mode_example.json`、`mode_template.txt`
4. 按需：`mode_quality_gate.txt`、`core/bad_cases.txt`、`core/expressive_pose_examples.txt`；以图还原时加 `core/image_restore_checklist.txt`

## 输出约定

- 成品为**纯 JSON**，结构对齐当前 mode 的 `mode_template.txt`。
- 禁止在成品中出现文件路径、规则名、开发说明、引用来源或不可执行元信息。
- 若用户要求保存文件，使用当前工作目录中用户指定的位置；未指定时只输出 JSON，不自行创建输出目录。

## 关键约束（摘要）

- 只处理日常社媒照片语境下的动作变量。
- 不属于动作变量层的要求只可转为安全的构图、边界、姿态和表情变量；不属于动作变量层的部分不写入 JSON。
- `mirror-selfie` 与固定场景参考图对接时：JSON 内不写具体背景、环境、灯光（由参考图与外层承担）。
- `ecommerce-clothing / ecommerce-tryon` 只在效果库或用户显式指定电商任务时启用；动作库 AUTO 只在前三个生活动作 mode 中判断。
- 全 mode 不写单反式虚化 / bokeh / 专业后期式修背景；锚定普通人手机原相机随拍，可选用极轻颗粒或社交压缩质感。
- 表情与氛围优先叙事触发式写法，见 `core/detail_control_logic.txt` 与各 `mode_rule.txt`。
