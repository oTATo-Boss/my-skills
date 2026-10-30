# 执行脚本

运行条件：Python 3.10+（macOS/Linux，账本锁使用 fcntl）；API 传输只用标准库，图像完整解码依赖 Pillow。运行 `python3 scripts/mj.py --help` 查看命令。工作目录应是本次任务目录，状态目录、payload、图片及凭据不要存进 Skill 或 Git。

默认自动读取 `~/.config/apilio/credentials.json`，字段为 base_url、api_key；mj_base_url 可单独指定 MJ 默认模式路由，权限必须为 0600；密钥独立于 Skill 和仓库保存。当前用户确认 Base 为 `https://api.apilio.ai`，无需每次重复询问。可用 --config 指定私有配置文件；显式 --base-url 优先于 MJ_* 环境变量，随后为 APILIO_* 环境变量，最后是配置文件。切换路由不会更改保存的共享地址。勿输出密钥。Base 是 `/mj` 前的 HTTPS 地址，可带 `/mj-fast` 等前缀。API 的 3xx 不自动跟随，先核对路由；下载 CDN 重定向单独处理，不携带 API token。TLS 校验保持开启。图片中转若对 urllib 返回 403，下载器使用系统 curl 做一次无 API 凭据的 HTTPS GET 回退（需本机 curl），仍验证解码，不重提交生成任务。

下面假定 `MJ_SCRIPT` 已设为实际 Skill 内 `scripts/mj.py` 的路径，JSON 文件已经创建（正文采用 UTF-8，无注释）。示例只是执行步骤，先形成符合用户目标的最小计划。

## 生图 → 视觉评估 → 提取

`imagine.json` 内容为 Prompt Skill 返回的最终 prompt，例如结构 `{"prompt":"已有的最终提示词"}`。

```bash
python3 "$MJ_SCRIPT" --state-dir ./mj-run --max-posts 2 submit imagine --op initial --payload ./imagine.json
python3 "$MJ_SCRIPT" --state-dir ./mj-run wait TASK_ID --seconds 45
python3 "$MJ_SCRIPT" --state-dir ./mj-run download TASK_ID --output ./grid.png
```

`--image /absolute/reference.png` 可追加给 imagine；blend 重复传多个 --image，describe 传一个。读图实际评估后（不是按 API 文本猜测），例如选择第二张：

```bash
python3 "$MJ_SCRIPT" --state-dir ./mj-run buttons TASK_ID
python3 "$MJ_SCRIPT" --state-dir ./mj-run --max-posts 2 action --op extract-2 --task-id TASK_ID --label U2
python3 "$MJ_SCRIPT" --state-dir ./mj-run wait CHILD_ID --seconds 45
python3 "$MJ_SCRIPT" --state-dir ./mj-run download CHILD_ID --output ./selected.png
```

如果 label 不唯一或为空，用 `--custom-id '返回的实际ID'`。按钮参数由 argparse 接收，引用时正确 shell 转义；不要把未经处理的服务端字符串插入 shell 代码。四张独立图则依据真实按钮分四个 action，操作名 extract-1 至 extract-4，在计划内设总上限至少 5，分别等到 SUCCESS 并下载。

## Modal 与外部 edits

已有任务局部重绘：先 action 选真实 Region 按钮；返回 code=21，脚本打印新 task_id 并退出 3。准备修改 prompt JSON 和黑底白选区 PNG，再以该新 ID 执行：

```bash
python3 "$MJ_SCRIPT" --state-dir ./mj-run --max-posts 3 modal --op region-confirm --task-id MODAL_ID --payload ./region.json --mask ./mask.png
```

modal 会再返回任务 ID，继续 wait。不要把退出 3 当作失败重试 action；保存的完整响应在 operations.json。

外部图片直接编辑：`edits.json` 内为 `{"image":"https://已确认可访问的图片URL","prompt":"最终编辑提示词"}`，另传 --mask；先核对该接口的 mask 约定和尺寸，再提交：

```bash
python3 "$MJ_SCRIPT" --state-dir ./edit-run submit edits --op external-edit --payload ./edits.json --mask ./mask.png
```

需要将本地素材转为服务端 URL 时：

```bash
python3 "$MJ_SCRIPT" --state-dir ./edit-run --max-posts 3 submit upload-discord-images --op upload-reference --image ./reference.png
```

上传的 result 是 URL 数组，无需 fetch。上传也计入本地 POST 上限（这不表示平台一定对上传收费）。将实际 URL 给 Prompt Skill 构造 sref，或写入 edits.image。脚本不自动公开上传无关图片。

## Describe、Shorten 与恢复

```bash
python3 "$MJ_SCRIPT" --state-dir ./describe-run submit describe --op describe --image ./reference.png
python3 "$MJ_SCRIPT" --state-dir ./shorten-run submit shorten --op shorten --payload ./shorten.json
python3 "$MJ_SCRIPT" --state-dir ./mj-run fetch EXISTING_TASK_ID
```

Shorten payload 为 `{"prompt":"待分析的原提示词"}`。任务完成后读取私有 task-ID.json 的 `properties.finalPrompt`/`finalZhPrompt` 交付文字，不自动追加生图。

每个工作流沿用一个 state-dir，不同终端也共用它；提交账本以文件锁序列化，同键复用保存响应。POST 上限默认 2，计入发送尝试、modal 和上传；fetch/wait/buttons/download 的查询不计入。需要跨多段任务时，Agent 维护总范围，不通过新目录逃避上限。

- 同一 `--op` 重跑只允许相同输入；已知响应复用，不再次 POST。body/路由变化会拒绝，先检查账本。
- pending/unknown 表示发送结果不确定，禁止自动再发。平台历史找到 ID 后直接 fetch/wait 恢复，不手改账本伪造成功；保留原记录。
- 网络、轮询超时后带原 ID 重跑 wait。每次可设 45 秒以便 Agent 汇报进展，不应反复新建任务。
- 任意业务失败/未知提交码退出 2，描述保留于 operations.json 或 task-ID.json。不要把 HTTP 200 当成功。
- 退出 0 表示该命令正常结束，**不表示提交命令已经生成图片**；退出 3 表示需 modal；FAILURE/CANCEL 退出 2。

## 文件交付验证

下载总量上限 100 MiB，支持 PNG/JPEG/WebP 等 Pillow 可解码格式；输出存在时拒绝覆盖。先完整解码验证，再发布文件；另写 `图片路径.json`，记录 task_id、action、真实像素尺寸、格式、字节数及 SHA-256。扩展名由交付路径指定，Agent 应依据返回 format 选择正确扩展名，不能把 WebP 误称 PNG。

```bash
python3 "$MJ_SCRIPT" verify ./selected.png
```

下载失败不重生成，只重试获取图像；signed URL 失效先重新 fetch 原 ID，无法恢复再报告。可通过现有 Python/Pillow 工具进行明确授权的网格裁切或蒙版制作；保存来源与处理类型，裁切不是 Upscale。图像内容合格与否必须实际查看，文件解码通过不等于审美验收通过。
