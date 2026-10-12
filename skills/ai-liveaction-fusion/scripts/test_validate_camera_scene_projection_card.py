#!/usr/bin/env python3
from validate_camera_scene_projection_card import validate


BASE = """# 镜头事实卡
## 镜头—场景投影
- 证据帧：关键帧 100；前邻帧 88；后邻帧 112
- 摄影机：高机位明显俯拍；无 roll；置信度高
- 人物姿态拓扑：头在中上；双肩斜线；双手在下部
- 人物接触与遮挡：女主后脑遮挡男主胸口
- 主导可见表面：地面
- 表面分布：背景地面约 75%；墙面仅顶部窄带
- 地墙交界 / 地平线：地墙交界在画面顶部；地平线不入画
- 消失方向与地面纹理收缩：石板向画面顶部收缩
- 场景资产映射：使用石地、墙根和立柱基座；按俯拍重投影
- 资产原视角级别：仅拓扑
- 空间边界：无
- 当前机位允许出现：石地、墙根、立柱基座
- 当前机位禁止出现：人物头后大面积高墙和高窗
- 高影响不确定项：无
"""

assert validate(BASE).ok

missing = BASE.replace("- 表面分布：背景地面约 75%；墙面仅顶部窄带\n", "")
result = validate(missing)
assert not result.ok and not result.blocked and any("表面分布" in e for e in result.errors)

missing_boundary = BASE.replace("- 空间边界：无\n", "")
result = validate(missing_boundary)
assert not result.ok and any("空间边界" in e for e in result.errors)

blocked = BASE.replace("- 高影响不确定项：无", "- 高影响不确定项：摄影机可能为平视，待用户确认")
result = validate(blocked)
assert not result.ok and result.blocked and not result.errors

print("ALL TESTS PASSED")
