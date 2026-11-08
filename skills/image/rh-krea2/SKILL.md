---
name: rh-krea2
description: "Use RunningHub Krea2 for single-reference image editing with the user's fixed model and two LoRAs. Supports direct API submission, batch jobs, shared RH concurrency, task recovery and verified image downloads. Use when the user asks for rh-krea2 or this RunningHub workflow."
metadata:
  version: "1.0.0"
---

# RH Krea2

直接调用 RunningHub AI 应用 `2080156609159286785`，不依赖网页执行。用于单参考图编辑；当前只核实了一个图片输入，不推断支持纯文生图或多参考图。先读取用户指定图片，明确保留项与修改项，再编写本次提示词；平台示例提示词不是用户指令。

## 固定配置

用户 2026-11-08 截图优先于 API 示例，每次提交显式发送：

| 配置 | 文件名 | 强度 |
|---|---|---|
| 底模 · 130 | `FinePorn_V6.1_INT8_20261105.safetensors` | — |
| LoRA1 · 133 | `realism_engine_krea2_v3.1_new.safetensors` | 0.4 |
| LoRA2 · 145 | `Krea-2-Turbo-HTT_c1-st10000.safetensors` | 0.4 |

无已核实触发词，执行器不自动追加或改写提示词。文件名只指向平台云端权重，本包不分发模型；模型名称不替代用户的实际内容要求。

| 输入 | 默认与范围 |
|---|---|
| images | 必填，一张本地参考图；本地限制 30 MiB |
| prompt | 必填，非空；可使用完整 JSON 提示词字符串 |
| aspect | 默认9:16，关闭原图比例；按任务选1:1、2:3、3:2、3:4、4:3、9:16、16:9、21:9；显式original可保持原比例 |
| megapixels | 1.0（用户要求约1K，以百万像素档表达）；本地限制0.1–16，实际宽高由工作流确定 |
| reference_strength | 2.25；平台说明范围 1–6，越大越偏向参考一致性、可改动程度越小 |
| count | 1；本地限制 1–4 张，实际结果数量以输出为准 |
| instance | default，沿用用户所给 API 示例；可显式选 plus / ultra |

原图比例对应 `142/value=false`；选其他比例时必须切换为 true，不能只改比例文本。ZIP 关闭，节点132的额外调节固定0。未核实种子、采样器、负向提示词、遮罩或自定义宽高输入，不传猜测字段。详细节点和证据见 [references/api.md](references/api.md)。

## 执行

依赖 Python 3.9+、requests、Pillow；缺失时安装本包 `requirements.txt`。`SKILL_DIR` 指本次读取的 Skill 目录。任务输入、回执和图片写在用户任务目录，避免写入 Skill 包。

创建 `job.json`，图片路径相对于此 JSON，也可写绝对路径：

```json
{
  "prompt": "保留参考图中杯子的形状、构图和背景，只将杯身改为蓝色，保持自然光影。",
  "images": ["cup.png"],
  "aspect": "9:16",
  "megapixels": 1.0,
  "reference_strength": 2.25,
  "count": 1,
  "instance": "default"
}
```

```bash
python3 "$SKILL_DIR/scripts/rh_krea2.py" /absolute/path/job.json --dry-run
python3 "$SKILL_DIR/scripts/rh_krea2.py" /absolute/path/job.json --submit --state /absolute/path/output/edit-01.json
python3 "$SKILL_DIR/scripts/rh_krea2.py" --resume --state /absolute/path/output/edit-01.json
```

默认仅离线预检，不读 Key、不联网、不上传。用户已要求生成且授权使用素材时执行 `--submit`；创建／安装此 Skill 本身不包含收费生成授权。

凭据依次读取 `RUNNINGHUB_API_KEY`、`RUNNINGHUB_ENV_FILE` 指定文件、`~/.config/runninghub/.env`，与其他 RH Skill 共用。env 文件格式 `RUNNINGHUB_API_KEY=...`，建议0600权限；不将密钥写入 job、日志或仓库。

批量文件为 `{"jobs": [{...}, {...}]}`，每项沿用单任务字段，可加唯一 `name`（英文字母、数字、短横线、下划线）。使用 `--submit --output /absolute/path/output`；先对整个批次 `--dry-run`。默认并发，下载不占远端额度。

Krea2、Qwen、H3 同一 Key 合计最多3个远端在途任务，通过兼容的 `rh_queue.py` 和 `~/.local/state/runninghub/queue/` 协调；其他机器或未接入的网页任务不在本机协调范围内。提交不明和查询超时不自动释放预约，不能通过更换回执名重提。

## 恢复和交付

提交前原子创建回执，已有回执拒绝再次提交。断线、提交超时或无 taskId 记为 `SUBMIT_UNKNOWN`，先核对平台任务／消费记录。已经拿到 taskId 始终查询原任务；查询超时不代表取消。下载失败可再次 resume，不创建生成任务。

从平台核实到 taskId 后，没有原回执时用新路径恢复：

```bash
python3 "$SKILL_DIR/scripts/rh_krea2.py" --resume --task-id VERIFIED_TASK_ID --state /absolute/path/output/recovered.json
```

原回执有不明提交预约时，先将已核实 ID 绑定至原回执，再 resume：

```bash
python3 "$SKILL_DIR/scripts/rh_queue.py" --receipt /absolute/path/output/edit-01.json --task-id VERIFIED_TASK_ID
```

`--max-wait` 默认1200秒，分别用于本地排队与远端等待；超时后保留回执。批次部分失败只处理对应回执，不重提整批。

下载全部可识别图片结果，下载请求不携带 RH Key；Pillow 完整解码后才标记为本地图片。结果链接有效期24小时，及时下载。交付本地绝对路径和图片预览、taskId、实际尺寸及平台 usage；缺少 usage 或 SUCCESS 无图片时如实说明，不自动反复生成。

## 验证与来源

```bash
python3 -B -m unittest discover -s "$SKILL_DIR/tests"
```

离线验证请求映射、输入校验、CLI 预检、批量并发、防重复提交、超时恢复及媒体下载；共享队列检查需同一技能库中的 Qwen/H3 包。平台节点已只读核对，当前固定模型组合尚未做收费出图实测。来源、许可未知项及版本记录见 [SOURCE.md](SOURCE.md)。
