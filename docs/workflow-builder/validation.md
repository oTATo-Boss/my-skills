# Workflow Builder 0.1.0 验证记录

日期：2026-10-28。范围：本次新增 Skill、独立项目生成器、POSIX JSON 子进程 Runtime 与项目索引。本报告记录源码验证阶段的证据；用户随后已授权提交、推送及本机安装，发布后同步结果另行记录。

## 实现与范围

- Builder 为总控 Skill，按阶段复用三个已安装伙伴；新增代码未复制第三方 Skill。
- 生成项目包含 workflow.yaml、Schema、规则、依赖声明、资源记录、真实入口及笔记报告示例。
- Runtime 提供 check、run、status、retry、resume、validate，执行脚本或用户提供的 JSON 子进程 Agent 适配器。
- 规则、角色文件和声明的 Skill 文本显式传入执行器；类型与产物检查后才提交节点成功。
- 运行状态、尝试、错误、进程 PID、检查点和文件散列在项目内持久保存。
- 第一个已验证目标为 macOS 上的脚本 Runtime；实现要求 Python 3.10+ 和 POSIX。Linux 尚未在本次机器上实测。

环境：Python 3.12；PyYAML 6.0.2；jsonschema 4.26.0。未为本次测试安装依赖或连接外部服务。模型、MCP、原生客户端、Windows、并行／分支和后台调度不在已验证范围。

## 自动黑盒验收

执行：

```bash
python3 -m unittest discover -s docs/workflow-builder/tests -v
```

结果：20 项通过，最后一次耗时约 5.9 秒。每个用例在临时目录生成项目并由新 Python 进程调用实际入口，生成项目不导入 Builder 源码或依赖聊天历史。

覆盖正常／重复运行、非法定义和输入、自动与显式重试、重试耗尽、检查点跨进程恢复、真实 SIGTERM、并发锁、SIGKILL 后仍存活子执行器的重放阻断、未知副作用阻断、超时、非法 JSON、空产物、最终业务拒绝、源代码与产物变更、缺失连接配置及恢复、Agent 协议中角色／Skill／规则传递、生成器不覆盖、缺失执行入口、外部及不存在的本地 Schema 引用、验证器修改产物、非 JSON 兼容 YAML 值，以及新增无关输入文件不破坏恢复。

测试执行器和 probe 是受控本地程序，不能证明真实模型或 MCP 已连通。

## 独立前向评估

评估按 skill-creator 的 Independent Forward-Testing 方法进行；评估者在隔离目录完成真实请求，未读取本仓库回归测试，也未修改仓库或安装目录。

| 场景 | 实际动作与结果 |
| --- | --- |
| 本地笔记报告 | 生成独立项目与中文报告；自写 7 项黑盒场景通过，覆盖正常、失败、重试／耗尽、跨进程恢复、真实 SIGTERM 和最终产物拒绝 |
| 缺认证的每日外部读取 | 保存设计和能力状态，标为 designed；认证受阻、调度 planned；没有发外部请求或假称已就绪 |
| 循环依赖与共享写入模板 | 原始循环被真实 check 拒绝；改成 prepare→render、唯一写入者和只读语义验收；7 项自写黑盒场景通过 |

评估发现恢复指纹把新增的下一次输入文件也作为源码依赖，导致有效恢复被拒绝。已将指纹收窄到定义、规范源码目录、规则、执行／验证入口及声明依赖；本次输入单独校验摘要。新增回归通过，独立评估重新生成项目后也复验通过，上游只执行一次。

临时交付物保留于 `/tmp/workflow-forward.XFA0tC/`，包括 notes-report、input-fingerprint-fixed、daily-external-design 和 repaired-report。修复模板最后一次已验运行 ID 为 `r9162742cbff74b188ed9`，真实产物为 repaired-report/outputs/r9162742cbff74b188ed9/report.md。临时目录可被系统清理，源码内黑盒测试可重复生成验收环境。

## 无 Skill 对照与触发评估

另一评估者从空上下文仅使用通用能力完成同一本地笔记请求，没有读取目标 Skill 或实现。其基线项目使用标准库，8 项实际检查通过；保留于 `/tmp/notes-workflow-baseline-9krzew6c/`。

简单笔记任务的基线同样可用，不能据此宣称加载 Skill 会提高所有任务的质量。可观察差异是：基线为专用笔记执行器，本 Skill 提供可复用的版本化节点契约、通用 JSON 进程接口、资源／角色绑定、统一生成器与验收要求，减少每次重新设计这些机制。未测量 Token 或美元节省，未进行统计显著性判断。

完整无 Skill 对照也完成另外两项：缺认证场景交付 designed-only 方案和能力状态，4 项一致性检查通过；错误模板场景改成 research→write→review→publish 专用执行器，8 项实际检查通过，包括审核拒绝、禁止绕过审核、SIGKILL 恢复与成品散列保护。两侧都没有连接外部服务，均可满足这些本地案例。结果未显示单次成品质量优势；本包的已观察增量是统一可复用的生成、契约、资源绑定和 Runtime，而非模型能力替代。

触发分类只给出 description 和 20 条未标注请求，评估者未读取 Skill 正文或预期标签。开发集 12/12、保留验证集 8/8，与预先保存的 eval-cases.json 一致。此为描述分类评估，不是客户端真实自动选 Skill 的端到端证明。

## 结构、索引与来源

- skill-creator quick_validate：通过。
- 项目结构审计：33 个 Skill、33 个可达入口、15 个索引，通过。
- 项目总索引、dev 分类索引、INSTALL_MAP.json 和 README 已增量登记。
- 全仓 check-sources 仍有三个原有 Anime.js SOURCE.md 缺少 evidence 字段；已核对与 HEAD 内容一致，本次未修改它们。新增 workflow-builder 的来源记录没有该错误。
- 包内引用、脚本语法、JSON 和 YAML 元数据另作针对性检查。

## 关键源码摘要

以下绑定本次最终 20 项自动验收的源码；后续修改应重新验证受影响部分：

| 文件 | SHA-256 |
| --- | --- |
| assets/project/runtime/runner.py | `73fc09ce224d18977459fb3999d36eb982a1c3ee3ff0cad340908399aec1742e` |
| assets/project/runtime/workflow.schema.json | `fa15f0d28da2536b02e0e5c00c85971b5fb3a9694c7ce0ffcc8cfd5a35cd1312` |
| scripts/create_workflow.py | `f9a60422fc384c940df1a3dfb4567874c99a4e2e104f1448ab8b0da4bbfdbf7b` |
| SKILL.md | `4fc96eb97ffc4b050f82c01ef54e4d5ef0e7929ed06957d93a18f7679d73e3cf` |

## 安装与运行声明

源码验证结束时，本机安装目录和 Claude 入口尚不存在，没有提前复制。用户随后已明确授权提交、推送和安装。按项目 AGENTS.md 先推送，再检查源／安装冲突并同步实体副本、更新本机索引和客户端入口。提交与安装是独立阶段，其最终结果见 Git 历史、本机来源记录和任务回执，不以本报告中的源码测试代替安装验证。

当前结论是源码与上述本地 Runtime 能力已验证；不表示任意未来生成的业务工作流自动 ready，也不表示真实账户、模型、MCP 或调度已经验证。
