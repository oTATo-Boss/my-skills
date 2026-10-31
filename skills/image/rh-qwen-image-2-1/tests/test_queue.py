"""Offline tests of both skills' shared, cross-process RunningHub quota."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
H3_SCRIPTS = Path(__file__).resolve().parents[3]/'video/ai/rh-minimax-h3/scripts'


def load(path):
    spec = importlib.util.spec_from_file_location('quota_test', path/'rh_queue.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QueueTests(unittest.TestCase):
    def test_two_skills_share_three_slots_and_unknown_stays_reserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            q = load(SCRIPTS).Queue('offline-key', root=tmp)
            h = load(H3_SCRIPTS).Queue('offline-key', root=tmp)
            self.assertEqual((SCRIPTS/'rh_queue.py').read_bytes(), (H3_SCRIPTS/'rh_queue.py').read_bytes())
            for owner in ('a', 'b', 'c'):
                q.acquire(owner, wait=0)
            with self.assertRaises(TimeoutError):
                h.acquire('d', wait=0)
            q.bind('a', 'task-a')
            # Only confirmed terminal tasks are reclaimed; unknown b/c persist.
            h.acquire('d', wait=0, query=lambda tid: {'status': 'SUCCESS'})
            self.assertEqual(len(q.snapshot()), 3)
            self.assertIn('b', q.snapshot())
            self.assertNotIn('offline-key', q.path.read_text())
            with self.assertRaises(RuntimeError):
                h.acquire('cancelled', wait=10, cancelled=lambda: True)
            h.release(owner='d')
            other = load(SCRIPTS).Queue('another-key', root=tmp)
            other.acquire('independent', wait=0)
            self.assertEqual(len(other.snapshot()), 1)

    def test_five_processes_overlap_and_refill_before_all_finish(self):
        with tempfile.TemporaryDirectory() as tmp:
            worker = '''
import sys,time,json
sys.path.insert(0,sys.argv[1])
from rh_queue import Queue
q=Queue('offline-key',root=sys.argv[2]); owner=sys.argv[3]
q.acquire(owner,wait=10)
print(json.dumps({'event':'start','owner':owner,'at':time.monotonic()}),flush=True)
time.sleep(float(sys.argv[4]))
print(json.dumps({'event':'end','owner':owner,'at':time.monotonic()}),flush=True)
q.release(owner=owner)
'''
            processes=[]
            for i, delay in enumerate((0.35, 0.9, 0.9, 0.2, 0.2)):
                script_dir = SCRIPTS if i % 2 else H3_SCRIPTS
                processes.append(subprocess.Popen([sys.executable,'-c',worker,str(script_dir),tmp,str(i),str(delay)],
                                 stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
                                 env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'}))
            events=[]
            for process in processes:
                out,err=process.communicate(timeout=15)
                self.assertEqual(process.returncode,0,err)
                events.extend(json.loads(line) for line in out.splitlines())
            starts=sorted(e['at'] for e in events if e['event']=='start')
            ends=sorted(e['at'] for e in events if e['event']=='end')
            self.assertLess(starts[2], ends[0], 'first three must overlap')
            self.assertLess(starts[3], ends[2], 'refill before original batch finishes')
            # End print is just after the release, so allow matching near boundaries.
            peak=0;active=0
            for event in sorted(events,key=lambda e:e['at']):
                active += 1 if event['event']=='start' else -1
                peak=max(peak,active)
            self.assertLessEqual(peak,3)


if __name__=='__main__':
    unittest.main()
