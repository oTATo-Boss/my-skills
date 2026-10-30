#!/usr/bin/env python3
"""Apilio MJ executor. Python 3.10+, standard library; no automatic POST retries."""
import argparse
import base64
import contextlib
import fcntl
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request


class MJError(Exception):
    pass


class HTTPFailure(MJError):
    def __init__(self, status):
        self.status = status
        super().__init__(f'HTTP {status}')


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_json(path):
    return json.loads(Path(path).read_text())


def task_id(value):
    value = str(value)
    if not re.fullmatch(r'[A-Za-z0-9_-]+', value):
        raise MJError('Invalid task ID')
    return value


def secure_url(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.fragment:
        raise MJError('An HTTPS URL without credentials or fragments is required')
    return url


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def opener():
    ctx = ssl.create_default_context()
    # python.org macOS installations may lack a bundled CA store; use system CAs.
    if not os.environ.get('SSL_CERT_FILE') and Path('/etc/ssl/cert.pem').is_file():
        ctx.load_verify_locations('/etc/ssl/cert.pem')
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), NoRedirect())


class Client:
    def __init__(self, base, key, timeout=30):
        self.base = secure_url(base.rstrip('/'))
        if urllib.parse.urlsplit(self.base).query:
            raise MJError('API base must not contain a query')
        if not key:
            raise MJError('Set MJ_API_KEY (never pass a key on the command line)')
        self.key, self.timeout, self.http = key, timeout, opener()

    def request(self, method, path, body=None):
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode()
        req = urllib.request.Request(self.base + '/mj/' + path, data=data, method=method,
                                     headers={'Authorization': 'Bearer ' + self.key,
                                              'Content-Type': 'application/json'})
        try:
            with self.http.open(req, timeout=self.timeout) as res:
                raw = res.read(8 * 1024 * 1024 + 1)
            if len(raw) > 8 * 1024 * 1024:
                raise MJError('API response exceeds 8 MiB')
            result = json.loads(raw)
            if not isinstance(result, dict):
                raise MJError('API response is not an object')
            return result
        except urllib.error.HTTPError as e:
            raise HTTPFailure(e.code) from None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            # Do not print request headers, credentials, signed URLs or raw server HTML.
            raise MJError('Network/TLS failure or invalid JSON response') from None


class Store:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.ledger = self.root / 'operations.json'

    @contextlib.contextmanager
    def lock(self):
        with (self.root / '.lock').open('a') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def snapshot(self, tid, result):
        atomic_json(self.root / ('task-' + task_id(tid) + '.json'), result)

    def mutate(self, client, kind, body, op, max_posts):
        digest = hashlib.sha256(json.dumps([client.base, kind, body], sort_keys=True).encode()).hexdigest()
        with self.lock():
            ledger = read_json(self.ledger) if self.ledger.exists() else {}
            if op in ledger:
                entry = ledger[op]
                if entry['fingerprint'] != digest:
                    raise MJError('Operation key already used for different input; inspect operations.json')
                if entry.get('response'):
                    return entry['response']
                raise MJError('Submission outcome unknown. Recover from provider history; do not repeat POST')
            if len(ledger) >= max_posts:
                raise MJError('POST budget exhausted; expand only within the authorized task scope')
            # Persist intent before network I/O. A crash or lost response remains ambiguous.
            entry = {'fingerprint': digest, 'kind': kind, 'parent': body.get('taskId'),
                     'phase': 'pending', 'time': time.time()}
            ledger[op] = entry
            atomic_json(self.ledger, ledger)
            try:
                response = client.request('POST', 'submit/' + kind, body)
            except MJError as e:
                entry['phase'] = 'unknown'
                entry['error'] = str(e)
                atomic_json(self.ledger, ledger)
                raise MJError(str(e) + '; POST not retried. Inspect operations.json and provider history') from None
            entry['response'] = response
            entry['phase'] = 'modal' if response.get('code') == 21 else (
                'accepted' if response.get('code') in (1, 22) else 'rejected')
            tid = response.get('result')
            if response.get('code') in (1, 21, 22) and tid and kind != 'upload-discord-images':
                entry['task_id'] = task_id(tid)
            atomic_json(self.ledger, ledger)
            return response


