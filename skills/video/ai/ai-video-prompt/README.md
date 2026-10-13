# AI Video Prompt 1.0.0

一个用于AI视频提示词创作、修改、审查与反馈改写的独立Skill。通过简洁的导演角色定义发挥LLM的创意、美术与设计能力，用通用模板统一新稿格式。

提供目标、明确要求和参考素材即可；未锁定的设计空间由LLM自主发挥。新建完整提示词在一个代码块中包含视频梗概、参考素材和按时间推进的内容，按需在末尾补充全片要求。局部修改、讨论、审查和用户指定的格式按实际请求处理。

运行内容只有 `SKILL.md`、`templates/video_prompt_template.md` 和调用元数据 `agents/openai.yaml`。没有风格案例库、统一导演方法、专项模式或提示词质量评分脚本；职责聚焦文本创作，不承担生成上传、项目审批或生产状态管理。

目录名称为 `AI-video-prompt`，机器标识为 `ai-video-prompt`，发布包为 `AI-video-prompt.skill`。在Codex中可以用 `$ai-video-prompt` 调用。

本机用户级安装路径为 `~/.agents/skills/ai-video-prompt`，通过符号链接指向此源码目录，后续更新沿用同一份文件。

文本试用只能反映提示词设计；素材与生成模型也影响最终视频质量。Not-tested: live video generation。
