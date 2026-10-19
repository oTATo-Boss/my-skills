---
name: rh-minimax-h3
description: 使用 RunningHub 指定 MiniMax H3 AI 应用执行短视频或长视频生成；支持图像参考，短视频应用另有音视频参考，以及 API Key 安全存入、节点任务构造、批量提交、查询恢复和结果下载。用户提到 RH-minimax-H3、RunningHub H3 或 H3 长视频模式时使用。
metadata:
  version: "1.1.0"
---

# RH-minimax-H3

通过 RunningHub 的两个 H3 AI 应用生视频。使用 **RunningHub API Key**；依赖 Python 3.9+、`requests`，可选 `ffprobe` 检查视频流。

| 模式 | 应用 | 节点依据与范围 |
|---|---|---|
| `short`（默认） | `2084320751339032577`，原多参数视频应用 | 2026-10-12 快照及历史成功任务；5–15 秒，6 张图、3 段音频与 1 段视频参考；[节点](references/node_map.json) |
| `long` | `2103012816681041921`，新增长视频应用 | 用户 2026-10-19 提供的 API 示例；示例为 35 秒、0.5 MP、16:9、default 实例，暴露 6 张图；[节点](references/node_map_long.json)。尚未线上生成验证，时长上下限和空图片处理待核实 |

用户指定长视频时显式使用 `--mode long`。长视频示例未暴露音频/视频参考和采样步数节点，不套用短视频的这些参数或画质映射。节点细节见 [api.md](references/api.md)。

## 什么时候用

用户指定这个工具生视频、配置 Key，或查询并下载已提交的 H3 任务时使用。它负责执行生成；创作内容与项目的脚本确认、声音、输出目录要求沿用当前任务。不要把 oTATo 的角色和台词规则带到其他项目。

## API 存入

将本 Skill 所在目录记为 `SKILL_DIR`，从任何工作目录运行包内脚本。先执行：

```bash
python3 "$SKILL_DIR/scripts/credentials.py" status
```

默认从 `RUNNINGHUB_API_KEY` 环境变量读取，其次读取 `~/.config/rh-minimax-h3/.env`。指定项目配置时设置 `RUNNINGHUB_ENV_FILE=/绝对路径/.env`。文件只解析键值，不执行 shell。

- 新 Key：`python3 "$SKILL_DIR/scripts/credentials.py" set`，隐藏输入，保存权限 0600。
- 已有项目配置：`python3 "$SKILL_DIR/scripts/credentials.py" import-env --from-env /绝对路径/.env`，不回显、不改动原文件。
- 替换现有配置需加 `--replace`；仅在用户要求更新 Key 时执行。
- 凭据独立于开发目录与安装包。不得写入 Skill、jobs、提示词、回包日志、Git 或交付。具体路径、保存和优先级见 [credentials.md](references/credentials.md)。

`status` 只证明本机已配置，不能证明 Key 有效或有余额。没有 Key 时请用户在本机隐藏输入，不要求发进聊天。

## 怎么用

1. 明确当前任务的内容、时长、画幅、画质、参考文件和输出目录；已有授权持续有效。本技能不自行新增“任何项目无限收费”的授权，也不重复询问已授权任务。
2. 按 [usage.md](references/usage.md) 选择模式并构造 jobs。两份映射只用于各自应用；字段以该应用当前 API 页为准，参数失败或应用更新时按 [api.md](references/api.md) 重新发现。构造器清空未使用图像/音频，所有可选 LoRA 强度设为 0；短视频关闭视频参考、提示词优化、补帧和仅 ZIP 输出，关闭参考时保留其原快照字段；长视频清空示例文本触发词，未声明用途的数值/开关保留示例值。
3. 先 `--dry-run`，通过后执行生成：

```bash
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" /绝对路径/jobs.json \
  --output /绝对路径/当前任务/素材 --dry-run
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" /绝对路径/jobs.json \
  --output /绝对路径/当前任务/素材
```

Dry-run 校验应用 ID、结构、占位符、重名和素材文件；不联网、不检查余额，也不证明节点当前在线有效。短视频画质映射为 480P→0.4 MP、720P→0.9 MP、1080P→2.0 MP；实际支持取决于应用与实例。长视频直接用 `--megapixels` 指定 MP，示例默认 0.5，不把它换算为未经验证的 P 档位。分辨率均按真实输出报告。

4. 每个批次最多 3 个在途任务，且应低于账户可用额度。脚本并发限制仅覆盖本次进程；不要启动多个批次绕过额度。脚本先保存提交请求，再保存 taskId。提交不明或查询超时后停止新的排队提交。
5. 已有 taskId 使用恢复命令，复用原名称和目录，不再生成一次：

```bash
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" --resume TASK_ID \
  --name 原任务名 --output /绝对路径/原任务/素材
```

没有 taskId 的 `SUBMIT_UNKNOWN` 先查平台任务和消费记录；没有证据前不清理回执、不盲目重提。`SUCCESS` 也可能下载失败，仍优先恢复。只有明确远端失败或用户安排新尝试时，才创建新任务。

6. 结果立即下载，记录 taskId、usage、文件和检查；CDN 下载不附带 API Key。客户端检查容器文件头，有 ffprobe 时核对视频流、尺寸、时长；审美、参考一致性、声音和完整播放另按任务检查。汇报有效视频路径、真实尺寸/时长、taskId、usage 及未验证项；usage 缺失就说明未返回，不估算成实际费用。

## 按需参考

- 首次接入、API 存入或换 Key：[credentials.md](references/credentials.md)。
- 文生、图生、多参考、批量和断点恢复：[usage.md](references/usage.md)。
- 节点、接口、画质及故障：[api.md](references/api.md)。
- 来源、许可状态与版本：[sources.md](references/sources.md)。
- 本地假服务验证：`python3 "$SKILL_DIR/tests/mock_test.py"`；不调用 RunningHub。配置和构造器行为验证：`python3 "$SKILL_DIR/tests/test_helpers.py"`。
