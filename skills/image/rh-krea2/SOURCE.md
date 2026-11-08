# 来源记录

- skill: `rh-krea2`
- kind: `local`
- status: `confirmed`
- source: 用户2026-11-08明确要求创建rh-krea2 Skill，并提供RunningHub应用API示例与模型/LoRA截图；本项目辅助编写并维护。
- version: `1.0.0`
- author: 用户定义需求和云端模型组合，Codex辅助编写；沿用本项目rh-qwen-image-2-1的执行与恢复实现及RH共享队列协议。不声明RunningHub服务、工作流和模型权重为原创。
- license: unknown；用户未为本包指定对外许可。第三方服务、工作流和模型归对应权利方，不分发其代码或权重。
- collected_at: `2026-11-08`
- recorded_at: `2026-11-08`
- evidence: 用户附件文本与截图的SHA-256见references/node_map.json；https://www.runninghub.ai/zh-cn/ai-detail/2080156609159286785 及平台apiCallDemo只读元数据；本包离线测试。

## 来源、依赖与能力区别

本包是按用户指定工作流编写的本地执行Skill，不是下载的第三方Skill原包。开发路径 `skills/image/rh-krea2/`；独立安装路径 `~/.agents/skills/image/rh-krea2/`，Claude发现链接指向安装副本。

运行依赖Python 3.9+、requests、Pillow，文件锁使用Unix fcntl。通过requirements.txt正常安装依赖，不打包依赖实现、密钥或用户素材。凭据读取复用已有RH共享配置；三包使用同一共享队列目录，最多3个同Key在途任务。

与Qwen互补：Krea2固定本次截图模型与双LoRA，单图、参考强度1–6及比例开关；不替代Qwen多图编辑能力。与H3的媒体产物及工作流不同，仅共享队列协议。未因工具或用途相近删除其他能力。质量档案待评；未进行生成效果评分。

## 版本与验证

- 1.0.0（2026-11-08）：首次创建。平台只读核对14个字段，截图覆盖底模与LoRA名称/强度；加入单图输入校验、离线预检、原比例开关、批量提交、共享并发、原子回执与恢复、全部图片下载和解码。队列类保持v1协议，包内恢复CLI适配Krea2凭据读取并同时回写原回执taskId、拒绝覆盖不同ID。离线测试和节点查询不等于实际出图；固定模型云端加载、画质、人物一致性和费用尚未实测。

用户同日后续调整：像素默认约1K，具体数值由执行端决定；本包用1.0MP表达近似1K档，默认9:16，原图比例关闭、张数1；可按任务选择其他已核实比例。实际像素尺寸以生成结果为准。
