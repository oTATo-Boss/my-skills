# 来源记录

- skill: `rh-qwen-image-2-1`
- kind: `local`
- status: `confirmed`
- source: 用户 2026-10-31 在本会话要求将其 RH Studio「Qwen Image 2.1 多图编辑」制作为独立 Skill；开发目录 `skills/image/rh-qwen-image-2-1`。
- version: `1.0.2`
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
