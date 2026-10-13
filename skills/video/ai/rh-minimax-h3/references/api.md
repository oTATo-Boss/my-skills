# RunningHub H3 API 与节点

固定应用 `2084320751339032577`，AI 应用 API（apiType=4）；使用 OpenAPI v2。生成不要混用旧 `/task/openapi/` 接口。此技能来自本项目已用工具与 2026-10-12 节点快照，不声称所有线上节点已重新核实。

## 接口

域名 `https://www.runninghub.ai`，请求头 `Authorization: Bearer RUNNINGHUB_API_KEY`（运行时注入）。

| 目的 | 请求 | 取用数据 |
|---|---|---|
| 上传 | `POST /openapi/v2/media/upload/binary`，multipart `file` | `data.fileName`，兼容 `data.filename` |
| 生成 | `POST /openapi/v2/run/ai-app/2084320751339032577`，JSON `nodeInfoList`、可选 `instanceType` / `usePersonalQueue` | `taskId`，立即落盘 |
| 查询 | `POST /openapi/v2/query`，JSON `{"taskId":"..."}` | `status`、`results`、`usage`、失败信息 |
| 下载 | `GET results[].url` | 所有结果；不向媒体 CDN 附带 Key |

CREATE / QUEUED / RUNNING 继续每 15 秒查询，SUCCESS 下载，FAILED / CANCEL / CANCELLED 保存失败。链接可能很快过期，生成完成立即下载；上传 fileName 也不要长期复用。

## 节点发现

打开用户指定应用的 [API 详情](https://www.runninghub.ai/zh-cn/call-api/api-detail/2084320751339032577?apiType=4)，取得此应用的完整 nodeInfoList 示例及字段类型/枚举。需要登录时沿用用户已授权登录，不自行换账户。

兼容发现接口为 `GET /api/webapp/apiCallDemo`，参数 `apiKey`、`webappId=2084320751339032577`；它用于发现节点，实际生成仍用 v2。通过客户端 `requests.get(..., params=...)` 在内存注入 Key，**不要打印 URL 或保存带 Key 的 curl**。只提取 `data.nodeInfoList` 和应用身份、日期，去掉密钥和示例中无关的上传素材，保留必需默认节点。实际参数随服务变化，以该应用当前示例为准。

新映射至少注明 `appId`、`snapshot_date`、`source`、`nodeInfoList`；不要把顶层 `curl` 或整份带凭据返回直接落盘。不可获得真实节点时停止提交并说明限制。

## 缓存字段（2026-10-12）

| nodeId / fieldName | 作用 | 值或约束 |
|---|---|---|
| 150 / value | 提示词 | 字符串 |
| 141、142、143、161、175、176 / image | 参考图 1–6 | fileName 或客户端 `$upload`；不用为 `"None"` |
| 144、160、189 / audio | 参考音频 1–3 | 同上 |
| 164 / video | 参考视频 | 本地上传并换 fileName；关闭开关时保留快照字段，不擅自删除 |
| 163 / value | 参考视频开关 | 字符串 `"true"` / `"false"` |
| 115 / aspect_ratio | 画幅 | 使用完整枚举，如 `"9:16 (Portrait Widescreen)"` |
| 186 / value | 秒数 | 字符串数字，5–15 |
| 147 / value | 百万像素 | 字符串数字，如 `"0.9"` |
| 192 / value | 采样步数 | 项目成功任务基线 8 |
| 171 / value | 最高画质参考 | 默认 `"false"`；开启前核实影响 |
| 185 / value | 提示词优化 | 默认 `"false"` |
| 169 / value | 补帧 | 默认 `"false"` |
| 158 / value | 仅 ZIP 输出 | 默认 `"false"`，开启可能不直接返回视频 |
| 159 / lora_name、strength_model | 可选 LoRA | 保留原名称，默认强度 `"0"`，不默认启用 |

完整字段类型和画幅枚举在 [node_map.json](node_map.json)。布尔和数字字段按应用示例使用字符串，不任意改 JSON 类型。

| 用户画质 | 实际像素参数 | 用户说明书的 16:9 参考尺寸 |
|---|---|---|
| 480P | 0.4 MP | 864×480 |
| 720P | 0.9 MP | 1280×736 |
| 1080P | 2.0 MP | 1920×1088 |

竖版尺寸不能仅靠宽高互换保证；最终以输出检测为准。2.0 MP 需应用和实例支持，不自动降档冒充。Plus 可能影响费用；并发最多 3，且受账户其他运行任务与额度约束。历史成本不作当前报价。

401/403 先查认证/账户权益；参数错误重新查此应用节点；余额不足、远端执行失败按回包处理。网络错误不是失败证据，先恢复原任务；不自动无限重试。
