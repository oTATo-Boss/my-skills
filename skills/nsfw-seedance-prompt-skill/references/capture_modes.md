# 唯一摄影机合同

每条提示词只有一个成片摄影机，写进默认设定的 `摄影机身份：`，全片唯一。机位与构图、运镜两栏服从它，不引入第二视点。

| capture_mode | 成片唯一视点 | 设备可见性 | 运镜来源 |
| --- | --- | --- | --- |
| `front_camera_selfie` | 人物手中手机前置摄像头 | 机身全程画外，仅持机前臂边缘可入画 | 只来自持机手腕、呼吸、身体重心 |
| `mirror_selfie` | 手机拍到的镜面反射 | 拍摄手机只在镜中反射内可见 | 持镜手与身体；不写镜外第三视角 |
| `third_party_capture` | 外部摄影机 / 固定机位 | 外部摄影机画外；人物手机只是道具 | 来自外部摄影者 / 固定支撑，不由人物动作驱动 |

默认 `front_camera_selfie`。反射构图不是第四种模式：只有成片主视点经镜面拍到人物才算 `mirror_selfie`；玻璃反光、金属高光、水面倒影服从当前唯一摄影机。

## 错误码

- `E_CAPTURE_MODE_REQUIRED`：默认设定缺少唯一摄影机身份。
- `E_CAPTURE_MODE_MIXED`：同一提示词出现多个 / 不一致的摄影机身份。
- `E_CAPTURE_SOURCE_CONFLICT`：起点截图与指定 capture_mode 冲突。
- `E_CAPTURE_DEVICE_VISIBILITY_CONFLICT`：设备可见性与合同矛盾。
- `E_CAMERA_OPERATOR_CONFLICT`：运镜来源与操作人矛盾。
- `E_HAND_OCCUPANCY_CONFLICT`：持机手执行了其他动作。
