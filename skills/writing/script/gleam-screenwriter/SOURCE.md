# 来源与版本

- skill: `gleam-screenwriter`
- version: `0.1.0`
- kind: `adapted`
- status: `confirmed`
- source: 本地应用 `/Users/griffith/Desktop/AI剧本`；开发快照及逐项哈希见 `.dev/source-manifest.json`。
- author: 本地工作流由用户授权 Agent 整合；继承部分原作者 unknown，当前材料未提供署名。
- license: unknown；原应用未提供可确认的独立分发许可，第三方依赖许可保留在包内。
- collected_at: `2026-10-26`
- evidence: `.dev/source-manifest.json`、`.dev/source/` 与 `docs/gleam-screenwriter/validation.md`。
- recorded_at: `2026-10-26`
- 本次来源：用户明确要求将本机「AI剧本 / Gleam Screenwriter」完整工作流封装成 Agent Skill。来源应用的 `agent/script-agent/`、阶段解析／验收／分集／导出 TypeScript 代码已保存到开发快照并按实际调用复用。
- 原应用更早的作者与单独分发许可：当前材料没有提供可确认的 LICENSE；不将继承的提示词／知识库标为新原创，也不擅自赋予 MIT 等许可。
- 新增部分：Skill 路由、文件项目 CLI、操作说明、持久化与审批记录、可移植构建和验证，由用户本次任务中 Agent 辅助整合。
- 第三方代码：JSZip、Mammoth 及其打包依赖的发布许可保留在 `references/licenses/`；PDF 解析器及 PDF.js 资源保留在 `scripts/vendor/pdf-parse/`，附各自许可或发布许可声明。PDF.js 的 node-ensure 依赖改为包内相对文件；App 静态提示词的“侧栏／工程侧”用语改为项目记录与文档，不改变用户素材正文。
- 分发内容不含用户项目、API Key、模型、桌面运行环境、数据库或 Next.js 服务。CLI 不执行模型调用。
- 格式依据：[Agent Skills 规范](https://agentskills.io/specification)、[脚本使用规范](https://agentskills.io/skill-creation/using-scripts)。
- 维护者源码、设计与行为验证在开发目录中维护，分发包排除 `.dev/`；初始交付时未提交／推送或同步；后续状态以 Git 记录与安装核对结果为准。
