#!/usr/bin/env python3
"""RH Qwen Image 2.1: preview, submit once, resume and download all images."""
import argparse
import json
import mimetypes
import os
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from PIL import Image

APP_ID = '2101915284503654402'
BASE = 'https://www.runninghub.ai/openapi/v2'
IMAGE_NODES = ('420', '432', '433', '436', '435', '434')
QUALITIES = {'1K': '1000', '2K': '2000', '4K': '4000'}
ASPECTS = ('original', '1:1', '3:2', '4:3', '16:9', '2:3', '3:4', '9:16')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, data, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if exclusive:
        # Reserve the task name atomically, including across concurrent processes.
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
        return
    fd, temporary = tempfile.mkstemp(prefix='.qwen-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def configured_key():
    key = os.getenv('RUNNINGHUB_API_KEY', '').strip()
    if key:
        return key
    path = Path(os.getenv('RUNNINGHUB_ENV_FILE') or
                '~/.config/runninghub/.env').expanduser()
    if path.is_file():
        for line in path.read_text(encoding='utf-8').splitlines():
            name, separator, value = line.strip().removeprefix('export ').partition('=')
            if separator and name.strip() == 'RUNNINGHUB_API_KEY':
                return value.strip().strip('\"\'').strip()
    return ''


def validate(job, check_files=True):
    if not isinstance(job, dict):
        raise ValueError('job 必须是 JSON 对象')
    if not isinstance(job.get('prompt'), str) or not job['prompt'].strip():
        raise ValueError('prompt 不能为空')
    images = job.get('images')
    if not isinstance(images, list) or not 1 <= len(images) <= 6:
        raise ValueError('images 必须有 1–6 张参考图，按图1至图6排列')
    if any(not isinstance(p, str) or not p.strip() for p in images):
        raise ValueError('images 必须是非空文件路径')
    if type(job.get('count', 1)) is not int or job.get('count', 1) not in range(1, 5):
        raise ValueError('count 必须是 1–4 的整数')
    if job.get('quality', '2K') not in QUALITIES:
        raise ValueError('quality 必须是 1K、2K 或 4K')
    if job.get('aspect', '9:16') not in ASPECTS:
        raise ValueError('aspect 不支持；custom 缺少可验证宽高节点，暂不开放')
    if job.get('instance', 'default') not in ('default', 'plus', 'ultra'):
        raise ValueError('instance 必须是 default、plus 或 ultra')
    if check_files:
        for filename in images:
            path = Path(filename).expanduser()
            if not path.is_file() or path.stat().st_size > 30 * 1024 * 1024:
                raise ValueError('参考图必须存在且不超过 30 MiB')
            with Image.open(path) as image:
                image.verify()


def nodes(prompt, uploaded, aspect='9:16', quality='2K', count=1):
    result = [dict(nodeId=n, fieldName='image',
                   fieldValue=uploaded[i] if i < len(uploaded) else 'None', description=None)
              for i, n in enumerate(IMAGE_NODES)]
    for node, field, value in [('479', 'aspect_ratio', aspect),
                               ('481', 'value', QUALITIES[quality]),
                               ('482', 'value', str(count)), ('478', 'text', prompt.strip())]:
        result.append(dict(nodeId=node, fieldName=field, fieldValue=value, description=None))
    return result


class Client:
    def __init__(self, key):
        if not key:
            raise ValueError('未配置 RUNNINGHUB_API_KEY；参见 Skill 凭据说明')
        self.key = key

    def request(self, route, **kwargs):
        # No automatic POST retries, no credential forwarding via redirects.
        response = requests.post(BASE + route, headers={'Authorization': 'Bearer ' + self.key},
                                 timeout=(15, 90), allow_redirects=False, **kwargs)
        if not 200 <= response.status_code < 300:
            raise RuntimeError(f'RunningHub HTTP {response.status_code}')
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError('RunningHub 返回非对象响应')
        if data.get('code') not in (None, 0, '0', 200, '200'):
            raise RuntimeError('RunningHub 返回业务错误，请核对平台任务记录')
        if data.get('errorCode') not in (None, '', 0, '0') and data.get('status') != 'FAILED':
            raise RuntimeError('RunningHub 返回 errorCode，请核对平台任务记录')
        # Protect receipts if an upstream error happens to echo the token.
        return json.loads(json.dumps(data).replace(self.key, '[REDACTED]'))

    def upload(self, filename):
        path = Path(filename).expanduser()
        with path.open('rb') as stream:
            data = self.request('/media/upload/binary', files={
                'file': (path.name, stream, mimetypes.guess_type(path.name)[0] or 'application/octet-stream')})
        body = data.get('data') if isinstance(data.get('data'), dict) else data
        value = body.get('fileName') or body.get('download_url')
        if not value:
            raise RuntimeError('上传没有返回 fileName / download_url')
        return value

    def submit(self, payload):
        return self.request('/run/ai-app/' + APP_ID, json=payload)

    def query(self, task_id):
        return self.request('/query', json={'taskId': task_id})

    def download(self, url, destination):
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname:
            raise ValueError('结果 URL 必须为 HTTPS')
        destination = Path(destination)
        temporary = destination.with_suffix('.part')
        # Separate unauthenticated GET: never send the RH key to media hosts.
        try:
            with requests.get(url, stream=True, timeout=(15, 120)) as response:
                response.raise_for_status()
                with temporary.open('wb') as stream:
                    for chunk in response.iter_content(1024 * 1024):
                        stream.write(chunk)
            with Image.open(temporary) as image:
                image.load()
                info = {'width': image.width, 'height': image.height, 'format': image.format}
            os.replace(temporary, destination)
            return {'path': str(destination.resolve()), **info}
        finally:
            temporary.unlink(missing_ok=True)


def submit_once(client, state_path, payload, queue=None, wait=1200):
    owner = str(Path(state_path).resolve())
    if queue:
        queue.acquire(owner, wait=wait, query=client.query)
    record = {'appId': APP_ID, 'status': 'SUBMITTING', 'payload': payload}
    try:
        write_json(state_path, record, exclusive=True)
    except Exception:
        if queue:
            queue.release(owner=owner)  # No submit has happened yet.
        raise
    try:
        data = client.submit(payload)
        if not data.get('taskId'):
            raise RuntimeError('提交响应缺少 taskId')
    except Exception:
        record['status'] = 'SUBMIT_UNKNOWN'
        write_json(state_path, record)
        raise RuntimeError('提交结果不明；已锁定回执，先核对平台记录，禁止直接重提') from None
    record.update(taskId=str(data['taskId']), status=str(data.get('status', 'SUBMITTED')).upper(),
                  response=data)
    write_json(state_path, record)
    if queue:
        queue.bind(owner, record['taskId'])
    return record


def resume(client, state_path, max_wait, queue=None):
    record = read_json(state_path)
    if not record.get('taskId'):
        raise ValueError('回执无 taskId；先核对 RunningHub 任务/消费记录，不能重新提交')
    if queue:
        queue.track(str(Path(state_path).resolve()), record['taskId'])
    deadline = time.monotonic() + max_wait
    while True:
        data = client.query(record['taskId'])
        status = str(data.get('status', '')).upper()
        if not status:
            raise RuntimeError('查询响应缺少 status；保留回执，稍后 resume')
        record.update(status=status, response=data, usage=data.get('usage'))
        write_json(state_path, record)
        if queue and status in ('SUCCESS', 'FAILED', 'CANCEL', 'CANCELLED', 'CANCELED'):
            queue.release(task_id=record['taskId'])
        if status in ('FAILED', 'CANCEL', 'CANCELLED', 'CANCELED'):
            raise RuntimeError('远端任务失败/取消；详情见回执，不自动重提')
        if status == 'SUCCESS':
            break
        if time.monotonic() >= deadline:
            raise TimeoutError('等待超时，远端可能仍运行；用同一回执 resume')
        time.sleep(min(10, max(0, deadline - time.monotonic())))
    files = []
    for index, item in enumerate(data.get('results') or [], 1):
        url = item.get('url', '')
        extension = str(item.get('outputType', '')).lower().lstrip('.')
        if extension not in ('png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'avif'):
            extension = Path(urlsplit(url).path).suffix.lstrip('.').lower()
        if not url or extension not in ('png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'avif'):
            continue
        destination = Path(state_path).parent / f'{Path(state_path).stem}-{index:02d}.{extension}'
        files.append(client.download(url, destination))
        record['files'] = files
        write_json(state_path, record)
    if not files:
        raise RuntimeError('SUCCESS 但没有可验证图片；查看回执 results，不宣称已出图')
    return record


def prepare_job(job, base):
    if isinstance(job, dict) and isinstance(job.get('images'), list):
        job = dict(job)
        job['images'] = [str((base / Path(p).expanduser()).resolve())
                         if isinstance(p, str) and p.strip() else p for p in job['images']]
    validate(job)
    return job


def payload_for(job, uploaded):
    return dict(nodeInfoList=nodes(job['prompt'], uploaded, job.get('aspect', '9:16'),
                job.get('quality', '2K'), job.get('count', 1)),
                instanceType=job.get('instance', 'default'), usePersonalQueue='false')


def run_job(job, state, max_wait):
    from rh_queue import Queue
    if state.exists():
        raise FileExistsError('回执已存在，请 resume；新任务使用新回执名')
    client = Client(configured_key())
    queue = Queue(client.key)
    uploaded = [client.upload(p) for p in job['images']]
    record = submit_once(client, state, payload_for(job, uploaded), queue=queue, wait=max_wait)
    print(f'{state.name}: taskId=' + record['taskId'], flush=True)
    return resume(client, state, max_wait, queue=queue)


def run_batch(jobs, output, max_wait):
    names = [job.get('name', f'job-{i:03d}') for i, job in enumerate(jobs, 1)]
    if any(not isinstance(n, str) or not n or n in ('.', '..') or
           any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in n)
           for n in names) or len(set(names)) != len(names):
        raise ValueError('批量 name 必须唯一，仅含英文字母、数字、短横线或下划线')
    states = [output/(n+'.json') for n in names]
    if any(state.exists() for state in states):
        raise FileExistsError('批次回执已存在，请恢复原任务，不重复提交整批')
    results = []
    failures = []
    # Extra workers allow a newly free remote slot to refill while prior outputs download.
    with ThreadPoolExecutor(max_workers=min(8, len(jobs))) as pool:
        futures = {pool.submit(run_job, job, state, max_wait): name
                   for job, state, name in zip(jobs, states, names)}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as error:
                failures.append({'name': futures[future], 'errorType': type(error).__name__})
    if failures:
        raise RuntimeError('部分任务未成功，先检查各回执并逐项 resume：' + json.dumps(failures))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', nargs='?', type=Path, help='JSON：prompt, images, aspect, quality, count')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true', help='离线检查并打印预览（默认）')
    mode.add_argument('--submit', action='store_true', help='上传并提交一次收费任务')
    mode.add_argument('--resume', action='store_true', help='仅查询已有回执并下载')
    parser.add_argument('--state', type=Path, help='回执路径，也是输出文件所在目录')
    parser.add_argument('--output', type=Path, help='批量 jobs 的回执和输出目录')
    parser.add_argument('--task-id', help='resume 时恢复平台已核实的 taskId')
    parser.add_argument('--max-wait', type=int, default=1200)
    args = parser.parse_args()
    if args.max_wait < 0:
        parser.error('--max-wait 不能小于 0')
    if args.task_id and not args.resume:
        parser.error('--task-id 只能与 --resume 使用')
    if args.resume:
        if not args.state:
            parser.error('resume 需要 --state')
        client = Client(configured_key())
        from rh_queue import Queue
        queue = Queue(client.key)
        if args.task_id:
            if args.state.exists():
                parser.error('--task-id 需要新的回执路径，以保留旧记录')
            write_json(args.state, {'appId': APP_ID, 'taskId': args.task_id,
                                   'status': 'RECOVERED'}, exclusive=True)
        result = resume(client, args.state, args.max_wait, queue=queue)
    else:
        if not args.job:
            parser.error('需要 job JSON')
        job = read_json(args.job)
        if isinstance(job, dict) and 'jobs' in job:
            if not isinstance(job['jobs'], list) or not job['jobs']:
                parser.error('jobs 必须为非空数组')
            jobs = [prepare_job(item, args.job.resolve().parent) for item in job['jobs']]
            if args.state:
                parser.error('批量使用 --output，而不是 --state')
            if not args.submit:
                result = {'dryRun': True, 'appId': APP_ID, 'jobs': [payload_for(item,
                          [f'UPLOAD_SLOT_{i}' for i in range(1, len(item['images'])+1)]) for item in jobs]}
            else:
                if not args.output:
                    parser.error('批量 submit 需要 --output')
                result = run_batch(jobs, args.output.expanduser().resolve(), args.max_wait)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        # All image paths are relative to the job file, not the caller's cwd.
        if isinstance(job, dict) and isinstance(job.get('images'), list):
            job['images'] = [str((args.job.resolve().parent / Path(p).expanduser()).resolve())
                             if isinstance(p, str) and p.strip() else p for p in job['images']]
        validate(job)
        uploaded = [f'UPLOAD_SLOT_{i}' for i in range(1, len(job['images']) + 1)]
        payload = dict(nodeInfoList=nodes(job['prompt'], uploaded, job.get('aspect', '9:16'),
                       job.get('quality', '2K'), job.get('count', 1)),
                       instanceType=job.get('instance', 'default'), usePersonalQueue='false')
        if not args.submit:
            result = {'dryRun': True, 'appId': APP_ID, 'images': job['images'], 'payload': payload}
        else:
            if not args.state:
                parser.error('submit 需要新的 --state 回执路径')
            if args.state.exists():
                raise FileExistsError('回执已存在，请 resume；新生成任务使用新回执名')
            result = run_job(job, args.state, args.max_wait)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Do not echo arbitrary transport exceptions containing signed media URLs.
        print('错误：' + (str(error) if isinstance(error, (ValueError, RuntimeError, TimeoutError,
                                                         FileExistsError)) else type(error).__name__))
        raise SystemExit(1)
