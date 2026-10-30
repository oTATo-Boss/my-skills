# Apilio Midjourney 接口参考

核实日期：2026-10-30。以下为平台代理协议的整理；兼容性、版本和价格由实际账号决定，不把示例中的模型版本当作默认。

## 地址、模式和鉴权

用户于 2026-10-30 确认基础地址为 `https://api.apilio.ai`；默认 Imagine 完整地址为 `https://api.apilio.ai/mj/submit/imagine`。这是用户提供的运行配置，不是从 Apifox 文档域名推断。

`Authorization: Bearer <MJ_API_KEY>`，JSON 请求体。`MJ_BASE_URL` 是 `/mj` 前的 HTTPS 地址。默认 URL 为 `BASE/mj/submit/imagine`；fast 可配置 `BASE/mj-fast`，实际请求为 `BASE/mj-fast/mj/submit/imagine`。同理有 `mj-relax`、`mj-turbo`；图片代理后缀有 relay/origin/proxy。令牌设置优先于 URL 路径，然后才是系统默认。因此脚本配置只代表请求路由，不能证明最终执行模式。

向导中的 `/fast/mj/...` 与补充文档不一致；本 Skill 以补充文档的明确路径规则为依据，仍应与账号提供的 Base URL 核对。**不要拿付费 POST 试探不同路径**。查询已有任务可验证路由，不能承诺任意 ID 跨模式查询均有效。

## 新任务字段

以下路径均在 `/mj/submit/` 下，方法 POST，返回提交结果（不是最终图像）。

| 后缀 | 关键字段 | 说明 |
|---|---|---|
| imagine | prompt 必需；base64Array 可选 | prompt 为字符串；垫图是 data URI 字符串数组 |
| blend | base64Array 必需；dimensions 可选 | 多图混合，dimensions 为 SQUARE / PORTRAIT / LANDSCAPE；执行器采用常见 2–5 张限制，代理变更时重新核实 |
| describe | base64 必需 | 单张 data URI |
| shorten | prompt 必需 | 分析已有文字 |
| edits | image、prompt、maskBase64 | 独立编辑入口，文档示例 image 是公开可访问图片 URL，mask 为 PNG data URI；示例还展示扩画布，画布/蒙版几何须按目标对齐，不能照抄示例 base64 |
| upload-discord-images | base64Array | 返回 result **URL 数组**，不是任务 ID；为 sref 等 URL 参考或外部编辑准备上传图片 |

本地 PNG/JPEG/WebP 可由脚本转换为 `data:image/...;base64,...`。风格/身份参考 URL 放在哪里由 Prompt Skill 根据已确认的模型参数决定。edits 文档未完整说明所有图像输入类型及蒙版极性；不要从 modal 的黑白规则直接推断所有 edits 模式，执行前查看当时接口说明并视觉核对蒙版。外部图没有公开 URL 时先用平台上传，不擅自传本地路径或推断 image 接受 base64。

## Action / Modal

POST `/mj/submit/action`：`taskId` 为成功父任务 ID，`customId` 为其真实 buttons 中选出的精确值；可选 notifyHook。`buttons` 每项可有 label、emoji、customId、style、type。不支持的特殊按钮包括 Describe 的 Imagine all 和放大后的爱心；不是所有展示按钮都代表可执行生图操作。

`code=21` 表示等待二次提交，`result` 是待确认任务 ID。POST `/mj/submit/modal` 使用这个 ID，prompt 可选（空表示沿用），局部重绘加 maskBase64。Region 蒙版为黑底白选区；Custom Zoom 的最终 prompt 包含 `--zoom`，文档范围 1–2。Remix 开启时 Reroll、Variation、Pan 也可能弹窗；部分账号自动提交 Remix 则不弹窗。以实际返回为准。

## 返回、查询与恢复

提交结果含 code、description、result、properties。

| code | 含义 | 处理 |
|---|---|---|
| 1 | 接受 | 保存 result ID 后查询 |
| 22 | 排队 | 保存 ID，不重复提交 |
| 21 | 弹窗 | 保存新 ID，转 modal |
| 23 | 队列满 | 保留原响应；示例即便含 result 也不能当已接受；不自动再提交 |
| 24 | 提示词被拒绝 | 保留 description，不自动改写绕过 |
| 其他 | 提交错误 | 保留响应，诊断后按授权处理 |

GET `/mj/task/{id}/fetch` 返回 id、action、status、progress、imageUrl、failReason、buttons、properties，以及时间字段。状态包括 NOT_START、SUBMITTED、IN_PROGRESS、MODAL、SUCCESS、FAILURE、CANCEL。ID 始终按字符串处理。

SUCCESS 才完成；失败保留 failReason。Describe/Shorten 的文字通常在 `properties.finalPrompt`、`properties.finalZhPrompt`；Shorten 的 Show Details 可进一步分析，但属于额外 action，按目标决定。生成中的 imageUrl 可能只是预览，勿提前交付为最终图。

GET 可对限流/瞬时错误有界重试，等待超时保持可恢复状态。POST 不自动重试；丢响应时不能依靠本地哈希冒充服务端幂等支持，必须恢复平台记录。本地操作账本只能防止本工具在同一状态目录重复发送，不能防止其他客户端或新状态目录重复提交。

平台标注查询免费；fast/relax 价格不同。Action、重绘、变体、高清增强等可能再计费，当前读取页面没有完整报价表；不写固定价格或承诺操作免费。以账号当时报价、模式和实际扣费为准。支持 notifyHook 的请求可设置回调，但脚本默认轮询，不搭建回调服务；回调也需按 ID 核对状态。

## 来源（按需核查）

- [接入向导](https://gpt-best.apifox.cn/doc-6172523)
- [模式、返回码、弹窗及回调](https://gpt-best.apifox.cn/doc-3530863)
- [Imagine](https://gpt-best.apifox.cn/api-139393505)
- [Blend](https://gpt-best.apifox.cn/api-139393503)
- [Describe](https://gpt-best.apifox.cn/api-139393504)
- [Shorten](https://gpt-best.apifox.cn/api-139393507)
- [Action](https://gpt-best.apifox.cn/api-139393501)
- [Modal](https://gpt-best.apifox.cn/api-139393506)
- [外部图片 edits](https://gpt-best.apifox.cn/api-323778871)
- [上传图片](https://gpt-best.apifox.cn/api-295408056)
- [查询任务](https://gpt-best.apifox.cn/api-139393509)
