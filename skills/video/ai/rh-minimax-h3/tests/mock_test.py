import json, os, subprocess, sys, threading, time, shutil, tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MODE = {'run': 'ok', 'query': 'success', 'file': 'video'}
STATE = {'runs': 0, 'queries': 0, 'inflight': 0, 'peak': 0, 'apps': [], 'payloads': []}
LOCK = threading.Lock()
MP4 = open(__import__('pathlib').Path(__file__).resolve().parent/'real.mp4','rb').read()

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, obj, code=200, ctype='application/json'):
        body = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(code); self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if MODE['file'] == 'video': self._send(MP4, ctype='video/mp4')
        elif MODE['file'] == 'empty': self._send(b'', ctype='video/mp4')
        else: self._send(b'PK\x03\x04zipdata', ctype='application/zip')
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0)); raw = self.rfile.read(n)
        if self.path.endswith('/media/upload/binary'):
            return self._send({'code': 0, 'data': {'fileName': 'openapi/up.png'}})
        if '/run/ai-app/' in self.path:
            with LOCK:
                STATE['runs'] += 1; STATE['inflight'] += 1; STATE['peak'] = max(STATE['peak'], STATE['inflight'])
                STATE['apps'].append(self.path.rsplit('/', 1)[-1])
                STATE['payloads'].append(json.loads(raw))
            if MODE['run'] == 'hang': time.sleep(3)
            if MODE['run'] == 'notaskid': return self._send({'status': 'RUNNING'})
            return self._send({'taskId': f"T{STATE['runs']}", 'status': 'RUNNING'})
        if self.path.endswith('/query'):
            STATE['queries'] += 1
            tid = json.loads(raw)['taskId']
            if MODE['query'] == 'error':
                return self._send({'message': 'temporary failure'}, 503)
            if MODE['query'] == 'never':
                return self._send({'taskId': tid, 'status': 'RUNNING'})
            with LOCK: STATE['inflight'] = max(0, STATE['inflight'] - 1)
            return self._send({'taskId': tid, 'status': 'SUCCESS', 'usage': {'consumeCoins': '1'},
                               'results': [{'url': f'http://127.0.0.1:{PORT}/f.mp4', 'outputType': 'mp4'}]})
        self._send({}, 404)

srv = ThreadingHTTPServer(('127.0.0.1', 0), H); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

HERE = Path(__file__).resolve().parent.parent
def run(args, **env):
    e = {**os.environ, 'RUNNINGHUB_API_KEY': 'testkey', 'RUNNINGHUB_BASE_URL': f'http://127.0.0.1:{PORT}',
         'RH_POLL_SECONDS': '0.2', **env}
    return subprocess.run([sys.executable, str(HERE / 'scripts/rh_minimax_h3.py'), *args], capture_output=True, text=True, env=e, timeout=60)

def jobs(tmp, n=1, node='150', field='value', prefix='j'):
    p = tmp / 'jobs.json'
    p.write_text(json.dumps({'jobs': [{'name': f'{prefix}{i}', 'nodeInfoList': [
        {'nodeId': node, 'fieldName': field, 'fieldValue': 'hi'}]} for i in range(n)]}))
    return str(p)

ok = True
def check(label, cond, extra=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + label, extra if not cond else '')
    ok &= bool(cond)

def reset(**m):
    MODE.update({'run': 'ok', 'query': 'success', 'file': 'video'}); MODE.update(m)
    STATE.update(runs=0, queries=0, inflight=0, peak=0, apps=[], payloads=[])

# 1 dry-run rejects placeholders, makes no requests
t = Path(tempfile.mkdtemp()); reset()
r = run([jobs(t, node='<真实节点ID>'), '--dry-run', '--output', str(t / 'o')])
check('placeholder rejected', r.returncode != 0 and '占位符' in (r.stderr + r.stdout), r.stderr)
check('placeholder: no request', STATE['runs'] == 0)
# 2 dry-run ok, no upload/submit, no key needed
r = run([jobs(t), '--dry-run', '--output', str(t / 'o')], RUNNINGHUB_API_KEY='')
check('dry-run passes without submitting', r.returncode == 0 and 'dry-run 通过' in r.stdout and STATE['runs'] == 0, r.stderr)
# 3 normal success
reset(); t = Path(tempfile.mkdtemp())
r = run([jobs(t), '--output', str(t / 'o')])
check('success path', r.returncode == 0 and STATE['runs'] == 1, r.stdout + r.stderr)
rec = json.loads((t / 'o' / 'j0_submitting.json').read_text())
chk=json.loads(next((t/'o').glob('j0_T*.json')).read_text()); check('ffprobe info recorded', any(v.get('width')==64 and v.get('duration',0)>0 for v in chk['checks'].values()), chk.get('checks'))
check('pending record has payload, no key', rec['status'] == 'DONE' and 'testkey' not in json.dumps(rec) and rec['payload']['nodeInfoList'])
check('legacy jobs keep short app and default to plus', rec['appId'] == '2084320751339032577' and
      STATE['apps'] == ['2084320751339032577'] and rec['payload']['instanceType'] == 'plus')
