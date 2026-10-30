# 新会话原生调用实测

本项会启动真实 Codex CLI 模型会话，使用当前登录及模型额度，默认不随单元测试运行。测试对象是临时项目中的虚构技能和受控评分，不能将其结果写入真实 Skill 库。完整案例：基线、B 高分、A 高分、明确指定低分 A、高分 B 依赖阻塞、项目根依赖已满足、无关计算任务。

## 隔离及前置条件

- 需要现有 Codex CLI、git、Python 3 和 macOS sandbox-exec；缺少外层隔离能力时停止，不降级为无隔离运行。
- 生成真正的临时 Git 项目，在其 `.agents/skills` 中放置同名描述但不同执行标记的 A、B。通过项目 AGENTS.md 接入正式参考文档中的维护模板；保持技能、任务不变，只交换受控评分验证选择是否反转。
- 外层 Seatbelt 拒绝读取／写入真实共享库、客户端 Skill 目录、全局指令及开发项目；仅允许核心工具运行时例外，关闭测试进程中的应用及插件扩展。先验证真实库目录访问被拒绝，预检失败不得启动模型。
- 策略路径保留 UTF-8，不能用 JSON 的 ASCII Unicode 转义替代真实中文路径。预检逐一检查所有声明的保护根，并用临时中文目录验证读／写拒绝；探针进程从临时目录启动，避免受保护的开发工作目录干扰标准库导入。真实目录只尝试验证读取被拒绝，写探针只落在临时受控路径。
- 保留当前认证，不复制凭据、不替换 HOME／CODEX_HOME。移除父 App 的会话／工具桥接环境字段，避免把子测试工具调用串回父聊天。使用新的 `codex exec --ephemeral`，不 resume／fork，不指定另一模型。
- macOS 不允许嵌套 Seatbelt；CLI 不再施加第二层沙箱，**始终由外层 sandbox-exec 运行**。脚本里的 CLI `danger-full-access` 是为避免内部二次施加沙箱，不表示外层保护关闭。不要把内部命令单独抽出运行。

认证及正常 CLI 状态存储仍由现有客户端管理；这里隔离的是测试项目与真实 Skill／开发目录，不宣称创建了一套独立账号或完整虚拟机。

## 执行

从本 Skill 根目录执行：

```bash
python3 -B evals/native_invocation.py prepare
python3 -B evals/native_invocation.py run /path/to/generated-fixture --case baseline
python3 -B evals/native_invocation.py run /path/to/generated-fixture --case managed-b
python3 -B evals/native_invocation.py run /path/to/generated-fixture --case managed-a
python3 -B evals/native_invocation.py run /path/to/generated-fixture --case explicit-lower
python3 -B evals/native_invocation.py run /path/to/generated-fixture --case blocked-higher
python3 -B evals/native_invocation.py run /path/to/generated-fixture --case project-ready
python3 -B evals/native_invocation.py run /path/to/generated-fixture --case unrelated
python3 -B evals/native_invocation.py collect /path/to/generated-fixture
```

`prepare` 返回全新的系统临时目录；每个 case 单独启动新会话。相同 case 不覆盖已有日志，再采样应重新 prepare。可同时运行不同项目案例，不能在正在运行的项目内调整评分或规则。

## 通过标准

1. 记录唯一新 thread ID、完整 turn.completed、CLI 退出码及输入材料前后内容比较；模型失败／无法读文件的零退出码不能当通过。
2. 普通 FERN 任务不点名 Skill，由原生发现和模型隐式选择；日志必须有真实脚本调用、零退出码、正确输出及相符的最终答复。仅声称“我选择 B”或答复正确但未执行不算通过。
3. 有同类评分的托管案例必须实际执行 `quality_registry.py select`，然后执行选定入口。A／B 分数对调时业务脚本也必须对调；只读取 JSON 后心算选择不满足新版确定性路由验收。
4. 明确指定 A 时即使其分数低也应执行 A；B 阻塞时不得先盲跑 B 再回退 A。项目根依赖存在时应识别为满足，不误查 Skill 内同名相对目录。
5. 无关任务应直接输出 4，不读取评分或 FERN 入口，不触发库审计。

原始 JSONL、stderr 和任务输出只保留在临时目录。提交的结果只包含必要命令、输出、线程证据及哈希，排除账号配置、凭据及运行缓存。早期探索日志可用 `collect --baseline-label baseline-valid` 指定已验证基线，但须注明它们没有新版前后快照；没有运行的案例明确失败，不能自动补齐为通过。

本验收器的离线反例测试为 `python3 -B scripts/test_native_invocation.py`；它验证判据不会接受虚假证据，不代替真实模型运行。实际结果见 [v1.4.1 实测记录](results/2026-10-30-v1.4.1.md)。结论仅适用于记录中的 CLI／规则／样本，不能推广为所有模型或桌面 UI 的稳定成功率；管理器仍不是原生数字优先级拦截器。
