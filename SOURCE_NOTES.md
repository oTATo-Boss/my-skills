# 来源与维护范围

2026-10-12 从本机正在使用的安装版本迁入 14 个 Skill，保持技能文件内容与执行权限不变。开发目录与本机安装目录均保存实体源码；文件同步遵循 `AGENTS.md`，安装位置见 `INSTALL_MAP.json`。

## 原创工作流

`ai-liveaction-fusion`、`single-shot-prompt`（曾用名 `ai-video-prompt`、`short-video-prompt`）、`json-prompt-system`、`character-outfit-design` 有本地开发记录；`nsfw-seedance-prompt-skill` 由用户明确确认原创。`character-outfit-design`（角色的服装设计）曾用名为 `fashion-picture`、`otato-fashion-design`。

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

2026-10-16 为 AI-SMA v2 新增四个独立方法 Skill：video-project-orchestration、screenwriting、production-continuity、video-production-pipeline，以 MIT 发布；本仓库现维护 25 个。目录、合同与执行权限由调用项目提供，不绑定账号或社媒竖屏模板。同步开发索引与安装映射；提交发布前不覆盖本机安装副本。

2026-10-16 将 codex-imagegen 升级至 v2.0.0，当前入口文档与执行程序重新编写为 Python 标准库实现，保留 shell 兼容入口；加入只读能力探测、工作区输出约束、独占创建和本次任务显式结果恢复。历史未知来源内容未继续复制进 v2 包；新的文档和代码由本项目以 MIT 维护。

2026-10-19 按用户明确要求，将 `R2V-Skill.zip` 的 `r2v/` 完整纳入 `skills/video/ai/r2v/`，用于跨模型的视频参考素材判断与制作交接。本次保留原包 11 个文件的内容与权限，新增来源及导入记录，同步项目索引、安装映射和 README；项目现维护 29 个 Skill。原包未声明独立版本、作者署名或许可证，按用户提供套件记录，不推断为用户原创，也不授予新许可。原包哈希和验证边界见 [SOURCE.md](skills/video/ai/r2v/SOURCE.md)；提交推送后再同步本机独立安装副本与 Claude 发现入口。

2026-10-19 按用户明确要求，将 `motion-video-source.zip` 的 `motion-video/` 完整纳入 `skills/video/creative/motion-video/`，用于面向导演的代码视频与媒体处理能力参考。原包 10 份文档保持内容不变，归档未指定文件权限，安装时统一采用普通文档权限 0644；新增来源及导入记录，同步项目索引、安装映射和 README，项目现维护 30 个 Skill。原包未声明独立版本、作者署名或许可证，保留其参考来源，不推断原创归属或授予新许可；归档哈希与注释标识见 [SOURCE.md](skills/video/creative/motion-video/SOURCE.md)。按项目约定先提交推送，再同步本机独立副本与 Claude 入口。

2026-10-19 按用户要求将 `rh-minimax-h3` 升级为 v1.1.0：从用户粘贴的 RunningHub API 示例接入长视频应用 `2103012816681041921`，新增独立节点映射、显式模式选择与逐任务提交路由，保留原短视频默认行为。示例参数、未说明字段与待线上验证项单独记录，不带入示例提示词、上传素材或启用的 LoRA 权重；来源与版本见 [sources.md](skills/video/ai/rh-minimax-h3/references/sources.md) 和 [CHANGELOG.md](skills/video/ai/rh-minimax-h3/CHANGELOG.md)。技能数量仍为 30，安装位置不变。

2026-10-19 按用户要求将 `rh-minimax-h3` 升级为 v1.1.1，两种模式默认使用 Plus；旧 jobs 缺少实例字段时由客户端补 `plus`，显式实例选择保留。同步版本、来源、使用说明与现有离线回归；原长视频 API 示例的 `default` 作为历史来源保留。

2026-10-21 根据用户长期使用反馈，将 `ai-video-prompt` 更名为 `short-video-prompt` v1.1.0，适用范围明确为不切镜的单镜头短视频。保留三节输出结构与创作、修改、审查流程，调整单镜头连续性要求；更新名称、调用元数据、分级索引、安装映射、管理示例与来源记录。技能数量仍为 30；本机安装目录为 `~/.agents/skills/video/ai/short-video-prompt/`，按项目同步顺序更新独立副本和 Claude 发现入口。

2026-10-21 按用户最终命名，将 `short-video-prompt` 更名为 `single-shot-prompt` v1.1.1；保留不切镜的单镜头短视频适用范围与工作流，同步当前名称、目录、调用入口、相关索引、安装映射和管理示例。技能数量不变，当前本机安装路径为 `~/.agents/skills/video/ai/single-shot-prompt/`。

2026-10-21 按用户要求，将本人开发的 `multi-shot-prompt.skill` 导入 `skills/video/ai/multi-shot-prompt/`。原包 46 个文件内容与 0644 权限保持不变，保留原有恢复范围说明，新增 SOURCE.md 与导入记录；用户原创归属已明确确认，原包未声明独立发布版本或许可证，不自行补授许可。原包只读校验通过 38 个资源引用、10 个正向用例和 32 个错误变体；未进行视频生成。同步项目索引、安装映射和安装说明，项目现维护 31 个 Skill；按已确认的顺序提交推送后，再同步本机独立副本与 Claude 发现入口。

## 2026-10-26 — gleam-screenwriter

从用户指定的本地「AI剧本」应用封装为可独立使用的 Agent Skill，开发路径 `skills/writing/script/gleam-screenwriter`，版本 0.1.0。继承的工程提示词与知识库保留本地改编来源，不擅自声明上游开放许可。CLI 复用阶段解析／验收引擎；当前只交付源码与分发 ZIP，未提交、推送或安装同步。

2026-10-27 按用户要求将 `rh-minimax-h3` 升级为 v2.0.0：生成仅使用应用 `2104753059472990209`，旧应用仅保留已有 taskId 的查询恢复。时长、画幅及参考素材由当前任务指定，默认 Plus、1 MP、自动提示词、视频直出与作者 LoRA；1080P 使用 2 MP + Ultra。修复自动提示词分支合并空图片导致的失败，默认 1 MP + Plus 和 2 MP + Ultra 均完成 5 秒真实生成和完整解码验证；详细结果、未验证项及来源见技能的 [api.md](skills/video/ai/rh-minimax-h3/references/api.md) 和 [来源记录](skills/video/ai/rh-minimax-h3/references/sources.md)。技能数量和安装位置不变。

## 2026-10-28 · 角色技能整合

`character-design`整合并替换`character-outfit-design`，保留其服装方法、模板与案例；旧名称仅作历史记录，不保留安装入口。新包增加用户确认的角色基础资产、三类画风、剧情状态裂变与拼接脚本，来源及许可边界见`skills/image/character-design/SOURCE.md`。

2026-10-29 按用户要求从 `visual-creative-director.zip` 完整导入视觉创意总监技能，登记于 `image/visual-creative-director`，并同步 M1rage Studio 内置创意指导分类。保留 8 个原包文件，来源、归档哈希及软件适配边界见技能 `SOURCE.md`；用户于同日明确确认作者为本人，归属记录为用户原创；原包版本和许可未声明。
