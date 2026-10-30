# 共享库统一查询与质量档案

本文件规定实际维护范围、唯一档案位置与执行顺序。评分权重和证据标准沿用 [质量规范](quality-scoring.md)，不另造评分算法。

## 范围固定

本 Skill **只管理 `~/.agents/skills/` 共享库**。全量指该共享库，不指全机所有项目。共享库内的父入口、真正子 Skill、套件共享资源均保留既有归属。

- 不枚举其他项目，不从客户端注册项目列表扩展范围；不审计或治理项目内置库、系统技能、插件缓存、客户端独立安装项。
- 客户端只核对已经指向共享实体的入口；不能顺着客户端目录把其他资源纳入清单。共享根内链接若解析到范围外，只记录边界，不跟进读取或评分。
- 本开发仓库只按已有 `INSTALL_MAP.json` 维护共享 Skill 对应的源码、版本和安装副本，不产生第二份评分档案，不扫描其他源码项目。
- “不含子 Skill”的展示折叠父包／套件；并列独立 Skill 仍分别列出。折叠不更改原有索引数量，也不把子项的分数平均为一个套件分数。

## 唯一位置与数据归属

| 文件 | 固定用途 |
|---|---|
| `~/.agents/skill-library-management/SKILL_QUALITY.json` | **唯一可维护数据源**：当前 profiles、去重仓库快照 repository_snapshots、旧评估 history |
| `~/.agents/skill-library-management/SKILL_QUALITY.md` | **唯一展示表**：从上述 JSON 原位生成，用途、场景、六项分数、原始 Star、完成状态；不能手工改分 |

不再为日期、项目、客户端、每次查询生成另一份当前评分 JSON／CSV／Markdown。共享索引仅导航到这里，不复制动态分数；本项目也不存一份真实用户评分数据。模板和隔离测试的虚构档案不属于活动档案。

每项以“共享根相对目录 ID + scenario”唯一定位；绝对 entry 必须位于共享根且解析目标仍在范围内。任务场景不同保留多个档案，不跨用途排名。用途说明 description 与任务契约 scenario 分开保存。同名查询返回全部匹配项和 ID，不能悄悄取第一个。

JSON 中 `profiles` 沿用原格式；`repository_snapshots` 以规范化的 owner/repo 为键，保存原始事实、查询日期及失败／重试记录；`history` 只保留被替换的旧评估，不能混入当前排序。更新使用文件锁、修订校验和同目录原子替换；短暂写入文件不是新增评分表，成功或失败后清理。JSON 已提交而展示生成失败时明确提示，用 render 修复展示，不把旧表当新数据。

## 根目录与历史资料

`~/.agents/` 根目录只保留 `skills/`、`SKILLS_INDEX.md`、`skill-library-management/`、实际被客户端使用的 `tools/` 和安装器 `.skill-lock.json`。Finder 缓存、空探针、断链及已失效登记核实后清理；不能按名称相似删除仍使用的工具或来源证据。

管理资料由 `skill-library-management/README.md` 导航：`receipts/` 统一保存安装／迁移回执，`reports/` 保存仍被 SOURCE 引用的真实修复与运行证据。移位时修正当前 SOURCE 路径，回执和历史报告原始内容保持不变。不重建过时的 SOURCE_RECORDS 汇总或另一份当前 Skill 清单。

可恢复备份和清理日志固定放到 `~/.local/state/skill-library-management/`，不再把临时上游仓库、客户端配置备份堆在 `.agents/backups/`。清理必须保留原路径、权限、链接原始目标和恢复步骤。来源路径等纯管理变更只有在核对包清单确认执行内容不变后，才可沿用评分并更新 revision；已有修订不匹配的记录仍需复核，不能覆盖成当前有效。

## 先复用，再补证据

