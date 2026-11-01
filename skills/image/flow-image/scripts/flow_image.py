#!/usr/bin/env python3
"""Flow image generation through Chrome DevTools CLI's persistent f10 daemon."""
import argparse,fcntl,hashlib,json,os,re,shutil,ssl,subprocess,sys,time,urllib.request,uuid
from pathlib import Path
ROOT=Path(os.environ.get('FLOW_IMAGE_HOME',str(Path.home()/'.local/share/flow-devtools'))).expanduser()
CONFIG=json.loads((ROOT/'config.json').read_text()) if (ROOT/'config.json').exists() else {}
CLI=CONFIG.get('cli') or shutil.which('chrome-devtools') or 'chrome-devtools'
SESSION=CONFIG.get('session','f10')
PROJECT=CONFIG.get('project','')
PROJECT_URL='https://flow.google.com/project/'+PROJECT
PENDING=ROOT/'pending.json'

def run_cli(*args,as_json=True,timeout=90):
    command=[CLI,'--sessionId='+SESSION,*map(str,args)]
    if as_json:command.append('--output-format=json')
    r=subprocess.run(command,capture_output=True,text=True,timeout=timeout)
    if r.returncode:raise RuntimeError(re.sub(r'(?:https?|wss?)://\S+','[URL]',r.stderr or r.stdout)[:800])
    return json.loads(r.stdout) if as_json else r.stdout

def evaluate(page,source):
    result=run_cli('evaluate_script',source,'--pageId',page,'--waitForStableDom=false')
    if isinstance(result,dict) and 'result' in result:return result['result']
    text=result.get('message','') if isinstance(result,dict) else '\n'.join(str(x) for x in result)
    match=re.search(r'```json\s*([\s\S]*?)\s*```',text)
    if not match:raise RuntimeError('DevTools returned no script result')
    return json.loads(match.group(1))

def ensure_daemon():
    status=run_cli('status',as_json=False)
    if 'daemon is not running' in status:
        run_cli('start','--autoConnect','--headless=false','--isolated=false','--usageStatistics=false','--performanceCrux=false','--workspace='+str(ROOT),'--workspace='+str(Path.home()/'.codex/visualizations'),'--workspace='+str(Path.home()/'Desktop'),as_json=False)
        status=run_cli('status',as_json=False)
    if '1.12.0' not in status or not any(flag in status for flag in ['autoConnect','auto-connect']):raise RuntimeError('Flow daemon must use Chrome DevTools CLI 1.12.0 with autoConnect')
    return status

def page_id():
    result=run_cli('list_pages')
    pages=result.get('pages',[]) if isinstance(result,dict) else []
    matches=[p for p in pages if p.get('url','').split('?')[0].rstrip('/')==PROJECT_URL]
    if len(matches)!=1:raise RuntimeError('Open the fixed Flow project in your bahadir Chrome; no new browser or project was created')
    return matches[0]['id']

STATE_JS=r"""() => {
 const visible=e=>!!e.getClientRects().length;
 const buttons=[...document.querySelectorAll('button,[role=button]')].filter(visible);
 const trigger=buttons.find(e=>/Nano Banana/.test(e.innerText)&&/x[1-4]/.test(e.innerText));
 const editor=[...document.querySelectorAll('[contenteditable=true]')].find(visible);
 const account=[...document.querySelectorAll('[aria-label]')].some(e=>(e.getAttribute('aria-label')||'').includes(__EXPECTED_ACCOUNT__));
 return {url:location.origin+location.pathname,account_ok:account,model_text:trigger?.innerText||'',draft:editor?.innerText?.trim()||''};
}""".replace('__EXPECTED_ACCOUNT__',json.dumps(CONFIG.get('account','__unconfigured__')))
MEDIA_JS=r"""() => {
 const out=[];
 [...document.images].forEach((im,position)=>{
  const src=im.currentSrc||im.src||'';
  const m=/^https:\/\/flow-content\.google\/image\/([0-9a-f-]{36})(?:[?/#]|$)/i.exec(src);
  if(m)out.push({id:m[1],src,width:im.naturalWidth,height:im.naturalHeight,position});
 });
 return out;
}"""

def validate_state(state):
    if state.get('url')!=PROJECT_URL:raise ValueError('Unexpected Flow project')
    if not state.get('account_ok'):raise ValueError('The bahadir account is not verified on this Flow page')
    if not re.search(r'Nano Banana\s+2\.1(?![\d.])',state.get('model_text','')):raise ValueError('Select Nano Banana 2.1 in the Flow page before generating')
    if state.get('draft','').strip():raise ValueError('Flow contains an unfinished prompt; it was preserved')

def new_images(rows,baseline):
    first_old=min((r['position'] for r in rows if r['id'] in baseline),default=float('inf'))
    return [r for r in rows if r['id'] not in baseline and r['position']<first_old and r['width']>=512 and r['height']>=512]