# 4 resubmit same name after DONE allowed; but open state refused
r = run([jobs(t), '--output', str(t / 'o')]); check('rerun after DONE allowed', r.returncode == 0)
# Mixed batches dispatch each job to its selected app; legacy jobs remain compatible.
reset(); t = Path(tempfile.mkdtemp())
mixed = t/'mixed.json'
mixed.write_text(json.dumps({'jobs': [
    {'name': 'short', 'nodeInfoList': [{'nodeId':'150', 'fieldName':'value', 'fieldValue':'a ceramic cup'}]},
    {'name': 'long', 'appId':'2103012816681041921', 'instanceType':'default', 'usePersonalQueue':False,
     'nodeInfoList': [{'nodeId':'59', 'fieldName':'prompt', 'fieldValue':'a ceramic cup'}]},
]}))
r = run([str(mixed), '--output', str(t/'o')])
check('mixed short/long endpoint routing', r.returncode == 0 and
      sorted(STATE['apps']) == ['2084320751339032577', '2103012816681041921'], r.stdout+r.stderr)
long_receipt = json.loads((t/'o'/'long_submitting.json').read_text())
check('long app identity saved outside API payload', long_receipt['appId'] == '2103012816681041921' and
      long_receipt['payload']['nodeInfoList'][0]['nodeId'] == '59' and
      long_receipt['payload']['instanceType'] == 'default' and
      all('appId' not in p for p in STATE['payloads']))
reset(); unknown = t/'unknown.json'
unknown.write_text(json.dumps({'jobs':[{'name':'unknown','appId':'unregistered',
    'nodeInfoList':[{'nodeId':'59','fieldName':'prompt','fieldValue':'a ceramic cup'}]}]}))
r = run([str(unknown), '--dry-run', '--output', str(t/'unused')])
check('unknown app rejected before network', r.returncode != 0 and STATE['runs'] == 0 and
      'appId' in r.stdout+r.stderr and not (t/'unused').exists())
# 5 submit timeout => UNKNOWN, no retry, then refused next time
reset(run='hang'); t = Path(tempfile.mkdtemp())
r = run([jobs(t), '--output', str(t / 'o')], RH_SUBMIT_READ_TIMEOUT='0.5')
rec = json.loads((t / 'o' / 'j0_submitting.json').read_text())
check('submit timeout -> SUBMIT_UNKNOWN', r.returncode != 0 and rec['status'] == 'SUBMIT_UNKNOWN' and '结果不明' in r.stdout + r.stderr, r.stdout + r.stderr)
time.sleep(3.5); runs_before = STATE['runs']
reset(); r = run([jobs(t), '--output', str(t / 'o')])
check('unknown state blocks resubmit', r.returncode != 0 and STATE['runs'] == 0 and '拒绝重复提交' in r.stdout + r.stderr, r.stdout + r.stderr)
# 6 no taskId => unknown
reset(run='notaskid'); t = Path(tempfile.mkdtemp())
r = run([jobs(t), '--output', str(t / 'o')])
rec = json.loads((t / 'o' / 'j0_submitting.json').read_text())
check('no taskId -> SUBMIT_UNKNOWN', rec['status'] == 'SUBMIT_UNKNOWN')
# 7 query timeout: remaining queued jobs not submitted (5 jobs, 3 workers)
reset(query='never'); t = Path(tempfile.mkdtemp())
r = run([jobs(t, n=5), '--output', str(t / 'o'), '--max-wait', '1'])
check('query timeout halts new submissions', STATE['runs'] == 3 and r.returncode != 0 and '--resume' in r.stdout + r.stderr, f"runs={STATE['runs']} " + r.stdout + r.stderr)
check('peak in-flight <= 3', STATE['peak'] <= 3, STATE['peak'])
# 8 --resume downloads without submitting
reset(); t = Path(tempfile.mkdtemp())
r = run(['--resume', 'T99', '--name', 'x', '--output', str(t / 'o')])
check('resume downloads, no submit', r.returncode == 0 and STATE['runs'] == 0 and list((t / 'o').glob('x_T99_1.mp4')), r.stdout + r.stderr)
# 9 fake header
reset(file='zip')
# 9b non-video output => not success
reset(file='zip'); t = Path(tempfile.mkdtemp())
r = run([jobs(t), '--output', str(t / 'o')])
# server serves zip bytes but outputType mp4 -> header check fails
check('fake video rejected', r.returncode != 0 and '没有通过验收的视频' in r.stdout + r.stderr, r.stdout + r.stderr)
reset(file='empty'); t = Path(tempfile.mkdtemp())
r = run([jobs(t), '--output', str(t / 'o')])
check('empty file rejected', r.returncode != 0 and '没有通过验收的视频' in r.stdout + r.stderr)
# Query errors preserve pending state and stop queued submissions.
reset(query='error'); t = Path(tempfile.mkdtemp())
r = run([jobs(t, n=5), '--output', str(t / 'o')])
records = [json.loads(p.read_text()) for p in (t/'o').glob('*_submitting.json')]
check('query transport error preserves SUBMITTED', r.returncode != 0 and records and
      all(p['status'] == 'SUBMITTED' for p in records) and STATE['runs'] <= 3)
reset()
r = run([jobs(t, n=5), '--output', str(t / 'o')])
# Same unresolved names cannot be submitted again, even if service comes back.
check('query error prevents same-name resubmit', r.returncode != 0 and '拒绝重复提交' in r.stdout+r.stderr)
# Resume success updates the original matching pending receipt.
reset(); t = Path(tempfile.mkdtemp())
(t/'o').mkdir()
pending = t/'o'/'x_submitting.json'
pending.write_text(json.dumps({'name':'x', 'taskId':'T99', 'status':'SUBMITTED'}))
r = run(['--resume','T99','--name','x','--output',str(t/'o')])
check('resume clears matching pending state', r.returncode == 0 and
      json.loads(pending.read_text())['status'] == 'DONE' and STATE['runs'] == 0)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
