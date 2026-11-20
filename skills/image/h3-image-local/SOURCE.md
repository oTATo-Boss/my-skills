# 来源记录

- skill: `h3-image-local`
- kind: `local`
- status: `confirmed`
- source: 用户在 2026-11-21 指定为已部署的本地 MiniMax H3 Image 创建调用 Skill，本项目编写并维护。
- version: `1.0.0`。参考本机 `h3-image-mlx 0.1.0a10`、MLX `0.32.4` 及 MiniMax H3 Image INT8 权重。
- author: 用户定义运行方式与质量要求，由 Codex 辅助编写工作流。
- license: unknown。用户未为本包指定独立对外许可。运行器、计算内核及模型按各自许可提供。
- collected_at: `2026-11-21`，本地新建。
- recorded_at: `2026-11-21`
- evidence: 本机 CLI 参数、权重清单、原版六步测试及同条件 pDMD 对照。

## 运行依赖

- [h3-image-mlx 0.1.0a10](https://pypi.org/project/h3-image-mlx/0.1.0a10/) 提供 MLX 命令行。本机安装包声明 Apache-2.0 AND MIT。
- [Comfy-Org MiniMax H3 Image](https://huggingface.co/Comfy-Org/MiniMax-H3-Image) 提供 INT8 ConvRot 主模型、文本编码器和 FP16 VAE。[MiniMax 模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3-Image) 记录模型源和社区许可。
- 本包包含原创调用说明和客户端展示元数据。运行器、权重和生成图片随本机运行目录管理。

## 本机验证

2026-11-21 直接执行入口文档中的命令，完成 1024×1024 文生图和单参考图编辑，两轮均为 6 步并通过 RGB PNG 解码。编辑样张将蓝色陶瓷杯改为深红色，保留主体、台面与构图。