def snapshot(page):return run_cli('take_snapshot',page,as_json=False)
def control(snapshot_text,role,name_pattern):
    matches=[]
    for line in snapshot_text.splitlines():
        m=re.search(r'uid=([^\s]+)\s+'+re.escape(role)+r'\s+"((?:\\.|[^"\\])*)"',line)
        if m and re.search(name_pattern,m.group(2)):matches.append(m.group(1))
    if len(matches)!=1:raise ValueError('Flow control is missing or ambiguous: '+name_pattern)
    return matches[0]

def choice(snapshot_text,name):
    for role in ('radio','button'):
        try:return control(snapshot_text,role,r'(?:^|\s)'+re.escape(name)+r'$')
        except ValueError:pass
    raise ValueError('Flow setting is missing: '+name)

def prepare(page,aspect):
    state=evaluate(page,STATE_JS);validate_state(state)
    snap=snapshot(page)
    # Clear leftover reference chips only when there is no unfinished prompt.
    try:clear=control(snap,'button',r'^清除提示$|^Clear prompt$')
    except ValueError:clear=None
    if clear:run_cli('click',page,clear);snap=snapshot(page)
    try:choice(snap,aspect);panel_open=True
    except ValueError:panel_open=False
    if not panel_open:
        trigger=control(snap,'button',r'^设置触发器$|^Settings')
        run_cli('click',page,trigger);snap=snapshot(page)
    ratio=choice(snap,aspect)
    run_cli('click',page,ratio);snap=snapshot(page)
    count=choice(snap,'x1')
    run_cli('click',page,count)
    run_cli('press_key',page,'Escape')
    validate_state(evaluate(page,STATE_JS))
    return snapshot(page)

REFS_JS=r"""() => [...document.querySelectorAll('button[aria-label="素材"],button[aria-label="Asset"]')]
 .filter(e=>e.getClientRects().length).map(e=>({busy:e.getAttribute('aria-busy')==='true',width:e.querySelector('img')?.naturalWidth||0,height:e.querySelector('img')?.naturalHeight||0}))"""

ERRORS_JS="() => [...document.querySelectorAll('.error-tile')].filter(e=>e.getClientRects().length).length"

def has_new_failure(current,baseline):return current>baseline

def references_ready(rows,expected=1):
    return expected>0 and len(rows)==expected and all(not r['busy'] and r['width']>0 and r['height']>0 for r in rows)

def validate_reference(path):
    if not path.is_absolute() or not path.is_file():raise ValueError('Reference must be an existing absolute file path')
    with path.open('rb') as f:header=f.read(16)
    if header.startswith(b'\xff\xd8\xff'):return '.jpg'
    if header.startswith(b'\x89PNG\r\n\x1a\n'):return '.png'
    if header.startswith(b'RIFF') and header[8:12]==b'WEBP':return '.webp'
    raise ValueError('Reference must contain a JPEG, PNG or WebP image')

def attach_reference(page,path,expected_count=1):
    suffix=validate_reference(path)
    stage_dir=ROOT/'uploads';stage_dir.mkdir(exist_ok=True)
    staged=stage_dir/('flow-ref-'+uuid.uuid4().hex+suffix)
    shutil.copyfile(path,staged)
    try:
        run_cli('click',page,control(snapshot(page),'button',r'^在提示框中添加素材$|^Add assets'))
        run_cli('upload_file',page,control(snapshot(page),'button',r'^上传媒体内容$|^Upload media$'),staged)
        deadline=time.monotonic()+120
        while time.monotonic()<deadline:
            snap=snapshot(page)
            try:uid=control(snap,'option',r'^'+re.escape(staged.name)+r' (?:图片|Image)$')
            except ValueError:time.sleep(2);continue
            run_cli('click',page,uid)
            run_cli('click',page,control(snapshot(page),'button',r'^添加到提示$|^Add to prompt$'))
            break
        else:raise TimeoutError('Reference upload did not complete; no generation was submitted')
        while time.monotonic()<deadline:
            if references_ready(evaluate(page,REFS_JS),expected_count):return
            time.sleep(2)
        raise TimeoutError('The reference chip did not become ready; no generation was submitted')
    finally:
        staged.unlink(missing_ok=True)

def download(url,requested):
    if not url.startswith('https://flow-content.google/image/'):raise ValueError('Unexpected image host')
    ctx=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
    try:
        with urllib.request.urlopen(url,context=ctx,timeout=120) as response:blob=response.read(40000000)
    except Exception as exc:raise RuntimeError('Image download failed: '+type(exc).__name__) from None
    if blob.startswith(b'\xff\xd8\xff'):suffix='.jpg'
    elif blob.startswith(b'\x89PNG\r\n\x1a\n'):suffix='.png'
    elif blob.startswith(b'RIFF') and blob[8:12]==b'WEBP':suffix='.webp'
    else:raise ValueError('Flow returned no supported image file')
    output=requested.with_suffix(suffix);output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('xb') as f:f.write(blob)
    return output

