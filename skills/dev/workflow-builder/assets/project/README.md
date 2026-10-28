# 独立工作流项目

此项目由 workflow-builder 生成，运行时不依赖 Builder、本次聊天或三个规划 Skill。
首版 Runtime 支持 Python 3.10+、macOS/Linux、顺序执行 DAG、脚本和 JSON 子进程 Agent 适配器。

先用将运行项目的 Python 安装依赖：

```bash
python3 -m pip install -r runtime/requirements.txt
python3 runtime/runner.py check
python3 runtime/runner.py run --input example-input.json
python3 runtime/runner.py status --run-id <运行ID>
python3 runtime/runner.py retry --run-id <运行ID> --step <失败节点>
python3 runtime/runner.py resume --run-id <运行ID>
python3 runtime/runner.py validate --run-id <运行ID>
```

`run` 创建独立运行 ID 和隔离输出；退出码 0 为成功，1 为执行/验收失败，2 为定义或调用错误，3 为资源受阻，4 为中断。
`run --pause-after <节点>` 在已提交检查点处暂停，之后可在新进程 resume。status 只读已有状态；validate 重新检查真实产物并保存最新验收结果。

每次运行的 runs/<ID>/state.json、events.jsonl、尝试日志和 outputs/<ID>/ 保存真实状态与证据。
重试次数含首次执行，retry 不扩大原预算；自动重试可关闭。manual 节点不自动重放未知副作用。
定义、代码、资源或已提交产物发生变化时，恢复会拒绝旧检查点；排查后启动新运行。不要手工编辑状态来绕过验证。

这不是后台调度器或沙箱，不宣称原生 Codex／Claude／Cursor 适配已验证。Agent 节点需要项目自行提供读取 job 并返回 JSON 的真实模型适配器。
工具 probe 必须是已授权的无副作用检查；stdout 返回 {"ok":true}。所需工具/模型资源必须定义 probe。
实际使用的领域 Skill 完整存放在 skills/<skill-name>/，包含脚本、参考资料和素材，绑定使用包内相对文件路径；不依赖构建者的共享技能库。Skill 文档随 job.resources 传入适配器，关联文件由适配器从包内读取；Runtime 不自动发现技能目录或遍历校验整个包，Builder 必须补充文件清单与摘要校验。未使用 Skill 的默认报告示例不创建空 skills/。
允许动作和工具范围是配置约定，不能替代外部权限控制。

workflow.yaml 是唯一工作流定义；resources.lock.json 记录实际依赖，规则由 Runtime 加载。交付后不会自动搜技能、装 MCP 或更换模型。分享前应在新位置、原始工作流和本机技能库路径不可用的隔离环境中验证包内 Skill；接收者需安装声明的系统／Python 依赖，并自行配置所需模型、MCP 和服务凭据。
所有源码、验证器、规则及资源锁都参与恢复指纹。环境变量值不保存，凭据变更后应重新 check；模型或工具版本应明确记录。
未经过正常、失败、重试、中断恢复、最终验收和重复运行验证的项目只能称为已生成项目，不能标记 ready。
