# 分类、索引与展示契约

## 目录层级

采用「总入口 → 一级用途分类 → 可选二级分类 → Skill／包内索引／资源」。一级沿用稳定用途，二级按任务阶段、产物或完整工具组划分。

分类多而混杂时增加二级；数量少、职责清楚时直接放 Skill。没有固定数量阈值，也不为对称而制造空目录。沿用用户确认的名称，新增分类通常用小写英文；`web design` 的空格和 `Rules` 的大小写等既有明确约定保留。

```text
skills/
├── video/
│   ├── SKILLS_INDEX.md
│   ├── ai/
│   │   ├── SKILLS_INDEX.md
│   │   └── short-video-prompt/SKILL.md
│   └── creative/
│       ├── SKILLS_INDEX.md
│       └── direct-video/SKILL.md
├── image/
│   ├── SKILLS_INDEX.md
│   └── fashion-picture/SKILL.md
└── social-media/
    ├── SKILLS_INDEX.md
    ├── social-media-router/SKILL.md
    ├── content-planning/SKILL.md
    └── shared/
```

真实分类与完整技能清单以该库当前索引为准，本指南不复制本机全量目录。一个 Skill 只有一个归属目录；跨用途在索引中引用，不复制安装。`references/`、`scripts/`、`assets/` 和 `shared/` 是资源，不拆成分类。嵌套包可以同时有自身 Skill 和子技能索引，例如 `blender-doc-reference` 的总入口与六个专题。

## 拥有清单与数量

- 总索引拥有分类索引；一级索引拥有二级索引或直接 Skill；二级索引拥有 Skill 或包内子索引。
- 每个 Skill 在一个完整拥有清单中登记一次。父级通过子索引递归汇总，不再列同一份子技能清单。
- 每个实际承载技能的分类／二级分类都有 `SKILLS_INDEX.md`；拥有嵌套技能的包也有包内索引。单个 Skill 的脚本和参考目录不需要索引。
- `技能数量：N` 是递归拥有的独立 Skill 数。包自身入口和真正的子技能各计一次；目录、示例、模板、源码／安装副本和客户端软链接不额外计数。
- 返回父级和跨分类参考写普通段落或表格；带用途说明的导航列表用于拥有关系。索引内代码示例不参与统计。

## 可解析的维护格式

拥有条目固定为 `- [名称](路径) — 一句话用途`，链接到真实 `SKILL.md` 或子级 `SKILLS_INDEX.md`。各层写一行 `技能数量：N`。子索引导航可附 `（N 个技能）`，应与子级实际数量一致。

总索引示例：

```markdown
# 技能库总入口

技能数量：3

- [video](skills/video/SKILLS_INDEX.md) — 视频提示词与导演。（2 个技能）
- [image](skills/image/SKILLS_INDEX.md) — 图片与服装设计。（1 个技能）
```

一级分类示例：

```markdown
# video 技能索引

技能数量：2

[返回总入口](../../SKILLS_INDEX.md)

- [ai](ai/SKILLS_INDEX.md) — AI 视频提示词。（1 个技能）
- [creative](creative/SKILLS_INDEX.md) — 视频导演。（1 个技能）
```

二级分类或浅分类示例：

```markdown
# video/ai 技能索引

技能数量：1

[返回分类索引](../SKILLS_INDEX.md)

- [short-video-prompt](short-video-prompt/SKILL.md) — 创作和审查单镜头短视频提示词。
```

分发到仓库的索引使用相对路径；本机索引可使用稳定绝对路径。路径含空格时包裹为 `<...>`，例如 `[web design](<skills/web design/SKILLS_INDEX.md>)`。Skill 名以 frontmatter 的 `name` 为准，目录名允许保留上游命名。

## 开发仓库与普通工作项目

技能开发仓库只保存其维护的 Skill，并按安装分类保存在 `skills/<分类>/[<二级分类>/]<skill-name>/`。`INSTALL_MAP.json` 的值同时是相对于项目 `skills/` 和本机安装根目录的路径。只建立实际需要的分类，数量按项目子集统计；开发与安装是独立实体副本。

普通工作项目的 `SKILLS_INDEX.md` 只登记项目选用的技能入口，可指向共享库或插件入口，并随任务增量补充。它是选型索引，不接管共享清单、不要求复制技能源码，也不套用完整库的覆盖检查。

## 给用户看的清单和结构方案

维护索引沿用上面的行式；展示按用户需要用表格。结构方案默认按一级文件夹分块，一行一个二级文件夹：

| 二级文件夹 | 数量 | 主要放什么 | 全部 Skill |
|---|---:|---|---|
| `ai/` | 2 | 短视频提示词与实拍融合 | short-video-prompt、ai-liveaction-fusion |

文件夹名保持原文，名称列写全该分组的 Skill，不用代表项或省略号。用户要求一行一个 Skill 时，再用「文件夹／Skill／简短说明」。方案只说明需要改变的层级，明确保持现状的分类；未授权执行时不移动文件。