def generate(prompt,output,aspect,reference=None):
    if not prompt.strip():raise ValueError('Prompt must not be empty')
    if not output.is_absolute():raise ValueError('Use an absolute output path')
    if any(output.with_suffix(s).exists() for s in ['.jpg','.png','.webp']):raise FileExistsError('Output already exists')
    if PENDING.exists():raise RuntimeError('An earlier submitted job is unresolved; inspect the Flow project before retrying')
    references=[] if reference is None else ([reference] if isinstance(reference,Path) else list(reference))
    for path in references:validate_reference(path)
    daemon=ensure_daemon();page=page_id();run_cli('select_page',page)
    snap=prepare(page,aspect)
    for count,path in enumerate(references,start=1):
        attach_reference(page,path,expected_count=count)
    if references:snap=snapshot(page)
    baseline={r['id'] for r in evaluate(page,MEDIA_JS)}
    editor=control(snap,'textbox',r'您希望创作什么|What do you want|Describe|Create')
    run_cli('fill',page,editor,prompt)
    if references and not references_ready(evaluate(page,REFS_JS),len(references)):
        raise ValueError('Reference disappeared before submission; request was not submitted')
    # Persist before the only submit gesture; never auto-resubmit on timeout.
    request={'request_id':uuid.uuid4().hex,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'project':PROJECT,'model':'Nano Banana 2.1','output':str(output),'baseline':sorted(baseline),'baseline_errors':evaluate(page,ERRORS_JS),'submitted_at':time.time()}
    request['mode']='image-to-image' if references else 'text-to-image'
    request['reference_count']=len(references)
    if references:request['reference_sha256']=[hashlib.sha256(path.read_bytes()).hexdigest() for path in references]
    PENDING.write_text(json.dumps(request,ensure_ascii=False)+'\n')
    run_cli('press_key',page,'Enter')
    deadline=time.monotonic()+240
    while time.monotonic()<deadline:
        rows=new_images(evaluate(page,MEDIA_JS),baseline)
        if rows:
            selected=rows[0];actual=download(selected['src'],output)
            result={'ok':True,'mode':request['mode'],'reference_count':len(references),'output':str(actual),'media_id':selected['id'],'width':selected['width'],'height':selected['height'],'model':'Nano Banana 2.1','project':PROJECT,'page_id':page,'daemon_pid':int(re.search(r'pid=(\d+)',daemon).group(1)),'elapsed_seconds':round(time.time()-request['submitted_at'])}
            with (ROOT/'history.jsonl').open('a') as f:f.write(json.dumps({**request,**result},ensure_ascii=False)+'\n')
            PENDING.unlink();return result
        if has_new_failure(evaluate(page,ERRORS_JS),request['baseline_errors']):
            with (ROOT/'history.jsonl').open('a') as f:
                f.write(json.dumps({**request,'ok':False,'terminal_state':'failed','error':'Flow displayed a new failed image tile; no automatic retry'},ensure_ascii=False)+'\n')
            PENDING.unlink()
            raise RuntimeError('Flow reported that image generation failed; request recorded as failed, not retried')
        time.sleep(3)
    raise TimeoutError('Submitted to Flow but no finished image was identified; the request was not retried')

def main():
    os.umask(0o077);ROOT.mkdir(parents=True,exist_ok=True);ROOT.chmod(0o700)
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('status');sub.add_parser('stop')
    image=sub.add_parser('image');image.add_argument('prompt');image.add_argument('--output','-o',required=True);image.add_argument('--aspect',choices=['1:1','16:9','9:16','4:3','3:4'],default='1:1')
    image.add_argument('--ref',action='append',default=[],type=lambda v:Path(v).expanduser(),help='Absolute JPEG/PNG/WebP reference image; repeat for multiple images in order')
    args=parser.parse_args()
    try:
        if not CONFIG.get('project') or not CONFIG.get('account'):raise ValueError('Configure project and account in FLOW_IMAGE_HOME/config.json first')
        with (ROOT/'generation.lock').open('w') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if args.command=='image':result=generate(args.prompt,Path(args.output).expanduser(),args.aspect,args.ref)
            elif args.command=='stop':result={'ok':True,'status':run_cli('stop',as_json=False)}
            else:
                status=ensure_daemon();page=page_id();state=evaluate(page,STATE_JS)
                result={'ok':True,'status':status,'state':state,'pending_job':PENDING.exists()}
        print(json.dumps(result,ensure_ascii=False));return 0
    except Exception as exc:
        print(json.dumps({'ok':False,'error_type':type(exc).__name__,'error':str(exc)[:1200],'may_have_submitted':PENDING.exists()},ensure_ascii=False),file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
