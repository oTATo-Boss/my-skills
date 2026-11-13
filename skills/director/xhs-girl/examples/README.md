# 完整摄影设计示例

例子是可迁移的原创设计，不是实际拍摄参数记录。无图例子的人物为成年原创设定，生产时替换身份依据和实际参考分工。

| 场景/关系 | 文件 | 关系模式 | 校准图例 |
|---|---|---|---|
| 身份图+摄影参考的职责分离 | [identity-plus-photography](identity-plus-photography.json) | third-person | 图1为实际成年身份，图2为实际上传的R22摄影参考 |
| 店内隔柜胸像 | [record-store](record-store.json) | third-person | R26、R21 的关系迁移 |
| 书店高位近拍 | [bookstore-overhead](bookstore-overhead.json) | third-person | R22 |
| 暖窗暗调低头 | [warm-window](warm-window.json) | third-person | R08 |
| 秋日隔桌 | [autumn-table](autumn-table.json) | third-person | R26 |
| 夜街正面补光 | [night-street](night-street.json) | third-person | R29 |
| 日光发色 | [sun-hair](sun-hair.json) | third-person | R11 |
| 镜前叠穿 | [mirror-outfit](mirror-outfit.json) | mirror-selfie | R15 |
| 前置表情近照 | [front-selfie](front-selfie.json) | front-camera-selfie | R28 的近距关系迁移 |

JSON prompt 根目录执行 `python3 scripts/compose.py third-person --photography --resolution 1K --ratio 3:4 < /absolute/path/record-store.json`。其他关系更换命令中的模式，并保持卡内拍摄关系一致。只要 JSON 加 `--json-only`。

双参考例子运行前实际上传对应的两张图。只拿到一张身份图时，应删除第二项并把摄影关系作为文字设计，不能声称工具见过图2。
