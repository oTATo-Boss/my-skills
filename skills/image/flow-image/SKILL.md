---
name: flow-image
description: "Generate and edit images with Nano Banana 2.1 in Google Flow through the local Chrome DevTools CLI persistent session. Use for Flow/Nano Banana image requests, including multiple local reference images; reuse the user's existing Chrome login."
metadata:
  version: "1.2.3"
---

# Flow 图片生成与编辑

调用本机 `~/.local/bin/flow-image`，通过 Chrome DevTools CLI **1.12.0** 的常驻会话 `f10` 操作现有 Chrome。使用用户指定的 `bahadir` 主个人资料和固定 Flow 项目；在 Flow 的实际界面核对 **Nano Banana 2.1**。模型名称是页面选项，不是 API 模型参数。

## 执行

文生图：

```bash
~/.local/bin/flow-image image '一只坐在草地上的橘色狐狸，水彩插画' \
  --aspect 1:1 --output '/绝对路径/狐狸.jpg'
```

单张参考图编辑：

```bash
~/.local/bin/flow-image image '保留狐狸、姿态和水彩风格，把蓝色帐篷改为红色，天空增加满月' \
  --ref '/绝对路径/原图.jpg' --aspect 1:1 --output '/绝对路径/修改后.jpg'
```

多张参考图合成（按需要重复 `--ref`）：

```bash
~/.local/bin/flow-image image '把狐狸图里的同一只狐狸放进木屋图的溪边，保留木屋和森林构图，不要帐篷' \
  --ref '/绝对路径/狐狸.jpg' --ref '/绝对路径/木屋.jpg' \
  --aspect 3:4 --output '/绝对路径/合成.jpg'
```

- 每个 `--ref` 接受一张本地 JPEG、PNG 或 WebP，可重复传入。脚本先验证全部文件，再逐张复用已有素材或仅首次上传到同一提示框；**只有参考图数量完全一致且每张已加载，才提交一次生成**。任何参考图失败都停止，不能静默降为单图或文生图。实际可用上限由 Flow 当前界面决定，本版本不宣称已验证任意数量。
- 提示词说明每张图的作用（如狐狸主体／木屋场景）及需要保留和修改的内容，避免只靠“图1／图2”造成歧义。当前未封装遮罩或视频。
- `--aspect`：`1:1`（默认）、`16:9`、`9:16`、`4:3`、`3:4`。每次生成一张；输出路径必须是绝对路径，已有文件不覆盖。实际文件后缀按下载内容确定，以成功 JSON 中的 `output` 为准。
- 输出 JSON 包含 `ok`、`mode`、图片路径、媒体 ID、参考图数量 `reference_count`、尺寸和耗时。查看保存图片，核对参考主体及修改要求后再报告成功；接口成功不等于画面满足要求。
- 文件锁只保护设置参数、上传参考和确认提交；提交后释放，同一项目中的图片可以重叠生成。不要在其他工具中同时编辑提示框。保持主 Chrome 和 daemon 常驻，不逐张开关或重启。

## 参考图复用

同一项目、相同文件内容（SHA-256）只需上传一次；改文件名、换目录或多个 Agent 连续调用仍复用同一个素材 ID。每笔任务仍会把全部指定参考图重新加入提示框，**复用素材不等于省略参考图**。返回的 `reference_reused_count` 表示本笔复用了几张。

对应关系在包外 `~/.local/share/flow-devtools/reference-cache.json`，按项目隔离，不能把它提交到 Git。升级前已上传的素材优先从本机任务记录和原浏览器请求核对参考图 ID 后接管，不按文件名或相似外观猜测。缓存命中但素材找不到、已知历史引用无法核验、或上次上传状态不确定时，停下来核对；不能静默再上传一个副本。修改图片字节内容会视为新图。上传尝试之前就保存状态，中断后先查找素材再恢复，不盲目重复上传。

当前 Flow 的 `/asb/…` 缩略图不直接包含素材 ID。脚本优先读取明确的 `data-media-id`；素材列表与提示框中的缩略图通过同一图片资源和项目网格 ID 对应，无法唯一核验仍停止，不按文件名猜测。直接加入提示框但缩略图尚未加载时会继续等待，不误点已关闭的“添加到提示”。

