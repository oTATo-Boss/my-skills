# 任务构造、生成与恢复

Python 3.9+，安装 `python3 -m pip install -r "$SKILL_DIR/requirements.txt"`；有 ffprobe 可记录视频实际尺寸和时长。提示词、jobs、回执和视频放当前任务目录，不能放安装包内。

## 文生视频

由 agent 将用户需求写入 UTF-8 `prompt.txt`。命令中的路径替换为真实任务目录：

```bash
SKILL_DIR="$HOME/.agents/skills/video/ai/rh-minimax-h3"
python3 "$SKILL_DIR/scripts/build_jobs.py" \
  --prompt-file /绝对路径/任务/prompt.txt \
  --name shot01 --seconds 15 --quality 720P --aspect 9:16 \
  --output /绝对路径/任务/jobs.json
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" /绝对路径/任务/jobs.json \
  --output /绝对路径/任务/素材 --dry-run
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" /绝对路径/任务/jobs.json \
  --output /绝对路径/任务/素材
```

构造器不联网、不上传、不提交，拒绝覆盖已有 jobs。默认 15 秒、0.9 MP、9:16、8 步、Plus 实例；明确任务规格优先。像素档位并不保证标准 720×1280 等精确尺寸。

## 图像、音频和视频参考

在构造命令上加 `--image /绝对路径/图.png`（最多重复 6 次）、`--audio /绝对路径/音.wav`（最多重复 3 次）、`--video /绝对路径/视频.mp4`。顺序分别对应参考图 1–6 和音频 1–3。视频参数会打开参考视频开关。每个文件不能超过 30MB；特殊编码、时长要求仍以应用为准。

构造器将本地媒体写为 `{"$upload":"/绝对路径"}`；客户端上传后换成平台 fileName。提示词中写文件名不会自动上传。可用 `<Subject N>`、`<Picture N>` 引用对应图；若确实需要台词，应用快照示例使用 `<d>[Chinese] 台词</d>`，声音和角色表达仍服从当前项目。

## jobs 与批量

`jobs.json` 顶层 `jobs` 是任务数组，每项包括唯一 `name`、`instanceType`、`usePersonalQueue`、完整 `nodeInfoList`（每项 `nodeId`、`fieldName`、`fieldValue`）。合并多个构造器结果的 `jobs` 数组即可批量执行。同一进程对同一绝对路径去重上传；跨次执行不要长期复用已过期上传名称。

像素 2.0 MP 和非默认开关需按 [api.md](api.md) 核实；只改真实存在的字段，不把说明文字、占位符、MP 单位或“1080P”直接传给像素节点。需要新发现的映射时 `--node-map /绝对路径/node_map.json`；应用更换 nodeId 后须核对构造器，不能继续假定旧节点。

## 输出和异常恢复

- `<name>_submitting.json`：最终请求、上传映射及提交状态，不含 Key。
- `<name>_<taskId>.json`：远端状态、usage、原回包、下载文件与技术检查。
- `<name>_<taskId>_<序号>.mp4` 等：全部结果，包括附带图片、ZIP、音频。

`--max-wait` 默认为 2400 秒，查询间隔 15 秒。超时不说明远端停止，不换目录重提。查询网络错误也会保留未结束提交并停止新的排队任务。

```bash
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" \
  --resume TASK_ID --name shot01 --output /绝对路径/原任务/素材 --max-wait 2400
```

恢复只查询和下载；成功时会将同目录、同名、同 taskId 的提交回执标 DONE。DONE 后客户端允许同名再次生成，但 agent 不应因此自动重试收费。没有 taskId 的 SUBMIT_UNKNOWN 要先查平台任务与消费；不能用删除记录绕过重复保护。

如果只返回 ZIP 或图片，客户端保留结果和费用但不判视频成功。ffprobe 只证明视频流可解析，完整解码、内容、声音、审美要按需求另查。将实际 output、usage 与任务请求分开报告。
