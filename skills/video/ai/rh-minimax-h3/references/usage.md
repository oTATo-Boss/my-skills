# 小白版 V2：任务构造、生成与恢复

Agent 按任务指定时长、画幅、提示词、参考图和交付目录；至少一张图片，纯文生未验证。不将素材或凭据写入技能目录。

```bash
python3 "$SKILL_DIR/scripts/build_jobs.py" \
  --prompt-file /绝对路径/任务/prompt.txt --name shot01 \
  --seconds 15 --aspect 9:16 --quality 720P \
  --image /绝对路径/任务/人物.png --audio /绝对路径/任务/音色.wav \
  --output /绝对路径/任务/jobs.json
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" /绝对路径/任务/jobs.json \
  --output /绝对路径/任务/输出 --dry-run
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" /绝对路径/任务/jobs.json \
  --output /绝对路径/任务/输出
```

示例不规定所有任务的时长或画幅。构造器拒绝覆盖已有 jobs；dry-run 不上传、不提交、不验证线上节点或账户余额。

- `--quality 480P|720P|1080P` 分别设置 **0.5、1、2 MP**；默认 720P（1 MP）。这是用户指定的档位映射，实际输出宽高不一定是标准分辨率。也可 `--megapixels` 指定数值。默认 Plus；2 MP 及以上使用 Ultra，显式传入其他实例会拒绝。
- `--image` 重复 1–6 次，`--audio` 重复 0–2 次。单文件限 30 MB，按参数顺序绑定素材，只提交所用槽并按文件路径去重上传。
- 四组 `--lora-N-name`、`--lora-N-strength`（N=1–4）可单次覆盖用户指定默认值；`--lora-trigger` 可覆盖触发词。换 LoRA 时应一起检查触发词，构造器不会推断新的触发词。
- 默认 `--output-format video`；`zip` 映射示例布尔开关 `true`，ZIP 输出未实测。版本开关默认沿用已成功样例的 `true`，可显式 `--version-switch true|false`；v1/v2 的布尔对应关系尚未核实。
- `--auto-prompt true|false` 控制自动提示词，默认为 `true`。其他可用参数见[节点映射](api.md)。

执行器在校验前略过空的可选素材槽。旧 jobs 若有 `827/value`，用原计数保留前 N 个参考图槽，移除其余占位图和计数字段。若真实参考槽与旧计数不符，先重建 jobs。此调整在内存中完成。

`<name>_submitting.json` 保存不含 Key 的请求与状态，`<name>_<taskId>.json` 保存状态、usage 和结果检查。平台返回 `803` 且无 taskId 时回执为 `REJECTED`，先按节点错误修正参数。提交结果不明时先查平台。已有 taskId 用以下命令恢复查询和下载。

```bash
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" --resume TASK_ID \
  --name 原任务名 --output /绝对路径/原输出目录
```

其他应用的历史任务可恢复，但其他应用 ID 和缺 appId 的 jobs 拒绝提交；查询恢复与当前应用选择相互独立。
