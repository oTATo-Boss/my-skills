# 来源记录

- skill: `rh-qwen-image-2-1`
- kind: `local`
- status: `confirmed`
- source: 用户 2026-10-31 在本会话要求将其 RH Studio「Qwen Image 2.1 多图编辑」制作为独立 Skill；开发目录 `skills/image/rh-qwen-image-2-1`。
- version: `3.0.0`
- author: 用户提出需求与应用范围，Codex 辅助编写 Skill、接口参考、Python 执行器和测试；不声明 Qwen 模型、RunningHub 服务或 RH Studio 前端为本包原创。
- license: unknown；用户未为本新包指定对外许可。第三方应用、模型及服务条款归对应权利方，本包不分发其实现或模型权重。
- collected_at: `2026-10-31`（首次创建）
- recorded_at: `2026-10-31`
- evidence: 本会话的网页只读观察；https://tools.otato.art/rh-studio/ 与 https://tools.otato.art/rh-studio/app.js?v=20261029-h3-v2 公开资源；本包 tests/test_qwen.py。

## 来源与依赖

公开页面 HTML SHA-256：`2bb57af043c5c631bfa8ce9c44c6dc492ed8edb0c79fe621c3a475fb282b5aab`。
公开 app.js SHA-256：`9cd045573412587112dc5ba7774674389e0487524c6467732c058ae48488424a`。页面脚本查询串不代表应用或 Skill 的发布版本。

节点映射按 RH Studio 的实际公开构造逻辑提炼；直连 RunningHub v2 路由参考本仓库 `rh-minimax-h3` 现有协议，Python 执行器独立编写，未复制其实现或第三方前端代码。Qwen 应用的直连上传、提交、查询与下载已完成两次真实测试；详情见 [接口与证据](references/api.md)。

运行依赖：Python 3.9+、requests、Pillow；均通过正常依赖管理使用，不打包库代码，不包含凭据与运行缓存。运行直接请求 RunningHub API，不依赖浏览器或 RH Studio；网页资料仅作为最初节点映射的来源证据。

## 版本记录与验证

- 1.0.0（2026-10-31）：首次创建；支持 1–6 图、1K/2K/4K、1–4 张、预检、单次提交回执、taskId 恢复、全部可识别图片下载与解码。离线测试不等于线上出图，质量档案待评。
- 源码与本机安装副本按项目约定维护，未提交推送前不冒充已完成安装同步。

## 2026-10-31 · 授权真实测试

用户明确要求「测试一下」；用自行绘制的蓝杯与条纹参考图进行两图编辑，未使用私人素材。任务 `2116466766565957634` SUCCESS，default、2K、9:16、1 张；输出 PNG 1152×2016，完整解码并实际查看通过，杯身采用参考配色与图案。平台报告 93 秒、19 RH 币。实际尺寸比请求比例略有差异，已记录；其他画质、实例、多张输出及人物换装不属于本次实测范围。

原始回执和输出保留在项目 `work/rh-qwen-image-2-1-test-20261031/`，不随 Skill 包发布。此次测试通过 `RUNNINGHUB_ENV_FILE` 复用同服务已有私有配置，未复制或输出密钥，也未创建新凭据文件。质量档案仍待评，不将单次成功描述为普遍成功率。

随后用户提供三张人物、服装与卧室参考图并要求对镜自拍。任务 `2116468148375212034` SUCCESS，default、2K、9:16、1 张，输出 PNG 1152×2016，完整解码并实际查看；平台记录 126 秒、26 RH 币。用户查看结果后回复 OK 并授权推送和本机安装。此次验证覆盖三图人物/穿搭/场景融合，不视为身份一致性的定量证明；素材与原始回执仅保留于本机 `work/rh-qwen-mirror-selfie-20261031/`，不提交或安装用户图片。

## 1.0.1 · 直接 API 调用定位

2026-10-31：按用户纠正，统一为与 rh-minimax-h3 同原理的 RunningHub AI 应用直接调用技能，移除网页执行备选及其参考文件，同步展示说明和索引。执行器原本即直连 RunningHub；两次已完成的真实测试均通过直接 API 提交，本次不改动生成链路，也不新增收费任务。

## 1.0.2 · 本机共享 RunningHub Key

