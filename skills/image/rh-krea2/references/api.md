# 接口与节点证据

应用：[krea2 图生图/图片编辑 N版](https://www.runninghub.ai/zh-cn/ai-detail/2080156609159286785)。2026-11-08 用户提供 API 文本和配置截图；同日只读 `GET /api/webapp/apiCallDemo` 核实应用名及全部14个字段。元数据返回的示例提示词和素材不是用户本次输入，不随包保存。脱敏快照见 [node_map.json](node_map.json)。

## 节点

| nodeId | fieldName | 映射 |
|---|---|---|
| 72 | image | 唯一参考图上传返回的 fileName，不能复用文档的示例图片 |
| 99 | text | 本次用户任务提示词 |
| 142 | value | 默认true，关闭原图比例并选9:16；显式original=false，其他八种比例=true |
| 83 | aspect_ratio | 完整选项；original 下发送9:16有效占位，由142关闭覆盖 |
| 141 | value | 像素/百万，默认1.0（用户要求约1K）；覆盖API示例1.5000000000000002 |
| 131 | value | 参考强度，默认2.25；API浮点展示2.2500000000000004；平台说明范围1–6 |
| 132 | strength_model | 平台额外身体调节，保持示例0，不开放本次无关控制 |
| 105 | value | 输出张数，默认1 |
| 130 | unet_name | 截图指定底模，覆盖API示例 krea2MuseByStable_v15TurboFp8.safetensors |
| 133 | lora_name / strength_model | 截图指定 realism_engine_krea2_v3.1_new.safetensors / 0.4 |
| 145 | lora_name / strength_model | 截图指定 Krea-2-Turbo-HTT_c1-st10000.safetensors / 0.4 |
| 119 | value | ZIP关闭，false |

八种比例完整字符串由执行器的 ASPECT_VALUES 映射。分辨率0.1–16、张数1–4、文件30MiB为本地执行限制；平台元数据没有给出等价上限，不能写成平台保证。原图比例控制与Qwen应用含义不同，不可复用其节点或布尔方向。

用户同日后续指定像素默认1K、原图比例关、张数1，比例可按任务选择。执行器用1.0MP近似1K档，不承诺长边恰好1024；分辨率选择器仍按比例和工作流尺寸档取整。

## 直连接口

基址 `https://www.runninghub.ai/openapi/v2`，认证 `Authorization: Bearer KEY`。

- 上传 `POST /media/upload/binary`，multipart字段 `file`；使用 `data.fileName`，其次 `download_url`。上传引用的有效期按用户文档为1天。
- 提交 `POST /run/ai-app/2080156609159286785`，JSON含 `nodeInfoList`、`instanceType`、布尔 `usePersonalQueue=false`。节点 fieldValue 使用字符串；不配置有额外保留费用的 retainSeconds。
- 查询 `POST /query`，JSON含 `taskId`；识别 SUCCESS / FAILED 等终态，保留 usage 与失败详情。
- 结果 `results[].url` 按用户文档有效24小时，下载全部图片，实际解码获取宽高。下载不携带API Key。
- 不对提交POST自动重试；先创建回执，结果不明时保留预约并核对平台，已有ID只恢复查询。

## 证据边界

截图确认底模、两个LoRA名称和强度；只读查询确认字段和说明，不证明云端实际存在／加载这些权重，也不证明生成效果。平台描述提醒人物一致性有限；参考强度的方向来自其说明，执行器不承诺身份一致性。当前单参考图限制来自已公开的唯一图片字段，不据应用标签“文生图”推断无图运行方式。

脚本由本项目 `rh-qwen-image-2-1` 的传输、回执、下载与批次实现改编；共享队列实现按原协议复制，以保持跨Skill额度一致。未修改其他RH包，未提交收费生成。
