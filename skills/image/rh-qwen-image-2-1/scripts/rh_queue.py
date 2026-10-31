"""Shared RunningHub quota protocol v1; identical helper shipped in both RH skills.

Local persistent reservations count remote tasks, including uncertain submissions.
No API key is stored. A private per-key digest selects the ledger, never logged.
"""
import contextlib
import fcntl
import hashlib
import json
import os
import tempfile
import time
from pathlib import Path

TERMINAL = {'SUCCESS', 'FAILED', 'CANCEL', 'CANCELLED', 'CANCELED'}


class Queue:
    def __init__(self, key, root=None):
        if not isinstance(key, str) or not key:
            raise ValueError('共享队列需要 RunningHub Key')
        self.root = Path(root or os.getenv('RH_QUEUE_DIR') or
                         '~/.local/state/runninghub/queue').expanduser()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.root.chmod(0o700)
        digest = hashlib.sha256(key.encode()).hexdigest()
        self.path = self.root/(digest+'.json')
        self.lock = self.root/(digest+'.lock')

    @contextlib.contextmanager
    def locked(self):
        fd = os.open(self.lock, os.O_CREAT | os.O_RDWR, 0o600)
        with os.fdopen(fd, 'a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            data = json.loads(self.path.read_text()) if self.path.exists() else {}
            if not isinstance(data, dict):
                raise RuntimeError('共享队列记录损坏，先核对远端任务，不自动清空')
            yield data
            descriptor, name = tempfile.mkstemp(prefix='.queue-', dir=self.root)
            try:
                with os.fdopen(descriptor, 'w') as output:
                    json.dump(data, output)
                os.replace(name, self.path)
            finally:
                if os.path.exists(name):
                    os.unlink(name)

    def snapshot(self):
        with self.locked() as data:
            return dict(data)

    def acquire(self, owner, wait=1200, query=None, cancelled=None):
        owner = str(owner)
        deadline = time.monotonic()+wait
        next_refresh = 0
        while True:
            if cancelled and cancelled():
                raise RuntimeError('批次已因结果不明暂停后续提交；当前任务未提交')
            with self.locked() as data:
                if owner in data:
                    raise RuntimeError('该任务已有队列预约；先恢复原任务，不重复提交')
                if len(data) < 3:
                    data[owner] = {'taskId': None}
                    return
                tasks = [item.get('taskId') for item in data.values() if item.get('taskId')]
            # Network reads happen outside the file lock. Never expire a running
            # reservation based on time or process death: remote work may continue.
            reclaimed = False
            if query and time.monotonic() >= next_refresh:
                next_refresh = time.monotonic()+10
                for task_id in set(tasks):
                    try:
                        status = str(query(task_id).get('status', '')).upper()
                    except Exception:
                        continue
                    if status in TERMINAL:
                        self.release(task_id=task_id)
                        reclaimed = True
            if reclaimed:
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError('同一 Key 的3个名额已占用；未提交此任务。已知任务可 resume，结果不明的提交须先核对平台记录')
            time.sleep(min(0.1, max(0, deadline-time.monotonic())))

    def bind(self, owner, task_id):
        with self.locked() as data:
            if str(owner) not in data:
                raise RuntimeError('缺少提交预约，保留 taskId 并恢复查询')
            data[str(owner)]['taskId'] = str(task_id)

    def release(self, owner=None, task_id=None):
        with self.locked() as data:
            for name in list(data):
                if (owner is not None and name == str(owner)) or (
                        task_id is not None and data[name].get('taskId') == str(task_id)):
                    del data[name]

    def recover(self, owner, task_id):
        """Attach an independently verified taskId to an uncertain reservation."""
        with self.locked() as data:
            if str(owner) in data:
                data[str(owner)]['taskId'] = str(task_id)

    def track(self, owner, task_id):
        """Count an already existing remote task while resuming; never submits."""
        with self.locked() as data:
            if not any(item.get('taskId') == str(task_id) for item in data.values()):
                data[str(owner)] = {'taskId': str(task_id)}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='恢复结果不明的共享预约；taskId 必须已在平台核实')
    parser.add_argument('--receipt', required=True, type=Path)
    parser.add_argument('--task-id', required=True)
    args = parser.parse_args()
    # Each package already knows how to read its shared private credential.
    try:
        from credentials import configured_api_key
        key = configured_api_key()
    except ImportError:
        from rh_qwen import configured_key
        key = configured_key()
    Queue(key).recover(str(args.receipt.expanduser().resolve()), args.task_id)
    print('已关联核实的 taskId；继续 resume 查询，终态才释放名额。')