def fetch(client, store, tid):
    tid = task_id(tid)
    result = client.request('GET', 'task/' + tid + '/fetch')
    if str(result.get('id', '')) != tid or not result.get('status'):
        raise MJError('Unexpected task response; check routing/authentication, do not resubmit')
    store.snapshot(tid, result)
    return result


def wait_task(client, store, tid, seconds, interval):
    deadline = time.monotonic() + seconds
    last = None
    while True:
        try:
            last = fetch(client, store, tid)
        except HTTPFailure as e:
            if e.status not in (408, 429, 500, 502, 503, 504) or time.monotonic() >= deadline:
                raise
        except MJError:
            # Only GET is retried; schema errors and connection errors remain bounded.
            if time.monotonic() >= deadline:
                raise
        if last and last.get('status') in ('SUCCESS', 'FAILURE', 'CANCEL', 'MODAL'):
            return last
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise MJError(f'Wait timed out; resume GET for task {tid}. No new submission needed')
        time.sleep(min(interval, remaining, 30))


def select_button(task, label=None, custom_id=None):
    if task.get('status') != 'SUCCESS':
        raise MJError('Action requires a completed source task')
    buttons = task.get('buttons') or []
    matches = [b for b in buttons if b.get('customId') and not b.get('disabled') and (
        b['customId'] == custom_id if custom_id else b.get('label') == label)]
    if len(matches) != 1:
        raise MJError('Button missing or ambiguous; inspect fresh buttons and select the exact returned customId')
    return matches[0]['customId']


def image_data(path):
    path = Path(path)
    mime = mimetypes.guess_type(str(path))[0]
    if mime not in ('image/png', 'image/jpeg', 'image/webp'):
        raise MJError('Local inputs must be PNG, JPEG or WebP')
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode()


def validate_body(kind, body):
    if not isinstance(body, dict):
        raise MJError('Payload must be a JSON object')
    required = {'imagine': ('prompt',), 'blend': ('base64Array',), 'describe': ('base64',),
                'shorten': ('prompt',), 'edits': ('prompt', 'image', 'maskBase64'),
                'action': ('taskId', 'customId'), 'modal': ('taskId',),
                'upload-discord-images': ('base64Array',)}
    for key in required[kind]:
        if not body.get(key):
            raise MJError(f'{kind} requires {key}')
        if key != 'base64Array' and not isinstance(body[key], str):
            raise MJError(f'{key} must be a string')
    if kind == 'blend':
        if not isinstance(body['base64Array'], list) or not 2 <= len(body['base64Array']) <= 5:
            raise MJError('Blend requires 2–5 images; recheck provider limits if changed')
        if body.get('dimensions', 'SQUARE') not in ('SQUARE', 'PORTRAIT', 'LANDSCAPE'):
            raise MJError('Invalid blend dimensions')


def verify_image(path):
    try:
        from PIL import Image
    except ImportError:
        raise MJError('Image verification requires Pillow; use an existing Python with Pillow or install it') from None
    with Image.open(path) as im:
        size, fmt = im.size, im.format
        im.verify()
    with Image.open(path) as im:
        im.load()
    if min(size) < 1:
        raise MJError('Invalid image dimensions')
    return {'width': size[0], 'height': size[1], 'format': fmt}


def publish_image(tmp, output):
    meta = verify_image(tmp)
    meta.update(bytes=Path(tmp).stat().st_size,
                sha256=hashlib.sha256(Path(tmp).read_bytes()).hexdigest())
    os.link(tmp, output)
    return dict(meta, path=str(output))


