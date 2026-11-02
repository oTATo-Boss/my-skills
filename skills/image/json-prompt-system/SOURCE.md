# 来源记录

- skill: `json-prompt-system`
- kind: `local`
- status: `confirmed`
- source: 本地开发／维护目录 `skills/image/json-prompt-system`；当前维护仓库 https://github.com/oTATo-Boss/my-skills
- version: 2.1.0
- author: oTATo-Boss（用户本人）；2026-10-30 在当前对话明确确认本人制作，Agent 辅助编写／整理。
- license: unknown；当前保留资料未包含足以确认的技能许可声明。
- collected_at: unknown；没有可靠安装／导入日期。
- recorded_at: `2026-10-30`
- evidence: [SOURCE_NOTES.md](</Users/griffith/Desktop/AI/我的项目/my skills/SOURCE_NOTES.md>)；[INSTALL_MAP.json](</Users/griffith/Desktop/AI/我的项目/my skills/INSTALL_MAP.json>)；当前入口 SHA-256 `61450e478e71a61f6614baa5f0e5b93f15de3491e7cae63493d8ce6b0a3e987c`（本次记录快照）。

## 版本记录

- 2026-11-02，v2.1.0：补齐独立使用所需的三块信息，并修正两处实测问题。
  - 三种生活图模式新增 `角色与服装` 块，`mirror-selfie` 与 `front-camera-selfie` 新增 `环境与光线` 块；`third-person` 原本有环境描述，只补角色与服装。
  - 规则改为按输入条件化：有对应参考图时只写一致性与边界贴合，不重述款式、颜色、材质与陈设；无参考图时必须写全，字段不留空。
  - 表情强度新增“勾引 / 挑逗”档，落到停住、咬唇、下巴微收，不靠幅度。
  - 人体规则新增“敏感位置的手”：胸口、裆部、腿间最容易糊，须写清五指、指节与接触面，或把手挪到安全位置。
  - 明确本 JSON 只是完整提示词的一部分，不承担网站端 MD 提示词、参考图编排或后端逻辑。

## 本地调整与边界

- 开发目录与本机安装目录保留独立实体副本，来源资料按项目约定同步。
- 本次仅补录来源资料；来源确认状态不等于版本、作者、许可或运行能力全部已确认。

## 2026-10-30 · 当前作者归属最终确认

用户明确确认本技能为本人制作；以本次直接确认取代此前“仅记录为本人／二创版本”的归属表述。Agent 辅助实现不改变本项目作者登记。工具、第三方依赖、参考资料、继承模板及素材的原作者与许可仍分别保留，不将技能归属扩展为这些外部资源的原创声明。
