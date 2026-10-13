#!/usr/bin/env python3
"""Build a single H3 job from the dated real-node snapshot, without network calls."""
import argparse
import json
from pathlib import Path

MAP = Path(__file__).resolve().parents[1] / 'references/node_map.json'
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
    parser.add_argument('--seconds', type=int, default=15, choices=range(5, 16))
    parser.add_argument('--quality', default='720P', choices=('480P', '720P', '1080P'))
    parser.add_argument('--aspect', default='9:16', choices=ASPECTS)
    parser.add_argument('--image', type=Path, action='append', default=[])
    parser.add_argument('--audio', type=Path, action='append', default=[])
    parser.add_argument('--video', type=Path)
    parser.add_argument('--steps', type=int, default=8)
    parser.add_argument('--node-map', type=Path, default=MAP)
    args = parser.parse_args()
    if len(args.image) > 6 or len(args.audio) > 3 or args.steps < 1:
        parser.error('最多 6 张图、3 段音频；steps 须大于 0')
    prompt = args.prompt_file.read_text(encoding='utf-8').strip()
    if not prompt:
        parser.error('提示词不能为空')
    mapping = json.loads(args.node_map.read_text(encoding='utf-8'))
    if mapping.get('appId') != '2084320751339032577':
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
    set_value('150', 'value', prompt)
    set_value('186', 'value', args.seconds)
    set_value('147', 'value', {'480P': '0.4', '720P': '0.9', '1080P': '2.0'}[args.quality])
    set_value('115', 'aspect_ratio', ASPECTS[args.aspect])
    set_value('192', 'value', args.steps)
    set_value('159', 'strength_model', '0')
    for node_id in ('171', '163', '185', '169', '158'):
        set_value(node_id, 'value', 'false')
    for node_id, path in zip(('141', '142', '143', '161', '175', '176'), args.image):
        media(node_id, 'image', path)
    for node_id, path in zip(('144', '160', '189'), args.audio):
        media(node_id, 'audio', path)
    if args.video:
        media('164', 'video', args.video)
        set_value('163', 'value', 'true')
    job = {'name': args.name, 'instanceType': mapping.get('instanceType', 'plus'),
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
