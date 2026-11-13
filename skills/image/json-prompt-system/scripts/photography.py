"""Validate an explicit, portable photography card without adding aesthetic defaults."""

FIELDS = {
    '版本': str, '分享重点': str,
    '相机': {'拍摄关系': str, '摄影者位置': str, '距离与透视': str, '画幅边界': str},
    '人物': {'身份依据': str, '妆发穿搭': str, '姿态与支撑': str, '视线与表情': str},
    '空间层次': str, '光线': str, '明暗与颜色': str, '成像质感': str,
    '成功条件': list, '参考分工': list,
}
RELATIONSHIPS = {
    'third-person': '朋友或摄影者从画外拍摄，人物与相机位置按摄影设计执行。',
    'front-camera-selfie': '前置自拍，持机位置、手臂可及范围和视线按摄影设计执行。',
    'mirror-selfie': '对镜自拍，反射方向、可见手机与遮挡按摄影设计执行。',
    'ecommerce-editorial': '时尚摄影，人物、相机与空间按摄影设计执行。',
}


def validate_fields(value, fields, path):
    if not isinstance(value, dict):
        raise ValueError(f'{path} must be an object')
    missing = fields.keys() - value.keys()
    extra = value.keys() - fields.keys()
    if missing or extra:
        raise ValueError(f'{path}: missing {sorted(missing)}, unknown {sorted(extra)}')
    for key, spec in fields.items():
        item = value[key]
        label = f'{path}.{key}'
        if isinstance(spec, dict):
            validate_fields(item, spec, label)
        elif not isinstance(item, spec):
            raise ValueError(f'{label} must be {spec.__name__}')
        elif spec is str and not item.strip():
            raise ValueError(f'{label} must not be empty')


def validate_card(card, mode):
    validate_fields(card, {'摄影设计': FIELDS}, 'card')
    shot = card['摄影设计']
    if shot['版本'] != '1.0':
        raise ValueError('摄影设计.版本 must be 1.0')
    if shot['相机']['拍摄关系'] != mode:
        raise ValueError('摄影设计.相机.拍摄关系 must match selected mode')
    criteria = shot['成功条件']
    if not 2 <= len(criteria) <= 3 or any(not isinstance(s, str) or not s.strip() for s in criteria):
        raise ValueError('成功条件 requires 2–3 nonempty strings')
    for index, ref in enumerate(shot['参考分工'], 1):
        validate_fields(ref, {'图号': int, '负责': str, '保留': str, '调整': str}, f'参考分工[{index}]')
        if type(ref['图号']) is not int or ref['图号'] != index:
            raise ValueError('参考分工.图号 must be consecutive upload order starting at 1')
    return shot


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON field: {key}')
        result[key] = value
    return result