def download_image(url, output, http=None):
    secure_url(url)
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise MJError('Output exists; choose a new path')
    # Separate unauthenticated request: never forward the API bearer token to a CDN.
    http = http or opener()
    fd, tmp = tempfile.mkstemp(dir=output.parent)
    try:
        for _ in range(6):
            try:
                response = http.open(urllib.request.Request(url), timeout=30)
                break
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    # Some image relays reject urllib while accepting system curl.
                    # This GET has no API credentials and never creates a new task.
                    os.close(fd)
                    fd = None
                    try:
                        result = subprocess.run(
                            ['curl', '--fail', '--silent', '--show-error', '--location',
                             '--proto', '=https', '--proto-redir', '=https', '--max-time', '60',
                             '--max-filesize', str(100 * 1024 * 1024), '--output', tmp, '--', url],
                            capture_output=True, timeout=65)
                    except (OSError, subprocess.TimeoutExpired):
                        raise MJError('CDN curl fallback unavailable or timed out') from None
                    if result.returncode:
                        raise MJError('CDN curl fallback failed; preserve task ID and retry download only')
                    return publish_image(tmp, output)
                if e.code not in (301, 302, 303, 307, 308) or not e.headers.get('Location'):
                    raise MJError(f'Download HTTP {e.code}') from None
                url = secure_url(urllib.parse.urljoin(url, e.headers['Location']))
        else:
            raise MJError('Too many CDN redirects')
        with os.fdopen(fd, 'wb') as f, response:
            fd = None
            total = 0
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                total += len(block)
                if total > 100 * 1024 * 1024:
                    raise MJError('Image exceeds 100 MiB')
                f.write(block)
        return publish_image(tmp, output)
    finally:
        if fd is not None:
            os.close(fd)
        if os.path.exists(tmp):
            os.unlink(tmp)


def load_settings(base_override=None, config_path=None):
    """Explicit CLI > MJ env > shared APILIO env > private local config."""
    path = Path(config_path).expanduser() if config_path else Path.home() / '.config/apilio/credentials.json'
    config = {}
    if path.exists():
        if path.stat().st_mode & 0o077:
            raise MJError('Apilio configuration must have mode 0600')
        try:
            config = read_json(path)
        except (OSError, ValueError):
            raise MJError('Cannot read Apilio private configuration') from None
        if not isinstance(config, dict):
            raise MJError('Apilio configuration must be an object')
    base = base_override or os.environ.get('MJ_BASE_URL') or os.environ.get('APILIO_BASE_URL') or config.get('mj_base_url') or config.get('base_url')
    key = os.environ.get('MJ_API_KEY') or os.environ.get('APILIO_API_KEY') or config.get('api_key')
    if not isinstance(base, str) or not base:
        raise MJError('Configure the provider base before /mj in local Apilio config or MJ_BASE_URL')
    if not isinstance(key, str) or not key:
        raise MJError('Configure the API key in local Apilio config or MJ_API_KEY')
    return base, key


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-url', help='Override base before /mj; may include /mj-fast etc.')
    p.add_argument('--config', help='Private Apilio JSON config; default ~/.config/apilio/credentials.json')
    p.add_argument('--state-dir', default='.mj-state', help='One private directory per workflow')
    p.add_argument('--max-posts', type=int, default=2, help='Total attempted mutations in this workflow, including modal')
    sub = p.add_subparsers(dest='command', required=True)
    for name in ('submit', 'action', 'modal'):
        q = sub.add_parser(name)
        q.add_argument('--op', required=True, help='Stable operation name for restart protection')
        q.add_argument('--payload', help='JSON file, never shell JSON or a credential file')
        q.add_argument('--image', action='append', default=[], help='Local image; repeat for imagine/blend')
        q.add_argument('--mask', help='Local PNG mask (black preserve, white edit for modal)')
        if name == 'submit':
            q.add_argument('kind', choices=['imagine', 'blend', 'describe', 'shorten', 'edits', 'upload-discord-images'])
        else:
            q.add_argument('--task-id', required=True)
        if name == 'action':
            g = q.add_mutually_exclusive_group(required=True)
            g.add_argument('--label')
            g.add_argument('--custom-id')
    for name in ('fetch', 'wait', 'buttons', 'download'):
        q = sub.add_parser(name)
        q.add_argument('task_id')
        if name == 'wait':
            q.add_argument('--seconds', type=float, default=600)
            q.add_argument('--interval', type=float, default=5)
        if name == 'download':
            q.add_argument('--output', required=True)
    q = sub.add_parser('verify')
    q.add_argument('path')
    return p


