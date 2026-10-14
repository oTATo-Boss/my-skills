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

首次纳入仓库的版本为 v1.0.0，维护记录见 [CHANGELOG.md](skills/Rules/skill-library-management/CHANGELOG.md)。

2026-10-13 按用户要求将本机分类目录 `meta/` 更名为 `Rules/`；当前安装位置为 `~/.agents/skills/Rules/skill-library-management/`。同步总索引、分类索引、安装映射与 Claude 发现软链接；Skill 版本仍为 v1.0.0，技能文件内容与执行权限保持不变。

2026-10-13 按用户要求卸载通用 `social-media`：删除开发源码、GitHub 当前分支内容、本机安装副本与 Claude 入口，并移除对应索引、安装映射和安装说明。本仓库当前维护 14 个 Skill；保留 `personal/otato-social-media`。

2026-10-13 按用户要求从 `Social Media.zip` 导入 6 个 Skill 到 `skills/social-media/`，完整保留原包 19 个文件与共享配置，新增分类索引、来源与导入记录；原包未声明作者、版本和许可证，不标为原创。本机安装映射统一为 `social-media/<skill-name>/`，本仓库当前维护 20 个 Skill。

2026-10-13 按用户确认方案为本机 `video/`、`blender/`、`threejs/`、`web design/` 增加 27 个二级分类，整包迁移 183 个目录（包含 189 个 Skill），同步分级索引、跨技能路径引用、Claude 发现软链接和项目安装映射；`cloudflare/` 及其余分类保持原目录结构。本机仍为 223 个 Skill，项目仍维护 20 个；迁移只调整路径及管理记录，不改变工作流版本。

2026-10-13 按用户要求将项目开发目录重排为与本机安装分类一致的路径：`video/ai/`、`video/creative/`、`image/`、`web design/design/`、`web design/effects/`、`Rules/`；`social-media/` 套件保持现状。整包移动 14 个 Skill，保留文件内容、执行权限与版本，更新项目分级索引、README、来源记录链接和项目目录约定；项目仍维护 20 个 Skill。

2026-10-13 将 `Rules/skill-library-management` 升级至 v1.1.0，按已确认的一级分类／可选二级分类更新管理模型、索引模板、整包迁移与副本同步指南，扩展只读审计至任意深度分类、导航数量、开发安装映射和内容权限比较，并加入行为回归用例；不把当前整库分类清单复制进 Skill。

2026-10-13 按用户要求将 oTATo 项目的 RunningHub MiniMax H3 工具整合为 `RH-minimax-H3` v1.0.0（标识 `rh-minimax-h3`），新增凭据存入、任务构造和离线恢复验证；详细来源、未知作者与许可边界见 [sources.md](skills/video/ai/rh-minimax-h3/references/sources.md)。本仓库当前维护 21 个 Skill。先按可用本机技能请求进行本地安装同步，再按用户后续授权提交与推送；密钥存本机私有配置，不在源码与安装包内。

2026-10-14 按用户要求卸载本机安装的 `personal/otato-social-media`（它不在本仓库维护，上面"保留"的说法到此为止）：安装副本、Claude 入口和空的 `personal/` 分类移入废纸篓；项目用到的打包脚本和品牌规则已并入 @土豆老板oTATo 项目。同日更新 `rh-minimax-h3/references/sources.md` 的原客户端位置说明。


2026-10-14 为本仓库 21 个 Skill 补充独立 `SOURCE.md`，并为本机共享库全部 223 个独立技能（含嵌套技能）建档，区分原始来源、维护仓库、参考资源和未知信息；管理技能升级 v1.2.0，新增来源记录指南与只读 `--check-sources` 检查。此资料补录不改变其他技能工作流版本；源码、安装同步和来源待确认状态分别核对。

2026-10-14 用户确认 `social-media/` 六个 Skill 由本人编写（此前按导入包记为作者、许可未知）；按用户决定在 `skills/social-media/LICENSE` 以 MIT 许可发布，同步更新套件 `SOURCES.md` 和六个 `SOURCE.md`。本机安装副本待来源记录同步时一并更新。

2026-10-14 修正来源补录的确认口径：本仓库 21 个 Skill 的用户自研／二创整合归属均已确认（13 个本地编写、8 个二创整合）。此前 8 个二创标记 partial，是把上游作者、原始仓库或许可缺口混入了当前版本归属判断；现改为 confirmed，并在作者字段与说明中单独保留第三方资料缺口。管理技能升级 v1.2.1。

2026-10-14 按用户决定，`rh-minimax-h3`、`direct-video`、`codex-imagegen`、`skill-library-management` 各自新增 MIT `LICENSE` 并更新 `SOURCE.md`。两个二创技能注明许可只覆盖用户编写和修改的部分，上游与 RunningHub 服务条款不在范围内。
