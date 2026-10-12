# my-skills

我的 Skill 开发仓库，集中维护自己开发及二创、整合编写的 Skill 源码、脚本、资源和版本。一个仓库包含多个独立、可复用的 Skill。

当前维护 **14 个 Skill**，来自本机正在使用的安装版本。入口和用途见 [SKILLS_INDEX.md](SKILLS_INDEX.md)，来源说明见 [SOURCE_NOTES.md](SOURCE_NOTES.md)。

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

每个 Skill 保留自身所需的文件和目录；可选目录不要求全部建立。

## 开发与安装

本仓库是开发目录，本机安装目录保存独立实体副本，两处同时保留源码。安装目录不通过软链接指向开发仓库；已有 Claude 客户端链接继续指向本机安装目录。

维护顺序：**在本仓库修改 → 针对性验证 → 提交并推送 → 同步更新本机安装副本 → 核验内容与入口**。

[INSTALL_MAP.json](INSTALL_MAP.json) 记录每个 Skill 在 `~/.agents/skills/` 下的相对安装位置。同步完整资源和执行权限；若安装副本存在独立修改，先协调差异。具体执行约定见 [AGENTS.md](AGENTS.md)。

## 新增与维护

1. 在 `skills/<skill-name>/` 创建独立目录，使用小写字母与连字符命名。
2. 在 `SKILL.md` 中声明 `name`、`description`，说明用途、使用条件、操作步骤和依赖。
3. 将脚本、参考和资源放在所属 Skill 内，内部引用使用相对路径。
4. 在 `SKILLS_INDEX.md` 登记名称、用途与入口；在该 Skill 的 `CHANGELOG.md` 记录版本、日期和变更。
5. 提交前检查引用与依赖，并按改动风险验证脚本或工作流。

收录本人原创及本人维护的二创、整合版本。引用外部代码或素材时保留来源、版本及适用许可，不将第三方参考资料标为原创。
