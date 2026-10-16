# 来源记录

- skill: `codex-imagegen`
- kind: `adapted`
- status: `confirmed`
- source: https://github.com/oTATo-Boss/my-skills/tree/main/skills/image/codex-imagegen
- version: `2.0.0`
- author: oTATo-Boss，Agent 辅助编写；历史版本的第三方原始出处未完整记录。
- license: 当前 v2 文档与脚本为本次重新编写的 MIT 实现，见 [LICENSE](LICENSE)。历史版本的未知上游许可不由此追溯变更。
- collected_at: 2026-10-16（本次重写 v2 可分发版本）
- evidence: `tests/test_codex_imagegen.py` 的八项离线行为测试；入口 SHA-256 `024cae653df07f817e13dbe2eab877e092583996afd12da0f872d31d2aaf1acb`。
- recorded_at: `2026-10-16`

## 当前包边界

当前 SKILL.md、Python 脚本和 shell 兼容层均在本次从头编写；没有随包复制历史未知上游源码。保留通过 Codex CLI 生图的原用途和参数兼容。Codex 服务、客户端与账户权限不由此许可证授予，也不随技能分发。

公开文档仅提供安装／运行方法；Python/macOS 预检与 mock 测试不证明 Windows/Linux 生图或账户实际调用可用。真实图片仍须实际生成及视觉验收。
