---
name: rh-minimax-h3
description: 使用 RunningHub 的 Minimax-H3（30s直出）应用生成视频；支持多图和音频参考、API Key 安全存入、节点任务构造、批量提交、查询恢复与结果下载。用户提到 RH-minimax-H3 或 RunningHub H3 时使用。
metadata:
  version: "2.0.0"
---

# RH-minimax-H3

调用 RunningHub **Minimax-H3（30s直出）多图生视频自动提示词-小白全能版**，应用 `2104753059472990209`。使用 RunningHub API Key，依赖 Python 3.9+、`requests`，可选 `ffprobe`。原有两个应用已从当前提交路径移除；旧任务仍可用 taskId 查询恢复，但旧 jobs 不能直接提交。

## 任务参数与默认策略

Agent 根据当前任务明确填写提示词、**时长 5–30 秒、画幅、参考图和输出目录**，不自行预设时长或画幅。至少 1 张、最多 6 张参考图；可选最多 2 段音频。纯文生及音频参考尚未线上验证。画幅可选 1:1、2:3、3:2、3:4、4:3、9:16、16:9、21:9。

用户指定的默认策略：**Plus 实例、自动提示词开启、直接输出视频、1 MP、作者示例的 3 组 LoRA 和触发词**。用户要求 1080P 时使用 **2 MP + Ultra**。1 MP 和 2 MP 是本技能的画质参数约定，不保证输出恰好为标准 720P/1080P 分辨率；报告实际尺寸。用户明确其他要求时按任务设置。

**线上节点提示超过 0.8 MP 需 Ultra**；用户指定的默认 1 MP + Plus 与之冲突，但已实测 5 秒可运行；其他时长仍须按任务验证，不自动降像素或切换实例。若远端失败，报告实际错误并与用户协调。2 MP 或以上强制 Ultra；详见 [api.md](references/api.md)。作者 LoRA 和自动提示词会影响内容，明确任务要求可覆盖；默认参数及 2 MP + Ultra 均已完成 5 秒生成和完整解码验证；30 秒、音频参考、纯文生仍未验证。

## 凭据

先执行 `python3 "$SKILL_DIR/scripts/credentials.py" status`，其中 `SKILL_DIR` 为本技能目录。优先读取环境变量 `RUNNINGHUB_API_KEY`，其次为 `~/.config/rh-minimax-h3/.env`；可用 `RUNNINGHUB_ENV_FILE` 指定文件。状态仅证明已配置，不证明 Key 有效或余额充足。

新 Key 用 `credentials.py set` 本机隐藏输入，权限 0600；从已授权项目导入用 `import-env --from-env /绝对路径/.env`。替换需用户要求并加 `--replace`。不得将 Key 写入技能、任务、日志、Git 或交付；详见 [credentials.md](references/credentials.md)。

## 使用与安全

按 [usage.md](references/usage.md) 构造 jobs；先 `--dry-run`，通过后才在当前任务授权范围内提交。Dry-run 不联网、不校验账户或节点在线有效性。素材上传后提交；每批最多 3 个在途任务，且不得超过账户可用额度。脚本保存提交请求和 taskId；提交不明或查询超时后停止排队，不盲目重试。

已有 taskId 用 `--resume TASK_ID --name 原名称 --output 原目录` 查询并下载，不重提。没有 taskId 的 `SUBMIT_UNKNOWN` 先查平台任务和消费记录。结果立即下载；报告 taskId、平台 usage、实际文件和尺寸/时长。usage 缺失时如实说明；ffprobe 不能代替完整播放与审美验收。

## 参考与验证

- [usage.md](references/usage.md)：构造、可选参数与恢复。
- [api.md](references/api.md)：节点、线上范围、默认策略和验证边界。
- [sources.md](references/sources.md)：来源、许可和历史版本。
- 离线行为：`python3 "$SKILL_DIR/tests/test_helpers.py"`；假服务：`python3 "$SKILL_DIR/tests/mock_test.py"`。假服务不调用 RunningHub。
