---
name: workflow-builder
description: >-
  Use this skill when the user wants to build, adapt, or migrate an executable
  workflow from a goal or template, or add and integrate workflows within an
  existing project: discover suitable local Skills and tools,
  design step contracts and agents, configure integrations, generate an independent
  runtime project, and verify repeatable execution. Also use when a workflow plan
  needs real launch, retry, or recovery mechanisms. Do not take over ordinary
  execution of an existing workflow, a single code fix, or installation of a named Skill.
metadata:
  version: "0.3.0"
---

# Workflow Builder

把用户需求或模板落实为可以独立启动、验证、重试和恢复的工作流项目。Builder 负责构建；生成项目的 Runtime 负责日常执行。完成交付后，Runtime 不加载本 Skill、不重走设计流程、不借用构建会话历史。

## 先确定本次交付

读取目标项目规则与技能索引，确认最终产物、输入、验收标准、执行环境，以及用户要求只设计、搭建还是改造。只问会改变实现的缺失信息，已有授权不重复索取。

先区分新建独立工作流、在已有项目新增工作流、整合多个已有工作流。后两类先确认真正的项目根和既有调用方式，读取 [已有项目接入](references/project-integration.md)，把工作流接入项目后再验收，不仅交付一个孤立文件夹。

只设计时交付蓝图、依赖与缺口，状态为 designed。搭建时继续生成、配置和运行验证。明确当前客户端交互、独立脚本、无人值守或自动触发的需要，不默认增加框架、后台任务或多个 Agent。

在调用命令前设置 `SKILL_DIR` 为本 Skill 的真实目录。`PROJECT_ROOT` 为真正的业务项目根，`WORKFLOW_DIR` 为某一完整工作流目录。在已有业务项目中新增、开发或导入工作流时，统一使用 `PROJECT_ROOT/workflows/<workflow-id>/`，与项目 `skills/<skill-name>/` 整包存放的逻辑一致；独立工作流项目时两者可以相同。不要把已有项目根交给生成器覆盖，也不要在任务、素材或临时目录重复创建项目规则和索引。核心规范跨平台；随包 Runtime 支持 Python 3.10+、macOS/Linux。其他运行平台由相应适配器实现并单独验证。

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

伙伴缺失时标明受影响功能；可继续的设计正常交付，不能虚报其工具已运行。业务工作流只携带实际使用的领域 Skill：选型优先查本机，交付时把每个 Skill 的完整目录及必要的关联资源放进 `WORKFLOW_DIR/skills/<skill-name>/`，保留来源与许可。绑定使用工作流内相对路径，不依赖本机共享技能库、客户端发现路径或指向外部的软链接；节点必须实际使用包内副本。构建伙伴不因参与设计就自动打包。工具、模型适配器和其他运行依赖另行声明。

只有必要能力缺失才进行外部搜索；比较适配性、维护证据、依赖成本、许可和平台兼容性。涉及选型、Skill 整包内置、检索、安装或服务连接时读取 [能力发现与接入](references/capabilities.md)，落实包内绑定、依赖闭合和迁移验收。

## 3. 设计、生成与项目接入

已有项目优先复用公共上下文、资料位置和规则入口；由构建 Agent 按业务决定是否增量补充配置、登记或路由。文件名、格式和业务目录不是固定模板。多个工作流按输入输出契约交接，各自保持独立状态；若需要统一调用，提供真实入口并验证它会找到和启动对应流程。

选最小充分 Runtime：已有可靠执行器满足需求时复用；否则按需生成脚本、原生 Agent 或混合适配。不要因客户端支持 Skills 就推定有后台调度、持久状态或跨会话恢复。

随包项目模板有真实入口、Schema、规则加载、JSON 节点协议、日志、检查点和最终验证。生成器不覆盖现有目录，也不标记 ready：

```bash
python3 "$SKILL_DIR/scripts/create_workflow.py" --path "$WORKFLOW_DIR" --name example-workflow
```

默认生成一个真正可运行的“笔记→Markdown 报告”示例，供检查契约与入口；将 workflow.yaml、业务脚本、规则和验收改成用户目标，删改无用的示例文件。`--spec` 可复制已有定义，但不会自动复制其业务资源或证明它可用。不要把默认例子当作已完成用户需求。

