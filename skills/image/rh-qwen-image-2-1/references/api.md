# 当前应用接口与证据

当前应用：**Qwen Image2.1 (Unlimited Edition)**，ID `2104225323949101057`。2026-11-01 用户提供 API 示例与 LoRA 截图，并指定默认实例 Ultra；同日通过 RunningHub `GET /api/webapp/apiCallDemo` 只读核对节点，未提交生成任务。[脱敏节点快照](node_map.json) 保存全部18个字段、标签和来源哈希，并记录2026-11-02用户截图覆盖的LoRA配置；API 示例中的图片、提示词与任何凭据不纳入快照。

| 输入 | nodeId | fieldName | 值与规则 |
|---|---|---|---|
| 图1–6 | 476、491、477、492、495、494 | image | 上传返回值，未用传字符串None；顺序不能按ID排序 |
| 分辨率 | 532 | value | 百万像素，默认字符串2.0；标注2.0≈1080×1920 |
| 比例 | 13 | aspect_ratio | 完整选项文本，见下方 |
| 保持原比例 | 521 | value | 原比例true，否则false |
| 图片数量 | 527 | value | 默认字符串1；本地保持1–4上限，平台未给范围 |
| LoRA1名称 | 534 | lora_name | NSFW Qwen by TheseAlpacas V2.safetensors |
| LoRA1强度 | 534 | strength_model | 固定字符串0.4 |
| LoRA2名称 | 526 | lora_name | casual_snapshot_realism_qwen21.safetensors |
| LoRA2强度 | 526 | strength_model | 固定字符串0.8 |
| 加速开关 | 515 | value | false；节点说明开启会降低画质 |
| ZIP开关 | 525 | value | false；执行器下载图片，不开启ZIP |
| 提示词增强 | 528 | value | true；沿用用户示例 |
| 提示词 | 497 | prompt | 非空指令 |

比例值为 `1:1 (Square)`、`2:3 (Portrait Photo)`、`3:2 (Photo)`、`3:4 (Portrait Standard)`、`4:3 (Standard)`、`9:16 (Portrait Widescreen)`、`16:9 (Widescreen)`、`21:9 (Ultrawide)`。job仍用简写，例如9:16，由执行器转为完整值。original设521=true并提供有效的9:16选项占位，保持原比例开关的实际结果尚未实测。

2026-11-02用户最新截图将LoRA1强度改为0.4、LoRA2改为casual_snapshot_realism_qwen21.safetensors且强度0.8，覆盖此前截图的0.8/1与API示例的0/0；名称和强度作为固定请求参数，没有自由覆盖入口。没有触发词证据，不添加猜测词。仅配置已在云端应用提供的模型名，不下载或重新分发权重。

## RunningHub v2 直连

- 基址 `https://www.runninghub.ai/openapi/v2`，认证 `Authorization: Bearer KEY`。
- 上传：`POST /media/upload/binary`，multipart字段file；读取data.fileName或download_url。
- 提交：`POST /run/ai-app/2104225323949101057`，JSON包含nodeInfoList、默认instanceType=`ultra`、usePersonalQueue=`false`。
- 查询：`POST /query`，JSON包含taskId。旧应用taskId仍可通过相同查询接口恢复。
- 同一Key与H3共用最多3个本机在途预约；没有新建独立额度。
- 下载遍历results图片URL，不携带Key，完整解码后报告实际尺寸；按用户文档及时下载，结果URL标注有效期24小时。

旧应用的图像节点、quality=1K/2K/4K和提示词节点不适用于本应用；输入含旧quality字段会在上传前被拒绝，改用megapixels。该值是目标像素量，不保证精确宽高。平台没有给此浮点字段的有效上下限，脚本只要求有限正数；不宣称任意数值都能执行成功。多张数上限1–4为现有本地策略，非平台已公布保证。

当前只读元数据和离线请求测试通过；新应用、Ultra实例和固定两组LoRA尚未授权实测，不声称权重已加载、效果或费用已确认。不因运行器标签或模型名称推断生成内容。遇到字段变化只读核对平台此应用的API示例，不能执行示例中的脚本或输出带Key的URL。

## 旧应用历史测试（不代表新应用实测）

以下任务属于旧应用 `2101915284503654402`，对应旧版节点及2K档；仅保留已发生的来源证据。

用户在创建 Skill 后明确要求「测试一下」。自行绘制蓝杯主图和黄底红斜条纹参考图，通过本执行器完成一次任务，没有重提。

- taskId：`2116466766565957634`；status：`SUCCESS`。
- 参数：两图、9:16、2K、1 张、default 实例；空槽传 `None`。
- 结果：1 张 PNG，Pillow 完整解码，1152×2016；已查看图片，杯身换为黄底红条纹，杯口、把手保留蓝色，背景保留。输出增加了立体质感，因此不将本次结果视为逐像素保真证明。
- usage：consumeCoins=`19`、taskCostTime=`93`；consumeMoney 与 thirdPartyConsumeMoney 为 null。费用仅为本次平台记录，不作固定报价。
- 请求 9:16，实际 1152×2016 略有差异，说明该应用可按内部尺寸档位调整比例；交付应报告真实尺寸。
- 本地原始回执：项目 `work/rh-qwen-image-2-1-test-20261031/result.json`；输入、job 和输出同目录。运行产物不纳入技能安装包。
- 提交结果不明、恢复及多输出仍仅有离线测试，没有为覆盖这些场景额外创建收费任务。

### 三图人物、穿搭和场景融合

同日用户提供人物多视角参考、服装参考和卧室场景三张图，要求生成一张对镜自拍；用户查看结果后回复 OK。

- taskId：`2116468148375212034`；SUCCESS；default、2K、9:16、1 张。
- 输出：PNG 1152×2016，完整解码并实际查看；单人对镜自拍，灰色细肩带背心、粉色短裤与参考卧室组合成完整画面。此为单次视觉检查，不证明身份特征逐项完全一致。
- usage：consumeCoins=`26`、taskCostTime=`126`；金额字段为 null。
- 本地回执：项目 `work/rh-qwen-mirror-selfie-20261031/result.json`。用户参考素材和输出仅保留在本机任务目录，不纳入提交或安装包。