1. 每次从唯一 JSON 查询当前条目、场景、版本、revision、各维度证据和 review_after；普通查询离线完成，不扫描其他库，不联网重查。
2. 首次归并历史结果时，只读取用户已知、已授权的现有记录；逐项核对共享范围、身份、原始证据、版本和日期。有效部分沿用，未知与失败照实保留，不能把“导入”写成“已完成评分”。历史表保留为历史材料，不再增量维护或自动反复导入；新档案之后始终以唯一 JSON 为准。
3. 缺指标时先查已知的真实产物、测试报告、SOURCE 与维护记录，不能因没做过本次测试就丢弃仍有效的历史证据。也不能把别人／旧版／其他任务的测试转嫁给当前场景。
4. 完整度、维护质量由 Agent 阅读实际流程、决定行为的参考与脚本后给分并说明扣分；不能依靠目录数量、描述长度或统一默认分。效果与可靠性需要对应任务的实际证据；缺少时设计最小必要的安全验证，不因需要实测就启动收费或有外部副作用的业务。
5. 能在当前授权内补完的继续完成；确实受账号、费用、环境或缺少原始证据阻塞的，记录具体缺口、已尝试动作和下一步。**只创建一批待评行不算评估完成。**

## 统一批量查询 GitHub

先由 Agent 核实 SOURCE 指向的是原始 Skill 仓库，区分维护 fork、合集、工具依赖与参考素材。未知归属先查证，不能机械抓取所有 GitHub 链接给分。

1. 收集本次范围内已确认原始仓库，以大小写不敏感的 owner/repo 去重；同仓库多个 Skill 只查一次。保留仓库重命名的请求名与规范名，不凭 301 或同名自动改写 Skill 来源。
2. 先运行 plan-github：只有缺失或到期快照进入 fetch；有效快照 reuse，失败冷却期 deferred。默认仓库事实保鲜期 7 天，可按本次需要用 `--max-age-days` 调整；这不延长各 Skill 指标的 review_after。
3. 已有 GitHub 连接器可用时，按该计划批量读取官方 API，结果直接组织为 update 的 repository_snapshots 数组，从标准输入写入同一档案。无足够连接器能力时用 refresh-github 复用现有官方 API／gh 后备。不要为每个 Skill 各调一次查询工具。
4. CLI 对暂时性网络／超时／服务端错误最多重试一次，**包含 urllib 与 gh 后备在内每仓库最多两次传输请求**；不叠加两层重试。HTTP 状态直接传递；gh 后备的限流也停止本批剩余请求。404 不重复请求，403／429 记录冷却。失败保留最后成功值及原查询时间，标明失败／过期，不能改成 0，也不能无限重试。默认次日可重试；服务明确要求更晚时遵从其 Retry-After，由 Agent 延后本批调度，不抢先重跑。
5. API 查询只更新仓库事实，不证明独立／合集归属、本人开发贡献或运行质量。Agent 核实关联后，仅更新相应 profile.github，保留来源依据与证据原日期，再由原评分脚本计算 Star 分。不能把刷新日期改成旧实测证据的新日期。

## 增量更新与冲突

| 变化 | 只处理必要部分 |
|---|---|
| 新增共享 Skill | 建立身份／用途／来源，查相关竞争候选；复用已有仓库快照，补必要评分与证据 |
| Skill 更新 | 比较实际版本／包内容／依赖；重评受影响维度，未受影响部分由 Agent 说明沿用依据，保留原证据版本和日期 |
| 新的真实运行结果 | 按运行 ID 去重，保留成功和失败；只更新该任务场景的效果／可靠性与运行记录 |
| 仓库数据到期 | 去重刷新仓库事实，再更新有关 Star 指标；不重建所有 profile |
| 原创／二创证据变化 | 更新来源归属和贡献判断，不重置无关实测；不能把“本人制作”机械等同所有资源均原创 |
| 路径变动／归档 | 按已授权变更迁移 ID、entry 和引用并保留关联历史；不自动恢复已停用项 |

更新先 query 获得 store_revision，然后提交**本次变化条目的完整 profile**（从当前条目改起，不从空模板覆盖）；未提交的条目原样保留。同一条目的未变维度和 runs 要保留，较旧评估不得覆盖较新评估。因明确变化需要将已核实项置为未知／过期时，在同一个更新请求的 invalidations 列出 id、scenario、dimension、reason；脚本拒绝无理由的降级或丢失运行记录。

