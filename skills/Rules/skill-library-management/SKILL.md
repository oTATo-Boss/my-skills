---
name: skill-library-management
description: Organize and maintain skill libraries with purpose-based categories, optional subcategories, package indexes, development/install mappings and client links. Use for installing, classifying, migrating, updating, removing or auditing skills and reusable resources; ordinary use of a selected skill does not require a library audit.
metadata:
  version: "1.1.0"
---

# 分级 Skill 库管理

按用途归类，通过分级索引找到技能，完整保留包内资源，并维护开发目录、本机安装副本与客户端入口。适用于接入、分类、迁移、更新、卸载和完整性检查；用户只要求方案时，交付方案即可。

## 管理模型

- **总入口 → 一级分类 → 可选二级分类 → Skill／包内索引／资源。** 一级按稳定用途，二级按任务阶段、产物或工具组；数量少、职责清楚的分类可以直接放 Skill。
- **完整包保持完整。** Skill 的脚本、参考、素材、许可证随目录移动；嵌套技能保留包内层级，套件的共享资料留在套件内。
- **每个完整清单只有一个拥有索引。** 父级导航到子索引，子索引登记 Skill；各层数量统计递归拥有的独立 Skill，参考资料、模板和客户端软链接不计数。
- **两种项目索引分开使用。** 普通工作项目只登记选用的入口；技能开发仓库只登记其维护的源码，并按安装映射沿用本机分类路径。

普通共享技能维护其真实来源；自研或明确纳入开发仓库的技能保留开发与安装两份独立实体副本。Codex 读取共享库，Claude 的逐技能软链接指向安装副本。系统、插件技能沿用发行渠道，不搬入共享库。

## 按任务执行

1. 明确本次范围和终点；先读项目索引、库总入口，再进入相关分类／二级分类和实际入口，不为普通选型扫描全库。
2. 根据现有拥有索引和真实文件归类。保留既有名称和用户例外，不强制所有分类拆二级，不凭名称相似或工具插件存在判定重复。分类与展示规则见 [索引契约](references/index-contract.md)。
3. 接入时核实来源、版本、作者与许可声明、依赖和同名冲突。用户提供的套件保持原始资料；未声明的信息标为未知，不标为原创。示例库按资源管理，不把每个案例包装成 Skill。
4. 迁移前确定旧路径到新路径的映射，检查独立修改，记录文件内容、权限及有效引用；整包移动后同步各层索引、导航数量、跨技能路径、客户端链接及项目安装映射。具体方法见 [变更与校验](references/change-checks.md)。
5. 自研更新在开发目录完成，遵守项目规定的提交／推送与安装同步顺序。同步前保留独立修改，同步新增、修改和本次授权删除的资源，排除缓存与私有配置。
6. 验证本次变更：索引与映射检查、资源和权限核对；改动脚本路径时运行相关行为检查。分别报告源码、安装同步、实际运行的证据，达到完成条件即停止。

删除仅覆盖明确授权的技能及其相关登记和入口，不顺带删除同名品牌工作流或其他来源的技能。用户已明确授权时继续执行；未授权的候选先列出范围，不自动恢复已删除或停用资源。

## 索引与工具

- [audit_library.py](scripts/audit_library.py)：只读检查完整维护库的分级导航、拥有关系、覆盖、数量和客户端入口；可检查开发／安装映射及副本一致性，不绑定机器路径。
- [test_audit_library.py](scripts/test_audit_library.py)：验证深浅分类、嵌套包、链接、映射和冲突诊断的回归用例。

```bash
python3 scripts/audit_library.py \
  --skills-root /path/to/shared/skills \
  --root-index /path/to/SKILLS_INDEX.md \
  --link-dir /path/to/client/skills
```

开发仓库额外传入 `--install-map /path/to/INSTALL_MAP.json`；完成安装同步后可加 `--compare-installed` 核对内容和权限。普通项目的选型索引不要求覆盖整个共享库；检查命令、范围与限制见变更指南。检查脚本不移动、删除、安装或自动修复资源。
