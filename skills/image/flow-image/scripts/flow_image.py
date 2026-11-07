#!/usr/bin/env python3
"""Flow image generation through Chrome DevTools CLI's persistent f10 daemon."""
import argparse,base64,contextlib,fcntl,hashlib,json,os,re,shutil,ssl,subprocess,sys,tempfile,time,urllib.parse,urllib.request,uuid
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
        if active_jobs():raise RuntimeError('Unfinished jobs depend on the previous daemon; do not restart it automatically')
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
IMAGE_ID_JS=r"""
 const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
 const imageKey=src=>{
  try {
   const u=new URL(src);
   return u.origin==='https://flow.google.com'&&u.pathname.startsWith('/asb/')
    ?u.origin+u.pathname.replace(/=s\d+(?:-[a-z]+)*$/,''):null;
  } catch {return null;}
 };
 const verifiedResources=globalThis[Symbol.for('flow-image.verified-resources')]||=new Map();
 const imageId=im=>{
  if(!im)return null;
  const src=im.currentSrc||im.src||'';
  const direct=im.getAttribute('data-media-id')||/^https:\/\/flow-content\.google\/image\/([0-9a-f-]{36})(?:[?/#]|$)/i.exec(src)?.[1];
  if(direct&&uuid.test(direct))return direct;
  const key=imageKey(src);
  if(!key)return null;
  // Match the actual image resource to a grid tile with an explicit ID.
  // A filename alone is not evidence of identity; ambiguity stays unresolved.
  const ids=verifiedResources.get(key)||new Set();
  [...document.querySelectorAll('flow-grid-tile-container img[data-media-id]')]
   .filter(g=>imageKey(g.currentSrc||g.src||'')===key)
   .map(g=>g.getAttribute('data-media-id')).filter(id=>uuid.test(id||''))
   .forEach(id=>ids.add(id));
  if(ids.size)verifiedResources.set(key,ids);
  return ids.size===1?[...ids][0]:null;
 };
"""
MEDIA_JS="() => {"+IMAGE_ID_JS+r"""
 const out=[];
 [...document.images].forEach((im,position)=>{
  const src=im.currentSrc||im.src||'';
  const id=imageId(im);
  if(id)out.push({id,src,width:im.naturalWidth,height:im.naturalHeight,position});
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

REFS_JS="() => {"+IMAGE_ID_JS+r"""return [...document.querySelectorAll('button[aria-label="素材"],button[aria-label="Asset"]')]
 .filter(e=>e.getClientRects().length).map(e=>({busy:e.getAttribute('aria-busy')==='true',width:e.querySelector('img')?.naturalWidth||0,height:e.querySelector('img')?.naturalHeight||0,id:imageId(e.querySelector('img'))}));}"""

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

def reference_digest(path):
    validate_reference(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()

def reference_cache():
    path=ROOT/'reference-cache.json'
    return json.loads(path.read_text()) if path.exists() else {'version':1,'projects':{}}

def cached_reference(digest):
    return reference_cache()['projects'].get(PROJECT,{}).get(digest)

def store_reference(digest,entry):
    # Called inside the composer lock, shared by every Agent/process.
    data=reference_cache();data['projects'].setdefault(PROJECT,{})[digest]=entry
    target=ROOT/'reference-cache.json';temp=target.with_name(target.name+'.'+uuid.uuid4().hex+'.tmp')
    try:temp.write_text(json.dumps(data,ensure_ascii=False)+'\n');os.replace(temp,target)
    finally:temp.unlink(missing_ok=True)

def historical_reference_ids(body,prompt_sha,count):
    if not request_matches(body,prompt_sha):return []
    try:
        outer=json.loads(urllib.parse.parse_qs(body)['f.req'][0]);args=json.loads(outer[0][0][1])
        ids=[r[0] for r in args[1][0][2]]
        if len(ids)!=count or any(not isinstance(i,str) or not re.fullmatch(r'[0-9a-f-]{36}',i) for i in ids):return []
        return ids
    except (ValueError,KeyError,IndexError,TypeError):return []

def lookup_historical_reference(page,digest):
    jobs=[json.loads(p.read_text()) for p in (ROOT/'jobs').glob('*.json')]
    history=ROOT/'history.jsonl'
    if history.exists():jobs.extend(json.loads(line) for line in history.read_text().splitlines() if line.strip())
    candidates=[j for j in jobs if j.get('project')==PROJECT and digest in j.get('reference_sha256',[])]
    if not candidates:return None
    pid=re.search(r'pid=(\d+)',run_cli('status',as_json=False))
    names=evaluate(page,"() => Object.fromEntries([...document.querySelectorAll('flow-grid-tile-container img[data-media-id]')].map(im=>[im.getAttribute('data-media-id'),im.closest('flow-grid-tile-container').getAttribute('aria-label')]))")
    for job in sorted(candidates,key=lambda j:j.get('submitted_at',0),reverse=True):
        if not pid or int(pid.group(1))!=job.get('daemon_pid') or not job.get('network_request_id'):continue
        try:body=read_network_body(page,job['network_request_id'],'request')
        except RuntimeError:continue
        hashes=job['reference_sha256'];ids=historical_reference_ids(body,job['prompt_sha256'],len(hashes))
        if not ids:continue
        for sha,media in zip(hashes,ids):
            # Keep already-established mappings instead of replacing them with duplicates.
            if cached_reference(sha) is None:
                store_reference(sha,{'media_id':media,'name':names.get(media),'state':'ready','provenance_job':job['request_id']})
        return cached_reference(digest)
    raise RuntimeError('This reference was used in this project before, but its material ID could not be verified; inspect the cache instead of uploading again')

def open_reference_menu(page):
    snap=snapshot(page)
    if not re.search(r'listbox "(?:资源列表|Asset list)"',snap):
        run_cli('click',page,control(snap,'button',r'^在提示框中添加素材$|^Add assets'))
        deadline=time.monotonic()+8
        while time.monotonic()<deadline:
            if re.search(r'listbox "(?:资源列表|Asset list)"',snapshot(page)):return
            time.sleep(0.4)
        raise RuntimeError('Reference menu did not open; no upload or generation was submitted')

ASSET_OPTIONS_JS="() => {"+IMAGE_ID_JS+r"""return [...document.querySelectorAll('[role=option]')].map(e=>({name:e.querySelector('.asset-title')?.textContent,id:imageId(e.querySelector('img'))})).filter(r=>r.name);}"""
CLICK_REFERENCE_JS="() => {"+IMAGE_ID_JS+r"""
 const matches=[...document.querySelectorAll('[role=option]')]
  .filter(e=>e.getClientRects().length&&imageId(e.querySelector('img'))===__MEDIA_ID__);
 if(matches.length!==1)return null;
 matches[0].click();return __MEDIA_ID__;
}"""
PROJECT_SEARCH_JS=r"""() => {
 const input=document.querySelector('input[aria-label="搜索"],input[aria-label="Search"]');
 return input?{url:location.origin+location.pathname,value:input.value,active:!!input.parentElement.querySelector('button[aria-label="返回"],button[aria-label="Back"]')}:null;
}"""

@contextlib.contextmanager
def reference_library_identity(page,entry):
    # ASB resources have no UUID in their URL. Expose the actual ID-bearing grid
    # tile when virtualization removed it; filenames narrow the view, not identity.
    original=evaluate(page,PROJECT_SEARCH_JS)
    if original is None:raise RuntimeError('Project search is unavailable; the reference was not uploaded again')
    if original['url']!=PROJECT_URL:raise RuntimeError('Flow project changed; the current page was preserved')
    run_cli('press_key',page,'Escape')
    try:
        run_cli('fill',page,control(snapshot(page),'textbox',r'^搜索$|^Search$'),entry['name'])
        deadline=time.monotonic()+10
        source='() => !!document.querySelector('+json.dumps('flow-grid-tile-container img[data-media-id="'+entry['media_id']+'"]')+')'
        while not evaluate(page,source):
            if time.monotonic()>=deadline:raise RuntimeError('The cached media ID could not be verified in the project library; it was not uploaded again')
            time.sleep(0.4)
        yield
    finally:
        current=evaluate(page,PROJECT_SEARCH_JS)
        if not current or current['url']!=original['url']:raise RuntimeError('Flow project changed during reference verification; the current page was preserved')
        snap=snapshot(page)
        if re.search(r'listbox "(?:资源列表|Asset list)"',snap):
            run_cli('press_key',page,'Escape');snap=snapshot(page)
        if original['active']:
            run_cli('fill',page,control(snap,'textbox',r'^搜索$|^Search$'),original['value'])
        else:
            run_cli('click',page,control(snap,'button',r'^返回$|^Back$'))

def select_reference(page,entry,expected_count,_library_checked=False):
    open_reference_menu(page)
    if entry.get('name'):
        run_cli('fill',page,control(snapshot(page),'textbox',r'^搜索资源$|^Search assets$'),entry['name'])
    deadline=time.monotonic()+40;selected=None
    while time.monotonic()<deadline:
        options=evaluate(page,ASSET_OPTIONS_JS)
        matches=[r for r in options if r['id']==entry['media_id']] if entry.get('media_id') else [r for r in options if r['name']==entry.get('name')]
        if len(matches)>1:raise RuntimeError('Reference material is ambiguous; verify its media ID instead of selecting a same-name copy or uploading again')
        selected=next((r for r in matches if r['id']),None)
        if selected:break
        if not _library_checked and entry.get('media_id') and entry.get('name') and any(r['name']==entry['name'] and not r['id'] for r in options):
            with reference_library_identity(page,entry):
                return select_reference(page,entry,expected_count,_library_checked=True)
        if not entry.get('name'):
            evaluate(page,"() => {const e=document.querySelector('[role=listbox]');if(e)e.scrollTop+=Math.max(e.clientHeight-40,200)}")
        time.sleep(0.5)
    if not selected:raise RuntimeError('Cached reference material was not found or is still unavailable; it was not uploaded again')
    clicked=evaluate(page,CLICK_REFERENCE_JS.replace('__MEDIA_ID__',json.dumps(selected['id'])))
    if clicked!=selected['id']:raise RuntimeError('The exact reference option changed or became ambiguous; no generation was submitted')
    deadline=time.monotonic()+40
    rows=evaluate(page,REFS_JS)
    if not (references_ready(rows,expected_count) and selected['id'] in {r.get('id') for r in rows}):
        # Selecting can attach immediately and close the menu before the chip's
        # thumbnail loads. Only click Add if the menu still offers that button.
        try:add=control(snapshot(page),'button',r'^添加到提示$|^Add to prompt$')
        except ValueError:add=None
        if add:run_cli('click',page,add)
    while time.monotonic()<deadline:
        rows=evaluate(page,REFS_JS)
        if references_ready(rows,expected_count) and selected['id'] in {r.get('id') for r in rows}:
            return {'media_id':selected['id'],'name':selected['name'],'state':'ready'}
        time.sleep(0.5)
    raise TimeoutError('The exact cached reference did not become ready; expected '+str(expected_count)+' chips including '+selected['id']+', observed '+json.dumps(rows)+'; no generation was submitted')

def upload_reference(page,path,entry,expected_count):
    stage_dir=ROOT/'uploads';stage_dir.mkdir(exist_ok=True);staged=stage_dir/entry['name']
    shutil.copyfile(path,staged)
    try:
        open_reference_menu(page)
        run_cli('upload_file',page,control(snapshot(page),'button',r'^上传媒体内容$|^Upload media$'),staged)
        return select_reference(page,entry,expected_count)
    finally:staged.unlink(missing_ok=True)

def attach_reference(page,path,expected_count=1):
    digest=reference_digest(path);entry=cached_reference(digest)
    if entry is None:entry=lookup_historical_reference(page,digest)
    if entry is not None:
        selected=select_reference(page,entry,expected_count)
        if selected is not None:store_reference(digest,{**entry,**selected})
        return {'sha256':digest,'reused':True,'media_id':entry.get('media_id') or selected['media_id']}
    entry={'media_id':None,'name':'flow-ref-'+digest+validate_reference(path),'state':'uploading'}
    # Persist before upload: an interrupted upload is searched, never blindly repeated.
    store_reference(digest,entry)
    selected=upload_reference(page,path,entry,expected_count);store_reference(digest,selected)
    return {'sha256':digest,'reused':False,'media_id':selected['media_id']}

def full_image_url(url):
    return re.sub(r'=s\d+(?:-[a-z]+)*$','=s0',url) if url.startswith('https://flow.google.com/asb/') else url

def download(url,requested,page=None):
    if url.startswith('https://flow.google.com/asb/'):
        # /asb/ is authenticated. Read only the image through the existing tab;
        # never export cookies or request headers to an external HTTP client.
        source=r"""async () => {
         const r=await fetch(__URL__);
         if(!r.ok)throw Error('Flow image fetch failed');
         const blob=await r.blob();
         if(!blob.type.startsWith('image/')||blob.size>40000000)throw Error('Invalid Flow image response');
         return await new Promise((resolve,reject)=>{
          const reader=new FileReader();
          reader.onload=()=>resolve(reader.result.split(',')[1]);
          reader.onerror=()=>reject(Error('Image read failed'));
          reader.readAsDataURL(blob);
         });
        }""".replace('__URL__',json.dumps(full_image_url(url)))
        try:blob=base64.b64decode(evaluate(page if page is not None else page_id(),source),validate=True)
        except Exception as exc:raise RuntimeError('Browser image download failed: '+type(exc).__name__) from None
    elif url.startswith('https://flow-content.google/image/'):
        ctx=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
        try:
            with urllib.request.urlopen(url,context=ctx,timeout=120) as response:blob=response.read(40000000)
        except Exception as exc:raise RuntimeError('Image download failed: '+type(exc).__name__) from None
    else:raise ValueError('Unexpected image host')
    if blob.startswith(b'\xff\xd8\xff'):suffix='.jpg'
    elif blob.startswith(b'\x89PNG\r\n\x1a\n'):suffix='.png'
    elif blob.startswith(b'RIFF') and blob[8:12]==b'WEBP':suffix='.webp'
    else:raise ValueError('Flow returned no supported image file')
    output=requested.with_suffix(suffix);output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('xb') as f:f.write(blob)
    return output

@contextlib.contextmanager
def composer_lock():
    with (ROOT/'generation.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        yield

def job_path(job_id):
    if not re.fullmatch(r'[0-9a-f]{32}',job_id):raise ValueError('Invalid job ID')
    return ROOT/'jobs'/(job_id+'.json')

def save_job(job):
    target=job_path(job['request_id']);target.parent.mkdir(exist_ok=True)
    temp=target.with_name(target.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        temp.write_text(json.dumps(job,ensure_ascii=False)+'\n');os.replace(temp,target)
    finally:temp.unlink(missing_ok=True)

def active_jobs():
    return [d for p in (ROOT/'jobs').glob('*.json') if (d:=json.loads(p.read_text())).get('state') not in ('completed','failed')]

def append_history(job):
    with (ROOT/'history.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        with (ROOT/'history.jsonl').open('a') as f:f.write(json.dumps(job,ensure_ascii=False)+'\n')

def network_requests(page):
    rows=[];index=0
    while True:
        result=run_cli('list_network_requests',page,'--resourceTypes','fetch','--pageSize',100,'--pageIdx',index)
        rows.extend(result.get('networkRequests',[]))
        if not result.get('pagination',{}).get('hasNextPage'):return rows
        index+=1

def nested_strings(value):
    if isinstance(value,str):
        yield value
        try:decoded=json.loads(value)
        except ValueError:return
        if decoded!=value:yield from nested_strings(decoded)
    elif isinstance(value,(list,dict)):
        for item in value.values() if isinstance(value,dict) else value:yield from nested_strings(item)

def request_matches(body,prompt_sha):
    try:payload=json.loads(urllib.parse.parse_qs(body)['f.req'][0])
    except (KeyError,ValueError,IndexError):return False
    return any(hashlib.sha256(text.encode()).hexdigest()==prompt_sha for text in nested_strings(payload))

class BodyUnavailable(RuntimeError):pass

def read_network_body(page,reqid,which):
    # Native CLI truncates inline bodies at 10k. Read a full body in a private,
    # short-lived directory; never keep tokens, request headers or signed URLs.
    with tempfile.TemporaryDirectory(prefix='.network-',dir=ROOT) as directory:
        path=Path(directory)/'body.txt'
        result=run_cli('get_network_request',page,'--reqid',reqid,'--'+which+'FilePath',path)
        if isinstance(result,list):result=result[0] if result else {}
        detail=result.get('networkRequest') or {}
        actual=Path(detail.get(which+'BodyFilePath') or path)
        if actual.is_file():return actual.read_text()
        raise BodyUnavailable('Browser network '+which+' body is unavailable')

def find_submission(page,baseline,prompt_sha):
    deadline=time.monotonic()+35
    while time.monotonic()<deadline:
        for row in network_requests(page):
            if row['requestId'] in baseline:continue
            parsed=urllib.parse.urlparse(row['url'])
            if row.get('method')!='POST' or parsed.hostname!='flow.google.com' or not parsed.path.endswith('/batchexecute'):continue
            if request_matches(read_network_body(page,row['requestId'],'request'),prompt_sha):return row['requestId']
        time.sleep(0.5)
    raise TimeoutError('Submission was not confirmed; inspect the job before resubmitting')

def rpc_result(body):
    for line in body.splitlines():
        try:batch=json.loads(line)
        except ValueError:continue
        if not isinstance(batch,list):continue
        for row in batch:
            if not isinstance(row,list) or len(row)<3 or row[0]!='wrb.fr' or not isinstance(row[2],str):continue
            try:payload=json.loads(row[2]);media=payload[0]
            except (ValueError,IndexError,TypeError):continue
            if not isinstance(media,list):continue
            for item in media:
                try:media_id=item[0];width,height=item[6][2]
                except (IndexError,TypeError,ValueError):continue
                if not isinstance(media_id,str) or not re.fullmatch(r'[0-9a-f-]{36}',media_id):continue
                if not isinstance(width,int) or not isinstance(height,int) or min(width,height)<512:continue
                prefix='https://flow-content.google/image/'+media_id+'?'
                src=next((x for x in nested_strings(item) if x.startswith(prefix) or x.startswith('https://flow.google.com/asb/')),None)
                if src:return {'id':media_id,'src':src,'width':width,'height':height}
    return None

def choose_ui_result(rows,prompt_sha):
    matches=[r for r in rows if hashlib.sha256(r['prompt'].encode()).hexdigest()==prompt_sha]
    if len(matches)>1:raise RuntimeError('UI result is ambiguous; keep this job and inspect it instead of guessing')
    return matches[0] if matches else None

def find_ui_result(job):
    with composer_lock():
        # UI overlays share the composer. Never inspect them while a different
        # caller is submitting; network-only polling does not need this lock.
        if PENDING.exists():return None
        if any(j['request_id']!=job['request_id'] and j.get('prompt_sha256')==job['prompt_sha256'] for j in active_jobs()):
            raise RuntimeError('Identical concurrent prompts are ambiguous without the response body; inspect the jobs')
        page=job['page_id'];state=evaluate(page,STATE_JS)
        if state.get('draft'):return None
        if state.get('url')!=PROJECT_URL:raise RuntimeError('Flow project changed during result collection')
        claimed=set()
        for file in (ROOT/'jobs').glob('*.json'):
            other=json.loads(file.read_text())
            if other['request_id']!=job['request_id'] and other.get('result'):claimed.add(other['result']['media_id'])
        candidates=evaluate(page,r"""() => [...document.querySelectorAll('flow-grid-tile-container img[data-media-id]')].map(im=>({id:im.getAttribute('data-media-id'),src:im.currentSrc||im.src,width:im.naturalWidth,height:im.naturalHeight,title:im.closest('flow-grid-tile-container')?.getAttribute('aria-label')})).filter(r=>r.width>=512&&r.height>=512)""")
        excluded=set(job.get('baseline_media_ids',[]))|claimed;matches=[]
        for row in candidates:
            if row['id'] in excluded:continue
            image_uid=None
            for line in snapshot(page).splitlines():
                if (row['id'] in line or 'url='+json.dumps(row['src'],ensure_ascii=False) in line) and re.search(r'\bimage\b',line):
                    match=re.search(r'uid=(\S+)',line)
                    if match:image_uid=match.group(1);break
            if not image_uid:continue
            run_cli('hover',page,image_uid)
            def toggle():
                run_cli('click',page,control(snapshot(page),'button','^'+re.escape(row['title'])+'$'))
            prompt=None;opened=False
            try:
                # Flow can leave the trigger expanded after Escape; toggle it
                # closed then open if needed, using native CLI input events.
                for attempt in range(2):
                    toggle();deadline=time.monotonic()+1.5
                    while time.monotonic()<deadline:
                        info=evaluate(page,"() => ({title:document.querySelector('flow-info-panel .title')?.textContent,prompt:[...document.querySelectorAll('flow-info-panel .prompt-text .text-part')].map(e=>e.textContent).join('')})")
                        if info.get('title')==row['title'] and info.get('prompt'):
                            prompt=info['prompt'];opened=True;break
                        time.sleep(0.1)
                    if opened:break
                if prompt is not None:row['prompt']=prompt;matches.append(row)
            finally:
                if opened:toggle()
                else:run_cli('press_key',page,'Escape')
        return choose_ui_result(matches,job['prompt_sha256'])

def submit_job(prompt,output,aspect,reference=None):
    if not prompt.strip():raise ValueError('Prompt must not be empty')
    if not output.is_absolute():raise ValueError('Use an absolute output path')
    references=[] if reference is None else ([reference] if isinstance(reference,Path) else list(reference))
    for path in references:validate_reference(path)
    with composer_lock():
        if PENDING.exists():raise RuntimeError('A legacy submitted job is unresolved; let it finish before switching')
        jobs=active_jobs()
        if any(j['state'] in ('submitting','unconfirmed') for j in jobs):raise RuntimeError('An earlier submission is unconfirmed; inspect its job before resubmitting')
        if any(output.with_suffix(ext).exists() for ext in ('.jpg','.png','.webp')):raise FileExistsError('Output already exists')
        if any(Path(j['output']).with_suffix('')==output.with_suffix('') for j in jobs):raise FileExistsError('Output is reserved by an unfinished job')
        daemon=ensure_daemon();page=page_id();run_cli('select_page',page)
        snap=prepare(page,aspect)
        attached=[]
        for count,path in enumerate(references,start=1):attached.append(attach_reference(page,path,expected_count=count))
        if references:snap=snapshot(page)
        baseline={r['requestId'] for r in network_requests(page)}
        baseline_media_ids=[r['id'] for r in evaluate(page,MEDIA_JS)]
        editor=control(snap,'textbox',r'您希望创作什么|What do you want|Describe|Create')
        run_cli('fill',page,editor,prompt)
        if references and not references_ready(evaluate(page,REFS_JS),len(references)):raise ValueError('Reference disappeared before submission; request was not submitted')
        job={'request_id':uuid.uuid4().hex,'state':'submitting','prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'project':PROJECT,'model':'Nano Banana 2.1','output':str(output),'submitted_at':time.time(),'mode':'image-to-image' if references else 'text-to-image','reference_count':len(references),'baseline_media_ids':baseline_media_ids,'page_id':page,'daemon_pid':int(re.search(r'pid=(\d+)',daemon).group(1))}
        if references:
            job['reference_sha256']=[r['sha256'] for r in attached]
            job['reference_media_ids']=[r['media_id'] for r in attached]
        job['reference_reused_count']=sum(r['reused'] for r in attached)
        save_job(job)
        try:
            run_cli('press_key',page,'Enter')
            job['network_request_id']=find_submission(page,baseline,job['prompt_sha256'])
            job.update(state='submitted',accepted_at=time.time());save_job(job)
        except Exception as exc:
            job.update(state='unconfirmed');save_job(job);exc.job_id=job['request_id'];raise
    # Generation proceeds remotely after the short composer lock is released.
    return job

def wait_job(job_id,timeout=240):
    job=json.loads(job_path(job_id).read_text())
    if job['state']=='completed':return job['result']
    if 'network_request_id' not in job:raise RuntimeError('This submission is unconfirmed; inspect it instead of resubmitting')
    page=job['page_id'];deadline=time.monotonic()+timeout
    try:
        while time.monotonic()<deadline:
            daemon=run_cli('status',as_json=False)
            pid=re.search(r'pid=(\d+)',daemon)
            if not pid or int(pid.group(1))!=job['daemon_pid']:raise RuntimeError('The original DevTools connection changed; request IDs cannot be reused safely')
            row=next((r for r in network_requests(page) if r['requestId']==job['network_request_id']),None)
            if row is None:raise RuntimeError('The submitted browser request is no longer available; inspect the job')
            status=str(row['status'])
            selected=None
            if status=='200':
                try:selected=rpc_result(read_network_body(page,job['network_request_id'],'response'))
                except BodyUnavailable:pass
            if not selected and (status=='200' or status.startswith('net::')):selected=find_ui_result(job)
            if selected:
                # A second waiter for the same job must not duplicate downloads/history.
                with (job_path(job_id).with_suffix('.lock')).open('a') as lock:
                    fcntl.flock(lock,fcntl.LOCK_EX)
                    latest=json.loads(job_path(job_id).read_text())
                    if latest['state']=='completed':return latest['result']
                    actual=(download(selected['src'],Path(job['output']),page) if selected['src'].startswith('https://flow.google.com/asb/')
                            else download(selected['src'],Path(job['output'])))
                    result={'ok':True,'job_id':job_id,'mode':job['mode'],'reference_count':job['reference_count'],'reference_reused_count':job.get('reference_reused_count'),'output':str(actual),'media_id':selected['id'],'width':selected['width'],'height':selected['height'],'model':job['model'],'project':job['project'],'page_id':page,'daemon_pid':job['daemon_pid'],'network_request_id':job['network_request_id'],'elapsed_seconds':round(time.time()-job['submitted_at'])}
                    job.update(state='completed',completed_at=time.time(),result=result);save_job(job);append_history({**job,**result});return result
            if status.isdigit() and int(status)>=400:
                job.update(state='failed',error='Browser request failed: '+status);save_job(job);append_history({**job,'ok':False})
                raise RuntimeError(job['error'])
            time.sleep(2)
        raise TimeoutError('Job is still unresolved; use flow-image wait '+job_id+' to resume without submitting again')
    except Exception as exc:
        exc.job_id=job_id;raise

def generate(prompt,output,aspect,reference=None):
    return wait_job(submit_job(prompt,output,aspect,reference)['request_id'])

def main():
    os.umask(0o077);ROOT.mkdir(parents=True,exist_ok=True);ROOT.chmod(0o700)
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('status');sub.add_parser('stop')
    image=sub.add_parser('image');image.add_argument('prompt');image.add_argument('--output','-o',required=True);image.add_argument('--aspect',choices=['1:1','16:9','9:16','4:3','3:4'],default='1:1')
    image.add_argument('--no-wait',action='store_true',help='Return the accepted job ID immediately; collect it later with wait')
    wait=sub.add_parser('wait');wait.add_argument('job_id')
    image.add_argument('--ref',action='append',default=[],type=lambda v:Path(v).expanduser(),help='Absolute JPEG/PNG/WebP reference image; repeat for multiple images in order')
    args=parser.parse_args()
    try:
        if not CONFIG.get('project') or not CONFIG.get('account'):raise ValueError('Configure project and account in FLOW_IMAGE_HOME/config.json first')
        if args.command=='image':
            if args.no_wait:
                job=submit_job(args.prompt,Path(args.output).expanduser(),args.aspect,args.ref)
                result={'ok':True,'job_id':job['request_id'],'state':job['state'],'network_request_id':job['network_request_id'],'reference_count':job['reference_count'],'reference_reused_count':job['reference_reused_count']}
            else:result=generate(args.prompt,Path(args.output).expanduser(),args.aspect,args.ref)
        elif args.command=='wait':result=wait_job(args.job_id)
        elif args.command=='stop':
            with composer_lock():
                if active_jobs() or PENDING.exists():raise RuntimeError('Unfinished jobs exist; collect their results before stopping the daemon')
                result={'ok':True,'status':run_cli('stop',as_json=False)}
        else:
            status=ensure_daemon();page=page_id();state=evaluate(page,STATE_JS)
            result={'ok':True,'status':status,'state':state,'pending_job':PENDING.exists(),'jobs':[{k:j.get(k) for k in ('request_id','state','network_request_id','output')} for j in active_jobs()]}
        print(json.dumps(result,ensure_ascii=False));return 0
    except Exception as exc:
        print(json.dumps({'ok':False,'error_type':type(exc).__name__,'error':str(exc)[:1200],'job_id':getattr(exc,'job_id',None),'may_have_submitted':PENDING.exists() or bool(getattr(exc,'job_id',None))},ensure_ascii=False),file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