2026-10-31：按用户要求，与另一 RH Skill 统一默认读取 `~/.config/runninghub/.env`，保留 `RUNNINGHUB_API_KEY` 优先和 `RUNNINGHUB_ENV_FILE` 显式覆盖。私有 Key 不随仓库或安装包分发；新增隔离测试验证共享路径与读取。

## 1.1.0 · 跨 Skill 共享并发

2026-10-31：按用户指定，同一 RunningHub API Key 合计最多3个远端在途任务，默认并发与滚动补位。新增两包一致的 rh_queue.py 协议实现，使用本机文件锁和持久预约协调多个进程；确认终态后释放，提交不明或查询失败保留预约。Qwen 新增 jobs 批量入口，H3 沿用原批量入口；下载阶段不占远端名额。离线5进程混合测试、Qwen批量测试与H3假服务回归通过，未新增收费生成；本机队列不覆盖未接入的其他工具或机器。

## 2.0.0 · 切换 AI 应用与固定 LoRA

2026-11-01：用户提供新应用 `2104225323949101057` 的 API 示例及 LoRA 截图，并后续要求 Ultra 默认实例。通过平台只读节点查询确认应用名称 Qwen Image2.1 (Unlimited Edition) 和全部18个字段；[node_map.json](references/node_map.json) 保存脱敏快照及原文、截图SHA-256。截图强度0.8/1优先于示例0/0，固定模型名为 NSFW Qwen by TheseAlpacas V2.safetensors 和 Pornmaster_QI2.1_Breasts_Slider_V1.safetensors。模型权重许可未核实，本包不分发权重。

更新六图顺序、分辨率MP、比例完整值、原比例开关、图片数量、提示词及辅助开关；旧quality字段拒绝提交，避免将2K误当2MP。共享Key、同Key最多3个在途和旧taskId查询恢复继续生效。新应用与两LoRA组合尚未真实出图；此前两次成功任务仅证明旧应用。代码、文档与平台只读查询的验证不冒充新配置加载或生成效果证明。

## 2.0.1 · 更新固定 LoRA 组合

2026-11-02：按用户最新截图，LoRA1保留 NSFW Qwen by TheseAlpacas V2.safetensors，强度从0.8调整为0.4；LoRA2替换为 casual_snapshot_realism_qwen21.safetensors，强度从1调整为0.8。节点534/526、Ultra及其他参数沿用现有配置。同步执行器、离线请求断言、技能说明和节点快照；保留旧配置的历史来源记录。最新截图SHA-256：`14330ccce91402b0ec9fc2aff46aef4c59801c87ec189e7ebfc3f1a5beb35acb`。

本次仅验证离线请求构造与副本一致性，未提交收费生成；新组合的实际加载与出图效果尚未验证。

## 3.0.0 · 切换全能无限版 V2

2026-11-02：用户提供新应用API示例与四张配置/模型卡截图，迁移到应用 `2104057271167791105`（中文页面 Qwen Image2.1 全能无限版 V2；API名称 Qwen Image2.1 Unlimited Omni Edition）。只读apiCallDemo核实全部24个字段，并从用户已有页面核实底模完整名 `noctQUncensoredRealismBuiltOn_v40Base_bf16.safetensors`。分辨率迁移至13/megapixels、LoRA1迁移至510；固定两LoRA为NSFW Qwen by TheseAlpacas V2（0.8）与QWEN真实时尚摄影高对比高级感大片风格_电商时尚真实高级感摄影大片（0.4）。提示词增强开启，加速和ZIP关闭；er_sde/beta/40步/CFG3.5沿用新示例，Ultra沿用用户既有指定。

新应用支持文生图与0–6张参考图，MP范围0.1–16；原图比例须有参考图1，该模式平台不支持调节MP/数量。LoRA2模型卡 `https://www.runninghub.ai/zh-cn/model/public/2114552841117831169` 及用户截图确认触发词 `high contrast editorial fashion photography`，交由提示词编写方放入风格字段，执行器不破坏完整JSON。模型卡推荐强度1不覆盖用户截图0.4。截图及API示例哈希保存在node_map.json，无凭据或用户生成内容入库，不分发权重。

离线测试覆盖新节点、底模/LoRA/采样设置、文生图空槽、MP边界与原比例输入校验；共享并发和旧taskId恢复沿用现有机制。只读核对与离线验证不代表新应用实际出图或模型加载成功，未创建收费任务。
