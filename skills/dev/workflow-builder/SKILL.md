---
name: workflow-builder
description: >-
  Use this skill when the user wants to build, adapt, or migrate an executable
  workflow from a goal or template: discover suitable local Skills and tools,
  design step contracts and agents, configure integrations, generate an independent
  runtime project, and verify repeatable execution. Also use when a workflow plan
  needs real launch, retry, or recovery mechanisms. Do not take over ordinary
  execution of an existing workflow, a single code fix, or installation of a named Skill.
metadata:
  version: "0.1.0"
---

# Workflow Builder

把用户需求或模板落实为可以独立启动、验证、重试和恢复的工作流项目。Builder 负责构建；生成项目的 Runtime 负责日常执行。完成交付后，Runtime 不加载本 Skill、不重走设计流程、不借用构建会话历史。

## 先确定本次交付

读取目标项目规则与技能索引，确认最终产物、输入、验收标准、执行环境，以及用户要求只设计、搭建还是改造。只问会改变实现的缺失信息，已有授权不重复索取。

只设计时交付蓝图、依赖与缺口，状态为 designed。搭建时继续生成、配置和运行验证。明确当前客户端交互、独立脚本、无人值守或自动触发的需要，不默认增加框架、后台任务或多个 Agent。

在调用命令前设置 `SKILL_DIR` 为本 Skill 的真实目录。具体业务执行项目是 `PROJECT_DIR`，两者不能混淆。核心规范跨平台；随包 Runtime 首版支持 Python 3.10+、macOS/Linux。其他运行平台由相应适配器实现并单独验证。

## 1. 需求转成执行契约

保存简短需求与验收记录，拆出每步输入、执行者、输出、完成条件和失败处理。先确定数据依赖，再决定角色；固定变换优先用脚本，只有独立职责、上下文隔离或真实并行价值才拆 Agent。

为 Agent 指定目标、输入输出、使用技能、工具动作范围和预算。为交接指定结构化产物引用，避免传整个聊天历史。只在有用且允许委派时启动子代理；设计了多个业务 Agent 不等于 Builder 也要启动相同数量的代理。

开始定义节点时读取 [契约与数据规范](references/contract.md)。

## 2. 选择能力并组合已有技能

从项目索引、本机总入口及相关分类定位候选，结合当前会话实际可用的系统、插件技能与工具。只读取本次候选的说明和必要资源。

按用途解析下列伙伴名称的真实入口，在使用处核对版本和资源是否存在；不要求每次全部加载，也不把构建依赖写进业务 Runtime：

- `agent-workflow-designer`：选择顺序、并行、层级等模式，参考实现骨架；需要 DAG 校验或 Mermaid 时复用其工具并适配数据格式。
- `agent-orchestration`：决定 Agent 是否必要，明确职责、交接、并串行、失败策略与预算。
- `workflow-orchestration`：组织实施任务、验证与修正。用户和项目约定优先，不机械增加每步确认或无关复盘文件。

伙伴缺失时标明受影响功能；可继续的设计正常交付，不能虚报其工具已运行。业务工作流只锁定实际使用的领域 Skill、工具、模型适配器和运行依赖。

只有必要能力缺失才进行外部搜索；比较适配性、维护证据、依赖成本、许可和平台兼容性。涉及检索、安装或服务连接时读取 [能力发现与接入](references/capabilities.md)。

## 3. 设计与生成独立项目

选最小充分 Runtime：已有可靠执行器满足需求时复用；否则按需生成脚本、原生 Agent 或混合适配。不要因客户端支持 Skills 就推定有后台调度、持久状态或跨会话恢复。

随包项目模板有真实入口、Schema、规则加载、JSON 节点协议、日志、检查点和最终验证。生成器不覆盖现有目录，也不标记 ready：

```bash
python3 "$SKILL_DIR/scripts/create_workflow.py" --path "$PROJECT_DIR" --name example-workflow
```

默认生成一个真正可运行的“笔记→Markdown 报告”示例，供检查契约与入口；将 workflow.yaml、业务脚本、规则和验收改成用户目标，删改无用的示例文件。`--spec` 可复制已有定义，但不会自动复制其业务资源或证明它可用。不要把默认例子当作已完成用户需求。

生成项目仅执行被明确接受的工作流命令，规则和工具范围不构成操作系统沙箱。需要接模型、MCP、原生客户端或自动触发时读取 [运行适配与连接边界](references/adapters.md)，依据目标版本官方资料实现和验证，不能编造 CLI 参数。

## 4. 配置、执行与观察

用项目自己的解释器安装声明依赖；需要时使用项目虚拟环境。保留运行依赖的实际版本与来源，密钥留在目标环境的凭据存储或环境变量里。

```bash
python3 -m pip install -r "$PROJECT_DIR/runtime/requirements.txt"
python3 "$PROJECT_DIR/runtime/runner.py" check
python3 "$PROJECT_DIR/runtime/runner.py" run --input "$PROJECT_DIR/example-input.json"
python3 "$PROJECT_DIR/runtime/runner.py" status --run-id RUN_ID
python3 "$PROJECT_DIR/runtime/runner.py" retry --run-id RUN_ID --step STEP_ID
python3 "$PROJECT_DIR/runtime/runner.py" resume --run-id RUN_ID
python3 "$PROJECT_DIR/runtime/runner.py" validate --run-id RUN_ID
```

模板 CLI 的 `RUN_ID`、`STEP_ID` 是需要替换的真实 ID；自定义工作流使用自己的输入文件。工具探测仅证明所需检查通过；不把找到工具、写好配置或存在环境变量称为已连通。

`check` 返回实际能力；首版为顺序 DAG，无内置并行、分支、后台调度或原生模型客户端。需要这些能力时采用合适执行器并提供实际适配与验收；不要向首版 Schema 填不支持的字段冒充已实现。

每轮实施读取已有构建进度，只修正受影响节点。运行实例的状态写在项目 runs/，与 Builder 的设计进度分开。副作用结果未知时先核对实际系统；manual 节点不能自动重放。

## 5. 独立验收与交付

读取 [验收和就绪门槛](references/acceptance.md)，为当前业务生成可执行测试与样例，覆盖新进程正常执行、失败、自动或显式重试及耗尽、中断恢复、最终产物拒绝和重复运行。需要调度时另验触发链路。

由生成项目自己的入口在新的进程或 Agent 会话执行。不能借助 Builder 的临时文件、隐含模型连接或聊天历史；领域 Skill 与外部服务可以保留，但必须是已声明、可访问且经过验证的运行依赖。

交付 README 中的真实启动方式、配置方法、依赖、验收记录、run ID、产物和恢复方式。区分 designed／generated／configured／verified／ready；未通过必需场景就报告准确状态与缺口。样例成功不是对任意业务需求的质量保证。

生成包使用稳定版本的 workflow.yaml 作为唯一定义源。修改定义、代码、锁定依赖或验收标准后重新验证受影响场景，不复用旧 ready 结论。日常执行不进入 Builder；只有用户要改流程或发现定义缺陷时才回到构建模式。
