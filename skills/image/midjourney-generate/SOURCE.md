# 来源记录

- skill: `midjourney-generate`
- kind: `local`
- status: `confirmed`
- source: 用户在本会话提供的 Midjourney 功能专家／工作流调度器／Apilio 执行器规格；本地开发目录 `skills/image/midjourney-generate`。
- version: `1.0.2`
- author: 用户定义需求与功能边界；Codex 按指令编写 Skill、参考和 Python 执行器。
- license: unknown；用户未声明本地源码对外许可。引用文档的版权与使用条件归原提供方，未复制第三方实现代码。
- collected_at: `2026-10-30`（本次首次创建）
- recorded_at: `2026-10-30`
- evidence: 本会话规格、Apifox 页面逐项核对及本地离线行为测试 `scripts/test_mj.py`。

## 参考资料与依赖

接口资料来源为 https://gpt-best.apifox.cn/doc-6172523 与 `references/apilio-api.md` 中链接的 Action、Modal、edits、上传和补充参数页面；页面读取日期 2026-10-30。文档快照没有统一协议版本号，部分 API 页面显示最后修改于 2025-12-26，向导/补充文档显示 2025-07-08。当前 Skill 不是平台官方发行包，不宣称完整实现其所有 API。

Python 3.10+ 标准库负责网络、状态和 CLI，Pillow 负责下载后的完整解码；实际运行版本由环境决定。提示词协作复用外部 `midjourney-prompting`，该 Skill 独立维护，未复制其正文或将其版本能力当作代理能力证明。

## 验证边界

用模拟 Client 和临时状态目录验证 mutation 账本、排队/弹窗/错误处理、真实按钮选择、状态恢复及图像验证；首次创建未进行线上测试；本次用户授权后的真实测试见下。价格表及外部 edits 的全部 mask 约定不完整，执行时按相应参考规则核查。

## 1.0.2 本机配置接入

2026-10-30：按用户明确提供的 Apilio 基础地址接入共享私有配置，支持 MJ/APILIO 环境变量覆盖；密钥保存在仓库与技能目录之外，不收录在来源记录或安装包。

## 1.0.2 真实生图验证

2026-10-30：用户授权配置并进行一次 Imagine，任务 1793343556045730 最终 SUCCESS，耗时约 355 秒；生成 2048×2048 PNG 四宫格，已实际查看并验证完整解码。图片中转域名对 urllib 返回 403、系统 curl 返回 200，执行器据此增加仅下载 GET 的 curl 回退；不会重新生成或向图片域名传 API Key。Action/Modal/edits 仍只有离线测试，未进行收费实测。
