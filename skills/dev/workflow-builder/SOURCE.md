# 来源记录

- skill: `workflow-builder`
- kind: `local`
- status: `confirmed`
- source: 本仓库 `skills/dev/workflow-builder/`；经用户确认的 v0.2 设计记录 `docs/workflow-builder/plan.md`。
- version: `0.2.1`；2026-10-28 明确项目 workflows/ 整包存放与外部导入规则；随包 Runtime 为 0.1.0。
- author: 用户需求与架构确认，Codex 辅助编写本包说明、生成器、Schema、Runtime 和示例。
- license: unknown；本次未指定新包发布许可，不继承或改写第三方伙伴 Skill 的许可。
- collected_at: `2026-10-28`
- recorded_at: `2026-10-28`
- evidence: 本次对话对 Builder／Runtime 分离、独立入口及验收方案的确认和开发授权；后续明确要求补充通用的已有项目新增／整合能力，工作流统一置于项目根 workflows/，业务资料目录由 Agent 决定。源码旁保留设计及验证记录。

## 依赖与参考边界

本包自行实现总控流程、生成器和 JSON 子进程 Runtime，未复制第三方 Skill 源码。调用伙伴时按名称发现并验证真实安装入口：

- agent-orchestration：SkillMedev/skills，提交 `97a13607d669157a4a16d5ba79b77f208319f7b9`，MIT。
- workflow-orchestration：vxcozy/workflow-orchestration，v1.0.0，提交 `547a0a0de6395eebed16f2e86043faf3cfb0863e`，MIT。
- agent-workflow-designer：borghei/Claude-Skills，v1.2.0，提交 `2c12c7efaad13a70bdea6e205698a6c4f93a0682`，MIT + Commons Clause。

以上为构建过程的可选伙伴，按阶段加载，不复制到生成项目，也不声明为本地原创。伙伴原包继续独立维护原始来源和许可。

Runtime 显式依赖 PyYAML 和 jsonschema，未随包复制其库代码；依赖声明在 assets/project/runtime/requirements.txt，实际环境版本另记验证报告。生成项目包括独立 Runtime、Schema 和真实报告示例；模型 SDK、MCP、客户端或调度器由业务需求决定，本次未自动安装或连接。

源码开发与本机安装副本按项目 AGENTS.md 的提交／推送后同步流程管理。开发测试资源位于 docs/workflow-builder/，不进入 Skill 分发目录。
