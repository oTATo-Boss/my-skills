# 当前应用接口与证据

当前应用：**Qwen Image2.1 全能无限版 V2**（平台API名称 Qwen Image2.1 Unlimited Omni Edition），ID `2104057271167791105`。2026-11-02按用户API示例、四张截图及平台 `GET /api/webapp/apiCallDemo` 只读核对全部24个字段；现有应用页读取截断底模的完整文件名。没有提交生成任务。[节点快照](node_map.json)只保存脱敏字段、配置来源和哈希，不保存Key、用户提示词或输入素材。

| 输入 | nodeId | fieldName | 值与规则 |
|---|---|---|---|
| 图1–6 | 476、491、477、492、495、494 | image | 上传返回值；未用传字符串None；纯文生图全部None |
| 提示词 | 497 | prompt | 非空；执行器仅去除首尾空白 |
| 提示词增强 | 528 | value | true；截图优先于示例false |
| 加速 | 515 | value | false |
| 比例 | 13 | aspect_ratio | 完整选项文本，见下方 |
| 原图比例 | 521 | value | original为true；须有参考图1 |
| 分辨率 | 13 | megapixels | 默认2.0，平台范围0.1–16 |
| 图片数量 | 527 | value | 默认1，本地限制1–4 |
| LoRA1名称 | 510 | lora_name | NSFW Qwen by TheseAlpacas V2.safetensors |
| LoRA1强度 | 510 | strength_model | 0.8；截图浮点尾数规范化 |
| LoRA2名称 | 526 | lora_name | QWEN真实时尚摄影高对比高级感大片风格_电商时尚真实高级感摄影大片.safetensors |
| LoRA2强度 | 526 | strength_model | 0.4；覆盖示例0 |
| ZIP输出 | 525 | value | false |
| 高级设置区提示 | 554 | text | 仅展示说明；保留在节点快照，不发送此无运算作用字段 |
| 底模 | 479 | unet_name | noctQUncensoredRealismBuiltOn_v40Base_bf16.safetensors；截图优先于示例int8 |
| 采样器 | 484 | sampler_name | er_sde |
| 调度器 | 484 | scheduler | beta |
| 步数 | 484 | steps | 40 |
| CFG | 484 | cfg | 3.5 |

比例值为 `1:1 (Square)`、`2:3 (Portrait Photo)`、`3:2 (Photo)`、`3:4 (Portrait Standard)`、`4:3 (Standard)`、`9:16 (Portrait Widescreen)`、`16:9 (Widescreen)`、`21:9 (Ultrawide)`。job使用简写，由执行器转换；original设521=true并提供9:16有效占位。应用说明原图比例模式不支持调整MP和数量；脚本仍发送对应占位，不能保证这些值生效。实际尺寸、数量以输出为准。

用户指定的底模、LoRA及开关优先于API示例。LoRA2来自用户提供的[模型卡](https://www.runninghub.ai/zh-cn/model/public/2114552841117831169)，触发词为 `high contrast editorial fashion photography`；编写自然语言提示词时纳入，完整JSON则放在风格字符串字段中。执行器不自动改写提示词，避免破坏已确认JSON。模型卡建议强度1不覆盖用户指定0.4。仅引用平台文件名，不下载或分发权重；未独立核实权重许可、云端加载和最终效果。

## RunningHub v2 直连

- 基址 `https://www.runninghub.ai/openapi/v2`，认证 `Authorization: Bearer KEY`。
- 上传：`POST /media/upload/binary`，multipart字段file；读取data.fileName或download_url。文生图无上传。
- 提交：`POST /run/ai-app/2104057271167791105`，默认instanceType=ultra、usePersonalQueue=false。Ultra沿用用户既有明确指定，示例default不覆盖。
- 查询：`POST /query`，JSON含taskId；旧应用已有taskId可继续恢复，不按新映射重新提交。
- 同一Key与H3共用最多3个远端在途预约，确认终态后释放；提交不明不盲重提。
- 下载遍历图片URL，不携带Key，完整解码并报告实际尺寸与usage；平台结果URL有效期24小时。
- 节点发现为只读 `GET /api/webapp/apiCallDemo`，apiKey仅注入内存请求参数；不打印完整URL、含Key的响应或执行网页/API中的示例代码。

## 迁移与验证边界

上一应用 `2104225323949101057` 使用532/value和534/LoRA1；新应用改为13/megapixels和510/LoRA1，并显式发送底模与采样设置。最初应用 `2101915284503654402` 使用quality=1K/2K/4K；旧quality字段继续在上传前拒绝，2K不等于2MP。新应用允许纯文生图，job需显式提供空images数组；original无参考图会在上传前拒绝。

本次完成元数据只读核对、离线节点/请求构造与恢复回归，未提交新应用的收费生成；不声称底模、LoRA、触发词或Ultra实际加载及画质已经验证。以下两次历史成功均属于最初旧应用。

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
