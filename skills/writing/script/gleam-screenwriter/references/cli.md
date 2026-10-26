# 项目 CLI

需要 Node.js 18+。用 `node "<skill-root>/scripts/script-project.cjs" help` 取得准确命令；下方省略这段入口。项目路径使用用户指定的工作目录。CLI 仅做本地确定性操作，不请求模型或联网。

- `init --project DIR --name NAME [--mode original|adaptation] [--direction general-screenplay|bl-short-drama]`：仅初始化新的／空目录。
- `import --project NEW_DIR --file PROJECT_JSON`：读取 App 或本 Skill 的项目 JSON；继承草稿，审批重置为待复核。不能直接导入 SQLite 数据库。
- `list --root DIR [--sort updated|name|stage]`：列出该目录下的一级项目文件夹。
- `status --project DIR`：项目修订号、文档状态、各阶段 gate 与最近操作。
- `source --project DIR --file FILE [--label NAME]`：导入 TXT、Markdown、DOCX 或可提取文本的 PDF；扫描件需要宿主 OCR，不能假装已读。不会调用 App。
- `set --project DIR --field FIELD --file FILE`：文档字段用 UTF-8 文本；`meta` 用 JSON。支持 `name`、`creativeBrief`、`seriesBible`、`sourceAnalysis`、`englishLocaleBrief`、`meta`。修改项目级资料会撤销审批，保留稿件。
- `ready --project DIR --confirmation TEXT`：记录真实立项确认；检查剧名、思路书、圣经，改编另需原作分析。
- `message --project DIR --role user|assistant --file TEXT [--channel studio|planning|adaptation]`：保存实际对话；不要伪造作者话语。
- `prompt --project DIR --phase PHASE ...`：返回所选指令与项目上下文。阶段用 `--phase stage --stage N`；分集用 `--phase episode --episode N`；事件批次用 `--phase outline-batch [--batch N]`，批次索引从 0 开始。`planning`、`adaptation-analysis`、`adaptation-discussion`、`adaptation-plan`、`bible`、`locale`、`prefill` 没有额外编号。
- `ingest --project DIR --stage N --file DRAFT [--replace-stage]`：按 App 的解析规则保存阶段草稿；返回解析键和真实 gate。`--replace-stage` 仅用于明确整版替换该阶段。
- `check --project DIR [--stage N]`：检查阶段缺项与未注册资产；`ok:true` 代表命令执行成功，是否过关看各 gate 的 `ok`。
- `approve --project DIR --stage N --confirmation TEXT [--override-reason TEXT]`：按顺序记录主创授权；结构未过时默认拒绝，覆盖必须依据实际授权并写明理由。
- `rollback --project DIR --stage N --reason TEXT`：撤销该阶段起的审批，不删除后续草稿。
- `batches --project DIR`：事件批次、下一待补大纲批次与最早未完成集数。
- `stats --project DIR --file DRAFT`：文字与时长启发式统计；通用方向不套 BL 的两分钟／八幕阈值。
- `export --project DIR --out NEW_ZIP [--replace]`：可读文档与完整 `project.json`。已有输出默认拒绝覆盖。

写操作可带 `--expected-revision N`；不一致时退出，重新 `status` 后处理冲突。stdout 是 JSON 成功结果，stderr 是 JSON 错误，失败退出码非 0。没有返回成功时，不要报告操作已完成。

## 项目文件

`project.json` 是唯一状态真源；`documents/*.md`、`artifacts/stage-N/*.md` 是阅读镜像，不要直接编辑镜像后声称状态更新。Agent 先写独立草稿，再运行 `set` / `ingest`。每次成功修改保存 `.history/修订号.json`，原子替换状态文件，保留操作与确认记录。导出 ZIP 中的 `project.json` 可以重新导入新目录。

`.writer.lock` 表示一次写操作。若出现锁，先检查是否有进程仍在写；不要盲目删锁或重跑写入。崩溃恢复时先保留 `project.json` 和 `.history`，确认原写进程已停止，再处理遗留锁。不要自动删除用户的项目历史。

## meta 示例

```json
{"seriesTitle":"潮汐档案","episodeCount":"8","episodeDurationMinutes":12,"targetMarket":"中文流媒体","dialogueLanguage":"中文","extraNotes":"档案悬疑；不采用恋爱主线"}
```

长片也使用项目指定的单位数；不把它强行变成长剧。集数不明确时先保留待确认，不能用缺省数字假装覆盖验收通过。
