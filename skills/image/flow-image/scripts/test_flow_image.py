import importlib.util,unittest,tempfile,contextlib,io,sys,json,subprocess
from unittest.mock import patch
from pathlib import Path
class DriverTests(unittest.TestCase):
 def dom(self,source,ambiguous=False,**options):
  fixture=Path(__file__).with_name('dom_fixture.cjs')
  result=subprocess.run(['node',str(fixture)],input=json.dumps({'source':source,'ambiguous':ambiguous,**options}),text=True,capture_output=True,check=True)
  return json.loads(result.stdout)
 def test_asb_asset_and_composer_chip_resolve_to_exact_grid_media_id(self):
  m=self.load();mid='cd82b996-cc81-40f8-bd2a-fee0f96556f0'
  self.assertEqual(self.dom(m.ASSET_OPTIONS_JS),[{'name':'reference.jpg','id':mid}])
  self.assertEqual(self.dom(m.REFS_JS),[{'busy':False,'width':896,'height':1200,'id':mid}])
 def test_verified_asb_identity_survives_grid_virtualization(self):
  m=self.load()
  self.assertEqual(self.dom(m.ASSET_OPTIONS_JS,hideGridAfterFirstResolution=True),[{'name':'reference.jpg','id':'cd82b996-cc81-40f8-bd2a-fee0f96556f0'}])
 def test_offscreen_cached_reference_is_verified_in_library_and_search_is_restored(self):
  m=self.load();wanted='11111111-1111-4111-8111-111111111111';state={'picker':True,'exposed':False,'attached':False,'query':''}
  def snap(page):
   text='uid=library textbox "搜索"\nuid=back button "返回"\nuid=add button "在提示框中添加素材"'
   return text+('\nuid=picker listbox "资源列表"\nuid=search textbox "搜索资源"' if state['picker'] else '')
  def cli(command,page,*args,**kw):
   if command=='press_key':state['picker']=False
   elif command=='click' and args[0]=='back':state.update(query='',exposed=False)
   elif command=='click':state['picker']=True
   elif command=='fill' and args[0]=='library':state.update(query=args[1],exposed=True)
  def browser(page,source):
   if source==m.ASSET_OPTIONS_JS:return [{'name':'reference.jpg','id':wanted if state['exposed'] else None}]
   if source==m.REFS_JS:return [{'id':wanted,'busy':False,'width':896,'height':1200}] if state['attached'] else []
   if 'matches[0].click()' in source:state['attached']=True;return wanted
   if 'input[aria-label' in source:return {'url':m.PROJECT_URL,'value':'','active':False}
   return state['exposed']
  m.snapshot=snap;m.run_cli=cli;m.evaluate=browser
  import itertools
  ticks=itertools.count()
  with patch.object(m.time,'sleep'),patch.object(m.time,'monotonic',side_effect=lambda:next(ticks)):
   try:result=m.select_reference(8,{'media_id':wanted,'name':'reference.jpg'},1)
   except RuntimeError as e:self.fail('A cached ASB asset outside the current grid must be resolved through verified library IDs: '+str(e))
  self.assertEqual(result['media_id'],wanted);self.assertTrue(state['attached']);self.assertEqual(state['query'],'')
 def test_library_recovery_does_not_restore_over_user_navigation(self):
  m=self.load();states=iter([{'url':m.PROJECT_URL,'value':'','active':False},None]);actions=[]
  m.evaluate=lambda page,source:next(states) if source==m.PROJECT_SEARCH_JS else True
  m.snapshot=lambda page:'uid=search textbox "搜索"\nuid=back button "返回"'
  m.run_cli=lambda *a,**k:actions.append(a)
  with self.assertRaisesRegex(RuntimeError,'changed'):
   with m.reference_library_identity(8,{'name':'reference.jpg','media_id':'known'}):pass
  self.assertNotIn(('click',8,'back'),actions)
 def test_asb_images_are_included_in_result_baseline_alongside_legacy_urls(self):
  m=self.load()
  self.assertEqual([r['id'] for r in self.dom(m.MEDIA_JS)],['cd82b996-cc81-40f8-bd2a-fee0f96556f0','22222222-2222-4222-8222-222222222222'])
 def test_ambiguous_asb_thumbnail_never_guesses_a_media_id(self):
  m=self.load()
  self.assertIsNone(self.dom(m.ASSET_OPTIONS_JS,ambiguous=True)[0]['id'])
  self.assertIsNone(self.dom(m.REFS_JS,ambiguous=True)[0]['id'])
 def test_asb_rpc_response_retains_its_own_output_identity(self):
  m=self.load();mid='11111111-1111-4111-8111-111111111111';url='https://flow.google.com/asb/opaque-result=s1200-rw'
  body=json.dumps([['wrb.fr','ogiZ0b',json.dumps([[[mid,None,None,None,None,None,[None,None,[896,1200],None,None,[url]]]]])]])
  self.assertEqual(m.rpc_result(body),{'id':mid,'src':url,'width':896,'height':1200})
 def test_asb_download_uses_existing_browser_session_and_preserves_output(self):
  m=self.load();import base64
  blob=b'RIFF'+bytes(4)+b'WEBP'+b'image-data';m.page_id=lambda:8
  m.evaluate=lambda page,source:base64.b64encode(blob).decode()
  with tempfile.TemporaryDirectory() as d:
   try:output=m.download('https://flow.google.com/asb/opaque-result=s1200-rw',Path(d)/'image.jpg')
   except ValueError as e:self.fail('A verified Flow asb image must be downloadable: '+str(e))
   self.assertEqual(output,Path(d)/'image.webp');self.assertEqual(output.read_bytes(),blob)
   with self.assertRaises(FileExistsError):m.download('https://flow.google.com/asb/opaque-result=s1200-rw',Path(d)/'image.jpg')
 def test_asb_download_rejects_other_origins_before_browser_access(self):
  m=self.load();m.evaluate=lambda *a:self.fail('Untrusted image URL must not reach the browser')
  with self.assertRaises(ValueError):m.download('https://flow.google.com.evil.test/asb/opaque',Path('/unused.jpg'))
 def test_asb_download_requests_original_instead_of_grid_thumbnail(self):
  m=self.load()
  self.assertEqual(m.full_image_url('https://flow.google.com/asb/opaque=s512-rw'),'https://flow.google.com/asb/opaque=s0')
  self.assertEqual(m.full_image_url('https://flow.google.com/asb/opaque=s3200-rw'),'https://flow.google.com/asb/opaque=s0')
  self.assertEqual(m.full_image_url('https://flow-content.google/image/id?signed=test'),'https://flow-content.google/image/id?signed=test')
 def load(self):
  p=Path(__file__).with_name('flow_image.py');self.assertTrue(p.exists(),'Flow CLI driver is not implemented yet')
  s=importlib.util.spec_from_file_location('flow_image',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 def test_model_is_verified_before_submit(self):
  m=self.load()
  with self.assertRaises(ValueError):m.validate_state({'url':m.PROJECT_URL,'account_ok':True,'model_text':'Nano Banana Pro x1','draft':''})
  with self.assertRaises(ValueError):m.validate_state({'url':m.PROJECT_URL,'account_ok':True,'model_text':'Nano Banana 2.1 x1','draft':'unfinished user prompt'})
  m.validate_state({'url':m.PROJECT_URL,'account_ok':True,'model_text':'Nano Banana 2.1 x1','draft':''})
 def test_does_not_mistake_old_or_unready_images_for_results(self):
  m=self.load();baseline={'old'}
  rows=[{'id':'new','position':0,'width':1024,'height':1024},{'id':'old','position':1,'width':1024,'height':1024},{'id':'late-old','position':2,'width':1024,'height':1024}]
  self.assertEqual(m.new_images(rows,baseline)[0]['id'],'new')
  self.assertEqual(m.new_images([dict(rows[0],width=0),rows[1]],baseline),[])
  self.assertEqual(m.new_images([rows[1],rows[2]],baseline),[])
 def test_accepts_cli_serialized_auto_connect_flag_without_restart(self):
  m=self.load();calls=[]
  def fake(*args,**kwargs):
   calls.append(args)
   return 'daemon is running.\npid=44561 version=1.12.0\nargs=["--auto-connect"]'
  m.run_cli=fake
  self.assertIn('44561',m.ensure_daemon())
  self.assertEqual(calls,[('status',)])
 def test_bad_reference_is_rejected_before_browser_or_submission(self):
  m=self.load()
  with self.assertRaisesRegex(ValueError,'Reference'):
   m.validate_reference(Path('/missing-reference.jpg'))
 def test_uploaded_reference_is_not_treated_as_a_generated_result(self):
  m=self.load()
  rows=[{'id':'result','position':0,'width':1024,'height':1024},{'id':'upload','position':1,'width':1024,'height':1024},{'id':'old','position':2,'width':1024,'height':1024}]
  self.assertEqual([r['id'] for r in m.new_images(rows,{'upload','old'})],['result'])
 def test_ready_reference_requires_a_loaded_nonbusy_chip(self):
  m=self.load()
  self.assertFalse(m.references_ready([]))
  self.assertFalse(m.references_ready([{'busy':True,'width':1024,'height':1024}]))
  self.assertFalse(m.references_ready([{'busy':False,'width':0,'height':0}]))
  self.assertTrue(m.references_ready([{'busy':False,'width':1024,'height':1024}]))
 def test_old_failure_does_not_fail_a_new_request(self):
  m=self.load()
  self.assertFalse(m.has_new_failure(1,1))
  self.assertTrue(m.has_new_failure(2,1))
 def test_every_reference_must_be_ready_before_submission(self):
  m=self.load();ready={'busy':False,'width':1024,'height':1024}
  self.assertTrue(m.references_ready([ready,ready],expected=2))
  self.assertFalse(m.references_ready([ready],expected=2))
  self.assertFalse(m.references_ready([ready,dict(ready,busy=True)],expected=2))
  self.assertFalse(m.references_ready([ready,dict(ready,width=0)],expected=2))
  self.assertFalse(m.references_ready([ready,ready,ready],expected=2))
 def test_repeated_ref_arguments_reach_generation_in_order(self):
  m=self.load();seen=[]
  with tempfile.TemporaryDirectory() as d:
   m.ROOT=Path(d);m.CONFIG={'account':'test','project':'test'}
   m.generate=lambda *args:seen.append(args) or {'ok':True}
   with patch.object(sys,'argv',['flow-image','image','combine','--ref','/a.jpg','--ref','/b.png','--output','/out.jpg']),contextlib.redirect_stdout(io.StringIO()):
    self.assertEqual(m.main(),0)
  self.assertEqual(seen[0][3],[Path('/a.jpg'),Path('/b.png')])
 def test_invalid_second_reference_stops_before_browser_activity(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);first=root/'a.jpg';first.write_bytes(b'\xff\xd8\xff'+b'0'*16)
   m.PENDING=root/'pending.json'
   m.ensure_daemon=lambda:self.fail('Browser must not be touched for an invalid second reference')
   with self.assertRaisesRegex(ValueError,'Reference'):
    m.generate('combine',root/'output.jpg','1:1',[first,root/'missing.png'])
 def test_network_response_is_attributed_to_its_own_media(self):
  m=self.load();import json
  def body(media):
   return json.dumps([['wrb.fr','ogiZ0b',json.dumps([[[media,None,None,None,None,None,[None,None,[1024,1024],None,None,['https://flow-content.google/image/'+media+'?signed=test']]]]]),None]])
  a='11111111-1111-4111-8111-111111111111';b='22222222-2222-4222-8222-222222222222'
  # B may complete before A; each response must keep its own output identity.
  self.assertEqual(m.rpc_result(body(b))['id'],b)
  self.assertEqual(m.rpc_result(body(a))['id'],a)
  self.assertIsNone(m.rpc_result('not a complete response'))
 def test_exact_prompt_match_handles_nested_form_encoded_payload(self):
  m=self.load();import json,urllib.parse,hashlib
  prompt='a fox & a cabin + snow'*2000
  body=urllib.parse.urlencode({'f.req':json.dumps([[['rpc',json.dumps([None,[prompt]])]]])})
  self.assertTrue(m.request_matches(body,hashlib.sha256(prompt.encode()).hexdigest()))
  self.assertFalse(m.request_matches(body,hashlib.sha256((prompt+'!').encode()).hexdigest()))
 def test_second_job_can_submit_while_first_waits_and_output_is_reserved(self):
  m=self.load();import fcntl,json
  with tempfile.TemporaryDirectory() as d:
   m.ROOT=Path(d);m.PENDING=m.ROOT/'pending.json'
   m.ensure_daemon=lambda:'pid=44561 version=1.12.0 auto-connect'
   m.page_id=lambda:8;m.prepare=lambda *a:'uid=1 textbox "What do you want"'
   m.run_cli=lambda *a,**kw:{}
   m.network_requests=lambda *a:[]
   m.evaluate=lambda *a:[]
   serial=iter([101,102]);m.find_submission=lambda *a:next(serial)
   a=m.submit_job('first',m.ROOT/'first.jpg','1:1',[])
   self.assertEqual(a['state'],'submitted')
   with (m.ROOT/'generation.lock').open('w') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   b=m.submit_job('second',m.ROOT/'second.jpg','1:1',[])
   self.assertNotEqual(a['request_id'],b['request_id'])
   self.assertEqual(a['network_request_id'],101);self.assertEqual(b['network_request_id'],102)
   with self.assertRaisesRegex(FileExistsError,'reserved'):
    m.submit_job('third',m.ROOT/'first.jpg','1:1',[])
 def test_ambiguous_submission_blocks_resubmit_but_known_inflight_jobs_do_not(self):
  m=self.load();import json
  with tempfile.TemporaryDirectory() as d:
   m.ROOT=Path(d);m.PENDING=m.ROOT/'pending.json'
   m.save_job({'request_id':'a'*32,'state':'submitting','output':str(m.ROOT/'a.jpg')})
   with self.assertRaisesRegex(RuntimeError,'unconfirmed'):
    m.submit_job('next',m.ROOT/'b.jpg','1:1',[])
 def test_ui_recovery_requires_one_exact_prompt_not_the_newest_image(self):
  m=self.load();import hashlib
  digest=hashlib.sha256(b'cactus').hexdigest()
  rows=[{'id':'newest-other','prompt':'grapes'},{'id':'mine','prompt':'cactus'}]
  self.assertEqual(m.choose_ui_result(rows,digest)['id'],'mine')
  self.assertIsNone(m.choose_ui_result([rows[0]],digest))
  with self.assertRaisesRegex(RuntimeError,'ambiguous'):
   m.choose_ui_result([rows[1],dict(rows[1],id='second-cactus')],digest)
 def test_aborted_connection_can_recover_its_verified_ui_result(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as d:
   m.ROOT=Path(d);m.PENDING=m.ROOT/'pending.json';out=m.ROOT/'image.jpg'
   job={'request_id':'b'*32,'state':'submitted','network_request_id':1,'page_id':8,'daemon_pid':44561,'output':str(out),'mode':'text-to-image','reference_count':0,'model':'Nano Banana 2.1','project':'test','submitted_at':0}
   m.save_job(job)
   m.run_cli=lambda *a,**kw:'pid=44561'
   m.network_requests=lambda *a:[{'requestId':1,'status':'net::ERR_ABORTED'}]
   m.find_ui_result=lambda j:{'id':'verified','src':'test','width':1024,'height':1024}
   def save(url,path):path.write_bytes(b'\xff\xd8\xff');return path
   m.download=save
   self.assertEqual(m.wait_job(job['request_id'],timeout=1)['media_id'],'verified')
   self.assertTrue(out.exists())
 def test_reference_content_reused_across_paths_and_scoped_to_project(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as d:
   m.ROOT=Path(d);a=m.ROOT/'first.jpg';b=m.ROOT/'renamed.jpg';a.write_bytes(b'\xff\xd8\xffsame-image');b.write_bytes(a.read_bytes())
   uploads=[];selections=[];m.lookup_historical_reference=lambda *args:None
   def upload(page,path,entry,count):
    uploads.append((m.PROJECT,path));return dict(entry,media_id='1'*8+'-1111-4111-8111-'+'1'*12,state='ready')
   m.upload_reference=upload;m.select_reference=lambda page,entry,count:selections.append(entry['media_id'])
   m.PROJECT='project-a';m.reference_digest(a);m.attach_reference(8,a);m.attach_reference(8,b)
   self.assertEqual(len(uploads),1);self.assertEqual(len(selections),1)
   # Loading the cache again must retain reuse; a different project cannot borrow it.
   self.assertEqual(m.cached_reference(m.reference_digest(b))['media_id'],selections[0])
   m.PROJECT='project-b';m.attach_reference(8,b);self.assertEqual(len(uploads),2)
 def test_cached_reference_failure_never_silently_uploads_again(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as d:
   m.ROOT=Path(d);p=m.ROOT/'a.jpg';p.write_bytes(b'\xff\xd8\xffsame-image')
   m.store_reference(m.reference_digest(p),{'media_id':'old','name':'old.jpg','state':'ready'})
   m.upload_reference=lambda *a:self.fail('A cached reference must not be uploaded again')
   def missing(*a):raise RuntimeError('cached material missing')
   m.select_reference=missing
   with self.assertRaisesRegex(RuntimeError,'missing'):m.attach_reference(8,p)
 def test_cached_timeout_preserves_mapping_without_reupload(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as d:
   m.ROOT=Path(d);p=m.ROOT/'a.jpg';p.write_bytes(b'\xff\xd8\xffsame-image')
   entry={'media_id':'known','name':'known.jpg','state':'ready'}
   m.store_reference(m.reference_digest(p),entry)
   m.upload_reference=lambda *a:self.fail('Timeout must not create another upload')
   def timeout(*a):raise TimeoutError('reference not ready')
   m.select_reference=timeout
   with self.assertRaises(TimeoutError):m.attach_reference(8,p)
   self.assertEqual(m.cached_reference(m.reference_digest(p)),entry)
 def test_unverifiable_history_does_not_start_a_new_upload(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as d:
   m.ROOT=Path(d);p=m.ROOT/'a.jpg';p.write_bytes(b'\xff\xd8\xffsame-image')
   def unverified(*a):raise RuntimeError('history cannot be verified')
   m.lookup_historical_reference=unverified
   m.upload_reference=lambda *a:self.fail('Unverified history must not create another upload')
   with self.assertRaisesRegex(RuntimeError,'history'):m.attach_reference(8,p)
   self.assertIsNone(m.cached_reference(m.reference_digest(p)))
 def test_same_name_material_is_clicked_by_exact_media_id(self):
  m=self.load();wanted='22222222-2222-4222-8222-222222222222';attached=[]
  m.snapshot=lambda page:'uid=1 listbox "资源列表"\nuid=2 textbox "搜索资源"\nuid=3 option "reference.jpg 图片"\nuid=4 option "reference.jpg 图片"'
  m.run_cli=lambda *a,**k:{}
  def browser(page,source):
   if source==m.REFS_JS:return [{'id':mid,'busy':False,'width':896,'height':1200} for mid in attached]
   observation=self.dom(source,duplicateNames=True,captureClick=True)
   attached.extend(observation['clicked'])
   return observation['result']
  m.evaluate=browser
  try:result=m.select_reference(8,{'media_id':wanted,'name':'reference.jpg'},1)
  except ValueError as e:self.fail('A verified media ID must remain selectable among same-name siblings: '+str(e))
  self.assertEqual(result['media_id'],wanted)
  self.assertEqual(attached,[wanted])
 def test_unidentified_duplicate_materials_stop_before_clicking(self):
  m=self.load();clicked=[]
  m.snapshot=lambda page:'uid=1 listbox "资源列表"\nuid=2 textbox "搜索资源"\nuid=3 option "reference.jpg 图片"\nuid=4 option "reference.jpg 图片"'
  m.run_cli=lambda *a,**k:{}
  def browser(page,source):
   observation=self.dom(source,duplicateNames=True,captureClick=True);clicked.extend(observation['clicked']);return observation['result']
  m.evaluate=browser
  with self.assertRaises((RuntimeError,ValueError)):m.select_reference(8,{'media_id':None,'name':'reference.jpg','state':'uploading'},1)
  self.assertEqual(clicked,[])
 def test_unavailable_network_body_stops_history_verification(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as d:
   m.ROOT=Path(d)
   for response in ([],[{'type':'text','text':'body unavailable'}],{'networkRequest':None}):
    with self.subTest(response=response):
     m.run_cli=lambda *a,**k:response
     try:
      with self.assertRaises(m.BodyUnavailable):m.read_network_body(8,1,'request')
     except (TypeError,KeyError,AttributeError) as e:self.fail('Missing body must report BodyUnavailable: '+str(e))
 def test_reference_menu_waits_for_its_search_control(self):
  m=self.load();snapshots=iter(['uid=1 button "在提示框中添加素材"','uid=1 button "在提示框中添加素材"','uid=2 listbox "资源列表"\nuid=3 textbox "搜索资源"']);calls=[]
  m.snapshot=lambda page:next(snapshots)
  m.run_cli=lambda *a,**k:calls.append(a)
  with patch.object(m.time,'sleep'):m.open_reference_menu(8)
  self.assertEqual(calls,[('click',8,'1')])
  with self.assertRaises(StopIteration):next(snapshots)
 def test_historical_reference_ids_require_exact_prompt_and_count(self):
  m=self.load();import json,urllib.parse,hashlib
  prompt='use both images';sha=hashlib.sha256(prompt.encode()).hexdigest()
  ids=['11111111-1111-4111-8111-111111111111','22222222-2222-4222-8222-222222222222']
  payload=[None,[[None,None,[[x,None] for x in ids],prompt]]]
  body=urllib.parse.urlencode({'f.req':json.dumps([[['ogiZ0b',json.dumps(payload)]]])})
  self.assertEqual(m.historical_reference_ids(body,sha,2),ids)
  self.assertEqual(m.historical_reference_ids(body,'wrong',2),[])
  self.assertEqual(m.historical_reference_ids(body,sha,3),[])
 def test_existing_asset_can_attach_directly_without_add_button(self):
  m=self.load();mid='11111111-1111-4111-8111-111111111111'
  snap='uid=1 listbox "资源列表"\nuid=2 textbox "搜索资源"\nuid=3 option "existing.jpg 图片"'
  m.snapshot=lambda page:snap;m.run_cli=lambda *a,**k:{}
  m.evaluate=lambda page,js:([{'name':'existing.jpg','id':mid}] if js==m.ASSET_OPTIONS_JS else ([{'id':mid,'busy':False,'width':1024,'height':1024}] if js==m.REFS_JS else mid))
  self.assertEqual(m.select_reference(8,{'name':'existing.jpg','media_id':mid},1)['media_id'],mid)
 def test_direct_attachment_waits_for_thumbnail_when_add_button_has_closed(self):
  m=self.load();mid='11111111-1111-4111-8111-111111111111'
  snap='uid=1 listbox "资源列表"\nuid=2 textbox "搜索资源"\nuid=3 option "existing.jpg 图片"'
  m.snapshot=lambda page:snap;m.run_cli=lambda *a,**k:{}
  chips=iter([[{'id':None,'busy':False,'width':0,'height':0}],[{'id':mid,'busy':False,'width':1024,'height':1024}]])
  m.evaluate=lambda page,js:([{'name':'existing.jpg','id':mid}] if js==m.ASSET_OPTIONS_JS else (next(chips) if js==m.REFS_JS else mid))
  try:result=m.select_reference(8,{'name':'existing.jpg','media_id':mid},1)
  except ValueError as e:self.fail('A directly attached reference must be allowed to finish loading: '+str(e))
  self.assertEqual(result['media_id'],mid)
 def test_interrupted_upload_is_recovered_without_upload_retry(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as d:
   m.ROOT=Path(d);p=m.ROOT/'a.jpg';p.write_bytes(b'\xff\xd8\xffsame-image')
   m.lookup_historical_reference=lambda *a:None;uploads=[]
   def interrupted(*a):uploads.append(1);raise TimeoutError('interrupted')
   m.upload_reference=interrupted
   with self.assertRaises(TimeoutError):m.attach_reference(8,p)
   self.assertEqual(m.cached_reference(m.reference_digest(p))['state'],'uploading')
   m.select_reference=lambda page,entry,count:dict(entry,media_id='recovered',state='ready')
   self.assertEqual(m.attach_reference(8,p)['media_id'],'recovered')
   self.assertEqual(len(uploads),1)
if __name__=='__main__' :unittest.main()