```json
{
  "profiles": [],
  "repository_snapshots": [],
  "invalidations": [
    {"id": "video/example", "scenario": "指定任务", "dimension": "reliability", "reason": "依赖更换，旧运行证据不再适用"}
  ]
}
```

发生并发修改时旧修订写入失败；重新读当前数据再合并，不能强制覆盖。失败不重新从历史表初始化，不造一个带日期的新评分表绕过冲突。

既有运行 ID 的记录不能静默修改结果、版本、证据或验证状态。确有原始记录录入错误时，提交 run_corrections 数组，每项明确 id、scenario、run_id、reason 与 previous_digest（原 run 对象按脚本 digest 算法得到的哈希）；旧事实和更正理由一并进入 history。不能将一次失败通过同 ID 更新成成功来提高调用优先级。

## 统一查询命令

从当前 Skill 根目录执行。正常省略 `--agents-home`；非默认覆盖被程序限制在系统临时目录下，仅用于隔离验收，不能拿其他真实项目作为另一个管理根。核对包修订时连同包内文件／目录链接检查边界，越界只报告，不打开外部目标计算哈希。

```bash
# 默认只展示父入口／套件；离线、只读、不创建文件
python3 -B scripts/quality_store.py query
# 指定名称或共享相对目录 ID；场景必须精确匹配
python3 -B scripts/quality_store.py query --id image/character-design
python3 -B scripts/quality_store.py query --id image/character-design --scenario '实际任务契约' --check-current
# 明确需要子项时才展开
python3 -B scripts/quality_store.py query --include-children
# 计划不联网；刷新必须使用刚查询所得修订
python3 -B scripts/quality_store.py plan-github
python3 -B scripts/quality_store.py refresh-github --apply --expected-revision ACTUAL_REVISION
# Agent 审查后的增量数据可直接从标准输入传递，不生成临时评分表
python3 -B scripts/quality_store.py update --input - --apply --expected-revision ACTUAL_REVISION
# 仅在展示损坏／需要重建时原位生成
python3 -B scripts/quality_store.py render --apply --expected-revision ACTUAL_REVISION
# 验收指定范围的评分是否真正完成；有待完成项返回 2
python3 -B scripts/quality_store.py query --check-current --require-complete
```

query 只读现有档案；未收录返回零条，不宣称全库覆盖。完整盘点的入口数量与已建档／完成评分数量分开报告；不能用 277 个折叠展示条目冒充展开后的 Skill 数。按任务匹配和名字检索无相关结果时沿共享分类索引找候选，再增量补入同一档案，不创建第二份表。

普通 query 不重算全部包哈希，其 current_revision 为 not_checked；实际竞争／评分验收须对相关候选使用 --check-current 或提供选择器要求的当前版本和 revision。包变化或入口缺失不复用旧分确定赢家，需 Agent 根据变更范围完成必要重评。外部工具的 score/select 仍是通用底层校验器，日常输入固定使用本文件规定的唯一 JSON。

## 完成标准与交付

分别报告：本次范围／数量、已完整评分数、部分完成数、各缺口与阻塞、实际查询／复用仓库数、验证结果和固定档案位置。

- 单项只有六项证据均满足、版本／内容与任务匹配、未过期且 scorer 给出确定 total，才计入该任务的已完成评分；无 GitHub 来源仅在已证明不存在时适用既有 not_applicable 规则。
- 任何未知／部分／过期维度使总分仍为 null。脚本退出 0 仅表示查询／写入成功，不能声称评估完成；用 summary.complete、incomplete 与 assessment_complete 区分，--require-complete 对未完成返回 2。
- 交付清单必须含用途、任务、六项分数或明确缺口、证据、原始 Star／查询时间、原创归属与状态。不能只交分类数量，也不能把已核实的来源分当完整质量总分。
- 全库评估不要求机械执行所有收费业务，但也不能直接将全部效果、可靠性、完整度、维护质量留空后宣称完成。先利用有效历史证据和安全验证；真正无法补齐的诚实交付未完成项。
- 本 Skill 的开发、规则与工具测试完成，和共享库全部 Skill 的评分完成，是两件事，必须分开报告。
