# 任务构造、生成与恢复

Agent 根据任务选择时长、画幅、图片、提示词与交付目录。无足够任务信息时询问；至少一张图片，纯文生未验证。不将任务素材或凭据写进技能目录。

```bash
python3 "$SKILL_DIR/scripts/build_jobs.py" \
  --prompt-file /绝对路径/任务/prompt.txt --name shot01 \
  --seconds 5 --aspect 9:16 --image /绝对路径/任务/参考.png \
  --output /绝对路径/任务/jobs.json
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" /绝对路径/任务/jobs.json \
  --output /绝对路径/任务/素材 --dry-run
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" /绝对路径/任务/jobs.json \
  --output /绝对路径/任务/素材
```

示例只是参数用法，不作为时长或画幅默认值。构造器拒绝覆盖既有 jobs。生成操作需属于用户授权的当前任务；dry-run 不联网、不提交、不证明线上参数可行。

`--quality 1080P` 使用 2 MP 和 Ultra，`--quality 720P` 使用 1 MP；也可用 `--megapixels` 指定数值。未指定为 1 MP。`--instance default|plus|ultra` 可选，缺省 Plus，但 2 MP 及以上必须 Ultra；其他数值线上节点提示超过 0.8 MP 需 Ultra，按用户指定默认不自动切换。不能保证对应标准 P 档的准确像素。

重复传 `--image` 最多 6 张、`--audio` 最多 2 段；实际图像数量自动设置到节点 827。自动提示词开启时，未使用的图片节点复用最后一张参考图，避免平台合并空图片报错；实际使用张数不变，上传按文件去重。关闭自动提示词时，未用节点为 `None`。单文件限 30 MB。`--auto-prompt on|off` 默认 on，`--output-format video|zip` 默认 video。ZIP 将下载保留，但客户端没有视频时不会判为视频成功。

作者示例默认三组 LoRA：`MysticXXX-ref2va-V4.safetensors` 强度 0.4、`HMNSFW-AIO-V2.5.safetensors` 强度 0.5、`H3_Motion_BoosterV2.safetensors` 强度 0.6；触发词 `dynv2,`。用 `--lora-1-name` / `--lora-1-strength` 到 `--lora-3-name` / `--lora-3-strength` 及 `--lora-trigger` 覆盖。输出是否适合当前任务另行检查。

参数构造示例 `--quality 1080P` 自动选 Ultra；不支持视频参考和采样步数。示例不证明高分辨率、音频或不同 LoRA 组合可运行。

`<name>_submitting.json` 记录提交前 payload 与状态；`<name>_<taskId>.json` 保存状态、usage、文件和检查。异常退出后不可盲目重提：

```bash
python3 "$SKILL_DIR/scripts/rh_minimax_h3.py" --resume TASK_ID \
  --name 原任务名 --output /绝对路径/原任务/素材
```

有 taskId 只恢复查询下载；没有 taskId 的 `SUBMIT_UNKNOWN` 先查平台任务和消费。无有效视频时保留回执及下载文件，不报告视频成功。旧应用任务仍可恢复，但旧应用 jobs 和无 appId 的旧 jobs 拒绝直接提交；须重新根据新应用构造，不能静默转投。
