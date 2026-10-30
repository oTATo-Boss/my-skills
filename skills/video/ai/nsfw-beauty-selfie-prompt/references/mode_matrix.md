# 模式仲裁（起点图 / 生成模式）

写提示词前先定两个值，缺一不阻断但需在交付前声明：

```text
capture_mode: front_camera_selfie | mirror_selfie | third_party_capture
generation:   T2V | I2V | R2V | FLF2V | EXTEND | EDIT
```

## 仲裁规则（按优先级）

1. **起点图路由**：提供起点图 → `generation` 优先 `I2V`（给终点图时 `FLF2V`）；先看起点截图判 capture。
2. **无起点图**：未提供起点图且未要求图生视频 → 自动落到 `T2V` + `front_camera_selfie`，交付前一句话声明，不阻断。
3. **上游素材**：`R2V` / `EXTEND` / `EDIT` 必须有对应上游 take 或参考素材；缺失阻断报 `E_SOURCE_ASSET_REQUIRED`。
4. **capture 冲突**：用户显式指定的 capture_mode 与起点截图判断结果冲突 → 阻断报 `E_CAPTURE_SOURCE_CONFLICT`，不静默纠正。

## 起点截图兼容门

| 截图特征 | 判定 |
| --- | --- |
| 完整手机机身直接出现在人物旁、无镜面介质 | `third_party_capture` |
| 手机与人物共同出现在可识别镜面内 | `mirror_selfie` |
| 手机不可见、近距离手臂延伸、轻微广角、屏幕视线 | `front_camera_selfie` |
| 只有玻璃 / 金属反光而主体不经镜面被拍到 | 不算 `mirror_selfie`，按上表逐条判断 |
