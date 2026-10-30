---
name: skill-library-management
description: "Manage the shared skill library at ~/.agents/skills: install, update, audit, deduplicate, score and select skills. Reuse one quality store, batch repository queries and incrementally refresh evidence. Maintain shared indexes, provenance, mapped development copies and client links. Excludes other projects, system skills and plugins; audits are read-only by default."
metadata:
  version: "1.6.0"
---

# 分级 Skill 库管理

只管理 `~/.agents/skills/` 共享库及其已登记的客户端链接；本项目仅维护对应源码与安装映射。不扫描其他项目内置库、系统／插件技能或客户端独立安装项。沿用分类、索引、来源、迁移和安装同步；普通调用不触发全库审计。

## 按需智能审计

日常只检查相关范围；全量指整个共享库。按 [智能审计与去重](references/semantic-audit.md) 核对共享实体、索引、已知源码映射和指向共享库的客户端链接，不将范围外目录纳入数量或评分。

Agent 阅读实际流程、输入输出、场景、脚本与依赖，比较重复、重叠、互补、调用冲突和独立能力；对竞争实现按证据评估质量并保留独特能力。目标是能力完整、调用准确、维护便利，不是数量最少。名称、关键词、描述或内容哈希只用于定位线索，不能代替语义与行为判断。

审计默认只读，先交付关系、依据、能力保留方案和待验证项；明确整理授权才执行相应变更。修改前保存可恢复备份与回滚记录，优先归档；执行复用下方流程与变更指南，完成后核对能力覆盖、结构和客户端入口。

## 评分、选型与持续优化

先执行 [统一查询与档案流程](references/shared-quality-store.md)：唯一数据源为 `~/.agents/skill-library-management/SKILL_QUALITY.json`，同目录 `SKILL_QUALITY.md` 仅由它生成。查询离线复用；仓库批量去重、只查缺失／到期事实；按实际变化增量更新，不再生成日期／项目临时评分表。

按 [100 分质量规范](references/quality-scoring.md) 维护效果 25、可靠性 20、完整度 15、维护 10、GitHub Star 15、本人开发 15 的证据档案；未知／过期项不冒充已知 0 或确定总分。Star 核实原始仓库及独立／合集归属，本人原创和深度二创按来源与实际贡献评估。

先复用有效历史产物与测试，再补最必要的语义评估和安全验证。日常允许先完成逐项内容审阅的参考评分，与严格实测总分分开；效果／可靠性估评不能冒充成功率或实测。参考分、质量分与来源偏好分开展示，未知元信息给区间，详细规则见质量规范。待评必须列缺口，不能交一批空分后声称完成。

按 [优先调用与持续优化](references/routing-and-refresh.md) 先尊重用户指定，再核对任务、可见范围和运行条件；有可用同类档案时运行选择器，同场景候选优先高分，接近时考虑本人开发、真实使用记录和专业适配。职责互补则组合使用。该策略通过项目调用指令和管理器流程生效，不是 Codex 原生评分拦截器。

新增／更新时自动进入相关候选的查重与必要重评；周期复核只刷新约定范围内的到期证据，不自行创建后台任务。更优候选先提出替代或吸收升级方案，保留独特能力与来源许可。普通调用只读相关索引及已有档案，无档案时按实际能力选用并标待评，不扫描全库。

## 管理模型

- **总入口 → 一级分类 → 可选二级分类 → Skill／包内索引／资源。** 一级按稳定用途，二级按任务阶段、产物或工具组；数量少、职责清楚的分类可以直接放 Skill。
- **完整包保持完整。** Skill 的脚本、参考、素材、许可证随目录移动；嵌套技能保留包内层级，套件的共享资料留在套件内。
- **每个完整清单只有一个拥有索引。** 父级导航到子索引，子索引登记 Skill；各层数量统计递归拥有的独立 Skill，参考资料、模板和客户端软链接不计数。
- **两种项目索引分开使用。** 普通工作项目只登记选用的入口；技能开发仓库只登记其维护的源码，并按安装映射沿用本机分类路径。

