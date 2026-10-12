# my-skills

我的原创 Skill 仓库，集中维护自己开发的 Skill 源码、脚本、资源和版本。一个仓库可以包含多个 Skill，每个 Skill 保持独立、可复用。

## 目录约定

```text
my-skills/
├── README.md
├── AGENTS.md
├── SKILLS_INDEX.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── scripts/       # 可选：执行脚本
        ├── references/    # 可选：参考文档
        ├── assets/        # 可选：素材与资源
        └── CHANGELOG.md   # 版本与变更记录
```

当前仓库尚未加入 Skill；上面是新增 Skill 时采用的目录约定。

## 新增与维护

1. 在 `skills/<skill-name>/` 创建独立目录，使用小写字母与连字符命名。
2. 在 `SKILL.md` 中声明 `name`、`description`，说明用途、使用条件、操作步骤和依赖。
3. 将脚本、参考和资源放在所属 Skill 内，内部引用使用相对路径。
4. 在 `SKILLS_INDEX.md` 登记名称、用途与入口；在该 Skill 的 `CHANGELOG.md` 记录版本、日期和变更。
5. 提交前检查引用与依赖，并按改动风险验证脚本或工作流。

只收录本人原创 Skill。引用外部代码或素材时记录来源、版本及适用许可。仓库作为源码和版本维护源，本机安装按需单独处理。