新增或开发时在项目根 `workflows/<workflow-id>/` 的未占用目录生成完整工作流；从外部添加已有工作流时，将完整定义、入口、代码与必要资源复制导入该位置，保留原始来源，修正路径与依赖，不以外部路径、软链接或包装调用替代导入。整合项目内已有流程时先保留基线，针对性修改，不重新生成覆盖，也不顺带批量迁移无关流程。公共规则和共享输入必须由实际入口或适配器显式加载，不能假定父级文档会自动传给脚本 Runtime。

生成项目仅执行被明确接受的工作流命令，规则和工具范围不构成操作系统沙箱。需要接模型、MCP、原生客户端或自动触发时读取 [运行适配与连接边界](references/adapters.md)，依据目标版本官方资料实现和验证，不能编造 CLI 参数。

## 4. 配置、执行与观察

用项目自己的解释器安装声明依赖；需要时使用项目虚拟环境。保留运行依赖的实际版本与来源，密钥留在目标环境的凭据存储或环境变量里。

```bash
python3 -m pip install -r "$WORKFLOW_DIR/runtime/requirements.txt"
python3 "$WORKFLOW_DIR/runtime/runner.py" check
python3 "$WORKFLOW_DIR/runtime/runner.py" run --input "$WORKFLOW_DIR/example-input.json"
python3 "$WORKFLOW_DIR/runtime/runner.py" status --run-id RUN_ID
python3 "$WORKFLOW_DIR/runtime/runner.py" retry --run-id RUN_ID --step STEP_ID
python3 "$WORKFLOW_DIR/runtime/runner.py" resume --run-id RUN_ID
python3 "$WORKFLOW_DIR/runtime/runner.py" validate --run-id RUN_ID
```

模板 CLI 的 `RUN_ID`、`STEP_ID` 是需要替换的真实 ID；自定义工作流使用自己的输入文件。工具探测仅证明所需检查通过；不把找到工具、写好配置或存在环境变量称为已连通。

`check` 返回实际能力；首版为顺序 DAG，无内置并行、分支、后台调度或原生模型客户端。需要这些能力时采用合适执行器并提供实际适配与验收；不要向首版 Schema 填不支持的字段冒充已实现。

每轮实施读取已有构建进度，只修正受影响节点。运行实例的状态写在项目 runs/，与 Builder 的设计进度分开。副作用结果未知时先核对实际系统；manual 节点不能自动重放。

## 5. 独立验收与交付

读取 [验收和就绪门槛](references/acceptance.md)，为当前业务生成可执行测试与样例，覆盖新进程正常执行、失败、自动或显式重试及耗尽、中断恢复、最终产物拒绝和重复运行。需要调度时另验触发链路。

由生成项目自己的入口在新的进程或 Agent 会话执行。不能借助 Builder 的临时文件、隐含模型连接或聊天历史；领域 Skill 必须随工作流完整内置并经过实际加载验证；外部服务、模型、MCP 和系统工具需声明安装／连接方式及必要凭据要求，凭据不随包分享。将工作流复制到新位置，在原始工作流和本机技能库路径不可用的隔离条件下验证新运行，不能把仅在构建机器上成功当作可分享。

接入已有项目时，另验从项目入口调用、每个流程独立启动、公共上下文生效、必要的跨流程产物交接，以及受影响旧流程仍可运行。只登记路径或把目录放在一起不能算整合成功；不承诺未实现的自动发现、并行或调度。

交付 README 中的真实启动方式、配置方法、依赖、验收记录、run ID、产物和恢复方式。区分 designed／generated／configured／verified／ready；未通过必需场景就报告准确状态与缺口。样例成功不是对任意业务需求的质量保证。

生成包使用稳定版本的 workflow.yaml 作为唯一定义源。修改定义、代码、锁定依赖或验收标准后重新验证受影响场景，不复用旧 ready 结论。日常执行不进入 Builder；只有用户要改流程或发现定义缺陷时才回到构建模式。