普通共享技能维护其真实来源；自研或明确纳入开发仓库的技能保留开发与安装两份独立实体副本。Codex 读取共享库，Claude 的逐技能软链接指向安装副本。系统、插件技能沿用发行渠道，不搬入共享库。

本地原创／二创归属与上游资料完整度分别记录：用户自研或二创已经确认时，来源状态记为已确认；缺失的上游作者、原始仓库或许可写在相应字段中，不把当前本地版本的归属降为未知。

## 按任务执行

1. 明确共享库内本次范围和终点；先读本项目索引与共享总入口，再进入相关分类／二级分类和实际入口，不因项目导航或客户端目录扩大管理范围。
2. 根据现有拥有索引和真实文件归类。保留既有名称和用户例外，不强制所有分类拆二级，不凭名称相似或工具插件存在判定重复。分类与展示规则见 [索引契约](references/index-contract.md)。
3. 接入时核实来源、版本、作者与许可声明、依赖和同类冲突，按上方生命周期流程评估相关候选；在每个独立 Skill 根目录保存 `SOURCE.md`，包括嵌套子技能；更新时维护记录，迁移时随完整包保留。按 [来源记录](references/source-records.md) 区分安装来源、二创来源与参考资源；无法确认的信息明确标为未知，不猜测、不标为原创。用户提供的套件保留原始资料，示例库按资源管理。
4. 迁移前确定旧路径到新路径的映射，检查独立修改，记录文件内容、权限及有效引用；整包移动后同步各层索引、导航数量、跨技能路径、客户端链接及项目安装映射。具体方法见 [变更与校验](references/change-checks.md)。
5. 自研更新在开发目录完成，遵守项目规定的提交／推送与安装同步顺序。同步前保留独立修改，同步新增、修改和本次授权删除的资源，排除缓存与私有配置。
6. 验证本次变更：索引与映射检查、来源记录覆盖、资源和权限核对；改动脚本路径时运行相关行为检查。分别报告源码、安装同步、实际运行的证据及来源待确认项，达到完成条件即停止。

删除仅覆盖明确授权的技能及其相关登记和入口，不顺带删除同名品牌工作流或其他来源的技能。用户已明确授权时继续执行；未授权的候选先列出范围，不自动恢复已删除或停用资源。

## 索引与工具

- [audit_library.py](scripts/audit_library.py)：只读检查完整维护库的分级导航、拥有关系、覆盖、数量和客户端入口；可检查来源记录、开发／安装映射及副本一致性，不绑定机器路径。
- [test_audit_library.py](scripts/test_audit_library.py)：验证深浅分类、嵌套包、链接、映射和冲突诊断的回归用例。
- [quality_registry.py](scripts/quality_registry.py)：只读计算与校验质量档案、过滤和排序 Agent 提供的候选，按需核实 GitHub 数据；不执行 Skill 或修改库。
- [quality_store.py](scripts/quality_store.py)：固定共享档案的离线查询、批量仓库复用与刷新、带修订保护的增量写入和唯一展示表生成；不执行业务技能。
- [test_quality_store.py](scripts/test_quality_store.py)：在隔离共享根验证范围、复用、增量、冲突、失败和完成状态。
- [test_quality_registry.py](scripts/test_quality_registry.py)：验证评分、证据边界、Star 口径、调用优先级与失效处理。
- [语义验收场景](evals/semantic-audit.md)：用隔离案例检查能力判断、授权边界和治理交付。
- [评分与调用验收](evals/quality-and-routing.md)：验证评分证据、候选优先级及原生调用接入边界。
- [新会话原生调用实测](evals/native-invocation.md)：按需在系统沙箱中运行真实 CLI 会话，验证隐式调用、评分互换及运行条件。

```bash
python3 scripts/audit_library.py \
  --skills-root /path/to/shared/skills \
  --root-index /path/to/SKILLS_INDEX.md \
  --link-dir /path/to/client/skills \
  --check-sources
```

本开发仓库额外传入其 `--install-map`；同步后可加 `--compare-installed`。底层结构工具保留通用根参数以支持本项目与隔离测试，不代表 Skill 有权扩展到其他真实库；其职责仍为只读结构检查。
