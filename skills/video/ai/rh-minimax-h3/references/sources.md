# 来源与版本

- 显示名称：RH-minimax-H3；技能标识及文件夹：`rh-minimax-h3`；版本 1.0.0（2026-10-13）。
- 按用户要求将已使用的项目工具封装为可跨项目使用的本地 Skill，新增独立凭据保存、任务构造和调用说明。
- 原客户端、测试和视频测试样本：`/Users/griffith/Desktop/土豆/@土豆老板oTATo/agent/tools/runninghub-minimax-h3/`，客户端 2026-10-10 修订版。用户说明书 `RunningHub_MiniMax_H3_API说明书.md` v1.1（2026-10-09）；实际脚本优先于说明书中的较旧示例代码。
- 节点结构：同目录 `node_discovery_20261012.json`；成功任务默认值取同目录 `node_map.json`。移除旧图像/音频、示例提示词与 curl，仅保留必要结构和关闭状态的参考视频默认字段。可选 LoRA 强度维持 0。
- 本次改编：读取本机私有配置；新增构造器；完整视频不整体读入内存检查头；查询网络错误保留未结束提交；恢复成功更新同 taskId 回执；JSON 记录和运行异常脱敏 Key。原应用与 API 归 RunningHub 及应用作者，原项目代码/说明未声明独立许可证，作者未完整核实；不声明整包均为原创、不授予第三方许可。
- 依赖：Python 3.9+、requests 2.x；可选 ffprobe。本机配置、输出和 Python 缓存不进入源码与安装同步。

官方资料：

- [应用详情](https://www.runninghub.ai/ai-detail/2084320751339032577) 与 [应用 API 页](https://www.runninghub.ai/zh-cn/call-api/api-detail/2084320751339032577?apiType=4)：节点变化时核对。2026-10-13 未重新取得该页面的在线节点，快照日期仍为 2026-10-12。
- [上传 v2](https://www.runninghub.ai/runninghub-api-doc-en/api-425761098)、[查询 v2](https://www.runninghub.ai/runninghub-api-doc-en/api-425767807)：2026-10-13 页面可读取导航，但抓取正文不含可核实请求字段；此版本接口参数依据项目已有说明与客户端，不把网页抓取当成完整验证。
- [官方集成说明](https://www.runninghub.ai/runninghub-api-doc-en/doc-8287470)：节点发现的历史出处。

v1.0.0 验证范围：本地假服务生成/下载、查询恢复、提交不明保护、超时停止、假/空视频拒绝；本地配置权限/读取优先级、构造器素材顺序与节点值。不在创建 Skill 时提交收费视频；不据此证明账户余额、实时线上节点或输出审美。
