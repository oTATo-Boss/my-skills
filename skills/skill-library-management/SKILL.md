---
name: skill-library-management
description: Manage a shared agent skill library through hierarchical indexes, purpose-based categories, canonical source ownership, client links and targeted checks. Use when installing, organizing, moving, updating, removing or auditing skills and reusable example libraries; ordinary use of an already selected skill does not require a library audit.
---

# 分级 Skill 库管理

把技能、工作流、创意示例与素材组织成可逐级检索、可追溯维护的资源库。适用于整理已有库、接入新资源、迁移目录、更新或按明确范围删除；管理行为遵循当前用户授权和环境规则。

## 管理模型

- **总入口**列分类、用途、选择提示和分类索引链接，保留系统／插件管理入口。
- **分类索引**维护本分类直接拥有的技能：`名称 — 一句话用途`与真实入口路径；按任务场景分组。
- **包内索引**维护嵌套子技能；分类索引链接到它，不重复维护同一份子技能清单。
- **Skill 入口**说明用途、执行与参考路由；大型示例／素材库另有按效果检索的目录。
- **项目索引**只记录该项目采用的入口、用途与必要约束，复用已有资源，不复制全库。

每份完整清单有一个维护源。共享技能保留一份真实源文件；客户端需要时通过软链接接入。系统、插件发行渠道的资源保留各自所有权和升级机制。物理目录按稳定用途组织，细分检索优先通过索引中的主题分组实现。

## 按任务执行

1. 理清这次是选型、接入、归类、迁移、更新还是删除，并确认受影响范围。发现问题不自动扩大为全库重构。
2. 读取总入口、相关分类索引，再读取具体 Skill 或示例目录；结合当前环境实际启用的系统／插件清单。只加载需要的层级。
3. 接入时核对真实来源、版本、资源闭包和实际能力。比较功能、模板与质量标准，而不是凭名字或工具存在与否判定重复。示例代码、Demo、素材可直接作为参考库接入，无需把每个案例都包装成 Skill。
4. 把用户收集的资源放到约定的共享分类中。保留源码、许可证、必要参考和素材，记录来源、版本与依赖；外部资源更新基于真实内容和版本，不从记忆重写。
5. 一次迁移中同步修改源位置、入口中的相关引用、拥有清单的索引、父级导航和受影响客户端软链接。保留本地定制；不覆盖未知冲突，不自动恢复已删除或停用的资源。
6. 按风险验证：索引变更检查链接、覆盖、重复与数量；新／改 Skill 校验元数据和引用；实际脚本运行针对性行为检查。源文件完整性、语法通过和运行效果分别报告。

删除、覆盖或清理仅按用户明确范围执行。发现未授权的删除候选时列出具体路径与影响；确认后在同一次操作中同步索引和链接。普通选型、只读检查和已授权范围内的整理无需重复请求许可。

## 索引与工具

- 创建或调整索引格式时，读取 [索引契约与模板](references/index-contract.md)。
- 执行迁移或处理不一致时，读取 [变更与校验](references/change-checks.md)。
- 用 [audit_library.py](scripts/audit_library.py) 做只读完整性检查；参数指定技能根目录、总索引及可选客户端链接目录，不绑定特定机器路径。

```bash
python3 scripts/audit_library.py \
  --skills-root /path/to/shared/skills \
  --root-index /path/to/SKILLS_INDEX.md \
  --link-dir /path/to/client/skills
```

脚本检查约定格式的索引导航、技能覆盖、重复登记、数量、失效入口与客户端链接。它不移动、删除、安装或修复文件，也不证明 Skill 的运行行为；遇到不同目录约定先理解其维护源，再调整检查范围。
