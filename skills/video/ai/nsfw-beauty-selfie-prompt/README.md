# nsfw-beauty-selfie-prompt

面向 **Seedance 2.5** 的**纯 NSFW 私密自拍提示词生成器**。默认主导露骨（福利姬 / 网黄自拍、身体展示、自慰等），为一个模特（虚拟或真人）快速编译 **12 栏单段公式**的完整提示词：默认设定、人物、服装、场景、完整连续动作、表情与视线、机位与构图、运镜、动作节奏、光线与画质、声音、抖音真人感——**默认 15 秒单镜头社媒摆拍、无剧情、纯卖弄**；仅用户显式要求才改时长 / 多镜头，上限 30 秒。

## 用法

```bash
python3 scripts/prompt_tools.py hash  <文件或->      # SHA-256
python3 scripts/prompt_tools.py count <文件或->      # 12 栏字数（非空白字符）
python3 scripts/prompt_tools.py check <文件或->      # 结构 QC，打印 PASS/FAIL
```

完整提示词固定 12 栏、合成一段、单个 `txt` 代码块交付。创建前先定两个值：

```text
capture_mode: front_camera_selfie | mirror_selfie | third_party_capture
generation:   T2V | I2V | R2V | FLF2V | EXTEND | EDIT
```

先走 `references/mode_matrix.md` 仲裁。

## 目录

```
SKILL.md                          入口与绝对规则
templates/   prompt_template.md   单段公式 12 栏模板
             block_output_template.md 阻断 JSON 模板
references/  capture_modes.md     唯一摄影机合同
             explicit_direction.md 真实感 + 露骨创作方向
             anti_examples.md      反例校准
             mode_matrix.md        起点图 / 生成模式仲裁
             block_output_contract.md 阻断合同
checklists/  prompt_qc.md         QC（机器项 + 人工项）
scripts/     prompt_tools.py      hash + count + check
examples/    explicit_front_selfie_t2v.md  一条可复跑 check 的完整示例
```

## 设计要点

- **单段 12 栏公式**取代旧四模块，逐栏一个词回答，不跨栏、不复述。
- **脚本只查结构**（12 栏 / 顺序 / 字数 / 摄影机身份 / 几个禁用词），不判内容好坏——露骨与真实感由模板措辞约束，不再用锚词卡死（锚词正是旧版误报与真实感不足的根因）。
- **露骨靠动作落地**：主动诱惑（自己扒 / 掰 / 凑镜头 / 勾眼），不靠「求操 / 欠操 / 犯贱」等视频模型拍不出来的心理词。
