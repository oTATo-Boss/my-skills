# 工作流运行规则

按 workflow.yaml 执行并验证产物。此入口仅运行已定义工作流，不加载 workflow-builder 或重新设计流程。

脚本和 Agent 适配器从 stdin 接收一个 JSON job，stdout 只返回一个 JSON 对象；日志写 stderr。运行上下文、命名输入、规则和 Skill 资料由 Runtime 显式传入。模型调用或 MCP 连接需由项目自己的适配器实现并验证。

产物保存到 job.output_dir，返回相对于该目录的路径。不要修改已通过节点的产物；不要把凭据写入产物或日志。manual 恢复模式代表副作用结果可能未知，失败或中断后需人工核对，不能自动重放。
