#!/usr/bin/env python3
"""Build a short- or long-video H3 job from a dated node snapshot, offline."""
import argparse
import json
import math
from pathlib import Path

MAP = Path(__file__).resolve().parents[1] / 'references/node_map.json'
LONG_MAP = MAP.with_name('node_map_long.json')
APP_IDS = {'short': '2084320751339032577', 'long': '2103012816681041921'}
ASPECTS = {
    '1:1': '1:1 (Square)', '2:3': '2:3 (Portrait Photo)', '3:2': '3:2 (Photo)',
    '3:4': '3:4 (Portrait Standard)', '4:3': '4:3 (Standard)',
    '9:16': '9:16 (Portrait Widescreen)', '16:9': '16:9 (Widescreen)',
    '21:9': '21:9 (Ultrawide)',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prompt-file', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--name', default='video')
    parser.add_argument('--mode', choices=APP_IDS, default='short', help='short：原应用；long：长视频应用')
    parser.add_argument('--seconds', type=int, help='short 默认 15（5–15）；long 示例默认 35，范围待应用确认')
    parser.add_argument('--quality', choices=('480P', '720P', '1080P'), help='仅 short，默认 720P')
    parser.add_argument('--megapixels', type=float, help='仅 long，直接传百万像素，默认 0.5')
    parser.add_argument('--aspect', choices=ASPECTS, help='short 默认 9:16；long 默认 16:9')
    parser.add_argument('--image', type=Path, action='append', default=[])
    parser.add_argument('--audio', type=Path, action='append', default=[])
    parser.add_argument('--video', type=Path)
    parser.add_argument('--steps', type=int, help='仅 short，默认 8；long 示例未声明步数节点')
    parser.add_argument('--node-map', type=Path, help='指定与所选 mode 应用 ID 一致的映射')
    args = parser.parse_args()
    if len(args.image) > 6 or len(args.audio) > 3:
        parser.error('最多 6 张图、3 段音频')
    if args.mode == 'long':
        if args.audio or args.video or args.steps is not None or args.quality is not None:
            parser.error('长视频示例未声明音频/视频参考或采样步数；画质请使用 --megapixels，不沿用短视频节点')
        seconds = args.seconds if args.seconds is not None else 35
        megapixels = args.megapixels if args.megapixels is not None else 0.5
        if seconds < 1 or not math.isfinite(megapixels) or megapixels <= 0:
            parser.error('长视频 seconds 须为正整数，megapixels 须为有限正数；线上范围仍须核实')
        aspect = args.aspect or '16:9'
    else:
        seconds = args.seconds if args.seconds is not None else 15
        steps = args.steps if args.steps is not None else 8
        if seconds not in range(5, 16) or steps < 1 or args.megapixels is not None:
            parser.error('短视频 seconds 须为 5–15，steps 须大于 0；长视频请显式选择 --mode long')
        aspect = args.aspect or '9:16'
    prompt = args.prompt_file.read_text(encoding='utf-8').strip()
    if not prompt:
        parser.error('提示词不能为空')
    map_path = args.node_map or (LONG_MAP if args.mode == 'long' else MAP)
    mapping = json.loads(map_path.read_text(encoding='utf-8'))
    if mapping.get('appId') != APP_IDS[args.mode]:
        parser.error('节点映射的应用 ID 不匹配')
    nodes = [{k: n[k] for k in ('nodeId', 'fieldName', 'fieldValue')}
             for n in mapping['nodeInfoList']]
    by_key = {(n['nodeId'], n['fieldName']): n for n in nodes}

    def set_value(node_id, field, value):
        if (node_id, field) not in by_key:
            parser.error('节点映射已变化，须核对当前应用接口后更新构造器')
        by_key[(node_id, field)]['fieldValue'] = str(value)

    def media(node_id, field, path):
        path = path.expanduser().resolve()
        if not path.is_file() or path.stat().st_size > 30 * 1024 * 1024:
            parser.error('素材不存在或超过 30MB：' + str(path))
        by_key[(node_id, field)]['fieldValue'] = {'$upload': str(path)}

    # Do not inherit someone else's uploaded assets or active optional LoRA.
    for node in nodes:
        if node['fieldName'] in ('image', 'audio'):
            node['fieldValue'] = 'None'
    if args.mode == 'long':
        set_value('59', 'prompt', prompt)
        set_value('291', 'value', seconds)
        set_value('426', 'megapixels', megapixels)
        set_value('426', 'aspect_ratio', ASPECTS[aspect])
        for node_id in ('446', '444', '443'):
            set_value(node_id, 'strength_model', '0')
        set_value('442', 'text', '')
        image_nodes = ('28', '273', '285', '436', '462', '463')
    else:
        set_value('150', 'value', prompt)
        set_value('186', 'value', seconds)
        set_value('147', 'value', {'480P': '0.4', '720P': '0.9', '1080P': '2.0'}[args.quality or '720P'])
        set_value('115', 'aspect_ratio', ASPECTS[aspect])
        set_value('192', 'value', steps)
        set_value('159', 'strength_model', '0')
        for node_id in ('171', '163', '185', '169', '158'):
            set_value(node_id, 'value', 'false')
        image_nodes = ('141', '142', '143', '161', '175', '176')
    for node_id, path in zip(image_nodes, args.image):
        media(node_id, 'image', path)
    for node_id, path in zip(('144', '160', '189'), args.audio):
        media(node_id, 'audio', path)
    if args.video:
        media('164', 'video', args.video)
        set_value('163', 'value', 'true')
    job = {'name': args.name, 'appId': mapping['appId'],
           'instanceType': mapping.get('instanceType', 'plus'),
           'usePersonalQueue': False, 'nodeInfoList': nodes}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump({'mapping_date': mapping.get('snapshot_date'), 'jobs': [job]},
                  stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print('已生成任务配置（未上传、未提交）：' + str(args.output))
    print('节点快照：' + str(mapping.get('snapshot_date')) + '；仍须核对当前应用与账户额度。')


if __name__ == '__main__':
    main()