def run(args):
    if args.command == 'verify':
        return verify_image(args.path)
    base, key = load_settings(args.base_url, args.config)
    client = Client(base, key)
    store = Store(args.state_dir)
    if args.command in ('submit', 'action', 'modal'):
        body = read_json(args.payload) if args.payload else {}
        if not isinstance(body, dict):
            raise MJError('Payload must be an object')
        kind = args.kind if args.command == 'submit' else args.command
        images = [image_data(path) for path in args.image]
        if images:
            if kind in ('imagine', 'blend', 'upload-discord-images'):
                body['base64Array'] = images
            elif kind == 'describe' and len(images) == 1:
                body['base64'] = images[0]
            else:
                raise MJError('For edits supply the documented remote image URL in payload.image')
        if args.mask:
            body['maskBase64'] = image_data(args.mask)
        if kind in ('action', 'modal'):
            body['taskId'] = task_id(args.task_id)
            if kind == 'action':
                task = fetch(client, store, args.task_id)
                body['customId'] = select_button(task, args.label, args.custom_id)
            else:
                task = fetch(client, store, args.task_id)
                if task['status'] != 'MODAL':
                    # Known completed operation may be replayed below; fresh modal is checked in mutate.
                    ledger = read_json(store.ledger) if store.ledger.exists() else {}
                    if args.op not in ledger:
                        raise MJError('Modal requires the pending ID returned by code=21/status=MODAL')
        validate_body(kind, body)
        response = store.mutate(client, kind, body, args.op, args.max_posts)
        code, tid = response.get('code'), response.get('result')
        if kind == 'upload-discord-images':
            if code != 1 or not isinstance(tid, list) or not tid:
                raise MJError('Upload rejected; inspect operations.json')
            return {'urls': [secure_url(u) for u in tid]}
        if code not in (1, 21, 22) or not tid:
            raise MJError(f'Submission rejected/invalid: code={code}; inspect private operations.json for description')
        return {'code': code, 'task_id': str(tid), 'needs_modal': code == 21,
                'state_dir': str(store.root.resolve())}
    tid = task_id(args.task_id)
    if args.command == 'wait':
        if args.seconds <= 0 or args.interval <= 0:
            raise MJError('Wait seconds and interval must be positive')
        task = wait_task(client, store, tid, args.seconds, args.interval)
    else:
        task = fetch(client, store, tid)
    if args.command == 'buttons':
        return {'task_id': tid, 'status': task['status'], 'buttons': task.get('buttons', [])}
    if args.command == 'download':
        if task['status'] != 'SUCCESS' or not task.get('imageUrl'):
            raise MJError('Download requires SUCCESS and imageUrl; describe/shorten may return text only')
        meta = download_image(task['imageUrl'], args.output)
        atomic_json(str(args.output) + '.json', dict(meta, task_id=tid, action=task.get('action')))
        return meta
    # Full text results, errors, URLs and prompts remain in private snapshots.
    return {'task_id': tid, 'status': task['status'], 'progress': task.get('progress'),
            'snapshot': str((store.root / ('task-' + tid + '.json')).resolve())}


def main():
    os.umask(0o077)
    args = parser().parse_args()
    try:
        result = run(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result.get('status') in ('FAILURE', 'CANCEL'):
            return 2
        if result.get('status') == 'MODAL' or result.get('needs_modal'):
            return 3
        return 0
    except (MJError, OSError, ValueError) as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