选择与点击均按同一个素材 ID 执行，同名条目不取第一项。缓存只有名称、没有 ID 且存在多个同名结果时，停止核对，不重新上传。已知 ID 的旧 `/asb/` 素材不在当前网格时，临时搜索项目库，让带明确 ID 的图块出现并核对同一图片资源，完成后恢复原搜索状态。已核验的资源映射仅留在当前页面内存中，支持网格虚拟滚动；不把图片地址写入磁盘缓存。页面被切换时停止并保留当前页面。

收图兼容 `/asb/…`：通过现有 Chrome 登录会话读取原尺寸图片，不导出 Cookie；仍按图片实际格式落盘并禁止覆盖。缩略图下载不作为原尺寸成品。

## 连续提交与并发收图

多个 Agent 可直接各自调用 `image`，每个命令等待自己的结果，期间不占用提示框锁。同一个 Agent 要先连续提交多笔，再收图，可使用：

```bash
~/.local/bin/flow-image image '一只黄色橡皮鸭，蓝碗，白背景' --output '/绝对路径/鸭子.jpg' --no-wait
~/.local/bin/flow-image image '紫葡萄，黄盘子，浅紫背景' --output '/绝对路径/葡萄.jpg' --no-wait
~/.local/bin/flow-image wait '<第一笔返回的job_id>'
~/.local/bin/flow-image wait '<第二笔返回的job_id>'
```

`--no-wait` 返回“已确认提交”的 `job_id`，不代表图片完成。`wait` 收取已提交任务，**不会再次提交**；已收取的任务再次 `wait` 返回原结果。每笔使用不同的输出路径，正在生成的任务也会预留输出路径。

优先按该次浏览器请求识别结果；Flow 若中止生成连接而页面继续出图，则短暂加锁打开图片详情，核对完整提示词及已认领媒体 ID 后恢复。不能取页面最新图片代替。相同提示词并发且响应体不可读、或详情匹配不唯一时，保留任务并停止猜测，需人工核对。

## 状态与恢复

必要时运行 `~/.local/bin/flow-image status`，无需每张图先检查或重新连接。账号、项目、模型或已有未完成提示词不符合时，脚本会停止，先处理明确报错。

新任务独立记录在 `~/.local/share/flow-devtools/jobs/<job_id>.json`，`status` 列出未完成任务。超时使用 `wait <job_id>` 继续收取，不重发。已绑定浏览器请求的在途任务不阻止其他任务提交；`submitting`／`unconfirmed` 表示无法确认提交归属，先核对后再提交新任务。

旧版 `pending.json` 存在时先让旧任务完成或核对其结果，不能直接删除后重试。Chrome／daemon 重启会使原请求编号失效；脚本拒绝拿新连接的同号请求当旧结果。参考图会留在 Flow 项目中，临时本地上传副本及读取的网络正文自动清理，不保存 Cookie 或签名 URL。

需要未封装的 UI 操作时，用 `chrome-devtools --sessionId=f10 ...` 和最新 `take_snapshot`，页 ID 从 `list_pages` 确认，不硬编码 UID。不要回退到 gflow-cli、Flow2API、其他图片服务，或复制 Cookie。只有用户明确要求停止服务时才用 `flow-image stop`。

## 维护与配置

可执行源码在 [scripts/flow_image.py](scripts/flow_image.py)，离线检查为 `python3 scripts/test_flow_image.py`（DOM 回归用例另需 Node.js，仅用于测试）。本机安装副本为 `~/.agents/skills/image/flow-image/`，快捷命令指向该副本。开发目录按项目安装映射维护。

运行状态和私有配置位于 `~/.local/share/flow-devtools/`（可用 `FLOW_IMAGE_HOME` 覆盖），不放进 Skill 包或 Git。`config.json` 包含本机 `cli`、`session`、`project` 和预期 `account`；不包含密码或 Cookie。依赖 Python 3.10+ 标准库及已安装、用户已允许连接的 Chrome DevTools CLI 1.12.0。新连接可能需要用户在 Chrome 确认；缺少授权时停下，不反复弹窗。

能力与真实测试边界见 [SOURCE.md](SOURCE.md)。
