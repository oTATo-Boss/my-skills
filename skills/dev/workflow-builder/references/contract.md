# 工作流契约

## 唯一维护源

workflow.yaml 使用平台无关的执行概念；随包 [Schema](../assets/project/runtime/workflow.schema.json) 是首版已实现的格式，schema_version 为 1。
模板以 JSON 格式序列化（合法 YAML 子集），也支持 PyYAML 解析的普通 YAML。不要同时维护另一份可独立修改的 workflow.json。

顶层：workflow_id、revision、goal、inputs（JSON Schema）、outputs（命名绑定）、runtime、trigger、steps、resources、rules、acceptance。首版 adapter 为 json-subprocess-posix，trigger 仅 manual。拒绝不支持的字段，不静默忽略。

每步必须有 id、depends_on、inputs、executor、outputs、completion、failure、recovery。节点只读取自己的输入或已声明依赖的上游产物。输出、最终验收和 JSON 文件可用 JSON Schema；输出 Schema 至少为 object、properties、required，使用有意义的约束，不能用空字段和自报成功代替质量检查。

## 数据绑定

每个命名输入取以下一种格式：

```json
{
  "topic": {"input": "/topic"},
  "material": {"step": "research", "pointer": "/facts"},
  "language": {"value": "zh-CN"}
}
```

pointer 使用 JSON Pointer；空字符串引用整个对象，`~1` 表示 `/`，`~0` 表示 `~`。最终 outputs 使用同样绑定。引用某个 step 时必须在 depends_on 的祖先闭包中；最终 outputs 可以引用任意已完成节点。

## 执行与检查

executor.kind 为 script 或 agent，command 是参数数组，禁止 shell 拼接。`{python}` 占位替换为启动 Runtime 的 Python。进程工作目录固定为项目根。Agent 节点还须声明 role，可通过 instructions 数组加载角色文件；生成适配器应实际消费这些指令和 resources 中的 Skill 文本。

```json
{
  "executor": {"kind": "script", "command": ["{python}", "scripts/write.py"], "resources": []},
  "failure": {"max_attempts": 2, "timeout_seconds": 30, "retry_on": ["timeout", "executor_failed"], "automatic": true},
  "recovery": {"mode": "idempotent"}
}
```

max_attempts 包含首次执行和已中断的尝试；retry 不重置预算。automatic=false 时失败后显式 retry。认证或配置错误不放入循环重试；通过前置资源检查报告 blocked。

recovery.mode 为 pure、idempotent 或 manual：前两者允许在预算内重放，后者代表可能有不可判定副作用，不自动重试或重放中断节点。幂等性由业务实现保证，Runtime 仅传递稳定 idempotency_key，不能保证外部 exactly-once。

completion 和顶层 acceptance 至少包含 schema、artifacts 或 command 之一；可组合使用。artifacts 根据输出中的 pointer 取得相对输出目录路径，检查文件存在、最小字节数、contains 文本及可选 JSON schema；文件散列记入检查点。command 为真实验证程序，stdin 获得 job 与 outputs，退出 0 且 stdout 为 {"ok":true} 才通过。

产物必须位于本次输出目录内。首次通过时保存的文件散列在恢复前复查。内容或源码变化时首版保守拒绝旧检查点，要求新 run；不自动实施状态迁移或智能重算。

首版顺序执行 DAG，不执行 when 分支、并行或有界反馈状态机。需要时由生成项目显式扩展适配器、Schema 和测试，或使用已满足需求的执行器，不能只画分支图就声称可运行。
