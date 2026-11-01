---
name: flow-image
description: "Generate and edit images with Nano Banana 2.1 in Google Flow through the local Chrome DevTools CLI persistent session. Use for Flow/Nano Banana image requests, including multiple local reference images; reuse the user's existing Chrome login."
metadata:
  version: "1.1.0"
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

- 每个 `--ref` 接受一张本地 JPEG、PNG 或 WebP，可重复传入。脚本先验证全部文件，再逐张上传到同一提示框；**只有参考图数量完全一致且每张已加载，才提交一次生成**。任何参考图失败都停止，不能静默降为单图或文生图。实际可用上限由 Flow 当前界面决定，本版本不宣称已验证任意数量。
- 提示词说明每张图的作用（如狐狸主体／木屋场景）及需要保留和修改的内容，避免只靠“图1／图2”造成歧义。当前未封装遮罩或视频。
- `--aspect`：`1:1`（默认）、`16:9`、`9:16`、`4:3`、`3:4`。每次生成一张；输出路径必须是绝对路径，已有文件不覆盖。实际文件后缀按下载内容确定，以成功 JSON 中的 `output` 为准。
- 输出 JSON 包含 `ok`、`mode`、图片路径、媒体 ID、参考图数量 `reference_count`、尺寸和耗时。查看保存图片，核对参考主体及修改要求后再报告成功；接口成功不等于画面满足要求。
- 同一提示框由文件锁串行使用，不在其他工具中同时编辑。保持主 Chrome 开着，调用之间保留 daemon；不逐张启动／关闭浏览器，也不重启常驻会话。

## 状态与恢复

必要时运行 `~/.local/bin/flow-image status`，无需每张图先检查或重新连接。账号、项目、模型或已有未完成提示词不符合时，脚本会停止，先处理明确报错。

`~/.local/share/flow-devtools/pending.json` 表示请求可能已经提交。超时先检查标记、当前项目和结果，恢复已有图片；**不能删除标记后盲目重试**。成功会自动移除标记；上传失败未提交不应宣称生成失败或重复生成。参考图会留在 Flow 的项目素材中，临时本地上传副本自动清理。

需要未封装的 UI 操作时，用 `chrome-devtools --sessionId=f10 ...` 和最新 `take_snapshot`，页 ID 从 `list_pages` 确认，不硬编码 UID。不要回退到 gflow-cli、Flow2API、其他图片服务，或复制 Cookie。只有用户明确要求停止服务时才用 `flow-image stop`。

## 维护与配置

可执行源码在 [scripts/flow_image.py](scripts/flow_image.py)，离线检查为 `python3 scripts/test_flow_image.py`。本机安装副本为 `~/.agents/skills/image/flow-image/`，快捷命令指向该副本。开发目录按项目安装映射维护。

运行状态和私有配置位于 `~/.local/share/flow-devtools/`（可用 `FLOW_IMAGE_HOME` 覆盖），不放进 Skill 包或 Git。`config.json` 包含本机 `cli`、`session`、`project` 和预期 `account`；不包含密码或 Cookie。依赖 Python 3.10+ 标准库及已安装、用户已允许连接的 Chrome DevTools CLI 1.12.0。新连接可能需要用户在 Chrome 确认；缺少授权时停下，不反复弹窗。

能力与真实测试边界见 [SOURCE.md](SOURCE.md)。
