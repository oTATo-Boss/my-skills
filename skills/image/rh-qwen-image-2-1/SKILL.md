---
name: rh-qwen-image-2-1
description: Use when 用户指定 RH-Qwen Image 2.1 或 RunningHub 的 Qwen Image 2.1 多图编辑 AI 应用，进行单图修改、多图融合、人物换装、场景替换或风格参考编辑。
metadata:
  version: "1.0.1"
---

# RH-Qwen Image 2.1

直接调用 RunningHub **Qwen Image 2.1 多图编辑** AI 应用，ID `2101915284503654402`。与 `rh-minimax-h3` 使用相同的 RunningHub v2 上传、提交和查询原理，应用 ID 与节点映射各自独立。支持 1–6 张有序参考图和非空编辑指令；本技能不提供纯文生图。

## 直接 API 执行

使用本包 `scripts/rh_qwen.py` 直接请求 `https://www.runninghub.ai/openapi/v2`：上传参考图 → 提交 `/run/ai-app/2101915284503654402` → 按 taskId 查询 `/query` → 下载结果。不依赖 RH Studio、浏览器登录或网页操作。缺少 API Key 时按下方凭据配置处理。依赖 Python 3.9+、requests、Pillow；缺失时按当前环境的依赖管理方式安装。

此版本已核对线上页面及公开前端的节点构造，完成离线模拟验证及两次真实编辑：两图杯身图案迁移、三图人物/穿搭/卧室融合。两次均为 default 实例、2K、1 张，上传、提交、查询、下载与解码成功。其他组合仍未实测。执行时若节点或接口变化，核对 [接口与证据](references/api.md) 的来源，不套用其他应用配置。

## 参考图和指令

读取用户指定参考图，明确图1至图6的作用。人物身份、服装、背景、风格分别对应到具体图号；按实际上传顺序写指令，不能交换图号。输入不足且影响执行时才询问，不擅自使用无关私人素材。

指令采用「主图与保留内容 → 各图用途 → 要修改的部分 → 自然融合要求」。例如两图换装：

> 以图1为主图，保留图1人物的身份、五官、发型、姿态和原有背景。将人物服装替换为图2中的服装，准确保留图2的版型、颜色和材质；根据图1的身形与姿势自然适配衣物，保持光线、透视和遮挡关系一致。

换装时图2提供服装，不默认移植其人物身份；多图融合不默认拼成参考图网格。用户指定的文字原样写入指令，实际文字准确性以输出为准。

| 参数 | 默认值与范围 |
|---|---|
| 参考图 | 1–6 张，每张不超过 30 MiB；传入 images 数组顺序就是图号 |
| 比例 | 默认 9:16；original、1:1、3:2、4:3、16:9、2:3、3:4、9:16 |
| 清晰度 | 默认 2K；1K / 2K / 4K 是档位，不保证精确输出尺寸 |
| 张数 | 默认 1；1–4 |
| 实例 | 默认 default；plus / ultra 仅在用户指定或应用要求已核实时选择 |

当前应用没有已核实的自定义宽高节点，因此脚本不开放任意尺寸。没有已核实的种子、负向提示词、遮罩或采样器参数；需要避免的内容可写在编辑指令中。

## CLI 与恢复

创建 `job.json`（图片路径相对于该 JSON 所在目录，也可用绝对路径）：

```json
{
  "prompt": "以图1为主图，保留人物身份与原有背景，将服装替换为图2中的服装，保持光线、透视和遮挡关系自然一致。",
  "images": ["person.png", "outfit.png"],
  "aspect": "9:16",
  "quality": "2K",
  "count": 1
}
```

`SKILL_DIR` 指本次读取的本技能目录；在用户的任务输出目录执行，生成回执与图片不写入 Skill 包。

```bash
python3 "$SKILL_DIR/scripts/rh_qwen.py" /absolute/path/job.json --dry-run
python3 "$SKILL_DIR/scripts/rh_qwen.py" /absolute/path/job.json --submit --state /absolute/path/output/edit-01.json
python3 "$SKILL_DIR/scripts/rh_qwen.py" --resume --state /absolute/path/output/edit-01.json
```

默认仅预检；`--dry-run` 不读 Key、不联网、不上传、不验证账户或线上节点。用户已要求生成且授权素材上传时，可执行 `--submit`；创建或维护 Skill 本身不代表要执行收费生成。

Key 优先读 `RUNNINGHUB_API_KEY`，其次 `RUNNINGHUB_ENV_FILE` 指定文件，缺省为 `~/.config/rh-qwen-image-2-1/.env`。文件格式为 `RUNNINGHUB_API_KEY=...`，建议权限 0600；不要把 Key 放在 job、命令行参数、日志或仓库。已有 H3 私有配置可在用户授权复用时用 `RUNNINGHUB_ENV_FILE` 指向，不复制密钥进包。

提交前原子创建回执；已有回执拒绝再次提交。同一任务的提交超时、断线或缺少 taskId 视为 `SUBMIT_UNKNOWN`：先核对平台任务/消费记录，不换回执名盲重提。拿到 taskId 后始终 resume；查询超时并不代表任务取消。若只在平台查到了 taskId，用新回执恢复：

```bash
python3 "$SKILL_DIR/scripts/rh_qwen.py" --resume --task-id VERIFIED_TASK_ID --state /absolute/path/output/recovered.json
```

下载失败保留 taskId 与结果响应，再次 resume 只查询与下载。执行器遍历全部可识别图片结果，下载请求不携带 API Key，并用 Pillow 完整解码、记录尺寸。SUCCESS 无图片时明确报告，无验证图片不宣称出图成功。

交付所有图片的本地绝对路径及可显示预览、taskId、实际尺寸与平台 usage；usage 缺失如实说明。只在用户要求或任务明确需要时追加修改，不自动反复生成。

## 验证与来源

- 离线检查：`python3 "$SKILL_DIR/tests/test_qwen.py"`，覆盖槽位映射、防重复提交、超时恢复、多结果下载与无凭据媒体请求。
- [接口与证据](references/api.md)：字段、来源、变更核对方式及未验证范围。
- [SOURCE.md](SOURCE.md)：作者、来源、许可及版本记录；质量档案待评，不将离线测试称为实际出图验证。
