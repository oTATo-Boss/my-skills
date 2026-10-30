# 来源记录

- skill: `skill-library-management`
- kind: `local`
- status: `confirmed`
- source: 本地开发／维护目录 `skills/Rules/skill-library-management`；当前维护仓库 https://github.com/oTATo-Boss/my-skills
- version: 1.4.1（原生新会话验收与确定性选型接入）；历史版本见 CHANGELOG.md。
- author: oTATo-Boss（用户本人）；2026-10-30 在当前对话明确确认本人制作，Agent 辅助编写／整理。
- license: MIT（2026-10-14 本人决定，见 [LICENSE](<LICENSE>)）
- collected_at: unknown；没有可靠安装／导入日期。
- recorded_at: `2026-10-30`
- evidence: [SOURCE_NOTES.md](</Users/griffith/Desktop/AI/我的项目/my skills/SOURCE_NOTES.md>)；[INSTALL_MAP.json](</Users/griffith/Desktop/AI/我的项目/my skills/INSTALL_MAP.json>)；当前入口 SHA-256 `d6f41379d26ac10ba541c1343c69b1d2475e92724a1c5b40632fbf468adbd353`（v1.4.1 记录快照）；本人 2026-10-14 决定以 MIT 许可发布。

## 本地调整与边界

- 开发目录与本机安装目录保留独立实体副本，来源资料按项目约定同步。
- v1.3.0 新增 Agent 语义审计；v1.3.1 在临时目录完成七组隔离回放，增加可复核证据并修正调用冲突与回滚边界。确定性结构检查脚本的职责保持不变；隔离验收不代表真实安装库、客户端或外部服务全部运行通过。

## 2026-10-30 · 当前作者归属最终确认

用户明确确认本技能为本人制作；以本次直接确认取代此前“仅记录为本人／二创版本”的归属表述。Agent 辅助实现不改变本项目作者登记。工具、第三方依赖、参考资料、继承模板及素材的原作者与许可仍分别保留，不将技能归属扩展为这些外部资源的原创声明。

## v1.4.0 扩展依据

本次按用户指定的六项权重升级评分与选型流程；Codex 发现和调用机制参考官方文档并核对本机 CLI 0.163.0 的生成协议，公共 Star 数据通过 GitHub 官方 API／已有连接器或 gh 获取。具体入口与边界见 [质量规范](references/quality-scoring.md) 和 [调用与持续优化](references/routing-and-refresh.md)。这些资料是功能参考，不改变本 Skill 的本地作者归属；没有引入第三方源码或新 Python 依赖。

## v1.4.1 实测与修正

使用已有 CLI 登录在系统临时项目中实测新会话，沿用原生 Skill 发现与隐式调用；加强项目选型指令，加入只读候选标准输入与可复核验收工具，不引入新 Python 依赖。证据及客户端范围限制见 [原生调用验收](evals/native-invocation.md)。未整理真实安装库。
