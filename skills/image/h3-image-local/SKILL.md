---
name: h3-image-local
description: 用已安装在 Apple Silicon Mac 上的 MiniMax H3 Image MLX 本地生成或按参考图编辑 PNG。用户指定本地 H3 Image、MiniMax H3 本机生图或 h3-image-local 时使用。
metadata:
  version: "1.0.0"
---

# 本地 H3 Image

直接调用本机安装的 `h3-image-mlx`，使用 **MiniMax H3 Image INT8 ConvRot 原版 6 步**。默认运行目录是 `$HOME/Desktop/AI/minimax h3 image`。目录位置已调整时，用 `H3_IMAGE_LOCAL_ROOT` 指向实际运行目录。目录中有 `.venv/bin/h3-image-mlx`、`models/` 和 `outputs/`。

## 生成与编辑

1. 按用户意图确定主体、画面布局、材质和光线。保留用户提供的原提示词、精确文案和指定参数。未给尺寸时，方图用 1024×1024，3:4 用 768×1024，竖版 9:16 用 576×1024。横版交换宽高。原生宽高各为 256–4096 范围内的 32 倍数。用户明确要交付其他像素尺寸时，按同一构图比例生成合适尺寸，再缩放或按用户指定的方式适配。
2. 用下方命令启动。默认输出到运行目录的 `outputs/`，每张图使用独立的 PNG 文件名。用户指定保存目录时按其要求交付。要复现某次测试时复用提示词、尺寸、种子和推理参数。需要多张变体时逐张使用不同种子。
3. 编辑时按参考图的实际顺序重复传入 `--reference "/绝对路径/参考图.png"`，在提示词用 `<Picture 1>`、`<Picture 2>` 指明各图用途，并交代要改什么、保留什么。CLI 支持 PNG、JPEG、WebP，最多 16 张有序参考图。

```bash
h3_root="${H3_IMAGE_LOCAL_ROOT:-$HOME/Desktop/AI/minimax h3 image}"
h3_output="$h3_root/outputs/h3-$(date +%Y%m%d-%H%M%S)-$$.png"
h3_prompt='A photorealistic studio photograph of a matte blue ceramic cup on a light gray surface, lit by a large soft window.'

env -u H3_LORA -u H3_STEPS -u H3_SIGMAS -u H3_SHIFT \
  -u H3_DIT -u H3_TEXT -u H3_TOKENIZER -u H3_VAE \
  H3_ASYNC=1 H3_PREFETCH=1 \
  "$h3_root/.venv/bin/h3-image-mlx" generate \
  --models "$h3_root/models" --model h3 --precision int8 \
  --dit-mode stream --width 1024 --height 1024 --seed 42 \
  --prompt "$h3_prompt" --output "$h3_output"
```

原版采样表随权重加载。上面的命令显式清除临时模型与采样覆盖。流式模式可以降低常驻内存，`--backend` 默认自动选择，在本机 M5 上使用 W8A8。等待进程完成后检查产物。原版 H3 的生成进度以进程状态为准，CLI 的 `--progress` 适用于 Qwen 请求。

## 验收

- 打开输出 PNG，核对尺寸、构图、参考图要求和关键细节。写实图按原像素重点查看皮肤、手、衣料和平坦背景上的块状噪点、规律网纹及局部扭曲。
- 若整体效果合适但需要更多细节，可尝试更大的原生画布，例如 3:4 的 1824×2432。按实图选择保留哪版。块状纹理是否改善以实际对照为准。
- 如果文件尚未产生，先检查进程和错误信息。缺少已有依赖或权重时，报告具体缺项，按用户授权处理安装或下载。完成后用绝对路径交付 PNG，并在有助于复现时附上尺寸、种子和步数。
