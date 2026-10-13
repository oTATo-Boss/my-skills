# 来源与维护范围

2026-10-12 从本机正在使用的安装版本迁入 14 个 Skill，保持技能文件内容与执行权限不变。开发目录与本机安装目录均保存实体源码；文件同步遵循 `AGENTS.md`，安装位置见 `INSTALL_MAP.json`。

## 原创工作流

`ai-liveaction-fusion`、`ai-video-prompt`、`json-prompt-system`、`fashion-picture` 有本地开发记录；`nsfw-seedance-prompt-skill` 由用户明确确认原创。`fashion-picture` 是原 `otato-fashion-design` 的当前安装版本。

## 二创与整合版本

- `codex-imagegen`：用户确认的二创版本，目标是让其他 Agent 通过 Codex CLI 调用生图能力。确切上游作者或仓库尚无完整记录，保留现有内容，不把上游部分声明为原创。
- `direct-video`：本地编写的视频创作与验收工作流；参考来源保留在技能内的 `references/sources.md`。
- 六个网页技能：从用户收集的设计技能合集重组、编写，保留原模块的参考资料与示例目录。入口及本地组织不代表所有参考内容均为原创；参考中的来源、版权和许可说明应继续保留。

第三方代码、文档、示例和素材按其自身许可处理。本文件记录来源范围，不替第三方资源授予新许可，也不设置统一覆盖全仓库的开源许可证。

## 技能库管理工作流

2026-10-13 从 `~/.agents/skills/meta/skill-library-management/` 引入本地编写的 `skill-library-management` 完整开发目录，保留入口、脚本、引用资料与 Agent 配置，排除 Python 缓存。本仓库现维护 15 个 Skill；本机安装副本与 Claude 入口沿用原位置。

首次纳入仓库的版本为 v1.0.0，维护记录见 [CHANGELOG.md](skills/skill-library-management/CHANGELOG.md)。

2026-10-13 按用户要求卸载通用 `social-media`：删除开发源码、GitHub 当前分支内容、本机安装副本与 Claude 入口，并移除对应索引、安装映射和安装说明。本仓库当前维护 14 个 Skill；保留 `personal/otato-social-media`。

2026-10-13 按用户要求从 `Social Media.zip` 导入 6 个 Skill 到 `skills/social-media/`，完整保留原包 19 个文件与共享配置，新增分类索引、来源与导入记录；原包未声明作者、版本和许可证，不标为原创。本机安装映射统一为 `social-media/<skill-name>/`，本仓库当前维护 20 个 Skill。
