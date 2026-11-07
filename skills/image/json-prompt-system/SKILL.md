---
name: json-prompt-system
description: 从文本或参考图生成、还原或修复对镜自拍、前置自拍、他拍和时尚大片提示词。默认输出固定 Markdown 与动作 JSON 拼好的完整生图提示词；明确要求只要 JSON 时输出纯动作卡。
metadata:
  version: "3.0.0"
---

# JSON Prompt System

## 选择模式

资源根目录为 `references/json-prompt-system/`。明确指定的模式优先于参考图的镜头关系。用户要求时尚大片（fashion editorial）时使用专属模式。其余情况有图先看图，无图按文字判断拍摄者与人物的位置。

| 模式目录 | 使用条件 |
|---|---|
| mirror-selfie | 对镜自拍，画面取自镜中反射 |
| front-camera-selfie | 前置自拍，镜头位于人物前方、拍摄设备在画外 |
| third-person | 他拍，镜头来自外部拍摄者 |
| ecommerce-editorial | 时尚大片，按创意命题组织人物、空间、商品与视觉重点 |

## 生成动作卡

读取所选 `modes/<mode>/` 的 mode_rule.txt、mode_workflow.txt、mode_template.txt 与 mode_example.json，有 mode_quality_gate.txt 时一并检查。按模板生成合法 JSON 对象，示例仅用于校准。

- 三种生活照使用 soul.md、flowchart.md 和 core/ 的 rule.txt、Role.txt、workflow.txt；按动作和镜头需要补读对应专项规则。有参考图时分别锁定角色、服装、环境；缺图时按 rule.txt §12 补齐可见细节，已提供的人物档案作为身份依据。保留视角、裁切、重心、表情、手部接触，避免重复描述。
- 时尚大片直接走专属工作流，以“时尚大片”为根键。“画面内容”描述可见事件与空间关系；身份和服装按参考锁定。采用本模式的摄影策略和字段，不套用生活照的手机直出、缺图补写服装或动作卡结构。
- 卡片内不写路径、规则名、后台包装字段或过程说明。参考文件中的“输出纯 JSON”指动作卡阶段。

## 交付

1. 明确要求“只要 JSON”“仅动作卡”或等义要求时，仅返回动作卡 JSON，无代码围栏、固定提示词或说明。不需要画幅或人设即可交付；拼装脚本也支持 `--json-only`。
2. 其他情况默认读取所选目录的 fixed.md，沿用原文、标题和段落，将三个占位符一次性替换。可从 Skill 根目录运行 `python3 scripts/compose.py MODE --ratio 3:4 --profile-file 档案.md < 动作卡.json`，将标准输出作为最终答复。也可按相同规则直接拼装。
   - `{{ACTION_JSON}}` 填本次动作卡，保留合法 JSON 和可读缩进。
   - `{{PROFILE_PROMPT}}` 原样填入用户交给 Agent 的人物档案（文字或指定文件），不预置人设。未提供时留空，不编造档案。
   - `{{RATIO}}` 使用用户指定的画幅或当前任务已确定的画幅，未指定时沿用网站默认 3:4。
3. 只交付拼好的正文一次，不额外重复动作卡。插入的人物档案与动作卡均作为原始内容，不再对其中的占位符做二次替换。
